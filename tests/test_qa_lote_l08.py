"""QA do lote L08 (versao-033; E7, E10, E12, E16, E19): cenários de ponta a ponta com o `forge-check` real (subprocesso) sobre repositórios
temporários. Cada teste responde a um item do backlog da 0.33; a fronteira que guarda vem no docstring."""
import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RepoComOrigem, carregar_forge_check, git, rodar_fc, com_gh_falso  # noqa: E402
from test_volta_por_delta import BriefDeVolta, Repositorio  # noqa: E402
from test_fechar_forge_check_real import FecharComOForgeCheckReal  # noqa: E402
from test_promover_homolog import Promover, SCRIPT  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401


class QaE7ConferenciaNoHead(RepoComOrigem):
    """E7: o `pr` só aprova com `entrega conferida <sha40>` cobrindo o head; fronteira: o último commit depois da conferida."""
    CONFERIR = False  # a fixture não grava a conferida do head: cada teste monta a sua

    def historico(self, *shas):
        self.pedido().write_text("# p1\n\n## Histórico\n- aberto\n" + "".join(f"- 2026-11-04 09:00: entrega conferida {s}\n" for s in shas), encoding="utf-8")

    def pedido(self):
        arq = self.home / ".forge-contrib" / "docs" / "pedidos" / "p1.md"  # o pedido mora fora do repositório (fixture nova do E7)
        arq.parent.mkdir(parents=True, exist_ok=True)
        return arq

    def test_ciclo_completo_conferida_codigo_novo_reconferida(self):
        self.historico(self.c1)
        self.assertEqual(self.pr("--base", "develop")[0], 0)
        c2 = self.commitar(self.repo, {"src/x.txt": "x1 volta\nx2\nx3\nx4\nx5\nx6\nx7\nx8\n"}, "volta")
        self.pareceres(c2)
        self.assertEqual(self.pr("--base", "develop")[0], 1)  # código novo sem conferência
        self.historico(self.c1, c2)
        self.assertEqual(self.pr("--base", "develop")[0], 0)

    def test_commit_de_teste_do_qa_depois_da_conferida_exige_nova_conferencia(self):
        """E7 x E16: o fluxo do QA (teste em commit próprio, depois o parecer) deixa o head fora da conferida; o `pr` reprova até haver outra."""
        self.historico(self.c1)
        teste = self.commitar(self.repo, {"tests/test_x.py": "# qa\n"}, "teste do QA")
        self.pareceres(teste)
        rc, saida, _ = self.pr("--base", "develop")
        self.assertEqual(rc, 1, saida)
        self.assertIn("conferência:", saida)

    def test_ref_por_sha_acha_a_branch_pelos_briefs_e_falha_fechada_sem_pedido_ou_historico(self):
        """E7 volta 1: o `forge-fechar` passa o sha; a branch única cujo head é o sha liga o pedido pelos briefs; sem pedido ou sem Histórico, reprova."""
        sha = git("rev-parse", "melhoria/x", cwd=self.repo).stdout.strip()
        self.pedido().unlink(missing_ok=True)
        contrib = self.home / ".forge-contrib" / "docs"
        (contrib / "briefs").mkdir(parents=True, exist_ok=True)
        (contrib / "briefs" / "real-tech-lead-1.md").write_text("Pedido: real\nBranch: melhoria/x   Base: develop\n\n## Objetivo\nx\n", encoding="utf-8")
        rc, saida, _ = self.pr("--base", "develop", ref=sha)
        self.assertEqual(rc, 1, saida)  # o brief liga a branch ao pedido `real`, que não existe: falha fechada
        self.assertIn("conferência: não consegui ler o pedido", saida)
        (contrib / "pedidos").mkdir(exist_ok=True)
        (contrib / "pedidos" / "real.md").write_text("# real\n", encoding="utf-8")
        rc, saida, _ = self.pr("--base", "develop", ref=sha)
        self.assertEqual(rc, 1, saida)
        self.assertIn("o pedido não tem ## Histórico", saida)
        (contrib / "pedidos" / "real.md").write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.c1}\n", encoding="utf-8")
        self.assertEqual(self.pr("--base", "develop", ref=sha)[0], 0)
        git("branch", "melhoria/gemea", sha, cwd=self.repo)  # duas branches no mesmo sha: ambíguo, não escolhe
        rc, saida, _ = self.pr("--base", "develop", ref=sha)
        self.assertEqual(rc, 1, saida)
        self.assertIn("conferência: sem o pedido", saida)

    def test_ref_origin_sem_checkout(self):
        """A ref `origin/melhoria/x` (PR aberto) segue a mesma regra."""
        git("push", "-q", "origin", "melhoria/x", cwd=self.repo)
        self.historico(self.c1)
        self.assertEqual(self.pr("--base", "develop", ref="origin/melhoria/x")[0], 0)
        self.historico("0" * 40)
        self.assertEqual(self.pr("--base", "develop", ref="origin/melhoria/x")[0], 1)

    def test_linha_conferida_sem_marcador_de_item_ou_fora_do_historico_nao_vale(self):
        for linha in (f"`entrega conferida {self.c1}`", f"entrega conferida {self.c1}", f"- 2026-11-04 09:00: entrega conferida {self.c1[:39]}",
                      f"- 2026-11-04 09:00: entrega NÃO conferida {self.c1}", f"- não: entrega conferida {self.c1}",
                      f"- 2026-11-04 09:00: conferência não cumpriu; conferida {self.c1}", f"- 2026-11-04: entrega conferida {self.c1}"):  # L08-1
            with self.subTest(linha):
                self.pedido().write_text(f"# p1\n\n## Histórico\n- aberto\n{linha}\n", encoding="utf-8")
                rc, saida, _ = self.pr("--base", "develop")
                self.assertEqual(rc, 1, saida)


