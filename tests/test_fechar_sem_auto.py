"""FECHAR-NUNCA-AUTO (decisão do dono de 24/11, v0478 E171.1): nenhum merge do time sai com check pendente, com merge automático ou de uma cópia
velha do `bin/forge-fechar`.

- Nenhum `gh pr merge` de `bin/` e `scripts/` leva `--auto` (varredura da fonte, com o detector provado contra o passo 6 antigo).
- O passo 6 exige todo check-run do head verde, não só os obrigatórios: terminado fora de success para; pendente espera; skipped não conta.
- O script se recusa a rodar (também no --dry-run, no --limpar, no --lote e no --promover) quando o próprio arquivo difere do
  bin/forge-fechar da origin/develop, depois de buscá-la; a busca que falha e a develop sem o arquivo também recusam.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

RAIZ = base.RAIZ
VERDES = ["bateria\t11\tcompleted\tsuccess", "bateria (python 3.14)\t12\tcompleted\tsuccess", "catraca\t13\tcompleted\tsuccess"]
MERGE = re.compile(r"\bpr\b[\"'\s,]+merge\b")
AUTO = re.compile(r"(?<![\w-])--auto(?![\w-])")
PASSO_6_ANTIGO = 'mesclar_auto() { "$gh" pr merge "$ref" --auto "$1" --match-head-commit "$2" "${@:3}"; }\n'


def merges_com_auto(texto):
    """As linhas lógicas (com as continuações `\\` juntas) que chamam `pr merge` e levam `--auto`."""
    logicas = texto.replace("\\\n", " ").splitlines()
    return [l for l in logicas if MERGE.search(l) and AUTO.search(l)]


def fontes():
    return sorted(p for pasta in ("bin", "scripts") for p in (RAIZ / pasta).rglob("*") if p.is_file() and "__pycache__" not in p.parts)


class SemAutoNaFonte(unittest.TestCase):
    def test_o_detector_pega_o_passo_6_antigo_e_a_continuacao(self):
        self.assertEqual(len(merges_com_auto(PASSO_6_ANTIGO)), 1)
        self.assertEqual(len(merges_com_auto('gh pr merge "$ref" \\\n  --auto --squash\n')), 1)
        self.assertEqual(len(merges_com_auto('subprocess.run(["gh", "pr", "merge", ref, "--auto"])\n')), 1)
        self.assertEqual(merges_com_auto('git fetch --no-auto-maintenance\ngh pr merge "$ref" --squash\n'), [])

    def test_nenhum_gh_pr_merge_de_bin_e_scripts_usa_auto(self):
        arquivos = fontes()
        self.assertGreaterEqual(len(arquivos), 20, "a varredura tem de alcançar bin/ e scripts/")
        achados, merges = [], 0
        for p in arquivos:
            texto = p.read_text(encoding="utf-8", errors="replace")
            merges += sum(1 for l in texto.replace("\\\n", " ").splitlines() if MERGE.search(l))
            achados += [f"{p.relative_to(RAIZ)}: {l.strip()}" for l in merges_com_auto(texto)]
        self.assertGreaterEqual(merges, 1, "o merge do forge-fechar tem de estar entre os varridos")
        self.assertEqual(achados, [], "merge automático proibido pelo dono (FECHAR-NUNCA-AUTO)")

    def test_forge_fechar_nao_cita_auto_em_lugar_nenhum(self):
        self.assertEqual(AUTO.findall((RAIZ / "bin" / "forge-fechar").read_text(encoding="utf-8")), [])


class TodoCheckRunDoHead(unittest.TestCase):
    setUp, tearDown, git, fechar = base.Fechar.setUp, base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar
    chamadas, merges = base.Fechar.chamadas, base.Fechar.merges

    def runs(self, *extras):
        (self.estado / "check_runs").write_text("".join(f"{l}\n" for l in (*VERDES, *extras)))

    def assert_recusou(self, r, *textos):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        for t in textos:
            self.assertIn(t, r.stderr)
        self.assertEqual(self.merges(), [])

    def test_check_run_fora_dos_obrigatorios_terminado_fora_de_success_para(self):
        for conclusao in ("failure", "cancelled", "neutral", "timed_out", "action_required"):
            with self.subTest(conclusao=conclusao):
                self.setUp()
                sha = self.git("rev-parse", "melhoria/x")
                self.runs(f"extra\t20\tcompleted\t{conclusao}")
                self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x"),
                                    f"parou no passo 6: o check-run extra do head {sha[:12]} terminou em {conclusao}", "FECHAR-NUNCA-AUTO")

    def test_check_run_fora_dos_obrigatorios_pendente_espera_e_para_no_prazo(self):
        sha = self.git("rev-parse", "melhoria/x")
        self.runs("extra\t20\tin_progress\t-")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "8", FORGE_FECHAR_INTERVALO="2")
        self.assert_recusou(r, f"o check-run extra do head {sha[:12]} não está verde (completed/success) na execução mais recente "
                               "(lida: in_progress/-)")
        self.assertIn(f"check-runs do head {sha[:12]}: espero extra (in_progress/-)", r.stdout)

    def test_skipped_e_execucao_antiga_vermelha_nao_param_e_mescla(self):
        self.runs("extra\t20\tcompleted\tskipped", "outro\t21\tcompleted\tfailure", "outro\t22\tcompleted\tsuccess")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("todo outro check-run do head também (FECHAR-NUNCA-AUTO)", r.stdout)
        self.assertEqual(len(self.merges()), 1)


class CopiaDaDevelop(unittest.TestCase):
    tearDown, git, fechar, chamadas, merges = base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.merges
    RECUSA = "difere do bin/forge-fechar da origin/develop"

    def setUp(self):
        base.Fechar.setUp(self)
        del self.env["FORGE_FECHAR_COPIA_LIVRE"]  # a conferência vale também com FORGE_FECHAR_TESTE=1

    def publicar(self, texto):
        """Um commit na develop com bin/forge-fechar = texto, enviado ao servidor; devolve o sha."""
        (self.proj / "bin").mkdir(exist_ok=True)
        (self.proj / "bin" / "forge-fechar").write_bytes(texto)
        self.git("add", "bin/forge-fechar")
        self.git("commit", "-q", "-m", "chore: fechar")
        self.git("push", "-q", "origin", "develop")
        return self.git("rev-parse", "HEAD")

    def assert_recusou(self, r, texto):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(f"forge-fechar: recusado: {texto}", r.stderr)
        self.assertIn("nada foi feito", r.stderr)
        self.assertEqual(self.chamadas(), [], "nada roda com a cópia recusada")

    def test_copia_velha_recusa_em_todos_os_modos_com_o_comando_da_copia_certa(self):
        self.publicar(b"#!/usr/bin/env bash\n# passo 6 antigo\n")
        sha = self.git("rev-parse", "melhoria/x")
        casos = (("p1", "--ref", "melhoria/x"), ("p1", "--ref", "melhoria/x", "--dry-run"), ("p1", "--ref", "melhoria/x", "--limpar"),
                 ("--lote", "p1:melhoria/x", "p2:melhoria/y"), ("release-0.9.0", "--promover", sha))
        for args in casos:
            with self.subTest(args=args):
                self.registro.write_text("")
                r = self.fechar(*args)
                self.assert_recusou(r, "esta cópia (")
                self.assertIn(self.RECUSA, r.stderr)
                self.assertIn(f"git worktree add --detach {self.tmp}/.forge-contrib/wt/fechar-develop origin/develop", r.stderr)
                self.assertNotIn("log: ", r.stdout)

    def test_develop_sem_o_arquivo_recusa(self):
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x", "--dry-run"), "a origin/develop não tem bin/forge-fechar")

    def test_busca_que_falha_recusa_mesmo_com_a_local_igual(self):
        self.publicar(base.SCRIPT.read_bytes())
        self.git("remote", "set-url", "origin", str(self.tmp / "nao-existe.git"))
        self.assert_recusou(self.fechar("p1", "--ref", "melhoria/x", "--dry-run"), "não consegui buscar a origin/develop")

    def test_confere_contra_a_develop_do_servidor_nao_a_local(self):
        igual = self.publicar(base.SCRIPT.read_bytes())
        self.publicar(b"#!/usr/bin/env bash\n# velha no servidor\n")
        self.git("update-ref", "refs/remotes/origin/develop", igual)  # a local ainda diz igual; a busca traz a do servidor
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assert_recusou(r, "esta cópia (")
        self.assertIn(self.RECUSA, r.stderr)

    def test_copia_igual_a_da_develop_segue(self):
        self.publicar(b"velha\n")
        igual = self.publicar(base.SCRIPT.read_bytes())
        self.git("update-ref", "refs/remotes/origin/develop", self.git("rev-parse", "HEAD~1"))  # local velha: a busca a atualiza
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("recusado", r.stderr)
        self.assertEqual(self.git("rev-parse", "refs/remotes/origin/develop"), igual)

    def test_copia_livre_sem_o_modo_de_teste_nao_dispensa(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_TESTE="", FORGE_FECHAR_COPIA_LIVRE="1",
                        FORGE_FECHAR_INTERVALO="30", FORGE_FECHAR_PAUSA="3")
        self.assert_recusou(r, "a origin/develop não tem bin/forge-fechar")


if __name__ == "__main__":
    unittest.main()
