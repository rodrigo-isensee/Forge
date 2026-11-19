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

    def test_brief_selado_conta_a_delegacao_sem_o_conferente(self):  # A2 do review de correção da 0.43.1
        selos = "".join(f"- 2026-11-1{d} 09:00: brief selado docs/briefs/p-dev-{d}.md {'c' * 64}\n" for d in (0, 1, 2))
        self.gravar("docs/pedidos/p.md", "# p\n\n## Histórico\n" + selos + "- 2026-11-03 09:00: brief selado docs/briefs/p-dev-9.md "
                    + "c" * 64 + "\n- 2026-11-11 10:00: ERRO-JARVIS: x\n- 2026-11-11 11:00: brief selado sem hash\n")
        rc, dados = self.json("--ate", "2026-11-14")
        self.assertEqual((dados["atual"]["delegacoes"], dados["anterior"]["delegacoes"]), (3, 1))
        self.assertEqual((dados["atual"]["erros_jarvis"], dados["atual"]["taxa_forma"]), (round(1 / 3, 4), 0.0))

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

    def test_raiz_pedidos_fora_do_clone_vale_sobre_o_raiz(self):  # RAIZ-PEDIDOS-PERDE-DADOS: o dado do pedido fora do clone não some
        contrib = self.raiz / "contrib"
        (contrib / "docs" / "kanban").mkdir(parents=True)
        (contrib / "docs" / "kanban" / "conferencias.md").write_text(CAB_CONF + semana("2026-11-10", 3, 1), encoding="utf-8")
        clone = self.raiz / "clone"
        clone.mkdir()
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.raiz / "home")}
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "--raiz", str(clone), "--raiz-pedidos", str(contrib), "--ate", "2026-11-14",
                            "--json"], capture_output=True, text=True, env=env, cwd=clone, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        atual = json.loads(r.stdout)["atual"]
        self.assertEqual((atual["vereditos"], atual["delegacoes"], atual["negativos"]), (4, 3, 1))

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



class PorPapel(Placar):
    """0.43.3 (E23, erros por papel): a taxa de cada papel pela coluna `autor` e os casos de eval do papel."""

    def linha(self, dia, brief, modo, resultado, autor, classe="—"):
        return f"| {dia} 10:00 | p | {brief} | {modo} | 1 | {resultado} | s | n | {classe} | {autor} |\n"

    def test_taxa_por_papel_com_destino_virando_o_papel_do_brief(self):
        self.gravar("docs/kanban/conferencias.md", CAB_CONF
                    + self.linha("2026-11-10", "p-tech-lead-1", "brief", "aprovado", "jarvis") * 3
                    + self.linha("2026-11-10", "p-tech-lead-2", "brief", "reprovado", "jarvis", "forma")
                    + self.linha("2026-11-10", "docs/briefs/p-qa-engineer-1.md", "entrega", "não cumpriu", "destino", "implementacao")
                    + self.linha("2026-11-10", "p-qa-engineer-2", "entrega", "cumpriu", "destino")
                    + self.linha("2026-11-10", "p-tech-lead-3", "entrega", "não cumpriu", "conferente", "escopo")
                    + "| 2026-11-10 10:00 | p | p-x-0 | brief | 1 | reprovado | s | 8 colunas |\n")
        evals = self.gravar("evals/test_x.py", "import unittest\nSEM_FERRAMENTA = {'qa-engineer': [('C9', 'x')]}\n"
                            "class A(unittest.TestCase):\n    PAPEL = 'qa-engineer'\n    def test_a(self): pass\n"
                            "    @unittest.expectedFailure\n    def test_b(self): pass\n"
                            "class B(unittest.TestCase):\n    def test_c(self): pass\n").parent
        rc, dados = self.json("--ate", "2026-11-14", "--evals", str(evals))
        self.assertEqual(rc, 0)
        atual = dados["papeis"]["atual"]
        self.assertEqual(atual["jarvis"], {"erros": 1, "base": 4, "taxa": 0.25})
        self.assertEqual(atual["qa-engineer"], {"erros": 1, "base": 2, "taxa": 0.5})
        self.assertEqual(atual["tech-lead"], {"erros": 0, "base": 1, "taxa": 0.0})
        self.assertEqual(atual["conferente"], {"erros": 1, "base": 7, "taxa": round(1 / 7, 4)})
        self.assertEqual(dados["papeis"]["anterior"]["jarvis"], {"erros": 0, "base": 0, "taxa": None})
        self.assertEqual(dados["papeis"]["evals"], {"qa-engineer": {"travados": 1, "backlog": 1, "sem_ferramenta": 1},
                                                    "jarvis": {"travados": 1, "backlog": 0, "sem_ferramenta": 0}})
        rc, saida, _ = self.rodar("--ate", "2026-11-14", "--evals", str(evals))
        self.assertIn("papel qa-engineer: atual 50.00% (1/2) · anterior - (0/0) · evals 1 travados, 1 backlog, 1 sem ferramenta", saida)
        self.assertTrue(saida.splitlines()[-1].startswith("resumo: "))

    def test_evals_do_forge_tem_casos_por_papel(self):
        rc, dados = self.json("--ate", "2026-11-14")
        evals = dados["papeis"]["evals"]
        self.assertGreaterEqual(set(evals), {"jarvis", "tech-lead", "conferente", "agile-coach"})
        self.assertGreater(evals["jarvis"]["travados"], 20)

    def test_sem_registro_nem_evals_nao_ha_papel(self):
        rc, dados = self.json("--ate", "2026-11-14", "--evals", str(self.raiz / "nada"))
        self.assertIsNone(dados["papeis"])


