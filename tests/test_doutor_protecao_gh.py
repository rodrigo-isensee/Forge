"""Aviso da F8: o `forge doutor` completo lê, só leitura, se `develop`, `homolog` e `main` estão protegidas no GitHub.

Arquivo próprio do item, para o commit dele se reverter sozinho. Usa a `Base` do `test_doutor`, cujo `gh` falso (`GH_FALSO`) responde por endpoint.
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_doutor as td  # noqa: E402

HOOK = td.HOOK


class Protecao(td.Base):
    """Aviso da F8: o doutor completo lê (só leitura) se `develop`, `homolog` e `main` estão protegidas no GitHub. Três estados: protegida
    (silêncio), sem proteção (aviso) e "não consegui conferir" (explícito, nunca diz que está protegido). Nunca ecoa a saída do `gh`."""
    MARCADOR = "MARCADOR-GH"

    def resp(self, nome, texto, rc=0):
        (self.home / f"gh-{nome}").write_text(texto, encoding="utf-8")
        (self.home / f"gh-{nome}.rc").write_text(str(rc), encoding="utf-8")

    def chamadas(self):
        return self.gh_log.read_text(encoding="utf-8").splitlines() if self.gh_log.exists() else []

    def apis(self):
        return [c for c in self.chamadas() if c.startswith("api ")]

    def sem_protecao(self, ramo):
        self.resp(f"regras-{ramo}", "[]")  # protecao-<ramo> já responde 404 "Branch not protected" por padrão

    def test_tres_branches_protegidas_ficam_em_silencio_e_so_se_le_com_get(self):
        r = self.doutor()
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        apis = self.apis()
        self.assertEqual(len(apis), 3)
        for chamada in apis:
            self.assertIn("--method GET", chamada)
            self.assertNotRegex(chamada, r"(^| )(-f|-F|--field|--raw-field|--input|-X|--header|-H)( |$)")
            self.assertRegex(chamada, r"repos/dono/proj/rules/branches/(develop|homolog|main)$")
        self.assertEqual(sorted(c.rsplit("/", 1)[1] for c in apis), ["develop", "homolog", "main"])

    def test_main_sem_protecao_vira_problema_que_cita_a_branch_e_a_skill_ci_cd(self):
        self.sem_protecao("main")
        r = self.doutor()
        self.assertEqual(r.returncode, 1)
        self.assertIn("A branch main no GitHub está sem proteção", r.stdout)
        self.assertIn("ci-cd", r.stdout)
        self.assertNotIn("develop no GitHub está sem", r.stdout)
        self.assertTrue(any(c.endswith("repos/dono/proj/branches/main/protection") and "--method GET" in c for c in self.apis()))

    def test_protecao_classica_vale_quando_os_rulesets_estao_vazios(self):
        self.sem_protecao("main")
        self.resp("protecao-main", '{"url": "https://api.github.com/x", "required_pull_request_reviews": {"required_approving_review_count": 1}}')
        self.assertEqual(self.doutor().stdout, "")

    def test_ruleset_desativado_ou_em_avaliacao_e_regra_que_nao_exige_pr_nem_check_nao_contam(self):
        for regras in ('[{"type": "pull_request", "enforcement": "disabled"}]', '[{"type": "pull_request", "enforcement": "evaluate"}]',
                       '[{"type": "deletion"}]'):
            with self.subTest(regras=regras):
                self.resp("regras-main", regras)
                self.assertIn("A branch main no GitHub está sem proteção", self.doutor().stdout)

    def test_403_e_404_do_repositorio_viram_nao_consegui_conferir_nunca_protegida_nem_sem_protecao(self):
        casos = {"403": ("regras-main", "gh: Resource not accessible by integration (HTTP 403)"),
                 "repositorio": ("repo", "gh: Could not resolve to a Repository (HTTP 404)")}
        for nome, (alvo, texto) in casos.items():
            with self.subTest(nome=nome):
                self.resp(alvo, texto, 1)
                r = self.doutor()
                self.assertIn("Não consegui conferir", r.stdout)
                self.assertNotIn("sem proteção", r.stdout)
                self.assertNotIn("está protegida", r.stdout)
                self.assertNotIn("Resource not accessible", r.stdout)
                (self.home / f"gh-{alvo}").unlink()

    def test_404_de_branch_sem_o_repo_view_ter_respondido_nao_vira_sem_protecao(self):
        self.resp("repo", "gh: Not Found (HTTP 404)", 1)
        self.sem_protecao("main")
        self.assertNotIn("sem proteção", self.doutor().stdout)

    def test_sem_rede_fica_em_silencio(self):
        for ramo in ("develop", "homolog", "main"):
            self.resp(f"regras-{ramo}", "error connecting to api.github.com", 1)
        r = self.doutor()
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.resp("repo", "error connecting to api.github.com", 1)
        self.assertEqual(self.doutor().stdout, "")

    def test_formato_inesperado_da_resposta_e_nao_consegui_conferir_sem_excecao(self):
        for lixo in ("garbage", "", "{}", "null", "[1, 2]", '{"x": '):
            with self.subTest(lixo=lixo):
                self.resp("regras-main", lixo)
                self.resp("protecao-main", lixo)
                r = self.doutor()
                self.assertNotIn("Traceback", r.stdout + r.stderr)
                self.assertNotIn("A branch main no GitHub está sem", r.stdout)
                self.assertIn("Não consegui conferir", r.stdout)

    def test_nome_do_repositorio_fora_do_padrao_nao_chega_ao_endpoint(self):
        for nome in ("a/b -X DELETE", "../x", "-f/y", "a/b/../c", "a/..", "a b/c", "dono/proj\nx", "so-um-segmento"):
            with self.subTest(nome=nome):
                self.gh_log.unlink(missing_ok=True)
                self.resp("repo", json.dumps({"nameWithOwner": nome, "url": "https://github.com/dono/proj"}))
                r = self.doutor()
                self.assertEqual(self.apis(), [])
                self.assertIn("Não consegui conferir", r.stdout)

    def test_outro_host_nao_e_consultado(self):
        r = self.doutor(env={**self.env, "GH_HOST": "outro.exemplo"})
        self.assertEqual(self.apis(), [])
        self.assertIn("Não consegui conferir", r.stdout)
        self.gh_log.unlink(missing_ok=True)
        self.resp("repo", '{"nameWithOwner": "dono/proj", "url": "https://outro.exemplo/dono/proj"}')
        r = self.doutor()
        self.assertEqual(self.apis(), [])
        self.assertIn("Não consegui conferir", r.stdout)

    def test_modo_rapido_e_o_hook_nao_chamam_o_gh(self):
        self.sem_protecao("main")
        self.doutor("--rapido")
        self.assertFalse(self.gh_log.exists() and self.gh_log.read_text())
        for evento in ("SessionStart", "Stop"):
            entrada = {"hook_event_name": evento, "session_id": "s1", "cwd": str(self.proj)}
            subprocess.run([sys.executable, str(HOOK)], input=json.dumps(entrada), env=self.env, cwd=self.proj, capture_output=True,
                           text=True, timeout=30)
        self.assertFalse(self.gh_log.exists() and self.gh_log.read_text())

    def test_branch_que_nao_existe_no_remoto_e_pulada(self):
        self.git("push", "-q", "origin", "--delete", "homolog")
        self.git("branch", "-D", "homolog")
        self.git("update-ref", "-d", "refs/remotes/origin/homolog")
        self.doutor()
        self.assertFalse(any(c.endswith("/homolog") for c in self.apis()))

    def test_sem_login_no_gh_so_o_aviso_do_login(self):
        (self.home / "gh-sem-login").write_text("", encoding="utf-8")
        r = self.doutor()
        self.assertIn("gh auth login", r.stdout)
        self.assertNotIn("proteção", r.stdout.replace("proteção do git", ""))
        self.assertEqual([c for c in self.chamadas() if not c.startswith("auth status")], [])

    def test_a_saida_do_gh_nunca_aparece_no_aviso(self):
        self.resp("regras-main", self.MARCADOR, 1)
        r = self.doutor()
        self.assertNotIn(self.MARCADOR, r.stdout + r.stderr)
        self.resp("regras-main", "[]")
        self.resp("protecao-main", self.MARCADOR, 1)
        r = self.doutor()
        self.assertNotIn(self.MARCADOR, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
