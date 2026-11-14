"""`bin/forge-testes` (TA-3): teste dirigido na iteração do autor; filtro do pre-push (EST-M8), nunca portão de CI."""
import ast
import importlib.machinery
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from apoio_sandbox import exigir  # noqa: E402  (ENVIO-DO-SANDBOX: pula só no sandbox fora do CI)
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-testes"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})


def carregar():
    carregador = importlib.machinery.SourceFileLoader("forge_testes", str(FERRAMENTA))
    spec = importlib.util.spec_from_loader("forge_testes", carregador)
    modulo = importlib.util.module_from_spec(spec)
    carregador.exec_module(modulo)
    return modulo


def sem_oraculos(plano):
    """O plano sem os testes-oráculo do portão (EXT-1): eles entram em todo plano dirigido enquanto existem na árvore, e a
    lista exata do mapa não depende de haver um."""
    modo, modulos = plano
    return modo, [m for m in modulos if not m.startswith("test_oraculo_")]


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=AMBIENTE, capture_output=True, text=True, check=True).stdout


class Mapa(unittest.TestCase):
    """O mapa de caminhos conhecidos e a falha fechada."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def plano(self, *caminhos):
        return self.f.planejar(list(caminhos), RAIZ)

    def test_caminhos_conhecidos_rodam_so_os_modulos_do_mapa(self):
        casos = {
            "bin/forge-changelog": ["evals.test_erros_por_papel", "evals.test_regressao_forma", "test_changelog", "test_conferir_release", "test_forge",
                                    "test_pre_push_afetados"],
            "bin/forge-placar": ["evals.test_placar", "test_forge"],  # 0.43.1, frente I
            ".devcontainer/devcontainer.json": ["test_forge"],  # 0.43.1, frente A
            "bin/forge-doutor": ["test_atualizar", "test_doutor", "test_doutor_branch_atrasada", "test_doutor_custo", "test_doutor_protecao_gh", "test_doutor_relogio",
                                 "test_forge", "test_medidas_m14b", "test_novo_projeto", "test_qa_doutor_f8"],  # v046 E22.1
            "bin/forge-sugerir": ["test_forge", "test_sugerir"],
            "scripts/ci-local": ["test_ci_local", "test_forge", "test_testes_tocados"],
        }
        for caminho, esperado in casos.items():
            with self.subTest(caminho):
                self.assertEqual(sem_oraculos(self.plano(caminho)), ("dirigido", esperado))

    def test_forge_check_roda_os_modulos_dele(self):
        modo, modulos = self.plano("bin/forge-check")
        self.assertEqual(modo, "dirigido")
        self.assertEqual(len([m for m in modulos if not m.startswith("test_oraculo_")]), 83)  # v047: + test_hook_destino_opaco e test_conformidade_opaco (A9). v047: + test_hook_erro_libera (HOOK-ERRO-LIBERA). v046: + test_pr_hook_prazo (PR-HOOK-PRAZO). v046 E20.29: + test_hook_git_comum. 0.45.7: + test_r_limites (AV5), test_forge_medidas (F6, E5.6), test_forge_dora (TM-16) e test_hooks_fila27 (FILA-27). v046 E12.1: + test_git_rede_config. 0.45.6: + test_forge_check_base_igual, test_forge_check_versao_livre e test_pre_push_link_apoio (junção), test_metricas_portoes (E1.1) e test_metricas_main_vermelha (E5.1). 0.44.2: + test_decisor (orkastery 3), test_forge_run (S5), test_meta (S4), test_pesado_fila (orkastery 5), test_aq1_texto e test_textos_034 (troca dos testes de frase). 0.44.1: + test_v0441_review (review), test_acao_da_reprovacao (O1) e test_forge_dono (O4, S2, S8, X1). 0.43.3: + test_aq5_parecer_novo, test_brief_gerar_custo, test_t1_codigo_sem_teste e evals.test_erros_por_papel (E23). 0.43.2: test_pre_push_afetados (COBERTURA-P6). 0.43.1: + evals.test_regressao_forma (I), test_governanca (H), test_selo_e_entrega (E), test_classe_risco (G) e test_parecer_conteudo (F)  # L08: test_fechar_forge_check_real e test_qa_lote_l08; L09 e L10: test_qa_lote_l09 e _l10; doutor-034: test_qa_doutor_034; E7: test_brief_forma_aceita; E4 da 0.35: test_conferente_estavel; E5 da versao-035: test_decisao_aprovacao_raiz; 0.37 E1+E2: test_historico_hora; EST-M4: test_reval_delta; ACELERA-P2: test_citacao_p2; VOLTAS-REVISOR-WT: test_revisor_wt
        for modulo in ("test_hooks_volta_corpus", "test_hooks_volta_lancador", "test_hooks_volta_propriedades",
                       "test_doutor_relogio", "test_erros_no_brief", "test_conferencia_base_dono", "test_anotar", "test_isencoes", "test_citacao", "test_medidas_m14b", "test_forge_medidas", "test_medida_cpu", "test_hook_ansi_c"):
            self.assertIn(modulo, modulos)

    def test_modulos_do_forge_check_rodam_os_testes_dele(self):  # FILA-31 F6: bin/forge_provas.py entra com os outros módulos
        esperado = ("dirigido", sorted(set(self.f.FORGE_CHECK) | set(self.f.oraculos(RAIZ))))
        for caminho in ("bin/forge_governanca.py", "bin/forge_decisor.py", "bin/forge_run.py", "bin/forge_meta.py", "bin/forge_provas.py"):
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), esperado)

    def test_evals_de_forma_rodam_com_a_ferramenta_que_exercitam(self):  # 0.43.1, frentes I e D: módulo em pacote
        for caminho in ("bin/forge-check", "hooks/conformidade.py", "bin/forge-changelog"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertIn("evals.test_regressao_forma", modulos)
        self.assertTrue(self.f.arquivo_do_modulo("evals.test_placar", RAIZ).is_file())

    def test_modulos_que_rodam_o_forge_doutor_estao_na_regra_dele(self):  # MAPA-FORGE-DOUTOR (v046 E22.1)
        regra = next(destino for padrao, destino in self.f.MAPA if padrao == r"bin/forge-doutor")
        modulos = sorted(RAIZ.glob("tests/test_*doutor*.py"))
        self.assertGreaterEqual(len(modulos), 6)  # a varredura achou os módulos do doutor
        rodam = {p.stem for p in modulos if re.search(r"\bself\.doutor\(|\bDOUTOR\b", p.read_text(encoding="utf-8"))}
        self.assertGreaterEqual(len(rodam), 5)
        self.assertLessEqual(rodam, set(regra))

    def test_os_casos_de_comportamento_rodam_so_o_modulo_deles(self):  # L36
        self.assertEqual(sem_oraculos(self.plano("tests/comportamento/casos.json")), ("dirigido", ["test_comportamento"]))

    def test_modulos_da_volta_unica_rodam_onde_o_test_hooks_roda(self):  # HOOKS-CORPUS-RAPIDO
        volta = {"test_hooks_volta_corpus", "test_hooks_volta_lancador", "test_hooks_volta_propriedades"}
        for caminho in ("hooks/doutor.py", "hooks/conformidade.py", "stacks/exemplo/seguranca.md", ".claude-plugin/plugin.json",
                        "bin/forge-check"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertLessEqual(volta, set(modulos))

    def test_hooks_incluem_hooks_e_catraca(self):
        modo, modulos = self.plano("hooks/conformidade.py")
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_hooks", modulos)
        self.assertIn("test_catraca", modulos)

    def test_conteudo_da_fabrica_roda_test_forge(self):
        for caminho in ("agents/jarvis.md", "skills/kanban-scrum/SKILL.md", "docs/economia-de-tokens.md",
                        "templates/projeto/CLAUDE.md", "stacks/x/pronto.md"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertIn("test_forge", modulos)

    def test_caminhos_do_forge_publicado_incluem_test_atualizar(self):
        for caminho in ("migrations/0.7.0/migrar", "templates/projeto/CLAUDE.md", ".claude-plugin/plugin.json",
                        "bin/forge-doutor", "bin/forge", "hooks/doutor.py", "bin/forge-upgrade"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertIn("test_atualizar", modulos)

    def test_stacks_incluem_test_hooks(self):
        modo, modulos = self.plano("stacks/node-react/pesados.json")
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_hooks", modulos)

    # M8, opção C (critério de fim, item 3): módulo de teste no diff não tem regra e roda a suíte inteira.
    def test_modulo_de_teste_no_diff_cai_na_completa_com_o_motivo_sem_mapa(self):
        for caminho in ("tests/test_fechar.py", "tests/test_sugerir.py",  # importado por 13 `test_fechar_*`; sem importador
                        "tests/test_modulo_novo_que_nao_existe.py", "tests/test_forge.py"):  # novo ou apagado; varre tests/
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("completo", [f"{caminho} sem mapa"]))

    def test_caminho_sem_mapa_cai_na_completa(self):
        for caminho in ("coisa-nova/x.py", ".github/workflows/ci.yml", ".githooks/pre-push", "LICENSE",
                        "tests/catraca.py", "tests/fixtures/a.txt", "bin/forge-inexistente"):
            with self.subTest(caminho):
                self.assertEqual(self.plano("bin/forge-sugerir", caminho)[0], "completo")

    def test_config_e_o_proprio_mapa_caem_na_completa(self):
        for caminho in ("tests/config.json", "bin/forge-testes"):
            with self.subTest(caminho):
                self.assertEqual(self.plano("bin/forge-sugerir", caminho)[0], "completo")

    def test_modulo_mapeado_sem_arquivo_cai_na_completa(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "tests").mkdir()
            self.assertEqual(self.f.planejar(["bin/forge-sugerir"], Path(t))[0], "completo")

    def test_modelos_de_parecer_rodam_os_testes_que_os_leem(self):  # MP-1: devops com o mesmo destino de security
        guardas = {"test_volta_por_delta", "test_modelos_parecer_avisos_2", "test_textos_034"}
        for caminho in ("docs/devops/_modelo.md", "templates/projeto/docs/devops/_modelo.md",
                        "docs/security/_modelo.md", "templates/projeto/docs/security/_modelo.md"):
            with self.subTest(caminho):
                modo, modulos = self.plano(caminho)
                self.assertEqual(modo, "dirigido")
                self.assertLessEqual(guardas, set(modulos))

    def test_promover_e_apoio_seguem_na_completa(self):  # MP-1: adendo 2, ponto 3 (decisão 7 do dono)
        for caminho in ("scripts/promover-homolog.py", "tests/apoio_volta_unica.py"):
            with self.subTest(caminho):
                self.assertEqual(self.plano(caminho), ("completo", [f"{caminho} sem mapa"]))

    def test_todo_modulo_do_mapa_existe(self):
        modulos = {m for _, destino in self.f.MAPA if destino for m in destino}
        self.assertGreaterEqual(len(modulos), 10)
        for m in sorted(modulos):
            with self.subTest(m):
                self.assertTrue(self.f.arquivo_do_modulo(m, RAIZ).is_file())  # `evals.test_x` é tests/evals/test_x.py


class Convencao(unittest.TestCase):
    """O2 (0.44.1): o teste se acha pela convenção de nome (bin/forge-x -> tests/test_forge_x.py, hooks/x.py e scripts/x.py ->
    tests/test_x.py); o MAPA fica só para as exceções, e sem o arquivo do teste o caminho segue na suíte completa."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def brinquedo(self, *arquivos):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        raiz = Path(t.name)
        for rel in ("tests/test_forge.py", "tests/test_testes_tocados.py") + arquivos:
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).write_text("x = 1\n", encoding="utf-8")
        return raiz

    def test_bin_scripts_e_hooks_pela_convencao(self):
        raiz = self.brinquedo("tests/test_forge_novo.py", "tests/test_coisa_nova.py", "tests/test_gancho.py")
        self.assertEqual(self.f.planejar(["bin/forge-novo"], raiz), ("dirigido", ["test_forge", "test_forge_novo"]))
        self.assertEqual(self.f.planejar(["scripts/coisa-nova.py"], raiz),
                         ("dirigido", ["test_coisa_nova", "test_forge", "test_testes_tocados"]))
        self.assertEqual(self.f.modulos_da_convencao("hooks/gancho.py", raiz), ("test_gancho", "test_forge"))
        self.assertIn("test_forge_novo", self.f.planejar_afetados(["bin/forge-novo"], raiz)[0])

    def test_sem_o_arquivo_do_teste_ou_fora_das_pastas_segue_na_completa(self):
        raiz = self.brinquedo("tests/test_x_y.py")
        for caminho in ("bin/forge-sem-teste", "outra/x_y.py", "bin/sub/forge-x", "scripts/x-y.sh.py"):
            with self.subTest(caminho):
                self.assertEqual(self.f.planejar([caminho], raiz), ("completo", [f"{caminho} sem mapa"]))
        self.assertIsNone(self.f.modulos_da_convencao("scripts/promover-homolog.py", RAIZ))  # decisão 7: exceção à convenção
        for caminho in ("outra/x_y.py", "bin/sub/forge-x"):  # fora das pastas: None, sem levantar
            with self.subTest(caminho):
                try:
                    achado = self.f.modulos_da_convencao(caminho, raiz)
                except AttributeError as e:
                    achado = f"levantou {e}"
                self.assertIsNone(achado)

    def test_o_mapa_nao_repete_o_que_a_convencao_ja_acha(self):  # some o conflito C8: a entrada do mapa vira exceção de verdade
        repetidas = []
        for padrao, destino in self.f.MAPA:
            convencao = self.f.modulos_da_convencao(padrao.replace("\\", ""), RAIZ)
            if convencao is not None and sorted(convencao) == sorted(destino):
                repetidas.append(padrao)
        self.assertEqual(repetidas, [])
        for caminho in ("bin/forge-mutante", "scripts/arvore-testada.py", "scripts/ci-local", "scripts/conferir-reversao.py"):
            with self.subTest(caminho):
                self.assertFalse(any(re.fullmatch(p, caminho) for p, _ in self.f.MAPA))
                self.assertEqual(self.f.planejar([caminho], RAIZ)[0], "dirigido")


