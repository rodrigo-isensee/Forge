"""v047 E1.197: o `bin/forge-fechar` integra um item por vez com o CI do push da develop verde (FECHAR-ESPERA-CI-DEVELOP), em lote
de até 3 sem arquivo em comum (INTEGRACAO-EM-LOTE, diretriz 26) e promove para a homolog exatamente o commit da marca (RELEASE-EM-1H,
diretriz 27).

Reaproveita o ambiente de `test_fechar.Fechar` (repositório temporário, `gh`, `git` e `forge-check` falsos) sem herdar os testes dele.
"""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
import test_fechar as base  # noqa: E402  (o módulo, não a classe: a classe seria coletada de novo aqui)

MERGE_PADRAO = "0123456789abcdef0123456789abcdef01234567"  # o mergeCommit que o gh falso devolve
# Item falso do lote: anota os argumentos, imprime `merge: <sha>` (sha1 do nome da branch) e sai com o código de $ESTADO/item_<branch>.rc.
ITEM_FALSO = r'''#!/usr/bin/env bash
echo "item $*" >> "$REGISTRO"
f="$ESTADO/item_$(printf '%s' "$3" | tr '/' '_')"
[ -f "$f.sem_merge" ] || echo "merge: $(printf '%s' "$3" | sha1sum | cut -c1-40)"
exit "$(cat "$f.rc" 2>/dev/null || echo 0)"
'''


def merge_de(branch):
    return hashlib.sha1(branch.encode()).hexdigest()


class Ambiente(unittest.TestCase):
    tearDown = base.Fechar.tearDown
    git = base.Fechar.git
    fechar = base.Fechar.fechar
    chamadas = base.Fechar.chamadas
    setUp = base.Fechar.setUp

    def runs(self):
        return [c for c in self.chamadas() if c.startswith("gh run list")]

    def merges(self):
        return [c for c in self.chamadas() if c.startswith("gh pr merge")]

    def topo(self):
        return self.git("rev-parse", "develop")


