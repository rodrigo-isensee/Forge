"""D5b (PA-5): `scripts/promover-homolog.py` prepara e confere a promoção develop -> homolog. Sem rede.

Repositório temporário com remoto local; `gh` é falso (FORGE_GH, só vale com FORGE_PROMOVER_TESTE=1) e registra cada chamada.
"""
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
SCRIPT = RAIZ / "scripts" / "promover-homolog.py"

GH_FALSO = r'''#!/usr/bin/env bash
echo "gh $*" >> "$REGISTRO"
case "$1 $2" in
  "pr list") cat "$ESTADO/aberto" 2>/dev/null; exit 0 ;;
  "pr create") echo "9 homolog" > "$ESTADO/aberto"; exit 0 ;;
  "pr checks") cat "$ESTADO/checks"; exit 0 ;;
  "pr view") cat "$ESTADO/rotulos" 2>/dev/null; exit 0 ;;
esac
exit 64
'''

PARECER = "---\ntipo: review\ncontrato: 1\npedido: {p}\nbranch: melhoria/{p}\ncommit: abc\nparecer: {v}\nrevisor: x\ndata: 2026-10-22\n---\n# R\n"
CHANGELOG = "# Changelog\n\n## [Não publicado]\n{np}\n## [{v}] - 2026-10-22\n- x\n"
MERGE = "gh pr " + "merge"  # montado: o texto do comando não aparece solto no arquivo


class Promover(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="promover-"))
        self.estado = self.tmp / "estado"
        self.estado.mkdir()
        self.registro = self.tmp / "registro"
        self.registro.write_text("")
        (self.tmp / "gh").write_text(GH_FALSO, encoding="utf-8")
        (self.tmp / "gh").chmod(0o755)
        (self.tmp / "gitconfig").write_text("[user]\n\tname = T\n\temail = t@exemplo.test\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "CLAUDE_PROJECT_DIR"}
        env.update(HOME=str(self.tmp), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.tmp / "gitconfig"),
                   FORGE_GH=str(self.tmp / "gh"), FORGE_PROMOVER_TESTE="1", REGISTRO=str(self.registro),
                   ESTADO=str(self.estado))
        self.env = sem_manutencao(env)
        self.remoto, self.proj = self.tmp / "remoto.git", self.tmp / "proj"
        self.git("init", "-q", "--bare", str(self.remoto), cwd=self.tmp)
        remoto_sem_manutencao(self.remoto)
        self.git("clone", "-q", str(self.remoto), str(self.proj), cwd=self.tmp)
        self.escrever(".claude-plugin/plugin.json", json.dumps({"name": "forge", "version": "0.1.0"}))
        self.escrever("CHANGELOG.md", CHANGELOG.format(np="", v="0.1.0"))
        self.git("add", ".")
        self.git("commit", "-q", "-m", "chore: base")
        self.git("branch", "-M", "develop")
        self.git("push", "-q", "origin", "develop")
        self.git("push", "-q", "origin", "develop:homolog")
        self.git("fetch", "-q", "origin")
        (self.estado / "checks").write_text("bateria\tpass\t1m\thttps://x/runs/1/job/2\ncatraca\tpass\t1s\thttps://x/runs/1/job/3\n")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, *args, cwd=None):
        return subprocess.run(["git", *args], cwd=cwd or self.proj, env=self.env, capture_output=True, text=True,
                              check=True).stdout.strip()

    def escrever(self, rel, texto):
        arquivo = self.proj / rel
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(texto, encoding="utf-8")

    def avancar(self, **arquivos):
        """Novo commit na develop, enviado ao remoto (o que a promoção vai levar). `__` vira `/`; o último `_` antes de
        `md` vira `.`."""
        for chave, texto in arquivos.items():
            self.escrever(chave.replace("__", "/").replace("_md", ".md").replace("changelog_d", "changelog.d"), texto)
        self.git("add", ".")
        self.git("commit", "-q", "--allow-empty", "-m", "feat: mudanca")
        self.git("push", "-q", "origin", "develop")
        self.git("fetch", "-q", "origin")

    def pronta(self, **extra):
        """Develop à frente da homolog, com release 0.2.0, parecer aprovado e changelog fechado."""
        self.escrever(".claude-plugin/plugin.json", json.dumps({"name": "forge", "version": "0.2.0"}))
        self.avancar(CHANGELOG_md=CHANGELOG.format(np="", v="0.2.0") + "\n## [0.1.0] - 2026-10-21\n- y\n",
                     docs__reviews__d5b_md=PARECER.format(p="d5b", v="aprovado"), **extra)

    def roda(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.proj, env={**self.env, **(env or {})},
                              capture_output=True, text=True, timeout=60)

    def gh_chamadas(self):
        return self.registro.read_text().splitlines()

    def refs(self):
        return self.git("for-each-ref", "--format=%(refname) %(objectname)")


