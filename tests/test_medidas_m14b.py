"""MEDIR-M14B: as medidas que dão a linha de base do processo antes de qualquer afrouxamento (esperas, PR `fix` que corrige PR
mesclado, defeito escapado, rótulo `afrouxa-regra` que era afrouxamento real) e o casamento do `--pedido` do custo com os cartões."""
import contextlib
import datetime
import hashlib
import io
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402
from apoio_jarvis import texto_do_jarvis  # noqa: E402
from test_voltas import FORGE_CHECK, RAIZ, Raiz, SemQueda  # noqa: E402


def carregar_forge_check_m14b():
    carregador = importlib.machinery.SourceFileLoader("forge_check_m14b", str(Path(__file__).resolve().parent.parent / "bin" / "forge-check"))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
    carregador.exec_module(modulo)
    return modulo


def carregar_forge_medidas():
    """bin/forge_medidas.py (FILA-31 F6, 0.45.7 E5.5), onde moram `medida` e `escape`."""
    carregador = importlib.machinery.SourceFileLoader("forge_medidas_m14b", str(Path(__file__).resolve().parent.parent / "bin" / "forge_medidas.py"))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
    carregador.exec_module(modulo)
    return modulo


FORGE_CHECK_M2B = str(Path(__file__).resolve().parent.parent / "bin" / "forge-check")
CABECALHO_HISTORICO = "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"


