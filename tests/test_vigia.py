"""AV3 etapa 1 (v0457 E2.1): a forma dos comandos críticos que o vigia mede por papel em `.forge/run/comandos.jsonl`.
Só mede: nada aqui passa a ser recusado. Os fixtures `tests/hooks/vigia/medida-*.json` cobrem o hook de ponta a ponta."""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "hooks"))
import vigia  # noqa: E402

POLITICA = json.loads((RAIZ / "hooks" / "conformidade.json").read_text(encoding="utf-8"))
PACOTES = POLITICA["pacotes"]


class FormaDoComando(unittest.TestCase):
    def medir(self, funcao, *args):
        """Exceção na medida é falha do teste, não erro: a medida não pode derrubar o vigia."""
        try:
            return funcao(*args)
        except Exception as erro:  # noqa: BLE001
            self.fail(f"a medida levantou {erro!r}")

    def test_formas_criticas(self):
        casos = {
            "git -C /x push --force origin a": ["git push --force"],
            "FOO=1 env git commit -m x && gh pr merge 12 --admin": ["git commit", "gh pr merge --admin"],
            "gh api repos/o/r -X PATCH": ["gh api"],
            "gh -R o/r release create v1": ["gh release create"],
            "npm ci; ls | grep a": ["npm ci"],
            "echo $(git push --all)": ["git push --all"],
            "/usr/bin/git push --no-verify=true": ["git push --no-verify"],
            "sudo apt-get install x": ["apt-get install"],
            "git push 'sem fim": ["git push"],
            "git --no-pager push": ["git push"],
            "git -C -c push": ["git push"],
        }
        for comando, esperado in casos.items():
            with self.subTest(comando=comando):
                self.assertEqual(self.medir(vigia.formas_criticas, comando, PACOTES), esperado)

    def test_comando_de_leitura_nao_conta(self):
        for comando in ("git status", "git log --oneline", "git -C commit status", "gh", "ls docs", "FOO=1", "npm test",
                        "pip3 list", "cat git"):
            with self.subTest(comando=comando):
                self.assertEqual(self.medir(vigia.formas_criticas, comando, PACOTES), [])

    def test_pacote_sem_verbos_na_politica_nao_conta(self):
        self.assertEqual(self.medir(vigia.formas_criticas, "npm install", {"npm": "malformado"}), [])

    def test_barrado_vem_do_resultado_da_mesma_chamada(self):
        linhas = [json.dumps({"message": {"content": [{"type": "tool_use", "id": i, "name": "Bash", "input": {"command": c}}]}})
                  for i, c in (("a", "git push"), ("b", "git merge x"))]
        linhas += [json.dumps({"message": {"content": [{"type": "tool_result", "tool_use_id": "a", "is_error": True,
                                                        "content": "R-MAIN: no"}]}}), "não é json"]
        linhas += [json.dumps(r) for r in ([], {"message": "x"}, {"message": {"content": 3}}, {"message": {"content": [3]}},
                                           {"message": {"content": [{"type": "tool_use", "name": "Bash", "input": "x"}]}})]
        linhas.append(json.dumps({"message": {"content": [{"type": "tool_use", "id": "c", "name": "Write",
                                                           "input": {"command": "git push"}}]}}))
        self.assertEqual(self.medir(vigia.comandos_criticos, linhas, PACOTES), [("git push", "R-MAIN"), ("git merge", None)])

    def test_papel_do_agente(self):
        self.assertEqual(vigia.papel_do_agente(POLITICA, "forge:qa-engineer"), "qa")
        self.assertEqual(vigia.papel_do_agente(POLITICA, ""), POLITICA["sem_agent_type"])
        self.assertEqual(vigia.papel_do_agente(POLITICA, "outro:tipo"), POLITICA["papel_padrao"])


if __name__ == "__main__":
    unittest.main()
