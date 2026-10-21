"""P3 (LOTE-FORGE-CHECK-0.28.0): citação conferida pela ferramenta. IDs citados existem no pedido; trecho com fonte explícita existe
literalmente nela; vocabulário fechado de `tipo:` e `--etapa`; `brief gerar --citar` e o PQ `forge-check docs`; D1: o PQ `pr` é prova
do conferente. Offline e só leitura; fixtures neutras."""
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
fc = SourceFileLoader("forge_check_citacao", str(FORGE_CHECK)).load_module()
REGRA = RAIZ.joinpath("docs", "regras", "R-BRIEF.md").read_text(encoding="utf-8").splitlines()
TRECHO_DA_REGRA = "passa pelo `forge:conferente` no modo `brief`"

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X
- E2. Documentar o recurso X
- E3. Medir o recurso X

## Etapas
- E1.1 (dev-exemplo): implementação, documentação e medida do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""


def brief(entregar="- Recurso (E1), texto (E2) e medida (E3).", extra=""):
    return ("Agente destino: forge:dev-exemplo\n\n## Objetivo\nExemplo.\n\n## Ler\n- o pedido.\n\n## Entregar\n" + entregar + "\n" + extra
            + "\n## Fora do escopo\n- nada.\n\n## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): \"A\".\n\n## Pronto quando\n"
              "- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.\n\n## Relatório\nAté 8 linhas.\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-citacao-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.gravar("docs/pedidos/exemplo.md", PEDIDO)
        self.gravar("docs/a.md", "linha um\nlinha dois\nprimeira metade\nsegunda metade\n")

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.tmp), *map(str, args)], capture_output=True,
                           text=True, env=dict(os.environ, HOME=str(self.tmp / "home")), timeout=60)
        return r.returncode, r.stdout

    def conferir(self, texto):
        return self.rodar("brief", self.gravar("b.md", texto), "--pedido", "exemplo")


class IdsCitados(Base):
    def test_id_que_nao_existe_no_pedido_reprova(self):
        rc, saida = self.conferir(brief("- Recurso (E1), texto (E2), medida (E3) e outra coisa (E8)."))
        self.assertIn("citação: E8 não existe no pedido", saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief())
        self.assertNotIn("não existe no pedido", saida)
        self.assertEqual(rc, 0, saida)


class TrechoComFonte(Base):
    def test_trecho_da_regra_literal_passa_e_palavra_trocada_reprova(self):
        self.assertTrue(any(TRECHO_DA_REGRA in l for l in REGRA))
        rc, saida = self.conferir(brief(extra=f'- "{TRECHO_DA_REGRA}" (R-BRIEF)\n'))
        self.assertIn("citação: ok R-BRIEF", saida)
        self.assertEqual(rc, 0, saida)
        rc, saida = self.conferir(brief(extra='- "passa pelo `forge:conferente` no modo `entrega`" (R-BRIEF)\n'))
        self.assertIn("citação: trecho fora da fonte R-BRIEF", saida)
        self.assertEqual(rc, 1)

    def test_linha_citada_e_a_que_vale(self):
        rc, saida = self.conferir(brief(extra='- "primeira metade segunda metade" (docs/a.md:3)\n'))
        self.assertIn("citação: trecho fora da fonte docs/a.md:3", saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief(extra='- "primeira metade segunda metade" (docs/a.md:3-4)\n'))
        self.assertIn("citação: ok docs/a.md:3-4", saida)
        self.assertEqual(rc, 0, saida)
        rc, saida = self.conferir(brief(extra='- "primeira … metade" (docs/a.md:3)\n'))
        self.assertEqual(rc, 0, saida)  # as reticências cortam o trecho

    def test_fonte_fora_da_raiz_nao_e_lida(self):
        fora = Path(tempfile.mkdtemp(prefix="forge-fora-"))
        self.addCleanup(shutil.rmtree, fora, ignore_errors=True)
        (fora / "b.md").write_text("segredo\n", encoding="utf-8")
        (self.tmp / "docs" / "link.md").symlink_to(fora / "b.md")
        for fonte in (f"../{fora.name}/b.md:1", "docs/link.md:1"):
            with self.subTest(fonte=fonte):
                rc, saida = self.conferir(brief(extra=f'- "segredo" ({fonte})\n'))
                self.assertIn(f"citação: fonte não verificável {fonte}", saida)
                self.assertNotIn("segredo", saida.replace(f'"segredo" ({fonte})', ""))
                self.assertEqual(rc, 0, saida)

    def test_arquivo_de_segredo_e_o_que_nao_e_md_nao_sao_lidos(self):
        """Revisão de segurança A2: `.env` (e outro arquivo que não é `.md`) nem imprime no `--citar` nem responde à conferência."""
        valor = "VALOR_" + "FALSO_9z"
        for rel in (".env", ".env.local", "docs/.env.md", "segredo.json", "docs/b.txt"):
            with self.subTest(fonte=rel):
                self.gravar(rel, f"CHAVE={valor}\n")
                for trecho in (f"CHAVE={valor}", "CHAVE=outro"):
                    rc, saida = self.conferir(brief(extra=f'- "{trecho}" ({rel}:1)\n'))
                    self.assertIn(f"citação: fonte não verificável {rel}:1", saida)
                    self.assertNotIn("citação: ok", saida)
                    self.assertNotIn("trecho fora da fonte", saida)
                    self.assertEqual(rc, 0, saida)
                rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--citar", f"{rel}:1")
                self.assertIn(f"- PREENCHER: --citar {rel}:1:", saida)
                self.assertNotIn(valor, saida)
        (self.tmp / "docs" / "env.md").symlink_to(self.tmp / ".env")  # `.md` que aponta para o `.env`: vale o nome resolvido
        rc, saida = self.conferir(brief(extra=f'- "CHAVE={valor}" (docs/env.md:1)\n'))
        self.assertIn("citação: fonte não verificável docs/env.md:1", saida)
        self.assertIn("citação: ok docs/a.md:3", self.conferir(brief(extra='- "primeira metade" (docs/a.md:3)\n'))[1])

    def test_aspas_sem_fonte_nao_sao_conferidas(self):
        rc, saida = self.conferir(brief(extra='- "qualquer coisa que não está em lugar nenhum".\n'))
        self.assertNotIn("citação:", saida)
        self.assertEqual(rc, 0, saida)