class EsperaCiDevelop(Ambiente):
    """FECHAR-ESPERA-CI-DEVELOP: o topo da develop verde antes do merge (6b) e o CI do push no merge acompanhado até o fim (8)."""

    def test_espera_o_ci_do_topo_antes_e_o_do_merge_depois(self):
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        chamadas = self.chamadas()
        antes = f"gh run list --branch develop --event push --commit {self.topo()} --json databaseId,status,conclusion"
        depois = f"gh run list --branch develop --event push --commit {MERGE_PADRAO} --json databaseId,status,conclusion"
        i_antes = next(i for i, c in enumerate(chamadas) if c.startswith(antes))
        i_merge = next(i for i, c in enumerate(chamadas) if c.startswith("gh pr merge"))
        i_depois = next(i for i, c in enumerate(chamadas) if c.startswith(depois))
        self.assertLess(i_antes, i_merge)
        self.assertLess(i_merge, i_depois)
        self.assertIn("[8] CI do push na develop", r.stdout)
        self.assertIn("Entrega p1 fechada em develop.", r.stdout)

    def test_develop_vermelha_antes_do_merge_para_sem_mesclar(self):
        (self.estado / f"runs_{self.topo()}").write_text("91\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6b: a develop está vermelha", r.stderr)
        self.assertIn("run 91 failure", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_topo_cancelado_nao_prova_e_para(self):
        (self.estado / f"runs_{self.topo()}").write_text("91\tcompleted\tcancelled\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6b: o CI do push na develop", r.stderr)
        self.assertIn("foi cancelado", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_vermelho_e_cancelado_juntos_contam_como_vermelho(self):
        (self.estado / f"runs_{self.topo()}").write_text("91\tcompleted\tcancelled\n92\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("a develop está vermelha", r.stderr)

    def test_ci_do_topo_em_andamento_espera_e_segue(self):
        (self.estado / "runs_pendentes").write_text("2")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        chamadas = self.chamadas()
        i_merge = next(i for i, c in enumerate(chamadas) if c.startswith("gh pr merge"))
        self.assertEqual(len([c for c in chamadas[:i_merge] if c.startswith("gh run list")]), 3)

    def test_sem_execucao_no_prazo_para_sem_mesclar(self):
        (self.estado / "runs").write_text("")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera-ci", "0")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6b: o CI do push na develop", r.stderr)
        self.assertIn("não terminou no prazo", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_leitura_do_ci_que_falha_para_sem_mesclar(self):
        (self.estado / "falha_runs").write_text("3")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo 6b: não consegui ler o CI do push na develop", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_topo_ilegivel_no_servidor_para(self):
        self.git("push", "-q", "origin", "--delete", "develop")
        self.git("push", "-q", "origin", "melhoria/x:refs/heads/outra")
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera", "0")
        self.assertNotEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.merges(), [])

    def test_ci_vermelho_no_merge_sai_com_5_e_imprime_a_reversao(self):
        (self.estado / f"runs_{MERGE_PADRAO}").write_text("93\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("aviso: a develop está vermelha no 0123456", r.stderr)
        self.assertIn(f"para reverter: git fetch origin develop && git switch --no-track -c melhoria/reverte-0123456 origin/develop && "
                      f"git revert --no-edit {MERGE_PADRAO} && git push origin melhoria/reverte-0123456", r.stderr)
        self.assertIn("não ficou verde (código 5)", r.stdout)
        self.assertNotIn("melhoria/x", self.git("ls-remote", "origin", "refs/heads/melhoria/x"))  # a limpeza roda antes do passo 8

    def test_ci_cancelado_no_merge_sai_com_5_sem_reversao(self):
        (self.estado / f"runs_{MERGE_PADRAO}").write_text("93\tcompleted\tcancelled\n")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("foi cancelado", r.stderr)
        self.assertNotIn("para reverter", r.stderr)

    def test_sem_limpar_com_ci_vermelho_no_merge_sai_com_5(self):
        (self.estado / f"runs_{MERGE_PADRAO}").write_text("93\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--sem-limpar")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertIn("para reverter:", r.stderr)

    def test_item_de_lote_nao_espera_o_ci_da_develop(self):
        (self.estado / "runs").write_text("91\tcompleted\tfailure\n")
        r = self.fechar("p1", "--ref", "melhoria/x", "--item-de-lote")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.runs(), [])
        self.assertIn(f"merge: {MERGE_PADRAO}", r.stdout)

    def test_head_ja_na_base_nao_espera_ci_de_merge(self):
        self.git("merge", "-q", "--ff-only", "melhoria/x")
        self.git("push", "-q", "origin", "develop")
        r = self.fechar("p1", "--ref", "melhoria/x")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.runs(), [])

    def test_espera_ci_fora_da_faixa_para_antes_do_passo_1(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--espera-ci", "7201")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("--espera-ci fora da faixa", r.stderr)
        self.assertEqual(self.chamadas(), [])

    def test_opcao_sem_valor_e_pedido_repetido_param_antes_do_passo_1(self):
        casos = ((("p1", "--ref", "melhoria/x", "--espera-ci"), "--espera-ci pede os segundos"),
                 (("release-0.9.0", "--promover"), "--promover pede o sha do commit da marca"),
                 (("p1", "p2", "--ref", "melhoria/x"), "pedido repetido: p2"))
        for args, msg in casos:
            with self.subTest(args=args):
                r = self.fechar(*args)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(msg, r.stderr)
                self.assertEqual(self.chamadas(), [])

    def test_dry_run_mostra_as_duas_esperas(self):
        r = self.fechar("p1", "--ref", "melhoria/x", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("[6b]", r.stdout)
        self.assertIn("[8] CI do push na develop no commit de merge", r.stdout)


class Lote(Ambiente):
    """INTEGRACAO-EM-LOTE: até 3 itens sem arquivo em comum, um CI só (o do último merge), reversão do lote no vermelho."""

    def setUp(self):
        super().setUp()
        for nome, arquivo in (("melhoria/y", "c"), ("melhoria/z", "d")):
            self.git("switch", "-q", "-c", nome, "develop")
            (self.proj / arquivo).write_text("3\n")
            self.git("add", arquivo)
            self.git("commit", "-q", "-m", f"feat: {arquivo}")
            self.git("push", "-q", "origin", nome)
        self.git("switch", "-q", "develop")
        item = self.tmp / "item"
        item.write_text(ITEM_FALSO, encoding="utf-8")
        item.chmod(0o755)
        self.env["FORGE_FECHAR_ITEM"] = str(item)

    def itens(self):
        return [c for c in self.chamadas() if c.startswith("item ")]

    def test_sem_arquivo_em_comum_fecha_em_ordem_e_espera_um_ci_so(self):
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", "p3:melhoria/z")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [f"item {p} --ref {b} --base origin/develop --espera 1800 --item-de-lote"
                                         for p, b in (("p1", "melhoria/x"), ("p2", "melhoria/y"), ("p3", "melhoria/z"))])
        commits = [c.split("--commit ")[1].split()[0] for c in self.runs()]
        self.assertEqual(commits, [self.topo(), merge_de("melhoria/z")])  # o topo antes do lote e só o último merge depois
        self.assertIn("Lote fechado em develop: 3 merge(s)", r.stdout)

    def test_arquivo_em_comum_para_sem_mesclar_nenhum(self):
        self.git("switch", "-q", "melhoria/y")
        (self.proj / "b").write_text("outro\n")
        self.git("add", "b")
        self.git("commit", "-q", "-m", "feat: b de novo")
        self.git("switch", "-q", "develop")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo L1: arquivo em comum", r.stderr)
        self.assertIn("  b (melhoria/x e melhoria/y)", r.stderr)
        self.assertEqual(self.itens(), [])

    def test_branch_ausente_para_no_l1(self):
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/nao-existe")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo L1: sem a branch melhoria/nao-existe", r.stderr)
        self.assertEqual(self.itens(), [])

    def test_diff_ilegivel_para_no_l1(self):
        r = self.fechar("--lote", "--base", "origin/develop", "p1:melhoria/x", "p2:melhoria/y",
                        GIT_DIR=str(self.proj / ".git"), GIT_WORK_TREE=str(self.proj), GIT_OBJECT_DIRECTORY=str(self.tmp / "vazio"))
        self.assertNotEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertEqual(self.itens(), [])

    def test_lote_vermelho_imprime_a_reversao_do_lote_inteiro_e_sai_com_5(self):
        (self.estado / f"runs_{merge_de('melhoria/y')}").write_text("94\tcompleted\tfailure\n")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        m1, m2 = merge_de("melhoria/x"), merge_de("melhoria/y")
        self.assertIn(f"git revert --no-edit {m2} {m1} && git push origin melhoria/reverte-{m2[:7]}", r.stderr)
        self.assertIn("lote vermelho: reverta o lote inteiro", r.stderr)
        self.assertIn("(código 5)", r.stdout)

    def test_lote_cancelado_sai_com_5_sem_reversao(self):
        (self.estado / f"runs_{merge_de('melhoria/y')}").write_text("94\tcompleted\tcancelled\n")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 5, r.stderr + r.stdout)
        self.assertNotIn("lote vermelho", r.stderr)

    def test_develop_vermelha_antes_do_lote_para_sem_item(self):
        (self.estado / f"runs_{self.topo()}").write_text("91\tcompleted\tfailure\n")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo L2: a develop está vermelha", r.stderr)
        self.assertEqual(self.itens(), [])

    def test_item_que_para_encerra_o_lote_e_o_ci_dos_mesclados_e_acompanhado(self):
        (self.estado / "item_melhoria_y.rc").write_text("1")
        (self.estado / "item_melhoria_y.sem_merge").write_text("")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", "p3:melhoria/z")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertEqual(len(self.itens()), 2)
        self.assertIn("parou no lote: o item p2 (melhoria/y) parou com código 1; os 1 merge(s) antes dele", r.stderr)
        self.assertIn(f"--commit {merge_de('melhoria/x')}", self.runs()[-1])

    def test_item_com_limpeza_pendente_da_codigo_3_ao_lote(self):
        (self.estado / "item_melhoria_x.rc").write_text("3")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(len(self.itens()), 2)

    def test_item_ja_mesclado_nao_conta_merge(self):
        (self.estado / "item_melhoria_y.sem_merge").write_text("")
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn(f"--commit {merge_de('melhoria/x')}", self.runs()[-1])

    def test_quantidade_e_forma_dos_itens(self):
        casos = ((("p1:melhoria/x",), "pede 2 ou 3 itens"),
                 (("p1:melhoria/x", "p2:melhoria/y", "p3:melhoria/z", "p4:melhoria/w"), "pede 2 ou 3 itens"),
                 (("p1:melhoria/x", "melhoria/y"), "item fora da forma"),
                 (("p1:melhoria/x", "p 2:melhoria/y"), "item fora da forma"),
                 (("p1:melhoria/x", "p2:melhoria..y"), "branch inválida"),
                 (("p1:melhoria/x", "p2:develop"), "não pode ser develop"),
                 (("p1:melhoria/x", "p2:melhoria/x"), "aparece duas vezes"))
        for itens, msg in casos:
            with self.subTest(itens=itens):
                r = self.fechar("--lote", *itens)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn(msg, r.stderr)
                self.assertEqual(self.itens(), [])

    def test_lote_recusa_opcao_de_item(self):
        for extra in (("--ref", "melhoria/x"), ("--armar",), ("--cartao", "C1"), ("--item-de-lote",), ("--promover", "a" * 40)):
            with self.subTest(extra=extra):
                r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", *extra)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("--lote recebe só os itens", r.stderr)

    def test_dry_run_do_lote(self):
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("[L1]", r.stdout)
        self.assertIn("[L3]", r.stdout)
        self.assertEqual(self.chamadas(), [])

    def test_item_real_e_o_proprio_script(self):
        self.assertIn('item_cmd="${FORGE_FECHAR_ITEM:-$eu}"', base.SCRIPT.read_text())
        r = self.fechar("--lote", "p1:melhoria/x", "p2:melhoria/y", FORGE_FECHAR_TESTE="0", FORGE_FECHAR_ITEM="/bin/false")
        self.assertIn("FORGE_FECHAR_ITEM", r.stderr)  # sem o modo de teste, o falso é ignorado com aviso