class CustoCasaOPedidoComOsCartoes(Raiz):
    """`transcricao custo --pedido`: o cartão do histórico não leva o id do pedido; o casamento é por nome, família ou coluna Pedido."""

    def setUp(self):
        super().setUp()
        for pedido in ("fix-x-pr", "outro"):
            self.gravar(f"docs/pedidos/{pedido}.md", "# Pedido\n")
        pasta = self.tmp / "home" / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(self.tmp.resolve()))
        pasta.mkdir(parents=True)
        horas = ["2026-10-20T09:00:00Z", "2026-10-20T10:30:00Z", "2026-10-20T11:30:00Z", "2026-10-20T14:00:00Z"]
        (pasta / "s.jsonl").write_text("\n".join(json.dumps(
            {"type": "assistant", "sessionId": "s", "isSidechain": False, "timestamp": h,
             "message": {"id": f"m{i}", "model": "m", "usage": {"input_tokens": 1, "output_tokens": 0}}}) for i, h in enumerate(horas)) + "\n",
            encoding="utf-8")

    def historico(self, *linhas):
        self.gravar("docs/kanban/historico.md", CABECALHO_HISTORICO + "".join(
            f"| 2026-10-20T{hora}:00+00:00 | {cartao} | A | B | x |\n" for hora, cartao in linhas))

    def custo(self, *args):
        cod, linhas, _ = self.rodar("transcricao", "custo", *args)
        return cod, linhas

    def test_cartao_da_mesma_familia_de_nome_casa_com_o_pedido(self):  # FIX-SUITE-LOCAL x FIX-SUITE-LOCAL-PR no histórico real
        self.historico(("10:00", "FIX-X"), ("11:00", "FIX-X"), ("12:30", "OUTRO-CARTAO"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: FIX-X", linhas)
        self.assertIn("custo: pedido: fix-x-pr janela 2026-10-20T10:00:00+00:00 a 2026-10-20T11:00:00+00:00", linhas)
        self.assertIn("custo: total: entrada=1 saida=0 cache_criacao=0 cache_leitura=0 total=1", linhas)
        self.assertNotIn("custo: aviso: 1 outros cartões em movimento na janela (o principal se mistura)", linhas)  # 12:30 fica fora

    def test_cartao_com_o_pedido_na_coluna_pedido_do_quadro_casa_e_os_outros_sao_avisados(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido | Responsável |\n|---|---|---|---|\n| E7 | trabalho | fix-x-pr | forge:tech-lead |\n"
                    "| E8 | outro trabalho | outro | forge:tech-lead |\n")
        self.historico(("10:00", "E7"), ("10:40", "E8"), ("11:00", "E7"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: E7", linhas)
        self.assertIn("custo: aviso: 1 outros cartões em movimento na janela (o principal se mistura)", linhas)

    def test_cartao_que_nao_e_do_pedido_nao_entra_na_janela(self):
        self.historico(("10:00", "OUTRO-CARTAO"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 1)
        self.assertTrue(any("sem movimento de cartão do pedido" in l for l in linhas), linhas)

    def test_prefixo_sem_hifen_nao_e_da_familia(self):
        self.historico(("10:00", "FIX"), ("10:10", "FIX-XA"))
        cod, linhas = self.custo("--pedido", "fix-x-pr")
        self.assertEqual(cod, 1)

    def test_nome_de_cartao_com_controle_nao_forja_linha(self):
        self.historico(("10:00", "OUTRO-\x1b[31mvermelho"), ("11:00", "OUTRO-\x1b[31mvermelho"))
        cod, linhas = self.custo("--pedido", "outro")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: cartões: OUTRO- [31mvermelho", linhas)
        self.assertFalse(any("\x1b" in l for l in linhas), linhas)


class Esperas(SemQueda, Raiz):
    """`forge-check esperas`: o registro de `forge-check movimento` vira minutos de espera pelo dono e por credencial."""
    HISTORICO = CABECALHO_HISTORICO + "".join(l + "\n" for l in (
        "| 2026-10-22T10:00:00-03:00 | K-1 | Em andamento | Aguardando o dono | decisão de escopo |",
        "| 2026-10-22T10:30:00-03:00 | K-1 | Aguardando o dono | Em andamento | dono decidiu |",
        "| 2026-10-22T11:00:00-03:00 | K-1 | Em andamento | Sem credencial | sem token do gh |",
        "| 2026-10-22T11:45:00-03:00 | K-1 | Sem credencial | Em andamento | token chegou |",
        "| 2026-10-22T12:00:00-03:00 | K-1 | Code review | Bloqueado | Aguardando o dono: rótulo no PR |",
        "| 2026-10-22T13:00:00-03:00 | K-2 | Em andamento | Bloqueado | dependência |",
        "| 2026-10-22T13:20:00-03:00 | K-2 | Bloqueado | Em andamento | liberou |",
        "| 2026-10-22T14:00:00-03:00 | K-3 | Em andamento | Aguardando o dono | pergunta |",
        "| 2026-10-22T14:10:00-03:00 | K-3 | Aguardando o dono | Bloqueado | Aguardando o dono: pergunta |",
        "| 2026-10-22T14:50:00-03:00 | K-3 | Bloqueado | Em andamento | respondeu |",
        "| sem-hora | K-3 | Em andamento | Aguardando o dono | linha sem hora ISO não conta |",
    ))

    def setUp(self):
        super().setUp()
        self.gravar("docs/kanban/historico.md", self.HISTORICO)

    def test_lista_cada_espera_com_tipo_e_minutos_e_o_total_por_tipo(self):
        cod, linhas, _ = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, [
            "esperas: K-1 dono inicio=2026-10-22T10:00:00-03:00 minutos=30",
            "esperas: K-1 credencial inicio=2026-10-22T11:00:00-03:00 minutos=45",
            "esperas: K-1 dono inicio=2026-10-22T12:00:00-03:00 minutos=aberta",
            "esperas: K-2 outra inicio=2026-10-22T13:00:00-03:00 minutos=20",
            "esperas: K-3 dono inicio=2026-10-22T14:00:00-03:00 minutos=50",  # Aguardando o dono -> Bloqueado (mesmo motivo) é a mesma espera
            "esperas: total: dono=3 minutos_dono=80 credencial=1 minutos_credencial=45 outra=1 minutos_outra=20 abertas=1 cartoes=3",
        ])

    def test_pedido_filtra_pelos_cartoes_do_pedido(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido |\n|---|---|---|\n| K-2 | x | ped-a |\n| K-3 | y | ped-a |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-a")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas[0], "esperas: pedido \"ped-a\" cartoes: K-2 K-3")
        self.assertEqual(linhas[1], "esperas: K-2 outra inicio=2026-10-22T13:00:00-03:00 minutos=20")
        self.assertEqual(linhas[-1], "esperas: total: dono=1 minutos_dono=50 credencial=0 minutos_credencial=0 outra=1 minutos_outra=20 abertas=0 cartoes=2")

    def test_pedido_com_dois_cartoes_soma_a_espera_do_dono_e_da_credencial(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido |\n|---|---|---|\n| K-1 | x | ped-b |\n| K-3 | y | ped-b |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-b")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas[0], "esperas: pedido \"ped-b\" cartoes: K-1 K-3")
        self.assertEqual(linhas[-1], "esperas: total: dono=3 minutos_dono=80 credencial=1 minutos_credencial=45 outra=0 minutos_outra=0 abertas=1 cartoes=2")

    def test_kanban_passado_vale_no_lugar_do_da_raiz(self):
        self.gravar("KANBAN.md", "# Quadro\n\n| ID | Cartão | Pedido |\n|---|---|---|\n| K-1 | x | ped-c |\n")
        self.gravar("fora/outro-quadro.md", "# Quadro\n\n| ID | Cartão | Pedido |\n|---|---|---|\n| K-2 | x | ped-c |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-c", "--kanban", str(self.tmp / "fora/outro-quadro.md"))
        self.assertEqual(cod, 0)
        self.assertEqual(linhas[0], "esperas: pedido \"ped-c\" cartoes: K-2")

    def test_motivo_que_cita_o_pedido_casa_o_cartao(self):
        self.gravar("docs/kanban/historico.md", self.HISTORICO + "| 2026-10-22T15:00:00-03:00 | K-4 | Em andamento | Em andamento | volta 1 do pedido ped-d. |\n"
                    + "| 2026-10-22T15:30:00-03:00 | K-5 | Em andamento | Aguardando o dono | pedido ped-dx |\n"
                    + "| 2026-10-22T15:10:00-03:00 | K-4 | Em andamento | Em andamento | outro motivo, sem o id |\n"
                    + "| 2026-10-22T16:00:00-03:00 | K-6 | Em andamento | Em andamento | PED-D em maiúsculas |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-d")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas[0], "esperas: pedido \"ped-d\" cartoes: K-4 K-6")  # ped-dx e ped-d-2 não são o pedido; o ponto final é

    def test_motivo_com_o_id_colado_ao_hifen_ou_ponto_nao_casa(self):
        self.gravar("docs/kanban/historico.md", self.HISTORICO + "| 2026-10-22T15:00:00-03:00 | K-4 | Em andamento | Em andamento | ped-d-2 e ped-d.md |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-d")
        self.assertEqual(cod, 1, linhas)

    def test_motivo_com_o_id_colado_atras_de_letra_digito_ponto_ou_hifen_nao_casa(self):
        self.gravar("docs/kanban/historico.md", self.HISTORICO + "| 2026-10-22T15:00:00-03:00 | K-4 | Em andamento | Em andamento | xped-d e 1ped-d e a.ped-d e x-ped-d |\n")
        cod, linhas, _ = self.rodar("esperas", "--pedido", "ped-d")
        self.assertEqual(cod, 1, linhas)

    def test_pedido_sem_cartao_rc_1_e_sem_historico_so_avisa(self):
        cod, linhas, _ = self.rodar("esperas", "--pedido", "nenhum")
        self.assertEqual(cod, 1)
        self.assertTrue(linhas[0].startswith("esperas: pedido"), linhas)

    def test_sem_historico_rc_0_com_total_zerado_e_aviso(self):
        (self.tmp / "docs/kanban/historico.md").unlink()
        cod, linhas, erro = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, ["esperas: total: dono=0 minutos_dono=0 credencial=0 minutos_credencial=0 outra=0 minutos_outra=0 abertas=0 cartoes=0"])
        self.assertIn("aviso", erro)

    def test_o_movimento_do_jarvis_alimenta_as_esperas(self):  # o registro real, não só a linha escrita à mão
        self.gravar("KANBAN.md", "# Quadro\n\n## Em andamento\n\n## Aguardando o dono\n")
        (self.tmp / "docs/kanban/historico.md").unlink()
        self.assertEqual(self.rodar("movimento", "K-9", "--de", "Em andamento", "--para", "Aguardando o dono", "--motivo", "validar")[0], 0)
        cod, linhas, _ = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertRegex(linhas[0], r"^esperas: K-9 dono inicio=\S+ minutos=aberta$")


class RepositorioDeTeste(Raiz):
    """Um repositório git descartável, com commits de data fixa (a hora entra nas medidas por janela)."""

    def git(self, *args, data=None):
        datas = {"GIT_AUTHOR_DATE": data, "GIT_COMMITTER_DATE": data} if data else {}
        env = sem_manutencao(dict(os.environ, GIT_AUTHOR_NAME="Teste", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="Teste",
                                  GIT_COMMITTER_EMAIL="t@example.com", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null", **datas))
        r = subprocess.run(["git", "-C", str(self.tmp), *args], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def iniciar(self):
        self.git("init", "-q", "-b", "develop")

    def commitar(self, mensagem, arquivos, dia="2026-10-20"):
        for nome, texto in arquivos.items():
            self.gravar(nome, texto)
        self.git("add", "--", *arquivos)
        self.git("commit", "-q", "-m", mensagem, data=f"{dia}T12:00:00+00:00")
        return self.git("rev-parse", "HEAD")


class PrsFixQueCorrigemPrMesclado(RepositorioDeTeste):
    def setUp(self):
        super().setUp()
        self.iniciar()
        self.commitar("feat(a): coisa nova (#10)", {"a.py": "1\n", "b.py": "1\n"}, "2026-10-14")
        self.commitar("feat(b): outra coisa (#11)", {"b.py": "2\n"}, "2026-10-15")
        self.commitar("docs(x): texto (#12)", {"x.md": "1\n"}, "2026-10-16")

    def corrigidos(self, *args):
        cod, linhas, erro = self.rodar("corrigidos", *args)
        self.assertNotIn("Traceback", erro)  # F6, E5.3: a queda do script é falha do teste, não erro de índice
        return cod, linhas

    def test_fix_que_cita_pr_mesclado_antes_e_prova_escrita(self):
        self.commitar("fix(c): conserta o que o #11 quebrou (#13)", {"c.py": "1\n"}, "2026-10-17")
        cod, linhas = self.corrigidos()
        self.assertEqual(cod, 0)
        self.assertRegex(linhas[0], r"^corrigidos: #13 [0-9a-f]{7} evidencia=cita cita=#11 toca=- fix\(c\): conserta o que o #11 quebrou \(#13\)$")
        self.assertRegex(linhas[-1], r"^corrigidos: total: prs=4 fix=1 cita=1 arquivo=0 nenhuma=0 dias=7 ref=[0-9a-f]{7}$")

    def test_fix_sem_citacao_que_mexe_em_arquivo_de_pr_recente_e_so_indicio(self):
        self.commitar("fix(b): ajusta b (#13)", {"b.py": "3\n"}, "2026-10-17")  # b.py: último PR #11, dois dias antes
        cod, linhas = self.corrigidos()
        self.assertRegex(linhas[0], r"evidencia=arquivo cita=- toca=#11 ")

    def test_arquivo_fora_da_janela_ou_citacao_de_pr_que_nao_existe_nao_contam(self):
        self.commitar("fix(a): ajusta a, que o #99 mexeu (#13)", {"a.py": "9\n"}, "2026-10-25")  # a.py mudou em 14/10: 11 dias
        cod, linhas = self.corrigidos()
        self.assertEqual(len(linhas), 1, linhas)  # só o resumo: nenhuma evidência
        self.assertIn("fix=1 cita=0 arquivo=0 nenhuma=1", linhas[0])
        cod, linhas = self.corrigidos("--dias", "30")
        self.assertIn("evidencia=arquivo cita=- toca=#10 ", linhas[0])

    def test_so_conta_fix_de_pr_e_a_propria_citacao_nao_vale(self):
        self.commitar("feat(c): coisa que cita o #11 (#13)", {"c.py": "1\n"}, "2026-10-17")
        self.commitar("fix(d): sem numero de pr, commit direto", {"b.py": "4\n"}, "2026-10-17")
        self.commitar("fix(e): fala de si mesmo, #14 (#14)", {"e.py": "1\n"}, "2026-10-18")
        cod, linhas = self.corrigidos()
        self.assertEqual(len(linhas), 1, linhas)
        self.assertIn("prs=5 fix=1 cita=0 arquivo=0 nenhuma=1", linhas[0])

    def test_commit_de_juncao_comum_conta_pelo_titulo_do_pr(self):
        self.git("switch", "-q", "-c", "fix/z")
        self.commitar("fix(z): corrige o #12", {"z.py": "1\n", "x.md": "2\n"}, "2026-10-17")
        self.git("switch", "-q", "develop")
        self.git("merge", "--no-ff", "-q", "-m", "Merge pull request #13 from o/fix/z", "-m", "fix(z): corrige o #12", "fix/z",
                 data="2026-10-17T13:00:00+00:00")
        cod, linhas = self.corrigidos()
        self.assertRegex(linhas[0], r"^corrigidos: #13 [0-9a-f]{7} evidencia=cita cita=#12 toca=#12 fix\(z\): corrige o #12$")

    def test_ref_inexistente_rc_1_e_a_ref_escolhe_a_linha(self):
        cod, linhas = self.corrigidos("--ref", "nao-existe")
        self.assertEqual(cod, 1)
        self.assertTrue(linhas[0].startswith("corrigidos: ref"), linhas)
        primeiro = self.git("rev-list", "--max-parents=0", "HEAD")
        cod, linhas = self.corrigidos("--ref", primeiro)
        self.assertIn("prs=1 fix=0", linhas[0])


ESCAPE = ["escape", "registrar", "--pedido", "ped-1", "--parecer-final", "docs/qa/ped-1.md", "--achado-por", "uso",
          "--gravidade", "alto", "--controle-que-faltou", "qa", "--nota", "quebra ao abrir o painel"]


class DefeitoEscapado(Raiz):
    """`forge-check escape`: o registro do bug achado depois do parecer final, num formato fixo que o agile-coach lê."""

    def setUp(self):
        super().setUp()
        self.gravar("KANBAN.md", "# Quadro\n")

    def arquivo(self):
        arq = self.tmp / "docs/kanban/escapes.md"
        self.assertTrue(arq.is_file(), "escapes.md não foi gravado")  # falta do arquivo é falha do teste, não erro (F6, E5.5)
        return arq.read_text(encoding="utf-8")

    def com(self, **troca):
        args = list(ESCAPE)
        for chave, valor in troca.items():
            args[args.index("--" + chave.replace("_", "-")) + 1] = valor
        return args

    def test_grava_linha_de_formato_fixo_com_cabecalho_e_hora_real(self):
        cod, saida, _ = self.rodar(*ESCAPE)
        self.assertEqual(cod, 0)
        linhas = self.arquivo().splitlines()
        self.assertEqual(linhas[0], "| data-hora | pedido | parecer-final | achado-por | gravidade | controle-que-faltou | nota | origem |")
        self.assertEqual(linhas[1], "|---|---|---|---|---|---|---|---|")
        self.assertRegex(linhas[2], r"^\| \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| ped-1 \| docs/qa/ped-1\.md \| uso \| alto \| qa \| quebra ao abrir o painel \| nao-classificado \|$")
        self.assertEqual(saida, [linhas[2]])
        self.rodar(*self.com(pedido="ped-2"))
        self.assertEqual(len(self.arquivo().splitlines()), 4)  # só acrescenta

    def test_acrescenta_sem_colar_na_ultima_linha_sem_quebra(self):
        self.gravar("docs/kanban/escapes.md", "| data-hora | x |\n|---|---|\n| 2020-01-01 10:00 | a")
        self.assertEqual(self.rodar(*ESCAPE)[0], 0)
        self.assertEqual(self.arquivo().splitlines()[2], "| 2020-01-01 10:00 | a")
        self.assertTrue(self.arquivo().splitlines()[3].startswith("| 2"))

    def test_recusa_sem_gravar_e_cita_o_campo_nunca_o_valor(self):
        for troca, campo in (({"gravidade": "enorme"}, "--gravidade"), ({"achado_por": "sonho"}, "--achado-por"),
                             ({"controle_que_faltou": "sorte"}, "--controle-que-faltou"), ({"nota": "a|b"}, "--nota"),
                             ({"nota": "a\nb"}, "--nota"), ({"pedido": "a b"}, "--pedido"), ({"parecer_final": "x|y"}, "--parecer-final"),
                             ({"nota": "  "}, "--nota")):
            with self.subTest(troca):
                cod, saida, _ = self.rodar(*self.com(**troca))
                self.assertEqual(cod, 1)
                self.assertTrue(saida[0].startswith("escape:"), saida)
                self.assertTrue(campo in saida[0] or "não podem ser vazios" in saida[0], saida)
                self.assertNotIn("enorme", saida[0])
        self.assertFalse((self.tmp / "docs/kanban/escapes.md").exists())

    def test_sem_quadro_nao_cria_arquivo(self):
        (self.tmp / "KANBAN.md").unlink()
        cod, saida, _ = self.rodar(*ESCAPE)
        self.assertEqual(cod, 1)
        self.assertFalse((self.tmp / "docs/kanban/escapes.md").exists())

    def test_resumo_conta_por_gravidade_e_controle_e_da_a_taxa_sobre_os_pedidos_prontos(self):
        self.rodar(*ESCAPE)
        self.rodar(*self.com(pedido="ped-2", gravidade="critico", controle_que_faltou="nenhum"))
        antigo = "| 2019-01-01 10:00 | velho | docs/qa/v.md | uso | baixo | review | fora da janela |\n"
        (self.tmp / "docs/kanban/escapes.md").write_text(self.arquivo() + antigo, encoding="utf-8")
        agora = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        self.gravar("docs/kanban/historico.md", CABECALHO_HISTORICO + "".join(
            f"| {agora} | {c} | Aguardando sua validação | {para} | x |\n" for c, para in (("A", "Pronto"), ("A", "Pronto"), ("B", "Pronto"),
                                                                                          ("C", "Pronto para fazer"))))
        cod, saida, _ = self.rodar("escape", "resumo")
        self.assertEqual(cod, 0)
        self.assertEqual(saida, ["escapes: gravidade: critico=1 alto=1 medio=0 baixo=0",
                                 "escapes: controle: review=0 seguranca=0 qa=1 conferencia=0 ci=0 nenhum=1",
                                 "escapes: origem: spec=0 ux=0 arquitetura=0 codigo=0 teste=0 brief=0 nao-classificado=2",
                                 "escapes: total: escapes=2 pedidos_prontos=2 taxa=1.00 dias=30"])

    def test_aq1_origem_gravada_na_ultima_coluna_e_o_padrao_e_nao_classificado(self):  # AQ1 T3 (E4): sucesso
        cod, saida, _ = self.rodar(*ESCAPE, "--origem", "codigo")
        self.assertEqual(cod, 0)
        self.assertRegex(saida[0], r"\| quebra ao abrir o painel \| codigo \|$")
        for origem in ("spec", "ux", "arquitetura", "teste", "brief", "nao-classificado"):
            with self.subTest(origem):
                self.assertEqual(self.rodar(*ESCAPE, "--origem", origem)[0], 0)
                self.assertTrue(self.arquivo().splitlines()[-1].endswith(f"| {origem} |"))

    def test_aq1_origem_invalida_e_recusada_sem_gravar_e_sem_ecoar_o_valor(self):  # AQ1 T3 (E4): falha
        for valor in ("design", "Codigo", "", "codigo|x", "spec\nux"):
            with self.subTest(valor):
                cod, saida, _ = self.rodar(*ESCAPE, "--origem", valor)
                self.assertEqual(cod, 1)
                self.assertEqual(len(saida), 1, saida)
                self.assertIn("escape: --origem deve ser um de spec, ux, arquitetura, codigo, teste, brief, nao-classificado", saida[0])
                self.assertNotIn("design", saida[0])
        self.assertFalse((self.tmp / "docs/kanban/escapes.md").exists())

    def test_aq1_resumo_conta_por_origem_e_le_a_linha_antiga_sem_a_coluna_como_nao_classificado(self):
        self.rodar(*ESCAPE, "--origem", "spec")
        self.rodar(*self.com(pedido="ped-2"), "--origem", "codigo")
        self.rodar(*self.com(pedido="ped-3"), "--origem", "codigo")
        hora = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
        antiga = f"| {hora} | velho | docs/qa/v.md | uso | baixo | review | linha de antes da coluna |\n"  # 7 colunas, dentro da janela
        invalida = f"| {hora} | torto | docs/qa/t.md | uso | baixo | review | origem fora da lista | inventada |\n"
        (self.tmp / "docs/kanban/escapes.md").write_text(self.arquivo() + antiga + invalida, encoding="utf-8")
        cod, saida, _ = self.rodar("escape", "resumo")
        self.assertEqual(cod, 0)
        self.assertIn("escapes: origem: spec=1 ux=0 arquitetura=0 codigo=2 teste=0 brief=0 nao-classificado=2", saida)
        self.assertEqual(saida[-1], "escapes: total: escapes=5 pedidos_prontos=0 taxa=- dias=30")
        mod, ctx = carregar_forge_medidas(), carregar_forge_check_m14b().ctx_das_medidas()  # F6, E5.5: mora em bin/forge_medidas.py
        self.assertEqual(mod.origem_do_escape(antiga.strip().strip("|").split("|"), ctx), "nao-classificado")
        self.assertEqual(mod.origem_do_escape(["a"] * 7, ctx), "nao-classificado")
        self.assertEqual(mod.origem_do_escape(["a"] * 7 + ["brief"], ctx), "brief")

    def test_resumo_sem_arquivo_nem_historico_zera_e_a_taxa_e_traco(self):
        cod, saida, _ = self.rodar("escape", "resumo", "--dias", "7")
        self.assertEqual(cod, 0)
        self.assertEqual(saida[-1], "escapes: total: escapes=0 pedidos_prontos=0 taxa=- dias=7")


class RotulosAfrouxaRegraQueEramReais(RepositorioDeTeste):
    """`forge-check afrouxamentos`: a catraca, a mesma do CI, sobre o diff de cada PR rotulado."""

    def setUp(self):
        super().setUp()
        self.iniciar()
        config = {"dono": "dono-do-forge", "invariantes": {"agents/a.md": ["regra importante", "outra regra"]}}
        self.commitar("chore: base", {"tests/config.json": json.dumps(config), "agents/a.md": "regra importante\noutra regra\n",
                                      "tests/catraca.py": "# controle\n"}, "2026-10-10")
        self.commitar("docs(x): texto novo (#20)", {"docs/x.md": "oi\n"}, "2026-10-11")
        config["invariantes"]["agents/a.md"] = ["regra importante"]
        self.commitar("refactor(a): tira uma regra (#21)", {"tests/config.json": json.dumps(config)}, "2026-10-12")
        self.commitar("fix(catraca): ajuste (#22)", {"tests/catraca.py": "controle = 2\n"}, "2026-10-13")

    def afrouxamentos(self, *args):
        cod, linhas, erro = self.rodar("afrouxamentos", *args)
        self.assertNotIn("Traceback", erro)  # F6, E5.3: a queda do script é falha do teste, não erro de índice
        return cod, linhas

    def test_classifica_real_so_protegido_sem_violacao_e_sem_commit(self):
        cod, linhas = self.afrouxamentos("--prs", "20,21,22,#23")
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas[:4], ["afrouxamentos: #20 sem-violacao", "afrouxamentos: #21 real regras=R-CONFORMIDADE",
                                      "afrouxamentos: #22 so-protegido", "afrouxamentos: #23 sem-commit"])
        self.assertRegex(linhas[4], r"^afrouxamentos: total: rotulados=4 real=1 so-protegido=1 sem-violacao=1 sem-commit=1 erro-git=0 ref=[0-9a-f]{7}$")

    def test_le_o_json_do_gh_e_repetido_conta_uma_vez(self):
        self.gravar("rotulados.json", json.dumps([{"number": 21, "title": "x"}, {"number": 20}, {"number": 21}]))
        cod, linhas = self.afrouxamentos("--rotulados", str(self.tmp / "rotulados.json"), "--prs", "22")
        self.assertEqual(cod, 0, linhas)
        self.assertIn("rotulados=3 real=1 so-protegido=1 sem-violacao=1", linhas[-1])

    def test_entrada_ruim_rc_2_sem_gravar_nada_e_sem_ecoar_o_valor(self):
        self.gravar("ruim.json", "{nao e json")
        self.gravar("sem-numero.json", json.dumps([{"id": 1}]))
        self.gravar("negativo.json", json.dumps([{"number": -4}]))
        for args in (("--prs", "20,abc"), ("--prs", "20\nresultado: ok"), (), ("--rotulados", str(self.tmp / "ruim.json")),
                     ("--rotulados", str(self.tmp / "sem-numero.json")), ("--rotulados", str(self.tmp / "negativo.json")),
                     ("--rotulados", str(self.tmp / "nao-existe.json"))):
            with self.subTest(args):
                cod, linhas = self.afrouxamentos(*args)
                self.assertEqual(cod, 2, linhas)
                self.assertEqual(len(linhas), 1, linhas)
                self.assertNotIn("resultado: ok", linhas[0])

    def test_ref_inexistente_rc_1(self):
        cod, linhas = self.afrouxamentos("--prs", "20", "--ref", "nao-existe")
        self.assertEqual(cod, 1)
        self.assertTrue(linhas[0].startswith("afrouxamentos: ref"), linhas)


class RamosDeFalhaDoModuloCorrigidos(RepositorioDeTeste):
    """F6, E5.3: os ramos de falha de `corrigidos` e `afrouxamentos` (bin/forge_corrigidos.py) que não tinham teste."""
    AUSENTE = "forge-check: bin/forge_corrigidos.py ausente ao lado do forge-check; nada feito\n"

    def setUp(self):
        super().setUp()
        self.iniciar()

    def rodar_limpo(self, script, *args):
        """(rc, stdout, stderr) do `script` sobre tmp; Python com -I e ambiente limpo (só PATH e HOME)."""
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.tmp / "home")}
        r = subprocess.run([sys.executable, "-I", str(script), "--raiz", str(self.tmp), *args],
                           capture_output=True, text=True, env=env, cwd=self.tmp)
        return r.returncode, r.stdout, r.stderr

    def rodar_copia(self, arquivos, *args):
        """O forge-check de uma cópia nova em tmp/copia só com `arquivos` de bin/."""
        copia = self.tmp / "copia"
        shutil.rmtree(copia, ignore_errors=True)
        (copia / "bin").mkdir(parents=True)
        for nome in arquivos:
            (copia / "bin" / nome).write_bytes((RAIZ / "bin" / nome).read_bytes())
        return self.rodar_limpo(copia / "bin" / "forge-check", *args)[:2]

    def test_sem_ref_e_sem_commit_cita_a_primeira_ref_padrao(self):
        for cmd, args in (("corrigidos", ()), ("afrouxamentos", ("--prs", "1"))):
            with self.subTest(cmd):
                self.assertEqual(self.rodar_limpo(FORGE_CHECK, cmd, *args), (1, f'{cmd}: ref "origin/develop" não existe ou o git falhou\n', ""))

    def test_rotulados_acima_do_teto_rc_2(self):
        (self.tmp / "grande.json").write_bytes(b" " * (1024 * 1024 + 1))
        self.assertEqual(self.rodar_limpo(FORGE_CHECK, "afrouxamentos", "--rotulados", str(self.tmp / "grande.json")),
                         (2, "afrouxamentos: --rotulados passa de 1048576 bytes\n", ""))

    def test_pr_no_commit_raiz_e_sem_commit(self):
        self.commitar("feat(a): raiz (#5)", {"a.py": "1\n"})
        cod, saida, erro = self.rodar_limpo(FORGE_CHECK, "afrouxamentos", "--prs", "5")
        self.assertEqual((cod, saida.splitlines()[:1], erro), (0, ["afrouxamentos: #5 sem-commit"], ""))

    def test_falha_do_git_na_catraca_e_erro_git(self):
        self.commitar("chore: base", {"a.py": "1\n"})
        self.commitar("fix(a): ajuste (#6)", {"a.py": "2\n"})
        carregador = importlib.machinery.SourceFileLoader("forge_corrigidos_e53", str(RAIZ / "bin" / "forge_corrigidos.py"))
        modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(carregador.name, carregador))
        carregador.exec_module(modulo)
        fc = carregar_forge_check_m14b()
        marca = "o rótulo não libera esta violação"
        catraca = types.SimpleNamespace(NAO_LIBERAVEL=marca, violacoes_das_regras=lambda raiz, base, head: [f"git: o diff falhou; {marca}"],
                                        arquivo_da_violacao=lambda v: None)
        ctx = {"git": fc.git, "sha_do_commit": fc.sha_do_commit, "nome_seguro": fc.nome_seguro, "sem_controle": fc.sem_controle,
               "carregar_catraca": lambda: catraca}
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            cod = modulo.cmd_afrouxamentos(self.tmp, "HEAD", "6", None, ctx)
        linhas = saida.getvalue().splitlines()
        self.assertEqual((cod, linhas[:1]), (0, ["afrouxamentos: #6 erro-git"]))
        self.assertIn(" erro-git=1 ", linhas[-1])

    def test_copia_sem_a_catraca_rc_1(self):
        self.commitar("fix(a): ajuste (#6)", {"a.py": "1\n"})
        self.assertEqual(self.rodar_copia(("forge-check", "forge_corrigidos.py"), "afrouxamentos", "--prs", "6"),
                         (1, "afrouxamentos: não carreguei tests/catraca.py\n"))

    def test_copia_avulsa_sem_o_modulo_sai_com_2_nos_dois(self):
        self.commitar("fix(a): ajuste (#6)", {"a.py": "1\n"})
        for args in (("corrigidos",), ("afrouxamentos", "--prs", "6")):
            with self.subTest(args):
                self.assertEqual(self.rodar_copia(("forge-check",), *args), (2, self.AUSENTE))


class TextosDizemQuandoCadaMedidaRoda(unittest.TestCase):
    """O Jarvis e o agile-coach dizem quando cada medida da M14b roda; sem o texto, a ferramenta existe e ninguém a roda."""
    RAIZ = Path(__file__).resolve().parent.parent

    def texto(self, rel):
        return (self.RAIZ / rel).read_text(encoding="utf-8")

    def test_jarvis_roda_custo_com_pedido_esperas_e_registra_escape(self):
        jarvis = texto_do_jarvis(self.RAIZ)
        for trecho in ("forge-check transcricao custo --entregas --entrega <pedido> --pedido <pedido>", "forge-check esperas --pedido <pedido>",
                       "forge-check escape registrar", "forge-check movimento"):
            self.assertIn(trecho, jarvis)

    def test_agile_coach_roda_a_linha_de_base_na_retrospectiva(self):
        coach = self.texto("agents/agile-coach.md")
        for trecho in ("forge-check esperas", "forge-check escape resumo", "forge-check escape registrar", "forge-check corrigidos",
                       "forge-check afrouxamentos --rotulados", "Linha de base (M14b)",
                       "forge-check decisoes --sem-cartao", "forge-check transcricao trava", "forge-check transcricao avisos --amostra"):
            self.assertIn(trecho, coach)

    def test_cada_medida_esta_na_tabela_de_metricas_e_no_uso_do_forge_check(self):
        tabela, uso = self.texto("docs/melhoria-continua.md"), self.texto("bin/forge-check")
        for comando in ("forge-check esperas", "forge-check corrigidos", "forge-check afrouxamentos", "forge-check escape resumo",
                        "forge-check transcricao trava", "forge-check transcricao avisos"):
            self.assertIn(comando, tabela)
        for comando in ("forge-check esperas", "forge-check corrigidos", "forge-check afrouxamentos", "forge-check escape registrar", "forge-check escape resumo",
                        "forge-check transcricao trava", "forge-check transcricao avisos"):
            self.assertIn(comando, uso.split('"""')[1])


class MedidaM2b(Raiz):
    """M15 E5c (decisão 9): `provas medida` conta as conferências de entrega com mérito que o CI com a M15 pegaria e as só do conferente."""
    BRIEF = ("# b\n\n## Pronto quando\n- PQ-2 (cmd): `python3 -m unittest tests.test_x` · espera: igual 'ok'\n"
             "- PQ-1 (cmd): `grep -c x arquivo` · espera: igual '1'\n- PQ-3 (arquivo): `git rev-parse HEAD`\n- PQ-4 (cmd): sem crase · espera: rc=0\n")
    CABECALHO = "| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota | classe | autor |\n|---|---|---|---|---|---|---|---|---|---|\n"

    def medir(self, *linhas, desde=()):
        self.gravar("docs/briefs/p-tech-lead-1.md", self.BRIEF)
        self.gravar("docs/kanban/conferencias.md", self.CABECALHO + "".join(f"| {l} |\n" for l in linhas))
        cod, saida, _ = self.rodar("provas", "medida", *desde)
        self.assertEqual(cod, 0, saida)
        return saida

    def linha(self, resultado, merito="s", brief="p-tech-lead-1", modo="entrega", hora="2026-11-06 10:00"):
        return f"{hora} | p | {brief} | {modo} | 1 | {resultado} | {merito} | nota | implementacao | destino"

    def total(self, n, k, j, i):
        return f"m2b: conferências de entrega com mérito={n}; pegas só pelo conferente={k}; que o CI (M15) pegaria={j}; ilegíveis={i}"

    def test_pq_unittest_da_lista_do_script_e_ci(self):
        saida = self.medir(self.linha("não cumpriu (PQ-2)", merito="parcial"))
        self.assertEqual(saida, ["m2b: 2026-11-06 10:00 · p-tech-lead-1 · ci · PQ-2=ci", self.total(1, 0, 1, 0)])

    def test_pq_fora_da_lista_nao_cmd_ou_sem_pq_e_so_do_conferente(self):
        for resultado, detalhe in (("não cumpriu (PQ-1)", "PQ-1=so-conferente"), ("não cumpriu (PQ-3)", "PQ-3=so-conferente"),
                                   ("não cumpriu (PQ-9)", "PQ-9=so-conferente"), ("não cumpriu (PQ-4)", "PQ-4=so-conferente"), ("escopo: fora", "sem PQ=so-conferente"),
                                   ("não cumpriu (PQ-2, PQ-1)", "PQ-2=ci, PQ-1=so-conferente")):
            with self.subTest(resultado=resultado):
                saida = self.medir(self.linha(resultado))
                self.assertEqual(saida, [f"m2b: 2026-11-06 10:00 · p-tech-lead-1 · so-conferente · {detalhe}", self.total(1, 1, 0, 0)])

    def test_so_conta_entrega_que_nao_aprovou_com_merito_em_linha_de_10_celulas(self):
        saida = self.medir(self.linha("não cumpriu (PQ-2)", merito="n"), self.linha("cumpriu"), self.linha("não cumpriu (PQ-2)", modo="brief"),
                           self.linha("não cumpriu (PQ-2)").rsplit(" | ", 1)[0], self.linha("não cumpriu (PQ-2)", hora="ontem"))
        self.assertEqual(saida, [self.total(0, 0, 0, 0)])

    def test_desde_corta_as_conferencias_antigas(self):
        saida = self.medir(self.linha("não cumpriu (PQ-2)", hora="2026-11-01 09:00"), self.linha("não cumpriu (PQ-1)"), desde=("--desde", "2026-11-06"))
        self.assertEqual(saida[-1], self.total(1, 1, 0, 0))

    def test_brief_ausente_ou_de_nome_inseguro_e_ilegivel_sem_ecoar_o_resultado(self):
        saida = self.medir(self.linha("não cumpriu (PQ-2) SEGREDO", brief="p-tech-lead-9"), self.linha("não cumpriu (PQ-2)", brief="../briefs/p-tech-lead-1"))
        self.assertEqual(saida, ["m2b: 2026-11-06 10:00 · p-tech-lead-9 · ilegível · brief=ilegível",
                                 "m2b: 2026-11-06 10:00 · ? · ilegível · brief=ilegível", self.total(2, 0, 0, 2)])

    def test_registro_em_link_ou_sem_o_script_do_ci_nao_verifica(self):
        self.gravar("docs/kanban/outro.md", self.CABECALHO)
        (self.tmp / "docs/kanban/conferencias.md").symlink_to("outro.md")
        cod, saida, _ = self.rodar("provas", "medida")
        self.assertEqual((cod, saida), (2, ["m2b: não verificável: docs/kanban/conferencias.md é link simbólico"]))
        copia = self.tmp / "plugin" / "bin" / "forge-check"
        copia.parent.mkdir(parents=True)
        copia.write_bytes(Path(FORGE_CHECK_M2B).read_bytes())
        r = subprocess.run([sys.executable, "-I", str(copia), "--raiz", str(self.tmp), "provas", "medida"], capture_output=True, text=True,
                           env={"PATH": "/usr/bin:/bin", "HOME": str(self.tmp / "home")})
        self.assertEqual((r.returncode, r.stdout), (2, "provas: não verificável (scripts/reexecutar-provas.py ausente)\n"))

    def test_agile_coach_leva_a_medida_ao_cartao_na_retrospectiva_da_042(self):
        coach = (Path(FORGE_CHECK_M2B).parent.parent / "agents" / "agile-coach.md").read_text(encoding="utf-8")
        self.assertIn("forge-check provas medida --desde <abertura da 0.41>", coach)
        self.assertIn("EST-M2B-REAVALIAR", coach)


class EsperaDaTrava(Raiz):
    """LAC-L1: `forge-check transcricao trava` mede a espera da trava pesada (R-TETO) nas transcrições, só com papel e números (T-14)."""
    CMD, BLOQUEIO = "bin/x SEGREDO123", "R-TETO: tarefa pesada de outra sessão ou agente há 3 min (`bin/x SEGREDO123`)"

    def chamada(self, uso, s, comando=CMD, texto=BLOQUEIO):
        base = {"isSidechain": True, "agentId": "a1", "agentType": "forge:qa-engineer", "sessionId": "s",
                "timestamp": (datetime.datetime(2026, 11, 6, 10, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=s)).isoformat()}
        return [{**base, "type": "assistant", "message": {"content": [{"type": "tool_use", "id": uso, "name": "Bash", "input": {"command": comando}}]}},
                {**base, "type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": uso, "is_error": bool(texto), "content": texto or "ok"}]}}]

    def trava(self, *chamadas, alvo="t", rc=0):
        sujeira = [{"type": "system"}, {"type": "assistant", "message": {"content": ["x", {"type": "tool_use", "id": "z", "name": "Bash", "input": {"command": "y"}},
                                                                                {"type": "tool_result", "tool_use_id": "w"}, {"type": "tool_result", "tool_use_id": "z", "is_error": True, "content": self.BLOQUEIO}]}}]
        if chamadas:
            self.gravar(f"{alvo}/s.jsonl", "".join(json.dumps(o) + "\n" for o in sujeira + [o for c in chamadas for o in c]))
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "transcricao", "trava", str(self.tmp / alvo)], capture_output=True, text=True,
                           env={"HOME": str(self.tmp), "PATH": "/usr/bin:/bin"})
        self.assertEqual(r.returncode, rc, r.stdout + r.stderr)
        return r.stdout + r.stderr

    def test_o_mesmo_comando_que_passou_fecha_a_espera_exata_sem_imprimir_o_comando(self):
        saida = self.trava(self.chamada("t1", 0), self.chamada("t2", 30), self.chamada("t3", 60, comando="ls", texto=""),
                           self.chamada("t4", 120, comando=" bin/x  SEGREDO123", texto=""))
        self.assertIn("trava: papel forge:qa-engineer bloqueios 2 espera_s 120 exata\n", saida)
        self.assertIn("trava: total: bloqueios 2 episodios 1 mediana_s 120 maximo_s 120 por_dia 1.0\ntrava: alta: sim\n", saida)
        for segredo in ("SEGREDO123", hashlib.sha256(self.CMD.encode()).hexdigest()[:12]):
            self.assertNotIn(segredo, saida)

    def test_bloqueio_sem_passagem_e_piso_e_baixa(self):
        saida = self.trava(self.chamada("t1", 0), self.chamada("t2", 50))
        self.assertIn("bloqueios 2 espera_s 50 piso\ntrava: total: bloqueios 2 episodios 1 mediana_s 50 maximo_s 50 por_dia 1.0\ntrava: alta: nao\n", saida)

    def test_onze_minutos_separam_episodios_e_cinco_nao(self):
        saida = self.trava(self.chamada("t1", 0), self.chamada("t2", 660), self.chamada("t3", 960), self.chamada("t4", 1000, texto=""))
        self.assertIn("bloqueios 1 espera_s 0 piso\ntrava: papel forge:qa-engineer bloqueios 2 espera_s 340 exata\n", saida)

    def test_o_mesmo_tool_use_id_conta_um_e_outra_recusa_do_r_teto_nao_conta(self):
        saida = self.trava(self.chamada("t1", 0), self.chamada("t1", 0), self.chamada("t2", 5, texto="R-TETO: 9 agentes em segundo plano"))
        self.assertIn("trava: total: bloqueios 1 episodios 1 ", saida)

    def test_sem_bloqueio_sem_jsonl_e_sem_caminho(self):
        self.assertIn("trava: total: bloqueios 0 episodios 0 mediana_s 0 maximo_s 0 por_dia 0.0\ntrava: alta: nao", self.trava(self.chamada("t1", 0, texto="")))
        (self.tmp / "vazia").mkdir()
        self.assertIn("trava: nenhum arquivo .jsonl", self.trava(alvo="vazia", rc=1))
        self.assertIn("trava: caminho inexistente", self.trava(alvo="nada", rc=1))



