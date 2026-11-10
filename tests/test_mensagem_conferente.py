"""T6 (T6T3-MENSAGEM): a mensagem ao conferente sai inteira do `forge-check brief mensagem`: a etapa vem do brief (E1) e a do modo
entrega também (E2). Raiz sintética do `Cenario`; biblioteca padrão, sem rede."""
import hashlib
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import ARQ, FORGE_CHECK_CC, ID, Cenario, carregar_forge_check, git  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

SHA_A, SHA_B, BASE_SHA = "a" * 40, "b" * 40, "c" * 40
SEM_WORKTREE = "--entrega exige --worktree <pasta absoluta existente> e não aceita --anterior, --ref nem --parecer"
SEM_CABECALHO = "--entrega exige `Etapa:`, `Branch:`, `Base:` e `Base-sha:` (40 hex) no cabeçalho do brief"
CABECALHO = f"Etapa: codigo   Cobre: E1.1\nBranch: melhoria/x   Base: develop   Base-sha: {BASE_SHA}\n"


class MensagemPelaEtapaDoBrief(Cenario):
    def setUp(self):
        super().setUp()
        self.completo = self.completo.replace("Agente destino: forge:dev-exemplo\n", "Agente destino: forge:dev-exemplo\n" + CABECALHO, 1)
        self.gravar(ARQ, self.completo)
        self.pasta = self.tmp / "wt"
        self.pasta.mkdir()

    def entrega(self, *extra, pedido_extra=""):
        self.gravar("docs/pedidos/pedido-sintetico.md", self.PEDIDO_CITANDO + "\n## Histórico\n" + pedido_extra)
        return self.mensagem("--entrega", *extra, etapa=None)

    def test_a_etapa_sai_da_linha_etapa_do_brief(self):
        rc, saida = self.mensagem(etapa=None)
        self.assertEqual(rc, 0, saida)
        self.assertIn("Etapa: codigo", saida.decode().splitlines()[1])
        self.assertEqual(self.mensagem(etapa="codigo")[0], 0)

    def test_etapa_diferente_da_do_brief_e_recusada_com_a_etapa_certa(self):
        rc, saida = self.mensagem(etapa="pr")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), "brief mensagem: --etapa difere da `Etapa:` do brief; a etapa do brief é codigo")

    def test_entrega_traz_tudo_do_arquivo_e_o_desde_da_ultima_conferida(self):
        historico = f"- 2026-10-29 07:36: entrega conferida {SHA_A}\n- 2026-10-29 10:08: entrega conferida {SHA_B}\n"
        rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra=historico)
        self.assertEqual(rc, 0, saida)
        conteudo = (self.tmp / ARQ).read_bytes()
        esperado = ["modo: entrega", f"Pedido: {ID}", "Agente conferido: forge:dev-exemplo", f"Arquivo: {(self.tmp / ARQ).resolve()}",
                    f"Worktree: {self.pasta}", "Branch: melhoria/x", "Base: develop", f"Base-sha: {BASE_SHA}", f"Desde: {SHA_B}",
                    f"Brief-sha256: {hashlib.sha256(conteudo).hexdigest()}", "Etapa: codigo"]
        self.assertEqual(saida.decode().splitlines(), esperado)  # TEMPO-B1: sem o bloco do texto
        self.assertNotIn(b"<<<BRIEF", saida)

    def test_sem_conferida_no_historico_a_linha_desde_nao_sai(self):
        rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra="- 2026-10-29 07:36: aberto\n")
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("Desde:", saida.decode())

    def test_desde_e_a_linha_mais_recente_entre_conferida_e_base_do_dono(self):
        dono = f"- 2026-10-29 11:00: base do delta fixada pelo dono {SHA_B}\n"
        decisao = "DECISÃO DO DONO (2026-10-29): \"fixar a base\".\n"
        conferida = f"- 2026-10-29 07:36: entrega conferida {SHA_A}\n"
        casos = {"dono depois da conferida": (decisao + conferida + dono, SHA_B), "so a do dono": (decisao + dono, SHA_B),
                 "conferida depois do dono": (decisao + dono + conferida, SHA_A)}
        for nome, (historico, esperado) in casos.items():
            with self.subTest(nome):
                rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra=historico)
                self.assertEqual(rc, 0, saida)
                self.assertIn(f"Desde: {esperado}", saida.decode().splitlines())

    def recusa(self, motivo, *extra):
        rc, saida = self.entrega(*extra)
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), f"brief mensagem: {motivo}")

    def test_entrega_sem_worktree_e_recusada(self):
        self.recusa(SEM_WORKTREE)

    def test_entrega_com_worktree_relativo_e_recusada(self):
        self.recusa(SEM_WORKTREE, "--worktree", ".")

    def test_entrega_com_worktree_inexistente_e_recusada(self):
        self.recusa(SEM_WORKTREE, "--worktree", str(self.pasta / "nao-existe"))

    def test_entrega_com_ref_anterior_ou_parecer_e_recusada(self):
        for extra in (("--ref", "melhoria/x"), ("--anterior", ARQ), ("--parecer", "docs/reviews/x.md")):
            with self.subTest(extra=extra):
                self.recusa(SEM_WORKTREE, "--worktree", str(self.pasta), *extra)

    def test_entrega_com_controle_no_worktree_e_recusada_sem_imprimir_o_valor(self):
        rc, saida = self.entrega("--worktree", str(self.pasta) + "\x01")
        self.assertEqual(rc, 2, saida)
        self.assertEqual(saida.decode().strip(), "brief mensagem: o campo --worktree tem o caractere de controle ou de formato U+0001")

    def test_brief_sem_etapa_branch_base_ou_base_sha_recusa_a_entrega(self):
        for faltando in ("Etapa: codigo   ", "Branch: melhoria/x   ", "Base: develop   ", f"   Base-sha: {BASE_SHA}"):
            with self.subTest(faltando=faltando):
                self.gravar(ARQ, self.completo.replace(faltando, "", 1))
                self.recusa(SEM_CABECALHO, "--worktree", str(self.pasta))


