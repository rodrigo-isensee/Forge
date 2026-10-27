"""M16, P2 e M5 (LOTE-FORGE-CHECK-0.28.0): a etapa no brief. Regra única de marca (R-BRIEF): um brief delega uma só etapa; toda
outra etapa do pedido vai ao "Fora do escopo" sem a marca; a marca só no corte real. Parser com sufixo de letra e etapas de qualquer
`E<n>`. Biblioteca padrão, sem rede; fixtures neutras."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gh_falso import com_gh_falso  # noqa: E402  (o gerar --branch consulta o PR; teste sem rede)
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_etapa_do_brief", str(FORGE_CHECK)).load_module()

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO
Modo: implementar

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E0.1 (arquiteto-exemplo): desenho do recurso X.
- E0.2 (seguranca-exemplo): modelo de ameaças do recurso X.
- E1.1 (dev-exemplo): implementação do recurso X.
- E1.2 (revisor-exemplo): review do recurso X.
- E1.3 (seguranca-exemplo): review de segurança do recurso X.
- E1.3b (infra-exemplo): parecer de infraestrutura do recurso X.
- E1.4 (qa-exemplo): QA do recurso X.
- E1.5 (revisor-exemplo, outra instância): merge na develop.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""

ETAPAS = {
    "E0.1": '"E0.1 (arquiteto-exemplo): desenho do recurso X."',
    "E0.2": '"E0.2 (seguranca-exemplo): modelo de ameaças do recurso X."',
    "E1.1": '"E1.1 (dev-exemplo): implementação do recurso X."',
    "E1.2": '"E1.2 (revisor-exemplo): review do recurso X."',
    "E1.3": '"E1.3 (seguranca-exemplo): review de segurança do recurso X."',
    "E1.3b": '"E1.3b (infra-exemplo): parecer de infraestrutura do recurso X."',
    "E1.4": '"E1.4 (qa-exemplo): QA do recurso X."',
    "E1.5": '"E1.5 (revisor-exemplo, outra instância): merge na develop."',
}


def ambiente_do_git():
    """Sem GIT_* herdado (um hook do git exporta GIT_DIR) e sem config global ou de sistema: o git só vê o repositório temporário."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return sem_manutencao(env)


def brief(destino, entregar, fora):
    return (f"Agente destino: forge:{destino}\n\n## Objetivo\nExemplo.\n\n## Ler\n- o pedido.\n\n## Entregar\n"
            + "".join(f"- {linha}\n" for linha in entregar)
            + "\n## Fora do escopo\n" + "".join(f"- {linha}\n" for linha in fora)
            + '\n## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): "A".\n\n## Pronto quando\n'
              "- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.\n\n## Relatório\nAté 8 linhas.\n")


def fora_sem(*exceto):
    return [f"{t} · outra etapa do pedido; continua nele" for e, t in ETAPAS.items() if e not in exceto]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-etapa-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedido = self.gravar("docs/pedidos/exemplo.md", PEDIDO)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        env = com_gh_falso(dict(os.environ, HOME=str(self.tmp / "home")))
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), *map(str, args)],
                           capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout

    def conferir(self, texto, nome="b.md"):
        return self.rodar("brief", self.gravar(nome, texto), "--pedido", self.pedido)


class ParserDeEtapas(unittest.TestCase):
    def test_sufixo_de_letra_e_etapas_fora_do_escopo_entram_em_ordem_natural(self):
        etapas = fc.ler_pedido_brief(PEDIDO)["etapas"]
        self.assertEqual(list(etapas), ["E0.1", "E0.2", "E1.1", "E1.2", "E1.3", "E1.3b", "E1.4", "E1.5"])
        self.assertEqual(etapas["E1.3b"][0], "infra-exemplo")
        self.assertEqual(len([e for e in etapas if e.startswith("E1.")]), 6)
        self.assertEqual(fc.ids_em_citacao("faz (E1.3b) e (E1.5)"), {"E1.3b", "E1.5"})


