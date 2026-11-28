"""bin/forge-contador: linha da versão (fragmentos da develop, patch acima, teto) e visão do backlog."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

BIN = Path(__file__).resolve().parent.parent / "bin" / "forge-contador"

QUADRO = """# Quadro

## Entrada
| ID | Cartão | Obs. |
|---|---|---|
| A | a | x |
| B | b | x |

## Pronto para fazer (WIP 5)
| ID | Cartão | Obs. |
|---|---|---|
| C | c | x |

## Code review (WIP 2)
| ID | Cartão | Obs. |
|---|---|---|

## Pronto
| ID | Cartão | Obs. |
|---|---|---|
| D | d | x |

## Fechado sem entrega
| ID | Cartão | Obs. |
|---|---|---|
| E | e | x |

## Aguardando o dono (PA-6: ação · comando)
| ID | Cartão | Obs. |
|---|---|---|
| F | f | x |
"""


def historico(*linhas):
    return "- 2026-11-22 nota solta fora da tabela\n| Quando | Cartão | De | Para | Obs. |\n|---|---|---|---|---|\n" + "".join(
        f"| {q} | X | {de} | {para} | o |\n" for q, de, para in linhas)


class Base(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.dir = Path(t.name).resolve()
        self.raiz = self.dir / "repo"
        self.env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))}
                                  | {"HOME": str(self.dir), "GIT_CONFIG_GLOBAL": "/dev/null",
                                     "GIT_CONFIG_SYSTEM": "/dev/null"})
        self.git("init", "-q", "-b", "develop", str(self.raiz), cwd=self.dir)

    def git(self, *a, cwd=None):
        return subprocess.run(["git", *a], cwd=cwd or self.raiz, env=self.env, capture_output=True, text=True,
                              check=True)

    def commit(self, arquivos, msg="c"):
        for nome, texto in arquivos.items():
            p = self.raiz / nome
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(texto, encoding="utf-8")
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)

    def contador(self, *a):
        return subprocess.run([sys.executable, "-I", str(BIN), "--raiz", str(self.raiz), *a], cwd=self.dir,
                              env=self.env, capture_output=True, text=True)

    def escrever(self, nome, texto):
        p = self.dir / nome
        p.write_text(texto, encoding="utf-8")
        return str(p)


class LinhaDaVersao(Base):
    def test_conta_fragmentos_sem_readme_e_sobe_o_patch(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "1.4.9"}),
                     "changelog.d/README.md": "r", "changelog.d/a.md": "a", "changelog.d/b.md": "b",
                     "changelog.d/nota.txt": "n"})
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (0, "1.5.0: 2 de 20 (develop local, sem origin)\n"), r.stderr)

    def test_versao_corta_no_9(self):
        # VERSAO-PATCH-ATE-9 (v048 E2.1): depois de X.Y.9 vem X.(Y+1).0; o patch nunca passa de 9
        for atual, seguinte in (("0.47.9", "0.48.0"), ("0.47.19", "0.48.0"), ("0.48.0", "0.48.1"),
                                ("0.48.8", "0.48.9"), ("0.48.9", "0.49.0")):
            with self.subTest(atual=atual):
                self.commit({".claude-plugin/plugin.json": json.dumps({"version": atual}), "changelog.d/a.md": "a"})
                r = self.contador()
                self.assertEqual((r.returncode, r.stdout), (0, f"{seguinte}: 1 de 20 (develop local, sem origin)\n"), r.stderr)

    def test_readme_com_caixa_mista_nao_conta(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "1.4.9"}),
                     "changelog.d/Readme.md": "r", "changelog.d/a.md": "a"})
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (0, "1.5.0: 1 de 20 (develop local, sem origin)\n"), r.stderr)

    def test_le_a_ref_e_nao_a_arvore(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}), "changelog.d/a.md": "a"})
        (self.raiz / "changelog.d" / "solto.md").write_text("s", encoding="utf-8")
        self.assertEqual(self.contador().stdout, "0.1.1: 1 de 20 (develop local, sem origin)\n")

    def test_sem_plugin_json_usa_a_ultima_marca(self):
        self.commit({"changelog.d/a.md": "a"})
        self.git("tag", "v2.0.3")
        self.assertEqual(self.contador().stdout, "2.0.4: 1 de 20 (develop local, sem origin)\n")

    def test_sem_plugin_json_nem_marca_parte_de_zero(self):
        self.commit({"changelog.d/a.md": "a"})
        self.assertEqual(self.contador().stdout, "0.0.1: 1 de 20 (develop local, sem origin)\n")

    def test_teto_da_configuracao(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}),
                     ".forge/config.json": json.dumps({"teto_versao": 7}), "changelog.d/README.md": "r"})
        self.assertEqual(self.contador().stdout, "0.1.1: 0 de 7 (develop local, sem origin)\n")

    def test_fragmento_com_nome_nao_ascii_conta(self):
        self.commit({"changelog.d/a.md": "a", "changelog.d/ação.md": "b", "changelog.d/çé.md": "c"})
        self.assertEqual(self.contador().stdout, "0.0.1: 3 de 20 (develop local, sem origin)\n")

    def test_plugin_json_ilegivel_e_erro(self):
        for texto in ("{", "[]"):
            with self.subTest(texto=texto):
                self.commit({".claude-plugin/plugin.json": texto})
                r = self.contador()
                self.assertEqual((r.returncode, r.stdout), (2, ""))
                self.assertIn("versão ilegível", r.stderr)
                self.assertNotIn("Traceback", r.stderr)

    def test_teto_invalido_e_erro(self):
        for valor in (0, "20", True, -3):
            with self.subTest(valor=valor):
                self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}),
                             ".forge/config.json": json.dumps({"teto_versao": valor})})
                r = self.contador()
                self.assertEqual(r.returncode, 2)
                self.assertIn("teto_versao", r.stderr)

    def test_versao_ilegivel_e_erro(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "1.2"})})
        r = self.contador()
        self.assertEqual(r.returncode, 2)
        self.assertIn("versão ilegível", r.stderr)

    def test_configuracao_ilegivel_e_erro(self):
        for texto in ("{", "[]"):
            with self.subTest(texto=texto):
                self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}),
                             ".forge/config.json": texto})
                r = self.contador()
                self.assertEqual((r.returncode, r.stdout), (2, ""))
                self.assertIn("config.json", r.stderr)

    def test_ref_inexistente_e_erro(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"})})
        r = self.contador("--ref", "nao-existe")
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("git ", r.stderr)

    def test_com_ref_nao_diz_a_fonte(self):
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}), "changelog.d/a.md": "a"})
        self.assertEqual(self.contador("--ref", "develop").stdout, "0.1.1: 1 de 20\n")

    def test_sem_develop_e_erro(self):
        self.commit({"x": "x"})
        self.git("branch", "-m", "outra")
        r = self.contador()
        self.assertEqual(r.returncode, 2)
        self.assertIn("--ref", r.stderr)


class SemChangelog(Base):
    """Projeto sem changelog.d/: N = PRs mesclados (merge ou squash #n) na ref desde a última marca."""

    def test_conta_merges_e_squashes_desde_a_marca(self):
        self.commit({"a": "a"}, "feat: antes da marca (#1)")
        self.git("tag", "v1.2.0")
        self.commit({"b": "b"}, "feat: item (#2)")
        self.commit({"c": "c"}, "chore: direto, sem PR")
        self.git("switch", "-q", "-c", "ramo")
        self.commit({"d": "d"}, "wip interno (#90)")
        self.git("switch", "-q", "develop")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "merge", "-q", "--no-ff", "-m",
                 "Merge pull request #3 from x/ramo", "ramo")
        self.commit({"e": "e"}, "fix: outro item (#4)")
        self.assertEqual(self.contador().stdout, "1.2.1: 3 de 20 (develop local, sem origin)\n")

    def test_sem_pr_reconhecivel_diz_sem_contagem(self):
        self.commit({"a": "a"})
        self.git("tag", "v1.2.0")
        self.commit({"b": "b"}, "chore: direto, sem PR")
        self.assertEqual(self.contador().stdout, "1.2.1: sem contagem de 20 (develop local, sem origin)\n")

    def test_marca_no_topo_da_zero(self):
        self.commit({"a": "a"}, "chore: direto")
        self.git("tag", "v1.2.0")
        self.assertEqual(self.contador().stdout, "1.2.1: 0 de 20 (develop local, sem origin)\n")


