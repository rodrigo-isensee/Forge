"""A3 (pedido v0478, E29.1): o sandbox nega aos agentes a escrita nos arquivos de controle; os hooks seguem gravando.

Arquivos de controle (registro de agentes, teto, fila pesada, registro da máquina) e o `denyWrite` que os cobre:
- modelo de projeto (`templates/projeto/.claude/settings.json`): `.forge/config.json` (teto), `.forge/run/agentes.json`,
  `.forge/run/pesado.json`, `.forge/run/pesado.fila` e `~/.forge/maquina` (o registro da máquina);
- Forge (`.claude/settings.json`, arquivo travado para os agentes; vai como patch `docs/devops/v0479-sandbox-controle.patch`, que o
  dono aplica): `.forge/` (no clone é um arquivo), `.git/forge/run` (o estado do clone) e `~/.forge/maquina`.

As provas estruturais sempre rodam. As do sandbox montam um bubblewrap com o `denyWrite` do arquivo (cada caminho existente vira
`--ro-bind` sobre ele, o que o runtime do Claude Code faz) e tentam `find -delete`, `tar` por cima e `chmod`; sem bubblewrap
utilizável pulam com o motivo fora do CI (`apoio_sandbox.exigir`) e reprovam no CI.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_sandbox import exigir  # noqa: E402
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "templates" / "projeto" / ".claude" / "settings.json"
FORGE = RAIZ / ".claude" / "settings.json"
PATCH = RAIZ / "docs" / "devops" / "v0479-sandbox-controle.patch"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})

CONTROLE_DO_MODELO = [".forge/config.json", ".forge/run/agentes.json", ".forge/run/pesado.json", ".forge/run/pesado.fila",
                      "~/.forge/maquina"]
CONTROLE_DO_FORGE = [".forge/", ".git/forge/run", "~/.forge/maquina"]


def deny_write(arquivo):
    return json.loads(Path(arquivo).read_text(encoding="utf-8"))["sandbox"]["filesystem"]["denyWrite"]


def deny_write_do_forge():
    """O `denyWrite` do Forge com o patch: o arquivo em vigor, se o dono já o aplicou; senão uma cópia temporária remendada."""
    if all(c in deny_write(FORGE) for c in CONTROLE_DO_FORGE):
        return deny_write(FORGE), True
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / ".claude").mkdir()
        shutil.copy2(FORGE, Path(tmp) / ".claude" / "settings.json")
        r = subprocess.run(["git", "apply", str(PATCH)], cwd=tmp, env=AMBIENTE, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        return deny_write(Path(tmp) / ".claude" / "settings.json"), False


class Estrutura(unittest.TestCase):
    def test_modelo_de_projeto_nega_os_cinco_caminhos_de_controle(self):
        deny = deny_write(MODELO)
        for caminho in CONTROLE_DO_MODELO:
            self.assertIn(caminho, deny)

    def test_forge_com_o_patch_nega_o_clone_e_o_registro_da_maquina(self):
        deny, _ = deny_write_do_forge()
        for caminho in CONTROLE_DO_FORGE:
            self.assertIn(caminho, deny)

    def test_o_patch_so_acrescenta_dois_caminhos_ao_denywrite(self):
        linhas = [x for x in PATCH.read_text(encoding="utf-8").splitlines() if x[:1] in "+-" and x[:3] not in ("+++", "---")]
        self.assertEqual([x for x in linhas if x[0] == "-"], ['-        ".forge/"'])
        self.assertEqual(["+" + x[1:].strip() for x in linhas if x[0] == "+"],
                         ['+".forge/",', '+".git/forge/run",', '+"~/.forge/maquina"'])

    def test_os_caminhos_negados_sao_os_que_os_hooks_gravam(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import _maquina
            import agentes
        finally:
            sys.path.remove(str(RAIZ / "hooks"))
        self.assertEqual(_maquina.PASTA, "~/.forge/maquina")
        with tempfile.TemporaryDirectory() as tmp:
            projeto = Path(tmp) / "p"
            (projeto / ".forge").mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(projeto)], env=AMBIENTE, check=True, capture_output=True)
            self.assertEqual(agentes.arquivo_de_estado(projeto), projeto / ".forge" / "run" / "agentes.json")
        fonte = (RAIZ / "hooks" / "pesado.py").read_text(encoding="utf-8")
        self.assertIn('"pesado.json"', fonte)
        self.assertIn('"pesado.fila"', fonte)
        self.assertIn('/ "forge" / "run"', (RAIZ / "hooks" / "agentes.py").read_text(encoding="utf-8"))
        self.assertIn("teto_agentes", (RAIZ / "hooks" / "agentes.py").read_text(encoding="utf-8"))

    def test_nada_do_time_grava_nos_caminhos_negados_pelo_bash(self):
        """Os leitores do estado (forge-pesado, forge-status, forge-check fila) não abrem os arquivos para escrita."""
        import re
        for nome in ("forge-pesado", "forge-status"):
            fonte = (RAIZ / "bin" / nome).read_text(encoding="utf-8")
            self.assertIsNone(re.search(r"write_text|open\([^)]*[\"'][wa]|os\.replace|\.unlink\(|\.gravar\(", fonte), nome)

    def test_o_denywrite_do_forge_nao_cobre_arquivo_versionado(self):
        """N6: o `denyWrite` de arquivo versionado quebra pull, checkout e merge."""
        versionados = subprocess.run(["git", "ls-files"], cwd=RAIZ, env=AMBIENTE, capture_output=True, text=True, check=True).stdout.splitlines()
        for caminho in deny_write_do_forge()[0]:
            prefixo = caminho if caminho.endswith("/") else caminho + "/"
            cobertos = [f for f in versionados if f == caminho or f.startswith(prefixo)]
            self.assertEqual(cobertos, [], caminho)


def caminho_real(entrada, raiz, casa):
    """Como o runtime resolve uma entrada de `denyWrite`: `~` é a casa, relativo é da raiz do projeto."""
    if entrada.startswith("~/"):
        return casa / entrada[2:].rstrip("/")
    return raiz / entrada.rstrip("/")


class SandboxNegaEscrita(unittest.TestCase):
    """O bubblewrap com o `denyWrite` do arquivo recusa o `find -delete`, o `tar` por cima e o `chmod`."""

    def montar(self, deny, clone):
        """Projeto e casa de mentira com cada caminho de controle no lugar; devolve (raiz, casa, alvos existentes)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-sandbox-controle-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        raiz, casa = tmp / "projeto", tmp / "casa"
        raiz.mkdir()
        casa.mkdir()
        alvos = []
        for entrada in deny:
            alvo = caminho_real(entrada, raiz, casa)
            if entrada == ".forge/" and clone:  # no clone do Forge, `.forge` é um arquivo
                alvo.write_text("proteção\n", encoding="utf-8")
            elif entrada in (".forge/run/pesado.fila", ".git/forge/run", "~/.forge/maquina"):
                alvo.mkdir(parents=True)
                alvo.chmod(0o700)  # o registro da máquina exige a pasta só do usuário (`_maquina.pasta`)
                (alvo / "1").write_text("original\n", encoding="utf-8")
            else:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_text("original\n", encoding="utf-8")
            alvos.append(alvo)
        if not (raiz / ".forge").is_file():
            (raiz / ".forge" / "run").mkdir(parents=True, exist_ok=True)
        return raiz, casa, alvos

    def argv(self, raiz, casa, alvos, cmd):
        base = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--bind", str(raiz), str(raiz), "--bind", str(casa), str(casa)]
        for alvo in alvos:
            base += ["--ro-bind", str(alvo), str(alvo)]
        return base + ["--chdir", str(raiz), "sh", "-c", cmd]

    def rodar(self, raiz, casa, alvos, cmd):
        return subprocess.run(self.argv(raiz, casa, alvos, cmd), capture_output=True, text=True, timeout=60)

    def lido(self, alvo):
        if alvo.is_dir():
            return sorted((p.name, p.read_text(encoding="utf-8")) for p in alvo.iterdir())
        return alvo.read_text(encoding="utf-8")

    def ataca(self, raiz, casa, alvos):
        """Cada ataque contra cada alvo é recusado (rc diferente de 0) e o alvo fica como estava; o controle prova que o
        sandbox monta (escrita ao lado passa) e que, sem a trava, o mesmo ataque funciona."""
        sobra = raiz / "ao-lado.txt"
        self.assertEqual(self.rodar(raiz, casa, alvos, f"echo ok > {sobra}").returncode, 0, "o sandbox deixa o resto gravável")
        self.assertEqual(sobra.read_text(encoding="utf-8"), "ok\n")
        for alvo in alvos:
            antes, modo = self.lido(alvo), alvo.stat().st_mode
            pacote = raiz.parent / f"{alvo.name}.tar"
            troca = raiz.parent / "troca" / alvo.name
            if alvo.is_dir():
                troca.mkdir(parents=True, exist_ok=True)
                (troca / "1").write_text("adulterado\n", encoding="utf-8")
            else:
                troca.parent.mkdir(parents=True, exist_ok=True)
                troca.write_text("adulterado\n", encoding="utf-8")
            subprocess.run(["tar", "-cf", str(pacote), "-C", str(troca.parent), alvo.name], check=True)
            ataques = {
                "find -delete": f"find '{alvo}' -delete",
                "tar por cima": f"tar -xf '{pacote}' -C '{alvo.parent}'",
                "chmod": f"chmod 000 '{alvo}'",
            }
            if alvo.is_dir():
                ataques["find -delete (arquivo de dentro)"] = f"find '{alvo}' -type f -delete"
                ataques["chmod no arquivo de dentro"] = f"chmod 000 '{alvo}'/1"
            for nome, cmd in ataques.items():
                with self.subTest(alvo=str(alvo.relative_to(raiz.parent)), ataque=nome):
                    r = self.rodar(raiz, casa, alvos, cmd)
                    self.assertNotEqual(r.returncode, 0, f"{nome} passou em {alvo}: {r.stdout}{r.stderr}")
                    self.assertTrue(alvo.exists())
                    self.assertEqual(self.lido(alvo), antes)
                    self.assertEqual(alvo.stat().st_mode, modo)
            livre = self.rodar(raiz, casa, [], f"chmod 000 '{alvo}' && chmod 700 '{alvo}'")  # sem a trava o chmod passa
            self.assertEqual(livre.returncode, 0, f"o controle sem a trava falhou: {livre.stderr}")
            alvo.chmod(modo & 0o7777)

    def test_modelo_de_projeto_recusa_find_tar_e_chmod_e_o_hook_grava(self):
        exigir(self, "bwrap")
        raiz, casa, alvos = self.montar(deny_write(MODELO), clone=False)
        self.ataca(raiz, casa, alvos)
        # O hook roda pelo harness, fora do sandbox: com o sandbox montado, ele grava o registro da máquina.
        maquina = casa / ".forge" / "maquina"
        sandbox = subprocess.Popen(self.argv(raiz, casa, alvos, "read x"), stdin=subprocess.PIPE, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            codigo = ("import sys; sys.path.insert(0, 'hooks'); import _maquina; "
                      "_maquina.gravar('projetos-ativos.json', {'projetos': ['x'], 'sessoes': {}})")
            r = subprocess.run([sys.executable, "-I", "-c", codigo], cwd=RAIZ, env={**AMBIENTE, "FORGE_MAQUINA": str(maquina)},
                               capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(json.loads((maquina / "projetos-ativos.json").read_text(encoding="utf-8"))["projetos"], ["x"])
        finally:
            sandbox.communicate("\n", timeout=30)

    def test_forge_com_o_patch_recusa_find_tar_e_chmod(self):
        exigir(self, "bwrap")
        deny, _ = deny_write_do_forge()
        raiz, casa, alvos = self.montar(deny, clone=True)
        self.ataca(raiz, casa, alvos)


if __name__ == "__main__":
    unittest.main()
