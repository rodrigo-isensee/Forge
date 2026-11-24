"""D7 (v0478 E174.2): `forge-check criterios <pedido>` monta a tabela pedido × entregue. Cada `C-n` do `## Critério de pronto` sai
`entregue` só com um `PQ-m ... cobre: C-n` de brief selado (o sha256 do selo confere) cuja etapa do `Cobre:` tem `entrega conferida`;
senão, `não entregue`."""
import hashlib
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
FORGE_CHECK = str(RAIZ / "bin" / "forge-check")
AMBIENTE = sem_manutencao({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})

PEDIDO = """# Pedido p1

## Etapas
- E1.1 (forge:dev-exemplo): implementar o recurso

## Critério de pronto
{criterios}

## Histórico
{historico}"""

CRITERIOS = ("- PQ-1 critério antigo, sem id estável · prova: cmd · `técnico`\n"
             "- C-1 Dado o pedido, quando roda, então sai a tabela · `confirmado`\n"
             "- C-2 Dado um critério sem prova, então sai não entregue · `confirmado`")

BRIEF = """Agente destino: forge:dev-exemplo
Pedido: p1
Branch: melhoria/p1   Base: develop
Etapa: codigo   Cobre: E1.1

## Objetivo
x

## Pronto quando
{provas}
"""

PROVAS = ("- PQ-1 (cmd): `true` · espera: rc=0 · cobre: C-1\n"
          "- PQ-2 (push): `git ls-remote origin refs/heads/melhoria/p1` igual ao head local\n"
          "- nota: o PQ-3 de outro brief · cobre: C-2")


