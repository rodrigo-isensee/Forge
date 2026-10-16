"""`forge-check sobreposicao` (TA-6) e `forge-check movimento` (PA-9), mais a fila de integração (PA-3) como texto."""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-check"
AMBIENTE = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=AMBIENTE, capture_output=True, text=True, check=True).stdout


def checar(cwd, *args):
    r = subprocess.run([sys.executable, str(FERRAMENTA), "--raiz", str(cwd), *args], capture_output=True, text=True, env=AMBIENTE)
    return r.returncode, r.stdout


class Sobreposicao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        git(self.repo, "init", "-q", "-b", "develop")
        self.escrever("base.txt", "base\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")

    def escrever(self, nome, texto):
        (self.repo / nome).write_text(texto, encoding="utf-8")

    def ramo(self, nome, **arquivos):
        git(self.repo, "switch", "-q", "-c", nome, "develop")
        for arq, texto in arquivos.items():
            self.escrever(arq.replace("__", "."), texto)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", nome)
        git(self.repo, "switch", "-q", "develop")

    def test_lista_so_os_pares_com_arquivo_em_comum_e_o_resumo(self):
        self.ramo("melhoria/a", comum__txt="a\n", so_a__txt="a\n")
        self.ramo("melhoria/b", comum__txt="b\n")
        self.ramo("melhoria/c", so_c__txt="c\n")
        self.ramo("feature/fora", comum__txt="f\n")  # fora do padrão melhoria/*
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertEqual(rc, 0)
        self.assertEqual(saida.splitlines(), [
            "melhoria/a <-> melhoria/b: comum.txt",
            "sobreposicao: 1 par(es) com arquivos em comum entre 3 branch(es) melhoria/* (base develop)"])

    def test_saida_deterministica(self):
        self.ramo("melhoria/a", x__txt="a\n", y__txt="a\n")
        self.ramo("melhoria/b", y__txt="b\n", x__txt="b\n")
        self.assertEqual({checar(self.repo, "sobreposicao", "--base", "develop")[1] for _ in range(3)},
                         {"melhoria/a <-> melhoria/b: x.txt, y.txt\n"
                          "sobreposicao: 1 par(es) com arquivos em comum entre 2 branch(es) melhoria/* (base develop)\n"})

    def test_sem_branches_so_o_resumo_e_rc_zero(self):
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertEqual((rc, saida), (0, "sobreposicao: 0 par(es) com arquivos em comum entre 0 branch(es) melhoria/* (base develop)\n"))

    def test_branch_remota_e_local_iguais_contam_uma_vez(self):
        self.ramo("melhoria/a", comum__txt="a\n")
        self.ramo("melhoria/b", comum__txt="b\n")
        origem = tempfile.TemporaryDirectory()
        self.addCleanup(origem.cleanup)
        git(self.repo, "clone", "-q", "--bare", str(self.repo), origem.name)
        git(self.repo, "remote", "add", "origin", origem.name)
        git(self.repo, "fetch", "-q", "origin")
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertIn("entre 2 branch(es)", saida)
        self.assertEqual(saida.count("<->"), 1)

    def test_base_inexistente_nao_falha(self):
        git(self.repo, "branch", "-m", "outra")
        rc, saida = checar(self.repo, "sobreposicao", "--base", "nao-existe-xyz")
        self.assertEqual(rc, 0)
        self.assertIn("base não encontrada", saida)


class Movimento(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        self.arq = self.raiz / "docs" / "kanban" / "historico.md"

    def test_cria_o_arquivo_e_acrescenta_com_hora_iso_e_fuso(self):
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Aguardando o dono", "--para", "Sem credencial")[0], 0)
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Sem credencial", "--para", "Em andamento", "--motivo", "chegou")[0], 0)
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[:2], ["| Data/hora | Cartão | De | Para | Motivo |", "|---|---|---|---|---|"])
        iso = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d"
        self.assertRegex(linhas[2], rf"^\| {iso} \| K-1 \| Aguardando o dono \| Sem credencial \| — \|$")
        self.assertRegex(linhas[3], rf"^\| {iso} \| K-1 \| Sem credencial \| Em andamento \| chegou \|$")
        self.assertEqual(len(linhas), 4)

    def test_nao_reescreve_o_que_existe_e_protege_a_tabela(self):
        self.arq.parent.mkdir(parents=True)
        self.arq.write_text("| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n| antiga | K-0 | a | b | — |\n", encoding="utf-8")
        checar(self.raiz, "movimento", "K-2", "--de", "a|b", "--para", "c\nd", "--motivo", "x | y")
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[2], "| antiga | K-0 | a | b | — |")
        self.assertEqual(len(linhas), 4)
        self.assertTrue(linhas[3].endswith("| K-2 | a/b | c d | x / y |"), linhas[3])

    def test_campo_vazio_falha_e_nao_grava(self):
        rc, saida = checar(self.raiz, "movimento", " ", "--de", "a", "--para", "b")
        self.assertEqual(rc, 1)
        self.assertFalse(self.arq.exists())


class RegrasEmTexto(unittest.TestCase):
    def texto(self, rel):
        return (RAIZ / rel).read_text(encoding="utf-8")

    def test_fila_de_integracao_na_regra_e_no_tech_lead(self):
        for rel, trechos in (("docs/regras/R-FLUXO.md", ("um por vez", "ordem de chegada", "forge-check sobreposicao")),
                             ("agents/tech-lead.md", ("Fila de integração", "ordem de chegada", "forge-check sobreposicao"))):
            for trecho in trechos:
                self.assertIn(trecho, self.texto(rel), rel)

    def test_jarvis_serializa_antes_de_disparar_e_registra_o_quadro(self):
        t = self.texto("agents/jarvis.md")
        for trecho in ("bin/forge-check sobreposicao", "serializam", "forge-check movimento"):
            self.assertIn(trecho, t)

    def test_skill_do_quadro_manda_registrar_com_o_subcomando(self):
        t = self.texto("skills/kanban-scrum/SKILL.md")
        for trecho in ("forge-check movimento", "Aguardando o dono", "Sem credencial", "ISO 8601"):
            self.assertIn(trecho, t)


if __name__ == "__main__":
    unittest.main()
