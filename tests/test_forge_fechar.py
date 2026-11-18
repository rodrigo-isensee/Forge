"""E3.45 (v0474): o passo 4 do `bin/forge-fechar` soma aos pares de CHECKS_EXIGIDOS os checks que o ruleset ou a proteção da develop exigem.

Reaproveita o ambiente de `test_fechar_checks_exigidos` (o `gh` falso com a sequência de leituras dos checks). O `gh api` falso devolve a
saída já filtrada pelo `--jq` (sem rede, R-CUSTO): `api_regras` e `api_protecao` no estado, uma linha por contexto; sem o arquivo, sai com 1,
como o 404 da branch sem regra.

MP6 (v0474 E3.251): o --limpar também acha e apaga os clones da branch em ~/.forge-contrib/wt (classe LimparClones).
"""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as fechar_base  # noqa: E402  (o módulo: a classe seria coletada de novo aqui)
import test_fechar_checks_exigidos as exig  # noqa: E402

API = '''if [ "$1" = api ]; then  # a chamada já foi registrada no começo do gh falso
  [ "$3" = --jq ] || exit 64
  case "$2" in
    "repos/{owner}/{repo}/rules/branches/develop") f=api_regras ;;
    "repos/{owner}/{repo}/branches/develop/protection/required_status_checks") f=api_protecao ;;
    *) exit 64 ;;
  esac
  [ -f "$ESTADO/$f" ] || { echo '{"message":"Not Found"}'; exit 1; }
  cat "$ESTADO/$f"; exit 0
fi
'''
CASO = 'case "$1 $2" in\n'


class FecharExigidosDoDestino(unittest.TestCase):
    E = exig.FecharChecksExigidos
    tearDown, git, fechar, chamadas, leituras, para = E.tearDown, E.git, E.fechar, E.chamadas, E.leituras, E.para
    leituras_de_checks, sem_merge = E.leituras_de_checks, E.sem_merge

    def setUp(self):
        self.E.setUp(self)
        gh = self.tmp / "gh"
        texto = gh.read_text(encoding="utf-8")
        self.assertEqual(texto.count(CASO), 1)
        gh.write_text(texto.replace(CASO, API + CASO, 1), encoding="utf-8")

    def test_exigido_do_ruleset_ausente_para(self):
        (self.estado / "api_regras").write_text("lint\n")
        self.para(exig.OK, "lint", "ausente após 0s", "--espera", "0")

    def test_exigido_da_protecao_em_skipping_para(self):
        (self.estado / "api_protecao").write_text("lint\n")
        self.para([*exig.OK, "lint\tskipping\t0\turl"], "lint", "skipping")

    def test_exigido_do_ruleset_de_qualquer_workflow_em_pass_mescla(self):
        (self.estado / "api_regras").write_text("lint\n")
        self.leituras([*exig.OK, "lint\tpass\t1m\turl\tQualquer"])
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("exigidos em pass: CI/bateria CI/bateria (python 3.14) Catraca/catraca */lint)", r.stdout)
        chamadas = [c for c in self.chamadas() if c.startswith("gh api")]
        self.assertIn("gh api repos/{owner}/{repo}/rules/branches/develop --jq .[] | select(.type == \"required_status_checks\") | "
                      ".parameters.required_status_checks[].context", chamadas)

    def test_ruleset_ilegivel_nao_acrescenta_e_a_protecao_vale(self):  # o corpo do 404 do ruleset não vira exigido
        (self.estado / "api_protecao").write_text("lint\n")
        self.leituras([*exig.OK, "lint\tpass\t1m\turl"])
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("exigidos em pass: CI/bateria CI/bateria (python 3.14) Catraca/catraca */lint)", r.stdout)

    def test_sem_regra_legivel_os_pares_continuam(self):  # o fallback: a leitura que falha não tira nenhum par
        self.para(["bateria\tskipping\t0\turl", *exig.OK[1:]], "bateria", "skipping")


RM_FALSO = '#!/usr/bin/env bash\ncase "$*" in *"/.forge-contrib/wt/"*) echo "rm: negado" >&2; exit 1 ;; esac\nexec /bin/rm "$@"\n'


