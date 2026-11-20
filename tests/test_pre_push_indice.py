"""INDICE-NO-PRE-PUSH (v0478 E45.1): o patch `docs/devops/v0479-indice-pre-push.patch` põe a conferência dos índices
(`scripts/indice-forge.py --conferir` e `scripts/indice-fixtures.py --conferir`) nas checagens baratas do envio leve.

O `.githooks/pre-push` em vigor é travado para os agentes: o teste copia o hook para $TMPDIR, aplica o patch na cópia (se o dono
ainda não aplicou) e roda o hook de verdade num repositório descartável. Classe do defeito: arquivo novo de bin/, hooks/ ou
scripts/ (ou fixture novo) sem linha no índice passar pelo envio e só falhar no CI.
Variantes: índice em dia passa; arquivo novo sem linha barra e a mensagem traz o comando que regenera; índice regenerado passa;
fixture novo sem linha barra; envio sem arquivo alterado não confere; ferramenta ausente (repositório mínimo) não barra.
Sem skip: o hook em vigor ainda sem o patch só entra como prova de que ele deixa o arquivo sem linha passar.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
PATCH = RAIZ / "docs" / "devops" / "v0479-indice-pre-push.patch"
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))})
ZERO = "0" * 40
MARCA = "INDICE-NO-PRE-PUSH"
COPIAS = ("bin/forge-testes", "bin/forge_apoio_testes.py", "scripts/indice-forge.py", "scripts/indice-fixtures.py", "tests/config.json")
FIXTURE = '{"descricao": "caso %s", "entrada": {}, "esperado": {"codigo": 0}}\n'


def hook_remendado(destino):
    """Copia o hook para `destino` e aplica o patch se o dono ainda não aplicou; devolve o caminho e se já estava em vigor."""
    destino.mkdir(parents=True)
    alvo = destino / ".githooks" / "pre-push"
    alvo.parent.mkdir()
    shutil.copy2(HOOK, alvo)
    em_vigor = MARCA in HOOK.read_text(encoding="utf-8")
    if not em_vigor:
        r = subprocess.run(["git", "apply", str(PATCH)], cwd=destino, env=AMBIENTE, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    return alvo, em_vigor


class IndiceNoEnvioLeve(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls._tmp.name)
        cls.remendado, cls.em_vigor = hook_remendado(cls.base / "hook")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(dir=self.base))
        self.run_dir = self.repo.parent / (self.repo.name + "-run")
        self.run_dir.mkdir()
        for rel in COPIAS:
            (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / rel, self.repo / rel)
        (self.repo / "tests" / "hooks" / "grupo").mkdir(parents=True)
        (self.repo / "tests" / "hooks" / "grupo" / "um-a.json").write_text(FIXTURE % "um")
        (self.repo / "docs").mkdir()
        (self.repo / "bin" / "ferr").write_text('#!/usr/bin/env python3\n"""Faz uma coisa."""\n')
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), HOME=str(self.repo.parent / "home"))
        self.git("init", "-q", "-b", "melhoria/x")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("add", "-A")  # o índice lê os versionados
        self.regenera()
        self.commit("base")
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD")

    def git(self, *args):
        r = subprocess.run(["git", *args], cwd=self.repo, env=AMBIENTE, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def regenera(self):
        self.git("add", "-A")
        for ferramenta in ("indice-forge", "indice-fixtures"):
            r = subprocess.run([sys.executable, "-I", f"scripts/{ferramenta}.py"], cwd=self.repo, env=AMBIENTE,
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
        self.git("add", "-A")

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    def roda(self, hook=None):
        sha = self.git("rev-parse", "HEAD")
        r = subprocess.run([str(hook or self.remendado), "origin", "u"], cwd=self.repo, env=self.env, capture_output=True,
                           text=True, timeout=120, input=f"refs/heads/x {sha} refs/heads/melhoria/x {ZERO}\n")
        return r.returncode, r.stderr

    def test_indice_em_dia_passa(self):
        (self.repo / "bin" / "ferr").write_text('#!/usr/bin/env python3\n"""Faz uma coisa."""\nx = 1\n')
        self.commit("muda sem mexer na doc")
        codigo, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertIn("plano=leve rc=0", erro)

    def test_arquivo_novo_sem_linha_no_indice_barra_com_o_comando_de_regenerar(self):
        (self.repo / "scripts" / "novo.py").write_text('"""Novo."""\n')
        self.commit("arquivo novo sem linha")
        codigo, erro = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertIn("índice fora de dia", erro)
        self.assertIn("python3 scripts/indice-forge.py", erro)
        self.assertIn("plano=baratas rc=1", erro)

    def test_indice_regenerado_depois_passa(self):
        (self.repo / "scripts" / "novo.py").write_text('"""Novo."""\n')
        self.regenera()
        self.commit("arquivo novo com linha")
        codigo, erro = self.roda()
        self.assertEqual(codigo, 0, erro)

    def test_fixture_novo_sem_linha_barra(self):
        (self.repo / "tests" / "hooks" / "grupo" / "dois-b.json").write_text(FIXTURE % "dois")
        self.commit("fixture novo sem linha")
        codigo, erro = self.roda()
        self.assertEqual(codigo, 1, erro)
        self.assertIn("python3 scripts/indice-fixtures.py", erro)

    def test_ferramenta_ausente_nao_barra(self):
        (self.repo / "scripts" / "novo.py").write_text('"""Novo."""\n')
        self.commit("arquivo novo sem linha")
        (self.repo / "scripts" / "indice-forge.py").unlink()
        (self.repo / "scripts" / "indice-fixtures.py").unlink()
        codigo, erro = self.roda()
        self.assertEqual(codigo, 0, erro)

    def test_hook_em_vigor_sem_o_patch_deixa_passar(self):
        """A prova do defeito: sem a conferência, o arquivo sem linha segue para o CI. Em vigor já remendado, vale a mesma barra."""
        (self.repo / "scripts" / "novo.py").write_text('"""Novo."""\n')
        self.commit("arquivo novo sem linha")
        codigo, erro = self.roda(HOOK)
        if self.em_vigor:
            self.assertEqual(codigo, 1, erro)
        else:
            self.assertEqual(codigo, 0, erro)


if __name__ == "__main__":
    unittest.main()
