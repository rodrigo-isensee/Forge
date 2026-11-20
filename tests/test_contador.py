"""AE2 C1 (v0478 E56.1): a contagem do contador da versão (bin/forge_contador.py). Repositório git temporário, sem rede: o
`origin/develop` é uma ref remota gravada com `update-ref`; os merges imitam os do GitHub (`--no-ff` com o assunto `Merge pull
request #N from ...`) e os squash, o assunto com `(#N)`."""
import functools
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_git_herdado  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=None)
def cont():
    """bin/forge_contador.py carregado sob demanda: sem ele (a base), cada teste falha sozinho."""
    return SourceFileLoader("forge_contador_teste", str(RAIZ / "bin" / "forge_contador.py")).load_module()


class Repo:
    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="contador-"))
        self.env = sem_git_herdado(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="t",
                                   GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        self.git("init", "-q", "-b", "develop")
        self.n = 0

    def git(self, *args, entrada=None):
        r = subprocess.run(["git", "-C", str(self.dir), *args], env=self.env, capture_output=True, input=entrada,
                           check=True, timeout=30)
        return r.stdout.decode().strip()

    def commit(self, mensagem):
        self.n += 1
        (self.dir / f"a{self.n}").write_text(str(self.n))
        self.git("add", "-A")
        self.git("commit", "-q", "-F", "-", entrada=mensagem.encode())
        return self.git("rev-parse", "HEAD")

    def pr(self, numero, *mensagens, ramo=None):
        """Um PR com um commit por mensagem, mesclado como o GitHub faz (`--no-ff`)."""
        ramo = ramo or f"item{numero}"
        self.git("switch", "-q", "-c", ramo)
        for mensagem in mensagens:
            self.commit(mensagem)
        self.git("switch", "-q", "develop")
        self.git("merge", "-q", "--no-ff", "-m", f"Merge pull request #{numero} from dono/{ramo}\n\ntitulo", ramo)

    def publicar(self):
        self.git("update-ref", "refs/remotes/origin/develop", "develop")

    def contar(self, **kw):
        self.publicar()
        return cont().contar(self.dir, **kw)

    def fechar(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class ComRepo(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.fechar)
        self.repo.commit("feat: começo\n\nCartão: ANTIGO")


class Contagem(ComRepo):
    def test_gatilho_dois_merges_tres_cartoes_depois_da_tag(self):
        self.repo.pr(1, "feat: antes da tag\n\nCartão: VELHO")
        self.repo.git("tag", "v0.47.11")
        self.repo.pr(2, "feat: a\n\nCartão: A-1\nCartão: B.2", "fix: a2\n\nCartão-parcial: P1")
        self.repo.pr(3, "feat: c\n\nCartão: C_3\nCartão: a-1")  # A-1 em dois PRs conta uma vez
        r = self.repo.contar()
        self.assertEqual((r["marca"], r["versao"]), ("v0.47.11", "0.47.12"))
        self.assertEqual(r["entregues"], ["A-1", "B.2", "C_3"])
        self.assertEqual([(p["numero"], p["cartoes"], p["parciais"]) for p in r["prs"]],
                         [(2, ["A-1", "B.2"], ["P1"]), (3, ["C_3", "a-1"], [])])
        self.assertEqual(r["avisos"], [])

    def test_squash_conta_pela_mensagem(self):
        self.repo.git("tag", "v1.0.0")
        self.repo.commit("feat: junto (#7)\n\n* um\n\nCartão: S1\n\n* dois\n\nCartão: S2")
        self.repo.commit("chore: sem PR\n\nCartão: FORA")  # commit direto, sem (#N), não é PR
        r = self.repo.contar()
        self.assertEqual([(p["numero"], p["cartoes"]) for p in r["prs"]], [(7, ["S1", "S2"])])
        self.assertEqual(r["entregues"], ["S1", "S2"])

    def test_sem_tag_conta_desde_o_primeiro_commit(self):
        self.repo.pr(4, "feat: x\n\nCartão: X")
        r = self.repo.contar()
        self.assertEqual((r["marca"], r["versao"]), (None, cont().SEM_MARCA))
        self.assertEqual(r["entregues"], ["X"])

    def test_tag_fora_da_forma_e_ignorada_e_vale_a_maior(self):
        self.repo.git("tag", "v0.9.0")
        self.repo.pr(1, "feat: a\n\nCartão: A")
        self.repo.git("tag", "v0.10.0")
        self.repo.pr(2, "feat: b\n\nCartão: B")
        for torta in ("v0.11", "v0.11.0-rc1", "x0.12.0", "v0.12.0.1"):
            self.repo.git("tag", torta)
        r = self.repo.contar()
        self.assertEqual((r["marca"], r["versao"]), ("v0.10.0", "0.10.1"))
        self.assertEqual(r["entregues"], ["B"])

    def test_so_tag_na_forma_sem_nenhuma_valida(self):
        self.repo.git("tag", "v1.2")
        self.assertEqual(self.repo.contar()["marca"], None)

    def test_assunto_de_merge_forjado_fora_da_primeira_linha_nao_e_pr(self):
        self.repo.pr(5, "Merge pull request #99 from x/y\n\nCartão: FORJADO-DENTRO", "feat: dentro (#42)\n\nCartão: OK")
        self.repo.commit("Merge pull request #98 from x/z\n\nCartão: FORJADO-UM-PAI")  # um pai: não é merge
        r = self.repo.contar()
        self.assertEqual([p["numero"] for p in r["prs"]], [5])  # nem o #99 nem o squash #42 de dentro do PR
        self.assertNotIn("FORJADO-UM-PAI", r["entregues"])

    def test_merge_sem_assunto_de_pr_nao_conta(self):
        self.repo.git("switch", "-q", "-c", "solto")
        self.repo.commit("feat: solto\n\nCartão: SOLTO")
        self.repo.git("switch", "-q", "develop")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge branch solto (#9)\n\nCartão: NO-MERGE", "solto")
        self.assertEqual(self.repo.contar()["prs"], [])  # dois pais com `(#N)` não é squash

    def test_tag_no_topo_sem_prs(self):
        self.repo.pr(1, "feat: a\n\nCartão: A")
        self.repo.git("tag", "v2.0.0")
        r = self.repo.contar()
        self.assertEqual((r["versao"], r["prs"], r["entregues"]), ("2.0.1", [], []))

    def test_mensagem_com_byte_invalido_nao_derruba(self):
        self.repo.git("switch", "-q", "-c", "bin")
        arvore = self.repo.git("rev-parse", "HEAD^{tree}")
        sha = self.repo.git("commit-tree", arvore, "-p", "HEAD", "-F", "-", entrada=b"feat: \xff\xfe\n\nCart\xc3\xa3o: BIN\n")
        self.repo.git("switch", "-q", "develop")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #6 from dono/bin", sha)
        self.assertEqual(self.repo.contar()["entregues"], ["BIN"])


class Citacoes(unittest.TestCase):
    def citar(self, *mensagens):
        avisos = []
        return (*cont().citacoes(mensagens, avisos, "PR #1"), avisos)

    def test_ids_recusados(self):
        for valor in ("A|B", "A\x07", "A​B", "Z" * 81, ".A", "-A", "A B", "Ação", "A\x1bB"):
            with self.subTest(valor=ascii(valor)):
                cartoes, parciais, avisos = self.citar(f"x\n\nCartão: {valor}\nCartão-parcial: {valor}")
                self.assertEqual((cartoes, parciais), ([], []))
                self.assertEqual(len(avisos), 2)
                self.assertTrue(all(a.isprintable() for a in avisos), avisos)  # o valor sai por ascii(): nada de controle nem Cf

    def test_id_vazio_e_recusado(self):
        self.assertEqual(self.citar("x\n\nCartão:   ")[:2], ([], []))

    def test_id_no_limite_de_80_passa(self):
        self.assertEqual(self.citar("Cartão: " + "Z" * 80)[0], ["Z" * 80])

    def test_chave_sem_caixa_nfd_e_fim_de_linha_crlf(self):
        nfd = "Cartão"
        cartoes, parciais, avisos = self.citar(f"x\r\n\r\ncartão: a1\r\n{nfd}: B2\nCARTÃO-PARCIAL:\tP\n")
        self.assertEqual((cartoes, parciais, avisos), (["a1", "B2"], ["P"], []))

    def test_linha_que_nao_comeca_pela_chave_nao_conta(self):
        self.assertEqual(self.citar("x\n\n  Cartão: A\nver Cartão: B\nCartões: C\nCartao: D")[:2], ([], []))

    def test_separador_unicode_nao_abre_linha(self):
        cartoes, _, avisos = self.citar("Cartão: A Cartão: B")
        self.assertEqual(cartoes, [])
        self.assertEqual(len(avisos), 1)

    def test_repetido_conta_uma_vez(self):
        self.assertEqual(self.citar("Cartão: A\nCartão: a")[0], ["A"])  # a primeira grafia fica
        self.assertEqual(self.citar("Cartão: B", "Cartão: b\nCartão-parcial: B")[:2], (["B"], ["B"]))

    def test_teto_de_dez_por_pr(self):
        linhas = "\n".join(f"Cartão: C{i}" for i in range(8)) + "\nCartão-parcial: P1\nCartão-parcial: P2\nCartão: C99"
        cartoes, parciais, avisos = self.citar(linhas)
        self.assertEqual((len(cartoes), parciais), (8, ["P1", "P2"]))
        self.assertNotIn("C99", cartoes)
        self.assertEqual(len(avisos), 1)
        self.assertIn("mais de 10", avisos[0])

    def test_dez_exatos_sem_aviso(self):
        cartoes, _, avisos = self.citar("\n".join(f"Cartão: C{i}" for i in range(10)))
        self.assertEqual((len(cartoes), avisos), (10, []))


class NaoVerificavel(ComRepo):
    def test_ref_com_hifen_e_recusada_sem_chamar_git(self):
        with mock.patch.object(cont().subprocess, "run") as run:
            for ref in ("--output=/tmp/x", "-n1", ""):
                with self.subTest(ref=ref), self.assertRaises(cont().ContagemIndisponivel):
                    cont().contar(self.repo.dir, ref=ref)
        run.assert_not_called()

    def test_ref_ausente(self):
        with self.assertRaisesRegex(cont().ContagemIndisponivel, "ref ausente: origin/develop"):
            cont().contar(self.repo.dir)

    def test_git_que_trava(self):
        self.repo.publicar()
        with mock.patch.object(cont().subprocess, "run", side_effect=subprocess.TimeoutExpired("git", 10)), \
                self.assertRaisesRegex(cont().ContagemIndisponivel, "TimeoutExpired"):
            cont().contar(self.repo.dir)

    def test_sem_git(self):
        self.repo.publicar()
        with mock.patch.object(cont().subprocess, "run", side_effect=FileNotFoundError("git")), \
                self.assertRaises(cont().ContagemIndisponivel):
            cont().contar(self.repo.dir)

    def test_git_que_falha_no_meio(self):
        self.repo.publicar()
        real = subprocess.run

        def falha_no_log(cmd, **kw):
            return subprocess.CompletedProcess(cmd, 128, b"", b"") if "log" in cmd else real(cmd, **kw)

        with mock.patch.object(cont().subprocess, "run", side_effect=falha_no_log), \
                self.assertRaisesRegex(cont().ContagemIndisponivel, "git log saiu com 128"):
            cont().contar(self.repo.dir)

    def test_git_sem_variaveis_herdadas(self):
        self.repo.publicar()
        with mock.patch.dict(os.environ, {"GIT_DIR": "/nao/existe"}):
            self.assertEqual(cont().contar(self.repo.dir)["marca"], None)


class Teto(unittest.TestCase):
    """AE2 C3: o teto da versão vem da configuração do projeto, com o padrão 20 e aviso quando o valor não vale."""

    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="contador-teto-"))
        self.addCleanup(shutil.rmtree, self.raiz, True)
        (self.raiz / ".forge").mkdir()
        self.arq = self.raiz.joinpath(*cont().CONFIG)

    def gravar(self, texto):
        self.arq.write_bytes(texto if isinstance(texto, bytes) else texto.encode())
        return cont().ler_teto(self.raiz)

    def test_sem_arquivo_e_sem_chave_vale_o_padrao_calado(self):
        self.assertEqual(cont().ler_teto(self.raiz), (20, None))
        self.assertEqual(cont().ler_teto(self.raiz, padrao=7), (7, None))
        self.assertEqual(self.gravar('{"outra": 1}'), (20, None))

    def test_valor_que_vale(self):
        for valor in (1, 20, 35, 200):
            with self.subTest(valor=valor):
                self.assertEqual(self.gravar(json.dumps({"teto_da_versao": valor})), (valor, None))

    def test_valor_que_nao_vale_usa_o_padrao_com_aviso(self):
        for valor in ("true", "false", "-1", "0", "201", "1000000000", '"20"', "20.0", "null", "[20]"):
            with self.subTest(valor=valor):
                teto, aviso = self.gravar(f'{{"teto_da_versao": {valor}}}')
                self.assertEqual(teto, 20)
                self.assertIn("fora de inteiro de 1 a 200; teto 20", aviso)

    def test_config_que_nao_e_objeto_json(self):
        for texto in ("[1]", "20", "nao e json", "", b"\xff\xfe", "[" * 5000 + "]" * 5000,
                      "[" * 32000 + "]" * 32000,  # no python 3.12, RecursionError; no 3.14, lista: aviso nos dois
                      '{"teto_da_versao": 30}' + " " * cont().TETO_DA_CONFIG):  # acima do teto de bytes, mesmo válido
            with self.subTest(texto=ascii(texto)[:30]):
                teto, aviso = self.gravar(texto)
                self.assertEqual(teto, 20)
                self.assertIn("não é objeto JSON", aviso)

    def test_config_por_link_nao_e_seguida(self):
        alvo = self.raiz / "alvo.json"
        alvo.write_text('{"teto_da_versao": 30}')
        self.arq.symlink_to(alvo)
        teto, aviso = cont().ler_teto(self.raiz)
        self.assertEqual(teto, 20)
        self.assertIn("não abre", aviso)

    def test_config_que_nao_e_arquivo_regular(self):
        self.arq.mkdir()  # pasta: o read daria IsADirectoryError sem a conferência do tipo
        self.assertEqual(cont().ler_teto(self.raiz)[0], 20)
        self.assertIn("não é objeto JSON", cont().ler_teto(self.raiz)[1])
        self.arq.rmdir()
        os.mkfifo(self.arq)  # O_NONBLOCK: a fifo sem escritor não trava a leitura
        teto, aviso = cont().ler_teto(self.raiz)
        self.assertEqual(teto, 20)
        self.assertIn("não é objeto JSON", aviso)


if __name__ == "__main__":
    unittest.main()
