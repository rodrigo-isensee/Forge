"""0.47.8 E3.19 (GH-REMOTO-NA-LINHA): o gerador sobre a matriz da cópia alheia do hook `parecer` (docs/hooks.md).

Numa cópia git alheia, sem `-R`, o gh age no repositório do GH_REPO e dos remotos dela, que o hook lê antes de a linha
rodar. Cada dimensão que dá valor a eles na mesma linha (D1 a D6) é cruzada com a posição na linha e com `gh pr ready` e
`gh pr merge`; as sondas S14 a S26 dos pareceres de segurança e de review (E3.16, E3.17) vão por extenso, e o corpus
legítimo segue com 0. A montagem é a da fixture `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia` (sessão no
clone `dono/forge` sem parecer, cópia alheia `outro/coisa`), feita uma vez; o hook roda uma vez por linha."""
import concurrent.futures
import copy
import itertools
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forge import minimo  # noqa: E402
from test_hooks import FIXTURES, Fixture, montar_proc, rodar  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
import parecer  # noqa: E402

BASE = FIXTURES / "parecer" / "incidente-r-copia-alheia-source-gh-repo-ready-bloqueia.json"
FORGE = "git@github.com:dono/forge.git"
CONFIG_DO_FORGE = '[remote "origin"]\n\tgh-resolved = dono/forge\n'
ARQUIVOS = {"vars": "GH_REPO=dono/forge\n", "g.cfg": CONFIG_DO_FORGE, "h/.gitconfig": CONFIG_DO_FORGE,
            "x/git/config": CONFIG_DO_FORGE, "muda.sh": f"git remote add upstream {FORGE}\n"}
GH = ("gh pr ready feature/x", "gh pr merge feature/x")

# Comando à parte, antes do gh (D1, D2 e D5), cruzado com POSICOES
ANTES = {
    "D1": ("command -p . ./env.sh", "command -- source ./env.sh", "builtin -- source ./env.sh", "command -p -- . ./env.sh"),
    "D2": ("c=source; $c env.sh", "c=.; ${c} ./env.sh", 'c=source; "$c" env.sh', "$(echo source) env.sh"),
    "D5": (f"git remote add upstream {FORGE}", f"git remote set-url origin {FORGE}",
           "git config remote.origin.gh-resolved dono/forge", "git -c remote.origin.gh-resolved=dono/forge status",
           "echo '[remote \"u\"]' >> .git/config", "sh muda.sh", "gh repo set-default dono/forge"),
}
POSICOES = ("{x}; {gh}", "{x} && {gh}", "{x}\n{gh}", "if {x}; then {gh}; fi", "{{ {x}; }} && {gh}")
# D4: a variável do config do git, de prefixo do gh, exportada antes e declarada antes
VARIAVEIS_DO_GIT = ("GIT_CONFIG_GLOBAL=g.cfg", "GIT_CONFIG_SYSTEM=g.cfg", "GIT_CONFIG_COUNT=1",
                    "GIT_CONFIG_PARAMETERS=\"'remote.origin.gh-resolved'='dono/forge'\"", "GIT_DIR=../proj/.git",
                    "HOME=$PWD/h", "XDG_CONFIG_HOME=$PWD/x")
POSICOES_DA_VARIAVEL = ("{v} {gh}", "export {v}; {gh}", "declare -x {v} && {gh}")
# D4, atribuição por expansão (A5 do review da E3.21): `${N:=v}` e `${N=v}` com `set -a`, em argumento, com aspas e em
# here-string; de elemento (`${N[0]:=v}`)
EXPANSOES = ("GH_REPO:=dono/forge", "GH_REPO=dono/forge", "GIT_CONFIG_GLOBAL:=g.cfg", "XDG_CONFIG_HOME:=$PWD/x",
             "HOME=$PWD/h", "GIT_DIR[0]:=../proj/.git")
POSICOES_DA_EXPANSAO = ("set -a; : ${{{e}}}; {gh}", 'set -a; echo "${{{e}}}" >/dev/null && {gh}',
                        "set -a; cat <<<${{{e}}}; {gh}")
# D3 e D6: a forma inteira, com o gh no lugar
INTEIRAS = {
    "D3": ("env $(cat vars) {gh}", 'v=GH_REPO=dono/forge; env "$v" {gh}', "env -- $(cat vars) {gh}",
           "c=env; $c GH_REPO=dono/forge {gh}"),
    "D6": ('d=../alheio2; cd "$d" && {gh}', 'cd "$(echo ../alheio2)" && {gh}'),
}
LEGITIMOS = ("{gh}", 'export PATH="$HOME/bin:$PATH"; {gh}', 'for f in $(ls); do echo "$f"; done; {gh}',
             'read -r -p "$pergunta" resposta; {gh}', "{gh} && echo feito", "cd . && {gh} 2>&1",
             "GH_PAGER=cat {gh}", "export LANG=C; {gh} >/dev/null",
             'set -a; : "${{GH_REPO:-dono/forge}}"; {gh}', "echo ${{HOME:+x}} ${{GH_REPO:?}}; {gh}",
             ": ${{PAGER:=less}}; {gh}")
