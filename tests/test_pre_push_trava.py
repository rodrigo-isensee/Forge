"""R-TETO: duas suítes do Forge não rodam ao mesmo tempo; o pre-push espera a vez por uma trava (flock).

Cada teste roda o hook de verdade, dentro de um repositório descartável com uma suíte mínima, para não
disparar a suíte do Forge de dentro dela. A trava vive em XDG_RUNTIME_DIR apontada para uma pasta temporária.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
HOOK = RAIZ / ".githooks" / "pre-push"
# FORGE_SUITE_* (processos, medição, trava) da suíte que roda estes testes não vazam para a suíte de brinquedo.
AMBIENTE = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_SUITE_"))})

SUITE_RAPIDA = '''import unittest, pathlib
class T(unittest.TestCase):
    def test_roda(self):
        pathlib.Path("rodou").write_text("sim")
'''
SUITE_LENTA = '''import unittest, pathlib, time
class T(unittest.TestCase):
    def test_espera_liberar(self):
        pathlib.Path("iniciou").write_text("sim")
        for _ in range(300):
            if pathlib.Path("liberar").exists():
                return
            time.sleep(0.1)
        self.fail("ninguem liberou")
'''
SUITE_FALHA = '''import unittest
class T(unittest.TestCase):
    def test_falha(self):
        self.fail("de proposito")
'''
SUITE_VE_DESCRITOR = '''import unittest, pathlib, os
class T(unittest.TestCase):
    def test_descritor(self):
        pathlib.Path("fd9").write_text(str(os.path.exists("/proc/self/fd/9")))
'''
SUITE_ORDEM = '''import unittest, pathlib, os
class T(unittest.TestCase):
    def test_ordem(self):
        with open("ordem", "a") as f:
            f.write(os.environ["QUEM"] + "\\n")
'''
SUITE_COM_PID = '''import unittest, pathlib, os, time
class T(unittest.TestCase):
    def test_espera_liberar(self):
        pathlib.Path("suite-pid").write_text(str(os.getpid()))
        for _ in range(600):
            if pathlib.Path("liberar").exists():
                return
            time.sleep(0.1)
        self.fail("ninguem liberou")
'''
SEGURA_TRAVA = '''import fcntl, sys, time
f = open(sys.argv[1], "a")
fcntl.flock(f, fcntl.LOCK_EX)
print("pronto", flush=True)
time.sleep(600)
'''


class PrePushTrava(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.run_dir = base / "run"
        self.run_dir.mkdir()
        self.repo = base / "repo"
        (self.repo / "tests").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True, env=AMBIENTE)
        self.env = dict(AMBIENTE, XDG_RUNTIME_DIR=str(self.run_dir), FORGE_TRAVA_ESPERA="20")
        self.trava = self.run_dir / f"forge-suite-{os.getuid()}.lock"
        self.filhos = []
        self.addCleanup(self._mata_filhos)

    def _mata_filhos(self):
        for p in self.filhos:
            if p.poll() is None:
                p.kill()
            p.wait()
            for fluxo in (p.stdout, p.stderr):
                if fluxo:
                    fluxo.close()

    def suite(self, texto):
        (self.repo / "tests" / "test_x.py").write_text(texto)

    def hook(self, *args, entrada=None, env=None, **extra):
        entrada = self.refs("melhoria/x") if entrada is None else entrada  # um push de verdade traz ao menos uma ref
        env = dict(self.env if env is None else env, **extra)
        arquivo = Path(self._tmp.name) / f"entrada-{len(self.filhos)}-{time.monotonic_ns()}"
        arquivo.write_text(entrada)
        with arquivo.open() as stdin:
            return subprocess.Popen(
                [str(HOOK), *args], cwd=self.repo, env=env, stdin=stdin,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def roda(self, *args, entrada=None, env=None, **extra):
        p = self.hook(*args, entrada=entrada, env=env, **extra)
        self.filhos.append(p)
        saida, erro = p.communicate(timeout=60)
        return p.returncode, saida, erro

    def env_recuo(self):
        """Sem XDG_RUNTIME_DIR: a trava cai em $TMPDIR, numa subpasta forge-<uid>."""
        env = {k: v for k, v in self.env.items() if k != "XDG_RUNTIME_DIR"}
        env["TMPDIR"] = str(self.run_dir)
        return env

    def subpasta(self):
        return self.run_dir / f"forge-{os.getuid()}"

    @staticmethod
    def refs(destino, local="1" * 40, remoto="0" * 40):
        return f"refs/heads/x {local} refs/heads/{destino} {remoto}\n"

    def espera_ate(self, condicao, limite=15):
        fim = time.monotonic() + limite
        while time.monotonic() < fim:
            if condicao():
                return True
            time.sleep(0.05)
        return False

    def segura_trava(self):
        """Um processo externo que segura a trava até ser morto; devolve o processo."""
        p = subprocess.Popen([sys.executable, "-I", "-c", SEGURA_TRAVA, str(self.trava)],
                             stdout=subprocess.PIPE, text=True)
        self.filhos.append(p)
        self.assertEqual(p.stdout.readline().strip(), "pronto")
        return p

    def test_suite_sem_concorrente_roda_e_devolve_o_codigo_da_suite(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, _ = self.roda()
        self.assertEqual(codigo, 0)
        self.assertTrue((self.repo / "rodou").exists())
        self.suite(SUITE_FALHA)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("testes do Forge falharam", erro)

    def test_segunda_execucao_espera_a_vez(self):
        self.suite(SUITE_LENTA)
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate((self.repo / "iniciou").exists), "a primeira suíte não começou")
        (self.repo / "iniciou").unlink()
        segunda = self.hook()
        self.filhos.append(segunda)
        # a segunda não pode ter começado a suíte enquanto a primeira segura a trava
        time.sleep(1.5)
        self.assertIsNone(segunda.poll(), "a segunda não esperou")
        self.assertFalse((self.repo / "iniciou").exists(), "a segunda rodou a suíte junto com a primeira")
        (self.repo / "liberar").write_text("")
        self.assertEqual(primeira.wait(timeout=60), 0)
        self.assertEqual(segunda.wait(timeout=60), 0)
        self.assertIn("esperando a vez", segunda.stderr.read())
        self.assertTrue((self.repo / "iniciou").exists(), "a segunda não rodou a suíte depois da vez")

    def test_status_acompanha_a_trava(self):
        self.suite(SUITE_LENTA)
        codigo, saida, _ = self.roda("--status")
        self.assertEqual((codigo, saida.strip()), (1, "nenhuma suíte do Forge rodando"))
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate(lambda: self.roda("--status")[0] == 0), "o status não viu a suíte")
        _, saida, _ = self.roda("--status")
        self.assertIn("suíte do Forge rodando", saida)
        self.assertIn("pre-push --suite", saida)  # SUITE-INICIO-ATOMICO: a dica do caminho que espera a vez
        (self.repo / "liberar").write_text("")
        self.assertEqual(primeira.wait(timeout=60), 0)
        codigo, _, _ = self.roda("--status")
        self.assertEqual(codigo, 1)

    def test_trava_orfa_de_processo_morto_e_liberada(self):
        self.suite(SUITE_RAPIDA)
        dono = self.segura_trava()
        self.assertEqual(self.roda("--status")[0], 0)
        dono.send_signal(signal.SIGKILL)
        dono.wait()
        # o arquivo continua lá (com ou sem texto), mas ninguém o segura
        self.assertTrue(self.trava.exists())
        self.assertEqual(self.roda("--status")[0], 1)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("esperando a vez", erro)
        self.assertTrue((self.repo / "rodou").exists())

    def test_limite_estourado_sai_com_erro_e_nao_roda_a_suite(self):
        self.suite(SUITE_RAPIDA)
        self.segura_trava()
        inicio = time.monotonic()
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="1")
        self.assertGreaterEqual(time.monotonic() - inicio, 0.9)
        self.assertEqual(codigo, 1)
        self.assertIn("esperando a vez", erro)
        self.assertIn("a vez não chegou", erro)
        self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou sem ter a trava")

    def test_limite_invalido_e_recusado(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="logo")
        self.assertEqual(codigo, 1)
        self.assertIn("FORGE_TRAVA_ESPERA", erro)

    def test_trava_que_e_link_simbolico_e_recusada(self):
        self.suite(SUITE_RAPIDA)
        self.trava.symlink_to(self.run_dir / "alvo")
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 1)
        self.assertIn("link simbólico", erro)
        self.assertFalse((self.run_dir / "alvo").exists())

    def test_remoto_chamado_status_segue_o_caminho_normal(self):
        # o git chama o pre-push com dois argumentos (nome e URL do remoto): "--status" aí não é o modo status
        self.suite(SUITE_RAPIDA)
        self.segura_trava()
        codigo, saida, erro = self.roda("--status", "/algum/lugar", entrada=self.refs("melhoria/x"),
                                        FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1, (saida, erro))
        self.assertNotIn("suíte do Forge rodando", saida)
        self.assertIn("esperando a vez", erro)
        self.assertFalse((self.repo / "rodou").exists())
        # só o argumento "--status" sozinho é o modo status; "--status extra" não
        codigo, saida, _ = self.roda("--status", "extra", entrada=self.refs("melhoria/x"),
                                     FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1)
        self.assertNotIn("suíte do Forge rodando", saida)

    def test_envio_direto_continua_barrado_com_trava_e_com_status(self):
        self.suite(SUITE_RAPIDA)
        self.segura_trava()
        for destino in ("develop", "homolog", "main"):
            with self.subTest(destino=destino):
                for args in (("origin", "/url"), ("--status", "/url")):
                    codigo, saida, erro = self.roda(*args, entrada=self.refs(destino), FORGE_TRAVA_ESPERA="1")
                    self.assertEqual(codigo, 1, (saida, erro))
                    self.assertIn(f"envio direto para {destino} bloqueado", erro)
                    self.assertNotIn("suíte do Forge rodando", saida)
        self.assertFalse((self.repo / "rodou").exists())

    def test_recuo_cria_subpasta_700_do_usuario(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda(env=self.env_recuo())
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(self.subpasta().stat().st_mode & 0o777, 0o700)
        self.assertTrue((self.subpasta() / f"forge-suite-{os.getuid()}.lock").exists())

    def test_status_nao_cria_subpasta_nem_trava(self):
        codigo, saida, _ = self.roda("--status", env=self.env_recuo())
        self.assertEqual((codigo, saida.strip()), (1, "nenhuma suíte do Forge rodando"))
        self.assertEqual(list(self.run_dir.iterdir()), [])

    def test_subpasta_que_e_link_e_recusada(self):
        self.suite(SUITE_RAPIDA)
        alvo = self.run_dir / "alvo"
        alvo.mkdir()
        self.subpasta().symlink_to(alvo)
        codigo, _, erro = self.roda(env=self.env_recuo())
        self.assertEqual(codigo, 1)
        self.assertIn("não é uma pasta do próprio usuário", erro)
        self.assertEqual(list(alvo.iterdir()), [])
        self.assertFalse((self.repo / "rodou").exists())
        codigo, saida, erro = self.roda("--status", env=self.env_recuo())
        self.assertEqual(codigo, 2)
        self.assertIn("não é uma pasta do próprio usuário", erro)
        self.assertNotIn("nenhuma suíte", saida)

    def test_trava_link_dentro_da_subpasta_e_recusada(self):
        self.suite(SUITE_RAPIDA)
        self.subpasta().mkdir(mode=0o700)
        (self.subpasta() / f"forge-suite-{os.getuid()}.lock").symlink_to(self.run_dir / "alvo")
        codigo, _, erro = self.roda(env=self.env_recuo())
        self.assertEqual(codigo, 1)
        self.assertIn("link simbólico", erro)
        self.assertFalse((self.run_dir / "alvo").exists())
        self.assertFalse((self.repo / "rodou").exists())

    def test_status_com_erro_sai_com_2(self):  # PRE-PUSH-STATUS-RC, C-4, C-6, C-7
        """rc 2 = não consegui conferir; 0 = rodando e 1 = nenhuma ficam como estão. O push segue com rc 1."""
        lock = f"forge-suite-{os.getuid()}.lock"

        def subpasta_link(sub):
            (sub.parent / "alvo").mkdir()
            sub.symlink_to(sub.parent / "alvo")

        def trava_link(sub):
            sub.mkdir(mode=0o700)
            (sub / lock).symlink_to(sub.parent / "alvo-trava")

        def trava_sem_leitura(sub):
            sub.mkdir(mode=0o700)
            (sub / lock).write_text("")
            os.chmod(sub / lock, 0)

        for nome, prepara in (("subpasta link", subpasta_link), ("trava link", trava_link),
                              ("trava sem leitura", trava_sem_leitura)):
            with self.subTest(nome):
                if nome == "trava sem leitura" and os.geteuid() == 0:
                    self.skipTest("root lê arquivo sem permissão")
                tmp = Path(self._tmp.name) / f"erro-{nome.replace(' ', '-')}"
                tmp.mkdir()
                prepara(tmp / f"forge-{os.getuid()}")
                env = dict(self.env_recuo(), TMPDIR=str(tmp))
                codigo, saida, erro = self.roda("--status", env=env)
                self.assertEqual(codigo, 2, (saida, erro))
                self.assertNotIn("nenhuma suíte", saida)
                self.assertIn("pre-push --suite", erro)  # C-7: aponta o caminho que espera a vez ou falha fechado
                self.suite(SUITE_RAPIDA)
                codigo, _, _ = self.roda(env=env)
                self.assertEqual(codigo, 1, "o push segue com rc 1 no mesmo erro")
                self.assertFalse((self.repo / "rodou").exists())

    def test_subpasta_que_nao_da_para_criar_falha_fechado(self):
        # um arquivo comum com o nome da subpasta impede o mkdir: o hook não pula a suíte nem recua
        self.suite(SUITE_RAPIDA)
        self.subpasta().write_text("ocupado")
        codigo, _, erro = self.roda(env=self.env_recuo())
        self.assertEqual(codigo, 1)
        self.assertIn("não é uma pasta do próprio usuário", erro)
        self.assertFalse((self.repo / "rodou").exists())

    def recuo_com_subpasta(self, nome, modo):
        """Ambiente de recuo (TMPDIR próprio e vazio) com a subpasta forge-<uid> já criada e com o modo pedido."""
        tmp = Path(self._tmp.name) / f"recuo-{nome}"
        sub = tmp / f"forge-{os.getuid()}"
        sub.mkdir(parents=True, mode=0o700)
        os.chmod(sub, modo)  # depois do mkdir, por causa do umask
        return dict(self.env_recuo(), TMPDIR=str(tmp)), sub

    def test_subpasta_gravavel_por_grupo_ou_outros_e_recusada(self):  # TRAVA-MODO-SUBPASTA, C-1
        self.suite(SUITE_RAPIDA)
        for modo in (0o777, 0o770, 0o702, 0o1777):
            with self.subTest(modo=oct(modo)):
                env, sub = self.recuo_com_subpasta(oct(modo), modo)
                codigo, _, erro = self.roda(env=env)
                self.assertEqual(codigo, 1, erro)
                self.assertIn("recusada", erro)
                self.assertFalse((self.repo / "rodou").exists())
                self.assertEqual(list(sub.iterdir()), [], "o hook escreveu na subpasta recusada")
                _, saida, erro = self.roda("--status", env=env)
                self.assertIn("recusada", erro)
                self.assertNotIn("nenhuma suíte", saida)

    def test_subpasta_sem_escrita_de_grupo_ou_outros_segue_aceita(self):  # contraprova de TRAVA-MODO-SUBPASTA
        self.suite(SUITE_RAPIDA)
        for modo in (0o700, 0o750, 0o755):
            with self.subTest(modo=oct(modo)):
                env, _ = self.recuo_com_subpasta(oct(modo), modo)
                codigo, _, erro = self.roda(env=env)
                self.assertEqual(codigo, 0, erro)
                self.assertTrue((self.repo / "rodou").exists())
                (self.repo / "rodou").unlink()

    def test_conferencia_do_modo_que_falha_recusa(self):  # C-2: erro ao ler o modo é recusa, nunca aceite
        self.suite(SUITE_RAPIDA)
        falso = Path(self._tmp.name) / "falso"
        falso.mkdir()
        (falso / "find").write_text("#!/bin/sh\nexit 1\n")
        (falso / "find").chmod(0o755)
        env, _ = self.recuo_com_subpasta("find-falso", 0o700)
        env["PATH"] = f"{falso}:{env['PATH']}"
        codigo, _, erro = self.roda(env=env)
        self.assertEqual(codigo, 1, erro)
        self.assertIn("recusada", erro)
        self.assertFalse((self.repo / "rodou").exists())

    # SUITE-FILA-JUSTA: ordem de chegada pela fila de vezes ao lado da trava.
    def fila(self):
        return self.run_dir / f"forge-suite-{os.getuid()}.fila"

    def vezes(self):
        return sorted(p.name for p in self.fila().iterdir() if not p.name.startswith(".")) if self.fila().is_dir() else []

    def segura_vez(self, nome="0000000000000000001-1"):
        """Uma espera anterior viva: a vez presa por um processo externo."""
        self.fila().mkdir(mode=0o700, exist_ok=True)
        vez = self.fila() / nome
        vez.write_text("")
        p = subprocess.Popen([sys.executable, "-I", "-c", SEGURA_TRAVA, str(vez)], stdout=subprocess.PIPE, text=True)
        self.filhos.append(p)
        self.assertEqual(p.stdout.readline().strip(), "pronto")
        return p

    def test_espera_anterior_viva_tem_a_vez_mesmo_com_a_trava_livre(self):
        self.suite(SUITE_RAPIDA)
        self.segura_vez()
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1, erro)
        self.assertIn("esperando a vez", erro)
        self.assertIn("a vez não chegou", erro)
        self.assertFalse((self.repo / "rodou").exists(), "passou na frente de quem chegou antes")
        self.assertEqual(self.vezes(), ["0000000000000000001-1"], "a vez de quem desistiu ficou na fila")

    def test_vez_de_processo_morto_e_descartada(self):
        self.suite(SUITE_RAPIDA)
        self.fila().mkdir(mode=0o700)
        (self.fila() / "0000000000000000001-1").write_text("")
        codigo, _, erro = self.roda(FORGE_TRAVA_ESPERA="5")
        self.assertEqual(codigo, 0, erro)
        self.assertTrue((self.repo / "rodou").exists())
        self.assertEqual(self.vezes(), [])

    def test_quem_chega_antes_roda_antes(self):
        self.suite(SUITE_ORDEM)
        dono = self.segura_trava()
        b = self.hook(QUEM="B")
        self.filhos.append(b)
        self.assertTrue(self.espera_ate(lambda: len(self.vezes()) == 1), "B não entrou na fila")
        c = self.hook(QUEM="C")
        self.filhos.append(c)
        self.assertTrue(self.espera_ate(lambda: len(self.vezes()) == 2), "C não entrou na fila")
        _, saida, _ = self.roda("--status")
        self.assertIn("2 na fila", saida)
        dono.kill()
        dono.wait()
        self.assertEqual(b.wait(timeout=60), 0)
        self.assertEqual(c.wait(timeout=60), 0)
        self.assertEqual((self.repo / "ordem").read_text().split(), ["B", "C"])
        self.assertEqual(self.vezes(), [])

    def test_fila_que_e_link_espera_so_pela_trava(self):
        self.suite(SUITE_RAPIDA)
        alvo = self.run_dir / "alvo"
        alvo.mkdir()
        self.fila().symlink_to(alvo)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertIn("espera sem a ordem de chegada", erro)
        self.assertEqual(list(alvo.iterdir()), [])
        self.assertTrue((self.repo / "rodou").exists())

    def test_push_sem_refs_a_enviar_nao_roda_a_suite(self):  # PREPUSH-JA-NO-REMOTO (decisão do dono, 2026-10-21 14:12)
        """A branch já igual à remota: o git chama o hook sem nenhuma linha no stdin; não há o que testar nem a trava a pegar."""
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda("origin", "u", entrada="")
        self.assertEqual(codigo, 0, erro)
        self.assertIn("nada a enviar", erro)
        self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou sem ref a enviar")
        self.assertEqual(list(self.run_dir.iterdir()), [], "sem ref a enviar, o hook não pega trava nem entra na fila")

    def test_push_que_so_apaga_nao_roda_a_suite(self):  # PREPUSH-DELETE (decisão do dono, 2026-10-23: opção A)
        """Só remoções (a limpeza pós-merge do R-FLUXO): sai com 0 sem suíte, sem trava e sem fila; uma ou várias."""
        self.suite(SUITE_RAPIDA)
        um = self.refs("melhoria/x", local="0" * 40, remoto="1" * 40)
        dois = um + self.refs("fix/y", local="0" * 40, remoto="2" * 40)
        for nome, entrada in (("uma", um), ("duas", dois)):
            with self.subTest(nome):
                codigo, _, erro = self.roda("origin", "u", entrada=entrada)
                self.assertEqual(codigo, 0, erro)
                self.assertIn("só remove", erro)
                self.assertFalse((self.repo / "rodou").exists(), "a suíte rodou em push que só apaga")
                self.assertEqual(list(self.run_dir.iterdir()), [], "push que só apaga não pega trava nem entra na fila")

    def test_push_que_so_apaga_nao_espera_a_trava_de_outra_suite(self):
        self.suite(SUITE_RAPIDA)
        self.segura_trava()
        codigo, _, erro = self.roda("origin", "u", FORGE_TRAVA_ESPERA="1",
                                    entrada=self.refs("melhoria/x", local="0" * 40, remoto="1" * 40))
        self.assertEqual(codigo, 0, erro)
        self.assertNotIn("esperando a vez", erro)

    def test_apagar_main_homolog_ou_develop_segue_barrado(self):
        self.suite(SUITE_RAPIDA)
        for destino in ("main", "homolog", "develop"):
            with self.subTest(destino):
                codigo, _, erro = self.roda("origin", "u", entrada=self.refs(destino, local="0" * 40, remoto="1" * 40))
                self.assertEqual(codigo, 1)
                self.assertIn(f"envio direto para {destino} bloqueado", erro)
                self.assertFalse((self.repo / "rodou").exists())

    def test_remocao_de_branch_comum_com_develop_junto_segue_barrada(self):
        self.suite(SUITE_RAPIDA)
        entrada = self.refs("melhoria/x", local="0" * 40, remoto="1" * 40) + self.refs("develop", local="0" * 40, remoto="1" * 40)
        codigo, _, erro = self.roda("origin", "u", entrada=entrada)
        self.assertEqual(codigo, 1)
        self.assertIn("envio direto para develop bloqueado", erro)

    def test_push_misto_remocao_mais_envio_roda_a_suite(self):
        """Basta uma ref que envia código: a suíte roda como hoje, também quando a remoção vem antes."""
        self.suite(SUITE_RAPIDA)
        remocao = self.refs("melhoria/x", local="0" * 40, remoto="1" * 40)
        envio = self.refs("melhoria/y")
        for nome, entrada in (("remocao-primeiro", remocao + envio), ("envio-primeiro", envio + remocao)):
            with self.subTest(nome):
                codigo, _, erro = self.roda("origin", "u", entrada=entrada)
                self.assertEqual(codigo, 0, erro)
                self.assertTrue((self.repo / "rodou").exists(), "o push misto deixou de rodar a suíte")
                (self.repo / "rodou").unlink()

    def test_ref_para_a_develop_segue_barrada(self):
        """Pular a suíte sem refs não afrouxa o bloqueio: uma ref para a develop barra como sempre."""
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda("origin", "u", entrada=self.refs("develop"))
        self.assertEqual(codigo, 1)
        self.assertIn("envio direto para develop bloqueado", erro)

    def test_modo_suite_usa_a_trava_e_nao_le_refs(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda("--suite", entrada=self.refs("develop"))
        self.assertEqual(codigo, 0, erro)  # não lê o stdin: nenhuma ref, nada a barrar
        self.assertTrue((self.repo / "rodou").exists())
        self.assertFalse((self.run_dir / f"forge-suite-{os.getuid()}.verde").exists(), "o modo --suite anotou prova")
        (self.repo / "rodou").unlink()
        self.segura_trava()
        codigo, _, erro = self.roda("--suite", FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1)
        self.assertIn("a vez não chegou", erro)
        self.assertFalse((self.repo / "rodou").exists())
        self.suite(SUITE_FALHA)
        codigo, _, _ = self.roda("--suite", FORGE_TRAVA_ESPERA="1")
        self.assertEqual(codigo, 1)

    def test_remoto_chamado_suite_segue_o_caminho_normal(self):
        self.suite(SUITE_RAPIDA)
        codigo, _, erro = self.roda("--suite", "/url", entrada=self.refs("develop"))
        self.assertEqual(codigo, 1)
        self.assertIn("envio direto para develop bloqueado", erro)
        self.assertFalse((self.repo / "rodou").exists())

    def test_parar_o_hook_para_so_a_propria_suite(self):  # PREPUSH-PKILL-ALHEIO, AB-6, AB-12
        self.suite(SUITE_COM_PID)
        pid_arquivo = self.repo / "suite-pid"
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate(pid_arquivo.exists), "a primeira suíte não começou")
        suite_da_primeira = int(pid_arquivo.read_text())
        segunda = self.hook()
        self.filhos.append(segunda)
        self.assertTrue(self.espera_ate(lambda: len(self.vezes()) == 1), "a segunda não entrou na fila")
        primeira.send_signal(signal.SIGTERM)  # o "kill <pid>" que o hook imprime
        self.assertEqual(primeira.wait(timeout=30), 1)
        erro = primeira.stderr.read()
        self.assertIn(f"para parar só esta execução: kill {primeira.pid}", erro)
        self.assertIn("nunca pkill", erro)
        self.assertIn("suíte interrompida", erro)
        with self.assertRaises(ProcessLookupError):  # a suíte da primeira morreu antes de a trava soltar
            os.kill(suite_da_primeira, 0)
        # a segunda segue: pega a vez e roda a própria suíte até o fim
        self.assertTrue(self.espera_ate(lambda: pid_arquivo.read_text() != str(suite_da_primeira), 30),
                        "a segunda não rodou depois da parada da primeira")
        self.assertIsNone(segunda.poll(), "parar a primeira derrubou a segunda")
        (self.repo / "liberar").write_text("")
        self.assertEqual(segunda.wait(timeout=60), 0)
        self.assertFalse((self.run_dir / f"forge-suite-{os.getuid()}.verde").exists())

    def test_descritor_da_trava_nao_vaza_para_a_suite(self):
        self.suite(SUITE_VE_DESCRITOR)
        codigo, _, erro = self.roda()
        self.assertEqual(codigo, 0, erro)
        self.assertEqual((self.repo / "fd9").read_text(), "False")

    def test_texto_da_trava_sai_limitado_e_sem_controle(self):  # C-14, T-C4h
        self.suite(SUITE_LENTA)
        primeira = self.hook()
        self.filhos.append(primeira)
        self.assertTrue(self.espera_ate(lambda: self.roda("--status")[0] == 0))
        self.trava.write_bytes(b"\x1b]0;x\x07\x1b[2J" + b"A" * (1 << 20))
        _, saida, _ = self.roda("--status")
        self.assertNotIn("\x1b", saida)
        self.assertNotIn("\x07", saida)
        self.assertLessEqual(len(saida), 200 + 120, "o texto da trava saiu sem limite")
        _, _, erro = self.roda(FORGE_TRAVA_ESPERA="1")
        self.assertIn("esperando a vez", erro)
        self.assertNotIn("\x1b", erro)
        self.assertLessEqual(len(erro), 200 + 400)
        (self.repo / "liberar").write_text("")
        self.assertEqual(primeira.wait(timeout=60), 0)


if __name__ == "__main__":
    unittest.main()
