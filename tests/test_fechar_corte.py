"""v0478 E174.4 (CORTE-PELO-CONTADOR, D4 do estudo determinístico): `forge-fechar --corte` lê as versões da develop, da homolog e da main,
promove a marca mesclada pelo --promover, abre o PR homolog -> main e, com o contador da develop no teto, grava a marca e abre o PR dela em
rascunho. O --laco que termina com 0 roda o --corte no fim.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário com remoto bare e `git` falso) com `gh` e item falsos próprios; o
`forge-contador` e o `forge-changelog` são os de verdade, ao lado do script.
"""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# gh falso: `pr list` devolve $ESTADO/pr_main (o número do PR homolog -> main aberto; sem o arquivo, nenhum) ou falha com $ESTADO/lista_falha;
# `pr create` devolve o endereço do PR ou falha com $ESTADO/create_falha. Os rótulos da promoção mesclada (`pr list --head promocao/...`)
# vêm de $ESTADO/rotulos, um nome por linha (o --jq não roda aqui; o nome exato é conferido no script); `pr edit` falha com $ESTADO/edit_falha.
GH_CORTE = r'''#!/usr/bin/env bash
echo "gh $*" >> "$REGISTRO"
case "$1 $2" in
  "pr list") [ -f "$ESTADO/lista_falha" ] && exit 1
    case "$*" in *"--head promocao/"*" --state merged "*) [ -f "$ESTADO/rotulos_falha" ] && exit 1; cat "$ESTADO/rotulos" 2>/dev/null; exit 0 ;; esac
    cat "$ESTADO/pr_main" 2>/dev/null; exit 0 ;;
  "pr create") [ -f "$ESTADO/create_falha" ] && exit 1; echo "https://github.com/o/r/pull/77" ;;
  "pr edit") [ -f "$ESTADO/edit_falha" ] && exit 1; exit 0 ;;
  *) exit 64 ;;
esac
'''
# Item falso (o --promover e o --corte que o laço chama): anota os argumentos e sai com $ESTADO/rc_item (padrão 0).
ITEM_CORTE = r'''#!/usr/bin/env bash
echo "item $*" >> "$REGISTRO"
exit "$(cat "$ESTADO/rc_item" 2>/dev/null || echo 0)"
'''
# git na frente do falso da base: a busca da marca na develop falha com $ESTADO/log_falha e o --numstat do forge-check (git -C <raiz>
# diff --numstat) com $ESTADO/numstat_falha; o
# `git <sub>` que cita o ramo da marca falha com $ESTADO/falha_marca_<sub>. A variável sem o prefixo GIT_: o forge-check tira as GIT_* do ambiente do git.
GIT_LOG = r'''#!/usr/bin/env bash
if [ -f "$ESTADO/log_falha" ] && [ "$1 $2" = "log -1" ]; then exit 128; fi
if [ -f "$ESTADO/numstat_falha" ] && [ "$1 $3 $4" = "-C diff --numstat" ]; then exit 128; fi
if [ -f "$ESTADO/falha_marca_$1" ]; then case "$*" in *marca-*) exit 128 ;; esac; fi
exec "$FALSO_GIT_DA_BASE" "$@"
'''
CHANGELOG = "# Changelog\n\n## [Não publicado]\n\n## [0.9.0] - 2026-01-01\n### Adicionado\n- inicio\n"
MARCA = "melhoria/marca-0.9.1"