class DesdeNaBranchNova(Cenario):
    """P-N1: a worktree é um repositório; com a última conferida fora do head e o Base-sha ancestral dele, o `Desde:` é o Base-sha."""

    entrega = MensagemPelaEtapaDoBrief.entrega

    def setUp(self):
        super().setUp()
        self.pasta = self.tmp / "wt"
        self.pasta.mkdir()
        git("init", "-q", "-b", "develop", cwd=self.pasta)
        self.base = self.commitar("base")
        git("switch", "-q", "-c", "melhoria/velha", cwd=self.pasta)
        self.velha = self.commitar("branch anterior, integrada por squash")
        git("switch", "-q", "--no-track", "-c", "melhoria/x", self.base, cwd=self.pasta)
        self.c1 = self.commitar("branch nova")
        self.gravar(ARQ, self.completo.replace("Agente destino: forge:dev-exemplo\n",
                                               "Agente destino: forge:dev-exemplo\n" + CABECALHO.replace(BASE_SHA, self.base), 1))

    def commitar(self, mensagem):
        git("-c", "user.name=Teste", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", mensagem, cwd=self.pasta)
        return git("rev-parse", "HEAD", cwd=self.pasta).stdout.strip()

    def desde(self, historico):
        rc, saida = self.entrega("--worktree", str(self.pasta), pedido_extra=historico)
        self.assertEqual(rc, 0, saida)
        return [linha for linha in saida.decode().splitlines() if linha.startswith("Desde:")]

    def test_conferida_fora_do_head_da_o_base_sha(self):
        self.assertEqual(self.desde(f"- 2026-10-29 07:36: entrega conferida {self.velha}\n"), [f"Desde: {self.base}"])

    def test_conferida_ancestral_do_head_segue_sendo_o_desde(self):
        historico = f"- 2026-10-29 07:36: entrega conferida {self.velha}\n- 2026-10-29 10:08: entrega conferida {self.c1}\n"
        self.assertEqual(self.desde(historico), [f"Desde: {self.c1}"])

    def test_sem_conferida_fica_o_comportamento_de_hoje(self):
        self.assertEqual(self.desde("- 2026-10-29 07:36: aberto\n"), [])
        dono = f"DECISÃO DO DONO (2026-10-29): \"fixar a base\".\n- 2026-10-29 11:00: base do delta fixada pelo dono {self.c1}\n"
        self.assertEqual(self.desde(dono), [f"Desde: {self.base}"])  # E12: a base do dono igual ao head não vale (o `entrega` a recusa)

    def test_desde_e_a_base_da_propria_branch_mesmo_com_outra_depois(self):  # E12 (CONFERIDA-DESDE-POR-BRANCH, MENSAGEM-DESDE-BASE-DONO)
        c2 = self.commitar("segunda entrega da branch nova")
        decisao = "DECISÃO DO DONO (2026-10-29): \"fixar a base\".\n"
        da_outra = f"- 2026-10-29 12:00: entrega conferida {self.velha}\n"
        casos = {"conferida da branch, depois a de outra": (f"- 2026-10-29 10:08: entrega conferida {self.c1}\n" + da_outra, self.c1),
                 "base do dono da branch, depois a de outra": (decisao + f"- 2026-10-29 11:00: base do delta fixada pelo dono {self.c1}\n" + da_outra, self.c1),
                 "só a de outra branch": (da_outra, self.base),
                 "base do dono igual ao head": (decisao + f"- 2026-10-29 11:00: base do delta fixada pelo dono {c2}\n", self.base)}
        for nome, (historico, esperado) in casos.items():
            with self.subTest(nome):
                self.assertEqual(self.desde(historico), [f"Desde: {esperado}"])


class UniaoDeEntregas(Cenario):  # UM-BRIEF: a união saiu; o um brief só de hoje (f) segue em MensagemPelaEtapaDoBrief
    def setUp(self):
        super().setUp()
        self.gravar("docs/pedidos/pedido-sintetico.md", self.PEDIDO_CITANDO + "\n## Histórico\n")
        self.pasta = self.tmp / "wt"
        self.pasta.mkdir()
        self.briefs = {p: self.brief_de(p, t) for p, t in (("tech-lead", "review"), ("qa-engineer", "qa"), ("dev-exemplo", "codigo"))}

    def brief_de(self, papel, tipo, sha=BASE_SHA, n=1):
        nome = f"docs/briefs/{ID}-{papel}-{n}.md"
        cabecalho = f"Agente destino: forge:{papel}\n" + (f"Tipo: {tipo}\n" if tipo else "") + CABECALHO.replace(BASE_SHA, sha)
        self.gravar(nome, self.completo.replace("Agente destino: forge:dev-exemplo\n", cabecalho, 1))
        return nome

    def uniao(self, *arquivos, extra=("--entrega", "--worktree")):
        args = ["brief", "mensagem", "--pedido", ID, *extra, *([str(self.pasta)] if "--worktree" in extra else []), "--arquivo", *arquivos]
        r = subprocess.run([sys.executable, FORGE_CHECK_CC, "--raiz", str(self.tmp), *args], capture_output=True, env=dict(os.environ, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout.decode()

    def recusada(self, trecho, *arquivos, **kw):
        rc, saida = self.uniao(*arquivos, **kw)
        self.assertEqual(rc, 2, saida)
        self.assertIn(trecho, saida)
        self.assertNotIn("modo: entrega", saida)  # C-1: nada sai antes de todas as recusas

    def test_varios_arquivos_sao_recusados_sem_bloco(self):  # UM-BRIEF (versao-075 UN-1): o caso que a união aceitava
        tl, qa = self.briefs["tech-lead"], self.briefs["qa-engineer"]
        for extra in (("--entrega", "--worktree"), ()):
            with self.subTest(extra=extra):
                self.recusada("um brief por mensagem", tl, qa, extra=extra)

    def test_pq_de_parecer_em_head_avisa_sem_mudar_o_rc(self):  # (g), C-9 e C-10
        pq, rcs = "`grep -c recurso docs/pedidos/pedido-sintetico.md`", set()
        casos = {("review", "`git log -1 --format=%H`"): True, ("qa", "`git rev-parse HEAD~1`"): True,
                 ("review", f"`git log -1 --format=%H {SHA_A}`"): False, ("codigo", "`git rev-parse HEAD`"): False}
        for (tipo, comando), avisa in casos.items():
            with self.subTest(tipo=tipo, comando=comando):
                tipado = self.completo.replace("forge:dev-exemplo\n", f"forge:dev-exemplo\nTipo: {tipo}\n", 1)
                self.gravar(ARQ, tipado.replace(pq, comando))
                rc, saida = self.brief()
                rcs.add(rc)
                self.assertEqual("aviso: PQ-2 de parecer lê HEAD; fixe o sha40 do commit do parecer" in "\n".join(saida), avisa, saida)
        self.assertEqual(len(rcs), 1)
        le_head_sem_sha, longo = carregar_forge_check().le_head_sem_sha, "H@-/a" * 52429  # C-10: 256 KiB numa linha só
        inicio = time.monotonic()
        self.assertFalse(le_head_sem_sha(longo, longo))
        self.assertLess(time.monotonic() - inicio, 1)


if __name__ == "__main__":
    unittest.main()
