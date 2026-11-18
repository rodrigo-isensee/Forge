"""MP3 (diretriz 35, dono 17/11 21:11): o teto de agentes flexível entre os projetos ativos da máquina."""
import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
sys.path.insert(0, str(RAIZ / "tests"))
import _maquina  # noqa: E402
import agentes  # noqa: E402
import pesado  # noqa: E402
from test_agentes_clone import montar_proc  # noqa: E402
from test_maquina import Maquina  # noqa: E402

TOTAL = 8


class Falso:
    """O pedaço do Hook que a `agentes.Maquina` lê: a raiz e a cópia principal (o nome do projeto)."""

    def __init__(self, raiz):
        self.raiz = raiz

    def copia_principal(self):
        return self.raiz


class Base(Maquina):
    def setUp(self):
        super().setUp()
        self.addCleanup(mock.patch.stopall)
        mock.patch.dict(os.environ, {"FORGE_MAQUINA": self.env["FORGE_MAQUINA"]}).start()
        self.raizes = {}

    def abrir(self, *nomes, batimento=None):
        """Sessões vivas (o pid deste processo) dos projetos `nomes` no registro do MP2."""
        agora, pid = time.time(), os.getpid()
        sessoes = {f"s-{n}": {"projeto": n, "pid": pid, "inicio": pesado.inicio_de(pid), "batimento": batimento or agora}
                   for n in nomes}
        self.gravar(_maquina.ATIVOS, {"projetos": sorted(nomes), "sessoes": sessoes})

    def raiz(self, nome, peso=None):
        if nome not in self.raizes:
            self.raizes[nome] = raiz = self.tmp / nome
            (raiz / ".forge").mkdir(parents=True)
            (raiz / ".forge" / "config.json").write_text(json.dumps({"peso": peso} if peso else {}), encoding="utf-8")
        return self.raizes[nome]

    def maquina(self, nome, peso=None):
        return agentes.Maquina(Falso(self.raiz(nome, peso)), time.time())

    def usos(self):
        return json.loads((self.tmp / "maquina" / agentes.USO_DA_MAQUINA).read_text(encoding="utf-8"))

    def disparar(self, nome, meu):
        return self.maquina(nome).recusa(meu, TOTAL)

    def recusado(self, trecho, texto):
        self.assertIsNotNone(texto, f"esperava a recusa: {trecho}")
        self.assertIn(trecho, texto)


class QuatroCasos(Base):
    def test_um_ativo_usa_o_teto_cheio(self):
        self.abrir("alfa")
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": TOTAL, "peso": 1, "espera": None}})  # beta fechou
        self.assertIsNone(self.disparar("alfa", TOTAL - 1))
        self.assertEqual(self.usos(), {"alfa": {"uso": TOTAL, "peso": 1.0, "espera": None}}, "beta devolveu a parte")

    def test_dois_ativos_um_parado_o_outro_usa_quase_tudo(self):
        self.abrir("alfa", "beta")
        for meu in range(TOTAL):
            self.assertIsNone(self.disparar("alfa", meu), meu)
        texto = self.disparar("alfa", TOTAL)
        self.recusado(f"máquina cheia: {TOTAL} de {TOTAL} vagas com 2 projetos ativos; parte de alfa 4, uso {TOTAL}", texto)
        self.assertNotIn("a próxima vaga", texto)
        self.assertEqual((self.usos()["alfa"]["uso"], self.usos()["alfa"]["espera"]), (TOTAL, None),
                         "a recusa não conta a vaga; acima da parte não deixa espera")

    def test_na_parte_e_com_a_maquina_cheia_nao_deixa_espera(self):
        self.abrir("alfa", "beta")
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 4, "peso": 1, "espera": None}})
        self.recusado("parte de alfa 4, uso 4", self.disparar("alfa", 4))
        self.assertIsNone(self.usos()["alfa"]["espera"])

    def test_sessao_sem_nome_de_projeto_e_config_fora_da_forma_nao_contam(self):
        self.abrir("alfa")
        registro = json.loads((self.tmp / "maquina" / _maquina.ATIVOS).read_text(encoding="utf-8"))
        registro["sessoes"]["s-5"] = dict(registro["sessoes"]["s-alfa"], projeto=5)
        self.gravar(_maquina.ATIVOS, registro)
        (self.raiz("alfa") / ".forge" / "config.json").write_text("[3]", encoding="utf-8")
        try:
            texto = self.disparar("alfa", TOTAL)
        except AttributeError as erro:
            self.fail(f"config que não é objeto quebrou a leitura do peso: {erro}")
        self.assertIsNone(texto, "só alfa ativo: o teto de sempre")
        self.assertEqual(self.usos()["alfa"]["peso"], 1.0)

    def test_o_parado_volta_e_ganha_a_proxima_vaga(self):
        self.abrir("alfa", "beta")
        self.gravar(agentes.USO_DA_MAQUINA, {"alfa": {"uso": TOTAL, "peso": 1, "espera": None}})
        self.recusado("parte de beta 4, uso 0; a próxima vaga livre é sua", self.disparar("beta", 0))
        self.maquina("alfa").anotar(TOTAL - 1)  # um agente de alfa terminou: nenhum é interrompido
        self.recusado("parte de alfa 4, uso 7: a vaga emprestada volta a beta", self.disparar("alfa", TOTAL - 1))
        self.assertIsNone(self.disparar("beta", 0))
        self.assertIsNone(self.usos()["beta"]["espera"], "a vaga devolvida apaga a espera")

    def test_a_espera_vence_e_o_emprestimo_volta_a_valer(self):
        self.abrir("alfa", "beta")
        velha = time.time() - agentes.RESERVA_S - 1
        self.gravar(agentes.USO_DA_MAQUINA, {"alfa": {"uso": 5, "peso": 1, "espera": None},
                                             "beta": {"uso": 0, "peso": 1, "espera": velha}})
        self.assertIsNone(self.disparar("alfa", 5))

    def test_so_quem_esta_abaixo_da_parte_cobra_a_vaga(self):
        self.abrir("alfa", "beta", "gama")  # 8 vagas, 3 projetos: parte 2 de cada
        for uso_de_beta, esperado in ((2, None), (1, "a vaga emprestada volta a beta")):
            with self.subTest(uso_de_beta=uso_de_beta):
                self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": uso_de_beta, "peso": 1, "espera": time.time()}})
                texto = self.disparar("alfa", 2)
                self.assertIsNone(texto) if esperado is None else self.recusado(esperado, texto)
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 1, "peso": 1, "espera": time.time()}})
        self.assertIsNone(self.disparar("alfa", 1), "dentro da parte, alfa dispara mesmo com a espera de beta")

    def test_um_fecha_e_o_outro_recupera_a_parte(self):
        self.abrir("alfa", "beta")
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 4, "peso": 1, "espera": None}})
        self.recusado("máquina cheia", self.disparar("alfa", 4))
        self.abrir("alfa")  # a sessão de beta fechou
        self.assertIsNone(self.disparar("alfa", 4))
        self.assertEqual(list(self.usos()), ["alfa"])

    def test_quem_para_de_bater_devolve_a_parte(self):
        self.abrir("beta", batimento=time.time() - _maquina.BATIMENTO_S - 1)
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": TOTAL, "peso": 1, "espera": None}})
        self.assertIsNone(self.disparar("alfa", 0))

    def test_o_peso_muda_a_parte(self):
        self.abrir("alfa", "beta")
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 2, "peso": 1, "espera": None}})
        self.recusado("parte de alfa 6, uso 6", self.maquina("alfa", peso=3).recusa(6, TOTAL))
        for invalido in (True, 0, -1, agentes.PESO_MAXIMO + 1, "3"):
            self.assertEqual(agentes.peso_valido(invalido), 1.0, invalido)
        self.assertEqual(agentes.peso_valido(agentes.PESO_MAXIMO), agentes.PESO_MAXIMO)


