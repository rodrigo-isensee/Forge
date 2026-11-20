"""TA-5: `bin/forge-fechar` (passos mecânicos de fechamento do integrador) em repositório temporário.

`gh` e `forge-check` são falsos (FORGE_GH e FORGE_CHECK); cada chamada vai para um registro, para provar o que rodou.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "bin" / "forge-fechar"

GH_FALSO = r'''#!/usr/bin/env bash
# GH-VERSAO-MINIMA: a conferência do passo 1 lê a versão; não entra no registro (os testes leem a 1ª chamada). VERSAO_GH muda a versão.
[ "$1" = "--version" ] && { echo "gh version ${VERSAO_GH:-2.104.0} (2026-11-12)"; exit 0; }
echo "gh $*" >> "$REGISTRO"
# falha_n <arquivo>: se o arquivo guarda um número > 0, desconta um e falha (erro passageiro, como o 502 do GitHub)
falha_n() {
  local f="$ESTADO/$1" n
  [ -f "$f" ] || return 1
  n="$(cat "$f")"
  [ "$n" -gt 0 ] || return 1
  echo $((n - 1)) > "$f"
}
case "$1 $2" in
  "pr list")
    case "$*" in *"--head "*) todos="$*"; h="${todos#*--head }"; echo "${h%% *}" > "$ESTADO/branch_vista" ;; esac  # a branch da entrega, para o head padrão do pr view
    falha_n falha_lista && { echo "HTTP 502" >&2; exit 1; }
    # o head do PR aberto, como o GitHub o devolve: o arquivo "aberto_head" (só da lista), o "head" ou o da branch no remoto
    h_aberto="$(cat "$ESTADO/aberto_head" 2>/dev/null || cat "$ESTADO/head" 2>/dev/null || { r="refs/heads/$(cat "$ESTADO/branch_vista")"; git ls-remote origin "$r" | awk -v r="$r" '$2 == r {print $1}'; })"
    [ -f "$ESTADO/aberto" ] && awk -v fork="$([ -f "$ESTADO/aberto_fork" ] && echo true || echo false)" -v h="$h_aberto" '{print $1 " OPEN " $2 " " h " " fork}' "$ESTADO/aberto"
    cat "$ESTADO/lista_extra" 2>/dev/null; exit 0 ;;
  "pr view")
    # head_do_pr [arquivo]: o head que o GitHub devolve (arquivo "head" ou o da branch no remoto, que é o conferido pelo script)
    head_do_pr() { cat "$ESTADO/${1:-head}" 2>/dev/null || cat "$ESTADO/head" 2>/dev/null || { r="refs/heads/$(cat "$ESTADO/branch_vista" 2>/dev/null || echo melhoria/x)"; git ls-remote origin "$r" | awk -v r="$r" '$2 == r {print $1}'; }; }
    case "$*" in
      *"--json number --jq"*) cat "$ESTADO/numero_por_nome" 2>/dev/null || { [ -f "$ESTADO/aberto" ] && cut -d' ' -f1 "$ESTADO/aberto" || echo 7; }; exit 0 ;;
      *number,state*) [ -f "$ESTADO/aberto" ] && cat "$ESTADO/aberto"; exit 0 ;;
      *state,headRefOid,baseRefName,mergeCommit*)
        falha_n falha_estado && exit 1
        if [ -f "$ESTADO/armado" ] && [ -f "$ESTADO/mescla_apos" ]; then
          n="$(cat "$ESTADO/mescla_apos")"; echo $((n - 1)) > "$ESTADO/mescla_apos"; [ "$n" -gt 1 ] || echo MERGED > "$ESTADO/estado"
        fi
        pre_base="$(cut -d' ' -f1 "$ESTADO/pre" 2>/dev/null || echo develop)"
        merge_oid="$(cat "$ESTADO/merge_commit" 2>/dev/null || echo 0123456789abcdef0123456789abcdef01234567)"
        [ -f "$ESTADO/merge_commit_vazio" ] && merge_oid=-
        echo "$(cat "$ESTADO/estado" 2>/dev/null || echo OPEN) $(head_do_pr head_final) $(cat "$ESTADO/base_final" 2>/dev/null || echo "$pre_base") $merge_oid"; exit 0 ;;
      *baseRefName,isDraft*isCrossRepository*)
        echo "$(cat "$ESTADO/pre" 2>/dev/null || echo "develop false") $(cat "$ESTADO/estado" 2>/dev/null || echo OPEN) $(head_do_pr) $(cat "$ESTADO/cross" 2>/dev/null || echo false)"; exit 0 ;;
      *baseRefName,isDraft*) echo "$(cat "$ESTADO/pre" 2>/dev/null || echo "develop false") $(cat "$ESTADO/estado" 2>/dev/null || echo OPEN)"; exit 0 ;;
      *mergeCommit*) cat "$ESTADO/merge_commit" 2>/dev/null; exit 0 ;;
      *headRefOid*) cat "$ESTADO/head" 2>/dev/null; exit 0 ;;
      *labels*|*title,body*) [ -f "$ESTADO/falha_leitura" ] && exit 1 ;;&
      *labels*)
        # rotulo_na_leitura N: o rótulo do dono só aparece a partir da N-ésima leitura (e a catraca passa a verde junto)
        if [ -f "$ESTADO/rotulo_na_leitura" ]; then
          n="$(( $(cat "$ESTADO/leituras_rotulo" 2>/dev/null || echo 0) + 1 ))"; echo "$n" > "$ESTADO/leituras_rotulo"
          if [ "$n" -ge "$(cat "$ESTADO/rotulo_na_leitura")" ]; then
            echo afrouxa-regra; [ -f "$ESTADO/checks_apos_rotulo" ] && cp "$ESTADO/checks_apos_rotulo" "$ESTADO/checks"; exit 0
          fi
          exit 0
        fi
        cat "$ESTADO/rotulos" 2>/dev/null; exit 0 ;;
      *title,body*) cat "$ESTADO/texto" 2>/dev/null; exit 0 ;;
      *state*) falha_n falha_estado && exit 1; cat "$ESTADO/estado" 2>/dev/null || echo OPEN; exit 0 ;;
    esac ;;
  "pr create")
    # como o CI real (passo "Nada pula degrau", review A2): o par head/base passa pelo modo `degrau` da catraca, com a tabela PROMOCOES
    # e o head do servidor; recusado, o PR não nasce (no GitHub, nasceria vermelho e nunca mesclaria)
    todos="$*"; b="${todos#*--base }"; b="${b%% *}"; h="${todos#*--head }"; h="${h%% *}"
    s="$(git ls-remote origin "refs/heads/$h" | awk -v r="refs/heads/$h" '$2 == r {print $1}')"
    if ! env -u GITHUB_STEP_SUMMARY HEAD_REPO=o/r BASE_REPO=o/r python3 -I "$CATRACA_REAL" --modo degrau --ramo "$h" --base-ref "$b" --head "${s:-sem-head}" >/dev/null 2>&1; then
      echo "degrau recusado: $h -> $b" >> "$REGISTRO"; echo "pull request create failed: $h -> $b fora da tabela de promoções" >&2; exit 1
    fi
    n="$(cat "$ESTADO/numero_criado" 2>/dev/null || echo 7)"
    echo "$n develop" > "$ESTADO/aberto"
    if [ -f "$ESTADO/saida_create" ]; then cat "$ESTADO/saida_create"; else echo "https://github.com/o/r/pull/$n"; fi
    exit 0 ;;
  "pr ready") exit 0 ;;
  "pr checks")
    # como o script pede (C-6): só a leitura por JSON; cada linha do arquivo (nome, estado, tempo, link e o workflow opcional) sai como o `--jq` dele
    # a monta: nome, estado, workflow e link; sem a 5.ª coluna, o workflow é o do repositório (catraca na Catraca, o resto no CI)
    [ "${*:4}" = "--json name,bucket,link,workflow --jq .[] | [.name, .bucket, .workflow, .link] | @tsv" ] || exit 64
    checks_json() { awk -F'\t' -v OFS='\t' 'NF >= 4 {$3 = (NF >= 5) ? $5 : ($1 == "catraca" ? "Catraca" : "CI"); NF = 4} 1'; }
    if [ -f "$ESTADO/sem_checks_ate" ] && [ "$(wc -l < "$REGISTRO")" -lt "$(cat "$ESTADO/sem_checks_ate")" ]; then
      echo "no checks reported on the 'melhoria/x' branch"; exit 1
    fi
    falha_n falha_checks && { echo "HTTP 502"; exit 1; }
    checks_json < "$ESTADO/checks"; exit 0 ;;
  "pr merge")
    [ -f "$ESTADO/merge_502" ] && exit 1
    [ -f "$ESTADO/merge_502_mas_mescla" ] && { echo MERGED > "$ESTADO/estado"; exit 1; }
    # como o GitHub: recusa se o head do PR (arquivo "head", quando existe) não é o do --match-head-commit
    if [ -f "$ESTADO/head" ]; then
      [[ "$*" == *"--match-head-commit $(cat "$ESTADO/head")"* ]] || exit 1
    fi
    [[ "$*" == *--match-head-commit* ]] || exit 1
    # R7: com "auto_arma", o --auto só arma (checks obrigatórios pendentes); "mescla_apos" N: o GitHub mescla na N-ésima leitura do estado
    if [ -f "$ESTADO/auto_arma" ] && [[ "$*" == *" --auto "* ]]; then : > "$ESTADO/armado"; exit 0; fi
    echo MERGED > "$ESTADO/estado"; exit 0 ;;
  "run list")
    # FECHAR-ESPERA-CI-DEVELOP: só a forma que o script pede (evento push, commit e o --jq dele); a saída é a do --jq: id, status e conclusão.
    [[ "$*" =~ ^run\ list\ --branch\ [a-z]+\ --event\ push\ --commit\ ([0-9a-f]{7,64})\ --json\ databaseId,status,conclusion\ --jq\ (.*)$ ]] || exit 64
    [ "${BASH_REMATCH[2]}" = '.[] | [.databaseId, .status, .conclusion] | @tsv' ] || exit 64
    falha_n falha_runs && { echo "HTTP 502" >&2; exit 1; }
    # runs_pendentes N: as N primeiras leituras saem em andamento; depois runs_<sha>, senão runs, senão uma execução verde
    falha_n runs_pendentes && { printf '1\tin_progress\t\n'; exit 0; }
    cat "$ESTADO/runs_${BASH_REMATCH[1]}" 2>/dev/null || cat "$ESTADO/runs" 2>/dev/null || printf '1\tcompleted\tsuccess\n'
    exit 0 ;;
esac
exit 64
'''
# git falso: o `push --delete` falha as primeiras N vezes (N em $ESTADO/falha_delete) e depois chama o git real; registra as
# chamadas de limpeza (worktree remove/prune, branch -D, push --delete) para provar a ordem; `worktree remove` pode simular o
# "Device or resource busy" ($ESTADO/wt_busy: "apaga" = o diretório some e o registro administrativo fica; "persiste" = nada some)
GIT_FALSO = r'''#!/usr/bin/env bash
if [ "$1 $2" = "push origin" ] && [ "$3" = "--delete" ]; then
  echo "git $*" >> "$REGISTRO"
  n="$(cat "$ESTADO/falha_delete" 2>/dev/null || echo 0)"
  if [ "$n" -gt 0 ]; then echo $((n - 1)) > "$ESTADO/falha_delete"; echo "HTTP 502" >&2; exit 1; fi
  # $ESTADO/delete_apaga_e_falha: o servidor apaga a ref, mas a resposta se perde (o comando sai com erro)
  if [ -f "$ESTADO/delete_apaga_e_falha" ]; then "$REAL_GIT_FALSO" "$@" >/dev/null 2>&1; exit 1; fi
fi
# $ESTADO/lsremote_develop_ok N: as N primeiras leituras da develop no servidor passam; depois falham ("vazio" em lsremote_develop_modo: sem a ref)
if [ "$1 $2 $3" = "ls-remote origin refs/heads/develop" ] && [ -f "$ESTADO/lsremote_develop_ok" ]; then
  n="$(cat "$ESTADO/lsremote_develop_ok")"
  if [ "$n" -gt 0 ]; then echo $((n - 1)) > "$ESTADO/lsremote_develop_ok"
  elif [ "$(cat "$ESTADO/lsremote_develop_modo" 2>/dev/null)" = vazio ]; then exit 0
  else echo "HTTP 502" >&2; exit 1; fi
fi
# $ESTADO/develop_no_servidor: o topo da develop que o servidor devolve (o item falso do lote o move ao "mesclar")
if [ "$1 $2 $3" = "ls-remote origin refs/heads/develop" ] && [ -f "$ESTADO/develop_no_servidor" ]; then
  printf '%s\trefs/heads/develop\n' "$(cat "$ESTADO/develop_no_servidor")"; exit 0
fi
case "$1 $2" in
  "worktree remove")
    echo "git $*" >> "$REGISTRO"
    modo="$(cat "$ESTADO/wt_busy" 2>/dev/null || true)"
    [ "$modo" = apaga ] && rm -rf "${@: -1}"
    if [ -n "$modo" ]; then echo "error: failed to delete '${@: -1}': Device or resource busy" >&2; exit 1; fi ;;
  "worktree prune"|"branch -D") echo "git $*" >> "$REGISTRO" ;;
esac
exec "$REAL_GIT_FALSO" "$@"
'''
CHECK_FALSO = '#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\nexit "${CHECK_RC:-0}"\n'
# FF-1: promover-homolog falso (rodado com `python3 -I`); anota os argumentos em $ESTADO/<marca> e sai com o rc dado (o padrão lê PROMOVER_RC)
PROMOVER_FALSO = """import os, sys
with open(os.path.join(os.environ["ESTADO"], "{marca}"), "a") as f: f.write(" ".join(sys.argv[1:]) + "\\n")
print(os.environ.get("PROMOVER_SAIDA", "linha do promover"))
sys.exit({rc})
"""


def promover_falso(caminho, marca, rc='int(os.environ.get("PROMOVER_RC", "0"))'):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(PROMOVER_FALSO.format(marca=marca, rc=rc), encoding="utf-8")
    return str(caminho)


class Fechar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fechar-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)  # cada pasta criada aqui (também a do subteste) é apagada no fim do teste
        self.estado = self.tmp / "estado"
        self.estado.mkdir()
        self.registro = self.tmp / "registro"
        self.registro.write_text("")
        for nome, texto in (("gh", GH_FALSO), ("check", CHECK_FALSO)):
            (self.tmp / nome).write_text(texto, encoding="utf-8")
            (self.tmp / nome).chmod(0o755)
        (self.tmp / "gitconfig").write_text("[user]\n\tname = T\n\temail = t@exemplo.test\n", encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"}
        self.env.update(HOME=str(self.tmp), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.tmp / "gitconfig"),
                        FORGE_GH=str(self.tmp / "gh"), FORGE_CHECK=str(self.tmp / "check"),
                        REGISTRO=str(self.registro), ESTADO=str(self.estado), FORGE_FECHAR_INTERVALO="0",
                        FORGE_FECHAR_TESTE="1", FORGE_FECHAR_LOG_DIR=str(self.tmp / "logs"), CATRACA_REAL=str(RAIZ / "tests" / "catraca.py"),
                        FORGE_PROMOVER=promover_falso(self.tmp / "promover.py", "promover"))
        (self.tmp / "bin").mkdir()
        (self.tmp / "bin" / "git").write_text(GIT_FALSO, encoding="utf-8")
        (self.tmp / "bin" / "git").chmod(0o755)
        self.env.update(REAL_GIT_FALSO=shutil.which("git"), FORGE_FECHAR_PAUSA="0", PATH=f"{self.tmp / 'bin'}:{os.environ['PATH']}")
        self.env = sem_manutencao(self.env)
        self.remoto, self.proj = self.tmp / "remoto.git", self.tmp / "proj"
        self.git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        remoto_sem_manutencao(self.remoto)
        self.git("clone", "-q", str(self.remoto), str(self.proj), cwd=self.tmp)
        (self.proj / "a").write_text("1\n")
        (self.proj / ".claude-plugin").mkdir()
        (self.proj / ".claude-plugin" / "plugin.json").write_text('{\n  "name": "forge"\n}\n')
        self.git("add", "a", ".claude-plugin/plugin.json")
        self.git("commit", "-q", "-m", "chore: inicio")
        self.git("branch", "-M", "develop")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "-c", "melhoria/x")
        (self.proj / "b").write_text("2\n")
        self.git("add", "b")
        self.git("commit", "-q", "-m", "feat: b")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        (self.estado / "checks").write_text("bateria\tpass\t1m\turl\nbateria (python 3.14)\tpass\t1m\turl\ncatraca\tpass\t5s\turl\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args, cwd=None):
        r = subprocess.run(["git", *args], cwd=cwd or self.proj, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def fechar(self, *args, **extra):
        env = dict(self.env, **extra)
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=self.proj, env=env, capture_output=True, text=True,
                              timeout=60)

    def chamadas(self):
        return self.registro.read_text().splitlines()

    def estado_do_repo(self):
        return (self.git("branch", "-a"), self.git("rev-parse", "develop"), self.git("ls-remote", "origin"))

    def test_fluxo_completo_mescla_com_squash_e_limpa(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        chamadas = self.chamadas()
        self.assertEqual(chamadas[0], "forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop")  # B5: o parecer é conferido no sha
        self.assertTrue(any(c.startswith("gh pr create --base develop --head melhoria/x") for c in chamadas))
        self.assertIn(f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}", chamadas)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        corpo = self.registro.read_text()
        self.assertIn("## Projeto de origem\nForge", corpo)
        self.assertIn("## Como medir\nVer", corpo)

    def test_1c_promovivel_segue_com_o_sha_conferido(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("[1c]", r.stdout)
        self.assertEqual((self.estado / "promover").read_text(), f"--conferir-ref {sha}\n")

    def assert_parou_no_1c(self, r):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 1c", r.stderr)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh pr create", "gh pr ready", "gh pr merge"))])

    def test_1c_rc_diferente_de_0_ou_prazo_para_sem_pr_nem_merge(self):
        for rc in ("1", "2", "124"):
            with self.subTest(rc=rc):
                r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC=rc, PROMOVER_SAIDA="docs/qa/x.md: parecer reprovado")
                self.assert_parou_no_1c(r)
                self.assertIn(f"(rc {rc};", r.stderr)
                self.assertIn("docs/qa/x.md: parecer reprovado", r.stderr)

    def test_1c_release_nao_promovida_para_e_manda_promover(self):
        r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC="1",
                        PROMOVER_SAIDA="forge-check pr release-9.9.9 contra a main: parecer desatualizado ou faltando")
        self.assert_parou_no_1c(r)
        self.assertIn("release-9.9.9 contra a main", r.stderr)
        self.assertIn("com release na develop ainda não promovida, promova-a (scripts/promover-homolog.py) antes de mesclar "
                      "outra branch (R-FLUXO)", r.stderr)

    def test_1c_script_ausente_para(self):
        r = self.fechar("p1", "--ref", "melhoria/x", FORGE_PROMOVER=str(self.tmp / "nao-existe.py"))
        self.assert_parou_no_1c(r)
        self.assertIn("não achei", r.stderr)

    def fabrica_copiada(self):
        """bin/forge-fechar copiado para outra pasta, com o promover dela (rc 1); o scripts/ do cwd (a branch) traz um que passa."""
        fab = self.tmp / "fab"
        (fab / "bin").mkdir(parents=True)
        shutil.copy(SCRIPT, fab / "bin" / "forge-fechar")
        promover_falso(fab / "scripts" / "promover-homolog.py", "da_fabrica", rc=1)
        promover_falso(self.proj / "scripts" / "promover-homolog.py", "do_cwd", rc=0)
        return fab / "bin" / "forge-fechar"

    def test_1c_usa_o_script_do_diretorio_do_fechar_e_nao_o_do_cwd(self):
        env = {k: v for k, v in self.env.items() if k != "FORGE_PROMOVER"}
        r = subprocess.run(["bash", str(self.fabrica_copiada()), "p1", "--ref", "melhoria/x"], cwd=self.proj, env=env,
                           capture_output=True, text=True, timeout=60)
        self.assert_parou_no_1c(r)
        self.assertTrue((self.estado / "da_fabrica").exists())
        self.assertFalse((self.estado / "do_cwd").exists())

    def test_1c_forge_promover_sem_o_modo_de_teste_e_ignorado_com_aviso(self):
        caminho = self.tmp / "caminho"
        caminho.mkdir()
        (caminho / "forge-check").symlink_to(self.tmp / "check")
        (caminho / "gh").symlink_to(self.tmp / "gh")
        env = {k: v for k, v in self.env.items() if k not in ("FORGE_FECHAR_TESTE", "FORGE_CHECK", "FORGE_GH",
                                                              "FORGE_FECHAR_INTERVALO", "FORGE_FECHAR_PAUSA")}
        env.update(PATH=f"{caminho}:{env['PATH']}", FORGE_PROMOVER=promover_falso(self.tmp / "falso.py", "falso", rc=0))
        r = subprocess.run(["bash", str(self.fabrica_copiada()), "p1", "--ref", "melhoria/x"], cwd=self.proj, env=env,
                           capture_output=True, text=True, timeout=60)
        self.assertIn("FORGE_PROMOVER só valem com FORGE_FECHAR_TESTE=1", r.stderr)
        self.assert_parou_no_1c(r)
        self.assertTrue((self.estado / "da_fabrica").exists())
        self.assertFalse((self.estado / "falso").exists())

    def test_1c_fora_da_base_develop_nao_roda(self):
        self.assertNotEqual(self.fechar("p1", "--ref", "melhoria/x", "--base", "origin/homolog").returncode, 0)
        self.assertFalse((self.estado / "promover").exists())

    # ---- FECHAR-DRY-RUN-1C (v0478): o --dry-run roda o --conferir-ref de verdade, sem buscar a homolog ----
    def test_1c_no_dry_run_roda_o_conferir_ref_contra_a_homolog_local_sem_busca(self):
        sha = self.git("rev-parse", "melhoria/x")
        self.git("push", "-q", "origin", "melhoria/x:refs/heads/homolog")
        local = self.git("rev-parse", "develop")
        self.git("update-ref", "refs/remotes/origin/homolog", local)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"[1c] python3 -I {self.tmp / 'promover.py'} --conferir-ref {sha}", r.stdout)
        self.assertEqual((self.estado / "promover").read_text(), f"--conferir-ref {sha}\n")
        self.assertIn(f"1c: promovível (contra a origin/homolog local {local[:12]}, sem busca).", r.stdout)
        self.assertEqual(self.homolog_local(), local)  # o --dry-run não fala com o servidor
        self.assertIn("[7]", r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh ", "forge-check "))])

    def test_1c_no_dry_run_que_recusa_para_com_1_e_diz_a_homolog_lida(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", PROMOVER_RC="1", PROMOVER_SAIDA="versão 0.47.6 já na homolog")
        self.assert_parou_no_1c(r)
        self.assertIn("versão 0.47.6 já na homolog", r.stderr)
        self.assertIn("--dry-run: conferido contra a origin/homolog local (ausente), sem busca; se ela estiver velha, rode git fetch "
                      "origin homolog e repita", r.stderr)
        self.assertNotIn("[2] ", r.stdout)
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 1"))

    def test_1c_no_dry_run_sem_a_branch_local_nao_roda(self):
        self.git("branch", "-q", "-D", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("1c: não rodou: sem a branch local melhoria/x.", r.stdout)
        self.assertFalse((self.estado / "promover").exists())

    # ---- FECHAR-SEM-HOMOLOG-LOCAL ----
    def homolog_no_servidor(self, rev):
        """A homolog no servidor em <rev>, e a origin/homolog deste clone apagada (o clone que nunca a buscou)."""
        self.git("push", "-q", "origin", f"{rev}:refs/heads/homolog")
        self.git("update-ref", "-d", "refs/remotes/origin/homolog")
        return self.git("rev-parse", rev)

    def homolog_local(self):
        return subprocess.run(["git", "rev-parse", "-q", "--verify", "refs/remotes/origin/homolog"], cwd=self.proj, env=self.env,
                              capture_output=True, text=True).stdout.strip()

    def test_1c_sem_origin_homolog_no_clone_busca_so_ela_antes_do_promover(self):
        sha_h = self.homolog_no_servidor("develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.homolog_local(), sha_h)
        self.assertNotIn("aviso: sem origin/homolog", r.stderr)

    def test_1c_com_origin_homolog_velha_no_clone_busca_a_do_servidor_antes_do_promover(self):
        # FECHAR-HOMOLOG-FRESCA (v0478): a local velha recusava por versão antiga (0.47.6 contra a 0.47.7 do servidor); o promover lê a nova
        velho = self.homolog_no_servidor("develop")
        self.git("push", "-q", "origin", "melhoria/x:refs/heads/homolog")
        novo = self.git("rev-parse", "melhoria/x")
        self.git("update-ref", "refs/remotes/origin/homolog", velho)
        visto = self.tmp / "homolog_vista"
        (self.tmp / "promover.py").write_text(
            "import subprocess, sys\n"
            "h = subprocess.run(['git', 'rev-parse', 'refs/remotes/origin/homolog'], capture_output=True, text=True).stdout.strip()\n"
            f"open({str(visto)!r}, 'w').write(h)\nsys.exit(0)\n", encoding="utf-8")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(visto.read_text(), novo)
        self.assertEqual(self.homolog_local(), novo)
        self.assertNotIn("aviso:", r.stderr)

    def test_1c_busca_que_falha_com_a_homolog_local_avisa_que_ela_pode_estar_velha(self):
        local = self.git("rev-parse", "develop")
        self.git("update-ref", "refs/remotes/origin/homolog", local)  # o servidor do setUp não tem homolog: a busca falha
        r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC="1")
        self.assert_parou_no_1c(r)
        self.assertIn(f"aviso: a busca da origin/homolog falhou (git fetch origin homolog); o promover-homolog decide com a local "
                      f"({local[:12]}), que pode estar velha.", r.stderr)
        self.assertNotIn("aviso: sem origin/homolog neste clone e a busca falhou (git fetch", r.stderr)
        self.assertEqual(self.homolog_local(), local)

    def test_1c_busca_da_homolog_que_falha_avisa_e_o_promover_decide(self):
        for rc in ("1", "0"):  # o 1 primeiro: o 0 mescla e limpa a branch
            with self.subTest(rc=rc):
                self.registro.write_text("")
                r = self.fechar("p1", "--ref", "melhoria/x", PROMOVER_RC=rc)  # o servidor do setUp não tem homolog
                self.assertIn("aviso: sem origin/homolog neste clone e a busca falhou (git fetch origin homolog); o promover-homolog decide.", r.stderr)  # a do 1c, não a do passo 1
                self.assertEqual(self.homolog_local(), "")
                if rc == "1":
                    self.assert_parou_no_1c(r)
                else:
                    self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def remota_apagada_depois_do_merge(self, lista_extra):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(lista_extra.format(sha=sha))
        self.git("push", "-q", "origin", "--delete", "melhoria/x")  # o GitHub apaga a branch depois do merge
        return sha

    def test_2_remota_apagada_com_pr_merged_no_head_nao_pede_push_e_limpa(self):
        self.remota_apagada_depois_do_merge("234 MERGED develop {sha} false\n")
        (self.estado / "estado").write_text("MERGED")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("não peço push", r.stdout)
        self.assertNotIn("git push origin melhoria/x", r.stderr)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_2_remota_apagada_com_o_head_ja_na_base_nao_pede_push(self):
        self.git("merge", "-q", "--no-ff", "melhoria/x", "-m", "merge x")
        self.git("push", "-q", "origin", "develop")
        self.remota_apagada_depois_do_merge("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("não peço push", r.stdout)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_2_remota_apagada_sem_merge_do_head_no_alvo_continua_pedindo_push(self):
        casos = {"sem PR": "", "PR aberto": "234 OPEN develop {sha} false\n", "PR de fork": "234 MERGED develop {sha} true\n",
                 "outra base": "234 MERGED homolog {sha} false\n", "outro head": "234 MERGED develop " + "0" * 40 + " false\n"}
        for nome, lista in casos.items():
            with self.subTest(caso=nome):
                self.registro.write_text("")
                self.git("push", "-q", "origin", "melhoria/x")
                self.remota_apagada_depois_do_merge(lista)
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("parou no passo 2: melhoria/x não está no origin (git push origin melhoria/x", r.stderr)
                self.assertEqual(self.merges(), [])

    def test_2_remota_com_outro_head_e_o_conferido_mesclado_continua_parando(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha} false\n")
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "c").write_text("3\n")
        self.git("add", "c")
        self.git("commit", "-q", "-m", "feat: c")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("reset", "-q", "--hard", sha)  # o clone ficou no head mesclado; o servidor tem um commit além dele
        self.git("switch", "-q", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 2: o head local", r.stderr)
        self.assertNotEqual(self.git("ls-remote", "origin", "refs/heads/melhoria/x"), "")

    def test_dry_run_nao_altera_nada_nem_chama_gh_ou_check(self):
        antes = self.estado_do_repo()
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        for n in "1234567":
            self.assertIn(f"[{n}]", r.stdout)
        self.assertEqual(self.chamadas(), [])
        self.assertEqual(self.estado_do_repo(), antes)

    def test_para_no_primeiro_erro_forge_check(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_RC="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 1", r.stderr)
        self.assertEqual(self.chamadas(), ["forge-check pr p1 --ref refs/heads/melhoria/x --base origin/develop"])

    def test_para_se_head_remoto_difere_do_local(self):
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "c").write_text("3\n")
        self.git("add", "c")
        self.git("commit", "-q", "-m", "feat: c")
        self.git("switch", "-q", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 2", r.stderr)
        self.assertFalse(any(c.startswith("gh ") for c in self.chamadas()))

    def test_recusa_base_main_e_base_fora_do_fluxo(self):
        for base in ("origin/main", "main", "origin/outra"):
            r = self.fechar("p1", "--ref", "melhoria/x", "--base", base)
            self.assertNotEqual(r.returncode, 0, base)
        self.assertIn("main", self.fechar("p1", "--ref", "melhoria/x", "--base", "origin/main", "--dry-run").stderr)
        self.assertEqual(self.chamadas(), [])

    def test_recusa_check_vermelho_e_nao_mescla(self):
        (self.estado / "checks").write_text("bateria\tfail\t1m\turl\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 4", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_check_pendente_ate_o_limite_nao_mescla(self):
        (self.estado / "checks").write_text("bateria\tpending\t0\turl\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pendentes", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    ITEM_MARCADO = "feat: x\n## Checklist\n- [x] Rótulo `afrouxa-regra` pedido ao dono (afrouxa regra, motivo no corpo)\n"

    def test_recusa_quando_item_do_rotulo_marcado_e_rotulo_nao_aplicado(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        chamadas = self.chamadas()
        self.assertFalse(any("pr merge" in c or "pr edit" in c or "--add-label" in c for c in chamadas))

    def test_mensagem_do_passo_5_diz_que_o_gatilho_foi_o_titulo(self):
        (self.estado / "texto").write_text("feat: x (afrouxa-regra)\nCorpo.\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertIn("pedido pelo título", r.stderr)
        self.assertNotIn("item marcado do corpo", r.stderr)
        self.assertIn("--esperar-rotulo", r.stderr)

    def test_mensagem_do_passo_5_diz_que_o_gatilho_foi_o_item_do_corpo(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertIn("pedido por um item marcado do corpo", r.stderr)
        self.assertNotIn("pedido pelo título", r.stderr)

    def test_prazo_esgotado_com_esperar_rotulo_para_sem_mandar_repetir_a_opcao(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("pedido por um item marcado do corpo", r.stderr)
        self.assertNotIn("rode de novo com --esperar-rotulo", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_corpo_que_so_cita_o_nome_do_rotulo_nao_para(self):
        (self.estado / "texto").write_text(
            "feat: x\nO #222 só o dono aplica o rótulo afrouxa-regra.\n"
            "- [ ] Rótulo afrouxa-regra pedido ao dono\n- [x] Testes verdes\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)

    def test_titulo_que_cita_o_rotulo_sem_o_rotulo_aplicado_para(self):
        (self.estado / "texto").write_text("feat: x (afrouxa-regra)\nCorpo sem item marcado.\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_titulo_que_cita_o_rotulo_com_o_rotulo_aplicado_segue(self):
        (self.estado / "texto").write_text("feat: x (afrouxa-regra)\nCorpo.\n")
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)

    def test_item_marcado_com_mais_ou_lista_numerada_tambem_para(self):
        for item in ("+ [x] pede o rótulo afrouxa-regra", "1. [x] pede o rótulo afrouxa-regra",
                     "12) [X] pede o rótulo afrouxa-regra"):
            with self.subTest(item=item):
                (self.estado / "texto").write_text(f"feat: x\n{item}\n")
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("passo 5", r.stderr)

    def test_corpo_gerado_traz_o_item_do_rotulo_desmarcado(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr)
        criacao = self.registro.read_text()  # o corpo tem várias linhas; o registro guarda o argumento inteiro
        self.assertIn("- [ ] ", criacao)
        self.assertIn("afrouxa-regra", criacao)
        self.assertNotIn("[x]", criacao.lower())

    def test_rotulo_pedido_e_aplicado_pelo_dono_segue(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)

    def test_item_marcado_com_x_maiusculo_e_marcador_asterisco_tambem_para(self):
        (self.estado / "texto").write_text("feat: x\n  * [X] pede o rótulo afrouxa-regra\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)

    def _espera_rotulo(self, leitura, catraca_vermelha=False):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        (self.estado / "rotulo_na_leitura").write_text(f"{leitura}\n")
        if catraca_vermelha:
            (self.estado / "checks").write_text("bateria\tpass\t1m\turl\ncatraca\tfail\t5s\turl\n")
            (self.estado / "checks_apos_rotulo").write_text("bateria\tpass\t1m\turl\nbateria (python 3.14)\tpass\t1m\turl\ncatraca\tpass\t5s\turl\n")

    def test_esperar_rotulo_mescla_quando_o_rotulo_aparece_na_leitura_n(self):
        self._espera_rotulo(4, catraca_vermelha=True)
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "head").write_text(sha)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "60")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        chamadas = self.chamadas()
        self.assertGreaterEqual(int((self.estado / "leituras_rotulo").read_text()), 4)
        self.assertTrue(any(f"--match-head-commit {sha}" in c for c in chamadas if "pr merge" in c))
        self.assertFalse(any("--add-label" in c or "pr edit" in c for c in chamadas))

    def test_esperar_rotulo_prazo_esgotado_para_como_sem_a_opcao(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        self.assertIn("o dono ainda não o aplicou", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_esperar_rotulo_prazo_esgotado_com_catraca_vermelha_nao_mescla(self):
        (self.estado / "checks").write_text("bateria\tpass\t1m\turl\ncatraca\tfail\t5s\turl\n")
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("o dono ainda não o aplicou", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_esperar_rotulo_head_que_muda_durante_a_espera_para(self):
        self._espera_rotulo(50)
        (self.estado / "head").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "60")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("head", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_esperar_rotulo_outro_check_vermelho_para_sem_esperar(self):
        (self.estado / "checks").write_text("bateria\tfail\t1m\turl\n")
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "60")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 4", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_esperar_rotulo_catraca_vermelha_com_rotulo_aplicado_para_apos_a_tolerancia(self):
        (self.estado / "checks").write_text("catraca\tfail\t5s\turl\n")
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--esperar-rotulo", "--espera", "600")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 4", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_sem_a_opcao_o_rotulo_pedido_e_ausente_continua_parando(self):
        self._espera_rotulo(2)
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "60")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def _com_diff_em(self, caminho):
        self.git("switch", "-q", "melhoria/x")
        alvo = self.proj / caminho
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text("x\n")
        self.git("add", caminho)
        self.git("commit", "-q", "-m", "feat: controle")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")

    def test_dry_run_avisa_quando_o_diff_toca_caminho_de_controle_da_catraca(self):
        self._com_diff_em("hooks/parecer.py")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("hooks/parecer.py", r.stdout)
        self.assertIn("rótulo", r.stdout)
        self.assertEqual(self.chamadas(), [])

    def test_dry_run_nao_avisa_sem_caminho_de_controle(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("vai ser pedido", r.stdout)
        self.assertNotIn("aviso", r.stdout)
        self.assertNotIn("aviso", r.stderr)

    def test_dry_run_avisa_quando_nao_consegue_ler_o_diff(self):
        r = self.fechar("p1", "--ref", "melhoria/inexistente", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("não consegui conferir", r.stdout)

    def test_dry_run_descreve_o_nome_e_o_numero_do_pr_que_os_passos_usam(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("pr p1 --ref refs/heads/melhoria/x --base", r.stdout)
        self.assertIn("gh pr checks <número do PR", r.stdout)
        self.assertIn("gh pr view <número do PR", r.stdout)
        self.assertNotIn("pr checks melhoria/x", r.stdout)
        self.assertNotIn("pr view melhoria/x", r.stdout)
        self.assertIn("gh pr merge melhoria/x", r.stdout)  # o passo 6 roda por nome
        self.assertEqual(self.chamadas(), [])

    def test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido(self):
        r = self.fechar("p1", "--ref", "melhoria/inexistente", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--ref <sha não lido: a branch local não existe> --base", r.stdout)
        self.assertNotIn("--ref melhoria/inexistente --base", r.stdout)

    def test_lista_de_controles_vem_da_catraca_e_nao_e_copiada_no_script(self):
        codigo = SCRIPT.read_text()
        self.assertIn("catraca.py", codigo)
        spec = importlib.util.spec_from_file_location("catraca_lida", RAIZ / "tests" / "catraca.py")
        catraca = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(catraca)
        self.assertGreater(len(catraca.PROTEGIDOS), 5)
        for caminho in catraca.PROTEGIDOS:
            if caminho == "tests/catraca.py":  # o próprio arquivo da lista, que o script precisa citar para carregá-la
                continue
            self.assertNotIn(caminho, codigo)

    def test_commit_novo_na_branch_durante_a_espera_impede_o_merge(self):
        (self.estado / "head").write_text("0" * 40)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 6", r.stderr)
        self.assertFalse((self.estado / "estado").exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")

    def test_merge_passa_quando_o_head_confere(self):
        (self.estado / "head").write_text(self.git("rev-parse", "melhoria/x"))
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)

    def test_pr_aberto_para_a_main_e_recusado_no_passo_3(self):
        (self.estado / "aberto").write_text("7 main\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 3", r.stderr)
        self.assertFalse(any("pr merge" in c or "pr create" in c for c in self.chamadas()))

    def test_base_que_vira_main_antes_do_merge_e_recusada(self):
        (self.estado / "pre").write_text("main false\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 6", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_variaveis_de_teste_sem_a_trava_sao_ignoradas_com_aviso(self):
        env = {k: v for k, v in self.env.items() if k != "FORGE_FECHAR_TESTE"}
        vazio = self.tmp / "vazio"
        vazio.mkdir()
        env["PATH"] = f"{vazio}:/usr/bin:/bin"
        env.pop("FORGE_FECHAR_INTERVALO")
        r = subprocess.run(["bash", str(SCRIPT), "p1", "--ref", "melhoria/x"], cwd=self.proj, env=env,
                           capture_output=True, text=True, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("só valem com FORGE_FECHAR_TESTE=1", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_ref_invalido_e_recusado(self):
        for ref in ("-x", "a..b", "a b"):
            r = self.fechar("p1", "--ref", ref)
            self.assertNotEqual(r.returncode, 0, ref)
            self.assertIn("nome de branch válido", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def merges(self):
        return [c for c in self.chamadas() if c.startswith("gh pr merge")]

    def criacoes(self):
        return [c for c in self.chamadas() if c.startswith("gh pr create")]

    def test_estado_desconhecido_e_relido_e_merged_nao_abre_pr_nem_mescla_de_novo(self):
        (self.estado / "falha_estado").write_text("2")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.criacoes()), 1)
        self.assertEqual(len(self.merges()), 1)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_estado_desconhecido_nas_tres_leituras_para_sem_repetir_o_merge(self):
        (self.estado / "falha_estado").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 6", r.stderr)
        self.assertEqual(len(self.merges()), 1)

    def test_nova_rodada_com_pr_ja_mesclado_no_head_nao_abre_pr_nem_mescla(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        (self.estado / "estado").write_text("MERGED")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.merges(), [])
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_pr_mesclado_com_outro_head_nao_impede_o_pr_novo(self):
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {'0' * 40}\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)
        self.assertEqual(len(self.criacoes()), 1)
        self.assertEqual(len(self.merges()), 1)

    def test_head_ja_mesclado_na_base_nao_abre_pr(self):
        self.git("merge", "-q", "--no-ff", "melhoria/x", "-m", "merge x")
        self.git("push", "-q", "origin", "develop")
        self.git("fetch", "-q", "origin")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.merges(), [])
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")

    def test_502_na_leitura_do_pr_repete_e_passa(self):
        (self.estado / "falha_lista").write_text("2")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("gh pr list")]), 3)
        self.assertEqual(len(self.criacoes()), 1)

    def test_502_na_leitura_do_pr_em_tres_tentativas_para_sem_abrir_pr(self):
        (self.estado / "falha_lista").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 3", r.stderr)
        self.assertEqual(self.criacoes(), [])
        self.assertEqual(self.merges(), [])

    def test_502_na_leitura_dos_checks_repete_e_passa(self):
        (self.estado / "falha_checks").write_text("2")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_502_nos_checks_em_tres_leituras_seguidas_para_no_passo_4(self):
        (self.estado / "falha_checks").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 4", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_502_no_merge_nao_repete_o_merge(self):
        (self.estado / "merge_502").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 6", r.stderr)
        self.assertEqual(len(self.merges()), 1)
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")

    def test_merge_com_erro_mas_pr_merged_segue_sem_repetir(self):
        (self.estado / "merge_502_mas_mescla").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.merges()), 1)

    def test_502_no_push_delete_da_limpeza_repete_e_apaga(self):
        (self.estado / "falha_delete").write_text("2")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("git push origin --delete")]), 3)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_push_delete_que_falha_tres_vezes_so_avisa(self):
        (self.estado / "falha_delete").write_text("9")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("não apaguei a branch remota", r.stderr)
        self.assertEqual(len([c for c in self.chamadas() if c.startswith("git push origin --delete")]), 3)

    def test_criacao_de_pr_ready_e_merge_nunca_passam_pela_repeticao(self):
        codigo = [l for l in SCRIPT.read_text().splitlines() if not l.lstrip().startswith("#")]
        for l in codigo:
            if any(t in l for t in ("pr merge", "pr create", "pr ready")):
                self.assertNotIn("ler ", l)
                self.assertNotIn("repetir ", l)

    def test_modelo_de_pr_traz_o_item_do_rotulo_desmarcado_igual_ao_do_script(self):
        modelo = (RAIZ / ".github" / "pull_request_template.md").read_text(encoding="utf-8")
        itens = [l for l in modelo.splitlines() if "afrouxa-regra" in l]
        self.assertEqual(len(itens), 1)
        self.assertTrue(itens[0].startswith("- [ ] "))
        self.assertIn(itens[0].replace("`", "\\`"), SCRIPT.read_text(encoding="utf-8"))

    def test_limpeza_apaga_a_branch_remota_por_refs_heads(self):
        self.assertIn('git push origin --delete "refs/heads/$ref"', SCRIPT.read_text())

    # ---- LSREMOTE-EXATO: `git ls-remote origin refs/heads/<ref>` casa pelo fim do nome; só a coluna 2 igual ao nome inteiro vale ----
    def isca(self, nome, sha):
        """Põe no servidor outra branch cujo nome termina em /refs/heads/<nome>, com outro sha, listada antes dela (a/ < d, m)."""
        self.git("push", "-q", "origin", f"{sha}:refs/heads/a/refs/heads/{nome}")
        self.assertEqual(len(self.git("ls-remote", "origin", f"refs/heads/{nome}").splitlines()), 2)

    def test_lsremote_exato_isca_com_o_mesmo_fim_nao_engana_o_passo_2_nem_a_limpeza(self):
        self.isca("melhoria/x", self.git("rev-parse", "develop"))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("remota=ok", r.stdout)
        self.assertEqual(self.git("ls-remote", "--heads", "origin", "melhoria/x").split()[1:],
                         ["refs/heads/a/refs/heads/melhoria/x"])  # a isca fica; só a branch da entrega sai

    def test_lsremote_exato_isca_da_base_nao_engana_o_passo_2b(self):
        self.isca("develop", self.git("rev-parse", "melhoria/x"))
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("passo 2b", r.stderr)

    def test_lsremote_exato_isca_nao_engana_a_conferencia_depois_do_delete_que_falhou(self):
        self.isca("melhoria/x", self.git("rev-parse", "develop"))
        (self.estado / "delete_apaga_e_falha").write_text("1")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("já não existe no servidor", r.stdout)

    def test_lsremote_exato_um_ajudante_unico_le_a_branch_remota(self):
        codigo = [l for l in SCRIPT.read_text().splitlines() if not l.lstrip().startswith(("#", "echo", "passo"))]
        chamadas = [l for l in codigo if "ls-remote" in l]
        self.assertEqual(len(chamadas), 1, chamadas)
        corpo = SCRIPT.read_text().split("remoto_exato() {", 1)[1].split("\n}", 1)[0]
        self.assertIn(chamadas[0].strip(), corpo)  # a única chamada é a do ajudante
        self.assertIn("$2 == r", corpo)  # e o ajudante filtra a coluna 2 pelo nome inteiro

    # ---- SHELLCHECK-FECHAR: o forge-fechar passa no shellcheck e está na lista do shellcheck do CI ----
    def test_shellcheck_fechar_esta_na_lista_do_ci(self):
        # COBERTURA-P6: a lista do CI vem do shebang (tests.test_pre_push_afetados.ShellcheckPeloShebang roda o passo); o
        # forge-fechar entra porque a primeira linha dele é de bash.
        ci = (RAIZ / ".github/workflows/ci.yml").read_text()
        self.assertIn("'#!'*bash*|'#!'*/sh|'#!'*' sh') lista+=(\"$f\")", ci)
        self.assertRegex(SCRIPT.read_text().splitlines()[0], r"^#!.*bash")

    def test_shellcheck_fechar_passa_limpo(self):
        if shutil.which("shellcheck") is None:
            self.skipTest("AVISO: shellcheck fora do PATH; o CI roda este passo")
        r = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fechar_sem_a_e_b_ou_c_solto(self):
        # O shellcheck do runner (pacote do Ubuntu, mais velho que o local) acusa SC2015 em `A && B || C`; o local não.
        # O teste recusa a forma na fonte, qualquer que seja a versão do shellcheck instalada.
        import re
        achados = []
        for n, linha in enumerate(SCRIPT.read_text().splitlines(), 1):
            t = linha.strip()
            if t.startswith("#"):
                continue
            t = re.sub(r'"(?:\\.|[^"\\])*"|\'[^\']*\'', '""', t)  # texto entre aspas
            ant = None
            while ant != t:  # tira grupos internos: $(...), (...), { ...; }, [[ ... ]], [ ... ]
                ant = t
                t = re.sub(r'\$?\([^()]*\)|\{ [^{}]*\}|\[\[ .*?\]\]|\[ [^\[\]]*\]', 'G', t)
            if re.search(r'&&.*\|\|', t):
                achados.append(f"{n}: {linha.strip()}")
        self.assertEqual(achados, [], "use `if ! { A && B; }; then C; fi`: " + "\n".join(achados))

    def test_espera_os_checks_aparecerem_em_pr_recem_aberto(self):
        (self.estado / "sem_checks_ate").write_text("6")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(any("pr merge" in c for c in self.chamadas()))

    def test_sem_checks_ate_o_limite_para_no_passo_4(self):
        (self.estado / "sem_checks_ate").write_text("999")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 4", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_pr_em_rascunho_vira_pronto_antes_do_merge(self):
        (self.estado / "pre").write_text("develop true\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)
        chamadas = self.chamadas()
        self.assertLess(chamadas.index("gh pr ready melhoria/x"),
                        next(i for i, c in enumerate(chamadas) if "pr merge" in c))

    def test_erro_do_gh_no_passo_5_para_o_fluxo(self):
        (self.estado / "falha_leitura").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        self.assertFalse(any("pr merge" in c for c in self.chamadas()))

    def test_recusa_rodar_fora_do_repositorio_do_forge(self):
        (self.proj / ".claude-plugin" / "plugin.json").write_text('{"name": "outro"}\n')
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("não é o repositório do Forge", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_script_nunca_usa_force_no_verify_nem_rotulo(self):
        codigo = "\n".join(l for l in SCRIPT.read_text().splitlines() if not l.lstrip().startswith("#"))
        for proibido in ("--force", "--no-verify", "--add-label", "gh label", "-u origin", "origin main"):
            self.assertNotIn(proibido, codigo)


    def test_log_em_arquivo_com_um_registro_por_passo_e_caminho_na_primeira_linha(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        primeira = r.stdout.splitlines()[0]
        self.assertTrue(primeira.startswith("log: "), primeira)
        log = Path(primeira[len("log: "):])
        self.assertTrue(log.is_file())
        self.assertEqual(log.parent, self.tmp / "logs")
        linhas = log.read_text().splitlines()
        for n in "1234567":
            self.assertEqual(sum(1 for x in linhas if f" [{n}] " in x), 1, (n, linhas))
        self.assertTrue(all(x[:4].isdigit() and x[10] == "T" for x in linhas), linhas)
        self.assertTrue(any("Entrega p1 fechada em develop." in x for x in linhas[-4:]), linhas)  # stderr do git pode chegar depois
        self.assertTrue(linhas[-1].endswith(" fim: código 0"), linhas[-1])
        self.assertEqual(oct(log.stat().st_mode & 0o777), "0o600")

    def test_log_tambem_guarda_a_saida_de_erro_e_mascara_segredo(self):
        (self.estado / "checks").write_text("bateria\tfail\t1m\thttps://x/?token=ghp_ABCDEF123456\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        log = Path(r.stdout.splitlines()[0][len("log: "):])
        texto = log.read_text()
        self.assertIn("parou no passo 4", texto)
        self.assertNotIn("ghp_ABCDEF123456", texto)
        self.assertIn("ghp_ABCDEF123456", r.stderr)  # a tela continua igual

    def test_dry_run_tambem_grava_o_log(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        log = Path(r.stdout.splitlines()[0][len("log: "):])
        self.assertIn("[7]", log.read_text())

    # ---- C1: log endurecido (L1 a L6) ----
    def fechar_sem(self, *args, remover=(), **extra):
        env = {k: v for k, v in self.env.items() if k not in remover}
        env.update(extra)
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=self.proj, env=env, capture_output=True, text=True,
                              timeout=60)

    def log_de(self, r):
        return Path(r.stdout.splitlines()[0][len("log: "):])

    def test_l1_pasta_padrao_e_por_usuario_com_xdg_ou_tmp(self):
        xdg, tmpd = self.tmp / "xdg", self.tmp / "tmpd"
        xdg.mkdir()
        tmpd.mkdir()
        r = self.fechar_sem("p1", "--ref", "melhoria/x", "--dry-run", remover=("FORGE_FECHAR_LOG_DIR",),
                            XDG_RUNTIME_DIR=str(xdg), TMPDIR=str(tmpd))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.log_de(r).parent, xdg / "forge-fechar-logs")
        self.assertEqual(oct((xdg / "forge-fechar-logs").stat().st_mode & 0o777), "0o700")
        r = self.fechar_sem("p1", "--ref", "melhoria/x", "--dry-run", remover=("FORGE_FECHAR_LOG_DIR", "XDG_RUNTIME_DIR"),
                            TMPDIR=str(tmpd))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.log_de(r).parent, tmpd / f"forge-fechar-logs-{os.getuid()}")

    def test_l1_recusa_pasta_que_e_link_ou_nao_e_diretorio(self):
        alvo = self.tmp / "alvo"
        alvo.mkdir(mode=0o700)
        link = self.tmp / "link"
        link.symlink_to(alvo)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(link))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("link simbólico", r.stderr)
        self.assertEqual(list(alvo.iterdir()), [])
        arquivo = self.tmp / "arquivo"
        arquivo.write_text("x\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run", FORGE_FECHAR_LOG_DIR=str(arquivo))
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(arquivo.read_text(), "x\n")

    def test_l1_arquivo_do_log_vem_de_mktemp_e_e_600(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        a, b = self.log_de(r), self.log_de(self.fechar("p1", "--ref", "melhoria/x", "--dry-run"))
        self.assertNotEqual(a, b)
        self.assertEqual(oct(a.stat().st_mode & 0o777), "0o600")

    SEGREDOS = (
        ("GH_TOKEN=abc123segredo", "abc123segredo"),
        ("export MEU_SECRET=segredo9", "segredo9"),
        ("DB_PASSWORD=senha777", "senha777"),
        ('{"token": "valorjson1"}', "valorjson1"),
        ("https://usuario:senhaurl@github.com/x", "senhaurl"),
        ("Authorization: Basic dXNlcjpwYXNzd29yZA==", "dXNlcjpwYXNzd29yZA"),
        ("authorization: token zzz999", "zzz999"),
        ("Basic dXNlcjpwYXNzd29yZA==", "dXNlcjpwYXNzd29yZA"),
        ("BEARER segredo5", "segredo5"),
        ("https://x/?access_token=qwerty42&a=1", "qwerty42"),
        ("TOKEN=maiusculo1", "maiusculo1"),
        ("Bearer abc123", "abc123"),
        ("token=abc", "=abc"),
    )

    def test_l2_mascara_cada_forma_de_segredo_no_log_e_mantem_a_tela(self):
        for linha, segredo in self.SEGREDOS:
            with self.subTest(linha=linha):
                (self.estado / "checks").write_text(f"bateria\tfail\t1m\t{linha}\n")
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(segredo, r.stderr)
                self.assertNotIn(segredo, self.log_de(r).read_text())

    def test_l3_a_mascara_nao_troca_prosa_com_a_palavra_token(self):
        for linha in ("token inválido", "o token expirou", "o token foi lido"):
            with self.subTest(linha=linha):
                (self.estado / "checks").write_text(f"bateria\tfail\t1m\t{linha}\n")
                r = self.fechar("p1", "--ref", "melhoria/x")
                self.assertIn(linha, self.log_de(r).read_text())

    def test_l4_retencao_apaga_so_log_velho_do_proprio_nome_dentro_da_pasta(self):
        logs = self.tmp / "logs"
        logs.mkdir(mode=0o700)
        velho = logs / "forge-fechar-velho-1.log"
        novo = logs / "forge-fechar-novo-1.log"
        outro = logs / "outro-nome.log"
        alvo = self.tmp / "fora.log"
        link = logs / "forge-fechar-link-1.log"
        for f in (velho, novo, outro, alvo):
            f.write_text("x\n")
        link.symlink_to(alvo)
        antigo = 1_000_000_000
        for f in (velho, outro, alvo):
            os.utime(f, (antigo, antigo))
        os.utime(link, (antigo, antigo), follow_symlinks=False)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(velho.exists())
        self.assertTrue(novo.exists())
        self.assertTrue(outro.exists())
        self.assertTrue(alvo.exists())

    def test_l5_todo_log_termina_em_fim_codigo_inclusive_em_erro(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_RC="1")
        self.assertNotEqual(r.returncode, 0)
        linhas = self.log_de(r).read_text().splitlines()
        # stdout e stderr têm registradores próprios, sem ordem entre si (contrato do registrar): a parada é a última linha [err],
        # não uma das três últimas (CI do PR 547, Python 3.14, parte 2/3: o "[1] pareceres" do stdout gravado depois do [err])
        erros = [x for x in linhas[:-1] if " [err] " in x]
        self.assertTrue(erros and "parou no passo 1" in erros[-1], linhas)
        self.assertTrue(linhas[-1].endswith(" fim: código 1"), linhas)
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))
        self.assertIn("fim: código 0", r.stdout)

    def test_l5_registrador_de_stderr_lento_ainda_grava_a_parada_antes_do_fim(self):
        # TESTE-FECHAR-L5-CORRIDA (v0478): a corrida do L5 com o tempo a favor do defeito. O `sed` do mascarar atrasa 1 s só a linha da
        # parada; o `fim` espera o registrador de stderr (wait) antes do `fim: código`, então a ordem sai a mesma de qualquer máquina.
        lento = self.tmp / "bin" / "sed"
        lento.write_text('#!/usr/bin/env bash\nif [ "${1-}" = -E ]; then\n  e="$(cat)"\n  case "$e" in *"parou no passo"*) sleep 1 ;; esac\n'
                         f'  printf "%s" "$e" | exec {shutil.which("sed")} "$@"\nfi\nexec {shutil.which("sed")} "$@"\n', encoding="utf-8")
        lento.chmod(0o755)
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_RC="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        linhas = self.log_de(r).read_text().splitlines()
        self.assertTrue(linhas[-1].endswith(" fim: código 1"), linhas)
        erros = [x for x in linhas if " [err] " in x]
        self.assertIn("[err] forge-fechar: parou no passo 1", erros[-1], linhas)

    def test_l6_stderr_vai_ao_log_com_prefixo_err_e_sem_linha_partida(self):
        (self.estado / "checks").write_text("bateria\tfail\t1m\turl\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        linhas = self.log_de(r).read_text().splitlines()
        erros = [x for x in linhas if " [err] " in x]
        self.assertTrue(any("parou no passo 4" in x for x in erros), linhas)
        self.assertFalse(any("[4] checks" in x and "[err]" in x for x in linhas))
        self.assertTrue(all(x[:4].isdigit() and x[10] == "T" and x[19] == "Z" for x in linhas), linhas)

    # ---- C2: número da execução e do job de cada check no log ----
    def test_c2_log_traz_run_e_job_de_cada_check_o_head_e_o_commit_do_merge(self):
        (self.estado / "checks").write_text(
            "bateria\tpass\t5m\thttps://github.com/o/r/actions/runs/111/job/222\n"
            "bateria (python 3.14)\tpass\t5m\thttps://github.com/o/r/actions/runs/111/job/223\n"
            "catraca\tpass\t5s\thttps://github.com/o/r/actions/runs/333/job/444\n"
            "extra\tskipping\t0\thttps://exemplo.test/sem-padrao?token=ghp_SEGREDO123\n")
        (self.estado / "merge_commit").write_text("abc123def456")
        sha = self.git("rev-parse", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        texto = self.log_de(r).read_text()
        for esperado in ("check bateria pass run=111 job=222", "check catraca pass run=333 job=444",
                         "check extra skipping run=? job=?", f"head: {sha}", "merge: abc123def456"):
            self.assertIn(esperado, r.stdout)
            self.assertIn(esperado, texto)
        self.assertNotIn("ghp_SEGREDO123", texto)
        self.assertLess(texto.index("check bateria"), texto.index("[6] "))
        self.assertLess(texto.index("[6] "), texto.index("merge: abc123def456"))

    def test_c2_check_vermelho_continua_parando_sem_linhas_de_resumo(self):
        (self.estado / "checks").write_text("bateria\tfail\t1m\thttps://github.com/o/r/actions/runs/1/job/2\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("check bateria", r.stdout)
        self.assertNotIn("checks verdes", r.stdout)

    def test_c2_contagem_pendente_so_quando_muda(self):
        (self.estado / "checks").write_text("bateria\tpending\t0\turl\ncatraca\tpass\t1s\turl\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "2", FORGE_FECHAR_INTERVALO="1")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout.count("checks: pass=1 pendentes=1"), 1, r.stdout)

    # ---- C3: limpeza como função única e modo --limpar ----
    def com_worktree(self):
        wt = self.tmp / "wt-x"
        self.git("worktree", "add", "-q", str(wt), "melhoria/x")
        return wt

    def resumo(self, r):
        return [l for l in r.stdout.splitlines() if l.startswith("limpeza: ")]

    def marcas(self, prefixo):
        return [i for i, c in enumerate(self.chamadas()) if c.startswith(prefixo)]

    def arvores(self):
        return [l for l in self.git("worktree", "list", "--porcelain").splitlines() if l.startswith("worktree ")]

    def test_c3_ebusy_com_o_diretorio_ja_apagado_roda_prune_e_termina_ok(self):
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("apaga")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual(len(self.marcas("git worktree prune")), 1)
        self.assertEqual(len(self.arvores()), 1)
        self.assertFalse(wt.exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))

    def test_c3_ebusy_com_o_diretorio_de_pe_deixa_pendente_com_o_comando_e_codigo_3(self):
        wt = self.com_worktree()
        (self.estado / "wt_busy").write_text("persiste")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertIn(f"git worktree remove {wt}", r.stdout)
        self.assertIn("git branch -D melhoria/x", r.stdout)
        self.assertEqual(self.marcas("git worktree prune"), [])
        self.assertTrue(wt.exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "+ melhoria/x")
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertIn("Entrega p1 fechada em develop", r.stdout)
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 3"))

    def test_c3_worktree_suja_so_avisa_sem_forcar(self):
        wt = self.com_worktree()
        (wt / "rascunho").write_text("não commitado\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=pendente branch=pendente"])
        self.assertTrue((wt / "rascunho").exists())
        self.assertNotIn("--force", self.registro.read_text())  # o texto do git ("use --force") é dele, não uma chamada do script
        self.assertNotIn("--force", SCRIPT.read_text().replace("# ", "#"). split("limpar_entrega() {")[1].split("\n}\n")[0])

    def test_c3_ordem_worktree_depois_branch_e_por_ultimo_o_push_delete(self):
        self.com_worktree()
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        (w,), (b,), (d,) = (self.marcas("git worktree remove"), self.marcas("git branch -D"),
                            self.marcas("git push origin --delete"))
        self.assertLess(w, b)
        self.assertLess(b, d)

    def test_c3_branch_com_commit_alem_do_mesclado_nao_e_apagada(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "novo").write_text("depois do merge\n")
        self.git("add", "novo")
        self.git("commit", "-q", "-m", "feat: depois do merge")
        self.git("switch", "-q", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=pendente"])
        self.assertEqual(self.marcas("git branch -D"), [])
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")

    def test_c3_branch_remota_com_commit_alem_do_mesclado_nao_e_apagada(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "novo").write_text("depois do merge\n")
        self.git("add", "novo")
        self.git("commit", "-q", "-m", "feat: depois do merge")
        self.git("push", "-q", "origin", "melhoria/x")
        novo = self.git("rev-parse", "melhoria/x")
        self.git("reset", "-q", "--hard", sha)
        self.git("switch", "-q", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=pendente worktree=ok branch=ok"])
        self.assertEqual(self.marcas("git push origin --delete"), [])
        self.assertIn(novo, self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_c3_limpar_sem_prova_de_pr_merged_recusa_e_nao_apaga_nada(self):
        self.com_worktree()
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertNotEqual(r.returncode, 0)
        self.assertNotEqual(r.returncode, 3)
        self.assertIn("sem prova", r.stderr)
        self.assertEqual(self.marcas("git "), [])
        self.assertIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "+ melhoria/x")
        # PR aberto, ou mesclado em outra base ou com outro head, também não é prova
        for extra in (f"7 OPEN develop {'a' * 40}\n", f"8 MERGED main {self.git('rev-parse', 'melhoria/x')}\n"):
            (self.estado / "lista_extra").write_text(extra)
            r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
            self.assertNotEqual(r.returncode, 0, extra)
            self.assertEqual(self.marcas("git "), [])

    def test_c3_limpar_com_prova_apaga_e_repete_sem_efeito_colateral(self):
        wt = self.com_worktree()
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertFalse(wt.exists())
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertFalse(any(c.startswith(("forge-check", "gh pr merge", "gh pr create")) for c in self.chamadas()))
        antes = self.chamadas()
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual([c for c in self.chamadas() if c.startswith("git ")], [c for c in antes if c.startswith("git ")])
        self.assertTrue(self.log_de(r).read_text().splitlines()[-1].endswith(" fim: código 0"))

    def test_c3_limpar_com_parte_ja_apagada_faz_so_o_que_falta(self):
        sha = self.git("rev-parse", "melhoria/x")
        (self.estado / "lista_extra").write_text(f"234 MERGED develop {sha}\n")
        self.git("branch", "-D", "melhoria/x")
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.resumo(r), ["limpeza: remota=ok worktree=ok branch=ok"])
        self.assertEqual(len(self.marcas("git push origin --delete")), 1)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))

    def test_c3_limpar_continua_recusando_main_develop_homolog_e_dry_run_nao_apaga(self):
        for ref in ("main", "develop", "homolog"):
            r = self.fechar("p1", "--ref", ref, "--limpar")
            self.assertNotEqual(r.returncode, 0, ref)
            self.assertIn("R-FLUXO", r.stderr)
        r = self.fechar("p1", "--ref", "melhoria/x", "--limpar", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.chamadas(), [])
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "melhoria/x")

    def test_c3_so_o_codigo_da_limpeza_vira_3_e_o_resto_segue_em_1(self):
        r = self.fechar("p1", "--ref", "melhoria/x", CHECK_RC="1")
        self.assertEqual(r.returncode, 1)

    def test_c3_a_limpeza_e_uma_funcao_chamada_do_passo_7_e_do_limpar(self):
        codigo = "\n".join(l for l in SCRIPT.read_text().splitlines() if not l.lstrip().startswith("#"))
        self.assertEqual(codigo.count("git branch -D \"$ref\""), 1)
        self.assertEqual(codigo.count('git push origin --delete "refs/heads/$ref"'), 1)
        self.assertGreaterEqual(codigo.count("limpar_entrega"), 3)


# BP2 I1 (--conserto): o gh das leituras do conserto, só nas formas exatas que o script pede (outra forma cai no gh falso de sempre,
# que sai com 64); o resto vai ao gh falso de sempre (GH_BASE). Arquivos em $ESTADO: c_run_<R> (a linha do run: evento, branch, sha,
# status, conclusão), c_jobs, c_anot_<job> (caminho<TAB>mensagem), c_run_pr, c_passos, a pasta c_pulados e c_verde; c_falha_<x>: falha.
GH_CONSERTO = r'''#!/usr/bin/env bash
[ "$1" = "--version" ] && exec "$GH_BASE" "$@"
saida() { echo "gh $*" >> "$REGISTRO"; [ -f "$ESTADO/c_falha_$1" ] && exit 1; }
case "$*" in
  "run view "*" --json event,headBranch,headSha,status,conclusion --jq \"\(.event) \(.headBranch) \(.headSha) \(.status) \(.conclusion)\"")
    [[ "$3" =~ ^[0-9]+$ ]] || exit 64; saida run "$@"; cat "$ESTADO/c_run_$3" 2>/dev/null || exit 1; exit 0 ;;
  "run view "*" --json jobs --jq .jobs[] | select(.conclusion == \"failure\") | .databaseId")
    saida jobs "$@"; cat "$ESTADO/c_jobs"; exit 0 ;;
  "api repos/{owner}/{repo}/check-runs/"*"/annotations --jq .[] | select(.annotation_level == \"failure\") | [.path, .message] | @tsv")
    j="${2#repos/\{owner\}/\{repo\}/check-runs/}"; j="${j%/annotations}"; saida anot "$@"; cat "$ESTADO/c_anot_$j" 2>/dev/null || exit 1; exit 0 ;;
  "run list --commit "*" --event pull_request --workflow CI --status success --limit 1 --json databaseId --jq .[0].databaseId")
    saida run_pr "$@"; cat "$ESTADO/c_run_pr" 2>/dev/null || echo 500; exit 0 ;;
  "run view "*" --json jobs --jq .jobs[].steps[] | select(.name == \"Testes do Forge (parte)\") | .conclusion")
    saida passos "$@"; cat "$ESTADO/c_passos" 2>/dev/null || printf 'success\nsuccess\n'; exit 0 ;;
  "run download "*" --pattern pulados-* --dir "*)
    saida download "$@"; [ -d "$ESTADO/c_pulados" ] || exit 1; cp -r "$ESTADO/c_pulados/." "${@: -1}/"; exit 0 ;;
  "run list --branch develop --event push --workflow CI --status success --limit 1 --json headSha --jq .[0].headSha")
    saida verde "$@"; cat "$ESTADO/c_verde"; exit 0 ;;
esac
exec "$GH_BASE" "$@"
'''
# $ESTADO/c_falha_diff: o `git diff` cujos argumentos contêm esse texto falha; o resto vai ao git falso de sempre (git-base).
GIT_CONSERTO = r'''#!/usr/bin/env bash
if [ "$1" = diff ] && [ -f "$ESTADO/c_falha_diff" ] && [[ "$*" == *"$(cat "$ESTADO/c_falha_diff")"* ]]; then exit 1; fi
exec "$(dirname "$0")/git-base" "$@"
'''
# forge-check falso do conserto: o `anotar` sai com CHECK_ANOTAR_RC (padrão 0); o resto, como o de sempre.
CHECK_CONSERTO = ('#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\n'
                  '[ "$1" = anotar ] && exit "${CHECK_ANOTAR_RC:-0}"\nexit "${CHECK_RC:-0}"\n')


class Conserto(unittest.TestCase):
    """BP2 I1: `--conserto <run>` libera o 6b com a develop vermelha só com C1, C3, C4 e C5; C7 registra; recusa --lote e --armar."""
    tearDown = Fechar.tearDown
    git = Fechar.git
    fechar = Fechar.fechar
    chamadas = Fechar.chamadas

    def setUp(self):
        Fechar.setUp(self)
        bin_ = self.tmp / "bin"
        (bin_ / "git").rename(bin_ / "git-base")
        for caminho, texto in ((bin_ / "git", GIT_CONSERTO), (self.tmp / "gh_conserto", GH_CONSERTO), (self.tmp / "check", CHECK_CONSERTO)):
            caminho.write_text(texto, encoding="utf-8")
            caminho.chmod(0o755)
        self.env.update(GH_BASE=self.env["FORGE_GH"], FORGE_GH=str(self.tmp / "gh_conserto"))
        self.base_com_os_testes()
        self.verde = self.topo = self.git("rev-parse", "develop")
        self.run_do_topo()
        (self.estado / "c_jobs").write_text("71\n")
        self.anotar("b\ttest_b.Caso.test_um: AssertionError: 1 != 2\n.github\tProcess completed with exit code 1.\n")
        self.pulados([])
        (self.estado / "c_verde").write_text(self.verde + "\n")
        for herdada in ("FORGE_FECHAR_LOTE_PAI", "FORGE_FECHAR_CONSERTO_H"):  # a marca e o head do pai nunca vêm do ambiente (AR-4)
            self.env.pop(herdada, None)

    def base_com_os_testes(self):
        """Os testes anotados (tests/test_b.py e tests/test_z.py) existem na develop e no head: o C4 exige o método no head."""
        self.git("switch", "-q", "develop")
        (self.proj / "tests").mkdir()
        metodos = "".join(f"    def test_{n}(self):\n        pass\n" for n in ["um", *range(10)])
        for nome in ("test_b", "test_z"):
            (self.proj / "tests" / f"{nome}.py").write_text(f"class Caso:\n{metodos}")
        self.git("add", "tests")
        self.git("commit", "-q", "-m", "test: base")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("rebase", "-q", "develop")
        self.git("push", "-q", "origin", "--delete", "melhoria/x")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        self.registro.write_text("")

    def run_do_topo(self, linha=None):
        (self.estado / "c_run_44").write_text((linha or f"push develop {self.topo} completed failure") + "\n")

    def anotar(self, texto, job="71"):
        (self.estado / f"c_anot_{job}").write_text(texto)

    def pulados(self, ids):
        pasta = self.estado / "c_pulados" / "pulados-doze-1"
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "parte-1.json").write_text(json.dumps({"parte": "1/5", "pulados": len(ids), "pulados_ids": ids}))

    def merges(self):
        return [c for c in self.chamadas() if c.startswith("gh pr merge")]

    def conserto(self, *extra, ref="melhoria/x", **env):
        return self.fechar("p1", "--ref", ref, "--conserto", "44", *extra, **env)

    def assert_parou(self, r, texto):
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(texto, r.stderr)
        self.assertEqual(self.merges(), [])

    def develop_anda(self, arquivo, texto=None, msg="feat: develop"):
        """Um commit na develop (e no origin) que grava `arquivo` (texto None: apaga); o topo e o run vermelho passam a ele."""
        self.git("switch", "-q", "develop")
        if texto is None:
            self.git("rm", "-q", arquivo)
        else:
            (self.proj / arquivo).write_text(texto)
            self.git("add", arquivo)
        self.git("commit", "-q", "-m", msg)
        self.git("push", "-q", "origin", "develop")
        self.topo = self.git("rev-parse", "develop")
        self.run_do_topo()
        return self.topo

    def ramo_da_develop(self, nome, arquivo, texto):
        self.git("switch", "-q", "-c", nome, "develop")
        (self.proj / arquivo).parent.mkdir(parents=True, exist_ok=True)
        (self.proj / arquivo).write_text(texto)
        self.git("add", arquivo)
        self.git("commit", "-q", "-m", "fix: conserto")
        self.git("push", "-q", "origin", nome)
        self.git("switch", "-q", "develop")

    def test_conserto_mescla_com_a_develop_vermelha_preso_ao_head_e_registra(self):
        sha = self.git("rev-parse", "melhoria/x")
        r = self.conserto()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.merges(), [f"gh pr merge melhoria/x --auto --squash --match-head-commit {sha}"])
        self.assertFalse([c for c in self.chamadas() if c.startswith(f"gh run list --branch develop --event push --commit {self.topo}")])
        linha = f"conserto da develop: run 44, topo {self.topo[:7]}, PR #7, head {sha[:7]}"
        self.assertIn(linha, r.stdout)
        self.assertIn(f"forge-check anotar --raiz-pedidos {self.tmp / '.forge-contrib'} --pedido p1 --tipo historico --literal {linha}",
                      self.chamadas())
        self.assertIn("C5: o PR toca o arquivo de um teste que falhou.", r.stdout)

    def test_sem_conserto_a_develop_vermelha_para_no_6b(self):
        (self.estado / f"runs_{self.topo}").write_text("44\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assert_parou(r, "parou no passo 6b: a develop está vermelha")

    def test_run_fora_da_forma_para_antes_do_passo_1(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--conserto", "44a")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--conserto pede o número do run (só dígitos; recebi: 44a)", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_conserto_sem_valor_para_antes_do_passo_1(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--conserto")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--conserto pede o número do run vermelho do push na develop", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_conserto_recusa_lote_e_armar(self):
        for args in (("--lote", "p1:melhoria/x", "p2:melhoria/y"), ("p1", "--ref", "melhoria/x", "--armar")):
            with self.subTest(args=args):
                r = self.fechar(*args, "--conserto", "44")
                self.assertEqual(r.returncode, 1)
                self.assertIn("--conserto não combina com --lote nem com --armar", r.stderr)
                self.assertEqual(self.chamadas(), [])

    # ---- C1: o run é o push vermelho do topo, relido antes do merge ----
    def test_c1_topo_ilegivel_ou_vazio_para(self):
        # o 2b e o 6a leem a develop no servidor antes; a terceira leitura, a do C1, falha ou volta sem a ref
        for modo, msg in (("falha", "servidor; nada foi mesclado"), ("vazio", "servidor (resposta vazia)")):
            with self.subTest(modo=modo):
                self.registro.write_text("")
                (self.estado / "lsremote_develop_ok").write_text("2")
                (self.estado / "lsremote_develop_modo").write_text(modo)
                self.assert_parou(self.conserto(), "parou no passo 6b (C1): não consegui ler a develop no " + msg)

    def test_c1_run_ilegivel_para(self):
        (self.estado / "c_falha_run").touch()
        self.assert_parou(self.conserto(), "parou no passo 6b (C1): não consegui ler o run 44")

    def test_c1_run_de_outro_evento_ou_branch_para(self):
        for linha in (f"pull_request develop {self.topo} completed failure", f"push melhoria/x {self.topo} completed failure"):
            with self.subTest(linha=linha):
                self.registro.write_text("")
                self.run_do_topo(linha)
                self.assert_parou(self.conserto(), "parou no passo 6b (C1): o run 44 não é do push na develop")

    def test_c1_run_de_outro_commit_para(self):
        self.run_do_topo(f"push develop {'a' * 40} completed failure")
        self.assert_parou(self.conserto(), f"o run 44 é do aaaaaaa, não do topo da develop ({self.topo[:7]})")

    def test_c1_run_pendente_ou_verde_para(self):
        for fim in ("in_progress ", "completed success", "completed cancelled"):
            with self.subTest(fim=fim):
                self.registro.write_text("")
                self.run_do_topo(f"push develop {self.topo} {fim}")
                self.assert_parou(self.conserto(), "parou no passo 6b (C1): o run 44 não terminou com falha")

    def test_c1_topo_que_anda_depois_do_6b_para_sem_mesclar(self):
        (self.estado / "lsremote_develop_ok").write_text("3")
        (self.estado / "lsremote_develop_modo").write_text("vazio")
        self.assert_parou(self.conserto(), "parou no passo 6 (C1): a develop andou depois do 6b")

    # ---- C3: o head é o revisado ou o merge dele com o topo gerado pelo 2b ----
    def test_c3_base_trazida_pelo_2b_mescla_o_merge_do_head_revisado_com_o_topo(self):
        h = self.git("rev-parse", "melhoria/x")
        topo = self.develop_anda("c", "3\n")
        r = self.conserto()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(len(self.merges()), 1)
        m = self.merges()[0].rsplit(" ", 1)[1]  # a branch já foi limpa: o head mesclado vem do --match-head-commit
        self.assertEqual(self.git("rev-list", "--parents", "-n", "1", m).split(), [m, h, topo])

    def trazida(self, **env):
        return self.fechar("p1", "--ref", "melhoria/x", "--conserto", "44", "--trazida", **env)

    def test_c3_trazida_sem_a_marca_do_pai_para(self):
        self.assert_parou(self.trazida(), "parou no passo 6b (C3): --trazida sem a marca do processo pai")

    def test_c3_head_que_nao_e_merge_do_revisado_com_o_topo_para(self):
        h = self.git("rev-parse", "melhoria/x")
        r = self.trazida(FORGE_FECHAR_LOTE_PAI=str(os.getpid()), FORGE_FECHAR_CONSERTO_H=h)
        self.assert_parou(r, "não é o merge do head revisado com o topo da develop")

    def test_c3_merge_com_arvore_diferente_da_do_merge_tree_para(self):
        h = self.git("rev-parse", "melhoria/x")
        topo = self.develop_anda("c", "3\n")
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "intruso").write_text("x\n")
        self.git("add", "intruso")
        arvore = self.git("write-tree")
        self.git("reset", "-q", "--hard", h)
        m = self.git("commit-tree", arvore, "-p", h, "-p", topo, "-m", "merge forjado")
        self.git("update-ref", "refs/heads/melhoria/x", m)
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        r = self.trazida(FORGE_FECHAR_LOTE_PAI=str(os.getpid()), FORGE_FECHAR_CONSERTO_H=h)
        self.assert_parou(r, "parou no passo 6b (C3): a árvore do head")

    # ---- C4: os testes que falharam no run passaram no CI do PR ----
    def test_c4_jobs_ilegiveis_para(self):
        (self.estado / "c_falha_jobs").touch()
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): não consegui ler os jobs do run 44")

    def test_c4_job_fora_da_forma_para(self):
        (self.estado / "c_jobs").write_text("71/../x\n")
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): job fora da forma")

    def test_c4_anotacoes_ilegiveis_para(self):
        (self.estado / "c_anot_71").unlink()
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): não consegui ler as anotações do job 71")

    def test_c4_dez_testes_anotados_num_job_pede_o_log(self):
        self.anotar("".join(f"b\ttest_b.Caso.test_{i}: erro\n" for i in range(10)))
        self.assert_parou(self.conserto(), "o job 71 tem 10 testes anotados (o GitHub mostra só 10 por passo)")

    def test_c4_nove_testes_anotados_seguem(self):
        self.anotar("".join(f"b\ttest_b.Caso.test_{i}: erro\n" for i in range(9)))
        r = self.conserto()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_c4_sem_teste_nas_anotacoes_para(self):
        self.anotar(".github\tProcess completed with exit code 1.\n")
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): nenhum teste nas anotações")

    def test_c4_e_c5_leituras_que_falham_param(self):
        for falha, msg in (("run_pr", "(C4): não consegui ler o CI do PR no head"),
                           ("passos", "(C4): não consegui ler os passos do CI do PR (run 500)"),
                           ("verde", "(C5): não consegui ler o último push verde da develop")):
            with self.subTest(falha=falha):
                self.registro.write_text("")
                for f in self.estado.glob("c_falha_*"):
                    f.unlink()
                (self.estado / f"c_falha_{falha}").touch()
                self.sem_teste_tocado()
                self.assert_parou(self.conserto(), "parou no passo 6b " + msg)

    def test_c4_sem_pasta_temporaria_para(self):
        self.assert_parou(self.conserto(TMPDIR=str(self.tmp / "nao-existe")), "parou no passo 6b (C4): sem pasta temporária")

    def test_c4_sem_ci_verde_do_pr_para(self):
        (self.estado / "c_run_pr").write_text("null\n")
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): sem o CI verde do PR no head")

    def test_c4_arvore_provada_na_develop_conta_como_passou(self):
        shutil.rmtree(self.estado / "c_pulados")
        (self.estado / "c_passos").write_text("skipped\nskipped\n")
        r = self.conserto()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("C4: árvore provada na develop (SP4)", r.stdout)

    def test_c4_sem_os_pulados_do_pr_para(self):
        shutil.rmtree(self.estado / "c_pulados")
        self.assert_parou(self.conserto(), "parou no passo 6b (C4): sem os pulados do CI do PR (run 500)")

    def test_c4_teste_que_falhou_pulado_no_pr_para(self):
        for id_ in ("test_b.Caso.test_um", "test_b.Caso.test_um (sub=1)"):
            with self.subTest(id_=id_):
                self.registro.write_text("")
                self.pulados([id_])
                self.assert_parou(self.conserto(), "o teste test_b.Caso.test_um, que falhou no run 44, foi pulado no CI do PR")

    def test_c4_subteste_com_parentese_no_parametro_e_conferido(self):
        self.anotar("b\ttest_b.Caso.test_um (entrada='f()'): AssertionError\nb\ttest_b.Caso.test_0: AssertionError\n")
        self.pulados(["test_b.Caso.test_um (entrada='f()')"])
        self.assert_parou(self.conserto(), "o teste test_b.Caso.test_um, que falhou no run 44, foi pulado no CI do PR")

    def test_c4_teste_pulado_pela_classe_ou_pelo_modulo_para(self):
        for pulado in ("setUpClass (test_b.Caso)", "tearDownClass (test_b.Caso)", "setUpModule (test_b)",
                       "tearDownModule (test_b)", "unittest.loader.ModuleSkipped.test_b"):
            with self.subTest(pulado=pulado):
                self.registro.write_text("")
                self.pulados([pulado])
                self.assert_parou(self.conserto(), "o teste test_b.Caso.test_um, que falhou no run 44, foi pulado no CI do PR")

    def test_c4_pulado_de_outra_classe_ou_modulo_segue(self):
        self.pulados(["setUpClass (test_b.Outra)", "unittest.loader.ModuleSkipped.test_bb", "setUpModule (test_b2)"])
        r = self.conserto()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)

    def test_c4_teste_apagado_no_pr_para(self):
        self.git("switch", "-q", "melhoria/x")
        (self.proj / "tests" / "test_b.py").write_text("class Caso:\n    def test_umdois(self):\n        pass\n")
        self.git("commit", "-q", "-am", "fix: apaga o teste")
        self.git("push", "-q", "origin", "melhoria/x")
        self.git("switch", "-q", "develop")
        self.assert_parou(self.conserto(), "o teste test_b.Caso.test_um, que falhou no run 44, não está em tests/test_b.py no head")

    # ---- C5: o diff tem relação com o vermelho ----
    def sem_teste_tocado(self):
        self.anotar("tests/test_z.py\ttest_z.Caso.test_um: AssertionError\n")

    def test_c5_diff_ilegivel_para(self):
        (self.estado / "c_falha_diff").write_text("...")
        self.assert_parou(self.conserto(), "parou no passo 6b (C5): não consegui ler o diff do PR")

    def test_c5_arquivo_do_modulo_do_teste_conta(self):
        self.anotar(".github\ttest_b2.Caso.test_um: erro\n")
        self.ramo_da_develop("melhoria/y", "tests/test_b2.py", "class Caso:\n    def test_um(self):\n        pass\n")
        r = self.conserto(ref="melhoria/y")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("C5: o PR toca o arquivo de um teste que falhou.", r.stdout)

    def test_c5_arquivo_mudado_desde_o_ultimo_verde_conta(self):
        self.sem_teste_tocado()
        self.develop_anda("c", "3\n")
        self.ramo_da_develop("melhoria/y", "c", "4\n")
        r = self.conserto(ref="melhoria/y")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"C5: o PR toca arquivo mudado entre o último verde ({self.verde[:7]}) e o topo.", r.stdout)

    def test_c5_sem_o_ultimo_verde_antes_do_topo_para(self):
        self.sem_teste_tocado()
        for verde in ("", "b" * 40):
            with self.subTest(verde=verde):
                self.registro.write_text("")
                (self.estado / "c_verde").write_text(verde + "\n")
                self.assert_parou(self.conserto(), "parou no passo 6b (C5): não achei o último push verde da develop antes do topo")

    def test_c5_leitura_do_que_mudou_desde_o_verde_que_falha_para(self):
        self.sem_teste_tocado()
        (self.estado / "c_falha_diff").write_text(f"{self.verde} {self.topo}")
        self.assert_parou(self.conserto(), "parou no passo 6b (C5): não consegui ler o que mudou desde o último verde")

    def test_c5_reversao_de_commit_do_intervalo_conta(self):
        self.sem_teste_tocado()
        self.develop_anda("c", "3\n", msg="feat: c")
        d2 = self.develop_anda("c", None, msg="feat: sem c")
        self.git("switch", "-q", "-c", "melhoria/y", "develop")
        self.git("revert", "--no-edit", d2)
        self.git("push", "-q", "origin", "melhoria/y")
        self.git("switch", "-q", "develop")
        r = self.conserto(ref="melhoria/y")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"C5: o PR reverte o {d2[:7]}, do intervalo vermelho.", r.stdout)

    def test_c5_reversao_de_commit_anterior_ao_verde_nao_conta(self):
        self.sem_teste_tocado()
        self.develop_anda("c", "3\n", msg="feat: c")
        d2 = self.develop_anda("c", None, msg="feat: sem c")
        (self.estado / "c_verde").write_text(d2 + "\n")
        self.develop_anda("d", "5\n")
        self.git("switch", "-q", "-c", "melhoria/y", "develop")
        self.git("revert", "--no-edit", d2)
        self.git("push", "-q", "origin", "melhoria/y")
        self.git("switch", "-q", "develop")
        self.assert_parou(self.conserto(ref="melhoria/y"), "parou no passo 6b (C5): o PR não toca arquivo de teste que falhou")

    def test_c5_diff_sem_relacao_para(self):
        self.sem_teste_tocado()
        self.assert_parou(self.conserto(), "nem reverte commit desse intervalo; nada foi mesclado (D2)")

    # ---- C6 e C7 ----
    def test_c7_historico_que_falha_vira_pendencia(self):
        r = self.conserto(CHECK_ANOTAR_RC="1")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("pendente, rode: forge-check anotar", r.stderr)
        self.assertEqual(len(self.merges()), 1)

    def test_c6_ci_vermelho_no_merge_imprime_o_fechamento_da_reversao_com_conserto(self):
        (self.estado / "runs_0123456789abcdef0123456789abcdef01234567").write_text("92\tcompleted\tcancelled\n93\tcompleted\tfailure\n")
        r = self.conserto()
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("e feche a reversão com: forge-fechar <pedido> --ref melhoria/reverte-0123456 --conserto 93", r.stderr)

    def test_dry_run_mostra_o_conserto_no_6b(self):
        r = self.conserto("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("[6b] conserto do run 44 (C1, C3, C4 e C5) no lugar de:", r.stdout)


if __name__ == "__main__":
    unittest.main()
