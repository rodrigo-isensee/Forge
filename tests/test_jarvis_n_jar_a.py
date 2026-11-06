"""N-JAR-A (0.37 E5): D2, D3, Q1 e Q2 do dono nas skills do Jarvis; o núcleo cita o lote de 3 sem ganhar linha."""
import json
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TETO = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))["limite_linhas"]["agente"]
PARALELO = "skills/trabalho-em-paralelo/SKILL.md"
DONO = "skills/falar-com-o-dono/SKILL.md"
FRASES = (
    (PARALELO, "entra na `develop` na hora, sem esperar o lote nem a versão"),
    (PARALELO, "até 3 tópicos pequenos sem arquivo em comum podem ir num lote, com as mesmas regras do \"Lote por arquivo\""),
    (PARALELO, "na pausa por limite de uso só seguem conferências e integradores; nada novo é disparado"),
    (DONO, "o time segue com a escolha provisória recomendada, registrada como `suposição` com `muda com` e `custo de reverter`"),
    (DONO, "se o dono trocar 2 de 5 escolhas provisórias, a prática volta a esperar"),
    (DONO, "nunca cobre aceite de risco, gasto (`R-CUSTO`), rótulo `afrouxa-regra`, merge na main nem ato destrutivo"),
)


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


class TextoDoNJarA(unittest.TestCase):
    def test_as_quatro_decisoes_existem_nas_skills(self):
        self.assertEqual(len(FRASES), 6)
        for rel, frase in FRASES:
            with self.subTest(arquivo=rel, frase=frase):
                self.assertIn(frase, ler(rel))

    def test_o_jarvis_cita_o_lote_de_3_e_nao_passa_do_teto(self):
        jarvis = ler("agents/jarvis.md")
        self.assertIn("lote por arquivo e lote de até 3 tópicos sem arquivo em comum", jarvis)
        self.assertLessEqual(len(jarvis.splitlines()), TETO)

