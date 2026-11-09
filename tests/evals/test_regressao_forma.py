"""Evals de regressão (0.43.1, frente I): cada erro de FORMA recorrente do catálogo do Jarvis (ERROS-JARVIS.md, linhas
ERRO-JARVIS dos pedidos e o estudo de causas C1 a C15) vira uma entrada real que antes passava errada e agora a ferramenta
tem de barrar ou corrigir sozinha.

Regra do módulo: o caso que a ferramenta já barra é um teste comum (regressão: se a trava sumir, a suíte cai). O caso
que ela ainda não barra fica com `@unittest.expectedFailure` e o nome do erro no docstring: é o backlog visível. Quando
uma frente implementar a trava, o teste passa a "sucesso inesperado", a suíte reprova e quem implementou tira o decorador
na mesma entrega (a trava nasce com a prova). Nenhum caso aqui implementa trava.

Cada classe cita `EJ <n>` (item de ERROS-JARVIS.md) e `C<n>` (causa do estudo 2-erros). Só biblioteca padrão, sem rede."""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTES))  # os apoios de tests/ também no modo `tests.evals.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)
import test_forge as tf  # noqa: E402  (módulo, não as classes: os testes dele não rodam de novo aqui)
import test_volta_por_delta as tvd  # noqa: E402

RAIZ = TESTES.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
FORGE_CHANGELOG = str(RAIZ / "bin" / "forge-changelog")
FIXTURES = TESTES / "fixtures" / "brief"
PEDIDO = (FIXTURES / "pedido.md").read_text(encoding="utf-8")
BRIEF = (FIXTURES / "etapa-outro-papel.md").read_text(encoding="utf-8")
ARQ_BRIEF = "docs/briefs/pedido-sintetico-dev-exemplo-1.md"
SHA_C = "c" * 40
CABECALHO = f"Etapa: codigo   Cobre: E1.1\nBranch: melhoria/x   Base: develop   Base-sha: {SHA_C}\n"
HASH = "a" * 64
MENSAGEM = (f"modo: brief\nPedido: pedido-sintetico\nAgente destino: forge:dev-exemplo\n"
            f"Arquivo: /r/{ARQ_BRIEF}\nBrief-sha256: {HASH}\nEtapa: codigo")


