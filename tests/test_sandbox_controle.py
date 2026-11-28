"""A3 (pedido v0478, E29.1): o sandbox nega aos agentes a escrita nos arquivos de controle; os hooks seguem gravando.

Arquivos de controle (registro de agentes, teto, fila pesada, registro da máquina) e o `denyWrite` que os cobre:
- modelo de projeto (`templates/projeto/.claude/settings.json`): `.forge/config.json` (teto), `.forge/run/agentes.json`,
  `.forge/run/pesado.json` e `~/.forge/maquina` (o registro da máquina); a fila do projeto (`.forge/run/pesado.fila`) não existe
  mais desde a MP4 e saiu da lista;
- Forge (`.claude/settings.json`, arquivo travado para os agentes; vai como patch `docs/engineering/v0479-sandbox-controle.patch`, que o
  dono aplica): `.forge/` (na cópia do dono é pasta, com `config.json` e `run/`), `.git/forge/run` (o estado do clone) e `~/.forge/maquina`.

As provas estruturais sempre rodam. As do sandbox montam um bubblewrap com o `denyWrite` do arquivo (cada caminho existente vira
`--ro-bind` sobre ele, o que o runtime do Claude Code faz) e tentam `find -delete`, `tar` por cima, `chmod`, a escrita direta
(`>`, `sort -o`), `git init` na pasta e `mv` por cima; sem bubblewrap
utilizável pulam com o motivo fora do CI (`apoio_sandbox.exigir`) e reprovam no CI.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_sandbox import exigir  # noqa: E402
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MODELO = RAIZ / "templates" / "projeto" / ".claude" / "settings.json"
FORGE = RAIZ / ".claude" / "settings.json"
PATCH = RAIZ / "docs" / "engineering" / "v0479-sandbox-controle.patch"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})

CONTROLE_DO_MODELO = [".forge/config.json", ".forge/run/agentes.json", ".forge/run/pesado.json", "~/.forge/maquina"]
CONTEUDO = {".forge/run/agentes.json": '{"agentes": []}\n', ".forge/run/pesado.json": "null\n"}
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
    def test_modelo_de_projeto_nega_os_quatro_caminhos_de_controle(self):
        deny = deny_write(MODELO)
        for caminho in CONTROLE_DO_MODELO:
            self.assertIn(caminho, deny)
        self.assertNotIn(".forge/run/pesado.fila", deny, "a fila do projeto morreu na MP4: negá-la só cria arquivo-lixo")

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


def produzir_controle(raiz):
    """Roda o `preparar_controle` do hook `doutor` (SessionStart) numa raiz de projeto com git: cria `agentes.json` e `pesado.json`."""
    sys.path.insert(0, str(RAIZ / "hooks"))
    try:
        import _comum
        import doutor
        hook = _comum.Hook("doutor")
        hook.raiz = raiz
        doutor.preparar_controle(hook)
    finally:
        sys.path.remove(str(RAIZ / "hooks"))


def caminho_real(entrada, raiz, casa):
    """Como o runtime resolve uma entrada de `denyWrite`: `~` é a casa, relativo é da raiz do projeto."""
    if entrada.startswith("~/"):
        return casa / entrada[2:].rstrip("/")
    return raiz / entrada.rstrip("/")


class ControleVazio(unittest.TestCase):
    """A2 da segurança: o runtime do sandbox cria vazio e 0444 o caminho negado que não existe. Os arquivos de controle passam a
    existir antes (forge-init, hook de início de sessão) e o vazio não trava o time nem solta a trava de tarefa pesada."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-controle-vazio-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.proj = self.tmp / "proj"
        (self.proj / ".forge").mkdir(parents=True)
        (self.proj / ".forge" / "versao").write_text("0.47.7\n", encoding="utf-8")
        (self.proj / ".forge" / "config.json").write_text(json.dumps({"pesados": ["python3 -m unittest"]}), encoding="utf-8")
        subprocess.run(["git", "init", "-q", "-b", "trabalho", str(self.proj)], env=AMBIENTE, check=True, capture_output=True)
        self.run_dir = self.proj / ".forge" / "run"

    def vazio_0444(self, nome):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        arquivo = self.run_dir / nome
        arquivo.write_text("", encoding="utf-8")
        arquivo.chmod(0o444)
        return arquivo

    def hook(self, nome, evento, **campos):
        sys.path.insert(0, str(RAIZ / "tests"))
        try:
            from test_agentes_clone import montar_proc, rodar_hook
        finally:
            sys.path.remove(str(RAIZ / "tests"))
        proc = self.tmp / "proc"
        if not proc.exists():
            montar_proc(self.tmp)
        entrada = {"hook_event_name": evento, "session_id": "s", "cwd": str(self.proj), **campos}
        return rodar_hook(nome, entrada, self.proj, proc, {"FORGE_NPROC": "4", "FORGE_PESADO_ESPERA_S": "0"})

    def pesado(self, agente, uso, evento="PreToolUse"):
        return self.hook("pesado", evento, tool_name="Bash", agent_id=agente, tool_use_id=uso,
                         tool_input={"command": "python3 -m unittest discover"})

    def test_agentes_json_de_0_byte_segue_ilegivel_e_o_pesado_json_de_0_byte_vale_sem_trava(self):
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import agentes
            import _comum
        finally:
            sys.path.remove(str(RAIZ / "hooks"))
        with self.assertRaises(agentes.EstadoIlegivel):  # HOOK-ESTADO-ILEGIVEL-LIBERA: o 0 byte do registro não vale sem registro
            agentes.ler_estado(self.vazio_0444("agentes.json"))
        ler_trava = getattr(_comum, "ler_trava", None)
        self.assertIsNotNone(ler_trava, "a trava de 0 byte vale como ausente: precisa do leitor próprio")
        self.assertIsNone(ler_trava(self.vazio_0444("pesado.json")))
        (self.run_dir / "pesado.json").chmod(0o644)
        (self.run_dir / "pesado.json").write_text("{", encoding="utf-8")
        with self.assertRaises(ValueError):  # JSON quebrado na trava segue erro
            ler_trava(self.run_dir / "pesado.json")

    def test_o_gravar_json_nao_segue_nem_reaproveita_o_temporario_plantado(self):
        """S1 da segurança (A5): o agente planta `pesado.json.<pid>.tmp` como link para um arquivo seu; o hook não escreve nele."""
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import _comum
        finally:
            sys.path.remove(str(RAIZ / "hooks"))
        alvo = self.tmp / "alvo-do-agente"
        alvo.write_text("null\n", encoding="utf-8")
        trava = self.run_dir / "pesado.json"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.run_dir / f"pesado.json.{os.getpid()}.tmp"
        os.symlink(alvo, tmp)
        _comum.gravar_json(trava, {"pid": 1, "desde": 1})  # a sobra sai antes: o link não é seguido
        self.assertEqual(alvo.read_text(encoding="utf-8"), "null\n")
        self.assertTrue(trava.is_file() and not trava.is_symlink())
        self.assertEqual(json.loads(trava.read_text(encoding="utf-8"))["pid"], 1)
        for planta in ("link", "arquivo"):  # o agente planta depois da checagem: a corrida cai no O_EXCL, que recusa
            with self.subTest(planta=planta), mock.patch.object(os.path, "lexists", return_value=False):
                if planta == "link":
                    os.symlink(alvo, tmp)
                else:
                    tmp.write_text("plantado\n", encoding="utf-8")
                with self.assertRaises(FileExistsError):
                    _comum.gravar_json(trava, {"pid": 2, "desde": 2})
                self.assertEqual(alvo.read_text(encoding="utf-8"), "null\n")
                self.assertEqual(json.loads(trava.read_text(encoding="utf-8"))["pid"], 1)
                if planta == "arquivo":
                    self.assertEqual(tmp.read_text(encoding="utf-8"), "plantado\n")
                tmp.unlink()

    def test_pesado_json_vazio_0444_nao_solta_a_trava_do_proximo(self):
        self.vazio_0444("pesado.json")
        self.assertEqual(self.pesado("a1", "u1").returncode, 0)
        r = self.pesado("a2", "u2")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO", r.stderr)

    def test_a_soltura_grava_null_e_nao_apaga_o_pesado_json(self):
        self.assertEqual(self.pesado("a1", "u1").returncode, 0)
        self.assertEqual(self.pesado("a1", "u1", "PostToolUse").returncode, 0)
        arquivo = self.run_dir / "pesado.json"
        self.assertTrue(arquivo.is_file(), "apagar deixaria o runtime recriá-lo vazio")
        self.assertIsNone(json.loads(arquivo.read_text(encoding="utf-8")))
        self.assertEqual(self.pesado("a2", "u2").returncode, 0, "trava solta: a próxima pega a vez")

    def test_inicio_de_sessao_cria_os_arquivos_de_controle_que_faltam_e_nao_regrava_os_que_existem(self):
        r = self.hook("doutor", "SessionStart")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.run_dir / "agentes.json").is_file() and (self.run_dir / "pesado.json").is_file())
        self.assertEqual(json.loads((self.run_dir / "agentes.json").read_text(encoding="utf-8")), {"agentes": []})
        self.assertIsNone(json.loads((self.run_dir / "pesado.json").read_text(encoding="utf-8")))
        (self.run_dir / "agentes.json").write_text('{"agentes": [{"id": "x"}]}', encoding="utf-8")
        self.hook("doutor", "SessionStart")
        self.assertIn('"x"', (self.run_dir / "agentes.json").read_text(encoding="utf-8"))

    def test_forge_init_cria_os_arquivos_de_controle_antes_da_primeira_sessao(self):
        destino = self.tmp / "novo"
        destino.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "trabalho", str(destino)], env=AMBIENTE, check=True, capture_output=True)
        casa = self.tmp / "casa"
        casa.mkdir()
        env = {**AMBIENTE, "HOME": str(casa), "FORGE_MAQUINA": str(self.tmp / "maquina")}
        subprocess.run(["bash", str(RAIZ / "bin" / "forge-init"), "--nome", "Demo", "--pronto", "make pronto", str(destino)],
                       cwd=destino, env=env, check=True, capture_output=True, text=True, timeout=120)
        run = destino / ".forge" / "run"
        self.assertTrue((run / "agentes.json").is_file() and (run / "pesado.json").is_file())
        self.assertEqual(json.loads((run / "agentes.json").read_text(encoding="utf-8")), {"agentes": []})
        self.assertIsNone(json.loads((run / "pesado.json").read_text(encoding="utf-8")))
        self.assertFalse((run / "pesado.fila").exists(), "a fila do projeto morreu na MP4")
        ignorados = subprocess.run(["git", "check-ignore", ".forge/run/agentes.json"], cwd=destino, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(ignorados.returncode, 0, "o estado de execução não vai ao git")


class SandboxNegaEscrita(unittest.TestCase):
    """O bubblewrap com o `denyWrite` do arquivo recusa o `find -delete`, o `tar` por cima e o `chmod`."""

    def montar(self, deny, clone):
        """Projeto e casa de mentira com cada caminho de controle no lugar, no estado que o `forge-init` e o hook de início de
        sessão deixam (`agentes.json` e `pesado.json` já existem; o runtime só cria caminho negado que falta); devolve
        (raiz, casa, alvos existentes)."""
        tmp = Path(tempfile.mkdtemp(prefix="forge-sandbox-controle-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        raiz, casa = tmp / "projeto", tmp / "casa"
        raiz.mkdir()
        casa.mkdir()
        subprocess.run(["git", "init", "-q", str(raiz)], env=AMBIENTE, check=True, capture_output=True)
        if any(e in CONTEUDO for e in deny):
            produzir_controle(raiz)  # o hook de início de sessão, não a mão do teste, cria os arquivos de controle do projeto
        alvos = []
        for entrada in deny:
            alvo = caminho_real(entrada, raiz, casa)
            if entrada in CONTEUDO:
                # o hook grava com `indent=1` e o `forge-init`, compacto: vale o JSON, não o texto
                self.assertEqual(json.loads(alvo.read_text(encoding="utf-8")), json.loads(CONTEUDO[entrada]), entrada)
                alvos.append(alvo)
                continue
            if entrada in (".forge/", ".git/forge/run", "~/.forge/maquina"):
                alvo.mkdir(parents=True)
                alvo.chmod(0o700)  # o registro da máquina exige a pasta só do usuário (`_maquina.pasta`)
                (alvo / "1").write_text("original\n", encoding="utf-8")
            else:
                alvo.parent.mkdir(parents=True, exist_ok=True)
                alvo.write_text("original\n", encoding="utf-8")
            alvos.append(alvo)
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
        if alvo.is_dir():  # `.forge/` guarda a pasta `run`: lê os arquivos de toda a árvore
            return sorted((str(p.relative_to(alvo)), p.read_text(encoding="utf-8")) for p in alvo.rglob("*") if p.is_file())
        return alvo.read_text(encoding="utf-8")

    def ataca(self, raiz, casa, alvos):
        """Cada ataque contra cada alvo é recusado (rc diferente de 0) e o alvo fica como estava; o controle prova que o
        sandbox monta (escrita ao lado passa) e que, sem a trava, o mesmo ataque funciona."""
        sobra = raiz / "ao-lado.txt"
        self.assertEqual(self.rodar(raiz, casa, alvos, f"echo ok > {sobra}").returncode, 0, "o sandbox deixa o resto gravável")
        self.assertEqual(sobra.read_text(encoding="utf-8"), "ok\n")
        for alvo in alvos:
            antes, modo = self.lido(alvo), alvo.stat().st_mode
            origem = raiz / "mv-origem"
            origem.write_text("adulterado\n", encoding="utf-8")
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
                "escrita direta (>)": f"echo adulterado > '{alvo}'",
                "escrita direta (sort -o)": f"echo adulterado | sort -o '{alvo}'",
                "mv por cima": f"mv '{origem}' '{alvo}'",
            }
            if alvo.is_dir():
                ataques["git init na pasta"] = f"git -C '{alvo}' init"
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
        with self.subTest(limite="renomear a pasta mãe"):
            self.limite_renomear_a_pasta_mae_escapa_da_trava_por_arquivo()

    def limite_renomear_a_pasta_mae_escapa_da_trava_por_arquivo(self):
        """A2 da segurança, limite conhecido (docs/hooks.md, docs/engineering/v0479-sandbox-controle.md): o `denyWrite` é por arquivo; a
        pasta mãe (`.forge/run`, que o Bash do time grava) é renomeável, e o agente recria o registro por cima. O teste prova o
        limite, não o fecha; o fecho é o cartão da identidade da pasta. Se o runtime passar a recusar, este teste cai e o limite sai da doc."""
        raiz, casa, alvos = self.montar(deny_write(MODELO), clone=False)
        run = raiz / ".forge" / "run"
        r = self.rodar(raiz, casa, alvos, f"mv '{run}' '{run}.velho' && mkdir '{run}' && echo '{{\"agentes\": []}}' > '{run}/agentes.json'")
        self.assertEqual(r.returncode, 0, f"o limite mudou (a pasta mãe agora é recusada): {r.stdout}{r.stderr}")
        self.assertEqual((run / "agentes.json").read_text(encoding="utf-8"), '{"agentes": []}\n')

    def test_forge_com_o_patch_recusa_find_tar_e_chmod(self):
        exigir(self, "bwrap")
        deny, _ = deny_write_do_forge()
        raiz, casa, alvos = self.montar(deny, clone=True)
        self.ataca(raiz, casa, alvos)


if __name__ == "__main__":
    unittest.main()
