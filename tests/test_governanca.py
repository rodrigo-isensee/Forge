"""0.43.1 H: `forge-check metricas` (tempo do código pronto à develop e à main, voltas, revalidações, suítes, espera do dono,
reprovações por classe e mérito declarado) e `forge-check regras` (validade: `Revisar em:` e `Medida:`), com pedidos, registro e
repositório git de exemplo."""
import datetime
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
FUSO = datetime.timezone(datetime.timedelta(hours=-3))


def carregar_modulo():
    spec = importlib.util.spec_from_file_location("forge_governanca_teste", RAIZ / "bin" / "forge_governanca.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


G = carregar_modulo()


def rodar(*args, cwd=None):
    r = subprocess.run([sys.executable, FORGE_CHECK, *args], capture_output=True, text=True, cwd=cwd, env=sem_manutencao())
    return r.returncode, r.stdout, r.stderr


class Repositorio:
    """Repositório temporário: main e develop, a branch do E1 mesclada na develop (03/11 10:00) e a develop na main (04/11 10:00);
    a branch do E2 nunca mesclada."""

    def __init__(self, pasta):
        self.pasta = pasta
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.commit("base", "2026-11-01T09:00:00-03:00")
        self.git("branch", "develop")
        self.git("switch", "-q", "-c", "melhoria/e1")
        self.e1 = self.commit("e1", "2026-11-02T10:00:00-03:00")
        self.git("switch", "-q", "-c", "melhoria/e2", "main")
        self.e2 = self.commit("e2", "2026-11-02T12:00:00-03:00")
        self.git("switch", "-q", "develop")
        self.git("merge", "-q", "--no-ff", "-m", "merge e1", "melhoria/e1", data="2026-11-03T10:00:00-03:00")
        self.git("switch", "-q", "main")
        self.git("merge", "-q", "--no-ff", "-m", "merge develop", "develop", data="2026-11-04T10:00:00-03:00")

    def git(self, *args, data=None):
        env = sem_manutencao()
        if data:
            env.update(GIT_AUTHOR_DATE=data, GIT_COMMITTER_DATE=data)
        r = subprocess.run(["git", "-C", str(self.pasta), *args], capture_output=True, text=True, env=env, check=True)
        return r.stdout.strip()

    def commit(self, nome, data):
        (self.pasta / f"{nome}.txt").write_text(nome, encoding="utf-8")
        self.git("add", f"{nome}.txt")
        self.git("commit", "-q", "-m", nome, data=data)
        return self.git("rev-parse", "HEAD")


PEDIDO = """---
id: versao-900
---
# Pedido versao-900: exemplo

## Decisões do usuário (registro literal)
PERGUNTA AO DONO (2026-11-02 14:00): "posso?"
DECISÃO DO DONO (2026-11-02 14:20): "pode"

## Histórico
- 2026-11-02 09:00: (E1 EXEMPLO) brief -1 aprovado na rodada 2; delegado ao forge:tech-lead.
- 2026-11-02 09:30: (E1) entrega não cumpriu (escopo); volta -2.
- 2026-11-02 10:30: entrega conferida {e1} (E1 EXEMPLO, melhoria/e1, brief -2).
- 2026-11-02 11:00: (E1) push da melhoria/e1 passou (rc 0).
- 2026-11-02 11:10: (E1) push reprovou na suíte (FLAKY-CARGA).
- 2026-11-02 12:00: (E1) revalidação do review entregue.
- 2026-11-02 12:10: (E1) a base do delta vai ao dono.
- 2026-11-02 12:40: DECISÃO DO DONO (2026-11-02 12:35): "Autorizo"
- 2026-11-02 13:00: (E2) entrega conferida {e2} (E2 OUTRO, melhoria/e2).
- 2026-11-03 08:00: linha do pedido inteiro, sem item; push único reprovou (rc 1).
"""

REGISTRO = """# Registro de conferências (S-4)

| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota |
|---|---|---|---|---|---|---|---|
| 2026-11-02 08:55 | versao-900 | docs/briefs/versao-900-tech-lead-1.md | brief | 1 | reprovado | s | Fora velho | escopo | jarvis |
| 2026-11-02 08:58 | versao-900 | docs/briefs/versao-900-tech-lead-1.md | brief | 2 | aprovado | — |  | — | conferente |
| 2026-11-02 09:30 | versao-900 | docs/briefs/versao-900-tech-lead-1.md | entrega | 1 | não cumpriu | parcial | arquivo fora | escopo | jarvis |
| 2026-11-03 09:00 | versao-900 | docs/briefs/versao-900-tech-lead-3.md | brief | 1 | reprovado | n | forma | forma | jarvis |
| 2026-11-03 09:00 | versao-901 | docs/briefs/versao-901-tech-lead-1.md | brief | 1 | reprovado | s | outro pedido | decisao | jarvis |
"""

HISTORICO_DO_QUADRO = """| Data/hora | Cartão | De | Para | Motivo |
|---|---|---|---|---|
| 2026-11-02T09:00:00-03:00 | C1 | — | Fazendo | — |
| 2026-11-02T10:30:00-03:00 | C1 | Code review | Pronto | — |
| 2026-11-02T10:00:00-03:00 | c1 | Fazendo | Code review | — |
| 2026-11-02T11:00:00-03:00 | C2 | — | Fazendo | — |
| 2026-11-02T11:30:00 | C3 | — | Fazendo | sem fuso: fora |
| 2026-11-02T99:00:00-03:00 | C4 | — | Fazendo | hora inválida: fora |
| C5 | — | Fazendo | sem hora | — |
| 2026-11-02T12:00:00-03:00 | C6 |
"""


class Metricas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="forge-metricas-"))
        cls.repo = Repositorio(cls.tmp)
        (cls.tmp / "docs" / "pedidos").mkdir(parents=True)
        (cls.tmp / "docs" / "kanban").mkdir(parents=True)
        (cls.tmp / "docs" / "pedidos" / "versao-900.md").write_text(PEDIDO.format(e1=cls.repo.e1, e2=cls.repo.e2[:9]), encoding="utf-8")
        (cls.tmp / "docs" / "kanban" / "conferencias.md").write_text(REGISTRO, encoding="utf-8")
        cls.args = ("--raiz", str(cls.tmp), "metricas", "--pedido", "versao-900", "--fuso=-03:00", "--agora", "2026-11-02T15:00",
                    "--develop", "develop", "--main", "main")
        rc, saida, cls.erro = rodar(*cls.args, "--json")
        assert rc == 0, (saida, cls.erro)
        cls.dados = json.loads(saida)
        cls.itens = {i["item"]: i for i in cls.dados["itens"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_tempo_do_pronto_ate_a_develop_e_a_main_vem_do_git(self):
        e1 = self.itens["E1"]
        self.assertEqual(e1["pronto"], "2026-11-02T10:30-03:00")
        self.assertEqual(e1["sha"], self.repo.e1)
        self.assertEqual(e1["pronto_ate_develop_h"], 23.5)  # merge na develop em 03/11 10:00
        self.assertEqual(e1["pronto_ate_main_h"], 47.5)  # develop na main em 04/11 10:00
        self.assertIsNone(e1["aberto_h"])

    def test_sha_fora_da_develop_fica_aberto_com_as_horas_ate_agora(self):
        e2 = self.itens["E2"]
        self.assertIsNone(e2["develop"])
        self.assertIsNone(e2["pronto_ate_develop_h"])
        self.assertEqual(e2["aberto_h"], 2.0)

    def test_voltas_revalidacoes_e_suites_do_item(self):
        e1 = self.itens["E1"]
        self.assertEqual((e1["voltas"], e1["revalidacoes"], e1["suites"], e1["suites_falhas"]), (1, 1, 2, 1))
        self.assertEqual(e1["branches"], ["melhoria/e1"])

    def test_linha_sem_item_vale_para_o_pedido(self):
        geral = self.itens["-"]
        self.assertEqual((geral["suites"], geral["suites_falhas"], geral["voltas"]), (1, 1, 0))  # suíte reprovada não é volta

    def test_espera_do_dono_vai_do_pedido_a_decisao_e_inclui_a_pergunta_registrada(self):
        self.assertEqual(self.itens["E1"]["espera_dono_min"], 25.0)  # 12:10 até a hora entre parênteses (12:35)
        self.assertEqual(self.itens["-"]["espera_dono_min"], 20.0)  # PERGUNTA 14:00 até DECISÃO 14:20

    def test_reprovacoes_por_classe_e_merito_declarado_so_do_pedido(self):
        pedido = self.dados["pedidos"][0]
        self.assertEqual(pedido["pedido"], "versao-900")
        self.assertEqual(pedido["reprovacoes_por_classe"], {"escopo": 2, "forma": 1})
        self.assertEqual(pedido["merito_declarado"], {"n": 1, "parcial": 1, "s": 1})
        self.assertIn("declarada", self.dados["fontes"]["merito"])

    def test_periodo_por_dia_e_por_semana(self):
        dias = {p["periodo"]: p for p in self.dados["periodos"]}
        self.assertEqual(sorted(dias), ["2026-11-02", "2026-11-03"])
        self.assertEqual(dias["2026-11-02"]["itens_prontos"], 2)
        self.assertEqual(dias["2026-11-03"]["reprovacoes_por_classe"], {"forma": 1})
        rc, saida, _ = rodar(*self.args, "--json", "--por", "semana")
        self.assertEqual(rc, 0)
        self.assertEqual([p["periodo"] for p in json.loads(saida)["periodos"]], ["2026-S45"])

    def test_janela_de_datas_corta_eventos_e_registro(self):
        rc, saida, _ = rodar(*self.args, "--json", "--desde", "2026-11-03")
        dados = json.loads(saida)
        self.assertEqual(rc, 0)
        self.assertEqual([i["item"] for i in dados["itens"]], ["-"])
        self.assertEqual(dados["pedidos"][0]["reprovacoes_por_classe"], {"forma": 1})

    def test_saida_em_texto_tem_item_pedido_periodo_e_fontes(self):
        rc, saida, _ = rodar(*self.args)
        self.assertEqual(rc, 0)
        linhas = saida.splitlines()
        self.assertTrue(any(l.startswith("metricas: item versao-900 E1 pronto=2026-11-02T10:30-03:00 develop_h=23.5 main_h=47.5")
                            for l in linhas), saida)
        self.assertTrue(any(l.startswith("metricas: item versao-900 E2 ") and "develop_h=aberto" in l for l in linhas))
        self.assertTrue(any(l.startswith("metricas: pedido versao-900 ") and "merito(declarada)=n=1,parcial=1,s=1" in l for l in linhas))
        self.assertTrue(linhas[-1].startswith("metricas: fontes: "))

    def test_ref_ausente_avisa_e_nao_mede(self):
        rc, saida, erro = rodar("--raiz", str(self.tmp), "metricas", "--pedido", "versao-900", "--fuso=-03:00", "--json",
                                "--develop", "origin/develop", "--main", "main")
        self.assertEqual(rc, 0)
        self.assertIn("ref origin/develop ausente", erro)
        self.assertIsNone({i["item"]: i for i in json.loads(saida)["itens"]}["E1"]["pronto_ate_develop_h"])

    def test_pedido_invalido_ou_ausente_so_avisa(self):
        for nome in ("../fora", "nao-existe"):
            with self.subTest(nome=nome):
                rc, saida, erro = rodar("--raiz", str(self.tmp), "metricas", "--pedido", nome, "--json")
                self.assertEqual(rc, 0)
                self.assertIn("ausente, fora de docs/pedidos/", erro)
                self.assertEqual(json.loads(saida)["itens"], [])

    def test_data_invalida_sai_com_2(self):
        self.assertEqual(rodar("--raiz", str(self.tmp), "metricas", "--desde", "ontem")[0], 2)

    def test_ci_pelo_gh_so_com_a_opcao(self):
        pasta = self.tmp / "gh-falso"
        pasta.mkdir(exist_ok=True)
        gh = pasta / "gh"
        gh.write_text("#!/bin/sh\necho '[{\"conclusion\":\"success\"},{\"conclusion\":\"failure\"},{\"conclusion\":\"\"}]'\n",
                      encoding="utf-8")
        gh.chmod(0o755)
        env = sem_manutencao()
        env["PATH"] = f"{pasta}{os.pathsep}{env.get('PATH', '')}"
        r = subprocess.run([sys.executable, FORGE_CHECK, *self.args, "--json", "--gh"], capture_output=True, text=True, env=env)
        itens = {i["item"]: i for i in json.loads(r.stdout)["itens"]}
        self.assertEqual(itens["E1"]["ci"], {"execucoes": 2, "falhas": 1})
        self.assertNotIn("ci", self.itens["E1"])


class LeadEColunas(unittest.TestCase):
    """0.45.3: lead time do item até a develop e a main com a fatia do autor, dos portões e da espera do dono, e os minutos por
    coluna do quadro (card voltas-tempo-colunas). Cada teste roda o forge-check e confere o rc antes de ler a saída."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="forge-lead-"))
        cls.repo = Repositorio(cls.tmp)
        (cls.tmp / "docs" / "pedidos").mkdir(parents=True)
        (cls.tmp / "docs" / "kanban").mkdir(parents=True)
        (cls.tmp / "docs" / "pedidos" / "versao-900.md").write_text(PEDIDO.format(e1=cls.repo.e1, e2=cls.repo.e2[:9]), encoding="utf-8")
        (cls.tmp / "docs" / "pedidos" / "versao-901.md").write_text("# p\n\n## Histórico\n- 2026-11-02 10:00: (E9) aberto\n",
                                                                    encoding="utf-8")
        (cls.tmp / "docs" / "kanban" / "historico.md").write_text(HISTORICO_DO_QUADRO, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def medir(self, *extra, raiz=None, pedido="versao-900", como_json=True):
        rc, saida, erro = rodar("--raiz", str(raiz or self.tmp), "metricas", "--pedido", pedido, "--fuso=-03:00", "--agora",
                                "2026-11-02T15:00", "--develop", "develop", "--main", "main", *extra, *(["--json"] if como_json else []))
        self.assertEqual(rc, 0, erro)
        return (json.loads(saida) if como_json else saida), erro

    def test_lead_time_ate_a_develop_e_a_main_com_a_fatia_do_autor_dos_portoes_e_do_dono(self):
        dados, _ = self.medir()
        itens = {i["item"]: i for i in dados["itens"]}
        e1 = itens["E1"]  # início 02/11 09:00, entrega conferida 10:30, dono 12:10-12:35, develop 03/11 10:00, main 04/11 10:00
        self.assertEqual((e1["inicio"], e1["lead_develop_h"], e1["lead_main_h"]), ("2026-11-02T09:00-03:00", 25.0, 49.0))
        self.assertEqual(e1["fatias_develop"], {"autor_min": 90.0, "portoes_min": 1385.0, "dono_min": 25.0,
                                                "autor_pct": 6.0, "portoes_pct": 92.3, "dono_pct": 1.7})
        self.assertEqual(e1["fatias_main"], {"autor_min": 90.0, "portoes_min": 2825.0, "dono_min": 25.0,
                                             "autor_pct": 3.1, "portoes_pct": 96.1, "dono_pct": 0.9})
        e2 = itens["E2"]
        self.assertEqual((e2["lead_develop_h"], e2["fatias_develop"], e2["fatias_main"]), (None, None, None))
        pedido = dados["pedidos"][0]
        self.assertEqual(pedido["lead_develop_h_p50"], 25.0)
        self.assertEqual(pedido["fatias_develop"], e1["fatias_develop"])
        texto, _ = self.medir(como_json=False)
        self.assertIn("lead_develop_h=25 lead_main_h=49 fatias_develop=autor=6%,portoes=92.3%,dono=1.7%", texto)
        self.assertRegex(texto, r"item versao-900 E2 .* fatias_develop=- fatias_main=- ")

    def test_pedido_sem_lead_sai_nao_medido(self):
        dados, _ = self.medir(pedido="versao-901")
        self.assertEqual((dados["pedidos"][0]["lead_develop_h_p50"], dados["pedidos"][0]["fatias_develop"]), (None, None))

    def test_fatias_somam_itens_e_a_chegada_antes_da_entrega_nao_se_mede(self):
        h = lambda hh: datetime.datetime(2026, 11, 2, hh, tzinfo=FUSO)  # noqa: E731
        try:
            self.assertIsNone(G.fatias(h(9), h(12), h(11), []))
            self.assertIsNone(G.fatias(h(9), None, h(11), []))
            self.assertEqual(G.fatias(h(9), h(10), h(10), [(h(8), h(9) + datetime.timedelta(minutes=30))])["dono_min"], 30.0)
            soma = G.somar_fatias([G.fatias(h(9), h(10), h(12), []), None, G.fatias(h(10), h(13), h(14), [])])
            self.assertEqual((soma["autor_min"], soma["portoes_min"], soma["autor_pct"]), (240.0, 180.0, 57.1))
            self.assertIsNone(G.somar_fatias([None]))
            zero = G.fatias(h(9), h(9), h(9), [])
            self.assertEqual((zero["autor_pct"], G.somar_fatias([zero])["autor_pct"]), (None, None))
        except Exception as erro:  # noqa: BLE001 - a conta que quebra é falha da medida, não erro do teste
            self.fail(f"a conta das fatias quebrou: {type(erro).__name__}: {erro}")

    def test_minutos_por_coluna_do_quadro(self):
        dados, _ = self.medir()
        self.assertEqual(dados["colunas"], {"Code review": {"minutos": 30.0, "cartoes": 1, "abertos": 0},
                                            "Fazendo": {"minutos": 300.0, "cartoes": 2, "abertos": 1}})
        texto, _ = self.medir(como_json=False)
        self.assertIn("metricas: coluna Fazendo minutos=300 cartoes=2 abertos=1", texto)
        self.assertEqual(self.medir("--desde", "2026-11-03")[0]["colunas"], {})

    def test_sem_historico_do_quadro_colunas_sai_vazio_e_link_avisa(self):
        tmp = Path(tempfile.mkdtemp(prefix="forge-colunas-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "docs" / "kanban").mkdir(parents=True)
        dados, erro = self.medir(raiz=tmp)
        self.assertEqual(dados["colunas"], None)
        self.assertNotIn("aviso: None", erro)
        self.assertNotIn("metricas: coluna", self.medir(raiz=tmp, como_json=False)[0])
        (tmp / "docs" / "kanban" / "historico.md").symlink_to(self.tmp / "docs" / "kanban" / "historico.md")
        dados, erro = self.medir(raiz=tmp)
        self.assertEqual(dados["colunas"], None)
        self.assertIn("historico.md ilegível, link simbólico", erro)


class DuracaoDoPrePush(unittest.TestCase):
    """F8 (0.43.3): o `metricas --log-prepush` lê as linhas `pre-push: duracao ...` que o .githooks/pre-push grava no log do envio."""
    LOG = ("12:00:01 pre-push: entrou 12:00:01\n"
           "pre-push: duracao inicio=2026-11-08T12:00:00Z fim=2026-11-08T12:05:00Z plano=dirigida rc=0\n"
           "[err] 2026-11-08 12:10 pre-push: duracao inicio=2026-11-08T12:10:00Z fim=2026-11-08T12:11:40Z plano=dirigida rc=1\n"
           "pre-push: duracao inicio=2026-11-08T13:00:00Z fim=2026-11-08T13:00:20Z plano=baratas rc=1\n"
           "pre-push: duracao inicio=2026-11-09T09:00:00Z fim=2026-11-09T09:30:00Z plano=completa rc=0\n"
           "pre-push: duracao inicio=2026-11-08T14:00:00Z fim=2026-11-08T13:00:00Z plano=dirigida rc=0\n"  # fim antes do início
           "pre-push: duracao inicio=2026-11-08T15:00:00Z fim=2026-11-08T15:01:00Z plano=dirigida rc=0 lixo\n"
           "eco: pre-push: duracao inicio=x fim=y plano=dirigida rc=0\n")

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-f8-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "envio.log").write_text(self.LOG, encoding="utf-8")

    def test_por_plano_conta_envios_falhas_p50_e_maximo(self):
        dados, avisos = G.duracoes_do_prepush([self.tmp / "envio.log"])
        self.assertEqual(avisos, [])
        self.assertEqual(dados, {"baratas": {"envios": 1, "falhas": 1, "p50_s": 20.0, "max_s": 20.0},
                                 "completa": {"envios": 1, "falhas": 0, "p50_s": 1800.0, "max_s": 1800.0},
                                 "dirigida": {"envios": 2, "falhas": 1, "p50_s": 200.0, "max_s": 300.0}})

    def test_janela_de_datas_e_log_ausente(self):
        dados, avisos = G.duracoes_do_prepush([self.tmp / "envio.log", self.tmp / "nao-existe.log"],
                                              desde=datetime.date(2026, 11, 9))
        self.assertEqual(list(dados), ["completa"])
        self.assertEqual(len(avisos), 1)
        self.assertIn("nao-existe.log", avisos[0])

    def test_linha_de_comando_em_texto_e_em_json(self):
        args = ("--raiz", str(self.tmp), "metricas", "--pedido", "x", "--log-prepush", str(self.tmp / "envio.log"))
        rc, saida, _ = rodar(*args)
        self.assertEqual(rc, 0)
        self.assertIn("metricas: prepush plano=dirigida envios=2 falhas=1 p50_s=200 max_s=300", saida.splitlines())
        self.assertIn("prepush=medida", saida.splitlines()[-1])
        rc, saida, _ = rodar(*args, "--json")
        self.assertEqual(json.loads(saida)["prepush"]["baratas"]["falhas"], 1)

    def test_sem_a_opcao_a_saida_nao_muda(self):
        rc, saida, _ = rodar("--raiz", str(self.tmp), "metricas", "--pedido", "x", "--json")
        self.assertEqual(rc, 0)
        self.assertNotIn("prepush", json.loads(saida))

    def test_a_linha_que_o_pre_push_grava_e_a_que_o_metricas_le(self):
        hook = (RAIZ / ".githooks" / "pre-push").read_text(encoding="utf-8")
        modelo = 'echo "pre-push: duracao inicio=${inicio_prepush} fim=$(date -u +%Y-%m-%dT%H:%M:%SZ) plano=$1 rc=$2" >&2'
        self.assertIn(modelo, hook)
        exemplo = "pre-push: duracao inicio=2026-11-08T12:00:00Z fim=2026-11-08T12:00:09Z plano=nada rc=0"
        self.assertTrue(G.LINHA_DE_DURACAO.search(exemplo))


class Funcoes(unittest.TestCase):
    def test_item_da_linha(self):
        casos = {"(E3-1a, E3-1d) volta 2": "E3-1a", "(E2.2 g1) brief": "E2.2", "entrega conferida abc1234 (E4-1 MAQ, x)": "E4-1",
                 "(pareceres da 0.43) review": None, "push único reprovou": None}
        for texto, item in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(G.item_da_linha(texto), item)

    def test_classe_de_suite(self):
        casos = {"push passou (rc 0)": "passou", "push reprovou": "falhou", "suite falhou": "falhou", "push: 10:11 a 10:34": None,
                 "review reprovado": None}
        for texto, classe in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(G.classe_de_suite(G.sem_acento(texto)), classe)

    def test_uniao_nao_conta_sobreposicao(self):
        h = lambda m: datetime.datetime(2026, 11, 2, 10, 0, tzinfo=FUSO) + datetime.timedelta(minutes=m)  # noqa: E731
        self.assertEqual(G.uniao_em_minutos([(h(0), h(30)), (h(20), h(40)), (h(60), h(70))]), 50.0)

    def test_pergunta_sem_resposta_nao_conta(self):
        texto = "## Histórico\n- 2026-11-02 10:00: (E1) vai ao dono a base.\n"
        eventos = G.eventos_do_pedido(texto, FUSO)
        self.assertEqual(G.esperas_do_dono(eventos, texto, FUSO), {})


class EsperaPorPortaoETokens(unittest.TestCase):
    """0.43.3: a espera por portão sai do recusas.log do R-TETO (RN-6) e os tokens por item, dos transcritos dos subagentes (CUSTO)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-metricas-custo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def test_recusas_do_mesmo_portao_proximas_sao_uma_espera(self):
        log = self.gravar("recusas.log", "2026-11-02T10:00:00 agentes R-TETO mem_gb=1.00 nproc=4 ativos=3 motivo=memoria\n"
                                         "2026-11-02T10:08:00 agentes R-TETO mem_gb=1.00 nproc=4 ativos=3 motivo=memoria\n"
                                         "2026-11-02T10:30:00 agentes R-TETO mem_gb=1.00 nproc=4 ativos=3 motivo=memoria\n"
                                         "2026-11-02T11:00:00 agentes R-TETO mem_gb=- nproc=- ativos=2 motivo=duplicado\n"
                                         "linha fora da forma motivo=teto\n"
                                         "2026-11-05T09:00:00 agentes R-TETO mem_gb=8.00 nproc=4 ativos=4 motivo=teto\n")
        janela = lambda q: q.date() <= datetime.date(2026, 11, 3)  # noqa: E731
        self.assertEqual(G.esperas_por_portao([log], janela),
                         {"duplicado": {"recusas": 1, "espera_min": 0.0}, "memoria": {"recusas": 3, "espera_min": 8.0}})

    def test_saida_em_texto_tem_o_portao_e_o_tracinho_sem_fonte(self):
        (self.tmp / "docs" / "pedidos").mkdir(parents=True)
        dados, _ = G.calcular(self.tmp, self.tmp, recusas=[self.gravar(
            "r.log", "2026-11-02T10:00:00 agentes R-TETO mem_gb=8.00 nproc=4 ativos=4 motivo=teto\n")])
        self.assertIn("metricas: portao teto recusas=1 espera_min=0", G.linhas_de_texto(dados))
        dados, _ = G.calcular(self.tmp, self.tmp, recusas=[], transcritos=[self.tmp / "nada"])
        self.assertEqual(dados["espera_por_portao"], None)
        self.assertTrue(any(l.startswith("metricas: portao - ") for l in G.linhas_de_texto(dados)))

    def transcrito(self, nome, prompt, usos):
        linhas = [json.dumps({"type": "user", "message": {"role": "user", "content": prompt}})]
        for i, (entrada, saida) in enumerate(usos):
            uso = {"input_tokens": entrada, "output_tokens": saida, "cache_read_input_tokens": 1, "cache_creation_input_tokens": 0}
            for _ in range(2):  # o mesmo id em dois pedaços de uma resposta conta uma vez
                linhas.append(json.dumps({"type": "assistant", "message": {"id": f"m{i}", "usage": uso}}))
        self.gravar(f"transcritos/sessao/subagents/{nome}.jsonl", "\n".join(linhas + ["{quebrado"]) + "\n")

    def test_tokens_por_item_pelo_brief_citado_e_rateio(self):
        self.gravar("docs/briefs/p9-tech-lead-1.md", "Pedido: p9\nEtapa: codigo   Cobre: E1\n\n## Entregar\n- x (E2).\n")
        self.gravar("docs/briefs/p9-qa-engineer-1.md", "Agente destino: forge:qa-engineer\n\n## Entregar\n- y.\n")
        self.transcrito("agent-a", "Brief: docs/briefs/p9-tech-lead-1.md sha", [(10, 89), (0, 0)])
        self.transcrito("agent-b", [{"type": "text", "text": "leia docs/briefs/p9-qa-engineer-1.md"}], [(4, 5)])
        self.transcrito("agent-c", "sem brief", [(1000, 1000)])
        custos = G.tokens_por_item([self.tmp / "transcritos"], self.tmp)
        self.assertEqual(custos, {("p9", "E1"): {"tokens": 50, "agentes": 1}, ("p9", "E2"): {"tokens": 50, "agentes": 1},
                                  ("p9", "-"): {"tokens": 10, "agentes": 1}})

    def test_transcritos_acima_dos_tetos_ficam_fora_com_aviso(self):  # B2 do review da 0.43.3
        self.gravar("docs/briefs/p9-tech-lead-1.md", "Pedido: p9\nCobre: E1\n")
        for nome in ("agent-a", "agent-b", "agent-c"):
            self.transcrito(nome, "docs/briefs/p9-tech-lead-1.md", [(5, 5)])
        avisos = []
        with mock.patch.object(G, "TETO_DE_TRANSCRITOS", 2):
            custos = G.tokens_por_item([self.tmp / "transcritos"], self.tmp, avisos)
        self.assertEqual(custos, {("p9", "E1"): {"tokens": 22, "agentes": 2}})  # 5 + 5 + 1 de cache por agente
        self.assertIn("1 transcritos mais antigos", avisos[0])
        avisos = []
        grande = self.tmp / "transcritos" / "sessao" / "subagents" / "agent-a.jsonl"
        with mock.patch.object(G, "TETO_DO_TRANSCRITO", grande.stat().st_size - 1):
            custos = G.tokens_por_item([self.tmp / "transcritos"], self.tmp, avisos)
        self.assertEqual(custos, {})
        self.assertEqual(len(avisos), 3)
        self.assertIn("agent-a.jsonl passa de", avisos[0])

    def test_item_do_historico_ganha_a_coluna_e_sem_fonte_sai_tracinho(self):
        self.gravar("docs/pedidos/p9.md", "# p9\n\n## Histórico\n- 2026-11-02 10:00: (E1) aberto\n- 2026-11-02 10:05: (E3) aberto\n")
        self.gravar("docs/briefs/p9-tech-lead-1.md", "Pedido: p9\nCobre: E1\n")
        self.transcrito("agent-a", "docs/briefs/p9-tech-lead-1.md", [(20, 19)])
        dados, _ = G.calcular(self.tmp, self.tmp, ["p9"], fuso=FUSO, transcritos=[self.tmp / "transcritos"], recusas=[])
        self.assertEqual({i["item"]: i["tokens"] for i in dados["itens"]}, {"E1": 40, "E3": None})
        self.assertEqual(dados["pedidos"][0]["tokens"], 40)
        texto = G.linhas_de_texto(dados)
        self.assertTrue(any(" E1 " in l and l.endswith("tokens=40") for l in texto), texto)
        self.assertTrue(any(" E3 " in l and l.endswith("tokens=-") for l in texto), texto)

    def test_opcao_transcritos_da_linha_de_comando_chega_ao_calculo(self):  # 0.43.3: --transcritos no forge-check metricas
        self.gravar("docs/pedidos/p9.md", "# p9\n\n## Histórico\n- 2026-11-02 10:00: (E1) aberto\n")
        self.gravar("docs/briefs/p9-tech-lead-1.md", "Pedido: p9\nCobre: E1\n")
        self.transcrito("agent-a", "docs/briefs/p9-tech-lead-1.md", [(20, 19)])
        cod, saida, erro = rodar("--raiz", str(self.tmp), "metricas", "--pedido", "p9", "--json", "--transcritos", str(self.tmp / "transcritos"))
        self.assertEqual(cod, 0, saida + erro)
        self.assertEqual(json.loads(saida)["pedidos"][0]["tokens"], 40)
        _, saida, _ = rodar("--raiz", str(self.tmp), "metricas", "--pedido", "p9", "--json", "--transcritos", str(self.tmp / "vazia"))
        self.assertEqual(json.loads(saida)["pedidos"][0]["tokens"], None)


REGRA_OK = "# R-A\n\nTexto.\n\n- **Revisar em:** 2027-01-10\n- **Medida:** 36 % das reprovações (609 de 1742)\n"


class OrcamentoDeTokens(unittest.TestCase):
    """X2 (0.44.1): `Tokens previstos:` e `Versão:` no pedido; o `metricas` soma o previsto e o gasto por versão e alerta quando o
    gasto passa do previsto (só leitura, rc 0)."""

    setUp, gravar, transcrito = EsperaPorPortaoETokens.setUp, EsperaPorPortaoETokens.gravar, EsperaPorPortaoETokens.transcrito

    def pedido(self, nome, previsto, versao="0.44.1", tokens=(20, 19)):
        self.gravar(f"docs/pedidos/{nome}.md", f"# {nome}\nVersão: {versao}\nTokens previstos: {previsto}\n\n## Histórico\n"
                    "- 2026-11-02 10:00: (E1) aberto\n")
        self.gravar(f"docs/briefs/{nome}-tech-lead-1.md", f"Pedido: {nome}\nCobre: E1\n")
        self.transcrito(f"agent-{nome}", f"docs/briefs/{nome}-tech-lead-1.md", [tokens])

    def calcular(self, *nomes):
        dados, _ = G.calcular(self.tmp, self.tmp, list(nomes), fuso=FUSO, transcritos=[self.tmp / "transcritos"], recusas=[])
        return dados

    def test_previsto_do_pedido(self):
        for texto, esperado in (("Tokens previstos: 2.000.000", 2_000_000), ("- **Tokens previstos:** 500k", 500_000),
                                ("Tokens previstos: 3M", 3_000_000), ("tokens previstos: 1_200", 1200), ("sem linha", None)):
            with self.subTest(texto):
                self.assertEqual(G.previsto_do_pedido(texto), esperado)

    def test_alerta_quando_o_gasto_passa_do_previsto_por_pedido_e_por_versao(self):
        self.pedido("p9", 30)
        self.pedido("p8", 100)
        dados = self.calcular("p8", "p9")
        self.assertEqual(dados["orcamento"]["versoes"], {"0.44.1": {"previsto": 130, "gasto": 80}})
        self.assertEqual(dados["orcamento"]["alertas"], ["pedido p9: gasto 40 tokens passa do previsto 30 (+33%)"])
        texto = G.linhas_de_texto(dados)
        self.assertIn("metricas: orcamento versao 0.44.1 previsto=130 gasto=80", texto)
        self.assertIn("metricas: alerta: pedido p9: gasto 40 tokens passa do previsto 30 (+33%)", texto)
        self.pedido("p8", 10)
        alertas = self.calcular("p8", "p9")["orcamento"]["alertas"]
        self.assertIn("versão 0.44.1: gasto 80 tokens passa do previsto 40 (+100%)", alertas)

    def test_dentro_do_previsto_ou_sem_previsto_nao_alerta(self):
        self.pedido("p9", 40)
        self.gravar("docs/pedidos/p7.md", "# p7\n\n## Histórico\n- 2026-11-02 10:00: (E1) aberto\n")
        dados = self.calcular("p7", "p9")
        self.assertEqual(dados["orcamento"], {"versoes": {"0.44.1": {"previsto": 40, "gasto": 40}}, "alertas": []})
        self.assertEqual([p.get("tokens_previstos") for p in dados["pedidos"]], [None, 40])
        self.assertFalse(any("alerta" in l for l in G.linhas_de_texto(dados)))

    def test_pedido_sem_versao_e_sem_medida_conta_gasto_zero_na_versao_tracinho(self):
        self.pedido("p9", 40)
        self.gravar("docs/pedidos/p6.md", "# p6\nTokens previstos: 5\n\n## Histórico\n- 2026-11-02 10:00: (E1) aberto\n")
        dados = self.calcular("p6", "p9")
        self.assertEqual(dados["orcamento"]["versoes"]["-"], {"previsto": 5, "gasto": 0})
        self.assertEqual(dados["orcamento"]["alertas"], [])


class Regras(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-regras-"))
        self.pasta = self.tmp / "docs" / "regras"
        self.pasta.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def escrever(self, **regras):
        for nome, texto in regras.items():
            (self.pasta / f"{nome.replace('_', '-')}.md").write_text(texto, encoding="utf-8")

    def rodar(self, *extra):
        return rodar("--raiz", str(self.tmp), "regras", "--hoje", "2026-11-08", *extra)

    def test_todas_em_dia_rc_0_tambem_estrito(self):
        self.escrever(R_A=REGRA_OK, R_B="# R-B\nRevisar em: 2026-11-20\nMedida: 3 escapes em 30 dias\n")
        for extra in ((), ("--estrito",)):
            rc, saida, _ = self.rodar(*extra)
            self.assertEqual(rc, 0, saida)
        self.assertIn("regras: R-A estado=ok revisar_em=2027-01-10 medida=sim", saida)
        self.assertIn("regras: R-B estado=a-vencer", saida)  # até 14 dias: sem aviso
        self.assertIn("regras: 2 regras, 2 em dia, 0 com aviso", saida)

    def test_falta_vencida_e_medida_sem_numero_avisam_rc_0(self):
        self.escrever(R_A=REGRA_OK, R_C="# R-C\nsó texto\n", R_D="# R-D\nRevisar em: 2026-11-01\nMedida: 12 voltas\n",
                      R_E="# R-E\nRevisar em: 2027-01-01\nMedida: muitas\n", R_F="# R-F\nRevisar em: 2027-02-30\nMedida: 1\n")
        rc, saida, _ = self.rodar()
        self.assertEqual(rc, 0)
        self.assertIn("R-C estado=aviso revisar_em=- medida=nao aviso: sem 'Revisar em: AAAA-MM-DD'; sem 'Medida:'", saida)
        self.assertIn("R-D estado=aviso revisar_em=2026-11-01 medida=sim aviso: vencida em 2026-11-01", saida)
        self.assertIn("R-E estado=aviso", saida)
        self.assertIn("'Medida:' sem número", saida)
        self.assertIn("'Revisar em' com data inválida", saida)
        self.assertIn("regras: 5 regras, 1 em dia, 4 com aviso", saida)

    def test_estrito_reprova_com_aviso(self):
        self.escrever(R_A=REGRA_OK, R_C="# R-C\n")
        rc, saida, _ = self.rodar("--estrito")
        self.assertEqual(rc, 1)
        self.assertIn("(--estrito: reprova)", saida)

    def test_json(self):
        self.escrever(R_A=REGRA_OK)
        rc, saida, _ = self.rodar("--json")
        dados = json.loads(saida)
        self.assertEqual((rc, dados["avisos"], dados["regras"][0]["medida"]), (0, 0, "36 % das reprovações (609 de 1742)"))

    def test_link_simbolico_nao_e_lido(self):
        alvo = self.tmp / "fora.md"
        alvo.write_text(REGRA_OK, encoding="utf-8")
        (self.pasta / "R-L.md").symlink_to(alvo)
        rc, saida, _ = self.rodar()
        self.assertIn("R-L estado=aviso", saida)
        self.assertIn("link simbólico", saida)

    def test_sem_regras_rc_2_e_hoje_invalido_rc_2(self):
        self.assertEqual(self.rodar()[0], 2)
        self.escrever(R_A=REGRA_OK)
        self.assertEqual(rodar("--raiz", str(self.tmp), "regras", "--hoje", "amanha")[0], 2)

    def test_copia_avulsa_do_forge_check_segue_e_so_os_dois_saem_com_2(self):
        (self.tmp / "bin").mkdir()
        shutil.copy(FORGE_CHECK, self.tmp / "bin" / "forge-check")  # sem o módulo ao lado, como nos testes que copiam só o script
        self.escrever(R_A=REGRA_OK)
        r = subprocess.run([sys.executable, str(self.tmp / "bin" / "forge-check"), "--raiz", str(self.tmp), "regras"],
                           capture_output=True, text=True, env=sem_manutencao())
        self.assertEqual((r.returncode, r.stdout.strip()), (2, "regras: bin/forge_governanca.py ausente ao lado do forge-check; nada medido"))
        r = subprocess.run([sys.executable, str(self.tmp / "bin" / "forge-check"), "--raiz", str(self.tmp), "regras", "--help"],
                           capture_output=True, text=True, env=sem_manutencao())
        self.assertEqual(r.returncode, 0)

    def test_regras_do_forge_sao_lidas_sem_erro(self):
        rc, saida, _ = rodar("--raiz", str(RAIZ), "regras")
        self.assertEqual(rc, 0)
        self.assertRegex(saida.splitlines()[-1], r"^regras: \d+ regras, \d+ em dia, \d+ com aviso")


def changelog(*versoes):
    """CHANGELOG.md com as versões (número, data), da mais nova à mais antiga."""
    return "# Changelog\n\n## [Não publicado]\n\n" + "".join(f"## [{v}] - {d}\n### Corrigido\n- x\n\n" for v, d in versoes)


SEIS = [("0.6.0", "2026-11-06"), ("0.5.0", "2026-11-05"), ("0.4.0", "2026-11-04"), ("0.3.0", "2026-11-03"),
        ("0.2.0", "2026-11-02"), ("0.1.0", "2026-11-01")]


class AvaliacaoDeFora(unittest.TestCase):
    """0.45.3: `forge-check avaliacao --pendente` diz se passaram 5 versões do CHANGELOG.md desde a última docs/avaliacoes/*.md;
    só avisa (rc 0 nos dois casos)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-avaliacao-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "docs" / "avaliacoes").mkdir(parents=True)

    def avaliacao(self, *versoes):
        (self.tmp / "CHANGELOG.md").write_text(changelog(*versoes), encoding="utf-8")
        return rodar("--raiz", str(self.tmp), "avaliacao", "--pendente")

    def test_sem_avaliacao_cinco_versoes_avisam_e_quatro_nao(self):
        rc, saida, _ = self.avaliacao(*SEIS[:5])
        self.assertEqual(rc, 0)
        self.assertIn("avaliação de fora pendente: 5 versões desde o início", saida)
        rc, saida, _ = self.avaliacao(*SEIS[:4])
        self.assertEqual(rc, 0, "só avisa, nunca barra")
        self.assertIn("em dia: 4 de 5", saida)
        self.assertNotIn("pendente", saida)

    def test_conta_so_as_versoes_depois_da_versao_da_ultima_avaliacao(self):
        (self.tmp / "docs" / "avaliacoes" / "2026-10-01.md").write_text("versao: 0.1.0\n", encoding="utf-8")
        (self.tmp / "docs" / "avaliacoes" / "2026-11-02.md").write_text("versao: 0.2.0\n", encoding="utf-8")
        rc, saida, _ = self.avaliacao(*SEIS)
        self.assertEqual(rc, 0)
        self.assertIn("em dia: 4 de 5 versões desde docs/avaliacoes/2026-11-02.md", saida)
        (self.tmp / "docs" / "avaliacoes" / "2026-11-02.md").write_text("versao: 0.1.0\n", encoding="utf-8")
        self.assertIn("pendente: 5 versões", self.avaliacao(*SEIS)[1])

    def test_sem_linha_versao_vale_a_data_do_nome(self):
        (self.tmp / "docs" / "avaliacoes" / "2026-11-01-forge.md").write_text("# avaliação\n", encoding="utf-8")
        self.assertIn("pendente: 5 versões", self.avaliacao(*SEIS)[1])  # depois de 01/11: 0.2.0 a 0.6.0
        (self.tmp / "docs" / "avaliacoes" / "2026-11-02.md").write_text("# avaliação\n", encoding="utf-8")
        self.assertIn("em dia: 4 de 5", self.avaliacao(*SEIS)[1])
        (self.tmp / "docs" / "avaliacoes" / "notas.md").write_text("versao: 0.6.0\n", encoding="utf-8")
        self.assertIn("em dia: 4 de 5", self.avaliacao(*SEIS)[1], "arquivo fora de <AAAA-MM-DD>*.md não conta")

    def test_versao_fora_do_changelog_ou_avaliacao_ilegivel_cai_na_data_do_nome(self):
        (self.tmp / "docs" / "avaliacoes" / "2026-11-01.md").write_text("versao: 9.9.9\n", encoding="utf-8")
        self.assertIn("pendente: 5 versões desde docs/avaliacoes/2026-11-01.md", self.avaliacao(*SEIS)[1])
        fora = self.tmp / "fora.md"
        fora.write_text("versao: 0.5.0\n", encoding="utf-8")
        (self.tmp / "docs" / "avaliacoes" / "2026-11-02.md").symlink_to(fora)  # link não é lido: vale a data
        self.assertIn("em dia: 4 de 5 versões desde docs/avaliacoes/2026-11-02.md", self.avaliacao(*SEIS)[1])

    def test_sem_changelog_nada_medido(self):
        rc, saida, _ = rodar("--raiz", str(self.tmp), "avaliacao", "--pendente")
        self.assertEqual(rc, 2)
        self.assertIn("nada medido", saida)


if __name__ == "__main__":
    unittest.main()
