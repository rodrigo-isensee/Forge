"""HOOK-ERRO-LIBERA (v047 E3.7; modelo de ameaças v047-v2, seção 1): o erro interno e o prazo vencido do `conformidade`
recusam a escrita protegida pelo marcador montado da política (C2 a C5), sem `.expanduser()` de `Path` nos hooks (C1), com
`python3 -s -E` em todo o hooks.json (C6) e com o R-BRIEF do `agentes` antes da leitura do estado (C7).

O erro e o prazo são forçados no processo do hook (chave `forcar` dos fixtures, `tests/test_hooks.py`), nunca por variável de
ambiente. Os casos de abuso fixos são os fixtures `errointerno-*` de tests/hooks/conformidade/ e tests/hooks/agentes/; o E3 é
gerado aqui, do JSON real da política: entrada nova já nasce coberta."""
import json
import re
import subprocess
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import RAIZ, ambiente_limpo, minimo  # noqa: E402
import test_hooks  # noqa: E402
from test_hooks import FIXTURES, HOOKS, Fixture, modulos_dos_hooks  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

POLITICA = HOOKS / "conformidade.json"
ERRO_FORCADO = {"onde": "Guarda.bash", "como": "erro"}


def bash(comando, papel="forge:tech-lead"):
    return {"tool_name": "Bash", "tool_input": {"command": comando}, "agent_type": papel,
            "hook_event_name": "PreToolUse", "tool_use_id": "toolu_1"}


