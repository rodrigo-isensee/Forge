"""v046 (E14.1): o hook `pesado` reconhece a bateria atrás de `timeout`, `nice`, `env` e por caminho (B4) e libera a vez
de processo morto, zumbi, de pid reaproveitado ou de sessão que acabou na fila (PROCESSO-ORFAO)."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
import _comum  # noqa: E402
import pesado  # noqa: E402

FORGE = pesado.PESADOS_DO_FORGE


def inicios_da_base(palavras):
    """A regra da base (develop 2b896503, antes do B4), copiada aqui congelada: o diferencial compara com ela."""
    palavras, saida, i = pesado.sem_atribuicoes([p.lower() for p in palavras]), [], 0
    while i < len(palavras):
        saida.append(" ".join(palavras[i:]))
        if palavras[i] in pesado.LANCADORES or pesado.re.match(r"^[a-z_][a-z0-9_]*=", palavras[i]):
            i += 1
        elif palavras[i] in pesado.GERENCIADORES and palavras[i + 1: i + 2] and palavras[i + 1] in pesado.SUBCOMANDOS_DE_LANCE:
            i += 2
        else:
            break
    return saida


def leve_da_base(inicio):
    nome, *argumentos = inicio.split()
    if nome in pesado.PELOS_ARGUMENTOS[:2]:
        return not any(pesado.pede_opcao(a, o) for a in argumentos for o in ("--completa", "--vermelho"))
    return argumentos == ["--listar"]


def casa_da_base(inicio, padrao):
    if padrao in pesado.PELOS_ARGUMENTOS:
        return inicio.split()[:1] == [padrao] and not leve_da_base(inicio)
    return inicio == padrao or inicio.startswith(padrao + " ")


def pesado_da_base(comando, padroes):
    padroes = [pesado.normalizar(p) for p in padroes]
    if not any(p in pesado.normalizar(comando) for p in padroes):
        return False
    partes = [inicios_da_base(palavras) for leitura in pesado.leituras(comando).partes for palavras, _, _ in leitura]
    return any(casa_da_base(t, p) for inicio in partes for t in inicio for p in padroes)


# Padrões de projeto que começam por cada lançador da tabela do `_comum` (`nice make test`, `timeout 600 make test`).
PADROES_COM_LANCADOR = [f"{nome} make test" for nome in _comum.LANCADORES] + [
    "timeout 600 make test", "nice -n 10 make test", "sudo -u ci make test", "time npm test", "env CI=1 npm test"]


class B4(unittest.TestCase):
    def test_atras_de_lancador_com_opcoes(self):
        for comando in ("timeout 600 python3 -m unittest discover", "timeout -s KILL 600 .githooks/pre-push --suite",
                        "timeout --signal=TERM 5m bin/forge-testes --completa", "nice -n 10 python3 -m unittest discover",
                        "env -i FOO=1 python3 -m unittest discover", "env -u X .githooks/pre-push --suite",
                        "/usr/bin/timeout 60 bin/forge-mutante x.json",
                        "timeout 60 nice -n 5 env A=1 /abs/bin/forge-testes --completa"):
            with self.subTest(comando=comando):
                self.assertTrue(pesado.pesado(comando, FORGE))

    def test_por_caminho_absoluto_ou_relativo(self):
        for comando in ("/x/bin/forge-testes --completa", "./.githooks/pre-push --suite", "/w/wt/.githooks/pre-push --suite",
                        "python3 /w/scripts/suite-paralela.py", "/usr/bin/python3 -m unittest discover",
                        "../wt/bin/forge-mutante t.json"):
            with self.subTest(comando=comando):
                self.assertTrue(pesado.pesado(comando, FORGE))

    def test_padrao_do_projeto_com_pasta_no_meio(self):
        self.assertTrue(pesado.pesado("pytest /abs/tests/e2e -x", ["pytest tests/e2e"]))
        self.assertFalse(pesado.pesado("pytest /abs/tests/e2ex", ["pytest tests/e2e"]), "palavra inteira, não sufixo")

    def test_padrao_do_projeto_que_comeca_por_lancador(self):
        self.assertGreaterEqual(len(_comum.LANCADORES), 12)
        for padrao in PADROES_COM_LANCADOR:
            for comando in (padrao, f"cd x && {padrao} -k y"):
                with self.subTest(padrao=padrao, comando=comando):
                    self.assertTrue(pesado.pesado(comando, [padrao]))

    def test_nada_pesado_na_base_vira_leve(self):
        """Diferencial: o corpus (formas da base, do B4 e padrões de projeto com lançador) pela regra congelada da base e
        pela do head; o pesado na base segue pesado."""
        projeto = PADROES_COM_LANCADOR + ["make test", "npm test", "pytest tests/e2e"]
        corpus = [*FORGE, *projeto, *(f"{p} --completa" for p in FORGE), *(f"{nome} {p}" for nome in _comum.LANCADORES
                                                                         for p in FORGE + projeto),
                  *(f"FOO=1 {p} -x" for p in projeto), "npx make test", "pnpm exec make test", "timeout 60 nice -n 5 make test",
                  "/x/bin/forge-testes --completa", "bin/forge-mutante --listar", "./bin/forge-testes tests/a.py"]
        pesados_na_base = 0
        for comando in corpus:
            for padroes in (FORGE, projeto):
                if pesado_da_base(comando, padroes):
                    pesados_na_base += 1
                    with self.subTest(comando=comando):
                        self.assertTrue(pesado.pesado(comando, padroes), "pesado na base, leve no head")
        self.assertGreater(pesados_na_base, 250, "o corpus ainda exercita a regra da base")

    def test_formas_leves_continuam_leves(self):
        for comando in ("/x/bin/forge-testes tests/test_a.py", "./bin/forge-testes", "timeout 60 bin/forge-mutante --listar",
                        "echo bin/forge-testes --completa", "timeout 5 echo python3 -m unittest discover",
                        "git log --grep '.githooks/pre-push --suite'", "python3 -m unittest; echo discover",
                        "/x/xbin/forge-testes --completa"):
            with self.subTest(comando=comando):
                self.assertFalse(pesado.pesado(comando, FORGE))


def pasta_temporaria(teste):
    pasta = tempfile.TemporaryDirectory(prefix="forge-orfao-")
    teste.addCleanup(pasta.cleanup)
    return Path(pasta.name)


class HookFalso:
    def __init__(self, pasta):
        self.pasta = pasta

    def cwd(self):
        return str(self.pasta)

    def run(self):
        return self.pasta

    def trava(self):
        return contextlib.nullcontext()

    def campo(self, *_):
        return None

    def expira_s(self):
        return pesado.TRAVA_S


def proc_deste_namespace():
    return pesado.processo(os.getpid()) is not None


class ProcessoOrfao(unittest.TestCase):
    def test_zumbi_de_verdade_nao_e_vivo(self):
        if not proc_deste_namespace():
            self.skipTest("o /proc é de outro namespace de pid (sandbox do Bash); o CI roda")
        filho = subprocess.Popen([sys.executable, "-I", "-c", "pass"], env={})
        self.addCleanup(filho.wait)
        for _ in range(200):
            if (pesado.processo(filho.pid) or ("?",))[0] == "Z":
                break
            time.sleep(0.05)
        self.assertEqual(pesado.processo(filho.pid)[0], "Z", "o filho virou zumbi sem ser colhido")
        self.assertFalse(pesado.pid_vivo(filho.pid))

    def test_zumbi_nao_e_vivo(self):
        for estado, vivo in (("Z", False), ("X", False), ("S", True)):
            with self.subTest(estado=estado), mock.patch.object(pesado, "processo", return_value=(estado, 100)):
                self.assertIs(pesado.pid_vivo(os.getpid()), vivo)

    def test_pid_reaproveitado_nao_e_vivo(self):
        with mock.patch.object(pesado, "processo", return_value=("S", 100)):
            self.assertTrue(pesado.pid_vivo(os.getpid(), 100))
            self.assertTrue(pesado.pid_vivo(os.getpid()), "trava antiga, sem o início: como antes")
            self.assertFalse(pesado.pid_vivo(os.getpid(), 101))
        with mock.patch.object(pesado, "processo", return_value=None):
            self.assertTrue(pesado.pid_vivo(os.getpid(), 101), "sem /proc legível, como antes")

    def test_sem_permissao_de_sinal_decide_pelo_proc(self):
        """O pid de outro usuário (os.kill dá PermissionError) se decide pelo estado e pelo início lidos no /proc."""
        for lido, inicio, vivo in ((("Z", 100), 100, False), (("S", 100), 101, False), (("S", 100), 100, True), (None, 1, True)):
            with self.subTest(lido=lido, inicio=inicio), mock.patch.object(pesado.os, "kill", side_effect=PermissionError), \
                    mock.patch.object(pesado, "processo", return_value=lido):
                self.assertIs(pesado.pid_vivo(4242, inicio), vivo)

    def test_a_vez_grava_o_dono_ja_checado(self):
        """A sessão some entre a checagem e a gravação: a trava leva o dono checado, não o pid relido (o do reaper)."""
        pasta = pasta_temporaria(self)
        with mock.patch.object(pesado, "pid_da_sessao", side_effect=[4242, 4242] + [1] * 50), \
                mock.patch.dict(os.environ, {"FORGE_PESADO_ESPERA_S": "0"}), \
                mock.patch.object(pesado, "processo", return_value=("S", 77)):
            pesado.esperar_a_vez(HookFalso(pasta), pasta, pasta / "pesado.json", "bin/forge-testes --completa", "toolu_1")
        trava = pesado.ler_json(pasta / "pesado.json", None)
        self.assertEqual((trava["pid"], trava["inicio"]), (4242, 77))

    def test_proc_de_outro_namespace_nao_se_le(self):
        with mock.patch.object(pesado.os, "getpid", return_value=-7):
            self.assertIsNone(pesado.processo(1), "o /proc/self não é este processo: não decide")

    def test_trava_de_pid_reaproveitado_nao_ocupa(self):
        hook = HookFalso(pasta_temporaria(self))
        trava = {"pid": os.getpid(), "inicio": 100, "agente": "outro", "desde": time.time(), "tool_use_id": "toolu_1"}
        with mock.patch.object(pesado, "processo", return_value=("S", 100)):
            self.assertTrue(pesado.ocupada(hook, trava, "toolu_2", time.time()))
            trava["inicio"] = 101
            self.assertFalse(pesado.ocupada(hook, trava, "toolu_2", time.time()))

    def test_a_vez_grava_o_inicio_da_sessao(self):
        pasta = pasta_temporaria(self)
        with mock.patch.dict(os.environ, {"FORGE_PESADO_ESPERA_S": "0"}), \
                mock.patch.object(pesado, "processo", return_value=("S", 123)):
            pesado.esperar_a_vez(HookFalso(pasta), pasta, pasta / "pesado.json", "bin/forge-testes --completa", "toolu_1")
        self.assertEqual(pesado.ler_json(pasta / "pesado.json", None)["inicio"], 123)

    def test_sessao_que_acabou_sai_da_fila_sem_pegar_a_vez(self):
        pasta = pasta_temporaria(self)
        erro = io.StringIO()
        with mock.patch.object(pesado, "pid_da_sessao", side_effect=[4242] + [1] * 50), \
                mock.patch.dict(os.environ, {"FORGE_PESADO_ESPERA_S": "1"}), contextlib.redirect_stderr(erro), \
                self.assertRaises(SystemExit) as saida:
            pesado.esperar_a_vez(HookFalso(pasta), pasta, pasta / "pesado.json", "bin/forge-testes --completa", "toolu_1")
        self.assertEqual(saida.exception.code, 2)
        self.assertIn("acabou", erro.getvalue())
        self.assertFalse((pasta / "pesado.json").exists(), "a vez não foi pega")
        self.assertEqual(list((pasta / "pesado.fila").iterdir()), [], "a senha saiu da fila")


if __name__ == "__main__":
    unittest.main()
