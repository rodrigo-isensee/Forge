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
        self.assertIn(f"--base-sha {self.base} --etapa codigo", texto)
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
        com `squash`, num commit de um pai só (`git merge --squash`), que o git não liga à base."""
        self.git("switch", "-q", "develop")
        for rel, texto in arquivos.items():
            self.gravar(rel, texto)
        self.git("add", *arquivos)
        self.commit("outro lote")
        self.git("push", "-q", "origin", "develop")
        self.git("switch", "-q", "melhoria/x")
        self.git("fetch", "-q", "origin")
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
        # cada lançamento sai sem reserva anterior: aqui só o selo é conferido; a delegação por branch (Z10) é de test_agentes_hash_brief
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

    ETAPA = {"reviews": "review", "devops": "devops", "qa": "qa", "security": "seguranca"}

    def selar_portao(self, etapa, revisado, trocas=None):
        """Um brief selado do portão `etapa` desta branch e pedido com `Revisar-sha: <revisado>` (o registro do Jarvis)."""
        self.n_portao = getattr(self, "n_portao", 10) + 1
        self.selar_copia(f"exemplo-portao-{self.n_portao}.md", {"Etapa: codigo": f"Revisar-sha: {revisado}\nEtapa: {etapa}", **(trocas or {})},
                         selar=False)

    def commitar_parecer(self, pasta, tipo, branch="melhoria/x", pedido="exemplo", revisado=None, parecer="aprovado", selar=True):
        """O parecer do portão sobre o head de agora (`revisado`, o `commit:` do frontmatter), commitado na branch; com `selar`, o brief
        selado do portão que o ancora."""
        rel, revisado = f"docs/{pasta}/x.md", revisado or self.git("rev-parse", "HEAD")
        if selar:
            self.selar_portao(self.ETAPA[pasta], revisado)
        self.gravar(rel, f"---\ntipo: {tipo}\ncontrato: 1\npedido: {pedido}\nbranch: {branch}\ncommit: {revisado}\nparecer: {parecer}\n---\n# parecer\n")
        self.git("add", rel)
        self.commit(f"docs({pasta}): parecer")
        return rel

    def entrega_com_parecer(self, **kw):
        self.brief()
        self.assertEqual(self.selar()[0], 0)
        self.entregar()
        return self.commitar_parecer("reviews", "review", **kw)

    def assert_fora(self):
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn('escopo: fora do declarado no brief "docs/reviews/x.md"', saida)

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
        self.assertFalse(fc.veredito_trocado(self.proj, self.base, "HEAD", "docs/reviews/x.md", revisado, "aprovado"))
        self.assertTrue(fc.veredito_trocado(self.proj, "0" * 40, "HEAD", "docs/reviews/x.md", revisado, "aprovado"))

    def test_parecer_sem_frontmatter_segue_fora(self):
        self.entrega_com_parecer()
        self.gravar("docs/reviews/x.md", "# parecer sem frontmatter\n")
        self.git("add", "docs/reviews/x.md")
        self.commit("docs(reviews): sem frontmatter")
        self.assert_fora()


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
        rc, saida = self.conferir()
        self.assertEqual(rc, 1, saida)
        self.assertIn("escopo: Base-sha fora da branch", saida)
        self.assertNotIn("base: merge-base", saida)

    def test_merge_base_sem_ancora_fica_o_base_sha(self):
        """Volta 1 (segurança A2): sem brief selado depois do da entrega, o merge-base não tem âncora do Jarvis e fica o Base-sha."""
        self.entrega_e_merge(ancorar=False)
        rc, saida = self.conferir()
        self.assertNotIn("base: merge-base", saida)
        self.assertEqual(rc, 1, saida)  # o comportamento de antes da E23.36: a conferida trazida vira Desde e a develop aparece

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
        _, saida = self.conferir()
        self.assertNotIn("base: merge-base", saida)
        self.assertNotIn("pendente: intervalo vazio", saida)


if __name__ == "__main__":
    unittest.main()
