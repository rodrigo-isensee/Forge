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
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ no caminho também no modo `tests.<módulo>`
from ambiente_git import remoto_sem_manutencao, sem_manutencao  # noqa: E402

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
        remoto_sem_manutencao(self.tmp / "origem.git")
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

    def test_etapa_com_prefixo_do_plugin_e_do_mesmo_papel(self):
        """Pedido que escreve `(forge:tech-lead)` na etapa: o `--cobre` aceita o destino `forge:tech-lead` (antes: `é de forge:tech-lead,
        não de tech-lead`)."""
        self.gravar("docs/pedidos/exemplo.md", PEDIDO.replace("E1.2 (tech-lead)", "E1.2 (forge:tech-lead, outra instância)"))
        rc, saida = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:tech-lead", "--cobre", "E1.2",
                               "--etapa", "review")
        self.assertEqual(rc, 0, saida)
        self.assertEqual(fc.ler_pedido_brief(self.pedido())["etapas"]["E1.2"][0], "tech-lead")

    def test_hash_muda_com_decisao_nova_e_nao_com_historico(self):
        cobradas = lambda t: fc.decisoes_cobradas(self.proj, self.proj / "docs/pedidos/exemplo.md", t)  # noqa: E731
        antes = fc.hash_das_decisoes(cobradas(PEDIDO))
        self.assertEqual(antes, fc.hash_das_decisoes(cobradas(PEDIDO + "- 2026-01-02 10:00: brief selado docs/briefs/a.md " + "a" * 64 + "\n")))
        nova = PEDIDO.replace("## Histórico", 'DECISÃO DO DONO (2026-01-02 10:00): "nova".\n\n## Histórico')
        self.assertNotEqual(antes, fc.hash_das_decisoes(cobradas(nova)))


class Selar(Repositorio):
    def test_sem_selar_corrige_os_derivados_e_nao_grava_selo(self):
        """B2 (review da 0.44.1): a ação automática do O1 (`brief selar --sem-selar`) recalcula o Base-sha e nunca grava o selo."""
        arq = self.brief(base_sha="0" * 40)
        rc, saida = self.rodar("brief", "selar", "--sem-selar", "--arquivo", "docs/briefs/exemplo-node-backend-1.md", "--pedido", "exemplo")
        self.assertEqual(rc, 0, saida)
        self.assertIn("sem selo", saida)
        self.assertIn(f"Base-sha: {self.base}", arq.read_text(encoding="utf-8"))
        self.assertEqual(fc.selos_do_pedido(self.pedido()), [])
        arq.write_text(arq.read_text(encoding="utf-8").replace(f"Base-sha: {self.base}\n", ""), encoding="utf-8")
        rc, saida = self.rodar("brief", "selar", "--sem-selar", "--arquivo", "docs/briefs/exemplo-node-backend-1.md", "--pedido", "exemplo")
        self.assertEqual(rc, 1, saida)
        self.assertIn("com reprovação (sem selo)", saida)
        self.assertEqual(fc.selos_do_pedido(self.pedido()), [])

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
        self.assertIn(f"--base-sha {self.base} --mutantes ${{TMPDIR:-/tmp}}/forge-mutantes.log --pronto ${{TMPDIR:-/tmp}}/forge-pronto.log --etapa codigo", texto)  # META85
        self.assertNotIn("1" * 40, texto)

    def test_referencia_desatualizada_e_corrigida_pela_decisao_nova(self):
        arq = self.brief()
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "outra regra geral")
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

    def test_vv3_arquivos_onde_o_hook_barra_o_destino_nao_sela(self):
        """VV-3: a linha `- arquivos:` declara `docs/reviews/`, que o hook só deixa o tech-lead escrever; o brief ao node-backend sai
        reprovado no selo, antes do trabalho, e o pedido fica sem selo."""
        self.brief(arquivos="bin/app, docs/reviews/exemplo.md")
        rc, saida = self.selar()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escrita: barrada "docs/reviews/exemplo.md" (', saida)
        self.assertIn('escrita: ok "bin/app"', saida)
        self.assertEqual(fc.selos_do_pedido(self.pedido()), [])

    def test_vv3_caminhos_da_linha_arquivos_sem_crase(self):
        secoes = {"Entregar": ["- a função f em `bin/app` (E1.1)", "- arquivos: bin/app, docs/notas/, tests/test_*.py"]}
        self.assertEqual(fc.caminhos_do_entregar(secoes), ["bin/app", "docs/notas/", "tests/test_*.py"])
        self.assertEqual(fc.caminhos_do_entregar({"Entregar": [f"- arquivos: {fc.PREENCHER}: caminhos"]}), [])

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

    def test_o_teto_do_texto_e_o_da_ferramenta(self):
        """R-BRIEF e a skill citam o mesmo teto que o selo aplica (o texto da T dizia 8.000; a ferramenta usa 10.000)."""
        numero = f"{fc.TETO_DE_CARACTERES_DO_BRIEF:,}".replace(",", ".")
        for rel in ("docs/regras/R-BRIEF.md", "skills/briefs-e-conferencia/SKILL.md"):
            with self.subTest(rel=rel):
                self.assertIn(f"até {numero} caracteres", (FORGE_CHECK.parent.parent / rel).read_text(encoding="utf-8"))

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
        rc, saida = self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "nova", "--propagar")
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
                      "prova: PQ-3 (cmd): ok (é esta conferência)", "commits: 1 em", "resultado: cumpriu",
                      "pronto: não rodado aqui (--so-leitura, sem worktree ou fora do Forge)"):  # D2-NO-BRIEF: fora do Forge
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

    def test_so_leitura_nao_roda_prova_cmd_nem_grava(self):
        """D4 (0.44.0, L2 do review de segurança da 0.43.1): a forma do conferente lê só git e disco; o PQ cmd fica com o autor e o CI."""
        self.selado(pq_extra="- PQ-4 (cmd): `git rev-parse HEAD` · espera: igual 'nada'\n")
        self.entregar()
        rc, saida = self.conferir("--so-leitura")
        self.assertEqual(rc, 0, saida)
        self.assertIn("prova: PQ-4 (cmd): não reexecutada (--so-leitura: quem confere não roda código da branch)", saida)
        self.assertIn("prova: PQ-1 (cmd): não reexecutada (--so-leitura", saida)
        self.assertIn("gravado: nada (--so-leitura)", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])
        rc, saida = self.conferir("--sem-gravar")
        self.assertEqual(rc, 1, saida)
        self.assertIn("prova: PQ-4 (cmd): diverge de", saida)
        rc, saida = self.rodar("entrega", "exemplo", "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                               "--etapa", "codigo", "--so-leitura")
        self.assertEqual(rc, 2, saida)
        self.assertIn("--so-leitura só valem com `entrega --pedido`", saida)

    def test_arquivo_fora_do_declarado_nao_cumpre(self):
        self.selado()
        self.gravar("fora.txt", "z\n")
        self.entregar("fora.txt")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])

    def merge_da_develop(self, arquivos, squash=False):
        """A develop anda no `origin` com `arquivos` (outro lote) e a branch a mescla, como depois de um `git merge origin/develop`;
        com `squash`, num commit de um pai só (`git merge --squash`), que o git não liga à base. A ponta fica ancorada num brief
        selado depois (FILTROS-L08-G2-ORIGIN-LOCAL: sem âncora, o que a develop trouxe segue no escopo)."""
        self.git("switch", "-q", "develop")
        for rel, texto in arquivos.items():
            self.gravar(rel, texto)
        self.git("add", *arquivos)
        self.commit("outro lote")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        Conferencia.selar_copia(self, "exemplo-outra-1.md", {"Branch: melhoria/x": "Branch: melhoria/y",
                                f"Base-sha: {self.base}": f"Base-sha: {self.git('rev-parse', 'origin/develop')}"}, selar=False)
        if squash:
            self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--squash", "origin/develop")
            self.commit("merge da develop")
        else:
            self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge da develop", "origin/develop")

    def conferida_e_merge_da_develop(self, squash):
        """A 1.a entrega conferida e, depois dela, o merge da develop com o parecer de outro lote."""
        self.selado()
        self.entregar()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.merge_da_develop({"docs/reviews/outro-1.md": "---\ntipo: review\nparecer: aprovado\n---\n# outro lote\n",
                               "bin/outro": "do outro lote\n"}, squash)

    def test_merge_da_develop_nao_tira_do_declarado(self):  # v0455: o que o merge da base trouxe, igual à base, sai do escopo
        self.merge_da_develop_cumpre(squash=False)

    def test_merge_squash_da_develop_fora_das_etapas_de_merge_segue_fora_do_declarado(self):
        """v0455 (A1 do review): o filtro por conteúdo vale só nas etapas de merge; o `merge --squash` da develop não é coberto
        na `codigo`, e o que ele trouxe conta como fora do declarado, como na 0.45.4."""
        self.conferida_e_merge_da_develop(squash=True)
        head = self.gravar_app_de_novo()
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "docs/reviews/outro-1.md"', saida)
        self.assertIn('escopo: fora do declarado no brief "bin/outro"', saida)
        self.assertNotIn(head, fc.entregas_conferidas(self.pedido()))

    def test_origin_da_base_forjada_nao_esconde_o_fora_do_declarado(self):
        """v0455 (A1 do review, sonda S1): a `origin/<base>` é ref local; reescrita com a árvore do head (`git update-ref`), o
        arquivo fora do declarado na etapa `codigo` continua reprovando e nada se grava."""
        self.selado()
        self.gravar("fora.txt", "z\n")
        self.entregar("fora.txt")
        arvore = self.git("rev-parse", "HEAD^{tree}")
        dev = self.git("rev-parse", "refs/remotes/origin/develop")
        falso = self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit-tree", arvore, "-p", dev, "-m", "forjado")
        self.git("update-ref", "refs/remotes/origin/develop", falso)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)
        self.assertNotIn("resultado: cumpriu", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])

    def gravar_app_de_novo(self):
        self.gravar("bin/app", "x\ny\nz\n")
        self.git("add", "bin/app")
        return self.commit("feat: f de novo")

    def merge_da_develop_cumpre(self, squash):
        self.conferida_e_merge_da_develop(squash)
        head = self.gravar_app_de_novo()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertNotIn("outro-1.md", saida)
        self.assertNotIn('"bin/outro"', saida)
        self.assertIn('escopo: ok (declarado no brief: bin/app) "bin/app"', saida)
        self.assertIn("resultado: cumpriu", saida)
        self.assertIn(head, fc.entregas_conferidas(self.pedido()))

    def test_merge_da_develop_nao_esconde_o_que_a_branch_mudou(self):  # v0455: o arquivo diferente da base segue contando
        self.merge_da_develop_nao_esconde(squash=False)

    def merge_da_develop_nao_esconde(self, squash):
        self.conferida_e_merge_da_develop(squash)
        self.gravar("bin/outro", "a branch mudou\n")
        self.gravar("fora.txt", "z\n")
        self.git("add", "bin/outro", "fora.txt")
        self.commit("feat: fora do declarado")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "bin/outro"', saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)
        self.assertNotIn("outro-1.md", saida)

    def test_d2_vermelho_na_copia_do_forge_nao_cumpre(self):
        """D2-NO-BRIEF (v0481 E14.51): na cópia do Forge, com .claude-plugin/plugin.json (aqui ignorado pelo git, a worktree segue
        limpa), a conferência roda o `forge-check pronto`; o rc fora de 0 reprova com a última linha dele e a entrega não é gravada."""
        self.selado()
        self.entregar()
        (self.proj / ".git" / "info" / "exclude").write_text(".claude-plugin/\n", encoding="utf-8")
        self.gravar(".claude-plugin/plugin.json", "{}\n")
        falsos = self.tmp / "falsos"
        falsos.mkdir()
        (falsos / "gh").write_text("#!/bin/sh\necho 'no pull requests found for branch' >&2\nexit 1\n", encoding="utf-8")
        (falsos / "gh").chmod(0o755)
        self.env["PATH"] = f"{falsos}{os.pathsep}{self.env.get('PATH', '')}"
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("pendente: D2 vermelho: forge-check pronto rc 1: pronto: reprovado em ", saida)
        self.assertIn("resultado: não cumpriu", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])

    def gh_falso(self, head, checks):
        """O gh do PR #7 da `melhoria/x` (nome exato, como o `gh pr view <branch>`) no `head`, com os `checks` do `gh pr checks 7`."""
        falsos = self.tmp / "falsos"
        falsos.mkdir(exist_ok=True)
        (falsos / "checks.json").write_text(json.dumps(checks), encoding="utf-8")
        pr = json.dumps({"number": 7, "headRefOid": head, "baseRefName": "develop"})
        (falsos / "gh").write_text(
            "#!/bin/sh\n"
            f"if [ \"$1 $2 $3\" = 'pr view melhoria/x' ]; then echo '{pr}'; exit 0; fi\n"
            f"if [ \"$1 $2 $3\" = 'pr checks 7' ]; then cat '{falsos}/checks.json'; exit 0; fi\n"
            "echo 'no pull requests found for branch' >&2; exit 1\n", encoding="utf-8")
        (falsos / "gh").chmod(0o755)
        self.env["PATH"] = f"{falsos}{os.pathsep}{self.env.get('PATH', '')}"

    def test_sem_worktree_com_o_head_no_forge_nao_cumpre(self):
        """E14.81 e G3-ENTREGA-PELO-CI (v0481 E28.1): o head traz o manifesto do Forge e a branch não tem worktree no repositório de
        quem confere (a cópia do autor é clone); o D2 local não roda: com o PR em outro head, ou o CI vermelho no head, a entrega não
        cumpre nem é gravada; com o CI concluído e verde no head (a `catraca`, fora da linha do CI, vermelha), cumpre."""
        self.selado(arquivos="bin/app, docs/notas/, .claude-plugin/")
        self.gravar(".claude-plugin/plugin.json", "{}\n")
        head = self.entregar(".claude-plugin")
        self.git("switch", "-q", "--detach")
        self.gh_falso("0" * 40, [])
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"pendente: o PR #7 está em 000000000000, não no head entregue {head[:12]}", saida)
        self.assertNotIn("D2 sem worktree", saida)
        self.gh_falso(head, [{"name": "bateria", "bucket": "pass", "workflow": "CI"},
                             {"name": "bateria (python 3.14)", "bucket": "fail", "workflow": "CI"}])
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f"pendente: CI do PR #7 no head {head[:12]} não concluído e verde: CI/bateria (python 3.14) (fail)", saida)
        self.assertIn("resultado: não cumpriu", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [])
        agregados = [{"name": par.split("/", 1)[1], "bucket": "pass", "workflow": "CI"} for par in fc.JOBS_DO_AGREGADOR]
        self.gh_falso(head, agregados + [{"name": "bateria (python 3.14)", "bucket": "pass", "workflow": "CI"},
                                         {"name": "catraca", "bucket": "fail", "workflow": "Catraca"}])
        rc, saida = self.conferir("--worktree", str(self.proj))  # a cópia no head, para os PQ cmd do brief
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"prova: CI do PR #7 concluído e verde no head {head[:12]} ({len(agregados) + 1} checks", saida)
        self.assertEqual(fc.entregas_conferidas(self.pedido()), [head])
        self.gravar(".forge/versao", "0.1.0\n")  # um projeto com o manifesto não é o Forge: a linha só informa
        self.git("add", ".forge")
        self.git("switch", "-q", "melhoria/x")
        self.commit("chore: versão do projeto")
        self.git("switch", "-q", "--detach")
        self.assertIn("pronto: não rodado aqui", self.conferir()[1])

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

    def lancar(self, prompt, tipo="forge:node-backend", limpar=True):
        self.n = getattr(self, "n", 0) + 1
        # cada lançamento sai sem reserva anterior: aqui só o selo é conferido; a delegação por branch (Z10) é de test_agentes_hash_brief
        if limpar:
            (self.proj / ".forge" / "run" / "agentes.json").unlink(missing_ok=True)
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

    def test_brief_selado_com_estado_ilegivel_recusa_por_r_teto(self):
        """HOOK-ESTADO-ILEGIVEL-LIBERA (A1): o selo em dia passa o R-BRIEF, e o agentes.json ilegível recusa por R-TETO, intacto."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        estado = self.proj / ".forge" / "run" / "agentes.json"
        estado.parent.mkdir(parents=True, exist_ok=True)
        estado.write_text("x", encoding="utf-8")
        r = self.lancar("Leia docs/briefs/exemplo-node-backend-1.md e execute.", limpar=False)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("R-TETO: registro de agentes ilegível", r.stderr)
        self.assertNotIn("R-BRIEF", r.stderr)
        self.assertEqual(estado.read_text(encoding="utf-8"), "x")

    def test_especialista_sem_brief_no_prompt_bloqueia(self):
        r = self.lancar("faça o recurso X")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("não cita o brief", r.stderr)

    def test_fora_do_plugin_pede_selo_e_conferente_nao(self):
        """D2 (0.44.0, M2 do review de segurança da 0.43.1): o tipo de fora do plugin também escreve e pede o selo."""
        self.assertEqual(self.lancar("faça X", tipo="general-purpose").returncode, 2)
        r = self.lancar("faça X", tipo="forge:conferente")  # o conferente segue com a forma da mensagem, sem selo
        self.assertEqual(r.returncode, 2)
        self.assertIn("forge-check brief mensagem", r.stderr)

    def test_executor_generico_com_brief_pede_selo(self):
        """BRIEF-EXECUTOR-SEM-PORTAO (0.43.2): o general-purpose, o fork e o claude que recebem um brief fazem o trabalho do especialista."""
        self.brief()
        prompt = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
        for tipo in ("general-purpose", "fork", "claude", ""):
            r = self.lancar(prompt, tipo=tipo)
            self.assertEqual(r.returncode, 2, f"{tipo}: {r.stderr}")
            self.assertIn("R-BRIEF", r.stderr)
            self.assertIn("sem selo", r.stderr)
        self.assertEqual(self.selar()[0], 0)
        for tipo in ("general-purpose", "fork", "claude"):
            self.assertEqual(self.lancar(prompt, tipo=tipo).returncode, 0, tipo)

    def test_todo_tipo_que_escreve_pede_selo_e_so_leitura_segue_livre(self):
        """D2 (0.44.0): sem brief, o executor genérico, o tipo de outro plugin e o desconhecido são barrados; a lista só de leitura passa."""
        self.brief()
        for tipo in ("general-purpose", "fork", "claude", "time:tech-lead", "forge-dev:aq", "outro", "statusline-setup"):
            r = self.lancar("procure onde o hook lê o selo e resuma", tipo=tipo)
            self.assertEqual(r.returncode, 2, tipo)
            self.assertIn("não cita o brief", r.stderr, tipo)
        for tipo in ("Explore", "Plan", "claude-code-guide", "web-fetch"):
            self.assertEqual(self.lancar("Leia docs/briefs/exemplo-node-backend-1.md e resuma.", tipo=tipo).returncode, 0, tipo)

    def test_brief_de_outro_plugin_casa_o_tipo_inteiro(self):
        """D2: o brief para `forge-dev:aq` dispara o `forge-dev:aq` (o prefixo de fora do Forge fica no nome), não o `outro:aq`."""
        self.brief()
        arq = self.proj / "docs/briefs/exemplo-node-backend-1.md"
        arq.write_text(arq.read_text(encoding="utf-8").replace("Agente destino: forge:node-backend", "Agente destino: forge-dev:aq"),
                       encoding="utf-8")
        self.gravar("docs/pedidos/exemplo.md", self.pedido() + "- 2026-01-02 10:00: brief selado docs/briefs/exemplo-node-backend-1.md "
                    + hashlib.sha256(arq.read_bytes()).hexdigest() + "\n")
        prompt = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
        self.assertEqual(self.lancar(prompt, tipo="forge-dev:aq").returncode, 0)
        for tipo in ("outro:aq", "aq", "forge:aq"):
            r = self.lancar(prompt, tipo=tipo)
            self.assertEqual(r.returncode, 2, tipo)
            self.assertIn("o brief é para `forge-dev:aq`", r.stderr, tipo)
        arq.write_text(arq.read_text(encoding="utf-8").replace("Agente destino: forge-dev:aq\n", ""), encoding="utf-8")
        self.gravar("docs/pedidos/exemplo.md", self.pedido() + "- 2026-01-02 10:01: brief selado docs/briefs/exemplo-node-backend-1.md "
                    + hashlib.sha256(arq.read_bytes()).hexdigest() + "\n")
        r = self.lancar(prompt, tipo="forge-dev:aq")  # sem `Agente destino:`, nenhum tipo casa (falha fechada)
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("o brief é para ``", r.stderr)

    def test_brief_vencido_so_avisa(self):
        """D3 (0.44.0): selado e depois vencido (decisão nova no pedido; a base trazida para a branch), o disparo segue com aviso."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        prompt = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("vencido", r.stderr + r.stdout)
        self.rodar("anotar", "--pedido", "exemplo", "--tipo", "decisao", "--confere", "mede", "--literal", "outra regra geral")
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("R-BRIEF: aviso: brief vencido", r.stderr)
        self.assertIn("corrigido: hash das decisões", r.stderr)
        self.assertIn("brief vencido", json.loads(r.stdout)["systemMessage"])
        self.assertEqual(self.selar()[0], 0)
        self.git("switch", "-q", "develop")
        self.gravar("bin/outro", "z\n")
        self.git("add", "bin/outro")
        self.commit("base anda")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-edit", "origin/develop")
        r = self.lancar(prompt)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("corrigido: Base-sha", r.stderr)

    def test_papel_do_forge_sem_o_prefixo_pede_selo(self):
        for tipo in ("node-backend", "tech-lead", "jarvis"):
            r = self.lancar("faça o recurso X", tipo=tipo)
            self.assertEqual(r.returncode, 2, f"{tipo}: {r.stderr}")
            self.assertIn("não cita o brief", r.stderr)
        r = self.lancar("faça X", tipo="conferente")  # o conferente sem o prefixo não vira especialista
        self.assertNotIn("não cita o brief", r.stderr)

    def test_brief_de_um_papel_nao_dispara_outro(self):  # M3 do review de segurança da 0.43.1
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        prompt = "Leia docs/briefs/exemplo-node-backend-1.md e execute."
        self.assertEqual(self.lancar(prompt, tipo="node-backend").returncode, 0)
        for tipo in ("forge:devops-engineer", "tech-lead"):
            r = self.lancar(prompt, tipo=tipo)
            self.assertEqual(r.returncode, 2, f"{tipo}: {r.stderr}")
            self.assertIn("o brief é para `node-backend`", r.stderr)

    def test_selo_forjado_com_outro_hash_nao_vale(self):
        self.brief()
        self.gravar("docs/pedidos/exemplo.md", self.pedido() + f"- 2026-01-02 10:00: brief selado docs/briefs/exemplo-node-backend-1.md {'d' * 64}\n")
        r = self.lancar("Leia docs/briefs/exemplo-node-backend-1.md")
        self.assertEqual(r.returncode, 2, r.stderr)


