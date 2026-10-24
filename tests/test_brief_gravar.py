"""P6 (LOTE-FORGE-CHECK-0.28.0): brief só pelo gerador. `brief gerar --gravar` escolhe o número livre (maior + 1), abre com `x` (nunca
sobrescreve), grava o lote (um arquivo por destino) e o `conferencia registrar` aprovado deixa o brief só leitura. Sem rede."""
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_brief_gravar", str(FORGE_CHECK)).load_module()

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E1.1 (dev-exemplo): implementação do recurso X.
- E1.2 (revisor-exemplo): review do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-gravar-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.addCleanup(self.liberar)
        self.gravar("docs/pedidos/exemplo.md", PEDIDO)
        self.gravar("KANBAN.md", "# Quadro\n")
        self.briefs = self.tmp / "docs" / "briefs"

    def liberar(self):  # o rmtree não apaga arquivo 0444 em alguns sistemas de arquivos montados
        for arq in self.tmp.rglob("*"):
            if arq.is_file() and not arq.is_symlink():
                arq.chmod(0o644)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), *map(str, args)], capture_output=True,
                           text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout

    def gerar(self, *destinos):
        return self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", *[f"forge:{d}" for d in destinos], "--gravar")


class Gravar(Base):
    def test_duas_vezes_grava_1_e_2_e_nunca_reescreve(self):
        rc, saida = self.gerar("dev-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertRegex(saida, r"^brief gravado: docs/briefs/exemplo-dev-exemplo-1\.md \d+ sha256 [0-9a-f]{64}\n$")
        primeiro = (self.briefs / "exemplo-dev-exemplo-1.md").read_bytes()
        rc, saida = self.gerar("dev-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertIn("exemplo-dev-exemplo-2.md", saida)
        self.assertEqual((self.briefs / "exemplo-dev-exemplo-1.md").read_bytes(), primeiro)
        self.assertIn("Agente destino: forge:dev-exemplo", primeiro.decode())

    def test_lacuna_nao_se_reaproveita(self):
        self.gravar("docs/briefs/exemplo-dev-exemplo-3.md", "antigo\n")
        rc, saida = self.gerar("dev-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertIn("exemplo-dev-exemplo-4.md", saida)
        self.assertFalse((self.briefs / "exemplo-dev-exemplo-1.md").exists())

    def test_arquivo_criado_entre_a_escolha_e_a_abertura_e_recusado(self):
        alvo = self.gravar("docs/briefs/exemplo-dev-exemplo-1.md", "de outro processo\n")
        linha, rc = fc.gravar_brief(self.tmp, "exemplo", "forge:dev-exemplo", "novo\n", numero=1)
        self.assertEqual(rc, 2)
        self.assertIn("já existe; nada gravado", linha)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "de outro processo\n")

    def test_lote_grava_um_arquivo_por_destino(self):
        rc, saida = self.gerar("dev-exemplo", "revisor-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertEqual(len(saida.splitlines()), 2, saida)
        self.assertTrue((self.briefs / "exemplo-dev-exemplo-1.md").is_file())
        self.assertIn("Cobre: E1.2", (self.briefs / "exemplo-revisor-exemplo-1.md").read_text(encoding="utf-8"))

    def test_lote_sem_gravar_e_recusado_e_recusa_de_um_destino_nao_grava_nada(self):
        rc, _ = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "forge:revisor-exemplo")
        self.assertEqual(rc, 2)
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "forge:revisor-exemplo",
                               "--gravar", "--cobre", "E1.2")
        self.assertEqual(rc, 2, saida)
        self.assertFalse(self.briefs.exists() and any(self.briefs.iterdir()))

    def test_sem_gravar_so_imprime(self):
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertFalse(self.briefs.exists())


class Protegido(Base):
    def registrar(self, brief):
        return self.rodar("conferencia", "registrar", "--pedido", "exemplo", "--brief", brief, "--modo", "brief",
                          "--rodada", "1", "--resultado", "aprovado", "--merito", "s")

    def test_registro_aprovado_deixa_o_brief_so_leitura(self):
        arq = self.gravar("docs/briefs/exemplo-dev-exemplo-1.md", "brief\n")
        rc, saida = self.registrar("exemplo-dev-exemplo-1")
        self.assertEqual(rc, 0, saida)
        self.assertIn("brief protegido: docs/briefs/exemplo-dev-exemplo-1.md (0444)", saida)
        self.assertEqual(stat.S_IMODE(arq.stat().st_mode), 0o444)

    def test_link_simbolico_nao_e_protegido(self):
        fora = self.gravar("fora.md", "alvo\n")
        self.briefs.mkdir(parents=True)
        (self.briefs / "exemplo-dev-exemplo-1.md").symlink_to(fora)
        rc, saida = self.registrar("exemplo-dev-exemplo-1")
        self.assertEqual(rc, 0, saida)
        self.assertIn("é link simbólico; não protejo", saida)
        self.assertNotEqual(stat.S_IMODE(fora.stat().st_mode), 0o444)

    def test_reprovado_nao_protege(self):
        arq = self.gravar("docs/briefs/exemplo-dev-exemplo-1.md", "brief\n")
        self.rodar("conferencia", "registrar", "--pedido", "exemplo", "--brief", "exemplo-dev-exemplo-1", "--modo", "brief",
                   "--rodada", "1", "--resultado", "reprovado", "--merito", "s", "--classe", "outra")
        self.assertNotEqual(stat.S_IMODE(arq.stat().st_mode), 0o444)


if __name__ == "__main__":
    unittest.main()
