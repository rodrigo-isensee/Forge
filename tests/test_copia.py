"""Hook `copia` (HOOK-AGENTE-FORA-DA-PROPRIA-COPIA, R-CONFORMIDADE): o agente do time grava e roda git de escrita só na
própria cópia. As fixtures de tests/hooks/copia/ rodam o script pelo executor de tests/test_hooks.py; o resto lê as funções
do hook no processo, com pastas temporárias e o `~` trocado pelo `HOME`."""
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_hooks  # noqa: E402
from test_forge import RAIZ, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

sys.path.insert(0, str(RAIZ / "hooks"))
import copia  # noqa: E402

FORA_DO_TMP = "/var/forge-copia-home"  # HOME que não fica em pasta temporária (só o caminho; nada se grava nele)


def repositorio(pasta, branch):
    pasta.mkdir(parents=True)
    git("init", "-q", "-b", branch, cwd=pasta)
    git("config", "user.email", "t@example.com", cwd=pasta)
    git("config", "user.name", "Teste", cwd=pasta)
    (pasta / "README.md").write_text("x\n", encoding="utf-8")
    git("add", "-A", cwd=pasta)
    git("commit", "-q", "-m", "base", cwd=pasta)
    return pasta


class FixturesDaCopia(unittest.TestCase):
    """As fixtures de tests/hooks/copia/ pelo executor de tests/test_hooks.py (o mesmo código, sem as outras pastas)."""
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_fixtures(self):
        casos = [(f"copia/{p.stem}", test_hooks.Fixture(p)) for p in sorted((test_hooks.FIXTURES / "copia").glob("*.json"))]
        self.assertGreaterEqual(len(casos), 18)
        self.assertGreaterEqual(sum(f.dados["esperado"]["codigo"] == 2 for _, f in casos), 8, "fixtures de recusa")
        self.assertEqual(self.executar_em_lote(casos), len(casos))


class Leitura(unittest.TestCase):
    """Os alvos de escrita que o hook lê na linha e nas ferramentas."""

    def test_resolver(self):
        self.assertEqual(copia.resolver("b/c", "/a"), "/a/b/c")
        self.assertIsNone(copia.resolver("b", None), "pasta incerta")
        self.assertIsNone(copia.resolver("$FORGE_COPIA_NAO_EXISTE/a", "/a"), "variável que sobra")
        self.assertIsNone(copia.resolver("`pwd`/a", "/a"), "substituição")

    def test_redirecao_cd_e_git(self):
        segmento = copia.alvos_do_segmento
        self.assertEqual(segmento(["echo", "x", ">", "f"], "/a"), (["/a/f"], "/a"))
        self.assertEqual(segmento(["cd", "b"], "/a"), ([], "/a/b"))
        self.assertEqual(segmento(["git", "commit", "-m", "x"], "/a"), (["/a"], "/a"))
        self.assertEqual(segmento(["git", "log"], "/a"), ([None], "/a"), "leitura não é alvo")
        self.assertEqual(segmento(["git", "-c", "x=1", "-C", "b", "commit"], "/a"), (["/a/b"], "/a"), "valor do -c não é subcomando")
        self.assertEqual(segmento(["git", "commit", "-C", "HEAD"], "/a"), (["/a"], "/a"), "-C depois do subcomando é dele")

    def test_linha_inteira(self):
        bash = copia.alvos_do_bash
        self.assertEqual(bash("echo a; git commit -m x", "/a"), ["/a"])
        self.assertEqual(bash("cd /b && git push origin x\ngit log > /c/l", "/a"), ["/b", "/c/l"])
        self.assertEqual(bash("cd $FORGE_COPIA_NAO_EXISTE && git commit", "/a"), [], "pasta incerta fica de fora")
        self.assertEqual(bash("git commit -m \"$(cat <<'EOF'\nx > /etc/a\nEOF\n)\"", "/a"), ["/a"], "corpo do heredoc não conta")
        self.assertEqual(bash("echo x > f 'sem par", "/a"), ["/a/f"], "aspa sem par: o que veio antes segue lido")

    def test_alvos_por_ferramenta(self):
        def hook(nome, entrada):
            return types.SimpleNamespace(campo=lambda c: {"tool_name": nome, "tool_input": entrada}[c], cwd=lambda: Path("/a"))
        self.assertEqual(copia.alvos(hook("Bash", {"command": "git commit"})), ["/a"])
        self.assertEqual(copia.alvos(hook("Write", {"file_path": "b.txt"})), ["/a/b.txt"])
        self.assertEqual(copia.alvos(hook("NotebookEdit", {"notebook_path": "/c/n.ipynb"})), ["/c/n.ipynb"])
        self.assertEqual(copia.alvos(hook("Write", {"file_path": ""})), [])
        self.assertEqual(copia.alvos(hook("Write", ["/b"])), [])
        self.assertEqual(copia.alvos(hook("Read", {"file_path": "/b"})), [])

    def test_dentro(self):
        self.assertTrue(copia.dentro("/a/b", "/a/b"))
        self.assertTrue(copia.dentro("/a/b/c", "/a/b/"))
        self.assertFalse(copia.dentro("/a/bc", "/a/b"), "pasta irmã com o mesmo começo")

    def test_livre(self):
        with mock.patch.dict(os.environ, {"HOME": FORA_DO_TMP}):
            self.assertTrue(copia.livre(f"{FORA_DO_TMP}/.forge-contrib/docs/x.md"))
            self.assertFalse(copia.livre(f"{FORA_DO_TMP}/.forge-contrib/wt/outra/x.md"), "wt/ não é pasta de controle")
            self.assertTrue(copia.livre("/dev/null"))
            self.assertTrue(copia.livre(os.path.join(tempfile.gettempdir(), "x")))
            self.assertFalse(copia.livre("/etc/x"))


