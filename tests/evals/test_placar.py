"""`bin/forge-placar` (0.43.1, frente I): placar por janela, portão `comparar` e checklist `propostas`, sobre fixtures sintéticas
numa raiz temporária. Só biblioteca padrão, sem rede."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTES))
from ambiente_git import sem_manutencao  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

PLACAR = TESTES.parent / "bin" / "forge-placar"
CAB_CONF = ("| data-hora | pedido | brief | modo | rodada | resultado | mérito (s/n/parcial) | nota | classe | autor |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n")
CAB_MELHORIAS = ("| ID | Hipótese | Mudança | Métrica | Critério de reversão | Início | Revisão | Resultado |\n"
                 "|---|---|---|---|---|---|---|---|\n")


def veredito(dia, modo="brief", resultado="aprovado", classe="—"):
    return f"| {dia} 10:00 | p | p-x-1 | {modo} | 1 | {resultado} | s | nota | {classe} | jarvis |\n"


def semana(dia, aprovados, forma, implementacao=0):
    """Vereditos de um dia: `aprovados` briefs aprovados (delegações), `forma` reprovações de forma e as de implementação."""
    return (veredito(dia) * aprovados + veredito(dia, resultado="reprovado", classe="forma") * forma
            + veredito(dia, "entrega", "não cumpriu", "implementacao") * implementacao)


class Placar(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-placar-"))
        self.addCleanup(shutil.rmtree, self.raiz, ignore_errors=True)

    def gravar(self, rel, texto):
        arq = self.raiz / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(PLACAR), *args, "--raiz", str(self.raiz)], capture_output=True, text=True,
                           env=dict(os.environ, HOME=str(self.raiz / "home")), timeout=60)
        return r.returncode, r.stdout, r.stderr

    def json(self, *args):
        rc, saida, erro = self.rodar(*args, "--json")
        self.assertIn(rc, (0, 1, 3), erro)
        return rc, json.loads(saida)


class Medir(Placar):
    def test_janela_atual_e_anterior_com_as_taxas(self):
        antigo = "| 2026-11-02 09:00 | p | p-x-0 | brief | 1 | reprovado | s | linha de 8 colunas |\n"  # formato antigo: sem classe
        self.gravar("docs/kanban/conferencias.md", CAB_CONF + antigo + semana("2026-11-03", 4, 2) + semana("2026-11-10", 5, 1, 1))
        self.gravar("docs/kanban/escapes.md", "| data-hora | pedido |\n|---|---|\n| 2026-11-11 08:00 | p |\n")
        self.gravar("docs/pedidos/p.md", "# p\n\n## Histórico\n- 2026-11-10 09:00: entrega conferida " + "a" * 40 + "\n"
                    "- 2026-11-10 09:30: ERRO-JARVIS: hora inventada\n- 2026-11-10 11:00: PR #9 mesclado na develop por squash\n"
                    "\n## Outra seção\n- 2026-11-10 12:00: ERRO-JARVIS: fora do Histórico não conta\n")
        rc, dados = self.json("--ate", "2026-11-14")
        self.assertEqual(rc, 0)
        atual, anterior = dados["atual"], dados["anterior"]
        self.assertEqual((atual["janela"], atual["delegacoes"], atual["negativos"], atual["negativos_forma"]),
                         (["2026-11-07", "2026-11-14"], 5, 2, 1))
        self.assertEqual((atual["taxa_forma"], atual["taxa_reprovacao"], atual["voltas_por_item"]), (0.2, round(2 / 7, 4), 0.4))
        self.assertEqual((atual["erros_jarvis"], atual["taxa_escape"], atual["pronto_ate_develop"]), (0.2, 0.2, 120))
        self.assertEqual((anterior["delegacoes"], anterior["negativos_forma"], anterior["taxa_forma"]), (4, 3, 0.75))
        self.assertEqual((anterior["escapes_n"], anterior["pedidos_mesclados"], anterior["pronto_ate_develop"]), (0, 0, None))
        self.assertEqual(dados["resumo"], "resumo: os erros de forma do time caíram 73%; os defeitos que escaparam subiram (antes não havia nenhum)")

    def test_fonte_ausente_sai_tracinho_e_nunca_zero(self):
        rc, saida, _ = self.rodar("--ate", "2026-11-14")
        self.assertEqual(rc, 0)
        self.assertIn("taxa_forma: atual - · anterior -", saida)
        self.assertIn("taxa_escape: atual - · anterior -", saida)

    def test_registro_de_erros_ci_e_reversoes_entram(self):
        self.gravar("docs/kanban/conferencias.md", CAB_CONF + semana("2026-11-10", 2, 0))
        erros = self.gravar("erros.md", "# Erros\n## 72. Veredito duas vezes (2026-11-10 07:52)\n## 1. Antigo (2026-10-01 10:00)\n")
        ci = self.gravar("ci.json", json.dumps([{"conclusion": "failure", "createdAt": "2026-11-11T10:00:00Z"},
                                                {"conclusion": "success", "createdAt": "2026-11-11T11:00:00Z"}]))
        repo = self.raiz / "repo"
        repo.mkdir()
        env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith("GIT_")} | {
            "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
            "GIT_COMMITTER_DATE": "2026-11-12T10:00:00", "GIT_CONFIG_GLOBAL": "/dev/null"})
        for args in (["init", "-q", "-b", "develop"], ["commit", "-q", "--allow-empty", "-m", "feat: x"],
                     ["commit", "-q", "--allow-empty", "-m", 'Revert "feat: x"']):
            subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)
        rc, dados = self.json("--ate", "2026-11-14", "--erros", str(erros), "--ci", str(ci), "--git", str(repo), "--ref", "develop")
        atual = dados["atual"]
        self.assertEqual((atual["erros_jarvis_n"], atual["ci_vermelha_n"], atual["reversoes_n"], atual["taxa_escape"]), (1, 1, 1, 1.0))

    def test_uso_errado_sai_com_2(self):
        for args in (("--ate", "ontem"), ("--dias", "0"), ("comparar", "--antes", "2026-11-10"),
                     ("comparar", "--antes", "2026-11-10", "--depois", "2026-11-01"),
                     ("comparar", "--antes", "2026-11-10", "--depois", "2026-11-10", "--metrica", "inventada")):
            with self.subTest(args):
                self.assertEqual(self.rodar(*args)[0], 2)


class Comparar(Placar):
    """O portão: a mudança de 2026-11-08 só fica se a taxa de forma e a de escape não pioram e a métrica declarada melhora."""

    def conf(self, antes, depois):
        self.gravar("docs/kanban/conferencias.md", CAB_CONF + semana("2026-11-05", *antes) + semana("2026-11-10", *depois))

    def comparar(self, *extra):
        return self.rodar("comparar", "--antes", "2026-11-08", "--depois", "2026-11-08", "--minimo", "10", *extra)

    def test_taxa_de_forma_que_cai_mantem(self):
        self.conf((10, 5), (10, 2))
        rc, saida, _ = self.comparar("--metrica", "taxa_forma")
        self.assertEqual(rc, 0, saida)
        self.assertIn("veredito: manter\n", saida)
        self.assertTrue(saida.endswith("resumo: os erros de forma do time caíram 60%; os defeitos que escaparam: sem dado para comparar; "
                                       "a mudança fica\n"), saida)

    def test_taxa_de_forma_que_piora_alem_da_tolerancia_reverte(self):
        self.conf((10, 2), (10, 4))
        rc, saida, _ = self.comparar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("motivo: taxa_forma piorou: 20.00% -> 40.00%", saida)
        self.assertIn("veredito: reverter\n", saida)
        self.assertIn("resumo: os erros de forma do time subiram 100%", saida)
        self.assertTrue(saida.endswith("a mudança sai\n"), saida)

    def test_piora_dentro_da_tolerancia_mantem(self):
        self.conf((10, 10), (10, 11))  # 100% -> 110%: no limite de 10% + 0,01
        self.assertEqual(self.comparar()[0], 0)
        self.assertEqual(self.comparar("--tolerancia", "0", "--folga", "0")[0], 1)

    def test_escape_que_aparece_reverte(self):
        self.conf((10, 2), (10, 2))
        self.gravar("docs/kanban/escapes.md", "| data-hora | pedido |\n|---|---|\n| 2026-11-09 08:00 | p |\n")
        rc, saida, _ = self.comparar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("motivo: taxa_escape piorou: 0.00% -> 10.00%", saida)
        self.assertIn("os erros de forma do time ficaram iguais; os defeitos que escaparam subiram (antes não havia nenhum)", saida)

    def test_metrica_declarada_sem_ganho_reverte(self):
        self.conf((10, 2), (10, 2))
        rc, saida, _ = self.comparar("--metrica", "voltas_por_item")
        self.assertEqual(rc, 1, saida)
        self.assertIn("motivo: voltas_por_item não melhorou: 20.00% -> 20.00% (mudança sem ganho sai)", saida)

    def test_metrica_declarada_sem_medida_reverte(self):
        self.conf((10, 2), (10, 1))
        rc, saida, _ = self.comparar("--metrica", "pronto_ate_develop")
        self.assertEqual(rc, 1, saida)
        self.assertIn("pronto_ate_develop sem medida", saida)

    def test_amostra_pequena_e_inconclusiva(self):
        self.conf((3, 2), (10, 9))
        rc, dados = self.json("comparar", "--antes", "2026-11-08", "--depois", "2026-11-08")
        self.assertEqual((rc, dados["veredito"], dados["amostra_pequena"]), (3, "inconclusivo", ["antes"]))


class Propostas(Placar):
    def checar(self, *linhas, hoje="2026-11-10", extra=()):
        self.gravar("docs/kanban/melhorias.md", "# Experimentos\n\n" + CAB_MELHORIAS + "".join(linhas))
        rc, saida, _ = self.rodar("propostas", "--hoje", hoje, *extra)
        return rc, saida

    BOA = "| M-1 | o prevoo em código corta forma | código: trava no forge-check | taxa_forma | sobe 2 semanas | 2026-11-08 | 2026-11-15 | |\n"

    def test_proposta_completa_e_no_prazo_passa(self):
        rc, saida = self.checar(self.BOA)
        self.assertEqual(rc, 0, saida)
        self.assertIn("propostas: 1 · abertas: 1 · resultado: ok", saida)

    def test_cada_falta_tem_a_sua_linha(self):
        casos = {
            "métrica fora do placar": (self.BOA.replace("| taxa_forma |", "| qualidade |"), "Métrica tem de começar"),
            "sem tipo de mudança": (self.BOA.replace("código: trava", "trava"), "Mudança tem de começar"),
            "sem critério de reversão": (self.BOA.replace("sobe 2 semanas", "—"), "sem critério de reversão"),
            "sem prazo": (self.BOA.replace("2026-11-15", "depois"), "nasce com prazo"),
            "prazo longo": (self.BOA.replace("2026-11-15", "2026-12-31"), "Revisão de 1 a 30 dias"),
            "resultado sem veredito": (self.BOA.replace(" | |\n", " | parece melhor |\n"), "Resultado tem de começar"),
        }
        for nome, (linha, trecho) in casos.items():
            with self.subTest(nome):
                rc, saida = self.checar(linha)
                self.assertEqual(rc, 1, saida)
                self.assertIn(trecho, saida)

    def test_revisao_vencida_sem_resultado_manda_rodar_o_comparar(self):
        rc, saida = self.checar(self.BOA, hoje="2026-11-15")
        self.assertEqual(rc, 1, saida)
        self.assertIn("forge-placar comparar --antes 2026-11-08 --depois 2026-11-08 --metrica taxa_forma", saida)
        fechada = self.BOA.replace(" | |\n", " | manter (veredito: manter; taxa_forma 20% -> 10%) |\n")
        self.assertEqual(self.checar(fechada, hoje="2026-11-15")[0], 0)

    def test_uma_causa_por_vez(self):
        outra = self.BOA.replace("M-1", "M-2")
        rc, saida = self.checar(self.BOA, outra)
        self.assertEqual(rc, 1, saida)
        self.assertIn("abertas: 2 (M-1, M-2), máximo 1: uma causa por vez", saida)
        self.assertEqual(self.checar(self.BOA, outra, extra=("--max-abertas", "2"))[0], 0)

    def test_modelo_de_projeto_sem_proposta_passa(self):
        modelo = TESTES.parent / "templates" / "projeto" / "docs" / "kanban" / "melhorias.md"
        r = subprocess.run([sys.executable, str(PLACAR), "propostas", str(modelo)], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
