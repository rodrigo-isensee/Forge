"""G1.2 (v0478, ORDEM DO DONO de 21/11 22:13): na revalidação, o bloqueante novo fica no que mudou entre o `commit:` anterior e o
atual (com a margem de 3 linhas) ou repete um bloqueante da rodada anterior; fora disso, o parecer é recusado ("vira recomendado
e cartão"). Exceção: a segurança com `explorável: S<n>` e a sonda em `## Sondas`. Sem rede; repositório temporário."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_fora_do_delta", str(FORGE_CHECK)).load_module()

CABECA = ("---\ntipo: {tipo}\ncontrato: 1\npedido: p1\nbranch: melhoria/x\ncommit: {c}\nparecer: reprovado\n"
          "revisor: forge:tech-lead\ndata: 2026-11-22\n---\n# Parecer\n\n## Achados\n{achados}\n{sondas}")
PASTA = {"review": "docs/reviews", "revisao-seguranca": "docs/security"}


def ambiente_do_git():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return sem_manutencao(env)


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=ambiente_do_git()).stdout.strip()


class Revalidacao(unittest.TestCase):
    """Rodada 1 no commit c1 com A1 bloqueante em src/a.py:5; o autor muda só a linha 15 (c2); a rodada 2 é a versão nova do arquivo."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-fora-do-delta-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        git("init", "-q", "-b", "develop", cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=self.tmp)
        git("config", "user.name", "Teste", cwd=self.tmp)
        self.linhas = [f"v{i}\n" for i in range(1, 31)]
        self.c1 = self.commitar({"src/a.py": "".join(self.linhas)})
        self.linhas[14] = "mudou\n"
        self.c2 = self.commitar({"src/a.py": "".join(self.linhas)})

    def commitar(self, arquivos):
        for rel, texto in arquivos.items():
            (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.tmp / rel).write_text(texto, encoding="utf-8")
        git("add", "-A", cwd=self.tmp)
        git("commit", "-q", "-m", "x", cwd=self.tmp)
        return git("rev-parse", "HEAD", cwd=self.tmp)

    def parecer(self, tipo, commit, achados, sondas=""):
        return CABECA.format(tipo=tipo, c=commit, achados="\n".join(achados), sondas=sondas)

    def rodadas(self, segunda, tipo="review", sondas="", primeira=("- A1 (bloqueante) src/a.py:5 · defeito provado na linha 5",)):
        """Grava a rodada 1 (commitada) e devolve as violações da rodada 2 (`fora_do_delta` sobre o texto novo, ref HEAD)."""
        rel = f"{PASTA[tipo]}/p1.md"
        self.commitar({rel: self.parecer(tipo, self.c1[:7], primeira)})
        texto = self.parecer(tipo, self.c2[:7], segunda, sondas)
        return fc.fora_do_delta(self.tmp, rel, texto, fc.ler_frontmatter(texto)[0], None)

    def test_bloqueante_novo_fora_do_delta_e_recusado(self):
        saida = self.rodadas(["- A2 (bloqueante) src/a.py:2 · achado novo onde nada mudou"])
        self.assertEqual(len(saida), 1, saida)
        self.assertIn("A2 bloqueante novo fora do que mudou", saida[0])
        self.assertIn("vira recomendado e cartão", saida[0])

    def recusas_por_linha(self, linhas):
        """{linha: quantas recusas}, um repositório novo por linha; sem subTest, para o `--vermelho` ver o erro da base no id do teste
        (E122.6, QA A4)."""
        contagem = {}
        for linha in linhas:
            self.setUp()
            contagem[linha] = len(self.rodadas([f"- A2 (bloqueante) src/a.py:{linha} · achado"]))
        return contagem

    def test_bloqueante_no_trecho_mudado_ou_na_margem_passa(self):
        linhas = ("15", "12", "18", "10-12", "1-20")
        self.assertEqual(self.recusas_por_linha(linhas), dict.fromkeys(linhas, 0))

    def test_fora_da_margem_de_3_linhas_e_recusado(self):
        linhas = ("11", "19", "5-11")
        self.assertEqual(self.recusas_por_linha(linhas), dict.fromkeys(linhas, 1))

    def test_faixa_larga_nao_cruza_o_delta(self):  # E122.6 (QA A2): `arquivo:1-99999` não escapa do delta
        linhas = ("1-21", "1-99999", "14-34")
        self.assertEqual(self.recusas_por_linha(linhas), dict.fromkeys(linhas, 1))

    def test_bloqueante_repetido_da_rodada_anterior_passa(self):
        self.assertEqual(self.rodadas(["- A1 (bloqueante) src/a.py:5 · defeito provado na linha 5, ainda aberto"]), [])

    def test_mesmo_id_em_outro_arquivo_nao_e_repeticao(self):
        self.assertEqual(len(self.rodadas(["- A1 (bloqueante) src/b.py:5 · outro arquivo"])), 1)

    def test_recomendado_fora_do_delta_passa(self):  # com o bloqueante repetido A1, o laço roda e chega ao recomendado (FD10)
        achados = ["- A1 (bloqueante) src/a.py:5 · ainda aberto", "- A2 (recomendado) src/a.py:2 · sugestão"]
        self.assertEqual(self.rodadas(achados), [])

    def test_primeira_rodada_nao_recusa(self):
        texto = self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"])
        self.assertEqual(fc.fora_do_delta(self.tmp, "docs/reviews/p1.md", texto, fc.ler_frontmatter(texto)[0], None), [])

    def test_rodada_anterior_de_outro_pedido_nao_conta(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], []).replace("pedido: p1", "pedido: p0")})
        texto = self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"])
        self.assertEqual(fc.fora_do_delta(self.tmp, rel, texto, fc.ler_frontmatter(texto)[0], None), [])

    def test_mesmo_commit_nao_e_rodada_anterior(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c2, [])})
        texto = self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"])
        self.assertEqual(fc.fora_do_delta(self.tmp, rel, texto, fc.ler_frontmatter(texto)[0], None), [])

    def test_seguranca_exploravel_com_sonda_passa(self):
        sondas = "\n## Sondas\n- S1 · entrada de ataque · espera: recusa · obtido: aceitou\n"
        achado = ["- A2 (bloqueante) src/a.py:2 · explorável: S1 caminho de ataque real"]
        self.assertEqual(self.rodadas(achado, "revisao-seguranca", sondas), [])

    def test_seguranca_exploravel_sem_a_sonda_e_recusado(self):
        sondas = "\n## Sondas\n- S2 · outra entrada qualquer · espera: recusa · obtido: aceitou\n"
        achado = ["- A2 (bloqueante) src/a.py:2 · explorável: S1 caminho de ataque real"]
        self.assertEqual(len(self.rodadas(achado, "revisao-seguranca", sondas)), 1)

    def test_exploravel_no_review_nao_vale(self):
        sondas = "\n## Sondas\n- S1 · entrada de ataque · espera: recusa · obtido: aceitou\n"
        self.assertEqual(len(self.rodadas(["- A2 (bloqueante) src/a.py:2 · explorável: S1"], "review", sondas)), 1)

    def test_git_que_falha_nao_recusa(self):
        original = fc.trechos_do_delta
        fc.trechos_do_delta = lambda *a: None
        self.addCleanup(setattr, fc, "trechos_do_delta", original)
        self.assertEqual(self.rodadas(["- A2 (bloqueante) src/a.py:2 · novo"]), [])

    def test_diff_que_falha_devolve_none(self):
        self.assertIsNone(fc.trechos_do_delta(self.tmp, "0" * 40, self.c2, "src/a.py"))
        self.assertEqual(fc.trechos_do_delta(self.tmp, self.c1, self.c2, "src/a.py"), [(12, 18)])

    def test_parecer_sem_commit_valido_nao_recusa(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], [])})
        for commit in ("", "HEAD"):  # `HEAD` resolve no git, mas não é o hash que o contrato pede
            with self.subTest(commit=commit):
                texto = self.parecer("review", commit, ["- A2 (bloqueante) src/a.py:2 · novo"])
                self.assertEqual(fc.fora_do_delta(self.tmp, rel, texto, fc.ler_frontmatter(texto)[0], None), [])

    def test_recomendado_anterior_promovido_fora_do_delta_e_recusado(self):
        primeira = ("- A2 (recomendado) src/a.py:2 · sugestão",)
        self.assertEqual(len(self.rodadas(["- A2 (bloqueante) src/a.py:2 · agora bloqueia"], primeira=primeira)), 1)

    def test_versao_sem_frontmatter_e_ignorada(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], [])})
        self.commitar({rel: "sem frontmatter\n"})
        texto = self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"])
        self.assertEqual(len(fc.fora_do_delta(self.tmp, rel, texto, fc.ler_frontmatter(texto)[0], None)), 1)

    def test_docs_sem_base_nao_e_estrito_e_nao_recusa(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], [])})
        (self.tmp / rel).write_text(self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"]), encoding="utf-8")
        self.assertFalse([v for v in fc.cmd_docs(self.tmp) if "fora do que mudou" in v])

    def test_docs_recusa_pela_cli(self):
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], [])})
        (self.tmp / rel).write_text(self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"]), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))}
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.tmp), "docs", str(self.tmp / rel)],
                           capture_output=True, text=True, env=dict(env, HOME=str(self.tmp / "home")), timeout=60)
        self.assertIn("A2 bloqueante novo fora do que mudou", r.stdout + r.stderr)
        self.assertNotEqual(r.returncode, 0)

    def test_pr_recusa_pela_cli(self):
        git("switch", "-q", "-c", "melhoria/x", cwd=self.tmp)
        git("branch", "-f", "develop", self.c1, cwd=self.tmp)
        rel = "docs/reviews/p1.md"
        self.commitar({rel: self.parecer("review", self.c1[:7], [])})
        self.commitar({rel: self.parecer("review", self.c2[:7], ["- A2 (bloqueante) src/a.py:2 · novo"])})
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))}
        r = subprocess.run([sys.executable, "-I", str(FORGE_CHECK), "--raiz", str(self.tmp), "pr", "p1", "--base", "develop"],
                           capture_output=True, text=True, env=dict(env, HOME=str(self.tmp / "home")), timeout=60)
        self.assertIn("A2 bloqueante novo fora do que mudou", r.stdout)
        self.assertNotEqual(r.returncode, 0)


