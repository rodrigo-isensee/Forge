"""Garante que nenhum teste roda `git` num repositório temporário com a manutenção automática do git ligada.

`ambiente_git.sem_manutencao` é o ponto único. Aqui: (1) ele junta as chaves em vez de sobrescrevê-las; (2) o
repositório que recebe push também fica sem manutenção (`remoto_sem_manutencao`); (3) uma leitura estática (ast) de
todos os `tests/*.py` falha se uma chamada direta a `git` (subprocess) não receber, na própria chamada, um ambiente
montado por ele; (4) os módulos de tests/ carregam também no modo dirigido (`python3 -m unittest tests.<módulo>`).
Origem: erros de tearDown por `maintenance.lock` só em worktree (S-9)."""
import ast
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import CONFIGURACAO, remoto_sem_manutencao, sem_manutencao  # noqa: E402

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
CHAMADAS = {"run", "Popen", "check_output", "check_call", "call"}
PONTO_UNICO = "sem_manutencao"
NOMES_DE_AMBIENTE = {"env", "ambiente", "AMBIENTE", "self.env"}
METODOS_DE_PREPARO = {"setUp", "setUpClass", "__init__"}
# Exceção por chamada: o repositório da chamada é o real do Forge (`-C RAIZ` ou, sem `-C`, `cwd=RAIZ`). Hoje só leituras
# (rev-parse, diff, ls-files): não cria nem faz commit em repositório temporário, então não dispara a manutenção.
REPOSITORIO_REAL = {"RAIZ", "str(RAIZ)"}
# Exceção por arquivo, explícita: fora da leitura estática, com o motivo.
EXCECOES = {
    "catraca.py": "controle protegido (R-SEGURANCA): não se mexe nele por este pedido; só lê o repositório (git show, "
                  "git diff), sem criar nem fazer commit, então não dispara a manutenção",
}


def _nome(chamada):
    return getattr(chamada.func, "id", getattr(chamada.func, "attr", None))


def _eh_git(chamada):
    f = chamada.func
    return (isinstance(f, ast.Attribute) and f.attr in CHAMADAS and getattr(f.value, "id", "") == "subprocess"
            and chamada.args and isinstance(chamada.args[0], ast.List) and chamada.args[0].elts
            and isinstance(chamada.args[0].elts[0], ast.Constant) and chamada.args[0].elts[0].value == "git")


def _no_repositorio_real(chamada):
    """True se o repositório da chamada é o real: `git -C RAIZ ...` ou, sem `-C`, `cwd=RAIZ`."""
    lista = chamada.args[0].elts
    if len(lista) > 2 and isinstance(lista[1], ast.Constant) and lista[1].value == "-C":
        return ast.unparse(lista[2]) in REPOSITORIO_REAL
    cwd = next((k.value for k in chamada.keywords if k.arg == "cwd"), None)
    return cwd is not None and ast.unparse(cwd) in REPOSITORIO_REAL


