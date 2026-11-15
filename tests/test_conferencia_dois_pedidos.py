"""CONFERENCIA-DOIS-PEDIDOS (v047, E1.277): a conferência numa branch cujos briefs citam dois pedidos.

1. `pedido_da_conferencia`: sem arquivo do pedido do argumento (a release) e com briefs de dois pedidos na branch, a conferência é do único
   pedido com brief de `Etapa: codigo` na branch; sem esse um só, segue a falha fechada.
2. `entrega --etapa codigo`: o parecer de portão gravado na branch é anexo quando um brief selado do portão (deste pedido ou de outro
   que cita a branch) manda gravá-lo: declara o arquivo, e o `pedido:` e o `commit:` do frontmatter são os do brief."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_selo_e_entrega as base  # noqa: E402

fc = base.fc
LIMPO = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))}


class PedidoDaConferencia(unittest.TestCase):
    """O pedido da conferência pelos briefs da branch, com dois pedidos."""

    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-dois-")).resolve()
        self.addCleanup(shutil.rmtree, self.raiz, True)
        subprocess.run(["git", "init", "-q", str(self.raiz)], check=True, env=LIMPO | {"GIT_CONFIG_NOSYSTEM": "1",
                                                                                       "GIT_CONFIG_GLOBAL": os.devnull})
        for pedido in ("a", "b"):
            self.gravar(f"docs/pedidos/{pedido}.md", f"---\nid: {pedido}\n---\n# {pedido}\n\n## Histórico\n- 2026-01-01 09:00: aberto\n")
        self.n = 0
        for trava in (mock.patch.object(fc, "RAIZES_DE_BRIEF", ()), mock.patch.dict(os.environ, LIMPO, clear=True)):  # AR-4: sem o GIT_ herdado
            trava.start()
            self.addCleanup(trava.stop)

    def gravar(self, rel, texto):
        arq = self.raiz / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def brief(self, pedido, etapa, branch="melhoria/x"):
        self.n += 1
        self.gravar(f"docs/briefs/{pedido}-{self.n}.md", f"Pedido: {pedido}\nBranch: {branch}   Base: develop\nEtapa: {etapa}\n\n## Objetivo\nx\n")

    def conferencia(self):
        caminho, texto, problema = fc.pedido_da_conferencia(self.raiz, "release-9.9.9", "melhoria/x")
        return (caminho.stem if caminho else None), problema

    def test_dois_pedidos_um_so_com_codigo_e_o_da_conferencia(self):
        self.brief("a", "review")
        self.brief("a", "qa")
        self.brief("b", "codigo")
        self.brief("b", "review")
        self.assertEqual(self.conferencia(), ("b", None))

    def test_dois_pedidos_com_codigo_falha_fechado(self):
        self.brief("a", "codigo")
        self.brief("b", "codigo")
        caminho, problema = self.conferencia()
        self.assertIsNone(caminho)
        self.assertIn('citam mais de um pedido ("a", "b")', problema)

    def test_dois_pedidos_sem_codigo_falha_fechado(self):
        self.brief("a", "review")
        self.brief("b", "qa")
        caminho, problema = self.conferencia()
        self.assertIsNone(caminho)
        self.assertIn('citam mais de um pedido ("a", "b")', problema)

    def test_um_pedido_sem_codigo_segue_valendo(self):
        self.brief("a", "review")
        self.brief("b", "codigo", branch="melhoria/y")
        self.assertEqual(self.conferencia(), ("a", None))

    def test_sem_brief_da_branch_nao_ha_pedido(self):
        self.brief("a", "codigo", branch="melhoria/y")
        self.assertEqual(self.conferencia(), (None, None))

    def test_sem_branch_nao_le_os_briefs(self):
        """Sem branch achada, nenhum brief vale, nem o que não tem linha `Branch:`."""
        self.gravar("docs/briefs/a-1.md", "Pedido: a\nEtapa: codigo\n\n## Objetivo\nx\n")
        self.assertEqual(fc.pedido_da_conferencia(self.raiz, "release-9.9.9", None), (None, None, None))

    def test_brief_ilegivel_e_pulado(self):
        self.brief("a", "codigo")
        (self.raiz / "docs/briefs/b-9.md").write_bytes(b"Pedido: b\nBranch: melhoria/x\n\xff\xfe\n")
        self.assertEqual(self.conferencia(), ("a", None))


class ParecerMandadoPeloPortao(base.Conferencia):
    """O parecer de portão da branch com `pedido:` da release e `commit:` fora do Revisar-sha, como na melhoria/mp1311-554-revalidacao."""

    RELEASE = "release-9.9.9"

    def setUp(self):
        super().setUp()
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.revisado = self.git("rev-parse", "HEAD")
        self.n = 10

    def portao(self, pedido="exemplo", papel="tech-lead", etapa="review", arquivos="docs/reviews/x.md", manda=None, selar=True, selo_em=None):
        """Um brief do portão desta branch, copiado do brief 1, que manda gravar `docs/reviews/x.md` com o `manda` no Entregar."""
        self.n += 1
        manda = manda if manda is not None else f"pedido: {self.RELEASE}, branch: melhoria/x, commit: {self.revisado}"
        texto = (self.proj / "docs/briefs/exemplo-node-backend-1.md").read_text(encoding="utf-8")
        for de, para in {"Etapa: codigo": f"Revisar-sha: {self.base}\nEtapa: {etapa}", "Agente destino: forge:node-backend":
                         f"Agente destino: forge:{papel}", "Pedido: exemplo": f"Pedido: {pedido}", "- arquivos: bin/app, docs/notas/":
                         f"- arquivos: {arquivos}", "- a função f em bin/app (E1.1)": f"- gravar docs/reviews/x.md: {manda}"}.items():
            self.assertIn(de, texto)
            texto = texto.replace(de, para)
        nome = f"{pedido}-portao-{self.n}.md"
        arq = self.gravar(f"docs/briefs/{nome}", texto)
        if selar:
            rel = f"docs/pedidos/{selo_em or pedido}.md"
            atual = (self.proj / rel).read_text(encoding="utf-8") if (self.proj / rel).exists() else \
                f"---\nid: {pedido}\n---\n# {pedido}\n\n## Histórico\n- 2026-01-01 09:00: aberto\n"
            sha = base.hashlib.sha256(arq.read_bytes()).hexdigest()
            self.gravar(rel, atual + f"- 2026-01-01 09:30: brief selado docs/briefs/{nome} {sha}\n")

    def parecer(self, pedido=None, commit=None, parecer="aprovado"):
        rel = "docs/reviews/x.md"
        self.gravar(rel, f"---\ntipo: review\ncontrato: 1\npedido: {pedido or self.RELEASE}\nbranch: melhoria/x\n"
                         f"commit: {commit or self.revisado}\nparecer: {parecer}\n---\n# parecer\n")
        self.git("add", rel)
        self.commit("docs(review): parecer")

    def assert_anexo(self):
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de tech-lead mandado por brief selado do portão da branch) "docs/reviews/x.md"', saida)

    def assert_fora(self):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "docs/reviews/x.md"', saida)

    def test_mandado_pelo_portao_do_pedido_e_anexo(self):
        self.portao()
        self.parecer()
        self.assert_anexo()

    def test_mandado_pelo_portao_de_outro_pedido_da_branch_e_anexo(self):
        self.portao(pedido="outro", manda=f"commit: {self.revisado}")
        self.parecer(pedido="outro")
        self.assert_anexo()

    def test_brief_do_outro_pedido_sem_selo_nao_ancora(self):
        self.portao(pedido="outro", manda=f"commit: {self.revisado}", selar=False)
        self.parecer(pedido="outro")
        self.assert_fora()

    def test_brief_selado_no_pedido_errado_nao_ancora(self):
        """O selo no exemplo de um brief com `Pedido: outro` (e sem docs/pedidos/outro.md) não é registro de nenhum dos dois."""
        self.portao(pedido="outro", manda=f"commit: {self.revisado}", selo_em="exemplo")
        self.parecer(pedido="exemplo")
        self.assert_fora()

    def test_arquivo_nao_declarado_pelo_portao_segue_fora(self):
        self.portao(arquivos="docs/reviews/y.md")
        self.parecer()
        self.assert_fora()

    def test_pedido_que_o_portao_nao_mandou_segue_fora(self):
        self.portao()
        self.parecer(pedido="forjado")
        self.assert_fora()

    def test_commit_que_o_portao_nao_mandou_segue_fora(self):
        self.portao()
        self.parecer(commit="e" * 40)  # nem o Revisar-sha (o Base-sha) nem o commit: do Entregar
        self.assert_fora()

    def test_brief_de_outro_papel_nao_ancora(self):
        self.portao(papel="qa-engineer")
        self.parecer()
        self.assert_fora()

    def test_parecer_com_veredito_invalido_segue_fora(self):
        self.portao()
        self.parecer(parecer="pendente")
        self.assert_fora()

    def test_parecer_sem_frontmatter_segue_fora(self):
        self.portao()
        self.gravar("docs/reviews/x.md", "# parecer sem frontmatter\n")
        self.git("add", "docs/reviews/x.md")
        self.commit("docs(review): sem frontmatter")
        self.assert_fora()

    def test_veredito_trocado_no_mesmo_commit_segue_fora(self):
        self.portao()
        self.parecer(parecer="reprovado")
        self.parecer()
        self.assert_fora()

    def test_fora_da_etapa_de_codigo_nao_e_anexo(self):
        self.portao()
        self.parecer()
        self.selar_copia("exemplo-node-backend-2.md", {"Etapa: codigo": "Etapa: pr"}, selar=False)
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "pr", "--so-leitura")
        self.assertIn("exemplo-node-backend-2.md", saida)
        self.assertIn('escopo: fora do declarado no brief "docs/reviews/x.md"', saida)


if __name__ == "__main__":
    unittest.main()
