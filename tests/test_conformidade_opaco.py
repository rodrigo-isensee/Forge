"""A9 e A10 (E1.139, v047): destino opaco sem resto no hook `conformidade`, por gerador com oráculo pelo bash.

O gerador cruza o mecanismo do destino (D1), a forma do valor (D2) e o nome da origem (D4), sem resto depois da parte
opaca (D3), e amostra a posição na linha (D6) e o ambiente (D7). O esperado não vem da regra do hook: o bash calcula o
destino real (`printf %s <valor>` no repositório temporário, C22 da v2, AR-6) e o caso espera 2 se ele cai no `.git`
(o próprio `.git` ou dentro dele, como no literal `cp x .git/x`), senão 0. Formas que o bash lê mas o hook não (aninhado,
`eval`, `sh -c`, `$'…'`, operador colado) só entram com valor no `.git`: fora dele a recusa é falso positivo aceito (U2).
Orçamento: até 150 execuções do hook; pelo menos 10 com o prazo de produção (3 s)."""
import concurrent.futures
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_forge import ambiente_limpo  # noqa: E402
from test_hooks import Fixture, rodar  # noqa: E402

MECANISMOS = (  # D1: (nome, modelo, o destino que é pasta recebe o nome da origem)
    ("cp", "cp {o} {d}", True), ("mv", "mv {o} {d}", True), ("install", "install {o} {d}", True),
    ("ln-s", "ln -s {o} {d}", True), ("ln", "ln {o} {d}", True), (">", "echo a > {d}", False),
    (">>", "echo a >> {d}", False), ("tee", "echo a | tee {d}", False), ("dd", "dd if={o} of={d}", False))
LEGIVEIS = (  # D2 que o hook lê: (nome, prefixo da linha, destino); `{v}` é o valor e `{g}` o valor com curinga
    ("echo", "", '"$(echo {v})"'), ("printf", "", '"$(printf %s {v})"'), ("crase", "", "`echo {v}`"),
    ("funcao", "f(){{ echo {v}; }}; ", '"$(f)"'), ("variavel", "d=$(echo {v}); ", '"$d"'),
    ("padrao", "", '"${{GITD:-{v}}}"'), ("curinga", "", '"$(echo {g})"'))
ILEGIVEIS = (  # D2 que o hook não lê (U2) ou de operador colado (A10): só com valor no `.git`
    ("aninhado", "", "$(echo $(echo {v}))"), ("eval", "", '"$(eval echo {v})"'), ("sh-c", "", "\"$(sh -c 'echo {v}')\""),
    ("ansi-c", "", "\"$(echo $'{v}')\""), ("colado", "", '"$(git rev-parse --git-dir;)"'))
NO_GIT = (".git", ".git/hooks", ".git/config")
FORA = ("docs", "src")
ORIGENS = ("config", "pre-push", "x")  # D4: nome do git, nome de hook, neutro
POSICOES = (  # D6
    lambda c: c, lambda c: f"true; {c}", lambda c: f"true && {c}", lambda c: f"false || {c}", lambda c: f"echo | {c}",
    lambda c: f"({c})", lambda c: f"bash <<'EOF'\n{c}\nEOF", lambda c: c.replace(" ", " \\\n", 1))
TETO_DE_EXECUCOES = 150


def com_curinga(valor):
    return valor[:-1] + "?"