class QaE10PrMesclado(RepoComOrigem):
    """E10: `pr --pr <n>` com o PR já mesclado; fronteira: branch apagada e squash na develop."""

    def squash(self):
        arq = self.home / ".forge-contrib" / "docs" / "pedidos" / "p1.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(f"# p1\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.c1}\n", encoding="utf-8")
        head = git("rev-parse", "melhoria/x", cwd=self.repo).stdout.strip()
        git("switch", "-q", "-c", "sq", "origin/develop", cwd=self.repo)
        git("merge", "-q", "--squash", "melhoria/x", cwd=self.repo)
        git("commit", "-q", "-m", "entrega (#7)", cwd=self.repo)
        git("push", "-q", "origin", "sq:develop", cwd=self.repo)
        git("switch", "-q", "--detach", "origin/develop", cwd=self.repo)
        git("branch", "-q", "-D", "melhoria/x", "sq", cwd=self.repo)
        return head

    def gh(self, head, estado="MERGED"):
        corpo = json.dumps({"state": estado, "headRefOid": head, "headRefName": "melhoria/x"})
        return {"PATH": com_gh_falso(script=f"printf '%s\\n' '{corpo}'\n")["PATH"]}

    def test_depois_do_squash_o_pr_aprova_e_o_commit_do_squash_nao_vale(self):
        head = self.squash()
        r = rodar_fc("pr", "p1", "--pr", "7", "--base", "develop", raiz=self.repo, home=self.home, env_extra=self.gh(head))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("head " + head[:7], r.stdout)  # o conferido é o head do PR, não o do squash

    def test_pr_mesclado_com_parecer_reprovado_reprova(self):
        head = self.squash()
        git("switch", "-q", "-c", "melhoria/x", head, cwd=self.repo)
        reprovado = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: reprovado\n"
                     "revisor: forge:tech-lead\ndata: 2026-11-04\n---\n# r\n")
        novo = self.commitar(self.repo, {"docs/reviews/p1.md": reprovado.format(c=self.c1)}, "reprova")
        git("switch", "-q", "--detach", "origin/develop", cwd=self.repo)
        r = rodar_fc("pr", "p1", "--pr", "7", "--base", "develop", raiz=self.repo, home=self.home, env_extra=self.gh(novo))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_pr_com_numero_gigante_ou_espaco_nao_quebra(self):
        for n in ("99999999999999999999", " 7", "7 ", "٧"):
            with self.subTest(n):
                r = rodar_fc("pr", "p1", "--pr", n, "--base", "develop", raiz=self.repo, home=self.home, env_extra=self.gh("1" * 40))
                self.assertNotIn("Traceback", r.stderr)
                self.assertIn(r.returncode, (1, 2))


