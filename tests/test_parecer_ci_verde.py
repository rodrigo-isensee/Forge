"""PARECER-SO-COM-CI-VERDE (v0478 E47.1): no Forge, o `forge-check pr` só conta o review e o QA aprovados com o CI verde no head ou com
a prova da suíte dos módulos tocados no `commit:` do parecer (`- suíte: <sha40> rc=0 módulos=<...>`). Sem rede: o gh é um falso que
confere o mesmo que o script (head exato, cada check e os exigidos); sem PR, sem rede ou com check pendente, falha fechada."""
import io
import json
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_isencoes import Repo, fc, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

FORGE = {".claude-plugin/plugin.json": json.dumps({"name": "forge"}) + "\n", "tests/test_forge.py": "x = 0\n"}
REVIEW = ("---\ntipo: review\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: aprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-10-12\n---\n# Review\n\n## Achados\n{prova}")
EXIGIDOS = [{"name": n.split("/", 1)[1], "workflow": n.split("/", 1)[0], "bucket": "pass"} for n in fc.CHECKS_EXIGIDOS_DO_FORGE]


def gh_falso(head, checks, pr_ok=True):
    """O `gh_json` com o PR da branch no `head` e os `checks`; `pr_ok=False` imita o gh sem rede (None e o erro)."""
    def falso(_raiz, *args):
        if args[:2] == ("pr", "view"):
            return ({"number": 7, "headRefOid": head, "baseRefName": "develop"}, "") if pr_ok else (None, "error connecting")
        if args[:2] == ("pr", "checks"):
            return checks, ""
        return None, "sem rede"  # o ruleset e a proteção: nada além dos exigidos do Forge
    return falso


class Base(Repo):
    def entregar(self):
        """Base do Forge, depois bin/forge-x e o teste dele na branch: o plano dos módulos tocados é {test_forge, test_forge_x}."""
        git("switch", "-q", "develop", cwd=self.tmp)
        self.base = self.commitar(FORGE, "forge")
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        git("merge", "-q", "develop", cwd=self.tmp)
        return self.commitar({"bin/forge-x": "print(1)\n", "tests/test_forge_x.py": "x = 1\n"}, "codigo")

    def falta(self, commit, prova):
        return fc.falta_na_prova(self.tmp, self.base, {"commit": commit}, REVIEW.format(c=commit, prova=prova))