class DevelopDoOrigin(Base):
    """DEVELOP-DO-GITHUB (v048 E14.1): sem --ref, conta pela develop do origin agora, nunca pela origin/develop local velha."""

    def setUp(self):
        super().setUp()
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}), "changelog.d/a.md": "a"})
        self.remoto = self.dir / "remoto.git"
        self.git("clone", "-q", "--bare", str(self.raiz), str(self.remoto), cwd=self.dir)
        self.git("remote", "add", "origin", str(self.remoto))
        self.git("fetch", "-q", "origin")
        self.velha = self.git("rev-parse", "origin/develop").stdout.strip()
        outra = self.dir / "outra"  # outra cópia integra dois itens; esta fica com a origin/develop atrasada
        self.git("clone", "-q", str(self.remoto), str(outra), cwd=self.dir)
        for nome in ("b", "c"):
            (outra / "changelog.d" / f"{nome}.md").write_text(nome, encoding="utf-8")
            self.git("add", "-A", cwd=outra)
            self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", nome, cwd=outra)
        self.git("push", "-q", "origin", "develop", cwd=outra)
        self.nova = self.git("rev-parse", "HEAD", cwd=outra).stdout.strip()

    def test_origin_develop_atrasada_conta_pela_do_origin(self):
        self.assertEqual(self.contador("--ref", "origin/develop").stdout, "0.1.1: 1 de 20\n")  # o número velho
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (0, f"0.1.1: 3 de 20 (develop do origin em {self.nova[:12]})\n"),
                         r.stderr)

    def test_commit_ja_presente_conta_sem_fetch(self):
        self.git("fetch", "-q", "origin")
        self.git("update-ref", "refs/remotes/origin/develop", self.velha)  # o commit fica, a ref local volta
        r = self.contador()
        self.assertEqual(r.stdout, f"0.1.1: 3 de 20 (develop do origin em {self.nova[:12]})\n", r.stderr)
        self.assertEqual(self.git("rev-parse", "origin/develop").stdout.strip(), self.velha)

    def test_origin_ilegivel_e_erro_claro(self):
        self.git("remote", "set-url", "origin", str(self.dir / "nao-existe.git"))
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("não li a develop do origin", r.stderr)
        self.assertIn("--ref", r.stderr)

    def test_origin_sem_develop_e_erro_claro(self):
        self.git("--git-dir", str(self.remoto), "branch", "-m", "develop", "outra")
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("não li a develop do origin", r.stderr)

    def test_fetch_que_falha_e_erro_claro(self):
        # packObjectsHook só vale da configuração global: o ls-remote passa, o fetch (que empacota) falha
        cfg = self.dir / "gitconfig"
        cfg.write_text("[uploadpack]\n\tpackObjectsHook = false\n", encoding="utf-8")
        self.env["GIT_CONFIG_GLOBAL"] = str(cfg)
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn(f"a develop do origin está em {self.nova[:12]}, que falta aqui, e o fetch falhou", r.stderr)

    def test_sem_origin_nem_develop_e_erro(self):
        self.git("remote", "remove", "origin")
        self.git("branch", "-m", "outra")
        r = self.contador()
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("sem origin e sem develop", r.stderr)