class QaE12DesdePorBranch(BriefDeVolta):
    """E12: o `Desde` vem da base da própria branch; fronteira: conferida de outra branch por último."""

    def test_gerar_volta_propoe_a_mais_recente_da_branch_e_nunca_a_da_outra(self):
        git("switch", "-q", "-c", "melhoria/outra", self.base, cwd=self.repo)
        outra = self.commitar({"src/outra.txt": "o\n"}, "outra branch")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        c2 = self.commitar({"src/app.txt": "v3\n"}, "segunda")
        dono = f"DECISÃO DO DONO (2026-11-04): \"fixar\".\n- 2026-11-04 11:00: base do delta fixada pelo dono {c2}\n"
        self.pedido.write_text(self.pedido.read_text(encoding="utf-8") + f"\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.c1}\n"
                               + dono + f"- 2026-11-04 12:00: entrega conferida {outra}\n", encoding="utf-8")
        c3 = self.commitar({"src/app.txt": "v4\n"}, "terceira")
        rc, saida = self.gerar(ref=c3)
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"--desde {c2}`", saida)
        self.assertNotIn(outra, saida)

    def test_entrega_aceita_a_conferida_da_propria_branch_com_a_de_outra_por_ultimo(self):
        git("switch", "-q", "-c", "melhoria/outra", self.base, cwd=self.repo)
        outra = self.commitar({"src/outra.txt": "o\n"}, "outra branch")
        git("switch", "-q", "melhoria/x", cwd=self.repo)
        self.pedido.write_text(self.pedido.read_text(encoding="utf-8") + f"\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.c1}\n"
                               f"- 2026-11-04 10:00: entrega conferida {outra}\n", encoding="utf-8")
        c2 = self.commitar({"src/app.txt": "v3\n"}, "volta")
        self.assertEqual(self.entrega(desde=self.c1)[0], 0)
        self.assertEqual(self.entrega(desde=outra)[0], 1)
        self.assertTrue(c2)


class QaPareceresDaBranch(RepoComOrigem):
    """E7 e E11 (integração do versao-033): numa branch de trabalho o `pr` conta só os pareceres da própria branch; o de outra branch do
    pedido, desatualizado ou reprovado, não vale nem reprova; sem parecer próprio, reprova (falha fechada)."""
    ALHEIO = ("---\ntipo: {t}\ncontrato: 1\npedido: p1\nbranch: melhoria/outra\ncommit: {c}\nparecer: {p}\n{extra}data: 2026-11-05\n---\n# alheio\n")

    def alheios(self, parecer):
        velho = git("rev-parse", f"{self.c1}^", cwd=self.repo).stdout.strip()  # commit antigo: o parecer alheio está desatualizado
        self.commitar(self.repo, {
            "docs/reviews/p1-outra.md": self.ALHEIO.format(t="review", c=velho, p=parecer, extra="revisor: forge:tech-lead\n"),
            "docs/qa/p1-outra.md": self.ALHEIO.format(t="qa", c=velho, p=parecer, extra="escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n")},
            "pareceres de outra branch, mais recentes")

    def test_parecer_proprio_aprovado_passa_com_alheio_desatualizado_ou_reprovado(self):
        for parecer in ("aprovado", "reprovado"):
            with self.subTest(parecer):
                self.alheios(parecer)
                rc, saida, _ = self.pr("--base", "develop")
                self.assertEqual((rc, saida.split(" · ")[0]), (0, "pr: veredito: aprovado"), saida)
                self.assertNotIn("p1-outra", saida)

    def test_sem_parecer_da_propria_branch_reprova_mesmo_com_alheio_aprovado(self):
        self.alheios("aprovado")
        git("rm", "-q", "docs/reviews/p1.md", "docs/qa/p1.md", cwd=self.repo)
        git("commit", "-q", "-m", "tira os pareceres da branch", cwd=self.repo)
        rc, saida, _ = self.pr("--base", "develop")
        self.assertEqual(rc, 1, saida)
        self.assertIn("sem parecer da branch \"melhoria/x\" para o pedido `p1`", saida)

    def test_so_o_parecer_de_qa_faltando_reprova(self):
        n = self.commitar(self.repo, {"src/z.txt": "".join(f"z{i}\n" for i in range(25))}, "entrega maior")  # P5: classe N, que pede QA
        self.pareceres(n)
        self.alheios("aprovado")
        git("rm", "-q", "docs/qa/p1.md", cwd=self.repo)
        git("commit", "-q", "-m", "tira o QA da branch", cwd=self.repo)
        rc, saida, _ = self.pr("--base", "develop")
        self.assertEqual(rc, 1, saida)
        self.assertIn("sem parecer da branch", saida)


