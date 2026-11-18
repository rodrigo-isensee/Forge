"""MP2 e MP4 (diretriz 35): o registro de projetos ativos da máquina e a fila pesada única, com projetos simulados."""
import json
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
sys.path.insert(0, str(RAIZ / "tests"))
import _maquina  # noqa: E402
import pesado  # noqa: E402
from test_hooks import ambiente_limpo, lancador, pid_morto, repositorio_vazio  # noqa: E402


class Maquina(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-maquina-"))
        self.env = dict(ambiente_limpo(), FORGE_MAQUINA=str(self.tmp / "maquina"), FORGE_PESADO_ESPERA_S="0")

    def projeto(self, nome):
        raiz = self.tmp / nome
        raiz.mkdir()
        repositorio_vazio(raiz, "develop")
        (raiz / ".forge").mkdir()
        (raiz / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        (raiz / ".forge" / "config.json").write_text(json.dumps({"pesados": ["npx playwright test"]}), encoding="utf-8")
        return raiz

    def hook(self, nome, raiz, **entrada):
        entrada = {"cwd": str(raiz), **entrada}
        return subprocess.run(lancador(nome), input=json.dumps(entrada), cwd=raiz, env=self.env, capture_output=True,
                              text=True, timeout=60)

    def anotar(self, raiz, sessao, evento="Stop"):
        return self.hook("_maquina", raiz, hook_event_name=evento, session_id=sessao)

    def registro(self):
        return json.loads((self.tmp / "maquina" / _maquina.ATIVOS).read_text(encoding="utf-8"))

    def status(self):
        return subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-status"), "--maquina"], env=self.env,
                              capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL).stdout

    def gravar(self, nome, dados):
        (self.tmp / "maquina").mkdir(exist_ok=True)
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
        (self.tmp / "maquina").mkdir()
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

    def test_pasta_em_link_nao_grava(self):
        alvo = self.tmp / "alvo"
        alvo.mkdir()
        (self.tmp / "maquina").symlink_to(alvo)
        self.assertEqual(self.anotar(self.projeto("alfa"), "s1").returncode, 0)
        self.assertEqual(list(alvo.iterdir()), [])


class FilaPesada(Maquina):
    def pedir(self, raiz, agente, evento="PreToolUse", uso="toolu_1"):
        return self.hook("pesado", raiz, hook_event_name=evento, tool_name="Bash", tool_use_id=uso, agent_id=agente,
                         tool_input={"command": "npx playwright test"})

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
        self.assertNotIn("/morto", self.ler_vezes(), "a vez de dono morto sai na gravação")
        (alfa / ".forge" / "run" / "pesado.json").unlink()  # a trava do projeto apagada à mão: a da máquina solta mesmo assim
        self.pedir(alfa, "a", "PostToolUse")
        self.pedir(beta, "b", uso="toolu_2")
        self.assertEqual(sorted(self.ler_vezes()), [str(beta / ".forge" / "run")])


if __name__ == "__main__":
    unittest.main()
