"""POS-RELEASE-SCRIPT-UNICO (v047 E2.223, Q5): o script único de pós-release do modelo de projeto confere o alvo antes do
primeiro comando, para no primeiro erro e termina com uma linha de resumo. Nada específico de projeto."""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "templates/projeto/scripts/pos-release"
MODELO = RAIZ / "templates/projeto/docs/devops"

REGRAS = ("alvo-variavel: ALVO\n"
          "padrao: db://padrao/base\n"
          "ensaio-aceita: db://*/descartavel-*\n"
          "real-aceita: db://*/producao\n")
DESCARTAVEL = "db://h/descartavel-1"
REAL = "db://h/producao"


class PosRelease(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.pasta = Path(t.name)
        (self.pasta / "scripts").mkdir()
        shutil.copy(SCRIPT, self.pasta / "scripts/pos-release")
        self.marca = self.pasta / "marca"

    def passos(self, texto):
        arq = self.pasta / "passos"
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, modo, texto, alvo=DESCARTAVEL, *, var="ALVO"):
        env = {"PATH": os.environ["PATH"], "LC_ALL": "C.UTF-8"}
        if alvo is not None:
            env[var] = alvo
        return subprocess.run(["bash", str(self.pasta / "scripts/pos-release"), modo, str(self.passos(texto))] if modo else
                              ["bash", str(self.pasta / "scripts/pos-release")],
                              env=env, capture_output=True, text=True, timeout=60)

    def resumo(self, r):
        linhas = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith("pos-release:")]
        self.assertEqual(len(linhas), 1, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).splitlines()[-1] if r.returncode else r.stdout.splitlines()[-1], linhas[0])
        return linhas[0]

    def passo(self, nome, cmd=None):
        return f"passo: {nome} :: {cmd or f'echo {nome} >> {self.marca}'}\n"

    def feito(self):
        return self.marca.read_text().split() if self.marca.exists() else []

    def test_ensaio_em_alvo_descartavel_roda_todos_os_passos_e_resume(self):
        r = self.rodar("ensaio", REGRAS + self.passo("um") + self.passo("dois"))
        self.assertEqual((r.returncode, self.feito()), (0, ["um", "dois"]), r.stderr)
        self.assertRegex(self.resumo(r), r"^pos-release: OK · 2 de 2 passos · modo ensaio · alvo db://h/descartavel-1 · \d+s$")

    def test_real_em_alvo_real_roda(self):
        r = self.rodar("real", REGRAS + self.passo("um"), REAL)
        self.assertEqual((r.returncode, self.feito()), (0, ["um"]), r.stderr)
        self.assertIn("modo real", self.resumo(r))

    def test_para_no_primeiro_erro_e_diz_qual(self):
        r = self.rodar("ensaio", REGRAS + self.passo("um") + self.passo("quebra", "exit 7") + self.passo("tres"))
        self.assertEqual((r.returncode, self.feito()), (1, ["um"]))
        self.assertRegex(self.resumo(r), r'^pos-release: FALHOU · passo 2 de 3 "quebra" saiu com rc=7 · 1 passos não rodaram · modo ensaio')

    def recusado(self, r, trecho):
        self.assertEqual((r.returncode, self.feito()), (2, []), r.stdout + r.stderr)
        self.assertRegex(self.resumo(r), r"^pos-release: RECUSADO · .*" + re.escape(trecho) + r".* · nenhum comando rodou$")

    def test_recusa_o_valor_padrao(self):
        self.recusado(self.rodar("ensaio", REGRAS.replace("db://*/descartavel-*", "*") + self.passo("um"), "db://padrao/base"), "valor padrão")

    def test_recusa_alvo_vazio_ou_ausente(self):
        regras = REGRAS.replace("db://*/descartavel-*", "*")
        self.recusado(self.rodar("ensaio", regras + self.passo("um"), ""), "está vazia")
        self.recusado(self.rodar("ensaio", regras + self.passo("um"), None), "está vazia")

    def test_ensaio_recusa_alvo_que_nao_prova_ser_descartavel(self):
        self.recusado(self.rodar("ensaio", REGRAS + self.passo("um"), REAL), "não casa com ensaio-aceita")

    def test_real_recusa_alvo_descartavel(self):
        self.recusado(self.rodar("real", REGRAS + self.passo("um"), DESCARTAVEL), "não casa com real-aceita")

    def test_recusa_regras_ambiguas(self):
        regras = REGRAS.replace("db://*/producao", "db://*/descartavel-*")
        self.recusado(self.rodar("ensaio", regras + self.passo("um")), "ambíguas")
        self.recusado(self.rodar("real", regras + self.passo("um")), "ambíguas")

    def test_recusa_modo_invalido_e_sem_modo(self):
        self.recusado(self.rodar("producao", REGRAS + self.passo("um")), "escolha o modo")
        self.recusado(self.rodar("", REGRAS + self.passo("um")), "escolha o modo")

    def test_recusa_arquivo_de_passos_ausente(self):
        env = {"PATH": os.environ["PATH"], "ALVO": DESCARTAVEL}
        r = subprocess.run(["bash", str(self.pasta / "scripts/pos-release"), "ensaio", str(self.pasta / "nao-existe")],
                           env=env, capture_output=True, text=True, timeout=60)
        self.recusado(r, "não encontrado")

    def test_recusa_chave_desconhecida_e_passo_mal_formado(self):
        self.recusado(self.rodar("ensaio", REGRAS + "intruso: x\n" + self.passo("um")), "chave desconhecida")
        self.recusado(self.rodar("ensaio", REGRAS + f"passo: so-comando echo oi >> {self.marca}\n"), "passo sem")
        self.recusado(self.rodar("ensaio", REGRAS + "passo: nome ::    \n"), "vazio")

    def test_linha_recuada_ou_com_comentario_no_fim_nao_e_pulada(self):
        # só linha vazia ou que começa por # é ignorada: recuada, com # no fim ou sem chave é recusada e nada roda
        passo = self.passo("um")
        for linha in (f"  passo: dois :: echo dois >> {self.marca} # nota\n", f"  passo: dois :: echo dois >> {self.marca}\n",
                      "  padrao: db://h/descartavel-1 # nota\n", "  ensaio-aceita: * # nota\n", "texto solto sem chave\n"):
            self.recusado(self.rodar("ensaio", REGRAS + passo + linha), "linha que não entendo")
        r = self.rodar("ensaio", REGRAS + "\n   \n# c\n   # recuado\n\t# tab\n" + passo)
        self.assertEqual((r.returncode, self.feito()), (0, ["um"]), r.stderr)

    def test_passo_com_nome_vazio_e_recusado(self):
        self.recusado(self.rodar("ensaio", REGRAS + f"passo:  :: echo oi >> {self.marca}\n"), "passo sem")
        self.recusado(self.rodar("ensaio", REGRAS + "passo: ::\n"), "passo sem")

    def test_mascara_senha_com_arroba_barra_e_consulta(self):
        for alvo, segredo in (("db://u:p@ss@h/descartavel-3", "ss@"), ("db://u:a/bXYZ@h/descartavel-3", "bXYZ"),
                              ("db://h/descartavel-3?password" "=XYZ123&x=1", "XYZ123"), ("db://h/descartavel-3?SENHA=XYZ123", "XYZ123"),
                              ("db://h/descartavel-3?token=XYZ123", "XYZ123")):
            for passo in (self.passo("um"), self.passo("quebra", "exit 3")):
                r = self.rodar("ensaio", REGRAS + passo, alvo)
                self.assertNotIn(segredo, r.stdout + r.stderr, alvo)
                self.assertIn("***", self.resumo(r), alvo)

    def test_recusa_arquivo_sem_passo_sem_regra_de_ensaio_ou_sem_variavel(self):
        self.recusado(self.rodar("ensaio", REGRAS), "nenhum passo")
        self.recusado(self.rodar("ensaio", REGRAS.replace("ensaio-aceita: db://*/descartavel-*\n", "") + self.passo("um")), "ensaio-aceita ausente")
        self.recusado(self.rodar("real", REGRAS.replace("real-aceita: db://*/producao\n", "") + self.passo("um"), REAL), "real-aceita ausente")
        self.recusado(self.rodar("ensaio", REGRAS.replace("alvo-variavel: ALVO\n", "") + self.passo("um")), "alvo-variavel")

    def test_modelo_entregue_recusa_ate_o_projeto_preencher(self):
        r = subprocess.run(["bash", str(self.pasta / "scripts/pos-release"), "ensaio", str(MODELO / "pos-release.passos")],
                           env={"PATH": os.environ["PATH"], "ALVO": DESCARTAVEL}, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_mascara_a_credencial_do_alvo_no_resumo_e_no_erro(self):
        alvo = "db://usuario:segredo@h/descartavel-2"
        ok = self.rodar("ensaio", REGRAS + self.passo("um"), alvo)
        ruim = self.rodar("ensaio", REGRAS + self.passo("quebra", "exit 3"), alvo)
        for r in (ok, ruim):
            self.assertNotIn("segredo", r.stdout + r.stderr)
            self.assertIn("db://***@h/descartavel-2", self.resumo(r))

    def test_passos_recebem_o_alvo_e_rodam_na_raiz_do_projeto(self):
        r = self.rodar("ensaio", REGRAS + self.passo("um", f'echo "$ALVO $(pwd)" > {self.marca}'))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.marca.read_text().split(), [DESCARTAVEL, str(self.pasta.resolve())])


class ModeloDeProjeto(unittest.TestCase):
    def test_script_executavel_sintaxe_e_sem_nada_de_projeto(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        self.assertEqual(subprocess.run(["bash", "-n", str(SCRIPT)]).returncode, 0)
        self.assertTrue((MODELO / "pos-release.md").is_file() and (MODELO / "pos-release.passos").is_file())

    def test_roteiro_em_texto_e_so_explicacao_e_cita_o_script(self):
        texto = (MODELO / "pos-release.md").read_text(encoding="utf-8")
        self.assertIn("scripts/pos-release", texto)
        self.assertIn("só explica", texto)


if __name__ == "__main__":
    unittest.main()
