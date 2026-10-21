"""`forge-check sobreposicao` (TA-6) e `forge-check movimento` (PA-9), mais a fila de integração (PA-3) como texto;
`forge-check fila` (P9: o que pode começar agora, T1 a T8)."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

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
        (self.raiz / "KANBAN.md").write_text("# Quadro\n", encoding="utf-8")  # sem quadro o movimento recusa (FC-PEDIDO-FORA)
        self.arq = self.raiz / "docs" / "kanban" / "historico.md"

    def test_cria_o_arquivo_e_acrescenta_com_hora_iso_e_fuso(self):
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Aguardando o dono", "--para", "Sem credencial")[0], 0)
        self.assertEqual(checar(self.raiz, "movimento", "K-1", "--de", "Sem credencial", "--para", "Em andamento", "--motivo", "chegou")[0], 0)
        linhas = self.arq.read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[:2], ["| Data/hora | Cartão | De | Para | Motivo |", "|---|---|---|---|---|"])
        iso = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d"
        self.assertRegex(linhas[2], rf"^\| {iso} \| K-1 \| Aguardando o dono \| Sem credencial \| — \|$")
        self.assertRegex(linhas[3], rf"^\| {iso} \| K-1 \| Sem credencial \| Em andamento \| chegou \|$")
        self.assertEqual(len(linhas), 4)

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
        checar(self.raiz, "movimento", "K-4", "--de", "a\x1b[31mb", "--para", "c\x01d\x7f", "--motivo", "e\x07f")
        linha = self.arq.read_text(encoding="utf-8").splitlines()[-1]
        self.assertTrue(linha.endswith("| K-4 | a[31mb | cd | ef |"), linha)
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
        t = self.texto("agents/jarvis.md")
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

    def rodar(self, *args):
        env = {**AMBIENTE, "FORGE_PROC": str(self.proc), "FORGE_NPROC": str(self.nucleos), "HOME": str(self.tmp / "home")}
        r = subprocess.run([sys.executable, str(FERRAMENTA), "--raiz", str(self.tmp), "fila", *args], capture_output=True, text=True, env=env)
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


if __name__ == "__main__":
    unittest.main()
