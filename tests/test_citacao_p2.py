"""ACELERA-P2 (versao-037, E4): no `forge-check brief`, sha do corpo na base ou na branch (ou `(outro repositório)` depois dele),
pedido e brief citados, caminho do `Ler` (ou `(novo)`) e `PQ-n` fora do `Pronto quando` existem; um caso que reprova e um que
passa por item."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")

PEDIDO = """---
id: exemplo
---
## Escopo
- E1. Fazer o recurso X

## Etapas
- E1.1 (dev-exemplo): implementação do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-citacao-p2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.gravar("docs/pedidos/exemplo.md", PEDIDO)
        self.gravar("docs/a.md", "um\n")
        self.gravar("docs/base.md", "na base\n")
        self.git("init", "-q", "-b", "develop")
        self.git("add", "docs/base.md")
        self.base = self.commit("base")
        self.git("checkout", "-q", "-b", "lado")
        self.lado = self.commit("lado")  # existe no repositório, fora da base e da branch
        self.git("checkout", "-q", "-b", "melhoria/x", self.base)
        self.ponta = self.commit("ponta")  # só na branch do brief

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                               *args], capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, nome):
        self.git("commit", "-q", "--allow-empty", "-m", nome)
        return self.git("rev-parse", "HEAD")

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def conferir(self, entregar="- Recurso (E1), etapa (E1.1).", ler="- docs/a.md", pronto="- PQ-1 (cmd): `true` · espera: rc=0"):
        texto = (f"Agente destino: forge:dev-exemplo\nPedido: exemplo\nBranch: melhoria/x   Base: develop   Base-sha: {self.base}\n\n"
                 f"## Objetivo\nExemplo.\n\n## Ler\n{ler}\n\n## Entregar\n{entregar}\n\n## Fora do escopo\n- nada.\n\n"
                 "## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): \"A\".\n\n"
                 f"## Pronto quando\n{pronto}\n\n## Relatório\nAté 8 linhas.\n")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "brief", str(self.gravar("b.md", texto)),
                            "--pedido", "exemplo"], capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")),
                           timeout=60)
        return r.returncode, r.stdout


class ShaCitado(Base):
    def test_sha_da_base_e_da_branch_passa(self):
        rc, saida = self.conferir(f"- Recurso (E1), etapa (E1.1) sobre {self.base[:7]} e {self.ponta[:10]}.")
        self.assertNotIn("citação: sha", saida)
        self.assertEqual(rc, 0, saida)

    def test_sha_que_existe_fora_da_base_e_da_branch_reprova(self):  # mutante: só existência, sem ancestralidade
        rc, saida = self.conferir(f"- Recurso (E1), etapa (E1.1) sobre {self.lado[:7]}.")
        self.assertIn(f"citação: sha {self.lado[:7]} não existe ou não está na base nem na branch", saida)
        self.assertEqual(rc, 1)

    def test_sha_que_nao_existe_reprova(self):
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1) sobre 0badc0de1.")
        self.assertIn("citação: sha 0badc0d não existe", saida)
        self.assertEqual(rc, 1)

    def test_outro_repositorio_marcado_passa(self):
        rc, saida = self.conferir(f"- Recurso (E1), etapa (E1.1) sobre {self.lado[:7]} (outro repositório).")
        self.assertNotIn("citação: sha", saida)
        self.assertEqual(rc, 0, saida)

    def test_decisao_do_dono_e_pronto_quando_sao_cobrados(self):  # (a) o corpo inteiro, fora só o cabeçalho
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1).\n- DECISÃO DO DONO (2026-01-01): \"A\" sobre 0badc0de1.",
                                  pronto="- PQ-1 (cmd): `git merge-base --is-ancestor 1badc0de origin/develop` · espera: rc=0")
        self.assertIn("citação: sha 0badc0d não existe", saida)
        self.assertIn("citação: sha 1badc0d não existe", saida)
        self.assertEqual(rc, 1)

    def test_merge_commit_do_gerar_nao_e_sha(self):  # (a) o PQ que o `brief gerar` põe na etapa de merge (S-18)
        rc, saida = self.conferir(pronto="- PQ-1 (cmd): `git merge-base --is-ancestor <mergeCommit> origin/develop` · espera: rc=0")
        self.assertNotIn("citação: sha", saida)

    def test_outro_repositorio_dispensa_so_o_sha_que_acompanha(self):  # (b)
        rc, saida = self.conferir(f"- Recurso (E1), etapa (E1.1) sobre {self.lado[:7]} (outro repositório) e 0badc0de1.")
        self.assertNotIn(f"sha {self.lado[:7]}", saida)
        self.assertIn("citação: sha 0badc0d não existe", saida)
        self.assertEqual(rc, 1)

    def test_sha_so_de_letras_e_cobrado_e_numero_puro_nao(self):  # (c) número puro: run, ruleset, pidns (relatório da volta 1)
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1) sobre deadbee, no run 40505555559 e no ruleset 25432260.")
        self.assertIn("citação: sha deadbee não existe", saida)
        self.assertNotIn("sha 4050555", saida)
        self.assertNotIn("sha 2543226", saida)
        self.assertEqual(rc, 1)


class RegistroCitado(Base):
    def test_pedido_e_brief_que_existem_passam_e_o_ausente_reprova(self):
        self.gravar("home/.forge-contrib/docs/briefs/outro-1.md", "x\n")
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), como docs/pedidos/exemplo.md e docs/briefs/outro-1.md.")
        self.assertNotIn("não existe na raiz", saida)
        self.assertEqual(rc, 0, saida)
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), como docs/pedidos/exemplo-2.md.")
        self.assertIn('citação: "docs/pedidos/exemplo-2.md" não existe na raiz nem nas raízes de brief', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1) e o brief docs/briefs/outro-2.md (novo).")  # (d) sem exceção
        self.assertIn('citação: "docs/briefs/outro-2.md" não existe na raiz nem nas raízes de brief', saida)
        self.assertEqual(rc, 1)


class CaminhoDoLer(Base):
    def test_caminho_ausente_reprova_e_novo_passa(self):
        rc, saida = self.conferir(ler="- docs/b.md e docs/a.md")
        self.assertIn('citação: Ler cita "docs/b.md", que não existe', saida)
        self.assertNotIn('"docs/a.md"', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(ler="- docs/b.md (novo)")
        self.assertEqual(rc, 0, saida)
        rc, saida = self.conferir(ler=f"- {self.tmp}/docs/a.md e {self.tmp}/docs/c.md.")
        self.assertIn(f'citação: Ler cita "{self.tmp}/docs/c.md", que não existe', saida)
        self.assertNotIn("docs/a.md", saida.split("citação: Ler")[1])
        self.assertEqual(rc, 1)

    def test_caminho_so_no_base_sha_passa(self):
        (self.tmp / "docs" / "base.md").unlink()  # fora do disco, segue no commit do Base-sha
        rc, saida = self.conferir(ler="- docs/base.md")
        self.assertNotIn("citação: Ler", saida)
        self.assertEqual(rc, 0, saida)


class PqCitado(Base):
    def test_pq_citado_fora_do_pronto_quando_existe_nele(self):  # mutante: PQ-n sem conferência
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), provado pelo PQ-1 e pelo PQ-2.")
        self.assertIn("citação: PQ-2 citado fora do Pronto quando não existe nele", saida)
        self.assertNotIn("citação: PQ-1", saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), provado pelo PQ-1.")
        self.assertEqual(rc, 0, saida)


if __name__ == "__main__":
    unittest.main()
