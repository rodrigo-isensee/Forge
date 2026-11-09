"""0.43.1 (frente E, P1, P2, P4): a ferramenta confere o brief e a entrega no lugar do agente conferente.

`brief selar` corrige os campos calculados, roda as checagens do `forge-check brief` e grava o selo no `## Histórico` do pedido; o hook
`agentes` só dispara `forge:<papel>` com brief selado e intacto; o `brief gerar` cita as decisões por referência (hash do bloco) e copia só
as aplicáveis à etapa; `entrega --pedido` confere escopo declarado, provas e commits e é o único escritor de `entrega conferida <sha40>`.
Sem rede: o `origin` é um repositório nu local."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import sem_manutencao  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ / "bin" / "forge-check"
HOOKS = RAIZ / "hooks"
fc = SourceFileLoader("forge_check_selo_e_entrega", str(FORGE_CHECK)).load_module()
LANCADOR = ("import runpy, sys; sys.path.insert(0, sys.argv[1]); import _comum; "
            "sys.argv = [sys.argv[2]]; runpy.run_path(sys.argv[0], run_name='__main__')")

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X · `confirmado`

## Etapas
- E1.1 (node-backend): implementação do recurso X.
- E1.2 (tech-lead): review do recurso X.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01 10:00): "regra geral A".
DECISÃO DO DONO (2026-01-01 10:01): "na E1.1 use a função f".

## Histórico
- 2026-01-01 09:00: aberto
"""


