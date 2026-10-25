"""M16, P2 e M5 (LOTE-FORGE-CHECK-0.28.0): a etapa no brief. Regra única de marca (R-BRIEF): um brief delega uma só etapa; toda
outra etapa do pedido vai ao "Fora do escopo" sem a marca; a marca só no corte real. Parser com sufixo de letra e etapas de qualquer
`E<n>`. Biblioteca padrão, sem rede; fixtures neutras."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
