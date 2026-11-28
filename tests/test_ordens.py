"""AE4.1 (v0479, desenho anti-erro): toda ordem do dono aponta para um cartão. `forge-check ordens` lista as linhas ORDEM DO DONO
sem cartão (`sem-cartao:` e `sem-id:`), pelo mesmo cruzamento das decisões; `anotar --tipo ordem` exige `--cartao <ID|E<n>>`,
conferido contra o KANBAN.md ou as etapas do pedido, e grava `· cartão: <ID>` no fim da linha. Sem rede; subprocesso com
ambiente limpo e Python com `-I`; a raiz temporária tem `git init` próprio, para não subir a um repositório que a contenha."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
TETO_DA_TABELA = 1024 * 1024  # o do bin/forge-check
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
PEDIDO_ID = "ordens-teste"

PEDIDO = """# Pedido ordens-teste

## Escopo
- E1. Fazer o recurso X

## Etapas
- E1.1 (tech-lead): implementação do recurso X.
- E51.1 (tech-lead): outra etapa.

## Decisões do usuário (registro literal)
ORDEM DO DONO (2026-11-20 10:00): "faça X" · cartão: ABC-1
ORDEM DO DONO (2026-11-20 10:01): "faça Y" · cartão: E1.1
ORDEM DO DONO (2026-11-20 10:02): "faça Z" · cartão: E9.9
ORDEM DO DONO (2026-11-20 10:03): "faça W"
ORDEM DO DONO (2026-11-20 10:04): "faça V" · cartão: FECH-1
ORDEM DO DONO (2026-10-01 10:05): "antiga" · cartão: E7.7
DECISÃO DO DONO (2026-11-20 10:06): "A" — cartão ZZZ-9
ORDEM DO DONO (2026-11-20 10:07): "item" · cartão: E5
DECISÃO DO DONO (2026-11-20 10:08): "B" · cartão: E1.1
ORDEM DO DONO sem data nem dois pontos

