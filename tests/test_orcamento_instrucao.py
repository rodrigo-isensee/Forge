"""Orçamento de instrução (P11, 0.43.1 H): o que cada agente carrega não passa do teto de docs/regras/orcamento.json.

O que o agente carrega: agents/<x>.md, as skills obrigatórias (as do `skills:` do cabeçalho e as que o texto manda ler com
"leia `${CLAUDE_PLUGIN_ROOT}/skills/<nome>/SKILL.md`") e os docs/regras/R-*.md citados pelo agente ou por essas skills. Mede-se em
caracteres (o arquivo do agente e o total) e em marcadores normativos (nunca, sempre, só, proibido, obrigatório, reprova). O alvo é a
meta documentada; só o teto reprova."""
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ORCAMENTO = RAIZ / "docs" / "regras" / "orcamento.json"
MARCADOR = re.compile(r"(?<!\w)(nunca|sempre|só|proibid[oa]s?|obrigatóri[oa]s?|reprovam?)(?!\w)", re.I)
SKILL_LIDA = re.compile(r"[Ll]eia `\$\{CLAUDE_PLUGIN_ROOT\}/skills/([a-z0-9-]+)/SKILL\.md")
ID_DE_REGRA = re.compile(r"\bR-[A-Z]+\b")
DIMENSOES = ("agente_caracteres", "total_caracteres", "marcadores")


def skills_obrigatorias(texto):
    """As do `skills:` do cabeçalho mais as que o texto manda ler."""
    cabecalho = texto.split("\n---", 1)[0] if texto.startswith("---") else ""
    achou = re.search(r"^skills:\s*(.+)$", cabecalho, re.M)
    nomes = {s.strip() for s in achou.group(1).split(",") if s.strip()} if achou else set()
    return sorted(nomes | set(SKILL_LIDA.findall(texto)))


def medir(raiz, agente):
    """{dimensão: valor, "skills": [...], "regras": [...]} do que o agente carrega na árvore `raiz`."""
    texto = (raiz / "agents" / f"{agente}.md").read_text(encoding="utf-8")
    skills = skills_obrigatorias(texto)
    textos = [texto] + [(raiz / "skills" / s / "SKILL.md").read_text(encoding="utf-8") for s in skills]
    ids = sorted({i for t in textos for i in ID_DE_REGRA.findall(t)})
    regras = [i for i in ids if (raiz / "docs" / "regras" / f"{i}.md").is_file()]
    todos = textos + [(raiz / "docs" / "regras" / f"{i}.md").read_text(encoding="utf-8") for i in regras]
    return {"agente_caracteres": len(texto), "total_caracteres": sum(len(t) for t in todos),
            "marcadores": sum(len(MARCADOR.findall(t)) for t in todos), "skills": skills, "regras": regras}


def estouros(raiz, orcamento):
    """Uma mensagem por dimensão acima do teto, e por agente sem orçamento ou orçamento sem agente."""
    agentes = sorted(p.stem for p in (raiz / "agents").glob("*.md"))
    erros = [f"{a}: sem orçamento em docs/regras/orcamento.json" for a in agentes if a not in orcamento["agentes"]]
    erros += [f"{a}: orçamento de agente que não existe" for a in orcamento["agentes"] if a not in agentes]
    for agente in agentes:
        if agente not in orcamento["agentes"]:
            continue
        medida, teto = medir(raiz, agente), orcamento["agentes"][agente]["teto"]
        erros += [f"{agente}: {d} = {medida[d]} passa do teto {teto[d]} (reduza o texto; subir o teto é afrouxar)"
                  for d in DIMENSOES if medida[d] > teto[d]]
    return erros