class Criterios(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-criterios-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.git("init", "-q", "-b", "develop")
        self.git("commit", "-q", "--allow-empty", "-m", "base")
        self.git("switch", "-q", "-c", "melhoria/p1")
        self.head = self.commitar("entrega")
        self.selo = " 2026-10-19 11:00: brief selado docs/briefs/p1-dev-exemplo-1.md {sha}"  # o sha256 real do brief, posto pelo `montar`
        self.conferida = f" 2026-10-19 12:00: entrega conferida {self.head}"

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.tmp), *args], check=True, capture_output=True, text=True, env=AMBIENTE).stdout.strip()

    def commitar(self, mensagem):
        self.git("commit", "-q", "--allow-empty", "-m", mensagem)
        return self.git("rev-parse", "HEAD")

    def gravar(self, rel, texto):
        arq = self.tmp / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")

    def montar(self, *historico, criterios=CRITERIOS, provas=PROVAS):
        brief = BRIEF.format(provas=provas)
        sha = hashlib.sha256(brief.encode("utf-8")).hexdigest()
        self.gravar("docs/briefs/p1-dev-exemplo-1.md", brief)
        self.gravar("docs/pedidos/p1.md", PEDIDO.format(criterios=criterios, historico="".join(f"-{l.replace('{sha}', sha)}\n" for l in historico)))

    def criterios(self, pedido="p1"):
        r = subprocess.run([sys.executable, "-I", FORGE_CHECK, "--raiz", str(self.tmp), "criterios", pedido], capture_output=True, text=True,
                           env=dict(AMBIENTE, HOME=str(self.tmp / "home")))
        return r.returncode, r.stdout.splitlines()

    def test_criterio_com_prova_conferida_entregue_e_sem_prova_nao_entregue(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo, self.selo, self.conferida)  # o selo repetido não duplica a prova
        rc, linhas = self.criterios()
        self.assertEqual(rc, 1, linhas)
        self.assertEqual(linhas, [
            "criterios: pedido p1 · 2 critérios · 1 entregues · 1 não entregues",
            "criterios: C-1 · entregue · docs/briefs/p1-dev-exemplo-1.md PQ-1 · Dado o pedido, quando roda, então sai a tabela · `confirmado`",
            "criterios: C-2 · não entregue · Dado um critério sem prova, então sai não entregue · `confirmado`"])

    def test_todos_entregues_sai_com_rc_zero(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo, self.conferida, provas="- PQ-1 (cmd): `true` · espera: rc=0 · cobre: C-1, C-2")
        rc, linhas = self.criterios()
        self.assertEqual(rc, 0, linhas)
        self.assertEqual(linhas[0], "criterios: pedido p1 · 2 critérios · 2 entregues · 0 não entregues")
        self.assertEqual(len(linhas), 3, linhas)  # nenhum `cobre:` fora do pedido
        self.assertIn("criterios: C-2 · entregue · docs/briefs/p1-dev-exemplo-1.md PQ-1 · Dado um critério sem prova, então sai não entregue · `confirmado`", linhas)

    def test_brief_sem_entrega_conferida_nao_prova(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo)
        rc, linhas = self.criterios()
        self.assertEqual(rc, 1, linhas)
        self.assertEqual(linhas[0], "criterios: pedido p1 · 2 critérios · 0 entregues · 2 não entregues")

    def test_brief_alterado_depois_do_selo_nao_prova(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo, self.conferida)
        self.gravar("docs/briefs/p1-dev-exemplo-1.md", BRIEF.format(provas=PROVAS.replace("cobre: C-1", "cobre: C-1, C-2")))
        self.assertEqual(self.criterios(), (1, [
            "criterios: pedido p1 · 2 critérios · 0 entregues · 2 não entregues",
            "criterios: C-1 · não entregue · Dado o pedido, quando roda, então sai a tabela · `confirmado`",
            "criterios: C-2 · não entregue · Dado um critério sem prova, então sai não entregue · `confirmado`"]))

    def test_cobre_de_criterio_fora_do_pedido_reprova_mesmo_com_todos_entregues(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo, self.conferida, provas="- PQ-1 (cmd): `true` · espera: rc=0 · cobre: C-1, C-2, C-9")
        rc, linhas = self.criterios()
        self.assertEqual(rc, 1, linhas)
        self.assertIn("criterios: C-9: `cobre:` de prova conferida fora do `## Critério de pronto`", linhas)

    def test_id_repetido_reprova_e_vale_o_primeiro(self):
        self.montar(" 2026-10-19 10:00: aberto", self.selo, self.conferida, criterios=CRITERIOS + "\n- C-1 outro texto",
                    provas="- PQ-1 (cmd): `true` · espera: rc=0 · cobre: C-1, C-2")
        rc, linhas = self.criterios()
        self.assertEqual(rc, 1, linhas)
        self.assertIn("criterios: C-1 repetido no pedido; vale o primeiro", linhas)
        self.assertEqual(linhas[0], "criterios: pedido p1 · 2 critérios · 2 entregues · 0 não entregues")
        self.assertFalse([l for l in linhas if "outro texto" in l], linhas)

    def test_linha_id_do_pedido_da_o_nome_da_tabela(self):
        self.montar(" 2026-10-19 10:00: aberto")
        self.gravar("docs/pedidos/p1.md", "id: p1-real\n" + (self.tmp / "docs/pedidos/p1.md").read_text(encoding="utf-8"))
        self.assertEqual(self.criterios()[1], [
            "criterios: pedido p1-real · 2 critérios · 0 entregues · 2 não entregues",
            "criterios: C-1 · não entregue · Dado o pedido, quando roda, então sai a tabela · `confirmado`",
            "criterios: C-2 · não entregue · Dado um critério sem prova, então sai não entregue · `confirmado`"])

    def test_pedido_sem_criterio_c_n_ou_ilegivel_sai_nao_verificavel(self):
        self.montar(" 2026-10-19 10:00: aberto", criterios="- PQ-1 critério antigo · prova: cmd")
        self.assertEqual(self.criterios(), (2, ["criterios: pedido p1: não verificável (sem item `C-n` no `## Critério de pronto`)"]))
        self.assertEqual(self.criterios("p9"), (2, ['criterios: pedido "p9": não verificável (o arquivo do pedido não abre)']))


if __name__ == "__main__":
    unittest.main()
