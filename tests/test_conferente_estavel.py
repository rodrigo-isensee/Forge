"""E4 da versao-035 (R-BRIEF): o texto do conferente não reabre por leitura o campo que o `forge-check brief` decidiu `ok`
e deixa a lista de comandos permitidos intacta (o hook `conformidade` a lê)."""
import hashlib
import re
import unittest
from pathlib import Path

TEXTO = (Path(__file__).resolve().parent.parent / "agents" / "conferente.md").read_text(encoding="utf-8")
COMANDOS_SHA = "9bfc0c302af03ae2ce9f9322cb908b1e086606a01635dffc8ee2eb632596eaf9"


def paragrafo(titulo):
    return next((linha for linha in TEXTO.splitlines() if linha.startswith(titulo)), "")


class NaoReabre(unittest.TestCase):
    def test_regra_existe_e_cita_os_campos_do_comando(self):
        regra = paragrafo("**Decidido pelo comando não se reabre.**")
        self.assertTrue(regra, "falta o parágrafo da regra")
        for campo in ("`forma: ok`", "`corte:` que não reprova", "`citação: ok`", "`decisões: ok`", "nesta passada"):
            self.assertIn(campo, regra)

    def test_o_que_segue_por_leitura_fica_fora_da_lista(self):
        """C-1 e T-3: etapa, fidelidade e contradição literal seguem sempre por leitura; a regra não os nomeia."""
        regra = paragrafo("**Decidido pelo comando não se reabre.**")
        for termo in ("etapa:", "etapa", "fidelidade", "contradição"):
            self.assertNotIn(termo, regra.lower())

    def test_hash_aprovado_nao_dispensa_fato_novo(self):
        regra = paragrafo("**Decidido pelo comando não se reabre.**")
        self.assertIn("fato novo do disco reprova sempre", regra)


class FerramentasDoDestino(unittest.TestCase):
    def test_pq_cmd_para_destino_sem_bash_reprova(self):
        """C-5 e C-6: o caminho sai só do `--destino`, e a reprovação tem a frase fixa."""
        forma = paragrafo("4. **Forma**")
        for trecho in ("grep -n '^tools:' agents/<nome>.md", "--destino forge:<nome>", "`forma: destino não encontrado`",
                       "`forma: PQ-n cmd para destino sem Bash (rode-o o Jarvis ou mude o verificador)`, que reprova"):
            self.assertIn(trecho, forma)

    def test_caminho_do_destino_sai_so_do_nome(self):
        """C-5 e T-2: todo comando sobre o destino lê só `agents/<nome>.md`, com `<nome>` limitado ao padrão."""
        forma = paragrafo("4. **Forma**")
        comandos = [c for c in re.findall(r"`((?:ls|grep|cat|head|test) [^`]*)`", forma)
                    if not all(arg.startswith("-") for arg in c.split()[1:])]  # `ls -l` citado sem caminho
        self.assertGreaterEqual(len(comandos), 2)
        for comando in comandos:
            self.assertTrue(comando.endswith(" agents/<nome>.md"), comando)
        self.assertEqual(set(re.findall(r"[\w./*<>-]*agents/[^\s`]*\.md", forma)), {"agents/<nome>.md"})
        self.assertIn("`<nome>` só de `[a-z0-9-]+`", forma)
        self.assertNotIn("stacks/", forma)


class ComandosPermitidos(unittest.TestCase):
    def test_secao_identica(self):
        """C-7 e T-1: a seção que o hook `conformidade` lê não muda."""
        ini = TEXTO.index("## Comandos permitidos")
        secao = TEXTO[ini:TEXTO.index("\n## ", ini)]
        self.assertEqual(hashlib.sha256(secao.encode("utf-8")).hexdigest(), COMANDOS_SHA)


if __name__ == "__main__":
    unittest.main()
