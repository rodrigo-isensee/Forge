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

API = '''# a chamada já foi registrada no começo do gh falso; a dos check-runs do head (FECHAR-CHECKS-ANTES-DO-MERGE) segue para o falso de base
if [ "$1" = api ] && [[ "$2" != "repos/{owner}/{repo}/commits/"* ]]; then
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
# E114.5 (A3 da segurança): o passo 6 confere também o exigido do ruleset nos check-runs do head; aqui ele vem verde
RUNS_COM_LINT = "bateria\t1\tcompleted\tsuccess\nbateria (python 3.14)\t2\tcompleted\tsuccess\ncatraca\t3\tcompleted\tsuccess\nlint\t4\tcompleted\tsuccess\n"


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
        (self.estado / "check_runs").write_text(RUNS_COM_LINT)
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("exigidos em pass: CI/bateria CI/bateria (python 3.14) Catraca/catraca */lint)", r.stdout)
        chamadas = [c for c in self.chamadas() if c.startswith("gh api")]
        self.assertIn("gh api repos/{owner}/{repo}/rules/branches/develop --jq .[] | select(.type == \"required_status_checks\") | "
                      ".parameters.required_status_checks[].context", chamadas)

    def test_ruleset_ilegivel_nao_acrescenta_e_a_protecao_vale(self):  # o corpo do 404 do ruleset não vira exigido
        (self.estado / "api_protecao").write_text("lint\n")
        self.leituras([*exig.OK, "lint\tpass\t1m\turl"])
        (self.estado / "check_runs").write_text(RUNS_COM_LINT)
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

    def test_clone_com_worktree_ligada_fica(self):  # sonda S1 da segurança: o rm levaria o repositório e o índice da ligada
        d = self.clone()
        w = self.tmp / ".forge-contrib" / "wt" / "zz-ligada"
        self.git("worktree", "add", "-q", "-b", "outra", str(w), "origin/develop", cwd=d)
        (w / "trabalho.txt").write_text("nao commitado\n")
        self.git("add", "trabalho.txt", cwd=w)
        self.fica(d, self.limpar())
        self.assertEqual(self.git("status", "--short", cwd=w).strip(), "A  trabalho.txt")

    def test_commit_so_em_tag_local_fica(self):
        d = self.clone()
        self.git("switch", "-q", "--detach", cwd=d)
        self.git("commit", "-q", "--allow-empty", "-m", "so na tag", cwd=d)
        self.git("tag", "t-local", cwd=d)
        self.git("switch", "-q", "melhoria/x", cwd=d)
        self.fica(d, self.limpar())

    def test_fsmonitor_do_clone_nao_roda(self):
        d = self.clone()
        marca = self.tmp / "marca-fsmonitor"
        self.git("config", "core.fsmonitor", f"touch {marca}; false #", cwd=d)
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse(marca.exists())
        self.assertFalse(d.exists())

    def test_clone_de_outra_branch_nao_e_tocado(self):  # o de outro origin fica pendente: test_fechar_limpar_clone (E166.1)
        outra = self.clone("c1", "develop")
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=nenhum"])
        self.assertTrue(outra.is_dir())

    def test_worktree_que_ficou_nao_e_apagada_como_clone(self):
        wt = self.tmp / ".forge-contrib" / "wt" / "w1"
        wt.parent.mkdir(parents=True)
        self.git("worktree", "add", "-q", str(wt), "melhoria/x")
        (self.estado / "wt_busy").write_text("persiste")
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(wt.is_dir())
        self.assertTrue(self.resumo(r)[0].endswith(" clone=nenhum"), r.stdout)  # LIMPAR-CLONE-NAO-LISTADO: o campo sempre sai

    # FORGE-FECHAR-CLONE-LIMPAR (v0478 E15.1): o --limpar rodado no clone que está na branch não o trata como worktree.
    def remota(self):
        return self.git("ls-remote", "origin", "refs/heads/melhoria/x")

    def no_clone(self, d):
        return subprocess.run(["bash", str(fechar_base.SCRIPT), "p1", "--ref", "melhoria/x", "--limpar"], cwd=d, env=self.env,
                              capture_output=True, text=True, timeout=60)

    def test_o_clone_que_roda_o_fechamento_nao_se_apaga_e_diz_o_que_ficou(self):
        d = self.clone()
        r = self.limpar(cwd=d)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(d.is_dir(), r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=pendente clone=pendente"])
        self.assertIn(f"aviso: a cópia {d.resolve()} é a principal deste repositório", r.stderr)
        self.assertIn("pendente, rode:\n# de outra cópia do Forge", r.stdout)
        self.assertIn("forge-fechar p1 --ref melhoria/x --limpar", r.stdout)
        for nao in ("worktree remove", "branch -D", "push origin --delete", "não apaguei a branch local"):
            self.assertNotIn(nao, r.stdout + r.stderr)
        self.assertNotEqual(self.remota(), "")  # o push daqui tiraria a origin/melhoria/x do clone

    def test_clone_por_caminho_com_link_ainda_e_de_wt(self):  # ~/.forge-contrib pode ser link (o do Forge aponta para /workspaces)
        real = self.tmp / "contrib-real"
        (real / "wt").mkdir(parents=True)
        (self.tmp / ".forge-contrib").symlink_to(real)
        d = self.clone()
        r = self.limpar(cwd=d)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("# de outra cópia do Forge", r.stdout)
        self.assertNotIn("switch develop", r.stdout)

    def test_o_limpar_de_outra_copia_apaga_o_clone_e_depois_a_remota(self):
        d = self.clone()
        self.assertEqual(self.limpar(cwd=d).returncode, 3)
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok clone=ok"])
        self.assertFalse(d.exists())
        self.assertEqual(self.remota(), "")

    def test_clone_com_commit_sem_merge_so_da_a_leitura(self):
        d = self.clone()
        self.mesclado()
        self.git("commit", "-q", "--allow-empty", "-m", "depois do merge", cwd=d)
        r = self.no_clone(d)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("git log --oneline origin/develop..refs/heads/melhoria/x", r.stdout)
        self.assertNotIn("forge-fechar p1", r.stdout)
        self.assertNotIn("switch develop", r.stdout)

    def test_copia_principal_fora_de_wt_troca_de_branch_e_repete(self):
        d = self.tmp / "fora"
        self.git("clone", "-q", str(self.remoto), str(d), cwd=self.tmp)
        self.git("switch", "-q", "melhoria/x", cwd=d)
        r = self.limpar(cwd=d)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        d = d.resolve()
        self.assertIn(f"git -C {d} switch develop\ngit -C {d} branch -D melhoria/x\nforge-fechar p1 --ref melhoria/x --limpar", r.stdout)
        self.assertNotIn("# de outra cópia do Forge", r.stdout)
        self.assertTrue(d.is_dir())

    def test_help_imprime_o_uso_e_sai_0_sem_log(self):
        for opcao in ("--help", "-h"):
            with self.subTest(opcao=opcao):
                r = self.fechar(opcao)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue(r.stdout.startswith("Forge: fecha uma entrega"), r.stdout[:200])
                self.assertIn("Uso: forge-fechar <pedido> --ref <branch>", r.stdout)
                self.assertFalse((self.tmp / "logs").exists())  # sai antes da pasta do log
                self.assertNotIn("set -euo", r.stdout)

    def test_rm_que_falha_fica_pendente_com_o_comando(self):
        d = self.clone()
        (self.tmp / "bin" / "rm").write_text(RM_FALSO)
        (self.tmp / "bin" / "rm").chmod(0o755)
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(self.resumo(r)[0].endswith(" clone=pendente"))
        self.assertIn(f"rm -rf -- {d}", r.stdout)


class LimparSemMerge(unittest.TestCase):
    """LIMPEZA-AO-FIM-DO-ITEM: o --limpar sem PR MERGED nem aberto passa as cópias de $ref ao `forge-copia limpar` (PR fechado sem merge);
    só a cópia limpa sai, e a branch local e a remota ficam. O `gh` do forge-copia é o falso do PATH (sem rede, R-CUSTO)."""
    F = fechar_base.Fechar
    setUp_f, tearDown, git, fechar = F.setUp, F.tearDown, F.git, F.fechar
    clone = LimparClones.clone

    def setUp(self):
        self.setUp_f()
        (self.tmp / "bin" / "gh").write_text('#!/bin/sh\ncat "$ESTADO/estados_copia"\n')
        (self.tmp / "bin" / "gh").chmod(0o755)
        (self.estado / "estados_copia").write_text("CLOSED false\n")
        (self.estado / "lista_extra").write_text(f"234 CLOSED develop {self.git('rev-parse', 'melhoria/x')} false\n")

    def limpar(self):
        return self.fechar("p1", "--ref", "melhoria/x", "--limpar")

    def test_pr_fechado_apaga_o_clone_limpo_e_a_branch_fica(self):
        d = self.clone()
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse(d.exists())
        self.assertIn("limpeza: sem merge, cópias apagadas=1", r.stdout)
        self.assertIn("refs/heads/melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")

    def test_pr_fechado_apaga_a_worktree_limpa(self):
        wt = self.tmp / ".forge-contrib" / "wt" / "w1"
        wt.parent.mkdir(parents=True)
        self.git("worktree", "add", "-q", str(wt), "melhoria/x")
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse(wt.exists())

    def test_copia_suja_fica_com_codigo_3(self):
        d = self.clone()
        (d / "novo").write_text("x\n")
        r = self.limpar()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertTrue(d.is_dir())
        self.assertIn(f"git -C {d} status --short --branch", r.stdout)

    def test_pr_aberto_para_sem_apagar(self):
        d = self.clone()
        (self.estado / "lista_extra").write_text(f"235 OPEN develop {self.git('rev-parse', 'melhoria/x')}\n")
        r = self.limpar()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("com PR aberto", r.stderr)
        self.assertTrue(d.is_dir())

    def test_sem_copia_para_como_antes(self):
        r = self.limpar()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("sem prova de merge", r.stderr)
        self.assertIn("refs/heads/melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_a_copia_principal_na_branch_nao_e_copia_do_item(self):
        self.git("switch", "-q", "melhoria/x")
        r = self.limpar()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("nenhuma cópia dela", r.stderr)
        self.assertTrue(self.proj.is_dir())

    def checa_vazio(self, linha, rc=0):
        """O forge-check falso do forge-fechar imprime `linha` (a do `vazio`) e sai `rc`; a do forge-copia segue pelo gh falso."""
        (self.tmp / "check").write_text(f'#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\necho "{linha}"\nexit {rc}\n')

    def recusa_sem_prova(self, d):
        r = self.limpar()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no --limpar: sem prova de merge: nenhum PR MERGED em develop para melhoria/x; nada foi apagado", r.stderr)
        self.assertNotIn("limpeza: sem merge", r.stdout)
        self.assertTrue(d.is_dir())

    def test_sem_pr_e_sem_vazio_sim_recusa_como_antes_e_a_copia_fica(self):
        (self.estado / "lista_extra").write_text("")
        self.recusa_sem_prova(self.clone())

    def test_pr_fechado_de_fork_nao_e_prova_e_a_copia_fica(self):
        (self.estado / "lista_extra").write_text(f"234 CLOSED develop {self.git('rev-parse', 'melhoria/x')} true\n")
        self.recusa_sem_prova(self.clone())

    def test_vazio_nao_recusa_como_antes_e_a_copia_fica(self):
        (self.estado / "lista_extra").write_text("")
        self.checa_vazio("vazio: não (1 arquivos)")
        self.recusa_sem_prova(self.clone())

    def test_forge_check_vazio_que_falha_nao_e_prova(self):
        (self.estado / "lista_extra").write_text("")
        self.checa_vazio("vazio: sim ref a base b árvore c", rc=2)
        self.recusa_sem_prova(self.clone())

    def test_sem_pr_com_vazio_sim_entra_na_limpeza_das_copias(self):
        (self.estado / "lista_extra").write_text("")
        self.checa_vazio("vazio: sim ref a base b árvore c")
        d = self.clone()
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("limpeza: sem merge, cópias apagadas=1", r.stdout)
        self.assertFalse(d.exists())

    def test_clone_de_outra_branch_nao_e_tocado(self):
        outra, d = self.clone("c1", "develop"), self.clone("c2")
        r = self.limpar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertFalse(d.exists())
        self.assertTrue(outra.is_dir())


if __name__ == "__main__":
    unittest.main()
