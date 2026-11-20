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
                "data: 2026-11-04\n---\n# parecer\n", encoding="utf-8")
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
        self.assertTrue([c for c in self.chamadas() if c.startswith("gh pr merge melhoria/x --auto --squash")])


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
    pareceres (os checks ficam para os passos 4 e 6): o --armar arma o auto-merge em vez de parar no passo 1."""

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

    def test_armar_com_checks_pendentes_passa_do_passo_1_e_arma(self):
        (self.estado / "auto_arma").write_text("")
        r = self.fechar("x", "--ref", "melhoria/x", "--armar")
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertNotIn("parou no passo 1", r.stdout + r.stderr)
        self.assertIn("auto-merge armado no PR #7", r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh-do-check pr ")], "o passo 1 não lê os checks")



# AE1.2 (E58.29): o `gh` e o `git` que o `forge-check movimento` real acha no PATH. O clone do teste tem origin local; o git responde
# o origin do GitHub (o forge-check recusa caminho local) e repassa o resto. O gh só responde preso a esse repositório (`--repo`): o PR 7
# MERGED na develop, com o merge na origin/develop do clone e o corpo que o `gh pr create` do forge-fechar gravou. A variável do próximo
# git não começa com GIT_: o git() do forge-check tira as GIT_* do ambiente.
GIT_DO_MOVIMENTO = """#!/usr/bin/env bash
if [ "$1" = -C ] && [ "$3 $4 $5" = "remote get-url origin" ]; then echo https://github.com/teste/forge.git; exit 0; fi
exec "$PROXIMO_GIT" "$@"
"""
GH_DO_MOVIMENTO = """#!/usr/bin/env bash
echo "gh-do-movimento $*" >> "$REGISTRO"
case "$*" in
  "pr view 7 --json number,state,baseRefName,headRefName,mergedAt,mergedBy,mergeCommit --repo github.com/teste/forge")
    printf '{"number": 7, "state": "MERGED", "baseRefName": "develop", "headRefName": "melhoria/x", "mergedAt": "2026-11-20T10:00:00Z", "mergeCommit": {"oid": "%s"}}\\n' \\
      "$(git rev-parse refs/remotes/origin/develop)" ;;
  "pr view 7 --json number,title,body --repo github.com/teste/forge")
    python3 -I -c 'import json, sys; print(json.dumps({"number": 7, "title": "melhoria/x", "body": open(sys.argv[1], encoding="utf-8").read()}))' \\
      "$ESTADO/corpo_criado" ;;
  *) exit 64 ;;
esac
"""


class MoverCartaoComOForgeCheckReal(unittest.TestCase):
    """FECHAR-MOVE-CARTAO: com o `forge-check movimento` real, o merge provado grava a linha do cartão no histórico do quadro; a prova
    pr:#7 se confere no corpo do PR que o forge-fechar abriu (AE1.2)."""

    git, fechar, chamadas, tearDown = base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas, base.Fechar.tearDown
    com_historico = mc.Teste.com_historico

    def setUp(self):
        mc.Teste.setUp(self)
        (self.tmp / "check").write_text(f'#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\n[ "$1" = movimento ] || exit 0\n'
                                        f'exec "{sys.executable}" -I "{base.RAIZ / "bin" / "forge-check"}" "$@"\n', encoding="utf-8")
        pasta = self.tmp / "do-movimento"
        pasta.mkdir()
        for nome, texto in (("gh", GH_DO_MOVIMENTO), ("git", GIT_DO_MOVIMENTO)):
            (pasta / nome).write_text(texto, encoding="utf-8")
            (pasta / nome).chmod(0o755)
        self.env.update(PROXIMO_GIT=str(self.tmp / "bin" / "git"), PATH=f"{pasta}:{self.env['PATH']}")

    def test_a_linha_do_cartao_vai_ao_historico(self):
        self.com_historico("2026-11-01T10:00:00-03:00 | K-1 | Em andamento | Code review | —")
        r = self.fechar("p1", "--ref", "melhoria/x", "--cartao", "K-1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        ultima = [c.strip() for c in self.historico.read_text(encoding="utf-8").splitlines()[-1].strip("|").split("|")]
        self.assertEqual(ultima[1:4], ["K-1", "Code review", "Pronto"])
        self.assertTrue(ultima[4].startswith("mesclado em develop: PR #7, merge 0123456 · prova: pr:#7 "), ultima)
        self.assertIn(" origem=github.com/teste/forge (onde: develop sim", ultima[4])


if __name__ == "__main__":
    unittest.main()