class MapaDosNovos(unittest.TestCase):
    """E14.1 (FORGE-TESTES-MAPA): comando, módulo do bin/ e spec de mutantes novos, sem regra no MAPA nem teste pela
    convenção O2, levam aos testes deles em vez de cair na suíte completa; o que não se resolve segue na completa."""

    SPEC_REAL = ('{"pedido": "varredura-caminho-pessoal", "executor": "unittest", "mutantes": ['
                 '{"id": "P1", "testes": ["tests.test_forge.VerificarContribuicao.test_home_com_ponto_no_nome_falha"]},'
                 '{"id": "P2", "testes": ["tests.evals.test_placar.Placar.test_x"]}]}')

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def brinquedo(self, **arquivos):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        raiz = Path(t.name)
        base = {"tests/test_forge.py": "x = 1\n", "tests/evals/__init__.py": "", "tests/evals/test_placar.py": "x = 1\n"}
        for rel, texto in {**base, **arquivos}.items():
            (raiz / rel).parent.mkdir(parents=True, exist_ok=True)
            (raiz / rel).write_text(texto, encoding="utf-8")
        return raiz

    def test_comando_novo_leva_ao_teste_dele_ao_test_forge_e_a_quem_o_cita(self):
        raiz = self.brinquedo(**{"tests/test_ritmo.py": "x = 1\n", "tests/test_cita.py": "RAIZ / 'bin/forge-ritmo'\n",
                                 "tests/test_outro.py": "'forge-ritmo-x' 'meu-forge-ritmo' 'forge-ritmox'\n"})
        self.assertEqual(self.f.planejar(["bin/forge-ritmo"], raiz), ("dirigido", ["test_cita", "test_forge", "test_ritmo"]))
        self.assertIn("test_ritmo", self.f.planejar_afetados(["bin/forge-ritmo"], raiz)[0])

    def test_comando_novo_sem_o_teste_dele_segue_na_completa(self):
        raiz = self.brinquedo(**{"tests/test_cita.py": "'bin/forge-ritmo'\n"})
        self.assertEqual(self.f.planejar(["bin/forge-ritmo"], raiz), ("completo", ["bin/forge-ritmo sem mapa"]))

    def test_modulo_novo_do_bin_leva_a_quem_o_importa_e_ao_test_forge(self):
        raiz = self.brinquedo(**{"tests/test_leitor.py": "import forge_fontes\n",
                                 "tests/test_outro.py": "'forge_fontes_x' 'o_forge_fontes'\n"})
        self.assertEqual(self.f.planejar(["bin/forge_fontes.py"], raiz), ("dirigido", ["test_forge", "test_leitor"]))
        self.assertEqual(self.f.planejar(["bin/forge_outro.py"], raiz), ("dirigido", ["test_forge"]))

    def test_spec_nova_leva_aos_modulos_do_campo_testes(self):
        raiz = self.brinquedo(**{"tests/mutantes/varredura-caminho-pessoal.json": self.SPEC_REAL})
        caminho = "tests/mutantes/varredura-caminho-pessoal.json"
        self.assertEqual(self.f.planejar([caminho], raiz), ("dirigido", ["evals.test_placar", "test_forge"]))
        self.assertIn("evals.test_placar", self.f.planejar_afetados([caminho], raiz)[0])

    def test_spec_ilegivel_sem_teste_ou_com_teste_de_fora_segue_na_completa(self):
        casos = {"quebrada": "{", "nula": '{"mutantes": null}', "vazia": '{"mutantes": []}',
                 "fora": '{"mutantes": [{"testes": ["test_forge.X.y"]}]}', "numero": '{"mutantes": [{"testes": [1]}]}',
                 "uma-fora": '{"mutantes": [{"testes": ["tests.test_forge.X.y", "outro.test_x"]}]}'}
        raiz = self.brinquedo(**{f"tests/mutantes/{nome}.json": texto for nome, texto in casos.items()})
        for nome in (*casos, "ausente"):
            caminho = f"tests/mutantes/{nome}.json"
            with self.subTest(nome):
                try:
                    plano = self.f.planejar([caminho], raiz)
                except Exception as e:  # noqa: BLE001  levantar é falha do caso, não erro do teste
                    plano = f"levantou {type(e).__name__}"
                self.assertEqual(plano, ("completo", [f"{caminho} sem mapa"]))

    def test_o_modulo_comum_do_bin_segue_com_os_testes_do_forge_mutante(self):
        self.assertIn("test_forge_mutante", self.f.planejar(["bin/forge_apoio_testes.py"], RAIZ)[1])