class Promover(Ambiente):
    """RELEASE-EM-1H: a homolog recebe o commit da marca pelo ramo promocao/<versão>, nunca o topo da develop."""

    def setUp(self):
        super().setUp()
        (self.proj / ".claude-plugin" / "plugin.json").write_text('{\n  "name": "forge",\n  "version": "0.9.0"\n}\n')
        self.git("commit", "-q", "-am", "chore(release): 0.9.0")
        self.marca = self.git("rev-parse", "HEAD")
        (self.proj / "depois").write_text("item depois da marca\n")
        self.git("add", "depois")
        self.git("commit", "-q", "-m", "feat: item depois da marca")
        self.depois = self.git("rev-parse", "HEAD")
        self.git("push", "-q", "origin", "develop")
        (self.estado / "base_final").write_text("homolog")

    def promover(self, *extra, **env):
        return self.fechar("release-0.9.0", "--promover", self.marca, *extra, **env)

    def ramo(self):
        return self.git("ls-remote", "origin", "refs/heads/promocao/0.9.0").split("\t")[0]

    def test_item_mesclado_depois_da_marca_nao_entra_na_promocao(self):
        (self.estado / "falha_delete").write_text("3")  # o ramo fica no servidor para a prova
        r = self.promover()
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertEqual(self.ramo(), self.marca)
        self.assertNotEqual(self.ramo(), self.depois)
        self.assertIn("a develop tem 1 commit(s) depois dela", r.stdout)
        self.assertIn("gh pr create --base homolog --head promocao/0.9.0", "\n".join(self.chamadas()))
        self.assertEqual(self.merges(), [f"gh pr merge promocao/0.9.0 --auto --merge --match-head-commit {self.marca}"])
        self.assertEqual((self.estado / "promover").read_text(), f"--conferir-ref {self.marca}\n")
        self.assertIn(f"--commit {self.marca}", self.runs()[0])
        self.assertIn("gh pr create --base main --head homolog", r.stdout)

    def test_promocao_completa_apaga_o_ramo(self):
        r = self.promover()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("promovida: a homolog recebeu o commit da marca", r.stdout)
        self.assertEqual(self.ramo(), "")

    def test_retomada_com_o_pr_ja_mesclado_nao_cria_nem_mescla(self):
        self.git("push", "-q", "origin", f"{self.marca}:refs/heads/promocao/0.9.0")
        (self.estado / "lista_extra").write_text(f"8 MERGED homolog {self.marca} false\n")
        (self.estado / "estado").write_text("MERGED")
        r = self.promover()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("retomo", r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith(("gh pr create", "gh pr merge"))])

    def test_retomada_com_o_pr_aberto_reusa(self):
        self.git("push", "-q", "origin", f"{self.marca}:refs/heads/promocao/0.9.0")
        (self.estado / "aberto").write_text("7 homolog")
        r = self.promover()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("PR #7 já aberto; retomo.", r.stdout)
        self.assertFalse([c for c in self.chamadas() if c.startswith("gh pr create")])

    def test_pr_aberto_com_outra_base_para(self):
        self.git("push", "-q", "origin", f"{self.marca}:refs/heads/promocao/0.9.0")
        (self.estado / "aberto").write_text("7 develop")
        r = self.promover()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P5: o PR aberto #7", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_dois_prs_abertos_param(self):
        self.git("push", "-q", "origin", f"{self.marca}:refs/heads/promocao/0.9.0")
        (self.estado / "aberto").write_text("7 homolog")
        (self.estado / "lista_extra").write_text(f"9 OPEN homolog {self.marca} false\n")
        r = self.promover()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("há mais de um PR aberto", r.stderr)

    def test_ramo_com_outro_commit_para(self):
        self.git("push", "-q", "origin", f"{self.depois}:refs/heads/promocao/0.9.0")
        r = self.promover()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P4: promocao/0.9.0 já existe no origin com outro commit", r.stderr)
        self.assertEqual(self.merges(), [])

    def test_marca_fora_da_develop_para(self):
        self.git("switch", "-q", "melhoria/x")
        fora = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "develop")
        r = self.fechar("release-0.9.0", "--promover", fora)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não está na develop do servidor", r.stderr)

    def test_marca_que_nao_existe_aqui_para(self):
        r = self.fechar("release-0.9.0", "--promover", "f" * 40)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P1: sem o commit da marca", r.stderr)

    def test_sha_fora_da_forma_para_antes_de_tudo(self):
        for sha in ("abc", "G" * 40, self.marca.upper()):
            with self.subTest(sha=sha):
                r = self.fechar("release-0.9.0", "--promover", sha)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("--promover pede o sha de 40 hex", r.stderr)
                self.assertEqual(self.chamadas(), [])

    def test_marca_sem_versao_para(self):
        r = self.fechar("release-0.9.0", "--promover", self.git("rev-parse", "develop~2"))
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não li a versão X.Y.Z", r.stderr)

    def test_marca_nao_promovivel_para(self):
        r = self.promover(PROMOVER_RC="1")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("não é promovível", r.stderr)
        self.assertEqual(self.ramo(), "")

    def test_ci_vermelho_na_marca_para_e_cancelado_segue(self):
        (self.estado / f"runs_{self.marca}").write_text("95\tcompleted\tfailure\n")
        r = self.promover()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P3", r.stderr)
        self.assertEqual(self.ramo(), "")
        (self.estado / f"runs_{self.marca}").write_text("95\tcompleted\tcancelled\n")
        r = self.promover()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("decide o CI do PR de promoção", r.stderr)

    def test_pr_que_nao_mescla_no_prazo_para_para_retomar(self):
        (self.estado / "auto_arma").write_text("")
        r = self.promover("--espera", "0")
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P6", r.stderr)
        self.assertIn("rode o mesmo comando para retomar", r.stderr)

    def test_merge_em_outra_base_nao_e_sucesso(self):
        (self.estado / "base_final").write_text("develop")
        r = self.promover()
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("parou no passo P6", r.stderr)

    def test_promover_recusa_opcao_de_item(self):
        for extra in (("--ref", "melhoria/x"), ("--limpar",), ("--cartao", "C1")):
            with self.subTest(extra=extra):
                r = self.promover(*extra)
                self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
                self.assertIn("--promover recebe só", r.stderr)

    def test_dry_run_da_promocao(self):
        r = self.promover("--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("[P6]", r.stdout)
        self.assertEqual(self.chamadas(), [])


if __name__ == "__main__":
    unittest.main()
