"""T-1: `forge-check voltas`, rodadas de brief em `transcricao custo --entregas` e as pastas padrão de transcrições."""
import contextlib
import datetime
import importlib.machinery
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ambiente_git import sem_manutencao  # noqa: E402
from apoio_forge_check_rapido import comando_do_forge_check  # noqa: E402

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
    # S-SUITE-RAPIDA: as classes daqui rodam o script direto, de ponta a ponta; as de test_forge que herdam esta raiz
    # (False) rodam o mesmo forge-check pelo bytecode em cache (`apoio_forge_check_rapido`).
    SCRIPT_DIRETO = True

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-voltas-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def gravar(self, rel, texto=""):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def rodar(self, *args, home=None):
        env = dict(os.environ, HOME=str(home or self.tmp / "home"))
        inicio = [sys.executable, FORGE_CHECK] if self.SCRIPT_DIRETO else comando_do_forge_check()
        r = subprocess.run([*inicio, "--raiz", str(self.tmp), *args],
                           capture_output=True, text=True, env=env)
        return r.returncode, r.stdout.splitlines(), r.stderr


class SemQueda:
    """F6, E5.4: a queda do script (Traceback) é falha do teste, não erro de índice adiante (o forge-mutante conta erro como inválido)."""
    def rodar(self, *args, **kwargs):
        cod, linhas, erro = super().rodar(*args, **kwargs)
        self.assertNotIn("Traceback", erro)
        return cod, linhas, erro


class Voltas(SemQueda, Raiz):
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
        cod, um, _ = self.rodar("voltas", "--pedido", "outro")
        self.assertEqual((cod, len(um)), (0, 2), um)  # F6, E5.4: rc e linhas antes do índice (falha, não erro)
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
        carga = subprocess.run([sys.executable, "-I", "-c", (
            "import importlib.machinery as m, importlib.util as u, sys\n"
            f"l = m.SourceFileLoader('fc', {FORGE_CHECK!r}); s = u.spec_from_loader('fc', l); mod = u.module_from_spec(s); l.exec_module(mod)\n"
            f"l2 = m.SourceFileLoader('fv', {str(RAIZ / 'bin' / 'forge_voltas.py')!r}); s2 = u.spec_from_loader('fv', l2)\n"
            "fv = u.module_from_spec(s2); l2.exec_module(fv); ctx = mod.ctx_das_voltas()\n"
            "c = lambda de, para, motivo: fv.classificar_volta(de, para, motivo, ctx)\n"
            "print(c('Conferência', 'Review', 'não cumpriu'), c('Conferência', 'Review', 'conferido'), c('Review', 'Review', 'reprovou'),"
            " c('Em andamento', 'Aguardando o dono', 'barrada'), c('Review', 'Em andamento', 'x'), c('Em andamento', 'Conferência', 'x'))")],
            capture_output=True, text=True, env={"PATH": os.environ.get("PATH", ""), "HOME": str(self.tmp / "home")})
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


class RodadasDeBrief(SemQueda, Raiz):
    def test_conferencias_manda_quando_ha_linhas_e_so_conta_modo_brief(self):
        self.gravar("docs/kanban/conferencias.md", CONFERENCIAS)
        self.gravar("docs/briefs/xpto-tech-lead-1.md")
        self.gravar("docs/briefs/xpto-tech-lead-2.md")
        self.gravar("docs/kanban/historico.md", "")
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual((cod, len(linhas)), (0, 3), linhas)  # F6, E5.4: rc e linhas antes do índice (falha, não erro)
        self.assertEqual(linhas[0], "voltas: xpto brief inicio=2026-10-15 21:07 minutos=7 ref=xpto-tech-lead-1")
        self.assertIn("brief=1 ", linhas[1])
        self.assertIn(" minutos=7 construcao=- ", linhas[1])  # F6, E5.4: os minutos da rodada extra entram no resumo

    def test_pedido_so_em_docs_pedidos_existe_sem_historico(self):  # F6, E5.4
        self.gravar("docs/pedidos/P1.md", "# p\n")
        self.gravar("docs/kanban/historico.md", "")
        self.assertEqual(self.rodar("voltas", "--pedido", "p1")[:2], (0, [
            "voltas: P1 resumo: brief=0 conferencia=0 review=0 revalidacao=0 barrada=0 nao-classificado=0 minutos=0 construcao=- razao=-",
            "voltas: total: pedidos=1 voltas=0 minutos=0"]))

    def test_sem_conferencias_vale_o_disco_dos_briefs_por_destino(self):
        for nome in ("xpto-tech-lead-1", "xpto-tech-lead-2", "xpto-tech-lead-3", "xpto-qa-engineer-1", "xptoz-tech-lead-1", "xpto-2-tech-lead-1"):
            self.gravar(f"docs/briefs/{nome}.md")
        self.gravar("docs/kanban/historico.md", "")
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual((cod, len(linhas)), (0, 2), linhas)  # F6, E5.4: rc e linhas antes do índice (falha, não erro)
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


