"""CI-RAPIDO (v047), R-QA: testes diretos das guardas de `scripts/pesos-do-ci.py` e de `scripts/suite-partes.py` que os
mutantes de `tests/mutantes/v047-ci-rapido-*.json` precisam matar (a volta da catraca do PR: uma guarda, um mutante que morre).
Classe do defeito: guarda trocada por `True`/`False` ou apagada e a suíte continuar verde."""
import collections
import io
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_pesos_do_ci import CONHECIDAS, REPO, SCRIPT as PESOS_SCRIPT, FalsaApi, api_completa, carregar as carregar_pesos  # noqa: E402
from test_pesos_do_ci import execucao, job, nota  # noqa: E402
from test_suite_partes import carregar as carregar_partes  # noqa: E402


class CampoEExecucao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar_pesos()

    def test_campo_so_desce_em_objeto_e_so_devolve_o_tipo_exato(self):
        self.assertEqual(self.p.campo({"a": {"b": 3}}, "a.b", int), 3)
        self.assertIsNone(self.p.campo({"a": 1}, "a.b", int))  # descer num inteiro não quebra
        self.assertIsNone(self.p.campo({"a": ["b"]}, "a.b", int))
        self.assertIsNone(self.p.campo({"a": True}, "a", int))  # bool não é int
        self.assertIsNone(self.p.campo({"a": 1}, "a", str))

    def test_execucao_valida_exige_id_inteiro_e_cada_campo(self):
        self.assertTrue(self.p.execucao_valida(execucao(), REPO))
        self.assertFalse(self.p.execucao_valida(execucao(id_="1"), REPO))
        self.assertFalse(self.p.execucao_valida(execucao(id_=True), REPO))
        self.assertFalse(self.p.execucao_valida({k: v for k, v in execucao().items() if k != "id"}, REPO))

    def test_perna_valida_cada_exigencia(self):
        self.assertEqual(self.p.perna_valida(job(5, "3.12", 1, 2)), ("3.12", 1, 2))
        self.assertIsNone(self.p.perna_valida({"id": 5, "conclusion": "success"}))  # sem nome
        self.assertIsNone(self.p.perna_valida(job(5, name="outro job")))
        self.assertIsNone(self.p.perna_valida(job(5, conclusion="failure")))
        self.assertIsNone(self.p.perna_valida(job(5, id=None)))
        self.assertIsNone(self.p.perna_valida(job(5, id="5")))
        self.assertIsNone(self.p.perna_valida(job(5, "3.12", 3, 2)))  # parte maior que o total
        self.assertEqual(self.p.perna_valida(job(5, "3.12", 2, 2)), ("3.12", 2, 2))

    def test_anotacao_de_titulo_alheio_ou_sem_mensagem_e_descartada(self):
        perna = ("3.12", 1, 2)
        ok = nota("1/2", "3.12", {"test_a": 1.0})
        self.assertEqual(self.p.ler_anotacao(ok, perna, CONHECIDAS), {"test_a": 1.0})
        self.assertIsNone(self.p.ler_anotacao({**ok, "title": "aviso"}, perna, CONHECIDAS))
        self.assertIsNone(self.p.ler_anotacao({**ok, "title": ""}, perna, CONHECIDAS))
        self.assertIsNone(self.p.ler_anotacao({**ok, "message": ""}, perna, CONHECIDAS))
        self.assertIsNone(self.p.ler_anotacao({"title": ok["title"]}, perna, CONHECIDAS))


class GerarEColetar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar_pesos()

    def test_gerar_usa_o_medido_depois_o_atual_e_ignora_o_que_nao_tem_nenhum(self):
        novos, sem = self.p.gerar({"a": 1.0, "b": 2.0}, {"a": 9.0, "c": 3.0}, {"a", "b", "c", "d"})
        self.assertEqual(novos, {"a": 9.0, "b": 2.0, "c": 3.0})  # `d` não tem peso nem medida
        self.assertEqual(sem, ["b"])

    def test_api_sem_lista_de_execucoes_ou_de_jobs_ou_de_anotacoes_nao_quebra(self):
        jobs, notas = api_completa()
        for errado in ({}, {"workflow_runs": "x"}, {"workflow_runs": None}):
            with self.subTest(errado):
                self.assertEqual(self.p.coletar(REPO, lambda _c, e=errado: e, CONHECIDAS)[0], {})

        def sem_jobs(caminho):
            return {"workflow_runs": [execucao()]} if "/workflows/" in caminho else {}

        self.assertEqual(self.p.coletar(REPO, sem_jobs, CONHECIDAS)[0], {})

        def sem_anotacoes(caminho):
            if "/check-runs/" in caminho:
                return None
            return FalsaApi([execucao()], jobs, notas)(caminho)

        self.assertEqual(self.p.coletar(REPO, sem_anotacoes, CONHECIDAS)[0], {})

    def test_perna_sem_anotacao_valida_deixa_o_conjunto_incompleto(self):
        jobs, notas = api_completa()
        notas[12] = [nota("2/2", "3.12", {"test_inventado": 1.0})]  # descartada inteira: a parte 2/2 do 3.12 fica sem tempo
        amostras = self.p.coletar(REPO, FalsaApi([execucao()], jobs, notas), CONHECIDAS)[0]
        self.assertEqual({py for py, _ in amostras}, {"3.14"})


class LeitorDaApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar_pesos()

    def pedido(self, env):
        visto = {}

        def abre(pedido, timeout):
            visto["cabecalhos"] = dict(pedido.header_items())
            visto["url"] = pedido.full_url
            raise OSError

        with unittest.mock.patch.object(self.p.urllib.request, "urlopen", abre):
            with self.assertRaises(OSError):
                self.p.leitor_da_api(env)("repos/x/y")
        return visto

    def test_sem_url_nem_token_usa_a_api_publica_e_nao_manda_autorizacao(self):
        visto = self.pedido({})
        self.assertEqual(visto["url"], "https://api.github.com/repos/x/y")
        self.assertNotIn("Authorization", visto["cabecalhos"])
        self.assertEqual(self.pedido({"GITHUB_API_URL": ""})["url"], "https://api.github.com/repos/x/y")


class PrincipalGuardas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = carregar_pesos()

    def roda(self, argv, env=None, api=None, conhecidas=CONHECIDAS, pesos=None):
        jobs, notas = api_completa()
        api = api or FalsaApi([execucao()], jobs, notas)
        with tempfile.TemporaryDirectory() as d, \
                unittest.mock.patch.object(self.p.sys, "stderr", new_callable=io.StringIO) as erro, \
                unittest.mock.patch.object(self.p.sys, "stdout", new_callable=io.StringIO) as saida:
            if pesos is not None:
                arquivo = Path(d) / "pesos.json"
                arquivo.write_text(pesos, encoding="utf-8")
                with unittest.mock.patch.object(self.p, "PESOS", arquivo):
                    codigo = self.p.main(argv, env, api, conhecidas)
            else:
                codigo = self.p.main(argv, env, api, conhecidas)
        return codigo, saida.getvalue(), erro.getvalue()

    def test_env_nao_informado_vem_do_ambiente_do_processo(self):
        with unittest.mock.patch.dict(self.p.os.environ, {"GITHUB_REPOSITORY": REPO}):
            codigo, saida, erro = self.roda([], None)
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(json.loads(saida), {"test_a": 12.0, "test_b": 5.0})

    def test_leitor_injetado_dispensa_o_da_api(self):
        with unittest.mock.patch.object(self.p, "leitor_da_api", side_effect=AssertionError("não devia ser chamado")):
            self.assertEqual(self.roda(["--repo", REPO], {})[0], 0)

    def test_conhecidas_injetadas_dispensam_o_plano_da_arvore(self):
        with unittest.mock.patch.object(self.p, "unidades_do_plano", side_effect=AssertionError("não devia ser chamado")):
            self.assertEqual(self.roda(["--repo", REPO], {})[0], 0)

    def test_peso_atual_que_nao_e_objeto_vale_vazio(self):
        conhecidas = CONHECIDAS | {"test_c"}
        codigo, saida, erro = self.roda(["--repo", REPO], {}, conhecidas=conhecidas, pesos='["test_c"]')
        self.assertEqual(codigo, 0, erro)
        self.assertEqual(json.loads(saida), {"test_a": 12.0, "test_b": 5.0})

    def test_aviso_de_sem_medida_so_com_unidade_sem_medida_e_abrevia_acima_de_dez(self):
        _, _, erro = self.roda(["--repo", REPO], {})
        self.assertNotIn("sem medida", erro)
        for quantas, reticencias in ((10, False), (11, True)):
            with self.subTest(quantas):
                extras = {f"test_x{i:02d}": 1.0 for i in range(quantas)}
                codigo, _, erro = self.roda(["--repo", REPO], {}, conhecidas=CONHECIDAS | set(extras), pesos=json.dumps(extras))
                self.assertEqual(codigo, 0, erro)
                self.assertIn(f"{quantas} unidade(s) sem medida", erro)
                self.assertEqual(" ..." in erro, reticencias, erro)

    def test_repo_ruim_ou_execucoes_fora_da_faixa_nao_chegam_a_ler_a_api(self):
        for args in (["--repo", "a/b;c"], ["--repo", REPO, "--execucoes", "0"], ["--repo", REPO, "--execucoes", "31"]):
            with self.subTest(args):
                api = unittest.mock.Mock()
                self.assertEqual(self.roda(args, {}, api=api)[0], 2)
                api.assert_not_called()
        self.assertEqual(self.roda(["--repo", REPO, "--execucoes", "30"], {})[0], 0)
        self.assertEqual(self.roda(["--repo", REPO, "--execucoes", "1"], {})[0], 0)

    def test_executado_como_script_sai_com_o_codigo_do_main(self):
        r = subprocess.run([sys.executable, "-I", str(PESOS_SCRIPT)], env={}, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("--repo fora do formato", r.stderr)


class GuardasDaDivisao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f = carregar_partes()
        cls.sp = cls.f.carregar_paralela()

    def test_id_sem_modulo_na_divisao_nao_tem_unidade_nem_vira_chave_nula(self):
        pesos = {"test_a": 1.0, "test_a.K": 2.0}
        self.assertIsNone(self.f.unidade_do_id(self.sp, "outro.Classe.teste", {"test_a"}, pesos))
        total = collections.Counter({"test_a.K.test_q": 1, "outro.Classe.teste": 1})
        por = self.f.esperado_por_unidade(self.sp, total, ["test_a"], pesos)
        self.assertEqual(set(por), {"test_a.K"})

    def test_o_cache_de_chaves_por_modulo_e_compartilhado_entre_ids(self):
        pesos = {"test_a.K": 2.0}
        with unittest.mock.patch.object(self.sp, "separadas", wraps=self.sp.separadas) as separadas:
            self.f.esperado_por_unidade(self.sp, collections.Counter({"test_a.K.test_q": 1, "test_a.T.test_p": 1}), ["test_a"], pesos)
        self.assertEqual(separadas.call_count, 1)
        cache = {}
        self.f.unidade_do_id(self.sp, "test_a.K.test_q", {"test_a"}, pesos, cache)
        self.assertEqual(cache, {"test_a": ["test_a.K"]})

    def test_modulo_sem_chave_separada_e_a_propria_unidade_e_com_chave_vai_pela_mais_longa(self):
        pesos = {"test_a.K": 2.0, "test_b": 1.0}
        self.assertEqual(self.f.unidade_do_id(self.sp, "test_b.T.test_y", {"test_a", "test_b"}, pesos), "test_b")
        self.assertEqual(self.f.unidade_do_id(self.sp, "test_a.K.test_q", {"test_a", "test_b"}, pesos), "test_a.K")
        self.assertEqual(self.f.unidade_do_id(self.sp, "test_a.T.test_p", {"test_a", "test_b"}, pesos), "test_a")

    def test_completude_usa_os_pesos_passados_e_nao_os_do_arquivo(self):
        total = collections.Counter({"test_a.K.test_q": 1})
        erros, por = self.f.completude_da_divisao(self.sp, total, ["test_a"], {"test_a.K": ("test_a", [0])}, [["test_a.K"]],
                                                  {"test_a.K": 1.0})
        self.assertEqual((erros, set(por)), ([], {"test_a.K"}))

    def test_anotacao_sem_duracoes_nao_gera_linha(self):
        self.assertEqual(self.f.anotacoes_de_tempos("1/5", "3.12", None), [])
        self.assertEqual(self.f.anotacoes_de_tempos("1/5", "3.12", {}), [])
        self.assertEqual(len(self.f.anotacoes_de_tempos("1/5", "3.12", {"a": 1.0})), 1)

    def test_anotar_tempos_ignora_relatorio_ausente(self):
        with unittest.mock.patch.object(self.f.sys, "stdout", new_callable=io.StringIO) as saida:
            self.f.anotar_tempos(1, 5, [None, {"duracoes": {"test_a": 1.5}}, None])
        (linha,) = saida.getvalue().splitlines()
        self.assertEqual(json.loads(linha.split("::", 2)[2])["t"], {"test_a": 1.5})


if __name__ == "__main__":
    unittest.main()
