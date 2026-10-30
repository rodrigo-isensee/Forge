"""N-FECHAR-a, A1: registro órfão com o prune negado e comandos pendentes escapados em `bin/forge-fechar`.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh` e `forge-check` falsos) sem herdar os testes dele.
"""
import sys
import unittest
import os
import shutil
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)
SCRIPT = base.SCRIPT
GIT_PRUNE = r'''#!/usr/bin/env bash
if [ "$1 $2" = "worktree prune" ] && [ -f "$ESTADO/prune_nega" ]; then
  echo "git $*" >> "$REGISTRO"
  echo "error: cannot prune: operation not permitted" >&2; exit 1
fi
if [ "$1 $2" = "worktree prune" ] && [ -f "$ESTADO/prune_muitos" ]; then
  # centenas de registros órfãos (WORKTREE-ORFAS); o git traduz a mensagem fora do LC_ALL=C
  msg=Removendo; [ "${LC_ALL:-}" != C ] || msg=Removing
  for i in $(seq "$(cat "$ESTADO/prune_muitos")"); do echo "$msg worktrees/orfa-$i: gitdir file points to non-existent location" >&2; done
fi
if [ "$1 $2 $3" = "push origin --delete" ] && [ -f "$ESTADO/delete_trava" ]; then
  echo "git $*" >> "$REGISTRO"
  exec sleep 30
fi
if [ "$1 $2 $3" = "push origin --delete" ] && [ -f "$ESTADO/delete_apaga_e_trava" ]; then
  # o servidor apaga a ref e a resposta não volta a tempo: o `timeout` corta; as tentativas seguintes falham porque a ref já não existe
  echo "git $*" >> "$REGISTRO"
  "$(dirname "$0")/git-base" "$@" >/dev/null 2>&1 || true
  [ ! -f "$ESTADO/ls_falha" ] || touch "$ESTADO/ls_deve_falhar"
  exec sleep 30
fi
if [ "$1" = ls-remote ] && [ -f "$ESTADO/ls_deve_falhar" ]; then
  echo "fatal: unable to access remote" >&2; exit 128
fi
exec "$(dirname "$0")/git-base" "$@"
'''


