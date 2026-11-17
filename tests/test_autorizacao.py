"""ADR 0018, G1.1a: formato e integridade das autorizações gravadas (`bin/forge_autorizacao.py`, `forge-check autorizacao ler`)."""
import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent.parent / "bin"
_spec = importlib.util.spec_from_file_location("forge_autorizacao", BIN / "forge_autorizacao.py")
fa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fa)
GRAVADOR = hashlib.sha256((BIN / "forge-check").read_bytes()).hexdigest()
CORPO = "pode aplicar o rótulo no PR 5\n\nnão é recorte"


def concessao(corpo=CORPO, **troca):
    campos = {"Id": "A-1", "Ato": "rotulo-afrouxa-regra", "Alvos": "pr:5", "Validade": "ate:2026-11-18 08:00",
              "Validade-utc": "2026-11-18 11:00", "Fuso": "America/Sao_Paulo", "Origem-da-validade": "esta noite",
              "Estado-inicial": "ativa", "Motivo-da-pendencia": "nenhum", "Mensagem": "u-1",
              "Hora-da-fala": "2026-11-18T00:00:00Z", "Sessao": "s-1", "Sha256": fa.sha(CORPO), "Gravado-por": GRAVADOR,
              "Autoriza": fa.AUTORIZA, **troca}
    return "".join(f"{k}: {v}\n" for k, v in campos.items() if v is not None) + "\n" + corpo


class Ler(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.raiz)
        self.pasta = self.raiz / fa.PASTA
        self.pasta.mkdir(parents=True)

    def ler(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            rc = fa.cmd_ler(self.raiz, {"gravador": GRAVADOR, "seguro": str})
        return rc, saida.getvalue()

    def test_integra_mostra_a_mensagem_inteira_validade_no_fuso_e_em_utc(self):
        (self.pasta / "A-1").write_text(concessao(), encoding="utf-8")
        rc, saida = self.ler()
        self.assertEqual(rc, 0, saida)
        self.assertIn("A-1 · íntegra · rotulo-afrouxa-regra · pr:5 · validade ate:2026-11-18 08:00 America/Sao_Paulo = "
                      "2026-11-18 11:00 UTC", saida)
        self.assertIn("> pode aplicar o rótulo no PR 5\n> \n> não é recorte\n", saida)

    def test_evento_adulterado_ou_fora_da_forma(self):
        casos = {"corpo": dict(corpo=CORPO + "!"), "gravador": dict(**{"Gravado-por": "0" * 64}),
                 "ato": dict(Ato="merge"), "alvos": dict(Alvos="pr:5 e pr:6"), "inicial": dict(**{"Estado-inicial": "x"}),
                 "autoriza": dict(Autoriza="tudo"), "ausente": dict(Sessao=None)}
        for caso, troca in casos.items():
            with self.subTest(caso=caso):
                (self.pasta / "A-1").write_text(concessao(**troca), encoding="utf-8")
                rc, saida = self.ler()
                self.assertEqual(rc, 1, saida)
                self.assertIn("A-1 · adulterada (", saida)

    def test_evento_ilegivel_e_erro_e_nada_e_integro_por_ele(self):
        fora = self.raiz / "fora"
        fora.write_text(concessao(), encoding="utf-8")
        duplicado = concessao().replace("Id: A-1\n", f"Sha256: {'0' * 64}\nId: A-1\n")
        casos = {"link": lambda a: a.symlink_to(fora), "pasta": lambda a: a.mkdir(),
                 "utf8": lambda a: a.write_bytes(b"Id: \xff\n\nx"), "repetido": lambda a: a.write_text(duplicado),
                 "sem-linha-vazia": lambda a: a.write_text(concessao("", Sha256=fa.sha("")).rstrip("\n"))}
        for caso, criar in casos.items():
            with self.subTest(caso=caso):
                shutil.rmtree(self.pasta)
                self.pasta.mkdir()
                criar(self.pasta / "A-1")
                rc, saida = self.ler()
                self.assertEqual(rc, 1, saida)
                self.assertIn("autorizacao: erro: A-1: ", saida)
                self.assertNotIn("íntegra", saida)

    def test_pasta_que_e_link_e_nome_fora_da_forma_sao_erro(self):
        outra = self.raiz / "outra"
        outra.mkdir()
        (outra / "A-1").write_text(concessao(), encoding="utf-8")
        self.pasta.rmdir()
        self.pasta.symlink_to(outra)
        rc, saida = self.ler()
        self.assertEqual((rc, "íntegra" in saida, "não é pasta comum" in saida), (1, False, True), saida)
        self.pasta.unlink()
        self.pasta.mkdir()
        (self.pasta / "A-1.bak").write_text(concessao(), encoding="utf-8")
        self.assertEqual(self.ler(), (1, "autorizacao: erro: A-1.bak: nome fora da forma\n"
                                         "autorizacao: 0 adulterada(s), 1 erro(s) de leitura; estado pela validade no G1.1b; "
                                         "nada barra\n"))

    def test_pasta_ausente_nada_e_so_concessao_e_listada(self):
        shutil.rmtree(self.pasta)
        self.assertEqual(self.ler()[0], 0)
        self.pasta.mkdir()
        for nome in ("U-A-1", "M-0a1b"):  # só presença: vazios, não são lidos
            (self.pasta / nome).write_text("", encoding="utf-8")
        (self.pasta / "C-A-1").write_text(concessao(Id="C-A-1"), encoding="utf-8")
        rc, saida = self.ler()
        self.assertEqual((rc, saida.count("autorizacao: ")), (0, 1), saida)

    def test_forge_check_autorizacao_ler_aceita_so_o_gravado_por_ele(self):
        (self.pasta / "A-1").write_text(concessao(), encoding="utf-8")
        (self.pasta / "A-2").write_text(concessao(**{"Id": "A-2", "Gravado-por": "f" * 64}), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "PYTHON"))}
        env["GIT_CEILING_DIRECTORIES"] = str(self.raiz.parent)
        r = subprocess.run([sys.executable, "-I", str(BIN / "forge-check"), "--raiz", str(self.raiz), "autorizacao", "ler"],
                           capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("A-1 · íntegra", r.stdout)
        self.assertIn("A-2 · adulterada (Gravado-por não é o forge-check carregado)", r.stdout)


if __name__ == "__main__":
    unittest.main()