def casos():
    """(nome, linha, prefixo e destino para o oráculo, ambiente D7, prazo de produção) de cada caso gerado."""
    gerados = []
    for i, ((mec, modelo, _), (forma, prefixo, destino)) in enumerate(itertools.product(MECANISMOS, LEGIVEIS + ILEGIVEIS)):
        gerados.append((mec, modelo, forma, prefixo, destino, NO_GIT[i % 3], ORIGENS[i // 3 % 3]))
    for i, ((mec, modelo, _), (forma, prefixo, destino)) in enumerate(zip(itertools.cycle(MECANISMOS), LEGIVEIS * 4)):
        gerados.append((mec, modelo, forma, prefixo, destino, FORA[i % 2], "x"))
    saida = []
    for n, (mec, modelo, forma, prefixo, destino, valor, origem) in enumerate(gerados):
        destino = destino.format(v=valor, g=com_curinga(valor))
        prefixo = prefixo.format(v=valor)
        linha = POSICOES[n % len(POSICOES)](prefixo + modelo.format(o=origem, d=destino))
        no_git = valor in NO_GIT
        ambiente = ("clone" if n % 31 == 7 else "worktree" if n % 9 == 4 else "projeto") if no_git else "projeto"
        saida.append((f"{n:03d}-{mec}-{forma}-{valor}-{origem}-{ambiente}", linha, prefixo, destino, ambiente,
                      n % 13 == 0, origem if dict((m, p) for m, _, p in MECANISMOS)[mec] else None))
    return saida


def dados_do_caso(linha, ambiente):
    """O fixture do caso, no formato de tests/hooks (`test_hooks.Fixture`)."""
    dados = {"arquivos": {"x": "x\n", "config": "c\n", "pre-push": "p\n", "docs/a.md": "a\n", "src/app.js": "v1\n"},
             "env": {"CLAUDE_PROJECT_DIR": "{tmp}/proj"}, "git": [{"branch": "melhoria/x"}],
             "entrada": {"tool_name": "Bash", "tool_input": {"command": linha}, "agent_type": "forge:tech-lead",
                         "hook_event_name": "PreToolUse", "tool_use_id": "toolu_9"}}
    if ambiente == "worktree":
        dados["env"]["CLAUDE_PROJECT_DIR"] = "{tmp}/wt"
        dados["git"] = [{"worktree": "wt", "branch": "melhoria/w"}]
        dados["entrada"]["cwd"] = "{tmp}/wt"
    elif ambiente == "clone":  # clone do Forge com papel de lista (conferente): a `Guarda` age
        dados.update(forge=False, git=[])
        dados["arquivos"][".claude-plugin/plugin.json"] = '{"name": "forge"}'
        dados["env"]["HOME"] = "{tmp}/home"
        dados["entrada"]["agent_type"] = "forge:conferente"
    return dados


def destino_real(pasta, prefixo, destino, origem):
    """O oráculo: o caminho que o bash grava (`printf %s` do destino, na pasta do caso), com o nome da origem quando o
    destino é uma pasta e o mecanismo o recebe; None se o bash não o calcula."""
    env = ambiente_limpo()
    env.update(HOME=str(pasta), LC_ALL="C")
    r = subprocess.run(["bash", "--norc", "--noprofile", "-c", f"{prefixo}printf %s {destino}"], cwd=pasta, env=env,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=10)
    if r.returncode or not r.stdout:
        return None
    alvo = Path(pasta, r.stdout)
    return alvo / origem if origem and alvo.is_dir() else alvo


def cai_no_git(pasta, alvo):
    """O alvo é o `.git` da pasta (arquivo na worktree) ou fica dentro dele ou do diretório comum do git."""
    env = ambiente_limpo()
    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir"], cwd=pasta,
                       env=env, capture_output=True, text=True, timeout=10)
    bases = {Path(os.path.realpath(pasta / ".git"))} | {Path(os.path.realpath(p)) for p in r.stdout.split()}
    real = Path(os.path.realpath(alvo))
    return any(real == b or b in real.parents for b in bases)


class DestinoOpacoSemResto(unittest.TestCase):
    def test_gerador_cobre_as_dimensoes_dentro_do_orcamento(self):
        gerados = casos()
        self.assertLessEqual(len(gerados), TETO_DE_EXECUCOES)
        self.assertGreaterEqual(len(gerados), 100)
        nomes = [g[0] for g in gerados]
        for mec, _, _ in MECANISMOS:
            self.assertTrue(any(f"-{mec}-" in n for n in nomes), mec)
        for forma, _, _ in LEGIVEIS + ILEGIVEIS:
            self.assertTrue(any(f"-{forma}-" in n for n in nomes), forma)
        for origem in ORIGENS:
            self.assertGreaterEqual(sum(f"-{origem}-" in n for n in nomes), 3, origem)
        for ambiente in ("projeto", "worktree", "clone"):
            self.assertGreaterEqual(sum(g[4] == ambiente for g in gerados), 3, ambiente)
        for i in range(len(POSICOES)):
            self.assertGreaterEqual(sum(1 for n in range(len(gerados)) if n % len(POSICOES) == i), 3)
        self.assertGreaterEqual(sum(g[5] for g in gerados), 10, "casos com o prazo de produção")

    def test_hook_concorda_com_o_bash(self):
        gerados = casos()
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
            resultados = list(pool.map(self.rodar_caso, gerados))
        no_git = 0
        for (nome, linha, *_), (esperado, obtido, erro) in zip(gerados, resultados):
            with self.subTest(caso=nome):
                self.assertIsNotNone(esperado, f"o bash não calculou o destino de {linha!r}")
                no_git += esperado == 2
                self.assertEqual(obtido, esperado, f"{linha!r}: {erro}")
        self.assertGreaterEqual(no_git, 50, "casos com destino real no .git")

    def rodar_caso(self, caso):
        _, linha, prefixo, destino, ambiente, producao, origem = caso
        tmp = Path(tempfile.mkdtemp(prefix="forge-opaco-"))
        try:
            dados = dados_do_caso(linha, ambiente)
            raiz, entrada = Fixture(Path("conformidade/gerado.json"), dados).montar(tmp, os.getpid())
            pasta = Path(entrada.get("cwd") or raiz)
            alvo = destino_real(pasta, prefixo, destino, origem)
            esperado = None if alvo is None else 2 if cai_no_git(pasta, alvo) else 0
            extra = {k: v.replace("{tmp}", str(tmp)) for k, v in dados["env"].items()}
            r = rodar("conformidade", entrada, raiz, None, extra, producao=producao)
            return esperado, r.returncode, r.stderr.strip()[:300]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