VIGIA = "Forge: 1 contorno — contorno: SEGREDO123 (.forge/run/violacoes.jsonl)"
DOUTOR = "Forge doutor: 1 coisa para ver — versão atrasada SEGREDO123 (rode: forge doutor)"


def aviso(texto, dia="2026-10-22", evento="Stop", tipo="hook_system_message"):
    """A linha que o Claude Code grava para o `systemMessage` de um hook (sonda: `type: attachment`, `attachment.type: hook_system_message`)."""
    return {"type": "attachment", "timestamp": f"{dia}T10:00:00.000Z", "sessionId": "s",
            "attachment": {"type": tipo, "content": texto, "hookName": evento, "hookEvent": evento}}


class AvisosDosHooks(Raiz):
    """LAC-L2 (E4a): `transcricao avisos` conta os avisos do doutor e do vigia por hook, evento e dia; a saída nunca traz o texto (T-14)."""

    def avisos(self, *objetos):
        self.gravar("t/s.jsonl", "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in objetos))
        cod, linhas, erro = self.rodar("transcricao", "avisos", str(self.tmp / "t"))
        self.assertNotIn("SEGREDO123", "\n".join(linhas) + erro)
        return cod, linhas

    def test_dois_do_vigia_e_um_do_doutor_por_hook_evento_e_dia(self):
        cod, linhas = self.avisos(aviso(VIGIA), aviso(VIGIA.replace("1 contorno", "2 contornos"), "2026-10-23", "SubagentStop"),
                                  aviso(DOUTOR, evento="PostToolUse"))
        self.assertEqual(cod, 0, linhas)
        self.assertEqual(linhas, ["avisos: hook doutor avisos=1 unicos=1 reincidencia=0", "avisos: hook vigia avisos=2 unicos=2 reincidencia=0",
                                  "avisos: evento Stop doutor=0 vigia=1", "avisos: evento SubagentStop doutor=0 vigia=1",
                                  "avisos: evento outro doutor=1 vigia=0", "avisos: dia 2026-10-22 doutor=1 vigia=1",
                                  "avisos: dia 2026-10-23 doutor=0 vigia=1", "avisos: total: avisos=3 unicos=3 reincidencia=0",
                                  "avisos: com_acao=0"])

    def test_mesmo_texto_no_mesmo_dia_reincide_e_em_dias_diferentes_nao(self):
        cod, linhas = self.avisos(aviso(VIGIA), aviso(VIGIA, evento="SubagentStop"), aviso(DOUTOR), aviso(DOUTOR, "2026-10-23"))
        self.assertIn("avisos: hook vigia avisos=2 unicos=1 reincidencia=1", linhas)
        self.assertIn("avisos: hook doutor avisos=2 unicos=1 reincidencia=0", linhas)
        self.assertIn("avisos: total: avisos=4 unicos=2 reincidencia=1", linhas)

    def test_aviso_de_outro_hook_ou_de_outro_registro_nao_conta(self):
        cod, linhas = self.avisos(aviso("Forge: versão nova SEGREDO123"), aviso("Forge: x (.forge/run/violacoes.jsonl) SEGREDO123"),
                                  aviso(DOUTOR, tipo="hook_additional_context"), dict(aviso(DOUTOR), type="user"),
                                  dict(aviso(DOUTOR), timestamp="ontem SEGREDO123"), {"type": "attachment", "attachment": DOUTOR})
        self.assertEqual(linhas, ["avisos: hook doutor avisos=1 unicos=1 reincidencia=0", "avisos: hook vigia avisos=0 unicos=0 reincidencia=0",
                                  "avisos: evento Stop doutor=1 vigia=0", "avisos: dia sem_data doutor=1 vigia=0",
                                  "avisos: total: avisos=1 unicos=1 reincidencia=0", "avisos: com_acao=0"])

    def test_pasta_sem_jsonl_e_caminho_inexistente_dao_rc_1(self):
        (self.tmp / "vazia").mkdir()
        for alvo, inicio in (("vazia", "avisos: nenhum arquivo .jsonl em "), ("nao-existe", "avisos: caminho inexistente: "),
                             (None, f"avisos: caminho inexistente: {self.tmp / 'home' / '.claude' / 'projects'}/")):  # sem alvo: a pasta padrão
            cod, linhas, _ = self.rodar("transcricao", "avisos", *([str(self.tmp / alvo)] if alvo else []))
            self.assertEqual(cod, 1, linhas)
            self.assertTrue(linhas[0].startswith(inicio), linhas)


def chamada(comando, texto=None, tipo="assistant"):
    """Uma mensagem com uma chamada de ferramenta (e, se dado, um texto antes dela)."""
    return {"type": tipo, "message": {"content": ([{"type": "text", "text": texto}] if texto else []) +
                                      [{"type": "tool_use", "name": "Bash", "input": {"command": comando}}]}}


class AvisosComAcao(Raiz):
    """LAC-L2 (E4b): o aviso tem ação quando uma das 3 chamadas seguintes da sessão age sobre ele; a `--amostra` só traz id e tipo (T-14)."""

    def medir(self, arquivos, *opcoes):
        for nome, objetos in arquivos.items():
            self.gravar(f"t/{nome}.jsonl", "".join(json.dumps(o, ensure_ascii=False) + "\n" for o in objetos))
        cod, linhas, erro = self.rodar("transcricao", "avisos", str(self.tmp / "t"), *opcoes)
        self.assertNotIn("SEGREDO123", "\n".join(linhas) + erro)
        self.assertEqual(cod, 0, linhas)
        return linhas

    def test_acao_na_segunda_chamada_conta_e_na_quarta_nao(self):
        estranhos = [{"type": "assistant", "message": "x"}, {"type": "assistant", "message": {"content": 5}},
                     {"type": "assistant", "message": {"content": ["solto"]}}, chamada("ls", "o doutor", tipo="user")]
        for agir in ("cat .forge/run/violacoes.jsonl", "forge doutor --rapido", "bin/forge-doutor"):
            self.assertIn("avisos: com_acao=1", self.medir({"a": [aviso(VIGIA), chamada("ls"), chamada(agir), chamada("ls")],
                                                             "b": [aviso(VIGIA), *estranhos, chamada("ls"), chamada("ls"), chamada("ls"), chamada(agir)]}))
        self.assertIn("avisos: com_acao=2", self.medir({"a": [aviso(DOUTOR), chamada("ls", "nada"), chamada("ls"), chamada("ls", "O Vigia avisou")],
                                                         "b": [aviso(VIGIA), chamada("ls", "vou ver o doutor")]}))

    def test_um_texto_sem_vigia_nem_doutor_nao_e_acao(self):  # F6, E5.2: um bloco só, sem ação, deixa o aviso sem ação
        texto = {"type": "assistant", "message": {"content": [{"type": "text", "text": "seguindo"}]}}
        self.assertIn("avisos: com_acao=0", self.medir({"a": [aviso(VIGIA), texto]}))

    def test_amostra_da_ids_deterministicos_sem_o_texto_do_aviso(self):
        arquivos = {"a": [aviso(VIGIA), aviso(DOUTOR)], "b": [], "c": [aviso(VIGIA, "2026-10-23")]}
        amostra = [l for l in self.medir(arquivos, "--amostra", "9") if "amostra" in l]
        self.assertEqual(amostra, ["avisos: amostra s1#1 vigia", "avisos: amostra s1#2 doutor", "avisos: amostra s3#1 vigia"])
        self.assertEqual([l for l in self.medir(arquivos, "--amostra", "2") if "amostra" in l], amostra[:2])
        self.assertFalse([l for l in self.medir(arquivos, "--amostra", "-1") + self.medir(arquivos) if "amostra" in l])


if __name__ == "__main__":
    unittest.main()