UNIDO = "anterior da mesma branch: escopo unido"


class Conferencia(Repositorio):
    """E23.17 (v0457): a conferência com `.github/...` declarado (a) e com volta na mesma branch (b)."""

    def conferir(self, etapa="codigo"):
        return self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", etapa, "--sem-gravar")

    def selar_copia(self, nome, trocas, selar=True):
        """Uma cópia do brief 1 com `trocas` (de -> para) gravada em docs/briefs/<nome>; selada pela ferramenta ou, com `selar=False`, pela
        linha do Histórico escrita à mão (o selo de um brief que a ferramenta recusaria, como o de outro pedido)."""
        texto = (self.proj / "docs/briefs/exemplo-node-backend-1.md").read_text(encoding="utf-8")
        for de, para in trocas.items():
            self.assertIn(de, texto)
            texto = texto.replace(de, para)
        arq = self.gravar(f"docs/briefs/{nome}", texto)
        if selar:
            rc, saida = self.selar(arq)
            self.assertEqual(rc, 0, saida)
        else:
            sha = hashlib.sha256(arq.read_bytes()).hexdigest()
            pedido = self.proj / "docs/pedidos/exemplo.md"
            pedido.write_text(self.pedido() + f"- 2026-01-01 09:30: brief selado docs/briefs/{nome} {sha}\n", encoding="utf-8")
        return arq

    def primeira_entrega_e_volta(self, antes_da_volta=None):
        """O brief 1 declara `bin/app, docs/notas/`; a volta (brief 2, mesma branch e pedido, o selo mais recente) declara só `volta.txt`."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        if antes_da_volta:
            antes_da_volta()
        self.entregar()
        self.gravar("volta.txt", "v\n")
        self.git("add", "volta.txt")
        self.commit("fix: volta")
        self.selar_copia("exemplo-node-backend-2.md", {"- arquivos: bin/app, docs/notas/": "- arquivos: volta.txt"})


class PontoInicial(Conferencia):
    """(a)"""

    def test_caminho_com_ponto_inicial_e_pontuacao_final(self):
        self.brief(arquivos="`.github/workflows/ci.yml`, ./bin/app; docs/notas/.")
        self.assertEqual(self.selar()[0], 0)
        self.gravar(".github/workflows/ci.yml", "on: push\n")
        self.entregar(".github")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        for linha in ('escopo: ok (declarado no brief: .github/workflows/ci.yml) ".github/workflows/ci.yml"',
                      'escopo: ok (declarado no brief: bin/app) "bin/app"', 'escopo: ok (declarado no brief: docs/notas/) "docs/notas/a.md"'):
            self.assertIn(linha, saida)


    def test_vv3_confere_o_caminho_com_o_ponto_inicial(self):
        """Volta 1 (segurança A3): o VV-3 do `brief selar` confere a escrita de `.github/...`, não de `github/...`."""
        secoes = {"Entregar": ["- arquivos: `.github/workflows/ci.yml`, ./bin/app; docs/notas/."]}
        self.assertEqual(fc.caminhos_do_entregar(secoes), [".github/workflows/ci.yml", "./bin/app", "docs/notas/"])


class VoltaNaMesmaBranch(Conferencia):
    """(b)"""

    def test_dois_briefs_da_mesma_branch_unem_o_escopo(self):
        self.primeira_entrega_e_volta()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"brief: {self.proj / 'docs/briefs/exemplo-node-backend-1.md'} (selado, {UNIDO})", saida)
        self.assertEqual(saida.count("exemplo-node-backend-2.md"), 1, saida)  # o brief da volta é o principal, não um anterior
        for linha in ('escopo: ok (declarado no brief: bin/app) "bin/app"', 'escopo: ok (declarado no brief: volta.txt) "volta.txt"'):
            self.assertIn(linha, saida)

    def test_pedido_com_id_diferente_do_nome_do_arquivo(self):
        """O `Pedido:` dos briefs é o `id:` do pedido, não o nome do arquivo."""
        self.primeira_entrega_e_volta()
        (self.proj / "docs/pedidos/exemplo.md").rename(self.proj / "docs/pedidos/outro-nome.md")  # `id: exemplo` num arquivo de outro nome
        rc, saida = self.rodar("entrega", "--pedido", "outro-nome", "--branch", "melhoria/x", "--etapa", "codigo", "--sem-gravar")
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: ok (declarado no brief: bin/app) "bin/app"', saida)

    def test_brief_de_outra_branch_nao_entra_na_uniao(self):
        self.primeira_entrega_e_volta()
        self.gravar("outra.txt", "o\n")
        self.git("add", "outra.txt")
        self.commit("feat: outra")
        self.selar_copia("exemplo-node-backend-3.md", {"Branch: melhoria/x": "Branch: melhoria/y", "- arquivos: bin/app, docs/notas/": "- arquivos: outra.txt"},
                         selar=False)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "outra.txt"', saida)
        self.assertNotIn("exemplo-node-backend-3.md", saida)

    def test_brief_de_outro_pedido_nao_entra_na_uniao(self):
        self.primeira_entrega_e_volta(lambda: self.selar_copia("outro-node-backend-1.md", {
            "Pedido: exemplo": "Pedido: outro", "- arquivos: bin/app, docs/notas/": "- arquivos: outra.txt"}, selar=False))
        self.gravar("outra.txt", "o\n")
        self.git("add", "outra.txt")
        self.commit("feat: outra")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "outra.txt"', saida)
        self.assertNotIn("outro-node-backend-1.md", saida)

    def test_outra_etapa_nao_une_os_briefs_de_codigo(self):
        self.primeira_entrega_e_volta()
        self.selar_copia("exemplo-node-backend-4.md", {"Etapa: codigo": "Etapa: qa", "- arquivos: bin/app, docs/notas/": "- arquivos: volta.txt"},
                         selar=False)
        rc, saida = self.conferir("qa")
        self.assertIn("exemplo-node-backend-4.md", saida)
        self.assertNotIn(UNIDO, saida)
        self.assertIn('escopo: fora do declarado no brief "bin/app"', saida)


class ParecerDoPortao(Conferencia):
    """E23.36 (d): na etapa codigo, o parecer de portão commitado na própria branch é anexo do portão; o de outra branch, não. Volta 1
    (segurança A1): só com o `commit:` ancorado no `Revisar-sha:` de um brief selado do portão, e sem veredito trocado no mesmo `commit:`."""

    ETAPA = {"reviews": "review", "devops": "review", "qa": "qa", "security": "seguranca"}  # o brief real do devops é `Etapa: review`
    PAPEL = {"reviews": "tech-lead", "devops": "devops-engineer", "qa": "qa-engineer", "security": "security-engineer"}

    def selar_portao(self, etapa, revisado, trocas=None, papel="tech-lead"):
        """Um brief selado do portão `etapa` desta branch e pedido para o `papel`, com `Revisar-sha: <revisado>` (o registro do Jarvis)."""
        self.n_portao = getattr(self, "n_portao", 10) + 1
        self.selar_copia(f"exemplo-portao-{self.n_portao}.md", {"Etapa: codigo": f"Revisar-sha: {revisado}\nEtapa: {etapa}",
                                                                "Agente destino: forge:node-backend": f"Agente destino: forge:{papel}",
                                                                **(trocas or {})}, selar=False)

    def commitar_parecer(self, pasta, tipo, branch="melhoria/x", pedido="exemplo", revisado=None, parecer="aprovado", selar=True, nome="x"):
        """O parecer do portão sobre o head de agora (`revisado`, o `commit:` do frontmatter) em docs/<pasta>/<nome>.md, commitado na
        branch; com `selar`, o brief selado do portão que o ancora."""
        rel, revisado = f"docs/{pasta}/{nome}.md", revisado or self.git("rev-parse", "HEAD")
        if selar:
            self.selar_portao(self.ETAPA[pasta], revisado, papel=self.PAPEL[pasta])
        self.gravar(rel, f"---\ntipo: {tipo}\ncontrato: 1\npedido: {pedido}\nbranch: {branch}\ncommit: {revisado}\nparecer: {parecer}\n---\n# parecer\n")
        self.git("add", rel)
        self.commit(f"docs({pasta}): parecer")
        return rel

    def entrega_com_parecer(self, **kw):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        return self.commitar_parecer("reviews", "review", **kw)

    def assert_fora(self, rel="docs/reviews/x.md"):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'escopo: fora do declarado no brief "{rel}"', saida)

    def test_parecer_da_propria_branch_e_anexo_do_portao(self):
        self.entrega_com_parecer()
        self.commitar_parecer("devops", "revisao-devops")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de tech-lead da própria branch) "docs/reviews/x.md"', saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de devops da própria branch) "docs/devops/x.md"', saida)

    def test_parecer_de_outra_branch_segue_fora(self):
        self.entrega_com_parecer(branch="melhoria/y")
        self.assert_fora()

    def test_parecer_de_outro_pedido_segue_fora(self):
        self.entrega_com_parecer(pedido="outro")
        self.assert_fora()

    def test_tipo_de_outra_pasta_segue_fora(self):
        """QA A1: o `tipo:` do frontmatter é o da pasta (um parecer de QA gravado em docs/reviews/ não é anexo do review)."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.git("rev-parse", "HEAD")
        self.commitar_parecer("reviews", "qa", revisado=revisado)
        self.assert_fora()

    def test_parecer_sem_veredito_valido_segue_fora(self):
        """QA A1: o `parecer:` é aprovado ou reprovado; outro valor não faz anexo."""
        self.entrega_com_parecer(parecer="pendente")
        self.assert_fora()

    def test_commit_sem_brief_selado_do_portao_segue_fora(self):
        """Segurança A1 (S1, parecer novo): o `commit:` é um commit da branch, mas nenhum brief selado do portão o tem como Revisar-sha."""
        self.entrega_com_parecer(selar=False)
        self.assert_fora()

    def test_brief_do_portao_de_outra_etapa_ou_pedido_nao_ancora(self):
        """O brief selado com o mesmo Revisar-sha, mas de outra etapa (qa para um parecer de review) ou de outro pedido, não ancora."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.git("rev-parse", "HEAD")
        self.selar_portao("qa", revisado)
        self.selar_portao("review", revisado, {"Pedido: exemplo": "Pedido: outro"})
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False)
        self.assert_fora()

    def test_veredito_trocado_no_mesmo_commit_segue_fora(self):
        """Segurança A1 (S1, veredito trocado): o reprovado do revisor vira aprovado sem mudar o `commit:`; com nova revisão (outro
        `commit:` e o brief selado dele), o aprovado é anexo."""
        self.entrega_com_parecer(parecer="reprovado")
        revisado = self.git("rev-parse", "HEAD~1")
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False)
        self.assert_fora()
        self.commitar_parecer("reviews", "review")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de tech-lead da própria branch) "docs/reviews/x.md"', saida)

    def test_git_que_falha_conta_como_veredito_trocado(self):
        """Falha fechada: sem o `rev-list` do intervalo (aqui, um `de` que não existe), o veredito conta como trocado."""
        self.entrega_com_parecer()
        revisado = self.git("rev-parse", "HEAD~1")
        self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))
        self.assertTrue(fc.veredito_trocado(self.proj, "0" * 40, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))

    def trocado_com_git_que_falha(self, subcomando):
        """O veredito de um parecer válido (sem troca) com o `subcomando` do git falhando e os outros reais."""
        self.entrega_com_parecer()
        revisado, git_real = self.git("rev-parse", "HEAD~1"), fc.git

        def git_que_falha(raiz, *args, **kw):
            return (128, "") if args[0] == subcomando else git_real(raiz, *args, **kw)
        self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))
        with mock.patch.object(fc, "git", git_que_falha):
            return fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review")

    def test_ls_tree_que_falha_conta_como_veredito_trocado(self):
        """Volta 2 (segurança A5), falha fechada: o `ls-tree` de uma versão da pasta que falha conta como trocado."""
        self.assertTrue(self.trocado_com_git_que_falha("ls-tree"))

    def test_rev_list_que_falha_conta_como_veredito_trocado(self):
        """Falha fechada: o `rev-list` do intervalo que falha conta como trocado, com o `ls-tree` de `de` respondendo."""
        self.assertTrue(self.trocado_com_git_que_falha("rev-list"))

    def test_grep_que_falha_conta_como_veredito_trocado(self):
        """VEREDITO-TROCADO-LENTO, falha fechada: o `git grep` que filtra as versões e falha conta como trocado."""
        self.assertTrue(self.trocado_com_git_que_falha("grep"))

    def test_so_le_a_versao_que_cita_o_sha_revisado(self):
        """VEREDITO-TROCADO-LENTO: um `git show` por arquivo da pasta levava 80 s no Forge; só a versão que cita o sha é lida."""
        self.entrega_com_parecer()
        revisado, git_real, lidos = self.git("rev-parse", "HEAD~1"), fc.git, []
        self.gravar("docs/reviews/outro.md", "---\ntipo: review\ncommit: " + "a" * 40 + "\n---\n")
        self.git("add", "docs/reviews/outro.md")
        self.commit("docs(reviews): outro")

        def git_que_conta(raiz, *args, **kw):
            lidos.extend(args[1:2] if args[0] == "show" else [])
            return git_real(raiz, *args, **kw)
        with mock.patch.object(fc, "git", git_que_conta):
            self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))
        self.assertTrue(lidos)
        self.assertEqual({n.split(":", 1)[1] for n in lidos}, {"docs/reviews/x.md"})

    def test_veredito_trocado_em_outro_arquivo_da_pasta_segue_fora(self):
        """Volta 2 (segurança A5, S3): o review reprovado em x.md e um y.md aprovado com o mesmo `commit:` ancorado; y.md não é anexo."""
        self.entrega_com_parecer(parecer="reprovado")
        self.commitar_parecer("reviews", "review", revisado=self.git("rev-parse", "HEAD~1"), selar=False, nome="y")
        self.assert_fora("docs/reviews/y.md")

    def test_x_apagado_e_y_aprovado_no_mesmo_commit_segue_fora(self):
        """Volta 2 (segurança A5): o autor apaga o x.md reprovado e cria o y.md aprovado no mesmo commit; a versão anterior conta."""
        self.entrega_com_parecer(parecer="reprovado")
        self.git("rm", "-q", "docs/reviews/x.md")
        self.commitar_parecer("reviews", "review", revisado=self.git("rev-parse", "HEAD~1"), selar=False, nome="y")
        self.assertEqual(self.git("show", "--no-renames", "--name-status", "--format=", "HEAD").split(), ["D", "docs/reviews/x.md", "A", "docs/reviews/y.md"])
        self.assert_fora("docs/reviews/y.md")

    def test_parecer_de_outra_branch_na_pasta_nao_troca_o_veredito(self):
        """Volta 2 (segurança A5): o mesmo `commit:` com outro veredito, mas de outra branch, não é troca do parecer desta."""
        self.entrega_com_parecer()
        revisado = self.git("rev-parse", "HEAD~1")
        self.commitar_parecer("reviews", "review", branch="melhoria/y", revisado=revisado, parecer="reprovado", selar=False, nome="y")
        self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))

    def test_arquivo_sem_frontmatter_na_pasta_nao_quebra_o_veredito(self):
        """O arquivo da pasta sem frontmatter não é parecer: não troca o veredito nem quebra a busca."""
        self.entrega_com_parecer()
        revisado = self.git("rev-parse", "HEAD~1")
        self.gravar("docs/reviews/notas.md", "# notas sem frontmatter\n")
        self.git("add", "docs/reviews/notas.md")
        self.commit("docs(reviews): notas")
        self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado", "melhoria/x", "review"))

    def forjar_em_ramo_lateral(self, revisor_primeiro):
        """Volta 3 (segurança A7, S6): o revisor commita x.md reprovado sobre o head revisado; um ramo lateral desse head traz y.md
        aprovado com o mesmo `commit:`, e o merge --no-ff apaga o x.md. Com `revisor_primeiro`, o commit do revisor é o primeiro pai."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.git("rev-parse", "HEAD")
        self.commitar_parecer("reviews", "review", revisado=revisado, parecer="reprovado")
        self.git("switch", "-q", "-c", "lado", revisado)
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False, nome="y")
        destino, outro = ("melhoria/x", "lado") if revisor_primeiro else ("lado", "melhoria/x")
        self.git("switch", "-q", destino)
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-commit", "--no-ff", outro)
        self.git("rm", "-q", "-f", "docs/reviews/x.md")
        self.commit("merge do ramo lateral")
        if not revisor_primeiro:
            self.git("switch", "-q", "melhoria/x")
            self.git("merge", "-q", "--ff-only", "lado")
        self.assert_fora("docs/reviews/y.md")

    def test_merge_de_ramo_lateral_que_apaga_o_reprovado_segue_fora(self):
        self.forjar_em_ramo_lateral(revisor_primeiro=True)

    def test_merge_com_o_ramo_lateral_como_primeiro_pai_segue_fora(self):
        self.forjar_em_ramo_lateral(revisor_primeiro=False)

    def test_parecer_em_subpasta_do_portao_com_o_reprovado_apagado_segue_fora(self):
        """Volta 3 (segurança A8, S7): x.md reprovado apagado num commit; docs/reviews/sub/y.md aprovado com o mesmo `commit:` busca
        o veredito na pasta do portão inteira, não só na subpasta dele."""
        self.entrega_com_parecer(parecer="reprovado")
        revisado = self.git("rev-parse", "HEAD~1")
        self.git("rm", "-q", "docs/reviews/x.md")
        self.commit("docs(reviews): apaga x")
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False, nome="sub/y")
        self.assert_fora("docs/reviews/sub/y.md")

    def portao_de_um_papel(self, papel, pasta, tipo):
        """O brief selado de `Etapa: review` só para o `papel` e o parecer de `pasta` com o mesmo Revisar-sha, sem brief próprio."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.git("rev-parse", "HEAD")
        self.selar_portao("review", revisado, papel=papel)
        self.commitar_parecer(pasta, tipo, revisado=revisado, selar=False)

    def test_brief_do_review_nao_ancora_o_devops(self):
        """Volta 2 (review A4): review e devops têm a mesma `Etapa: review`; o `Agente destino:` separa o portão de cada um."""
        self.portao_de_um_papel("tech-lead", "devops", "revisao-devops")
        self.assert_fora("docs/devops/x.md")

    def test_brief_do_devops_nao_ancora_o_review(self):
        self.portao_de_um_papel("devops-engineer", "reviews", "review")
        self.assert_fora("docs/reviews/x.md")

    def test_parecer_sem_frontmatter_segue_fora(self):
        self.entrega_com_parecer()
        self.gravar("docs/reviews/x.md", "# parecer sem frontmatter\n")
        self.git("add", "docs/reviews/x.md")
        self.commit("docs(reviews): sem frontmatter")
        self.assert_fora()


class VocabularioDaEtapaDoPortao(unittest.TestCase):
    """FIXTURE-ETAPA-FORA-VOCABULARIO: a `Etapa:` que o fixture sela para cada pasta de parecer é a do `ETAPA_DO_PORTAO` para o tipo
    daquela pasta. Um fixture com etapa fora do vocabulário (`Etapa: devops` à mão) mascarou a regressão A4 da E23.36."""

    def test_fixture_sela_a_etapa_do_vocabulario(self):
        tipo_da_pasta = {pasta.removeprefix("docs/"): tipo for tipo, (pasta, _) in fc.PASTA_E_REGRA.items()}
        self.assertEqual(set(ParecerDoPortao.ETAPA), set(tipo_da_pasta))
        for pasta, etapa in ParecerDoPortao.ETAPA.items():
            with self.subTest(pasta=pasta):
                self.assertEqual(etapa, fc.ETAPA_DO_PORTAO[tipo_da_pasta[pasta]])


class JanelaDaEntrega(Conferencia):
    """MP1311 (item 1, com MP1103-D-8): a janela da conferência desconta o parecer dos outros portões em toda etapa de código (o caso do
    PR 530) e aceita `--desde` no commit do autor que os portões revisaram (o `Revisar-sha:` de brief selado do portão da branch)."""

    ETAPA, PAPEL = ParecerDoPortao.ETAPA, ParecerDoPortao.PAPEL
    selar_portao, commitar_parecer = ParecerDoPortao.selar_portao, ParecerDoPortao.commitar_parecer

    def entrega_revisada(self):
        """A entrega conferida (linha gravada) e o parecer de review sobre ela; devolve o head da entrega."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        head = self.entregar()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.commitar_parecer("reviews", "review", revisado=head)
        return head

    def test_parecer_de_outro_portao_na_etapa_qa_e_anexo_do_portao(self):
        head = self.entrega_revisada()
        self.commitar_parecer("security", "revisao-seguranca", revisado=head)
        self.commitar_parecer("qa", "qa", revisado=head)
        rc, saida = self.conferir("qa")
        self.assertEqual(rc, 0, saida)
        for papel, rel in (("tech-lead", "reviews"), ("seguranca", "security"), ("qa", "qa")):
            self.assertIn(f'escopo: ok (anexo do portão: parecer de {papel} da própria branch) "docs/{rel}/x.md"', saida)

    def conferir_desde(self, desde):
        return self.rodar("entrega", "exemplo", "--branch", "melhoria/x", "--base", "develop", "--base-sha", self.base,
                          "--etapa", "codigo", "--desde", desde)

    def volta(self):
        self.gravar("volta.txt", "v\n")
        self.git("add", "volta.txt")
        return self.commit("fix: volta")

    def test_desde_no_commit_revisado_pelo_portao_vale(self):
        head = self.entrega_revisada()
        (self.proj / "docs/pedidos/exemplo.md").write_text(self.pedido().replace(f"entrega conferida {head}", "aberto"), encoding="utf-8")
        self.volta()
        rc, saida = self.conferir_desde(head)
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {head}..", saida)
        self.assertIn("base: commit do autor revisado pelo portão (Revisar-sha de brief selado)", saida)
        self.assertNotIn('"bin/app"', saida)
        self.assertNotIn("sem conferência anterior", saida)

    def test_desde_em_commit_nao_revisado_segue_recusado(self):
        self.entrega_revisada()
        parecer = self.git("rev-parse", "HEAD")
        self.volta()
        rc, saida = self.conferir_desde(parecer)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_desde_revisado_fora_da_branch_segue_recusado(self):
        """O `Revisar-sha:` de um commit que não é ancestral do head (outra linha de história) não vira Desde."""
        self.entrega_revisada()
        self.git("switch", "-q", "-c", "melhoria/lado", "develop")
        self.gravar("lado.txt", "l\n")
        self.git("add", "lado.txt")
        lado = self.commit("feat: lado")
        self.git("switch", "-q", "melhoria/x")
        self.selar_portao("review", lado)
        rc, saida = self.conferir_desde(lado)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_desde_revisado_na_base_segue_recusado(self):
        """O `Revisar-sha:` que é ancestral do Base-sha (um commit da base, não do autor) não vira Desde."""
        self.entrega_revisada()
        self.selar_portao("review", self.base)
        rc, saida = self.conferir_desde(self.base)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde sem conferência anterior", saida)

    def test_desde_revisado_com_pedido_na_entrega_segue_recusado(self):
        head = self.entrega_revisada()
        self.gravar("docs/pedidos/outro.md", "x\n")
        self.git("add", "docs/pedidos/outro.md")
        self.commit("docs: pedido na entrega")
        rc, saida = self.conferir_desde(head)
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: --desde gravado na própria entrega", saida)


