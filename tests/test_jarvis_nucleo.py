"""L51 (AQ-8): o Jarvis em núcleo curto. O texto saiu de `agents/jarvis.md` para skills lidas no passo; nenhum invariante
sumiu (T-51a): cada trecho que o `tests/config.json` exigia do Jarvis na base b2580c6 segue exigido, no Jarvis ou na skill
para onde foi, e o texto de cada um existe lá; o núcleo manda ler cada skill nova."""
import json
import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))
ANTES = json.loads((RAIZ / "tests" / "fixtures" / "jarvis-invariantes-b2580c6.json").read_text(encoding="utf-8"))
JARVIS = "agents/jarvis.md"
SKILLS_NOVAS = ("briefs-e-conferencia", "trabalho-em-paralelo", "falar-com-o-dono")
# 0.43.1 (decisões do dono de 2026-11-08, "Faça tudo"): o brief é selado pela ferramenta, a entrega é conferida por ela e as
# perguntas ao dono vão em lote. Estes trechos descreviam a conferência manual pelo agente conferente (mensagem, hash, Base-sha,
# passada única, autoconferência) e a pergunta uma por vez: saem por mudança de processo, não por afrouxamento. O que eles
# protegiam passou para a ferramenta (`forge-check brief selar`, `forge-check entrega`) e para R-BRIEF, R-PROVA e R-DECISAO.
RETIRADOS_0431 = frozenset({
    "lista \\*\\*todos os achados\\*\\* de uma vez; corrija todos", "Autoconferência fixa do brief", "Brief-sha256",
    "nunca a própria branch", "ele não vê o relatório", "uma pergunta por vez", "`<<<BRIEF`", "`Base-sha:`",
    "`Arquivo:` \\(o caminho do brief", "linhas>=N",
})
ORCAMENTO_0431 = 37_511  # metade de jarvis.md + docs/regras/*.md na base da 0.43 (75.022 caracteres), decisão 11 do dono


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def arquivos_do_nucleo():
    return [JARVIS] + [f"skills/{nome}/SKILL.md" for nome in SKILLS_NOVAS]


class NucleoCurtoDoJarvis(unittest.TestCase):
    def test_todo_invariante_do_jarvis_existe_no_jarvis_ou_na_skill_nova(self):
        self.assertGreaterEqual(len(ANTES), 73)
        self.assertEqual(len(RETIRADOS_0431 & set(ANTES)), len(RETIRADOS_0431), "retirado que não era invariante")
        exigidos = {t: [] for t in ANTES if t not in RETIRADOS_0431}
        for rel in arquivos_do_nucleo():
            for t in CONFIG["invariantes"].get(rel, []):
                if t in exigidos:
                    exigidos[t].append(rel)
        for trecho, onde in exigidos.items():
            with self.subTest(trecho=trecho):
                self.assertTrue(onde, "o trecho deixou de ser exigido")
                self.assertTrue(any(re.search(trecho, ler(rel), re.S) for rel in onde), "o texto não existe no arquivo exigido")

    def test_o_nucleo_manda_ler_cada_skill_no_passo_dela(self):
        nucleo = ler(JARVIS)
        for nome in SKILLS_NOVAS:
            with self.subTest(skill=nome):
                self.assertIn(f"skills/{nome}/SKILL.md", nucleo)
                self.assertIn(f"skills/{nome}/SKILL\\.md", CONFIG["invariantes"][JARVIS])  # o ponteiro também é invariante

    def test_o_nucleo_ficou_curto_e_as_skills_tem_o_texto_que_saiu(self):
        self.assertLess(len(ler(JARVIS)), 24000)  # 29.092 bytes na base
        for nome in SKILLS_NOVAS:
            with self.subTest(skill=nome):
                texto = ler(f"skills/{nome}/SKILL.md")
                self.assertGreater(len(texto), 1000)
                self.assertIn("L51", texto)

    def test_os_ids_de_portao_seguem_no_nucleo(self):
        nucleo = ler(JARVIS)
        for regra in ("R-MAIN", "R-VERIFY", "R-CONFORMIDADE", "R-DECISAO", "R-SEGURANCA", "R-REVIEW", "R-QA", "R-CUSTO"):
            with self.subTest(regra=regra):
                self.assertIn(f"`{regra}`", nucleo)

    def test_o_passo_8_encerra_pelo_vazio_sem_apagar_nada(self):  # ACELERA-E2b, C-7
        nucleo = ler(JARVIS)
        passo = next(linha for linha in nucleo.splitlines() if linha.startswith("8. "))
        for trecho in ("`forge-check vazio --ref <branch>`", "só `vazio: sim` encerra", "`não verificável` não encerra",
                       "linha inteira", "a branch e a worktree ficam até a limpeza normal (`R-VERIFY`)"):
            self.assertIn(trecho, passo)
        for proibido in ("branch -D", "worktree remove", "push --delete"):
            self.assertNotIn(proibido, passo)
        self.assertLessEqual(len(nucleo.splitlines()), 110)

    def test_o_qa_corre_em_paralelo_e_a_volta_e_um_brief_so(self):  # EST-M6 (versao-040 E4), decisão 7b
        nucleo = ler(JARVIS)
        passo6 = re.search(r"^6\. \*\*QA\*\*.*$", nucleo, re.M)
        self.assertIsNotNone(passo6, "o passo 6 (QA) sumiu do núcleo")
        for trecho in ("obrigatório nas classes N e C", "em paralelo ao passo 5, no mesmo head", "brief único"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, passo6.group(0))
        self.assertLessEqual(len(nucleo.splitlines()), 110)