class HookErroLibera(unittest.TestCase):
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def lote(self, fixtures):
        casos = [(f"{f.hook}/{f.caminho.stem}", f) for f in fixtures]
        self.assertEqual(self.executar_em_lote(casos), len(casos), "todo caso é verificado")

    def test_fixtures_do_pedido(self):
        """E1, E2, E4 a E6, E8 e os legítimos com erro forçado: os fixtures `errointerno-*` dos dois hooks."""
        self.lote(minimo([Fixture(p) for p in sorted(FIXTURES.glob("*/errointerno-*.json"))], 38, "fixtures errointerno-*"))

    def test_fixtures_do_prazo(self):
        """E4 e o legítimo do prazo (C5): só os fixtures de prazo forçado."""
        self.lote(minimo([Fixture(p) for p in sorted(FIXTURES.glob("conformidade/errointerno-prazo-*.json"))], 7, "fixtures de prazo"))

    def test_fixtures_do_agentes(self):
        """E8 e o estado corrompido (C7): só os fixtures do `agentes`."""
        self.lote(minimo([Fixture(p) for p in sorted(FIXTURES.glob("agentes/errointerno-*.json"))], 8, "fixtures do agentes"))

    def test_cada_entrada_da_politica_com_erro_forcado_recusa(self):
        """E3 (C2): para cada entrada de `caminhos` do JSON real, `cp x <entrada>` com erro forçado em `Guarda.bash` recusa."""
        entradas = minimo([e["caminho"] for e in json.loads(POLITICA.read_text(encoding="utf-8"))["caminhos"]], 48,
                          "entradas de caminhos na política")
        self.lote([Fixture(FIXTURES / "conformidade" / f"politica-{i}.json", {
            "descricao": f"HOOK-ERRO-LIBERA (E3): {c}", "forcar": ERRO_FORCADO, "entrada": bash(f"cp x {c}"),
            "esperado": {"codigo": 2, "stderr": "erro interno do hook conformidade", "erros_log": "erro forcado"}})
            for i, c in enumerate(entradas)])

    def test_nenhum_expanduser_de_path_nos_hooks(self):
        """C1: o `Path.expanduser()` lança `RuntimeError` com `~usuario` que não existe; só `expandir_home` expande o `~`."""
        fontes = minimo(sorted(HOOKS.glob("*.py")), 8, "scripts em hooks/")
        achados = [f"{p.name}:{n}" for p in fontes for n, linha in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
                   if re.search(r"\.expanduser\(\)", linha)]
        self.assertEqual(achados, [])
        _comum, _, _ = modulos_dos_hooks()
        self.assertEqual(_comum.expandir_home("~zzq-nao-existe/x"), "~zzq-nao-existe/x")
        self.assertEqual(_comum.expandir_home("docs/x"), "docs/x")

    def test_politica_ilegivel_ou_sem_caminhos_marca_tudo(self):
        """C2: sem os termos da política, qualquer linha conta como marcada para a falha fechada."""
        _, conformidade, _ = modulos_dos_hooks()
        for pol in ({}, [], {"caminhos": []}, {"caminhos": ["x"]}, {"caminhos": [{"caminho": "/"}]}):
            with self.subTest(pol=pol):
                self.assertIsNone(conformidade.termos_da_politica(pol))
        hook = types.SimpleNamespace(entrada={"tool_name": "Bash"})
        for arquivo in (RAIZ / "nao-existe.json", HOOKS / "hooks.json"):
            with self.subTest(arquivo=arquivo.name):
                marcador = conformidade.MarcadorDaPolitica(conformidade.CRITICO, arquivo)
                self.assertTrue(marcador.marca(hook, ["git status"]))
        marcador = conformidade.MarcadorDaPolitica(conformidade.CRITICO, POLITICA)
        self.assertFalse(marcador.marca(hook, ["git status"]))

    def test_write_fora_da_raiz_em_caminho_da_politica_marca(self):
        """C4: no Write, o caminho resolvido dentro da raiz ou casando a política (`~/.claude.json`, fora da raiz) marca;
        fora das duas, não. Sem raiz declarada, a raiz é a pasta corrente; caminho vazio marca."""
        _, conformidade, _ = modulos_dos_hooks()
        marcador = conformidade.MarcadorDaPolitica(conformidade.CRITICO, POLITICA)
        tmp = self._pasta_temporaria()
        hook = types.SimpleNamespace(entrada={"tool_name": "Write"}, cwd=lambda: tmp)
        raiz = tmp / "raiz"
        with mock.patch.object(conformidade, "raiz_declarada", return_value=raiz):
            self.assertTrue(marcador.arquivo_marcado(hook, str(Path.home() / ".claude.json"), marcador.termos()))
            self.assertTrue(marcador.arquivo_marcado(hook, str(raiz / "src" / "app.js"), marcador.termos()))
            self.assertFalse(marcador.arquivo_marcado(hook, "/nao-existe-forge/x.md", marcador.termos()))
            self.assertFalse(marcador.arquivo_marcado(hook, "x.md", marcador.termos()), "na pasta corrente, fora da raiz")
            self.assertTrue(marcador.arquivo_marcado(hook, "", marcador.termos()), "caminho vazio marca")
        with mock.patch.object(conformidade, "raiz_declarada", return_value=None):
            self.assertTrue(marcador.arquivo_marcado(hook, "x.md", marcador.termos()), "sem raiz: a pasta corrente")

    def test_marcador_que_responde_decide(self):
        """O `marcado` usa a resposta do marcador da política (`marca`), não a busca do texto."""
        _comum, _, _ = modulos_dos_hooks()
        for resposta in (False, True):
            with self.subTest(resposta=resposta):
                hook = _comum.Hook("conformidade")
                hook.entrada = {"tool_name": "Bash", "tool_input": {"command": "git push --force"}}
                self.assertIs(_comum.marcado(hook, types.SimpleNamespace(marca=lambda *_a, r=resposta: r), ""), resposta)

    def test_catraca_compara_o_script_sem_as_opcoes_do_interpretador(self):
        """C6: `-s -E` antes do script não conta como hook removido; trocar o script conta."""
        import catraca

        def config(*args):
            return json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"command": "python3", "args": list(args)}]}]}})
        antes = catraca.chaves_de_hooks(config("${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py"))
        self.assertEqual(antes - catraca.chaves_de_hooks(config("-s", "-E", "${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py")), set())
        self.assertTrue(antes - catraca.chaves_de_hooks(config("-s", "-E", "${CLAUDE_PLUGIN_ROOT}/hooks/outro.py")))

    def test_erro_do_marcador_marca(self):
        """O erro do próprio marcador (qualquer exceção, não só `RuntimeError`) conta como marcado: a falha fecha."""
        _comum, _, _ = modulos_dos_hooks()
        for erro in (ValueError, KeyError, RuntimeError):
            with self.subTest(erro=erro.__name__):
                hook = _comum.Hook("conformidade")
                hook.entrada = {"tool_name": "Bash", "tool_input": {"command": "git status"}}
                def marca(*_args, erro=erro):
                    raise erro("x")
                self.assertTrue(_comum.marcado(hook, types.SimpleNamespace(marca=marca), ""))

    def test_usercustomize_e_pythonpath_nao_desligam_os_hooks(self):
        """E7 (C6): `usercustomize.py` no site do usuário e `sitecustomize.py` no PYTHONPATH que saem com 0 (`os._exit`; o
        `sys.exit` no site é erro fatal, código 1, que o Claude Code também libera) não desligam o hook rodado pela linha do
        hooks.json (`cp x .git/config` segue recusado); sem as opções, o mesmo ambiente libera."""
        d = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        args = minimo([h["args"] for g in d["hooks"]["PreToolUse"] for h in g["hooks"]
                       if h["args"][-1].endswith("/conformidade.py")], 1, "conformidade no hooks.json")[0]
        tmp = self._pasta_temporaria()
        raiz, entrada = Fixture(FIXTURES / "conformidade" / "e7.json", {"entrada": bash("cp x .git/config")}).montar(tmp, 0)
        env = ambiente_limpo()
        env.pop("FORGE_GUARDA_ABERTA", None)
        env.update(HOME=str(tmp / "home"), CLAUDE_PROJECT_DIR=str(raiz), PYTHONPATH=str(tmp / "pp"))
        site = subprocess.run([sys.executable, "-I", "-c", "import site; print(site.getusersitepackages())"], env=env,
                              capture_output=True, text=True, check=True).stdout.strip()
        for pasta, nome in ((Path(site), "usercustomize.py"), (tmp / "pp", "sitecustomize.py")):
            with self.subTest(nome=nome):
                pasta.mkdir(parents=True, exist_ok=True)
                (pasta / nome).write_text("import os\nos._exit(0)\n", encoding="utf-8")
                comando = [sys.executable, *(a.replace("${CLAUDE_PLUGIN_ROOT}", str(RAIZ)) for a in args)]
                rodar = lambda c: subprocess.run(c, input=json.dumps(entrada), cwd=raiz, env=env, capture_output=True,  # noqa: E731
                                                 text=True, timeout=120)
                self.assertEqual(rodar([sys.executable, comando[-1]]).returncode, 0, "controle: o arquivo desliga o hook")
                r = rodar(comando)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn(".git/config", r.stderr)
                (pasta / nome).unlink()


if __name__ == "__main__":
    unittest.main()