class Vocabulario(Base):
    def test_tipo_fora_do_vocabulario_reprova_com_sugestao(self):
        rc, saida = self.conferir(brief(extra="- O parecer leva `tipo: seguranca`.\n"))
        self.assertIn('vocabulário: tipo "seguranca" não existe (use revisao-seguranca)', saida)
        self.assertEqual(rc, 1)
        rc, saida = self.conferir(brief(extra="- O parecer leva `tipo: revisao-seguranca` e roda `forge-check entrega x --etapa qa`.\n"))
        self.assertNotIn("vocabulário:", saida)
        rc, saida = self.conferir(brief(extra="- Rode `forge-check entrega x --etapa merge`.\n"))
        self.assertIn('vocabulário: etapa "merge" não existe', saida)
        self.assertEqual(rc, 1)


class Gerar(Base):
    def test_etapa_de_parecer_traz_o_pq_do_forge_check_docs(self):
        for etapa in ("review", "seguranca", "qa"):
            with self.subTest(etapa=etapa):
                rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:revisor-exemplo", "--etapa", etapa)
                self.assertEqual(rc, 0, saida)
                self.assertIn("- PQ-N (cmd): `forge-check docs` · espera: rc=0", saida)
        self.assertTrue(fc.comando_do_conferente("forge-check docs"))
        _, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--etapa", "codigo")
        self.assertNotIn("`forge-check docs`", saida)

    def test_citar_imprime_a_linha_literal_com_a_fonte(self):
        n = next(i for i, l in enumerate(REGRA, 1) if TRECHO_DA_REGRA in l)
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo", "--citar", f"R-BRIEF:{n}",
                               "--citar", "docs/a.md:3-4", "--citar", "nada")
        self.assertEqual(rc, 0, saida)
        self.assertIn("## Citações (copie para onde couber e apague o bloco)", saida)
        self.assertIn(f'- "{fc.normalizar_espacos(REGRA[n - 1])}" (R-BRIEF)\n', saida)
        self.assertIn('- "primeira metade segunda metade" (docs/a.md:3-4)\n', saida)
        self.assertIn("- PREENCHER: --citar nada:", saida)
        citado = brief(extra='- "primeira metade segunda metade" (docs/a.md:3-4)\n')
        self.assertEqual(self.conferir(citado)[0], 0)  # o que o --citar imprime passa na conferência


class ProvaDePr(Base):
    def test_pq_pr_vale_como_prova_do_conferente(self):
        texto = brief("- Abrir o PR do commit (E1, E2, E3).").replace(
            "- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.",
            "- PQ-1 (pr): `gh pr view melhoria/x --json number,state` mostra OPEN")
        rc, saida = self.conferir(texto)
        self.assertNotIn("forma: sem PQ que o conferente confira", saida)
        self.assertEqual(rc, 0, saida)


if __name__ == "__main__":
    unittest.main()