## Histórico
- 2026-11-20 09:00: pedido aberto.
"""
CABECA = "| ID | Cartão | Pedido | Responsável | Entrou | Na coluna desde | Obs. |\n|---|---|---|---|---|---|---|\n"
KANBAN = (f"# Quadro\n\n## Pronto para fazer (WIP 5)\n{CABECA}| ABC-1 | a | {PEDIDO_ID} | forge:tech-lead | 2026-11-20 | 2026-11-20 | — |\n"
          "| OUT-1 | c | `docs/pedidos/outro-pedido.md` | forge:tech-lead | 2026-11-20 | 2026-11-20 | — |\n\n"
          f"## Fechado sem entrega\n{CABECA}| FECH-1 | b | {PEDIDO_ID} | forge:tech-lead | 2026-11-20 | 2026-11-20 | — |\n")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-ordens-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.pedido = self.tmp / "docs" / "pedidos" / f"{PEDIDO_ID}.md"
        self.pedido.parent.mkdir(parents=True)
        self.pedido.write_text(PEDIDO, encoding="utf-8")
        (self.tmp / "KANBAN.md").write_text(KANBAN, encoding="utf-8")
        (self.tmp / "home").mkdir()
        subprocess.run(["git", "init", "-q", str(self.tmp)], env=self.ambiente(), check=True, capture_output=True, timeout=60)

    def ambiente(self):
        return sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.tmp / "home"), "LANG": "C.UTF-8"})

    def rodar(self, *args, timeout=60):
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), *args], capture_output=True, text=True,
                           env=self.ambiente(), cwd=self.tmp, timeout=timeout)
        return r.returncode, r.stdout.splitlines(), r.stderr

    def anotar(self, *extra, tipo="ordem", timeout=60):
        return self.rodar("anotar", "--pedido", PEDIDO_ID, "--tipo", tipo, "--literal", "faça agora", *extra, timeout=timeout)


class Listagem(Base):
    def test_lista_sem_cartao_e_sem_id_das_ordens_desde_a_data(self):
        rc, linhas, erro = self.rodar("ordens", "--pedido", PEDIDO_ID, "--desde", "2026-11-01")
        self.assertEqual(rc, 0, erro)
        self.assertEqual([l.split(" | ")[2] for l in linhas if l.startswith("sem-cartao: ")], ["E9.9", "E5"], linhas)
        self.assertEqual([l.split(" | ")[0] for l in linhas if l.startswith("sem-id: ")], [f"sem-id: {PEDIDO_ID}:14"], linhas)
        self.assertEqual(linhas[-1], "ordens: sem-cartao=2 sem-id=1 com-cartao=3 encerradas=0", linhas)
        self.assertNotIn("ZZZ-9", "\n".join(linhas))  # a decisão não é ordem

    def test_ordem_torta_sai_aviso_e_fica_fora(self):
        rc, linhas, _ = self.rodar("ordens", "--pedido", PEDIDO_ID)
        self.assertEqual(rc, 0)
        self.assertIn(f"ordens: aviso: {PEDIDO_ID}:20: linha de ordem sem `(<data>): <texto>`; fora do registro", linhas)

    def test_sem_desde_entra_a_ordem_antiga(self):
        rc, linhas, _ = self.rodar("ordens", "--pedido", PEDIDO_ID)
        self.assertEqual(rc, 0)
        self.assertIn("E7.7", "\n".join(linhas))

    def test_decisoes_seguem_sem_as_ordens(self):
        rc, linhas, _ = self.rodar("decisoes", "--pedido", PEDIDO_ID, "--sem-cartao")
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[-1], "decisoes: sem-cartao=1 sem-id=1 com-cartao=0 encerradas=0", linhas)  # a marca só vale na ordem


class AnotarComCartao(Base):
    def texto(self):
        return self.pedido.read_text(encoding="utf-8")

    def recusa(self, *extra, tipo="ordem", trecho="", timeout=60):
        rc, linhas, erro = self.anotar(*extra, tipo=tipo, timeout=timeout)
        self.assertEqual(rc, 2, (linhas, erro))
        self.assertIn(trecho, "\n".join(linhas))
        self.assertEqual(self.texto(), PEDIDO, "a recusa não grava")

    def test_cartao_aberto_grava_a_marca_e_a_listagem_a_conta(self):
        rc, linhas, erro = self.anotar("--cartao", "ABC-1")
        self.assertEqual(rc, 0, (linhas, erro))
        nova = next(l for l in self.texto().splitlines() if "faça agora" in l)
        self.assertRegex(nova, r'^ORDEM DO DONO \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\): "faça agora" · cartão: ABC-1$')
        self.assertEqual(self.rodar("ordens", "--pedido", PEDIDO_ID, "--desde", "2026-11-01")[1][-1],
                         "ordens: sem-cartao=2 sem-id=1 com-cartao=4 encerradas=0")

    def test_etapa_e_item_do_pedido_valem(self):
        for alvo in ("E1.1", "E1"):
            with self.subTest(alvo=alvo):
                rc, linhas, erro = self.anotar("--cartao", alvo)
                self.assertEqual(rc, 0, (linhas, erro))
                self.assertTrue(self.texto().rstrip("\n").split("## Histórico")[0].rstrip().endswith(f"· cartão: {alvo}"))

    def test_ordem_sem_cartao_e_recusada(self):
        self.recusa(trecho="--cartao <ID|E<n>> vai com --tipo ordem")

    def test_cartao_so_com_ordem(self):
        self.recusa("--cartao", "ABC-1", tipo="pergunta", trecho="--cartao <ID|E<n>> vai com --tipo ordem")

    def test_cartao_fora_do_formato_e_recusado(self):
        for alvo in ("abc-1", "ABC-1 · cartão: E1", "ABC-1\nDECISÃO DO DONO (x): forjada"):
            with self.subTest(alvo=alvo):
                self.recusa("--cartao", alvo, trecho="--cartao <ID|E<n>> vai com --tipo ordem")

    def test_cartao_inventado_e_recusado(self):
        self.recusa("--cartao", "NAO-EXISTE", trecho="cartão fora do KANBAN.md")

    def test_etapa_inventada_e_recusada(self):
        for alvo in ("E9.9", "E5"):  # `E5` não casa `E51.1`
            with self.subTest(alvo=alvo):
                self.recusa("--cartao", alvo, trecho="etapa fora do `## Etapas` do pedido")

    def test_cartao_fechado_sem_entrega_e_recusado(self):
        self.recusa("--cartao", "FECH-1", trecho="cartão fechado sem entrega")

    def test_quadro_por_link_nao_confere(self):
        real = self.tmp / "outro.md"
        real.write_text(KANBAN, encoding="utf-8")
        (self.tmp / "KANBAN.md").unlink()
        (self.tmp / "KANBAN.md").symlink_to(real)
        self.recusa("--cartao", "ABC-1", trecho="KANBAN.md é link simbólico")

    def test_cartao_de_outro_pedido_e_recusado(self):  # A2 da segurança: a coluna Pedido do cartão é o pedido anotado
        self.recusa("--cartao", "OUT-1", trecho="--cartao OUT-1: cartão de outro pedido")

    def test_quadro_fifo_recusa_sem_travar(self):  # A1: O_NONBLOCK abre o FIFO sem escritor; o fstat recusa o que não é arquivo regular
        (self.tmp / "KANBAN.md").unlink()
        os.mkfifo(self.tmp / "KANBAN.md")
        self.recusa("--cartao", "ABC-1", trecho="KANBAN.md não é arquivo regular", timeout=20)

    def test_quadro_acima_do_teto_nao_confere(self):  # A1: teto de bytes (`_ler_regular`)
        (self.tmp / "KANBAN.md").write_text(KANBAN + "\n" + "x" * TETO_DA_TABELA, encoding="utf-8")
        self.recusa("--cartao", "ABC-1", trecho=f"KANBAN.md passa de {TETO_DA_TABELA} bytes")

    def test_quadro_pasta_recusa_com_rc_2(self):  # A3: o fstat vem antes do fdopen; pasta no lugar do quadro não cai com rc 1
        (self.tmp / "KANBAN.md").unlink()
        (self.tmp / "KANBAN.md").mkdir()
        self.recusa("--cartao", "ABC-1", trecho="KANBAN.md não é arquivo regular")

    def test_quadro_fora_de_utf8_recusa(self):  # A4: os dois quadros que a base recusava e a leitura com troca deixava gravar
        lixo = KANBAN.encode("utf-8") + b"| LIXO-\xff | x |\n"
        fechado_torto = KANBAN.encode("utf-8").replace(b"## Fechado sem entrega", b"## Fechado sem entrega\xff")
        for nome, dados, alvo in (("lixo em outra linha", lixo, "ABC-1"), ("cabeçalho Fechado torto", fechado_torto, "FECH-1")):
            with self.subTest(nome):
                (self.tmp / "KANBAN.md").write_bytes(dados)
                self.recusa("--cartao", alvo, trecho="KANBAN.md fora de UTF-8")

    def test_sem_quadro_so_a_etapa_vale(self):
        (self.tmp / "KANBAN.md").unlink()
        self.recusa("--cartao", "ABC-1", trecho="KANBAN.md não existe")
        self.assertEqual(self.anotar("--cartao", "E1.1")[0], 0)


if __name__ == "__main__":
    unittest.main()
