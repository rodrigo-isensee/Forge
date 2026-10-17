"""T-1: `forge-check voltas`, rodadas de brief em `transcricao custo --entregas` e as pastas padrão de transcrições."""
import json
import os
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

    def test_voltas_de_um_pedido_em_linhas_fixas_com_minutos(self):
        cod, linhas, _ = self.rodar("voltas", "--pedido", "xpto")
        self.assertEqual(cod, 0)
        self.assertEqual(linhas, [
            "voltas: XPTO conferencia inicio=2026-10-17T10:12:00-03:00 minutos=18",
            "voltas: XPTO review inicio=2026-10-17T10:15:00-03:00 minutos=21",
            "voltas: XPTO revalidacao inicio=2026-10-17T10:36:00-03:00 minutos=aberta",
            "voltas: XPTO nao-classificado inicio=2026-10-17T10:50:00-03:00 minutos=8",
            "voltas: XPTO barrada inicio=2026-10-17T11:00:00-03:00 minutos=20",
            "voltas: XPTO resumo: brief=0 conferencia=1 review=1 revalidacao=1 barrada=1 nao-classificado=1 "
            "minutos=67 construcao=10 razao=6.70",
            "voltas: total: pedidos=1 voltas=5 minutos=67",
        ])

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
        self.assertEqual(linhas[:2], ["voltas: xpto brief inicio=sem-hora minutos=sem-hora ref=xpto-tech-lead-2",
                                      "voltas: xpto brief inicio=sem-hora minutos=sem-hora ref=xpto-tech-lead-3"])

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
        self.assertTrue(linhas[0].startswith("| 2026-10-17 | xpto | jarvis (principal) | 2 | 3 | - |"), linhas)
        self.assertIn("rodadas de brief: fonte=briefs", linhas[0])
        sem = self.rodar("transcricao", "custo", str(pasta), "--entregas", "--entrega", "nenhum")[1][0]
        self.assertTrue(sem.startswith("| 2026-10-17 | nenhum | jarvis (principal) | 2 | - | - |"), sem)


class PastasPadrao(Raiz):
    def test_acha_a_pasta_do_contrib_e_as_das_worktrees_sem_rede(self):
        home = self.tmp / "home"
        projetos = home / ".claude" / "projects"
        enc = str(home / ".forge-contrib").replace("/", "-").replace(".", "-")
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


if __name__ == "__main__":
    unittest.main()
