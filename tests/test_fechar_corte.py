"""v0478 E174.4 (CORTE-PELO-CONTADOR, D4 do estudo determinístico): `forge-fechar --corte` lê as versões da develop, da homolog e da main,
promove a marca mesclada pelo --promover, abre o PR homolog -> main e, com o contador da develop no teto, grava a marca e abre o PR dela em
rascunho. O --laco que termina com 0 roda o --corte no fim.

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário com remoto bare e `git` falso) com `gh` e item falsos próprios; o
`forge-contador` e o `forge-changelog` são os de verdade, ao lado do script.
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# gh falso: `pr list` devolve $ESTADO/pr_main (o número do PR homolog -> main aberto; sem o arquivo, nenhum) ou falha com $ESTADO/lista_falha;
# `pr create` devolve o endereço do PR ou falha com $ESTADO/create_falha.
GH_CORTE = r'''#!/usr/bin/env bash
echo "gh $*" >> "$REGISTRO"
case "$1 $2" in
  "pr list") [ -f "$ESTADO/lista_falha" ] && exit 1; cat "$ESTADO/pr_main" 2>/dev/null; exit 0 ;;
  "pr create") [ -f "$ESTADO/create_falha" ] && exit 1; echo "https://github.com/o/r/pull/77" ;;
  *) exit 64 ;;
esac
'''
# Item falso (o --promover e o --corte que o laço chama): anota os argumentos e sai com $ESTADO/rc_item (padrão 0).
ITEM_CORTE = r'''#!/usr/bin/env bash
echo "item $*" >> "$REGISTRO"
exit "$(cat "$ESTADO/rc_item" 2>/dev/null || echo 0)"
'''
# git na frente do falso da base: a busca da marca na develop falha com $ESTADO/log_falha.
GIT_LOG = r'''#!/usr/bin/env bash
if [ -f "$ESTADO/log_falha" ] && [ "$1 $2" = "log -1" ]; then exit 128; fi
exec "$GIT_DA_BASE" "$@"
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
        self.env.update(FORGE_FECHAR_ITEM=str(self.tmp / "item"), GIT_DA_BASE=str(self.tmp / "bin" / "git"),
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


if __name__ == "__main__":
    unittest.main()