class MapaCobreOQueOsTestesLeem(unittest.TestCase):
    """Cada arquivo do Forge que um tests/test_*.py lê ou executa tem de levar a esse módulo (o pre-push filtra por isto).

    Formas reconhecidas (ast, não regex): `RAIZ / "a" / "b"`, `RAIZ.joinpath(...)`, uma variável de módulo que guarda
    um caminho (`HOOKS = RAIZ / "hooks"` ou `...parent.parent / "hooks"`) usada como `HOOKS / "x.py"`, e `ler("...")`.
    Quando o módulo monta o caminho com uma variável (`RAIZ / rel`), todo literal do módulo que é um arquivo do
    Forge conta: falha fechada, o mapa tem de ser tão largo quanto o que o teste pode ler."""

    # Este próprio módulo só passa caminhos como texto para `planejar`: não os lê.
    SO_CITA = {"test_testes_tocados"}

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    @classmethod
    def partes(cls, no, vars_):
        """Caminho relativo à raiz (tupla) de uma expressão de caminho, ou None; "*" marca a parte dada por variável."""
        if isinstance(no, ast.Constant) and isinstance(no.value, str):
            return tuple(p for p in no.value.split("/") if p)
        if isinstance(no, ast.Name):
            return vars_.get(no.id)
        if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Div):
            esq = cls.partes(no.left, vars_)
            if esq is None:
                return None
            direita = cls.partes(no.right, vars_) if isinstance(no.right, ast.Constant) else None
            return esq + (direita if direita is not None else ("*",))
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute) and no.func.attr == "joinpath":
            base = cls.partes(no.func.value, vars_)
            if base is None:
                return None
            for arg in no.args:
                p = cls.partes(arg, vars_) if isinstance(arg, ast.Constant) else None
                base = base + (p if p is not None else ("*",))
            return base
        if isinstance(no, ast.Attribute) and no.attr == "parent":  # Path(__file__).resolve().parent[.parent]
            dentro = no.value
            if isinstance(dentro, ast.Attribute) and dentro.attr == "parent":
                return () if ast.unparse(dentro.value) in ("Path(__file__).resolve()", "Path(__file__)") else None
            return ("tests",) if ast.unparse(dentro) in ("Path(__file__).resolve()", "Path(__file__)") else None
        return None

    @classmethod
    def variaveis(cls, arvore):
        """Variáveis de módulo que guardam um caminho fixo (tupla relativa à raiz)."""
        vars_ = {"RAIZ": ()}
        for no in arvore.body:
            if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
                p = cls.partes(no.value, vars_)
                if p is not None and "*" not in p:
                    vars_.setdefault(no.targets[0].id, p)
        return vars_

    def lidos(self, modulo):
        return self.lidos_do_texto(modulo, (RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))

    def lidos_do_texto(self, modulo, texto):
        arvore = ast.parse(texto)
        vars_ = self.variaveis(arvore)
        achados, dinamico = set(), False
        for no in ast.walk(arvore):
            candidato = None
            if isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and no.func.id == "ler":
                if no.args and isinstance(no.args[0], ast.Constant) and isinstance(no.args[0].value, str):
                    candidato = tuple(p for p in no.args[0].value.split("/") if p)
            elif (isinstance(no, ast.BinOp) and isinstance(no.op, ast.Div)) or isinstance(no, ast.Call):
                candidato = self.partes(no, vars_)
            if candidato is None:
                continue
            if "*" in candidato:
                dinamico = True
                candidato = candidato[:candidato.index("*")]
            if candidato and (RAIZ / Path(*candidato)).is_file():
                achados.add("/".join(candidato))
        if dinamico and modulo not in self.SO_CITA:
            for no in ast.walk(arvore):
                if isinstance(no, ast.Constant) and isinstance(no.value, str) and "/" in no.value \
                        and "\n" not in no.value and (RAIZ / no.value).is_file():
                    achados.add(no.value)
        return achados

    def test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo(self):
        modulos = sorted(p.stem for p in (RAIZ / "tests").glob("test_*.py"))
        total = 0
        for modulo in modulos:
            for caminho in sorted(self.lidos(modulo)):
                total += 1
                with self.subTest(modulo=modulo, caminho=caminho):
                    modo, planejados = self.f.planejar([caminho], RAIZ)
                    self.assertTrue(modo == "completo" or modulo in planejados, f"{caminho} -> {planejados}")
        self.assertGreaterEqual(total, 40)

    def test_a_conferencia_enxerga_as_formas_de_citar_um_caminho(self):  # LOTE-M8-PREPUSH (seg A1)
        fonte = (
            "from pathlib import Path\n"
            "RAIZ = Path(__file__).resolve().parent.parent\n"
            "HOOKS = Path(__file__).resolve().parent.parent / 'hooks'\n"
            "def ler(rel):\n    return (RAIZ / rel).read_text()\n"
            "a = HOOKS / 'agentes.py'\n"
            "b = ler('hooks/vigia.py')\n"
            "c = RAIZ.joinpath('bin', 'forge-changelog')\n"
            "def f(rel):\n    return RAIZ / rel\n"
            "d = ('docs/regras/R-BRIEF.md',)\n"
        )
        self.assertEqual(self.lidos_do_texto("test_x", fonte),
                         {"hooks/agentes.py", "hooks/vigia.py", "bin/forge-changelog", "docs/regras/R-BRIEF.md"})

    def test_a_familia_dos_testes_que_executam_hooks_e_bin_roda_no_envio_dirigido(self):  # LOTE-M8-PREPUSH (seg A1)
        for caminho, modulo in (("hooks/agentes.py", "test_agentes_hash_brief"), ("hooks/agentes.py", "test_agentes_clone"),
                                ("hooks/_comum.py", "test_agentes_hash_brief"), ("hooks/_comum.py", "test_agentes_clone"),
                                ("hooks/vigia.py", "test_textos_dono_f10"), ("bin/forge-changelog", "test_conferir_release"),
                                ("agents/jarvis.md", "test_clareza")):
            with self.subTest(caminho=caminho, modulo=modulo):
                self.assertIn(modulo, self.f.planejar([caminho], RAIZ)[1])

    def test_manifesto_do_plugin_de_dev_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):  # FORGE-TESTES-CAMINHOS
        modo, modulos = self.f.planejar(["dev/.claude-plugin/plugin.json"], RAIZ)
        self.assertEqual(modo, "dirigido")
        self.assertEqual(modulos, self.f.planejar([".claude-plugin/plugin.json"], RAIZ)[1])

    def test_conferir_reversao_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):  # REVERSAO-MAPA (A5)
        self.assertEqual(sem_oraculos(self.f.planejar(["scripts/conferir-reversao.py"], RAIZ)),
                         ("dirigido", ["test_conferir_reversao", "test_forge", "test_testes_tocados"]))

    def test_forge_mutante_tem_regra_no_mapa_e_nao_cai_na_suite_completa(self):
        self.assertEqual(sem_oraculos(self.f.planejar(["bin/forge-mutante"], RAIZ)),
                         ("dirigido", ["test_forge", "test_forge_mutante"]))


class Execucao(unittest.TestCase):
    """Roda o script de verdade num repositório de brinquedo."""

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        (self.dir / "tests").mkdir()
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n", encoding="utf-8")
        for modulo in ("test_outro", "test_forge"):
            (self.dir / "tests" / f"{modulo}.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n", encoding="utf-8")
        (self.dir / "bin").mkdir()
        (self.dir / "bin" / "forge-sugerir").write_text("x = 1\n", encoding="utf-8")  # o mapa leva a test_forge e test_sugerir
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(FERRAMENTA), "--base", "develop", *args], cwd=self.dir,
                              env=AMBIENTE, capture_output=True, text=True)

    def log(self):
        return (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8")

    def test_dirigido_roda_so_os_modulos_do_mapa_e_anota_o_log(self):
        (self.dir / "bin" / "forge-sugerir").write_text("x = 2\n", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout)
        self.assertNotIn("test_outro", r.stdout)
        linha = self.log().strip().splitlines()[-1]
        for trecho in ("modo=dirigido", "modulos=test_forge,test_sugerir", "duracao=", "saida=0", "Z "):
            self.assertIn(trecho, linha)

    def test_arquivo_novo_nao_versionado_conta(self):
        (self.dir / "tests" / "test_novo.py").write_text("x = 1\n", encoding="utf-8")
        r = self.rodar("--listar")
        self.assertIn("suíte completa (tests/test_novo.py sem mapa)", r.stdout)  # o teste novo leva à completa

    def test_sem_mapa_roda_a_completa_e_anota(self):
        (self.dir / "novo.txt").write_text("x\n", encoding="utf-8")
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("suíte completa (novo.txt sem mapa)", r.stdout)
        self.assertIn("modo=completo", self.log())

    def test_completa_pedida_e_listar_nao_roda_nada(self):
        self.assertEqual(self.rodar("--listar", "--completa").returncode, 0)
        self.assertFalse((self.dir / ".forge").exists())
        self.assertEqual(self.rodar("--completa").returncode, 0)
        self.assertIn("modo=completo", self.log())

    def test_falha_de_teste_devolve_codigo_e_anota(self):
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ruim(self):\n        self.fail('x')\n",
            encoding="utf-8")
        r = self.rodar()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("saida=1", self.log())

    def test_base_ilegivel_cai_na_completa(self):
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "nao-existe"], cwd=self.dir, env=AMBIENTE,
                           capture_output=True, text=True)
        self.assertIn("suíte completa (não consegui ler o git", r.stdout)

    def test_arquivo_protegido_renomeado_cai_na_completa(self):
        (self.dir / "tests" / "config.json").write_text("{}\n", encoding="utf-8")
        (self.dir / "docs").mkdir()
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "config")
        git(self.dir, "switch", "-q", "-c", "melhoria/y")
        git(self.dir, "mv", "tests/config.json", "docs/config.json")
        git(self.dir, "commit", "-qm", "move")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "melhoria/x", "--listar"], cwd=self.dir,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertIn("suíte completa (tests/config.json altera o mapa ou a configuração)", r.stdout)

    def test_arquivo_mapeado_renomeado_inclui_os_modulos_do_caminho_antigo(self):
        (self.dir / "tests" / "test_forge_mutante.py").write_text("x = 1\n", encoding="utf-8")  # o mapa de bin/forge-mutante o cita
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "bin")
        git(self.dir, "switch", "-q", "-c", "melhoria/z")
        git(self.dir, "mv", "bin/forge-sugerir", "bin/forge-mutante")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "melhoria/x", "--listar"], cwd=self.dir,
                           env=AMBIENTE, capture_output=True, text=True)
        self.assertIn("dirigido (test_forge, test_forge_mutante, test_sugerir)", r.stdout)  # test_sugerir vem do caminho antigo

    # FORGE-TESTES-CAMINHOS: classe "a ferramenta recusa a forma de chamada que os briefs mandam usar". Variantes:
    # caminho relativo, absoluto, com `..`, a partir de subpasta, vários, fora do repositório, junto de opção
    # incompatível e caminho começado por `-` (depois de `--`).
    def rodar_com(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=cwd or self.dir, env=AMBIENTE,
                              capture_output=True, text=True)

    def test_caminhos_dirigem_o_plano_sem_olhar_o_git(self):
        r = self.rodar_com("--listar", "bin/forge-sugerir", "bin/forge-sugerir")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout)
        self.assertFalse((self.dir / ".forge").exists())

    def test_caminho_sem_mapa_cai_na_completa_e_o_alterado_no_git_nao_conta(self):
        (self.dir / "tests" / "test_sugerir.py").write_text("x = 1\n", encoding="utf-8")  # alterado, mas não citado
        r = self.rodar_com("--listar", "novo.txt")
        self.assertIn("suíte completa (novo.txt sem mapa)", r.stdout)

    def test_caminho_absoluto_com_ponto_ponto_e_de_subpasta_valem(self):
        (self.dir / "sub").mkdir()
        absoluto = str(self.dir / "bin" / "forge-sugerir")
        for args, cwd in (((absoluto,), None), (("sub/../bin/forge-sugerir",), None),
                          (("../bin/forge-sugerir",), self.dir / "sub")):
            with self.subTest(args=args, cwd=cwd):
                r = self.rodar_com("--listar", *args, cwd=cwd)
                self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout, r.stdout + r.stderr)

    def test_caminho_fora_do_repositorio_e_recusado(self):
        r = self.rodar_com("--listar", "../fora.py")
        self.assertEqual(r.returncode, 2)
        self.assertIn("fora do repositório", r.stderr)
        self.assertNotIn("dirigido", r.stdout)

    def test_caminhos_nao_combinam_com_completa_nem_com_vermelho(self):
        for opcao in (("--completa",), ("--vermelho", "HEAD")):  # o `--vermelho` consome o argumento seguinte como base
            with self.subTest(opcao):
                r = self.rodar_com(*opcao, "tests/test_sugerir.py")
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("caminhos não combinam", r.stderr)

    def test_caminho_comecado_por_hifen_so_depois_de_dois_hifens(self):
        r = self.rodar_com("--listar", "--", "-x.py")
        self.assertIn("suíte completa (-x.py sem mapa)", r.stdout)

    def test_nada_alterado_nao_roda(self):
        r = self.rodar()
        self.assertIn("nada alterado", r.stdout)
        self.assertFalse((self.dir / ".forge").exists())


