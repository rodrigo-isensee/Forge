"""L51 (AQ-8): o Jarvis em núcleo curto. O texto saiu de `agents/jarvis.md` para skills lidas no passo; nenhum invariante
sumiu (T-51a): cada trecho que o `tests/config.json` exigia do Jarvis na base b2580c6 segue exigido, no Jarvis ou na skill
para onde foi, e o texto de cada um existe lá; o núcleo manda ler cada skill nova."""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apoio_jarvis import (INDICE_DAS_REGRAS, conjunto_do_jarvis, ids_da_tabela, problemas_das_diretrizes, problemas_das_regras,  # noqa: E402
                          skills_citadas, skills_sem_ordem_de_leitura)

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "tests" / "config.json").read_text(encoding="utf-8"))
ANTES = json.loads((RAIZ / "tests" / "fixtures" / "jarvis-invariantes-b2580c6.json").read_text(encoding="utf-8"))
JARVIS = "agents/jarvis.md"
SKILLS_L51 = ("briefs-e-conferencia", "trabalho-em-paralelo", "falar-com-o-dono")
# Folga do texto do Jarvis (v047, P2): o ponteiro pelo caminho também é invariante para a skill nova `fluxo-do-pedido`.
SKILLS_COM_PONTEIRO = SKILLS_L51 + ("fluxo-do-pedido",)
DIRETRIZES = json.loads((RAIZ / "tests" / "fixtures" / "diretrizes-do-dono.json").read_text(encoding="utf-8"))["diretrizes"]
# P4 (decisões do dono de 14/11 08:16 e 08:38): pendentes 2, 11, 23, 24, 26, 27 e 28, cada uma com o seu cartão; só desce.
# A 29 virou de fábrica com o FOCO-NAS-DECISOES.
MAX_PENDENTES = 7
# P3: a mensagem do núcleo manda mover, não reduzir (diretriz 25).
MOVA = ("não apague nem resuma regra (diretriz 25): mova o detalhe para uma skill que o Jarvis manda ler e deixe o resumo; "
        "não suba o teto")
# 0.43.1 (decisões do dono de 2026-11-08, "Faça tudo"): o brief é selado pela ferramenta, a entrega é conferida por ela e as
# perguntas ao dono passavam a ser juntadas numa só mensagem (revisto na 0.46, uma a uma). Estes trechos descreviam a conferência manual pelo agente conferente (mensagem, hash, Base-sha,
# passada única, autoconferência) e a pergunta uma por vez: saem por mudança de processo, não por afrouxamento. O que eles
# protegiam passou para a ferramenta (`forge-check brief selar`, `forge-check entrega`) e para R-BRIEF, R-PROVA e R-DECISAO.
RETIRADOS_0431 = frozenset({
    "lista \\*\\*todos os achados\\*\\* de uma vez; corrija todos", "Autoconferência fixa do brief", "Brief-sha256",
    "nunca a própria branch", "ele não vê o relatório", "uma pergunta por vez", "`<<<BRIEF`", "`Base-sha:`",
    "`Arquivo:` \\(o caminho do brief", "linhas>=N",
})
# 0.46 (decisão do dono de 2026-11-11 13:06): a lista do que não se delega por "decidam vocês" ganhou aceite de risco, rótulo e
# merge na main; o trecho antigo foi substituído pelo novo (config.json), não removido.
RETIRADOS_046 = frozenset({"que não se oferece em pergunta de custo, acesso, exceção a regra ou ato irreversível"})
# Um número só por trava (docs/regras/orcamento.json): o núcleo (jarvis.md + docs/regras/*.md, decisão 11 do dono) e o teto do
# arquivo do Jarvis (o mesmo que tests/test_orcamento_instrucao.py aplica).
ORCAMENTO = json.loads((RAIZ / "docs" / "regras" / "orcamento.json").read_text(encoding="utf-8"))
ORCAMENTO_0431 = ORCAMENTO["nucleo"]["teto_caracteres"]


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def arquivos_do_nucleo():
    return list(conjunto_do_jarvis())