class RegraUnicaDeMarca(Base):
    def test_merge_do_mesmo_papel_com_as_outras_etapas_sem_marca_aprova(self):
        """Caso 1: o merge do revisor (E1.5); a E1.2 é do mesmo papel em outra delegação e vai ao Fora sem a marca."""
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar na develop (E1.5)."], fora_sem("E1.5")))
        self.assertEqual(rc, 0, saida)
        for etapa in ("E0.1", "E1.2", "E1.3b", "E1.4"):
            self.assertIn(f'corte: etapa (ok) "{etapa}"', saida)
        self.assertNotIn("corte: sem marca", saida)

    def test_parecer_de_seguranca_com_etapas_de_outras_instancias_sem_marca_aprova(self):
        """Caso 2: a E0.2; as etapas do revisor (outras instâncias) não mudam nada para este destino."""
        rc, saida = self.conferir(brief("seguranca-exemplo", ["Modelo de ameaças (E0.2).", "Do recurso (E1)."], fora_sem("E0.2")))
        self.assertEqual(rc, 0, saida)

    def test_justificativa_livre_sem_registro_externo_aprova(self):
        """Caso 3: a E1.3b; a justificativa não se confere e a E1.1 vai ao Fora sem a marca."""
        fora = [f"{t} · qualquer justificativa" for e, t in ETAPAS.items() if e != "E1.3b"]
        rc, saida = self.conferir(brief("infra-exemplo", ["Parecer (E1.3b)."], fora))
        self.assertEqual(rc, 0, saida)

    def test_etapa_com_a_marca_completa_e_corte_real(self):
        fora = fora_sem("E1.5", "E1.2") + [f'Retira do escopo original: {ETAPAS["E1.2"]} · justificativa: x · consequência: y · '
                                           'decisão: DECISÃO DO DONO (2026-01-01): "A".']
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora))
        self.assertIn('corte: real (marca completa) "E1.2"', saida)
        self.assertEqual(rc, 0, saida)

    def test_etapa_omitida_reprova_de_qualquer_papel(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E1.4")))
        self.assertIn('corte: sem marca "E1.4" (etapa sem menção)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E1.2")))
        self.assertIn('corte: sem marca "E1.2" (etapa do papel do destino fora do Entregar)', saida)
        self.assertEqual(rc, 1)

    def test_item_citado_nao_cobre_a_outra_etapa_do_papel_do_destino(self):
        """Review A1 (8b018b1): citar o item `(E1)` no Entregar não dispensa a etapa do papel do destino; a E1.5 do revisor, omitida
        no brief que delega a E1.2, reprova como qualquer etapa sem menção (R-BRIEF, M5)."""
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2).", "Do recurso (E1)."], fora_sem("E1.2", "E1.5")))
        self.assertIn('corte: sem marca "E1.5" (etapa do papel do destino fora do Entregar)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("dev-exemplo", ["Recurso (E1)."], fora_sem("E1.1")))
        self.assertIn('corte: sem marca "E1.1" (etapa do papel do destino fora do Entregar)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2).", "Do recurso (E1)."], fora_sem("E1.2")))
        self.assertIn('corte: etapa (ok) "E1.5"', saida)
        self.assertEqual(rc, 0, saida)

    def test_etapa_fora_do_escopo_tambem_e_conferida(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E0.1")))
        self.assertIn('corte: sem marca "E0.1" (etapa sem menção)', saida)
        self.assertEqual(rc, 1)

    def test_review_e_merge_do_mesmo_papel_no_mesmo_entregar_reprovam(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2).", "Merge (E1.5)."], fora_sem("E1.2", "E1.5")))
        self.assertIn("etapa: junta delegações E1.2, E1.5 (R-BRIEF)", saida)
        self.assertEqual(rc, 1)



class LoteDoBriefG1(Base):
    """PR-VERDE-LOTE-CHECK (G1): o que o conferente reprovava por leitura, o `forge-check brief` reprova antes, com linha própria."""

    def test_a_etapa_do_cobre_no_fora_do_escopo_sem_marca_reprova(self):
        texto = brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2"))
        rc, saida = self.conferir(texto.replace("\n\n## Objetivo", "\nCobre: E1.5\n\n## Objetivo", 1))
        self.assertIn('corte: sem marca "E1.5" (etapa do próprio papel cortada: o cabeçalho a delega em Cobre) (R-BRIEF)', saida)
        self.assertEqual(rc, 1, saida)
        rc, saida = self.conferir(texto.replace("\n\n## Objetivo", "\nCobre: E1.2\n\n## Objetivo", 1), "ok.md")
        self.assertNotIn("etapa do próprio papel cortada", saida)
        self.assertEqual(rc, 0, saida)

    def test_caminho_do_pq_que_nao_existe_nem_e_criado_reprova(self):
        self.gravar("bin/existe", "x\n")
        pq = "- PQ-2 (cmd): `bin/existe bin/nao-existe refs/heads/x origin/develop` · espera: rc=0\n"
        texto = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace("\n\n## Relatório", "\n" + pq + "\n## Relatório")
        rc, saida = self.conferir(texto)
        self.assertIn('pq: PQ-2 cita "bin/nao-existe", que não existe nem é criado pelo Entregar (R-PROVA)', saida)
        self.assertEqual([l for l in saida.splitlines() if l.startswith("pq:")], ['pq: PQ-2 cita "bin/nao-existe", que não existe nem é criado pelo Entregar (R-PROVA)'])
        self.assertEqual(rc, 1, saida)
        rc, saida = self.conferir(texto.replace("Mesclar (E1.5).", "Mesclar (E1.5) e criar `bin/nao-existe`."), "ok.md")
        self.assertNotIn("pq:", saida)
        self.assertEqual(rc, 0, saida)

    def test_no_rev_falta_a_decisao_do_pedido_de_origem_reprova(self):
        rev = self.gravar("docs/pedidos/exemplo-REV.md", PEDIDO.replace('DECISÃO DO DONO (2026-01-01): "A".', "nenhuma."))
        sem = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace('DECISÃO DO DONO (2026-01-01): "A".', "nada.")
        rc, saida = self.rodar("brief", self.gravar("b.md", sem), "--pedido", rev)
        self.assertIn('decisões: falta "DECISÃO DO DONO (2026-01-01): \\"A\\"." (docs/pedidos/exemplo.md:21)', saida)
        self.assertEqual(rc, 1, saida)
        rc, saida = self.rodar("brief", self.gravar("ok.md", brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5"))), "--pedido", rev)
        self.assertIn("fonte: docs/pedidos/exemplo.md (1 decisões)", saida)
        self.assertEqual(rc, 0, saida)


SHA = "0123456789abcdef0123456789abcdef01234567"


def preencher(gerado, pq_proprio=True, base_sha=SHA):
    """O que o Jarvis faz com a saída do `gerar`: apaga o que tem PREENCHER e o bloco da marca não usado, põe Objetivo, Ler e um PQ
    (ou, com `pq_proprio=False`, fica só com o PQ de merge do gerar, com o sha no lugar de <mergeCommit>)."""
    linhas, pula = [], False
    for linha in gerado.splitlines():
        if linha.startswith("## "):
            pula = linha.startswith("## Marca de corte")
        if not pq_proprio and "<mergeCommit>" in linha:
            linhas.append(linha.split(" · PREENCHER", 1)[0].replace("<mergeCommit>", SHA).replace("PQ-N", "PQ-1"))
            continue
        if linha.startswith("Branch:"):
            linha = linha.replace("Base-sha: PREENCHER", f"Base-sha: {base_sha}")
        if pula or "PREENCHER" in linha:
            continue
        if linha.startswith("## Entregar"):
            linhas += ["## Objetivo", "Exemplo.", "", "## Ler", "- o pedido.", "", linha, "- Mesclar o commit aprovado."]
            continue
        if linha.startswith("## Pronto quando") and pq_proprio:
            linhas += [linha, "- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local."]
            continue
        linhas.append(linha)
    texto = "\n".join(linhas) + "\n"
    if "## Entregar" not in texto:
        texto = texto.replace("## Decisões e restrições", "## Objetivo\nExemplo.\n\n## Ler\n- o pedido.\n\n## Entregar\n- O recurso (E1).\n\n## Decisões e restrições", 1)
    return texto


class GerarComCobre(Base):
    """P2: `brief gerar --cobre E<n>.<m>` escreve a etapa no Entregar e as outras no Fora do escopo sem a marca."""

    def gerar(self, destino, *extra):
        return self.rodar("brief", "gerar", "--pedido", self.pedido, "--destino", f"forge:{destino}", *extra)

    def test_mais_de_uma_etapa_do_destino_exige_cobre(self):
        rc, saida = self.gerar("revisor-exemplo")
        self.assertEqual(rc, 2)
        self.assertIn("brief gerar: --cobre obrigatório (forge:revisor-exemplo tem E1.2, E1.5)", saida)

    def test_cobre_de_outro_papel_e_recusado(self):
        rc, saida = self.gerar("revisor-exemplo", "--cobre", "E1.4")
        self.assertEqual(rc, 2)
        self.assertIn("brief gerar: E1.4 é de qa-exemplo, não de revisor-exemplo", saida)
        rc, saida = self.gerar("revisor-exemplo", "--cobre", "E9.9")
        self.assertEqual(rc, 2)

    def test_etapa_unica_do_destino_e_deduzida_e_as_outras_vao_sem_marca(self):
        rc, saida = self.gerar("dev-exemplo", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.assertIn("Etapa: codigo   Cobre: E1.1\n", saida)
        self.assertIn('- "E1.1 (dev-exemplo): implementação do recurso X." (E1.1)\n', saida)
        self.assertIn("## Fora do escopo (outras etapas do pedido, sem a marca; R-BRIEF)", saida)
        for etapa, trecho in ETAPAS.items():
            if etapa != "E1.1":
                self.assertIn(f"- {trecho} · etapa de outra delegação; continua no pedido\n", saida)
        fora = saida.split("## Fora do escopo", 1)[1].split("## Marca de corte", 1)[0]
        self.assertNotIn("Retira do escopo original", fora)
        self.assertNotIn("E1.1 (dev-exemplo)", fora)

    def test_ida_e_volta_o_brief_gerado_e_preenchido_passa_no_corte(self):
        rc, saida = self.gerar("revisor-exemplo", "--etapa", "review", "--cobre", "E1.2")
        self.assertEqual(rc, 0, saida)
        rc, conferido = self.conferir(preencher(saida))
        self.assertEqual(rc, 0, conferido)
        self.assertNotIn("corte: sem marca", conferido)
        self.assertIn('corte: etapa (ok) "E1.5"', conferido)


class ProvaDoConferente(Base):
    """M4: o PQ `cmd` que o conferente roda e o PQ `merge` contam como prova do conferente num brief com commit."""

    def com_pq(self, *pqs):
        texto = brief("revisor-exemplo", ["Mesclar o commit aprovado (E1.5)."], fora_sem("E1.5"))
        cabeca, _ = texto.split("## Pronto quando\n", 1)
        return cabeca + "## Pronto quando\n" + "".join(f"- {pq}\n" for pq in pqs) + "\n## Relatório\nAté 8 linhas.\n"

    def test_cmd_do_conferente_e_merge_valem_como_prova(self):
        for pq in (f"PQ-1 (cmd): `git merge-base --is-ancestor {SHA} origin/develop` · espera: rc=0",
                   "PQ-1 (merge): `gh pr view melhoria/x --json state,mergedAt` mostra MERGED"):
            with self.subTest(pq=pq):
                rc, saida = self.conferir(self.com_pq(pq))
                self.assertNotIn("forma: sem PQ que o conferente confira", saida)
                self.assertEqual(rc, 0, saida)

    def test_cmd_do_autor_continua_sem_valer(self):
        rc, saida = self.conferir(self.com_pq("PQ-1 (cmd): `python3 -m unittest -q` · espera: rc=0"))
        self.assertIn("forma: sem PQ que o conferente confira", saida)
        self.assertEqual(rc, 1)


class Repo(Base):
    """A raiz vira repositório git: `develop` com o pedido e a branch `melhoria/x` com a entrega."""
    REVIEW = ("---\ntipo: {tipo}\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n{extra}data: 2026-10-12\n---\n# x\n")
    EXTRA = {"review": "revisor: forge:tech-lead\n",
             "qa": "escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n",
             "revisao-devops": "revisor: forge:devops-engineer\n"}
    PASTA = {"review": "docs/reviews", "qa": "docs/qa", "revisao-devops": "docs/devops"}

    def setUp(self):
        super().setUp()
        self.git("init", "-q", "-b", "develop")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "Teste")
        self.commitar({"README.md": "x\n", "src/app.py": "v1\n"}, "base")
        self.git("switch", "-q", "-c", "melhoria/x")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.tmp, capture_output=True, text=True, check=True, env=ambiente_do_git()).stdout.strip()

    def commitar(self, arquivos, mensagem):
        for rel, texto in arquivos.items():
            self.gravar(rel, texto)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", mensagem)
        return self.git("rev-parse", "HEAD")

    def entrega(self, arquivos, *pareceres):
        head = self.commitar(arquivos, "entrega")
        if pareceres:
            self.commitar({f"{self.PASTA[t]}/exemplo.md": self.REVIEW.format(tipo=t, c=head, extra=self.EXTRA[t]) for t in pareceres},
                          "pareceres")

    def gerar(self, etapa, destino="revisor-exemplo", cobre="E1.5"):
        return self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", f"forge:{destino}", "--etapa", etapa,
                          "--cobre", cobre, "--branch", "melhoria/x", "--base", "develop")


class TabelaDePareceres(Repo):
    """P2 (tabela 3) e M5: o `gerar` recusa PR e merge sem os pareceres que o `forge-check pr` exige; o `brief` avisa."""

    def test_pr_so_de_md_comum_sem_review_recusa(self):
        self.entrega({"docs/x.md": "# x\n"})
        rc, saida = self.gerar("pr")
        self.assertEqual(rc, 1)
        self.assertIn("brief gerar: recusado: docs/reviews: review: sem parecer para o pedido `exemplo` (R-REVIEW)", saida)
        self.assertNotIn("## Entregar", saida)

    def test_pr_so_de_md_comum_com_review_e_sem_qa_gera(self):
        self.entrega({"docs/x.md": "# x\n"}, "review")
        rc, saida = self.gerar("pr")
        self.assertEqual(rc, 0, saida)
        self.assertIn("Etapa: pr   Cobre: E1.5", saida)

    def test_md_de_controle_sem_qa_recusa(self):
        self.entrega({"agents/x.md": "# x\n"}, "review")
        rc, saida = self.gerar("merge-integracao")
        self.assertEqual(rc, 1)
        self.assertIn("brief gerar: recusado: docs/qa: qa: sem parecer", saida)

    def test_merge_com_devops_faltando_num_diff_de_pipeline_recusa(self):
        self.entrega({".github/workflows/ci.yml": "on: push\n"}, "review", "qa")
        rc, saida = self.gerar("merge-integracao")
        self.assertEqual(rc, 1)
        self.assertIn("revisao-devops: sem parecer", saida)
        self.assertNotIn("docs/qa: qa: sem parecer", saida)

    def test_etapa_de_merge_sem_branch_recusa(self):
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:revisor-exemplo",
                               "--etapa", "merge-integracao", "--cobre", "E1.5")
        self.assertEqual(rc, 1)
        self.assertIn("--branch obrigatório na etapa merge-integracao", saida)

    def test_ida_e_volta_do_brief_de_merge_gerado(self):
        """M4: o brief de merge que o gerar monta, preenchido, passa no `brief` (o PQ de merge é prova do conferente)."""
        self.entrega({"src/app.py": "v2\n"}, "review", "qa")
        rc, saida = self.gerar("merge-integracao")
        self.assertEqual(rc, 0, saida)
        preenchido = preencher(saida, pq_proprio=False, base_sha=self.git("rev-parse", "develop"))
        self.assertIn(f"git merge-base --is-ancestor {SHA} origin/develop", preenchido)
        rc, conferido = self.conferir(preenchido)
        self.assertNotIn("forma: sem PQ que o conferente confira", conferido)
        self.assertNotIn("aviso: etapa:", conferido)
        self.assertEqual(rc, 0, conferido)

    def test_brief_avisa_a_etapa_sem_parecer_e_nao_reprova(self):
        self.entrega({"src/app.py": "v2\n"}, "review", "qa")
        rc, saida = self.gerar("merge-integracao")
        preenchido = preencher(saida, pq_proprio=False, base_sha=self.git("rev-parse", "develop"))
        self.git("reset", "-q", "--hard", "HEAD~1")  # os pareceres somem da branch depois do gerar
        rc, conferido = self.conferir(preenchido)
        self.assertIn("aviso: etapa: docs/reviews: review: sem parecer para o pedido `exemplo` (R-REVIEW)", conferido)
        self.assertEqual(rc, 0, conferido)

    def test_brief_da_etapa_imprime_o_comando_com_o_slug(self):  # C2, qa A1: a fiação no `forge-check brief`
        self.entrega({"docs/x.md": "# x\n"}, "review")
        rc, saida = self.gerar("pr")
        preenchido = preencher(saida, pq_proprio=True, base_sha=self.git("rev-parse", "develop"))
        rc, conferido = self.conferir(preenchido)
        self.assertIn("etapa: comando forge-check pr x --ref origin/melhoria/x --base develop\n", conferido)

    def test_qa_gera_com_aviso_do_review(self):
        self.entrega({"src/app.py": "v2\n"})
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "brief", "gerar", "--pedido", "exemplo",
                            "--destino", "forge:qa-exemplo", "--etapa", "qa", "--branch", "melhoria/x"],
                           capture_output=True, text=True, env=com_gh_falso(dict(os.environ, HOME=str(self.tmp / "home"))), timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("brief gerar: aviso: docs/reviews: review: sem parecer", r.stderr)
        self.assertNotIn("docs/qa", r.stderr)


class QuatroDefeitosDoScript(Repo):
    """EST-030-L1 (M1): os quatro defeitos reais de brief que o conferente pegava viram checagem do `forge-check brief`; o conferente
    segue lendo todo brief (decisão do dono "C", 2026-10-24: a dispensa, BRIEF-MECANICO, saiu do código)."""
    CABECALHO = "\nEtapa: review   Branch: melhoria/x   Base: develop\n\n## Objetivo"

    def com_remoto(self):
        """`origin` de verdade (um repositório nu local) com a branch enviada: o `commit:` lê o remoto por `git ls-remote`."""
        self.git("init", "-q", "--bare", str(self.tmp / "remoto.git"))
        remoto_sem_manutencao(self.tmp / "remoto.git")
        self.git("remote", "add", "origin", str(self.tmp / "remoto.git"))
        self.git("push", "-q", "origin", "melhoria/x")

    def test_papel_errado_o_destino_nao_tem_a_etapa_citada(self):
        rc, saida = self.conferir(brief("dev-exemplo", ["Review (E1.2)."], fora_sem("E1.2")))
        self.assertIn('etapa: papel errado E1.2 (o pedido a põe em "revisor-exemplo", o destino é "dev-exemplo") (R-BRIEF)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")), "ok.md")
        self.assertNotIn("papel errado", saida)

    def test_decisao_ausente_a_linha_do_pedido_falta_no_brief(self):
        sem = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace('DECISÃO DO DONO (2026-01-01): "A".', "nada.")
        rc, saida = self.conferir(sem)
        self.assertIn('decisões: falta "DECISÃO DO DONO (2026-01-01): \\"A\\"."', saida)
        self.assertEqual(rc, 1)

    def test_pedido_contraditorio_o_entregar_manda_o_que_o_fora_do_escopo_do_pedido_exclui(self):
        self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("## Decisões", "## Fora do escopo\n- O review (E1.2) não entra nesta rodada · `confirmado`\n\n## Decisões"))
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")))
        self.assertIn("contradição: o Entregar manda E1.2, que o `Fora do escopo` do pedido exclui (R-BRIEF)", saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")), "ok.md")
        self.assertNotIn("contradição: o Entregar", saida)

    def test_o_id_dentro_de_outro_nome_ou_na_prosa_do_fora_do_escopo_nao_exclui_nada(self):
        """Review A1: `E1.2` no nome de outro pedido (`EXEMPLO-E1.2-ENVIO`) e como contexto de uma frase não contradizem o Entregar."""
        for item in ("Envio dos textos: pedido EXEMPLO-E1.2-ENVIO · `técnico`",
                     "Mudar o processo sem o dono: a proposta do E1.2 que afrouxa controle vai a ele · `confirmado`"):
            with self.subTest(item=item):
                self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("## Decisões", f"## Fora do escopo\n- {item}\n\n## Decisões"))
                rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")))
                self.assertNotIn("contradição:", saida)
                self.assertEqual(rc, 0, saida)
        self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("## Decisões", "## Fora do escopo\n- E1.2 e E1.3: pedido seguinte\n\n## Decisões"))
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")))
        self.assertIn("contradição: o Entregar manda E1.2", saida)

    def test_commit_so_na_worktree_o_head_nao_esta_em_origin(self):
        self.entrega({"src/app.py": "v2\n"})
        head = self.git("rev-parse", "HEAD")
        texto = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace("\n\n## Objetivo", self.CABECALHO, 1)
        rc, saida = self.conferir(texto)
        self.assertNotIn("commit:", saida, "sem remoto conhecido não há o que conferir (como parecer_commitado)")
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "develop"))
        rc, saida = self.conferir(texto)
        self.assertIn(f"commit: o head {head[:7]} de melhoria/x só existe na worktree (origin/melhoria/x ausente)", saida)
        self.assertEqual(rc, 1)
        self.git("update-ref", "refs/remotes/origin/melhoria/x", head)
        rc, saida = self.conferir(texto)
        self.assertNotIn("commit:", saida)
        self.assertEqual(rc, 0, saida)

    def test_o_commit_le_o_remoto_e_nao_so_o_ref_de_rastreio_velho(self):
        """Segurança A8, review A6: o ref de rastreio local diz que a branch foi enviada, mas `origin` ainda está atrás."""
        self.com_remoto()
        self.entrega({"src/app.py": "v2\n"})
        self.git("update-ref", "refs/remotes/origin/melhoria/x", self.git("rev-parse", "HEAD"))
        texto = brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")).replace("\n\n## Objetivo", self.CABECALHO, 1)
        rc, saida = self.conferir(texto)
        self.assertIn("(origin/melhoria/x atrás); rode git fetch origin", saida)
        self.assertEqual(rc, 1)

    def test_na_etapa_codigo_o_commit_nao_se_confere_e_o_gerar_sem_etapa_escreve_preencher(self):
        """O brief de `codigo` é para quem ainda vai commitar: head só local não reprova. O `gerar` com `--cobre` e sem `--etapa`
        escreve `Etapa: PREENCHER` (segurança A11), que o `brief` reprova até o Jarvis escolher a etapa."""
        self.com_remoto()
        self.entrega({"src/app.py": "v2\n"})
        codigo = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace("\n\n## Objetivo", self.CABECALHO.replace("review", "codigo"), 1)
        rc, saida = self.conferir(codigo)
        self.assertNotIn("commit:", saida)
        self.assertEqual(rc, 0, saida)
        self.assertIn("commit: o head", self.conferir(codigo.replace("Etapa: codigo", "Etapa: review"))[1])
        self.assertIn("Etapa: PREENCHER   Cobre: E1.1\n", self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--cobre", "E1.1")[1])

    def test_o_brief_mecanico_nao_dispensa_o_conferente(self):
        """Decisão do dono "C" (2026-10-24): o fixture que antes saía `conferente: dispensado (brief mecânico)` (primeira rodada, etapa
        `codigo`, branch no remoto, só cópias literais do pedido) não imprime linha `conferente:` nenhuma; todo brief passa pelo conferente."""
        self.com_remoto()
        texto = brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")).replace("\n\n## Objetivo", self.CABECALHO.replace("review", "codigo"), 1)
        rc, saida = self.conferir(texto)
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("dispensado", saida)
        self.assertNotIn("conferente:", saida)
        self.assertTrue(saida.endswith("resultado: aprovado\n"), saida)

    def fora_do_pedido(self, item):
        self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("## Decisões", f"## Fora do escopo\n- {item}\n\n## Decisões"))

    def test_o_trecho_copiado_do_fora_do_escopo_contradiz_so_com_20_caracteres_ou_mais_e_se_o_entregar_o_traz(self):
        """QA A2 e A3: o trecho entre aspas (sem id) de 20 caracteres ou mais que o Entregar copia contradiz; com 19, ou ausente do Entregar, não."""
        vinte, dezenove = "desenho do recurso X", "esenho do recurso X"
        self.assertEqual((len(vinte), len(dezenove)), (20, 19))
        for trecho, esperado in ((vinte, True), (dezenove, False)):
            with self.subTest(trecho=trecho):
                self.fora_do_pedido(f'Não entra o "{trecho}" · `confirmado`')
                rc, saida = self.conferir(brief("revisor-exemplo", [f"Mesclar (E1.5) com o {trecho}."], fora_sem("E1.5")))
                self.assertEqual("contradição: o Entregar manda" in saida, esperado, saida)
                self.assertEqual(rc, 1 if esperado else 0, saida)
        self.fora_do_pedido(f'Não entra o "{vinte}" · `confirmado`')
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5")), "ausente.md")
        self.assertNotIn("contradição:", saida)
        self.assertEqual(rc, 0, saida)

    def test_o_id_que_o_pedido_nao_tem_nao_exclui_nada(self):
        """QA A4: `(E9)` no Fora do escopo do pedido e no Entregar, sem E9 no pedido, não é contradição."""
        self.fora_do_pedido("Outra frente (E9) fica para depois · `confirmado`")
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5), sem tocar (E9)."], fora_sem("E1.5")))
        self.assertNotIn("contradição:", saida)

    def test_head_local_atras_do_remoto_nao_reprova(self):
        """QA A1 (sonda X2): a branch avançou em `origin` e a worktree ficou para trás: o head local está em `origin/<branch>`."""
        self.entrega({"src/app.py": "v2\n"})
        atras = self.git("rev-parse", "HEAD")
        self.entrega({"src/app.py": "v3\n"})
        self.com_remoto()
        self.git("reset", "-q", "--hard", atras)
        texto = brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")).replace("\n\n## Objetivo", self.CABECALHO, 1)
        rc, saida = self.conferir(texto)
        self.assertNotIn("commit:", saida)
        self.assertEqual(rc, 0, saida)

    def test_branch_sem_commit_local_nao_reprova_nem_quebra(self):
        """QA A1 (sonda X3): `Branch:` que não existe na worktree não tem head a conferir (sem traceback)."""
        self.com_remoto()
        texto = brief("revisor-exemplo", ["Review (E1.2)."], fora_sem("E1.2")).replace(
            "\n\n## Objetivo", self.CABECALHO.replace("melhoria/x", "melhoria/outra"), 1)
        rc, saida = self.conferir(texto)
        self.assertNotIn("commit:", saida)
        self.assertNotIn("Traceback", saida)
        self.assertEqual(rc, 0, saida)

    def test_a_saida_malformada_do_remoto_nao_vira_sha(self):
        """QA A5: `git ls-remote` com rc 0 e linha que não começa por sha40 (ou vazia) é branch ausente, não sha."""
        real = fc.git
        try:
            for saida in ("lixo\trefs/heads/melhoria/x\n", ""):
                fc.git = lambda raiz, *args, _s=saida: (0, _s)
                self.assertEqual(fc.remoto_da_branch(self.tmp, "melhoria/x"), (None, True), repr(saida))
            sha = "a" * 40
            fc.git = lambda raiz, *args: (0, f"{sha}\trefs/heads/melhoria/x\n")
            self.assertEqual(fc.remoto_da_branch(self.tmp, "melhoria/x"), (sha, True))
        finally:
            fc.git = real