class PlanoAfetados(unittest.TestCase):
    """SUITE-NO-CI: o plano `--afetados` do pre-push, conferido no repositório real. Conservador: nunca menos que o mapa,
    todo módulo que cita o caminho entra e os arquivos de controle levam todo módulo que os exercita."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.textos = cls.f.textos_dos_testes(RAIZ)

    def plano(self, *caminhos):
        return self.f.planejar_afetados(list(caminhos), RAIZ)

    def citam(self, *agulhas):
        return {m for m, texto in self.textos.items() if any(a in texto for a in agulhas)}

    def test_nunca_menos_que_o_mapa(self):
        rastreados = git(RAIZ, "ls-files").splitlines()
        conferidos = 0
        for padrao, _ in self.f.MAPA:
            for caminho in [c for c in rastreados if re.fullmatch(padrao, c)][:2]:
                modo, mapa = self.f.planejar([caminho], RAIZ)
                if modo != "dirigido":
                    continue
                conferidos += 1
                with self.subTest(caminho):
                    self.assertLessEqual(set(mapa), set(self.plano(caminho)[0]))
        self.assertGreaterEqual(conferidos, 20)

    def test_quem_cita_o_caminho_entra(self):
        for caminho in ("bin/forge-sugerir", "scripts/ci-local", "docs/economia-de-tokens.md"):
            with self.subTest(caminho):
                self.assertLessEqual(self.citam(caminho), set(self.plano(caminho)[0]))

    def test_arquivos_de_controle_levam_todo_modulo_que_os_exercita(self):
        casos = {"hooks/_comum.py": ("_comum", "hooks/"), "bin/forge-check": ("forge-check", "forge_check"),
                 ".githooks/pre-push": (".githooks", "pre-push", "pre_push"),
                 "scripts/suite-paralela.py": ("suite-paralela", "suite_paralela"), "scripts/suite-partes.py": ("suite-partes",)}
        for caminho, agulhas in casos.items():
            with self.subTest(caminho):
                modulos = set(self.plano(caminho)[0])
                exercitam = self.citam(*agulhas)
                self.assertGreaterEqual(len(exercitam), 2)
                self.assertLessEqual(exercitam, modulos)
        self.assertLessEqual(set(self.f.FORGE_CHECK), set(self.plano("bin/forge-check")[0]))
        self.assertLessEqual({"test_hooks", "test_catraca"} | set(self.f.VOLTA_UNICA), set(self.plano("hooks/_comum.py")[0]))
        self.assertLessEqual({"test_pre_push_afetados", "test_pre_push_trava", "test_pre_push_shellcheck", "test_prepush_so_docs"},
                             set(self.plano(".githooks/pre-push")[0]))
        self.assertLessEqual({"test_suite_paralela", "test_suite_partes"}, set(self.plano("scripts/suite-paralela.py")[0]))
        # 0.45.4: o módulo comum dos dois scripts leva quem roda o forge-testes de verdade (o repositório falso do pre-push)
        self.assertLessEqual({"test_pre_push_afetados", "test_pre_push_parecer_curto", "test_forge_mutante", "test_testes_tocados"},
                             set(self.plano("bin/forge_apoio_testes.py")[0]))

    def test_modulo_de_teste_roda_ele_quem_o_importa_e_quem_varre_tests(self):
        modulos = set(self.plano("tests/test_fechar.py")[0])
        importam = {m for m, texto in self.textos.items() if "from test_fechar import" in texto or "import test_fechar" in texto}
        self.assertTrue(importam)
        self.assertLessEqual({"test_fechar", "test_testes_tocados", "test_forge"} | importam, modulos)
        self.assertNotIn("test_hooks", modulos)  # não é a suíte inteira

    def test_apoio_de_tests_roda_quem_o_importa(self):
        modulos, notas = self.plano("tests/apoio_volta_unica.py")
        self.assertLessEqual(self.citam("apoio_volta_unica"), set(modulos))
        self.assertTrue(modulos)
        self.assertEqual(notas, [])

    def test_caminho_sem_leitor_vira_nota_e_nao_suite_completa(self):
        caminho = "coisa-" + "nova/" + "ninguem" + "-le.txt"  # montado: o texto deste módulo não pode citá-lo
        modulos, notas = self.plano(caminho)
        self.assertEqual(modulos, [])
        self.assertEqual(notas, [f"{caminho}: nenhum teste o lê; fica para o CI"])

    def test_caminho_sem_mapa_nas_pastas_varridas_leva_test_forge(self):
        self.assertIn("test_forge", self.plano("scripts/script-novo-sem-leitor.py")[0])

    def test_modulo_de_pacote_mudado_roda_ele(self):  # tests/evals/ é pacote: o discover o acha
        modulos = set(self.plano("tests/evals/test_placar.py")[0])
        self.assertIn("evals.test_placar", modulos)
        self.assertIn("evals.test_regressao_forma", self.textos)
        self.assertLessEqual({"evals.test_placar", "test_forge"}, set(self.plano("bin/forge-placar")[0]))

    def test_modulo_do_mapa_sem_arquivo_sai_com_nota(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "tests").mkdir()
            (Path(d) / "tests" / "test_sugerir.py").write_text("x = 1\n", encoding="utf-8")
            modulos, notas = self.f.planejar_afetados(["bin/forge-sugerir"], Path(d))
        self.assertEqual(modulos, ["test_sugerir"])
        self.assertIn("test_forge", notas[0])


class ExecucaoAfetados(Execucao):
    """`--afetados` de verdade: os módulos rodam em paralelo pelo `scripts/suite-partes.py` quando ele existe."""

    def setUp(self):
        super().setUp()
        (self.dir / "scripts").mkdir()
        for origem in ("scripts/suite-paralela.py", "scripts/suite-partes.py", "tests/guarda_git.py", "tests/ambiente_git.py"):
            (self.dir / origem).write_bytes((RAIZ / origem).read_bytes())
        (self.dir / ".gitignore").write_text("__pycache__/\n/.forge\n", encoding="utf-8")
        git(self.dir, "switch", "-q", "develop")  # o mecanismo está na base: fora do diff da branch
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "mecanismo paralelo")
        git(self.dir, "switch", "-q", "-C", "melhoria/x")

    # Os testes herdados de Execucao continuam valendo com os scripts no repositório: o modo padrão não mudou.

    def test_afetados_rodam_em_paralelo_e_anotam_o_log(self):
        (self.dir / "bin" / "forge-sugerir").write_text("x = 2\n", encoding="utf-8")
        r = self.rodar("--afetados")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("dirigido (test_forge, test_sugerir)", r.stdout)
        self.assertIn("suite-partes: afetados: 2 testes em 2 módulos", r.stderr)
        self.assertIn("modo=dirigido", self.log())

    def test_afetados_paralelo_reprova_a_falha(self):
        (self.dir / "tests" / "test_sugerir.py").write_text(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ruim(self):\n        self.fail('x')\n", encoding="utf-8")
        r = self.rodar("--afetados")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAILED", r.stdout)
        self.assertIn("saida=1", self.log())

    def test_com_k_roda_em_serie(self):
        (self.dir / "bin" / "forge-sugerir").write_text("x = 2\n", encoding="utf-8")
        r = self.rodar("--afetados", "-k", "test_ok")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("suite-partes", r.stderr)

    def test_afetados_nunca_a_completa_e_sem_nada_nao_roda(self):
        (self.dir / "novo.txt").write_text("x\n", encoding="utf-8")
        r = self.rodar("--afetados")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("nada a rodar", r.stdout)
        self.assertIn("novo.txt: nenhum teste o lê; fica para o CI", r.stderr)
        self.assertNotIn("suíte completa", r.stdout)

    def test_afetados_nao_combina_com_completa_nem_vermelho(self):
        for opcao in (("--completa",), ("--vermelho",)):
            with self.subTest(opcao):
                self.assertEqual(self.rodar("--afetados", *opcao).returncode, 2)


class NaoEPortao(unittest.TestCase):
    """Decisão do dono: "A, desde que para main rode tudo." O CI e os hooks do Claude não chamam o script; o único
    portão local que o chama é o pre-push (M8, decisões do dono de 2026-10-23 e 2026-10-24: A), que recua para a
    suíte inteira quando o plano não é dirigido."""

    def test_nenhum_portao_cita_o_script(self):
        alvos = [RAIZ / ".github", RAIZ / "hooks", RAIZ / "scripts" / "ci-local", RAIZ / "bin" / "forge-check"]
        arquivos = []
        for alvo in alvos:
            # __pycache__ fica de fora: o .pyc guarda o caminho da worktree, que pode se chamar forge-testes-*
            arquivos += [alvo] if alvo.is_file() else [p for p in alvo.rglob("*")
                                                       if p.is_file() and "__pycache__" not in p.parts]
        self.assertGreaterEqual(len(arquivos), 4)
        for arquivo in arquivos:
            with self.subTest(str(arquivo.relative_to(RAIZ))):
                texto = arquivo.read_text(encoding="utf-8", errors="replace")
                if arquivo == RAIZ / "hooks" / "pesado.py":
                    # Exceção única (maq-a1b-classe, 0.45.1): o pesado não roda o script, só classifica a carga do comando
                    # (R-TETO); o nome entra numa linha só, a constante PELOS_ARGUMENTOS, e nada no hook o executa.
                    linhas = [l for l in texto.splitlines() if "forge-testes" in l]
                    self.assertEqual([l.split(" =", 1)[0] for l in linhas], ["PELOS_ARGUMENTOS"], linhas)
                    continue
                self.assertNotIn("forge-testes", texto)

    # REVERSAO-MAPA (A6): script de aviso chama o forge-testes e não é portão; a lista é fechada. Script novo que o
    # cite sem entrar aqui reprova, e a entrada na lista é a decisão consciente de que ele só avisa.
    AVISOS = {"scripts/conferir-reversao.py"}

    def test_so_script_de_aviso_cita_o_script_em_scripts(self):
        citam = set()
        arquivos = [p for p in (RAIZ / "scripts").rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        self.assertGreaterEqual(len(arquivos), 5)
        for arquivo in arquivos:
            if "forge-testes" in arquivo.read_text(encoding="utf-8", errors="replace"):
                citam.add(arquivo.relative_to(RAIZ).as_posix())
        self.assertEqual(citam, self.AVISOS)

    def test_so_o_pre_push_cita_o_script_em_githooks(self):
        citam = {p.relative_to(RAIZ).as_posix() for p in (RAIZ / ".githooks").rglob("*")
                 if p.is_file() and "forge-testes" in p.read_text(encoding="utf-8", errors="replace")}
        self.assertEqual(citam, {".githooks/pre-push"})

    def test_pre_push_recua_para_a_suite_inteira(self):
        self.assertIn("python3 -m unittest discover -s tests",
                      (RAIZ / ".githooks" / "pre-push").read_text(encoding="utf-8"))

    def test_regra_5_cita_o_script_e_a_decisao_do_dono(self):
        texto = (RAIZ / "docs" / "economia-de-tokens.md").read_text(encoding="utf-8")
        self.assertIn("bin/forge-testes", texto)
        self.assertIn("M8", texto)
        self.assertIn("2026-10-24", texto)  # a decisão do dono que substitui a de 2026-10-15
        self.assertNotIn("pre-push, review, QA, CI e o caminho para a main rodam a suíte inteira", texto)
        self.assertIn("CI de todo PR", texto)

    def test_docstring_cita_a_decisao_m8_de_2026_10_24(self):  # COMENTARIOS-PREPUSH
        doc = ast.get_docstring(ast.parse(FERRAMENTA.read_text(encoding="utf-8")))
        self.assertIn("M8", doc)
        self.assertIn("2026-10-24", doc)
        self.assertIn("substitui", doc)

    def test_docstring_nao_manda_review_e_qa_rodarem_a_suite_inteira(self):  # COMENTARIOS-PREPUSH, review A4
        doc = ast.get_docstring(ast.parse(FERRAMENTA.read_text(encoding="utf-8"))).replace("\n", " ")
        self.assertNotIn("Review, QA, o CI do PR", doc)
        self.assertIn("autor e os revisores rodam só os testes do item", doc)
        self.assertIn("a suíte inteira fica no pre-push e no CI", doc)

    def test_log_fica_fora_do_git(self):
        self.assertIn("/.forge", (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines())


class MapaCobreImportacaoEVarredura(unittest.TestCase):
    """M8, opção C: importação entre testes e varredura de pasta (`glob`, `rglob`, `iterdir`) não pedem grafo no mapa,
    porque módulo de teste no diff roda a suíte inteira."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()
        cls.testes = sorted(p.stem for p in (RAIZ / "tests").glob("test_*.py"))

    def importados(self, texto):
        """Módulos de teste importados por nome (`import`, `from ... import`, `import_module` com literal)."""
        achados = set()
        for no in ast.walk(ast.parse(texto)):
            if isinstance(no, ast.Import):
                nomes = [a.name for a in no.names]
            elif isinstance(no, ast.ImportFrom) and not no.level:
                nomes = [no.module or ""]
            elif isinstance(no, ast.Call) and getattr(no.func, "attr", "") == "import_module" and no.args \
                    and isinstance(no.args[0], ast.Constant):
                nomes = [str(no.args[0].value).split(".")[-1]]
            else:
                continue
            achados.update(n for n in nomes if re.fullmatch(r"test_[a-z0-9_]+", n))
        return achados

    def varridos(self, texto):
        """Arquivos do Forge que um `glob`, `rglob` ou `iterdir` sobre caminho conhecido alcança, e a pasta varrida."""
        arvore = ast.parse(texto)
        vars_ = MapaCobreOQueOsTestesLeem.variaveis(arvore)
        achados, pastas = set(), set()
        for no in ast.walk(arvore):
            if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Attribute)
                    and no.func.attr in ("glob", "rglob", "iterdir")):
                continue
            base = MapaCobreOQueOsTestesLeem.partes(no.func.value, vars_)
            if base is None or "*" in base or not (RAIZ / Path(*base)).is_dir():
                continue
            pasta = RAIZ / Path(*base)
            casados = pasta.iterdir() if no.func.attr == "iterdir" else getattr(pasta, no.func.attr)(getattr(no.args[0], "value", "*"))
            pastas.add("/".join(base))
            achados.update(c.relative_to(RAIZ).as_posix() for c in casados if c.is_file() and "__pycache__" not in c.parts)
        return achados, pastas

    def cobre(self, caminho, modulo):
        modo, planejados = self.f.planejar([caminho], RAIZ)
        return modo == "completo" or modulo in planejados

    def test_todo_teste_importado_por_outro_leva_quem_importa_a_suite_inteira(self):  # critério C.1
        arestas = 0
        for modulo in self.testes:
            importados = self.importados((RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))
            for importado in sorted(importados & set(self.testes)):
                arestas += 1
                with self.subTest(modulo=modulo, importado=importado):
                    self.assertEqual(self.f.planejar([f"tests/{importado}.py"], RAIZ)[0], "completo")
        self.assertGreaterEqual(arestas, 31)  # as 31 linhas de `import`/`from` entre testes na varredura da segurança

    def test_toda_varredura_de_pasta_conhecida_leva_o_modulo_a_suite_inteira_ou_ao_plano(self):  # critério C.2
        total, varrem_tests = 0, set()
        for modulo in self.testes:
            achados, pastas = self.varridos((RAIZ / "tests" / f"{modulo}.py").read_text(encoding="utf-8"))
            if "tests" in pastas:
                varrem_tests.add(modulo)
            for caminho in sorted(achados):
                total += 1
                with self.subTest(modulo=modulo, caminho=caminho):
                    self.assertTrue(self.cobre(caminho, modulo))
        self.assertGreaterEqual(total, 1000)
        # quem varre `tests/` cai quando um módulo de teste muda: todo módulo de teste dá a suíte inteira (C.1 e `Mapa`)
        self.assertLessEqual({"test_ambiente_git", "test_testes_tocados", "test_forge"}, varrem_tests)