class NucleoCurtoDoJarvis(unittest.TestCase):
    def test_todo_invariante_do_jarvis_existe_no_jarvis_ou_na_skill_nova(self):
        self.assertGreaterEqual(len(ANTES), 73)
        self.assertEqual(len(RETIRADOS_0431 & set(ANTES)), len(RETIRADOS_0431), "retirado que não era invariante")
        exigidos = {t: [] for t in ANTES if t not in RETIRADOS_0431 | RETIRADOS_046}
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
        for nome in SKILLS_COM_PONTEIRO:
            with self.subTest(skill=nome):
                self.assertIn(f"skills/{nome}/SKILL.md", nucleo)
                self.assertIn(f"skills/{nome}/SKILL\\.md", CONFIG["invariantes"][JARVIS])  # o ponteiro também é invariante

    def test_o_nucleo_ficou_curto_e_as_skills_tem_o_texto_que_saiu(self):
        self.assertLess(len(ler(JARVIS)), 24000)  # 29.092 bytes na base
        for nome in SKILLS_L51:
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
        self.assertEqual(ORCAMENTO_0431, 75_022 // 2)  # metade da base da 0.43: subir é afrouxar
        arquivos = [RAIZ / JARVIS, *sorted((RAIZ / "docs" / "regras").glob("*.md"))]
        self.assertGreaterEqual(len(arquivos), 14)  # AV5: seis regras viraram trechos de R-LIMITES.md e uma linha do README
        total = sum(len(a.read_text(encoding="utf-8")) for a in arquivos)
        self.assertLessEqual(total, ORCAMENTO_0431, f"núcleo: passa do teto em {total - ORCAMENTO_0431}; {MOVA}")

    def test_toda_regra_tem_revisao_e_medida(self):  # decisão 10: `Revisar em:` e `Medida:` no começo da linha
        regras = sorted((RAIZ / "docs" / "regras").glob("R-*.md"))
        self.assertGreaterEqual(len(regras), 12)  # AV5: R-LIMITES.md junta cinco; R-WIP é linha do README
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
        nucleo, teto = ler(JARVIS), ORCAMENTO["agentes"]["jarvis"]["teto"]["agente_caracteres"]
        self.assertLessEqual(len(nucleo), teto, f"{JARVIS}: passa do teto em {len(nucleo) - teto}; {MOVA}")
        self.assertLessEqual(len(nucleo.splitlines()), 110)


class VoltaRetomadaEAceiteEmParalelo(unittest.TestCase):
    """0.43.3: a volta vai ao autor retomado por `SendMessage` (V3: 26 a 38 min por volta numa instância nova) e, nas classes N e C,
    o QA escreve o aceite do pedido em paralelo, sem ver o código (V4)."""

    def test_o_passo_6_manda_a_volta_ao_autor_retomado(self):
        passo6 = next(l for l in ler(JARVIS).splitlines() if l.startswith("6. **QA**"))
        self.assertIn("brief único ao autor, retomado por `SendMessage`; sem o id, instância nova", passo6)

    def test_o_tech_lead_e_retomado_e_recebe_o_aceite_sem_altera_lo(self):
        texto = ler("agents/tech-lead.md")
        self.assertIn("**Na volta** você é retomado por `SendMessage`", texto)
        self.assertIn("Classes N e C: o aceite do QA (do pedido, sem ver o código) vem em paralelo; não o altere.", texto)

    def test_o_qa_escreve_o_aceite_do_pedido_nas_classes_n_e_c(self):
        passo2 = next(l for l in ler("agents/qa-engineer.md").splitlines() if l.startswith("2. Escreva o plano"))
        self.assertIn("sem ler o código", passo2)
        self.assertIn("nas classes N e C, também os testes de aceite, do pedido, num commit seu", passo2)


class Diretrizes18e19(unittest.TestCase):
    """0.46 (diretrizes 18 e 19 do dono, 2026-11-12): uma instância do papel por item à espera, e o Jarvis anda sozinho, esperando
    em segundo plano com prazo no próprio comando, sem pedir para ser chamado; medida de cada uma no texto."""

    def setUp(self):
        self.skill = ler("skills/trabalho-em-paralelo/SKILL.md")
        self.sozinho = next(l for l in self.skill.splitlines() if l.startswith("- **Anda sozinho:**"))
        self.wip = next(l for l in ler("docs/regras/README.md").splitlines() if l.startswith("**`R-WIP`"))

    def test_o_jarvis_anda_sozinho_e_nunca_pede_para_ser_chamado(self):
        self.assertIn("Você anda sozinho e nunca pede para ser chamado", ler(JARVIS))
        self.assertIn("nunca peça para ser chamado", self.sozinho)
        self.assertIn('Medida: zero pedidos de "me chame" ou "continue"', self.sozinho)

    def test_a_espera_em_segundo_plano_traz_o_prazo_no_proprio_comando(self):
        self.assertIn("`run_in_background`", self.sozinho)
        self.assertIn("`fim=$((SECONDS+N)); until <condição> || [ $SECONDS -ge $fim ]; do sleep 60; done`", self.sozinho)
        self.assertIn("subagente segue a skill `esperar-estado`", self.sozinho)  # a regra 2 dela proíbe esperar em segundo plano
        self.assertIn("nada novo é disparado", self.sozinho)
        self.assertIn("grave onde parou (`forge-check pausa --gravar`)", self.sozinho)

    def test_uma_instancia_por_item_com_volta_e_medida(self):
        self.assertIn("uma instância do papel por item à espera", ler(JARVIS))
        self.assertIn("ganham uma instância cada, ao mesmo tempo", self.wip)
        self.assertIn("a volta vai à instância que o fez (sem ela, a uma nova com o mesmo brief)", self.wip)
        self.assertIn("espera do item pronto até cada portão; vagas livres com fila parada (zero)", self.wip)
        self.assertIn("Itens com arquivo em comum não andam em paralelo", self.skill)


class WorktreeAntesDeDelegar(unittest.TestCase):
    """MP1311 item 12: subagente não fica parado sem escrita na worktree; o Jarvis a cria na própria sessão ou o brief avisa."""

    def test_o_jarvis_cria_a_worktree_antes_de_delegar(self):
        passo4 = next(l for l in ler(JARVIS).splitlines() if l.startswith("4. **Desenvolvimento:**"))
        self.assertIn("crie a worktree na sua sessão antes de delegar", passo4)

    def test_a_skill_manda_avisar_no_brief_e_oferece_o_caminho_pelo_github(self):
        skill = ler("skills/briefs-e-conferencia/SKILL.md")
        self.assertRegex(skill, r"(?s)worktree de outra sessão.*só leitura.*update-branch")

    def test_a_skill_da_o_clone_local_como_saida_quando_a_worktree_nao_grava(self):
        skill = ler("skills/briefs-e-conferencia/SKILL.md")
        self.assertRegex(skill, r"(?s)não gravável.*clone local.*~/\.forge-contrib/wt/<nome>-c.*origin/develop")


class PresencaDasRegrasEDasDiretrizes(unittest.TestCase):
    """Folga do texto do Jarvis (v047, P4; diretriz 25): cada regra com ID e cada diretriz de fábrica seguem presentes no Jarvis
    ou no que ele manda ler; cada skill que o Jarvis cita vem com a ordem de leitura ("leia" ou "antes de"). Falta reprova e diz
    onde procurar; o teste não corrige sozinho."""

    def test_o_conjunto_e_calculado_e_traz_as_skills_novas(self):
        conjunto = conjunto_do_jarvis()
        self.assertGreaterEqual(len(conjunto), 20)
        for rel in ("skills/fluxo-do-pedido/SKILL.md", "skills/kanban-metricas/SKILL.md", "docs/regras/R-DECISAO.md",
                    INDICE_DAS_REGRAS, "docs/economia-de-tokens.md"):
            with self.subTest(arquivo=rel):
                self.assertIn(rel, conjunto)

    def test_cada_skill_citada_pelo_jarvis_traz_a_ordem_de_leitura(self):
        self.assertGreaterEqual(len(skills_citadas(ler(JARVIS))), 8)
        self.assertEqual(skills_sem_ordem_de_leitura(), [])

    def test_cada_regra_com_id_aparece_e_tem_texto(self):
        self.assertGreaterEqual(len(ids_da_tabela()), 17)
        self.assertEqual(problemas_das_regras(RAIZ, conjunto_do_jarvis()), [])

    def test_cada_diretriz_tem_entrada_e_a_de_fabrica_aparece(self):
        self.assertGreaterEqual(len(DIRETRIZES), 29)
        self.assertEqual(problemas_das_diretrizes(DIRETRIZES, conjunto_do_jarvis(), MAX_PENDENTES), [])

    def test_cada_numero_do_arquivo_do_dono_tem_entrada(self):
        arquivo = os.environ.get("FORGE_DIRETRIZES_DONO", "")
        if not arquivo or not Path(arquivo).is_file():
            self.skipTest("FORGE_DIRETRIZES_DONO sem o arquivo do dono (fora do git; no CI, a tabela neutra basta)")
        numeros = [int(n) for n in re.findall(r"^(\d+)\. ", Path(arquivo).read_text(encoding="utf-8"), re.M)]
        self.assertTrue(numeros, "nenhum número no arquivo do dono")
        self.assertEqual(problemas_das_diretrizes(DIRETRIZES, conjunto_do_jarvis(), MAX_PENDENTES, numeros), [])


class FocoNasDecisoes(unittest.TestCase):
    """FOCO-NAS-DECISOES (diretriz 29 do dono, com a correção de 14/11): o detalhe na skill falar-com-o-dono, no Jarvis o resumo e
    a ordem de leitura (diretriz 25), e o modelo de projeto leva a regra a todo projeto novo."""

    def test_o_jarvis_traz_o_resumo_e_manda_ler_a_skill_antes_de_responder(self):
        linha = next(l for l in ler(JARVIS).splitlines() if l.startswith("- **Pedido de decisões** (diretriz 29):"))
        for trecho in ("uma a uma", "sem aviso de andamento no meio", "o time segue",
                       "Leia `${CLAUDE_PLUGIN_ROOT}/skills/falar-com-o-dono/SKILL.md` antes de responder a um pedido de decisões"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, linha)

    def test_a_skill_traz_o_detalhe_inteiro(self):
        paragrafo = next(l for l in ler("skills/falar-com-o-dono/SKILL.md").splitlines()
                         if l.startswith("**Pedido de decisões (diretriz 29):**"))
        for trecho in ('"me traga as decisões", "o que precisa de mim" ou "quais as pendências"', "faça só isso",
                       "sem disparo, cartão, registro, conferência nem andamento antes",
                       'Leia só as perguntas abertas (`PERGUNTA:` e "precisa de você", nos pedidos e no quadro, numa consulta)',
                       "Responda já: a lista curta de todas as decisões pendentes, da de maior peso para a menor",
                       "a primeira pergunta completa (contexto simples, opções, recomendação, o que acontece sem decisão)",
                       "Uma a uma, cada resposta por `forge-check anotar` e a próxima logo", "O time não para",
                       "sem aviso ao dono entre as perguntas (resumo no fim)", "o que depende de uma decisão espera só ela",
                       'Sem pendência: "Não há decisão sua pendente", numa linha'):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, paragrafo)

    def test_o_modelo_de_projeto_leva_a_regra(self):
        modelo = next(l for l in ler("templates/projeto/CLAUDE.md").splitlines() if l.startswith("- `R-DECISAO`"))
        self.assertIn("Pedido de decisões do usuário: o Jarvis responde já, só com elas, por peso e uma a uma (skill `falar-com-o-dono`)",
                      modelo)