class Disco(Placar):
    """MP6: a medida do disco das cópias de trabalho, com o limiar de bin/forge_disco.py; disco falso no processo."""

    def test_json_e_texto_trazem_o_uso_e_o_limiar(self):
        (self.raiz / "home" / ".forge-contrib").mkdir(parents=True)
        rc, dados = self.json("--ate", "2026-11-14")
        self.assertEqual(dados["disco"]["limiar"], 90)
        self.assertIsInstance(dados["disco"]["uso"], int)
        rc, saida, _ = self.rodar("--ate", "2026-11-14")
        self.assertRegex(saida.splitlines()[-2], r"^disco: \d+% de uso em ~/.forge-contrib \(limiar 90%\)$")

    def test_disco_ilegivel_da_uso_none(self):  # a medida que falha volta None; o traço do texto é o M15
        from importlib.machinery import SourceFileLoader
        from unittest import mock
        mod = SourceFileLoader("forge_placar_teste", str(PLACAR)).load_module()
        with mock.patch("shutil.disk_usage", side_effect=OSError("sem statvfs")):
            self.assertEqual(mod.disco(), {"uso": None, "limiar": 90})
        with mock.patch("shutil.disk_usage", return_value=shutil._ntuple_diskusage(100, 37, 63)):
            self.assertEqual(mod.disco(), {"uso": 37, "limiar": 90})


