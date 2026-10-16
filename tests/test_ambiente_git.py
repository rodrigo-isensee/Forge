"""Garante que nenhum teste roda `git` num repositório temporário com a manutenção automática do git ligada.

`ambiente_git.sem_manutencao` é o ponto único. Aqui: (1) ele junta as chaves em vez de sobrescrevê-las; (2) uma leitura
estática (ast) de todos os `tests/test_*.py` falha se uma chamada direta a `git` (subprocess) não receber um ambiente
montado por ele; (3) os módulos de tests/ carregam também no modo dirigido (`python3 -m unittest
tests.<módulo>`). Origem: erros de tearDown por `maintenance.lock` só em worktree (S-9)."""
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
CONSTRUTORES = {"sem_manutencao", "ambiente_limpo"}   # funções que devolvem o ambiente sem manutenção
NOMES_DE_AMBIENTE = {"env", "ambiente", "AMBIENTE", "self.env"}
# Exceção explícita e única: chamada que mexe no repositório real do Forge (`RAIZ`), só para ler (rev-parse, diff,
# ls-files). Não cria nem faz commit em repositório temporário, então não dispara a manutenção.
EXCECAO_REPOSITORIO_REAL = "RAIZ"
# Fora da leitura: tests/guarda_git.py só lê o `.git/config` comum do repositório real; tests/catraca.py é protegido.


def _chama(no, nomes):
    return any(isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", None)) in nomes
               for n in ast.walk(no))


def _eh_git(chamada):
    f = chamada.func
    return (isinstance(f, ast.Attribute) and f.attr in CHAMADAS and getattr(f.value, "id", "") == "subprocess"
            and chamada.args and isinstance(chamada.args[0], ast.List) and chamada.args[0].elts
            and isinstance(chamada.args[0].elts[0], ast.Constant) and chamada.args[0].elts[0].value == "git")


def _escopo(no, pais, tipos):
    while no in pais:
        no = pais[no]
        if isinstance(no, tipos):
            return no
    return None


def problemas(fonte, nome="<modulo>"):
    """Lista de textos `arquivo:linha: problema` do código `fonte`; vazia se tudo usa o ponto único."""
    arvore = ast.parse(fonte)
    pais = {filho: pai for pai in ast.walk(arvore) for filho in ast.iter_child_nodes(pai)}
    achados = []
    for no in ast.walk(arvore):
        if not (isinstance(no, ast.Call) and _eh_git(no)) or EXCECAO_REPOSITORIO_REAL in ast.unparse(no):
            continue
        env = next((k.value for k in no.keywords if k.arg == "env"), None)
        if env is None:
            achados.append(f"{nome}:{no.lineno}: git sem `env=` do ponto único (ambiente_git.sem_manutencao)")
        elif not _chama(env, CONSTRUTORES):
            texto = ast.unparse(env)
            # `env`/`self.env`/`AMBIENTE`: tem de ser montado com o ponto único na função, na classe ou no módulo
            # (`self.env` pode vir de uma classe-base do módulo: procura no módulo todo)
            escopos = [_escopo(no, pais, (ast.FunctionDef, ast.Lambda)) or arvore, arvore]
            montado = texto in NOMES_DE_AMBIENTE and any(
                isinstance(a, ast.Assign) and any(ast.unparse(alvo) == texto for alvo in a.targets)
                and _chama(a.value, CONSTRUTORES) for escopo in escopos for a in ast.walk(escopo))
            if not montado:
                achados.append(f"{nome}:{no.lineno}: `{texto}` não é montado com sem_manutencao")
    return achados


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
