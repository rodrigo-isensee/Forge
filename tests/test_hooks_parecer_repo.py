"""0.47.8 E3.1: as fixtures `incidente-r-*` e `leitura-api-*` do hook `parecer` (tests/hooks/parecer/).

INCIDENTE-HOOK-PARECER-CONTORNADO: `gh pr ready`, `gh pr merge` e `gh pr create` fora de um repositório git, com
`-R`/`--repo`, `GH_REPO=` ou a URL do PR, passavam sem conferência (o hook só achava raiz pela pasta). Agora o hook confere
no clone da sessão (`CLAUDE_PROJECT_DIR`) que tem remoto desse repositório e recusa quando não o acha (falha fechada).
GH-API-LEITURA-UNICA: a leitura dos arquivos do `gh api` (`hooks/_gh_api.py`) lê o mesmo arquivo que o gh ou recusa:
`~` no começo do caminho, curinga e o `@` de `--input=@arq` (que é parte do nome).
Roda a mesma máquina do `tests/test_hooks.py`; existe à parte para os mutantes de `tests/mutantes/` rodarem rápido."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, Fixture  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
import _gh_api  # noqa: E402


class ParecerForaDoRepo(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def rodar(self, padrao, total):
        fixtures = minimo([Fixture(p) for p in sorted((FIXTURES / "parecer").glob(padrao))], total, padrao)
        lados = {f.dados["esperado"]["codigo"] for f in fixtures}
        self.assertEqual(lados, {0, 2}, "o corpus tem os dois lados: o que passa e o que barra")
        casos = [(f"parecer/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(fixtures), "toda fixture é verificada")

    def test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao(self):
        self.rodar("incidente-r-*.json", 38)

    def test_leitura_dos_arquivos_do_gh_api(self):
        self.rodar("leitura-api-*.json", 9)

    def test_graphql_fora_do_clone_e_arquivo_trocado_na_linha(self):
        """GRAPHQL-FORA-DO-CLONE e GH-API-ARQUIVO-TROCADO (A3 e A4 da E3.4): o graphql não usa a pasta, e a linha com
        outro comando pode trocar o arquivo da consulta depois da leitura do hook."""
        self.rodar("graphql-*.json", 6)


class TamanhoNaAbertura(unittest.TestCase):
    """F5.2 (v0481 E38.4, docs/arquitetura/f5-tamanho-pela-ferramenta.md): no clone do Forge, o `gh pr create` para a develop, com
    ou sem `--draft`, acima do teto do H1 recusa com o corte sugerido; a exceção só vale no `--body-file` comum, na cópia, até 64 KiB.
    Cada caso é a fixture `tamanho-rascunho-151-bloqueia` (151 linhas de código) com o comando, os arquivos e o esperado trocados."""
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)
    MODELO = FIXTURES / "parecer" / "tamanho-rascunho-151-bloqueia.json"
    EXCECAO = "teto: excedido, 151 linhas, cortar mais deixa a suíte vermelha\n"
    RECUSA = "R-REVIEW: 151 linhas de código acima do teto de 150 por item"

    def caso(self, nome, opcoes, codigo, stderr=None, arquivos=None, linhas=151, sem=None, entrada_antes="", **extra):
        dados = json.loads(self.MODELO.read_text(encoding="utf-8"))
        dados["arquivos"].update(arquivos or {})
        dados["git"][1]["arquivos"]["src/b.py"] = ["x"] * (linhas - 2)  # mais as 2 do src/app.py
        dados["entrada"]["tool_input"]["command"] = f"{entrada_antes}gh pr create --title t {opcoes}"
        dados["esperado"] = {"codigo": codigo, **({"stderr": stderr} if stderr else {}), **({"stderr_sem": sem} if sem else {})}
        dados.update(extra)
        return (f"parecer/tamanho-{nome}", Fixture(FIXTURES / "parecer" / f"tamanho-{nome}.json", dados))

    def rodar(self, casos):
        self.assertEqual(self.executar_em_lote(casos), len(casos), "todo caso é verificado")

    def test_rascunho_e_pr_normal_acima_do_teto_recusam_e_no_teto_passam(self):
        self.rodar([
            self.caso("rascunho-150", "--draft --base develop --body x", 0, linhas=150),
            self.caso("rascunho-151", "--draft --base develop --body x", 2, f"{self.RECUSA} (H1, decisão do dono 17/11 11:15); corte"),
            self.caso("normal-151", "--base develop --body x", 2, self.RECUSA),  # antes da conferência do parecer
            self.caso("normal-150", "--base develop --body x", 2, "nenhum parecer", linhas=150, sem=["acima do teto"]),
            self.caso("rascunho-151-origin", "--draft -B origin/develop --body x", 2, self.RECUSA),
        ])

    def test_excecao_so_no_body_file_comum_da_copia_com_o_total(self):
        self.rodar([
            self.caso("body-file", "--draft --base develop --body-file c.md", 0, arquivos={"c.md": self.EXCECAO}),
            self.caso("body-file-igual", "--draft --base develop --body-file=c.md", 0, arquivos={"c.md": self.EXCECAO}),
            self.caso("body-file-curto", "--draft --base develop -Fc.md", 0, arquivos={"c.md": self.EXCECAO}),
            self.caso("body-file-absoluto", "--draft --base develop -F {raiz}/c.md", 0, arquivos={"c.md": self.EXCECAO}),
            self.caso("excecao-menor", "--draft --base develop -F c.md", 2, self.RECUSA,
                      arquivos={"c.md": "teto: excedido, 150 linhas, motivo\n"}),
            self.caso("ultimo-vale", "--draft --base develop -F c.md -F d.md", 2, self.RECUSA,
                      arquivos={"c.md": self.EXCECAO, "d.md": "sem\n"}),
            self.caso("stdin", "--draft --base develop -F -", 2, self.RECUSA, arquivos={"-": self.EXCECAO}),
            self.caso("expansao", "--draft --base develop -F '$X.md'", 2, self.RECUSA, arquivos={"$X.md": self.EXCECAO}),
            self.caso("body", f"--draft --base develop --body '{self.EXCECAO.strip()}'", 2, self.RECUSA),
            self.caso("link", "--draft --base develop -F l.md", 2, self.RECUSA, arquivos={"c.md": self.EXCECAO},
                      links={"l.md": "{raiz}/c.md"}),
            self.caso("grande", "--draft --base develop -F c.md", 2, self.RECUSA,
                      arquivos={"c.md": self.EXCECAO + "x" * (64 * 1024)}),
            self.caso("fora-da-copia", "--draft --base develop -F {tmp}/fora.md", 2, self.RECUSA,
                      passos=[{"gravar": {"{tmp}/fora.md": self.EXCECAO}}]),
            self.caso("pasta", "--draft --base develop -F c.md", 2, self.RECUSA, arquivos={"c.md/x": self.EXCECAO}),
            self.caso("f-sem-valor", "--draft --base develop --body x -F", 2, self.RECUSA),
            self.caso("valor-de-outra-opcao", "--draft --base develop --body -Fc.md", 2, self.RECUSA,
                      arquivos={"c.md": self.EXCECAO}),  # `-Fc.md` é o texto do --body, não o arquivo
            self.caso("cd-incerto-absoluto", "--draft --base develop -F {raiz}/c.md", 0, arquivos={"c.md": self.EXCECAO},
                      entrada_antes='cd "$NADA"; '),
            self.caso("cd-incerto-relativo", "--draft --base develop -F c.md", 2, self.RECUSA, arquivos={"c.md": self.EXCECAO},
                      entrada_antes='cd "$NADA"; '),
        ])

    def test_fora_da_develop_e_no_projeto_nao_confere_e_git_que_falha_recusa(self):
        self.rodar([
            self.caso("homolog", "--draft --base homolog --body x", 0),
            self.caso("sem-base", "--draft --body x", 0),
            self.caso("integracao", "--draft --base develop --head homolog --body x", 0),  # promoção: nem lê o diff
            self.caso("projeto", "--draft --base develop --body x", 2, "nenhum parecer", sem=["acima do teto"], forge=True),
            self.caso("head-ausente", "--draft --base develop --head feature/nada --body x", 2,
                      "R-REVIEW: branch `feature/nada` não existe localmente, sem tamanho a conferir"),
            self.caso("sem-develop", "--draft --base develop --body x", 2,
                      "R-REVIEW: tamanho não conferido: o git não leu o diff origin/develop...HEAD",
                      passos=[{"git": ["branch", "-D", "develop"]}]),
        ])

    def test_recusa_em_uma_linha_de_ate_200_caracteres(self):
        _, fixture = self.caso("uma-linha", "--draft --base develop --body x", 2)
        tmp = self._pasta_temporaria()
        raiz, entrada = fixture.montar(tmp, os.getpid())
        r = test_hooks.rodar("parecer", entrada, raiz, test_hooks.montar_proc(tmp, None), {"FORGE_NPROC": "8"})
        self.assertEqual(r.returncode, 2, r.stderr)
        linhas = r.stderr.strip().splitlines()
        self.assertEqual(len(linhas), 1, r.stderr)
        self.assertLessEqual(len(linhas[0]), 200)
        self.assertIn("corte sugerido: PR 1", linhas[0])


class TamanhoComGitLento(unittest.TestCase):
    """Nota da segurança do F5.1 para o F5.2: o `TimeoutExpired` do git em `corte_do_intervalo` (ou no `numstat`) recusa a abertura
    com o motivo, em vez de subir como erro interno (ADR 0009, seção 7)."""

    def test_git_que_passa_do_prazo_recusa(self):
        _, _, parecer = test_hooks.modulos_dos_hooks()
        lento = mock.Mock(side_effect=subprocess.TimeoutExpired(["git", "diff"], 5))
        fc = SimpleNamespace(base_da_entrega=lambda *a, **k: "origin/develop", tamanho_na_abertura=lento)
        with mock.patch.object(parecer, "forge_check", return_value=fc), \
                mock.patch.object(parecer, "git", return_value=(0, "melhoria/x")), \
                mock.patch.object(parecer, "bloquear", side_effect=SystemExit(2)) as bloquear, \
                self.assertRaises(SystemExit):
            parecer.tamanho_da_abertura("/nada", None, (None, None))
        bloquear.assert_called_once_with(
            "R-REVIEW", "tamanho não conferido: o git passou do prazo no diff origin/develop...HEAD; tente de novo")



    """`textos_do_gh_api` direto: o arquivo lido é o que o gh lê."""

    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pasta)
        for nome, texto in (("q", "consulta"), ("query=@q", "nome com =@")):
            with open(os.path.join(self.pasta, nome), "w", encoding="utf-8") as f:
                f.write(texto)

    def test_campo_longo_com_igual_le_o_arquivo_depois_do_arroba(self):
        """`--field=query=@q`: o gh lê `q`; antes, o hook procurava `query=@q` e recusava o que o gh aceita."""
        textos, legivel = _gh_api.textos_do_gh_api(["graphql", "--field=query=@q"], self.pasta)
        self.assertTrue(legivel)
        self.assertIn("consulta", textos)

    def test_pasta_desconhecida_com_relativo_e_ilegivel(self):
        self.assertFalse(_gh_api.textos_do_gh_api(["graphql", "-F", "query=@q"], None)[1])
        self.assertTrue(_gh_api.textos_do_gh_api(["graphql", "-F", "query=@q"], self.pasta)[1])


if __name__ == "__main__":
    unittest.main()
