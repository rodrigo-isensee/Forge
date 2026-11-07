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
DECISÃO DO DONO (2026-01-01 10:00): "A" — lote em {sha}
"""
DATAS = {"GIT_AUTHOR_DATE": "2026-01-01T10:00:00Z", "GIT_COMMITTER_DATE": "2026-01-01T10:00:00Z"}  # sha determinístico


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-citacao-p2-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.gravar("docs/a.md", "um\n")
        self.gravar("docs/base.md", "na base\n")
        self.git("init", "-q", "-b", "develop")
        self.git("add", "docs/base.md")
        self.commit("base")
        self.base = self.num_base = self.numerado("base")  # sha[:7] só de algarismos (adendo (1) do E4)
        self.git("checkout", "-q", "-b", "lado")
        self.lado = self.commit("lado")  # existe no repositório, fora da base e da branch
        self.num_lado = self.numerado("lado")
        self.decisao = self.pedido(self.lado[:7])
        self.git("checkout", "-q", "-b", "melhoria/x", self.base)
        self.ponta = self.commit("ponta")  # só na branch do brief

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
                               *args], capture_output=True, text=True, check=True, env=dict(os.environ, **DATAS)).stdout.strip()

    def numerado(self, nome):
        for i in range(400):
            sha = self.commit(f"{nome} {i}")
            if sha[:7].isdigit():
                return sha
        self.fail("400 commits sem sha[:7] só de algarismos; troque a data fixa em DATAS")

    def pedido(self, sha):
        texto = PEDIDO.format(sha=sha)
        self.gravar("docs/pedidos/exemplo.md", texto)
        return texto.strip().split("\n")[-1]

    def commit(self, nome):
        self.git("commit", "-q", "--allow-empty", "-m", nome)
        return self.git("rev-parse", "HEAD")

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def conferir(self, entregar="- Recurso (E1), etapa (E1.1).", ler="- docs/a.md", pronto="- PQ-1 (cmd): `true` · espera: rc=0",
                 decisoes=None):
        decisoes = decisoes if decisoes is not None else f"- {self.decisao}"
        texto = (f"Agente destino: forge:dev-exemplo\nPedido: exemplo\nBranch: melhoria/x   Base: develop   Base-sha: {self.base}\n\n"
                 f"## Objetivo\nExemplo.\n\n## Ler\n{ler}\n\n## Entregar\n{entregar}\n\n## Fora do escopo\n- nada.\n\n"
                 f"## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): \"A\".\n{decisoes}\n\n"
                 f"## Pronto quando\n{pronto}\n\n## Relatório\nAté 8 linhas.\n")
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), "brief", str(self.gravar("b.md", texto)),
                            "--pedido", "exemplo"], capture_output=True, text=True, env=dict(os.environ, HOME=str(self.tmp / "home")),
                           timeout=60)
        return r.returncode, r.stdout


class PqCitado(Base):
    def test_pq_citado_fora_do_pronto_quando_existe_nele(self):  # mutante: PQ-n sem conferência
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), provado pelo PQ-1 e pelo PQ-2.")
        self.assertIn("citação: PQ-2 citado fora do Pronto quando não existe nele", saida)
        self.assertNotIn("citação: PQ-1", saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir("- Recurso (E1), etapa (E1.1), provado pelo PQ-1.")
        self.assertEqual(rc, 0, saida)

    def test_pronto_quando_nao_cobra_pq_nem_registro_dele(self):  # (4) e (2) leem só fora do Pronto quando
        rc, saida = self.conferir(pronto="- PQ-1 (cmd): `true` · espera: rc=0, como o PQ-9 e docs/pedidos/exemplo-9.md")
        self.assertNotIn("citação: PQ-9", saida)
        self.assertNotIn("exemplo-9.md", saida)


if __name__ == "__main__":
    unittest.main()
