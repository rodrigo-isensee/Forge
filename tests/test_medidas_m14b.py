"""MEDIR-M14B: as medidas que dão a linha de base do processo antes de qualquer afrouxamento (esperas, PR `fix` que corrige PR
mesclado, defeito escapado, rótulo `afrouxa-regra` que era afrouxamento real) e o casamento do `--pedido` do custo com os cartões."""
import datetime
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from test_voltas import Raiz  # noqa: E402

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


class Esperas(Raiz):
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
        self.assertEqual(linhas[0], "esperas: K-2 outra inicio=2026-10-22T13:00:00-03:00 minutos=20")
        self.assertEqual(linhas[-1], "esperas: total: dono=1 minutos_dono=50 credencial=0 minutos_credencial=0 outra=1 minutos_outra=20 abertas=0 cartoes=2")

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
        self.gravar("KANBAN.md", "# Quadro\n")
        (self.tmp / "docs/kanban/historico.md").unlink()
        self.assertEqual(self.rodar("movimento", "K-9", "--de", "Em andamento", "--para", "Aguardando o dono", "--motivo", "validar")[0], 0)
        cod, linhas, _ = self.rodar("esperas")
        self.assertEqual(cod, 0)
        self.assertRegex(linhas[0], r"^esperas: K-9 dono inicio=\S+ minutos=aberta$")


class RepositorioDeTeste(Raiz):
    """Um repositório git descartável, com commits de data fixa (a hora entra nas medidas por janela)."""

    def git(self, *args, data=None):
        env = dict(os.environ, GIT_AUTHOR_NAME="Teste", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="Teste",
                   GIT_COMMITTER_EMAIL="t@example.com", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_SYSTEM="/dev/null")
        if data:
            env.update(GIT_AUTHOR_DATE=data, GIT_COMMITTER_DATE=data)
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
        cod, linhas, _ = self.rodar("corrigidos", *args)
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
        return (self.tmp / "docs/kanban/escapes.md").read_text(encoding="utf-8")

    def com(self, **troca):
        args = list(ESCAPE)
        for chave, valor in troca.items():
            args[args.index("--" + chave.replace("_", "-")) + 1] = valor
        return args

    def test_grava_linha_de_formato_fixo_com_cabecalho_e_hora_real(self):
        cod, saida, _ = self.rodar(*ESCAPE)
        self.assertEqual(cod, 0)
        linhas = self.arquivo().splitlines()
        self.assertEqual(linhas[0], "| data-hora | pedido | parecer-final | achado-por | gravidade | controle-que-faltou | nota |")
        self.assertEqual(linhas[1], "|---|---|---|---|---|---|---|")
        self.assertRegex(linhas[2], r"^\| \d{4}-\d{2}-\d{2} \d{2}:\d{2} \| ped-1 \| docs/qa/ped-1\.md \| uso \| alto \| qa \| quebra ao abrir o painel \|$")
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
                                 "escapes: total: escapes=2 pedidos_prontos=2 taxa=1.00 dias=30"])

    def test_resumo_sem_arquivo_nem_historico_zera_e_a_taxa_e_traco(self):
        cod, saida, _ = self.rodar("escape", "resumo", "--dias", "7")
        self.assertEqual(cod, 0)
        self.assertEqual(saida[-1], "escapes: total: escapes=0 pedidos_prontos=0 taxa=- dias=7")


if __name__ == "__main__":
    unittest.main()