def carregar_hook_agentes():
    """`hooks/agentes.py` como módulo (o `_comum` vem da mesma pasta)."""
    sys.path.insert(0, str(RAIZ / "hooks"))
    spec = importlib.util.spec_from_file_location("forge_hook_agentes_evals", RAIZ / "hooks" / "agentes.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class RaizSintetica(unittest.TestCase):
    """Raiz temporária com o pedido e o brief das fixtures; `conferir` roda `forge-check brief` como o conferente."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-evals-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def rodar(self, *args):
        env = dict(os.environ, HOME=str(self.tmp / "home"))
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), *args], capture_output=True, text=True, env=env, timeout=120)
        return r.returncode, r.stdout

    def conferir(self, brief=BRIEF, pedido=PEDIDO):
        self.gravar("docs/pedidos/pedido-sintetico.md", pedido)
        self.gravar(ARQ_BRIEF, brief)
        return self.rodar("brief", ARQ_BRIEF, "--pedido", "pedido-sintetico")

    def assertBarra(self, rc, saida, trecho=None):
        """Barrar = reprovar (rc 1); o `trecho`, se dado, diz por quê na saída."""
        self.assertEqual(rc, 1, saida)
        if trecho:
            self.assertIn(trecho, saida)



class Controle(RaizSintetica):
    def test_o_brief_da_fixture_passa(self):  # sem este controle, todo "barra" abaixo passaria por acaso
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)


class DecisaoDoDonoFaltando(RaizSintetica):
    """EJ 9-12, 25, 28, 42, 56, 62, 74 · C1 (a causa mais frequente: brief derivado sem a decisão nova do dono)."""

    def test_brief_sem_a_decisao_nova_reprova(self):
        rc, saida = self.conferir(BRIEF.replace('- DECISÃO DO DONO (2026-01-02): "sem custo".\n', ""))
        self.assertBarra(rc, saida, 'decisões: falta "DECISÃO DO DONO (2026-01-02)')


class ResiduoDoMolde(RaizSintetica):
    """EJ 5, 13, 34, 39, 52, 69, 73 · C2 (molde ou gerador herdando texto de outro brief)."""

    def test_bloco_gerado_sem_preencher_reprova(self):
        rc, saida = self.conferir(BRIEF.replace("em um commit (E1, E1.1).", "em um commit (E1, E1.1). PREENCHER"))
        self.assertBarra(rc, saida, "forma: bloco gerado sem preencher (PREENCHER)")

    def test_worktree_de_outra_branch_no_brief_reprova(self):
        """ERRO EJ 34 (resíduo de worktree de outra correção): o brief da melhoria/x manda trabalhar na worktree de outra branch."""
        brief = BRIEF.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1)
        brief = brief.replace("## Entregar\n", "## Entregar\n- Trabalhe em ~/.forge-contrib/wt/outra-correcao-antiga.\n", 1)
        self.assertBarra(*self.conferir(brief), "worktree: o brief da")


class ContradicaoComOPedido(RaizSintetica):
    """EJ 5, 52, 53 · C2 (Fora do escopo ou NÃO tocar herdado contradiz o desenho do pedido)."""

    def test_entregar_que_manda_o_que_o_pedido_exclui_reprova(self):
        pedido = PEDIDO.replace("## Etapas", "## Fora do escopo\n- E2. a documentação fica para depois.\n\n## Etapas", 1)
        rc, saida = self.conferir(pedido=pedido)
        self.assertBarra(rc, saida, "contradição: o Entregar manda E2")


class EtapaDeOutroPapel(RaizSintetica):
    """EJ 61 · C14 (etapa ou papel errado: brief de código que manda fazer a revisão)."""

    def test_entregar_com_etapa_de_outro_papel_reprova(self):
        brief = BRIEF.replace("- Documentação do recurso A (E2).", "- Documentação do recurso A (E2).\n- Revisão de código da branch (E3.1).")
        rc, saida = self.conferir(brief)
        self.assertBarra(rc, saida, "etapa: papel errado E3.1")


class HoraDoHistorico(RaizSintetica):
    """EJ 22, 63, 79, 94 · C12 (hora estimada ou no futuro no Histórico: 5 repetições depois da prevenção escrita)."""
    FUTURO = "\n## Histórico\n- 2026-01-01 10:00: aberto\n- 2099-01-01 00:00: hora inventada\n"

    def test_hora_no_futuro_e_acusada(self):
        rc, saida = self.conferir(pedido=PEDIDO + self.FUTURO)
        self.assertIn("histórico: 2099-01-01 00:00 no futuro", saida)

    def test_hora_no_futuro_reprova(self):
        """ERRO EJ 63/79 (hora escrita sem date): só avisava e o brief seguia aprovado; reprova desde a 0.43.3."""
        self.assertBarra(*self.conferir(pedido=PEDIDO + self.FUTURO), "histórico: 2099-01-01 00:00 no futuro (hora escrita sem `date`")


class BranchDoBrief(RaizSintetica):
    """EJ 1, 2, 100 · C2 (nome de branch fora do desenho; `melhoria/melhoria/...` custou ~40 min na 0.43)."""

    def test_prefixo_melhoria_duplicado_reprova(self):
        """ERRO EJ 1/100 (branch com prefixo duplicado)."""
        brief = BRIEF.replace("Agente destino: forge:dev-exemplo\n",
                              "Agente destino: forge:dev-exemplo\n" + CABECALHO.replace("melhoria/x", "melhoria/melhoria/x"), 1)
        self.assertBarra(*self.conferir(brief), "branch: prefixo duplicado")


class PareceresPresosAoHead(RaizSintetica):
    """EJ 33, 84 · C5 (`commit:` do parecer lido do HEAD vivo com pareceres em série na mesma worktree: 5 repetições)."""

    def test_brief_que_manda_gravar_commit_do_head_antes_do_commit_reprova(self):
        """ERRO EJ 84 (commit: do parecer lido do HEAD vivo numa sequência)."""
        brief = BRIEF.replace("## Pronto quando\n", "## Pronto quando\n- PQ-4 (cmd): grave `commit:` com `git rev-parse HEAD` "
                              "antes do seu commit · espera: rc=0\n", 1)
        self.assertBarra(*self.conferir(brief), "parecer: `commit:` tirado de `rev-parse HEAD`")


class ProvasDoBrief(RaizSintetica):
    """EJ 89, 96, 101 · C7 e C2 (provas e escopo que o prevoo fora do repositório pega, e o forge-check não)."""

    def test_recomendado_condicional_sem_decisao_reprova(self):
        """ERRO EJ 89 (recomendado incluído no brief sem decisão, "só se couber no teto")."""
        brief = BRIEF.replace("- Documentação do recurso A (E2).", "- Documentação do recurso A (E2).\n- O A2 recomendado, só se couber no teto.")
        self.assertBarra(*self.conferir(brief), "escopo: recomendado condicional")

    def test_caminho_tmp_do_pq_fora_do_entregar_reprova(self):
        """ERRO EJ 96 (caminho do PQ diferente do criado no Entregar)."""
        brief = BRIEF.replace("## Pronto quando\n", "## Pronto quando\n- PQ-4 (cmd): `cd /tmp/sec-neutro/repo && git status` · espera: rc=0\n", 1)
        self.assertBarra(*self.conferir(brief), "que o Entregar não cria (EJ 96)")

    def test_log_de_pq_com_nome_generico_reprova(self):
        """ERRO EJ 101 (log de PQ com nome genérico no scratch comum, sobrescrito por outro agente)."""
        brief = BRIEF.replace("## Pronto quando\n", "## Pronto quando\n- PQ-4 (cmd): `python3 -m unittest tests.test_x > /tmp/pq4.log` · espera: rc=0\n", 1)
        self.assertBarra(*self.conferir(brief), "nome comum a todos os agentes")


class MensagemAoConferente(unittest.TestCase):
    """EJ 23, 35, 60, 64, 65, 93 · C4 (mensagem ao conferente fora do formato: 8 repetições depois da prevenção escrita)."""

    @classmethod
    def setUpClass(cls):
        cls.hook = carregar_hook_agentes()

    def test_controle_a_mensagem_do_forge_check_passa(self):
        self.assertIsNone(self.hook.mensagem_sem_forma(MENSAGEM))

    def test_texto_livre_e_barrado(self):  # EJ 23
        self.assertIn("`modo: brief` ou `modo: entrega` na primeira linha",
                      self.hook.mensagem_sem_forma(f"Confira o brief {ARQ_BRIEF}, por favor"))

    def test_varios_briefs_numa_mensagem_e_barrado(self):  # EJ 35, 60
        self.assertIn("um brief por mensagem", self.hook.mensagem_sem_forma(MENSAGEM + "\n\n" + MENSAGEM))

    def test_hash_preencher_e_barrado(self):  # EJ 65
        self.assertIn("Brief-sha256:", self.hook.mensagem_sem_forma(MENSAGEM.replace(HASH, "PREENCHER")))

    def test_nota_antes_do_cabecalho_e_barrada(self):  # EJ 64 (variante: texto antes do `modo:`)
        self.assertIsNotNone(self.hook.mensagem_sem_forma("Nota: rodada 2\n" + MENSAGEM))

    @unittest.expectedFailure
    def test_instrucao_ao_conferente_na_nota_e_barrada(self):
        """ERRO EJ 64 (instrução ao conferente na Nota da mensagem): a Nota só traz fato, nunca comando."""
        self.assertIsNotNone(self.hook.mensagem_sem_forma(MENSAGEM + "\nNota: rode o forge-check com --raiz /workspaces/Forge"))


class EtapaRedigitada(RaizSintetica):
    """EJ 23, 93 · C4 (Etapa redigitada na mensagem diferente da do brief)."""

    def test_etapa_diferente_da_do_brief_e_recusada(self):
        self.conferir(BRIEF.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1))
        rc, saida = self.rodar("brief", "mensagem", "--arquivo", ARQ_BRIEF, "--pedido", "pedido-sintetico", "--etapa", "seguranca")
        self.assertEqual(rc, 2, saida)


class VereditoDuplicado(RaizSintetica):
    """EJ 72, 78 · C11 (o mesmo veredito registrado duas vezes; a guarda escrita do EJ 72 não foi usada no EJ 78)."""
    REGISTRAR = ("conferencia", "registrar", "--pedido", "xpto", "--brief", "xpto-tech-lead-1", "--modo", "brief",
                 "--rodada", "1", "--resultado", "aprovado", "--merito", "—")

    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")

    def test_segundo_registro_da_mesma_chave_e_recusado(self):
        """ERRO EJ 72/78 (veredito registrado duas vezes): mesmo brief, modo e rodada."""
        self.assertEqual(self.rodar(*self.REGISTRAR)[0], 0)
        rc, saida = self.rodar(*self.REGISTRAR)
        linhas = (self.tmp / "docs" / "kanban" / "conferencias.md").read_text(encoding="utf-8").count("| xpto-tech-lead-1 | brief | 1 |")
        self.assertEqual((rc != 0, linhas), (True, 1), saida)


class DesdeDaEntrega(tvd.Repositorio):
    """EJ 3, 50, 51, 68, 80, 92 · C3 (Desde e intervalo da conferência errados: 8 repetições depois da prevenção escrita)."""

    def setUp(self):
        super().setUp()
        self.c1 = self.commitar({"a.txt": "1\n"}, "1a")
        self.c2 = self.commitar({"b.txt": "2\n"}, "2a")
        self.c3 = self.commitar({"c.txt": "3\n"}, "3a")

    def test_desde_que_nao_e_a_ultima_conferida_reprova(self):
        self.gravar_pedido([self.c1, self.c2])
        self.assertEqual(self.entrega(desde=self.c2)[0], 0)  # controle: a última conferida vale
        rc, saida = self.entrega(desde=self.c1)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    @unittest.expectedFailure
    def test_linha_conferida_com_prefixo_de_etapa_e_acusada(self):
        """ERRO EJ 29 ("entrega conferida" com prefixo de etapa): a linha fora da forma tem de ser apontada, não ignorada calada."""
        self.gravar_pedido(extra=f"- 2026-10-19 16:30: (E2.7) entrega conferida {self.c2}\n")
        rc, saida = self.entrega(desde=self.c2)
        self.assertIn("(E2.7)", saida)


class BaseShaForaDaBranch(tf.RepoComOrigem):
    """EJ 3, 68, 80 · C3 (Base-sha da develop atual em branch que nasceu antes ou empilhada)."""

    def brief_com_base(self, sha):
        pedido = self.home / ".forge-contrib" / "docs" / "pedidos" / "pedido-sintetico.md"
        pedido.parent.mkdir(parents=True, exist_ok=True)
        pedido.write_text(tf.PEDIDO, encoding="utf-8")
        texto = tf.BRIEF.replace("Agente destino: forge:dev-exemplo\n",
                                 f"Agente destino: forge:dev-exemplo\nBranch: melhoria/x   Base: develop   Base-sha: {sha}\n", 1)
        arq = self.repo / "docs" / "briefs" / f"{tf.ID}-dev-exemplo-1.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        r = tf.rodar_fc("brief", str(arq), "--pedido", str(pedido), "--destino", "forge:dev-exemplo", raiz=self.repo, home=self.home)
        return r.returncode, r.stdout

    def test_base_sha_da_develop_nova_reprova(self):
        nova = self.develop_anda({"src/y.txt": "y1 de outro\ny2\ny3\ny4\ny5\ny6\ny7\ny8\n"})
        rc, saida = self.brief_com_base(nova)
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"base: Base-sha {nova[:7]} não está na branch melhoria/x", saida)


class ParecerComCommitHead(tf.RepoComOrigem):
    """EJ 33, 84 · C5 (parecer gravado com `commit: HEAD` em vez do sha revisado)."""

    def test_controle_parecer_com_sha_passa(self):
        self.assertEqual(self.pr()[0], 0)

    def test_parecer_com_commit_head_reprova(self):
        self.pareceres("HEAD")
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1, saida)
        self.assertIn("docs/reviews/p1.md: commit: hash hexadecimal", saida)


class FragmentoDoChangelog(unittest.TestCase):
    """EJ 43, 46, 54, 70, 76 · C8 (fragmento com tipo inválido ou com o nome de outra branch: CI vermelho de 61 min e envios caídos)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-evals-cl-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.git("init", "-q", "-b", "develop")
        self.escrever("CHANGELOG.md", "# Changelog\n\n## [Não publicado]\n\n## [0.1.0] - 2026-01-01\n### Adicionado\n- x\n")
        self.escrever("agents/a.md", "a\n")
        self.escrever(".claude-plugin/plugin.json", '{"version": "0.1.0"}\n')
        self.commitar()
        self.git("switch", "-q", "-c", "melhoria/minha")
        self.escrever("agents/a.md", "b\n")

    def git(self, *args):
        env = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_AUTHOR_NAME": "t",
                              "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
        subprocess.run(["git", *args], cwd=self.tmp, env=env, capture_output=True, check=True)

    def escrever(self, rel, texto):
        (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.tmp / rel).write_text(texto, encoding="utf-8")

    def commitar(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "c")

    def conferir(self, nome, texto):
        self.escrever(f"changelog.d/{nome}", texto)
        self.commitar()
        env = {k: v for k, v in os.environ.items() if k not in ("GITHUB_HEAD_REF", "CI")}
        r = subprocess.run([sys.executable, "-I", FORGE_CHANGELOG, "conferir", "--base", "develop", "--branch=melhoria/minha"],
                           cwd=self.tmp, env=env, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_controle_fragmento_certo_passa(self):
        self.assertEqual(self.conferir("minha.md", "### Corrigido\n- x\n")[0], 0)

    def test_tipo_inexistente_reprova(self):  # EJ 46 ("### Mudado")
        rc, saida = self.conferir("minha.md", "### Mudado\n- x\n")
        self.assertEqual(rc, 1, saida)
        self.assertIn("tipo 'Mudado' inválido", saida)

    def test_fragmento_com_nome_de_outra_branch_reprova(self):  # EJ 43, 54, 70, 76
        rc, saida = self.conferir("outra.md", "### Corrigido\n- x\n")
        self.assertEqual(rc, 1, saida)
        self.assertIn("(CHANGELOG-BRANCH)", saida)


if __name__ == "__main__":
    unittest.main()
