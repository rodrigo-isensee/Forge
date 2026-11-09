"""Orkastery 3 (0.44.2): decisão óbvia por regra fixa (`bin/forge_decisor.py`, pelo `forge-check decisoes registrar|reverter|conferir`),
placar no `forge-check metricas` e a linha `decidido:` conferida no .githooks/commit-msg."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
FATOS_OK = {"irreversivel": "nao", "dinheiro": "nao", "escopo": "nao", "alternativas-piores": "sim", "reversivel": "sim", "erro-barato": "sim"}
TEXTO = {"pedido": "p1", "porta": "nome do arquivo de teste", "criterio": "R-PROVA", "fato": "a convenção test_<modulo> já vale",
         "porque": "segue a convenção", "como-mudar": "renomear o arquivo", "custo-reverter": "um commit"}


class Decisor(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-decisor-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def rodar(self, *args):
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), *args], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout

    def registrar(self, **troca):
        campos = {**TEXTO, **FATOS_OK, **troca}
        return self.rodar("decisoes", "registrar", *[x for k, v in campos.items() for x in (f"--{k}", v)])

    def registro(self):
        arq = self.tmp / "docs" / "kanban" / "decisoes-obvias.jsonl"
        return [json.loads(l) for l in arq.read_text(encoding="utf-8").splitlines()]

    def test_as_quatro_condicoes_de_pe_decide_e_imprime_a_linha_do_commit(self):
        rc, out = self.registrar()
        self.assertEqual(rc, 0, out)
        self.assertIn("decidido: nome do arquivo de teste — R-PROVA — a convenção test_<modulo> já vale", out)
        r = self.registro()[0]
        self.assertEqual((r["resultado"], r["o_que"], r["como_mudar"], r["custo_reverter"]),
                         ("decidida", "nome do arquivo de teste", "renomear o arquivo", "um commit"))

    def test_porta_fechada_vira_pergunta(self):
        for porta in ("irreversivel", "dinheiro", "escopo"):
            rc, out = self.registrar(**{porta: "sim"})
            self.assertEqual(rc, 1, out)
            self.assertIn(f"porta fechada: {porta}", out)
        self.assertEqual({r["resultado"] for r in self.registro()}, {"pergunta"})

    def test_condicao_que_falta_vira_pergunta(self):
        for k in ("alternativas-piores", "reversivel", "erro-barato"):
            rc, out = self.registrar(**{k: "nao"})
            self.assertEqual(rc, 1, (k, out))
        rc, out = self.registrar(criterio="porque sim")
        self.assertEqual(rc, 1, out)
        self.assertIn("critério escrito", out)

    def test_fato_ausente_nao_grava(self):
        rc, _ = self.registrar(reversivel="talvez")
        self.assertEqual(rc, 2)
        self.assertFalse((self.tmp / "docs" / "kanban" / "decisoes-obvias.jsonl").exists())

    def test_o_decisor_nao_recebe_objetivo_nem_conversa(self):
        sys.path.insert(0, str(RAIZ / "bin"))
        try:
            import forge_decisor  # noqa: PLC0415
        finally:
            sys.path.pop(0)
        fatos = {"irreversivel": False, "dinheiro": False, "escopo": False, "criterio": "R-PROVA", "alternativas_piores": True,
                 "reversivel": True, "erro_barato": True}
        self.assertEqual(forge_decisor.decidir(**fatos), ("decidida", None))
        for extra in ("objetivo", "conversa"):
            with self.assertRaises(TypeError):
                forge_decisor.decidir(**fatos, **{extra: "x"})
        rc, _ = self.rodar("decisoes", "registrar", "--objetivo", "x")
        self.assertEqual(rc, 2, "o CLI não tem --objetivo")

    def test_reverter_e_placar_no_metricas(self):
        self.registrar()
        self.registrar(dinheiro="sim")
        self.assertEqual(self.rodar("decisoes", "reverter", "--id", "D0001", "--porque", "quebrou o nome")[0], 0)
        self.assertEqual(self.rodar("decisoes", "reverter", "--id", "D0002", "--porque", "x")[0], 1, "pergunta não se reverte")
        rc, out = self.rodar("metricas", "--develop", "x", "--main", "y")
        self.assertIn("metricas: placar decididas=1 perguntas=1 revertidas=1", out)

    def test_conferir_recusa_linha_decidido_fora_da_forma(self):
        msg = self.tmp / "msg"
        for texto, rc in (("feat: x\n\ndecidido: nome — R-PROVA — o fato\n", 0), ("feat: x\n\ndecidido: escolhi o nome\n", 1),
                          ("feat: x\n\ndecidido: nome — porque quis — fato\n", 1), ("feat: sem linha\n", 0)):
            msg.write_text(texto, encoding="utf-8")
            self.assertEqual(self.rodar("decisoes", "conferir", "--mensagem", str(msg))[0], rc, texto)

    def test_commit_msg_do_githooks_recusa_o_commit(self):
        repo = self.tmp / "r"
        shutil.copytree(RAIZ / ".githooks", repo / ".githooks")
        (repo / "bin").mkdir()
        for nome in ("forge-check", "forge_decisor.py"):
            shutil.copy(RAIZ / "bin" / nome, repo / "bin" / nome)
        env = dict(os.environ, HOME=str(self.tmp / "home"), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        g = lambda *a: subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "-c",  # noqa: E731
                                       "core.hooksPath=.githooks", *a], capture_output=True, text=True, env=env)
        g("init", "-q")
        g("add", ".")
        self.assertNotEqual(g("commit", "-q", "-m", "x\n\ndecidido: sem forma").returncode, 0)
        self.assertEqual(g("commit", "-q", "-m", "x\n\ndecidido: nome — R-PROVA — fato").returncode, 0)


if __name__ == "__main__":
    unittest.main()
