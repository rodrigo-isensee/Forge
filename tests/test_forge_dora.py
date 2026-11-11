"""0.45.7 (TM-16): `forge-check dora` (bin/forge_dora.py): frequência de entrega, espera da mudança, taxa de falha, recuperação e
vazão por semana, lidas de um repositório git e de um quadro de exemplo; um teste por métrica e o ramo de falha de cada guarda."""
import datetime
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "bin"))
import forge_dora as D  # noqa: E402

FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
FUSO = datetime.timezone(datetime.timedelta(hours=9))  # longe do fuso da máquina: o padrão local não acerta por acaso

HISTORICO = """# Histórico
| data-hora | cartão | de | para | motivo |
|---|---|---|---|---|
| 2026-11-02T10:00:00-03:00 | A | Entrada | Pronto | entregue |
| 2026-11-09T10:00:00-03:00 | a | Pronto | Pronto | de novo, conta uma vez |
| 2026-11-10T10:00:00-03:00 | B | Code review | Pronto | |
| 2026-11-10T11:00:00-03:00 | C | Entrada | Code review | |
| 2026-11-10T11:00:00 | D | Entrada | Pronto | |
| 2026-11-10T11:00:00-03:00 |  | Entrada | Pronto | |
| 2026-11-10T11:00:00-03:00 | E | Entrada | |
- 2026-11-10 11:00 linha solta fora da tabela
"""
ESCAPES = """| data-hora | pedido | parecer-final | achado-por | gravidade | controle-que-faltou | nota | origem |
|---|---|---|---|---|---|---|---|
| 2026-11-01 09:00 | p0 | x | ci | baixo | qa | antes da primeira release | codigo |
| 2026-11-04 09:00 | p1 | x | ci | alto | qa | na v0.2.0 | codigo |
| 2026-11-11 09:00 | p2 | x | uso | medio | qa | na v0.2.1, sem correção | codigo |
| 2026-11-05 | p3 | x | uso | medio | qa | data sem hora | codigo |
| 2026-11-06 09:00 |  | x | uso | medio | qa | sem pedido | codigo |
"""