class RamosDeFalhaDoModuloVoltas(Raiz):
    """F6, E5.4: `voltas` e `esperas` moram em bin/forge_voltas.py; os ramos de falha que o script de ponta a ponta não alcança."""
    AUSENTE = "forge-check: bin/forge_voltas.py ausente ao lado do forge-check; nada feito\n"

    def carregar(self, nome, arquivo):
        carregador = importlib.machinery.SourceFileLoader(nome, str(arquivo))
        modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader(nome, carregador))
        carregador.exec_module(modulo)
        return modulo

    def test_copia_avulsa_sem_o_modulo_sai_com_2_nos_dois(self):
        copia = self.tmp / "copia" / "bin"
        copia.mkdir(parents=True)
        (copia / "forge-check").write_bytes(Path(FORGE_CHECK).read_bytes())
        self.gravar("docs/kanban/historico.md", HISTORICO)
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.tmp / "home")}
        for args in (("voltas",), ("esperas",), ("voltas", "--pedido", "xpto"), ("esperas", "--pedido", "xpto")):
            with self.subTest(args):
                r = subprocess.run([sys.executable, "-I", str(copia / "forge-check"), "--raiz", str(self.tmp), *args],
                                   capture_output=True, text=True, env=env, cwd=self.tmp)
                self.assertEqual((r.returncode, r.stdout), (2, self.AUSENTE), r.stderr)

    def test_historico_que_nao_le_da_rc_1_e_nada_medido(self):
        self.gravar("docs/kanban/historico.md", HISTORICO)
        fc = self.carregar("forge_check_e54", FORGE_CHECK)
        fv = self.carregar("forge_voltas_e54", RAIZ / "bin" / "forge_voltas.py")
        saida, erro = io.StringIO(), io.StringIO()
        with mock.patch.object(Path, "read_text", side_effect=PermissionError(13, "Permission denied")), \
                contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro):
            cod = fv.cmd_voltas(self.tmp, "xpto", fc.ctx_das_voltas())
        self.assertEqual((cod, saida.getvalue(), erro.getvalue()),
                         (1, "", "voltas: docs/kanban/historico.md ilegivel (Permission denied); nada medido\n"))


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


