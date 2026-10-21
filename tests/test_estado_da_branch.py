"""P5 (LOTE-FORGE-CHECK-0.28.0): estado lido antes do ato. `brief gerar --branch` imprime as linhas `estado:` (PR pelo `gh`, base que
andou, worktree que já existe, parecer desatualizado) e recusa brief de etapa que não cabe com o PR já mesclado; o `--volta` mantém a
Branch e o Base-sha do brief anterior e diz o que leu. O `gh` é sempre falso (sem rede)."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gh_falso import com_gh_falso  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

RAIZ = Path(__file__).resolve().parent.parent
FORGE_CHECK = RAIZ.joinpath("bin", "forge-check")

PEDIDO = """---
id: exemplo
---
# Pedido EXEMPLO

## Escopo
- E1. Fazer o recurso X

## Etapas
- E1.1 (dev-exemplo): implementação do recurso X.
- E1.2 (revisor-exemplo): merge na develop.

## Decisões do usuário (registro literal)
DECISÃO DO DONO (2026-01-01): "A".
"""
PARECER = ("---\ntipo: {tipo}\ncontrato: 1\npedido: exemplo\nbranch: melhoria/x\ncommit: {c}\nparecer: {p}\n{extra}data: 2026-10-12\n---\n"
           "# x\n{corpo}")
EXTRA = {"review": "revisor: forge:tech-lead\n",
         "qa": "escopo: completo\nbugs_criticos: 0\nbugs_altos: 0\nbugs_medios: 0\nbugs_baixos: 0\n"}
GH_MERGED = 'echo \'{"number": 7, "state": "MERGED", "headRefOid": "abcdef0123456789abcdef0123456789abcdef01"}\'\n'


def ambiente_do_git():
    """Sem GIT_* herdado (um hook do git exporta GIT_DIR) e sem config global ou de sistema: o git só vê o repositório temporário."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return env


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=ambiente_do_git()).stdout.strip()


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-estado-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.origem = self.tmp / "origem.git"
        git("init", "-q", "--bare", "-b", "develop", str(self.origem), cwd=self.tmp)
        self.semente = self.clone("semente")
        self.commitar(self.semente, {"README.md": "x\n", "src/app.py": "v1\n", "docs/pedidos/exemplo.md": PEDIDO}, "base")
        git("push", "-q", "origin", "develop", cwd=self.semente)
        self.repo = self.clone("repo")
        git("switch", "-q", "-c", "melhoria/x", cwd=self.repo)
        self.c1 = self.commitar(self.repo, {"src/app.py": "v2\n"}, "entrega")

    def clone(self, nome):
        destino = self.tmp / nome
        git("clone", "-q", str(self.origem), str(destino), cwd=self.tmp)
        git("config", "user.email", "t@example.com", cwd=destino)
        git("config", "user.name", "Teste", cwd=destino)
        return destino

    def commitar(self, pasta, arquivos, mensagem):
        for rel, texto in arquivos.items():
            arq = pasta / rel
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_text(texto, encoding="utf-8")
        git("add", "-A", cwd=pasta)
        git("commit", "-q", "-m", mensagem, cwd=pasta)
        return git("rev-parse", "HEAD", cwd=pasta)

    def pareceres(self, commit, p="aprovado", corpo=""):
        self.commitar(self.repo, {f"docs/{pasta}/exemplo.md": PARECER.format(tipo=tipo, c=commit, p=p, extra=EXTRA[tipo], corpo=corpo)
                                  for tipo, pasta in (("review", "reviews"), ("qa", "qa"))}, "pareceres")

    def rodar(self, *args, env=None):
        env = env or com_gh_falso()
        env["HOME"] = str(self.tmp / "home")
        inicio = time.monotonic()
        r = subprocess.run([sys.executable, str(FORGE_CHECK), "--raiz", str(self.repo), *map(str, args)], capture_output=True,
                           text=True, env=env, timeout=60)
        self.duracao = time.monotonic() - inicio
        return r.returncode, r.stdout, r.stderr

    def gerar(self, *extra, destino="dev-exemplo", env=None):
        return self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", f"forge:{destino}", "--branch", "melhoria/x",
                          "--base", "develop", *extra, env=env)