class OrcamentoDeInstrucao(unittest.TestCase):
    """0.43.1, decisão 11: o Jarvis e as regras que ele carrega com no máximo metade do tamanho da base; o procedimento mora na ferramenta."""

    def test_jarvis_e_regras_cabem_na_metade_da_base(self):
        arquivos = [RAIZ / JARVIS, *sorted((RAIZ / "docs" / "regras").glob("*.md"))]
        self.assertGreaterEqual(len(arquivos), 18)
        total = sum(len(a.read_text(encoding="utf-8")) for a in arquivos)
        self.assertLessEqual(total, ORCAMENTO_0431)

    def test_toda_regra_tem_revisao_e_medida(self):  # decisão 10: `Revisar em:` e `Medida:` no começo da linha
        regras = sorted((RAIZ / "docs" / "regras").glob("R-*.md"))
        self.assertGreaterEqual(len(regras), 17)
        for regra in regras:
            with self.subTest(regra=regra.name):
                texto = regra.read_text(encoding="utf-8")
                self.assertRegex(texto, r"(?m)^Revisar em: \d{4}-\d{2}-\d{2}$")
                self.assertRegex(texto, r"(?m)^Medida: \S")

    def test_o_conferente_e_opcional_e_a_forma_e_da_ferramenta(self):
        nucleo = ler(JARVIS)
        for trecho in ("forge-check brief selar", "forge-check entrega --pedido <p> --branch <b> --etapa <etapa>", "forge-check classe",
                       "forge-check parecer delta <parecer>", "Opcional, só leitura"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, nucleo)


class RevalidaMesmaInstancia(unittest.TestCase):
    """E6 da 0.36 (decisão 27): a revalidação de um parecer retoma a instância que o deu, no passo 5, sem linha nova."""

    def test_o_passo_5_manda_retomar_a_instancia_e_abrir_nova_sem_ela(self):
        nucleo = ler(JARVIS)
        passo5 = next(l for l in nucleo.splitlines() if l.startswith("5. **Conferência da entrega e code review:**"))
        self.assertRegex(passo5, r"revalidação de um parecer.*retoma a instância que o deu \(`SendMessage`")
        self.assertIn("sem a instância (sessão reiniciada), abra uma nova com o mesmo brief", passo5)

    def test_o_nucleo_segue_no_teto(self):
        nucleo = ler(JARVIS)
        self.assertLess(len(nucleo), 24000)
        self.assertLessEqual(len(nucleo.splitlines()), 110)


if __name__ == "__main__":
    unittest.main()