class Repositorio(unittest.TestCase):
    """Um projeto git com `origin` local, a develop publicada e a branch `melhoria/x` nascida dela."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-selo-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.proj = self.tmp / "proj"
        self.env = sem_manutencao({k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "FORGE_"))}
                                  | {"HOME": str(self.home), "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
        self.git_em(self.tmp, "init", "-q", "--bare", "origem.git")
        self.git_em(self.tmp, "init", "-q", "-b", "develop", "proj")
        self.gravar("docs/pedidos/exemplo.md", PEDIDO)
        self.gravar("bin/app", "x\n")
        self.gravar("KANBAN.md", "# Quadro\n")
        self.gravar("docs/economia-de-tokens.md", "# economia\n")
        self.git("add", "bin", "KANBAN.md", "docs/economia-de-tokens.md")
        self.commit("base")
        self.git("remote", "add", "origin", str(self.tmp / "origem.git"))
        self.git("push", "-q", "origin", "develop")
        self.git("fetch", "-q", "origin")
        self.git("switch", "-q", "-c", "melhoria/x")
        self.base = self.git("rev-parse", "HEAD")

    def git_em(self, pasta, *args):
        r = subprocess.run(["git", "-C", str(pasta), *args], capture_output=True, text=True, env=self.env, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def git(self, *args):
        return self.git_em(self.proj, *args)

    def commit(self, mensagem):
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", mensagem)
        return self.git("rev-parse", "HEAD")

    def gravar(self, rel, texto):
        arq = self.proj / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def rodar(self, *args):
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.proj), *map(str, args)], capture_output=True,
                           text=True, env=self.env, timeout=300)
        return r.returncode, r.stdout + r.stderr

    def pedido(self):
        return (self.proj / "docs" / "pedidos" / "exemplo.md").read_text(encoding="utf-8")

    def brief(self, base_sha=None, arquivos="bin/app, docs/notas/", pq_extra="", decisoes=None):
        """O brief que o `brief gerar` monta, já completado como o Jarvis faria."""
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--branch", "melhoria/x",
                               "--etapa", "codigo", "--gravar")
        self.assertEqual(rc, 0, saida)
        arq = self.proj / "docs" / "briefs" / "exemplo-node-backend-1.md"
        texto = arq.read_text(encoding="utf-8")
        texto = texto.split("\n", 1)[1]  # o comentário do gerador
        texto = texto.replace("Cobre: E1.1\n", "Cobre: E1.1\n\n## Objetivo\nFazer X (E1).\n")
        texto = texto.replace("- PREENCHER: o que esta etapa entrega, cada item citando o ID do pedido\n", "- a função f em bin/app (E1.1)\n")
        texto = texto.replace("- arquivos: PREENCHER: caminhos, pastas/ ou globs que esta etapa toca, tirados do desenho", f"- arquivos: {arquivos}")
        corte, pronto = texto.index("## Marca de corte"), texto.index("## Pronto quando")
        texto = texto[:corte] + texto[pronto:]
        pronto, autor = texto.index("## Pronto quando"), texto.index("- PQ-N (cmd, do autor)")
        texto = (texto[:pronto] + "## Pronto quando\n- PQ-1 (cmd): `git rev-parse HEAD` · espera: rc=0\n- PQ-2 (arquivo): `test -e bin/app` · existe\n"
                 + pq_extra + texto[autor:].replace("PQ-N", "PQ-3", 1))
        if base_sha:
            texto = texto.replace(f"Base-sha: {self.base}", f"Base-sha: {base_sha}")
        if decisoes is not None:
            texto = decisoes(texto)
        arq.write_text(texto, encoding="utf-8")
        return arq

    def selar(self, arq=None):
        return self.rodar("brief", "selar", "--arquivo", f"docs/briefs/{(arq or self.proj / 'docs/briefs/exemplo-node-backend-1.md').name}",
                          "--pedido", "exemplo")

    def entregar(self, *extra):
        self.gravar("docs/notas/a.md", "nota\n")
        self.gravar("bin/app", "x\ny\n")
        self.git("add", "bin/app", "docs/notas", *extra)
        return self.commit("feat: f")


class Gerar(Repositorio):
    def test_decisoes_por_referencia_e_so_a_aplicavel_copiada(self):
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--branch", "melhoria/x",
                               "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        cobradas = fc.decisoes_cobradas(self.proj, self.proj / "docs/pedidos/exemplo.md", PEDIDO)
        self.assertIn(f"- decisões: pedido exemplo até {fc.hash_das_decisoes(cobradas)} (2 linhas DECISÃO DO DONO em 1 fontes", saida)
        self.assertIn('- DECISÃO DO DONO (2026-01-01 10:01): "na E1.1 use a função f".', saida)
        self.assertNotIn("regra geral A", saida)  # vale pela referência, sem cópia
        self.assertIn("- arquivos: PREENCHER", saida)

    def test_hash_muda_com_decisao_nova_e_nao_com_historico(self):
        cobradas = lambda t: fc.decisoes_cobradas(self.proj, self.proj / "docs/pedidos/exemplo.md", t)  # noqa: E731
        antes = fc.hash_das_decisoes(cobradas(PEDIDO))
        self.assertEqual(antes, fc.hash_das_decisoes(cobradas(PEDIDO + "- 2026-01-02 10:00: brief selado docs/briefs/a.md " + "a" * 64 + "\n")))
        nova = PEDIDO.replace("## Histórico", 'DECISÃO DO DONO (2026-01-02 10:00): "nova".\n\n## Histórico')
        self.assertNotEqual(antes, fc.hash_das_decisoes(cobradas(nova)))


class Selar(Repositorio):
    def test_sela_uma_vez_e_grava_no_historico(self):
        arq = self.brief()
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.assertIn("decisões: ok por referência", saida)
        sha = hashlib.sha256(arq.read_bytes()).hexdigest()
        self.assertEqual(fc.selos_do_pedido(self.pedido()), [("docs/briefs/exemplo-node-backend-1.md", sha)])
        self.assertIn(f"Brief-sha256: {sha}", saida)
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.assertIn("selo: já gravado", saida)
        self.assertEqual(len(fc.selos_do_pedido(self.pedido())), 1)
        self.assertIsNone(fc.selo_do_brief(arq))
        arq.write_text(arq.read_text(encoding="utf-8") + "linha nova\n", encoding="utf-8")
        self.assertIn("mudou depois do selo", fc.selo_do_brief(arq))

    def test_base_sha_digitado_errado_e_corrigido(self):
        arq = self.brief(base_sha="1" * 40)
        texto = arq.read_text(encoding="utf-8").replace(f"--base-sha {self.base}", "--base-sha " + "2" * 40)
        arq.write_text(texto, encoding="utf-8")
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"corrigido: Base-sha {'1' * 40} -> {self.base}", saida)
        texto = arq.read_text(encoding="utf-8")
        self.assertIn(f"Base-sha: {self.base}", texto)
        self.assertIn(f"--base-sha {self.base} --etapa codigo", texto)
        self.assertNotIn("1" * 40, texto)

    def test_referencia_desatualizada_e_corrigida_pela_decisao_nova(self):
        arq = self.brief()
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--literal", "outra regra geral")
        rc, saida = self.rodar("brief", str(arq), "--pedido", "exemplo")
        self.assertIn("difere do bloco atual", saida)  # informativo: a decisão nova vale pela referência
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)
        self.assertIn("corrigido: hash das decisões", saida)

    def test_brief_incompleto_nao_sela(self):
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:node-backend", "--branch", "melhoria/x",
                               "--etapa", "codigo", "--gravar")
        self.assertEqual(rc, 0, saida)
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("resultado: reprovado (sem selo)", saida)
        self.assertEqual(fc.selos_do_pedido(self.pedido()), [])

    def test_aplicavel_ausente_e_outro_pedido_reprovam(self):
        self.brief(decisoes=lambda t: t.replace('- DECISÃO DO DONO (2026-01-01 10:01): "na E1.1 use a função f".\n', ""))
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn("decisões: falta a aplicável", saida)

    def test_teto_de_caracteres(self):
        self.brief(decisoes=lambda t: t.replace("Fazer X (E1).", "Fazer X (E1). " + "palavra " * 1300))
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"teto {fc.TETO_DE_CARACTERES_DO_BRIEF}", saida)

    def test_anotar_nao_grava_linha_da_ferramenta(self):
        for literal in ("brief selado docs/briefs/x.md " + "a" * 64, "entrega conferida " + "b" * 40):
            rc, saida = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "historico", "--literal", literal)
            self.assertEqual(rc, 2, saida)
            self.assertIn("só a ferramenta grava", saida)
        self.assertEqual(self.pedido(), PEDIDO)

    def test_propagar_pula_brief_por_referencia(self):
        arq = self.brief()
        arq.chmod(0o444)  # em voo: aprovado
        self.addCleanup(arq.chmod, 0o644)
        rc, saida = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--literal", "nova", "--propagar")
        self.assertEqual(rc, 0, saida)
        self.assertIn("decisões por referência; nada a propagar", saida)
        self.assertFalse((arq.parent / "exemplo-node-backend-2.md").exists())


class Entrega(Repositorio):
    def selado(self, **kw):
        self.brief(**kw)
        rc, saida = self.selar()
        self.assertEqual(rc, 0, saida)

    def conferir(self, *extra):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", *extra)

    def test_cumpriu_grava_uma_vez(self):
        self.selado()
        head = self.entregar()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        for linha in ('escopo: ok (declarado no brief: bin/app) "bin/app"', "prova: PQ-1 (cmd): ok", "prova: PQ-2 (arquivo): ok",
                      "prova: PQ-3 (cmd): ok (é esta conferência)", "commits: 1 em", "resultado: cumpriu"):
            self.assertIn(linha, saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [head])
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn("gravado: já existia", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [head])

    def test_sem_gravar_nao_grava(self):
        self.selado()
        self.entregar()
        rc, saida = self.conferir("--sem-gravar")
        self.assertEqual(rc, 0, saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])

    def test_arquivo_fora_do_declarado_nao_cumpre(self):
        self.selado()
        self.gravar("fora.txt", "z\n")
        self.entregar("fora.txt")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])

    def test_prova_que_falha_nao_cumpre(self):
        self.selado(pq_extra="- PQ-4 (cmd): `git rev-parse HEAD` · espera: igual 'nada'\n")
        self.entregar()
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("prova: PQ-4 (cmd): diverge de 'igual 'nada''", saida)

    def test_worktree_suja_e_sem_brief_selado_nao_cumprem(self):
        self.brief()
        self.entregar()
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("nenhum brief selado", saida)
        self.assertEqual(self.selar()[0], 0)
        self.gravar("bin/app", "sujo\n")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("com mudança fora do commit", saida)

    def test_etapa_diferente_do_brief_nao_acha(self):
        self.selado()
        self.entregar()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "qa")
        self.assertEqual(rc, 1, saida)
        self.assertIn("nenhum brief selado", saida)

    def test_forma_nova_recusa_campos_digitados(self):
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo", "--base-sha", self.base)
        self.assertEqual(rc, 2, saida)
        self.assertIn("são calculados", saida)


class Hook(Repositorio):
    """O hook `agentes`: especialista só com brief selado e intacto; o conferente segue opcional."""

    def setUp(self):
        super().setUp()
        (self.proj / ".forge").mkdir()
        (self.proj / ".forge" / "versao").write_text("0.0.0\n", encoding="utf-8")
        proc = self.tmp / "proc"
        proc.mkdir()
        (proc / "loadavg").write_text("0.1 0.1 0.1\n", encoding="utf-8")
        (proc / "meminfo").write_text(f"MemTotal: {16 * 1024 * 1024} kB\nMemFree: 1 kB\nMemAvailable: {8 * 1024 * 1024} kB\n", encoding="utf-8")
        self.proc = proc

    def lancar(self, prompt, tipo="forge:node-backend"):
        self.n = getattr(self, "n", 0) + 1
        entrada = {"hook_event_name": "PreToolUse", "tool_name": "Agent", "session_id": "s", "cwd": str(self.proj),
                   "tool_input": {"subagent_type": tipo, "description": f"d{self.n}", "prompt": prompt}}
        env = dict(self.env, FORGE_PROC=str(self.proc), FORGE_NPROC="8")
        return subprocess.run([sys.executable, "-c", LANCADOR, str(HOOKS), str(HOOKS / "agentes.py")], input=json.dumps(entrada),
                              cwd=self.proj, env=env, capture_output=True, text=True, timeout=120)

    def test_especialista_so_com_brief_selado_e_intacto(self):
        arq = self.brief()
        prompt = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-BRIEF", r.stderr)
        self.assertIn("sem selo", r.stderr)
        self.assertEqual(self.selar()[0], 0)
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 0, r.stderr)
        sha = hashlib.sha256(arq.read_bytes()).hexdigest()
        self.assertEqual(self.lancar(prompt + f"\nBrief-sha256: {sha}").returncode, 0)
        r = self.lancar(prompt + f"\nBrief-sha256: {'c' * 64}")
        self.assertEqual(r.returncode, 2, r.stderr)
        arq.write_text(arq.read_text(encoding="utf-8") + "editado depois\n", encoding="utf-8")
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("mudou depois do selo", r.stderr)

    def test_especialista_sem_brief_no_prompt_bloqueia(self):
        r = self.lancar("faça o recurso X")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("não cita o brief", r.stderr)

    def test_fora_do_plugin_e_conferente_nao_pedem_selo(self):
        self.assertEqual(self.lancar("faça X", tipo="general-purpose").returncode, 0)
        r = self.lancar("faça X", tipo="forge:conferente")  # o conferente segue com a forma da mensagem, sem selo
        self.assertEqual(r.returncode, 2)
        self.assertIn("forge-check brief mensagem", r.stderr)

    def test_selo_forjado_com_outro_hash_nao_vale(self):
        self.brief()
        self.gravar("docs/pedidos/exemplo.md", self.pedido() + f"- 2026-01-02 10:00: brief selado docs/briefs/exemplo-node-backend-1.md {'d' * 64}\n")
        r = self.lancar("Leia docs/briefs/exemplo-node-backend-1.md")
        self.assertEqual(r.returncode, 2, r.stderr)


if __name__ == "__main__":
    unittest.main()
