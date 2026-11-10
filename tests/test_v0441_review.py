"""Review da 0.44.1: os bloqueantes B1 (tipos só de leitura no papel só de leitura) e os médios S2/S8 (gravação do `forge-check`
só na sessão principal)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_hooks import montar_proc, rodar as rodar_hook  # noqa: E402  (só funções)
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)


class Projeto(unittest.TestCase):
    def setUp(self):
        self.projeto = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.projeto, True)
        subprocess.run(["git", "init", "-q"], cwd=self.projeto, check=True, env=sem_manutencao(dict(os.environ, HOME=str(self.projeto))))
        (self.projeto / ".forge").mkdir()
        (self.projeto / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        (self.projeto / "x.txt").write_text("a\n", encoding="utf-8")
        self.proc = montar_proc(self.projeto, {"loadavg": "0.1 0.1 0.1", "mem_gb": 8})

    def hook(self, tipo, ferramenta, entrada):
        dados = {"hook_event_name": "PreToolUse", "tool_name": ferramenta, "session_id": "s", "cwd": str(self.projeto),
                 "tool_input": entrada}
        if tipo:
            dados["agent_type"] = tipo
        return rodar_hook("conformidade", dados, self.projeto, self.proc, {"FORGE_NPROC": "8"})


class TiposSoDeLeitura(Projeto):
    """B1: Explore, Plan, claude-code-guide, web-fetch e o `conferente` sem prefixo não escrevem (antes caíam no `dev`)."""

    TIPOS = ("Explore", "Plan", "claude-code-guide", "web-fetch", "conferente")

    def test_nao_escrevem_por_bash_nem_por_ferramenta(self):
        for tipo in self.TIPOS:
            for comando in ("sed -i s/a/b/ x.txt", "echo b > x.txt", "cp x.txt y.txt"):
                with self.subTest(tipo=tipo, comando=comando):
                    self.assertEqual(self.hook(tipo, "Bash", {"command": comando}).returncode, 2)
            for ferramenta, entrada in (("Write", {"file_path": str(self.projeto / "y.txt"), "content": "b"}),
                                        ("Edit", {"file_path": str(self.projeto / "x.txt"), "old_string": "a", "new_string": "b"})):
                with self.subTest(tipo=tipo, ferramenta=ferramenta):
                    self.assertEqual(self.hook(tipo, ferramenta, entrada).returncode, 2)

    def test_leem(self):
        for tipo in self.TIPOS:
            with self.subTest(tipo=tipo):
                self.assertEqual(self.hook(tipo, "Bash", {"command": "grep -n a x.txt"}).returncode, 0)

    def test_dev_segue_escrevendo(self):
        self.assertEqual(self.hook("forge:node-backend", "Bash", {"command": "sed -i s/a/b/ x.txt"}).returncode, 0)


class GravacaoDoForgeCheckSoNaSessaoPrincipal(Projeto):
    """S2 e S8: `pedido fala --gravar` e `recado --para` gravam no pedido e na caixa de recados: só a sessão principal (jarvis)."""

    LINHAS = ("forge-check pedido fala --gravar --pedido p --texto x", "forge-check recado --para . --texto x", "forge-check recado --p /tmp/outra --texto x",
              "forge-check pedido fala --g --pedido p --texto x", "forge-check pausa --gravar --retoma-em 10:00 --onde x")

    def test_agente_nao_grava(self):
        for tipo in ("forge:node-backend", "forge:tech-lead", "forge:conferente"):
            for linha in self.LINHAS:
                with self.subTest(tipo=tipo, linha=linha):
                    self.assertEqual(self.hook(tipo, "Bash", {"command": linha}).returncode, 2)

    def test_agente_le(self):
        for linha in ("forge-check pedido fala --ler --pedido p", "forge-check recado --confirmar", "forge-check pedido fala --le --pedido p",
                      "forge-check recado --conf x.md",
                      "forge-check pausa --retomar"):
            with self.subTest(linha=linha):
                self.assertEqual(self.hook("forge:node-backend", "Bash", {"command": linha}).returncode, 0)

    def test_sessao_principal_grava(self):
        for linha in self.LINHAS:
            with self.subTest(linha=linha):
                self.assertEqual(self.hook(None, "Bash", {"command": linha}).returncode, 0)


if __name__ == "__main__":
    unittest.main()
