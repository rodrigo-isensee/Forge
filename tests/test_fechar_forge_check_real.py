"""E7 (TEMPO-B2): o `forge-fechar` com o `bin/forge-check` real no passo 1. Módulo próprio para que só ele, e não todo `test_fechar_*`
(que importa `test_fechar`), entre no mapa FORGE_CHECK do `bin/forge-testes`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` falso) sem herdar os testes dele.
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
import test_fechar_move_cartao as mc  # noqa: E402  (idem)


class FecharComOForgeCheckReal(unittest.TestCase):
    """E7 (TEMPO-B2, review A1 do L08): o `forge-fechar` passa o sha da branch ao `forge-check pr`; com o `forge-check` real, o passo 1
    acha a branch pelo sha, lê os briefs dela e para sem a linha `entrega conferida` do head (nada é aberto nem mesclado)."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown  # o cenário do Fechar, sem herdar os testes dele

    def setUp(self):
        base.Fechar.setUp(self)
        real = self.tmp / "check-real"
        real.write_text(f'#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\nexec "{sys.executable}" "{base.RAIZ / "bin" / "forge-check"}" "$@"\n',
                        encoding="utf-8")
        real.chmod(0o755)
        self.env["FORGE_CHECK"] = str(real)
        self.git("switch", "-q", "melhoria/x")
        self.entrega = self.git("rev-parse", "HEAD")
        for pasta, tipo, extra in (("reviews", "review", "revisor: forge:tech-lead\n"),
                                   ("qa", "qa", "escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n")):
            (self.proj / "docs" / pasta).mkdir(parents=True)
            (self.proj / "docs" / pasta / "x.md").write_text(
                f"---\ntipo: {tipo}\ncontrato: 1\npedido: x\nbranch: melhoria/x\ncommit: {self.entrega}\nparecer: aprovado\n{extra}"
                f"data: 2026-11-04\n---\n# parecer\n\n- ci: {self.entrega} verde\n", encoding="utf-8")  # PARECER-LE-O-CI
        self.git("add", "docs")
        self.git("commit", "-q", "-m", "docs: pareceres")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        contrib = self.tmp / ".forge-contrib" / "docs"  # HOME é o tmp: o pedido e o brief moram onde o Jarvis do Forge os guarda
        (contrib / "briefs").mkdir(parents=True)
        (contrib / "pedidos").mkdir(parents=True)
        (contrib / "briefs" / "real-tech-lead-1.md").write_text("Pedido: real\nBranch: melhoria/x   Base: develop\n\n## Objetivo\nx\n",
                                                               encoding="utf-8")
        self.pedido = contrib / "pedidos" / "real.md"

    def test_sem_a_conferida_do_head_para_no_passo_1(self):
        self.pedido.write_text("# real\n\n## Histórico\n- 2026-11-04 08:00: aberto\n", encoding="utf-8")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("conferência: nenhuma linha", r.stdout + r.stderr)
        self.assertIn("parou no passo 1", r.stdout + r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh pr create", "gh pr merge"))])

    def test_com_a_conferida_do_head_fecha(self):
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega} (E1.2)\n", encoding="utf-8")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue([c for c in self.chamadas() if c.startswith("gh pr merge melhoria/x --squash")])