class Corte(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    def setUp(self):
        base.Fechar.setUp(self)
        for nome, texto in (("gh", GH_CORTE), ("item", ITEM_CORTE), ("bin2/git", GIT_LOG)):
            (self.tmp / nome).parent.mkdir(exist_ok=True)
            (self.tmp / nome).write_text(texto, encoding="utf-8")
            (self.tmp / nome).chmod(0o755)
        self.env.update(FORGE_FECHAR_ITEM=str(self.tmp / "item"), FALSO_GIT_DA_BASE=str(self.tmp / "bin" / "git"),
                        PATH=f"{self.tmp / 'bin2'}:{self.env['PATH']}")
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge" / "config.json").write_text('{"teto_versao": 2}\n')  # fora do git (não versionado): o teto do contador
        (self.proj / "CHANGELOG.md").write_text(CHANGELOG)
        (self.proj / "changelog.d").mkdir()
        (self.proj / "changelog.d" / "README.md").write_text("fragmentos\n")
        self.versao("0.9.0", "chore: versão 0.9.0")
        for destino in ("homolog", "main"):
            self.git("push", "-q", "origin", f"develop:{destino}")

    def versao(self, v, msg):
        (self.proj / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "forge", "version": v}, indent=2) + "\n")
        self.git("add", "-A", ".claude-plugin", "CHANGELOG.md", "changelog.d")
        self.git("commit", "-q", "-m", msg)
        self.git("push", "-q", "origin", "develop")
        return self.git("rev-parse", "HEAD")

    def fragmentos(self, n):
        for i in range(n):
            (self.proj / "changelog.d" / f"item-{i}.md").write_text(f"### Adicionado\n- item {i}\n")
        self.git("add", "changelog.d")
        self.git("commit", "-q", "-m", f"feat: {n} itens")
        self.git("push", "-q", "origin", "develop")

    def gh(self, prefixo):
        return [c for c in self.chamadas() if c.startswith(prefixo)]

    def no_origin(self, ramo):
        return self.git("ls-remote", "origin", f"refs/heads/{ramo}")

    def sem_merge(self):  # R-MAIN: o --corte só abre PR; nenhum caminho dele chama `pr merge` nem `--auto`
        self.assertEqual([c for c in self.chamadas() if "pr merge" in c or "--auto" in c], [])

    def test_abaixo_do_teto_nada_faz(self):
        self.fragmentos(1)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("contador: 0.9.1: 1 de 2", r.stdout)
        self.assertIn("corte: a 0.9.1 ainda não fecha.", r.stdout)
        self.assertEqual(self.gh("gh pr create"), [])
        self.assertEqual(self.no_origin(MARCA), "")

    def test_no_teto_grava_a_marca_e_abre_o_pr_em_rascunho(self):
        self.fragmentos(2)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("PR da marca em rascunho: https://github.com/o/r/pull/77", r.stdout)
        criar = self.gh("gh pr create")
        self.assertEqual(len(criar), 1)
        self.assertTrue(criar[0].startswith(f"gh pr create --draft --base develop --head {MARCA} --title chore(release): marca da 0.9.1 na develop"))
        self.assertIn("## Projeto de origem", self.registro.read_text())
        self.assertNotEqual(self.no_origin(MARCA), "")
        self.git("fetch", "-q", "origin", MARCA)
        self.assertEqual(json.loads(self.git("show", "FETCH_HEAD:.claude-plugin/plugin.json"))["version"], "0.9.1")
        self.assertIn("## [0.9.1] - ", self.git("show", "FETCH_HEAD:CHANGELOG.md"))
        self.assertEqual(self.git("ls-tree", "--name-only", "FETCH_HEAD", "changelog.d/"), "changelog.d/README.md")
        self.assertEqual(self.git("log", "-1", "--format=%s", "FETCH_HEAD"), "chore(release): marca da 0.9.1 na develop")
        self.assertEqual(self.git("rev-parse", "FETCH_HEAD^"), self.git("rev-parse", "origin/develop"))
        self.assertEqual(len(self.git("worktree", "list").splitlines()), 1)  # a worktree da marca saiu
        self.assertEqual(self.gh("item"), [])

    def test_ramo_da_marca_ja_no_origin_nada_faz(self):
        self.fragmentos(2)
        self.git("push", "-q", "origin", f"develop:{MARCA}")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"corte: {MARCA} já existe no origin", r.stdout)
        self.assertEqual(self.gh("gh pr create"), [])

    def test_marca_que_nao_grava_para_sem_pr(self):
        (self.proj / "CHANGELOG.md").write_text("# Changelog\n")  # sem [Não publicado]: o forge-changelog release recusa
        self.versao("0.9.0", "docs: changelog sem a seção")
        self.fragmentos(2)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V5: a marca da 0.9.1 não foi gravada nem enviada", r.stderr)
        self.assertEqual(self.gh("gh pr create"), [])
        self.assertEqual(self.no_origin(MARCA), "")

    def test_pr_da_marca_que_nao_abre_para(self):
        self.fragmentos(2)
        (self.estado / "create_falha").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(f"parou no passo V5: {MARCA} foi enviado, mas o PR não foi aberto", r.stderr)

    def test_marca_mesclada_promove_e_abre_o_pr_da_main(self):
        for rc in ("0", "3"):  # 3: promovida com o ramo de promoção não apagado
            with self.subTest(rc=rc):
                self.registro.write_text("")
                (self.estado / "rc_item").write_text(rc)
                if rc == "0":
                    self.marca = self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
                    (self.proj / "a").write_text("depois da marca\n")
                    self.git("commit", "-q", "-am", "feat: depois da marca")
                    self.git("push", "-q", "origin", "develop")
                r = self.fechar("--corte")
                self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
                self.assertEqual(self.gh("item"), [f"item release-0.9.1 --promover {self.marca} --espera 1800 --espera-ci 3600"])
                self.assertEqual(len(self.gh("gh pr create --base main --head homolog --title release 0.9.1 ")), 1)
                self.assertIn("contador: 0.9.2: 0 de 2", r.stdout)
                self.sem_merge()

    def test_promocao_que_para_sai_com_o_codigo_dela(self):
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        for rc in (1, 5):
            with self.subTest(rc=rc):
                (self.estado / "rc_item").write_text(str(rc))
                r = self.fechar("--corte")
                self.assertEqual(r.returncode, rc, r.stderr + r.stdout)
                self.assertIn(f"corte: a promoção da 0.9.1 parou com código {rc}", r.stderr)
                self.assertEqual(self.gh("gh pr create"), [])

    def test_pr_da_main_aberto_espera_o_dono(self):
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        (self.estado / "pr_main").write_text("62\n")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("corte: a marca da 0.9.1 espera o dono mesclar o PR #62 da main", r.stdout)
        self.assertEqual(self.gh("item"), [])
        self.assertEqual(self.gh("gh pr create"), [])

    def test_homolog_promovida_abre_so_o_pr_da_main_e_uma_vez(self):
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        self.git("push", "-q", "origin", "develop:homolog")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.gh("item"), [])
        self.assertEqual(len(self.gh("gh pr create --base main --head homolog --title release 0.9.1 ")), 1)
        self.registro.write_text("")
        (self.estado / "pr_main").write_text("62\n")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.gh("gh pr create"), [])
        self.assertIn("PR #62 homolog -> main aberto", r.stdout)
        self.sem_merge()

    def test_pr_da_main_que_nao_abre_para(self):
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        self.git("push", "-q", "origin", "develop:homolog")
        (self.estado / "create_falha").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V3: não abri o PR homolog -> main da 0.9.1", r.stderr)

    def test_homolog_a_frente_da_develop_para(self):
        self.git("switch", "-q", "-c", "outra")
        (self.proj / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "forge", "version": "0.9.2"}, indent=2) + "\n")
        self.git("commit", "-q", "-am", "chore: 0.9.2 só na homolog")
        self.git("push", "-q", "origin", "outra:homolog")
        self.git("switch", "-q", "develop")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V1: a homolog (0.9.2) está à frente da develop (0.9.0)", r.stderr)
        self.assertEqual(self.gh("item"), [])

    def test_main_a_frente_da_homolog_para(self):  # v0478 E174.26 (QA A1, segurança A2): não abre PR de versão velha para a main
        self.git("push", "-q", "origin", "develop:homolog")
        self.git("switch", "-q", "-c", "outra")
        (self.proj / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "forge", "version": "0.9.1"}, indent=2) + "\n")
        self.git("commit", "-q", "-am", "chore: 0.9.1 só na main")
        self.git("push", "-q", "origin", "outra:main")
        self.git("switch", "-q", "develop")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V1: a main (0.9.1) está à frente da homolog (0.9.0)", r.stderr)
        self.assertEqual(self.gh("item"), [])
        self.assertEqual(self.gh("gh pr create"), [])

    def test_leituras_que_falham_param(self):
        casos = (("lista_falha", "parou no passo V1: não li o PR homolog -> main"),
                 ("log_falha", "parou no passo V2: não achei o commit da marca da 0.9.1"))
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        for arquivo, msg in casos:
            with self.subTest(arquivo=arquivo):
                (self.estado / arquivo).write_text("")
                r = self.fechar("--corte")
                (self.estado / arquivo).unlink()
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(msg, r.stderr)
                self.assertEqual(self.gh("item"), [])

    def test_versao_ilegivel_ou_ramo_ausente_param(self):
        (self.proj / ".claude-plugin" / "plugin.json").write_text('{"name": "forge"}\n')
        self.git("commit", "-q", "-am", "chore: sem versão")
        self.git("push", "-q", "origin", "develop:homolog")  # o plugin.json sem a versão
        self.git("rm", "-q", ".claude-plugin/plugin.json")
        self.git("commit", "-q", "-m", "chore: sem plugin.json")
        self.git("push", "-q", "origin", "develop:main")  # sem o plugin.json: a leitura falha e a versão sai vazia
        self.git("reset", "-q", "--hard", "origin/develop")  # a cópia volta a ter o plugin.json do Forge
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V1: versão X.Y.Z ilegível no plugin.json (develop '0.9.0', homolog '', main ''", r.stderr)
        self.git("push", "-q", "origin", "--delete", "main")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V1: não busquei develop, homolog e main do origin", r.stderr)

    def test_contador_que_falha_ou_sem_contagem(self):
        (self.proj / ".forge" / "config.json").write_text('{"teto_versao": "x"}\n')
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V4: o forge-contador falhou", r.stderr)
        (self.proj / ".forge" / "config.json").write_text('{"teto_versao": 2}\n')
        self.git("rm", "-q", "-r", "changelog.d")
        self.git("commit", "-q", "-m", "chore: sem fragmentos")
        self.git("push", "-q", "origin", "develop")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("corte: sem contagem legível; nada a cortar.", r.stdout)
        self.assertEqual(self.gh("gh pr create"), [])

    def test_dry_run_le_e_nao_age(self):
        self.fragmentos(2)
        r = self.fechar("--corte", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"rodaria: forge-changelog release 0.9.1 <hoje> sobre a origin/develop, commit, git push origin HEAD:refs/heads/{MARCA}", r.stdout)
        self.assertEqual(self.no_origin(MARCA), "")
        marca = self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        r = self.fechar("--corte", "--dry-run")
        self.assertIn(f"rodaria: forge-fechar release-0.9.1 --promover {marca}", r.stdout)
        self.git("push", "-q", "origin", "develop:homolog")
        r = self.fechar("--corte", "--dry-run")
        self.assertIn("rodaria: ", r.stdout)
        self.assertIn("pr create --base main --head homolog --title 'release 0.9.1'", r.stdout)
        self.assertEqual(self.gh("item"), [])
        self.assertEqual(self.gh("gh pr create"), [])

    def test_recusa_o_que_nao_e_do_corte(self):
        for extra in (["p1"], ["--ref", "melhoria/a"], ["--laco"], ["--limpar"], ["--promover", "a" * 40]):
            with self.subTest(extra=extra):
                r = self.fechar("--corte", *extra)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("--corte recebe só --base, --espera, --espera-ci ou --dry-run", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_sem_corte_o_fluxo_do_item_segue(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertNotIn("[V1]", r.stdout)

    # v0481 E13.15 (CORTE-MARCA-PRONTA): a marca já nasce pronta para a promoção.
    def corpo_criado(self):
        texto = self.registro.read_text()
        return texto[texto.index("gh pr create --draft"):]

    def codigo(self, linhas):
        (self.proj / "ferramenta.py").write_text("x = 1\n" * linhas)  # código entre a main e a marca, que o 1c mede (H1)
        self.git("add", "ferramenta.py")
        self.git("commit", "-q", "-m", "feat: ferramenta")

    def novo_fragmento(self):
        (self.proj / "changelog.d" / "novo.md").write_text("### Corrigido\n- novo depois do corte\n")
        self.git("add", "changelog.d")
        self.git("commit", "-q", "-m", "fix: novo")
        self.git("push", "-q", "origin", "develop")

    def test_marca_nasce_com_o_teto_os_pareceres_release_e_a_classe(self):
        self.codigo(151)
        self.fragmentos(2)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        corpo = self.corpo_criado()
        self.assertIn("\nteto: excedido, 151 linhas, marca de versão\n", corpo)
        for parecer in ("reviews/release-0.9.1.md (review)", "qa/release-0.9.1.md (QA)", "security/release-0.9.1.md (segurança)"):
            self.assertIn(f"\n- docs/{parecer}\n", corpo)
        self.assertIn("classe do PR da marca: C; a promoção exige os pareceres release-0.9.1", r.stdout)
        self.assertIn("Classe do PR: C.", corpo)

    def test_marca_no_teto_sai_sem_a_linha_de_teto(self):
        self.codigo(150)
        self.fragmentos(2)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("teto: excedido", self.corpo_criado())
        self.assertIn("\n- docs/qa/release-0.9.1.md (QA)\n", self.corpo_criado())

    def test_marca_que_nao_mede_nao_envia(self):
        self.fragmentos(2)
        (self.estado / "numstat_falha").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V5: a marca da 0.9.1 não foi gravada nem enviada (ou não foi medida)", r.stderr)
        self.assertEqual(self.no_origin(MARCA), "")
        self.assertEqual(self.gh("gh pr create"), [])

    def test_data_da_secao_e_o_dia_local(self):
        real = subprocess.run(["sh", "-c", "command -v date"], capture_output=True, text=True, check=True).stdout.strip()
        falso = self.tmp / "bin2" / "date"  # o dia local e o UTC diferentes: só o local pode entrar na seção
        falso.write_text(f'#!/usr/bin/env bash\ncase "$*" in "+%F") echo 2031-02-03 ;; "-u +%F") echo 2031-02-04 ;; *) exec {real} "$@" ;; esac\n')
        falso.chmod(0o755)
        self.fragmentos(2)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.git("fetch", "-q", "origin", MARCA)
        self.assertIn("## [0.9.1] - 2031-02-03\n", self.git("show", "FETCH_HEAD:CHANGELOG.md"))

    def test_fragmento_depois_do_corte_entra_na_secao_da_versao(self):
        self.fragmentos(2)
        self.assertEqual(self.fechar("--corte").returncode, 0)
        self.novo_fragmento()
        self.registro.write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("aviso: a develop recebeu fragmento depois do corte da 0.9.1, que ficaria fora da seção: changelog.d/novo.md;", r.stderr)
        self.git("fetch", "-q", "origin", MARCA)
        secao = self.git("show", "FETCH_HEAD:CHANGELOG.md").split("## [0.9.1]")[1].split("## [0.9.0]")[0]
        self.assertIn("- novo depois do corte", secao)
        self.assertEqual(self.git("ls-tree", "--name-only", "FETCH_HEAD", "changelog.d/"), "changelog.d/README.md")
        self.assertEqual(self.git("merge-base", "FETCH_HEAD", "origin/develop"), self.git("rev-parse", "origin/develop"))
        self.assertEqual(len(self.gh(f"gh pr edit {MARCA} --body ## Projeto de origem")), 1)
        self.assertEqual(self.gh("gh pr create"), [])
        self.assertEqual(len(self.git("worktree", "list").splitlines()), 1)  # a worktree do anexar saiu
        self.registro.write_text("")  # de novo: nada novo, nada feito
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("aviso: a develop recebeu fragmento", r.stderr)
        self.assertEqual(self.gh("gh pr edit"), [])

    def test_anexar_que_falha_para_sem_enviar(self):
        self.fragmentos(2)
        self.git("push", "-q", "origin", f"develop:{MARCA}")  # ramo sem a seção da 0.9.1: o --anexar recusa
        self.novo_fragmento()
        antes = self.no_origin(MARCA)
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo V5: o fragmento novo não entrou na marca da 0.9.1", r.stderr)
        self.assertEqual(self.no_origin(MARCA), antes)
        self.assertEqual(self.gh("gh pr edit"), [])

    def test_leituras_do_ramo_da_marca_que_falham_param(self):
        self.fragmentos(2)
        self.assertEqual(self.fechar("--corte").returncode, 0)
        self.novo_fragmento()
        for falha, msg in (("fetch", f"não busquei {MARCA}"), ("merge-base", f"sem base comum entre a develop e {MARCA}")):
            with self.subTest(falha=falha):
                (self.estado / f"falha_marca_{falha}").write_text("")
                r = self.fechar("--corte")
                (self.estado / f"falha_marca_{falha}").unlink()
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(f"parou no passo V5: {msg} (nada foi anexado)", r.stderr)
                self.assertEqual(self.gh("gh pr edit"), [])

    def test_corpo_que_nao_refaz_para(self):
        self.fragmentos(2)
        self.assertEqual(self.fechar("--corte").returncode, 0)
        self.novo_fragmento()
        (self.estado / "edit_falha").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn(f"parou no passo V5: o fragmento entrou em {MARCA}, mas o corpo do PR não foi refeito", r.stderr)
        self.assertIn("ajuste o corpo à mão com a medida em ", r.stderr)

    def test_leitura_do_origin_que_falha_nao_anexa(self):  # v0481 E13.19 (review A2): ls-remote em erro sai em 0, sem tocar o ramo
        self.fragmentos(2)
        self.assertEqual(self.fechar("--corte").returncode, 0)
        self.novo_fragmento()
        antes = self.no_origin(MARCA)
        self.registro.write_text("")
        (self.estado / "falha_marca_ls-remote").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"corte: {MARCA} já existe no origin (ou a leitura falhou)", r.stdout)
        self.assertNotIn("aviso: a develop recebeu fragmento", r.stderr)
        (self.estado / "falha_marca_ls-remote").unlink()  # o falso vale para o git do teste também
        self.assertEqual(self.no_origin(MARCA), antes)
        self.assertEqual(self.gh("gh pr edit"), [])
        self.assertEqual(self.gh("gh pr create"), [])

    def test_dry_run_so_avisa_o_fragmento_novo(self):
        self.fragmentos(2)
        self.assertEqual(self.fechar("--corte").returncode, 0)
        antes = self.no_origin(MARCA)
        self.novo_fragmento()
        r = self.fechar("--corte", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"rodaria: merge da origin/develop em {MARCA}, forge-changelog release --anexar 0.9.1", r.stdout)
        self.assertEqual(self.no_origin(MARCA), antes)

    def test_promocao_com_afrouxa_regra_pede_o_rotulo_na_main(self):
        self.versao("0.9.1", "chore(release): marca da 0.9.1 na develop")
        self.git("push", "-q", "origin", "develop:homolog")
        linha = ("rótulo: a promoção da 0.9.1 levou afrouxa-regra; o PR da main vai pedir o mesmo rótulo ao dono, que o aplica no PR: "
                 "gh pr view https://github.com/o/r/pull/77 --web")
        for rotulos, pede in (("outro\nafrouxa-regra\n", True), ("afrouxa-regra-nao\nnao-afrouxa-regra\n", False), ("", False)):
            with self.subTest(rotulos=rotulos):
                (self.estado / "rotulos").write_text(rotulos)
                r = self.fechar("--corte")
                self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
                self.assertEqual(linha in r.stdout, pede, r.stdout)
        self.assertEqual(self.gh("gh pr edit"), [])  # o rótulo é do dono: o script só imprime o comando
        (self.estado / "rotulos_falha").write_text("")
        r = self.fechar("--corte")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("aviso: não li os rótulos da promoção da 0.9.1; confira se o PR da main pede afrouxa-regra.", r.stderr)
        self.assertIn("[V4]", r.stdout)


# AUTORIZACOES-FIXAS (v0481 E14.52): a corte-diario gravada como o forge-check a grava, lida pelo forge-check de verdade.
FALA_FIXA = "autorizo o corte diario fixo"
GRAVADOR = hashlib.sha256((base.RAIZ / "bin" / "forge-check").read_bytes()).hexdigest()
CHECK_REAL = f'#!/usr/bin/env bash\nexec python3 -I "{base.RAIZ / "bin" / "forge-check"}" "$@"\n'
AS_06, AS_0559, AS_07_DO_DIA_DA_0_9_0 = "1795586400", "1795586340", "1767250800"  # 25/11 06:00 e 05:59, 01/01 07:00 (UTC)


def corte_diario(**troca):
    campos = {"Id": "A-1", "Ato": "corte-diario", "Alvos": "fixo", "Validade": "fixa", "Validade-utc": "fixa", "Fuso": "UTC",
              "Origem-da-validade": "sem prazo", "Estado-inicial": "ativa", "Motivo-da-pendencia": "nenhum", "Mensagem": "u-1",
              "Hora-da-fala": "2026-11-18T00:00:00Z", "Sessao": "s-1", "Pedido": "v0481",
              "Sha256": hashlib.sha256(FALA_FIXA.encode()).hexdigest(), "Gravado-por": GRAVADOR,
              "Autoriza": "só o ato e os alvos acima, até a validade; não amplia outra regra (R-DECISAO)", **troca}
    return "".join(f"{k}: {v}\n" for k, v in campos.items()) + "\n" + FALA_FIXA


class CorteDiario(unittest.TestCase):
    """F3 da emenda AUTORIZACOES-FIXAS: abaixo do teto, o --corte corta a partir das 06:00 locais, uma vez por dia, com item e só com
    a corte-diario ativa, gravada no corpo do PR da marca; faltando qualquer um, nada muda."""
    tearDown, git, fechar, chamadas = base.Fechar.tearDown, base.Fechar.git, base.Fechar.fechar, base.Fechar.chamadas
    versao, fragmentos, gh, no_origin, sem_merge = Corte.versao, Corte.fragmentos, Corte.gh, Corte.no_origin, Corte.sem_merge

    def setUp(self):
        Corte.setUp(self)
        (self.tmp / "check_real").write_text(CHECK_REAL, encoding="utf-8")
        (self.tmp / "check_real").chmod(0o755)
        (self.proj / ".forge" / "autorizacoes").mkdir(mode=0o700)
        (self.proj / ".forge" / "autorizacoes" / "A-1").write_text(corte_diario(), encoding="utf-8")

    def cortar(self, agora=AS_06, check=None):
        return self.fechar("--corte", FORGE_FECHAR_AGORA=agora, TZ="UTC", FORGE_CHECK=check or str(self.tmp / "check_real"))

    def nao_corta(self, r, motivo):
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("corte: a 0.9.1 ainda não fecha.", r.stdout)
        self.assertIn(motivo, r.stderr)
        self.assertEqual(self.gh("gh pr create"), [])
        self.assertEqual(self.no_origin(MARCA), "")

    def test_abaixo_do_teto_as_06h_corta_e_grava_a_autorizacao_no_corpo(self):
        self.fragmentos(1)
        r = self.cortar()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        usada = f"A-1 sha256 {hashlib.sha256(FALA_FIXA.encode()).hexdigest()} · corte-diario · fixo"
        self.assertIn(f"corte diário abaixo do teto, pela autorização {usada}", r.stdout)
        self.assertEqual(len(self.gh("gh pr create --draft --base develop --head melhoria/marca-0.9.1 ")), 1)
        self.assertIn(f"## Autorização usada (corte diário abaixo do teto, emenda AUTORIZACOES-FIXAS da ADR 0018)\n{usada}\n",
                      self.registro.read_text())
        self.assertNotEqual(self.no_origin(MARCA), "")
        self.sem_merge()

    def test_no_teto_o_corpo_nao_cita_autorizacao(self):
        self.fragmentos(2)
        r = self.cortar(check=str(self.tmp / "check"))  # o falso anota a chamada: no teto, o forge-check nem é lido
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertNotIn("## Autorização usada", self.registro.read_text())
        self.assertEqual([c for c in self.chamadas() if c.startswith("forge-check")], [])

    def test_sem_item_nao_corta(self):
        self.nao_corta(self.cortar(), "corte: nenhum item na develop para o corte diário.")

    def test_antes_das_06h_relogio_ilegivel_ou_versao_de_hoje_nao_corta(self):
        self.fragmentos(1)
        for agora, motivo in ((AS_0559, "só sai a partir das 06:00 locais (agora 0559)"), ("x", "corte: relógio ilegível."),
                              (AS_07_DO_DIA_DA_0_9_0, "a develop já tem versão de hoje (2026-01-01)")):
            with self.subTest(agora=agora):
                self.nao_corta(self.cortar(agora), motivo)

    def test_sem_corte_diario_ativa_ou_saida_fora_da_forma_nao_corta(self):
        self.fragmentos(1)
        self.nao_corta(self.cortar(check=str(self.tmp / "check")), "corte: autorização corte-diario fora da forma.")
        (self.proj / ".forge" / "autorizacoes" / "A-1").write_text(corte_diario(Ato="merge-main"), encoding="utf-8")
        self.nao_corta(self.cortar(), "corte: autorizacao: nenhuma corte-diario ativa")
        (self.proj / ".forge" / "autorizacoes" / "A-1").unlink()
        self.nao_corta(self.cortar(), "corte: autorizacao: nenhuma corte-diario ativa")

    def test_changelog_ilegivel_na_develop_nao_corta(self):
        self.fragmentos(1)
        self.git("rm", "-q", "CHANGELOG.md")
        self.git("commit", "-q", "-m", "sem changelog")
        self.git("push", "-q", "origin", "develop")
        self.nao_corta(self.cortar(), "ou o CHANGELOG.md não foi lido")


if __name__ == "__main__":
    unittest.main()
