"""MP3 (diretriz 35, dono 17/11 21:11): o teto de agentes flexível entre os projetos ativos da máquina."""
import json
import os
import subprocess
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
from ambiente_git import sem_manutencao  # noqa: E402
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
        """Sessões vivas (o pid deste processo) dos projetos `nomes` (caminhos sob o tmp) no registro do MP2."""
        agora, pid = time.time(), os.getpid()
        sessoes = {f"s-{n}": {"projeto": Path(n).name, "pasta": self.chave(n), "pid": pid, "inicio": pesado.inicio_de(pid),
                              "batimento": batimento or agora} for n in nomes}
        self.gravar(_maquina.ATIVOS, {"projetos": sorted({Path(n).name for n in nomes}), "sessoes": sessoes})

    def raiz(self, nome, peso=None):
        raiz = self.raizes.setdefault(nome, self.tmp.resolve() / nome)
        (raiz / ".forge").mkdir(parents=True, exist_ok=True)
        if peso or not (raiz / ".forge" / "config.json").exists():
            (raiz / ".forge" / "config.json").write_text(json.dumps({"peso": peso} if peso else {}), encoding="utf-8")
        return raiz

    def chave(self, nome):
        """A chave do projeto `nome` na máquina: a pasta da cópia principal (`_maquina.identidade`)."""
        return str(self.raiz(nome))

    def gravar(self, nome, dados):
        """O uso de agentes da máquina se escreve pelo nome do projeto no teste e vai ao arquivo pela pasta."""
        if nome == agentes.USO_DA_MAQUINA and isinstance(dados, dict):
            dados = {self.chave(projeto): entrada for projeto, entrada in dados.items()}
        super().gravar(nome, dados)

    def maquina(self, nome, peso=None):
        return agentes.Maquina(Falso(self.raiz(nome, peso)), time.time())

    def usos(self):
        """O uso de agentes da máquina, de volta pelo nome do projeto no teste."""
        usos = json.loads((self.tmp / "maquina" / agentes.USO_DA_MAQUINA).read_text(encoding="utf-8"))
        return {Path(pasta).relative_to(self.tmp.resolve()).as_posix(): entrada for pasta, entrada in usos.items()}

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

    def test_sessao_sem_pasta_de_projeto_e_config_fora_da_forma_nao_contam(self):
        self.abrir("alfa")
        registro = json.loads((self.tmp / "maquina" / _maquina.ATIVOS).read_text(encoding="utf-8"))
        registro["sessoes"]["s-5"] = dict(registro["sessoes"]["s-alfa"], pasta=5)
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

    def test_dois_projetos_de_mesmo_nome_de_pasta_sao_dois(self):
        """Segurança A2: a chave é a pasta da cópia principal; o homônimo noutra pasta não sai da conta."""
        self.abrir("p1/app", "p2/app")
        self.gravar(agentes.USO_DA_MAQUINA, {"p2/app": {"uso": 4, "peso": 1, "espera": None}})
        self.recusado("máquina cheia: 8 de 8 vagas com 2 projetos ativos; parte de app 4, uso 4", self.disparar("p1/app", 4))
        self.assertEqual(sorted(self.usos()), ["p1/app", "p2/app"], "cada um com a sua entrada")

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
                 (agentes.USO_DA_MAQUINA, "[1]"), (agentes.USO_DA_MAQUINA, {"beta": 3}),
                 (agentes.USO_DA_MAQUINA, {"beta": {"uso": -1}}), (agentes.USO_DA_MAQUINA, {"beta": {"uso": True}}),
                 (agentes.USO_DA_MAQUINA, {"beta": {"uso": 1, "espera": "x"}})]
        for nome, bruto in casos:
            with self.subTest(nome=nome, bruto=bruto):
                self.abrir("alfa", "beta")
                (self.tmp / "maquina" / agentes.USO_DA_MAQUINA).unlink(missing_ok=True)
                self.gravar(nome, bruto)
                with self.assertRaises(Exception) as caso:
                    self.disparar("alfa", 0)
                self.assertIsInstance(caso.exception, agentes.Ilegivel, "a forma conferida, não um erro qualquer")
                self.assertEqual(str(caso.exception), f"{_maquina.PASTA}/{nome}", "a recusa nomeia o arquivo")