class Backlog(Base):
    def setUp(self):
        super().setUp()
        self.commit({".claude-plugin/plugin.json": json.dumps({"version": "0.1.0"}),
                     ".forge/config.json": json.dumps({"teto_versao": 3})})
        self.quadro = self.escrever("KANBAN.md", QUADRO)

    def test_so_quadro(self):
        r = self.contador("--quadro", self.quadro)
        self.assertEqual(r.stdout.splitlines()[1],
                         "backlog: 4 abertos (Entrada 2 · Pronto para fazer 1 · Aguardando o dono 1)"
                         " · versões que faltam: 2")
        self.assertEqual(len(r.stdout.splitlines()), 2)

    def test_previsao_pela_vazao_liquida(self):
        h = self.escrever("h.md", historico(
            ("2026-11-20T10:00-03:00", "Entrada", "Pronto"),
            ("2026-11-21T10:00-03:00", "Pronto para fazer", "Fechado sem entrega"),
            ("2026-11-22T09:00-03:00", "—", "Entrada"),
            ("2026-11-22T10:00-03:00", "Code review", "Pronto"),
            ("2026-11-22T11:00-03:00", "Code review", "Pronto"),
            ("2026-11-22T12:00-03:00", "Entrada", "Pronto para fazer"),
            ("2026-11-22T13:00-03:00", "Pronto", "Fechado sem entrega"),
            ("sem data", "—", "Entrada"),
            ("2026-11-19T10:00-03:00", "Entrada", "Pronto")))
        linhas = self.contador("--quadro", self.quadro, "--historico", h, "--data", "2026-11-22").stdout.splitlines()
        self.assertTrue(linhas[1].endswith(" · hoje +1 -2"), linhas[1])
        self.assertEqual(linhas[2], "previsão: 2026-11-26 pela vazão líquida de 1.0/dia nos últimos 3 dias")

    def test_crescendo_sem_data(self):
        h = self.escrever("h.md", historico(
            ("2026-11-22T09:00-03:00", "—", "Entrada"),
            ("2026-11-22T09:10-03:00", "Pronto", "Entrada"),
            ("2026-11-21T09:00-03:00", "Entrada", "Pronto")))
        linhas = self.contador("--quadro", self.quadro, "--historico", h, "--data", "2026-11-22").stdout.splitlines()
        self.assertTrue(linhas[1].endswith(" · hoje +2 -0 (crescendo)"), linhas[1])
        self.assertEqual(linhas[2], "previsão: sem data enquanto crescer")

    def test_quadro_vazio(self):
        vazio = self.escrever("vazio.md", "## Entrada\n| ID | Cartão |\n|---|---|\n\n## Pronto\n| ID | Cartão |\n|---|---|\n| D | d |\n")
        self.assertEqual(self.contador("--quadro", vazio).stdout.splitlines()[1],
                         "backlog: 0 abertos (nenhum) · versões que faltam: 0")

    def test_vazao_zero_sem_data(self):
        h = self.escrever("h.md", historico(
            ("2026-11-22T09:00-03:00", "—", "Entrada"),
            ("2026-11-22T10:00-03:00", "Entrada", "Pronto")))
        linhas = self.contador("--quadro", self.quadro, "--historico", h, "--data", "2026-11-22").stdout.splitlines()
        self.assertTrue(linhas[1].endswith(" · hoje +1 -1"), linhas[1])
        self.assertEqual(linhas[2], "previsão: sem data enquanto crescer")

    def test_historico_sem_quadro_e_recusado(self):
        r = self.contador("--historico", self.escrever("h.md", historico()))
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("--historico pede --quadro", r.stderr)

    def test_previsao_alem_do_calendario_e_erro(self):
        h = self.escrever("h.md", historico(("9999-12-31T10:00-03:00", "Entrada", "Pronto")))
        r = self.contador("--quadro", self.quadro, "--historico", h, "--data", "9999-12-31")
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertTrue(r.stderr.startswith("forge-contador: "), r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_quadro_fora_de_utf8_e_erro(self):
        quadro = self.dir / "ruim.md"
        quadro.write_bytes(b"## Entrada\n| A | \xff |\n")
        r = self.contador("--quadro", str(quadro))
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("não é UTF-8", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    def test_quadro_ausente_e_erro(self):
        r = self.contador("--quadro", str(self.dir / "nao.md"))
        self.assertEqual((r.returncode, r.stdout), (2, ""))


if __name__ == "__main__":
    unittest.main()