class QaE16TesteEParecer(RepoComOrigem):
    """E16: teste e parecer separados; fronteira: parecer que cita o commit anterior ao teste."""
    QA = ("---\ntipo: qa\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\nescopo: completo\n"
          "bugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\ndata: 2026-11-04\n---\n# q\n")

    def test_parecer_citando_o_commit_anterior_ao_teste_e_recusado_mesmo_em_commit_separado(self):
        teste = self.commitar(self.repo, {"tests/test_x.py": "# qa\n"}, "teste")
        self.commitar(self.repo, {"docs/qa/p1.md": self.QA.format(c=self.c1)}, "parecer citando o anterior")
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"docs/qa/p1.md: commit: desatualizado: tests/test_x.py mudou depois do parecer", saida)
        self.assertNotIn("commitado junto", saida)  # commits separados: a explicação do junto não se aplica
        self.assertTrue(teste)

    def test_mensagem_do_junto_nao_vaza_com_nome_de_arquivo_hostil(self):
        nome = "tests/test_\x1b[31m.py"
        try:
            self.commitar(self.repo, {nome: "# qa\n", "docs/qa/p1.md": self.QA.format(c=self.c1)}, "junto")
        except OSError:
            self.skipTest("nome sem suporte")
        rc, saida, _ = self.pr()
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("\x1b", saida)


class QaE19AtoGithub(Repositorio):
    """E19: `entrega --etapa ato-github`; fronteira: brief com duas PQs, PQ maiúscula, vários briefs."""
    BASE_BRIEF = "Agente destino: forge:devops-engineer\nPedido: p1\nTipo: ato-github\nBranch: —   Base: develop   Base-sha: {b}\n\n## Objetivo\nx\n\n## Pronto quando\n{pqs}"

    def setUp(self):
        super().setUp()
        self.gravar_pedido()
        (self.repo / "docs" / "briefs").mkdir(parents=True, exist_ok=True)

    def brief(self, pqs, nome="p1-devops-engineer-1.md"):
        (self.repo / "docs" / "briefs" / nome).write_text(self.BASE_BRIEF.format(b=self.base, pqs=pqs), encoding="utf-8")
        return f"docs/briefs/{nome}"

    def ato(self, *briefs, branch="—"):
        args = ["entrega", self.pedido, "--branch", branch, "--base", "develop", "--base-sha", self.base, "--etapa", "ato-github"]
        for b in briefs:
            args += ["--brief", b]
        return self.check(*args)

    def test_pr_merge_run_passam_com_confira(self):
        rc, saida = self.ato(self.brief("- PQ-1 (merge): o PR #3 mesclado\n- PQ-2 (run): CI verde\n"))
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.count("confira PQ-"), 2)

    def test_dois_briefs_reprova(self):
        rc, saida = self.ato(self.brief("- PQ-1 (pr): x\n"), self.brief("- PQ-1 (pr): y\n", "p1-devops-engineer-2.md"))
        self.assertEqual(rc, 1, saida)

    def test_pq_de_commit_junto_de_pq_do_github_reprova(self):
        rc, saida = self.ato(self.brief("- PQ-1 (pr): x\n- PQ-2 (push): y\n"))
        self.assertEqual(rc, 1, saida)

    def test_pq_de_commit_em_maiuscula_reprova(self):  # L08-2
        rc, saida = self.ato(self.brief("- PQ-1 (SHA): x\n- PQ-2 (pr): y\n"))
        self.assertEqual(rc, 1, saida)
        self.assertIn("prova de commit", saida)

    def test_branch_de_trabalho_com_commit_reprova_e_nao_diz_nada_a_conferir(self):
        rc, saida = self.ato(self.brief("- PQ-1 (pr): x\n"), branch="melhoria/x")
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("nada a conferir", saida)