class MedidaDoTopico(Raiz):  # D12 (E3a): `forge-check medida` mede um tópico mesclado e grava a linha; casos (d) e (e) do desenho
    def setUp(self):
        super().setUp()
        self.env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp / "home"), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        self.gravar("KANBAN.md", "## Em andamento\n")
        self.gravar("a.txt", "1\n2\n3\n4\n5\n")
        for passo in (("init", "-q", "-b", "develop"), ("add", "KANBAN.md"), ("commit", "-qm", "base"), ("checkout", "-qb", "topico"),
                      ("add", "a.txt"), ("commit", "-qm", "topico"), ("checkout", "-q", "develop")):
            self.git(*passo)
        self.git("merge", "-q", "--no-ff", "-m", "Merge topico", "topico", data="2026-10-17T12:20:00-03:00")
        self.merge = self.git("rev-parse", "HEAD")
        self.gravar("docs/kanban/historico.md", "| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n"
                    "| 2026-10-17T10:00:00-03:00 | P | Pronto para fazer | Em andamento | brief |\n"
                    "| 2026-10-17T10:30:00-03:00 | P | Em andamento | Aguardando o dono | pergunta |\n"
                    "| 2026-10-17T11:30:00-03:00 | P | Aguardando o dono | Em andamento | respondeu |\n"
                    "| 2026-10-17T11:40:00-03:00 | P | Em andamento | Review | espera deliberada: fila da suíte |\n"
                    "| 2026-10-17T12:10:00-03:00 | P | Review | Em andamento | review |\n"
                    "| 2026-10-17T13:00:00-03:00 | P | Em andamento | Aguardando o dono | depois do merge não conta |\n"
                    "| 2026-10-17T09:00:00-03:00 | Q | Pronto para fazer | Em andamento | outro cartão |\n")
        self.gravar("docs/kanban/entregas.md", "| data | entrega | agente | tokens | r | v | nota |\n|---|---|---|---|---|---|---|\n"
                    "| 2026-10-17 | P | jarvis | 100 | - | - | |\n| 2026-10-17 | p | forge:tech-lead | 23 | - | - | |\n"
                    "| 2026-10-17 | Q | jarvis | 999 | - | - | |\n")

    def git(self, *args, data=None):
        env = sem_manutencao(dict(self.env, **({"GIT_AUTHOR_DATE": data, "GIT_COMMITTER_DATE": data} if data else {})))
        return subprocess.run(["git", "-C", str(self.tmp), *args], capture_output=True, text=True, env=env, check=True).stdout.strip()

    def rodar(self, *args):
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), *args], capture_output=True, text=True, env=self.env)
        return r.returncode, r.stdout.splitlines(), r.stderr

    def medidas(self):
        return [l.split(" | ")[1:] for l in (self.tmp / "docs/kanban/medidas.md").read_text(encoding="utf-8").splitlines()[2:]]

    def test_tempo_ativo_desconta_o_dono_e_a_espera_deliberada_e_soma_os_tokens_do_pedido(self):  # (d)
        cod, linhas, erro = self.rodar("medida", "--pedido", "p", "--merge", self.merge)
        self.assertEqual(cod, 0, erro)
        self.assertEqual(self.medidas(), [["p", self.merge, "50", "5", "sim", "123 |"]])  # 140 min - 60 do dono - 30 deliberados
        self.assertEqual(linhas[-1], "medida: só tabela (n=1)")
        self.rodar("medida", "--pedido", "q", "--merge", self.merge)
        self.assertEqual(self.medidas()[1], ["q", self.merge, "200", "5", "sim", "999 |"])

    def test_sem_fonte_a_celula_diz_lacuna_e_o_cabecalho_nomeia_a_fonte_de_cada_numero(self):  # (e)
        (self.tmp / "docs/kanban/entregas.md").unlink()
        for pedido in ("p", "sem-cartao"):
            self.assertEqual(self.rodar("medida", "--pedido", pedido, "--merge", self.merge)[0], 0)
        self.gravar("docs/kanban/entregas.md", "| d | e | a | t |\n|---|---|---|---|\n| 1 | p | x | 12 |\n| 1 | p | y | ? |\n")
        for pedido in ("p", "q"):
            self.rodar("medida", "--pedido", pedido, "--merge", self.merge)
        self.assertEqual([m[2::3] for m in self.medidas()], [["50", "lacuna:sem-entregas.md |"], ["lacuna:sem-movimento", "lacuna:sem-entregas.md |"],
                                                            ["50", "lacuna:tokens-nao-numericos |"], ["200", "lacuna:sem-linha-do-pedido |"]])
        cabecalho = (self.tmp / "docs/kanban/medidas.md").read_text(encoding="utf-8").splitlines()[0]
        for fonte in ("ativo_min (historico.md)", "linhas (git diff)", "tokens (entregas.md)"):
            self.assertIn(fonte, cabecalho)

    def test_entrada_recusada_sai_com_2_e_nada_grava(self):
        ruins = [("p", "HEAD"), ("p", self.merge[:12]), ("p", "--output=" + "0" * 31), ("p", self.merge + "\n"),
                 ("p", self.merge.upper()), ("p", "f" * 40), ("../p", self.merge), ("..", self.merge)]
        for pedido, merge in ruins:
            cod, linhas, erro = self.rodar("medida", "--pedido", pedido, "--merge", merge)
            self.assertEqual((cod, linhas), (2, []), (pedido, merge, erro))
            self.assertIn("medida:", erro)
        (self.tmp / "KANBAN.md").unlink()
        self.assertEqual(self.rodar("medida", "--pedido", "p", "--merge", self.merge)[0], 2)
        self.gravar("KANBAN.md", "## Em andamento\n")
        (self.tmp / "docs/kanban/medidas.md").symlink_to(self.tmp / "fora.md")
        self.assertEqual(self.rodar("medida", "--pedido", "p", "--merge", self.merge)[0], 2)
        self.assertFalse((self.tmp / "fora.md").exists())
        (self.tmp / "docs/kanban/medidas.md").unlink()
        self.git("checkout", "-q", "--orphan", "raiz")
        self.git("commit", "-qm", "sem pai")
        cod, _, erro = self.rodar("medida", "--pedido", "p", "--merge", self.git("rev-parse", "HEAD"))
        self.assertEqual(cod, 0, erro)
        self.assertEqual(self.medidas()[0][3:5], ["lacuna:git-diff", "-"])


