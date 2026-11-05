"""E4 da versao-035 (R-BRIEF): o texto do conferente não reabre por leitura o campo que o `forge-check brief` decidiu `ok`
e deixa a lista de comandos permitidos intacta (o hook `conformidade` a lê)."""
import hashlib
import unittest
from pathlib import Path

TEXTO = (Path(__file__).resolve().parent.parent / "agents" / "conferente.md").read_text(encoding="utf-8")
COMANDOS_SHA = "9bfc0c302af03ae2ce9f9322cb908b1e086606a01635dffc8ee2eb632596eaf9"


def paragrafo(titulo):
    return next((linha for linha in TEXTO.splitlines() if linha.startswith(f"**{titulo}")), "")


class NaoReabre(unittest.TestCase):
    def test_regra_existe_e_cita_os_campos_do_comando(self):
        regra = paragrafo("Decidido pelo comando não se reabre")
        self.assertTrue(regra, "falta o parágrafo da regra")
        for campo in ("`forma: ok`", "`corte:` que não reprova", "`citação: ok`", "`decisões: ok`", "nesta passada"):
            self.assertIn(campo, regra)

    def test_o_que_segue_por_leitura_fica_fora_da_lista(self):
        """C-1 e T-3: etapa, fidelidade e contradição literal seguem sempre por leitura; a regra não os nomeia."""
        regra = paragrafo("Decidido pelo comando não se reabre")
        for termo in ("etapa:", "etapa", "fidelidade", "contradição"):
            self.assertNotIn(termo, regra.lower())

    def test_hash_aprovado_nao_dispensa_fato_novo(self):
        regra = paragrafo("Decidido pelo comando não se reabre")
        self.assertIn("fato novo do disco reprova sempre", regra)


class ComandosPermitidos(unittest.TestCase):
    def test_secao_identica(self):
        """C-7 e T-1: a seção que o hook `conformidade` lê não muda."""
        ini = TEXTO.index("## Comandos permitidos")
        secao = TEXTO[ini:TEXTO.index("\n## ", ini)]
        self.assertEqual(hashlib.sha256(secao.encode("utf-8")).hexdigest(), COMANDOS_SHA)


if __name__ == "__main__":
    unittest.main()