class MatrizDaBuscaDoVeredito(ParecerDoPortao):
    """Volta 4 (segurança A10, cartão AR-BUSCA-VEREDITO): A5, A7, A8 e A10 são uma busca só, a do veredito trocado, e a matriz das
    dimensões dela fecha a família. O revisor commita docs/reviews/x.md reprovado sobre o head revisado; o autor forja um parecer
    aprovado com o mesmo `commit:`. Dimensões: janela (Desde no Base-sha; Desde no commit do revisor; Desde depois de uma volta
    conferida que tirou o x.md da pasta, a S8), topologia (linear; merge lateral nas duas ordens; octopus nas duas ordens), pasta (raiz
    do portão, subpasta, pasta parecida fora) e nome (outro arquivo, o mesmo arquivo, `git mv`). Toda célula recusa o forjado. As
    células são a janela cruzada com cada outra dimensão, com as demais no valor de partida (linear, raiz, outro arquivo)."""

    JANELAS = ("base_sha", "desde_no_revisor", "volta_anterior_apagada")
    TOPOLOGIAS = ("linear", "lateral_revisor_primeiro", "lateral_forjado_primeiro", "octopus_revisor_primeiro", "octopus_forjado_primeiro")
    PASTAS = {"raiz": "docs/reviews/y.md", "subpasta": "docs/reviews/sub/y.md", "parecida_fora": "docs/reviewsX/y.md"}
    NOMES = ("outro", "mesmo", "git_mv")

    def aprovar(self, rel, revisado):
        self.gravar(rel, f"---\ntipo: review\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {revisado}\nparecer: aprovado\n---\n# p\n")
        self.git("add", rel)

    def tirar_x(self):
        """O x.md reprovado sai da pasta (apagado), se ainda estiver na árvore."""
        if (self.proj / "docs/reviews/x.md").exists():
            self.git("rm", "-q", "-f", "docs/reviews/x.md")

    def janela(self, janela):
        """O head revisado, o x.md reprovado do revisor e a janela; devolve (revisado, Desde ou None para o Base-sha)."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.git("rev-parse", "HEAD")
        self.commitar_parecer("reviews", "review", revisado=revisado, parecer="reprovado")
        if janela == "base_sha":
            return revisado, None
        if janela == "desde_no_revisor":
            return revisado, self.git("rev-parse", "HEAD")
        self.git("mv", "docs/reviews/x.md", "docs/notas/x.md")  # a volta 2 tira o x.md da pasta junto com uma mudança declarada
        self.gravar("docs/notas/b.md", "b\n")
        self.git("add", "docs/notas/b.md")
        return revisado, self.commit("volta 2")

    def forjar(self, revisado, topologia, rel, nome):
        if topologia == "linear":
            if nome == "git_mv":
                origem = "docs/reviews/x.md" if (self.proj / "docs/reviews/x.md").exists() else "docs/notas/x.md"
                (self.proj / rel).parent.mkdir(parents=True, exist_ok=True)
                self.git("mv", origem, rel)
            elif nome == "outro":
                self.tirar_x()
            self.aprovar(rel, revisado)
            self.commit("forja")
            return
        self.git("switch", "-q", "-c", "lado1", revisado)
        self.aprovar(rel, revisado)
        self.commit("forja no ramo lateral")
        ramos = ["lado1"]
        if topologia.startswith("octopus"):
            self.git("switch", "-q", "-c", "lado2", revisado)
            self.gravar("docs/notas/c.md", "c\n")
            self.git("add", "docs/notas/c.md")
            self.commit("nota")
            ramos.append("lado2")
        revisor_primeiro = topologia.endswith("revisor_primeiro")
        self.git("switch", "-q", "melhoria/x" if revisor_primeiro else "lado1")
        outros = ramos if revisor_primeiro else ramos[1:] + ["melhoria/x"]
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-commit", "--no-ff", *outros)
        self.tirar_x()
        self.commit("merge")
        if not revisor_primeiro:
            self.git("switch", "-q", "melhoria/x")
            self.git("merge", "-q", "--ff-only", "lado1")

    def celula(self, janela, topologia="linear", pasta="raiz", nome="outro"):
        rel = "docs/reviews/x.md" if nome == "mesmo" else self.PASTAS[pasta]
        revisado, desde = self.janela(janela)
        self.forjar(revisado, topologia, rel, nome)
        if desde:
            pedido = self.proj / "docs/pedidos/exemplo.md"
            pedido.write_text(self.pedido() + f"- 2026-01-01 12:00: entrega conferida {desde}\n", encoding="utf-8")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'escopo: fora do declarado no brief "{rel}"', saida)
        self.assertIn(f"intervalo: {desde or self.base}..", saida)

    def test_s8_volta_anterior_tirou_o_reprovado_da_pasta(self):
        """S8 (segurança A10): a volta 2 tira o x.md da pasta e é conferida (Desde D); a volta 3 cria o y.md aprovado com o `commit:`
        do revisado. A busca começa no Base-sha, não no Desde."""
        self.celula("volta_anterior_apagada")

    def test_janela_por_topologia(self):
        for janela in self.JANELAS:
            for topologia in self.TOPOLOGIAS:
                with self.subTest(janela=janela, topologia=topologia):
                    self.setUp()
                    self.celula(janela, topologia=topologia)

    def test_janela_por_pasta(self):
        for janela in self.JANELAS:
            for pasta in self.PASTAS:
                with self.subTest(janela=janela, pasta=pasta):
                    self.setUp()
                    self.celula(janela, pasta=pasta)

    def test_janela_por_nome(self):
        for janela in self.JANELAS:
            for nome in self.NOMES:
                with self.subTest(janela=janela, nome=nome):
                    self.setUp()
                    self.celula(janela, nome=nome)


class MergeDaBaseDepoisDoBrief(Conferencia):
    """E23.36 (e): com a develop trazida por merge, o intervalo parte do merge-base com a origin/develop; a conferida de outra branch
    que veio com ela não é Desde, e o que a develop mudou não é escopo."""

    def develop_anda(self, *conteudos):
        """A develop ganha um commit por conteúdo de `agents/outro.md` (outro lote) no `origin`; devolve os shas."""
        self.git("switch", "-q", "develop")
        shas = []
        for texto in conteudos:
            self.gravar("agents/outro.md", texto)
            self.git("add", "agents/outro.md")
            shas.append(self.commit("outro lote"))
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        return shas

    def ancorar(self, base_sha, nome="exemplo-outra-1.md"):
        """Um brief selado de outra branch com `Base-sha: <base_sha>`: o registro do Jarvis que ancora o merge-base (volta 1, segurança A2)."""
        self.selar_copia(nome, {"Branch: melhoria/x": "Branch: melhoria/y", f"Base-sha: {self.base}": f"Base-sha: {base_sha}"}, selar=False)

    def mesclar_develop(self):
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge da develop", "origin/develop")

    def entrega_e_merge(self, ancorar=True):
        """A entrega, a develop com a conferida de outra branch do mesmo pedido (o 1.o commit), o brief selado depois com o Base-sha da
        develop (com `ancorar`) e o merge dela na branch."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        outra, ponta = self.develop_anda("a\n", "a\nb\n")
        (self.proj / "docs/pedidos/exemplo.md").write_text(self.pedido() + f"- 2026-01-01 10:00: entrega conferida {outra}\n", encoding="utf-8")
        if ancorar:
            self.ancorar(ponta)
        self.mesclar_develop()
        return self.git("rev-parse", "refs/remotes/origin/develop")

    def test_conferida_trazida_pela_develop_nao_e_desde(self):
        ponto = self.entrega_e_merge()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"base: merge-base {ponto[:12]} com a", saida)
        self.assertIn(f"intervalo: {ponto}..", saida)
        self.assertIn(f"commits: 2 em {ponto[:12]}", saida)
        self.assertNotIn("agents/outro.md", saida)

    def test_arquivo_da_develop_mudado_depois_do_merge_segue_fora(self):
        self.entrega_e_merge()
        self.gravar("agents/outro.md", "a\nb\nda branch\n")
        self.git("add", "agents/outro.md")
        self.commit("feat: muda o da develop")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "agents/outro.md"', saida)

    def test_base_sha_fora_da_branch_segue_reprovado(self):
        """O Base-sha adiante do merge-base (a develop andou e a branch não a trouxe) não vira o merge-base: segue fora da branch."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        adiante, = self.develop_anda("a\n")
        self.selar_copia("exemplo-node-backend-2.md", {f"Base-sha: {self.base}": f"Base-sha: {adiante}"}, selar=False)
        self.ancorar(adiante)  # o merge-base (o Base-sha antigo) está ancorado: só a guarda do "adiante do Base-sha" o recusa
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: Base-sha fora da branch", saida)
        self.assertNotIn("base: merge-base", saida)

    def test_brief_selado_sem_base_sha_nao_conta_como_ancora(self):
        """O brief selado mais novo sem `Base-sha:` legível fica fora das âncoras (sem quebrar a conferência); vale o da develop."""
        ponto = self.entrega_e_merge()
        self.selar_copia("exemplo-outra-3.md", {"Branch: melhoria/x": "Branch: melhoria/y", f"Base-sha: {self.base}": "Base-sha: ausente"},
                         selar=False)
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"base: merge-base {ponto[:12]} com a", saida)

    def test_merge_base_sem_ancora_fica_o_base_sha(self):
        """Volta 1 (segurança A2): sem brief selado depois do da entrega, o merge-base não tem âncora do Jarvis e fica o Base-sha;
        FILTROS-L08-G2-ORIGIN-LOCAL: o filtro G2 também não tira o que a develop sem âncora trouxe. ENTREGA-MERGE-DA-DEVELOP: sai pelo
        merge-base com a develop do `git ls-remote origin` (o remoto, não a ref local), com o blob igual ao dele."""
        self.entrega_e_merge(ancorar=False)
        rc, saida = self.conferir()
        self.assertNotIn("base: merge-base", saida)
        # v047 E1.185 (CONFERIDA-POR-BRANCH): a conferida trazida, já na develop, não vira Desde; o intervalo é o do Base-sha
        self.assertIn(f"intervalo: {self.base}..", saida)
        self.assertIn("base: Base-sha do brief (sem conferida na branch)", saida)
        self.assertIn("escopo: integração da base pelo remoto (1 arquivo(s) iguais ao merge-base", saida)
        self.assertNotIn("agents/outro.md", saida)
        self.assertEqual(rc, 0, saida)

    def reprova_com(self, *nomes):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        for nome in nomes:
            self.assertIn(f'escopo: fora do declarado no brief "{nome}"', saida)
        return saida

    def test_sem_rede_o_que_a_develop_trouxe_segue_no_escopo(self):
        """ENTREGA-MERGE-DA-DEVELOP: sem o `git ls-remote` (origin que não responde), a ref local não vale: nada sai do escopo."""
        self.entrega_e_merge(ancorar=False)
        self.git("remote", "set-url", "origin", str(self.tmp / "nao-existe.git"))
        self.assertNotIn("pelo remoto", self.reprova_com("agents/outro.md"))

    def test_o_que_o_autor_mudou_por_cima_da_develop_segue_dele(self):
        self.entrega_e_merge(ancorar=False)
        self.gravar("agents/outro.md", "a\nb\ndo autor\n")
        self.git("add", "agents/outro.md")
        self.commit("feat: por cima da develop")
        self.reprova_com("agents/outro.md")

    def test_merge_de_fora_da_develop_segue_no_escopo(self):
        """O merge de uma branch que não está na develop do remoto, mesmo com a `origin/develop` local reescrita para ela."""
        self.entrega_e_merge(ancorar=False)
        self.git("switch", "-q", "-c", "lateral", self.base)
        self.gravar("fora.txt", "f\n")
        self.git("add", "fora.txt")
        lateral = self.commit("feat: fora da develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("update-ref", "refs/remotes/origin/develop", lateral)
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge lateral", lateral)
        self.reprova_com("fora.txt")

    def test_aceite_do_usuario_vindo_da_develop_segue_no_escopo(self):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.git("switch", "-q", "develop")
        self.gravar("docs/security/aceites/a.md", "aceite\n")
        self.git("add", "docs/security/aceites/a.md")
        self.commit("aceite")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.mesclar_develop()
        self.reprova_com("docs/security/aceites/a.md")

    def test_ref_local_sem_o_merge_nao_consulta_o_remoto(self):
        """Com a `origin/develop` local de volta ao Base-sha, o merge da base não aparece por ela: nada sai (sem rede). Sem a conferida
        de outra branch (`entrega_e_merge`), que com a ref local recuada viraria o Desde e tiraria o arquivo pelos desfeitos."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.develop_anda("a\n")
        self.mesclar_develop()
        self.git("update-ref", "refs/remotes/origin/develop", self.base)
        self.reprova_com("agents/outro.md")

    def test_o_que_a_branch_mudou_e_o_merge_devolveu_a_develop_segue_a_vista(self):
        """Segurança A1: o arquivo da entrega conferida que o merge trocou pelo da develop (`-X theirs`) segue no escopo."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        conferida = self.entregar()
        (self.proj / "docs/pedidos/exemplo.md").write_text(self.pedido() + f"- 2026-01-01 10:00: entrega conferida {conferida}\n",
                                                           encoding="utf-8")
        self.git("switch", "-q", "develop")
        self.gravar("bin/app", "x\nda develop\n")
        self.git("add", "bin/app")
        self.commit("outro lote")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-X", "theirs", "-m", "merge", "origin/develop")
        saida = self.conferir()[1]
        self.assertIn('escopo: ok (declarado no brief: bin/app) "bin/app"', saida)
        self.assertNotIn("pelo remoto", saida)

    def test_develop_remota_sem_fetch_nao_tira_nada(self):
        """O commit da develop do remoto ainda não buscado: sem merge-base com ele, nada sai, nem o arquivo que o autor apagou."""
        self.entrega_e_merge(ancorar=False)
        self.git("rm", "-q", "KANBAN.md")
        self.commit("chore: apaga o quadro")
        outro = self.tmp / "outro"
        self.git_em(self.tmp, "clone", "-q", "-b", "develop", str(self.tmp / "origem.git"), "outro")
        (outro / "novo.txt").write_text("n\n", encoding="utf-8")
        self.git_em(outro, "add", "novo.txt")
        self.git_em(outro, "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "develop anda")
        self.git_em(outro, "push", "-q", "origin", "develop")
        self.reprova_com("KANBAN.md", "agents/outro.md")

    def selado_e_entregue(self):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        return self.entregar()

    def test_ref_homonima_por_cauda_no_remoto_nao_e_a_develop(self):
        """Segurança A1 (S1): `refs/heads/a/refs/heads/develop` casa o padrão do `ls-remote` e vem antes; com a `origin/develop` local
        reescrita para ela, o arquivo fora do brief segue no escopo."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.gravar("agents/fora.md", "fora do brief\n")
        self.git("add", "agents/fora.md")
        forjado = self.commit("feat: fora do brief")
        self.git("push", "-q", "origin", f"{forjado}:refs/heads/a/refs/heads/develop")
        self.entregar()
        self.git("update-ref", "refs/remotes/origin/develop", forjado)
        self.assertNotIn("pelo remoto", self.reprova_com("agents/fora.md"))

    def test_remoto_da_branch_so_aceita_o_nome_exato(self):
        """Segurança A1, também nos usos antigos (`estado_do_commit`, `aviso_de_review_proprio`): a linha de nome exato, ou nenhuma."""
        forjado, real = "a" * 40, "b" * 40
        for saida, esperado in ((f"{forjado}\trefs/heads/a/refs/heads/develop\n{real}\trefs/heads/develop\n", real),
                                (f"{forjado}\trefs/heads/a/refs/heads/develop\n", None)):
            with mock.patch.object(fc, "git", lambda raiz, *args, _s=saida: (0, _s)):
                self.assertEqual(fc.remoto_da_branch(self.proj, "develop"), (esperado, True), saida)

    def lateral_na_develop(self, rel, fraco, forte):
        """Um PR lateral mesclado na develop com `--no-ff`: X (versão intermediária; `fraco` None apaga) e a correção; o autor mescla X."""
        self.git("switch", "-q", "-c", "pr", self.base)
        if fraco is None:
            self.git("rm", "-q", rel)
        else:
            self.gravar(rel, fraco)
            self.git("add", rel)
        x = self.commit("pr: versão intermediária")
        self.gravar(rel, forte)
        self.git("add", rel)
        self.commit("pr: correção pedida no review")
        self.git("switch", "-q", "develop")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge pr", "pr")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge x", x)
        return x

    def test_merge_base_fora_da_primeira_linha_de_pais_nao_tira_nada(self):
        """Segurança A2 (S2): o autor mescla o commit intermediário de um PR lateral já na develop; a versão que a develop nunca teve na
        ponta segue no escopo."""
        self.selado_e_entregue()
        x = self.lateral_na_develop("agents/guarda.md", "fraco\n", "forte\n")
        self.assertEqual(self.git("merge-base", "origin/develop", "HEAD"), x)
        self.reprova_com("agents/guarda.md")

    def test_arquivo_apagado_pelo_intermediario_segue_no_escopo(self):
        """Segurança A2 (S3): o intermediário apaga o quadro e a correção o devolve; o merge do intermediário não tira a remoção."""
        self.selado_e_entregue()
        self.lateral_na_develop("KANBAN.md", None, "# Quadro\nnovo\n")
        self.reprova_com("KANBAN.md")

    def test_arquivo_ausente_nos_dois_lados_segue_no_escopo(self):
        """Segurança A3: a develop apaga o quadro na 1.a linha de pais e o autor a mescla; ausente no head e no merge-base não é igual."""
        self.selado_e_entregue()
        self.git("switch", "-q", "develop")
        self.git("rm", "-q", "KANBAN.md")
        self.commit("chore: apaga o quadro")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.mesclar_develop()
        self.reprova_com("KANBAN.md")

    def test_merge_cruzado_com_dois_merge_bases_nao_tira_nada(self):
        """Segurança A2: a branch mescla a develop (d1) e a develop mescla o commit do autor (b1); `merge-base --all` dá d1 e b1, e d1,
        o mais novo e na 1.a linha de pais, viria primeiro: com mais de um merge-base, nada sai."""
        b1 = self.selado_e_entregue()
        self.env["GIT_COMMITTER_DATE"] = "2030-01-01T00:00:00Z"  # d1 mais novo que b1: a ordem do `merge-base --all` fica fixa
        d1, = self.develop_anda("a\n")
        del self.env["GIT_COMMITTER_DATE"]
        self.mesclar_develop()
        head = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "develop")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-m", "merge b1", b1)
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.assertEqual(self.git("merge-base", "--all", "origin/develop", head).split(), [d1, b1])
        self.assertEqual(fc.vindos_do_remoto_da_base(self.proj, "develop", self.base, head, {"agents/outro.md"}), set())

    def test_brief_selado_antes_do_da_entrega_nao_ancora(self):
        """A âncora é o Base-sha de brief selado MAIS NOVO que o da entrega; o selado antes dele, mesmo com a develop adiante, não vale."""
        ponta, = self.develop_anda("a\n")
        self.brief()
        self.ancorar(ponta)
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.mesclar_develop()
        _, saida = self.conferir()
        self.assertNotIn("base: merge-base", saida)

    def test_origin_develop_reescrita_nao_move_o_intervalo(self):
        """Volta 1 (segurança A2, sonda S2): a `origin/develop` reescrita (`git update-ref`) para um commit da branch põe o merge-base
        adiante do código fora do declarado; sem âncora (nem com a da develop real), fica o Base-sha e o arquivo segue fora. O fora.txt
        muda duas vezes: o filtro L08 (commit já na base, igual nela) só tira o segundo, e só o merge-base movido o esconderia."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        ponta, = self.develop_anda("a\n")
        self.ancorar(ponta)
        for texto in ("f\n", "g\n"):
            self.gravar("fora.txt", texto)
            self.git("add", "fora.txt")
            self.commit("feat: fora do declarado")
        self.entregar()
        self.git("update-ref", "refs/remotes/origin/develop", "HEAD~1")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("base: merge-base", saida)
        self.assertIn('escopo: fora do declarado no brief "fora.txt"', saida)

    def test_head_ja_na_develop_mantem_o_base_sha(self):
        """Com o head já na develop, o merge-base seria o próprio head (intervalo vazio): fica o Base-sha, como antes da E23.36."""
        self.entrega_e_merge()
        self.git("push", "-q", "origin", "melhoria/x:develop")
        self.git("fetch", "-q", "origin")
        self.ancorar(self.git("rev-parse", "HEAD"), "exemplo-outra-2.md")  # o head ancorado: só a guarda do "head já na base" o recusa
        _, saida = self.conferir()
        self.assertNotIn("base: merge-base", saida)
        self.assertIn(f"intervalo: {self.base}..", saida)  # o Desde é o Base-sha, nunca o head (v047 E1.185: a conferida da develop não vale)


class JuncaoLimpa(Conferencia):
    """E2.302: depois da entrega conferida, o intervalo só com merge da develop sem resolução à mão (cada merge igual à mescla
    automática, a develop ancorada num Base-sha selado) cumpre sem commit novo; resolução à mão, merge sem âncora ou conferida fora
    da forma seguem pendentes (na dúvida, recusa)."""

    develop_anda, ancorar, mesclar_develop = (MergeDaBaseDepoisDoBrief.develop_anda, MergeDaBaseDepoisDoBrief.ancorar,
                                             MergeDaBaseDepoisDoBrief.mesclar_develop)  # sem herdar (e rodar de novo) os testes de lá

    def conferida(self):
        """A entrega de código conferida e gravada pela ferramenta; devolve o head conferido."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        feito = self.entregar()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        return feito

    def juncao(self, *conteudos, ancorar=True):
        """Um merge limpo da develop por conteúdo de `agents/outro.md`; com `ancorar`, a ponta ancorada num brief selado depois."""
        for texto in conteudos:
            ponta, = self.develop_anda(texto)
            self.mesclar_develop()
        if ancorar:
            self.ancorar(ponta)
        return self.git("rev-parse", "HEAD")

    def test_caso_real_duas_juncoes_limpas_cumprem_e_gravam(self):
        feito = self.conferida()
        head = self.juncao("a\n", "a\nb\n")
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"escopo: junção limpa da base (só merge da \"develop\" sem resolução à mão; a entrega conferida {feito[:12]}", saida)
        self.assertNotIn("pendente:", saida)
        self.assertIn(f"entrega conferida {head}", self.pedido())

    def test_uma_juncao_limpa_cumpre(self):
        self.conferida()
        self.juncao("a\n")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn("escopo: junção limpa da base", saida)

    def test_juncao_sem_ancora_segue_pendente(self):
        """A `origin/develop` é ref local que o autor reescreve: sem Base-sha selado que a cubra, recusa; e o que a develop trouxe
        segue no escopo (FILTROS-L08-G2-ORIGIN-LOCAL), salvo o igual ao merge-base com a develop do `git ls-remote`
        (ENTREGA-MERGE-DA-DEVELOP): sem nada do autor, o intervalo fica pendente."""
        self.conferida()
        self.juncao("a\n", ancorar=False)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("pendente: intervalo vazio na etapa codigo", saida)
        self.assertNotIn("agents/outro.md", saida)
        self.assertIn("escopo: merge da \"develop\" sem âncora", saida)
        # segurança A5: o aviso sem âncora não contradiz a linha da integração pelo remoto
        self.assertIn("segue no escopo, salvo o igual ao merge-base com a base do `git ls-remote origin`", saida)
        self.assertIn("escopo: integração da base pelo remoto (", saida)

    def test_conflito_resolvido_a_mao_segue_pendente(self):
        self.conferida()
        self.git("switch", "-q", "develop")
        self.gravar("bin/app", "x\nda develop\n")
        self.git("add", "bin/app")
        ponta = self.commit("outro lote")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        r = subprocess.run(["git", "-C", str(self.proj), "-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff",
                            "origin/develop"], capture_output=True, text=True, env=self.env, timeout=60)
        self.assertIn("CONFLICT", r.stdout + r.stderr)
        self.git("checkout", "--ours", "bin/app")
        self.git("add", "bin/app")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "merge da develop")
        self.ancorar(ponta)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("pendente: a entrega é só a integração da base", saida)
        self.assertNotIn("junção limpa", saida)

    def test_merge_que_descarta_a_mudanca_da_develop_segue_pendente(self):
        """Sem conflito, mas a árvore do merge não é a da mescla automática (o arquivo da develop tirado à mão)."""
        self.conferida()
        ponta, = self.develop_anda("a\n")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-commit", "origin/develop")
        self.git("rm", "-q", "-f", "agents/outro.md")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "-m", "merge da develop")
        self.ancorar(ponta)
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("pendente: a entrega é só a integração da base", saida)

    def test_conferida_fora_da_forma_nao_cobre_o_primeiro_pai(self):
        """Só a linha `- <data> <hora>: entrega conferida <sha40>` que a ferramenta grava cobre o primeiro pai."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        feito = self.entregar()
        (self.proj / "docs/pedidos/exemplo.md").write_text(self.pedido() + f"- 2026-01-01: entrega conferida {feito}\n", encoding="utf-8")
        self.juncao("a\n")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertNotIn("junção limpa", saida)

    def test_intervalo_vazio_commit_comum_ou_sem_base_recusam(self):
        feito = self.conferida()
        head = self.juncao("a\n", ancorar=False)
        base_ref = self.git("rev-parse", "origin/develop")
        self.assertTrue(fc.juncao_limpa(self.proj, feito, head, base_ref, [base_ref]))
        self.assertFalse(fc.juncao_limpa(self.proj, head, head, base_ref, [base_ref]))  # nada no intervalo
        self.assertFalse(fc.juncao_limpa(self.proj, feito, head, None, [base_ref]))  # sem a base
        self.assertFalse(fc.juncao_limpa(self.proj, feito, head, base_ref, []))  # sem âncora
        self.gravar("volta.txt", "v\n")
        self.git("add", "volta.txt")
        depois = self.commit("feat: depois da junção")
        self.assertFalse(fc.juncao_limpa(self.proj, feito, depois, base_ref, [base_ref]))  # commit comum no primeiro pai

    def test_segundo_pai_ancorado_mas_fora_da_base_recusa(self):
        """QA A1: o segundo pai num Base-sha selado não basta; ele também precisa estar na `base_ref`."""
        feito = self.conferida()
        head = self.juncao("a\n", ancorar=False)
        ponta, antes = self.git("rev-parse", "origin/develop"), self.git("rev-parse", "origin/develop^")
        self.assertTrue(fc.juncao_limpa(self.proj, feito, head, ponta, [ponta]))
        self.assertFalse(fc.juncao_limpa(self.proj, feito, head, antes, [ponta]))  # ancorado, fora da base

    def test_gitattributes_da_arvore_de_trabalho_nao_resolve_conflito(self):
        """Segurança A1: `merge=union` num `.gitattributes` não versionado deixa limpa a mescla da develop em conflito; a conferência
        lê os atributos da árvore vazia e vê o conflito."""
        feito = self.conferida()
        self.git("switch", "-q", "develop")
        self.gravar("bin/app", "x\nda develop\n")
        self.git("add", "bin/app")
        ponta = self.commit("outro lote")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.gravar(".gitattributes", "bin/app merge=union\n")
        self.mesclar_develop()  # sem conflito só pela união
        head = self.git("rev-parse", "HEAD")
        self.assertFalse(fc.juncao_limpa(self.proj, feito, head, ponta, [ponta]))


class ParecerMescladoNaVolta(Conferencia):
    """E50.1 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR): o caso real (melhoria/v0479-bp1-q1-leitor, df0251ca..eec2c1c1): o portão
    revalida sem brief novo (SendMessage), commita ou mescla o parecer na branch depois da conferida e antes do commit da volta; o
    parecer é anexo do portão. O autor que toca o parecer (no commit do código ou numa resolução de merge à mão) segue fora."""

    ETAPA, PAPEL = ParecerDoPortao.ETAPA, ParecerDoPortao.PAPEL
    selar_portao, commitar_parecer, assert_fora = ParecerDoPortao.selar_portao, ParecerDoPortao.commitar_parecer, ParecerDoPortao.assert_fora
    OK_REVIEW = 'escopo: ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer) "docs/reviews/x.md"'

    def codigo(self, texto, *extra):
        self.gravar("bin/app", texto)
        self.git("add", "bin/app", *extra)
        return self.commit("fix: volta")

    def ate_a_conferida(self, conferida=True):
        """A 1.a entrega, o reprovado do review ancorado no brief selado do portão e a correção do autor, conferida (o Desde)."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.commitar_parecer("reviews", "review", parecer="reprovado")
        revisado = self.codigo("x\ny\nz\n")
        if conferida:
            pedido = self.proj / "docs/pedidos/exemplo.md"
            pedido.write_text(self.pedido() + f"- 2026-01-01 12:00: entrega conferida {revisado}\n", encoding="utf-8")
        return revisado

    def mesclar_parecer(self, revisado, pasta="reviews", tipo="review", **kw):
        """O portão grava o parecer numa branch ao lado e o mescla na branch (o `Merge remote-tracking branch` do caso real)."""
        self.git("switch", "-q", "-c", "lado")
        self.commitar_parecer(pasta, tipo, revisado=revisado, selar=False, **kw)
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-edit", "lado")

    def volta_com_parecer(self, **kw):
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(kw.pop("revisado", revisado), **kw)
        self.codigo("x\ny\nz\nw\n")

    def test_caso_real_parecer_mesclado_e_commitado_antes_da_volta_e_anexo(self):
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(revisado)
        self.commitar_parecer("security", "revisao-seguranca", revisado=revisado, selar=False)
        self.codigo("x\ny\nz\nw\n")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {revisado}..", saida)
        self.assertIn(self.OK_REVIEW, saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de seguranca commitado na volta só com parecer) "docs/security/x.md"', saida)

    def test_autor_que_edita_o_parecer_no_commit_do_codigo_segue_fora(self):
        revisado = self.ate_a_conferida()
        rel = "docs/reviews/x.md"
        self.gravar(rel, f"---\ntipo: review\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {revisado}\nparecer: aprovado\n---\n# eu\n")
        self.codigo("x\ny\nz\nw\n", rel)
        self.assert_fora()

    def test_merge_com_o_parecer_resolvido_a_mao_segue_fora(self):
        revisado = self.ate_a_conferida()
        self.git("switch", "-q", "-c", "lado")
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False)
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-commit", "lado")
        self.gravar("docs/reviews/x.md", f"---\ntipo: review\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {revisado}\n"
                                         "parecer: aprovado\n---\n# resolvido à mão\n")
        self.git("add", "docs/reviews/x.md")
        self.commit("Merge branch 'lado'")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora()

    def test_sem_conferida_a_regra_nao_vale(self):
        """Sem Desde (a 1.a entrega), o parecer sem brief selado do portão segue fora, como antes (ParecerDoPortao)."""
        revisado = self.ate_a_conferida(conferida=False)
        self.mesclar_parecer(revisado)
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora()

    def test_sem_conferida_o_parecer_com_commit_no_base_sha_segue_fora(self):
        """A1 do QA (E50.11): na 1.a entrega, o parecer de outro papel com `commit:` igual ao Base-sha, commitado só com a
        pasta dele, segue fora: a regra só vale com o Desde de conferida ou Revisar-sha (`and valido`)."""
        self.ate_a_conferida(conferida=False)
        self.mesclar_parecer(self.base, pasta="security", tipo="revisao-seguranca")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora("docs/security/x.md")

    def test_frontmatter_de_outra_branch_pedido_tipo_ou_sem_veredito_segue_fora(self):
        for kw in ({"branch": "melhoria/y"}, {"pedido": "outro"}, {"parecer": "pendente"}, {"tipo": "qa"}):
            with self.subTest(**kw):
                self.setUp()
                self.volta_com_parecer(**kw)
                self.assert_fora()

    def test_commit_fora_do_intervalo_ou_abreviado_segue_fora(self):
        for abreviado in (False, True):
            with self.subTest(abreviado=abreviado):
                self.setUp()
                revisado = self.ate_a_conferida()
                self.mesclar_parecer(revisado[:12] if abreviado else self.base)
                self.codigo("x\ny\nz\nw\n")
                self.assert_fora()

    def test_parecer_sem_frontmatter_segue_fora(self):
        self.ate_a_conferida()
        self.git("switch", "-q", "-c", "lado")
        self.gravar("docs/reviews/x.md", "# parecer sem frontmatter\n")
        self.git("add", "docs/reviews/x.md")
        self.commit("docs(reviews): parecer")
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-edit", "lado")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora()

    def test_veredito_trocado_no_mesmo_commit_segue_fora(self):
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(revisado, parecer="reprovado")
        self.commitar_parecer("reviews", "review", revisado=revisado, selar=False)
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora()

    def test_git_que_falha_conta_como_commit_do_autor(self):
        self.volta_com_parecer()
        rel = "docs/reviews/x.md"
        lado = self.git("rev-parse", "lado")
        self.assertTrue(fc.commit_so_de_parecer(self.proj, lado, rel, "docs/reviews"))
        self.assertFalse(fc.commit_so_de_parecer(self.proj, "0" * 40, rel, "docs/reviews"))
        original = fc.git

        def sem_diff_tree(raiz, *args, **kw):
            return (128, b"docs/reviews/x.md\0") if args[0] == "diff-tree" else original(raiz, *args, **kw)  # código de erro com saída
        with mock.patch.object(fc, "git", sem_diff_tree):
            self.assertFalse(fc.commit_so_de_parecer(self.proj, lado, rel, "docs/reviews"))
        self.assertFalse(fc.parecer_mesclado_na_volta(self.proj, self.base, "0" * 40, "HEAD", rel, "review", "melhoria/x", "exemplo", "x", {"node-backend"}, {}))

    def test_rev_list_que_falha_recusa(self):
        """E50.5 (A1 do review): o rev-list do intervalo que falha não vira `all([])` (aceite); o mesmo caso com o git certo é anexo."""
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(revisado)
        self.codigo("x\ny\nz\nw\n")
        rel, original = "docs/reviews/x.md", fc.git
        argumentos = (self.proj, self.base, revisado, "HEAD", rel, "review", "melhoria/x", "exemplo", "x", {"node-backend"}, {})
        self.assertTrue(fc.parecer_mesclado_na_volta(*argumentos))

        def sem_rev_list(raiz, *args, **kw):
            return (128, "") if args[0] == "rev-list" and args[-1] == rel else original(raiz, *args, **kw)  # só o do arquivo, não o da pasta
        with mock.patch.object(fc, "git", sem_rev_list):
            self.assertFalse(fc.parecer_mesclado_na_volta(*argumentos))

    def test_autor_que_forja_aprovado_citando_o_proprio_codigo_segue_fora(self):
        """E50.5 (S1 da segurança): o `commit:` é o Desde, nunca outro commit do intervalo."""
        self.ate_a_conferida()
        novo = self.codigo("x\ny\nz\nw\n")
        self.commitar_parecer("reviews", "review", revisado=novo, selar=False)
        self.assert_fora()

    def test_reprovado_do_portao_trocado_por_aprovado_com_outro_commit_segue_fora(self):
        """E50.5 (S3 da segurança): o reprovado no Desde não some sob um aprovado que cita o código novo."""
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(revisado, parecer="reprovado")
        novo = self.codigo("x\ny\nz\nw\n")
        self.commitar_parecer("reviews", "review", revisado=novo, selar=False)
        self.assert_fora()

    def test_um_commit_com_pareceres_de_varias_pastas_segue_fora(self):
        """E50.5 (S2 da segurança): cada tipo só vale num commit da própria pasta, mesmo citando o Desde."""
        revisado = self.ate_a_conferida()
        self.codigo("x\ny\nz\nw\n")
        for pasta, tipo in (("reviews", "review"), ("security", "revisao-seguranca"), ("qa", "qa")):
            rel = f"docs/{pasta}/x.md"
            self.gravar(rel, f"---\ntipo: {tipo}\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {revisado}\nparecer: aprovado\n---\n# f\n")
            self.git("add", rel)
        self.commit("docs: pareceres")
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        for rel in ("docs/reviews/x.md", "docs/security/x.md", "docs/qa/x.md"):
            self.assertIn(f'escopo: fora do declarado no brief "{rel}"', saida)

    def test_parecer_de_seguranca_com_aceite_no_mesmo_commit_segue_fora(self):
        """E50.5 (A2 da segurança): `docs/security/aceites/` (do usuário) não entra no commit do portão; o modelo de ameaças, sim."""
        for extra, anexo in (("docs/security/aceites/exemplo.md", False), ("docs/security/ameacas/x.md", True)):
            with self.subTest(extra=extra):
                self.setUp()
                revisado = self.ate_a_conferida()
                self.gravar(extra, "# extra\n")
                self.git("add", extra)
                self.commitar_parecer("security", "revisao-seguranca", revisado=revisado, selar=False)
                self.codigo("x\ny\nz\nw\n")
                rc, saida = self.conferir()
                ok = 'escopo: ok (anexo do portão: parecer de seguranca commitado na volta só com parecer) "docs/security/x.md"'
                (self.assertIn if anexo else self.assertNotIn)(ok, saida)