class Estado(Repo):
    def test_pr_mesclado_recusa_etapa_que_nao_e_de_merge(self):
        rc, saida, erro = self.gerar("--etapa", "codigo", env=com_gh_falso(script=GH_MERGED))
        self.assertEqual(rc, 1, saida)
        self.assertIn("estado: PR #7 MERGED head abcdef0", erro)
        self.assertIn("brief gerar: recusado: o PR #7 já foi mesclado", saida)
        self.pareceres(self.c1)
        rc, saida, erro = self.gerar("--etapa", "merge-integracao", destino="revisor-exemplo", env=com_gh_falso(script=GH_MERGED))
        self.assertEqual(rc, 0, saida + erro)

    def test_sem_gh_no_path_a_linha_e_nao_verificavel(self):
        so_git = Path(tempfile.mkdtemp(prefix="forge-so-git-"))
        self.addCleanup(shutil.rmtree, so_git, ignore_errors=True)
        (so_git / "git").symlink_to(shutil.which("git"))
        rc, saida, erro = self.gerar("--etapa", "codigo", env=dict(os.environ, PATH=str(so_git)))
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("estado: PR de melhoria/x não verificável (sem gh)", erro)
        rc, _, erro = self.gerar("--etapa", "codigo")
        self.assertIn("não verificável (gh sem rede ou sem acesso)", erro)

    def test_base_que_andou_conta_os_commits(self):
        for i in range(3):
            self.commitar(self.semente, {f"src/outro{i}.py": "x\n"}, f"outro {i}")
        git("push", "-q", "origin", "develop", cwd=self.semente)
        git("fetch", "-q", "origin", cwd=self.repo)
        _, _, erro = self.gerar("--etapa", "codigo")
        self.assertIn("estado: origin/develop 3 commits à frente do Base-sha", erro)

    def test_worktree_que_ja_existe(self):
        git("switch", "-q", "develop", cwd=self.repo)
        wt = self.tmp / "wt-x"
        git("worktree", "add", "-q", str(wt), "melhoria/x", cwd=self.repo)
        _, _, erro = self.gerar("--etapa", "codigo")
        self.assertIn(f"estado: worktree {wt} já existe para melhoria/x", erro)

    def test_parecer_desatualizado(self):
        self.pareceres(self.c1)
        self.commitar(self.repo, {"src/app.py": "v3\n"}, "mudou depois do parecer")
        _, _, erro = self.gerar("--etapa", "codigo")
        self.assertRegex(erro, r"estado: parecer review desatualizado \(")

    def test_gh_lento_respeita_o_teto(self):
        rc, saida, erro = self.gerar("--etapa", "codigo", env=com_gh_falso(script="sleep 30\n"))
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn("não verificável (gh passou de 10 s)", erro)
        self.assertLess(self.duracao, 25)


class Volta(Repo):
    ANTERIOR = ("Agente destino: forge:dev-exemplo\nPedido: exemplo\nBranch: melhoria/x   Base: develop   Base-sha: {base}\n\n"
                "## Objetivo\nRecurso.\n\n## Ler\n- o pedido.\n\n## Entregar\n- Recurso (E1).\n\n## Fora do escopo\n"
                '- "E1.2 (revisor-exemplo): merge na develop." · outra etapa\n\n## Decisões e restrições\n- DECISÃO DO DONO (2026-01-01): "A".\n\n'
                "## Pronto quando\n- PQ-1 (push): `git ls-remote origin refs/heads/melhoria/x` igual ao head local.\n\n## Relatório\nAté 8 linhas.\n")

    def anterior(self):
        base = git("merge-base", "origin/develop", "melhoria/x", cwd=self.repo)
        arq = self.repo / "docs" / "briefs" / "exemplo-dev-exemplo-1.md"
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(self.ANTERIOR.format(base=base), encoding="utf-8")
        (self.repo / ".git" / "info" / "exclude").write_text("docs/briefs/\n", encoding="utf-8")
        return base

    def test_ref_por_sha_mantem_a_branch_e_o_base_sha_do_anterior(self):
        base = self.anterior()
        self.pareceres(self.c1, p="reprovado", corpo="## Achados\n- A1 (bloqueante) src/app.py:1 · o valor está errado\n")
        head = git("rev-parse", "HEAD", cwd=self.repo)
        rc, saida, erro = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo",
                                     "--volta", "docs/briefs/exemplo-dev-exemplo-1.md", "--ref", head)
        self.assertEqual(rc, 0, saida + erro)
        self.assertIn(f"Branch: melhoria/x   Base: develop   Base-sha: {base}", saida)
        self.assertNotIn(f"Branch: {head}", saida)
        self.assertIn("A1", saida.split("## Entregar", 1)[1].split("## Fora do escopo", 1)[0])
        self.assertIn("volta: lido docs/reviews/exemplo.md parecer=reprovado bloqueantes=1", erro)

    def test_sem_parecer_lido_nao_ha_volta(self):
        self.anterior()
        rc, saida, _ = self.rodar("brief", "gerar", "--pedido", "exemplo", "--destino", "forge:dev-exemplo",
                                  "--volta", "docs/briefs/exemplo-dev-exemplo-1.md", "--ref", "melhoria/x")
        self.assertEqual(rc, 1)
        self.assertIn("nenhum parecer lido", saida)
        self.assertNotIn("## Entregar", saida)


if __name__ == "__main__":
    unittest.main()