class MapaDoForgeCheck(unittest.TestCase):
    """O mapa de `bin/forge-check` lista todo módulo que importa ou executa o script (FORGE-TESTES-MAPA)."""

    CITA = re.compile(r'bin/forge-check|"bin"\s*[,/]\s*"forge-check"|joinpath\("bin",\s*"forge-check"\)')
    IMPORTA = re.compile(r"^\s*(?:from|import)\s+(test_[a-z0-9_]+)\b", re.M)
    IMPORTA_APOIO = re.compile(r"^\s*(?:from|import)\s+(apoio_[a-z0-9_]+)\b", re.M)

    def modulos_que_usam(self):
        textos = {p.stem: p.read_text(encoding="utf-8") for p in (RAIZ / "tests").glob("test_*.py")}
        apoios = {p.stem: p.read_text(encoding="utf-8") for p in (RAIZ / "tests").glob("apoio_*.py")}
        # `tests/apoio_*.py` importado por um módulo de teste conta como parte dele: o que o apoio cita ou importa de
        # `test_*` vale para quem o importa (HOOKS-CORPUS-RAPIDO: os `test_hooks_volta_*` rodam o script pelo apoio).
        for modulo, texto in textos.items():
            for apoio in self.IMPORTA_APOIO.findall(texto):
                textos[modulo] += "\n" + apoios.get(apoio, "")
        usam = {m for m, t in textos.items() if self.CITA.search(t)}
        usam.discard("test_doutor")  # só grava um `bin/forge-check` falso na semente; não executa o real
        usam.add("test_catraca")  # carrega o script por `catraca.forge_check()`, sem citar o caminho
        mudou = True
        while mudou:  # quem importa um módulo que usa o script também o executa
            mudou = False
            for m, t in textos.items():
                if m not in usam and usam & set(self.IMPORTA.findall(t)):
                    usam.add(m)
                    mudou = True
        return usam

    def test_mapa_lista_todo_modulo_que_usa_o_forge_check(self):
        usam = {m for m in self.modulos_que_usam() if not m.startswith("test_oraculo_")}  # EXT-1: entram por oraculos()
        self.assertGreaterEqual(len(usam), 8)
        listados = set(carregar().FORGE_CHECK)
        self.assertEqual(sorted(usam - listados), [], "faltam no mapa FORGE_CHECK")
        self.assertEqual(sorted(listados - usam), [], "sobram no mapa FORGE_CHECK")

    def test_erros_no_brief_roda_quando_so_o_forge_check_muda(self):
        modo, modulos = carregar().planejar(["bin/forge-check"], RAIZ)
        self.assertEqual(modo, "dirigido")
        self.assertIn("test_erros_no_brief", modulos)


class Oraculos(unittest.TestCase):
    """EXT-1: o teste-oráculo do portão (`tests/test_oraculo_<pedido>.py`) entra em todo plano dirigido; nome fora do
    padrão, link ou pasta faz o `forge-testes` falhar, nunca sumir do plano (C-5); o oráculo não se pula (C-4)."""
    TRIVIAL = "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"
    PULA = re.compile(r"\bskip(If|Unless)?\b|SkipTest|expectedFailure")

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        (self.dir / "tests").mkdir()
        self.f = carregar()

    def gravar(self, nome, texto=TRIVIAL):
        alvo = self.dir / "tests" / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)  # módulo de pacote (evals/test_x.py)
        alvo.write_text(texto, encoding="utf-8")

    def test_oraculo_entra_no_plano_sem_mudar_a_contagem(self):
        self.gravar("test_oraculo_x.py")
        for caminho in ("bin/forge-check", "hooks/conformidade.py"):
            with self.subTest(caminho):
                _, real = self.f.planejar([caminho], RAIZ)
                for m in real:
                    self.gravar(m.replace(".", "/") + ".py")
                modo, modulos = self.f.planejar([caminho], self.dir)
                self.assertEqual(modo, "dirigido")
                self.assertIn("test_oraculo_x", modulos)
                self.assertEqual(sorted(set(modulos) - {"test_oraculo_x"}), sorted(set(real) - {"test_oraculo_x"}))
        self.assertEqual(self.f.planejar([], self.dir), ("dirigido", []), "nada alterado, nada a rodar")

    def test_nome_fora_do_padrao_link_ou_pasta_falha(self):
        alvo = self.dir / "fora.py"
        alvo.write_text(self.TRIVIAL, encoding="utf-8")
        casos = {"maiuscula": lambda: self.gravar("test_oraculo_X.py"), "ponto": lambda: self.gravar("test_oraculo_a.b.py"),
                 "link": lambda: (self.dir / "tests" / "test_oraculo_l.py").symlink_to(alvo),
                 "pasta": lambda: (self.dir / "tests" / "test_oraculo_p.py").mkdir()}
        for nome, criar in casos.items():
            with self.subTest(nome):
                for p in (self.dir / "tests").glob("test_oraculo_*"):
                    p.rmdir() if p.is_dir() and not p.is_symlink() else p.unlink()
                criar()
                with self.assertRaises(ValueError):
                    self.f.oraculos(self.dir)

    def test_forge_testes_sai_com_erro_e_o_nome_saneado(self):
        git(self.dir, "init", "-q", "-b", "develop")
        self.gravar("test_oraculo_a\x1b.py")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--base", "develop", "--listar"], cwd=self.dir, env=AMBIENTE,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("test_oraculo_a\\x1b.py", r.stderr)
        self.assertNotIn("\x1b", r.stderr)

    def test_oraculo_do_repositorio_nao_se_pula(self):
        self.assertTrue(self.PULA.search("@unittest.skipIf(True, 'x')") and self.PULA.search("@unittest.expectedFailure"))
        for p in sorted((RAIZ / "tests").glob("test_oraculo_*.py")):
            with self.subTest(p.name):
                self.assertIsNone(self.PULA.search(p.read_text(encoding="utf-8")), "oráculo sem skip nem expectedFailure (C-4)")


