"""S8 (versao-037 E7): o hook `conformidade` barra escrita na prova da suíte (`.verde`, `.dirigida`, `.novo`) e deixa a leitura
(casos de abuso e corpus de legítimos de docs/security/ameacas/versao-037.md, E7). Pastas temporárias só deste teste.
CF1 (v047 E2.179): as fixtures `opaco-cf1-*` e `trava-cf1-*`, com o oráculo pelo bash (`OraculoCf1`)."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_forge import ambiente_limpo, minimo  # noqa: E402
from test_hooks import FIXTURES, Fixture, rodar  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


class ComProjeto(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="forge-s8-")))
        self.proj, self.d, self.verde = self.tmp / "proj", self.tmp / "forge-1000", self.tmp / "forge-1000/forge-suite-1000.verde"
        (self.proj / ".forge").mkdir(parents=True)
        (self.proj / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        self.d.mkdir()
        (self.tmp / "s").symlink_to(self.verde)  # link simbólico para a prova (C-2, nome resolvido)
        subprocess.run(["git", "init", "-q", str(self.proj)], check=True, env=sem_manutencao(self.env()))

    def env(self, **extra):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
        return {**env, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "XDG_RUNTIME_DIR": str(self.d), **extra}

    def rodar(self, ferramenta, entrada, papel="forge:node-backend", cwd=None, **extra):
        dados = {"tool_name": ferramenta, "tool_input": entrada, "hook_event_name": "PreToolUse", "agent_type": papel}
        return subprocess.run([sys.executable, str(RAIZ / "hooks" / "conformidade.py")], input=json.dumps(dados),
                              cwd=cwd or self.proj, env=self.env(**extra), capture_output=True, text=True, timeout=120)

    def recusa(self, r, caso):
        self.assertEqual(r.returncode, 2, f"{caso}: {r.stderr}")
        self.assertRegex(r.stderr, "R-VERIFY.*só é gravada pelo pre-push.*pre-push --suite", caso)
        self.assertNotIn("--no-verify", r.stderr, caso)


class ProvaDaSuite(ComProjeto):
    def test_escrita_na_prova_recusa(self):
        v, d = str(self.verde), str(self.d)
        for papel in ("forge:node-backend", "forge:tech-lead", "forge:qa-engineer", None):
            self.recusa(self.rodar("Write", {"file_path": v, "content": "x"}, papel), f"Write ({papel})")
        self.recusa(self.rodar("Write", {"file_path": v, "content": "x"}, None, CLAUDE_PROJECT_DIR=str(RAIZ)), "sessão")
        self.recusa(self.rodar("Edit", {"file_path": f"{v}.novo", "old_string": "a", "new_string": "b"}), "Edit")
        self.recusa(self.rodar("Write", {"file_path": str(self.tmp / "s"), "content": "x"}), "Write por link")
        (self.d / "forge-suite-1000.dirigida").symlink_to(self.tmp / "outro")  # C-2: o nome literal, não só o resolvido
        self.recusa(self.rodar("Write", {"file_path": f"{d}/forge-suite-1000.dirigida", "content": "x"}), "nome literal")
        for c in ('printf x >> "$XDG_RUNTIME_DIR/forge-suite-1000.verde"', f"echo x >> {self.tmp}/s",
                  'echo x > "/tmp/forge-$(id -u)/forge-suite-$(id -u).verde"', f"echo x > {d}/forge-suite-*.verde",
                  f"cp a {d}/forge-suite-1000.dirigida", f"mv x {v}.novo", f"tee -a {v}", f"dd if=/dev/zero of={v}",
                  f"sed -i s/a/b/ {v}", f"ln {v} /tmp/h", f"ln -s {v} /tmp/h2", f"cp -l {v} /tmp/h", f"rm -f {v}",
                  f"python3 -c \"open('{v}','a').write('x')\"", f"python3 - <<'FIM'\nopen('{v}', 'w')\nFIM",
                  f"TMPDIR=/tmp/x bash -c 'echo y > /tmp/x/forge-1000/forge-suite-1000.verde'"):
            self.recusa(self.rodar("Bash", {"command": c}), c)
        (self.proj / ".forge" / "perfil").write_text("iniciante\n", encoding="utf-8")
        self.recusa(self.rodar("Write", {"file_path": str(self.verde), "content": "x"}), "iniciante")

    def test_pasta_fora_de_projeto_tambem_recusa(self):  # A2 da segurança g3: o ramo `externo is False` de principal
        v, fora = str(self.verde), self.tmp / "fora"
        fora.mkdir()
        outra = "echo x > ~/.claude/settings.json"  # recusa de dentro de projeto, que fora dele não vale
        for raiz, pasta in ((RAIZ, fora), (RAIZ, RAIZ), (None, fora)):
            extra = {"CLAUDE_PROJECT_DIR": str(raiz)} if raiz else {}
            for papel in ("forge:tech-lead", None):
                caso = f"raiz {raiz}, pasta {pasta}, papel {papel}"
                self.recusa(self.rodar("Write", {"file_path": v, "content": "x"}, papel, cwd=pasta, **extra), f"Write, {caso}")
                for c in (f"echo x > {v}", f"{outra}; echo x > {v}"):  # 2.º: a outra recusa vem antes
                    self.recusa(self.rodar("Bash", {"command": c}, papel, cwd=pasta, **extra), f"{c}, {caso}")
                for c in (f"cat {v}", f"echo x > {self.tmp}/outro.txt", *([] if raiz else [outra])):  # ADR 0009, 6
                    r = self.rodar("Bash", {"command": c}, papel, cwd=pasta, **extra)
                    self.assertEqual(r.returncode, 0, f"{c}, {caso}: {r.stderr}")
        for papel in ("forge:tech-lead", None):  # linha que o hook não lê (sem_leitura): volta ao texto e recusa só se cita a prova
            self.recusa(self.rodar("Bash", {"command": f"(true)#' {v}"}, papel, cwd=fora), f"ilegível com a prova, papel {papel}")
            r = self.rodar("Bash", {"command": f"(true)#' {self.tmp}/outro.txt"}, papel, cwd=fora)
            self.assertEqual(r.returncode, 0, f"ilegível sem a prova, papel {papel}: {r.stderr}")
        nb = self.rodar("NotebookEdit", {"notebook_path": v, "new_source": "x"}, "forge:conferente", cwd=fora)
        self.recusa(nb, "papel só de leitura: a recusa dele vem antes e não vale fora de projeto")
        self.assertFalse((fora / ".forge").exists(), "a outra recusa não é erro interno: nada no erros.log")

    def test_leitura_trava_e_fila_passam(self):
        v, d = str(self.verde), str(self.d)
        for c in (f"cat {v}", f"tail -n 3 {v}", f"grep -c . {v}", f"wc -l {v}", f"ls -l {d}/", f"stat {v}",
                  f"cp {v} {self.tmp}/copia", f"python3 -c \"print(open('{v}').read())\"",
                  f"cat > docs-x.md <<'FIM'\ncite {v}\nFIM", f"echo x > {d}/forge-suite-1000.lock",
                  f"touch {d}/forge-suite-1000.fila/.nova-5 {d}/forge-suite-1000.fila/1-5", f"rm -f {d}/forge-suite-1000.lock",
                  f"echo x > {d}/forge-suite-1000.verde.lock"):
            r = self.rodar("Bash", {"command": c})
            self.assertEqual(r.returncode, 0, f"{c}: {r.stderr}")
        r = self.rodar("Write", {"file_path": str(self.proj / "tests" / "test_x.py"), "content": f"# {v}\n"})
        self.assertEqual(r.returncode, 0, r.stderr)


class CarimboK6(ComProjeto):
    """N4/P3 (versao-045 E5a): o carimbo K6 (`forge-suite-verde`) e o temporário do `os.replace` de scripts/suite-paralela.py
    entram na prova da suíte (C-1 a C-4 de docs/security/ameacas/versao-045.md, E5a). C-3 refeito no adendo do desenho de
    2026-11-07: a leitura literal de `.git/forge-suite-verde` passa no clone do Forge, onde o carimbo existe; no projeto, a
    regra da marca da sessão fala antes e recusa (só o caminho montado passa)."""

    def test_clone_do_forge_le_e_recusa_escrita(self):  # caso 1 do adendo: raiz sem .forge/versao
        k6 = f"{RAIZ}/.git/forge-suite-verde"
        for c in ("cat .git/forge-suite-verde", f"cat {k6}", 'cat "$(git rev-parse --git-common-dir)/forge-suite-verde"'):
            r = self.rodar("Bash", {"command": c}, cwd=RAIZ, CLAUDE_PROJECT_DIR=str(RAIZ))
            self.assertEqual(r.returncode, 0, f"{c}: {r.stderr}")
        for f, e in (("Bash", {"command": "printf x > .git/forge-suite-verde.123"}), ("Write", {"file_path": k6, "content": "x"}),
                     ("Bash", {"command": "python3 -c \"open('.git/forge-suite-verde','w')\""})):
            r = self.rodar(f, e, cwd=RAIZ, CLAUDE_PROJECT_DIR=str(RAIZ))
            self.assertEqual(r.returncode, 2, f"{e}: {r.stderr}")
            self.assertNotRegex(r.stderr, r"\brm\b|apague", f"{e}: C-4, nunca sugere apagar")

    def test_projeto_recusa_o_literal_pela_marca(self):  # caso 2 do adendo: a precedência da regra da marca
        r = self.rodar("Bash", {"command": "cat .git/forge-suite-verde"})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("marca da sessão", r.stderr)
        r = self.rodar("Bash", {"command": 'cat "$(git rev-parse --git-common-dir)/forge-suite-verde"'})
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_escrita_no_carimbo_recusa(self):
        d, k6 = str(self.d), str(self.proj / ".git" / "forge-suite-verde")
        comum = "import subprocess as s; d=s.check_output(['git','rev-parse','--git-common-dir']).decode().strip(); "
        self.recusa(self.rodar("Write", {"file_path": k6, "content": "x"}), "Write")
        self.recusa(self.rodar("Write", {"file_path": f"{d}/forge-suite-verde.123", "content": "x"}), "temporário")
        self.recusa(self.rodar("Write", {"file_path": f"{d}/forge-suite-verde", "content": "x"}, cwd=self.tmp), "fora de projeto")
        for c in ("printf x > .git/forge-suite-verde.123", "python3 -c \"open('.git/forge-suite-verde','w')\""):
            self.assertEqual(self.rodar("Bash", {"command": c}).returncode, 2, c)  # o literal `.git/forge` já recusa antes
        for c in ('d=$(git rev-parse --git-common-dir); echo x > "$d/forge-suite-verde"', f"echo x > {d}/forge-suite-verde.4294967295",
                  'cd "$(git rev-parse --git-common-dir)" && echo x > forge-suite-verde', f"ln {d}/forge-suite-verde /tmp/h",
                  f"cp -l {d}/forge-suite-verde /tmp/h",
                  f"python3 -c \"{comum}open(d+'/forge-suite-verde','w')\"", f"printf x > {d}/forge-suite-verde.123"):
            r = self.rodar("Bash", {"command": c})
            self.recusa(r, c)
            self.assertIn("scripts/suite-paralela.py", r.stderr, f"{c}: C-4, quem grava o carimbo")
            self.assertNotRegex(r.stderr, r"\brm\b|apague", f"{c}: C-4, nunca sugere apagar")

    def test_curinga_que_casa_a_prova_recusa(self):  # A1 e A2 da segurança g1 da 0.45 (sondas S1 a S4)
        d = str(self.d)
        for k in (self.d / "forge-suite-verde", self.d / "forge-suite-verde.1", self.verde, self.proj / ".git/forge-suite-verde"):
            k.write_text("x", encoding="utf-8")
        for c in (f"echo x > {d}/forge-suite-verd?", f"echo x > {d}/forge-suite-ver*", f"echo x > {d}/forge-suite-verd[e]",
                  f"cp /tmp/x {d}/forge-suite-verd?", f"echo x > {d}/forge-suite-verde.[0-9]", f"ln {d}/forge-suite-verd? /tmp/h",
                  'echo x > "$(git rev-parse --git-common-dir)"/forge-suite-verd?', f"echo x > {d}/forge-suite-1000.ver?e"):
            self.recusa(self.rodar("Bash", {"command": c}), c)
        for c in (f"echo x > {d}/forge-suite-verdX?", f"cat {d}/forge-suite-verd?"):  # curinga que não casa, e leitura
            self.assertEqual(self.rodar("Bash", {"command": c}).returncode, 0, c)

    def test_curinga_no_fallback_fora_de_projeto(self):  # A1 da segurança g1, 4.ª posição: a outra recusa vem antes
        d, fora, outra = str(self.d), self.tmp / "fora", "echo x > ~/.claude/settings.json"
        fora.mkdir()
        (self.d / "forge-suite-verde").write_text("x", encoding="utf-8")
        for c in (f"{outra}; echo x > {d}/forge-suite-verd?", f"{outra}; cp /tmp/x {d}/forge-suite-ver*"):
            self.recusa(self.rodar("Bash", {"command": c}, cwd=fora, CLAUDE_PROJECT_DIR=str(RAIZ)), c)
        c = f"{outra}; echo x > {d}/forge-suite-verdX?"  # curinga que não casa a prova: a outra recusa não vale fora
        self.assertEqual(self.rodar("Bash", {"command": c}, cwd=fora, CLAUDE_PROJECT_DIR=str(RAIZ)).returncode, 0, c)

    def test_curinga_com_substituicao_no_fallback(self):  # A1 da segurança g1, sonda S3 no fallback fora de projeto
        fora, outra, comum = self.tmp / "fora", "echo x > ~/.claude/settings.json", '"$(git rev-parse --git-common-dir)"'
        subprocess.run(["git", "init", "-q", str(fora)], check=True, env=sem_manutencao(self.env()))
        (fora / ".git" / "forge-suite-verde").write_text("x", encoding="utf-8")
        for c in (f"{outra}; echo x > {comum}/forge-suite-verd?", f"{outra}; cp /tmp/x {comum}/forge-suite-ver*"):
            self.recusa(self.rodar("Bash", {"command": c}, cwd=fora, CLAUDE_PROJECT_DIR=str(RAIZ)), c)
        c = f"{outra}; echo x > {comum}/forge-suite-verdX?"  # curinga que não casa a prova passa
        self.assertEqual(self.rodar("Bash", {"command": c}, cwd=fora, CLAUDE_PROJECT_DIR=str(RAIZ)).returncode, 0, c)

    def test_curinga_na_origem_do_link_com_substituicao(self):  # A1 da segurança g1-r2 (S5, S6): o diretório comum
        comum, fora = '"$(git rev-parse --git-common-dir)"', self.tmp / "fora"
        subprocess.run(["git", "init", "-q", str(fora)], check=True, env=sem_manutencao(self.env()))
        for k in (g / ".git" / n for g in (self.proj, fora) for n in ("forge-suite-verde", "forge-suite-verde.1")):
            k.write_text("x", encoding="utf-8")
        for c in (f"ln {comum}/forge-suite-verd? /tmp/h", "ln $(git rev-parse --git-common-dir)/forge-suite-verd? h",
                  f"cp -l {comum}/forge-suite-ver* h", f"ln -s {comum}/forge-suite-verd? h", f"cp -s {comum}/forge-suite-verd? h",
                  'd=$(git rev-parse --git-common-dir); ln "$d"/forge-suite-verd? h', f"cp -l {comum}/forge-suite-verde.[0-9] h"):
            par = c.replace("forge-suite-ver", "forge-suite-Xver")  # o par legítimo: curinga que não casa o carimbo
            for cwd in (self.proj, fora):
                self.recusa(self.rodar("Bash", {"command": c}, cwd=cwd), f"{cwd}: {c}")
                self.assertEqual(self.rodar("Bash", {"command": par}, cwd=cwd).returncode, 0, f"{cwd}: {par}")
        (self.proj / "forge-suite-verde.7").write_text("x", encoding="utf-8")  # o resto depois de `$(…)`, lido da raiz
        c = "ln $(git rev-parse --show-toplevel)/forge-suite-verde.[7] h"
        self.recusa(self.rodar("Bash", {"command": c}), c)

    def test_leitura_gravador_e_vizinhos_passam(self):
        d = str(self.d)
        for c in (f"cat {d}/forge-suite-verde", 'cat "$(git rev-parse --git-common-dir)/forge-suite-verde"',
                  "python3 -m unittest tests.test_suite_reuso",
                  "python3 -I scripts/suite-paralela.py", ".githooks/pre-push --suite", f"echo x > {d}/forge-suite-verdeX",
                  f"echo x > {d}/forge-suite-verde.", f"echo x > {d}/forge-suite-verde.bak", f"echo x > {d}/forge-suite-verde.lock",
                  f"echo x > {d}/forge-suite-verde.12345678901", f"touch {d}/forge-suite-verde.fila/1-5"):
            r = self.rodar("Bash", {"command": c})
            self.assertEqual(r.returncode, 0, f"{c}: {r.stderr}")


def estado_do_git(pasta):
    """O conteúdo de cada arquivo do `.git`, fora de `objects/` (o oráculo do CF1 compara antes e depois do bash)."""
    return {str(p.relative_to(pasta)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pasta.rglob("*"))
            if p.is_file() and "objects" not in p.relative_to(pasta).parts}

class OraculoCf1(unittest.TestCase):
    """CF1 (v047 E2.179, A17 a A19 da segurança E1.344): as fixtures `opaco-cf1-*` do corpus, cada uma com o oráculo pelo
    bash. O hook roda no repositório do caso; depois a mesma linha roda no `bash -c` ali, e o esperado da fixture tem de
    ser 2 se o bash mudou o `.git` (fora de `objects/`), senão 0: o esperado não vem da regra do hook."""

    def rodar_cartao(self, cartao, piso):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "conformidade").glob(f"opaco-cf1-{cartao}-*.json"))],
                          piso, f"opaco-cf1-{cartao}-*")
        self.assertEqual({f.dados["esperado"]["codigo"] for f in fixtures}, {0, 2}, "o corpus tem os dois lados")
        for f in fixtures:
            with self.subTest(caso=f.caminho.stem):
                esperado, obtido, erro, pelo_bash = self.rodar_caso(f)
                self.assertEqual(obtido, esperado["codigo"], f"hook: {erro}")
                self.assertIn(esperado.get("stderr", ""), erro)
                if pelo_bash is not None:  # sem o programa (rsync) na máquina, só o hook
                    self.assertEqual(pelo_bash, esperado["codigo"], "oráculo: o bash discorda da fixture")

    def rodar_caso(self, fixture):
        tmp = Path(tempfile.mkdtemp(prefix="forge-cf1-"))
        try:
            raiz, entrada = fixture.montar(tmp, os.getpid())
            extra = {k: v.replace("{tmp}", str(tmp)) for k, v in fixture.dados["env"].items()}
            r = rodar("conformidade", entrada, raiz, None, extra)
            linha = entrada["tool_input"]["command"]
            if "rsync" in linha and not shutil.which("rsync"):
                return fixture.dados["esperado"], r.returncode, r.stderr, None
            antes = estado_do_git(raiz / ".git")
            env = {**ambiente_limpo(), "HOME": str(tmp), "LC_ALL": "C"}
            subprocess.run(["bash", "--norc", "--noprofile", "-c", linha], cwd=raiz, env=env, capture_output=True,
                           stdin=subprocess.DEVNULL, timeout=30)
            return fixture.dados["esperado"], r.returncode, r.stderr, 2 if estado_do_git(raiz / ".git") != antes else 0
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_redirecao_com_numero(self):  # CONFORMIDADE-REDIRECAO-NUMERO (A17, S52 a S54)
        self.rodar_cartao("redirecao", 13)

    def test_set_posicional(self):  # CONFORMIDADE-SET-POSICIONAL (A18, S55): `$@` e `$*` de `set --`
        self.rodar_cartao("set", 8)

    def test_declare_n(self):  # CONFORMIDADE-DECLARE-N (A19, S56): `declare|typeset|local -n d=_` faz de `$d` o `$_`
        self.rodar_cartao("declare", 10)

    def test_atribuicao_em_linha_ilegivel_nao_vale(self):  # A19: o ramo da linha que o hook não lê, falha fechada
        sys.path.insert(0, str(RAIZ / "hooks"))
        try:
            import conformidade
        finally:
            sys.path.remove(str(RAIZ / "hooks"))
        self.assertTrue(conformidade.atribui_como_argumento("d", "d=x; echo 'aberto"))
        self.assertFalse(conformidade.atribui_como_argumento("d", "d=x; echo fechado"))

    def test_numero_antes_do_git_nao_o_esconde(self):  # A17: `2>/dev/null git push --force`
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "conformidade").glob("trava-cf1-*.json"))], 1,
                          "trava-cf1-*")
        for f in fixtures:
            with self.subTest(caso=f.caminho.stem):
                tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="forge-cf1-")))
                raiz, entrada = f.montar(tmp, os.getpid())
                r = rodar("conformidade", entrada, raiz, None,
                          {k: v.replace("{tmp}", str(tmp)) for k, v in f.dados["env"].items()})
                self.assertEqual(r.returncode, f.dados["esperado"]["codigo"], r.stderr)
                self.assertIn(f.dados["esperado"]["stderr"], r.stderr)


# AGENTES-JSON-SEM-GUARDA (v0478 E1.1; C9 e C10 de docs/security/v047-v2-ameacas.md, seção 2): no clone do Forge, o
# papel sem lista de permissão passava só pela `GuardaDaProva`, e o estado do hook `agentes` (`<diretório comum>/forge/run/`)
# ficava sem guarda. A recusa da política `.git/forge/` passa a valer ali para todo papel, o jarvis incluído; o resto do clone
# segue livre. Fixture própria: clone temporário com o manifesto do Forge, sem tocar o `.git` real.
HOOKS_DO_CLONE = Path(__file__).resolve().parent.parent / "hooks"
LANCADOR_DO_CLONE = "import runpy, sys; sys.path.insert(0, sys.argv[1]); sys.argv = sys.argv[2:]; runpy.run_path(sys.argv[0], run_name='__main__')"
PAPEIS_DO_CLONE = ("forge:tech-lead", "forge:security-engineer", "forge:qa-engineer", "forge:devops-engineer", "forge:jarvis", None)


class CloneDoForge(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-estado-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.clone = self.tmp / "clone"
        (self.clone / ".claude-plugin").mkdir(parents=True)
        (self.clone / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n', encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.clone)], check=True, env=self.env(), capture_output=True, timeout=60)
        self.run = self.clone / ".git" / "forge" / "run"
        self.run.mkdir(parents=True)
        self.estado = self.run / "agentes.json"
        self.estado.write_text('{"agentes": []}', encoding="utf-8")

    def env(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_")) and k != "CLAUDE_PROJECT_DIR"}
        return sem_manutencao({**env, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})

    def rodar(self, ferramenta, entrada, papel="forge:tech-lead", cwd=None):
        dados = {"tool_name": ferramenta, "tool_input": entrada, "hook_event_name": "PreToolUse", "agent_type": papel}
        return subprocess.run([sys.executable, "-I", "-c", LANCADOR_DO_CLONE, str(HOOKS_DO_CLONE), str(HOOKS_DO_CLONE / "conformidade.py")],
                              input=json.dumps(dados), cwd=cwd or self.clone, capture_output=True, text=True, timeout=120,
                              env={**self.env(), "CLAUDE_PROJECT_DIR": str(self.clone)})

    def recusa(self, r, caso):
        self.assertEqual(r.returncode, 2, f"{caso}: {r.stderr}")
        self.assertIn("R-CONFORMIDADE", r.stderr, caso)

    def libera(self, r, caso):
        self.assertEqual(r.returncode, 0, f"{caso}: {r.stderr}")


class EstadoDoAgentesNoClone(CloneDoForge):
    def test_escrita_remocao_e_link_no_estado_recusam_para_todo_papel(self):  # J1 a J15 (C9)
        absoluto = str(self.estado)
        comandos = ("echo '{}' > .git/forge/run/agentes.json", "rm .git/forge/run/agentes.json", "rm -rf .git/forge",
                    "mv .git/forge/run /tmp/r", "python3 -c \"open('.git/forge/run/agentes.json','w')\"",
                    "cd .git/forge/run && : > agentes.json", "ln .git/forge/run/agentes.json h",
                    "ln -sf /dev/null .git/forge/run/agentes.json", "truncate -s0 .git/forge/run/agentes.json",
                    "d=.git/forge/run; echo x > $d/agentes.json", f"echo x > {absoluto}",
                    "echo a >> .git/forge/run/autoria.jsonl", "rm -rf .git", "chmod 000 .git/forge/run/agentes.json")
        for papel in PAPEIS_DO_CLONE:  # a lista inteira para o tech-lead e o jarvis; para os outros, escrita e remoção
            for c in comandos if papel in ("forge:tech-lead", "forge:jarvis") else comandos[:2]:
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
            self.recusa(self.rodar("Write", {"file_path": absoluto, "content": "{}"}, papel), f"{papel}: Write")
            self.recusa(self.rodar("Edit", {"file_path": absoluto, "old_string": "[]", "new_string": "[1]"}, papel),
                        f"{papel}: Edit")
        self.assertEqual(self.estado.read_text(encoding="utf-8"), '{"agentes": []}')

    def test_comando_que_escreve_ou_remove_por_opcao_recusa(self):  # A2 da segurança (v0478): S4 a S8
        (self.clone / "docs").mkdir()
        comandos = ("find .git/forge -delete", "find .git -name agentes.json -delete", "find -L .git/forge/run -delete",
                    "find docs -exec rm .git/forge/run/agentes.json \\;", "find .git/forge/run -exec rm {} +",
                    "find docs -fprint .git/forge/run/agentes.json", "tar -xf docs/a.tar -C .git/forge/run",
                    "tar --extract --file docs/a.tar --directory=.git", "tar --extract --file docs/a.tar --directory .git/forge",
                    "cd .git/forge/run && tar xf ../../../docs/a.tar",
                    "tar -cf .git/forge/run/agentes.json docs", "chmod 000 .git/forge/run/agentes.json",
                    "chmod -R 000 .git/forge", "chown nobody .git/forge/run/agentes.json", "chattr +i .git/forge/run",
                    "cd .git/forge/run && find -delete", "tar --extr --fi docs/a.tar --dir .git/forge")
        for papel in ("forge:tech-lead", "forge:jarvis"):
            for c in comandos:
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
        self.assertEqual(self.estado.read_text(encoding="utf-8"), '{"agentes": []}')

    def test_extrator_e_tar_por_opcao_recusam(self):  # volta 2: A2 e A4 da segurança (S10 a S13), A1 do review (S1, S2)
        (self.clone / "docs").mkdir()
        rm = "'rm .git/forge/run/agentes.json'"
        sondas = ("unzip -o docs/a.zip -d .git/forge/run", "cd .git/forge/run && cpio -idm < ../../../docs/a.cpio",
                  f"tar --to-command={rm} -xf docs/a.tar", f"tar -xf docs/a.tar --checkpoint=1 --checkpoint-action=exec={rm}",
                  "tar -xf docs/a.tar -C.git/forge/run", "tar -cf.git/forge/run/agentes.json docs",
                  "bsdtar -xf docs/a.tar -C .git/forge/run", "busybox tar -xf docs/a.tar -C .git/forge/run",
                  "7z x docs/a.7z -o.git/forge/run")
        vizinhas = ("tar -xvzfdocs/a.tar -C.git/forge", f"tar --checkpoint-action exec={rm} -xf docs/a.tar",
                    f"tar --checkpoint --checkpoint-act=exec={rm} -xf docs/a.tar -C docs",
                    f"tar --use-compress-program={rm} -xf docs/a.tar -C docs", f"tar -I {rm} -xf docs/a.tar -C docs",
                    "tar -xIrm\\ .git/forge/run/agentes.json -f docs/a.tar -C docs", f"tar --to-com {rm} -xf docs/a.tar -C docs",
                    f"tar -F {rm} -xf docs/a.tar -C docs", "tar -cf docs/a.tar --remove-files .git/forge/run/agentes.json",
                    "tar -C .git/forge -cf docs/a.tar --remove-files run/agentes.json",
                    "tar -cf docs/a.tar -g .git/forge/run/agentes.json docs", "tar xfC docs/a.tar .git/forge",
                    "cpio -p .git/forge/run < docs/l", "cpio -iD.git/forge/run < docs/a.cpio",
                    "cpio --extract --directory=.git/forge < docs/a.cpio", "cpio -o -O .git/forge/run/agentes.json < docs/l",
                    "cpio -o -F .git/forge/run/agentes.json < docs/l", f"cpio -i --rsh-command={rm} < docs/a.cpio",
                    "unzip -d.git/forge/run docs/a.zip", "unzip data -d .git/forge/run",
                    "cd .git/forge/run && unzip ../../../docs/a.zip", "7z e docs/a.7z -o.git/forge/run",
                    "7z a .git/forge/run/agentes.json docs", "7z a docs/a.7z .git/forge/run/agentes.json -sdel",
                    "7za x docs/a.7z -o.git/forge", "/usr/bin/gtar -xf docs/a.tar -C .git/forge",
                    "busybox rm .git/forge/run/agentes.json", "busybox unzip docs/a.zip -d .git/forge/run",
                    "tar --checkpoint -xf docs/a.tar -C .git/forge", "tar -xf docs/a.tar -Cdocs/b -C .git/forge",
                    "7z -y a .git/forge/run/agentes.json docs", "cd .git/forge/run && 7z x ../../../docs/a.7z")
        for papel in ("forge:tech-lead", "forge:jarvis"):
            for c in sondas + (vizinhas if papel == "forge:jarvis" else ()):
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
        self.assertEqual(self.estado.read_text(encoding="utf-8"), '{"agentes": []}')

    def test_opcoes_do_catalogo_recusam(self):  # volta 3 (E1.13): review A1 (S3, S4) e segurança A5 (S15)
        (self.clone / "docs").mkdir()
        sondas = ("tar -xf docs/a.tar --one-top-level=.git/forge/run",  # S3
                  "tar -xf docs/a.tar -C docs --one-top-level=../.git/forge",  # S4: relativo ao -C
                  "7z x docs/a.7z -O.git/forge/run", "7z a docs/a.7z .git/forge/run/agentes.json -SDEL",  # S15
                  "bsdtar -xf docs/a.tar --cd .git/forge/run", "toybox tar -xf docs/a.tar -C .git/forge/run")
        vizinhas = ("tar -xf docs/a.tar --one=.git/forge", "tar xf docs/a.tar --one-top-level=.git/forge",
                    "tar -xf docs/a.tar --transform 's,^,.git/forge/run/,'", "tar -xf docs/a.tar --xform=s,.*,.git/forge/&,",
                    "tar -xf docs/a.tar -C docs --transform='s|^|../.git/forge/|'",
                    "tar -cf docs/a.tar --volno-file=.git/forge/run/agentes.json docs",
                    "tar -cf docs/a.tar --index-file .git/forge/run/agentes.json docs",
                    "bsdtar -xf docs/a.tar -s ',^,.git/forge/run/,'", "bsdtar -x -f docs/a.tar --directory=.git/forge",
                    "7z e docs/a.7z -O.git/forge", "7z x docs/a.7z -o.git/forge/run -y",
                    "7z u docs/a.7z docs -up0q0!.git/forge/run/agentes.json", "7z a docs/a.7z docs -w.git/forge/run",
                    "7z a docs/a.7z -sDeL -- .git/forge/run/agentes.json", "toybox cpio -idD.git/forge < docs/a.cpio",
                    "busybox tar -xf docs/a.tar --one-top-level=.git/forge")
        for papel in ("forge:tech-lead", "forge:jarvis"):
            for c in sondas + (vizinhas if papel == "forge:jarvis" else ()):
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
        self.assertEqual(self.estado.read_text(encoding="utf-8"), '{"agentes": []}')

    def test_opcoes_do_catalogo_fora_do_estado_seguem_livres(self):  # volta 3: o legítimo de cada opção nova
        (self.clone / "docs").mkdir()
        for c in ("tar -xf docs/a.tar --one-top-level=docs/b", "tar -xf docs/a.tar --one-top-level",
                  "tar -xf docs/a.tar -C docs --one-top-level=b", "tar -xf docs/a.tar --transform 's,^,docs/b/,'",
                  "tar -xf docs/a.tar --xform=s/a/b/", "tar -cf docs/a.tar --transform 's,^,.git/forge/,' docs",
                  "tar -cf docs/a.tar --volno-file=docs/v docs", "tar -cf docs/a.tar -T docs/l",
                  "tar -cf docs/a.tar --exclude .git/forge .", "tar -cf docs/a.tar --exclude-from docs/x docs",
                  "tar -czf docs/a.tgz --remove-files docs/x", "tar -tf .git/forge/a.tar --one-top-level=.git/forge",
                  "7z x docs/a.7z -Odocs", "7z a docs/a.7z docs/x -SDEL", "7z u docs/a.7z docs -up0q0!docs/n.7z",
                  "7z u docs/a.7z docs -up0q0", "7z a docs/a.7z docs -wdocs", "7z a docs/a.7z docs -w",
                  "7z l .git/forge/a.7z -O.git/forge", "bsdtar -xf docs/a.tar --cd docs", "bsdtar -xf docs/a.tar -s ',^,docs/b/,'",
                  "bsdtar -tf .git/forge/a.tar", "toybox tar -xf docs/a.tar -C docs", "toybox ls .git/forge", "toybox --help"):
            self.libera(self.rodar("Bash", {"command": c}), c)

    def test_find_tar_e_chmod_fora_do_estado_seguem_livres(self):  # o ato por opção só conta no alvo; a raiz, como no `rm`, fica de fora
        (self.clone / "docs").mkdir()
        for c in ("find . -name '*.py'", "find docs -name x -delete", "find . -name x -exec grep y {} +",
                  "find .git/forge -name '*.json'", "tar -xf docs/a.tar -C docs", "tar -tf docs/a.tar",
                  "tar -cf docs/a.tar .git/forge", "tar -xf .git/forge/a.tar -C docs", "tar -tf docs/a.tar -- .git/forge",
                  "tar -cf docs/a.tar -C .git/forge run", "chmod +x docs/a.sh", "find . -name x -delete",
                  "tar --checkpoint -xf docs/a.tar -C docs", "tar --to-command=cat -xf docs/a.tar -C docs",
                  "tar -czf docs/a.tgz --remove-files docs/x", "unzip docs/a.zip -d docs", "cd docs && unzip a.zip",
                  "cd docs && cpio -id < a.cpio", "cpio -o < docs/l > docs/a.cpio", "7z x docs/a.7z -odocs",
                  "7z l .git/forge/a.7z", "7z a docs/a.7z .git/forge", "busybox ls .git/forge", "busybox --list",
                  "tar -xf docs/a.tar -C docs -- -C.git/forge", "cd .git/forge/run && cpio -o < ../../../docs/l > ../../../docs/a.cpio"):
            self.libera(self.rodar("Bash", {"command": c}), c)

    def test_de_fora_do_clone_pelo_caminho_absoluto_recusa(self):  # J12: pasta corrente fora do clone
        fora = self.tmp / "fora"
        fora.mkdir()
        self.recusa(self.rodar("Bash", {"command": f"rm {self.estado}"}, cwd=fora), "rm de fora")

    def test_linha_que_o_hook_nao_le_e_cita_o_estado_recusa(self):  # J16, C10: o recuo de falha fechada
        teto = ": " + "a " * 5001 + "; echo x > .git/forge/run/agentes.json"  # acima do teto de palavras: sem leitura
        for c in ("echo x > .git/forge/run/agentes.json (true)#'", "echo x > .git/forge/run/agentes.json \\", teto):
            self.recusa(self.rodar("Bash", {"command": c}), c[:60])

    def test_prova_da_suite_na_linha_que_o_hook_nao_le_segue_com_a_recusa_propria(self):
        # `.git/forge-suite-verde` não é o estado: a recusa é a da prova (R-VERIFY), não a do estado dos hooks.
        for c in ("echo x > .git/forge-suite-verde; git push \\", "echo x > .git/forge-suite-verde (true)#'"):
            r = self.rodar("Bash", {"command": c})
            self.assertEqual(r.returncode, 2, f"{c}: {r.stderr}")
            self.assertIn("R-VERIFY: a prova da suíte só é gravada pelo pre-push", r.stderr, c)

    def test_leitura_e_resto_do_clone_seguem_livres(self):  # legítimos do modelo de ameaças
        for c in ("cat .git/forge/run/agentes.json", "ls .git/forge/run", "git status", "cp a docs/a.md",
                  "echo x > docs/a.md \\"):
            self.libera(self.rodar("Bash", {"command": c}), c)
        self.libera(self.rodar("Write", {"file_path": str(self.clone / "docs" / "a.md"), "content": "x"}), "Write em docs")
        c = "d=.claude/x; echo x > $d/a"  # o que o hook não modela só vale se a linha cita o estado
        self.libera(self.rodar("Bash", {"command": c}), c)

    def test_fora_do_clone_do_forge_a_guarda_nao_se_estende(self):  # outro repositório, sem o manifesto do Forge
        (self.clone / ".claude-plugin" / "plugin.json").unlink()
        for c in ("rm .git/forge/run/agentes.json", "echo x > .git/forge/run/agentes.json \\"):
            self.libera(self.rodar("Bash", {"command": c}), c)


class CatalogoDosDestinos(unittest.TestCase):
    """Volta 3 (E1.13): o catálogo `DESTINOS` do hook declara, por programa, as opções que escolhem a pasta de destino ou o
    arquivo gravado; a do tar é conferida contra o `tar --help` da máquina (GNU tar), nos dois sentidos."""

    METAVARS = ("FILE", "DIR", "ARCHIVE", "DATE-OR-FILE")  # o valor da opção é um caminho

    def ajuda_do_tar(self):
        tar = shutil.which("tar")
        ajuda = subprocess.run([tar, "--help"], capture_output=True, text=True, timeout=60,
                               env={"PATH": os.environ.get("PATH", ""), "LC_ALL": "C"}).stdout if tar else ""
        if "GNU" not in ajuda:  # um pulo só, com o motivo (a catraca conta cada pulo)
            self.skipTest("sem o GNU tar no PATH: o catálogo do tar é o da ajuda do GNU e não tem com o que ser conferido")
        return ajuda

    def catalogo(self, programa):
        codigo = ("import json, sys; sys.path.insert(0, sys.argv[1]); import conformidade as c; "
                  "print(json.dumps(c.DESTINOS[sys.argv[2]]._asdict()))")
        r = subprocess.run([sys.executable, "-I", "-c", codigo, str(HOOKS_DO_CLONE), programa], capture_output=True,
                           text=True, timeout=60, env={"PATH": os.environ.get("PATH", "")})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_toda_opcao_de_caminho_da_ajuda_do_tar_esta_no_catalogo(self):
        ajuda, cat = self.ajuda_do_tar(), self.catalogo("tar")
        declaradas = {n for campo in cat.values() for n in campo} | {"info-script", "new-volume-script", "F"}  # executam
        com_caminho = set()
        for linha in ajuda.splitlines():
            curta = re.match(r"\s+-(\w), --", linha)
            for longa, meta in re.findall(r"--([a-z-]+)\[?=([A-Z-]+)", linha):
                if meta in self.METAVARS:
                    com_caminho |= {longa, curta.group(1)} if curta else {longa}
        self.assertGreaterEqual(len(com_caminho), 20, "a leitura da ajuda achou poucas opções de caminho")
        self.assertEqual(com_caminho - declaradas, set(), "opção da ajuda que lê ou grava caminho fora do catálogo")
        self.assertIn("one-top-level", com_caminho)  # o review A1: `[=DIR]` opcional também é pasta

    def test_toda_opcao_do_catalogo_do_tar_existe_na_ajuda(self):
        ajuda, cat = self.ajuda_do_tar(), self.catalogo("tar")
        longas = set(re.findall(r"--([a-z-]+)", ajuda))
        curtas = set(re.findall(r"^\s+-(\w), --", ajuda, re.M))
        nomes = [n for campo in cat.values() for n in campo]
        self.assertGreaterEqual(len(nomes), 25)
        self.assertEqual([n for n in nomes if n not in (curtas if len(n) == 1 else longas)], [])

    def test_one_top_level_do_gnu_tar_extrai_na_pasta_dada(self):  # S5: a razão de a opção estar em `subpasta`
        self.ajuda_do_tar()
        tmp = Path(tempfile.mkdtemp(prefix="forge-tar-")).resolve()
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "src").mkdir()
        (tmp / "src" / "f").write_text("x", encoding="utf-8")
        env = {"PATH": os.environ.get("PATH", ""), "LC_ALL": "C"}
        for c in (["tar", "-cf", "a.tar", "src"], ["tar", "-xf", "a.tar", "--one-top-level=dst/alvo"]):
            subprocess.run(c, cwd=tmp, check=True, capture_output=True, timeout=60, env=env)
        self.assertTrue((tmp / "dst" / "alvo" / "src" / "f").is_file())


class ConfigDoTetoNoClone(CloneDoForge):
    """CONFIG-TETO-SEM-GUARDA, parte do hook (v0478 E1.1): no clone, `teto_agentes` em `.forge/config.json` da raiz da sessão
    (o que o hook `agentes` lê) subia o próprio teto com rc 0. A recusa da política vale para todo papel; o modelo
    `templates/projeto/.forge/config.json` e o de outra pasta seguem livres."""

    def setUp(self):
        super().setUp()
        (self.clone / ".forge").mkdir()
        self.config = self.clone / ".forge" / "config.json"
        self.config.write_text('{"teto_agentes": 2}\n', encoding="utf-8")

    def test_escrita_no_config_da_raiz_recusa_para_todo_papel(self):
        comandos = ("echo '{\"teto_agentes\": 99}' > .forge/config.json", "rm -rf .forge",
                    "python3 -c \"open('.forge/config.json','w').write('{}')\"", f"sed -i s/2/99/ {self.config}")
        for papel in PAPEIS_DO_CLONE:
            for c in comandos if papel in ("forge:tech-lead", "forge:jarvis") else comandos[:1]:
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
            self.recusa(self.rodar("Write", {"file_path": str(self.config), "content": '{"teto_agentes": 99}'}, papel),
                        f"{papel}: Write")
            self.recusa(self.rodar("Edit", {"file_path": str(self.config), "old_string": "2", "new_string": "99"}, papel),
                        f"{papel}: Edit")
        self.assertEqual(self.config.read_text(encoding="utf-8"), '{"teto_agentes": 2}\n')

    def test_find_tar_e_chmod_no_config_da_raiz_recusam(self):  # A2 da segurança (v0478): S7
        for c in ("find .forge -delete", "tar -xf docs/a.tar -C .forge", "chmod 000 .forge/config.json"):
            for papel in ("forge:tech-lead", "forge:jarvis"):
                self.recusa(self.rodar("Bash", {"command": c}, papel), f"{papel}: {c}")
        r = self.rodar("Bash", {"command": "tar -xf docs/a.tar -C .forge"})
        self.assertIn("extrair em .forge/ alcança .forge/config.json", r.stderr)  # o ato certo, não "apagar"

    def test_linha_que_o_hook_nao_le_e_cita_o_config_recusa(self):  # C10 estendido ao config da raiz
        c = ": " + "a " * 5001 + "; echo '{}' > .forge/config.json"
        self.recusa(self.rodar("Bash", {"command": c}), "teto de palavras com o config")

    def test_modelo_e_config_de_outra_pasta_seguem_livres(self):
        modelo = self.clone / "templates" / "projeto" / ".forge" / "config.json"
        outro = self.tmp / "outro" / ".forge" / "config.json"
        for alvo in (modelo, outro):
            self.libera(self.rodar("Write", {"file_path": str(alvo), "content": "{}"}), str(alvo))
            self.libera(self.rodar("Bash", {"command": f"echo '{{}}' > {alvo}"}), f"echo em {alvo}")
        self.libera(self.rodar("Bash", {"command": "cat .forge/config.json"}), "leitura")


class ConfigDaWorktreeNoClone(CloneDoForge):
    """A1 da segurança (v0478, S1 a S3): o hook `agentes` lia o `.forge/config.json` da cópia da pasta corrente, e a
    worktree do clone (sem guarda) subia o teto. No clone, o hook lê o da raiz da sessão, o mesmo que a conformidade guarda."""
    LEITOR = ("import sys; sys.path.insert(0, sys.argv[1]); import agentes; from _comum import Hook; h = Hook('agentes'); "
              "h.projeto(sys.argv[2], clone_do_forge=True); c = agentes.ler_config(h); "
              "print(c['teto_agentes'], c['piso_memoria_gb'], agentes.ritmo_do_projeto(agentes.pasta_da_config(h)), "
              "agentes.Maquina(h, 0).peso, h.config()['teto_agentes'], h.config()['piso_memoria_gb'])")

    def setUp(self):
        super().setUp()
        (self.clone / ".forge").mkdir()
        (self.clone / ".forge" / "config.json").write_text('{"teto_agentes": 2}\n', encoding="utf-8")
        git = ["git", "-C", str(self.clone), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run([*git, "add", ".claude-plugin"], check=True, env=self.env(), capture_output=True, timeout=60)
        subprocess.run([*git, "commit", "-qm", "x"], check=True, env=self.env(), capture_output=True, timeout=60)
        self.wt = self.tmp / "wt"
        subprocess.run([*git, "worktree", "add", "-q", str(self.wt)], check=True, env=self.env(), capture_output=True, timeout=60)
        (self.wt / ".forge").mkdir()
        (self.wt / ".forge" / "config.json").write_text(
            '{"teto_agentes": 99, "piso_memoria_gb": 0.1, "ritmo": "acelerado", "peso": 10}\n', encoding="utf-8")

    def ler(self, sessao):
        r = subprocess.run([sys.executable, "-I", "-c", self.LEITOR, str(HOOKS_DO_CLONE), str(self.wt)], cwd=self.wt,
                           capture_output=True, text=True, timeout=60, env={**self.env(), "CLAUDE_PROJECT_DIR": str(sessao)})
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.split()

    def test_teto_da_worktree_nao_vale_com_a_sessao_no_clone(self):
        self.assertEqual(self.ler(self.clone), ["2", "2.0", "equilibrado", "1.0", "2", "2.0"])

    def test_versao_na_worktree_nao_deixa_o_config_dela_no_cache(self):  # S9 (volta 2): `.forge/versao` na worktree faz o
        # `hook.projeto` ler o config dela (o `hooks_desligados`); o cache não vence o da raiz da sessão no teto nem no piso
        (self.wt / ".forge" / "versao").write_text("1\n", encoding="utf-8")
        self.assertEqual(self.ler(self.clone), ["2", "2.0", "equilibrado", "1.0", "2", "2.0"])

    def test_sessao_na_worktree_le_o_config_dela(self):  # a raiz da sessão é a worktree: a conformidade guarda esse
        self.assertEqual(self.ler(self.wt), ["99", "0.1", "acelerado", "10.0", "99", "0.1"])

    def test_escrita_no_config_da_worktree_com_a_sessao_nela_recusa(self):
        c = "echo '{\"teto_agentes\": 99}' > .forge/config.json"
        dados = {"tool_name": "Bash", "tool_input": {"command": c}, "hook_event_name": "PreToolUse", "agent_type": "forge:tech-lead"}
        r = subprocess.run([sys.executable, "-I", "-c", LANCADOR_DO_CLONE, str(HOOKS_DO_CLONE), str(HOOKS_DO_CLONE / "conformidade.py")],
                           input=json.dumps(dados), cwd=self.wt, capture_output=True, text=True, timeout=120,
                           env={**self.env(), "CLAUDE_PROJECT_DIR": str(self.wt)})
        self.recusa(r, c)

    def test_sessao_e_pasta_corrente_na_mesma_raiz_nao_consultam_o_clone(self):
        # C7 (HOOK-ERRO-LIBERA): o erro de `e_clone_do_forge` fica com quem fixa o estado, depois do R-BRIEF; a leitura do
        # config com a mesma raiz não o antecipa como "configuração ilegível".
        codigo = ("import sys; sys.path.insert(0, sys.argv[1]); import agentes; from _comum import Hook\n"
                  "def erro(_):\n    raise OSError('erro forcado')\n"
                  "agentes.e_clone_do_forge = erro; h = Hook('agentes'); h.raiz = sys.argv[2]; print(agentes.pasta_da_config(h))")
        r = subprocess.run([sys.executable, "-I", "-c", codigo, str(HOOKS_DO_CLONE), str(self.wt)], cwd=self.wt,
                           capture_output=True, text=True, timeout=60, env={**self.env(), "CLAUDE_PROJECT_DIR": str(self.wt)})
        self.assertEqual((r.returncode, r.stdout.strip()), (0, str(self.wt)), r.stderr)


# A6 da segurança (v0478, E1.18): o `busybox` (e o `toybox`) trocado pelo applet não perde a varredura de `forge atualizar`
# que o `busybox` tinha em ENVOLVEDORES. Applets que rodam outro programa; `{c}` é a carga recusada.
APPLETS_QUE_RODAM_PROGRAMA = (
    "chroot / {c}", "nsenter -t 1 {c}", "setarch x86_64 {c}", "linux32 {c}", "linux64 {c}", "chpst -u x {c}",
    "su -c '{c}'", "watch {c}", "start-stop-daemon -S -x {c}", "ssd -S -x {c}", "run-parts {c}", "setuidgid x {c}",
    "envdir d {c}", "envuidgid x {c}", "softlimit -m 1 {c}", "cttyhack {c}", "runuser -u x {c}", "ash -c '{c}'",
    "hush -c '{c}'", "toybox {c}", "tclsh {c}", "awk -f x {c}", "inotifyd {c} d", "tcpsvd 0 1 {c}", "udpsvd 0 1 {c}",
    "nc -e {c}", "ftpd {c}", "httpd {c}", "crond {c}", "sv {c}", "runsv {c}", "runsvdir {c}", "sh -c {c}", "bash -c {c}",
    "env {c}", "nice {c}", "nohup {c}", "timeout 1 {c}", "setsid {c}", "time {c}", "xargs {c}", "taskset 1 {c}",
    "flock l {c}", "unshare {c}", "ionice {c}", "chrt 1 {c}", "script -c '{c}'", "exec {c}", "stdbuf -o0 {c}",
    "sh -c '{c}'", "bash -c '{c}'", "ash -c {c}", "su -s /bin/sh -c '{c}'", "sudo {c}")
CARGAS_DE_ATUALIZACAO = ("forge-atualizar", "forge atualizar", "forge voltar-versao 0.1.0")


class AtualizacaoAtrasDoBusybox(CloneDoForge):
    def rodar_em(self, raiz, c, papel):
        dados = {"tool_name": "Bash", "tool_input": {"command": c}, "hook_event_name": "PreToolUse", "agent_type": papel}
        return subprocess.run([sys.executable, "-I", "-c", LANCADOR_DO_CLONE, str(HOOKS_DO_CLONE), str(HOOKS_DO_CLONE / "conformidade.py")],
                              input=json.dumps(dados), cwd=raiz, capture_output=True, text=True, timeout=120,
                              env={**self.env(), "CLAUDE_PROJECT_DIR": str(raiz)})

    def projeto(self):
        proj = self.tmp / "proj"
        (proj / ".forge").mkdir(parents=True)
        (proj / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(proj)], check=True, env=self.env(), capture_output=True, timeout=60)
        return proj

    def test_applet_que_roda_programa_nao_esconde_a_atualizacao(self):  # S19: rc 2 como na origin/develop
        self.assertGreaterEqual(len(APPLETS_QUE_RODAM_PROGRAMA), 54)
        prefixos = ("busybox", "/bin/busybox", "toybox")
        casos = [(prefixos[i % 3], a.format(c=CARGAS_DE_ATUALIZACAO[i % 3])) for i, a in enumerate(APPLETS_QUE_RODAM_PROGRAMA)]
        proj = self.projeto()  # no clone do Forge a atualização não é recusada nem direta: a guarda é do projeto
        for papel in ("forge:tech-lead", "forge:qa-engineer"):
            for prefixo, applet in casos:
                c = f"{prefixo} {applet}"
                r = self.rodar_em(proj, c, papel)
                self.recusa(r, f"{papel}: {c}")
                self.assertRegex(r.stderr, "troca o plugin", c)

    def test_applet_sem_atualizacao_segue_livre(self):  # o legítimo atrás do busybox continua passando
        proj = self.projeto()
        for c in ("busybox ls docs", "busybox chroot / ls", "toybox watch date", "busybox env ls", "busybox --list"):
            self.libera(self.rodar_em(proj, c, "forge:tech-lead"), c)


class TrocaDeBranchAtrasDoBusybox(CloneDoForge):  # A8 da segurança (S21): nem busybox nem toybox têm applet git
    rodar_em = AtualizacaoAtrasDoBusybox.rodar_em
    ACOES_NA_MAIN = ("git push", "git commit -m x", "git merge develop", "git rebase develop", "git reset --hard HEAD~1",
                     "git cherry-pick abc123", "git revert HEAD")

    def projeto_na_main(self):
        proj = self.tmp / "proj"
        (proj / ".forge").mkdir(parents=True)
        (proj / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        for args in (["init", "-q", "-b", "main"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x"]):
            subprocess.run(["git", "-C", str(proj), *args], check=True, env=self.env(), capture_output=True, timeout=60)
        return proj

    def test_troca_pelo_applet_nao_libera_a_main(self):
        proj = self.projeto_na_main()
        for troca in ("busybox git switch -c feature/x", "toybox git checkout -b feature/x", "/bin/busybox git switch -c feature/x"):
            for op in (";", "||", "&&"):
                for acao in self.ACOES_NA_MAIN:
                    c = f"{troca} {op} {acao}"
                    r = self.rodar_em(proj, c, "forge:tech-lead")
                    self.assertEqual(r.returncode, 2, f"{c}: {r.stderr}")

    def test_troca_direta_segue_registrada(self):  # contraprova: sem applet, a troca vale para o comando seguinte
        proj = self.projeto_na_main()
        for op in (";", "&&"):
            c = f"git switch -c feature/x {op} git commit -m x"
            self.libera(self.rodar_em(proj, c, "forge:tech-lead"), c)
