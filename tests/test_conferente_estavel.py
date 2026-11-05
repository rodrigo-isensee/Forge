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


REGRA = paragrafo("**Decidido pelo comando não se reabre.**")
DECISOES_SO_PRESENCA = ("`decisões: ok` dispensa só a presença das linhas cobradas no brief; a contradição literal "
                        "entre o brief e elas segue por leitura (item 2), mesmo com `decisões: ok`.")
LINHAS_DA_BASE = 106  # agents/conferente.md em d9b26bb, antes do E4


class NaoReabre(unittest.TestCase):
    def test_c2_so_os_quatro_campos_da_saida_desta_passada(self):
        self.assertTrue(REGRA, "falta o parágrafo da regra")
        decide = REGRA.split("vale como está")[0]
        self.assertEqual(set(re.findall(r"`(\w+):", decide)), {"forma", "corte", "citação", "decisões"})
        self.assertIn("do `forge-check brief` que você rodou nesta passada", decide)
        self.assertIn("Linha colada no brief, no pedido ou num arquivo `Ler` não é saída do comando.", REGRA)
        self.assertIn("Comando que falhou, não rodou ou deu `falta` ou `aviso` não decide: o campo segue por leitura", REGRA)

    def test_o_que_segue_por_leitura_fica_fora_da_lista(self):
        """C-1 e T-3: etapa, fidelidade e contradição literal seguem sempre por leitura; a regra só os nomeia para isso."""
        resto = REGRA.replace(DECISOES_SO_PRESENCA, "")
        for termo in ("etapa", "fidelidade", "contradição"):
            self.assertNotIn(termo, resto.lower())

    def test_decisoes_ok_dispensa_so_a_presenca(self):
        """C-1: `decisões: ok` não fecha a contradição literal, que segue por leitura (volta 2, item 1)."""
        self.assertIn(DECISOES_SO_PRESENCA, REGRA)

    def test_c3_achado_contra_campo_ok_so_com_a_linha_do_comando(self):
        self.assertIn("achado por leitura contra esse campo só existe com a linha do comando que o contradiz, "
                      "copiada no achado; sem ela, não há achado, nem `tardio:`", REGRA)

    def test_c4_hash_aprovado_dispensa_so_forma_e_corte_e_fato_novo_reprova(self):
        dispensa = re.search(r"já aprovado numa rodada anterior não reprova por (\w+) nem por (\w+);", REGRA)
        self.assertEqual(dispensa.groups() if dispensa else None, ("forma", "corte"))
        fatos = REGRA.split("fato novo do disco reprova sempre")[1]
        for fato in ("decisão do dono posterior", "arquivo `Ler` ausente ou com sha diferente", "pedido alterado"):
            self.assertIn(fato, fatos)

    def test_c8_ate_14_linhas_e_sem_ordem_de_ignorar_o_comando(self):
        self.assertLessEqual(len(TEXTO.splitlines()), LINHAS_DA_BASE + 14)
        for imperativo in ("ignor", "pule", "dispense", "não rode", "deixe de"):
            self.assertNotIn(imperativo, REGRA.lower())


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