class QaE7FecharReal(FecharComOForgeCheckReal):
    """E7 com o `forge-fechar` real e o `forge-check` real: duas branches no mesmo sha (ambíguo) e pedido sem Histórico param no passo 1."""

    def parou_no_passo_1(self):
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("parou no passo 1", r.stdout + r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh pr create", "gh pr merge"))])
        return r.stdout + r.stderr

    def test_pedido_sem_historico_para_no_passo_1(self):
        self.pedido.write_text("# real\n", encoding="utf-8")
        self.assertIn("conferência:", self.parou_no_passo_1())

    def test_duas_branches_no_mesmo_sha_param_no_passo_1_sem_a_branch_local(self):
        """Sem a branch local o `forge-check` recebe o sha (FECHAR-REF-POR-NOME) e o sha com duas branches segue ambíguo."""
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega}\n", encoding="utf-8")
        self.git("branch", "melhoria/gemea", "melhoria/x")
        self.git("branch", "-q", "-D", "melhoria/x")
        self.assertIn("conferência:", self.parou_no_passo_1())

    def test_com_a_branch_local_a_gemea_no_mesmo_sha_nao_confunde_a_conferencia(self):
        """Com a branch local o `forge-check` recebe `refs/heads/<branch>`: o nome decide, a gêmea não para o passo 1."""
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega}\n", encoding="utf-8")
        self.git("branch", "melhoria/gemea", "melhoria/x")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertNotIn("conferência:", r.stdout + r.stderr)
        self.assertIn("pr x --ref refs/heads/melhoria/x", r.stdout + r.stderr)


class QaA9Promocao(Promover):
    """A9 do review: `scripts/promover-homolog.py` real, com o `forge-check` real, num repositório descartável; a promoção não cobra a
    conferência do head (sem pedido de release e sem conferida), e a branch de trabalho com `--base main` segue cobrada."""

    def test_promocao_real_passa_sem_pedido_de_release_e_sem_conferida(self):
        self.pronta()
        self.assertFalse((self.tmp / ".forge-contrib").exists())  # HOME sem pedido algum
        for args in (("--dry-run",), ()):
            with self.subTest(args):
                r = self.roda(*args)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn("valem contra a main", r.stdout)
                self.assertNotIn("conferência:", r.stdout + r.stderr)
        self.assertIn("pr create --base homolog --head develop", "\n".join(self.gh_chamadas()))

    def test_branch_de_trabalho_com_base_main_ou_homolog_reprova(self):
        self.pronta()
        self.git("switch", "-q", "-c", "melhoria/y", "origin/develop")
        self.escrever("src/y.txt", "trabalho\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "feat: trabalho")
        for base in ("main", "homolog"):
            with self.subTest(base):
                r = subprocess.run([sys.executable, "-I", str(SCRIPT.parent.parent / "bin" / "forge-check"), "pr", "release-0.2.0", "--ref",
                                    "melhoria/y", "--base", base], cwd=self.proj, env=self.env, capture_output=True, text=True, timeout=60)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("conferência: sem o pedido", r.stdout)
                self.assertNotIn("promoção", r.stderr)


class AceiteDoQaComDecisao(RepoComOrigem):
    """QA-ACEITE-FALSO (0.72 E1): `aceite_usuario: sim` do QA aprovado com bug médio só vale com a DECISÃO DO DONO no pedido que traz
    `aceite QA <commit do parecer>`; fronteira: a linha com outro commit, o token colado em outra palavra e a citação fora da decisão."""
    QA = ("---\ntipo: qa\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\nescopo: completo\n"
          "bugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 1\nbugs_baixos: 0\naceite_usuario: {a}\ndata: 2026-11-09\n---\n# q\n")

    def setUp(self):
        super().setUp()
        self.n = self.commitar(self.repo, {"src/z.txt": "".join(f"z{i}\n" for i in range(25))}, "entrega maior")  # classe N: pede QA
        self.pareceres(self.n)

    def qa(self, aceite="sim", linha=None):
        (self.repo / "docs" / "qa" / "p1.md").write_text(self.QA.format(c=self.n, a=aceite), encoding="utf-8")
        git("commit", "-q", "--allow-empty", "-am", "parecer do QA com bug médio", cwd=self.repo)  # os subTests regravam o mesmo parecer
        arq = self.home / ".forge-contrib" / "docs" / "pedidos" / "p1.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text("# p1\n\n## Decisões\n" + (f"{linha}\n" if linha else ""), encoding="utf-8")
        return self.pr("--base", "develop")

    def test_sim_sem_a_linha_do_dono_reprova(self):
        rc, saida, _ = self.qa()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'docs/qa/p1.md: aceite_usuario: sim sem DECISÃO DO DONO no pedido com "aceite QA {self.n[:7]}"', saida)

    def test_sim_com_a_linha_do_dono_do_mesmo_commit_aprova(self):
        for c in (self.n[:7], self.n):
            with self.subTest(c=c):
                rc, saida, _ = self.qa(linha=f"- DECISÃO DO DONO (2026-11-09 10:00): pode seguir com o bug médio; aceite QA {c}")
                self.assertEqual(rc, 0, saida)

    def test_linha_com_outro_commit_colada_ou_fora_da_decisao_reprova(self):
        for linha in (f"- DECISÃO DO DONO (2026-11-09 10:00): aceite QA {self.c1[:7]}",
                      f"- DECISÃO DO DONO (2026-11-09 10:00): xaceite QA {self.n[:7]}y",
                      f"- o QA disse que a DECISÃO DO DONO foi aceite QA {self.n[:7]}"):
            with self.subTest(linha=linha):
                rc, saida, _ = self.qa(linha=linha)
                self.assertEqual(rc, 1, saida)
                self.assertIn("aceite_usuario: sim sem DECISÃO DO DONO", saida)

    def test_sem_aceite_declarado_segue_a_bur_b4(self):
        rc, saida, _ = self.qa(aceite="nao")
        self.assertEqual(rc, 0, saida)

    def test_pedido_ausente_reprova_no_projeto_e_so_avisa_no_forge(self):
        fc = carregar_forge_check()
        campos = {"parecer": "aprovado", "aceite_usuario": "sim", "bugs_medios": "1", "commit": self.n}
        with mock.patch.object(fc, "RAIZES_DE_BRIEF", (self.home / ".forge-contrib",)), contextlib.redirect_stderr(io.StringIO()) as erro:
            violacoes = fc.aceite_do_qa_sem_dono(self.repo, "p9", "docs/qa/p9.md", campos)  # lista vazia é falha, não erro
            self.assertEqual(len(violacoes), 1, violacoes)
            self.assertIn("sem o pedido", violacoes[0])
            self.assertEqual(erro.getvalue(), "")
            (self.repo / ".claude-plugin").mkdir()
            (self.repo / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}', encoding="utf-8")
            self.assertEqual(fc.aceite_do_qa_sem_dono(self.repo, "p9", "docs/qa/p9.md", campos), [])
            self.assertIn("aceite_usuario não verificável sem o pedido", erro.getvalue())