class NoHook(Base):
    """O hook inteiro, noutro processo (ambiente limpo do `test_maquina`), com 4 núcleos simulados."""

    def setUp(self):
        super().setUp()
        (self.tmp / "p").mkdir()
        self.env.update(FORGE_NPROC="4", FORGE_PROC=str(montar_proc(self.tmp / "p")))
        self.alfa = self.projeto("alfa")

    def rodar(self, prompt="..."):
        return self.hook("agentes", self.alfa, hook_event_name="PreToolUse", tool_name="Agent", tool_use_id="toolu_1",
                         tool_input={"subagent_type": "Explore", "description": "Ler", "prompt": prompt})

    def test_sessao_em_worktree_conta_como_o_projeto_dela(self):
        """Review e segurança A1: o registro (MP2) e o teto (MP3) dão à worktree o nome e a pasta da cópia principal."""
        beta, wt = self.projeto("beta"), self.tmp / "wt-beta"
        for args in (("commit", "-q", "--allow-empty", "-m", "x"), ("worktree", "add", "-q", "--detach", str(wt))):
            subprocess.run(["git", "-C", str(beta), *args], env=sem_manutencao(self.env), check=True, capture_output=True,
                           timeout=60)
        (wt / ".forge").mkdir()
        (wt / ".forge" / "versao").write_text("0.5.0\n", encoding="utf-8")
        for raiz, sessao in ((self.alfa, "s1"), (wt, "s2")):
            self.assertEqual(self.anotar(raiz, sessao, "SessionStart").returncode, 0)
        self.assertEqual(self.registro()["projetos"], ["alfa", "beta"])
        self.assertEqual(self.registro()["sessoes"]["s2"]["pasta"], self.chave("beta"))
        self.gravar(agentes.USO_DA_MAQUINA, {"beta": {"uso": 4, "peso": 1, "espera": None}})
        r = self.rodar()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("máquina cheia: 4 de 4 vagas com 2 projetos ativos; parte de alfa 2, uso 0", r.stderr)
        self.assertEqual(self.usos()["beta"]["uso"], 4, "o uso da worktree segue na conta")

    def test_branch_ocupada_nao_conta_a_vaga_na_maquina(self):
        """Review A3: a recusa por branch ocupada vem antes da máquina; o uso de alfa não sobe."""
        (self.alfa / "docs" / "briefs").mkdir(parents=True)
        (self.alfa / "docs" / "briefs" / "a.md").write_text(
            "Agente destino: forge:x\nBranch: melhoria/a   Base: develop\nEtapa: codigo\n\n## Objetivo\nx\n", encoding="utf-8")
        (self.alfa / ".forge" / "run").mkdir()
        ocupante = {"id": "a1", "tipo": "forge:qa-engineer", "descricao": "o", "desde": time.time(),
                    "branches": ["melhoria/a"], "escrita": ["melhoria/a"]}
        (self.alfa / ".forge" / "run" / "agentes.json").write_text(json.dumps({"agentes": [ocupante]}), encoding="utf-8")
        self.gravar(agentes.USO_DA_MAQUINA, {"alfa": {"uso": 1, "peso": 1, "espera": None}})
        r = self.rodar("docs/briefs/a.md")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("melhoria/a ocupada por", r.stderr)
        self.assertEqual(self.usos()["alfa"]["uso"], 1, "a recusa não deixa vaga fantasma")

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
        self.assertIn("registro da máquina ilegível: ~/.forge/maquina/projetos-ativos.json; o usuário pode apagá-lo", r.stderr)

    def test_pasta_da_maquina_aberta_ao_grupo_recusa(self):
        """Outro erro ao ler a máquina (pasta fora de 0700) também recusa (falha fechada), com a pasta."""
        self.gravar(_maquina.ATIVOS, {"sessoes": {}})
        os.chmod(self.tmp / "maquina", 0o750)
        r = self.rodar()
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("registro da máquina ilegível (~/.forge/maquina; registrado no erros.log)", r.stderr)


if __name__ == "__main__":
    unittest.main()
