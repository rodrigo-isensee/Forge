"""BP3 S2, volta única (v0478 E39.17): a tarefa do VS Code e a configuração do container são arquivos em vigor.

O VS Code executa `.vscode/tasks.json` ao abrir a pasta (tarefa `runOn: folderOpen`) e o container roda os comandos de
`.devcontainer/devcontainer.json` como root, os dois fora do sandbox do Claude Code. A1 e A2 do parecer de segurança
(docs/security/v0479-bp3-s2-container.md, sondas S1 e S2): nenhum agente os grava, por Write, Edit ou Bash.
A3 (E39.21): `.vscode/settings.json` muda o PATH e o shell da tarefa e também é protegido. O controle
mostra que a entrada é o arquivo exato, não a pasta inteira."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_hooks  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_hooks import Fixture  # noqa: E402

PROTEGIDOS = (".vscode/tasks.json", ".vscode/settings.json", ".devcontainer/devcontainer.json")
LIVRES = (".vscode/extensions.json", ".devcontainer/preparar-ambiente.sh")
PAPEIS = ("forge:dev", "forge:devops-engineer", "forge:tech-lead")


def entradas(alvo):
    """(forma, tool_name, tool_input) de cada jeito de gravar o `alvo`, relativo à raiz do projeto."""
    return (
        ("write", "Write", {"file_path": f"{{raiz}}/{alvo}", "content": "{}\n"}),
        ("edit", "Edit", {"file_path": f"{{raiz}}/{alvo}", "old_string": "{", "new_string": "{ "}),
        ("printf", "Bash", {"command": f"printf x > {alvo}"}),
        ("cp", "Bash", {"command": f"cp src/app.js {alvo}"}),
        ("tee", "Bash", {"command": f"echo x | tee {alvo}"}),
    )


def caso(alvo, papel, forma, ferramenta, entrada, codigo):
    dados = {
        "arquivos": {"src/app.js": "v1\n", **{a: "{}\n" for a in (*PROTEGIDOS, *LIVRES)}},
        "git": [{"branch": "feature/x"}],
        "entrada": {"tool_name": ferramenta, "tool_input": entrada, "agent_type": papel,
                    "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"},
        "esperado": {"codigo": codigo, **({"stderr": "R-CONFORMIDADE: arquivo em vigor"} if codigo == 2 else {})},
    }
    nome = f"vigor-{alvo.replace('/', '_')}-{papel.split(':')[1]}-{forma}"
    return (f"conformidade/{nome}", Fixture(Path("conformidade") / f"{nome}.json", dados))


class ArquivosQueOVsCodeExecuta(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    def test_write_edit_e_bash_no_arquivo_em_vigor_saem_2(self):
        casos = [caso(alvo, papel, *e, 2) for alvo in PROTEGIDOS for papel in PAPEIS for e in entradas(alvo)]
        self.assertEqual(len(casos), len(PROTEGIDOS) * len(PAPEIS) * 5)
        self.assertEqual(self.executar_em_lote(casos), len(casos))

    def test_vizinho_na_mesma_pasta_segue_gravavel(self):
        casos = [caso(alvo, "forge:dev", *e, 0) for alvo in LIVRES for e in entradas(alvo)]
        self.assertEqual(len(casos), len(LIVRES) * 5)
        self.assertEqual(self.executar_em_lote(casos), len(casos))


if __name__ == "__main__":
    unittest.main()