def cabecalho_c2(etapa, branch="melhoria/meu-slug", base="develop"):
    return f"Agente destino: forge:revisor\nPedido: x\nBranch: {branch}   Base: {base}   Base-sha: {'a' * 40}\nEtapa: {etapa}\n\n## Objetivo\nX.\n"


# --- CONF-C2C3 (CONFERENTE-VELOCIDADE, E3.1): o comando decide o que o conferente lia por julgamento -----------
class ComandoDoPr(unittest.TestCase):
    def test_etapa_pr_imprime_o_comando_com_o_slug_sem_o_prefixo(self):
        for etapa in ("pr", "merge-integracao", "pedido-de-merge-ao-dono"):
            self.assertEqual(fc.linha_do_comando_pr(cabecalho_c2(etapa)),
                             [("etapa: comando forge-check pr meu-slug --ref origin/melhoria/meu-slug --base develop", False)])

    def test_outras_etapas_e_branch_estranha_nao_imprimem(self):
        self.assertEqual(fc.linha_do_comando_pr(cabecalho_c2("codigo")), [])
        self.assertEqual(fc.linha_do_comando_pr(cabecalho_c2("pr", branch="melhoria/a;b")), [])
        self.assertEqual(fc.linha_do_comando_pr(cabecalho_c2("pr", base="dev;x")), [])  # a base também é validada

    def test_fora_da_convencao_melhoria_nao_imprime(self):  # review A2: o slug não existe; o argumento é o `pedido:` do parecer
        self.assertEqual(fc.linha_do_comando_pr(cabecalho_c2("pr", branch="feature/cad-cliente")), [])


