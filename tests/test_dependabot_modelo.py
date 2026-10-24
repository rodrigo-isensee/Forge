"""Lote N-TPL-a, M9: o modelo de dependabot.yml, o bloco por stack e as regras da skill ci-cd existem e dizem o que o modelo de ameaças exige."""
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(caminho):
    return (RAIZ / caminho).read_text(encoding="utf-8")


DEPENDABOT = "templates/projeto/.github/dependabot.yml"


def grupos(texto):
    """Os grupos de um dependabot.yml, lidos por expressão regular (a suíte só usa a biblioteca padrão): nome -> bloco."""
    achados = re.split(r"^ {6}([\w-]+):\n", texto.split("groups:", 1)[1], flags=re.M) if "groups:" in texto else [""]
    return dict(zip(achados[1::2], achados[2::2]))


class TestModeloDependabot(unittest.TestCase):
    def test_modelo_dependabot(self):
        texto = ler(DEPENDABOT)
        self.assertRegex(texto, r"(?m)^version: 2$")
        self.assertRegex(texto, r"(?m)^\s+target-branch: develop$")
        self.assertRegex(texto, r"(?m)^\s+open-pull-requests-limit: \d+$")
        self.assertRegex(texto, r"(?m)^\s+cooldown:$")
        todos = grupos(texto)
        self.assertGreaterEqual(len(todos), 2)
        majors = [n for n, b in todos.items() if re.search(r"update-types:\s*\[\s*\"?major\"?\s*\]", b)]
        self.assertEqual(len(majors), 1, "um grupo só de major")
        for nome, bloco in todos.items():
            tipos = re.search(r"update-types:\s*\[([^\]]*)\]", bloco)
            self.assertIsNotNone(tipos, nome)
            if nome not in majors:
                self.assertNotIn("major", tipos.group(1), nome)
        self.assertNotIn("@dependabot", texto)

    def test_modelo_dependabot_nunca_traz_o_que_o_modelo_de_ameacas_proibe(self):
        texto = ler(DEPENDABOT)
        for proibido in ["insecure-external-code-execution", "registries", "automerge", "auto-merge"]:
            self.assertNotIn(proibido, texto, proibido)
        self.assertNotRegex(texto, r"(?m)^\s+ignore:")
        self.assertIn("target-branch", texto)
        self.assertIn("branch padrão", texto)

    def test_modelo_dependabot_manda_acrescentar_o_ecossistema_da_stack(self):
        self.assertIn("stacks/<stack>/pronto.md", ler(DEPENDABOT))

    def test_toda_stack_traz_o_ecossistema_do_dependabot(self):
        pronto = sorted(RAIZ.glob("stacks/*/pronto.md"))
        self.assertGreaterEqual(len(pronto), 1)
        for arq in pronto:
            texto = arq.read_text(encoding="utf-8")
            self.assertIn("\n## CI\n", texto, arq.parent.name)
            ci = texto.split("\n## CI\n", 1)[1].split("\n## ", 1)[0]
            self.assertIn("package-ecosystem", ci, arq.parent.name)
            self.assertIn("cooldown", ci, arq.parent.name)
            self.assertIn("maiores", ci, arq.parent.name)
            self.assertRegex(ci, r"update-types:\s*\[\s*\"?major\"?\s*\]", arq.parent.name)
            self.assertRegex(ci, r"ignore: \[\]", arq.parent.name)

    def test_ci_cd_avisa_branch_padrao_e_pr_do_robo(self):
        texto = ler("skills/ci-cd/SKILL.md").split("## Tempo e dependências", 1)[1].split("\n## ", 1)[0]
        for trecho in [
            "templates/projeto/.github/dependabot.yml",
            "só vale na branch padrão",
            "alerta de segurança abre contra a branch padrão",
            "Não edite o PR do robô",
            "nada de `@dependabot ignore`",
            "cartão de migração",
        ]:
            self.assertIn(trecho, texto)


if __name__ == "__main__":
    unittest.main()