class FalhaFechada(Base):
    def test_registro_ou_uso_fora_da_forma_levanta(self):
        casos = [(_maquina.ATIVOS, "{"), (_maquina.ATIVOS, "[1]"), (_maquina.ATIVOS, '{"sessoes": [1]}'),
                 (agentes.USO_DA_MAQUINA, "[1]"), (agentes.USO_DA_MAQUINA, '{"beta": 3}'),
                 (agentes.USO_DA_MAQUINA, '{"beta": {"uso": -1}}'), (agentes.USO_DA_MAQUINA, '{"beta": {"uso": true}}'),
                 (agentes.USO_DA_MAQUINA, '{"beta": {"uso": 1, "espera": "x"}}')]
        for nome, bruto in casos:
            with self.subTest(nome=nome, bruto=bruto):
                self.abrir("alfa", "beta")
                (self.tmp / "maquina" / agentes.USO_DA_MAQUINA).unlink(missing_ok=True)
                self.gravar(nome, bruto)
                with self.assertRaises(Exception) as caso:
                    self.disparar("alfa", 0)
                self.assertIsInstance(caso.exception, ValueError, "a forma conferida, não um erro qualquer")


class NoHook(Base):
    """O hook inteiro, noutro processo (ambiente limpo do `test_maquina`), com 4 núcleos simulados."""

    def setUp(self):
        super().setUp()
        (self.tmp / "p").mkdir()
        self.env.update(FORGE_NPROC="4", FORGE_PROC=str(montar_proc(self.tmp / "p")))
        self.alfa = self.projeto("alfa")

    def rodar(self):
        return self.hook("agentes", self.alfa, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_1",
                         tool_input={"subagent_type": "Explore", "description": "Ler", "prompt": "..."})

    def test_um_projeto_libera_e_anota_o_uso(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.usos()["alfa"]["uso"], 1)

    def test_maquina_cheia_recusa_com_a_parte_e_o_uso(self):
        self.abrir("alfa", "beta")
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 4, "peso": 1, "espera": None}})
        r = self.rodar()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("máquina cheia: 4 de 4 vagas com 2 projetos ativos; parte de alfa 2, uso 0", r.stderr)

    def test_registro_ilegivel_recusa(self):
        self.gravar(_maquina.ATIVOS, "{")
        r = self.rodar()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("registro da máquina ilegível", r.stderr)


if __name__ == "__main__":
    unittest.main()
