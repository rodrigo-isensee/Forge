"""Segurança da auditoria (v0478 E113.1): três brechas do hooks/conformidade.py, cada uma com as fixtures dela.

S22 (CONFORMIDADE-S22-FLUXO): a troca de branch vale certa só quando o operador garante que ela rodou.
A20 (CONFORMIDADE-A20-RESTO-BARRA-OPACO): o resto com barra depois do opaco que cai no .git recusa como o literal.
RESTO-SOBE (CONFORMIDADE-RESTO-SOBE): o resto que sobe com `..` depois do opaco vale resolvido.
Volta única da E113.6 (achados dos três portões): S22-MERGE (com duas candidatas de integração vale a da regra mais
dura), S22-NEG (a troca negada), S22-SUB (o subshell: a cadeia segue pelo `)`, sem falso positivo), RESTO-ANULA (o
resto que se anula ou sobe vale como o opaco sem resto) e A20-MAIS (a atribuição com `+=`).
As fixtures moram em tests/hooks/conformidade/ (a suíte inteira as roda em test_hooks); aqui, só as de cada cartão,
pelo prefixo da descrição, para a mutação do diff rodar rápido."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_hooks  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_hooks import FIXTURES, Fixture  # noqa: E402


def lote(prefixo):
    """(nome, Fixture) das fixtures do conformidade cuja descrição começa por `prefixo`."""
    fixtures = [Fixture(p) for p in sorted((FIXTURES / "conformidade").glob("*.json"))]
    return [(f"{f.hook}/{f.caminho.stem}", f) for f in fixtures if f.dados.get("descricao", "").startswith(prefixo)]


class SegurancaDaAuditoria(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def conferir(self, prefixo, recusam, liberam):
        casos = lote(prefixo)
        livres = [n for n, f in casos if f.dados["esperado"]["codigo"] == 0]
        self.assertGreaterEqual(len(casos) - len(livres), recusam, f"{prefixo} formas recusadas")
        self.assertGreaterEqual(len(livres), liberam, f"{prefixo} formas livres")
        self.assertEqual(self.executar_em_lote(casos), len(casos))

    def test_s22_troca_de_branch_so_vale_com_o_operador_que_garante(self):
        self.conferir("S22:", recusam=5, liberam=2)

    def test_a20_resto_com_barra_depois_do_opaco_no_git_recusa_como_o_literal(self):
        self.conferir("A20:", recusam=9, liberam=2)

    def test_resto_sobe_depois_do_opaco_vale_resolvido(self):
        self.conferir("RESTO-SOBE:", recusam=5, liberam=1)

    def test_s22_merge_com_duas_candidatas_de_integracao_vale_a_mais_dura(self):
        self.conferir("S22-MERGE:", recusam=12, liberam=4)

    def test_s22_troca_negada_nao_vale(self):
        self.conferir("S22-NEG:", recusam=5, liberam=1)

    def test_s22_subshell_segue_a_cadeia_so_com_o_comeco_que_garante(self):
        self.conferir("S22-SUB:", recusam=9, liberam=5)

    def test_resto_que_se_anula_ou_sobe_vale_como_o_opaco_sem_resto(self):
        self.conferir("RESTO-ANULA:", recusam=10, liberam=4)

    def test_a20_atribuicao_com_mais_igual_junta_os_pedacos(self):
        self.conferir("A20-MAIS:", recusam=7, liberam=2)


if __name__ == "__main__":
    unittest.main()