# META85 (ordem do dono 18/11): `forge-placar fases`, sobre um repositório git temporário com datas fixas em 2025.
def ambiente_limpo(raiz):
    """Ambiente limpo: nada herdado de quem roda a suíte (AR-4), sem config global nem de sistema."""
    return sem_manutencao({"PATH": os.environ.get("PATH", ""), "HOME": str(raiz / "home"), "GIT_CONFIG_GLOBAL": os.devnull,
                           "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def parecer_md(resultado):
    return f"---\ntipo: review\nparecer: {resultado}\n---\n# parecer\n"


class Fases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raiz = Path(tempfile.mkdtemp(prefix="forge-placar-fases-"))
        cls.repo = cls.raiz / "repo"
        cls.repo.mkdir()
        cls.env = ambiente_limpo(cls.raiz)
        cls.git("init", "-q", "-b", "develop")
        cls.commit("2025-03-17T09:00", {"base.txt": "0"}, "chore: base")
        # Item A (dia 18): desenvolvimento 30, pareceres 30, voltas 30, integração 30; o review reprova na 1.ª rodada
        cls.git("switch", "-q", "-c", "melhoria/a")
        cls.commit("2025-03-18T10:00", {"a.py": "1"}, "feat: a")
        cls.commit("2025-03-18T10:30", {"a.py": "2"}, "feat: a mais")
        cls.commit("2025-03-18T10:40", {"docs/reviews/a.md": parecer_md("reprovado")}, "docs(review): reprova")
        cls.commit("2025-03-18T10:45", {"docs/qa/bugs/a-01.md": "# bug sem frontmatter\n"}, "docs(qa): bug")
        cls.commit("2025-03-18T11:00", {"a.py": "3", "docs/devops/nota.md": "nota\n"}, "fix: a com nota")  # misto: é código
        cls.commit("2025-03-18T11:20", {"docs/reviews/a.md": parecer_md("aprovado")}, "docs(review): aprova")
        cls.commit("2025-03-18T11:30", {"docs/qa/a.md": parecer_md("aprovado")}, "docs(qa): aprova")
        cls.mesclar("melhoria/a", "2025-03-18T12:00", "Merge pull request #7 from dono/melhoria/a")
        # Item B (dia 18): pareceres 20, integração 30; aprovado na 1.ª rodada
        cls.git("switch", "-q", "-c", "melhoria/b")
        cls.commit("2025-03-18T13:00", {"b.py": "1"}, "feat: b")
        cls.commit("2025-03-18T13:20", {"docs/security/b.md": parecer_md("aprovado")}, "docs(security): aprova")
        cls.mesclar("melhoria/b", "2025-03-18T13:50", "Merge branch 'melhoria/b' into develop")
        # Item C (dia 19): sem parecer, assunto fora dos dois formatos
        cls.git("switch", "-q", "-c", "melhoria/c")
        cls.commit("2025-03-19T14:00", {"c.py": "1"}, "feat: c")
        cls.commit("2025-03-19T14:10", {"c.py": "2"}, "feat: c mais")
        cls.mesclar("melhoria/c", "2025-03-19T14:30", "integra c")
        # Item D (dia 20): tudo no mesmo minuto, total 0
        cls.git("switch", "-q", "-c", "melhoria/d")
        cls.commit("2025-03-20T15:00", {"d.py": "1"}, "feat: d")
        cls.mesclar("melhoria/d", "2025-03-20T15:00", "Merge pull request #9 from dono/melhoria/d")
        # Item E (dia 21): squash como o do forge-fechar (`gh pr merge --squash`: um pai, "<título> (#11)"), com os commits do
        # PR em refs/pull/11/head; pareceres 20, integração 40. No mesmo dia, um commit direto (fora) e o squash #12 sem a ref.
        cls.git("switch", "-q", "-c", "melhoria/e")
        cls.commit("2025-03-21T09:00", {"e.py": "1"}, "feat: e")
        cls.commit("2025-03-21T09:20", {"docs/reviews/e.md": parecer_md("aprovado")}, "docs(review): aprova")
        cls.git("update-ref", "refs/pull/11/head", "melhoria/e")
        cls.git("switch", "-q", "develop")
        cls.git("merge", "-q", "--squash", "melhoria/e")
        cls.git("commit", "-q", "-m", "feat: e (#11)", quando="2025-03-21T10:00")
        cls.commit("2025-03-21T10:30", {"direto.txt": "1"}, "chore: commit direto")
        cls.commit("2025-03-21T11:00", {"g.py": "1"}, "feat: g (#12)")
        # Dia 22: só um squash sem a ref do PR
        cls.commit("2025-03-22T11:00", {"h.py": "1"}, "feat: h (#13)")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.raiz, ignore_errors=True)

    @classmethod
    def git(cls, *args, quando="2025-03-17T08:00"):
        env = dict(cls.env, GIT_AUTHOR_DATE=f"{quando}:00+0000", GIT_COMMITTER_DATE=f"{quando}:00+0000")
        subprocess.run(["git", *args], cwd=cls.repo, env=env, check=True, capture_output=True, timeout=30)

    @classmethod
    def commit(cls, quando, arquivos, msg):
        for nome, texto in arquivos.items():
            (cls.repo / nome).parent.mkdir(parents=True, exist_ok=True)
            (cls.repo / nome).write_text(texto, encoding="utf-8")
        cls.git("add", "-A")
        cls.git("commit", "-q", "-m", msg, quando=quando)

    @classmethod
    def mesclar(cls, branch, quando, msg):
        cls.git("switch", "-q", "develop")
        cls.git("merge", "-q", "--no-ff", "-m", msg, branch, quando=quando)

    def rodar(self, *args):
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "fases", "--git", str(self.repo), "--ref", "develop", *args],
                           capture_output=True, text=True, env=self.env, cwd=self.raiz, timeout=60)
        return r.returncode, r.stdout, r.stderr

    def json(self, dia):
        rc, saida, erro = self.rodar("--dia", dia, "--json")
        self.assertEqual(rc, 0, erro)
        return json.loads(saida)

    def test_fases_e_primeira_rodada_por_item_e_total_do_dia(self):
        dados = self.json("2025-03-18")
        itens = {i["item"]: i for i in dados["itens"]}
        self.assertEqual(set(itens), {"melhoria/a", "melhoria/b"})  # o C e o D, de outros dias, ficam fora
        a, b = itens["melhoria/a"], itens["melhoria/b"]
        self.assertEqual(a["fases"], {"desenvolvimento": 30, "pareceres": 30, "voltas": 30, "integração": 30})
        self.assertEqual((a["total"], a["primeira_rodada"]), (120, False))  # a 1.ª versão do review reprovou
        self.assertEqual(b["fases"], {"desenvolvimento": 0, "pareceres": 20, "voltas": 0, "integração": 30})
        self.assertEqual((b["total"], b["primeira_rodada"]), (50, True))
        self.assertEqual((dados["soma"]["integração"], dados["media_min"], dados["meta_min"], dados["primeira_rodada"]), (60, 85, 85, [1, 2]))

    def test_texto_traz_a_meta_e_a_primeira_rodada(self):
        rc, saida, erro = self.rodar("--dia", "2025-03-18")
        self.assertEqual(rc, 0, erro)
        self.assertIn("meta 85 min do 1.º commit ao merge", saida)
        self.assertIn("item melhoria/a: desenvolvimento 30 min · pareceres 30 min · voltas 30 min · integração 30 min · total 120 min"
                      " · primeira rodada aprovada: não", saida)
        self.assertIn("total do dia: 2 itens · desenvolvimento 30 min (18%)", saida)
        self.assertIn("média 85 min por item (meta 85 min) · primeira rodada aprovada 1/2", saida)

    def test_item_sem_parecer_e_assunto_sem_branch(self):
        (c,) = self.json("2025-03-19")["itens"]
        self.assertEqual(len(c["item"]), 8)  # o sha curto do merge
        self.assertEqual(c["fases"], {"desenvolvimento": 10, "pareceres": 0, "voltas": 0, "integração": 20})
        self.assertIsNone(c["primeira_rodada"])

    def test_item_de_total_zero_nao_divide_por_zero(self):
        rc, saida, erro = self.rodar("--dia", "2025-03-20")
        self.assertEqual(rc, 0, erro)
        self.assertIn("total do dia: 1 itens · desenvolvimento 0 min (0%)", saida)
        self.assertIn("primeira rodada aprovada: -", saida)

    def test_dia_sem_item(self):
        dados = self.json("2025-03-17")
        self.assertEqual((dados["itens"], dados["media_min"], dados["primeira_rodada"]), ([], None, [0, 0]))
        rc, saida, _ = self.rodar("--dia", "2025-03-17")
        self.assertEqual((rc, saida.splitlines()[-1]), (0, "total do dia: nenhum item mesclado"))

    def test_sem_dia_vale_hoje(self):
        rc, saida, erro = self.rodar("--json")
        self.assertEqual(rc, 0, erro)
        self.assertEqual(json.loads(saida)["itens"], [])  # o repositório só tem 2025

    def test_sem_git_vale_a_pasta_atual(self):
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "fases", "--ref", "develop", "--dia", "2025-03-19", "--json"],
                           capture_output=True, text=True, env=self.env, cwd=self.repo, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(json.loads(r.stdout)["itens"]), 1)

    def test_squash_mede_pelos_commits_do_pr_e_conta_a_parte_sem_eles(self):  # review A1 do v0479-placar-fases
        dados = self.json("2025-03-21")
        (e,) = dados["itens"]
        self.assertEqual(e["item"], "#11")
        self.assertEqual(e["fases"], {"desenvolvimento": 0, "pareceres": 20, "voltas": 0, "integração": 40})
        self.assertEqual((e["total"], e["primeira_rodada"], dados["media_min"], dados["sem_fases"]), (60, True, 60, 1))
        rc, saida, erro = self.rodar("--dia", "2025-03-21")
        self.assertEqual(rc, 0, erro)
        self.assertIn("itens sem fases (squash): 1 (", saida)
        self.assertIn("total do dia: 1 itens · ", saida)

    def test_dia_so_com_squash_sem_ref_nao_diz_nenhum_mesclado(self):
        self.assertEqual((self.json("2025-03-22")["itens"], self.json("2025-03-22")["sem_fases"]), ([], 1))
        rc, saida, erro = self.rodar("--dia", "2025-03-22")
        self.assertEqual((rc, saida.splitlines()[-2:]), (0, ["itens sem fases (squash): 1 (sem os commits do PR em refs/pull/N/head;"
                                                            " fora da média)", "total do dia: nenhum item medido"]))

    def test_dia_sem_squash_nao_traz_a_linha(self):
        rc, saida, _ = self.rodar("--dia", "2025-03-18")
        self.assertNotIn("itens sem fases", saida)
        self.assertEqual(self.json("2025-03-18")["sem_fases"], 0)

    def test_ref_que_nao_existe_sai_com_2(self):
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "fases", "--git", str(self.repo), "--ref", "nao-existe"],
                           capture_output=True, text=True, env=self.env, cwd=self.repo, timeout=60)
        self.assertEqual(r.returncode, 2)
        self.assertIn("git log falhou", r.stderr)