class DryRun(Promover):
    def test_dry_run_nao_muda_nada_e_nao_chama_gh(self):
        self.pronta()
        antes, status = self.refs(), self.git("status", "--porcelain")
        outro = self.tmp / "outro"
        self.git("clone", "-q", "-b", "develop", str(self.remoto), str(outro), cwd=self.tmp)
        (outro / "z").write_text("1\n")
        self.git("add", "z", cwd=outro)
        self.git("commit", "-q", "-m", "feat: z", cwd=outro)
        self.git("push", "-q", "origin", "develop", cwd=outro)  # só o remoto sabe: o fetch mudaria a ref local
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.refs(), antes)  # nem o fetch rodou
        self.assertEqual(self.git("status", "--porcelain"), status)
        self.assertEqual(self.gh_chamadas(), [])
        self.assertFalse((self.estado / "aberto").exists())
        for trecho in ("--dry-run", "pareceres", "versão", "CHANGELOG", "checks"):
            self.assertIn(trecho, r.stdout)

    def test_dry_run_confere_o_local_e_acusa_parecer_reprovado(self):
        self.pronta()
        self.avancar(docs__qa__d5b_md=PARECER.format(p="d5b", v="reprovado"))
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("docs/qa/d5b.md", r.stdout + r.stderr)
        self.assertEqual(self.gh_chamadas(), [])

    def test_dry_run_nunca_mescla(self):
        self.pronta()
        r = self.roda("--dry-run")
        self.assertNotIn(MERGE, "\n".join(self.gh_chamadas()))
        self.assertIn("não mescla", r.stdout)


class Recusas(Promover):
    def test_recusa_main_como_base_e_branch_fora_do_fluxo(self):
        self.pronta()
        for args in (("--base", "origin/main"), ("--base", "main"), ("--ref", "origin/main"), ("--ref", "melhoria/x")):
            r = self.roda("--dry-run", *args)
            self.assertEqual(r.returncode, 1, args)
            self.assertIn("R-FLUXO", r.stdout + r.stderr)

    def test_nada_a_promover_para(self):
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("nada a promover", r.stdout + r.stderr)

    def test_gh_falso_sem_a_variavel_de_teste_e_ignorado_com_aviso(self):
        self.pronta()
        env = {k: v for k, v in self.env.items() if k != "FORGE_PROMOVER_TESTE"}
        r = subprocess.run([sys.executable, str(SCRIPT), "--dry-run"], cwd=self.proj, env=env, capture_output=True, text=True)
        self.assertIn("FORGE_PROMOVER_TESTE", r.stderr)


class Pareceres(Promover):
    def test_parecer_aprovado_passa(self):
        self.pronta()
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_parecer_sem_frontmatter_ou_sem_valor_para(self):
        self.pronta()
        self.avancar(docs__security__d5b_md="# sem frontmatter\n")
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("docs/security/d5b.md", r.stdout + r.stderr)

    def test_modelo_com_sublinhado_e_ignorado_e_parecer_antigo_nao_conta(self):
        self.escrever("docs/reviews/velho.md", PARECER.format(p="velho", v="reprovado"))
        self.git("add", ".")
        self.git("commit", "-q", "-m", "docs: velho")
        self.git("push", "-q", "origin", "develop", "develop:homolog")  # já está na homolog: fora do intervalo
        self.git("fetch", "-q", "origin")
        self.pronta(docs__reviews___modelo_md=PARECER.format(p="m", v="reprovado"))
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_parecer_reprovado_regravado_como_aprovado_vale_o_da_ref(self):
        self.pronta()
        self.avancar(docs__reviews__d5b_md=PARECER.format(p="d5b", v="reprovado"))
        self.avancar(docs__reviews__d5b_md=PARECER.format(p="d5b", v="aprovado"))
        self.assertEqual(self.roda("--dry-run").returncode, 0)


