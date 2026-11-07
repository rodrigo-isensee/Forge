"""T-1: `forge-check voltas`, rodadas de brief em `transcricao custo --entregas` e as pastas padrão de transcrições."""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")

HISTORICO = """| Data/hora | Cartão | De | Para | Motivo |
|---|---|---|---|---|
| 2026-10-17T10:00:00-03:00 | XPTO | Pronto para fazer | Em andamento | brief aprovado |
| 2026-10-17T10:10:00-03:00 | XPTO | Em andamento | Conferência | entrega |
| 2026-10-17T10:12:00-03:00 | XPTO | Conferência | Review | conferência não cumpriu (PQ-2) |
| 2026-10-17T10:15:00-03:00 | XPTO | Review | Em andamento | review e segurança reprovaram |
| 2026-10-17T10:30:00-03:00 | XPTO | Em andamento | Conferência | retrabalho entregue |
| 2026-10-17T10:36:00-03:00 | XPTO | Conferência | Review | conferido; revalidação de review |
| 2026-10-17T10:50:00-03:00 | XPTO | Review | Em andamento | ajuste qualquer sem palavra-chave |
| 2026-10-17T10:58:00-03:00 | XPTO | Em andamento | Review | ajuste entregue |
| 2026-10-17T11:00:00-03:00 | XPTO | Em andamento | Aguardando o dono | escrita barrada pelo hook |
| 2026-10-17T11:20:00-03:00 | XPTO | Aguardando o dono | Em andamento | dono decidiu |
| 2026-10-17T11:30:00-03:00 | OUTRO | Pronto para fazer | Em andamento | brief aprovado |
- 2026-10-17T11:31:00-03:00 linha de lista, não é tabela
| sem-hora | XPTO | Review | Em andamento | reprovou sem hora ISO |
"""

CONFERENCIAS = """| data-hora | pedido | brief | modo | rodada | resultado | mérito | nota |
|---|---|---|---|---|---|---|---|
| 2026-10-15 21:00 | xpto | xpto-tech-lead-1 | brief | 1 | reprovado | s | |
| 2026-10-15 21:07 | xpto | xpto-tech-lead-1 | brief | 2 | aprovado | — | |
| 2026-10-15 21:20 | xpto | xpto-tech-lead-1 | entrega | 1 | aprovado | — | modo entrega não conta |
| 2026-10-15 22:00 | outro | outro-qa-engineer-1 | brief | 1 | aprovado | — | |
"""


