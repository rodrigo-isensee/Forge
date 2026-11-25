"""D2-PORTAO-ENTREGA-AUTOR (v0481 E11.1): o `forge-check pronto`, o portão de entrega do autor (bin/forge_pronto.py).

As checagens externas são as que já existem (forge-testes e as classes de neutralidade); aqui o teste prova o agregador com comandos
falsos, o teto e o corpo com o pr-texto falso, e o `cmd_pronto` de verdade num repositório descartável (base ausente, corpo ilegível,
corpo nenhum).
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_pronto  # noqa: E402

sys.path.insert(0, str(RAIZ / "tests"))
from ambiente_git import sem_manutencao  # noqa: E402

PY = sys.executable
OK, FALHA = (PY, "-I", "-c", "pass"), (PY, "-I", "-c", "import sys; print('saida da falha'); sys.exit(3)")
CORPO_COM_MOTIVO = "teto: excedido, 151 linhas, cortar mais quebra a suíte\n"
# gh falso: só o `gh pr view develop --json ...` com o nome exato da branch (checklist 12); outra chamada sai 3.
GH = '#!/bin/sh\n[ "$1 $2 $3" = "pr view develop" ] || exit 3\n'
SEM_PR = GH + 'echo "no pull requests found for branch" >&2\nexit 1\n'
COM_PR = GH + 'echo \'{"number": 7, "state": "%s", "headRefOid": "x", "body": "corpo do pr"}\'\n'
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_", "GH_", "GITHUB_"))})


def conferir(lista, falhas=()):
    saida, erro = io.StringIO(), io.StringIO()
    with mock.patch.object(forge_pronto, "tamanho_e_corpo", return_value=list(falhas)), \
            mock.patch.object(forge_pronto, "passos", return_value=[("dos passos", FALHA)]), \
            contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
        rc = forge_pronto.conferir(".", "origin/develop", "abc", 10, "", lista)
    return rc, saida.getvalue(), erro.getvalue()


class Agregador(unittest.TestCase):
    def test_tudo_passa_sai_0(self):
        rc, saida, _ = conferir([("a", OK), ("b", OK)])
        self.assertEqual(rc, 0)
        self.assertIn("pronto: a: ok", saida)
        self.assertIn("tudo passou", saida)

    def test_uma_checagem_reprovada_sai_1_e_mostra_a_saida(self):
        rc, saida, erro = conferir([("a", OK), ("b", FALHA)])
        self.assertEqual(rc, 1)
        self.assertIn("pronto: b: reprovado (saída 3)", saida)
        self.assertIn("reprovado em b;", saida)
        self.assertIn("saida da falha", erro)

    def test_teto_ou_corpo_reprovado_sai_1(self):
        rc, saida, erro = conferir([("a", OK)], ["falha do corpo"])
        self.assertEqual(rc, 1)
        self.assertIn("reprovado em tamanho e corpo do PR", saida)
        self.assertIn("pronto: tamanho e corpo do PR (10 linhas de código): reprovado", saida)
        self.assertIn("pronto: falha do corpo", erro)

    def test_comando_que_nao_abre_sai_2(self):
        self.assertEqual(forge_pronto.rodar(".", ["/nao/existe/comando"])[0], 2)

    def test_passos_cobrem_as_checagens_do_cartao(self):
        lista = dict(forge_pronto.passos("origin/x"))
        self.assertEqual(list(lista), ["registros", "neutralidade", "texto", "testes"])
        self.assertIn("tests.test_forge.NeutralidadeDoNucleo", lista["neutralidade"])
        self.assertEqual(lista["testes"][-2:], ["--base", "origin/x"])


class TamanhoECorpo(unittest.TestCase):
    def falhas(self, total, corpo, rc=0):
        with mock.patch.object(forge_pronto, "rodar", return_value=(rc, "violação do pr-texto")) as rodar:
            return forge_pronto.tamanho_e_corpo(".", "abc", total, corpo), rodar

    def test_sem_corpo_reprova_sem_rodar_a_catraca(self):
        falhas, rodar = self.falhas(10, None)
        self.assertEqual(len(falhas), 1)
        self.assertIn("--corpo", falhas[0])
        rodar.assert_not_called()

    def test_acima_do_teto_sem_motivo_reprova(self):
        falhas, _ = self.falhas(151, "corpo")
        self.assertEqual(len(falhas), 1)
        self.assertIn("tamanho: 151 linhas", falhas[0])

    def test_acima_do_teto_com_motivo_e_no_teto_passam(self):
        self.assertEqual(self.falhas(151, CORPO_COM_MOTIVO)[0], [])
        self.assertEqual(self.falhas(150, "corpo")[0], [])

    def test_pr_texto_reprovado_reprova_com_o_corpo_no_ambiente(self):
        falhas, rodar = self.falhas(10, "corpo", rc=1)
        self.assertEqual(len(falhas), 1)
        self.assertIn("violação do pr-texto", falhas[0])
        self.assertEqual(rodar.call_args.args[2]["PR_BODY"], "corpo")


class CmdPronto(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.dir)])
        for args in (["init", "-q", "-b", "develop"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
                                                         "-m", "base"]):
            subprocess.run(["git", "-C", str(self.dir), *args], check=True, env=AMBIENTE)

    def pronto(self, *args, gh=SEM_PR):
        falsos = self.dir / "falsos"
        falsos.mkdir(exist_ok=True)
        (falsos / "gh").write_text(gh, encoding="utf-8")
        (falsos / "gh").chmod(0o755)
        env = dict(AMBIENTE, PATH=f"{falsos}{os.pathsep}{AMBIENTE.get('PATH', '')}")
        return subprocess.run([PY, "-I", str(RAIZ / "bin" / "forge-check"), "--raiz", str(self.dir), "pronto", *args],
                              capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, cwd=self.dir)

    def test_base_ausente_sai_2(self):
        r = self.pronto("--base", "nao-existe")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("não verificável", r.stderr)

    def test_corpo_ilegivel_sai_2(self):
        r = self.pronto("--base", "develop", "--corpo", str(self.dir / "sem-arquivo.md"))
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("ilegível", r.stderr)

    def test_corpo_do_arquivo_chega_ao_portao(self):
        (self.dir / "corpo.md").write_text("o corpo", encoding="utf-8")
        r = self.pronto("--base", "develop", "--corpo", str(self.dir / "corpo.md"))
        self.assertIn("pronto: tamanho e corpo do PR (0 linhas de código)", r.stdout, r.stderr)
        self.assertNotIn("corpo do PR não conferido", r.stderr)

    def test_sem_corpo_e_sem_pr_reprova(self):
        r = self.pronto("--base", "develop")
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn("corpo do PR não conferido", r.stderr)

    def test_pr_aberto_da_o_corpo_e_fechado_nao(self):
        r = self.pronto("--base", "develop", gh=COM_PR % "OPEN")
        self.assertNotIn("corpo do PR não conferido", r.stderr)
        self.assertIn("pronto: tamanho e corpo do PR (0 linhas de código)", r.stdout, r.stderr)
        r = self.pronto("--base", "develop", gh=COM_PR % "CLOSED")
        self.assertIn("corpo do PR não conferido", r.stderr)