SONDAS = {  # por extenso, como nos pareceres
    "S14": "command -p . ./env.sh; gh pr ready feature/x",
    "S15": "command -- source ./env.sh; gh pr ready feature/x",
    "S16": "builtin -- source ./env.sh; gh pr ready feature/x",
    "S17": "c=source; $c env.sh; gh pr ready feature/x",
    "S18a": "env $(cat vars) gh pr ready feature/x",
    "S18b": "env $(cat vars) gh pr merge feature/x",
    "S19a": "GIT_CONFIG_GLOBAL=g.cfg gh pr ready feature/x",
    "S19b": "export GIT_CONFIG_GLOBAL=g.cfg; gh pr ready feature/x",
    "S20": "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.gh-resolved GIT_CONFIG_VALUE_0=dono/forge gh pr ready "
           "feature/x",
    "S21": "export GIT_CONFIG_PARAMETERS=\"'remote.origin.gh-resolved'='dono/forge'\"; gh pr ready feature/x",
    "S22a": "HOME=$PWD/h gh pr ready feature/x",
    "S22b": "export XDG_CONFIG_HOME=$PWD/x; gh pr ready feature/x",
    "S23": f"git remote add upstream {FORGE} && gh pr ready feature/x",
    "S24": f"git remote set-url origin {FORGE}; gh pr ready feature/x",
    "S25a": "git config remote.origin.gh-resolved dono/forge; gh pr ready feature/x",
    "S25b": f"git config url.{FORGE}.insteadOf git@github.com:outro/coisa.git; gh pr ready feature/x",
    "S26": "command -- . ./env.sh; gh pr ready feature/x",
    "S28a": "set -a; : ${GH_REPO:=dono/forge}; gh pr ready feature/x",
    "S28b": 'set -a; : "${GH_REPO:=dono/forge}"; gh pr ready feature/x',
    "S28c": "set -a; echo ${GH_REPO:=dono/forge}; gh pr ready feature/x",
    "S29a": "set -a; : ${XDG_CONFIG_HOME:=$PWD/x}; gh pr merge feature/x",
    "S29b": "set -a; : ${GIT_CONFIG_GLOBAL:=g.cfg}; gh pr ready feature/x",
    "S29c": "n=GH_REPO; set -a; : ${!n:=dono/forge}; gh pr ready feature/x",
}


def gerar():
    """[(nome, linha, código esperado)] da matriz: cada dimensão × posição × gh, as sondas e os legítimos."""
    casos = [(f"{d}/{p}/{g.split()[2]}/{i}", p.format(x=x, gh=g), 2)
             for d, formas in ANTES.items() for i, x in enumerate(formas) for p in POSICOES for g in GH]
    casos += [(f"D4/{p}/{g.split()[2]}/{v}", p.format(v=v, gh=g), 2)
              for v, p, g in itertools.product(VARIAVEIS_DO_GIT, POSICOES_DA_VARIAVEL, GH)]
    casos += [(f"D4/{p}/{g.split()[2]}/{e}", p.format(e=e, gh=g), 2)
              for e, p, g in itertools.product(EXPANSOES, POSICOES_DA_EXPANSAO, GH)]
    casos += [(f"{d}/{f}/{g.split()[2]}", f.format(gh=g), 2) for d, formas in INTEIRAS.items() for f in formas for g in GH]
    casos += [(s, linha, 2) for s, linha in SONDAS.items()]
    casos += [(f"legitimo/{f}/{g.split()[2]}", f.format(gh=g), 0) for f in LEGITIMOS for g in GH]
    return casos


class MatrizDaCopiaAlheia(unittest.TestCase):
    def test_cada_dimensao_posicao_e_gh_recusa_e_o_legitimo_passa(self):
        casos = minimo(gerar(), 190, "matriz da cópia alheia")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        f = Fixture(BASE)
        dados = copy.deepcopy(f.dados)
        dados["repos"]["alheio"]["arquivos"].update(ARQUIVOS)
        dados["repos"]["alheio2"] = {"remotos": {"origin": FORGE}}
        raiz, entrada = Fixture(BASE, dados).montar(tmp, os.getpid())
        proc = montar_proc(tmp, None)
        extra = {k: v.replace("{tmp}", str(tmp)) for k, v in dados["env"].items()}
        extra["FORGE_NPROC"] = "8"

        def um(linha):
            e = copy.deepcopy(entrada)
            e["tool_input"]["command"] = linha
            return rodar("parecer", e, raiz, proc, extra)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            resultados = list(pool.map(um, [linha for _, linha, _ in casos]))
        for (nome, linha, codigo), r in zip(casos, resultados):
            with self.subTest(caso=nome, linha=linha):
                self.assertEqual(r.returncode, codigo, r.stderr)
                self.assertEqual(r.stdout, "")
                if codigo == 2:
                    self.assertIn("R-REVIEW", r.stderr)
                else:
                    self.assertEqual(r.stderr, "")
        # sessão fora de cópia de trabalho: não há clone com parecer a conferir, e a cópia alheia segue como antes
        r = rodar("parecer", dict(entrada, tool_input={"command": SONDAS["S23"]}), raiz, proc,
                  dict(extra, CLAUDE_PROJECT_DIR=str(tmp)))
        self.assertEqual((r.returncode, r.stderr), (0, ""))


