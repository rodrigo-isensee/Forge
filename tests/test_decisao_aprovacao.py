"""P-N4 (PN4-DECISAO-APROVACAO): o brief aprovado é comparado com as decisões do dono que valiam na hora da aprovação (a última linha
`aprovado` dele em docs/kanban/conferencias.md); a decisão posterior que falta sai como aviso. Biblioteca padrão, sem rede."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
ANTES = 'DECISÃO DO DONO 2026-01-01 09:00: "A".'
DEPOIS = 'DECISÃO DO DONO 2026-01-01 11:00: "B".'
PEDIDO = f"""---
id: exemplo
---
# Pedido EXEMPLO
Modo: implementar

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E1.1 (dev-exemplo): implementação do recurso X.

## Decisões do usuário (registro literal)
- {ANTES}
- {DEPOIS}
"""
CABECALHO = "| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota | classe | autor |\n|---|---|---|---|---|---|---|---|---|---|\n"


def brief(*decisoes):
    return ("Agente destino: forge:dev-exemplo\n\n## Objetivo\nExemplo.\n\n## Ler\n- o pedido.\n\n## Entregar\n- Fazer o recurso X (E1.1).\n\n"
            "## Fora do escopo\n- nada.\n\n## Decisões e restrições\n" + "".join(f"- {d}\n" for d in decisoes)
            + "\n## Pronto quando\n- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.\n\n## Relatório\nAté 8 linhas.\n")


def linha(hora, resultado="aprovado", nome="exemplo-dev-exemplo-1", modo="brief"):
    return f"| {hora} | exemplo | {nome} | {modo} | 1 | {resultado} | s | — | — | jarvis |\n"


class DecisaoPosteriorAprovacao(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-pn4-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedido = self.gravar("docs/pedidos/exemplo.md", PEDIDO)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def conferir(self, *linhas, decisoes=(ANTES,)):
        if linhas:
            self.gravar("docs/kanban/conferencias.md", CABECALHO + "".join(linhas))
        arq = self.gravar("docs/briefs/exemplo-dev-exemplo-1.md", brief(*decisoes))
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))}
        env["HOME"] = str(self.tmp / "home")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "brief", str(arq), "--pedido", str(self.pedido)],
                           capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout

    def assertCobrada(self, rc, saida, hora="11:00"):
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'decisões: falta "DECISÃO DO DONO 2026-01-01 {hora}', saida)
        self.assertNotIn("posterior à aprovação", saida)

    def test_aprovado_com_decisao_posterior_avisa_e_passa(self):
        rc, saida = self.conferir(linha("2026-01-01 08:00", "reprovado"), linha("2026-01-01 10:00"))
        self.assertIn('decisões: decisão posterior à aprovação 2026-01-01 10:00: "DECISÃO DO DONO 2026-01-01 11:00:', saida)
        self.assertNotIn("decisões: falta", saida)
        self.assertEqual(rc, 0, saida)

    def test_aprovado_com_decisao_anterior_faltando_reprova(self):
        rc, saida = self.conferir(linha("2026-01-01 10:00"), decisoes=(DEPOIS,))
        self.assertCobrada(rc, saida, "09:00")

    def test_sem_aprovacao_cobra_tudo(self):
        self.assertCobrada(*self.conferir())

    def test_vale_a_ultima_aprovacao(self):
        self.assertCobrada(*self.conferir(linha("2026-01-01 10:00"), linha("2026-01-01 12:00")))

    def test_hora_igual_a_da_aprovacao_segue_cobrada(self):
        self.assertCobrada(*self.conferir(linha("2026-01-01 11:00")))

    def test_decisao_sem_hora_segue_cobrada(self):
        self.pedido = self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("2026-01-01 11:00", "(2026-01-02)"))
        rc, saida = self.conferir(linha("2026-01-01 10:00"))
        self.assertIn('decisões: falta "DECISÃO DO DONO (2026-01-02)', saida)
        self.assertEqual(rc, 1, saida)

    def test_reprovacao_outro_brief_outro_modo_ou_hora_torta_nao_valem_como_aprovacao(self):
        for falsa in (linha("2026-01-01 10:00", "reprovado"), linha("2026-01-01 10:00", nome="exemplo-dev-exemplo-2"),
                      linha("2026-01-01 10:00", "cumpriu", modo="entrega"), linha("2026")):
            with self.subTest(falsa=falsa):
                self.assertCobrada(*self.conferir(falsa))


if __name__ == "__main__":
    unittest.main()