class ClassificacaoDoVermelho(unittest.TestCase):
    """A classe de cada teste vem do resultado por teste (falha × erro), nunca do código de saída do processo."""

    @classmethod
    def setUpClass(cls):
        cls.f = carregar()

    def classe(self, h, b, mudou=False, removidos=()):
        def entrada(res, tipo=None, nome=None):
            return {"id": "tests.m.T.t", "res": res, "tipo": tipo, "nome": nome}
        return self.f.classificar(entrada(*h), None if b is None else entrada(*b), mudou, set(removidos))

    def test_falha_por_asserção_na_base_e_prova(self):
        self.assertEqual(self.classe(("ok",), ("falha", "AssertionError")), "prova (asserção)")

    def test_api_ausente_e_prova(self):
        for tipo in ("AttributeError", "NameError", "ImportError"):
            with self.subTest(tipo):
                self.assertEqual(self.classe(("ok",), ("erro", tipo)), "prova (API ausente)")

    def test_modulo_que_a_diff_cria_e_api_ausente(self):
        self.assertEqual(self.classe(("ok",), ("erro", "ModuleNotFoundError", "pacote.apoio"), removidos=["apoio"]),
                         "prova (API ausente)")

    def test_erro_do_proprio_modulo_de_teste_e_sem_veredito_e_nunca_vermelho(self):  # CA-4
        for b in (("erro", "ModuleNotFoundError", "nao_existe"), ("erro", "SyntaxError"), ("erro", "ValueError")):
            with self.subTest(b):
                self.assertEqual(self.classe(("ok",), b, removidos=["apoio"]), "sem veredito")

    def test_passa_nos_dois_nao_prova(self):
        self.assertEqual(self.classe(("ok",), ("ok",)), "não prova (passa na base)")

    def test_cai_no_head_e_passa_na_base_e_regressao(self):
        self.assertEqual(self.classe(("falha", "AssertionError"), ("ok",)), "regressão")

    def test_divida_so_vale_com_modulo_sem_mudanca_e_falha_por_asserção_na_base(self):  # CA-6 e CA-7
        falha = ("falha", "AssertionError")
        self.assertEqual(self.classe(falha, falha, mudou=False), "dívida pré-existente")
        self.assertEqual(self.classe(falha, falha, mudou=True), self.f.ENTREGA)
        self.assertEqual(self.classe(falha, ("erro", "ImportError"), mudou=False), self.f.ENTREGA)
        self.assertEqual(self.classe(falha, None), self.f.ENTREGA)

    def test_sem_registro_na_base_e_sem_veredito(self):
        self.assertEqual(self.classe(("ok",), None), "sem veredito")

    def test_erro_de_setup_da_classe_na_base_vale_para_os_testes_da_classe(self):  # A3 do review
        erro = {"id": "setUpClass (tests.m.T)", "res": "erro", "tipo": "FileNotFoundError", "nome": "novo"}
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a"), erro)
        outra = {"id": "setUpClass (tests.m.U)", "res": "erro", "tipo": "ValueError", "nome": None}
        self.assertIsNone(self.f.da_base({outra["id"]: outra}, "tests.m.T.test_a"))

    def test_erro_de_setup_do_modulo_na_base_vale_para_os_testes_do_modulo(self):  # A3 do review
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": None}
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a"), erro)

    def test_entrada_herdada_de_teste_que_ja_existia_na_base_vira_herdada_e_nao_prova(self):  # A1 do review e da segurança
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": "novo"}
        b = self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a", {"T.test_a"})
        self.assertTrue(b["herdada"])
        self.assertEqual(self.classe(("ok",), (b["res"], b["tipo"], b["nome"]), removidos=["novo"]), "prova (API ausente)")
        self.assertEqual(self.f.classificar({"res": "ok"}, b, False, {"novo"}), "não prova (herdada da base)")
        self.assertIs(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_b", {"T.test_a"}), erro)

    def test_base_ilegivel_do_modulo_nao_da_prova_herdada(self):
        erro = {"id": "setUpModule (tests.m)", "res": "erro", "tipo": "ImportError", "nome": "novo"}
        self.assertTrue(self.f.da_base({erro["id"]: erro}, "tests.m.T.test_a", self.f.TodosExistiam())["herdada"])

    def test_a_entrada_do_proprio_teste_vence_a_do_setup(self):
        proprio = {"id": "tests.m.T.test_a", "res": "ok", "tipo": None, "nome": None}
        erro = {"id": "setUpClass (tests.m.T)", "res": "erro", "tipo": "ImportError", "nome": None}
        self.assertIs(self.f.da_base({proprio["id"]: proprio, erro["id"]: erro}, proprio["id"]), proprio)

    def test_arquivo_que_o_diff_cria_e_o_setup_nao_achou_na_base_e_api_ausente(self):  # A3 do review
        erro = ("erro", "FileNotFoundError", "novo.txt")
        self.assertEqual(self.classe(("ok",), erro, removidos=["novo"]), "prova (API ausente)")
        self.assertEqual(self.classe(("ok",), erro, removidos=["outro"]), "sem veredito")


class Vermelho(unittest.TestCase):
    """`--vermelho BASE` num repositório de brinquedo: duas cópias em $TMPDIR, a árvore real intacta."""

    LIB = "def dobro(x):\n    return x\n"
    BASE_TESTE = ("import unittest\nimport lib\n\n\nclass T(unittest.TestCase):\n"
                  "    def test_um(self):\n        self.assertEqual(lib.dobro(0), 0)\n")

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name) / "repo"
        self.tmp = Path(self._t.name) / "tmp"
        self.dir.mkdir()
        self.tmp.mkdir()
        git(self.dir, "init", "-q", "-b", "develop")
        self.gravar("lib.py", self.LIB)
        self.gravar("tests/test_lib.py", self.BASE_TESTE)
        self.gravar(".gitignore", ".forge\n")
        self.salvar("base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def gravar(self, nome, texto):
        alvo = self.dir / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(texto, encoding="utf-8")

    def salvar(self, mensagem):
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", mensagem)

    def metodo(self, nome, corpo):
        return f"\n    def {nome}(self):\n        {corpo}\n"

    def env(self, **extra):
        return {**AMBIENTE, "TMPDIR": str(self.tmp), **extra}

    def rodar(self, *args, **extra):
        return subprocess.run([sys.executable, str(FERRAMENTA), *args], cwd=self.dir, env=self.env(**extra),
                              capture_output=True, text=True)

    def vermelho(self, *args, **extra):
        return self.rodar("--vermelho", "develop", *args, **extra)

    def corrigir_lib(self):
        self.gravar("lib.py", "def dobro(x):\n    return x * 2\n")

    TRIVIAL = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"

    def com_modulos_do_mapa(self):
        """Base do vermelho: `bin/forge-sugerir` (o mapa leva a test_forge e test_sugerir) e test_outro (fora do mapa)."""
        self.gravar("bin/forge-sugerir", "x = 1\n")
        for modulo in ("test_forge", "test_sugerir", "test_outro"):
            self.gravar(f"tests/{modulo}.py", self.TRIVIAL)
        self.salvar("apoio")

    def modulos_do_vermelho(self, r):
        linha = next(l for l in r.stdout.splitlines() if l.startswith("vermelho: base="))
        return linha.split("módulos=")[1].split(" ")[0].split(","), linha

    # M8, opção C (critério de fim, item 4): o `--vermelho` sem `--modulos` não manda módulo de teste ao `planejar`.
    def test_vermelho_usa_o_modulo_de_teste_do_diff_mais_o_plano_dos_outros_caminhos(self):
        self.com_modulos_do_mapa()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.gravar("tests/test_sugerir.py", self.TRIVIAL + "# mudou\n")
        self.gravar("tests/test_outro.py", self.TRIVIAL + "# mudou\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, linha = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_outro", "test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("restrito", linha)

    # VERMELHO-FILTRO: os dados de teste do diff (a spec de mutantes de todo item) não levam à suíte completa.
    def test_vermelho_com_spec_e_fixture_no_diff_roda_so_o_plano_do_mapa(self):
        self.com_modulos_do_mapa()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.gravar("tests/mutantes/x.json", "{}\n")
        self.gravar("tests/fixtures/y.txt", "y\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, _ = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("o mapa não sabe", r.stdout)

    def test_vermelho_com_caminho_sem_mapa_avisa_e_roda_a_suite_completa(self):
        self.com_modulos_do_mapa()
        self.gravar("lib.py", "def dobro(x):\n    return x\n# mudou\n")
        self.gravar("tests/mutantes/x.json", "{}\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, _ = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_lib", "test_outro", "test_sugerir"], r.stdout + r.stderr)
        self.assertIn("vermelho: o mapa não sabe (lib.py sem mapa); suíte completa.", r.stdout)

    def test_vermelho_com_config_no_diff_segue_na_suite_completa(self):
        self.com_modulos_do_mapa()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.gravar("tests/config.json", "{}\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, _ = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_lib", "test_outro", "test_sugerir"], r.stdout + r.stderr)
        self.assertIn("tests/config.json altera o mapa", r.stdout)

    def test_vermelho_com_modulos_ignora_o_mapa_e_nao_avisa(self):
        self.com_modulos_do_mapa()
        self.gravar("lib.py", "def dobro(x):\n    return x\n# mudou\n")
        self.salvar("muda")
        r = self.rodar("--vermelho", "HEAD~1", "--modulos", "test_outro")
        modulos, linha = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_outro"], r.stdout + r.stderr)
        self.assertIn("(restrito por --modulos)", linha)
        self.assertNotIn("o mapa não sabe", r.stdout)

    def test_vermelho_aceita_o_modulo_pelo_nome_com_o_pacote(self):  # FORGE-TESTES-MODULOS-NOME
        """`tests.test_outro` (a forma do `unittest`) dá o mesmo plano que `test_outro`; outra grafia segue rc 2, sem cópia."""
        self.com_modulos_do_mapa()
        self.gravar("lib.py", "def dobro(x):\n    return x\n# mudou\n")
        self.salvar("muda")
        curto = self.modulos_do_vermelho(self.rodar("--vermelho", "HEAD~1", "--modulos", "test_outro"))
        r = self.rodar("--vermelho", "HEAD~1", "--modulos", "tests.test_outro,test_lib")
        self.assertIn("vermelho: base=", r.stdout, r.stderr)
        self.assertEqual(self.modulos_do_vermelho(r)[0], ["test_outro", "test_lib"], r.stdout + r.stderr)
        r = self.rodar("--vermelho", "HEAD~1", "--modulos", "tests.test_outro")
        self.assertEqual(self.modulos_do_vermelho(r), curto, r.stdout + r.stderr)
        for grafia in ("tests.tests.test_outro", "tests/test_outro.py", "tests.", "test_a,,test_b", "tests.test_a;b",
                       "Tests.test_outro", "tests.test_outro.py", "xtests.test_outro"):
            with self.subTest(grafia):
                r = self.rodar("--vermelho", "HEAD~1", "--modulos", grafia)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertIn("test_<nome> ou tests.test_<nome>", r.stderr)
                self.assertEqual(list(self.tmp.iterdir()), [])

    def test_vermelho_com_modulo_de_teste_apagado_no_diff_nao_o_roda(self):
        self.com_modulos_do_mapa()
        (self.dir / "tests" / "test_outro.py").unlink()
        self.gravar("bin/forge-sugerir", "x = 2\n")
        self.salvar("apaga")
        r = self.rodar("--vermelho", "HEAD~1")
        modulos, _ = self.modulos_do_vermelho(r)
        self.assertEqual(modulos, ["test_forge", "test_sugerir"], r.stdout + r.stderr)
        self.assertNotIn("sem veredito", r.stdout)

    def test_producao_mudada_e_teste_novo_que_a_cobre_e_prova_por_asserção(self):  # lib.py sem mapa: todos os módulos
        self.corrigir_lib()
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_dobro", "self.assertEqual(lib.dobro(2), 4)"))
        self.salvar("corrige")
        antes = git(self.dir, "status", "--porcelain")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("vermelho: base=", r.stdout)
        self.assertIn("revertidos à base: lib.py", r.stdout)
        self.assertIn("tests.test_lib.T.test_dobro · H=ok · B=falha · prova (asserção)", r.stdout)
        self.assertEqual(git(self.dir, "status", "--porcelain"), antes)
        self.assertEqual(list(self.tmp.iterdir()), [], "sobrou cópia em $TMPDIR")
        self.assertIn("modo=vermelho", (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8"))

    def test_teste_que_chama_funcao_que_a_base_nao_tem_e_prova_de_api_ausente(self):
        self.gravar("lib.py", self.LIB + "\n\ndef triplo(x):\n    return x * 3\n")
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_triplo", "self.assertEqual(lib.triplo(2), 6)"))
        self.salvar("triplo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("B=erro · prova (API ausente)", r.stdout)

    def test_arquivo_de_apoio_de_tests_e_producao_e_volta_a_base(self):  # CA-3
        self.gravar("tests/apoio.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_apoio", "import sys; sys.path.insert(0, os.path.dirname(__file__)); import apoio; self.assertEqual(apoio.VALOR, 1)"))
        self.salvar("apoio")
        r = self.vermelho()
        self.assertIn("revertidos à base: tests/apoio.py", r.stdout)
        self.assertIn("mantidos no HEAD: tests/test_lib.py", r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("prova (API ausente)", r.stdout)

    def test_setup_da_classe_que_carrega_o_arquivo_novo_prova_e_nao_vira_sem_veredito(self):  # A3 do review
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\nfrom pathlib import Path\n\n\nclass T(unittest.TestCase):\n"
                    "    @classmethod\n    def setUpClass(cls):\n        cls.texto = Path('novo.py').read_text()\n\n"
                    "    def test_um(self):\n        self.assertIn('VALOR', self.texto)\n\n"
                    "    def test_dois(self):\n        self.assertTrue(self.texto)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertIn("tests.test_novo.T.test_dois · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def test_setup_do_modulo_que_importa_o_arquivo_novo_prova_e_nao_vira_sem_veredito(self):  # A3 do review
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\n\n\ndef setUpModule():\n    global novo\n    import novo\n\n\n"
                    "class T(unittest.TestCase):\n    def test_um(self):\n        self.assertEqual(novo.VALOR, 1)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)

    def test_modulo_que_importa_o_arquivo_novo_no_topo_prova_e_nao_vira_sem_veredito(self):  # R3 da segurança
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\n\nimport novo\n\n\nclass T(unittest.TestCase):\n"
                    "    def test_um(self):\n        self.assertEqual(novo.VALOR, 1)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_novo.T.test_um · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def modulo_existente_com_entrada_nova(self, antes, depois=""):
        """Entrega que cria `novo.py` e só acrescenta ao módulo que já existia na base uma entrada que o importa."""
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", antes + self.BASE_TESTE + depois)
        self.salvar("so entrada")
        return self.vermelho()

    def confere_sem_prova_herdada(self, r):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("tests.test_lib.T.test_um · H=ok · B=erro · não prova (herdada da base)", r.stdout)
        self.assertNotIn("prova (API ausente)", r.stdout)
        self.assertNotIn("sem veredito", r.stdout)

    def test_import_novo_no_topo_de_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.confere_sem_prova_herdada(self.modulo_existente_com_entrada_nova("import novo  # noqa: F401\n"))

    def test_setup_da_classe_novo_em_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_lib.py", self.BASE_TESTE.replace(
            "    def test_um", "    @classmethod\n    def setUpClass(cls):\n        import novo  # noqa: F401\n\n    def test_um"))
        self.salvar("so setup")
        self.confere_sem_prova_herdada(self.vermelho())

    def test_setup_do_modulo_novo_em_modulo_existente_sem_teste_novo_sai_1(self):  # A1 do review e da segurança
        self.confere_sem_prova_herdada(self.modulo_existente_com_entrada_nova(
            "def setUpModule():\n    import novo  # noqa: F401\n\n\n"))

    def test_teste_novo_ao_lado_do_existente_prova_e_o_existente_continua_neutro(self):
        r = self.modulo_existente_com_entrada_nova(
            "import novo\n", self.metodo("test_novo", "self.assertEqual(novo.VALOR, 1)"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("tests.test_lib.T.test_novo · H=ok · B=erro · prova (API ausente)", r.stdout)
        self.assertIn("tests.test_lib.T.test_um · H=ok · B=erro · não prova (herdada da base)", r.stdout)

    def test_setup_da_classe_que_falha_por_outro_motivo_nao_vira_vermelho(self):  # a ampliação tem o alvo do diff
        self.gravar("novo.py", "VALOR = 1\n")
        self.gravar("tests/test_novo.py", "import unittest\nfrom pathlib import Path\n\n\nclass T(unittest.TestCase):\n"
                    "    @classmethod\n    def setUpClass(cls):\n        cls.texto = Path('faltando.txt').read_text()\n\n"
                    "    def test_um(self):\n        self.assertTrue(True)\n")
        self.salvar("novo")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("prova (API ausente)", r.stdout)

    def test_teste_mudado_que_passa_na_base_nao_prova_e_sai_1(self):
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_novo", "self.assertTrue(True)"))
        self.salvar("so teste")
        r = self.vermelho("--modulos", "test_lib")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("não prova (passa na base)", r.stdout)
        self.assertIn("nenhum teste prova a mudança", r.stdout)
        self.assertIn("(restrito por --modulos)", r.stdout)

    def test_teste_sem_mudanca_que_cai_no_head_e_regressao(self):
        self.gravar("lib.py", "def dobro(x):\n    return 2\n")
        self.salvar("quebra")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("H=falha · B=ok · regressão", r.stdout)

    def test_teste_sem_mudanca_que_ja_caia_na_base_e_divida_e_continua_bloqueando(self):  # CA-7
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_ruim", "self.assertEqual(lib.dobro(1), 5)"))
        self.salvar("divida")
        git(self.dir, "switch", "-q", "-c", "melhoria/y")
        self.gravar("lib.py", self.LIB + "\n\ndef outro():\n    return 0\n")
        self.salvar("outro")
        r = self.rodar("--vermelho", "melhoria/x")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("dívida pré-existente", r.stdout)
        self.assertIn("há teste que falha no HEAD", r.stdout)

    def test_teste_alterado_que_falha_na_base_e_no_head_nao_e_divida(self):  # CA-6
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_ruim", "self.fail('x')"))
        self.salvar("ruim")
        r = self.vermelho()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("regressão ou sem veredito", r.stdout)
        self.assertNotIn("dívida", r.stdout)

    def test_teste_que_estoura_o_prazo_e_sem_veredito_e_sai_2(self):  # CA-9
        self.corrigir_lib()
        self.gravar("tests/test_lib.py", self.BASE_TESTE + self.metodo("test_lento", "__import__('time').sleep(60)"))
        self.salvar("lento")
        r = self.vermelho("--prazo", "2")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("sem veredito", r.stdout)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_arvore_suja_sai_2_e_nao_cria_copia(self):  # CA-1
        self.corrigir_lib()
        r = self.vermelho()
        self.assertEqual(r.returncode, 2)
        self.assertIn("mudança não commitada", r.stderr)
        self.assertEqual((self.dir / "lib.py").read_text(encoding="utf-8"), "def dobro(x):\n    return x * 2\n")
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_base_invalida_sai_2_sem_criar_arquivo_nem_recuar(self):  # CA-8
        self.corrigir_lib()
        self.salvar("corrige")
        for args in (["--vermelho=--output=gravado.txt"], ["--base=--output=gravado.txt", "--vermelho"],
                     ["--vermelho", "nao-existe"]):
            with self.subTest(args):
                r = self.rodar(*args)
                self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                self.assertFalse((self.dir / "gravado.txt").exists())
                self.assertNotIn("suíte completa", r.stdout)

    def test_uso_invalido_sai_2(self):
        for args in (["--vermelho", "develop", "--completa"], ["--modulos", "test_lib"], ["--prazo", "5"],
                     ["--vermelho", "develop", "--modulos", "a;b"], ["--vermelho", "develop", "--prazo", "0"]):
            with self.subTest(args):
                self.assertEqual(self.rodar(*args).returncode, 2)

    def test_sinal_no_meio_da_rodada_deixa_a_arvore_intacta_e_apaga_as_copias(self):  # CA-2
        self.corrigir_lib()
        corpo = "open(os.environ['MARCA'], 'w').close(); __import__('time').sleep(60)"
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_dorme", corpo))
        self.salvar("dorme")
        antes = git(self.dir, "status", "--porcelain")
        marca = Path(self._t.name) / "marca"
        processo = subprocess.Popen([sys.executable, str(FERRAMENTA), "--vermelho", "develop"], cwd=self.dir,
                                    env=self.env(MARCA=str(marca)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(processo.kill)
        for _ in range(300):
            if marca.exists():
                break
            time.sleep(0.1)
        self.assertTrue(marca.exists(), "o teste lento não começou")
        processo.terminate()
        processo.wait(timeout=60)
        self.assertEqual(git(self.dir, "status", "--porcelain"), antes)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_ambiente_da_copia_nao_herda_git_nem_forge(self):
        self.corrigir_lib()
        corpo = "self.assertEqual([k for k in os.environ if k.startswith(('GIT_DIR', 'GIT_WORK_TREE', 'FORGE_'))], [])"
        self.gravar("tests/test_lib.py", "import os\n" + self.BASE_TESTE + self.metodo("test_ambiente", corpo)
                    + self.metodo("test_dobro", "self.assertEqual(lib.dobro(2), 4)"))
        self.salvar("ambiente")
        r = self.vermelho(GIT_DIR=str(self.dir / ".git"), GIT_WORK_TREE=str(self.dir), FORGE_X="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("H=falha", r.stdout)
        self.assertNotIn("H=erro", r.stdout)


class CaminhoFiltroEAviso(unittest.TestCase):
    """CAMINHO de módulo sem mapa (FORGE-TESTES-SEM-MAPA), aviso cedo do MAPA (MAPA-TESTES-AVISO-CEDO) e `-k`
    (TESTES-DO-ITEM-FILTRO), num repositório de brinquedo."""

    CORPO = ("import unittest\n{leitura}class Rapido(unittest.TestCase):\n    def test_a(self):\n        pass\n"
             "class Lento(unittest.TestCase):\n    def test_b(self):\n        pass\n")

    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dir = Path(self._t.name)
        git(self.dir, "init", "-q", "-b", "develop")
        (self.dir / "tests").mkdir()
        (self.dir / "bin").mkdir()
        (self.dir / "bin" / "forge-sugerir").write_text("x = 1\n", encoding="utf-8")
        for modulo in ("test_forge", "test_sugerir", "test_novo", "test_outro"):
            self.escrever(modulo)
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-qm", "base")
        git(self.dir, "switch", "-q", "-c", "melhoria/x")

    def escrever(self, modulo, leitura=""):
        (self.dir / "tests" / f"{modulo}.py").write_text(self.CORPO.format(leitura=leitura), encoding="utf-8")

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(FERRAMENTA), "--base", "develop", *args], cwd=self.dir,
                              env=AMBIENTE, capture_output=True, text=True)

    def test_caminho_de_modulo_de_teste_roda_so_esse_modulo_e_avisa(self):  # FORGE-TESTES-SEM-MAPA
        r = self.rodar("tests/test_novo.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("sem mapa para tests/test_novo.py; roda só test_novo", r.stderr)
        self.assertIn("dirigido (test_novo)", r.stdout)
        self.assertNotIn("suíte completa", r.stdout)
        self.assertIn("modulos=test_novo ", (self.dir / ".forge" / "run" / "testes.log").read_text(encoding="utf-8"))

    def test_caminho_de_modulo_inexistente_ou_misturado_com_outro_arquivo_segue_o_mapa(self):
        self.assertIn("suíte completa", self.rodar("tests/test_nao_existe.py").stdout)
        self.assertIn("suíte completa", self.rodar("tests/test_novo.py", "docs/sem-regra.txt").stdout)

    def test_teste_que_le_bin_fora_do_mapa_avisa_cedo(self):  # MAPA-TESTES-AVISO-CEDO
        self.escrever("test_novo", 'RAIZ = None\nx = RAIZ / "bin" / "forge-sugerir"\n')
        r = self.rodar("--listar", "tests/test_novo.py")
        self.assertIn("tests/test_novo.py lê bin/forge-sugerir, mas o MAPA não leva a test_novo", r.stderr)

    def test_sem_aviso_quando_o_mapa_ja_leva_o_modulo_ou_so_cita_o_caminho(self):
        self.escrever("test_sugerir", 'RAIZ = None\nx = RAIZ / "bin" / "forge-sugerir"\n')
        self.escrever("test_novo", 'CITA = "bin/forge-sugerir"\n')
        r = self.rodar("--listar", "tests/test_sugerir.py", "tests/test_novo.py")
        self.assertNotIn("o MAPA não leva", r.stderr)

    def test_sem_aviso_quando_o_teste_passa_bin_x_como_argumento_ou_dado(self):  # bug forge-testes-034-aviso-falso-chamada
        self.escrever("test_novo", 'def plano(c):\n    return c\nx = plano("bin/forge-sugerir")\ny = ("bin/forge-sugerir", 1)\n')
        r = self.rodar("--listar", "tests/test_novo.py")
        self.assertNotIn("o MAPA não leva", r.stderr)

    def test_aviso_vale_tambem_no_diff_sem_caminho(self):
        self.escrever("test_novo", 'RAIZ = None\nx = RAIZ.joinpath("bin", "forge-sugerir")\n')
        self.assertIn("o MAPA não leva a test_novo", self.rodar("--listar").stderr)

    def test_k_filtra_os_testes_do_modulo(self):  # TESTES-DO-ITEM-FILTRO
        r = self.rodar("-k", "Lento", "tests/test_novo.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Ran 1 test", r.stderr)
        self.assertIn("Ran 2 tests", self.rodar("tests/test_novo.py").stderr)

    def test_k_repetido_soma_os_padroes_e_nao_combina_com_vermelho(self):
        self.assertIn("Ran 2 tests", self.rodar("-k", "test_a", "-k", "test_b", "tests/test_novo.py").stderr)
        r = self.rodar("--vermelho", "-k", "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn("-k não combina com --vermelho", r.stderr)


def proc_falso(pasta, quem=b"bin/forge-testes"):
    """/proc de brinquedo: 10 é quem anota, 5 o ancestral pesado, 20 a outra pesada, 40 sumiu no meio da leitura."""
    for pid, pai, linha in ((10, 5, quem), (5, 1, b"suite-paralela.py"), (20, 1, b"-m\0unittest\0discover"), (40, 1, b"")):
        (pasta / str(pid)).mkdir(parents=True)
        (pasta / str(pid) / "stat").write_text(f"{pid} (a b) S {pai} 0", encoding="utf-8")
        (pasta / str(pid) / ("cmdline" if linha else "outro")).write_bytes(linha)
    (pasta / "self").mkdir()
    return pasta


class MedidaDaVagaPesada(unittest.TestCase):
    """MAQ-A7: a linha do testes.log guarda os campos de hoje e ganha entrada, load1, nproc e outras."""
    setUp, log = Execucao.setUp, Execucao.log

    def rodar_com(self, **env):
        limpo = {k: v for k, v in AMBIENTE.items() if k not in ("FORGE_ENTRADA", "CI")}
        return subprocess.run([sys.executable, "-I", str(FERRAMENTA), "--base", "develop", "--completa"], cwd=self.dir,
                              env={**limpo, **env}, capture_output=True, text=True)

    def test_a_linha_mantem_o_formato_de_hoje_e_so_aceita_entrada_valida(self):
        for valor, esperado in ((None, "autor"), ("push", "push"), ("push\n", "?"), ("push\nmodo=x", "?")):
            with self.subTest(valor):
                self.assertEqual(self.rodar_com(**({} if valor is None else {"FORGE_ENTRADA": valor})).returncode, 0)
                self.assertRegex(self.log().splitlines()[-1], r"^\S+Z modo=completo modulos=- duracao=[0-9.]+s saida=0 "
                                 rf"entrada={re.escape(esperado)} load1=[0-9.]+ nproc=\d+ outras=(\d+|\?)$")
        self.assertEqual(len(self.log().splitlines()), 4)  # a quebra de linha no valor não abre linha nova

    def test_conta_a_pesada_viva_sem_gravar_a_linha_de_comando_dela(self):
        exigir(self, "proc")
        falso = self.dir / "marca-a7" / "suite-paralela.py"
        falso.parent.mkdir()
        falso.write_text("import time\ntime.sleep(120)\n", encoding="utf-8")
        processo = subprocess.Popen([sys.executable, "-I", str(falso)])
        self.addCleanup(processo.wait)
        self.addCleanup(processo.kill)
        cmdline = Path("/proc") / str(processo.pid) / "cmdline"
        fim = time.monotonic() + 30  # espera o estado (a pesada já aparece no /proc), não uma janela fixa
        lido = lambda: cmdline.read_bytes() if cmdline.exists() else b""
        while b"suite-paralela.py" not in lido() and time.monotonic() < fim:
            time.sleep(0.1)
        self.assertIn(b"suite-paralela.py", lido())
        self.rodar_com()
        self.assertGreaterEqual(int(re.search(r"outras=(\d+)", self.log()).group(1)), 1)
        self.assertNotIn("marca-a7", self.log())

    def test_outras_e_contexto_toleram_falha_de_leitura(self):
        f = carregar()
        self.assertEqual(f.outras(proc_falso(self.dir / "proc"), eu=10), 1)  # nem a própria, nem o ancestral, nem a 40
        self.assertEqual(f.outras(self.dir / "sem-proc", eu=10), "?")
        with mock.patch("os.getloadavg", side_effect=OSError), mock.patch.dict(os.environ, {"FORGE_ENTRADA": "push\n"}):
            self.assertRegex(f.contexto(), r"^ entrada=\? load1=\? nproc=")

    def test_fila31_forge_testes_e_forge_mutante_usam_o_mesmo_modulo_comum(self):
        """FILA-31 F1: a linha de contexto do log (MAQ-A7) vem de bin/forge_apoio_testes.py nos dois scripts."""
        from test_forge_mutante import carregar as carregar_mutante  # noqa: PLC0415
        testes, mutante = carregar(), carregar_mutante()
        comum = str(Path(testes.__file__).resolve().parent / "forge_apoio_testes.py")
        for nome in ("outras", "contexto"):
            with self.subTest(nome=nome):
                self.assertEqual(getattr(testes, nome).__code__.co_filename, comum)
                self.assertEqual(getattr(mutante, nome).__code__.co_filename, comum)
        self.assertEqual((testes.ENTRADA.pattern, testes.PESADA.pattern), (mutante.ENTRADA.pattern, mutante.PESADA.pattern))
        with mock.patch.dict(os.environ, {"FORGE_ENTRADA": "push"}):
            self.assertRegex(mutante.contexto(), r"^ entrada=push load1=")


def sem_git(**extra):
    """os.environ sem `GIT_*` herdado (um hook exporta `GIT_DIR`), mais `extra`."""
    return {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **extra}


class GitDaCopia(unittest.TestCase):
    """FILA-31 F2: `git_da_copia`, `resolver` e `montar_copia` vêm de bin/forge_apoio_testes.py nos dois scripts, cada um
    com o próprio `ambiente_da_copia` (o do forge-mutante também tira o PYTHONPYCACHEPREFIX)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.raiz = self.dir / "raiz"
        self.raiz.mkdir()
        git(self.raiz, "init", "-q", "-b", "main")
        (self.raiz / "a.txt").write_text("a\n", encoding="utf-8")
        git(self.raiz, "add", "a.txt")
        git(self.raiz, "commit", "-qm", "a")
        self.sha = git(self.raiz, "rev-parse", "HEAD").strip()

    def test_fila31_f2_os_dois_scripts_usam_o_git_da_copia_comum_com_o_proprio_ambiente(self):
        from test_forge_mutante import carregar as carregar_mutante  # noqa: PLC0415
        testes, mutante = carregar(), carregar_mutante()
        comum = str(Path(testes.__file__).resolve().parent / "forge_apoio_testes.py")
        for script in (testes, mutante):
            with self.subTest(script=script.__name__):
                for nome in ("git_da_copia", "montar_copia"):
                    parcial = getattr(script, nome)
                    self.assertEqual(parcial.func.__code__.co_filename, comum)
                    self.assertEqual(parcial.args, (script.ambiente_da_copia,))
                self.assertEqual(script.resolver.__code__.co_filename, comum)

    def test_fila31_f2_copia_isolada_do_git_dir_herdado_e_erro_do_git_levanta(self):
        for script in (carregar(), __import__("test_forge_mutante").carregar()):
            with self.subTest(script=script.__name__):
                destino = self.dir / script.__name__
                with mock.patch.dict(os.environ, sem_git(GIT_DIR=str(self.dir / "nao-existe")), clear=True):
                    try:
                        script.montar_copia(self.raiz, destino, self.sha)
                    except RuntimeError as erro:
                        self.fail(f"o GIT_DIR herdado venceu a cópia: {erro}")
                    with self.assertRaisesRegex(RuntimeError, "^git rev-parse"):
                        script.git_da_copia("rev-parse", "--verify", "--quiet", "refs/nao/existe", cwd=destino)
                self.assertEqual(git(destino, "rev-parse", "HEAD").strip(), self.sha)

    def test_fila31_f2_resolver_da_o_sha_ou_none(self):
        for script in (carregar(), __import__("test_forge_mutante").carregar()):
            with self.subTest(script=script.__name__), \
                    mock.patch.dict(os.environ, sem_git(GIT_DIR=str(self.raiz / ".git")), clear=True):
                self.assertEqual(script.resolver("HEAD"), self.sha)
                self.assertIsNone(script.resolver("refs/nao/existe"))
                self.assertIsNone(script.resolver("-h"))


if __name__ == "__main__":
    unittest.main()
