"""FECHAR-BUSCA-PARECERES-CITADOS (v0478 E132.1): antes do passo 1, o forge-fechar busca só por leitura os commits de `parecer
conferido <sha40>` do `## Histórico` do pedido que a cópia não lê: da origin pelo sha40 e, para a branch do parecer já apagada na
origin, da cópia --principal; diz os que não existem em lugar nenhum. Sem push, sem ref nova, sem mudar o veredito do passo 1.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) pelo `test_fechar_sha_conferido`.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar_sha_conferido as sc  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

INEXISTENTE, FORA_DO_HISTORICO = "c" * 40, "d" * 40
# registra cada `git fetch` desta cópia que leva um sha40 e segue para o git falso de baixo
FETCH_REGISTRADO = r'''#!/usr/bin/env bash
if [ "$1" = fetch ] && [[ " $* " =~ \ [0-9a-f]{40}\  ]]; then echo "$*" >> "$FETCHES"; fi
exec "$GIT_DE_BAIXO" "$@"
'''


class FecharBuscaPareceres(unittest.TestCase):
    tearDown, git, fechar, chamadas = sc.FecharShaConferido.tearDown, sc.FecharShaConferido.git, sc.FecharShaConferido.fechar, sc.FecharShaConferido.chamadas

    def setUp(self):
        sc.FecharShaConferido.setUp(self)
        # A: commit de parecer só na origin (branch parecer/a de outra cópia); B: só na cópia principal (branch apagada na origin)
        self.outra, self.principal = self.tmp / "outra", self.tmp / "principal"
        for pasta in (self.outra, self.principal):
            self.git("clone", "-q", str(self.remoto), str(pasta), cwd=self.tmp)
        self.git("-C", str(self.outra), "switch", "-q", "-c", "parecer/a", "origin/develop")
        self.git("-C", str(self.outra), "commit", "-q", "--allow-empty", "-m", "docs(review): parecer A")
        self.git("-C", str(self.outra), "push", "-q", "origin", "parecer/a")
        self.a = self.git("-C", str(self.outra), "rev-parse", "HEAD")
        self.git("-C", str(self.principal), "switch", "-q", "-c", "parecer/b", "origin/develop")
        self.git("-C", str(self.principal), "commit", "-q", "--allow-empty", "-m", "docs(review): parecer B")
        self.b = self.git("-C", str(self.principal), "rev-parse", "HEAD")

    def pedido(self, *shas, pasta=None):
        pasta = pasta or self.tmp / ".forge-contrib"
        (pasta / "docs" / "pedidos").mkdir(parents=True, exist_ok=True)
        linhas = "".join(f"- 2026-11-23 10:0{i}: docs/reviews/x.md aprovado: parecer conferido {s}\n" for i, s in enumerate(shas))
        (pasta / "docs" / "pedidos" / "p1.md").write_text(
            f"# Pedido p1\n\n## Histórico\n{linhas}\n## Notas\n- parecer conferido {FORA_DO_HISTORICO}\n", encoding="utf-8")

    def le(self, sha):
        return sc.base.subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=self.proj, env=self.env).returncode == 0

    def test_busca_da_origin_e_da_principal_e_diz_o_que_nao_existe(self):
        self.pedido(self.a, self.b, INEXISTENTE)
        self.assertFalse(self.le(self.a) or self.le(self.b))
        r = self.fechar("p1", "--ref", "melhoria/x", "--principal", str(self.principal))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(self.le(self.a) and self.le(self.b), r.stderr)
        self.assertIn(f"sem commit aqui nem em origin {self.principal}: {INEXISTENTE}", r.stderr)
        self.assertNotIn(FORA_DO_HISTORICO, r.stderr + r.stdout)
        self.assertNotIn(self.a, r.stderr)
        self.assertEqual(self.git("for-each-ref", "--contains", self.a), "")  # sem ref nova
        self.assertEqual(self.git("for-each-ref", "--contains", self.b), "")
        fetch_head = self.proj / ".git" / "FETCH_HEAD"  # o do `fetch origin homolog` do passo 1 pode existir; o da busca, não
        self.assertNotIn(self.b, fetch_head.read_text() if fetch_head.exists() else "")
        self.assertEqual(self.chamadas()[0], "forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop")

    def test_sem_principal_busca_so_da_origin(self):
        self.pedido(self.a, self.b)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(self.le(self.a))
        self.assertFalse(self.le(self.b))
        self.assertIn(f"sem commit aqui nem em origin: {self.b}", r.stderr)

    def test_pedido_da_copia_principal_do_repositorio(self):
        (self.proj / ".git" / "info" / "exclude").write_text("docs/\n", encoding="utf-8")
        self.pedido(self.a, pasta=self.proj)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(self.le(self.a), r.stderr)

    def test_tudo_legivel_nao_busca_nada(self):
        self.pedido(self.git("rev-parse", "develop"))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("sem commit aqui", r.stderr)
        self.assertEqual(self.git("for-each-ref", "refs/remotes/origin/parecer"), "")  # sem o fetch da refspec padrão

    def test_o_veredito_do_passo_1_nao_muda(self):
        self.pedido(self.a)
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_RC="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 1: forge-check pr acusou violação", r.stderr)
        self.assertTrue(self.le(self.a))

    def test_principal_que_nao_e_repositorio_para_antes_do_passo_1(self):
        self.pedido(self.a)
        r = self.fechar("p1", "--ref", "melhoria/x", "--principal", str(self.tmp / "nada"))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--principal pede a pasta de uma cópia git", r.stderr)
        self.assertEqual(self.chamadas(), [])
        self.assertFalse(self.le(self.a))

    def test_principal_sem_pasta_e_erro_de_uso(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--principal")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--principal pede a pasta de uma cópia git", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_sha_ausente_entre_muitos_busca_por_metades(self):  # A1 do review E132.2: só a metade que falha se divide de novo
        for i in range(14):
            self.git("-C", str(self.outra), "commit", "-q", "--allow-empty", "-m", f"docs(review): parecer A{i}")
        self.git("-C", str(self.outra), "push", "-q", "origin", "parecer/a")
        bons = self.git("-C", str(self.outra), "rev-list", "-15", "parecer/a").split()
        self.pedido(*bons, INEXISTENTE)
        embrulho, fetches = self.tmp / "bin2", self.tmp / "fetches"
        embrulho.mkdir()
        (embrulho / "git").write_text(FETCH_REGISTRADO, encoding="utf-8")
        (embrulho / "git").chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", FETCHES=str(fetches), GIT_DE_BAIXO=str(self.tmp / "bin" / "git"),
                        PATH=f"{embrulho}:{self.env['PATH']}")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertTrue(all(self.le(s) for s in bons), r.stderr)
        self.assertIn(f"sem commit aqui nem em origin: {INEXISTENTE}", r.stderr)
        self.assertEqual(len(fetches.read_text().splitlines()), 9)  # 16, 8 e 8, 4 e 4, 2 e 2, 1 e 1; um por sha seriam 17

    def test_principal_vazio_e_erro_de_uso(self):  # A2 do review E132.2
        r = self.fechar("p1", "--ref", "melhoria/x", "--principal", "")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--principal pede a pasta de uma cópia git (recebi o valor vazio)", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_promover_recusa_principal(self):
        r = self.fechar("v9", "--promover", "a" * 40, "--principal", str(self.principal))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--promover recebe só", r.stderr)

    def test_limpar_recusa_principal(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--principal", str(self.principal))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--principal não combina com --limpar", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_lote_recusa_principal(self):
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", "--principal", str(self.principal))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--lote recebe só", r.stderr)


if __name__ == "__main__":
    unittest.main()