class Exemplo:
    """Releases v0.1.0 (02/11 10:00), v0.2.0 (03/11 16:00, commits de 03/11 10:00 e 16:00) e v0.2.1 (10/11 12:00, commit de autor
    às 08:00), todas em -03:00; a v1.0.0-rc1 (05/11) e a `marco` não são release."""

    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.git("init", "-q", "-b", "main")
        self.commit("c1", "2026-11-02T10:00:00-03:00")
        self.git("tag", "v0.1.0")
        self.commit("c2", "2026-11-03T10:00:00-03:00")
        self.commit("c3", "2026-11-03T16:00:00-03:00")
        self.git("tag", "v0.2.0")
        self.commit("c4", "2026-11-05T10:00:00-03:00")
        self.git("tag", "v1.0.0-rc1")
        self.git("tag", "marco")
        self.commit("c5", "2026-11-10T08:00:00-03:00", "2026-11-10T12:00:00-03:00")
        self.git("tag", "v0.2.1")
        kanban = self.pasta / "docs" / "kanban"
        kanban.mkdir(parents=True)
        (kanban / "historico.md").write_text(HISTORICO, encoding="utf-8")
        (kanban / "escapes.md").write_text(ESCAPES, encoding="utf-8")

    def git(self, *args, data=None):
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_") or k.startswith("GIT_CONFIG")})
        env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        if data:
            env.update(GIT_AUTHOR_DATE=data[0], GIT_COMMITTER_DATE=data[1])
        subprocess.run(["git", "-C", str(self.pasta), *args], check=True, capture_output=True, env=env)

    def commit(self, nome, autor, commit=None):
        (self.pasta / nome).write_text(nome, encoding="utf-8")
        self.git("add", nome)
        self.git("commit", "-q", "-m", nome, data=(autor, commit or autor))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.ex = Exemplo(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def calcular(self, desde=None, ate=None):
        return D.calcular(self.ex.pasta, self.ex.pasta, desde, ate, FUSO)


class Metricas(Base):
    def test_frequencia_conta_so_tags_de_versao_por_semana(self):
        self.assertEqual(self.calcular()["frequencia"], {"n": 3, "semanas": {"2026-S45": 2, "2026-S46": 1}})

    def test_espera_da_mudanca_do_commit_de_autor_ate_a_tag(self):
        self.assertEqual(self.calcular()["espera_da_mudanca_h"], {"n": 4, "brutos": [0.0, 4.0, 6.0, 122.0]})

    def test_taxa_de_falha_conta_release_com_escape(self):
        self.assertEqual(self.calcular()["taxa_de_falha"], {"entregas": 3, "com_falha": 2})

    def test_recuperacao_do_escape_ate_a_release_seguinte(self):
        # escape 04/11 09:00 +09:00 = 04/11 00:00Z; v0.2.1 em 10/11 15:00Z: 159 h; o de 11/11 fica aberto
        self.assertEqual(self.calcular()["recuperacao_h"], {"n": 1, "brutos": [159.0], "abertas": 1})

    def test_vazao_conta_cada_cartao_uma_vez_no_primeiro_pronto(self):
        self.assertEqual(self.calcular()["vazao"], {"n": 2, "semanas": {"2026-S45": 1, "2026-S46": 1}})

    def test_recusa_linha_incompleta_com_o_motivo(self):
        self.assertEqual(self.calcular()["recusados"], [
            {"fonte": "escapes.md:6", "cartao": "p3", "motivo": "data-hora ilegível"},
            {"fonte": "escapes.md:7", "cartao": "-", "motivo": "coluna vazia ou faltando"},
            {"fonte": "escapes.md:3", "cartao": "p0", "motivo": "escape antes da primeira release"},
            {"fonte": "historico.md:8", "cartao": "D", "motivo": "data-hora sem fuso"},
            {"fonte": "historico.md:9", "cartao": "-", "motivo": "coluna vazia ou faltando"},
            {"fonte": "historico.md:10", "cartao": "E", "motivo": "coluna vazia ou faltando"}])

    def test_janela_inclusiva_corta_release_escape_e_cartao(self):
        dados = self.calcular(datetime.date(2026, 11, 4), datetime.date(2026, 11, 9))  # v0.2.0 é 04/11 em +09:00: inclusiva
        self.assertEqual(dados["frequencia"]["semanas"], {"2026-S45": 1})
        self.assertEqual(dados["espera_da_mudanca_h"]["brutos"], [0.0, 6.0])
        self.assertEqual((dados["taxa_de_falha"], dados["recuperacao_h"]["n"]), ({"entregas": 1, "com_falha": 1}, 1))
        self.assertEqual(dados["vazao"]["semanas"], {})

    def test_quadro_ausente_vale_vazio_sem_recusado(self):
        with tempfile.TemporaryDirectory() as vazio:
            dados = D.calcular(self.ex.pasta, Path(vazio), fuso=FUSO)
        self.assertEqual((dados["vazao"]["n"], dados["recusados"], dados["taxa_de_falha"]["com_falha"]), (0, [], 0))

    def test_git_que_falha_da_aviso_e_nenhuma_release(self):
        with tempfile.TemporaryDirectory() as fora:
            dados = D.calcular(Path(fora), self.ex.pasta, fuso=FUSO)
        self.assertEqual(dados["frequencia"]["n"], 0)
        self.assertEqual(len(dados["avisos"]), 1)


class Brutos(unittest.TestCase):
    def test_abaixo_de_20_so_os_brutos_e_com_20_os_percentis(self):
        self.assertEqual(D.resumir(list(range(19))), {"n": 19, "brutos": list(range(19))})
        self.assertEqual(D.resumir(list(range(20))), {"n": 20, "p50": 9.5, "p90": 17.9})

    def test_media_por_semana_so_com_20(self):
        self.assertNotIn("media_por_semana", D.por_semana({"S1": 19}))
        self.assertEqual(D.por_semana({"S1": 12, "S2": 8}).get("media_por_semana"), 10.0)

    def test_taxa_pct_so_com_20_releases(self):
        base = datetime.datetime(2026, 1, 5, tzinfo=FUSO)
        for n, esperado in ((19, None), (20, 0.0)):
            lista = [(f"v0.0.{i}", base + datetime.timedelta(days=i)) for i in range(n)]
            with mock.patch.object(D, "releases", return_value=(lista, [])), \
                    mock.patch.object(D, "esperas_da_mudanca", return_value=[]), tempfile.TemporaryDirectory() as vazio:
                self.assertEqual(D.calcular(Path(vazio), Path(vazio), fuso=FUSO)["taxa_de_falha"].get("taxa_pct"), esperado)


class Comando(Base):
    def rodar(self, *args):
        env = {k: v for k, v in sem_manutencao().items() if not k.startswith("FORGE_")}
        return subprocess.run([sys.executable, "-I", FORGE_CHECK, "dora", "--raiz", str(self.ex.pasta), *args],
                              capture_output=True, text=True, env=env, cwd=self.ex.pasta)

    def test_texto_traz_cada_medida_e_os_recusados(self):
        r = self.rodar("--fuso", "+09:00")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('dora: frequencia n=3 semanas={"2026-S45":2,"2026-S46":1}', r.stdout)
        self.assertIn("dora: recuperacao_h n=1 brutos=[159.0] abertas=1", r.stdout)
        self.assertIn("dora: recusado historico.md:8 D motivo: data-hora sem fuso", r.stdout)

    def test_raiz_pedidos_le_o_quadro_de_la(self):
        with tempfile.TemporaryDirectory(dir=self.ex.pasta) as vazio:  # dentro da raiz: o forge-check recusa fora dela
            r = self.rodar("--fuso", "+09:00", "--raiz-pedidos", vazio)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('dora: vazao n=0 semanas={}', r.stdout)
        self.assertIn('dora: frequencia n=3 ', r.stdout)

    def test_json(self):
        r = self.rodar("--fuso", "+09:00", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(r.stdout.startswith("{"), r.stdout)
        self.assertEqual(json.loads(r.stdout)["vazao"]["n"], 2)

    def test_data_ou_fuso_invalido_sai_2(self):
        for args in (("--desde", "2026-13-01"), ("--fuso", "-3h")):
            self.assertEqual(self.rodar(*args).returncode, 2, args)


if __name__ == "__main__":
    unittest.main()