class RegrasPorClasse(unittest.TestCase):
    """As funções de cada regra, direto: o ramo que recusa e o vizinho que passa."""

    def test_d1_opcoes_depois_de_builtin_e_command(self):
        for palavras in (["command", "-p", ".", "./env.sh"], ["builtin", "--", "source", "x"],
                         ["command", "-p", "--", "builtin", "--", ".", "x"]):
            self.assertEqual(parecer.mexidas_na_linha(palavras), frozenset(parecer.SENSIVEIS), palavras)
        self.assertEqual(parecer.mexidas_na_linha(["command", "-p", "ls"]), frozenset())

    def test_d2_nome_por_expansao_e_caminho_de_variavel(self):
        for nome in ("$c", "${c}", "$(…)", "`echo source`", "$c$d"):
            self.assertTrue(parecer.nome_incerto(nome), nome)
            self.assertEqual(parecer.mexidas_na_linha([nome, "env.sh"]), frozenset(parecer.SENSIVEIS), nome)
        for nome in ("$F/bin/x", "${F}/x", "./x", "source", "$F/a/b"):
            self.assertFalse(parecer.nome_incerto(nome), nome)
        self.assertEqual(parecer.mexidas_na_linha(["$F/bin/x", "a"]), frozenset())

    def test_d4_classe_do_config_do_git(self):
        self.assertEqual(parecer.mexidas_na_linha(["GIT_CONFIG_KEY_0=x", "gh", "pr"]), frozenset({"GIT_CONFIG_KEY_0"}))
        self.assertEqual(parecer.mexidas_na_linha(["export", "GIT_CONFIG_GLOBAL=g"]), frozenset({"GIT_CONFIG_GLOBAL"}))
        for mexidas in ({"GIT_CONFIG_PARAMETERS"}, {"HOME"}, {"XDG_CONFIG_HOME"}, {"GIT_DIR"}):
            self.assertTrue(parecer.mexe_no_config_do_git(frozenset(mexidas)), mexidas)
        for mexidas in (set(), {"CDPATH"}, {"GH_REPO"}, {"GH_CONFIG_DIR"}):
            self.assertFalse(parecer.mexe_no_config_do_git(frozenset(mexidas)), mexidas)

    def test_d4_atribuicao_por_expansao(self):
        for texto, nomes in ((": ${GH_REPO:=x}", {"GH_REPO"}), ('echo "${GIT_CONFIG_GLOBAL=g}"', {"GIT_CONFIG_GLOBAL"}),
                             ("cat <<<${HOME[0]:=h} > ${XDG_CONFIG_HOME:=x}", {"HOME", "XDG_CONFIG_HOME"}),
                             ("echo ${A:-${GIT_DIR:=d}}", {"GIT_DIR"})):
            self.assertEqual(parecer.mexidas_por_expansao(texto), frozenset(nomes), texto)
        self.assertEqual(parecer.mexidas_por_expansao(": ${!n:=x}"), frozenset(parecer.SENSIVEIS))
        for texto in (": ${GH_REPO:-x} ${HOME:+y} ${GIT_DIR:?z} ${#HOME} ${HOME/a=b}", ": ${PAGER:=less}", "HOME=x",
                      ": $GH_REPO=x"):
            self.assertEqual(parecer.mexidas_por_expansao(texto), frozenset(), texto)

    def test_d5_programas_que_mantem_os_remotos(self):
        for linha in ("gh pr ready x", "export A=1; gh pr ready x", "for f in $(ls); do echo $f; done; gh pr merge x",
                      "gh pr ready x >/dev/null 2>&1", "cd . && gh pr view x"):
            self.assertTrue(parecer.linha_mantem_os_remotos(linha), linha)
        for linha in ("git status; gh pr ready x", "echo a >> .git/config; gh pr ready x", "gh pr ready x > log",
                      "gh repo set-default dono/forge; gh pr ready x", "gh pr checkout 1; gh pr ready x",
                      "gh pr; gh pr ready x", "./muda.sh; gh pr ready x", "x=$(git remote add u y); gh pr ready x",
                      "echo a &> f; gh pr ready x", "gh pr ready x 'aberto"):
            self.assertFalse(parecer.linha_mantem_os_remotos(linha), linha)


if __name__ == "__main__":
    unittest.main()
