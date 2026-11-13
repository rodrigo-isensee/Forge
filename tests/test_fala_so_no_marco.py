"""FALA-SO-NO-MARCO (diretriz 24, MP1311 E2.16): o Jarvis conta o andamento só nos marcos e todo dono é orientado a ligar o
modo foco (Focus view) do VSCode. Sem chave inventada: o modelo de projeto não grava configuração de foco."""
import subprocess
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class FalaSoNoMarco(unittest.TestCase):
    def test_jarvis_conta_o_andamento_so_nos_marcos(self):
        t = ler("agents/jarvis.md")
        self.assertNotIn("ao fim de cada etapa: estado", t)
        for trecho in ("só ao fim de cada marco", "o dono precisa decidir ou agir", "muda prazo ou risco", "um marco fecha",
                       "no máximo 30 minutos", "recibo e perguntas sempre completos", "Sem nome de branch nem de pasta"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, t)

    def test_modo_iniciante_tem_a_mesma_regra_em_linguagem_simples(self):
        t = ler("skills/modo-iniciante/SKILL.md")
        self.assertNotIn("Ao fim de cada etapa, resuma", t)
        for trecho in ("Fale só nos marcos", "a cada 30 minutos", "se nada mudou, não escreva", "Focus view"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, t)

    def test_modo_foco_orientado_no_init_na_skill_e_no_readme(self):
        for rel in ("bin/forge-init", "skills/novo-projeto/SKILL.md", "README.md"):
            t = ler(rel)
            with self.subTest(arquivo=rel):
                self.assertIn("Focus view", t)
                self.assertIn("Ctrl+Alt+F", t)

    def test_forge_init_imprime_a_orientacao_do_modo_foco(self):
        with __import__("tempfile").TemporaryDirectory() as d:
            r = subprocess.run(["bash", str(RAIZ / "bin" / "forge-init"), d], capture_output=True, text=True,
                               env={"PATH": "/usr/bin:/bin", "HOME": d}, cwd=d)
        self.assertIn("Focus view", r.stdout + r.stderr)

    def test_modelo_de_projeto_nao_inventa_chave_de_foco(self):
        self.assertFalse((RAIZ / "templates" / "projeto" / ".vscode").exists())


if __name__ == "__main__":
    unittest.main()
