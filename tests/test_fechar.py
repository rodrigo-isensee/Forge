"""TA-5: `bin/forge-fechar` (passos mecânicos de fechamento do integrador) em repositório temporário.

`gh` e `forge-check` são falsos (FORGE_GH e FORGE_CHECK); cada chamada vai para um registro, para provar o que rodou.
"""
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
echo "gh $*" >> "$REGISTRO"
case "$1 $2" in
  "pr view")
    case "$*" in
      *number,state*) [ -f "$ESTADO/aberto" ] && cat "$ESTADO/aberto"; exit 0 ;;
      *baseRefName,isDraft*) cat "$ESTADO/pre" 2>/dev/null || echo "develop false"; exit 0 ;;
      *labels*|*title,body*) [ -f "$ESTADO/falha_leitura" ] && exit 1 ;;&
      *labels*) cat "$ESTADO/rotulos" 2>/dev/null; exit 0 ;;
      *title,body*) cat "$ESTADO/texto" 2>/dev/null; exit 0 ;;
      *state*) cat "$ESTADO/estado" 2>/dev/null || echo OPEN; exit 0 ;;
    esac ;;
  "pr create") echo "7 develop" > "$ESTADO/aberto"; exit 0 ;;
  "pr ready") exit 0 ;;
  "pr checks")
    if [ -f "$ESTADO/sem_checks_ate" ] && [ "$(wc -l < "$REGISTRO")" -lt "$(cat "$ESTADO/sem_checks_ate")" ]; then
      echo "no checks reported on the 'melhoria/x' branch"; exit 1
    fi
    cat "$ESTADO/checks"; exit 0 ;;
  "pr merge")
    # como o GitHub: recusa se o head do PR (arquivo "head", quando existe) não é o do --match-head-commit
    if [ -f "$ESTADO/head" ]; then
      [[ "$*" == *"--match-head-commit $(cat "$ESTADO/head")"* ]] || exit 1
    fi
    [[ "$*" == *--match-head-commit* ]] || exit 1
    echo MERGED > "$ESTADO/estado"; exit 0 ;;
esac
exit 64
'''
CHECK_FALSO = '#!/usr/bin/env bash\necho "forge-check $*" >> "$REGISTRO"\nexit "${CHECK_RC:-0}"\n'


class Fechar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fechar-"))
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
                        FORGE_FECHAR_TESTE="1")
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
        (self.estado / "checks").write_text("bateria\tpass\t1m\turl\n")

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
        self.assertEqual(chamadas[0], "forge-check pr p1 --ref melhoria/x --base origin/develop")
        self.assertTrue(any(c.startswith("gh pr create --base develop --head melhoria/x") for c in chamadas))
        self.assertIn(f"gh pr merge melhoria/x --squash --match-head-commit {sha}", chamadas)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))
        self.assertEqual(self.git("branch", "--list", "melhoria/x"), "")
        corpo = self.registro.read_text()
        self.assertIn("## Projeto de origem\nForge", corpo)
        self.assertIn("## Como medir\nVer", corpo)

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
        self.assertEqual(self.chamadas(), ["forge-check pr p1 --ref melhoria/x --base origin/develop"])

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

    def test_recusa_quando_rotulo_pedido_e_nao_aplicado(self):
        (self.estado / "texto").write_text("feat: x (afrouxa-regra)\ncorpo\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        chamadas = self.chamadas()
        self.assertFalse(any("pr merge" in c or "pr edit" in c or "--add-label" in c for c in chamadas))

    def test_rotulo_pedido_e_aplicado_pelo_dono_segue(self):
        (self.estado / "texto").write_text("feat: x (afrouxa-regra)\ncorpo\n")
        (self.estado / "rotulos").write_text("afrouxa-regra\n")
        self.assertEqual(self.fechar("p1", "--ref", "melhoria/x").returncode, 0)

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

    def test_limpeza_apaga_a_branch_remota_por_refs_heads(self):
        self.assertIn('push origin --delete "refs/heads/$ref"', SCRIPT.read_text())

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


if __name__ == "__main__":
    unittest.main()
