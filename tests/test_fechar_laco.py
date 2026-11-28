"""v0478 E173.1 (INTEGRADOR-EM-LACO, D1 do estudo determinístico): `forge-fechar --laco` lê os PRs abertos para a develop, avisa o vermelho
ou em conflito sem commit há mais de 2 h e fecha, em ordem de chegada, os que passam no forge-check pr, em grupos de até 3 sem arquivo em
comum pelo --lote (um só, sem ele).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário e `git` falso) com `gh`, `forge-check` e item falsos próprios.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

# gh falso: a lista do laço (a saída do --jq: número, branch, mergeable e checks ruins, lida de $ESTADO/lista) e a data do último commit do
# PR <n> ($ESTADO/data_<n>, só na forma que o script pede; sem o arquivo, a leitura falha).
GH_LACO = r'''#!/usr/bin/env bash
echo "gh $*" >> "$REGISTRO"
case "$1 $2" in
  "pr list") [ -f "$ESTADO/lista_falha" ] && exit 1; cat "$ESTADO/lista" ;;
  "pr view") [ "${*:4}" = '--json commits --jq .commits[-1].committedDate // ""' ] || exit 64; [ -f "$ESTADO/data_$3" ] || exit 1; cat "$ESTADO/data_$3" ;;
  *) exit 64 ;;
esac
'''
# forge-check falso: reprova o pedido com $ESTADO/reprova_<pedido>; `parecer pedido <branch>` (C0-3) devolve o pedido dos briefs da
# branch, o conteúdo de $ESTADO/brief_<branch com / trocada por _>, e sem o arquivo sai 1 (nenhum ou dois pedidos nos briefs); com
# $ESTADO/rc1_<branch>, imprime o nome e sai 1 (o código vale, não a saída).
CHECK_LACO = r'''#!/usr/bin/env bash
echo "forge-check $*" >> "$REGISTRO"
if [ "$1 $2" = "parecer pedido" ]; then
  f="$ESTADO/brief_${3//\//_}"; { [ "$#" = 3 ] && [ -f "$f" ]; } || exit 1; cat "$f"; [ ! -f "$ESTADO/rc1_${3//\//_}" ]; exit
fi
[ ! -f "$ESTADO/reprova_$2" ]
'''
# Item falso: anota os argumentos e sai com o código de $ESTADO/rc_<ordem da chamada> (padrão 0).
ITEM_LACO = r'''#!/usr/bin/env bash
echo "item $*" >> "$REGISTRO"
k="$(grep -c '^item ' "$REGISTRO")"
exit "$(cat "$ESTADO/rc_$k" 2>/dev/null || echo 0)"
'''
VERDE = "MERGEABLE\t0"  # sem conflito e sem check ruim
FIM = "--base origin/develop --espera 1800 --espera-ci 3600"


class Laco(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas

    def setUp(self):
        base.Fechar.setUp(self)
        for nome, texto in (("gh", GH_LACO), ("check", CHECK_LACO), ("item", ITEM_LACO)):
            (self.tmp / nome).write_text(texto, encoding="utf-8")
            (self.tmp / nome).chmod(0o755)
        # relógio fixo em 2026-01-01T00:00:00Z: antes da meia-noite de hoje (o que o GNU date dá à data vazia) e longe das datas dos testes
        self.env.update(FORGE_FECHAR_ITEM=str(self.tmp / "item"), FORGE_FECHAR_AGORA="1767225600")
        # branch: (arquivo do diff, pedidos dos pareceres de review com `branch:` igual a ela); o pedido do laço vem só dos briefs (C0-3):
        # um brief por branch de um pedido só, nenhum na `so-parecer` (o parecer dela leva `pedido: ps`, que não vale sozinho)
        for br, arquivo, pedidos in (("a", "fa", ["pa"]), ("b", "fb", ["pb"]), ("c", "fc", ["pc"]), ("d", "fa", ["pd"]),
                                     ("e", "fe", ["pe"]), ("dois", "fg", ["pf", "pg"]), ("sem", "fh", []), ("so-parecer", "fs", ["ps"])):
            self.ramo(f"melhoria/{br}", arquivo, pedidos, brief=len(pedidos) == 1 and br != "so-parecer")
        self.ramo("melhoria/pre", "fp", ["pp"], outros={"px": "melhoria/prefixo"}, brief=True)

    def ramo(self, br, arquivo, pedidos, orfao=False, outros=None, brief=False):
        if brief:  # o pedido que os briefs da pasta de controle dão à branch (o `forge-check parecer pedido` falso)
            (self.estado / f"brief_{br.replace('/', '_')}").write_text(pedidos[0])
        self.git("switch", "-q", "--orphan" if orfao else "-c", br, *([] if orfao else ["develop"]))
        (self.proj / arquivo).write_text(br + "\n")
        revs = self.proj / "docs" / "reviews"
        revs.mkdir(parents=True, exist_ok=True)
        # o corpo cita a branch deste ramo: só o frontmatter conta (o parecer de outra branch que a cita no texto fica fora)
        for p, b in [(p, br) for p in pedidos] + list((outros or {}).items()):
            (revs / f"{p}.md").write_text(f"---\ntipo: review\npedido: {p}\nbranch: {b}\nparecer: aprovado\n---\n# Review\nbranch: {br}\n")
        if outros:  # arquivo sem frontmatter com as duas linhas: não é parecer
            (revs / "notas.md").write_text(f"pedido: pz\nbranch: {br}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", f"feat: {br}")
        self.git("push", "-q", "origin", br)
        self.git("switch", "-q", "-f", "develop")
        self.git("clean", "-qfdx")

    def lista(self, *linhas):
        (self.estado / "lista").write_text("".join(f"{n}\t{br}\t{resto}\n" for n, br, resto in linhas))

    def itens(self):  # os fechamentos; o --corte do fim da volta (CORTE-PELO-CONTADOR) tem teste próprio
        return [c.removeprefix("item ") for c in self.chamadas() if c.startswith("item ") and not c.startswith("item --corte ")]

    def cortes(self):
        return [c for c in self.chamadas() if c.startswith("item --corte ")]

    def test_grupos_de_ate_3_em_ordem_e_o_ultimo_sozinho_sem_lote(self):
        self.lista(*((n, f"melhoria/{b}", VERDE) for n, b in ((11, "a"), (12, "b"), (13, "c"), (14, "e"))))
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [f"--lote pa:melhoria/a pb:melhoria/b pc:melhoria/c {FIM}", f"pe --ref melhoria/e {FIM}"])
        self.assertIn("Laço: 2 grupo(s), código 0.", r.stdout)
        lista = next(c for c in self.chamadas() if c.startswith("gh pr list"))
        self.assertIn("gh pr list --base develop --state open --limit 100 --json number,headRefName,isCrossRepository,mergeable,", lista)
        self.assertIn("forge-check pr pa --ref refs/remotes/origin/melhoria/a --base origin/develop", self.chamadas())

    def test_arquivo_em_comum_abre_grupo_novo(self):
        self.lista((11, "melhoria/a", VERDE), (12, "melhoria/d", VERDE), (13, "melhoria/b", VERDE))
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [f"pa --ref melhoria/a {FIM}", f"--lote pd:melhoria/d pb:melhoria/b {FIM}"])

    def test_parado_ha_mais_de_2_h_avisa_e_nao_entra(self):
        (self.estado / "data_21").write_text("2025-12-31T21:59:59Z\n")  # 2 h e 1 s antes do relógio
        (self.estado / "data_22").write_text("2025-12-31T22:00:00Z\n")  # 2 h exatas: ainda não é parado
        (self.estado / "data_25").write_text("\n")  # 23: a leitura falha; 25: o GitHub não devolve data
        self.lista((21, "melhoria/a", "CONFLICTING\t0"), (22, "melhoria/b", "MERGEABLE\t1"), (23, "melhoria/c", "MERGEABLE\t2"),
                   (24, "melhoria/e", VERDE), (25, "melhoria/d", "CONFLICTING\t3"))
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("aviso: PR #21 (melhoria/a) parado: em conflito e sem commit há mais de 2 h (último: 2025-12-31T21:59:59Z)", r.stderr)
        self.assertNotIn("PR #22", r.stderr)  # vermelho com commit recente: alguém trabalha nele
        self.assertIn("aviso: PR #23 (melhoria/c) parado: vermelho e sem commit há mais de 2 h (último: desconhecido)", r.stderr)
        self.assertIn("aviso: PR #25 (melhoria/d) parado: em conflito e sem commit há mais de 2 h (último: desconhecido)", r.stderr)
        self.assertEqual(self.itens(), [f"pe --ref melhoria/e {FIM}"])
        self.assertFalse([c for c in self.chamadas() if c.startswith("forge-check") and "melhoria/e" not in c])
        vistos = [c.split()[3] for c in self.chamadas() if c.startswith("gh pr view")]
        self.assertEqual(sorted(set(vistos)), ["21", "22", "23", "25"])  # só os vermelhos ou em conflito (o 23 com as 3 tentativas)

    def test_so_entram_os_aprovados_com_um_pedido_so(self):
        (self.estado / "reprova_pb").write_text("")
        self.lista((31, "melhoria/a", VERDE), (32, "melhoria/b", VERDE), (33, "melhoria/dois", VERDE), (34, "melhoria/sem", VERDE),
                   (35, "feature/q", VERDE), (36, "melhoria/a:b", VERDE), (37, "melhoria/sumiu", VERDE), (38, "melhoria/pre", VERDE),
                   (39, "melhoria/so-parecer", VERDE), (40, "melhoria/c", VERDE))
        (self.estado / "rc1_melhoria_c").write_text("")
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [f"--lote pa:melhoria/a pp:melhoria/pre {FIM}"])
        self.assertIn("PR #32 (melhoria/b): pareceres do pedido pb não aprovados no head", r.stdout)
        self.assertIn("PR #33 (melhoria/dois): sem um pedido só", r.stdout)
        self.assertIn("PR #34 (melhoria/sem): sem um pedido só", r.stdout)
        # C0-3: o `pedido:` do parecer de review da própria branch não vale sem brief que a cite (a conferência seria tautológica)
        self.assertIn("PR #39 (melhoria/so-parecer): sem um pedido só nos briefs da branch (C0-3); fica de fora.", r.stdout)
        self.assertIn("PR #40 (melhoria/c): sem um pedido só nos briefs da branch (C0-3)", r.stdout)  # rc 1 com nome impresso
        self.assertIn("forge-check parecer pedido melhoria/a", self.chamadas())
        self.assertFalse([c for c in self.chamadas() if c.startswith("forge-check pr ps ")])
        self.assertIn("aviso: PR #37: não busquei melhoria/sumiu", r.stderr)
        self.assertNotIn("PR #35", r.stdout + r.stderr)  # fora de melhoria/*
        self.assertNotIn("PR #36", r.stdout + r.stderr)  # nome inválido nem chega à busca

    def test_diff_ilegivel_fica_de_fora_e_o_laco_segue(self):
        self.ramo("melhoria/orfa", "fo", ["po"], orfao=True, brief=True)
        self.lista((41, "melhoria/orfa", VERDE), (42, "melhoria/a", VERDE))
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("aviso: não li o diff de melhoria/orfa contra origin/develop", r.stderr)
        self.assertEqual(self.itens(), [f"pa --ref melhoria/a {FIM}"])

    def test_codigos_dos_grupos(self):
        linhas = ((11, "melhoria/a", VERDE), (12, "melhoria/d", VERDE), (13, "melhoria/c", VERDE))  # grupos [a] e [d, c]
        for rcs, esperado, n_itens in (({1: "5"}, 5, 1), ({1: "1"}, 1, 2), ({1: "3"}, 3, 2), ({1: "3", 2: "1"}, 1, 2), ({1: "1", 2: "3"}, 1, 2)):
            with self.subTest(rcs=rcs):
                self.registro.write_text("")
                for f in self.estado.glob("rc_*"):
                    f.unlink()
                for k, v in rcs.items():
                    (self.estado / f"rc_{k}").write_text(v)
                self.lista(*linhas)
                r = self.fechar("--laco")
                self.assertEqual(r.returncode, esperado, r.stderr + r.stdout)
                self.assertEqual(len(self.itens()), n_itens)
                if esperado == 5:
                    self.assertIn("laço parado: o CI da develop não ficou verde", r.stderr)

    def test_dry_run_le_e_nao_fecha(self):
        self.lista((11, "melhoria/a", VERDE), (12, "melhoria/b", VERDE))
        r = self.fechar("--laco", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [])
        self.assertIn(f"rodaria: forge-fechar --lote pa:melhoria/a pb:melhoria/b {FIM}", r.stdout)

    def test_volta_sem_pendencia_roda_o_corte_no_fim(self):  # v0478 E174.4 (CORTE-PELO-CONTADOR, D4)
        self.lista((11, "melhoria/a", VERDE))
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.chamadas()[-1], f"item --corte {FIM}")
        for rcs, esperado, n_cortes in (({2: "1"}, 1, 1), ({1: "1"}, 1, 0), ({1: "3"}, 3, 0)):  # o código do corte vale; grupo que para ou limpeza pendente não cortam
            with self.subTest(rcs=rcs):
                self.registro.write_text("")
                for f in self.estado.glob("rc_*"):
                    f.unlink()
                for k, v in rcs.items():
                    (self.estado / f"rc_{k}").write_text(v)
                r = self.fechar("--laco")
                self.assertEqual(r.returncode, esperado, r.stderr + r.stdout)
                self.assertEqual(len(self.cortes()), n_cortes)
        self.registro.write_text("")
        r = self.fechar("--laco", "--dry-run")
        self.assertIn("rodaria: forge-fechar --corte --base origin/develop", r.stdout)
        self.assertEqual(self.cortes(), [])

    def test_lista_ilegivel_para(self):
        (self.estado / "lista_falha").write_text("")
        r = self.fechar("--laco")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo C1: não consegui ler os PRs abertos", r.stderr)
        self.assertEqual(self.itens(), [])

    def test_recusa_o_que_nao_e_do_laco(self):
        for extra in (["p1"], ["--ref", "melhoria/a"], ["--lote", "p1:melhoria/a", "p2:melhoria/b"], ["--limpar"]):
            with self.subTest(extra=extra):
                r = self.fechar("--laco", *extra)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("--laco recebe só --base, --espera, --espera-ci ou --dry-run", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_sem_laco_o_fluxo_do_item_segue(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertNotIn("[C1]", r.stdout)
        self.assertNotIn("Laço:", r.stdout)


if __name__ == "__main__":
    unittest.main()