class ParecerDoMesmoPapelDoAutor(Conferencia):
    """E50.6 (A4 da segurança, S12): o tech-lead autor da volta é o dono de docs/reviews/; o review mesclado na volta só vale com o
    `parecer conferido` do Jarvis no Histórico com o blob do head, nunca pela forma do git. O portão de outro papel segue como antes."""

    ETAPA, PAPEL, OK_REVIEW = ParecerDoPortao.ETAPA, ParecerDoPortao.PAPEL, ParecerMescladoNaVolta.OK_REVIEW
    selar_portao, commitar_parecer, assert_fora = ParecerDoPortao.selar_portao, ParecerDoPortao.commitar_parecer, ParecerDoPortao.assert_fora
    codigo, ate_a_conferida, mesclar_parecer = (ParecerMescladoNaVolta.codigo, ParecerMescladoNaVolta.ate_a_conferida,
                                                ParecerMescladoNaVolta.mesclar_parecer)
    REL = "docs/reviews/x.md"

    def volta_do_tech_lead(self, conferido=False):
        """A volta selada para o tech-lead; o review mesclado de `lado`; com `conferido`, a linha do Jarvis cita o commit de `lado` (o P)
        e a segurança não grava (com linha no Histórico, todo parecer do intervalo precisa ser conferido, M2)."""
        revisado = self.ate_a_conferida()
        self.selar_copia("exemplo-tech-lead-2.md", {"Agente destino: forge:node-backend": "Agente destino: forge:tech-lead"}, selar=False)
        self.mesclar_parecer(revisado)
        if conferido:
            pedido = self.proj / "docs/pedidos/exemplo.md"
            pedido.write_text(self.pedido() + f"- 2026-01-01 13:00: parecer conferido {self.git('rev-parse', 'lado')}\n", encoding="utf-8")
        else:
            self.commitar_parecer("security", "revisao-seguranca", revisado=revisado, selar=False)
        self.codigo("x\ny\nz\nw\n")
        return revisado

    def test_mesmo_papel_sem_linha_do_jarvis_segue_fora(self):
        self.volta_do_tech_lead()
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(f'escopo: fora do declarado no brief "{self.REL}"', saida)
        self.assertIn('escopo: ok (anexo do portão: parecer de seguranca commitado na volta só com parecer) "docs/security/x.md"', saida)

    def test_mesmo_papel_com_parecer_conferido_do_jarvis_e_anexo(self):
        self.volta_do_tech_lead(conferido=True)
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(self.OK_REVIEW, saida)

    def test_parecer_conferido_de_outra_versao_nao_ancora(self):
        """A linha do Jarvis vale para o blob que ele conferiu: um P com outra versão do parecer (o reprovado) não ancora o aprovado."""
        revisado = self.volta_do_tech_lead()
        argumentos = (self.proj, self.base, revisado, "HEAD", self.REL, "review", "melhoria/x", "exemplo", "x", {"tech-lead"})
        self.assertTrue(fc.parecer_mesclado_na_volta(*argumentos, {self.REL: self.git("rev-parse", "lado")}))
        self.assertFalse(fc.parecer_mesclado_na_volta(*argumentos, {self.REL: revisado}))
        self.assertFalse(fc.parecer_mesclado_na_volta(*argumentos, {}))

    def test_sem_autor_conhecido_falha_fechada(self):
        """Sem brief selado de codigo (nenhum autor lido), o parecer mesclado precisa da linha do Jarvis, como o do mesmo papel."""
        revisado = self.ate_a_conferida()
        self.mesclar_parecer(revisado)
        self.codigo("x\ny\nz\nw\n")
        argumentos = (self.proj, self.base, revisado, "HEAD", self.REL, "review", "melhoria/x", "exemplo", "x")
        self.assertTrue(fc.parecer_mesclado_na_volta(*argumentos, {"node-backend"}, {}))
        self.assertFalse(fc.parecer_mesclado_na_volta(*argumentos, set(), {}))
        self.assertFalse(fc.parecer_mesclado_na_volta(*argumentos, {"node-backend", "tech-lead"}, {}))
        self.assertEqual(fc.autores_da_volta(self.proj, self.proj / "docs/pedidos/exemplo.md", self.pedido(), "melhoria/x", "exemplo"),
                         {"node-backend"})

    def test_brief_de_outro_pedido_nao_e_autor_da_volta(self):
        """Só os briefs de codigo deste pedido dizem quem é o autor; o tech-lead de outro pedido na mesma branch não entra."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.selar_copia("outro-tech-lead-1.md", {"Pedido: exemplo": "Pedido: outro",
                                                  "Agente destino: forge:node-backend": "Agente destino: forge:tech-lead"}, selar=False)
        self.assertEqual(fc.autores_da_volta(self.proj, self.proj / "docs/pedidos/exemplo.md", self.pedido(), "melhoria/x", "exemplo"),
                         {"node-backend"})


class BugDoQaNaVolta(Conferencia):
    """E62.1 (DECISÃO DO DONO v0478, 2026-11-20 17:29, item 2): o caso real (AE2 C1, AE1.4, AE1.2): o QA grava o registro de bug em
    docs/qa/bugs/ (sem frontmatter) e o commita ou mescla na branch depois da conferida; na volta, ele é anexo do portão de QA, como o
    parecer (E50.1). O autor que o toca, o merge resolvido à mão e o commit que leva outro arquivo seguem fora."""

    ETAPA, PAPEL = ParecerDoPortao.ETAPA, ParecerDoPortao.PAPEL
    selar_portao, commitar_parecer, assert_fora = ParecerDoPortao.selar_portao, ParecerDoPortao.commitar_parecer, ParecerDoPortao.assert_fora
    codigo, ate_a_conferida = ParecerMescladoNaVolta.codigo, ParecerMescladoNaVolta.ate_a_conferida
    REL = "docs/qa/bugs/x-01-defeito.md"
    OK = 'escopo: ok (anexo do portão: registro de bug de qa commitado na volta só com docs/qa) "docs/qa/bugs/x-01-defeito.md"'

    def commitar_bug(self, *extra, rel=None):
        rel = rel or self.REL
        self.gravar(rel, "# X-01 - defeito\n- Severidade: média\n")
        self.git("add", rel, *extra)
        return self.commit("docs(qa): registro de bug")

    def mesclar_bug(self, *extra, rel=None):
        """O QA grava o bug numa branch ao lado e a mescla na branch (o `Merge remote-tracking branch` do caso real)."""
        self.git("switch", "-q", "-c", "lado")
        self.commitar_bug(*extra, rel=rel)
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-edit", "lado")

    def argumentos(self, revisado):
        return (self.proj, revisado, "HEAD", self.REL)

    def test_caso_real_bug_mesclado_antes_da_volta_e_anexo(self):
        revisado = self.ate_a_conferida()
        self.mesclar_bug()
        self.codigo("x\ny\nz\nw\n")
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {revisado}..", saida)
        self.assertIn(self.OK, saida)

    def test_bug_commitado_na_branch_depois_da_volta_e_anexo(self):
        self.ate_a_conferida()
        self.codigo("x\ny\nz\nw\n")
        self.commitar_bug()
        rc, saida = self.conferir()
        self.assertEqual(rc, 0, saida)
        self.assertIn(self.OK, saida)

    def test_autor_que_grava_o_bug_no_commit_do_codigo_segue_fora(self):
        self.ate_a_conferida()
        self.gravar(self.REL, "# X-01 - corrigido pelo autor\n")
        self.codigo("x\ny\nz\nw\n", self.REL)
        self.assert_fora(self.REL)

    def test_commit_do_bug_com_arquivo_fora_de_docs_qa_segue_fora(self):
        self.ate_a_conferida()
        self.gravar("docs/notas/b.md", "nota\n")
        self.mesclar_bug("docs/notas/b.md")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora(self.REL)

    def test_merge_com_o_bug_resolvido_a_mao_segue_fora(self):
        self.ate_a_conferida()
        self.git("switch", "-q", "-c", "lado")
        self.commitar_bug()
        self.git("switch", "-q", "melhoria/x")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-commit", "lado")
        self.gravar(self.REL, "# X-01 - resolvido à mão\n")
        self.git("add", self.REL)
        self.commit("Merge branch 'lado'")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora(self.REL)

    def test_sem_conferida_a_regra_nao_vale(self):
        """Na 1.a entrega (sem Desde), o bug segue fora, como o parecer do E50.1."""
        self.ate_a_conferida(conferida=False)
        self.mesclar_bug()
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora(self.REL)

    def test_arquivo_de_docs_qa_fora_de_bugs_sem_frontmatter_segue_fora(self):
        """Só a pasta docs/qa/bugs/ é registro de bug; o arquivo de docs/qa/ sem frontmatter segue a regra do parecer (fora)."""
        self.ate_a_conferida()
        self.mesclar_bug(rel="docs/qa/nota.md")
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora("docs/qa/nota.md")

    def test_qa_autor_da_volta_sem_linha_do_jarvis_segue_fora(self):
        """E50.6: com o qa-engineer autor de uma volta (brief selado de codigo), o bug só vale com o `parecer conferido` do Jarvis."""
        self.ate_a_conferida()
        self.selar_copia("exemplo-qa-engineer-2.md", {"Agente destino: forge:node-backend": "Agente destino: forge:qa-engineer"}, selar=False)
        self.mesclar_bug()
        self.codigo("x\ny\nz\nw\n")
        self.assert_fora(self.REL)

    def test_autores_e_linha_do_jarvis(self):
        revisado = self.ate_a_conferida()
        self.mesclar_bug()
        self.codigo("x\ny\nz\nw\n")
        lado = self.git("rev-parse", "lado")
        self.assertTrue(fc.bug_do_qa_na_volta(*self.argumentos(revisado), {"node-backend"}, {}))
        for autores in (set(), {"node-backend", "qa-engineer"}):
            with self.subTest(autores=autores):
                self.assertFalse(fc.bug_do_qa_na_volta(*self.argumentos(revisado), autores, {}))
                self.assertFalse(fc.bug_do_qa_na_volta(*self.argumentos(revisado), autores, {self.REL: revisado}))
                self.assertTrue(fc.bug_do_qa_na_volta(*self.argumentos(revisado), autores, {self.REL: lado}))

    def test_rev_list_que_falha_ou_vazio_recusa(self):
        revisado = self.ate_a_conferida()
        self.mesclar_bug()
        self.codigo("x\ny\nz\nw\n")
        original = fc.git
        self.assertTrue(fc.bug_do_qa_na_volta(*self.argumentos(revisado), {"node-backend"}, {}))
        for resposta in ((128, ""), (0, "")):
            def falso(raiz, *args, **kw):
                return resposta if args[0] == "rev-list" and args[-1] == self.REL else original(raiz, *args, **kw)
            with self.subTest(resposta=resposta), mock.patch.object(fc, "git", falso):
                self.assertFalse(fc.bug_do_qa_na_volta(*self.argumentos(revisado), {"node-backend"}, {}))


class MergeDeParecerAninhado(Repositorio):
    """ENTREGA-MERGE-DE-PARECER-ANINHADO (caso real: merge 445f1988 da v0479-pv-a2-concessao, outro pai cdb616f7): um portão trouxe o
    parecer do outro por merge e a branch mesclou esse merge de pareceres. O diff do outro pai contra o primeiro pai dele só tem o
    parecer do portão; o do outro portão vale pelo blob de um `parecer conferido` ancestral do outro pai que mude o arquivo."""

    def parecer(self, ramo, arquivos, de):
        self.git("switch", "-q", "-c", ramo, de)
        for rel, texto in arquivos.items():
            self.gravar(rel, texto)
        self.git("add", *arquivos)
        sha = self.commit(f"docs: parecer {ramo}")
        self.git("switch", "-q", "melhoria/x")
        return sha

    def mesclar(self, alvo, ramo="melhoria/x", trocar=None):
        """O merge de `alvo` em `ramo`; com `trocar` (arquivo -> texto), resolvido à mão com esse conteúdo."""
        self.git("switch", "-q", ramo)
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "--no-commit", alvo)
        for rel, texto in (trocar or {}).items():
            self.gravar(rel, texto)
            self.git("add", rel)
        sha = self.commit(f"merge {alvo[:7]}")
        self.git("switch", "-q", "melhoria/x")
        return sha

    def aninhado(self, revisao=None, ramo_rev="rev"):
        """O autor entrega; review e segurança commitam o parecer cada um na sua cópia; a segurança vai à branch e a review mescla a
        segurança (o merge de pareceres); a branch mescla esse merge, que traz só o parecer da review."""
        self.autor = self.entregar()
        self.rev = self.parecer(ramo_rev, revisao or {"docs/reviews/x.md": "r\n"}, self.autor)
        self.seg = self.parecer("seg", {"docs/security/x.md": "s\n"}, self.autor)
        self.de_pareceres = self.mesclar(self.seg, ramo_rev)
        self.mesclar(self.seg)

    def recusas(self, *conferidos):
        texto = PEDIDO + "".join(f"- 2026-01-01 10:00: parecer conferido {sha}\n" for sha in conferidos)
        head, base_ref = self.git("rev-parse", "HEAD"), self.git("rev-parse", "origin/develop")
        return fc.merges_nao_conferidos(self.proj, texto, self.autor, head, base_ref)[0]

    def test_parecer_do_merge_de_pareceres_vale_pelo_blob_conferido(self):
        self.aninhado()
        self.mesclar(self.de_pareceres)
        self.assertEqual(self.recusas(self.rev, self.seg, self.de_pareceres), [])

    def test_blob_diferente_do_conferido_reprova(self):
        self.aninhado()
        m = self.mesclar(self.de_pareceres, trocar={"docs/reviews/x.md": "r\nmudado no merge\n"})
        self.assertEqual(self.recusas(self.rev, self.seg, self.de_pareceres),
                         [(f'escopo: fora (o merge {m[:7]} traz "docs/reviews/x.md" fora dos pareceres conferidos)', True)])

    def test_conferido_fora_da_historia_do_outro_pai_nao_vale(self):
        """O mesmo blob num `parecer conferido` que não é ancestral do outro pai (outra cópia do parecer) não vale."""
        self.aninhado(ramo_rev="rev-copia")
        fora = self.parecer("rev", {"docs/reviews/x.md": "r\n"}, self.autor)
        m = self.mesclar(self.de_pareceres)
        self.assertEqual(self.recusas(fora, self.seg, self.de_pareceres),
                         [(f'escopo: fora (o merge {m[:7]} traz "docs/reviews/x.md" fora dos pareceres conferidos)', True)])

    def test_aceite_do_usuario_no_parecer_conferido_reprova(self):
        self.aninhado(revisao={"docs/reviews/x.md": "r\n", "docs/security/aceites/a.md": "aceite\n"})
        m = self.mesclar(self.de_pareceres)
        self.assertIn((f"escopo: fora (aceite trazido pelo merge {m[:7]})", True), self.recusas(self.rev, self.seg, self.de_pareceres))

    def test_outro_pai_sem_linha_segue_nao_conferido(self):
        self.aninhado()
        self.mesclar(self.de_pareceres)
        self.assertIn((f"escopo: fora (merge de {self.de_pareceres[:7]} não conferido)", True), self.recusas(self.rev, self.seg))

    N = "docs/reviews/x.md"

    def fora(self, m):
        return [(f'escopo: fora (o merge {m[:7]} traz "{self.N}" fora dos pareceres conferidos)', True)]

    def dois_conferidos(self):
        """P1 (aprovado) e P2 (reprovado, sobre P1) do mesmo portão no mesmo arquivo."""
        self.autor = self.entregar()
        p1 = self.parecer("rev", {self.N: "parecer: aprovado\n"}, self.autor)
        return p1, self.parecer("rev2", {self.N: "parecer: reprovado\n"}, p1)

    def test_o_conferido_mais_novo_vale(self):
        p1, p2 = self.dois_conferidos()
        self.mesclar(p2)
        self.assertEqual(self.recusas(p1, p2), [])

    def test_parecer_conferido_antigo_restaurado_no_merge_reprova(self):
        """Review A2 (S2): o merge de P2 resolvido à mão com o blob de P1 não vale (só o último conferido que muda o arquivo)."""
        p1, p2 = self.dois_conferidos()
        m = self.mesclar(p2, trocar={self.N: "parecer: aprovado\n"})
        self.assertEqual(self.recusas(p1, p2), self.fora(m))

    def test_outro_pai_que_rebaixa_o_parecer_reprova(self):
        """Segurança A4: o outro pai conferido é um merge que guardou o blob superado de P1; sem resolução no merge da branch, não vale."""
        p1, p2 = self.dois_conferidos()
        q = self.mesclar(p2, "rev", trocar={self.N: "parecer: aprovado\n"})
        m = self.mesclar(q)
        self.assertEqual(self.recusas(p1, p2, q), self.fora(m))

    def test_mudanca_fora_do_portao_depois_do_conferido_reprova(self):
        """Um commit sem linha muda o parecer depois de P1 e um conferido de outro arquivo (P3) vem por cima: o mais novo que muda o
        arquivo é P1, e o blob trazido não é o dele."""
        self.autor = self.entregar()
        p1 = self.parecer("rev", {self.N: "parecer: aprovado\n"}, self.autor)
        c = self.parecer("solto", {self.N: "parecer: mudado fora do portão\n"}, p1)
        p3 = self.parecer("seg", {"docs/security/x.md": "s\n"}, c)
        m = self.mesclar(p3)
        self.assertEqual(self.recusas(p1, p3), self.fora(m))

    def test_dois_conferidos_sem_ordem_nao_tem_o_mais_novo(self):
        """Dois pareceres conferidos em ramos paralelos, unidos por merge que guarda um deles: nenhum é o mais novo (falha fechada)."""
        self.autor = self.entregar()
        pa = self.parecer("ra", {self.N: "a\n"}, self.autor)
        pb = self.parecer("rb", {self.N: "b\n"}, self.autor)
        self.git("switch", "-q", "ra")
        self.git("-c", "user.email=a@b", "-c", "user.name=a", "merge", "-q", "--no-ff", "-s", "ours", "-m", "une", pb)
        q = self.git("rev-parse", "HEAD")
        self.git("switch", "-q", "melhoria/x")
        self.assertIsNone(fc.conferido_mais_novo(self.proj, {pa, pb, q}, q, self.N))

    def na_branch(self, rel, texto):
        self.gravar(rel, texto)
        self.git("add", rel)
        return self.commit(f"docs: {rel} na branch")

    def outro_pai_sobre_conferido(self):
        """CONFERENCIA-MERGE-DE-PARECERES (caso real: merge 3bd82d6, outro pai d5816e86): o QA commita na branch; a segurança commita
        sobre a review no remoto; a branch mescla a segurança, e o parecer da review vem do conferido ancestral do outro pai."""
        self.autor = self.entregar()
        self.na_branch("docs/qa/x.md", "q\n")
        self.rev = self.parecer("rev", {self.N: "r\n"}, self.autor)
        self.seg = self.parecer("seg", {"docs/security/x.md": "s\n"}, self.rev)
        return self.mesclar(self.seg)

    def test_caso_real_outro_pai_sobre_conferido_vale(self):
        self.outro_pai_sobre_conferido()
        self.assertEqual(self.recusas(self.rev, self.seg), [])

    def test_caso_real_ancestral_sem_linha_reprova(self):
        m = self.outro_pai_sobre_conferido()
        self.assertEqual(self.recusas(self.seg), self.fora(m))

    def merge_do_merge_de_pareceres(self):
        """Caso real (merge bca3bf42, outro pai 151bdda5): três portões em paralelo; a review mescla a segurança, o QA também, e a
        review mescla o merge do QA, que traz o parecer do QA do primeiro pai do outro pai."""
        self.autor = self.entregar()
        self.na_branch(self.N, "r\n")
        self.seg = self.parecer("seg", {"docs/security/x.md": "s\n"}, self.autor)
        self.mesclar(self.seg)
        self.qa = self.parecer("qa", {"docs/qa/x.md": "q\n"}, self.autor)
        self.q = self.mesclar(self.seg, "qa")
        return self.mesclar(self.q)

    def test_caso_real_merge_de_merge_de_pareceres_vale(self):
        self.merge_do_merge_de_pareceres()
        self.assertEqual(self.recusas(self.seg, self.qa, self.q), [])

    def test_caso_real_merge_de_merge_com_o_qa_sem_linha_reprova(self):
        m = self.merge_do_merge_de_pareceres()
        self.assertEqual(self.recusas(self.seg, self.q),
                         [(f'escopo: fora (o merge {m[:7]} traz "docs/qa/x.md" fora dos pareceres conferidos)', True)])


FORA_DO_878 = 'escopo: fora do declarado no brief "docs/indice.md"'


class CicloDo878(Conferencia):
    """E16.1 (v0481, ENTREGA-DESDE-REVISAR-SHA): o ciclo do #878. O autor entrega na volta um commit revisado pelos três portões (o
    `Revisar-sha:` dos briefs selados deles) sem a `entrega conferida` dele; os pareceres aprovados entram na branch e a develop é
    trazida por merge. Com o Desde na última conferida, o que os portões revisaram e o brief não declara sai `fora do declarado`, e a
    conferência do head nunca é gravada (o merge espera por ela). Com o conserto, o Desde é o `commit:` dos pareceres aprovados no head;
    cada condição que falta devolve o Desde de sempre. Sem rede: o `origin` é um repositório nu local."""

    ETAPA, PAPEL = ParecerDoPortao.ETAPA, ParecerDoPortao.PAPEL
    selar_portao, commitar_parecer = ParecerDoPortao.selar_portao, ParecerDoPortao.commitar_parecer
    develop_anda, mesclar_develop = MergeDaBaseDepoisDoBrief.develop_anda, MergeDaBaseDepoisDoBrief.mesclar_develop

    def volta_revisada(self):
        """A 1.a entrega conferida e a volta do autor (com um arquivo que o brief não declara), sem conferida: o commit revisado."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        conferida = self.entregar()
        self.historico(f"entrega conferida {conferida}")
        self.gravar("bin/app", "x\ny\nz\n")
        self.gravar("docs/indice.md", "linha nova\n")
        self.git("add", "bin/app", "docs/indice.md")
        return self.commit("fix: volta")

    def historico(self, linha):
        pedido = self.proj / "docs/pedidos/exemplo.md"
        pedido.write_text(self.pedido() + f"- 2026-01-01 12:00: {linha}\n", encoding="utf-8")

    def portoes(self, revisado, seguranca="aprovado", selar=True):
        for pasta, tipo, parecer in (("reviews", "review", "aprovado"), ("qa", "qa", "aprovado"),
                                     ("security", "revisao-seguranca", seguranca)):
            self.commitar_parecer(pasta, tipo, revisado=revisado, parecer=parecer, selar=selar)

    def ciclo(self, **kw):
        revisado = self.volta_revisada()
        self.portoes(revisado, **kw)
        self.develop_anda("a\n")
        self.mesclar_develop()
        return revisado

    def test_ciclo_do_878_o_desde_e_o_revisar_sha_e_a_conferencia_cobre_o_head(self):
        revisado = self.ciclo()
        rc, saida = self.rodar("entrega", "--pedido", "exemplo", "--branch", "melhoria/x", "--etapa", "codigo")
        self.assertEqual(rc, 0, saida)
        self.assertIn(f"intervalo: {revisado}..", saida)
        self.assertNotIn("docs/indice.md", saida)
        head = self.git("rev-parse", "HEAD")
        self.assertIn(f"entrega conferida {head}", self.pedido())
        self.assertEqual(fc.conferencia_do_head(self.proj, "x", ref="melhoria/x", base="origin/develop", branch="melhoria/x"), [])

    def assert_desde_de_sempre(self):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn(FORA_DO_878, saida)

    def test_parecer_nao_aprovado_mantem_o_desde_da_conferida(self):
        self.ciclo(seguranca="reprovado")
        self.assert_desde_de_sempre()

    def reprovado_tirado(self, *passo, selar=True):
        """E16.6 (review A1 S1, segurança A1 S2 a S4): o ciclo do 878 com o parecer de segurança `reprovado` sobre o revisado e, depois
        do merge da develop, o `passo` git que o tira da conta do head (apagado, renomeado para `_x.md`); sem `passo`, regravado com
        `contrato: 0`. O reprovado segue no histórico da branch: o Desde é o de sempre e o que a volta não declara sai fora."""
        self.ciclo(seguranca="reprovado") if selar else self.ciclo_sem_selo_da_seguranca()
        rel = "docs/security/x.md"
        if passo:
            self.git(*passo)
        else:
            self.gravar(rel, (self.proj / rel).read_text(encoding="utf-8").replace("contrato: 1", "contrato: 0"))
            self.git("add", rel)
        self.commit("docs(security): o reprovado sai da conta")
        self.assert_desde_de_sempre()

    def ciclo_sem_selo_da_seguranca(self):
        revisado = self.volta_revisada()
        self.commitar_parecer("reviews", "review", revisado=revisado)
        self.commitar_parecer("qa", "qa", revisado=revisado)
        self.commitar_parecer("security", "revisao-seguranca", revisado=revisado, parecer="reprovado", selar=False)
        self.develop_anda("a\n")
        self.mesclar_develop()

    def test_reprovado_apagado_depois_mantem_o_desde_da_conferida(self):
        self.reprovado_tirado("rm", "-q", "docs/security/x.md")

    def test_reprovado_renomeado_para_sublinhado_mantem_o_desde_da_conferida(self):
        self.reprovado_tirado("mv", "docs/security/x.md", "docs/security/_x.md")

    def test_reprovado_com_contrato_zero_mantem_o_desde_da_conferida(self):
        self.reprovado_tirado()

    def test_reprovado_sem_brief_selado_apagado_mantem_o_desde_da_conferida(self):
        """Os portões selados (review e QA) aprovam e o reprovado de segurança, sem brief selado, sai do head: só o histórico o vê."""
        self.reprovado_tirado("rm", "-q", "docs/security/x.md", selar=False)

    def test_portao_selado_sem_parecer_mantem_o_desde_da_conferida(self):
        """O brief de segurança selou o revisado e o parecer dela não está no head: os aprovados de review e QA não bastam."""
        revisado = self.volta_revisada()
        self.commitar_parecer("reviews", "review", revisado=revisado)
        self.commitar_parecer("qa", "qa", revisado=revisado)
        self.selar_portao(self.ETAPA["security"], revisado, papel=self.PAPEL["security"])
        self.develop_anda("a\n")
        self.mesclar_develop()
        self.assert_desde_de_sempre()

    def test_sem_conferida_pela_entrega_o_intervalo_parte_do_base_sha(self):
        """E16.6 (review A2): sem conferida, o Desde do parecer não entra e a `entrega --pedido` confere desde o Base-sha."""
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        self.portoes(self.commit_da_volta())
        rc, saida = self.conferir()
        self.assertIn(f"intervalo: {self.base}..", saida)

    def test_sem_brief_selado_do_portao_mantem_o_desde_da_conferida(self):
        self.ciclo(selar=False)
        self.assert_desde_de_sempre()
        self.assertIsNone(self.chamar(valido=self.git("rev-parse", "HEAD~5")))  # antes do merge, dos três pareceres e da volta

    def test_codigo_depois_dos_pareceres_mantem_o_desde_da_conferida(self):
        self.ciclo()
        self.gravar("bin/app", "x\ny\nz\nw\n")
        self.git("add", "bin/app")
        self.commit("fix: depois do review")
        self.assert_desde_de_sempre()

    def test_sem_review_mantem_o_desde_da_conferida(self):
        revisado = self.volta_revisada()
        self.commitar_parecer("qa", "qa", revisado=revisado)
        self.assert_desde_de_sempre()

    def test_pareceres_com_commits_diferentes_mantem_o_desde_da_conferida(self):
        revisado = self.volta_revisada()
        self.commitar_parecer("reviews", "review", revisado=revisado)
        self.commitar_parecer("qa", "qa")  # o `commit:` do QA é o head de agora, não o revisado
        self.assert_desde_de_sempre()

    def test_dois_commits_revisados_selados_nao_dao_desde(self):
        """Review e QA com `commit:` diferentes, cada um selado nos dois portões e cada um valendo sozinho: nenhum é o Desde."""
        revisado = self.volta_revisada()
        conferida = self.git("rev-parse", "HEAD~1")
        self.commitar_parecer("reviews", "review", revisado=revisado)
        outro = self.git("rev-parse", "HEAD")
        self.selar_portao("review", outro, papel="tech-lead")
        self.selar_portao("qa", revisado, papel="qa-engineer")
        self.commitar_parecer("qa", "qa", revisado=outro)
        self.assertIsNone(self.chamar(valido=conferida))

    def test_sem_conferida_anterior_nao_ha_desde_do_parecer(self):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        revisado = self.commit_da_volta()
        self.portoes(revisado)
        caminho = self.proj / "docs/pedidos/exemplo.md"
        head = self.git("rev-parse", "HEAD")
        self.assertIsNone(fc.desde_do_parecer_aprovado(self.proj, caminho, self.pedido(), "melhoria/x", head, self.base, None, None))

    def commit_da_volta(self):
        self.gravar("bin/app", "x\ny\nz\n")
        self.git("add", "bin/app")
        return self.commit("fix: volta")

    def chamar(self, base_sha=None, valido=None):
        """A função direto no HEAD, com o pedido do disco (o HEAD~4 de `volta_revisada` mais os três pareceres é a conferida)."""
        caminho = self.proj / "docs/pedidos/exemplo.md"
        return fc.desde_do_parecer_aprovado(self.proj, caminho, self.pedido(), "melhoria/x", self.git("rev-parse", "HEAD"),
                                            base_sha or self.base, self.git("rev-parse", "refs/remotes/origin/develop"), valido)

    def test_conferida_adiante_do_revisado_fica(self):
        """A conferida gravada depois do commit revisado (o fluxo certo) segue sendo o Desde."""
        revisado = self.volta_revisada()
        self.portoes(revisado)
        self.assertEqual(self.chamar(valido=self.git("rev-parse", "HEAD~4")), revisado)
        self.assertIsNone(self.chamar(valido=self.git("rev-parse", "HEAD")))

    def test_revisado_na_base_nao_e_desde(self):
        revisado = self.volta_revisada()
        self.portoes(revisado)
        self.assertIsNone(self.chamar(base_sha=revisado, valido=self.git("rev-parse", "HEAD~4")))

    def test_revisado_fora_do_head_nao_e_desde(self):
        """Os pareceres citam um commit de outra branch, adiante da conferida e selado como Revisar-sha: não é Desde."""
        self.volta_revisada()
        conferida = self.git("rev-parse", "HEAD~1")
        self.git("switch", "-q", "-c", "lado", conferida)
        self.gravar("bin/app", "x\ny\nz\n")  # a mesma árvore da volta: só a ancestralidade separa os dois
        self.gravar("docs/indice.md", "linha nova\n")
        self.git("add", "bin/app", "docs/indice.md")
        lado = self.commit("fix: lado")
        self.git("switch", "-q", "melhoria/x")
        self.portoes(lado)
        self.assertIsNone(self.chamar(valido=conferida))

    def test_parecer_de_outra_branch_ou_pedido_vindo_da_develop_nao_conta(self):
        """O parecer de outro item (outra branch, outro pedido), trazido pela develop, não entra na conta dos `commit:`."""
        revisado = self.volta_revisada()
        self.portoes(revisado)
        conferida = self.git("rev-parse", "HEAD~4")
        self.git("switch", "-q", "develop")
        for nome, branch, pedido in (("y", "melhoria/y", "exemplo"), ("z", "melhoria/x", "outro")):
            self.gravar(f"docs/reviews/{nome}.md", f"---\ntipo: review\ncontrato: 1\npedido: {pedido}\nbranch: {branch}\n"
                                                    f"commit: {self.base}\nparecer: reprovado\n---\n# outro item\n")
            self.git("add", f"docs/reviews/{nome}.md")
        self.commit("docs(reviews): parecer de outro item")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
        self.mesclar_develop()
        self.assertEqual(self.chamar(valido=conferida), revisado)


if __name__ == "__main__":
    unittest.main()