class AceiteDeOutroPedidoDesatualiza(RepoComOrigem):
    """ACEITE-AUTORIA, E1g da 0.55 (LIVRES estreito): o aceite deste pedido entra depois do parecer sem desatualizá-lo; o de outro pedido,
    mudado depois, desatualiza; fronteira: `p10` não é o aceite de `p1`."""
    ACEITE = "---\npedido: {p}\ncommit: {c}\naceite: sim\n---\nAceito.\n"

    def test_aceite_do_proprio_pedido_nao_desatualiza(self):
        self.commitar(self.repo, {"docs/security/aceites/p1.md": self.ACEITE.format(p="p1", c=self.c1)}, "aceite do dono")
        rc, saida, _ = self.pr("--base", "develop")
        self.assertEqual(rc, 0, saida)

    def test_aceite_de_outro_pedido_desatualiza_os_pareceres(self):
        for outro in ("p2", "p10"):
            with self.subTest(outro=outro):
                self.commitar(self.repo, {f"docs/security/aceites/{outro}.md": self.ACEITE.format(p=outro, c=self.c1)}, "aceite alheio")
                rc, saida, _ = self.pr("--base", "develop")
                self.assertEqual(rc, 1, saida)
                self.assertIn(f"commit: desatualizado: docs/security/aceites/{outro}.md mudou depois do parecer", saida)
                git("reset", "-q", "--hard", "HEAD~1", cwd=self.repo)


def load_tests(loader, tests, pattern):
    """As classes herdam as bases dos módulos de teste do autor; só os testes próprios daqui entram (os herdados já rodam nos módulos deles)."""
    suite = unittest.TestSuite()
    for cls in (QaE7ConferenciaNoHead, QaE10PrMesclado, QaE12DesdePorBranch, QaE16TesteEParecer, QaE19AtoGithub, QaE7FecharReal, QaA9Promocao, QaPareceresDaBranch,
                AceiteDoQaComDecisao, AceiteDeOutroPedidoDesatualiza):
        suite.addTests(cls(nome) for nome in vars(cls) if nome.startswith("test"))
    return suite


if __name__ == "__main__":
    unittest.main()
