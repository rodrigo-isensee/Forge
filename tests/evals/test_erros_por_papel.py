"""Erros por papel (0.43.3, E23 da versao-075, DECISÃO DO DONO de 2026-11-08 20:04): cada erro real de um papel do time vira um caso
executável aqui, e não um arquivo de texto lido antes de agir (a prevenção em texto falhou 8 vezes seguidas, estudo 2-erros §4).

Cada classe declara `PAPEL` (o agente que errou) e cita a fonte do erro (`EJ <n>` de ERROS-JARVIS.md, `C<n>` do estudo 2-erros ou o
portão que o achou). Como em test_regressao_forma.py: o caso que a ferramenta já barra é teste comum; o verificável que ela ainda
não barra fica `@unittest.expectedFailure` (backlog: quem fizer a trava tira o decorador na mesma entrega). O erro que nenhuma
ferramenta verifica (julgamento) fica em `SEM_FERRAMENTA`, por papel, com a fonte: é backlog de texto, não de trava.
`forge-placar` conta os casos por papel (classes com `PAPEL`; as de test_regressao_forma.py, sem `PAPEL`, são do jarvis) ao lado
da taxa de reprovação de cada papel. Só biblioteca padrão, sem rede."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

TESTES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTES))  # os apoios de tests/ também no modo `tests.evals.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401  (guarda do .git/config comum)
from evals.test_regressao_forma import BRIEF, CABECALHO, RaizSintetica  # noqa: E402

RAIZ = TESTES.parent
FORGE_PLACAR = str(RAIZ / "bin" / "forge-placar")

# Erros de julgamento, sem ferramenta que os verifique: ficam como backlog de texto do papel (o placar os conta à parte).
SEM_FERRAMENTA = {
    "jarvis": [("EJ 61", "escolha técnica do arquiteto feita no brief"),
               ("C10", "afirmação ou premissa sem conferir (ex.: 'cada branch já tem review')")],
    "conferente": [("C13", "achado novo em rodada posterior sobre texto que não mudou (tardio)"),
                   ("C13", "conferência rodada com o cwd errado")],
    "qa-engineer": [("C9", "teste de tempo de parede que cai sob carga (7 envios caídos); verificável, sem trava ainda")],
}


def carregar(nome, caminho):
    """Script sem extensão ou módulo de hook como módulo (só biblioteca padrão)."""
    sys.path.insert(0, str(caminho.parent))  # o hook importa o `_comum` da mesma pasta
    spec = importlib.util.spec_from_loader(nome, SourceFileLoader(nome, str(caminho)))
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class PastaTemporariaComum(RaizSintetica):
    """EJ 88 · C2 (pasta /tmp comum entre QAs paralelos: um apagou o trabalho do outro)."""
    PAPEL = "jarvis"

    def test_pasta_tmp_sem_o_id_do_pedido_no_entregar_reprova(self):
        brief = BRIEF.replace("## Entregar\n", "## Entregar\n- Monte o clone em /tmp/qa-comum/repo e rode a suíte lá.\n", 1)
        self.assertBarra(*self.conferir(brief), "pasta comum aos agentes em paralelo")

    def test_controle_pasta_com_o_id_do_pedido_e_modelo_do_mktemp_passam(self):
        for pasta in ("/tmp/qa-pedido-sintetico/repo", "/tmp/qa.XXXXXX"):
            with self.subTest(pasta):
                brief = BRIEF.replace("## Entregar\n", f"## Entregar\n- Monte o clone em {pasta} (E1).\n", 1)
                self.assertEqual(self.conferir(brief)[0], 0)


class FerramentaQueODestinoNaoTem(RaizSintetica):
    """EJ 97 · C2 (brief manda o destino usar uma ferramenta que o `tools:` dele não tem)."""
    PAPEL = "jarvis"

    @unittest.expectedFailure
    def test_brief_que_manda_o_destino_usar_sendmessage_reprova(self):
        """ERRO EJ 97: o `forge-check brief` ainda não lê o `tools:` do agente destino em agents/<nome>.md."""
        brief = BRIEF.replace("## Entregar\n", "## Entregar\n- Avise o revisor pela ferramenta SendMessage ao terminar (E1).\n", 1)
        self.assertBarra(*self.conferir(brief))


class BranchDoTechLead(RaizSintetica):
    """EJ 1, 100 · C2 (o tech-lead criou e enviou `melhoria/melhoria/...` tirado do brief; ~40 min na 0.43)."""
    PAPEL = "tech-lead"

    def test_brief_com_o_prefixo_duplicado_nao_chega_ao_tech_lead(self):
        brief = BRIEF.replace("Agente destino: forge:dev-exemplo\n",
                              "Agente destino: forge:dev-exemplo\n" + CABECALHO.replace("melhoria/x", "melhoria/melhoria/x"), 1)
        self.assertBarra(*self.conferir(brief), "branch: prefixo duplicado")


class SpecDeMutante(unittest.TestCase):
    """Pareceres de review da 0.43 à 0.75: 20 dos 52 bloqueantes foram spec de mutante faltando ou inválida (estudo 2-erros §2)."""
    PAPEL = "tech-lead"

    @classmethod
    def setUpClass(cls):
        cls.mutante = carregar("forge_mutante_evals_papel", RAIZ / "bin" / "forge-mutante")

    def spec(self, **troca):
        m = {"id": "M1", "guarda": "g", "arquivo": "bin/x", "de": "a", "para": "b", "testes": ["tests.test_x.T.test_y"]}
        m.update(troca)
        return {"pedido": "p", "mutantes": [{k: v for k, v in m.items() if v is not None}]}

    def test_controle_spec_completa_passa(self):
        self.assertEqual(self.mutante.validar_spec(self.spec()), [])

    def test_mutante_sem_os_testes_que_o_matam_e_invalido(self):
        self.assertTrue(self.mutante.validar_spec(self.spec(testes=None)))

    def test_mutante_com_trecho_vazio_e_invalido(self):
        self.assertTrue(self.mutante.validar_spec(self.spec(de="")))


class ConferenteQueGrava(unittest.TestCase):
    """EJ 83, 87 · C13 (o conferente executou o brief em vez de conferir; grava no pedido pela forma nova do forge-check)."""
    PAPEL = "conferente"

    @classmethod
    def setUpClass(cls):
        cls.conformidade = carregar("forge_conformidade_evals_papel", RAIZ / "hooks" / "conformidade.py")

    def grava(self, linha):
        args = linha.split()
        return self.conformidade.grava_no_pedido(self.conformidade.livres_do_forge_check(args), args)

    def test_entrega_com_pedido_e_brief_selar_gravam_no_pedido(self):
        for linha in ("entrega --pedido p1 --branch melhoria/x --etapa codigo", "entrega --ped=p1 --etapa codigo",
                      "brief selar --arquivo docs/briefs/p1-x-1.md --pedido p1"):
            with self.subTest(linha):
                self.assertTrue(self.grava(linha))

    def test_controle_so_leitura_nao_grava(self):
        for linha in ("entrega p1 --branch melhoria/x --etapa codigo", "entrega --pedido p1 --sem-gravar --etapa codigo"):
            with self.subTest(linha):
                self.assertFalse(self.grava(linha))


class PropostaSemMedida(unittest.TestCase):
    """2-erros §4 (102 prevenções escritas sem medida; a taxa não caiu): proposta de melhoria sem métrica nem critério de reversão."""
    PAPEL = "agile-coach"
    CABECALHO = "| ID | Hipótese | Mudança | Métrica | Critério de reversão | Início | Revisão | Resultado |\n|---|---|---|---|---|---|---|---|\n"

    def propostas(self, linha):
        with tempfile.TemporaryDirectory(prefix="forge-evals-papel-") as tmp:
            arq = Path(tmp) / "melhorias.md"
            arq.write_text(self.CABECALHO + linha, encoding="utf-8")
            r = subprocess.run([sys.executable, FORGE_PLACAR, "propostas", str(arq), "--hoje", "2026-11-08"],
                               capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout

    def test_controle_proposta_com_metrica_prazo_e_reversao_passa(self):
        rc, saida = self.propostas("| P1 | h | código: trava | taxa_forma | piora 10% | 2026-11-08 | 2026-11-20 | — |\n")
        self.assertEqual(rc, 0, saida)

    def test_prevencao_em_texto_sem_metrica_nem_reversao_reprova(self):
        rc, saida = self.propostas("| P1 | h | reler o arquivo antes de agir | — | — | 2026-11-08 | 2026-11-20 | — |\n")
        self.assertEqual(rc, 1, saida)
        self.assertIn("Métrica tem de começar", saida)
        self.assertIn("sem critério de reversão", saida)


class EtapaJaResolvidaNaDevelop(RaizSintetica):
    """v047 E2.180, ETAPA-SO-APOS-CONFERIR-DEVELOP (Histórico do v047, 13/11 08:00 e 08:39: E3.2 e E5.3 abertas pelo cartão com o
    item já na develop; 13/11, etapa entregue havia 3 h quase delegada de novo). O texto está na skill falar-com-o-dono; a trava,
    no backlog: o `forge-check brief` ainda não procura na `develop` um commit que cite o pedido e a etapa do `Cobre:`."""
    PAPEL = "jarvis"

    def develop_com(self, mensagem):
        """A raiz sintética vira repositório com um commit na `develop` com a `mensagem`."""
        limpo = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}  # sem GIT_DIR e afins herdados de um hook (AR-4)
        env = dict(sem_manutencao(limpo), HOME=str(self.tmp / "home"), GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
                   GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        for args in (["init", "-q", "-b", "develop"], ["commit", "-q", "--allow-empty", "-m", mensagem]):
            subprocess.run(["git", "-C", str(self.tmp), *args], check=True, capture_output=True, env=env, timeout=60)

    def brief_da_etapa(self):
        return BRIEF.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1)

    def test_controle_etapa_sem_commit_na_develop_passa(self):
        self.develop_com("feat(outro): recurso B (pedido-sintetico E1.2)")
        rc, saida = self.conferir(self.brief_da_etapa())
        self.assertEqual(rc, 0, saida)

    @unittest.expectedFailure
    def test_brief_de_etapa_ja_resolvida_na_develop_reprova(self):
        """ERRO 13/11: o `forge-check brief` ainda não confere a `develop` antes de abrir a etapa."""
        self.develop_com("feat(exemplo): recurso A (pedido-sintetico E1.1)")
        self.assertBarra(*self.conferir(self.brief_da_etapa()))


class MensagemEmOutroIdioma(unittest.TestCase):
    """JARVIS-SO-PORTUGUES (ORDEM DO DONO 16/11 21:36, v047: às 21:18 o Jarvis escreveu ao dono em inglês). A regra única está em
    skills/falar-com-o-dono/toda-mensagem.md (SIEG-G4); a medida é o `outro_idioma` do hook meta. A nota entre chamadas de
    ferramenta também é medida (E25.1, 0.47.9)."""
    PAPEL = "jarvis"
    PT = "Disparei os portões da branch e não ficou pendência; você já pode ver o PR quando quiser."
    EN = "Waiting for the agents to finish; the branch is ready and you can check it now."

    @classmethod
    def setUpClass(cls):
        cls.meta = carregar("forge_meta_evals_papel", RAIZ / "hooks" / "meta.py")

    def medir(self, final, notas=()):
        """As linhas do mensagens.jsonl para a mensagem `final`, com as `notas` antes de ferramentas no transcrito; dono sem config."""
        with tempfile.TemporaryDirectory(prefix="forge-evals-idioma-") as tmp:
            transcrito = Path(tmp) / "sessao.jsonl"
            linhas = [{"type": "assistant", "message": {"content": [{"type": "text", "text": n},
                                                                   {"type": "tool_use", "name": "Bash", "input": {}}]}} for n in notas]
            linhas.append({"type": "assistant", "message": {"content": [{"type": "text", "text": final}]}})
            transcrito.write_text("".join(json.dumps(l) + "\n" for l in linhas), encoding="utf-8")
            campos = {"last_assistant_message": final, "transcript_path": str(transcrito)}
            hook = type("Hook", (), {"campo": lambda self, chave: campos.get(chave), "run": lambda self: Path(tmp),
                                     "iniciante": lambda self: False})()
            self.meta.medir_mensagem(hook, None)
            return [json.loads(l) for l in (Path(tmp) / "mensagens.jsonl").read_text(encoding="utf-8").splitlines()]

    def test_controle_mensagem_em_portugues_passa(self):
        self.assertEqual([l["outro_idioma"] for l in self.medir(self.PT)], [False])

    def test_mensagem_final_ao_dono_em_ingles_e_acusada(self):
        (linha,) = self.medir(self.EN)
        self.assertEqual((linha["idioma"], linha["idioma_do_dono"], linha["outro_idioma"]), ("en", "pt", True))

    def test_nota_entre_ferramentas_em_ingles_e_acusada(self):
        """ERRO 16/11 21:18: a nota em inglês antes de uma ferramenta passava sem acusação; E25.1 (0.47.9) a mede."""
        self.assertTrue(any(l["outro_idioma"] for l in self.medir(self.PT, notas=[self.EN])))


class RodadaQueNaoEncerra(unittest.TestCase):
    """JARVIS-ENCERRA-RODADA (ORDEM DO DONO 16/11 21:36, v047: duas mensagens do dono presas na fila por mais de 10 min porque a
    rodada não encerrava). A regra está em skills/falar-com-o-dono/toda-mensagem.md; a medida, no backlog: nenhuma ferramenta lê
    ainda o `queue-operation` (enqueue e dequeue) do transcrito para contar a espera da mensagem do dono."""
    PAPEL = "jarvis"

    @unittest.expectedFailure
    def test_mensagem_do_dono_presa_mais_de_10_min_e_acusada(self):
        """ERRO 16/11 21:36: o `forge-check transcricao` não tem medida da fila do dono (alvo 0 acima de 10 min)."""
        fila = [("enqueue", "2026-11-16T21:25:00.000Z"), ("dequeue", "2026-11-16T21:37:00.000Z"),
                ("enqueue", "2026-11-16T21:40:00.000Z"), ("dequeue", "2026-11-16T21:41:00.000Z")]
        with tempfile.TemporaryDirectory(prefix="forge-evals-rodada-") as tmp:
            transcrito = Path(tmp) / "sessao.jsonl"
            transcrito.write_text("".join(json.dumps({"type": "queue-operation", "operation": op, "timestamp": t,
                                                      "content": "mensagem do dono"}) + "\n" for op, t in fila), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", str(RAIZ / "bin" / "forge-check"), "transcricao", "fila", str(transcrito)],
                               capture_output=True, text=True, timeout=60, env={"PATH": os.environ.get("PATH", ""), "HOME": tmp})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("acima de 10 min: 1", r.stdout)


class Catalogo(unittest.TestCase):
    """O `SEM_FERRAMENTA` tem a forma que o placar lê: papel -> [(fonte, descrição)]."""

    def test_forma_do_backlog_sem_ferramenta(self):
        for papel, erros in SEM_FERRAMENTA.items():
            self.assertRegex(papel, r"^[a-z][a-z-]+$")
            for fonte, descricao in erros:
                self.assertRegex(fonte, r"^(EJ \d+|C\d+)$")
                self.assertTrue(descricao)
        json.dumps(SEM_FERRAMENTA)  # o placar a lê por AST: só literais


if __name__ == "__main__":
    unittest.main()
