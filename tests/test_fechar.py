"""TA-5: `bin/forge-fechar` (passos mecânicos de fechamento do integrador) em repositório temporário.

`gh` e `forge-check` são falsos (FORGE_GH e FORGE_CHECK); cada chamada vai para um registro, para provar o que rodou.
"""
import importlib.util
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
    falha_n falha_lista && { echo "HTTP 502" >&2; exit 1; }
    [ -f "$ESTADO/aberto" ] && awk '{print $1 " OPEN " $2 " -"}' "$ESTADO/aberto"
    cat "$ESTADO/lista_extra" 2>/dev/null; exit 0 ;;
  "pr view")
    case "$*" in
      *number,state*) [ -f "$ESTADO/aberto" ] && cat "$ESTADO/aberto"; exit 0 ;;
      *baseRefName,isDraft*) echo "$(cat "$ESTADO/pre" 2>/dev/null || echo "develop false") $(cat "$ESTADO/estado" 2>/dev/null || echo OPEN)"; exit 0 ;;
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
  "pr create") echo "7 develop" > "$ESTADO/aberto"; exit 0 ;;
  "pr ready") exit 0 ;;
  "pr checks")
    if [ -f "$ESTADO/sem_checks_ate" ] && [ "$(wc -l < "$REGISTRO")" -lt "$(cat "$ESTADO/sem_checks_ate")" ]; then
      echo "no checks reported on the 'melhoria/x' branch"; exit 1
    fi
    falha_n falha_checks && { echo "HTTP 502"; exit 1; }
    cat "$ESTADO/checks"; exit 0 ;;
  "pr merge")
    [ -f "$ESTADO/merge_502" ] && exit 1
    [ -f "$ESTADO/merge_502_mas_mescla" ] && { echo MERGED > "$ESTADO/estado"; exit 1; }
    # como o GitHub: recusa se o head do PR (arquivo "head", quando existe) não é o do --match-head-commit
    if [ -f "$ESTADO/head" ]; then
      [[ "$*" == *"--match-head-commit $(cat "$ESTADO/head")"* ]] || exit 1
    fi
    [[ "$*" == *--match-head-commit* ]] || exit 1
    echo MERGED > "$ESTADO/estado"; exit 0 ;;
esac
exit 64
'''
# git falso: o `push --delete` falha as primeiras N vezes (N em $ESTADO/falha_delete) e depois chama o git real
GIT_FALSO = r'''#!/usr/bin/env bash
if [ "$1 $2" = "push origin" ] && [ "$3" = "--delete" ]; then
  echo "git $*" >> "$REGISTRO"
  n="$(cat "$ESTADO/falha_delete" 2>/dev/null || echo 0)"
  if [ "$n" -gt 0 ]; then echo $((n - 1)) > "$ESTADO/falha_delete"; echo "HTTP 502" >&2; exit 1; fi
fi
exec "$REAL_GIT_FALSO" "$@"
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
                        FORGE_FECHAR_TESTE="1", FORGE_FECHAR_LOG_DIR=str(self.tmp / "logs"))
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

    ITEM_MARCADO = "feat: x\n## Checklist\n- [x] Rótulo `afrouxa-regra` pedido ao dono (afrouxa regra, motivo no corpo)\n"

    def test_recusa_quando_item_do_rotulo_marcado_e_rotulo_nao_aplicado(self):
        (self.estado / "texto").write_text(self.ITEM_MARCADO)
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("passo 5", r.stderr)
        chamadas = self.chamadas()
        self.assertFalse(any("pr merge" in c or "pr edit" in c or "--add-label" in c for c in chamadas))

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
            (self.estado / "checks_apos_rotulo").write_text("bateria\tpass\t1m\turl\ncatraca\tpass\t5s\turl\n")

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
        self.assertEqual(r.returncode, 0, r.stderr)
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
        self.assertIn("Entrega p1 fechada em develop.", linhas[-1])
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


if __name__ == "__main__":
    unittest.main()