# PLACAR-SEM-TESTE-POR-SEMANA (decisão do dono 18/11 15:10): `--prs` com JSON de exemplo, sem rede nem git.
EXEMPLO = [
    {"mergedAt": "2026-11-06T23:00:00Z", "body": "## Sem teste\nantes da janela"},
    {"mergedAt": "2026-11-07T10:00:00Z", "body": "## Sem teste\nsó texto"},
    {"mergedAt": "2026-11-10T10:00:00Z", "body": "## Sem teste\nmotivo"},
    {"mergedAt": "2026-11-10T11:00:00Z", "body": "Sem teste no texto, sem a seção"},
    {"mergedAt": "2026-11-11T10:00:00Z", "body": "### Sem teste\noutro nível de título"},
    {"mergedAt": "2026-11-12T10:00:00Z", "body": None},
    {"mergedAt": "2026-11-16T10:00:00Z", "body": "## O que mudou\nx\n\n## sem teste  \nmotivo"},
    {"mergedAt": "2026-11-20T10:00:00Z", "body": "## O que mudou\nx"},
    {"mergedAt": "2026-11-21T00:00:00Z", "body": "## Sem teste\nno fim exclusivo da janela"},
    {"mergedAt": None, "body": "## Sem teste\nPR aberto"},
    "não é PR",
]