class Orcamento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orcamento = json.loads(ORCAMENTO.read_text(encoding="utf-8"))

    def test_nenhum_agente_passa_do_teto(self):
        self.assertEqual(estouros(RAIZ, self.orcamento), [])

    def test_todo_teto_e_alvo_tem_as_tres_dimensoes_e_o_alvo_nao_passa_do_teto(self):
        for agente, valores in self.orcamento["agentes"].items():
            with self.subTest(agente=agente):
                self.assertEqual(sorted(valores["teto"]), sorted(DIMENSOES))
                for d in DIMENSOES:
                    self.assertIsInstance(valores["teto"][d], int)
                if "alvo" in valores:
                    self.assertEqual(sorted(valores["alvo"]), sorted(DIMENSOES))
                    for d in DIMENSOES:
                        self.assertLessEqual(valores["alvo"][d], valores["teto"][d])

    def test_jarvis_e_conferente_tem_alvo_bem_menor(self):
        for agente in ("jarvis", "conferente"):
            with self.subTest(agente=agente):
                alvo, teto = self.orcamento["agentes"][agente]["alvo"], self.orcamento["agentes"][agente]["teto"]
                self.assertLessEqual(alvo["total_caracteres"], teto["total_caracteres"] // 2)

    def test_orcamento_tem_revisao_e_medida(self):
        self.assertRegex(self.orcamento["revisar_em"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(self.orcamento["medida"], r"\d")

    def test_jarvis_carrega_as_skills_que_manda_ler(self):
        medida = medir(RAIZ, "jarvis")
        self.assertIn("briefs-e-conferencia", medida["skills"])
        self.assertIn("R-BRIEF", medida["regras"])


class Medida(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-orcamento-"))
        for pasta in ("agents", "skills/s1", "skills/s2", "docs/regras"):
            (self.tmp / pasta).mkdir(parents=True)
        (self.tmp / "agents" / "a.md").write_text(
            "---\nname: a\nskills: s1\n---\nNunca faça X; sempre `R-UM`. Só isso (só).\n"
            "Antes, leia `${CLAUDE_PLUGIN_ROOT}/skills/s2/SKILL.md`. Sozinho, nunca-mais e somente não contam.\n", encoding="utf-8")
        (self.tmp / "skills" / "s1" / "SKILL.md").write_text("Proibido Y. Obrigatória a prova. `R-DOIS` e `R-SEM-ARQUIVO`.\n",
                                                             encoding="utf-8")
        (self.tmp / "skills" / "s2" / "SKILL.md").write_text("O conferente reprova; eles reprovam.\n", encoding="utf-8")
        (self.tmp / "skills" / "s3").mkdir()
        (self.tmp / "skills" / "s3" / "SKILL.md").write_text("nunca nunca nunca\n", encoding="utf-8")  # não declarada: fora
        (self.tmp / "docs" / "regras" / "R-UM.md").write_text("Sempre.\n", encoding="utf-8")
        (self.tmp / "docs" / "regras" / "R-DOIS.md").write_text("Obrigatório.\n", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_medida_soma_agente_skills_obrigatorias_e_regras_citadas(self):
        medida = medir(self.tmp, "a")
        self.assertEqual(medida["skills"], ["s1", "s2"])
        self.assertEqual(medida["regras"], ["R-DOIS", "R-UM"])
        # agente: Nunca, sempre, Só, só, nunca(-mais conta: o hífen não é letra) = 5; s1: Proibido, Obrigatória = 2;
        # s2: reprova, reprovam = 2; R-UM: Sempre = 1; R-DOIS: Obrigatório = 1
        self.assertEqual(medida["marcadores"], 11)
        textos = [self.tmp / "agents" / "a.md", self.tmp / "skills" / "s1" / "SKILL.md", self.tmp / "skills" / "s2" / "SKILL.md",
                  self.tmp / "docs" / "regras" / "R-UM.md", self.tmp / "docs" / "regras" / "R-DOIS.md"]
        self.assertEqual(medida["total_caracteres"], sum(len(p.read_text(encoding="utf-8")) for p in textos))

    def test_passar_do_teto_reprova_e_agente_sem_orcamento_tambem(self):
        medida = medir(self.tmp, "a")
        justo = {d: medida[d] for d in DIMENSOES}
        self.assertEqual(estouros(self.tmp, {"agentes": {"a": {"teto": justo}}}), [])
        apertado = dict(justo, marcadores=justo["marcadores"] - 1)
        erros = estouros(self.tmp, {"agentes": {"a": {"teto": apertado}}})
        self.assertEqual(len(erros), 1)
        self.assertIn("a: marcadores = 11 passa do teto 10", erros[0])
        self.assertEqual(estouros(self.tmp, {"agentes": {"b": {"teto": justo}}}),
                         ["a: sem orçamento em docs/regras/orcamento.json", "b: orçamento de agente que não existe"])


if __name__ == "__main__":
    unittest.main()
