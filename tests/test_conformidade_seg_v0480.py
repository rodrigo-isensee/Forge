"""Segurança da auditoria (v0478 E113.1): três brechas do hooks/conformidade.py, cada uma com as fixtures dela.

S22 (CONFORMIDADE-S22-FLUXO): a troca de branch vale certa só quando o operador garante que ela rodou.
A20 (CONFORMIDADE-A20-RESTO-BARRA-OPACO): o resto com barra depois do opaco que cai no .git recusa como o literal.
RESTO-SOBE (CONFORMIDADE-RESTO-SOBE): o resto que sobe com `..` depois do opaco vale resolvido.
Volta única da E113.6 (achados dos três portões): S22-MERGE (com duas candidatas de integração vale a da regra mais
dura), S22-NEG (a troca negada), S22-SUB (o subshell: a cadeia segue pelo `)`, sem falso positivo), RESTO-ANULA (o
resto que se anula ou sobe vale como o opaco sem resto) e A20-MAIS (a atribuição com `+=`).
Segunda volta (E113.11, achados da segurança E113.8): S22-PRIMEIRO (a troca sai do subshell só se é o primeiro comando
dele: `exit` ou `exec` antes dela), S22-CD (o `cd` dentro de `( … )` fica nele) e A5-COPIA (a cópia recursiva para
variável de fora da linha recusa como a de arquivo).
Terceira volta (E113.15, achados da segurança E113.13): A6-PASTA (o `cd` de um lado de pipe ou da lista que termina em
`&` fica no subshell), A7-VOLTA (`cd -`, `cd ~-`, `popd` e `pushd` sem pasta: o comando depois recusa), A5-RESTO (as
abreviações longas do `cp` e o `-t` colado) e A8-EXTRAI (`tar -C`, `unzip -d` e `rsync -r` para variável de fora).
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

    def test_s22_troca_so_sai_do_subshell_se_e_o_primeiro_comando(self):
        self.conferir("S22-PRIMEIRO:", recusam=9, liberam=2)

    def test_s22_cd_dentro_do_subshell_fica_nele(self):
        self.conferir("S22-CD:", recusam=5, liberam=2)

    def test_a5_copia_recursiva_para_opaco_sem_resto_recusa(self):
        self.conferir("A5-COPIA:", recusam=5, liberam=4)

    def test_a6_cd_de_pipe_ou_segundo_plano_fica_no_subshell(self):
        self.conferir("A6-PASTA:", recusam=8, liberam=3)

    def test_a7_volta_de_pasta_desconhecida_recusa_o_comando_depois(self):
        self.conferir("A7-VOLTA:", recusam=5, liberam=6)

    def test_a5_copia_com_opcao_abreviada_ou_alvo_colado_recusa(self):
        self.conferir("A5-RESTO:", recusam=8, liberam=2)

    def test_a8_extracao_para_opaco_sem_resto_recusa(self):
        self.conferir("A8-EXTRAI:", recusam=4, liberam=3)


if __name__ == "__main__":
    unittest.main()