class LimparClones(unittest.TestCase):
    """MP6: o --limpar acha e apaga os clones da branch em ~/.forge-contrib/wt (o HOME do teste é a pasta temporária), só limpos, com tudo
    na origem e mesclados; o resto fica, com leitura no lugar de comando que apaga. Ambiente de `test_fechar.Fechar` (git e gh falsos)."""
    F = fechar_base.Fechar
    setUp, tearDown, git, fechar, resumo = F.setUp, F.tearDown, F.git, F.fechar, F.resumo

    def clone(self, nome="c1", branch="melhoria/x"):
        d = self.tmp / ".forge-contrib" / "wt" / nome
        d.parent.mkdir(parents=True, exist_ok=True)
        self.git("clone", "-q", str(self.remoto), str(d), cwd=self.tmp)
        self.git("switch", "-q", branch, cwd=d)
        return d

    def mesclado(self):
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {self.git('rev-parse', 'melhoria/x')}\n")

    def limpar(self, cwd=None):
        self.mesclado()
        if cwd is None:
            return self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        return subprocess.run(["bash", str(fechar_base.SCRIPT), "p1", "--ref", "melhoria/x", "--limpar"], cwd=cwd, env=self.env,
                              capture_output=True, text=True, timeout=60)

    def fica(self, d, r):
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(d.is_dir())
        self.assertTrue(self.resumo(r)[0].endswith(" clone=pendente"), r.stdout)
        self.assertIn(f"git -C {d} status --short --branch", r.stdout)
        self.assertNotIn("rm -rf", r.stdout)

    def test_clone_limpo_e_mesclado_e_apagado(self):
        d = self.clone()
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=ok"])
        self.assertFalse(d.exists())

    def test_arquivo_novo_fica(self):
        d = self.clone()
        (d / "novo").write_text("x\n")
        self.fica(d, self.limpar())

    def test_stash_fica(self):
        d = self.clone()
        (d / "b").write_text("mudado\n")
        self.git("stash", "-q", cwd=d)
        self.fica(d, self.limpar())

    def test_commit_nao_enviado_em_outra_branch_fica(self):
        d = self.clone()
        self.git("switch", "-q", "develop", cwd=d)
        self.git("commit", "-q", "--allow-empty", "-m", "local", cwd=d)
        self.git("switch", "-q", "melhoria/x", cwd=d)
        self.fica(d, self.limpar())

    def test_commit_enviado_e_nao_mesclado_fica(self):
        d = self.clone()
        self.mesclado()
        self.git("commit", "-q", "--allow-empty", "-m", "depois do merge", cwd=d)
        self.git("push", "-q", "origin", "melhoria/x", cwd=d)
        self.fica(d, self.fechar("p1", "--ref", "melhoria/x", "--limpar"))

    def test_clone_de_outra_branch_ou_de_outro_origin_nao_e_tocado(self):
        outra = self.clone("c1", "develop")
        alheio = self.clone("c2")
        self.git("remote", "set-url", "origin", str(self.tmp / "outro.git"), cwd=alheio)
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertTrue(outra.is_dir() and alheio.is_dir())

    def test_worktree_que_ficou_nao_e_apagada_como_clone(self):
        wt = self.tmp / ".forge-contrib" / "wt" / "w1"
        wt.parent.mkdir(parents=True)
        self.git("worktree", "add", "-q", str(wt), "melhoria/x")
        (self.estado / "wt_busy").write_text("persiste")
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(wt.is_dir())
        self.assertNotIn("clone=", self.resumo(r)[0])

    def test_o_clone_que_roda_o_fechamento_nao_se_apaga(self):
        d = self.clone()
        r = self.limpar(cwd=d)
        self.assertTrue(d.is_dir(), r.stdout)
        self.assertNotIn("clone=", self.resumo(r)[0])

    def test_rm_que_falha_fica_pendente_com_o_comando(self):
        d = self.clone()
        (self.tmp / "bin" / "rm").write_text(RM_FALSO)
        (self.tmp / "bin" / "rm").chmod(0o755)
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(self.resumo(r)[0].endswith(" clone=pendente"))
        self.assertIn(f"rm -rf -- {d}", r.stdout)


if __name__ == "__main__":
    unittest.main()