class Raiz(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-voltas-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def gravar(self, rel, texto=""):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def rodar(self, *args, home=None):
        env = dict(os.environ, HOME=str(home or self.tmp / "home"))
        r = subprocess.run([sys.executable, FORGE_CHECK, "--raiz", str(self.tmp), *args],
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout.splitlines(), r.stderr


class Voltas(Raiz):
    def setUp(self):
        super().setUp()
        self.gravar("docs/kanban/historico.md", HISTORICO)

    def test_reversoes_de_suposicao_por_pedido(self):  # L11 (OK-6): o placar da escolha provisória que o dono trocou
        self.gravar("docs/pedidos/XPTO.md", "# p\n\n## Histórico\n- 2026-10-17 10:00: aberto\n- 2026-10-17 11:00: suposição revertida: a fila\n"
                    "- 2026-10-17 12:00: Suposição revertida: o banco\n- 2026-10-17 12:30: suposição mantida\n")
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertIn("voltas: XPTO reversoes=2", linhas)
        self.gravar("docs/pedidos/XPTO.md", "# p\n\n## Histórico\n- 2026-10-17 10:00: aberto\n")
        self.assertFalse([l for l in self.rodar("voltas", "--pedido", "xpto")[1] if "reversoes" in l])

    def test_voltas_de_um_pedido_em_linhas_fixas_com_minutos(self):
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, [
            "voltas: XPTO conferencia inicio=2026-10-17T10:12:00-03:00 minutos=18",
            "voltas: XPTO review inicio=2026-10-17T10:15:00-03:00 minutos=21",
            "voltas: XPTO revalidacao inicio=2026-10-17T10:36:00-03:00 minutos=22",
            "voltas: XPTO nao-classificado inicio=2026-10-17T10:50:00-03:00 minutos=8",
            "voltas: XPTO barrada inicio=2026-10-17T11:00:00-03:00 minutos=20",
            "voltas: XPTO resumo: brief=0 conferencia=1 review=1 revalidacao=1 barrada=1 nao-classificado=1 "
            "minutos=66 construcao=10 razao=6.60",  # união: conferência e review se sobrepõem; revalidação e ajuste também
            "voltas: total: pedidos=1 voltas=5 minutos=66",
        ])

    def test_dois_relogios_do_pedido_que_chegou_a_develop(self):  # L49 (D-4): aberto -> develop e pronto para fazer -> develop (meta 30 min)
        self.gravar("docs/kanban/historico.md", "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"
                    "| 2026-10-17T08:00:00-03:00 | P1 | Backlog | Empatizar e definir | aberto |\n"
                    "| 2026-10-17T08:40:00-03:00 | P1 | Empatizar e definir | Pronto para fazer | discovery |\n"
                    "| 2026-10-17T08:50:00-03:00 | P1 | Pronto para fazer | Em andamento | brief |\n"
                    "| 2026-10-17T09:10:00-03:00 | P1 | Em andamento | Aguardando sua validação | PR |\n"
                    "| 2026-10-17T09:30:00-03:00 | P1 | Aguardando sua validação | Pronto | merge |\n"
                    "| 2026-10-17T10:00:00-03:00 | P2 | Pronto para fazer | Em andamento | brief |\n"
                    "| 2026-10-17T11:00:00-03:00 | P2 | Em andamento | Pronto | feito |\n"
                    "| 2026-10-17T12:00:00-03:00 | P3 | Pronto para fazer | Em andamento | aberto |\n")
        _, p1, _ = self.rodar("voltas", "--pedido", "p1")
        self.assertIn("voltas: P1 relogios: aberto_ate_develop=70 pronto_ate_develop=30 meta=30 dentro=sim", p1)
        _, p2, _ = self.rodar("voltas", "--pedido", "p2")
        self.assertIn("voltas: P2 relogios: aberto_ate_develop=60 pronto_ate_develop=60 meta=30 dentro=nao", p2)
        cod3, p3, _ = self.rodar("voltas", "--pedido", "p3")
        self.assertEqual(cod3, 0, p3)
        self.assertFalse([l for l in p3 if "relogios" in l], p3)  # ainda não chegou à develop: sem relógio

    def test_cartao_que_nunca_esteve_em_pronto_para_fazer_tem_so_o_relogio_aberto(self):  # L49
        self.gravar("docs/kanban/historico.md", "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"
                    "| 2026-10-17T08:00:00-03:00 | P4 | Backlog | Em andamento | x |\n"
                    "| 2026-10-17T08:05:00-03:00 | P4 | Em andamento | Pronto | y |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "p4")
        self.assertIn("voltas: P4 relogios: aberto_ate_develop=5 pronto_ate_develop=- meta=30 dentro=-", linhas)

    def test_pedido_que_andou_sem_volta_traz_o_relogio_tambem_sem_pedido(self):  # L49, A5 do review: a tabela por release não perde o pedido sem volta
        self.gravar("docs/kanban/historico.md", "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"
                    "| 2026-10-17T08:00:00-03:00 | P5 | Backlog | Em andamento | x |\n"
                    "| 2026-10-17T08:05:00-03:00 | P5 | Em andamento | Pronto | y |\n")
        _, todos, _ = self.rodar("voltas")
        self.assertIn("voltas: P5 relogios: aberto_ate_develop=5 pronto_ate_develop=- meta=30 dentro=-", todos)
        _, um, _ = self.rodar("voltas", "--pedido", "p5")
        self.assertIn("voltas: P5 relogios: aberto_ate_develop=5 pronto_ate_develop=- meta=30 dentro=-", um)

    def test_pedido_sem_voltas_so_aparece_com_pedido_explicito(self):
        _, todos, _ = self.rodar("voltas")
        self.assertFalse(any("OUTRO" in l for l in todos), todos)
        _, um, _ = self.rodar("voltas", "--pedido", "outro")
        self.assertEqual(um[0], "voltas: OUTRO resumo: brief=0 conferencia=0 review=0 revalidacao=0 barrada=0 "
                                "nao-classificado=0 minutos=0 construcao=- razao=-")

    def test_linha_de_lista_e_linha_sem_hora_iso_sao_ignoradas(self):
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(sum(1 for l in linhas if l.startswith("voltas: XPTO review ")), 1)

    def test_volta_aberta_e_motivo_fora_do_vocabulario_nao_somem(self):
        self.gravar("docs/kanban/historico.md", HISTORICO + "| 2026-10-17T12:00:00-03:00 | XPTO | Review | Em andamento | reprovou de novo |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertIn("voltas: XPTO review inicio=2026-10-17T12:00:00-03:00 minutos=aberta", linhas)
        self.assertIn("voltas: XPTO nao-classificado inicio=2026-10-17T10:50:00-03:00 minutos=8", linhas)

    def test_classificacao_por_coluna_e_motivo(self):
        carga = subprocess.run([sys.executable, "-c", (
            "import importlib.machinery as m, importlib.util as u, sys\n"
            f"l = m.SourceFileLoader('fc', {FORGE_CHECK!r}); s = u.spec_from_loader('fc', l); mod = u.module_from_spec(s); l.exec_module(mod)\n"
            "c = mod.classificar_volta\n"
            "print(c('Conferência', 'Review', 'não cumpriu'), c('Conferência', 'Review', 'conferido'), c('Review', 'Review', 'reprovou'),"
            " c('Em andamento', 'Aguardando o dono', 'barrada'), c('Review', 'Em andamento', 'x'), c('Em andamento', 'Conferência', 'x'))")],
            capture_output=True, text=True)
        self.assertEqual(carga.stdout.split(), ["conferencia", "None", "review", "barrada", "nao-classificado", "None"], carga.stderr)

    def test_sem_historico_avisa_e_nao_quebra(self):
        (self.tmp / "docs/kanban/historico.md").unlink()
        cod, linhas, erro = self.rodar("voltas")
        self.assertEqual((cod, linhas), (0, ["voltas: total: pedidos=0 voltas=0 minutos=0"]))
        self.assertIn("historico.md ausente", erro)

    def test_so_le_nao_escreve(self):
        antes = HISTORICO
        self.rodar("voltas")
        self.assertEqual((self.tmp / "docs/kanban/historico.md").read_text(encoding="utf-8"), antes)


class RodadasDeBrief(Raiz):
    def test_conferencias_manda_quando_ha_linhas_e_so_conta_modo_brief(self):
        self.gravar("docs/kanban/conferencias.md", CONFERENCIAS)
        self.gravar("docs/briefs/xpto-tech-lead-1.md")
        self.gravar("docs/briefs/xpto-tech-lead-2.md")
        self.gravar("docs/kanban/historico.md", "")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(linhas[0], "voltas: xpto brief inicio=2026-10-15 21:07 minutos=7 ref=xpto-tech-lead-1")
        self.assertIn("brief=1 ", linhas[1])

    def test_sem_conferencias_vale_o_disco_dos_briefs_por_destino(self):
        for nome in ("xpto-tech-lead-1", "xpto-tech-lead-2", "xpto-tech-lead-3", "xpto-qa-engineer-1", "xptoz-tech-lead-1", "xpto-2-tech-lead-1"):
            self.gravar(f"docs/briefs/{nome}.md")
        self.gravar("docs/kanban/historico.md", "")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertFalse([l for l in linhas if " brief inicio=" in l], linhas)  # delegações não são voltas
        self.assertIn("brief=0 ", linhas[0])
        self.assertTrue(linhas[0].startswith("voltas: xpto resumo:"), linhas)

    def test_sem_conferencias_nem_briefs_o_historico_nao_inventa_rodada(self):
        self.gravar("docs/kanban/historico.md", "| 2026-10-17T10:00:00-03:00 | xpto | Review | Review | segurança rodada 3 reprovou |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertFalse([l for l in linhas if " brief inicio=" in l], linhas)

    def test_voltas_sobrepostas_nao_somam_minutos_em_dobro(self):
        self.gravar("docs/kanban/historico.md",
                    "| 2026-10-17T10:00:00-03:00 | xpto | Conferência | Review | revalidação |\n"
                    "| 2026-10-17T10:10:00-03:00 | xpto | Review | Review | rodada 3 reprovou |\n"
                    "| 2026-10-17T10:20:00-03:00 | xpto | Review | Em andamento | retrabalho delegado |\n"
                    "| 2026-10-17T11:00:00-03:00 | xpto | Em andamento | Review | entregue |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(len([l for l in linhas if l.startswith("voltas: xpto review ")]), 1, linhas)
        self.assertIn("minutos=60 ", linhas[-2])  # revalidação 10:00-11:00 contém a volta de review (10:20-11:00)

    def test_revalidacao_do_fluxo_paralelo_fecha_na_chegada_a_review_sem_conferencia(self):
        """Q-1: Em andamento -> Review (VV-4) fecha a volta de revalidação; sem isso ela ficava `aberta`."""
        self.gravar("docs/kanban/historico.md",
                    "| 2026-10-17T10:00:00-03:00 | xpto | Conferência | Review | revalidação |\n"
                    "| 2026-10-17T10:10:00-03:00 | xpto | Review | Em andamento | retrabalho |\n"
                    "| 2026-10-17T10:30:00-03:00 | xpto | Em andamento | Review | entregue, em paralelo |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertIn("voltas: xpto revalidacao inicio=2026-10-17T10:00:00-03:00 minutos=30", linhas)
        self.gravar("docs/kanban/historico.md",
                    "| 2026-10-17T10:00:00-03:00 | xpto | Conferência | Review | revalidação |\n"
                    "| 2026-10-17T10:20:00-03:00 | xpto | Review | QA | aprovado |\n")
        _, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertIn("voltas: xpto revalidacao inicio=2026-10-17T10:00:00-03:00 minutos=20", linhas)

    def test_historico_ilegivel_da_mensagem_e_rc_1(self):
        self.gravar("docs/kanban/historico.md", HISTORICO)
        arq = self.tmp / "docs/kanban/historico.md"
        arq.chmod(0)
        try:
            if os.access(arq, os.R_OK):
                self.skipTest("o usuário ignora permissões de arquivo")
            cod, _, erro = self.rodar("voltas", "--pedido", "xpto")
        finally:
            arq.chmod(0o644)
        self.assertEqual(cod, 1)
        self.assertIn("ilegivel", erro)
        self.assertNotIn("Traceback", erro)

    def test_pedido_inexistente_avisa_e_sai_com_1(self):
        cod, linhas, erro = self.rodar("voltas", "--pedido", "nao-existe")
        self.assertEqual((cod, linhas), (1, []))
        self.assertIn("nao existe", erro)

    def test_entregas_traz_as_rodadas_na_coluna_do_quadro(self):
        self.gravar("docs/briefs/xpto-tech-lead-1.md")
        self.gravar("docs/briefs/xpto-tech-lead-2.md")
        self.gravar("docs/briefs/xpto-qa-engineer-1.md")
        pasta = self.tmp / "sessoes"
        pasta.mkdir()
        msg = {"type": "assistant", "timestamp": "2026-10-17T10:00:00Z", "sessionId": "s", "isSidechain": False,
               "message": {"id": "m1", "model": "m", "usage": {"input_tokens": 1, "output_tokens": 1}}}
        (pasta / "a.jsonl").write_text(json.dumps(msg) + "\n", encoding="utf-8")
        cod, linhas, _ = self.rodar("transcricao", "custo", str(pasta), "--entregas", "--entrega", "xpto")
        self.assertEqual(cod, 0)
        self.assertTrue(linhas[0].startswith("| 2026-10-17 | xpto | jarvis (principal) | 2 | 3 delegações | - |"), linhas)
        self.assertIn("rodadas de brief: fonte=briefs", linhas[0])
        sem = self.rodar("transcricao", "custo", str(pasta), "--entregas", "--entrega", "nenhum")[1][0]
        self.assertTrue(sem.startswith("| 2026-10-17 | nenhum | jarvis (principal) | 2 | - | - |"), sem)


class PastasPadrao(Raiz):
    def test_acha_a_pasta_do_contrib_e_as_das_worktrees_sem_rede(self):
        home = self.tmp / "home"
        projetos = home / ".claude" / "projects"
        enc = re.sub(r"[^A-Za-z0-9]", "-", str(home / ".forge-contrib"))  # a mesma regra do código
        msg = {"type": "assistant", "timestamp": "2026-10-17T10:00:00Z", "isSidechain": False,
               "message": {"id": "m", "model": "m", "usage": {"input_tokens": 5, "output_tokens": 5}}}
        for nome, sid in ((enc, "c1"), (enc + "-wt-t-1", "w1"), (enc + "-wt-bp-1", "w2"), ("-outro-projeto", "x")):
            (projetos / nome).mkdir(parents=True)
            corpo = dict(msg, sessionId=sid, message=dict(msg["message"], id="m-" + sid))
            (projetos / nome / f"{sid}.jsonl").write_text(json.dumps(corpo) + "\n", encoding="utf-8")
        cod, linhas, erro = self.rodar("transcricao", "custo", home=home)
        self.assertEqual(cod, 0, linhas)
        self.assertIn("custo: vai ler 3 arquivo(s) .jsonl em 3 pasta(s) de sessoes", erro)
        self.assertIn("custo: total: entrada=15 saida=15 cache_criacao=0 cache_leitura=0 total=30", linhas)
        self.assertNotIn(str(home), "\n".join(linhas))

    def test_sem_nenhuma_pasta_diz_que_nao_existe_e_sai_com_1(self):
        cod, linhas, erro = self.rodar("transcricao", "custo", home=self.tmp / "vazio")
        self.assertEqual(cod, 1)
        self.assertTrue(linhas[0].startswith("custo: caminho inexistente: "), linhas)
        self.assertNotIn("Traceback", erro)


class RetroPorGatilho(Raiz):
    """EST-M11 (E2-1): `forge-check retro` imprime a linha de métricas e os gatilhos `lead`, `escape` e `decisao-reprovacao`."""
    SEM = "retro: alvo lead=nao-medido p85=nao-medido(n=0) voltas-classe=nao-medido divergentes=nao-medido escapes=0 decisao-reprovacao=0 custo=lacuna"

    def setUp(self):
        super().setUp()
        self.gravar("docs/pedidos/alvo.md", "# alvo\n")

    def rodar(self, *args, home=None):
        env = {"HOME": str(self.tmp / "home"), "PATH": "/usr/bin:/bin"}  # ambiente limpo: nada de CI nem PATH herdado
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), "retro", *args],
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout.splitlines(), r.stderr

    def leads(self, outros, alvo):
        """historico.md: `outros` cartões de lead 10 min e o `alvo` com `alvo` min, todos chegados à develop há um dia."""
        fim = datetime.datetime.now().astimezone() - datetime.timedelta(days=1)
        linhas = [f"| {fim.isoformat(timespec='seconds')} | curta |"]  # linha curta não conta nem quebra
        for nome, minutos in [("alvo", alvo)] + [(f"c{i}", 10) for i in range(outros)]:
            inicio = (fim - datetime.timedelta(minutes=minutos)).isoformat(timespec="seconds")
            linhas += [f"| {inicio} | {nome} | — | Em andamento | x |",
                       f"| {fim.isoformat(timespec='seconds')} | {nome} | Review | Pronto | custo total: 7 tokens · atributos: custo total: 9 tokens |"]
        self.gravar("docs/kanban/historico.md", "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n" + "\n".join(linhas) + "\n")

    def test_pedido_sem_nada_nao_tem_gatilho(self):
        self.assertEqual(self.rodar("--pedido", "alvo"), (0, [self.SEM, "retro: sem gatilho"], ""))

    def test_escape_do_pedido_e_gatilho_e_link_e_nao_medido(self):
        tabela = "| data-hora | pedido |\n|---|---|\n| 2026-11-07 10:00 | alvo | p | uso | baixo | qa | n | codigo |\n"
        self.gravar("docs/kanban/fora.md", tabela)
        self.gravar("docs/kanban/escapes.md", tabela + "| 2026-11-07 10:00 | outro | p | uso | baixo | qa | n | codigo |\n")
        cod, linhas, _ = self.rodar("--pedido", "alvo")
        self.assertEqual((cod, linhas[1]), (0, "retro: gatilho: escape"))
        self.assertIn(" escapes=1 ", linhas[0])
        (self.tmp / "docs/kanban/escapes.md").unlink()
        (self.tmp / "docs/kanban/escapes.md").symlink_to(self.tmp / "docs/kanban/fora.md")
        linhas = self.rodar("--pedido", "alvo")[1]
        self.assertEqual(linhas, [self.SEM.replace("escapes=0", "escapes=nao-medido"), "retro: sem gatilho"])

    def test_decisao_do_dono_sobre_reprovacao(self):
        self.gravar("docs/pedidos/alvo.md", '- DECISÃO DO DONO (2026-11-07 10:00): "A" — Reprovação aceita\n')
        self.assertEqual(self.rodar("--pedido", "alvo")[1][1], "retro: gatilho: decisao-reprovacao")
        self.gravar("docs/pedidos/alvo.md", '- DECISÃO DO DONO (2026-11-07 10:00): "A" — entrega aceita\nCitada: reprovação\n')
        self.assertEqual(self.rodar("--pedido", "alvo")[1][1], "retro: sem gatilho")

    def test_lead_acima_do_p85_com_vinte_pedidos(self):
        self.leads(19, 100)
        cod, linhas, _ = self.rodar("--pedido", "alvo")
        self.assertEqual((cod, linhas[1]), (0, "retro: gatilho: lead"))
        self.assertTrue(linhas[0].startswith("retro: alvo lead=100 p85=10 "), linhas)
        self.assertTrue(linhas[0].endswith(" custo=7"), linhas)  # o custo depois de `· atributos:` não vale
        self.assertIn(" p85=nao-medido(n=0) ", self.rodar("--pedido", "alvo", "--dias", "0")[1][0])

    def test_janela_conta_pela_chegada_a_develop(self):
        self.leads(19, 4320)  # o alvo abriu há 4 dias e chegou à develop há 1
        self.assertEqual(self.rodar("--pedido", "alvo", "--dias", "2")[1][1], "retro: gatilho: lead")

    def test_historico_link_ou_grande_e_nao_medido_com_aviso(self):
        self.leads(19, 100)
        hist = self.tmp / "docs/kanban/historico.md"
        hist.rename(self.tmp / "docs/kanban/real.md")
        hist.symlink_to(self.tmp / "docs/kanban/real.md")
        for motivo in ("é link simbólico", "passa de 1048576 bytes"):
            cod, linhas, erro = self.rodar("--pedido", "alvo")
            self.assertEqual((cod, linhas[1]), (0, "retro: sem gatilho"), motivo)
            self.assertIn(" lead=nao-medido p85=nao-medido(n=0) ", linhas[0])
            self.assertIn(f"retro: aviso: docs/kanban/historico.md {motivo}; lead e p85 nao-medido", erro)
            hist.unlink()
            hist.write_text((self.tmp / "docs/kanban/real.md").read_text(encoding="utf-8") + "x" * (1024 * 1024), encoding="utf-8")

    def test_lead_igual_ao_p85_nao_dispara(self):
        self.leads(19, 10)
        self.assertEqual(self.rodar("--pedido", "alvo")[1][1], "retro: sem gatilho")

    def test_dezenove_pedidos_sem_percentil(self):
        self.leads(18, 100)
        linhas = self.rodar("--pedido", "alvo")[1]
        self.assertIn(" lead=100 p85=nao-medido(n=19) ", linhas[0])
        self.assertEqual(linhas[1], "retro: sem gatilho")

    def test_pedido_fora_de_docs_pedidos_e_inexistente_dao_2(self):
        self.gravar("docs/x.md", "# fora\n")
        self.gravar("fora.md", "# fora\n")
        (self.tmp / "docs/pedidos/link.md").symlink_to(self.tmp / "fora.md")
        for pedido in ("../x", "link", "nenhum"):
            cod, linhas, erro = self.rodar("--pedido", pedido)
            self.assertEqual((cod, linhas), (2, []), pedido)
            self.assertIn("nao existe em docs/pedidos/", erro)


if __name__ == "__main__":
    unittest.main()
