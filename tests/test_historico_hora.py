"""P4 e P5 da 0.37 (E1 e E2): o `forge-check brief` avisa hora do `## Histórico` no futuro ou fora de ordem e o pedido
aberto depois da mudança sem a linha `DECISÃO DO DONO (...): recibo confirmado: "<resposta>"`. Só aviso: o rc não muda."""
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import FORGE_CHECK, Raiz  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "brief"
PEDIDO = (FIXTURES / "pedido.md").read_text(encoding="utf-8")
BRIEF = (FIXTURES / "etapa-outro-papel.md").read_text(encoding="utf-8")
DATA_DO_RECIBO = SourceFileLoader("forge_check_historico_hora", FORGE_CHECK).load_module().DATA_DO_RECIBO
ULTIMA_DECISAO = 'DECISÃO DO DONO (2026-01-02): "sem custo".\n'


class HistoricoERecibo(Raiz):
    def conferir(self, historico, decisao=""):
        """(rc, avisos de histórico e de recibo) do brief da fixture sobre o pedido com o `## Histórico` e a decisão dados."""
        pedido = PEDIDO.replace(ULTIMA_DECISAO, ULTIMA_DECISAO + decisao)
        self.gravar("docs/pedidos/pedido-sintetico.md", pedido + ("\n## Histórico\n" + historico if historico else ""))
        self.gravar("docs/briefs/pedido-sintetico-dev-exemplo-1.md", BRIEF)
        rc, saida, _ = self.rodar("brief", "docs/briefs/pedido-sintetico-dev-exemplo-1.md", "--pedido", "pedido-sintetico")
        return rc, [l for l in saida if l.startswith(("aviso: histórico:", "aviso: recibo:"))]

    def test_hora_no_futuro_avisa_sem_mudar_o_rc(self):
        rc_sem, avisos_sem = self.conferir("- 2026-01-01 10:00: aberto\n")
        rc, avisos = self.conferir("- 2026-01-01 10:00: aberto\n- 2099-01-01 00:00: hora inventada\n")
        self.assertEqual(avisos_sem, [])
        self.assertEqual(avisos, ["aviso: histórico: 2099-01-01 00:00 no futuro"])
        self.assertEqual(rc, rc_sem)

    def test_ordem_decrescente_avisa(self):
        _, avisos = self.conferir("- 2026-01-01 10:00: aberto\n- 2026-01-01 09:59: antes\n")
        self.assertEqual(avisos, ["aviso: histórico: 2026-01-01 09:59 antes da linha anterior (2026-01-01 10:00)"])

    def test_marcas_fora_da_forma_e_registro_tardio_nao_avisam(self):
        _, avisos = self.conferir("- 2026-01-01 10:00: aberto\n- 2026-01-01 11:2x: minuto incerto\n- 2026-01-01: sem hora\n"
                                  "- 2026-01-01 10:05: cita 09:00 e 2099-01-01 00:00 no texto\n"
                                  "- 2026-01-01 08:00: registro tardio de 08:00\n- 2026-01-01 10:06: segue\n")
        self.assertEqual(avisos, [])

    def test_historico_em_ordem_com_mesmo_minuto_nao_avisa(self):
        _, avisos = self.conferir("- 2026-01-01 10:00: aberto\n- 2026-01-01 10:00: mesmo minuto\n- 2026-01-02 08:00: dia seguinte\n")
        self.assertEqual(avisos, [])

    def test_recibo(self):
        aviso = 'aviso: recibo: o pedido não tem a linha DECISÃO DO DONO (<data hora>): recibo confirmado: "<resposta literal>" (R-DECISAO)'
        hoje = f"- {DATA_DO_RECIBO} 00:00: aberto\n"
        casos = [("sem a linha", hoje, "", [aviso]),
                 ("com a resposta", hoje, f'DECISÃO DO DONO ({DATA_DO_RECIBO} 00:00): recibo confirmado: "isso"\n', []),
                 ("resposta vazia", hoje, f'DECISÃO DO DONO ({DATA_DO_RECIBO} 00:00): recibo confirmado: ""\n', [aviso]),
                 ("resposta do modelo", hoje, 'DECISÃO DO DONO (AAAA-MM-DD HH:MM): recibo confirmado: "<resposta literal>"\n', [aviso]),
                 ("citada fora da linha de decisão", hoje, 'nota: recibo confirmado: "isso"\n', [aviso]),
                 ("pedido anterior à mudança", "- 2026-01-01 10:00: aberto\n", "", []),
                 ("sem Histórico datado", "", "", [])]
        for nome, historico, decisao, esperado in casos:
            with self.subTest(nome):
                avisos = self.conferir(historico, decisao)[1]
                self.assertEqual([a for a in avisos if a.startswith("aviso: recibo:")], esperado)  # a data do recibo pode estar no futuro

    def test_decisao_comum_nao_vale_como_recibo(self):  # o pedido da fixture já tem duas DECISÃO DO DONO comuns
        _, avisos = self.conferir(f"- {DATA_DO_RECIBO} 00:00: aberto\n", f'DECISÃO DO DONO ({DATA_DO_RECIBO} 00:00): "isso"\n')
        self.assertEqual(len([a for a in avisos if a.startswith("aviso: recibo:")]), 1)


if __name__ == "__main__":
    unittest.main()
