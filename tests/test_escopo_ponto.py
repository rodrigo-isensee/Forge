"""E23.17 (v0457): três defeitos da conferência de entrega (`forge-check entrega --pedido`).

(a) o escopo declarado não tira o ponto inicial de caminho (`.github/...`), só a pontuação final; (b) na etapa codigo, a volta na mesma
branch herda o escopo dos briefs de codigo selados antes, do mesmo pedido, nunca o de outra branch, de outro pedido ou de outra etapa;
(c) na merge-integracao, os pareceres são achados pelo pedido do brief, como no `forge-check pr <pedido>`, e não pelo slug da branch.
Repositórios temporários, sem rede."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_selo_e_entrega import Repositorio as RepositorioSelado  # noqa: E402
from test_volta_por_delta import Repositorio as RepositorioDaEntrega  # noqa: E402
from test_conf_escopo import PARECER, OK_INTEGRACAO, SEM_PARECER  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

UNIDO = "anterior da mesma branch: escopo unido"


class Conferencia(RepositorioSelado):
    def conferir(self, etapa="codigo"):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", etapa, "--sem-gravar")

    def selar_copia(self, nome, trocas, selar=True):
        """Uma cópia do brief 1 com `trocas` (de -> para) gravada em docs/briefs/<nome>; selada pela ferramenta ou, com `selar=False`, pela
        linha do Histórico escrita à mão (o selo de um brief que a ferramenta recusaria, como o de outro pedido)."""
        texto = (self.proj / "docs/briefs/exemplo-node-backend-1.md").read_text(encoding="utf-8")
        for de, para in trocas.items():
            self.assertIn(de, texto)
            texto = texto.replace(de, para)
        arq = self.gravar(f"docs/briefs/{nome}", texto)
        if selar:
            rc, saida = self.selar(arq)
            self.assertEqual(rc, 0, saida)
        else:
            sha = hashlib.sha256(arq.read_bytes()).hexdigest()
            pedido = self.proj / "docs/pedidos/exemplo.md"
            pedido.write_text(self.pedido() + f"- 2026-01-01 09:30: brief selado docs/briefs/{nome} {sha}\n", encoding="utf-8")
        return arq

    def primeira_entrega_e_volta(self, antes_da_volta=None):
        """O brief 1 declara `bin/app, docs/notas/`; a volta (brief 2, mesma branch e pedido, o selo mais recente) declara só `volta.txt`."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        if antes_da_volta:
            antes_da_volta()
        self.entregar()
        self.gravar("volta.txt", "v\n")
        self.git("add", "volta.txt")
        self.commit("fix: volta")
        self.selar_copia("exemplo-node-backend-2.md", {"- arquivos: bin/app, docs/notas/": "- arquivos: volta.txt"})


class PontoInicial(Conferencia):
    """(a)"""

    def test_caminho_com_ponto_inicial_e_pontuacao_final(self):
        self.brief(arquivos="`.github/workflows/ci.yml`, ./bin/app; docs/notas/.")
        self.assertEqual(self.selar()[0], 0)
        self.gravar(".github/workflows/ci.yml", "on: push\n")
        self.entregar(".github")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        for linha in ('escopo: ok (declarado no brief: .github/workflows/ci.yml) ".github/workflows/ci.yml"',
                      'escopo: ok (declarado no brief: bin/app) "bin/app"', 'escopo: ok (declarado no brief: docs/notas/) "docs/notas/a.md"'):
            self.assertIn(linha, saida)


class VoltaNaMesmaBranch(Conferencia):
    """(b)"""

    def test_dois_briefs_da_mesma_branch_unem_o_escopo(self):
        self.primeira_entrega_e_volta()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"brief: {self.proj / 'docs/briefs/exemplo-node-backend-1.md'} (selado, {UNIDO})", saida)
        self.assertEqual(saida.count("exemplo-node-backend-2.md"), 1, saida)  # o brief da volta é o principal, não um anterior
        for linha in ('escopo: ok (declarado no brief: bin/app) "bin/app"', 'escopo: ok (declarado no brief: volta.txt) "volta.txt"'):
            self.assertIn(linha, saida)

    def test_brief_de_outra_branch_nao_entra_na_uniao(self):
        self.primeira_entrega_e_volta()
        self.gravar("outra.txt", "o\n")
        self.git("add", "outra.txt")
        self.commit("feat: outra")
        self.selar_copia("exemplo-node-backend-3.md", {"Branch: melhoria/x": "Branch: melhoria/y", "- arquivos: bin/app, docs/notas/": "- arquivos: outra.txt"},
                         selar=False)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "outra.txt"', saida)
        self.assertNotIn("exemplo-node-backend-3.md", saida)

    def test_brief_de_outro_pedido_nao_entra_na_uniao(self):
        self.primeira_entrega_e_volta(lambda: self.selar_copia("outro-node-backend-1.md", {
            "Pedido: exemplo": "Pedido: outro", "- arquivos: bin/app, docs/notas/": "- arquivos: outra.txt"}, selar=False))
        self.gravar("outra.txt", "o\n")
        self.git("add", "outra.txt")
        self.commit("feat: outra")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "outra.txt"', saida)
        self.assertNotIn("outro-node-backend-1.md", saida)

    def test_outra_etapa_nao_une_os_briefs_de_codigo(self):
        self.primeira_entrega_e_volta()
        self.selar_copia("exemplo-node-backend-4.md", {"Etapa: codigo": "Etapa: qa", "- arquivos: bin/app, docs/notas/": "- arquivos: volta.txt"},
                         selar=False)
        rc, saida = self.conferir("qa")
        self.assertIn("exemplo-node-backend-4.md", saida)
        self.assertNotIn(UNIDO, saida)
        self.assertIn('escopo: fora do declarado no brief "bin/app"', saida)


class PareceresPeloPedido(RepositorioDaEntrega):
    """(c): o pedido `p1` não é o slug `x` da branch."""

    def review(self, pedido):
        texto = PARECER.format(t="review", c=self.codigo, p="aprovado", extra="revisor: forge:tech-lead\n", achados="")
        self.commitar({"docs/reviews/x.md": texto.replace("pedido: x", f"pedido: {pedido}")}, "review")

    def setUp(self):
        super().setUp()
        self.codigo = self.commitar({"notas.md": "a\n"}, "trabalho")
        self.gravar_pedido()

    def test_parecer_com_o_pedido_do_brief_aprova(self):
        self.review("p1")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 0, saida)
        self.assertIn(OK_INTEGRACAO, saida)

    def test_parecer_de_outro_pedido_segue_reprovando(self):
        self.review("z")
        rc, saida = self.entrega(etapa="merge-integracao")
        self.assertEqual(rc, 1, saida)
        self.assertIn(SEM_PARECER, saida)