class Copias(unittest.TestCase):
    """As cópias com branch (worktrees e clones de ~/.forge-contrib/wt/) e as branches do agente no registro."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-copia-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.raiz = repositorio(self.tmp / "proj", "develop")

    def test_head_de(self):
        git("worktree", "add", "-q", "-b", "melhoria/x", str(self.tmp / "wt"), cwd=self.raiz)
        git("worktree", "add", "-q", "--detach", str(self.tmp / "solta"), cwd=self.raiz)
        self.assertEqual(copia.head_de(self.raiz), "refs/heads/develop")
        self.assertEqual(copia.head_de(self.tmp / "wt"), "refs/heads/melhoria/x", "worktree: .git é arquivo")
        self.assertIsNone(copia.head_de(self.tmp / "solta"), "HEAD solto")
        self.assertIsNone(copia.head_de(self.tmp / "nada"))

    def test_copias(self):
        git("worktree", "add", "-q", "-b", "melhoria/x", str(self.tmp / "wt"), cwd=self.raiz)
        git("worktree", "add", "-q", "--detach", str(self.tmp / "solta"), cwd=self.raiz)
        repositorio(self.tmp / "home" / ".forge-contrib" / "wt" / "meu", "melhoria/y")
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp / "home"), "GIT_DIR": str(self.tmp / "nao-existe")}):
            achadas = copia.copias(self.raiz)
        real = os.path.realpath
        self.assertEqual(achadas, {real(self.raiz): "refs/heads/develop", real(self.tmp / "wt"): "refs/heads/melhoria/x",
                                   real(self.tmp / "home/.forge-contrib/wt/meu"): "refs/heads/melhoria/y"})

    def test_branches_do_agente(self):
        run = self.raiz / ".forge" / "run"
        run.mkdir(parents=True)
        (self.raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        registro = {"agentes": [{"id": "a1", "escrita": ["melhoria/x"]}, {"id": "a2", "escrita": ["melhoria/y"]}, "lixo"]}
        (run / "agentes.json").write_text(json.dumps(registro), encoding="utf-8")
        self.assertEqual(copia.branches_do_agente(self.raiz, "a1"), {"refs/heads/melhoria/x"})
        self.assertEqual(copia.branches_do_agente(self.raiz, "a3"), set())

    def test_sem_projeto_nao_le_as_copias(self):
        hook = types.SimpleNamespace(campo=lambda *c: {"agent_id": "a1", "hook_event_name": "PreToolUse", "tool_name": "Write",
                                                        "tool_input": {"file_path": "/etc/x"}}[c[0]],
                                     cwd=lambda: self.tmp, projeto=lambda *a, **k: None)
        with mock.patch.object(copia, "copias", side_effect=AssertionError("leu as cópias sem projeto")):
            self.assertIsNone(copia.principal(hook))


if __name__ == "__main__":
    unittest.main()
