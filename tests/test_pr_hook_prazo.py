"""PR-HOOK-PRAZO (E20.1, v046): o `forge-check pr` grava o resultado por head em `<diretório comum do git>/forge/pr/<head>/`, e o
hook `parecer` decide o `gh pr create` só lendo esse resultado (antes, refazia a checagem: 26 s com carga 22, e o prazo de 3 s recusava).
Sem o aprovado do mesmo head, branch e base, recusa e diz o comando a rodar antes.

Os testes que provam "só lê" rodam o hook com o `cmd_pr` e o `pedidos_da_branch` do `forge-check` trocados por uma saída 97: se o hook
refizesse a checagem, sairia 97 em vez de 0 ou 2."""
import contextlib
import io
import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, git  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, HOOKS, Fixture, modulos_dos_hooks, montar_proc, rodar  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

BASE = FIXTURES / "parecer" / "pr-com-pareceres-aprovados.json"
REFEZ = 97
# O hook como o Claude Code o roda (vigia de prazo de produção), com a checagem cara trocada por `os._exit(97)` e o tempo da decisão
# (do início do processo, com a carga do `forge-check` como módulo, até a saída) gravado no arquivo do 3.o argumento.
LANCADOR_SO_LE = """
import atexit, os, runpy, sys, time
inicio = time.monotonic()
sys.path.insert(0, sys.argv[1])
import _comum
fc = _comum.forge_check()
def refez(*args, **kwargs):
    os._exit(97)
fc.cmd_pr = fc.pedidos_da_branch = refez
destino = sys.argv[3]
atexit.register(lambda: open(destino, "w").write(str(time.monotonic() - inicio)))
sys.argv = [sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""
# A1 do review (E20.11): o mesmo hook com a conferência de hoje (`cmd_pr`) lenta, para o vigia de produção vencer nela.
LANCADOR_LENTO = """
import runpy, sys, time
sys.path.insert(0, sys.argv[1])
import _comum
_comum.forge_check().cmd_pr = lambda *args, **kwargs: time.sleep(60)
sys.argv = [sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
"""


def forge_check(raiz, *args):
    return subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), *args], cwd=raiz, env=ambiente_limpo(),
                          capture_output=True, text=True, timeout=300)


def registros(raiz):
    head = git("rev-parse", "HEAD", cwd=raiz).stdout.strip()
    pasta = raiz / ".git" / "forge" / "pr" / head
    return pasta, [json.loads(p.read_text(encoding="utf-8")) for p in sorted(pasta.glob("*.json"))] if pasta.is_dir() else []


class PrHookPrazo(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria

    def montar(self, com_resultado=True):
        """O fixture de review e QA aprovados (feature/x, pedido p1); com `com_resultado`, o aprovado gravado (`resultado_do_pr`)."""
        dados = json.loads(BASE.read_text(encoding="utf-8"))
        self.assertEqual(dados.pop("resultado_do_pr"), {"pedido": "p1", "base": "develop"})
        if com_resultado:
            dados["resultado_do_pr"] = {"pedido": "p1", "base": "develop"}
        self.tmp = self._pasta_temporaria()
        f = Fixture(self.tmp / "parecer" / "caso.json", dados)
        raiz, self.entrada = f.montar(self.tmp, os.getpid())
        f.executar_passos(raiz, None)
        return raiz

    def hook(self, raiz, comando=None):
        entrada = dict(self.entrada, tool_input={"command": comando}) if comando else self.entrada
        return rodar("parecer", entrada, raiz, montar_proc(self._pasta_temporaria(), None), {})

    def hook_so_lendo(self, raiz):
        """(resultado, segundos da decisão) com a checagem cara proibida e o prazo de produção."""
        tempo = self._pasta_temporaria() / "tempo"
        lancador = [sys.executable, "-c", LANCADOR_SO_LE, str(HOOKS), str(HOOKS / "parecer.py"), str(tempo)]
        with mock.patch.object(test_hooks, "lancador", lambda *a: lancador):
            r = rodar("parecer", self.entrada, raiz, montar_proc(self._pasta_temporaria(), None), {}, producao=True)
        return r, float(tempo.read_text(encoding="utf-8")) if tempo.exists() else None

    def hook_lento(self, raiz):
        """O hook com o vigia de produção e o `cmd_pr` lento: o prazo vence na conferência de hoje."""
        lancador = [sys.executable, "-I", "-c", LANCADOR_LENTO, str(HOOKS), str(HOOKS / "parecer.py")]
        with mock.patch.object(test_hooks, "lancador", lambda *a: lancador):
            return rodar("parecer", self.entrada, raiz, montar_proc(self._pasta_temporaria(), None), {}, producao=True)

    def um_registro(self, raiz):
        """(pasta, o registro do head): conta antes de desempacotar, para a base sem gravação falhar por asserção (A1 do QA, E20.11)."""
        pasta, lista = registros(raiz)
        self.assertEqual(len(lista), 1, "um registro gravado para o head")
        return pasta, lista[0]

    def test_aprovado_do_head_libera_so_lendo_dentro_do_prazo(self):
        raiz = self.montar()
        r, segundos = self.hook_so_lendo(raiz)
        self.assertEqual((r.returncode, r.stderr), (0, ""), "libera sem refazer a checagem (97 = refez)")
        _comum = modulos_dos_hooks()[0]
        self.assertLess(segundos, _comum.PRAZO_DA_DECISAO_S, "a decisão só lendo cabe no prazo de produção")

    def test_reprovado_do_head_recusa_so_lendo(self):
        raiz = self.montar()
        fc = modulos_dos_hooks()[0].forge_check()
        fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", ["docs/qa/p1.md: parecer: reprovado (R-QA)"])
        r, _ = self.hook_so_lendo(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-REVIEW: forge-check pr p1 reprovou o head", r.stderr)
        self.assertIn("docs/qa/p1.md: parecer: reprovado", r.stderr)

    def test_head_diferente_recusa_e_diz_o_comando(self):
        raiz = self.montar()
        git("commit", "-q", "--allow-empty", "-m", "outro head", cwd=raiz)
        r = self.hook(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        novo = git("rev-parse", "--short=7", "HEAD", cwd=raiz).stdout.strip()
        self.assertIn(f"sem resultado aprovado do forge-check pr para o head {novo}", r.stderr)
        self.assertIn("rode antes forge-check pr <pedido> --ref feature/x --base develop", r.stderr)

    def test_sem_resultado_recusa_mesmo_sem_violacao(self):
        raiz = self.montar(com_resultado=False)
        r = self.hook(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-REVIEW: sem resultado aprovado do forge-check pr", r.stderr)

    def test_resultado_de_outra_base_recusa(self):
        raiz = self.montar(com_resultado=False)
        fc = modulos_dos_hooks()[0].forge_check()
        fc.gravar_resultado_do_pr(raiz, "p1", None, None, [])  # o modo estrito, sem base: o PR pede a develop
        self.assertEqual([r["resultado"] for r in registros(raiz)[1]], ["aprovado"])
        r = self.hook(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("sem resultado aprovado do forge-check pr", r.stderr)

    def test_ilegivel_de_outra_branch_ou_de_outro_head_nao_vale(self):
        raiz = self.montar()
        pasta, registro = self.um_registro(raiz)
        aprovado = next(pasta.glob("*.json"))
        for nome, mudanca in (("outra branch", {"branch": "feature/y"}), ("outro head", {"head": "0" * 40}),
                              ("resultado estranho", {"resultado": "sim"}), ("outro escritor", {"escritor": "0" * 64}),
                              ("sem escritor", {"escritor": None})):
            with self.subTest(nome):
                aprovado.write_text(json.dumps({**registro, **mudanca}), encoding="utf-8")
                self.assertEqual(self.hook(raiz).returncode, 2)
        (pasta / "lixo.json").write_text("{", encoding="utf-8")
        aprovado.write_text(json.dumps(registro), encoding="utf-8")
        self.assertEqual(self.hook(raiz).returncode, 0, "o ilegível ao lado não derruba o aprovado")

    def test_pedido_da_branch_sem_resultado_recusa(self):
        raiz = self.montar()
        pasta, registro = self.um_registro(raiz)
        next(pasta.glob("*.json")).write_text(json.dumps({**registro, "pedidos_da_branch": ["p1", "p2"]}), encoding="utf-8")
        r = self.hook(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("sem resultado aprovado", r.stderr)

    def test_branch_sem_pedido_gravado_recusa(self):
        raiz = self.montar()
        pasta, registro = self.um_registro(raiz)
        next(pasta.glob("*.json")).write_text(json.dumps({**registro, "pedidos_da_branch": []}), encoding="utf-8")
        r, _ = self.hook_so_lendo(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("nenhum parecer com `branch: feature/x`", r.stderr)

    def test_pedidos_da_branch_malformado_nao_derruba_a_leitura(self):
        """`pedidos_da_branch` que não é lista vale como sem pedido (recusa); o item que não é texto é ignorado."""
        raiz = self.montar()
        pasta, registro = self.um_registro(raiz)
        for nome, pedidos, codigo, trecho in (("nulo", None, 2, "R-REVIEW: nenhum parecer com `branch: feature/x`"),
                                              ("item numérico", [1, "p1"], 0, "")):
            with self.subTest(nome):
                next(pasta.glob("*.json")).write_text(json.dumps({**registro, "pedidos_da_branch": pedidos}), encoding="utf-8")
                r = self.hook(raiz)
                self.assertEqual(r.returncode, codigo, r.stderr)
                self.assertTrue(r.stderr.startswith(trecho) and (codigo or not r.stderr), r.stderr)

    def test_merge_segue_a_conferencia_de_sempre(self):
        """O resultado gravado só decide o `gh pr create`: o `git merge` na develop confere como antes (com a checagem proibida, 97)."""
        raiz = self.montar()
        self.entrada = dict(self.entrada, tool_input={"command": "git merge feature/x"})
        git("switch", "-q", "develop", cwd=raiz)
        r, _ = self.hook_so_lendo(raiz)
        self.assertEqual(r.returncode, REFEZ, r.stderr)

    def test_prazo_vencido_diz_rode_antes_so_no_pr_create_sem_resultado(self):
        """A1 do review (E20.11): o prazo vencido na conferência de hoje do `gh pr create` sem resultado diz o comando que o grava;
        no merge, que não lê o resultado gravado, segue o contorno de sempre."""
        raiz = self.montar(com_resultado=False)
        r = self.hook_lento(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-REVIEW: o hook não decidiu", r.stderr)
        self.assertIn("Corrigir: rode antes forge-check pr", r.stderr)
        self.entrada = dict(self.entrada, tool_input={"command": "git merge feature/x"})
        git("switch", "-q", "develop", cwd=raiz)
        r = self.hook_lento(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn(f"Corrigir: {modulos_dos_hooks()[0].CONTORNO_DO_TETO[:20]}", r.stderr)  # a recusa corta em 200 caracteres
        self.assertNotIn("rode antes", r.stderr)


class GravacaoDoForgeCheck(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    montar = PrHookPrazo.montar
    hook_so_lendo = PrHookPrazo.hook_so_lendo
    um_registro = PrHookPrazo.um_registro

    def test_pr_grava_o_reprovado_e_o_hook_o_le(self):
        raiz = self.montar(com_resultado=False)
        r = forge_check(raiz, "pr", "p1", "--base", "develop")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)  # sem a conferência de entrega do pedido
        pasta, registro = self.um_registro(raiz)
        head = git("rev-parse", "HEAD", cwd=raiz).stdout.strip()
        develop = git("rev-parse", "develop", cwd=raiz).stdout.strip()
        self.assertEqual({k: registro[k] for k in ("contrato", "resultado", "pedido", "branch", "head", "base_sha", "pedidos_da_branch")},
                         {"contrato": 1, "resultado": "reprovado", "pedido": "p1", "branch": "feature/x", "head": head,
                          "base_sha": develop, "pedidos_da_branch": ["p1"]})
        self.assertTrue(str(registro["violacao"]).startswith("pr: conferência:"), registro["violacao"])
        self.assertEqual(pasta.stat().st_mode & 0o777, 0o700)
        r, _ = self.hook_so_lendo(raiz)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("reprovou o head", r.stderr)

    def test_pr_aprovado_grava_e_o_hook_libera_so_lendo(self):
        raiz = self.montar(com_resultado=False)
        conferido = git("rev-parse", "HEAD~1", cwd=raiz).stdout.strip()  # o commit do código; depois dele, só os pareceres
        pedido = raiz / "docs" / "pedidos" / "p1.md"
        pedido.parent.mkdir(parents=True)
        pedido.write_text(f"# p1\n\n## Histórico\n- 2026-11-11 10:00: entrega conferida {conferido}\n", encoding="utf-8")
        r = forge_check(raiz, "pr", "p1", "--base", "develop")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual([x["resultado"] for x in registros(raiz)[1]], ["aprovado"])
        r, _ = self.hook_so_lendo(raiz)
        self.assertEqual((r.returncode, r.stderr), (0, ""))

    def test_previo_e_head_sem_branch_nao_gravam(self):
        raiz = self.montar(com_resultado=False)
        forge_check(raiz, "pr", "p1", "--base", "develop", "--previo")
        self.assertEqual(registros(raiz)[1], [], "o pré-voo não é veredito")
        git("switch", "-q", "--detach", cwd=raiz)
        r = forge_check(raiz, "pr", "p1", "--base", "develop")
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(registros(raiz)[1], [], "sem branch, o hook não teria o que casar")

    def test_ref_ou_base_que_nao_resolvem_sao_ausentes(self):
        raiz = self.montar(com_resultado=False)
        fc = modulos_dos_hooks()[0].forge_check()
        fc.gravar_resultado_do_pr(raiz, "p1", None, None, [])  # aprovado no modo estrito: base_sha nulo

        def estado(ref, base):  # a exceção vira valor: o ramo de falha é conferido por asserção, não por erro do teste
            try:
                return fc.resultado_gravado_do_pr(raiz, "feature/x", ref, base)[0]
            except Exception as erro:  # noqa: BLE001
                return repr(erro)
        self.assertEqual(estado(None, None), "aprovado")
        self.assertEqual(estado(None, "refs/heads/nao-existe"), "ausente")
        self.assertEqual(estado("nao-existe", None), "ausente")
        motivo = fc.resultado_gravado_do_pr(raiz, "feature/x", "nao-existe", None)[1]  # sem head nem base dada: o comando sem --base
        self.assertIn("para o head ? da branch feature/x", motivo)
        self.assertTrue(motivo.endswith("rode antes forge-check pr <pedido> --ref feature/x"), motivo)

    def test_falha_ao_gravar_avisa_e_nao_muda_o_codigo(self):
        raiz = self.montar(com_resultado=False)
        (raiz / ".git" / "forge").write_text("não é pasta\n", encoding="utf-8")
        r = forge_check(raiz, "pr", "p1", "--base", "develop")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("pr: aviso: resultado não gravado para o hook", r.stderr)
        self.assertRegex(r.stderr, r"resultado não gravado para o hook \([^)\[]+\)")  # o motivo curto do sistema, sem o caminho
        self.assertNotIn("resultados antigos", r.stderr, "sem gravar, não poda")

    def test_gravar_poda_os_heads_que_nao_sao_mais_ponta(self):
        """A3 do review (E20.11): gravar apaga a pasta do head que deixou de ser ponta de branch; ficam a gravada, a de ponta de outra
        branch e o que não é pasta de head. Sem a lista das pontas, nada se apaga; a falha ao apagar só avisa."""
        raiz = self.montar(com_resultado=False)
        fc = modulos_dos_hooks()[0].forge_check()
        fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", [])
        velha, _ = self.um_registro(raiz)
        develop = git("rev-parse", "develop", cwd=raiz).stdout.strip()
        orfa, ponta, alheia = velha.parent / ("0" * 40), velha.parent / develop, velha.parent / "nao-e-head"
        for pasta in (orfa, ponta, alheia):
            pasta.mkdir()
            (pasta / "x.json").write_text("{}", encoding="utf-8")
        git("commit", "-q", "--allow-empty", "-m", "outro head", cwd=raiz)
        git_de_verdade = fc.git
        sem_pontas = lambda r, *args, **kw: (1, "") if args[0] == "for-each-ref" else git_de_verdade(r, *args, **kw)  # noqa: E731
        with mock.patch.object(fc, "git", sem_pontas):
            fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", [])
        self.assertTrue(orfa.is_dir() and velha.is_dir(), "sem a lista das pontas, não apaga")
        (orfa / "sub").mkdir()
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro):
            try:  # a exceção vira texto: o ramo de falha é conferido por asserção, não por erro do teste
                fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", [])
            except OSError as e:
                erro.write(f"exceção: {e!r}")
        self.assertRegex(erro.getvalue(), r"pr: aviso: resultados antigos não apagados \([^)\[]+\)")  # o motivo curto, sem o caminho
        (orfa / "sub").rmdir()
        fc.gravar_resultado_do_pr(raiz, "p1", None, "develop", [])
        nova, _ = self.um_registro(raiz)
        self.assertEqual(sorted(p.name for p in velha.parent.iterdir()), sorted([nova.name, develop, "nao-e-head"]))


if __name__ == "__main__":
    unittest.main()