class ProvaDaSuite(Base):
    def test_prova_que_cobre_o_plano_vale(self):
        head = self.entregar()
        self.assertEqual(fc.modulos_tocados(self.tmp, self.base, head), {"test_forge", "test_forge_x"})
        self.assertIsNone(self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x,test_outro,test_forge\n"))
        self.assertIsNone(self.falta(head[:12], f"- suíte: {head} rc=0 módulos=test_forge,test_forge_x\n"))  # `commit:` curto, prefixo do sha40

    def test_sem_linha_outro_sha_rc_ou_modulo_faltando_nao_vale(self):
        head = self.entregar()
        self.assertIn("sem a linha `- suíte:", self.falta(head, ""))
        self.assertIn("sem a linha", self.falta(head, f"- suíte: {self.base} rc=0 módulos=test_forge_x\n"))
        self.assertIn("sem a linha", self.falta(head, f"- suíte: {head} rc=1 módulos=test_forge_x\n"))
        self.assertIn("sem a linha", self.falta("", f"- suíte: {head} rc=0 módulos=test_forge,test_forge_x\n"))  # `commit:` vazio é prefixo de tudo
        self.assertIn("falta test_forge_x", self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge\n"))

    def test_plano_completo_pede_a_suite_inteira(self):
        git("switch", "-q", "develop", cwd=self.tmp)
        self.base = self.commitar(FORGE, "forge")
        git("switch", "-q", "melhoria/x", cwd=self.tmp)
        head = self.commitar({"src/sem_mapa.py": "y = 2\n"}, "codigo")
        self.assertEqual(fc.modulos_tocados(self.tmp, self.base, head), "completa")
        self.assertIn("falta completa", self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x\n"))
        self.assertIsNone(self.falta(head, f"- suíte: {head} rc=0 módulos=completa\n"))

    def test_base_ou_ferramenta_ilegivel_falha_fechado(self):
        head = self.entregar()
        self.assertIsNone(fc.modulos_tocados(self.tmp, None, head))
        self.assertIsNone(fc.modulos_tocados(self.tmp, "nao-existe", head))
        with mock.patch.object(fc, "carregar_forge_testes", return_value=None):
            self.assertIsNone(fc.modulos_tocados(self.tmp, self.base, head))
            self.assertIn("não foi lido", self.falta(head, f"- suíte: {head} rc=0 módulos=test_forge_x\n"))
        falso = mock.Mock(planejar=mock.Mock(side_effect=ValueError("oráculo fora do padrão")),
                          TESTE_DO_DIFF=fc.re.compile("$^"), ALTERA_O_MAPA=set())
        with mock.patch.object(fc, "carregar_forge_testes", return_value=falso):
            self.assertIsNone(fc.modulos_tocados(self.tmp, self.base, head))


class CiVerde(Base):
    def verde(self, head, checks, pr_ok=True, ref_head=None):
        with mock.patch.object(fc, "gh_json", gh_falso(head, checks, pr_ok)):
            return fc.ci_verde_no_head(self.tmp, "melhoria/x", ref_head or head)

    def test_verde_so_com_o_mesmo_head_e_tudo_em_pass(self):
        head = self.entregar()
        self.assertTrue(self.verde(head, EXIGIDOS))
        self.assertTrue(self.verde(head, EXIGIDOS + [{"name": "x", "workflow": "W", "bucket": "skipping"}]))

    def test_pendente_vermelho_ausente_outro_head_ou_sem_rede_nao_e_verde(self):
        head = self.entregar()
        self.assertFalse(self.verde(head, EXIGIDOS + [{"name": "x", "workflow": "W", "bucket": "pending"}]))
        self.assertFalse(self.verde(head, EXIGIDOS[1:]))  # exigido ausente
        self.assertFalse(self.verde(head, []))  # nenhum check: CI que não rodou não é verde
        self.assertFalse(self.verde(head, None))  # checks ilegíveis
        self.assertFalse(self.verde(self.base, EXIGIDOS, ref_head=head))  # o PR está em outro head
        self.assertFalse(self.verde(head, EXIGIDOS, pr_ok=False))  # sem rede
        with mock.patch.object(fc, "gh_json", gh_falso(head, EXIGIDOS)):  # o gh acharia um PR verde: a guarda vem antes
            self.assertFalse(fc.ci_verde_no_head(self.tmp, None, head))
        with mock.patch.object(fc, "gh_json", gh_falso(None, EXIGIDOS)):
            self.assertFalse(fc.ci_verde_no_head(self.tmp, "melhoria/x", None))


class NoPr(Base):
    def violacoes(self, prova, suite=False, verde=False, forge=True):
        head = self.entregar()
        if not forge:
            git("rm", "-q", ".claude-plugin/plugin.json", cwd=self.tmp)
            git("commit", "-q", "-m", "sem forge", cwd=self.tmp)
            head = git("rev-parse", "HEAD", cwd=self.tmp)
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova=prova.format(h=head))}, "review")
        erro = io.StringIO()
        with mock.patch.object(fc, "ci_verde_no_head", return_value=verde) as ci, redirect_stderr(erro):
            linhas = fc.cmd_pr(self.tmp, "p1", None, self.base, "melhoria/x", suite=suite)
        return [l for l in linhas if "PARECER-SO-COM-CI-VERDE" in l], ci.call_count, erro.getvalue()

    def test_sem_prova_e_sem_ci_verde_reprova(self):
        linhas, chamadas, _ = self.violacoes("")
        self.assertEqual(len(linhas), 1, linhas)
        self.assertTrue(linhas[0].startswith("docs/reviews/p1.md: suíte: o parecer aprovado só conta com o CI verde"), linhas)
        self.assertEqual(chamadas, 1)

    def test_ci_verde_basta(self):
        self.assertEqual(self.violacoes("", verde=True)[0], [])

    def test_prova_basta_sem_ler_o_gh(self):
        linhas, chamadas, _ = self.violacoes("- suíte: {h} rc=0 módulos=test_forge,test_forge_x\n")
        self.assertEqual((linhas, chamadas), ([], 0))  # a prova local dispensa a leitura do gh

    def test_adiar_so_avisa_sem_ler_o_gh(self):
        linhas, chamadas, erro = self.violacoes("", suite=True)
        self.assertEqual((linhas, chamadas), ([], 0))
        self.assertIn("aviso: docs/reviews/p1.md: suíte:", erro)

    def test_sem_suite_a_catraca_nada_muda(self):
        self.assertEqual(self.violacoes("", suite=None)[0], [])  # a catraca: o próprio CI

    def test_fora_do_forge_nada_muda(self):
        self.assertEqual(self.violacoes("", forge=False)[0], [])


class PeloPrDaCli(Base):
    """O `pr_da_cli` (o `forge-check pr`, o `brief gerar` e o passo 1 do `forge-fechar`) liga a guarda; o `--previo` e o passo 1 só
    avisam; `conferir=False` (o escopo da merge-integracao) não a liga."""

    def linhas(self, **kw):
        head = self.entregar()
        self.commitar({"docs/reviews/p1.md": REVIEW.format(c=head, prova="")}, "review")
        sem_gh = mock.patch.object(fc, "gh_json", return_value=(None, "no git remotes found"))
        with sem_gh, mock.patch.object(fc, "ci_verde_no_head", return_value=False), redirect_stderr(io.StringIO()):
            saida = fc.pr_da_cli(self.tmp, "p1", base="develop", **kw)
        return [l for l in saida if "PARECER-SO-COM-CI-VERDE" in l]

    def test_o_pr_reprova(self):
        self.assertEqual(len(self.linhas()), 1)

    def test_previo_so_avisa(self):
        self.assertEqual(self.linhas(previo=True), [])

    def test_passo_1_do_fechar_so_avisa(self):
        self.assertEqual(self.linhas(sem_checks=True), [])

    def test_sem_conferir_nao_liga(self):
        self.assertEqual(self.linhas(conferir=False), [])


class Esqueleto(unittest.TestCase):
    def test_review_e_qa_trazem_a_linha_da_prova_para_preencher(self):
        for tipo in ("review", "qa"):
            with self.subTest(tipo=tipo):
                texto = fc.esqueleto_do_parecer(tipo, "p1", "melhoria/x", "a" * 40, "aprovado", "2026-01-01")
                self.assertIn(f"- suíte: {fc.PREENCHER} rc=0 módulos={fc.PREENCHER}\n", texto)


if __name__ == "__main__":
    unittest.main()