class Versao(Promover):
    def test_sem_versao_nova_nao_e_release_e_nao_confere_changelog(self):
        self.avancar(docs__reviews__d5b_md=PARECER.format(p="d5b", v="aprovado"),
                     changelog_d__esquecido_md="### Adicionado\n- x\n")  # reprovaria se fosse release
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("não é release", r.stdout)

    def test_versao_menor_que_a_da_homolog_para(self):
        self.escrever(".claude-plugin/plugin.json", json.dumps({"name": "forge", "version": "0.0.9"}))
        self.avancar()
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("versão", r.stdout + r.stderr)

    def test_entrada_da_versao_ausente_no_changelog_para(self):
        self.escrever(".claude-plugin/plugin.json", json.dumps({"name": "forge", "version": "0.2.0"}))
        self.avancar(CHANGELOG_md=CHANGELOG.format(np="", v="0.1.0"))
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("## [0.2.0]", r.stdout + r.stderr)

    def test_nao_publicado_com_conteudo_para(self):
        self.escrever(".claude-plugin/plugin.json", json.dumps({"name": "forge", "version": "0.2.0"}))
        self.avancar(CHANGELOG_md=CHANGELOG.format(np="- sobrou\n", v="0.2.0"))
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Não publicado", r.stdout + r.stderr)

    def test_fragmento_pendente_em_changelog_d_para_mas_readme_nao(self):
        self.pronta(changelog_d__README_md="# pasta\n")
        self.assertEqual(self.roda("--dry-run").returncode, 0)
        self.avancar(changelog_d__novo_md="### Adicionado\n- x\n")
        r = self.roda("--dry-run")
        self.assertEqual(r.returncode, 1)
        self.assertIn("changelog.d/novo.md", r.stdout + r.stderr)


class Execucao(Promover):
    def test_abre_o_pr_para_a_homolog_le_os_checks_e_imprime_o_merge_sem_executar(self):
        self.pronta()
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        chamadas = "\n".join(self.gh_chamadas())
        self.assertIn("pr create --base homolog --head develop", chamadas)
        self.assertNotIn("pr merge", chamadas)
        self.assertNotIn("--force", chamadas)
        sha = self.git("rev-parse", "origin/develop")
        self.assertIn(f"{MERGE} develop --auto --merge --match-head-commit {sha}", r.stdout)
        self.assertIn("check bateria pass run=1 job=2", r.stdout)

    def test_pr_ja_aberto_e_reusado(self):
        self.pronta()
        (self.estado / "aberto").write_text("9 homolog\n")
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("pr create", "\n".join(self.gh_chamadas()))

    def test_pr_aberto_com_base_main_para(self):
        self.pronta()
        (self.estado / "aberto").write_text("9 main\n")
        r = self.roda()
        self.assertEqual(r.returncode, 1)
        self.assertIn("R-MAIN", r.stdout + r.stderr)

    def test_parecer_ruim_para_antes_de_abrir_o_pr(self):
        self.pronta()
        self.avancar(docs__qa__d5b_md=PARECER.format(p="d5b", v="reprovado"))
        r = self.roda()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(self.gh_chamadas(), [])

    def test_check_pendente_sai_3_sem_merge(self):
        self.pronta()
        (self.estado / "checks").write_text("bateria\tpending\t0\turl\n")
        r = self.roda()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertNotIn(MERGE, r.stdout)

    def test_check_vermelho_para(self):
        self.pronta()
        (self.estado / "checks").write_text("bateria\tfail\t1m\turl\n")
        r = self.roda()
        self.assertEqual(r.returncode, 1)
        self.assertNotIn(MERGE, r.stdout)

    def test_catraca_vermelha_sem_rotulo_aguarda_o_dono(self):
        self.pronta()
        (self.estado / "checks").write_text("bateria\tpass\t1m\turl\ncatraca\tfail\t1s\turl\n")
        r = self.roda()
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("afrouxa-regra", r.stdout)
        self.assertNotIn(MERGE, r.stdout)
        self.assertNotIn("pr edit", "\n".join(self.gh_chamadas()))  # nunca aplica o rótulo

    def test_sem_checks_ainda_conta_como_pendente(self):
        self.pronta()
        (self.estado / "checks").write_text("")
        self.assertEqual(self.roda().returncode, 3)

    def test_fetch_traz_a_develop_nova_do_remoto(self):
        self.pronta()
        outro = self.tmp / "outro"
        self.git("clone", "-q", "-b", "develop", str(self.remoto), str(outro), cwd=self.tmp)
        (outro / "z").write_text("1\n")
        self.git("add", "z", cwd=outro)
        self.git("commit", "-q", "-m", "feat: z", cwd=outro)
        self.git("push", "-q", "origin", "develop", cwd=outro)
        r = self.roda()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn(self.git("rev-parse", "origin/develop"), r.stdout)


class Executavel(unittest.TestCase):
    def test_script_e_executavel(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))


if __name__ == "__main__":
    unittest.main()