class RecusaDoIdDoPedido(unittest.TestCase):
    """C2: numa branch `melhoria/<slug>`, o id do pedido no lugar do slug é recusado (rc=2); fora dela, ou com parecer do pedido, vale."""
    ID = "ID-DO-PEDIDO"
    PARECER = "---\ntipo: review\ncontrato: 1\npedido: ID-DO-PEDIDO\nbranch: melhoria/outra\ncommit: {c}\nparecer: aprovado\nrevisor: forge:tech-lead\ndata: 2026-10-12\n---\n# x\n"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-c2c3-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        (self.tmp / "docs" / "pedidos" / f"{self.ID}.md").write_text(f"---\nid: {self.ID}\n---\n", encoding="utf-8")
        self.git("init", "-q", "-b", "develop")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "x")
        self.git("switch", "-q", "-c", "melhoria/outra")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), *args], check=True, capture_output=True, text=True, env=ambiente_do_git()).stdout.strip()

    def pr(self, argumento, *extra):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "pr", argumento, *extra],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp)), timeout=60)
        return r.returncode, r.stdout

    def test_id_de_pedido_existente_sem_branch_sai_rc2_com_uso(self):
        rc, saida = self.pr(self.ID)
        self.assertEqual(rc, 2, saida)
        self.assertIn("uso: use o slug da branch (<slug>), não o id do pedido", saida)

    def test_slug_sem_pedido_com_esse_nome_segue_o_caminho_antigo(self):
        rc, saida = self.pr("meu-slug")
        self.assertNotEqual(rc, 2, saida)
        self.assertNotIn("uso:", saida)

    def test_com_a_branch_do_mesmo_nome_o_argumento_vale(self):
        self.git("branch", f"melhoria/{self.ID}")
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID))

    def test_com_a_branch_do_mesmo_nome_so_em_origin_o_argumento_vale(self):
        self.git("update-ref", f"refs/remotes/origin/melhoria/{self.ID}", "HEAD")
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID))

    def test_argumento_com_barra_nao_sobe_nem_desce_de_pasta(self):
        (self.tmp / "docs" / "pedidos" / "sub").mkdir()
        (self.tmp / "docs" / "pedidos" / "sub" / "X.md").write_text("x\n", encoding="utf-8")
        self.assertIsNone(fc.uso_do_pr(self.tmp, "sub/X"))
        self.assertIsNotNone(fc.uso_do_pr(self.tmp, self.ID))

    def test_fora_da_convencao_melhoria_o_id_do_parecer_vale(self):  # review A1: o projeto usa feature/ e `pedido: <id>`
        self.git("switch", "-q", "-c", "feature/cad-cliente")
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID))
        rc, saida = self.pr(self.ID)
        self.assertNotEqual(rc, 2, saida)
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID, "origin/feature/cad-cliente"))
        self.assertIsNotNone(fc.uso_do_pr(self.tmp, self.ID, "origin/melhoria/outra"))

    def test_com_parecer_do_pedido_na_ref_o_argumento_vale(self):  # review A1: o `pedido:` do parecer é o argumento
        head = self.git("rev-parse", "HEAD")
        (self.tmp / "docs" / "reviews").mkdir()
        (self.tmp / "docs" / "reviews" / "x.md").write_text(self.PARECER.format(c=head), encoding="utf-8")
        self.git("add", "docs/reviews/x.md")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "parecer")
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID, "melhoria/outra"))
        self.git("branch", "melhoria/vazia", "develop")
        self.assertIsNotNone(fc.uso_do_pr(self.tmp, self.ID, "melhoria/vazia"))  # a ref sem o parecer não o vê

    def test_pedido_so_na_copia_principal_ou_na_raiz_de_brief_tambem_recusa(self):  # review A3, qa A4
        (self.tmp / "docs" / "pedidos" / f"{self.ID}.md").unlink()
        outra = Path(tempfile.mkdtemp(prefix="forge-c2c3-outra-"))
        self.addCleanup(shutil.rmtree, outra, ignore_errors=True)
        (outra / "docs" / "pedidos").mkdir(parents=True)
        (outra / "docs" / "pedidos" / f"{self.ID}.md").write_text("x\n", encoding="utf-8")
        self.assertIsNone(fc.uso_do_pr(self.tmp, self.ID))
        with mock.patch.object(fc, "raiz_principal", return_value=outra):
            self.assertIsNotNone(fc.uso_do_pr(self.tmp, self.ID))
        with mock.patch.object(fc, "RAIZES_DE_BRIEF", (outra,)):
            self.assertIsNotNone(fc.uso_do_pr(self.tmp, self.ID))


