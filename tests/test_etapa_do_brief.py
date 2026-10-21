"""M16, P2 e M5 (LOTE-FORGE-CHECK-0.28.0): a etapa no brief. Regra única de marca (R-BRIEF): um brief delega uma só etapa; toda
outra etapa do pedido vai ao "Fora do escopo" sem a marca; a marca só no corte real. Parser com sufixo de letra e etapas de qualquer
`E<n>`. Biblioteca padrão, sem rede; fixtures neutras."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")
fc = SourceFileLoader("forge_check_etapa_do_brief", str(FORGE_CHECK)).load_module()

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO
Modo: implementar

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E0.1 (arquiteto-exemplo): desenho do recurso X.
- E0.2 (seguranca-exemplo): modelo de ameaças do recurso X.
- E1.1 (dev-exemplo): implementação do recurso X.
- E1.2 (revisor-exemplo): review do recurso X.
- E1.3 (seguranca-exemplo): review de segurança do recurso X.
- E1.3b (infra-exemplo): parecer de infraestrutura do recurso X.
- E1.4 (qa-exemplo): QA do recurso X.
- E1.5 (revisor-exemplo, outra instância): merge na develop.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""

ETAPAS = {
    "E0.1": '"E0.1 (arquiteto-exemplo): desenho do recurso X."',
    "E0.2": '"E0.2 (seguranca-exemplo): modelo de ameaças do recurso X."',
    "E1.1": '"E1.1 (dev-exemplo): implementação do recurso X."',
    "E1.2": '"E1.2 (revisor-exemplo): review do recurso X."',
    "E1.3": '"E1.3 (seguranca-exemplo): review de segurança do recurso X."',
    "E1.3b": '"E1.3b (infra-exemplo): parecer de infraestrutura do recurso X."',
    "E1.4": '"E1.4 (qa-exemplo): QA do recurso X."',
    "E1.5": '"E1.5 (revisor-exemplo, outra instância): merge na develop."',
}


def brief(destino, entregar, fora):
    return (f"Agente destino: forge:{destino}\n\n## Objetivo\nExemplo.\n\n## Ler\n- o pedido.\n\n## Entregar\n"
            + "".join(f"- {linha}\n" for linha in entregar)
            + "\n## Fora do escopo\n" + "".join(f"- {linha}\n" for linha in fora)
            + '\n## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): "A".\n\n## Pronto quando\n'
              "- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.\n\n## Relatório\nAté 8 linhas.\n")


def fora_sem(*exceto):
    return [f"{t} · outra etapa do pedido; continua nele" for e, t in ETAPAS.items() if e not in exceto]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-etapa-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedido = self.gravar("docs/pedidos/exemplo.md", PEDIDO)

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        env = dict(os.environ, HOME=str(self.tmp / "home"))
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), *map(str, args)],
                           capture_output=True, text=True, env=env, timeout=60)
        return r.returncode, r.stdout

    def conferir(self, texto, nome="b.md"):
        return self.rodar("brief", self.gravar(nome, texto), "--pedido", self.pedido)


class ParserDeEtapas(unittest.TestCase):
    def test_sufixo_de_letra_e_etapas_fora_do_escopo_entram_em_ordem_natural(self):
        etapas = fc.ler_pedido_brief(PEDIDO)["etapas"]
        self.assertEqual(list(etapas), ["E0.1", "E0.2", "E1.1", "E1.2", "E1.3", "E1.3b", "E1.4", "E1.5"])
        self.assertEqual(etapas["E1.3b"][0], "infra-exemplo")
        self.assertEqual(len([e for e in etapas if e.startswith("E1.")]), 6)
        self.assertEqual(fc.ids_em_citacao("faz (E1.3b) e (E1.5)"), {"E1.3b", "E1.5"})


class RegraUnicaDeMarca(Base):
    def test_merge_do_mesmo_papel_com_as_outras_etapas_sem_marca_aprova(self):
        """Caso 1: o merge do revisor (E1.5); a E1.2 é do mesmo papel em outra delegação e vai ao Fora sem a marca."""
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar na develop (E1.5)."], fora_sem("E1.5")))
        self.assertEqual(rc, 0, saida)
        for etapa in ("E0.1", "E1.2", "E1.3b", "E1.4"):
            self.assertIn(f'corte: etapa (ok) "{etapa}"', saida)
        self.assertNotIn("corte: sem marca", saida)

    def test_parecer_de_seguranca_com_etapas_de_outras_instancias_sem_marca_aprova(self):
        """Caso 2: a E0.2; as etapas do revisor (outras instâncias) não mudam nada para este destino."""
        rc, saida = self.conferir(brief("seguranca-exemplo", ["Modelo de ameaças (E0.2).", "Do recurso (E1)."], fora_sem("E0.2")))
        self.assertEqual(rc, 0, saida)

    def test_justificativa_livre_sem_registro_externo_aprova(self):
        """Caso 3: a E1.3b; a justificativa não se confere e a E1.1 vai ao Fora sem a marca."""
        fora = [f"{t} · qualquer justificativa" for e, t in ETAPAS.items() if e != "E1.3b"]
        rc, saida = self.conferir(brief("infra-exemplo", ["Parecer (E1.3b)."], fora))
        self.assertEqual(rc, 0, saida)

    def test_etapa_com_a_marca_completa_e_corte_real(self):
        fora = fora_sem("E1.5", "E1.2") + [f'Retira do escopo original: {ETAPAS["E1.2"]} · justificativa: x · consequência: y · '
                                           'decisão: DECISÃO DO DONO (2026-01-01): "A".']
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora))
        self.assertIn('corte: real (marca completa) "E1.2"', saida)
        self.assertEqual(rc, 0, saida)

    def test_etapa_omitida_reprova_de_qualquer_papel(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E1.4")))
        self.assertIn('corte: sem marca "E1.4" (etapa sem menção)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E1.2")))
        self.assertIn('corte: sem marca "E1.2" (etapa do papel do destino fora do Entregar)', saida)
        self.assertEqual(rc, 1)

    def test_etapa_fora_do_escopo_tambem_e_conferida(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Mesclar (E1.5)."], fora_sem("E1.5", "E0.1")))
        self.assertIn('corte: sem marca "E0.1" (etapa sem menção)', saida)
        self.assertEqual(rc, 1)

    def test_review_e_merge_do_mesmo_papel_no_mesmo_entregar_reprovam(self):
        rc, saida = self.conferir(brief("revisor-exemplo", ["Review (E1.2).", "Merge (E1.5)."], fora_sem("E1.2", "E1.5")))
        self.assertIn("etapa: junta delegações E1.2, E1.5 (R-BRIEF)", saida)
        self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