class MutantesDaPresenca(unittest.TestCase):
    """P4, item 7: cada mutante numa árvore sintética reprova (lista completa, AR-1)."""

    JARVIS_OK = "Leia `${CLAUDE_PLUGIN_ROOT}/skills/s1/SKILL.md` antes de agir; `R-UM` e `R-DOIS`.\n"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-presenca-"))
        self.escrever("agents/jarvis.md", self.JARVIS_OK)
        self.escrever("skills/s1/SKILL.md", "Detalhe da skill: veja também a skill `s2`.\n")
        self.escrever("skills/s2/SKILL.md", "Cada pergunta ao dono traz a origem do item.\n")
        self.escrever("docs/regras/R-UM.md", "Texto da regra um.\n")
        self.escrever(INDICE_DAS_REGRAS, "| ID | Regra |\n|---|---|\n| [`R-UM`](R-UM.md) | Um |\n| `R-DOIS` | Dois |\n\n"
                      "**`R-DOIS` (regra só de hook):** texto da regra dois.\n")
        self.tabela = {"1": {"onde": "fabrica", "trechos": ["traz a origem do item"]},
                       "2": {"onde": "sessao", "motivo": "vale só na sessão do Forge"},
                       "3": {"onde": "pendente", "cartao": "CARTAO-3", "trechos": ["texto que ainda não entrou na fábrica"]}}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def escrever(self, rel, texto):
        (self.tmp / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.tmp / rel).write_text(texto, encoding="utf-8")

    def diretrizes(self, tabela=None, numeros=()):
        return problemas_das_diretrizes(tabela or self.tabela, conjunto_do_jarvis(self.tmp), 1, numeros)

    def test_a_arvore_sintetica_passa(self):
        self.assertEqual(sorted(conjunto_do_jarvis(self.tmp)), ["agents/jarvis.md", "docs/regras/R-UM.md", INDICE_DAS_REGRAS,
                                                                "skills/s1/SKILL.md", "skills/s2/SKILL.md"])
        self.assertEqual((self.diretrizes(numeros=[1, 2, 3]), skills_sem_ordem_de_leitura(self.tmp)), ([], []))
        self.assertEqual(problemas_das_regras(self.tmp, conjunto_do_jarvis(self.tmp)), [])

    def test_apagar_o_trecho_reprova_e_diz_onde_procurar(self):
        self.escrever("skills/s2/SKILL.md", "Outro texto.\n")
        erro = self.diretrizes()
        self.assertEqual(len(erro), 1)
        self.assertIn("diretriz 1: 'traz a origem do item' não está em agents/jarvis.md nem nas skills que ele manda ler", erro[0])
        self.assertIn("não apague (diretriz 25)", erro[0])

    def test_tirar_a_citacao_da_skill_reprova(self):
        self.escrever("skills/s1/SKILL.md", "Detalhe da skill, sem citar outra.\n")
        self.assertIn("diretriz 1: 'traz a origem do item' não está", self.diretrizes()[0])

    def test_citar_sem_leia_nem_antes_de_reprova(self):
        self.escrever("agents/jarvis.md", "Veja `${CLAUDE_PLUGIN_ROOT}/skills/s1/SKILL.md`; `R-UM` e `R-DOIS`.\n")
        self.assertEqual(skills_sem_ordem_de_leitura(self.tmp), ["s1"])

    def test_id_no_readme_sem_texto_reprova(self):
        self.escrever(INDICE_DAS_REGRAS, "| [`R-UM`](R-UM.md) | Um |\n| `R-DOIS` | Dois |\n")
        self.assertEqual(problemas_das_regras(self.tmp, conjunto_do_jarvis(self.tmp)), ["R-DOIS: sem texto em docs/regras/"])

    def test_id_fora_do_conjunto_reprova(self):
        self.escrever("agents/jarvis.md", "Leia `${CLAUDE_PLUGIN_ROOT}/skills/s1/SKILL.md` antes de agir; `R-UM`.\n")
        self.assertEqual(problemas_das_regras(self.tmp, conjunto_do_jarvis(self.tmp)),
                         ["R-DOIS: não aparece no Jarvis nem nas skills citadas"])

    def test_id_que_some_do_jarvis_reprova_com_o_indice_no_conjunto(self):  # A1 e A2 do QA e da segurança (v047)
        self.escrever("agents/jarvis.md", "Leia `${CLAUDE_PLUGIN_ROOT}/skills/s1/SKILL.md` antes de agir; `R-DOIS`.\n")
        self.assertIn(INDICE_DAS_REGRAS, conjunto_do_jarvis(self.tmp))
        self.assertEqual(problemas_das_regras(self.tmp, conjunto_do_jarvis(self.tmp)),
                         ["R-UM: não aparece no Jarvis nem nas skills citadas"])
        self.escrever("skills/s2/SKILL.md", "Cada pergunta ao dono traz a origem do item; `R-UM`.\n")
        self.assertEqual(problemas_das_regras(self.tmp, conjunto_do_jarvis(self.tmp)), [])

    def test_numero_do_arquivo_do_dono_sem_entrada_reprova(self):
        self.assertEqual(self.diretrizes(numeros=[1, 2, 3, 4]), ["diretriz 4 do arquivo do dono sem entrada"])

    def test_buraco_na_numeracao_reprova(self):
        tabela = dict(self.tabela)
        del tabela["2"]
        self.assertEqual(self.diretrizes(tabela), ["diretriz 2: buraco na numeração"])

    def test_pendente_que_ja_aparece_reprova(self):
        tabela = dict(self.tabela, **{"3": {"onde": "pendente", "cartao": "CARTAO-3", "trechos": ["traz a origem do item"]}})
        self.assertEqual(self.diretrizes(tabela), ["diretriz 3: pendente com o trecho 'traz a origem do item' já presente; passe a fabrica"])

    def test_trecho_curto_reprova(self):
        tabela = dict(self.tabela, **{"1": {"onde": "fabrica", "trechos": ["a origem do item"]}})
        self.assertEqual(self.diretrizes(tabela), ["diretriz 1: trecho com menos de 20 caracteres: 'a origem do item'"])

    def test_pendente_acima_do_maximo_sem_cartao_ou_onde_desconhecido_reprova(self):
        tabela = dict(self.tabela, **{"2": {"onde": "pendente", "cartao": ""}, "4": {"onde": "talvez"},
                                      "5": {"onde": "fabrica"}, "6": {"onde": "sessao", "motivo": "curto"}})
        self.assertEqual(self.diretrizes(tabela), ["diretriz 2: pendente sem cartão", "diretriz 4: onde = 'talvez', esperava fabrica, "
                                                   "sessao ou pendente", "diretriz 5: de fábrica sem trecho", "diretriz 6: de sessão sem motivo",
                                                   "2 diretrizes pendentes, máximo 1: pendente só desce"])


if __name__ == "__main__":
    unittest.main()
