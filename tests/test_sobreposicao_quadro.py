"""`forge-check sobreposicao` (TA-6) e `forge-check movimento` (PA-9), mais a fila de integração (PA-3) como texto;
`forge-check fila` (P9: o que pode começar agora, T1 a T8)."""
import datetime
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402
from apoio_jarvis import texto_do_jarvis  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FERRAMENTA = RAIZ / "bin" / "forge-check"
AMBIENTE = sem_manutencao({**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                           "GIT_COMMITTER_EMAIL": "t@t"})


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=AMBIENTE, capture_output=True, text=True, check=True).stdout


def checar(cwd, *args):
    r = subprocess.run([sys.executable, str(FERRAMENTA), "--raiz", str(cwd), *args], capture_output=True, text=True, env=AMBIENTE)
    return r.returncode, r.stdout


class Sobreposicao(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        git(self.repo, "init", "-q", "-b", "develop")
        self.escrever("base.txt", "base\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")

    def escrever(self, nome, texto):
        (self.repo / nome).write_text(texto, encoding="utf-8")

    def ramo(self, nome, **arquivos):
        git(self.repo, "switch", "-q", "-c", nome, "develop")
        for arq, texto in arquivos.items():
            self.escrever(arq.replace("__", "."), texto)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", nome)
        git(self.repo, "switch", "-q", "develop")

    def test_lista_so_os_pares_com_arquivo_em_comum_e_o_resumo(self):
        self.ramo("melhoria/a", comum__txt="a\n", so_a__txt="a\n")
        self.ramo("melhoria/b", comum__txt="b\n")
        self.ramo("melhoria/c", so_c__txt="c\n")
        self.ramo("feature/fora", comum__txt="f\n")  # fora do padrão melhoria/*
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertEqual(rc, 0)
        self.assertEqual(saida.splitlines(), [
            "melhoria/a <-> melhoria/b: comum.txt",
            "sobreposicao: 1 par(es) com arquivos em comum entre 3 branch(es) melhoria/* (base develop)"])

    def test_saida_deterministica(self):
        self.ramo("melhoria/a", x__txt="a\n", y__txt="a\n")
        self.ramo("melhoria/b", y__txt="b\n", x__txt="b\n")
        self.assertEqual({checar(self.repo, "sobreposicao", "--base", "develop")[1] for _ in range(3)},
                         {"melhoria/a <-> melhoria/b: x.txt, y.txt\n"
                          "sobreposicao: 1 par(es) com arquivos em comum entre 2 branch(es) melhoria/* (base develop)\n"})

    def test_sem_branches_so_o_resumo_e_rc_zero(self):
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertEqual((rc, saida), (0, "sobreposicao: 0 par(es) com arquivos em comum entre 0 branch(es) melhoria/* (base develop)\n"))

    def test_branch_remota_e_local_iguais_contam_uma_vez(self):
        self.ramo("melhoria/a", comum__txt="a\n")
        self.ramo("melhoria/b", comum__txt="b\n")
        origem = tempfile.TemporaryDirectory()
        self.addCleanup(origem.cleanup)
        git(self.repo, "clone", "-q", "--bare", str(self.repo), origem.name)
        remoto_sem_manutencao(origem.name)
        git(self.repo, "remote", "add", "origin", origem.name)
        git(self.repo, "fetch", "-q", "origin")
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertIn("entre 2 branch(es)", saida)
        self.assertEqual(saida.count("<->"), 1)

    def test_branch_so_no_remoto_continua_listada(self):
        self.ramo("melhoria/a", comum__txt="a\n")
        self.ramo("melhoria/b", comum__txt="b\n")
        origem = tempfile.TemporaryDirectory()
        self.addCleanup(origem.cleanup)
        git(self.repo, "clone", "-q", "--bare", str(self.repo), origem.name)
        remoto_sem_manutencao(origem.name)
        git(self.repo, "remote", "add", "origin", origem.name)
        git(self.repo, "fetch", "-q", "origin")
        git(self.repo, "branch", "-D", "melhoria/b")
        rc, saida = checar(self.repo, "sobreposicao", "--base", "develop")
        self.assertEqual(rc, 0)
        self.assertIn("melhoria/a <-> melhoria/b: comum.txt", saida)

    def test_base_inexistente_nao_falha(self):
        git(self.repo, "branch", "-m", "outra")
        rc, saida = checar(self.repo, "sobreposicao", "--base", "nao-existe-xyz")
        self.assertEqual(rc, 0)
        self.assertIn("base não encontrada", saida)


class TravaDeRelease(unittest.TestCase):
    """DV-5: com release em curso, `sobreposicao --ref` barra a branch que não é a da release."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        git(self.repo, "init", "-q", "-b", "develop")
        (self.repo / "base.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "-m", "base")

    def versao(self, remoto, texto):
        """Grava plugin.json com `texto` num commit e aponta refs/remotes/origin/<remoto> para ele (sem rede)."""
        pasta = self.repo / ".claude-plugin"
        pasta.mkdir(exist_ok=True)
        (pasta / "plugin.json").write_text(texto, encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-q", "--allow-empty", "-m", f"v {remoto}")
        git(self.repo, "update-ref", f"refs/remotes/origin/{remoto}", "HEAD")

    def par(self, dev, hom):
        self.versao("homolog", '{"version": "%s"}' % hom)
        self.versao("develop", '{"version": "%s"}' % dev)

    def test_release_em_curso_e_branch_de_fora_barra(self):
        self.par("0.24.0", "0.23.0")
        rc, saida = checar(self.repo, "sobreposicao", "--ref", "melhoria/outra")
        self.assertEqual(rc, 1)
        self.assertIn("release 0.24.0 em curso", saida)
        self.assertIn("espere a promoção", saida)

    def test_branch_da_release_passa(self):
        self.par("0.24.0", "0.23.0")
        for ref in ("melhoria/release-0.24.0", "origin/melhoria/release-0.24.0"):
            self.assertEqual(checar(self.repo, "sobreposicao", "--ref", ref)[0], 0)

    def test_release_de_outra_versao_nao_passa(self):
        self.par("0.24.0", "0.23.0")
        self.assertEqual(checar(self.repo, "sobreposicao", "--ref", "melhoria/release-0.23.0")[0], 1)

    def test_sem_release_em_curso_nada_muda(self):
        for dev, hom in (("0.23.0", "0.23.0"), ("0.22.0", "0.23.0")):
            self.par(dev, hom)
            rc, saida = checar(self.repo, "sobreposicao", "--ref", "melhoria/outra")
            self.assertEqual(rc, 0)
            self.assertNotIn("release", saida)

    def test_versao_numerica_compara_por_numero_nao_por_texto(self):
        self.par("0.9.0", "0.10.0")
        self.assertEqual(checar(self.repo, "sobreposicao", "--ref", "melhoria/outra")[0], 0)

    def test_sem_ref_nada_muda_mesmo_com_release_em_curso(self):
        self.par("0.24.0", "0.23.0")
        rc, saida = checar(self.repo, "sobreposicao")
        self.assertEqual(rc, 0)
        self.assertNotIn("release", saida)

    def test_versao_ilegivel_so_avisa(self):
        self.par("0.24.0", "0.23.0")
        self.versao("develop", "isto nao e json")
        rc, saida = checar(self.repo, "sobreposicao", "--ref", "melhoria/outra")
        self.assertEqual(rc, 0)
        self.assertIn("aviso: versão ilegível em origin/develop", saida)

    def test_versao_ausente_so_avisa(self):
        rc, saida = checar(self.repo, "sobreposicao", "--ref", "melhoria/outra")
        self.assertEqual(rc, 0)
        self.assertIn("aviso: não li", saida)


class Movimento(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz = Path(self._tmp.name)
        (self.raiz / "KANBAN.md").write_text("# Quadro\n\n## Aguardando o dono\n\n## Em andamento (WIP 1 por agente)\n\n## Pronto\n\n## a\n\n## b\n\n## a/b\n\n## c d\n", encoding="utf-8")  # sem quadro o movimento recusa (FC-PEDIDO-FORA)
        self.arq = self.raiz / "docs" / "kanban" / "historico.md"

    def test_cria_o_arquivo_e_acrescenta_com_hora_iso_e_fuso(self):
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Aguardando o dono", "--para", "Sem credencial")[0], 0)
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Sem credencial", "--para", "Em andamento", "--motivo", "chegou")[0], 0)
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[:2], ["| Data/hora | Cartão | De | Para | Motivo |", "|---|---|---|---|---|"])
        iso = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d"
        self.assertRegex(linhas[2], rf"^\| {iso} \| K-1 \| Aguardando o dono \| Sem credencial \| custo do trecho: lacuna \|$")  # L16: parada sem transcrição
        self.assertRegex(linhas[3], rf"^\| {iso} \| K-1 \| Sem credencial \| Em andamento \| chegou \|$")
        self.assertEqual(len(linhas), 4)

    def transcricao(self, horas, uso=None):
        pasta = self.raiz / "home" / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(self.raiz.resolve()))
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "s.jsonl").write_text("\n".join(json.dumps(
            {"type": "assistant", "sessionId": "s", "isSidechain": False, "timestamp": h,
             "message": {"id": f"m{i}", "model": "m", "usage": uso or {"input_tokens": 10, "output_tokens": 5}}}) for i, h in enumerate(horas)) + "\n", encoding="utf-8")

    def historico(self, *linhas):
        self.arq.parent.mkdir(parents=True, exist_ok=True)
        self.arq.write_text("| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n" + "".join(
            f"| {hora} | {cartao} | A | B | {motivo} |\n" for hora, cartao, motivo in linhas), encoding="utf-8")

    def movimento(self, *args):
        env = dict(os.environ, HOME=str(self.raiz / "home"))
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--raiz", str(self.raiz), "movimento", *args], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return self.arq.read_text(encoding="utf-8").splitlines()[-1]

    def test_parada_grava_o_custo_do_trecho_e_o_pronto_soma(self):  # L16 (EXT-3): o custo do trecho vai pelo `movimento`, só acrescentando
        agora = datetime.datetime.now(datetime.timezone.utc)
        inicio = (agora - datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        dentro = [(agora - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"), (agora - datetime.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")]
        fora = (agora - datetime.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")  # antes do último movimento: não entra
        self.transcricao([fora, *dentro])
        self.historico((inicio, "K-7", "—"))
        linha = self.movimento("K-7", "--de", "Em andamento", "--para", "Aguardando o dono", "--motivo", "validar")
        self.assertTrue(linha.endswith("| validar · custo do trecho: 30 tokens |"), linha)  # 2 mensagens de 15 tokens
        linha = self.movimento("K-7", "--de", "Aguardando o dono", "--para", "Pronto")
        self.assertRegex(linha, r"custo total: 30 tokens( \(1 trechos em lacuna\))? \|$")  # o trecho de agora não tem mensagem: lacuna dita, nunca 0
        self.assertIn("(1 trechos em lacuna)", linha)

    def test_custo_do_trecho_com_o_uso_no_formato_real_do_claude_code(self):  # L16, A1 do review: server_tool_use aninhado não derruba o movimento
        agora = datetime.datetime.now(datetime.timezone.utc)
        inicio = (agora - datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        dentro = (agora - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.transcricao([dentro], uso={"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 3, "cache_read_input_tokens": 2,
                                        "server_tool_use": {"web_search_requests": 1}, "service_tier": "standard"})
        self.historico((inicio, "K-10", "—"))
        linha = self.movimento("K-10", "--de", "Em andamento", "--para", "Aguardando o dono", "--motivo", "validar")
        self.assertTrue(linha.endswith("| validar · custo do trecho: 20 tokens |"), linha)

    def test_sem_transcricao_o_custo_e_lacuna_nunca_zero(self):
        self.historico(("2026-10-20T09:00:00+00:00", "K-8", "—"))
        linha = self.movimento("K-8", "--de", "Em andamento", "--para", "Sem credencial")
        self.assertTrue(linha.endswith("| custo do trecho: lacuna |"), linha)
        linha = self.movimento("K-8", "--de", "Sem credencial", "--para", "Pronto")
        self.assertTrue(linha.endswith("| custo total: lacuna |"), linha)
        self.assertNotIn("0 tokens", self.arq.read_text(encoding="utf-8"))

    def test_movimento_fora_de_parada_nao_grava_custo(self):
        linha = self.movimento("K-9", "--de", "Em andamento", "--para", "Aguardando o dono")
        self.assertIn("custo do trecho: lacuna", linha)
        self.assertNotIn("custo", self.movimento("K-9", "--de", "Aguardando o dono", "--para", "Em andamento"))

    def test_coluna_fora_do_quadro_recusa_sem_gravar(self):  # LOTE E2: o historico.md tinha "Discovery", "Fila" e "Feito" que o quadro não tem
        for args in (("--de", "Em andamento", "--para", "Discovery"), ("--de", "Fila", "--para", "Em andamento"), ("--de", "—", "--para", "—")):
            rc, saida = checar(self.raiz, "movimento", "K-6", *args)
            self.assertEqual(rc, 1, saida)
            self.assertIn("fora do KANBAN.md", saida)
        self.assertFalse(self.arq.exists())
        self.assertEqual(checar(self.raiz, "movimento", "K-6", "--de", "—", "--para", "aguardando O DONO")[0], 0)  # cartão novo; acento e caixa não contam
        self.assertEqual(checar(self.raiz, "movimento", "K-6", "--de", "Em andamento", "--para", "Conferência")[0], 0)  # estado fora do quadro

    def test_nao_reescreve_o_que_existe_e_protege_a_tabela(self):
        self.arq.parent.mkdir(parents=True)
        self.arq.write_text("| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n| antiga | K-0 | a | b | — |\n", encoding="utf-8")
        checar(self.raiz, "movimento", "K-2", "--de", "a|b", "--para", "c\nd", "--motivo", "x | y")
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[2], "| antiga | K-0 | a | b | — |")
        self.assertEqual(len(linhas), 4)
        self.assertTrue(linhas[3].endswith("| K-2 | a/b | c d | x / y |"), linhas[3])

    def test_arquivo_sem_quebra_final_nao_cola_a_linha_nova(self):
        self.arq.parent.mkdir(parents=True)
        self.arq.write_text("| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n| antiga | K-0 | a | b | — |", encoding="utf-8")
        self.assertEqual(checar(self.raiz, "movimento", "K-3", "--de", "a", "--para", "b")[0], 0)
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[2], "| antiga | K-0 | a | b | — |")
        self.assertEqual(len(linhas), 4)
        self.assertIn("| K-3 | a | b | — |", linhas[3])

    def test_remove_caracteres_de_controle(self):
        checar(self.raiz, "movimento", "K-4", "--de", "a\x1b", "--para", "b\x01\x7f", "--motivo", "e\x07f")
        linha = self.arq.read_text(encoding="utf-8").splitlines()[-1]
        self.assertTrue(linha.endswith("| K-4 | a | b | ef |"), linha)
        self.assertNotRegex(linha, r"[\x00-\x08\x0b-\x1f\x7f]")

    def test_link_simbolico_e_recusado_sem_escrever(self):
        self.arq.parent.mkdir(parents=True)
        alvo = self.raiz / "alvo.md"
        alvo.write_text("intacto\n", encoding="utf-8")
        self.arq.symlink_to(alvo)
        rc, saida = checar(self.raiz, "movimento", "K-5", "--de", "a", "--para", "b")
        self.assertEqual(rc, 1)
        self.assertIn("link simbólico", saida)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "intacto\n")

    def test_campo_vazio_falha_e_nao_grava(self):
        rc, saida = checar(self.raiz, "movimento", " ", "--de", "a", "--para", "b")
        self.assertEqual(rc, 1)
        self.assertFalse(self.arq.exists())


class RegrasEmTexto(unittest.TestCase):
    def texto(self, rel):
        return (RAIZ / rel).read_text(encoding="utf-8")

    def test_fila_de_integracao_na_regra_e_no_tech_lead(self):
        for rel, trechos in (("docs/regras/R-FLUXO.md", ("um por vez", "ordem de chegada", "forge-check sobreposicao")),
                             ("agents/tech-lead.md", ("Fila de integração", "ordem de chegada", "forge-check sobreposicao"))):
            for trecho in trechos:
                self.assertIn(trecho, self.texto(rel), rel)

    def test_jarvis_serializa_antes_de_disparar_e_registra_o_quadro(self):
        t = texto_do_jarvis(RAIZ)
        for trecho in ("bin/forge-check sobreposicao", "serializam", "forge-check movimento"):
            self.assertIn(trecho, t)

    def test_skill_do_quadro_manda_registrar_com_o_subcomando(self):
        t = self.texto("skills/kanban-scrum/SKILL.md")
        for trecho in ("forge-check movimento", "Aguardando o dono", "Sem credencial", "ISO 8601"):
            self.assertIn(trecho, t)



CABECALHO_FILA = "| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
COLUNAS_FILA = ["Pronto para fazer (WIP 5)", "Em andamento (WIP 1 por agente)", "Pronto"]


class Fila(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-fila-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.proc = self.tmp / "proc-falso"  # a carga da máquina real não pode mudar o resultado
        self.carga(0.1)

    def carga(self, load, nucleos=8):
        self.proc.mkdir(exist_ok=True)
        (self.proc / "loadavg").write_text(f"{load} 0.1 0.1 1/100 1\n", encoding="utf-8")
        (self.proc / "meminfo").write_text("MemTotal: 16777216 kB\nMemAvailable: 12582912 kB\n", encoding="utf-8")
        self.nucleos = nucleos

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def quadro(self, **colunas):
        """colunas: pronto_para_fazer, em_andamento, pronto = lista de (cartão, pedido)."""
        texto = "# Quadro\n"
        for nome, chave in zip(COLUNAS_FILA, ("pronto_para_fazer", "em_andamento", "pronto")):
            texto += f"\n## {nome}\n{CABECALHO_FILA}"
            for cartao, pedido in colunas.get(chave, []):
                texto += f"| {cartao} | {cartao} | {pedido} | forge:tech-lead | 2026-10-21 | 2026-10-21 | |\n"
        self.gravar("KANBAN.md", texto)

    def pedido(self, id_, depende=None):
        linha = "" if depende is None else f"- **Depende de:** {depende}\n"
        self.gravar(f"docs/pedidos/{id_}.md", f"# Pedido {id_}\n\n- **Modo:** implementar\n{linha}\n## Escopo\n- E1. x\n")

    def teto(self, teto, agentes=0):
        self.gravar(".forge/config.json", json.dumps({"teto_agentes": teto}))
        self.gravar(".forge/run/agentes.json", json.dumps({"agentes": [
            {"id": f"a{i}", "tipo": "forge:dev", "descricao": "", "desde": time.time()} for i in range(agentes)]}))

    def rodar(self, *args, raiz=None):
        env = {**AMBIENTE, "FORGE_PROC": str(self.proc), "FORGE_NPROC": str(self.nucleos), "HOME": str(self.tmp / "home")}
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--raiz", str(raiz or self.tmp), "fila", *args], capture_output=True, text=True, env=env)
        return r.returncode, r.stdout.splitlines()

    def test_t1_dependencia_fora_de_pronto_espera(self):
        self.quadro(pronto_para_fazer=[("C1", "p1")], em_andamento=[("C0", "p0")])
        self.pedido("p1", "p0")
        self.pedido("p0")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[0], "espera: C1 (p1) | depende de p0 (coluna Em andamento)")
        self.assertTrue(linhas[-1].startswith("fila: 0 podem começar"), linhas)

    def test_t2_dependencia_em_pronto_pode_comecar(self):
        self.quadro(pronto_para_fazer=[("C1", "p1")], pronto=[("C0", "p0")])
        self.pedido("p1", "p0")
        self.pedido("p0")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[0], "pode-comecar: C1 (p1)")
        self.assertTrue(linhas[-1].startswith("fila: 1 podem começar"), linhas)

    def test_t3_ciclo_espera(self):
        self.quadro(pronto_para_fazer=[("C1", "p1"), ("C2", "p2")])
        self.pedido("p1", "p2")
        self.pedido("p2", "p1")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual([l for l in linhas if l.startswith("espera:")],
                         ["espera: C1 (p1) | ciclo de dependências", "espera: C2 (p2) | ciclo de dependências"])
        self.assertTrue(linhas[-1].startswith("fila: 0 podem começar"), linhas)

    def test_t4_excedentes_do_teto_esperam(self):
        self.quadro(pronto_para_fazer=[("C1", "p1"), ("C2", "p2"), ("C3", "p3")])
        for p in ("p1", "p2", "p3"):
            self.pedido(p, "nenhum")
        self.teto(3, agentes=1)  # 2 vagas
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[:3], ["pode-comecar: C1 (p1)", "pode-comecar: C2 (p2)", "espera: C3 (p3) | teto"])
        self.assertEqual(linhas[-1], "fila: 2 podem começar, 2 vagas de 3 (1 ativos), 1 esperam")

    def test_t5_carga_alta_zera_as_vagas(self):
        self.quadro(pronto_para_fazer=[("C1", "p1")])
        self.pedido("p1", "nenhum")
        self.teto(3)
        self.carga(50.0, nucleos=4)
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[0], "espera: C1 (p1) | teto")
        self.assertEqual(linhas[-1], "fila: 0 podem começar, 0 vagas de 3 (0 ativos), 1 esperam")

    def test_t6_sobreposicao_avisa_sem_bloquear(self):
        git(self.tmp, "init", "-q", "-b", "develop")
        self.gravar("base.txt", "base\n")
        git(self.tmp, "add", "base.txt")
        git(self.tmp, "commit", "-q", "-m", "base")
        for ramo in ("melhoria/p1", "melhoria/outra"):
            git(self.tmp, "switch", "-q", "-c", ramo, "develop")
            self.gravar("comum.txt", ramo)
            git(self.tmp, "add", "comum.txt")
            git(self.tmp, "commit", "-q", "-m", ramo)
        git(self.tmp, "switch", "-q", "develop")
        self.quadro(pronto_para_fazer=[("C1", "p1")])
        self.pedido("p1", "nenhum")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[0], "pode-comecar: C1 (p1)")
        self.assertIn("aviso: C1 sobrepõe melhoria/outra: comum.txt", linhas)
        self.assertTrue(linhas[-1].startswith("fila: 1 podem começar"), linhas)

    def test_t7_pedido_sem_a_linha_avisa_e_trata_como_nenhum(self):
        self.quadro(pronto_para_fazer=[("C1", "p1")])
        self.pedido("p1")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertIn("pode-comecar: C1 (p1)", linhas)
        self.assertIn("aviso: p1 sem Depende de", linhas)

    def test_agentes_ativos_vem_da_copia_principal_numa_worktree(self):
        principal, wt = self.tmp / "principal", self.tmp / "wt"
        principal.mkdir()
        git(principal, "init", "-q", "-b", "develop")
        (principal / "a.txt").write_text("a\n", encoding="utf-8")
        git(principal, "add", "a.txt")
        git(principal, "commit", "-q", "-m", "base")
        git(principal, "worktree", "add", "-q", "--no-track", "-b", "melhoria/x", str(wt))
        agentes = [{"id": f"a{i}", "tipo": "forge:dev", "descricao": "", "desde": time.time()} for i in range(2)]
        (principal / ".forge" / "run").mkdir(parents=True)
        (principal / ".forge" / "run" / "agentes.json").write_text(json.dumps({"agentes": agentes}), encoding="utf-8")
        (wt / ".forge").mkdir()
        (wt / ".forge" / "config.json").write_text(json.dumps({"teto_agentes": 3}), encoding="utf-8")
        self.tmp, original = wt, self.tmp
        try:
            self.quadro(pronto_para_fazer=[("C1", "p1")])
            self.pedido("p1", "nenhum")
            rc, linhas = self.rodar(raiz=wt)
        finally:
            self.tmp = original
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[-1], "fila: 1 podem começar, 1 vagas de 3 (2 ativos), 0 esperam", linhas)

    def test_agentes_vigentes_contados_sem_config_na_raiz(self):
        principal, wt = self.tmp / "principal", self.tmp / "wt"
        principal.mkdir()
        git(principal, "init", "-q", "-b", "develop")
        (principal / "a.txt").write_text("a\n", encoding="utf-8")
        git(principal, "add", "a.txt")
        git(principal, "commit", "-q", "-m", "base")
        git(principal, "worktree", "add", "-q", "--no-track", "-b", "melhoria/x", str(wt))
        agentes = [{"id": f"a{i}", "tipo": "forge:dev", "descricao": "", "desde": time.time()} for i in range(2)]
        (principal / ".forge" / "run").mkdir(parents=True)
        (principal / ".forge" / "run" / "agentes.json").write_text(json.dumps({"agentes": agentes}), encoding="utf-8")
        self.tmp, original = wt, self.tmp
        try:
            self.quadro(pronto_para_fazer=[("C1", "p1")])
            self.pedido("p1", "nenhum")
            rc, linhas = self.rodar(raiz=wt)
        finally:
            self.tmp = original
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[-1], "fila: 1 podem começar, 6 vagas de 8 (2 ativos), 0 esperam", linhas)

    def test_quadro_sem_as_colunas_avisa_qual_falta(self):
        self.gravar("KANBAN.md", f"# Quadro\n\n## Em andamento\n{CABECALHO_FILA}")
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertIn("aviso: o quadro não tem a coluna \"Pronto para fazer\"", linhas)
        self.assertIn("aviso: o quadro não tem a coluna \"Pronto\"", linhas)
        self.assertTrue(linhas[-1].startswith("fila: 0 podem começar"), linhas)

    def test_t8_sem_quadro(self):
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertEqual(len(linhas), 1)
        self.assertTrue(linhas[0].startswith("fila: ") and "não tem KANBAN.md" in linhas[0], linhas)
        self.assertFalse((self.tmp / "docs" / "kanban").exists())

    def test_saida_limitada_a_15_linhas_e_so_leitura(self):
        self.quadro(pronto_para_fazer=[(f"C{i}", f"p{i}") for i in range(30)])
        for i in range(30):
            self.pedido(f"p{i}", "nenhum")
        antes = sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*") if p.is_file())
        rc, linhas = self.rodar()
        self.assertEqual(rc, 0)
        self.assertLessEqual(len(linhas), 15)
        self.assertTrue(linhas[-1].startswith("fila: "))
        self.assertEqual(antes, sorted(p.relative_to(self.tmp).as_posix() for p in self.tmp.rglob("*") if p.is_file()))

    def test_ajuda_sai_com_zero(self):
        r = subprocess.run([sys.executable, str(FERRAMENTA), "fila", "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


def secao(titulo, *cartoes):
    return f"## {titulo}\n| {' | '.join(fc.COLUNAS)} |\n|---|---|---|---|---|---|---|\n" + "".join(f"| {c} |\n" for c in cartoes)


fc = SourceFileLoader("forge_check_quadro", str(FERRAMENTA)).load_module()
NOTA = "# Quadro\n\n> nota do agile-coach: fica byte a byte\n\n"
QUADRO = NOTA + secao("Em andamento (WIP 1 por agente)", "K-1 | Da ponte | p-1 | forge:dev | 2026-09-01 | x | y",
                      "K-9 | Sem movimento | p-1 | forge:qa | 2026-09-01 | x | y", "K-3 | Ponte ruim | p-1 | forge:X Y | 2026-09-01 | x | y") + \
    "\ntexto entre tabelas | com barra\n\n" + secao("Code review (WIP 2)") + "\n" + secao("Pronto") + "\n" + secao("Bloqueado")
AGORA = datetime.datetime(2026, 11, 7, 12, 0, tzinfo=datetime.timezone.utc)


def mov(dias, cartao, para, motivo="—"):
    return [(AGORA - datetime.timedelta(days=dias)).isoformat(timespec="seconds"), cartao, "—", para, motivo]


class QuadroGerado(unittest.TestCase):
    """EST-M12, E3-1a: `montar_quadro` pura (C-3 a C-6; casos de abuso 6, 13 e 14; legítimo 7 do modelo de ameaças)."""
    def montar(self, *movimentos, quadro=QUADRO):
        texto, por_secao, avisos = fc.montar_quadro(quadro, [["Data/hora", "Cartão", "De", "Para", "Motivo"], ["---"] * 5, *movimentos], AGORA)
        return texto, {c[0]: (s, *c[1:]) for s, cs in por_secao.items() for c in cs}, avisos

    def test_coluna_e_a_do_ultimo_movimento_na_ordem_do_arquivo_nunca_por_hora(self):
        _, q, avisos = self.montar(mov(10, "k-1", "Code review"), mov(-400, "K-1", "Pronto"), mov(5, "K-1", "Em andamento", "voltou"),
                                   ["ontem", "K-1", "—", "Pronto", "x"], mov(31, "P-1", "Pronto"), mov(29, "P-2", "Pronto"))
        self.assertEqual(q.get("K-1"), ("Em andamento", "Da ponte", "p-1", "forge:dev", mov(10, "", "")[0][:10], mov(5, "", "")[0], "voltou"))
        self.assertEqual([q.get("P-1"), q.get("P-2", "")[0]], [None, "Pronto"])  # a janela do Pronto: 31 dias sai, 29 fica
        self.assertIn("linha do histórico fora da forma, ignorada: ontem", avisos)

    def test_marca_do_fim_vence_a_ponte_e_marca_fora_da_forma_e_ignorada_inteira(self):
        _, q, avisos = self.montar(mov(3, "K-1", "Em andamento", "a · atributos: titulo=Novo; pedido=p-2; responsavel=forge:qa"),
                                   mov(2, "K-1", "Em andamento", "b · atributos: responsavel=forge:X"),
                                   mov(1, "K-1", "Em andamento", "c · atributos: responsavel=forge:y · atributos: pedido=p-3"))
        self.assertEqual(q.get("K-1")[1:4] + q.get("K-1")[6:], ("Novo", "p-3", "forge:qa", "c · atributos: responsavel=forge:y"))
        self.assertIn("cartão K-1: marca de atributos fora da forma, ignorada", avisos)
        for ruim in ("responsavel=forge:a; responsavel=forge:b", "dono=forge:a", "pedido=../x", "responsavel=forge:X", "titulo=a\u200bb", "titulo=", "titulo=a=b"):
            self.assertEqual(fc.ler_marca("m · atributos: " + ruim), ("m", None, "marca de atributos fora da forma, ignorada"), ruim)

    def test_ponte_fora_de_id_resp_vira_travessao_e_cartao_sem_movimento_fica(self):
        _, q, avisos = self.montar(mov(1, "K-3", "Em andamento"))
        self.assertEqual([q.get("K-3", "")[3:4], q.get("K-9", "")[1:2], q.get("K-1", "")[3:4]], [("—",), ("Sem movimento",), ("forge:dev",)])
        self.assertEqual(avisos, ["cartão K-3: responsável da linha do quadro fora da forma; vira —", "cartão K-1 sem movimento no histórico; fica onde está",
                                  "cartão K-9 sem movimento no histórico; fica onde está", "cartão K-3 sem responsável válido"])

    def test_estado_sem_secao_aparece_com_estado_e_aviso(self):
        _, q, avisos = self.montar(mov(1, "R-1", "Review", "rv"), mov(1, "R-2", "Integração"), mov(90, "R-3", "Feito"), mov(1, "R-4", "Outro"))
        self.assertEqual({i: (q[i][0], q[i][6]) for i in q if i.startswith("R-")}, {"R-1": ("Code review", "estado: Review · rv"),
                         "R-2": ("Code review", "estado: Integração · —"), "R-3": ("Pronto", "estado: Feito · —"), "R-4": ("Bloqueado", "estado: Outro · —")})
        self.assertIn('cartão R-1: estado "Review" sem seção no quadro; posto em Code review', avisos)
        self.assertIsNone(self.montar(mov(1, "R-4", "Outro"), quadro=NOTA + secao("Pronto"))[0])

    def test_texto_fora_das_tabelas_igual_quadro_passa_no_kanban_e_regerar_da_o_mesmo(self):
        historico = [mov(2, "K-1", "Code review"), mov(1, "N-1", "Pronto", "ok · atributos: titulo=T; pedido=p; responsavel=forge:dev")]
        legitimo = QUADRO.replace("| K-3 | Ponte ruim | p-1 | forge:X Y | 2026-09-01 | x | y |\n", "")
        texto, _, _ = self.montar(*historico, quadro=legitimo)
        fora = lambda t: [l for l in t.split("\n") if not l.startswith("|")]  # noqa: E731
        self.assertEqual(fora(texto), fora(QUADRO))
        self.assertEqual(self.montar(*historico, quadro=texto)[0], texto)
        self.assertIn("| N-1 | T | p | forge:dev |", texto)
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "KANBAN.md").write_text(texto, encoding="utf-8")
            self.assertEqual(fc.cmd_kanban(Path(tmp)), [])

    def test_quadro_por_coluna_corta_a_secao_como_colunas_do_quadro(self):  # C-6: a mesma função para os dois
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "KANBAN.md").write_text(secao("Pronto (develop)") + secao("Em andamento (WIP 3)"), encoding="utf-8")
            self.assertEqual([*fc.quadro_por_coluna(Path(tmp))], fc.colunas_do_quadro(Path(tmp))[:2])

    def test_proximo_ve_o_pedido_parado_em_secao_com_nota(self):  # C-6 no leitor: sem o corte, a coluna não casa ESPERAS_DO_PROXIMO
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "KANBAN.md").write_text(secao("Aguardando o dono (PA-6: resposta)", "K-1 | C | p-1 | forge:dev | 2026-09-01 | x | y"), encoding="utf-8")
            self.assertTrue(fc.pedido_em_coluna(Path(tmp), "p-1", fc.ESPERAS_DO_PROXIMO))

    def test_estados_antigos_vao_a_coluna_que_o_quadro_ja_lhes_da(self):  # adendo dos estados antigos; o resto segue em "Bloqueado"
        quadro = QUADRO + "\n" + secao("Entrada") + "\n" + secao("Pronto para fazer (WIP 5)")
        _, q, avisos = self.montar(mov(1, "E-1", "a fazer"), mov(1, "E-2", "Backlog"), mov(31, "E-3", "Pronto (develop)"), mov(1, "E-4", "Outro"), quadro=quadro)
        self.assertEqual({i: q[i][0] for i in q if i[0] == "E"}, {"E-1": "Pronto para fazer", "E-2": "Entrada", "E-3": "Pronto", "E-4": "Bloqueado"})
        self.assertIn('cartão E-3: estado "Pronto (develop)" sem seção no quadro; posto em Pronto', avisos)


SEGREDO = "TOKEN=x\n" + QUADRO


class KanbanGerar(unittest.TestCase):
    """EST-M12, E3-1b: `kanban --gerar` (C-1, C-2, C-10, C-15; casos de abuso 1 a 4 e duas gerações iguais do modelo de ameaças)."""
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raiz, self.fora = Path(self._tmp.name, "p"), Path(self._tmp.name, "segredo.md")
        self.kanban, self.hist = self.raiz / "KANBAN.md", self.raiz / "docs" / "kanban" / "historico.md"
        self.hist.parent.mkdir(parents=True)
        self.fora.write_text(SEGREDO, encoding="utf-8")
        self.kanban.write_text(QUADRO.replace("| K-3 | Ponte ruim | p-1 | forge:X Y | 2026-09-01 | x | y |\n", ""), encoding="utf-8")
        self.hist.write_text("| Data/hora | Cartão | De | Para | Motivo |\n|---|---|---|---|---|\n" + "".join(f"| {' | '.join(m)} |\n" for m in (
            mov(2, "K-1", "Code review"), mov(1, "N-1", "Em andamento", "ok · atributos: titulo=T; pedido=p; responsavel=forge:qa"))), encoding="utf-8")

    def recusa(self, causa, antes):
        linhas, rc = fc.cmd_kanban_gerar(self.raiz)
        self.assertEqual((rc, self.kanban.read_bytes(), self.fora.read_text(encoding="utf-8")), (1, antes, SEGREDO), causa)
        self.assertIn(causa, linhas[-1])

    def test_gera_do_historico_duas_vezes_igual_e_avisa_a_edicao_a_mao(self):  # C-15 e C-6 como aviso; legítimo 6
        rc, saida = checar(self.raiz, "kanban", "--gerar")
        self.assertEqual(rc, 0, saida)
        self.assertIn("aviso: quadro editado fora do movimento: K-1, N-1", saida)
        self.assertIn("forge:qa com 2 cartões", saida)  # o `kanban` sobre o quadro novo: K-9 e N-1 do mesmo agente sem worktree
        gerado = self.kanban.read_bytes()
        self.assertIn(b"| K-1 | Da ponte | p-1 | forge:dev |", gerado.split(b"## Code review")[1])
        self.assertEqual((fc.cmd_kanban_gerar(self.raiz)[1], self.kanban.read_bytes()), (0, gerado))
        self.assertNotIn("editado", "\n".join(fc.cmd_kanban_gerar(self.raiz)[0]))
        self.kanban.write_bytes(gerado.replace(b"| K-1 | Da ponte", b"| K-1 | A mao"))
        self.assertIn("aviso: quadro editado fora do movimento: K-1", fc.cmd_kanban_gerar(self.raiz)[0])

    def test_historico_link_grande_fifo_ou_ausente_recusa_com_o_quadro_intacto(self):  # C-1; casos 2 e 3
        antes = self.kanban.read_bytes()
        for causa, preparar in (("é link simbólico", lambda h: h.symlink_to(self.fora)), ("não existe", lambda h: None),
                                ("passa de", lambda h: h.write_bytes(b"|" * (fc.TETO_DA_TABELA + 1))), ("não é arquivo regular", os.mkfifo)):
            self.hist.unlink(missing_ok=True)
            preparar(self.hist)
            self.recusa(causa, antes)

    def test_kanban_link_recusa_sem_ler_nem_escrever_no_alvo(self):  # C-1; caso 1
        self.kanban.unlink()
        self.kanban.symlink_to(self.fora)
        self.recusa("KANBAN.md: é link simbólico", SEGREDO.encode())
        self.assertTrue(self.kanban.is_symlink())

    def test_temporario_exclusivo_e_apagado_em_erro(self):  # C-2; caso 4
        (self.raiz / ".KANBAN.tmp").symlink_to(self.fora)
        self.assertEqual(fc.cmd_kanban_gerar(self.raiz)[1], 0)
        antes = self.kanban.read_bytes()
        with mock.patch.object(fc.os, "replace", side_effect=OSError(5, "falhou")):
            self.recusa("falhou", antes)
        self.assertEqual([p.name for p in self.raiz.glob(".KANBAN.*")], [".KANBAN.tmp"])

    def test_trava_ocupada_ou_link_recusa_e_solta_gera(self):  # C-10 no `--gerar`
        antes, trava = self.kanban.read_bytes(), self.raiz / ".forge" / "run" / "quadro.trava"
        trava.parent.mkdir(parents=True)
        with open(trava, "w") as f, mock.patch.object(fc, "ESPERA_DA_TRAVA_S", 0.3):
            fcntl.flock(f, fcntl.LOCK_EX)
            self.recusa("trava do quadro ocupada", antes)
        trava.unlink()
        trava.symlink_to(self.fora)
        self.recusa("quadro.trava", antes)
        trava.unlink()
        self.assertEqual(fc.cmd_kanban_gerar(self.raiz)[1], 0)


if __name__ == "__main__":
    unittest.main()