class DevelopSoNoFim(unittest.TestCase):
    """F3 (v0481 E30.1): a develop entra uma vez, no passo 2b; com o merge limpo (a árvore do `git merge-tree`), o parecer aprovado no
    head revisado segue valendo no head com a base, sem parecer novo; qualquer byte à mão no merge o desatualiza."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown

    def setUp(self):
        FecharComOForgeCheckReal.setUp(self)
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega} (E1.2)\n", encoding="utf-8")
        (self.proj / "c").write_text("3\n")  # a develop anda depois do parecer, sem arquivo em comum
        self.git("add", "c")
        self.git("commit", "-q", "-m", "feat: c na develop")
        self.git("push", "-q", "origin", "develop")
        self.develop = self.git("rev-parse", "develop")

    def mesclado_no(self):
        return [c.split()[-1] for c in self.chamadas() if c.startswith("gh pr merge melhoria/x --squash --match-head-commit")]

    def autor_mescla_a_develop(self, mao=None):
        self.git("switch", "-q", "melhoria/x")
        self.git("merge", "-q", "--no-commit", "develop")
        if mao:
            (self.proj / "b").write_text(mao)
            self.git("add", "b")
        self.git("commit", "-q", "--no-edit")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")

    def test_o_2b_traz_a_base_uma_vez_e_o_parecer_do_head_revisado_vale(self):
        revisado = self.git("rev-parse", "melhoria/x")
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.count("trago a base por merge (H4)"), 1, r.stdout)
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("forge-check pr x")]), 2,
                         "o passo 1 roda no head revisado e no head com a base, com o mesmo parecer")
        (novo,) = self.mesclado_no()
        self.assertEqual(self.git("rev-parse", f"{novo}^1", f"{novo}^2").split(), [revisado, self.develop])
        self.assertEqual(self.git("rev-parse", f"{novo}^{{tree}}"),
                         self.git("merge-tree", "--write-tree", revisado, self.develop).splitlines()[0])

    def test_merge_da_base_pelo_autor_sem_resolucao_nao_reabre_o_parecer(self):
        self.autor_mescla_a_develop()
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("trago a base", r.stdout)
        self.assertEqual(len(self.mesclado_no()), 1)

    def test_merge_da_base_com_mudanca_a_mao_desatualiza_o_parecer(self):
        self.autor_mescla_a_develop(mao="2 e mais\n")  # um byte da branch a mais no commit de merge
        r = self.fechar("x", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("parou no passo 1", r.stderr)
        self.assertIn("desatualizado: b mudou depois do parecer", r.stdout + r.stderr)
        self.assertEqual(self.mesclado_no(), [])


# O `gh` que o forge-check real acha no PATH (o fechar usa o FORGE_GH): PR pronto no head da branch e o CI ainda rodando.
GH_DO_CHECK = '''#!/usr/bin/env bash
echo "gh-do-check $*" >> "$REGISTRO"
case "$*" in
  "pr view melhoria/x --json number,state,isDraft,headRefOid,baseRefName")
    printf '{"number": 7, "state": "OPEN", "isDraft": false, "headRefOid": "%s", "baseRefName": "develop"}\\n' "$(cat "$ESTADO/head_do_pr")" ;;
  "pr checks 7 --json name,bucket,workflow") echo '[{"name": "bateria", "bucket": "pending", "workflow": "CI"}]' ;;
  api*) echo '{"message": "Not Found"}'; exit 1 ;;
  *) exit 64 ;;
esac
'''


class FecharComChecksPendentes(unittest.TestCase):
    """A1 e A2 do review (E3.80): com o PR pronto e o CI rodando, o `forge-check pr` real reprova, mas o passo 1 do fechar só confere os
    pareceres (os checks ficam para os passos 4 e 6): com checks pendentes, o fechamento passa do passo 1 e espera no passo 4."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown

    def setUp(self):
        FecharComOForgeCheckReal.setUp(self)
        self.pedido.write_text(f"# real\n\n## Histórico\n- 2026-11-04 09:00: entrega conferida {self.entrega} (E1.2)\n", encoding="utf-8")
        pasta = self.tmp / "gh-do-check"
        pasta.mkdir()
        (pasta / "gh").write_text(GH_DO_CHECK, encoding="utf-8")
        (pasta / "gh").chmod(0o755)
        self.env["PATH"] = f"{pasta}:{self.env['PATH']}"
        (self.estado / "head_do_pr").write_text(self.git("rev-parse", "melhoria/x") + "\n", encoding="utf-8")
        (self.estado / "checks").write_text("bateria\tpending\t1m\turl\n")

    def test_o_forge_check_real_reprova_o_pr_com_checks_pendentes(self):  # o falso responde: sem a variável do fechar, reprova
        r = subprocess.run([sys.executable, "-I", str(base.RAIZ / "bin" / "forge-check"), "pr", "x", "--ref", "refs/heads/melhoria/x",
                            "--base", "origin/develop"], cwd=self.proj, env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("checks do head no PR #7 não concluídos e verdes: CI/bateria (pending)", r.stdout)

    def test_checks_pendentes_passam_do_passo_1_e_param_no_4_sem_merge(self):
        r = self.fechar("x", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("parou no passo 1", r.stdout + r.stderr)
        self.assertIn("parou no passo 4", r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh pr merge")])
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh-do-check pr ")], "o passo 1 não lê os checks")



class MoverCartaoComOForgeCheckReal(unittest.TestCase):
    """FECHAR-MOVE-CARTAO: com o `forge-check movimento` real, o merge provado grava a linha do cartão no histórico do quadro."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown
    com_historico = mc.Teste.com_historico

    def setUp(self):
        mc.Teste.setUp(self)
        (self.tmp / "check").write_text(f'#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\n[ "$1" = movimento ] || exit 0\n'
                                        f'exec "{sys.executable}" -I "{base.RAIZ / "bin" / "forge-check"}" "$@"\n', encoding="utf-8")

    def test_a_linha_do_cartao_vai_ao_historico(self):
        self.com_historico("2026-11-01T10:00:00-03:00 | K-1 | Em andamento | Code review | —")
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        ultima = [c.strip() for c in self.historico.read_text(encoding="utf-8").splitlines()[-1].strip("|").split("|")]
        self.assertEqual(ultima[1:4], ["K-1", "Code review", "Pronto"])
        self.assertTrue(ultima[4].startswith("mesclado em develop: PR #7, merge 0123456"), ultima)


if __name__ == "__main__":
    unittest.main()
