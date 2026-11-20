"""MP2 e MP4 (diretriz 35): o registro de projetos ativos da máquina e a fila pesada única, com projetos simulados."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "bin"))
import _maquina  # noqa: E402
import forge_dono  # noqa: E402
import pesado  # noqa: E402
from test_hooks import ambiente_limpo, lancador, pid_morto, repositorio_vazio  # noqa: E402


class Maquina(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-maquina-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.env = dict(ambiente_limpo(), FORGE_MAQUINA=str(self.tmp / "maquina"), FORGE_PESADO_ESPERA_S="0")

    def projeto(self, nome):
        raiz = self.tmp / nome
        raiz.mkdir()
        repositorio_vazio(raiz, "develop")
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (raiz / ".forge" / "config.json").write_text(json.dumps({"pesados": ["npx playwright test"]}), encoding="utf-8")
        return raiz

    def hook(self, nome, raiz, nucleos=None, **entrada):
        entrada, comando = {"cwd": str(raiz), **entrada}, lancador(nome)
        if nucleos:  # o hook roda noutro processo: os núcleos (e as vagas) se fixam lá
            comando[2] = f"import os; os.cpu_count = lambda: {nucleos}\n" + comando[2]
        return subprocess.run(comando, input=json.dumps(entrada), cwd=raiz, env=self.env, capture_output=True,
                              text=True, timeout=60)

    def anotar(self, raiz, sessao, evento="Stop"):
        return self.hook("_maquina", raiz, hook_event_name=evento, session_id=sessao)

    def registro(self):
        return json.loads((self.tmp / "maquina" / _maquina.ATIVOS).read_text(encoding="utf-8"))

    def status(self):
        """As linhas de projeto do `--maquina`; as `máquina:` da medida (MP8) ficam em StatusDaMaquina."""
        saida = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-status"), "--maquina"], env=self.env,
                               capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL).stdout
        return "".join(linha for linha in saida.splitlines(True) if not linha.startswith("máquina: "))

    def gravar(self, nome, dados):
        (self.tmp / "maquina").mkdir(mode=0o700, exist_ok=True)
        (self.tmp / "maquina" / nome).write_text(dados if isinstance(dados, str) else json.dumps(dados), encoding="utf-8")


class Registro(Maquina):
    def test_dois_projetos_ativos_e_o_status_lista(self):
        alfa, beta = self.projeto("alfa"), self.projeto("beta")
        self.assertEqual(self.anotar(alfa, "s1", "SessionStart").returncode, 0)
        self.assertEqual(self.anotar(beta, "s2").returncode, 0)
        self.assertEqual(self.registro()["projetos"], ["alfa", "beta"])
        linhas = self.status().splitlines()
        self.assertEqual([linha.split(" · ")[:2] for linha in linhas], [["alfa", str(alfa)], ["beta", str(beta)]])

    def test_sessao_que_para_de_bater_ou_fecha_some(self):
        agora, vivo = time.time(), os.getpid()
        self.gravar(_maquina.ATIVOS, {"projetos": ["velho", "morto"], "sessoes": {
            "velha": {"projeto": "velho", "pid": vivo, "batimento": agora - _maquina.BATIMENTO_S - 1},
            "morta": {"projeto": "morto", "pid": pid_morto(), "batimento": agora}}})
        self.assertEqual(self.status().strip(), "forge: nenhum projeto ativo na máquina", "quem lê filtra de novo")
        self.anotar(self.projeto("alfa"), "s1")
        self.assertEqual((self.registro()["projetos"], list(self.registro()["sessoes"])), (["alfa"], ["s1"]))

    def test_registro_ilegivel_recomeca(self):
        for bruto in ("{", "[1]", '{"sessoes": [1]}'):
            with self.subTest(bruto=bruto):
                self.gravar(_maquina.ATIVOS, bruto)
                self.assertEqual(self.status().strip(), "forge: nenhum projeto ativo na máquina")
                self.assertEqual(self.anotar(self.tmp, "s1").returncode, 0)  # fora de projeto: não grava
                self.anotar(self.projeto(f"p{len(bruto)}"), "s1")
                self.assertEqual(self.registro()["projetos"], [f"p{len(bruto)}"])

    def test_sessao_fora_da_forma_e_registro_em_link_nao_contam(self):
        agora, vivo = time.time(), os.getpid()
        (self.tmp / "fora.json").write_text(json.dumps({"sessoes": {"x": {"projeto": "fora", "pid": vivo, "batimento": agora}}}))
        (self.tmp / "maquina").mkdir(mode=0o700)
        (self.tmp / "maquina" / _maquina.ATIVOS).symlink_to(self.tmp / "fora.json")
        self.anotar(self.projeto("alfa"), "s1")
        self.assertEqual(self.registro()["projetos"], ["alfa"], "o registro em link não se lê")
        self.gravar(_maquina.ATIVOS, {"sessoes": {"n": 1, "e": {"projeto": 5, "pid": vivo, "batimento": agora}}})
        self.anotar(self.tmp / "alfa", "s1")
        self.assertEqual((self.registro()["projetos"], sorted(self.registro()["sessoes"])), (["alfa"], ["e", "s1"]))

    def test_a_pasta_e_a_do_registro_que_o_meta_e_o_agentes_leem(self):
        with mock.patch.dict(os.environ, {"HOME": str(self.tmp)}):
            os.environ.pop("FORGE_MAQUINA", None)
            self.assertEqual(_maquina.caminho_da_pasta() / _maquina.ATIVOS, self.tmp / ".forge/maquina/projetos-ativos.json")

    def test_so_a_sessao_de_projeto_no_inicio_e_no_fim_anota(self):
        alfa = self.projeto("alfa")
        for entrada in ({"hook_event_name": "PreToolUse", "session_id": "s1"}, {"hook_event_name": "Stop"},
                        {"hook_event_name": "Stop", "session_id": ""}):
            with self.subTest(entrada=entrada):
                self.assertEqual(self.hook("_maquina", alfa, **entrada).returncode, 0)
                self.assertFalse((self.tmp / "maquina" / _maquina.ATIVOS).exists())

    def test_pasta_aberta_ao_grupo_nao_grava(self):
        """Segurança A6: a pasta que já existe vale só com o modo 0700."""
        (self.tmp / "maquina").mkdir(mode=0o700)
        os.chmod(self.tmp / "maquina", 0o750)
        self.assertEqual(self.anotar(self.projeto("alfa"), "s1").returncode, 0)
        self.assertFalse((self.tmp / "maquina" / _maquina.ATIVOS).exists())

    def test_pasta_em_link_nao_grava(self):
        alvo = self.tmp / "alvo"
        alvo.mkdir(mode=0o700)  # só do usuário: quem recusa é a guarda do link
        (self.tmp / "maquina").symlink_to(alvo)
        self.assertEqual(self.anotar(self.projeto("alfa"), "s1").returncode, 0)
        self.assertEqual(list(alvo.iterdir()), [])


class Leitura(Maquina):
    """Segurança A4 e A5: a leitura não segue link nem espera FIFO e tem teto; a gravação não segue link plantado."""

    def setUp(self):
        super().setUp()
        patch = mock.patch.dict(os.environ, {"FORGE_MAQUINA": str(self.tmp / "maquina")})
        patch.start()
        self.addCleanup(patch.stop)
        self.pasta = _maquina.pasta()

    def test_fifo_e_arquivo_acima_do_teto_valem_vazio(self):
        os.mkfifo(self.pasta / "pesado.json")
        self.assertEqual(_maquina.ler("pesado.json"), {}, "FIFO sem escritor não prende a leitura")
        escritor = os.open(self.pasta / "pesado.json", os.O_RDWR)  # FIFO com dado à espera: também não se lê
        self.addCleanup(os.close, escritor)
        os.write(escritor, b'{"x": 1}')
        self.assertEqual(_maquina.ler("pesado.json"), {})
        self.gravar(_maquina.ATIVOS, json.dumps({"x": "a" * (_maquina.TETO_DE_BYTES - 8)}))  # teto + 1 bytes
        self.assertEqual(_maquina.ler(_maquina.ATIVOS), {})
        self.gravar(_maquina.ATIVOS, {"x": 1})
        self.assertEqual(_maquina.ler(_maquina.ATIVOS), {"x": 1})

    def test_gravar_que_falha_nao_deixa_temporario(self):
        (self.pasta / "pesado.json").mkdir()
        with self.assertRaises(OSError):
            _maquina.gravar("pesado.json", {"a": 1})
        self.assertEqual([c.name for c in self.pasta.iterdir()], ["pesado.json"])

    def test_gravar_nao_segue_o_temporario_plantado(self):
        fora = self.tmp / "fora.txt"
        fora.write_text("intacto", encoding="utf-8")
        (self.pasta / f"pesado.json.{os.getpid()}.tmp").symlink_to(fora)
        _maquina.gravar("pesado.json", {"a": 1})
        self.assertEqual((fora.read_text(encoding="utf-8"), _maquina.ler("pesado.json")), ("intacto", {"a": 1}))
        self.assertEqual({c.name for c in self.pasta.iterdir()}, {f"pesado.json.{os.getpid()}.tmp", "pesado.json"}, "sem temporário solto")

    def test_fila_em_link_levanta_e_senha_fora_da_forma_nao_conta(self):
        fila = self.pasta / "pesado.fila"
        fila.mkdir()
        alvo = self.tmp / "alvo"
        alvo.mkdir()
        (alvo / "000001-1-1").write_text("", encoding="utf-8")
        (fila / "000001-1-1").symlink_to(alvo / "000001-1-1")
        os.mkfifo(fila / "000002-1-1")
        self.assertEqual(pesado.fila_viva(fila), [])
        self.assertTrue((alvo / "000001-1-1").exists(), "a poda não apaga fora da pasta")
        self.assertTrue((fila / "000002-1-1").exists(), "o que não é arquivo regular não é senha")
        self.assertEqual(pesado.chave_da_senha(fila / "000003-1-1"), "", "a senha que sumiu não tem chave")
        shutil.rmtree(fila)
        fila.symlink_to(alvo)
        with self.assertRaises(OSError):
            pesado.pasta_da_fila()


class Protegida(unittest.TestCase):
    """Segurança A1: nenhum papel grava nem apaga ~/.forge/maquina/ (só os hooks, fora da ferramenta)."""

    def test_nenhum_papel_escreve_na_pasta_da_maquina(self):
        import conformidade
        politica = json.loads((RAIZ / "hooks" / "conformidade.json").read_text(encoding="utf-8"))
        self.assertEqual([c["quem"] for c in politica["caminhos"] if c["caminho"].startswith("~/.forge/maquina")], [[]])
        tipos = [t for lista in politica["papeis"].values() for t in lista] + [None, "general-purpose"]
        self.assertGreaterEqual(len(tipos), 10)
        with tempfile.TemporaryDirectory() as raiz:
            for tipo in tipos:
                for alvo in ("~/.forge/maquina", "~/.forge/maquina/pesado.json", "~/.forge/maquina/projetos-ativos.json",
                             "~/.forge/maquina/.trava", "~/.forge/maquina/pesado.fila/x"):
                    with self.subTest(tipo=tipo, alvo=alvo):
                        recusa = conformidade.escrita_barrada(tipo, alvo, raiz, "melhoria/x")
                        self.assertIsNotNone(recusa)
                        self.assertIn("MP4", " ".join(map(str, recusa)))


class FilaPesada(Maquina):
    def pedir(self, raiz, agente, evento="PreToolUse", uso="toolu_1", nucleos=None):
        return self.hook("pesado", raiz, nucleos, hook_event_name=evento, tool_name="Bash", tool_use_id=uso, agent_id=agente,
                         tool_input={"command": "npx playwright test"})

    def vez(self, nome, desde=None):
        """A vez viva de um projeto simulado na máquina (dono: este processo, outro agente)."""
        return str(self.tmp / nome / ".forge" / "run"), {"pid": os.getpid(), "agente": "outro", "tool_use_id": f"t-{nome}",
                                                          "desde": time.time() if desde is None else desde}

    def senha(self, nome, prio=0):
        """A senha presa de um pedido de `nome` na fila da máquina, com a chave do projeto dentro."""
        (self.tmp / "maquina").mkdir(mode=0o700, exist_ok=True)
        _, preso = pesado.entrar_na_fila(self.tmp / "maquina" / "pesado.fila", prio, self.vez(nome)[0])
        self.addCleanup(preso.close)

    def test_com_duas_vagas_senha_presa_pela_vez_do_proprio_projeto_nao_prende_outro(self):
        """Review A1, A2 e A4 (sonda S1): X tem a vez e outra senha de X espera; Y passa na vaga livre."""
        self.gravar("pesado.json", dict([self.vez("x")]))
        self.senha("x")
        r = self.pedir(self.projeto("y"), "b", nucleos=12)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_com_vaga_e_a_frente_parada_nao_entra_na_fila(self):
        """Review A2: no caminho rápido, Y pega a vaga sem entrar na fila (o cartão em "Aguardando o dono" só vale na espera)."""
        self.gravar("pesado.json", dict([self.vez("x")]))
        self.senha("x")
        y = self.projeto("y")
        (y / "KANBAN.md").write_text("## Aguardando o dono\n| develop |\n", encoding="utf-8")
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "c"], cwd=y, env=self.env, check=True, capture_output=True)
        self.assertTrue(pesado.aguardando_o_dono(y, pesado.branch_de(y)), "na espera, o cartão recusaria")
        r = self.pedir(y, "b", nucleos=12)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_senha_a_frente_que_pode_andar_segura_quem_vem_atras(self):
        self.senha("z")  # z sem vez na máquina: a senha dele anda primeiro
        r = self.pedir(self.projeto("y"), "b", nucleos=12)
        self.assertEqual(r.returncode, 2)
        self.assertIn("senha à frente na fila da máquina", r.stderr)
        self.assertNotIn("apague .forge/run/pesado.json", r.stderr, "review A3: a trava do projeto não é a causa")

    def test_na_espera_a_vaga_solta_passa_por_cima_da_senha_presa(self):
        """Review A1: na fila (não no caminho rápido), Y anda quando a vaga solta, com a senha de X presa à frente."""
        self.gravar("pesado.json", dict([self.vez("x"), self.vez("z")]))
        self.senha("x")
        fila = self.tmp / "maquina" / "pesado.fila"
        y, entrada = self.projeto("y"), {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "toolu_1",
                                         "agent_id": "b", "tool_input": {"command": "npx playwright test"}}
        comando = lancador("pesado")
        comando[2] = "import os; os.cpu_count = lambda: 12\n" + comando[2]
        proc = subprocess.Popen(comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=y, text=True,
                                env=dict(self.env, FORGE_PESADO_ESPERA_S="30"))
        self.addCleanup(lambda: (proc.kill(), proc.wait(), proc.stdout.close(), proc.stderr.close()))
        proc.stdin.write(json.dumps({"cwd": str(y), **entrada}))
        proc.stdin.close()
        for _ in range(200):
            if len(list(fila.iterdir())) == 2:
                break
            time.sleep(0.05)
        self.assertEqual(len(list(fila.iterdir())), 2, "Y entrou na fila")
        self.gravar("pesado.json", dict([self.vez("x")]))  # z solta a vaga
        self.assertEqual(proc.wait(timeout=20), 0, proc.stderr.read())

    def test_maquina_cheia_diz_a_pasta_da_maquina_e_os_projetos(self):
        self.gravar("pesado.json", dict([self.vez("x"), self.vez("z")]))
        r = self.pedir(self.projeto("y"), "b", nucleos=12)
        self.assertEqual(r.returncode, 2)
        self.assertIn("máquina cheia: 2 vaga(s) com x, z (~/.forge/maquina/pesado.json)", r.stderr)

    def test_vez_com_desde_no_futuro_nao_ocupa(self):
        """Segurança A2 (sonda S2): a vez forjada com `desde` adiante nunca venceria."""
        self.gravar("pesado.json", dict([self.vez("x", time.time() + 9e6), self.vez("z", time.time() + 9e6)]))
        self.assertEqual(self.pedir(self.projeto("y"), "b", nucleos=12).returncode, 0)

    def test_vagas_um_por_seis_nucleos(self):
        for nucleos, vagas in ((None, 1), (4, 1), (6, 1), (12, 2), (18, 3)):
            with self.subTest(nucleos=nucleos), mock.patch.object(pesado.os, "cpu_count", return_value=nucleos):
                self.assertEqual(pesado.vagas(), vagas)

    def test_bateria_de_outro_projeto_espera_a_vaga_da_maquina(self):
        cheios = [self.projeto(f"p{i}") for i in range(pesado.vagas())]
        for i, raiz in enumerate(cheios):
            self.assertEqual(self.pedir(raiz, f"a{i}").returncode, 0, "há vaga na máquina")
        outro = self.projeto("outro")
        r = self.pedir(outro, "b", uso="toolu_2")
        self.assertEqual(r.returncode, 2, "a máquina está cheia: espera na fila e recusa no teto")
        self.assertIn("fila: posição 1 de 1", r.stderr)
        self.assertEqual(self.pedir(cheios[0], "a0", "PostToolUse").returncode, 0)
        self.assertNotIn(str(cheios[0]), json.dumps(self.ler_vezes()), "o Post solta a vaga da máquina")
        self.assertEqual(self.pedir(outro, "b", uso="toolu_2").returncode, 0, "a vaga solta passa à próxima")

    def test_a_propria_vez_nao_toma_vaga(self):
        alfa, agora = self.projeto("alfa"), time.time()
        vezes = {f"/x{i}": {"pid": os.getpid(), "agente": "outro", "desde": agora, "tool_use_id": f"t{i}"} for i in range(pesado.vagas() - 1)}
        vezes[str(alfa / ".forge" / "run")] = {"pid": os.getpid(), "agente": "outro", "desde": agora, "tool_use_id": "t"}
        self.gravar("pesado.json", vezes)
        self.assertEqual(self.pedir(alfa, "a").returncode, 0, "a vez do próprio projeto não conta contra ele")

    def ler_vezes(self):
        return json.loads((self.tmp / "maquina" / "pesado.json").read_text(encoding="utf-8"))

    def test_post_de_outro_uso_mantem_e_dono_morto_sai(self):
        alfa, beta = self.projeto("alfa"), self.projeto("beta")
        self.gravar("pesado.json", {"/morto": {"pid": pid_morto(), "desde": time.time(), "tool_use_id": "t"}})
        self.pedir(alfa, "a")
        self.pedir(alfa, "a", "PostToolUse", uso="toolu_outro")
        self.assertEqual(len([c for c in self.ler_vezes() if c.startswith(str(alfa))]), 1, "o Post de outro uso não solta")
        trava = json.loads((alfa / ".forge" / "run" / "pesado.json").read_text(encoding="utf-8"))
        self.assertIsNotNone(trava, "o Post de outro uso não grava null na trava do projeto")  # P10: a soltura grava null, não apaga
        self.assertNotIn("/morto", self.ler_vezes(), "a vez de dono morto sai na gravação")
        (alfa / ".forge" / "run" / "pesado.json").unlink()  # a trava do projeto apagada à mão: a da máquina solta mesmo assim
        self.pedir(alfa, "a", "PostToolUse")
        self.pedir(beta, "b", uso="toolu_2")
        self.assertEqual(sorted(self.ler_vezes()), [str(beta / ".forge" / "run")])


# MP8 (v0479, diretriz 35): `forge-status --maquina`, a visão da máquina para o dono, sem projeto, com um e com vários.
class StatusDaMaquina(Maquina):
    def setUp(self):
        super().setUp()
        self.proc = self.tmp / "proc"
        self.proc.mkdir()
        (self.proc / "loadavg").write_text("1.5 1.0 0.5 1/100 42\n", encoding="utf-8")
        (self.proc / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n", encoding="utf-8")
        self.env.update(FORGE_PROC=str(self.proc), FORGE_NPROC="12", HOME=str(self.tmp))
        self.sessoes = {}

    def ativo(self, nome, versao="0.47.9", sessoes=1, **extra):
        raiz = self.tmp / nome
        (raiz / ".forge").mkdir(parents=True)
        if versao:
            (raiz / ".forge" / "versao").write_text(f"{versao}\n", encoding="utf-8")
        for n in range(sessoes):
            self.sessoes[f"{nome}{n}"] = {"projeto": nome, "pasta": str(raiz), "pid": os.getpid(), "batimento": time.time(),
                                          **extra}
        self.gravar(_maquina.ATIVOS, {"projetos": sorted({s["projeto"] for s in self.sessoes.values()}), "sessoes": self.sessoes})
        return raiz

    def linhas(self, *argumentos):
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-status"), "--maquina", *argumentos], env=self.env,
                           capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        return r.stdout.splitlines()


class SemProjeto(StatusDaMaquina):
    def test_sem_projeto_diz_nenhum_e_mede_a_maquina(self):
        linhas = self.linhas()
        self.assertEqual(linhas[0], "forge: nenhum projeto ativo na máquina")
        self.assertEqual(len(linhas), 3)
        medida, escape = linhas[1:]
        for trecho in ("máquina: 12 núcleos", "carga 1.5", "memória 8.0 de 16.0 GB disponíveis", "disco ",
                       "recusa cópia nova acima de 90%", "tarefas pesadas 0 de ", "teto 12 agentes"):
            self.assertIn(trecho, medida)
        self.assertEqual(escape, "máquina: FORGE_CARGA_LIVRE vale (um projeto ativo ou nenhum; só o dono)")

    def test_sem_leitura_de_proc_nem_de_nucleos(self):
        for arquivo in self.proc.iterdir():
            arquivo.unlink()
        self.env["FORGE_NPROC"] = "abc"
        medida = self.linhas()[1]
        for trecho in ("máquina: ? núcleos", "carga ?", "memória sem leitura", "teto 3 agentes"):
            self.assertIn(trecho, medida)

    def test_registro_ilegivel_nao_lista_e_recusa_o_escape(self):
        self.gravar(_maquina.ATIVOS, "{")
        nenhum, _, escape = self.linhas()
        self.assertEqual(nenhum, "forge: nenhum projeto ativo na máquina")
        self.assertEqual(escape, "máquina: FORGE_CARGA_LIVRE recusado: registro de projetos ilegível")

    def test_sessao_sem_pasta_absoluta_fica_fora(self):
        self.gravar(_maquina.ATIVOS, {"projetos": ["solto"], "sessoes": {
            "a": {"projeto": "solto", "pasta": "relativa", "pid": os.getpid(), "batimento": time.time()},
            "b": {"projeto": "solto", "pid": os.getpid(), "batimento": time.time()}}})
        self.assertEqual(self.linhas()[0], "forge: nenhum projeto ativo na máquina")

    def test_help_mostra_a_opcao(self):
        r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-status"), "--help"], env=self.env,
                           capture_output=True, text=True, timeout=60)
        self.assertIn("--maquina", r.stdout)
        self.assertIn("visão da máquina", r.stdout)


class UmProjeto(StatusDaMaquina):
    def test_um_projeto_tem_o_teto_inteiro_versao_e_decisoes(self):
        raiz = self.ativo("alfa", sessoes=2)
        (raiz / "docs" / "pedidos").mkdir(parents=True)
        (raiz / "docs" / "pedidos" / "p1.md").write_text(
            "## Histórico\nPERGUNTA AO DONO (2026-11-18 10:00): seguir? 1a) sim [recomendada]\n", encoding="utf-8")
        self.gravar("agentes.json", {str(raiz): {"uso": 3, "peso": 2, "espera": None}})
        projeto, _, escape = self.linhas()
        self.assertEqual(projeto.split(" · ")[:7], ["alfa", str(raiz), "Forge 0.47.9", "agentes 3 de 12 (peso 2)",
                                                    "decisões pendentes 1", "2 sessões", "batimento há 0 min"])
        self.assertIn("FORGE_CARGA_LIVRE vale", escape)

    def test_versao_do_clone_do_forge_link_e_sem_versao(self):
        raiz = self.ativo("clone", versao=None)
        (raiz / ".claude-plugin").mkdir()
        (raiz / ".claude-plugin" / "plugin.json").write_text('{"name": "forge", "version": "0.47.9"}', encoding="utf-8")
        (self.tmp / "fora").write_text("9.9.9\n", encoding="utf-8")
        (raiz / ".forge" / "versao").symlink_to(self.tmp / "fora")
        self.assertIn(" · Forge 0.47.9 · ", self.linhas()[0], "o link não se segue; vale a do plugin")
        (raiz / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        self.assertIn(" · Forge ? · ", self.linhas()[0])

    def test_pasta_da_versao_em_link_nao_se_segue(self):  # sonda S1 da segurança (A1)
        raiz = self.ativo("alfa", versao=None)
        (raiz / ".forge").rmdir()
        alvo = self.tmp / "alvo"
        alvo.mkdir()
        (alvo / "versao").write_text("segredo 9.8.7 aqui\n", encoding="utf-8")
        (alvo / "plugin.json").write_text('{"version": "9.8.6"}', encoding="utf-8")
        (raiz / ".forge").symlink_to(alvo)
        (raiz / ".claude-plugin").mkdir()
        (raiz / ".claude-plugin" / "plugin.json").write_text('{"version": "0.47.9"}', encoding="utf-8")
        self.assertIn(" · Forge 0.47.9 · ", self.linhas()[0], ".forge por link: vale a fonte seguinte")
        (raiz / ".claude-plugin" / "plugin.json").unlink()
        (raiz / ".claude-plugin").rmdir()
        (raiz / ".claude-plugin").symlink_to(alvo)
        self.assertIn(" · Forge ? · ", self.linhas()[0], "as duas pastas por link: nada se lê")

    def test_pedido_acima_do_teto_nao_conta(self):  # sonda S2 da segurança (A2)
        raiz = self.ativo("alfa")
        (raiz / "docs" / "pedidos").mkdir(parents=True)
        pergunta = "PERGUNTA AO DONO (2026-11-18 10:00): seguir? 1a) sim [recomendada]\n"
        (raiz / "docs" / "pedidos" / "p1.md").write_text(pergunta, encoding="utf-8")
        enorme = raiz / "docs" / "pedidos" / "p2.md"
        enorme.write_text(pergunta + "x" * forge_dono.TETO_DO_ARQUIVO, encoding="utf-8")
        self.assertIn(" · decisões pendentes 1 · ", self.linhas()[0], "o pedido acima do teto fica fora")
        enorme.write_text(pergunta + "x" * (forge_dono.TETO_DO_ARQUIVO - len(pergunta)), encoding="utf-8")
        self.assertIn(" · decisões pendentes 2 · ", self.linhas()[0], "no teto exato ainda conta")

    def test_decisoes_por_link_e_uso_fora_da_forma(self):
        raiz = self.ativo("alfa")
        (self.tmp / "outro").mkdir()
        (raiz / "docs").symlink_to(self.tmp / "outro")
        self.gravar("agentes.json", {str(raiz): 5})
        self.assertIn(" · agentes 0 de 12 (peso 1) · decisões pendentes ? · ", self.linhas()[0])
        self.gravar("agentes.json", "[1]")
        self.assertIn(" · agentes 0 de 12 (peso 1) · ", self.linhas()[0])

    def test_tarefa_pesada_viva_conta(self):
        self.ativo("alfa")
        self.gravar("pesado.json", {"x": {"pid": os.getpid(), "desde": time.time()}})
        self.assertIn("tarefas pesadas 1 de ", self.linhas()[1])


class VariosProjetos(StatusDaMaquina):
    def test_varios_projetos_repartem_o_teto_pelo_peso_e_o_escape_nao_vale(self):
        alfa, beta = self.ativo("alfa"), self.ativo("beta")
        self.gravar("agentes.json", {str(alfa): {"uso": 7, "peso": 2, "espera": None}, str(beta): {"uso": 1, "espera": None}})
        a, b, _, escape = self.linhas()
        self.assertIn(f"alfa · {alfa} · Forge 0.47.9 · agentes 7 de 8 (peso 2) · decisões pendentes 0 · 1 sessões", a)
        self.assertIn(f"beta · {beta} · Forge 0.47.9 · agentes 1 de 4 (peso 1) · ", b)
        self.assertEqual(escape, "máquina: FORGE_CARGA_LIVRE recusado: 2 projetos ativos, a trava de memória vale sempre")


if __name__ == "__main__":
    unittest.main()