class LeiturasEmLote(unittest.TestCase):
    """E140.12 (ORDEM DO DONO de 24/11): as versões anteriores do parecer saem num `cat-file --batch` só, e o parecer sem bloqueante
    não roda git nenhum; o que a checagem decide não muda (as recusas de `Revalidacao` seguem as mesmas)."""
    setUp, commitar, parecer = Revalidacao.setUp, Revalidacao.commitar, Revalidacao.parecer
    REL = "docs/reviews/p1.md"

    def contar_git(self):
        chamadas, original = [], fc.git

        def contado(raiz, *args, **kw):
            chamadas.append(args[1] if args[0] == "--literal-pathspecs" else args[0])
            return original(raiz, *args, **kw)
        fc.git = contado
        self.addCleanup(setattr, fc, "git", original)
        return chamadas

    def falso_git(self, cod, lote):
        original = fc.git
        fc.git = lambda *a, **kw: (cod, lote)
        self.addCleanup(setattr, fc, "git", original)

    def revalidar(self, achado):
        texto = self.parecer("review", self.c2[:7], [achado])
        return fc.fora_do_delta(self.tmp, self.REL, texto, fc.ler_frontmatter(texto)[0], None)

    def test_sem_bloqueante_nao_roda_git(self):
        self.commitar({self.REL: self.parecer("review", self.c1[:7], ["- A1 (bloqueante) src/a.py:5 · x"])})
        chamadas = self.contar_git()
        self.assertEqual(self.revalidar("- A2 (recomendado) src/a.py:2 · sugestão"), [])
        self.assertEqual(chamadas, [])

    def test_varias_versoes_num_lote_so(self):
        self.commitar({self.REL: self.parecer("review", self.c1[:7], ["- A1 (bloqueante) src/a.py:5 · x"])})
        for n in range(3):  # versões do mesmo commit (não são a rodada anterior): o laço passa por todas
            self.commitar({self.REL: self.parecer("review", self.c2[:7], [f"- A{n + 5} (recomendado) src/a.py:2 · v{n}"])})
        chamadas = self.contar_git()
        self.assertEqual(len(self.revalidar("- A2 (bloqueante) src/a.py:2 · novo")), 1)
        self.assertEqual((chamadas.count("cat-file"), chamadas.count("show"), len(chamadas)), (1, 0, 5), chamadas)

    def test_versao_apagada_sai_none_e_o_lote_segue(self):
        com = self.commitar({self.REL: "um\n"})
        git("rm", "-q", self.REL, cwd=self.tmp)
        git("commit", "-q", "-m", "apaga", cwd=self.tmp)
        sem = git("rev-parse", "HEAD", cwd=self.tmp)
        self.assertEqual(fc.versoes_em_lote(self.tmp, [com, sem, com], self.REL), ["um", None, "um"])

    def test_nome_com_quebra_de_linha_nao_vai_ao_lote(self):
        com = self.commitar({self.REL: "um\n"})
        self.assertEqual(fc.versoes_em_lote(self.tmp, [com, com], self.REL + "\nx"), [None, None])

    def test_lote_que_falha_nao_le_nada(self):
        self.falso_git(1, b"abc blob 5\nhello\n")
        self.assertEqual(fc.versoes_em_lote(self.tmp, ["a"], "r.md"), [None])

    def test_cabecalho_sem_fim_de_linha_nao_vira_texto(self):
        self.falso_git(0, b"x blob 5\nhello\nabc blob 12")
        self.assertEqual(fc.versoes_em_lote(self.tmp, ["a", "b"], "r.md"), ["hello", None])

    def test_corpo_truncado_nao_vira_texto_parcial(self):
        self.falso_git(0, b"x blob 9\nhel")
        self.assertEqual(fc.versoes_em_lote(self.tmp, ["a"], "r.md"), [None])

    def test_cabecalho_fora_do_protocolo_nao_le_nada(self):
        self.falso_git(0, b"lixo\nhello\n")
        self.assertEqual(fc.versoes_em_lote(self.tmp, ["a"], "r.md"), [None])


if __name__ == "__main__":
    unittest.main()