class VoltaIdentica(unittest.TestCase):
    ANTES = "Agente destino: forge:dev\n\n## Objetivo\nA.\n\n## Fora do escopo\n- b\n\n## Relatório\nR.\n"

    def test_bloco_igual_byte_a_byte_e_marcado_idêntico(self):
        linhas = [l for l, _ in fc.blocos_identicos(self.ANTES, self.ANTES)]
        self.assertEqual(linhas, [f'volta: bloco "{n}" idêntico ao anterior (exigido)' for n in ("Objetivo", "Fora do escopo", "Relatório")])

    def test_bloco_alterado_nao_e_marcado(self):
        linhas = [l for l, _ in fc.blocos_identicos(self.ANTES.replace("- b", "- c"), self.ANTES)]
        self.assertNotIn('volta: bloco "Fora do escopo" idêntico ao anterior (exigido)', linhas)
        self.assertEqual(len(linhas), 2)


    def test_bloco_ausente_no_anterior_nao_e_marcado(self):
        sem_fora = self.ANTES.replace("## Fora do escopo\n- b\n\n", "")
        novo = self.ANTES.replace("- b\n", "")  # o bloco existe, vazio, no brief novo
        linhas = [l for l, _ in fc.blocos_identicos(novo, sem_fora)]
        self.assertNotIn('volta: bloco "Fora do escopo" idêntico ao anterior (exigido)', linhas)


class VerificadorOk(unittest.TestCase):
    def test_pq_do_vocabulario_termina_em_rotulo_do_verificador_ok(self):
        for pq in ("- PQ-1 (cmd): `git log` · espera: rc=0", "- PQ-2 (cmd, do autor): `pytest` · espera: rc=0"):
            linhas, _ = fc.conferir_pq([pq])
            self.assertTrue(linhas[-1][0].endswith("· rótulo do verificador: ok"), linhas)
            self.assertFalse(linhas[-1][1])


if __name__ == "__main__":
    unittest.main()