class Teste(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    com_worktree = base.Fechar.com_worktree
    resumo = base.Fechar.resumo
    marcas = base.Fechar.marcas
    log_de = base.Fechar.log_de
    arvores = base.Fechar.arvores

    def setUp(self):
        base.Fechar.setUp(self)
        # o `prune` pode ser negado ($ESTADO/prune_nega, como no sandbox); o resto vai para o git falso da suíte
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-base")
        (bin_ / "git").write_text(GIT_PRUNE, encoding="utf-8")
        (bin_ / "git").chmod(0o755)

    # ---- N-FECHAR-a, A1: registro órfão com o prune negado; comandos impressos escapados ----
    def test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove(self):
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("apaga")
        (self.estado / "prune_nega").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertIn("git worktree prune", pendentes)
        self.assertFalse(any(l.startswith("git worktree remove") for l in pendentes), pendentes)
        self.assertIn("registro órfão", r.stderr)
        self.assertIn("repositório todo", r.stderr)
        self.assertIn("registro: prune tirou 0 registro(s) de worktree órfã", r.stdout)
        self.assertIn("aviso: o prune saiu com código 1; a saída dele está no log", r.stderr)
        self.assertNotIn("cannot prune", r.stderr)
        self.assertFalse(wt.exists())
        self.assertEqual(len(self.marcas("git branch -D")), 0)  # a branch local espera o registro sumir
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_c3_prune_automatico_lista_no_log_o_que_removeu(self):
        self.com_worktree()
        outra = self.tmp / "wt-outra"
        self.git("worktree", "add", "-q", "-b", "melhoria/outra", str(outra))
        shutil.rmtree(outra)  # diretório ausente com registro: o prune do repositório tira este também
        (self.estado / "wt_busy").write_text("apaga")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.marcas("git worktree prune -v")), 1)
        self.assertIn("Removing worktrees/wt-outra", self.log_de(r).read_text())
        self.assertEqual(self.git("branch", "--list", "melhoria/outra"), "melhoria/outra")  # só o registro some

    # ---- WORKTREE-ORFAS: a lista do prune vai só ao log; a tela recebe a contagem e a linha `limpeza:` fecha o passo 7 ----
    def test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log(self):
        self.com_worktree()
        (self.estado / "wt_busy").write_text("apaga")
        (self.estado / "prune_muitos").write_text("300")
        r = self.fechar("p1", "--ref", "melhoria/x", LANG="pt_BR.UTF-8")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("orfa-", r.stdout + r.stderr)
        linhas = r.stdout.splitlines()
        i = linhas.index("limpeza: remota=ok worktree=ok branch=ok")
        self.assertEqual(linhas[i + 1:], ["Entrega p1 fechada em develop.", "fim: código 0"])
        self.assertIn("registro: prune tirou 301 registro(s) de worktree órfã", linhas[:i])
        log = self.log_de(r).read_text()
        self.assertEqual(log.count("[prune] Removing worktrees/orfa-"), 300)
        self.assertIn("[prune] Removing worktrees/wt-x", log)

    def argumentos_da_linha(self, linha):
        """Roda a linha impressa com `git` trocado por um eco dos argumentos, como faria quem a cola no shell."""
        r = subprocess.run(["bash", "-c", 'git() { printf "%s\\n" "$@"; }\n' + linha], capture_output=True, text=True,
                           cwd=self.tmp, env={"PATH": os.environ["PATH"]})
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.splitlines()

    def test_c3_comandos_pendentes_escapam_o_nome_da_branch_e_o_caminho_da_worktree(self):
        ref = "melhoria/y;echo$IFS/p"
        self.git("switch", "-q", "-c", ref)
        (self.proj / "c").write_text("3\n")
        self.git("add", "c")
        self.git("commit", "-q", "-m", "feat: c")
        self.git("push", "-q", "origin", ref)
        self.git("switch", "-q", "develop")
        wt = self.tmp / "wt com espaço;z"
        self.git("worktree", "add", "-q", str(wt), ref)
        (self.estado / "wt_busy").write_text("persiste")
        (self.estado / "falha_delete").write_text("3")
        r = self.fechar("p1", "--ref", ref)
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=pendente branch=pendente"])
        linhas = [l for l in r.stdout.split("pendente, rode:\n")[1].splitlines() if l.startswith("git ")]
        esperado = [["worktree", "remove", str(wt)], ["branch", "-D", ref], ["push", "origin", "--delete", f"refs/heads/{ref}"]]
        self.assertEqual([self.argumentos_da_linha(l) for l in linhas], esperado)
        self.assertTrue(wt.exists())  # o caminho com espaço foi lido inteiro (o awk antigo cortava no espaço)
        final = [l for l in r.stdout.splitlines() if "ou forge-fechar" in l][0]  # o aviso final também é colado: ref escapado
        self.assertEqual(self.argumentos_da_linha("forge-fechar() { printf '%s\\n' \"$@\"; }; " + final.split("ou ")[1].rstrip(".")),
                         ["p1", "--ref", ref, "--limpar"])

    # ---- LOTE-FECHAR-031, E2: rodado de dentro da worktree da própria branch ----
    def test_de_dentro_da_worktree_da_branch_sai_para_a_principal_remove_e_fecha_com_0(self):
        wt = self.com_worktree()
        r = base.subprocess.run(["bash", str(SCRIPT), "p1", "--ref", "melhoria/x"], cwd=wt, env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertIn(f"registro: saí da worktree de melhoria/x para a principal: {self.proj}", r.stdout)
        self.assertNotIn("saia dela", r.stderr)
        self.assertFalse(wt.exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        self.assertEqual(len(self.arvores()), 1)
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))

    def test_de_dentro_da_worktree_com_commit_nao_mesclado_continua_pendente_sem_apagar(self):
        # --limpar com o PR MERGED no head antigo: o passo 7 roda de dentro da worktree e só a guarda de sha impede o `worktree remove`
        sha_mesclado = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha_mesclado}\n")
        wt = self.com_worktree()
        (wt / "c").write_text("3\n")
        self.git("add", "c", cwd=wt)
        self.git("commit", "-q", "-m", "feat: c", cwd=wt)
        r = self.fechar_em(wt, "p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertIn("tem commit que não foi mesclado", r.stderr)
        self.assertEqual(self.marcas("git worktree remove"), [])
        self.assertTrue(wt.exists())
        self.assertIn("melhoria/x", self.git("branch", "--list", "melhoria/x"))

    def test_de_dentro_da_worktree_com_log_relativo_com_ponto_ponto_fecha_com_fim_e_codigo_0(self):
        # QA A1: FORGE_FECHAR_LOG_DIR relativo com `..` virava `$PWD/../x`; a worktree some no passo 7 e o registrador perdia o arquivo (SIGPIPE, sem `fim:`)
        wt = self.com_worktree()
        r = base.subprocess.run(["bash", str(SCRIPT), "p1", "--ref", "melhoria/x"], cwd=wt, capture_output=True, text=True, timeout=60,
                                env=dict(self.env, FORGE_FECHAR_LOG_DIR="../x/../logrel"))
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        log = self.log_de(r)
        self.assertEqual(log.parent, self.tmp.resolve() / "logrel")  # absoluto e normalizado
        self.assertTrue(log.read_text().splitlines()[-1].endswith(" fim: código 0"))
        self.assertFalse(wt.exists())

    def test_branch_na_worktree_principal_rodado_nela_nao_acha_outra_para_sair_e_fica_pendente(self):
        # QA A3: sem outra worktree para sair, a limpeza não remove nada e imprime o comando; código 3
        sha_mesclado = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha_mesclado}\n")
        self.git("switch", "-q", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("não achei outra para sair", r.stderr)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertEqual(self.marcas("git worktree remove"), [])
        self.assertEqual(self.marcas("git branch -D"), [])
        self.assertIn("melhoria/x", self.git("branch", "--list", "melhoria/x"))

    # ---- LOTE-S1, FECHAR-DA-RAIZ: teto de tempo do push --delete e a remota viva dita em voz alta ----
    def test_push_delete_que_trava_e_cortado_pelo_teto_e_a_remota_viva_e_dita(self):
        (self.estado / "delete_trava").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_TETO_DELETE="1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("git push origin --delete")]), 3)
        self.assertIn("apagando a branch remota melhoria/x (até 1s por tentativa", r.stdout)
        self.assertIn("a branch remota continua viva", r.stderr)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=ok"])
        self.assertIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_corte_depois_que_o_servidor_apagou_a_remota_confere_e_nao_diz_que_ela_continua_viva(self):
        (self.estado / "delete_apaga_e_trava").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_TETO_DELETE="1")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("continua viva", r.stderr + r.stdout)
        self.assertIn("já não existe no servidor", r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/melhoria/x").strip(), "")

    def test_corte_com_a_remota_ainda_no_servidor_segue_dizendo_que_ela_continua_viva(self):
        (self.estado / "delete_trava").write_text("")  # não apaga: a conferência acha a ref
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_TETO_DELETE="1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("a branch remota continua viva", r.stderr)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=ok"])

    def test_corte_com_a_conferencia_da_remota_falhando_fica_pendente_sem_afirmar_que_esta_viva(self):
        (self.estado / "delete_apaga_e_trava").write_text("")
        (self.estado / "ls_falha").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_FECHAR_TETO_DELETE="1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("não consegui conferir a branch remota melhoria/x", r.stderr)
        self.assertNotIn("continua viva", r.stderr)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=ok"])

    def test_teto_do_delete_fora_da_faixa_e_recusado_e_o_pior_caso_das_tres_tentativas_fica_em_300s(self):
        # pior caso: 3 tentativas no teto + 2 pausas no máximo (30 s) + a conferência da remota (10 s); o teto máximo é o maior que cabe em 300 s
        for v in ("0", "76", "100", "101", "x"):
            with self.subTest(v=v):
                r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_TETO_DELETE=v)
                self.assertEqual(r.returncode, 1, r.stderr)
                self.assertIn("FORGE_FECHAR_TETO_DELETE", r.stderr)
                self.assertIn("1 a 75", r.stderr)
        for v in ("1", "75"):
            with self.subTest(v=v):
                r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_TETO_DELETE=v)
                self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLessEqual(3 * 75 + 2 * 30 + 10, 300)
        self.assertIn('"${FORGE_FECHAR_TETO_DELETE:-75}"', SCRIPT.read_text())  # o padrão é o teto máximo

    def fechar_em(self, cwd, *args):
        return base.subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd, env=self.env, capture_output=True, text=True, timeout=60)

    # ---- LOTE-FECHAR-031, E3: --sem-limpar ----
    def test_sem_limpar_mescla_pula_o_passo_7_imprime_os_comandos_e_sai_com_3(self):
        wt = self.com_worktree()
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn(f"gh pr merge melhoria/x --squash --match-head-commit {sha}", self.chamadas())
        self.assertEqual(self.resumo(r), ["limpeza: pulada (--sem-limpar)"])
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertEqual(pendentes[:4], ["forge-fechar p1 --ref melhoria/x --limpar", f"git worktree remove {wt}",
                                        "git branch -D melhoria/x", "git push origin --delete refs/heads/melhoria/x"])
        self.assertEqual(len(self.marcas("git branch -D")), 0)
        self.assertEqual(len(self.marcas("git worktree remove")), 0)
        self.assertTrue(wt.exists())
        self.assertIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_sem_limpar_sem_branch_local_nao_imprime_branch_d_e_poe_o_limpar_primeiro(self):
        # a branch local some entre o passo 1 e o passo 7: o falso do GitHub a apaga ao mesclar
        falso = self.tmp / "gh"
        falso.rename(self.tmp / "gh-base")
        falso.write_text(f'#!/usr/bin/env bash\n[ "$1 $2" = "pr merge" ] && git -C "{self.proj}" branch -q -D melhoria/x\nexec "{self.tmp / "gh-base"}" "$@"\n')
        falso.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        pendentes = r.stdout.split("pendente, rode:\n")[1].splitlines()
        self.assertEqual(pendentes[:2], ["forge-fechar p1 --ref melhoria/x --limpar", "git push origin --delete refs/heads/melhoria/x"])
        self.assertFalse(any("branch -D" in l for l in pendentes), pendentes)

    def test_sem_limpar_com_limpar_e_erro_de_uso_antes_de_qualquer_passo(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--sem-limpar")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("não combinam", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_sem_limpar_com_dry_run_so_descreve(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--sem-limpar: o passo 7 é pulado", r.stdout)
        self.assertEqual(self.chamadas(), [])


if __name__ == "__main__":
    unittest.main()