class SemTeste(unittest.TestCase):
    def setUp(self):
        self.raiz = Path(tempfile.mkdtemp(prefix="forge-placar-sem-teste-"))
        self.addCleanup(shutil.rmtree, self.raiz, ignore_errors=True)

    def rodar(self, *args):
        """Python com -I e ambiente limpo (AR-4): nada herdado de quem roda a suíte."""
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(self.raiz / "home")}
        r = subprocess.run([sys.executable, "-I", str(PLACAR), "--raiz", str(self.raiz), "--ate", "2026-11-21",
                            "--evals", str(self.raiz / "sem-evals"), *args], capture_output=True, text=True, env=env, cwd=self.raiz,
                           timeout=60)
        return r.returncode, r.stdout, r.stderr

    def prs(self, texto, nome="prs.json"):
        arq = self.raiz / nome
        arq.write_text(texto, encoding="utf-8")
        return str(arq)

    def test_dados_de_exemplo_por_semana(self):
        arq = self.prs(json.dumps(EXEMPLO))
        rc, saida, erro = self.rodar("--prs", arq, "--json")
        self.assertEqual(rc, 0, erro)
        self.assertEqual(json.loads(saida)["sem_teste"], {"2026-W45": [1, 1], "2026-W46": [1, 4], "2026-W47": [1, 2]})
        rc, saida, erro = self.rodar("--prs", arq)
        self.assertIn("sem_teste: 2026-W45 1/1 · 2026-W46 1/4 · 2026-W47 1/2 (PRs com a seção Sem teste / PRs mesclados, por semana)",
                      saida)

    def test_sem_dados_sai_tracinho_nunca_zero(self):
        rc, saida, erro = self.rodar("--json")
        self.assertEqual(rc, 0, erro)
        self.assertIsNone(json.loads(saida)["sem_teste"])
        rc, saida, erro = self.rodar()
        self.assertIn("sem_teste: - (", saida)

    def test_lista_vazia_diz_nenhum_pr(self):
        rc, saida, erro = self.rodar("--prs", self.prs("[]"))
        self.assertEqual(rc, 0, erro)
        self.assertIn("sem_teste: nenhum PR mesclado (", saida)

    def test_arquivo_ausente_ou_invalido_sai_com_2(self):
        casos = ((str(self.raiz / "nada.json"), "não existe"), (self.prs("{nao json", "a.json"), "não é JSON"),
                 (self.prs('{"mergedAt": "2026-11-10"}', "b.json"), "não é uma lista"),
                 (self.prs('[{"mergedAt": "2026-13-45T10:00:00Z"}]', "c.json"), "mergedAt inválido: 2026-13-45"),  # segurança A1
                 (self.prs("[" * 100000 + "]" * 100000, "d.json"), "não é JSON legível"))
        for arq, motivo in casos:
            with self.subTest(motivo=motivo):
                rc, _, erro = self.rodar("--prs", arq)
                self.assertEqual(rc, 2, erro)
                self.assertIn(motivo, erro)
                self.assertNotIn("Traceback", erro)

    def test_aninhamento_no_teto_e_colchete_em_string_passam(self):
        """Volta do CI (E20.13): o teto é do forge-placar, igual em toda versão do Python; colchete dentro de string não conta."""
        no_teto = "[" * 64 + "]" * 64
        em_string = json.dumps([{"mergedAt": "2026-11-17T10:00:00Z", "body": "[" * 1000 + "{" * 1000 + '\\"'}])
        for texto in (no_teto, em_string):
            with self.subTest(texto=texto[:20]):
                rc, _, erro = self.rodar("--prs", self.prs(texto))
                self.assertEqual(rc, 0, erro)
        rc, _, erro = self.rodar("--prs", self.prs("[" * 65 + "]" * 65))
        self.assertEqual(rc, 2, erro)
        self.assertIn("não é JSON legível (aninhado acima de 64 níveis)", erro)


    def test_varredura_de_aninhamento_e_de_um_passe_e_trata_escape(self):
        """Volta da segurança (E20.17): custo linear sem relógio (cada caractere é lido uma vez, de um iterável que conta) e
        o mesmo resultado nas strings com escape, na sem fecho e no teto."""
        from importlib.machinery import SourceFileLoader
        mod = SourceFileLoader("forge_placar_varredura", str(PLACAR)).load_module()

        class Contado:
            def __init__(self, texto):
                self.texto, self.lidos = texto, 0

            def __iter__(self):
                for c in self.texto:
                    self.lidos += 1
                    yield c

        sem_fecho = '"' + '\\"' * 40000
        for texto in (sem_fecho, "[" * 70 + sem_fecho, "[" * 10 + "]" * 10):
            with self.subTest(texto=texto[:12]):
                contado = Contado(texto)
                mod.fundo_demais(contado, teto=1000)
                self.assertEqual(contado.lidos, len(texto))
        casos = ((r'["a\\"] ' + "[" * 64, False),      # a barra escapada deixa a aspa fechar a string
                 (r'"\"' + "[" * 100 + '"', False),     # aspa escapada não fecha a string
                 (r'"\\"' + "[" * 65, True),           # barra escapada, a string fecha, 65 abertos
                 ('[' * 64 + ']' * 64, False), ('{' * 65, True), ('[]' * 65, False), ('[' * 65 + '"]"', True))
        for texto, esperado in casos:
            with self.subTest(texto=texto[:20]):
                self.assertIs(mod.fundo_demais(texto), esperado)


if __name__ == "__main__":
    unittest.main()