class _Leitura:
    """Resolve, para cada chamada, de onde vem o `env=`: só vale o que sai do ponto único na mesma função (atribuição
    mais próxima antes da chamada), no preparo da classe (`self.env`) ou no nível do módulo, ou de uma função do
    módulo que devolve o ponto único."""

    def __init__(self, arvore, pasta=AQUI, vistos=frozenset()):
        self.arvore = arvore
        self.pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
        self.classes = {c.name: c for c in ast.walk(arvore) if isinstance(c, ast.ClassDef)}
        self.construtores = {PONTO_UNICO} | self._importados(pasta, vistos)
        funcoes = [f for f in ast.walk(arvore) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
        mudou = True
        while mudou:  # função que devolve o ponto único (ou outra que o devolve) também é construtora
            mudou = False
            for f in funcoes:
                if f.name not in self.construtores and any(
                        isinstance(r, ast.Return) and r.value is not None and self.vem(r.value)
                        for r in ast.walk(f)):
                    self.construtores.add(f.name)
                    mudou = True

    def _importados(self, pasta, vistos):
        """Construtores importados de outro módulo de tests/ (`from test_forge import ambiente_limpo`): valem só se lá
        a função devolve o ponto único."""
        nomes = set()
        for imp in ast.walk(self.arvore):
            origem = pasta / f"{getattr(imp, 'module', None)}.py"
            if isinstance(imp, ast.ImportFrom) and imp.module and imp.module not in vistos and origem.is_file():
                daquele = _Leitura(ast.parse(origem.read_text(encoding="utf-8")), pasta, vistos | {imp.module})
                nomes |= {a.asname or a.name for a in imp.names if a.name in daquele.construtores}
        return nomes

    def _acima(self, no, tipos):
        while no in self.pais:
            no = self.pais[no]
            if isinstance(no, tipos):
                return no
        return None

    @staticmethod
    def _ultima(escopos, texto, antes_de=None):
        atribuicoes = [a for escopo in escopos for a in escopo
                       if isinstance(a, (ast.Assign, ast.AnnAssign))
                       and any(ast.unparse(alvo) == texto for alvo in (a.targets if isinstance(a, ast.Assign) else [a.target]))
                       and (antes_de is None or a.lineno < antes_de)]
        return max(atribuicoes, key=lambda a: a.lineno, default=None)

    def _preparo(self, classe, vistas):
        """Atribuições dos métodos de preparo da classe; se não houver `self.env` ali, das classes-base do módulo."""
        if classe is None or classe.name in vistas:
            return None
        vistas.add(classe.name)
        metodos = [m for m in classe.body if isinstance(m, ast.FunctionDef) and m.name in METODOS_DE_PREPARO]
        achada = self._ultima([list(ast.walk(m)) for m in metodos], "self.env")
        if achada is not None:
            return achada
        for base in classe.bases:
            achada = self._preparo(self.classes.get(getattr(base, "id", None)), vistas)
            if achada is not None:
                return achada
        return None

    def montado(self, texto, referencia, profundidade=0):
        if texto not in NOMES_DE_AMBIENTE or profundidade > 10:
            return False
        funcao = self._acima(referencia, (ast.FunctionDef, ast.AsyncFunctionDef))
        achada = None
        if funcao is not None:
            achada = self._ultima([list(ast.walk(funcao))], texto, antes_de=referencia.lineno)
        if achada is None and texto == "self.env":
            achada = self._preparo(self._acima(referencia, ast.ClassDef), set())
        if achada is None:
            achada = self._ultima([self.arvore.body], texto)
        return achada is not None and achada.value is not None and self.vem(achada.value, profundidade + 1)

    def vem(self, expr, profundidade=0):
        """True se a expressão sai do ponto único: chamada a um construtor, `dict(x, ...)`/`{**x, ...}` com x que vem
        dele, ou um nome de ambiente montado com ele."""
        if isinstance(expr, ast.Call):
            if _nome(expr) in self.construtores:
                return True
            return _nome(expr) == "dict" and bool(expr.args) and self.vem(expr.args[0], profundidade)
        if isinstance(expr, ast.Dict):
            return any(k is None and self.vem(v, profundidade) for k, v in zip(expr.keys, expr.values))
        if isinstance(expr, (ast.Name, ast.Attribute)):
            return self.montado(ast.unparse(expr), expr, profundidade)
        return False


def problemas(fonte, nome="<modulo>", pasta=AQUI):
    """Lista de textos `arquivo:linha: problema` do código `fonte`; vazia se toda chamada usa o ponto único. `pasta`:
    onde procurar os módulos importados (para os construtores que vêm de outro módulo de tests/)."""
    leitura = _Leitura(ast.parse(fonte), pasta)
    achados = []
    for no in ast.walk(leitura.arvore):
        if not (isinstance(no, ast.Call) and _eh_git(no)) or _no_repositorio_real(no):
            continue
        env = next((k.value for k in no.keywords if k.arg == "env"), None)
        if env is None:
            achados.append(f"{nome}:{no.lineno}: git sem `env=` do ponto único (ambiente_git.sem_manutencao)")
        elif not leitura.vem(env):
            achados.append(f"{nome}:{no.lineno}: `{ast.unparse(env)}` não é montado com sem_manutencao")
    return achados


def bare_sem_remoto(fonte, nome="<modulo>"):
    """Funções que criam repositório bare (`--bare`) sem chamar `remoto_sem_manutencao` na mesma função."""
    achados = []
    arvore = ast.parse(fonte)
    pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
    for f in ast.walk(arvore):
        if not isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        cria = any(isinstance(n, ast.Constant) and n.value == "--bare" and isinstance(pais.get(n), (ast.Call, ast.List))
                   for n in ast.walk(f))  # argumento de uma chamada (git("init", "--bare", ...) ou ["git", ...])
        if cria and not any(isinstance(n, ast.Call) and _nome(n) == "remoto_sem_manutencao" for n in ast.walk(f)):
            achados.append(f"{nome}:{f.lineno}: `{f.name}` cria repositório bare sem remoto_sem_manutencao")
    return achados


def modulos_lidos():
    return [m for m in sorted(AQUI.glob("*.py")) if m.name not in EXCECOES]


class SemManutencao(unittest.TestCase):
    def pares(self, env):
        return {env[f"GIT_CONFIG_KEY_{i}"]: env[f"GIT_CONFIG_VALUE_{i}"] for i in range(int(env["GIT_CONFIG_COUNT"]))}

    def test_tres_chaves_desligam_a_manutencao(self):
        self.assertEqual(self.pares(sem_manutencao({})),
                         {"maintenance.auto": "false", "gc.auto": "0", "receive.autogc": "false"})

    def test_junta_as_chaves_do_chamador_sem_perder_nenhuma(self):
        env = sem_manutencao({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "user.name", "GIT_CONFIG_VALUE_0": "t", "X": "1"})
        self.assertEqual(self.pares(env), {"user.name": "t", **dict(CONFIGURACAO)})
        self.assertEqual(env["X"], "1")
        self.assertEqual(env["GIT_CONFIG_COUNT"], "4")

    def test_idempotente_e_nao_altera_o_original(self):
        original = {"A": "b"}
        uma = sem_manutencao(original)
        self.assertEqual(sem_manutencao(uma), uma)
        self.assertEqual(original, {"A": "b"})

    def test_usa_os_environ_por_padrao(self):
        self.assertEqual(sem_manutencao()["PATH"], os.environ["PATH"])


class LeituraEstatica(unittest.TestCase):
    def test_detecta_git_sem_ambiente(self):
        self.assertTrue(problemas('import subprocess\nsubprocess.run(["git", "init"], cwd=d)\n'))
        self.assertTrue(problemas('import subprocess\nsubprocess.run(["git", "init"], env=os.environ)\n'))
        self.assertTrue(problemas('import subprocess\nenv = {}\nsubprocess.run(["git", "init"], env=env)\n'))

    def test_aceita_ambiente_do_ponto_unico_e_repositorio_real(self):
        self.assertEqual(problemas('subprocess.run(["git", "init"], env=sem_manutencao({}))\n'), [])
        self.assertEqual(problemas('self.env = sem_manutencao(x)\nsubprocess.run(["git", "init"], env=self.env)\n'), [])
        self.assertEqual(problemas('subprocess.run(["git", "-C", str(RAIZ), "diff"])\n'), [])

    def test_nenhum_modulo_roda_git_sem_o_ponto_unico(self):
        modulos = sorted(AQUI.glob("test_*.py"))
        com_git = [m for m in modulos if '["git"' in m.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(com_git), 10, "a leitura deveria alcançar os módulos que rodam git")
        for modulo in modulos:
            with self.subTest(modulo=modulo.name):
                self.assertEqual(problemas(modulo.read_text(encoding="utf-8"), modulo.name), [])

    def test_ambiente_por_chamada_nao_por_modulo(self):
        monta = 'def a():\n    env = sem_manutencao({})\n    subprocess.run(["git", "init"], env=env)\n'
        self.assertEqual(problemas(monta), [])
        # outra função do mesmo módulo com `env` próprio, sem `env` nenhum, ou reatribuído depois da montagem
        self.assertTrue(problemas(monta + 'def b(d):\n    env = {}\n    subprocess.run(["git", "commit"], cwd=d, env=env)\n'))
        self.assertTrue(problemas(monta + 'def b(d):\n    subprocess.run(["git", "commit"], cwd=d, env=env)\n'))
        self.assertTrue(problemas('def a():\n    env = sem_manutencao({})\n    env = {}\n'
                                  '    subprocess.run(["git", "init"], env=env)\n'))
        # derivado do montado vale; `self.env` do preparo da classe ou da classe-base do módulo vale
        self.assertEqual(problemas(monta.replace('env=env)', 'env={**env, "A": "1"})')), [])
        base = 'class Base:\n    def setUp(self):\n        self.env = sem_manutencao({})\n'
        usa = '    def test_x(self):\n        subprocess.run(["git", "init"], env=self.env)\n'
        self.assertEqual(problemas(base + 'class Filha(Base):\n' + usa), [])
        self.assertTrue(problemas(base + 'class Filha(Base):\n    def setUp(self):\n        self.env = {}\n' + usa))
        self.assertTrue(problemas('class Solta:\n' + usa))

    def test_guarda_falha_numa_copia_com_funcao_que_chama_git_sem_o_ambiente(self):
        """Cópia de um módulo real que monta `env` numa função; acrescenta outra função que chama git sem ele."""
        real = (AQUI / "test_portao_diff_proprio.py").read_text(encoding="utf-8")
        self.assertIn("env = sem_manutencao(", real)
        self.assertEqual(problemas(real), [])
        for corpo in ('    subprocess.run(["git", "commit", "-q"], cwd=d, env=env)\n',
                      '    env = {}\n    subprocess.run(["git", "commit", "-q"], cwd=d, env=env)\n'):
            copia = real + "\n\ndef outra(d):\n" + corpo
            with self.subTest(corpo=corpo):
                linha = len(copia.splitlines())
                self.assertEqual([a.split(":")[1] for a in problemas(copia)], [str(linha)])

    def test_excecao_do_repositorio_real_exige_que_ele_seja_o_repositorio_da_chamada(self):
        self.assertEqual(problemas('subprocess.run(["git", "ls-files"], cwd=RAIZ)\n'), [])
        self.assertTrue(problemas('subprocess.run(["git", "commit", "-F", str(RAIZ / "msg")], cwd=d)\n'))
        self.assertTrue(problemas('subprocess.run(["git", "-C", str(d), "commit"], cwd=RAIZ)\n'))
        self.assertTrue(problemas('subprocess.run(["git", "commit", "-C", str(RAIZ)], cwd=d)\n'))  # -C do commit

    def test_construtor_vale_por_devolver_o_ponto_unico_e_nao_pelo_nome(self):
        chama = 'subprocess.run(["git", "init"], env=ambiente_limpo())\n'
        self.assertTrue(problemas('def ambiente_limpo():\n    return {}\n' + chama))
        self.assertEqual(problemas('def ambiente_limpo():\n    return sem_manutencao({})\n' + chama), [])
        with tempfile.TemporaryDirectory() as d:
            for retorno, esperado in (("{}", False), ("sem_manutencao({})", True)):
                (Path(d) / "apoio.py").write_text(f"def ambiente_limpo():\n    return {retorno}\n", encoding="utf-8")
                with self.subTest(retorno=retorno):
                    self.assertEqual(problemas("from apoio import ambiente_limpo\n" + chama, pasta=Path(d)) == [],
                                     esperado)

    def test_modulos_de_apoio_tambem_sao_lidos(self):
        lidos = {m.name for m in modulos_lidos()}
        self.assertTrue({"ambiente_git.py", "guarda_git.py", "neutralidade.py"} <= lidos)
        for nome in sorted(lidos - {m.name for m in AQUI.glob("test_*.py")}):
            with self.subTest(modulo=nome):
                self.assertEqual(problemas((AQUI / nome).read_text(encoding="utf-8"), nome), [])
        for nome in EXCECOES:  # a exceção existe e chama git de fato; senão, sai da lista
            self.assertIn('["git"', (AQUI / nome).read_text(encoding="utf-8"), nome)
            self.assertNotIn(nome, lidos)

    def test_todo_repositorio_bare_recebe_a_configuracao_no_remoto(self):
        com_bare = 0
        for modulo in modulos_lidos():
            fonte = modulo.read_text(encoding="utf-8")
            com_bare += '"--bare"' in fonte
            with self.subTest(modulo=modulo.name):
                self.assertEqual(bare_sem_remoto(fonte, modulo.name), [])
        self.assertGreaterEqual(com_bare, 7, "a leitura deveria alcançar os módulos que criam repositório bare")
        self.assertTrue(bare_sem_remoto('def f():\n    git("init", "--bare", "r")\n'))


class RemotoSemManutencao(unittest.TestCase):
    """O push local roda o receive-pack sem as `GIT_CONFIG_*` do ambiente; o config do remoto é o que vale."""

    def git(self, *args, cwd):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        return subprocess.run(["git", *args], cwd=cwd, env=sem_manutencao(env), check=True, capture_output=True,
                              text=True, timeout=60)

    def test_config_chega_ao_receive_pack_so_pelo_remoto(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            repo = d / "repo"
            self.git("init", "-q", "-b", "main", str(repo), cwd=d)
            self.git("commit", "-q", "--allow-empty", "-m", "x", cwd=repo)
            vistos = {}
            for nome, preparar in (("sem", False), ("com", True)):
                remoto, saida = d / f"{nome}.git", d / f"{nome}.txt"
                self.git("init", "-q", "--bare", str(remoto), cwd=d)
                if preparar:
                    remoto_sem_manutencao(remoto)
                gancho = remoto / "hooks" / "post-receive"
                gancho.parent.mkdir(exist_ok=True)
                gancho.write_text("#!/bin/sh\nfor c in receive.autogc gc.auto maintenance.auto; do\n"
                                  f'  printf "%s=%s\\n" "$c" "$(git config --get "$c")" >> "{saida}"\n'
                                  f'done\nprintf "COUNT=%s\\n" "$GIT_CONFIG_COUNT" >> "{saida}"\n', encoding="utf-8")
                gancho.chmod(0o755)
                self.git("push", "-q", str(remoto), "main", cwd=repo)
                vistos[nome] = saida.read_text(encoding="utf-8").split()
            # o ambiente do push não chega ao remoto (por isso o ambiente sozinho não basta) ...
            self.assertEqual(vistos["sem"], ["receive.autogc=", "gc.auto=", "maintenance.auto=", "COUNT="])
            # ... e o config gravado por remoto_sem_manutencao chega
            self.assertEqual(vistos["com"], [f"{c}={v}" for c, v in (("receive.autogc", "false"), ("gc.auto", "0"),
                                                                      ("maintenance.auto", "false"))] + ["COUNT="])
            self.assertEqual(dict(CONFIGURACAO), {"receive.autogc": "false", "gc.auto": "0", "maintenance.auto": "false"})


class ModoDirigido(unittest.TestCase):
    """O `bin/forge-testes` roda `python3 -m unittest tests.<módulo>`: sem `tests/` no caminho, todo módulo carrega."""

    def test_todo_modulo_de_tests_carrega_como_tests_modulo(self):
        nomes = sorted(m.stem for m in AQUI.glob("*.py"))
        self.assertGreaterEqual(len(nomes), 15)
        # cada módulo carrega do zero: caminho e módulos de antes restaurados, para um não carregar pelo outro
        codigo = ("import importlib, sys\n"
                  "caminho, modulos = list(sys.path), set(sys.modules)\n"
                  "assert not any(p.rstrip('/').endswith('tests') for p in caminho), caminho\n"
                  "for n in sys.argv[1:]:\n"
                  "    importlib.import_module('tests.' + n)\n"
                  "    sys.path[:] = caminho\n"
                  "    for m in set(sys.modules) - modulos:\n"
                  "        del sys.modules[m]\n")
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, "-c", codigo, *nomes], cwd=RAIZ, env=env, capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