class MedidaDaRelease(Raiz):  # D12 (E3b): a release separada pelas tags v* e o aviso de piora; casos (a), (b), (c) e (f) do desenho
    git, rodar = MedidaDoTopico.git, MedidaDoTopico.rodar
    ANTERIOR = [(70, 100), (90, 100), (103, 100), (114, 100)]  # a 0.26.0 de estudo-tempo-topico.md:192: mediana 96,5, maior 114

    def setUp(self):
        super().setUp()
        self.env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp / "home"), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        self.gravar("KANBAN.md", "## Em andamento\n")
        self.git("init", "-q", "-b", "develop")
        self.shas = []
        for i in range(11):  # 0 e 1: v0.1.0 (penúltima); 2 a 5: v0.2.0 (anterior); 6 a 9: atual, pequenos; 10: atual, grande
            self.git("commit", "-q", "--allow-empty", "-m", f"merge {i}")
            self.shas.append(self.git("rev-parse", "HEAD"))
            if i in (1, 5):  # a v0.1.0 nasce depois da v0.2.0: ler a release pela data, e não pela versão, troca as duas
                self.git("tag", "-a", "-m", "r", f"v0.{i // 5 + 1}.0", data="2026-10-20T00:00:00Z" if i == 1 else "2026-10-10T00:00:00Z")

    def medir(self, anterior, atual, extras=()):
        """medidas.md com um tópico de 999 na penúltima, um grande na atual, os `extras` e os (ativo, tokens) das duas releases; a
        medida roda sobre o primeiro merge da penúltima, fora das duas releases comparadas."""
        linhas = [(self.shas[1], "sim", 999, 999), (self.shas[10], "nao", 999, 999), *extras]
        linhas += [(s, "sim", *v) for s, v in [*zip(self.shas[2:6], anterior), *zip(self.shas[6:10], atual)]]
        self.gravar("docs/kanban/medidas.md", "| h | p | m | a | l | s | t |\n|---|---|---|---|---|---|---|\n"
                    + "".join(f"| 2026-10-17T12:00:00-03:00 | x | {s} | {a} | 1 | {p} | {t} |\n" for s, p, a, t in linhas))
        return self.rodar("medida", "--pedido", "z", "--merge", self.shas[0])

    def test_a_piora_da_026_para_a_028_avisa_com_os_numeros_e_a_fonte_e_sai_0(self):  # (a) e (f)
        cod, linhas, erro = self.medir(self.ANTERIOR, [(84, 100), (153, 100), (127, 100), ("lacuna:x", "lacuna:y")])
        self.assertEqual((cod, linhas[1:]), (0, [
            "medida: aviso: piora no tempo ativo (min, historico.md): mediana 96.5 → 127 (limite +20%: 115.8), 2 tópicos acima do maior da"
            " anterior (114); n=3 contra 4; fonte: docs/kanban/medidas.md, release atual (sem tag v*) contra v0.2.0"]), erro)
        cod, linhas, erro = self.medir([(t, a) for a, t in self.ANTERIOR], [(100, 84), (100, 153), (100, 127)])
        self.assertEqual((cod, len(linhas)), (0, 2), erro)
        self.assertTrue(linhas[-1].startswith("medida: aviso: piora no tokens novos (entregas.md): mediana 96.5 → 127 "), linhas)

    def test_b_ruido_da_028_um_so_acima_do_maior_ou_mediana_ate_20_por_cento_nao_avisam(self):  # (b)
        for anterior, atual in (([(84, 1), (127, 1), (153, 1)], [(100, 1), (150, 1), (152, 1)]),  # o ruído interno da 0.28.0
                                ([(50, 1), (96, 1), (200, 1)], [(120, 1), (200, 1), (250, 1)]),  # mediana +108%, só 1 acima de 200 (empate não passa)
                                ([(100, 1), (100, 1), (105, 1)], [(90, 1), (110, 1), (115, 1)])):  # 2 acima de 105, mas mediana +10%
            cod, linhas, erro = self.medir(anterior, atual)
            self.assertEqual((cod, linhas[1:]), (0, ["medida: só tabela (n=3)"]), (anterior, erro))

    def test_c_menos_de_3_pequenos_na_atual_ou_sem_release_anterior_so_tabela(self):  # (c)
        estranhos = [("HEAD", "sim", 999, 999), ("f" * 40, "sim", 999, 999), (self.shas[6], "sim", 1, 1)]  # ref, sha ausente, medida velha
        cod, linhas, erro = self.medir(self.ANTERIOR, [(127, 127), (153, 153)], estranhos)
        self.assertEqual((cod, linhas[1:]), (0, ["medida: só tabela (n=2)"]), erro)
        self.git("tag", "-d", "v0.1.0")  # só uma tag: a anterior é tudo o que ela contém, com o 999 da v0.1.0
        self.assertEqual(self.medir(self.ANTERIOR, [(84, 1), (153, 1), (127, 1)])[1][1:], ["medida: só tabela (n=3)"])
        self.git("tag", "-d", "v0.2.0")  # sem tag: tudo é a release atual e não há anterior medida
        self.assertEqual(self.medir(self.ANTERIOR, [(84, 1), (153, 1), (127, 1)])[1][1:], ["medida: só tabela (n=8)"])


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
