#!/usr/bin/env python3
"""Forge: parecer de review e de QA antes de PR e de merge (ADR 0003, R-REVIEW, R-QA).

PreToolUse (Bash) com `gh pr create`, `gh pr merge`, `gh api .../pulls/<n>/merge`, ou `git merge <branch>` e
`git pull <remoto> <branch>` na branch de integração: exige parecer aprovado e válido para a branch (validado pelo
forge-check, ADR 0004); com pipeline, contêiner ou IaC no diff, também o de devops (R-REVIEW); com gatilho de segurança, o
de segurança (R-SEGURANCA). A branch atual acompanha `cd`, `git checkout` e `git switch` anteriores na mesma linha. A
pasta do git é a que o bash e o git calculam (`cd` no nível de cima da linha, cada `-C` em ordem e `~`), só com caminho
literal; o que o hook não resolve (variável, crase, `$( )`, `cd` em subshell, pipeline, segundo plano, condicional
(`if cd`, `! cd`) ou bloco, pasta inexistente, `popd`, `pushd`, `--git-dir`, `--work-tree`, `GIT_DIR`) recusa o merge e o pull, nunca é julgado pela pasta
da sessão (HK3-PARECER, E1 e E3).
Os pareceres exigidos são os do forge-check (P5, `exigidos_do_pr`: a classe T dispensa o QA e exige o review; os gatilhos de
segurança e devops somam por cima); `.md` de controle (`agents/`, `skills/`, `stacks/*/agents|skills/`, `stacks/*/seguranca.md` e `pronto.md`, `docs/regras/`, `templates/projeto/`, `CLAUDE.md`) não tem isenção. Libera
atualização a partir de uma branch de integração e promoção entre branches de integração. O merge de PR (ADR 0008, 4.3) é resolvido sem rede, pela branch: base `main` é `R-MAIN`;
PR só por número, `gh api` de merge e merge no Forge a partir de projeto são `R-CONTRIB`.
No clone do Forge (`raiz_de_estado`: `~/Forge` e as worktrees de `~/.forge-contrib/wt/`) age também, sem
`hooks_desligados`, e o PR fica em rascunho até o parecer: `gh pr create --draft` passa sem parecer e `gh pr ready`
exige o parecer, como o merge (o GitHub não mescla PR em rascunho).
O `gh pr` rodado fora de cópia de trabalho (com `-R`/`--repo`, `GH_REPO=` ou a URL do PR) é conferido no clone da sessão
que tem remoto desse repositório; sem ele, recusa (INCIDENTE-HOOK-PARECER-CONTORNADO, `pasta_do_gh`). Fora de clone e
de projeto, GH_REPO exportado antes na linha recusa: o hook não lê o valor (GH-REPO-EXPORTADO).
O `gh pr create` fora do rascunho decide pelo resultado que o `forge-check pr` gravou para o mesmo head, branch e base
(PR-HOOK-PRAZO, `verificar` com `gravado`): sem o aprovado, recusa e diz o comando a rodar antes. O `gh pr ready` e o
`gh pr merge` usam o mesmo resultado como atalho (E2.117): o aprovado do mesmo head e base decide sem refazer a checagem, o
reprovado recusa e, sem ele, a conferência de hoje decide como antes (o prazo vencido diz o comando que grava o resultado).
Falha fechado nas ações críticas (ADR 0009, seção 7), também no clone do Forge.
"""
import ast
import collections
import functools
import json
import os
import re
from pathlib import Path
from types import SimpleNamespace

from _comum import (CONTORNO_DA_GRAMATICA, CONTORNO_DO_TETO, INTEGRACAO, OPACO, OPCAO_DE_REAVALIACAO, PLUGIN,
                    PROFUNDIDADE, SHELLS_DA_REAVALIACAO, LancadorDemais, TextoDivididoAberto, bloquear,
                    contorno_da_reavaliacao, conteudos_de_crase, copia_de_trabalho, formas_que_o_shell_le, corpo_so_lido, depois_das_atribuicoes, e_clone_do_forge,
                    excede_o_teto, executar,
                    fora_da_gramatica_com_heredoc, forge_check, git, nome_da_branch, nome_do_caminho, leituras, motivo_da_reavaliacao,
                    palavras_do_texto, programas_e_atribuicoes, raiz_declarada, raiz_de_estado, reavaliacao, reavaliacao_das_palavras, reduzida, sem_atribuicoes,
                    separar_lancadores, separar_regra, tirar_heredocs)
from _gh_api import expande, textos_do_gh_api  # GH-API-LEITURA-UNICA: a palavra que o bash expande e a leitura do gh api

MERGE = r"merge(?!-base\b)"  # `git merge-base` só lê o grafo (HK3-PARECER, E2): não é merge
PREFILTRO = re.compile(rf"\bgh\b.*\bpr\b.*\b(create|{MERGE}|ready)\b|\bgh\b.*\bapi\b|\bgit\b.*\b({MERGE}|pull)\b", re.S)
class MERGE_DE_PR:  # noqa: N801 - o `prazo_longo` do `executar`, que espera a interface de um regex (`.search`)
    """A linha com `gh pr merge` como palavras de um comando ganha o prazo `PRAZO_DO_MERGE_S` (v0455; com a máquina carregada,
    o `forge-check pr` passa dele, e o resultado gravado do mesmo head decide antes: E2.117). A menção em comentário, string ou corpo de heredoc não ganha (A1 da segurança da 0.45.5).
    Só dá mais prazo, nunca libera; o prazo vencido segue recusando, e a dúvida ao ler fica com os 3 s."""

    @staticmethod
    def search(texto):
        try:
            simples = palavras_do_texto(tirar_heredocs(texto)[0]).simples
        except Exception:  # noqa: BLE001 - na dúvida, o prazo comum: menos tempo, nunca uma liberação
            return None
        for comando in simples:
            valores = [Path(p.valor).name if i == 0 else p.valor for i, p in enumerate(comando.palavras)]
            if any(tuple(valores[i:i + 3]) == ("gh", "pr", "merge") for i in range(len(valores))):
                return True
        return None
CRITICO = re.compile(rf"\bpr\b.*\b(create|{MERGE}|ready)\b|\bapi\b|\b({MERGE}|pull)\b", re.S)
# A palavra crítica só no texto (HK3-PARECER, E2). `sed -n <N,Mp> <arquivos>` só imprime: vale `cat <arquivos>` (só números,
# sem metacaractere: a troca não muda o que o bash lê). `sh -c` cujo texto só usa estes programas não roda merge, pull nem gh pr.
SED_LE = re.compile(r"(?<![^\s;&|(])sed -n (['\"]?)\d+(?:,\d+)?p\1((?: +[\w./~@:+%,][\w./~@:+%,=-]*)*)(?=[ \t]*(?:[;&|)\n]|$))")
# Chamada só de `cat` (sem aspa, `$`, `#`, `;`, `&`, `|` nem parêntese: nada que mude como o bash lê as linhas): os corpos de
# heredoc dela são texto, e a gramática positiva do D (a rede contra o que o leitor não vê) não tem o que recusar.
SO_CAT = re.compile(r"(?:[ \t]*cat(?:[ \t]+>{0,2}[ \t]*[\w./~@:+%,-]+)*[ \t]*(?:\n|$))+")
# `<<`/`<<-` seguido de `'PALAVRA'`, `"PALAVRA"` ou `PALAVRA` (só \w): o bash e o hook cortam o corpo no mesmo ponto.
HEREDOC_SIMPLES = re.compile(r"(?<!<)<<(-?)[ \t]*(?:'(\w+)'|\"(\w+)\"|(\w+))(?=[ \t]|$)")
# HOOK-TEXTO-COM-MERGE: o alvo do `cat > arq <<` entre aspas ou com `$NOME`/`${NOME}` (`"$TMPDIR/x.md"`, `'docs/a b.md'`)
# grava um arquivo como o alvo literal da K1: a rede D o lê como `cat > _` e decide o resto como antes. Sem `\`, aspa de
# dentro, `$(`, `${X:-…}` nem crase: o bash lê essa palavra como uma só, sem rodar nada.
VARIAVEL = r"\$(?:[A-Za-z_]\w*|\{[A-Za-z_]\w*\})"
ALVO_DO_CAT = re.compile(rf"(?<![^\s;&|(])(cat[ \t]+>>?[ \t]*)(?:\"(?:[\w./:@,+%~^ -]|{VARIAVEL})+\"|'[\w./:@,+%~^ -]+'"
                         rf"|{VARIAVEL}[\w./:@,+%~^-]*)(?=[ \t]+<<)")
LE_O_TEXTO = {"grep", "cat"}
SO_ESPERA = {"sleep", "echo", ""}
CONTROLE = {"if", "elif", "while", "until", "!", "then", "do", "else", "fi", "done"}
CREATE_COM_VALOR = {"-a", "--assignee", "-B", "--base", "-b", "--body", "-F", "--body-file", "-H", "--head", "-l",
                    "--label", "-m", "--milestone", "-p", "--project", "-r", "--reviewer", "-t", "--title", "-T",
                    "--template", "-R", "--repo", "--recover"}
READY_COM_VALOR = {"-R", "--repo"}
VERDADE = {"1", "t", "true"}  # o que o `gh` aceita como verdadeiro em `--draft=<valor>`
MERGE_PR_COM_VALOR = {"-b", "--body", "-F", "--body-file", "-t", "--subject", "-A", "--author-email",
                      "--match-head-commit", "-R", "--repo"}
API_COM_VALOR = {"-X", "--method", "-H", "--header", "-f", "--raw-field", "-F", "--field", "--input", "-q", "--jq",
                 "-t", "--template", "--hostname", "--cache", "-p", "--preview"}
ENDPOINT_MERGE = re.compile(r"pulls/\d+/merge\b")
NUMERO_OU_URL = re.compile(r"^(#?\d+|https?://\S+)$")
MERGE_COM_VALOR = {"-m", "-F", "-s", "-X", "--message", "--file", "--strategy", "--strategy-option", "--into-name"}
PULL_COM_VALOR = {"-s", "-X", "--strategy", "--strategy-option", "--depth", "--deepen", "--shallow-since",
                  "--shallow-exclude", "-j", "--jobs", "--upload-pack", "-o", "--server-option"}
CRIA_BRANCH = {"-b", "-B", "-c", "-C", "--create", "--force-create", "--orphan"}
MERGE_SEM_ALVO = {"--abort", "--continue", "--quit", "--skip"}
GIT_COM_VALOR = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# A pasta em que o git roda (HK3-PARECER, E1 e E3): o hook a calcula como o bash e o git. Ela só se resolve com caminho
# literal (`~` no início da palavra incluído); variável, crase, `$( )` e o resto são desconhecidos, e o merge ou o pull
# nela recusa, seja qual for a branch da sessão (docs/security/hk3-parecer-ameacas.md). Variável o hook não segue.
SEGUE = {"", ";", "&&", "\n", "&&\n"}  # liga ao comando seguinte sem pipeline, `||` nem segundo plano
COMECA = {"", ";", "\n"}  # o comando que vem depois deles roda sempre; depois de `&&` ele pode não rodar
CORPO = {"{", "then", "do", "else"}
CONDICAO = {"if", "elif", "while", "until", "!", "time", "function"}  # abrem a parte; o `cd` depois delas roda
SUBCOMANDOS = {"merge", "pull", "checkout", "switch"}
ABRE = {"if", "while", "until", "for", "case", "select", "then", "do", "else", "elif", "{", "function", "coproc"}
LE_VARIAVEL = {"source", ".", "eval", "read", "mapfile", "readarray", "getopts", "for", "select", "let", "declare",
               "typeset", "local", "readonly", "unset", "set", "printf"}  # mexem em variável sem `NOME=` na palavra
# GH-REPO-DE-ARQUIVO (A5 da E3.13): `source` e `.` leem um arquivo que pode definir qualquer variável; NOMEIA, os comandos
# cujas palavras são nomes (o `export` também); LE_COM_VALOR, as opções do `read` cuja palavra seguinte é valor, não nome
CARREGA_ARQUIVO = {"source", "."}
NOMEIA = {"export", "declare", "typeset", "local", "readonly", "unset"}
LE_COM_VALOR = {"-p", "-d", "-t", "-n", "-N", "-u", "-i"}
DESVIOS = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
# 0.45.4: as variáveis que mudam o config.yml que o gh lê (e os aliases dele); mexidas antes na linha, o alias fica incerto
CONFIG_DO_GH = {"GH_CONFIG_DIR", "XDG_CONFIG_HOME", "HOME"}
SENSIVEIS = DESVIOS | {"HOME", "CDPATH", "GH_REPO"} | CONFIG_DO_GH  # o bash, o git e o gh os leem sozinhos: mexidos na
# linha, a pasta (ou o alias do gh, ou o repositório do gh: GH-REPO-EXPORTADO) fica desconhecida
ATRIBUICAO = re.compile(r"^([A-Za-z_]\w*)\+?=")
# GH-REMOTO-NA-LINHA (E3.19, matriz em docs/hooks.md): D2, o caminho de variável simples com `/` literal antes do nome é
# arquivo, nunca builtin nem função; D4, o config que o git do gh lê (todo `GIT_*`, HOME, XDG_CONFIG_HOME); D5, os
# programas que não mudam os remotos da cópia e os `gh pr` que só os leem
CAMINHO_DE_VARIAVEL = re.compile(r"(?:[^$`(){}]|\$[A-Za-z_]\w*|\$\{[A-Za-z_]\w*\})*/[^$`/(){}]+")
CONFIG_DO_GIT = {"HOME", "XDG_CONFIG_HOME"}
# D4 (A5 do review da E3.21): `${N:=v}` e `${N=v}`, também de elemento (`${N[0]:=v}`) e indireta (`${!n:=v}`)
EXPANSAO_QUE_ATRIBUI = re.compile(r"\$\{(!?)([A-Za-z_]\w*)(?:\[[^]}]*\])?:?=")
# D4 (A10 da segurança da E3.27): a aritmética também dá valor (`$((N=0))`, `$[N+=1]`, `((N++))`, `let N-=1`, `${A[N=0]}`,
# `${P:N=0:0}`); o nome seguido de operador de atribuição (não `==`, `!=`, `<=`, `>=`) ou precedido de `++`/`--`.
# O `=` simples só conta com um contexto aritmético no texto (ABRE_ARITMETICA): sem ele, `N=v` é a atribuição do shell,
# que `mexidas_na_linha` já lê na ordem (`GH_CONFIG_DIR=x gh <alias>` segue lendo o alias)
ATRIBUICAO_ARITMETICA = re.compile(r"(?<![\w$])([A-Za-z_]\w*)"
                                   r"(?=(?:\[[^]]*\])?\s*((?:[-+*/%&^|]|<<|>>)?=(?!=)|\+\+|--))"
                                   r"|(?:\+\+|--)\s*([A-Za-z_]\w*)")
ABRE_ARITMETICA = re.compile(r"\(\(|\$\[|\[|\$\{|\b(?:let|declare|typeset|local)\b")  # `[`: subscrito; `declare -i`
SO_LEEM_A_COPIA = frozenset({"cd", "echo", "printf", "true", "false", ":", "test", "[", "export", "declare", "typeset",
                             "local", "readonly", "read", "set", "unset", "shift", "pwd", "sleep", "for", "done", "fi",
                             "}", "ls", "cat", "wc", "head", "tail", "grep", "stat"})
GH_PR_QUE_SO_LE = frozenset({"ready", "merge", "view", "list", "status", "checks", "diff"})
Ambiente = collections.namedtuple("Ambiente", "mexidas desviado")  # mexidas: os SENSIVEIS que a linha mexeu (frozenset)
SEM_AMBIENTE = Ambiente(frozenset(), bool(DESVIOS & set(os.environ)))
# PARECER-HOOK-DICA-EDIT: o contorno das recusas de corpo de heredoc que a chamada pode rodar; o texto (`.md` e afins)
# vai pelas ferramentas de arquivo, e o programa, noutra chamada
GRAVE_E_RODE_NOUTRA = "grave pelo Write ou Edit e rode o programa noutra chamada"
BASES = ("develop", "origin/develop", "main", "origin/main", "master", "origin/master")
# PR-HOOK-PRAZO: o prazo vencido do `gh pr create`, `gh pr ready` ou `gh pr merge` sem o resultado gravado diz o comando que o
# grava (cabe nos 200 caracteres)
CONTORNO_DO_PRAZO = "rode antes forge-check pr"
TETO_DO_CORPO = 64 * 1024  # F5.2 (v0481 E38.4): bytes do `--body-file` lidos para a exceção do H1
# `gravado` do `verificar`: o `gh pr create` exige o resultado gravado; `gh pr ready` e `gh pr merge` o usam como atalho (E2.117)
EXIGE, ATALHO = "exige", "atalho"


def so_le_ou_espera(script):
    """O texto de um `sh -c` só tem comandos de `LE_O_TEXTO` e `SO_ESPERA` (laços e condições incluídos) e nenhuma
    substituição: a palavra crítica nele é argumento, não comando (o heredoc, o D o recusa)."""
    if any(m in script for m in ("`", "$(")):
        return False
    lidas = leituras(script, com_sinal=True)
    return not lidas.ilegivel and all(next((p for p in palavras if p not in CONTROLE), "") in LE_O_TEXTO | SO_ESPERA
                                      for leitura in lidas.partes for palavras, *_ in leitura)


def heredocs_simples(texto):
    """Todo `<<` da chamada é de `HEREDOC_SIMPLES` e as linhas de comando, fora dos corpos, não têm `\\` nem `$`: o corpo
    acaba onde o hook o corta (`<<$'EOF'`, `<<\\`, `<<EOF\\` e afins voltam à rede D)."""
    pendentes = []  # (terminador, com `-`) dos heredocs já abertos, na ordem do bash
    for linha in texto.split("\n"):
        if pendentes:
            if linha.endswith("\\"):
                return False
            pendentes = pendentes[1:] if (linha.lstrip("\t") if pendentes[0][1] else linha) == pendentes[0][0] else pendentes
            continue
        achados = [(m.group(2) or m.group(3) or m.group(4), bool(m.group(1))) for m in HEREDOC_SIMPLES.finditer(linha)]
        if "\\" in linha or "$" in linha or linha.count("<<") != len(achados):
            return False
        pendentes = achados
    return True


def e_shell_c_de_texto(texto):
    """Toda reavaliação do texto é `<shell> -c <script>` (o `-c` logo depois do shell, e ele a primeira reavaliação do
    comando) e o script só lê ou espera. Fora disso: shell sem `-c` (lê o stdin, `echo … | sh`) ou `BASH_ENV=` na linha."""
    if "BASH_ENV=" in texto:
        return False
    for simples in palavras_do_texto(texto).simples:
        palavras = [reduzida(p.cru) for p in simples.palavras]
        achada = reavaliacao_das_palavras(palavras)
        if achada is None:
            if any(isinstance(p, str) and Path(p).name in SHELLS_DA_REAVALIACAO for p in palavras):
                return False
            continue
        i = next((k for k, p in enumerate(palavras) if isinstance(p, str) and Path(p).name in SHELLS_DA_REAVALIACAO
                  and achada == f"{Path(p).name} -c"), len(palavras))
        resto = palavras[i + 1:i + 3]  # a opção e o script
        if (len(resto) < 2 or not all(isinstance(p, str) for p in resto)
                or not OPCAO_DE_REAVALIACAO.fullmatch(resto[0]) or not so_le_ou_espera(resto[1])):
            return False
    return True


# HOOK-CONTRIB-HEREDOC-FP e HOOK-REVIEW-HEREDOC-TIMEOUT: o heredoc que só um interpretador lê da entrada (`python3 -`,
# `timeout 60 python3`, `sh`, `bash -e`), pelo nome puro, sem caminho nem atribuição (também a do lançador, `env PATH=…`).
PYTHON_DA_ENTRADA = re.compile(r"python3?(?:\.\d+)?")
OPCAO_DO_PYTHON = re.compile(r"-[IuBEsSqO]+")
SHELLS_DA_ENTRADA = frozenset({"sh", "bash", "dash"})
OPCAO_DO_SHELL = re.compile(r"-[euxv]+")
# O corpo de Python que lança processo e tem um comando de PR no texto que ele monta segue como antes: é o caso
# verdadeiro. A barreira é uma lista de nomes, não fronteira (o `python3 -c '…'` o hook já não lê): na dúvida, o corpo
# segue conferido. Lançador é qualquer nome da lista, também depois de `_` (`create_subprocess_exec`, `posix_spawnp`), e
# o que acha função pelo nome montado (`getattr`, `globals`, `vars`, `__import__`, `sys.modules`); o comando é o
# marcador crítico no texto junto de todas as constantes de texto do corpo, menos as soltas (docstring), o que pega a
# lista montada em várias linhas e a concatenação (`"gh " + "pr merge"`).
LANCA_PROCESSO = re.compile(r"(?<![A-Za-z0-9])(?:subprocess|pty|ctypes|importlib|runpy|system|popen|spawn|exec|eval|"
                            r"fork|getattr|globals|vars|builtins|__import__|__dict__|modules|webbrowser|compile)")
ATRIBUICAO_SOLTA = re.compile(r"[A-Za-z_]\w*\+?=")


def comando_de_pr_no_python(corpo):
    """O corpo de Python, junto das constantes de texto dele (sem as soltas, que não rodam), tem o marcador crítico;
    corpo que o `ast` não lê conta como tendo."""
    try:
        arvore = ast.parse(corpo)
        soltas = {id(n.value) for n in ast.walk(arvore) if isinstance(n, ast.Expr)}
        textos = [n.value if isinstance(n.value, str) else n.value.decode("latin-1") for n in ast.walk(arvore)
                  if isinstance(n, ast.Constant) and isinstance(n.value, (str, bytes)) and id(n) not in soltas]
    except Exception:  # noqa: BLE001 - SyntaxError, RecursionError…: na dúvida, o corpo segue conferido
        return True
    return critico_ou_alias(" ".join(textos))


def chamada_muda_o_corpo(comando):
    """A2 e A3 da segurança da E4.4: a chamada, fora dos corpos, tem atribuição (`PATH=<pasta>` antes de `python3 -`
    muda o programa que lê o corpo) ou um `git` (o arquivo que o corpo grava fica no disco e o `git` roda ganchos e
    `core.fsmonitor`): o corpo segue como antes."""
    return any(ATRIBUICAO_SOLTA.match(p.cru) or nome_do_caminho(p.valor) == "git"
               for simples in palavras_do_texto(comando).simples for p in simples.palavras)


def leitor_da_entrada(comando):
    """`python` ou `shell` se o comando (palavras, sem lançador) só lê o programa da entrada (no Python, o que vem depois
    do `-` vai ao `sys.argv` do corpo: `python3 - a.md`); senão None."""
    nome, args = comando[0], comando[1:]
    opcoes = args[:args.index("-")] if "-" in args else args
    if PYTHON_DA_ENTRADA.fullmatch(nome) and all(OPCAO_DO_PYTHON.fullmatch(a) for a in opcoes):
        return "python"
    if nome in SHELLS_DA_ENTRADA and all(OPCAO_DO_SHELL.fullmatch(a) for a in args):
        return "shell"
    return None


def interprete_do_corpo(dono):
    """`python` ou `shell` se todo programa do dono do heredoc (`DonosDosHeredocs`), em toda leitura dos lançadores, é
    do mesmo tipo de `leitor_da_entrada`; senão None (o corpo segue como antes)."""
    tipos = set()
    try:
        for programa, argumentos, _ in programas_e_atribuicoes(dono):  # a atribuição já saiu em `chamada_muda_o_corpo`
            lidas = separar_lancadores([programa, *argumentos])
            if any(lancadas or not comando for comando, lancadas in lidas):
                return None
            tipos.update(leitor_da_entrada(comando) for comando, _ in lidas)
    except Exception:  # noqa: BLE001 - na dúvida, o corpo segue como comando (a regra de antes)
        return None
    return next(iter(tipos)) if len(tipos) == 1 else None


def leitores_dos_corpos(original, comando, corpos):
    """O tipo de cada corpo de `corpos` ([(dono, corpo)]), na mesma ordem: `python`, corpo de Python sem comando de PR
    lançado, que não é comando nem marca a chamada; `shell`, corpo que o shell roda e que só lê ou espera
    (`so_le_ou_espera`, a regra do `sh -c` de texto), que segue conferido como comando e não marca a gramática com
    heredoc; None, o corpo como antes (o `git merge` que o sh roda segue na rede D). Só com todo `<<` simples
    (`heredocs_simples`): o bash e o hook cortam o corpo no mesmo ponto; e sem atribuição nem `git` na chamada
    (`chamada_muda_o_corpo`). `dado`: nenhum corpo da chamada roda (`corpos_de_dado`), nem conferido nem marca."""
    if corpos_de_dado(original, comando):
        return ["dado"] * len(corpos)
    if not heredocs_simples(original) or chamada_muda_o_corpo(comando):
        return [None] * len(corpos)
    tipos = [interprete_do_corpo(dono) for dono, _ in corpos]
    return [None if tipo == "python" and LANCA_PROCESSO.search(corpo) and comando_de_pr_no_python(corpo)
            or tipo == "shell" and not so_le_ou_espera(corpo) else tipo
            for tipo, (_, corpo) in zip(tipos, corpos)]


# HOOK-HEREDOC-PALAVRA-FP: a chamada em que todo programa, fora dos corpos, só grava, lista ou lê arquivo não roda o corpo
# nem o arquivo gravado: o corpo é dado, e a palavra crítica nele não marca a chamada (decidem os comandos de fora). Só
# com todo `<<` simples (o bash e o hook cortam o corpo no mesmo ponto), sem atribuição (`chamada_muda_o_corpo`) e sem
# gravar arquivo com o nome de um programa da chamada (`cat > /usr/local/bin/ls`). O programa de crase, `$( )`, `<( )`,
# subshell, função e `case` o leitor acha (`programas_e_atribuicoes`) e fica fora da lista.
PROGRAMAS_DE_DADO = frozenset({"cat", "cd", "mkdir", "echo", "true", "ls", "wc", "head", "tail", "grep", "stat"})


def corpos_de_dado(original, comando):
    """True se nenhum corpo de heredoc da chamada roda: todo programa de `comando` (a linha sem os corpos) é de
    `PROGRAMAS_DE_DADO`, a linha não tem crase, todo alvo de redireção tem valor literal e nenhum grava arquivo com o
    nome de um programa da chamada (nem com curinga ou chave no nome)."""
    if not heredocs_simples(original):
        return False
    if chamada_muda_o_corpo(comando):
        return False
    if "`" in comando:  # a crase faz o nome do alvo (`cat > `echo bin/ls``) e não tem valor literal para cruzar
        return False
    leitura = palavras_do_texto(comando)
    nomes = {programa for programa, _, _ in programas_e_atribuicoes(comando)}
    lidos = [r.alvo for simples in leitura.simples for r in simples.redirecoes]
    if any(alvo is None or not alvo.valor for alvo in lidos):  # alvo sem valor literal: o nome gravado não se prova
        return False
    alvos = {Path(alvo.valor).name for alvo in lidos}
    if any(c in alvo for alvo in alvos for c in "*?[{"):  # o bash expande o curinga e a chave (`bin/l{s..s}` grava `bin/ls`)
        return False
    return nomes <= PROGRAMAS_DE_DADO and not alvos & nomes


def opcao(args, longa, curta):
    for i, a in enumerate(args):
        if a in (longa, curta) and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(longa + "="):
            return a.split("=", 1)[1]
        if not curta.startswith("--") and a.startswith(curta) and len(a) > len(curta):
            return a[len(curta):].removeprefix("=")  # `-XDELETE`, `-X=DELETE`
    return None


def posicionais(args, com_valor):
    saida, j = [], 0
    while j < len(args):
        if args[j] in com_valor:
            j += 2
            continue
        if not args[j].startswith("-"):
            saida.append(args[j])
        j += 1
    return saida


def bandeira(args, com_valor, nomes):
    """A bandeira booleana (`--draft`, `-d`, `--draft=true`) está ligada? Pula os valores das opções (`--title -d` não é
    rascunho) e vale a última, como no `gh`. Forma desconhecida (`-dw`) conta como desligada: o portão fica mais
    estrito, nunca mais frouxo."""
    ligada, j = False, 0
    while j < len(args):
        a = args[j]
        if a in com_valor:
            j += 2
            continue
        if a in nomes:
            ligada = True
        elif "=" in a and a.split("=", 1)[0] in nomes:
            ligada = a.split("=", 1)[1].lower() in VERDADE
        j += 1
    return ligada


def corpo_pedido(args):
    """F5.2: o caminho do último `--body-file`/`-F` do `gh pr create` (o gh vale o último), pulando os valores das outras opções;
    None sem ele."""
    caminho, j = None, 0
    while j < len(args):
        a = args[j]
        if a in ("--body-file", "-F"):
            caminho = args[j + 1] if j + 1 < len(args) else None
        elif a.startswith(("--body-file=", "-F")):
            caminho = a.removeprefix("--body-file=").removeprefix("-F").removeprefix("=")
        j += 2 if a in CREATE_COM_VALOR else 1
    return caminho


def troca_de_branch(args):
    """Branch depois de `git checkout`/`git switch` ("" se HEAD solto ou desconhecida); None se não troca."""
    if "--" in args:
        k = args.index("--")
        if k + 1 < len(args):
            return None  # restaura arquivos
        args = args[:k]  # `--` sem caminho depois não restaura nada: é troca de branch
    for k, a in enumerate(args):
        if a in CRIA_BRANCH:
            return args[k + 1] if k + 1 < len(args) else None
        if a in ("-d", "--detach"):
            return ""
    pos = posicionais(args, set())
    if not pos or len(pos) > 1:
        return None  # `git checkout <ref> <arquivo>...` restaura arquivos; trocar de branch leva um só nome
    return "" if pos[0] == "-" else pos[0]


def globais(toks):
    """Das opções globais de `git ...` (sem atribuições): (posição do subcomando, os `-C` em ordem, as pastas são
    incertas?). Palavra com expansão antes do subcomando pode sumir ou virar várias (`-C $(true) P`, `$(echo -C P)`): as
    pastas ficam incertas e o subcomando é o primeiro `merge`, `pull`, `checkout` ou `switch`."""
    i, pastas, incertas = 1, [], False
    while i < len(toks) and toks[i].startswith("-"):
        valor = (toks[i + 1:] + [""])[0]
        if toks[i] == "-C" and i + 1 < len(toks):
            pastas.append(valor)
        incertas |= (toks[i] in ("--git-dir", "--work-tree") or toks[i].startswith(("--git-dir=", "--work-tree="))
                     or toks[i] == "-c" and valor.lower().startswith("core.worktree"))
        i += 2 if toks[i] in GIT_COM_VALOR else 1
    sub = next((j for j in range(1, len(toks)) if toks[j] in SUBCOMANDOS), len(toks))
    if any(map(expande, toks[1:sub])):
        return sub, pastas, True
    return i, pastas, incertas


GH_SEM_VALOR = {"--help", "-h", "--version"}  # as opções de `gh` antes do subcomando que não levam o valor seguinte
GH_SUBCOMANDOS_CRITICOS = ("api", "pr")
GH_INCERTO = ("gh com opção antes do subcomando que o hook não lê (expansão do shell, ou api/pr como valor de opção), ou "
              "com chave ({a,b}, {a..c}) até o endpoint",
              "escreva o subcomando logo depois do gh e as opções depois dele (gh pr view 1 -R dono/repo), sem chave")
# E168.9 (A5) e E168.13 (A7 da segurança do #854): a palavra que pode ter expansão de chaves (o bash a divide em várias)
CHAVES = re.compile(r"\{.*(?:,|\.\.)", re.S)
MARCADOR_DO_GH = re.compile(r"\{(?:owner|repo|branch)\}")  # o gh troca no endpoint; sem vírgula, o bash não expande


def chave_incerta(palavra):
    """E168.13 (A7): a palavra pode ter chave que o bash expande (`{api,graphql}`, `{graphq,-Hx:}l`). Sem as aspas do
    texto, a chave entre aspas também conta: na dúvida, recusa. Os marcadores do gh (`{owner}`) saem antes."""
    return bool(CHAVES.search(MARCADOR_DO_GH.sub("", palavra)))


def leva_valor(opcao):
    """A opção do gh que toma a palavra seguinte como valor, pela regra do cobra: `--x` sem `=` e `-x` de duas letras,
    salvo `GH_SEM_VALOR`."""
    return "=" not in opcao and opcao not in GH_SEM_VALOR and (opcao.startswith("--") or len(opcao) == 2)


def subcomando_do_gh(toks):
    """A posição do subcomando de `gh …`, achado como o gh acha: as opções antes dele e os valores delas ficam para trás;
    `--` para."""
    i = 1
    while i < len(toks) and toks[i].startswith("-") and toks[i] != "--":
        i += 2 if leva_valor(toks[i]) else 1
    return i


def gh_incerto(toks):
    """E168.9 (A1 e A2 do review, A4 da segurança do #854): `gh` com opção antes do subcomando que o hook não lê com
    certeza: palavra com expansão antes dele (o bash a divide ou a apaga: `gh -X $M graphql`) ou `api`/`pr` como valor de
    opção (`gh -b api pr merge`, que o gh roda como `pr merge`). Quem chama recusa (`GH_INCERTO`), sem escolher leitura.
    E168.13 (A7 da segurança do #854): chave antes do subcomando, nele ou no endpoint do `gh api` (`chave_incerta`)."""
    if not toks or Path(toks[0]).name != "gh":
        return False
    i = subcomando_do_gh(toks)
    sub = toks[i:i + 1]
    endpoint = [endpoint_da_api(toks[i + 1:])] if sub == ["api"] else []
    return (any(expande(a) or a in GH_SUBCOMANDOS_CRITICOS or chave_incerta(a) for a in toks[1:i])
            or any(map(chave_incerta, sub + endpoint)))


def ordem_do_gh(toks):
    """E168.5 (A1 da segurança do #854): o gh aceita opção antes do subcomando (`gh -X PUT api …`, `gh -R o/r pr merge`),
    e as roda como depois dele. Devolve `toks` com o subcomando logo depois do `gh` (`subcomando_do_gh`) e as opções de
    antes logo atrás dele, na ordem. A leitura incerta (`gh_incerto`) quem chama recusa antes."""
    if not toks or Path(toks[0]).name != "gh" or not toks[1:2] or not toks[1].startswith("-"):
        return toks
    i = subcomando_do_gh(toks)
    if i >= len(toks) or toks[i] == "--":
        return toks
    return [toks[0], toks[i], *toks[1:i], *toks[i + 1:]]


def analisar(toks):
    """('cd', dir) | ('pr', None, base, head, rascunho, repo, body_file) | ('prmerge', repo, alvo) | ('prready', alvo, desfaz, repo)
    | ('api', args)
    | ('merge', dir, [(branch, [refs candidatas])]) | ('branch', dir, nome) | None."""
    sem = sem_atribuicoes(toks)
    atribuicoes, toks = toks[: len(toks) - len(sem)], ordem_do_gh(sem)
    if not toks:
        return None
    if toks[0] == "cd":
        return ("cd", toks[1] if len(toks) > 1 else None)
    if Path(toks[0]).name == "gh":  # `/usr/bin/gh`, `./gh`: o mesmo programa (GH-MERGE-ADMIN, C-1)
        if toks[1:2] == ["api"]:
            return ("api", toks[2:])
        if "pr" not in toks:
            return None
        i = toks.index("pr")
        j, repo_pr = i + 1, None
        while j < len(toks) and toks[j].startswith("-") and toks[j] != "--":
            # a opção entre `pr` e o subcomando: `-R`/`--repo` persistente do `gh pr` e a que veio de antes do `pr`
            # (`ordem_do_gh`: `gh -b x pr merge` é `gh pr -b x merge`); pula o valor como o gh (E168.9)
            if toks[j] in ("-R", "--repo"):
                repo_pr = toks[j + 1] if j + 1 < len(toks) else None
            elif toks[j].startswith(("--repo=", "-R")):
                repo_pr = toks[j].split("=", 1)[-1].removeprefix("-R")
            j += 2 if leva_valor(toks[j]) else 1
        args = toks[j + 1:]
        repo = repo_pr or opcao(args, "--repo", "-R") or next((a.split("=", 1)[1] for a in atribuicoes
                                                               if a.startswith("GH_REPO=")), None)
        if toks[j: j + 1] == ["create"]:
            return ("pr", None, opcao(args, "--base", "-B"), opcao(args, "--head", "-H"),
                    bandeira(args, CREATE_COM_VALOR, {"--draft", "-d"}), repo, corpo_pedido(args))
        if toks[j: j + 1] == ["ready"]:
            alvo = (posicionais(args, READY_COM_VALOR) or [None])[0]
            return ("prready", alvo, bandeira(args, READY_COM_VALOR, {"--undo"}), repo or repo_da_url(alvo))
        if toks[j: j + 1] == ["merge"]:
            alvo = (posicionais(args, MERGE_PR_COM_VALOR) or [None])[0]
            return ("prmerge", repo or repo_da_url(alvo), alvo)
        return None
    if toks[0] != "git":
        return None
    i, pastas, _ = globais(toks)
    pasta = next(reversed(pastas), None)
    sub, args = (toks[i], toks[i + 1:]) if i < len(toks) else (None, [])
    if sub in ("checkout", "switch"):
        nome = troca_de_branch(args)
        return None if nome is None else ("branch", pasta, nome)
    if sub == "pull":  # `git pull <remoto> <branch>` mescla a branch na atual, como o merge
        pos = posicionais(args, PULL_COM_VALOR)
        alvos = [s.split(":")[0].lstrip("+") for s in pos[1:]]
        return ("merge", pasta, [(nome_da_branch(a), [f"{pos[0]}/{a}", a]) for a in alvos if a])
    if sub != "merge" or MERGE_SEM_ALVO & set(args):
        return None
    return ("merge", pasta, [(nome_da_branch(r), [r]) for r in posicionais(args, MERGE_COM_VALOR)])


# FURO-HOOK-A, A2: o que o parecer vê atrás de um lançador. O `find -exec` e estes lançadores (fora de `LANCADORES`) rodam o
# merge sem que o hook o leia: recusa (ADR 0011), como o conformidade faz com `LANCADORES_RECUSADOS`.
EXEC_DO_FIND = {"-exec", "-execdir", "-ok", "-okdir"}
OUTROS_LANCADORES = {"ionice", "chrt", "taskset", "flock", "unshare", "script", "watch", "parallel", "doas", "busybox",
                     "expect", "socat"}


def analise_do_comando(palavras):
    """A2: `analisar` do comando simples atrás dos lançadores (`separar_lancadores`, a fonte do conformidade). O `cd` de
    lançador roda noutro processo e não vale; atrás do `xargs` o alvo do merge vem da entrada padrão e recusa. A opção de
    lançador fora da tabela recusa antes, com o marcador do hook, então a leitura é uma só."""
    sem = sem_atribuicoes(palavras)
    try:
        (comando, lancadas), *_ = separar_lancadores(palavras)
    except (LancadorDemais, TextoDivididoAberto) as achado:
        bloquear("R-REVIEW", f"`{achado}` antes de gh pr, gh api, merge ou pull: opção de lançador que o hook não lê. "
                             "Corrigir: rode o comando direto, sem lançador")
    if comando and nome_incerto(comando[0]) and critico_ou_alias(" ".join(comando)):  # D2 e D3: `$c gh`, `env $(…) gh`
        bloquear("R-REVIEW", f"`{comando[0]}` como nome do comando com gh pr, gh api, merge ou pull: o hook não sabe o "
                             "que ele roda. Corrigir: escreva o comando por extenso, sem variável nem $( no nome")
    if gh_incerto(comando):  # E168.9: na dúvida sobre o subcomando, recusa (R-CONFORMIDADE), sem escolher leitura
        bloquear("R-CONFORMIDADE", f"{GH_INCERTO[0]}. Corrigir: {GH_INCERTO[1]}")
    nome = next((Path(c).name for c in comando[:1]), "")
    if nome in OUTROS_LANCADORES or nome == "find" and EXEC_DO_FIND & set(comando):
        bloquear("R-REVIEW", f"`{nome}` na chamada com gh pr, gh api, merge ou pull: o hook não lê o que ele roda. "
                             f"Corrigir: rode o comando direto, sem `{nome}`")
    analise = analisar(palavras[: len(palavras) - len(sem)] + lancadas + comando)
    analise = alias_do_gh(palavras[: len(palavras) - len(sem)] + lancadas, comando, analise)  # 0.45.4
    antes = sem[: max(0, len(sem) - len(comando))]
    lidas = analise[2] if analise and analise[0] == "alias" else [analise]  # cada expansão do alias do gh, também
    if any(lida and lida[0] in ("prmerge", "merge") for lida in lidas) and "xargs" in {Path(p).name for p in antes}:
        bloquear("R-REVIEW", "`xargs` antes de gh pr merge, git merge ou git pull: o alvo vem da entrada padrão e o hook "
                             "não o conhece. Corrigir: rode o merge direto, com a branch na linha")
    return None if antes and analise and analise[0] == "cd" else analise


# 0.45.4 (N1 resto no parecer): o alias do gh já gravado (`aliases:` do config.yml) troca o comando que o hook lê. A leitura
# é a do conformidade (`aliases_do_gh`, `expandir_alias_do_gh`, `Guarda.configs_do_gh`, `COMANDOS_DO_GH`), por import tardio:
# o conformidade importa este módulo, e só a linha com `gh <nome>` paga o import. O nome logo depois do `gh` e a menção às
# variáveis da configuração do gh abrem o filtro de entrada.
NOME_DO_GH = re.compile(r"\bgh\s+['\"\\]*([^\s;&|()<>'\"\\-][^\s;&|()<>'\"\\]*)")
MENCIONA_A_CONFIG_DO_GH = re.compile(r"\b(?:GH_CONFIG_DIR|XDG_CONFIG_HOME|HOME)\b")


def leitor_do_alias():
    import conformidade  # noqa: PLC0415 - import tardio: o conformidade importa o parecer
    return conformidade


def expansoes_do_alias(nome, ambiente):
    """(as expansões de `nome` nos `aliases:` dos config.yml que o gh lê, com GH_CONFIG_DIR e XDG_CONFIG_HOME de `ambiente`;
    o primeiro config.yml que o hook não lê, se `nome` não é comando do gh, senão None), como o conformidade."""
    leitor, expansoes = leitor_do_alias(), []
    for arquivo in leitor.Guarda.configs_do_gh(SimpleNamespace(ambiente=ambiente)):
        try:
            aliases = leitor.aliases_do_gh(arquivo.read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        except (OSError, ValueError):  # `AliasIlegivel` e o texto que não é UTF-8 também
            if nome in leitor.COMANDOS_DO_GH:
                continue
            return expansoes, arquivo
        if nome in aliases:
            expansoes.append(aliases[nome])
    return expansoes, None


def alias_na_linha(textos):
    """A linha chama `gh <nome>` com alias gravado que expande para o que o parecer confere (gh pr create, merge ou ready,
    gh api), de shell (`!`) ou num config.yml que o hook não lê; ou chama `gh <nome fora dos comandos do gh>` e cita
    GH_CONFIG_DIR, XDG_CONFIG_HOME ou HOME."""
    nomes = sorted({m.group(1) for texto in textos for m in NOME_DO_GH.finditer(texto)})
    if set(nomes) - leitor_do_alias().COMANDOS_DO_GH and any(MENCIONA_A_CONFIG_DO_GH.search(texto) for texto in textos):
        return True
    for nome in nomes:
        expansoes, ilegivel = expansoes_do_alias(nome, {})
        if ilegivel or any(e.startswith("!") or PREFILTRO.search(f"gh {e}") for e in expansoes):
            return True
    return False


def textos_da_linha(comando):
    """A linha e as formas que o shell lê dela, cada uma também sem aspas nem barra (`g\\h`, `g'h'`)."""
    return [g for f in [comando, *formas_que_o_shell_le(comando, True)] for g in (f, re.sub(r"[\\'\"]", "", f))]


@functools.lru_cache(maxsize=256)
def critico_ou_alias(texto):
    """A1 da segurança da 0.45.4: a linha é crítica para as travas do parecer se tem o marcador (`CRITICO`) ou se chama
    alias do gh que o parecer confere (`alias_na_linha`). Sem isso, `eval gh junta …` (junta = pr merge) escapava da
    reavaliação, do teto, do heredoc gravado, da gramática com heredoc, da falha fechada e do prazo.
    O resultado depende também do ambiente do gh (os config.yml que `alias_na_linha` lê), mas o cache tem só o texto como
    chave: vale por processo, e o hook roda um processo por chamada. Teste que mude o ambiente no mesmo processo chama
    `critico_ou_alias.cache_clear()` antes (A4 do review da 0.45.4)."""
    return bool(CRITICO.search(texto)) or alias_na_linha(textos_da_linha(texto))


class CriticoOuAlias:
    """`critico_ou_alias` com a interface que `executar` espera do marcador (`.search`: None sem marcador). O erro ao ler a
    configuração do gh marca a chamada: ela falha fechada, como a que tem o marcador."""

    @staticmethod
    def search(texto):
        try:
            if critico_ou_alias(texto):
                return True
        except Exception:  # noqa: BLE001 - ADR 0009, seção 7: na dúvida, a ação é crítica
            return True
        return None


def alias_do_gh(atribuicoes, comando, analise):
    """`gh <nome>` com `nome` no `aliases:` do gh roda a expansão: ("alias", nome, [`analise` e a `analisar` de cada expansão]);
    a própria `analise` se o comando não é `gh <nome>` ou se `nome` é comando do gh sem alias. GH_CONFIG_DIR e
    XDG_CONFIG_HOME de prefixo ou de lançador valem. Recusam, como no conformidade: alias de shell, expansão ou config.yml que o hook não lê; e o
    prefixo que muda a configuração sem valor literal (HOME, `$`, crase, `+=`) com nome fora dos comandos do gh."""
    comando = ordem_do_gh(comando)  # E168.5: `gh -R o/r <alias>` roda o alias como `gh <alias> -R o/r`
    nome, do_gh = (comando + ["", ""])[1], leitor_do_alias().COMANDOS_DO_GH
    if Path((comando + [""])[0]).name != "gh" or not nome or nome.startswith("-"):
        return analise
    ambiente = {}
    for chave, _, valor in (a.partition("=") for a in atribuicoes):
        if chave.rstrip("+") in CONFIG_DO_GH and nome not in do_gh and (chave.startswith("HOME") or expande(valor)
                                                                           or chave.endswith("+")):
            bloquear("R-REVIEW", f"gh {nome}: a linha muda a configuração do gh ({chave.rstrip('+')}) e o hook não sabe "
                                 "qual alias vale. Corrigir: rode o comando do gh por extenso")
        ambiente[chave] = valor
    expansoes, ilegivel = expansoes_do_alias(nome, ambiente)
    if ilegivel:
        bloquear("R-REVIEW", f"gh {nome}: o hook não lê os aliases do gh em {ilegivel}. Corrigir: rode o comando do gh "
                             "por extenso")
    analises = [analise]
    for expansao in expansoes:
        if expansao.startswith("!"):
            bloquear("R-REVIEW", f"gh {nome}: alias de shell (`!`) do gh roda o que o hook não lê. Corrigir: rode o "
                                 "comando direto, sem alias")
        novas = leitor_do_alias().expandir_alias_do_gh(expansao, comando[2:])
        if not novas:
            bloquear("R-REVIEW", f"gh {nome}: alias do gh que o hook não lê. Corrigir: rode o comando do gh por extenso")
        analises.append(analisar(list(atribuicoes) + [comando[0], *novas]))  # só a leitura da expansão; nada roda
    return analise if nome in do_gh and not expansoes else ("alias", nome, analises)


def soltos(leitura):
    """Para cada comando da leitura (com o sinal), se ele roda no shell de fora e sempre: nada de `( )`, `{ }`,
    if/for/while, `$( )`, pipeline, `||` nem segundo plano antes ou depois, e nenhum `&&` antes dele (só `;` e quebra de
    linha), que pode pular o comando. Só o `cd` desses comandos muda a pasta dos seguintes."""
    saida, anterior, aberto = [], "", False
    for palavras, _, sub, sinal in leitura:
        aberto = aberto or sinal in ("(", ")") or bool(palavras) and palavras[0] in ABRE
        saida.append(not sub and not aberto and anterior in COMECA and sinal in SEGUE)
        anterior = sinal
    return saida


def sem_chaves(palavras):
    """Tira a palavra que abre o corpo de um bloco (`then cd P`, `{ cd P`, `do`, `else`): o comando dele é o que vem depois."""
    k = 0
    while k < len(palavras) and palavras[k] in CORPO:
        k += 1
    return palavras[k:]


def sem_condicao(palavras):
    """Tira o que vem antes do comando de uma parte (`if cd P`, `while`, `until`, `elif`, `!`, `time -p`, `function f {`,
    atribuição `A=1`), em qualquer ordem: o `cd` que sobra roda no shell de cima, mas fora do nível que o hook lê (HK3-03)."""
    k, no_time = 0, False
    while k < len(palavras):
        no_time = no_time or palavras[k] == "time"
        if palavras[k] in CONDICAO | CORPO:
            k += 2 if palavras[k] == "function" else 1  # `function NOME`: o nome também sai
        elif ATRIBUICAO.match(palavras[k]) or no_time and palavras[k] in ("-p", "--"):
            k += 1  # `if A=1 cd P`, `time -p cd P`: atribuição e opção do `time` também saem
        else:
            break
    return palavras[k:]


def com_til(palavra, mexidas=frozenset()):
    """`~` e `~/...` no início da palavra viram o HOME, como o bash faz antes do comando rodar; None se a linha mexeu no
    HOME e o hook não sabe o valor."""
    if palavra != "~" and not palavra.startswith("~/"):
        return palavra
    return None if "HOME" in mexidas else str(Path(os.path.expanduser("~"))) + palavra[1:]


def nomes_dinamicos(comando):
    """GH-REPO-DE-ARQUIVO: o comando dá valor a uma variável cujo nome sai de expansão (`export $(cat .env)`,
    `export "$k=$v"`, `read "$n"`, `printf -v "$n"`): o hook não o lê, e ele pode ser qualquer um dos SENSIVEIS."""
    nome, args = comando[0], comando[1:]
    if nome == "printf":
        args = [p[2:] for p in args if p.startswith("-v")] + [b for a, b in zip(args, args[1:]) if a == "-v"]  # `-vN`, `-v N`
    elif nome == "read":
        args = [b for a, b in zip([""] + args, args) if a not in LE_COM_VALOR]
    elif nome not in NOMEIA:
        return False
    return any(expande(p) and not ATRIBUICAO.match(p) for p in args)


def mexidas_na_linha(palavras):
    """Os SENSIVEIS que o comando mexe: por prefixo (`HOME=x cd`), atribuição (`HOME=x`, `export HOME=x`) ou nome em `read`,
    `printf -v`, `declare`, `unset`... A pasta que depende deles fica desconhecida. GH-REPO-DE-ARQUIVO (A5 da E3.13, A2
    da E3.12): `source` e `.` (também depois de `builtin` ou `command`) e o nome que sai de expansão mexem em todos."""
    k = depois_das_atribuicoes(palavras)
    nomes = {ATRIBUICAO.match(a).group(1) for a in palavras[:k]}
    nomes |= {m.group(1) for m in map(ATRIBUICAO.match, palavras[k:]) if m}
    comando = sem_condicao(palavras[k:])
    while comando[:1] in (["builtin"], ["command"]):
        comando = comando[1:]
        while comando[:1] and comando[0].startswith("-"):  # D1: `command -p`, `command --`, `builtin --`
            comando = comando[1:]
    if comando and (comando[0] in CARREGA_ARQUIVO or nome_incerto(comando[0])):  # D2: `c=source; $c env.sh`
        return frozenset(SENSIVEIS)
    if comando and comando[0] in LE_VARIAVEL | NOMEIA:
        if nomes_dinamicos(comando):
            return frozenset(SENSIVEIS)
        nomes |= {n for p in comando[1:] for n in p.split("=")}  # `read HOME`, `printf -v GIT_DIR`, `declare -n r=HOME`
    return frozenset(n for n in nomes if n in SENSIVEIS or n.startswith("GIT_"))  # D4: `GIT_CONFIG_GLOBAL=` e afins


def mexidas_por_expansao(texto):
    """D4 (A5 do review da E3.21): `${N:=v}` e `${N=v}` dão valor a N em qualquer ponto do texto (argumento, redireção,
    here-string, corpo de heredoc), e com `set -a` o bash o exporta; a indireta (`${!n:=v}`) mexe em todos. Vale para a
    linha inteira, antes do primeiro comando (falha fechada sobre a ordem); `${N:-v}` e `${N:+v}` não dão valor."""
    nomes = set()
    for m in EXPANSAO_QUE_ATRIBUI.finditer(texto):
        if m.group(1):  # `${!n:=v}`: o nome sai de expansão
            return frozenset(SENSIVEIS)
        nomes.add(m.group(2))
    return frozenset(nome for nome in nomes if nome in SENSIVEIS or nome.startswith("GIT_"))


def mexidas_por_aritmetica(texto):
    """D4 (A10 da segurança da E3.27): o nome de `SENSIVEIS` ou `GIT_*` com operador de atribuição aritmética em qualquer
    ponto do texto conta como mexido (falha fechada: fora de `$((…))`, `$[…]`, `((…))`, `let`, subscrito e deslocamento
    também, recusa a mais; o `=` simples, só com um contexto aritmético no texto); `$N=` não atribui (o `$n=` de nome por expansão e o valor avaliado, `v='HOME=0'; $((v))`,
    ficam fora: docs/hooks.md, D4)."""
    aritmetica = bool(ABRE_ARITMETICA.search(texto))
    nomes = {m.group(1) or m.group(3) for m in ATRIBUICAO_ARITMETICA.finditer(texto) if aritmetica or m.group(2) != "="}
    return frozenset(v for v in nomes if v in SENSIVEIS or v.startswith("GIT_"))


def mexidas_do_texto(textos):
    """D4 (A9 e A10 da segurança da E3.27): as mexidas por expansão e por aritmética de cada forma que o shell lê da
    linha (`textos_da_linha`: a barra e a quebra de linha dentro da chave somem, `${GH_\\`⏎`REPO:=x}`)."""
    return frozenset().union(*(mexidas_por_expansao(t) | mexidas_por_aritmetica(t) for t in textos))


def nome_incerto(palavra):
    """D2 (GH-REMOTO-NA-LINHA): o nome do comando sai de expansão (`$c`, `${c}`, `$(…)`, crase) e pode ser um builtin
    (`source`) ou outro comando; o caminho de variável com `/` literal (`$F/bin/x`) é arquivo e não conta."""
    return expande(palavra) and not CAMINHO_DE_VARIAVEL.fullmatch(palavra)


def mexe_no_config_do_git(mexidas):
    """D4: a linha mexeu numa variável que troca o config ou o repositório que o git do gh lê."""
    return bool(CONFIG_DO_GIT & mexidas) or any(n.startswith("GIT_") for n in mexidas)


def linha_mantem_os_remotos(linha):
    """D5 (GH-REMOTO-NA-LINHA): todo programa da linha, de qualquer nível, é de `SO_LEEM_A_COPIA` ou `gh pr` de
    `GH_PR_QUE_SO_LE`, e nenhuma redireção grava arquivo (só `/dev/null` e a cópia de descritor). Qualquer outro, `git`
    incluído (numa cópia alheia ele roda o `core.fsmonitor` e os ganchos dela), pode mudar os remotos antes do gh."""
    leitura = palavras_do_texto(linha)
    for simples in leitura.simples:
        for r in simples.redirecoes:
            alvo = getattr(r.alvo, "valor", None)  # sem alvo: None, que grava
            if ">" in r.operador and alvo != "/dev/null" and not (r.operador == ">&" and alvo and alvo.isdigit()):
                return False
    return not leitura.duvida and all(
        programa in SO_LEEM_A_COPIA or programa == "gh" and args[:1] == ["pr"] and args[1:2] and args[1] in GH_PR_QUE_SO_LE
        for programa, args, _ in programas_e_atribuicoes(linha))


def resolver(palavra, mexidas, base, fisico=False):
    """O caminho que a palavra dá a partir de `base`, ou None se o hook não o resolve: palavra que o bash expande (`$`,
    crase, `$( )`), HOME mexido na linha, relativo sem base conhecida ou pasta que não existe (confere o caminho como
    escrito, sem apagar o `nao/..`). `fisico`: o `-C` do git segue o link antes do `..`; o `cd` do bash, não."""
    palavra = com_til(palavra, mexidas)
    if palavra is None or expande(palavra) or base is None and not os.path.isabs(palavra):
        return None
    caminho = os.path.join(base or "", palavra)
    if not os.path.isdir(caminho):
        return None
    return Path(os.path.realpath(caminho) if fisico else os.path.normpath(caminho))


def depois_do_cd(pasta, args, mexidas):
    """A pasta depois de `cd <args>`; None se o hook não a resolve ou ela depende do `CDPATH`."""
    if len(args) != 1:
        return None  # com opção (`cd -P x`) ou argumento a mais o hook não resolve (`cd -` vira uma pasta que não existe)
    cdpath = None if "CDPATH" in mexidas else os.environ.get("CDPATH", "")  # None: mexido na linha
    if not args[0].startswith(("/", "~", "./", "../")) and args[0] not in (".", "..") and (
            cdpath is None or cdpath):
        return None  # o `cd` relativo procura no CDPATH
    return resolver(args[0], mexidas, pasta)


def pastas_do_git(palavras):
    """Os `-C` das opções globais do `git`, em ordem, ou None se a linha desvia ou deixa incerto o repositório
    (`--git-dir`, `--work-tree`, `-c core.worktree=`, palavra com expansão antes do subcomando)."""
    _, pastas, incertas = globais(sem_atribuicoes(palavras))
    return None if incertas else pastas


def pasta_do_git(pasta, pastas, mexidas, desviado):
    """A pasta em que o git roda: a do `cd` e cada `-C` em ordem, um relativo ao anterior; None se o hook não a resolve."""
    if desviado or pastas is None:
        return None
    for p in pastas:  # o `-C` absoluto também refaz a pasta desconhecida; `-C ""` não muda nada (o `resolver` o devolve)
        pasta = resolver(p, mexidas, pasta, fisico=True)
    return pasta


def existe(raiz, ref):
    return git(raiz, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0


def guarda_de_versao(fc, raiz):
    """A mesma guarda do `forge-check pr` (versão defasada): num projeto, a cópia comprovadamente atrás do repositório bloqueia o
    portão (`R-CONFORMIDADE`). No Forge, nos clones de contribuição e quando a comparação falha, o hook segue mudo (ADR 0003,
    item 1: sem violação, sem saída); o aviso chega pelo `forge-check` e pelo `forge-fechar`."""
    nivel, texto = fc.avaliar_versao(SimpleNamespace(cmd="pr", alvo=None, base=None), raiz)
    if nivel == "bloqueio":
        bloquear("R-CONFORMIDADE", texto)


def exigidos_sem_pedido(fc, raiz, ref, base):
    """(pareceres exigidos, classe) da branch sem pedido: a mesma soma do `forge-check pr` (`pareceres_exigidos`, P5), com os gatilhos
    só do diff (sem pedido não há plano técnico). A classe nunca exige menos que os gatilhos de segurança e devops."""
    classe = fc.classe_da_entrega(raiz, ref, base)[0]
    infra, seguranca = fc.gatilhos_do_diff(fc.arquivos_da_entrega(raiz, ref, base))
    return fc.pareceres_exigidos(classe, infra, seguranca), classe


def verificar(hook, raiz, branch, ref, base, dica="", gravado=None):
    """Bloqueia se a branch não tem os pareceres exigidos aprovados e válidos. Os exigidos são os do `forge-check` (P5: a classe
    da entrega mais os gatilhos de segurança e devops; o review vale sempre). `dica` abre o motivo. `gravado` (PR-HOOK-PRAZO): o
    resultado que o `forge-check pr` gravou para o mesmo head, branch e base decide sem refazer a checagem (o aprovado libera, o
    reprovado recusa). Sem ele, a conferência de hoje decide e o prazo vencido diz o comando que o grava; com `EXIGE` (o
    `gh pr create`), a recusa vem mesmo sem violação; com `ATALHO` (`gh pr ready` e `gh pr merge`, E2.117), sem violação libera.
    Fora do clone do Forge, o `ATALHO` só recusa pelo reprovado e nunca libera pelo aprovado: no Forge, o CI de pareceres é o
    segundo portão; no projeto, não há outro, e a conferência de hoje decide."""
    fc = forge_check()
    guarda_de_versao(fc, raiz)
    pedida = base
    base, _ = fc.base_do_delta(raiz, base, ref) if base else (None, None)  # a mesma base do `forge-check pr` (K-164)
    estado, motivo = fc.resultado_gravado_do_pr(raiz, branch, ref, base, pedida) if gravado else (None, None)
    if estado == "aprovado" and (gravado == EXIGE or e_clone_do_forge(raiz)):
        return  # A1 da segurança (E2.142): no projeto, o aprovado gravado é forjável e o merge não tem outro portão
    if estado == "reprovado":
        bloquear("R-REVIEW", f"{dica}{motivo}")
    if motivo:  # sem o resultado gravado, o prazo vencido da conferência de hoje diz o comando que o grava (o resto: CONTORNO_DO_TETO)
        hook.contorno_do_prazo = CONTORNO_DO_PRAZO
    pedidos = fc.pedidos_da_branch(raiz, branch, ref)
    if not pedidos:
        exigidos, classe = exigidos_sem_pedido(fc, raiz, ref, base)
        pastas = " e ".join(f"{fc.CONTRATOS[t][0]}/" for t in exigidos)
        bloquear("R-REVIEW", f"{dica}nenhum parecer em {pastas} com `branch: {branch}`; "
                             + ("faça o code review antes do PR ou do merge (classe T: sem QA, R-QA)." if exigidos == ["review"] else
                                f"faça o code review e os pareceres da classe {classe} e dos gatilhos antes do PR ou do merge "
                                "(forge-check classe)."))
    for pedido in pedidos:
        violacoes = fc.cmd_pr(raiz, pedido, ref, base)  # a mesma base do `forge-check pr`: merge puro da base não invalida; base fora do fluxo, estrito
        if violacoes:
            rid, texto = separar_regra(violacoes[0], "R-REVIEW")
            extra = f" (e mais {len(violacoes) - 1})" if len(violacoes) > 1 else ""
            bloquear(rid, f"{dica}{texto}{extra}; confira com forge-check pr {pedido}.")
    if motivo and gravado == EXIGE:  # PR-HOOK-PRAZO: a conferência de hoje não achou violação, mas o `gh pr create` exige o gravado
        bloquear("R-REVIEW", f"{dica}{motivo}")


def corpo_do_pr(raiz, pasta, caminho):
    """F5.2: o texto do `--body-file` (lido só acima do teto): caminho literal, arquivo comum que não é link, dentro da cópia, até
    TETO_DO_CORPO bytes; `-`, expansão, relativo com a pasta do gh desconhecida e o que não se lê como arquivo (pasta; FIFO, vazio) dão ""
    (sem a exceção do H1)."""
    if not caminho or caminho == "-" or re.search(r"[$`~*?\[{]", caminho) or pasta is None and not os.path.isabs(caminho):
        return ""
    alvo = Path(pasta or "/", caminho)
    real = Path(os.path.realpath(alvo))
    if alvo.is_symlink() or not real.is_relative_to(Path(raiz).resolve()):
        return ""
    try:
        with open(os.open(real, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "rb") as arquivo:
            dados = arquivo.read(TETO_DO_CORPO + 1)
        return dados.decode("utf-8") if len(dados) <= TETO_DO_CORPO else ""
    except (OSError, UnicodeDecodeError):
        return ""


def tamanho_da_abertura(raiz, head, corpo):
    """F5.2 (v0481 E38.4): o `gh pr create` para a develop no clone do Forge, com ou sem rascunho, acima do teto do H1 e sem a
    exceção no `--body-file` recusa com o corte sugerido (`tamanho_na_abertura`); o git que não lê o diff recusa (ADR 0009, seção 7)."""
    fc = forge_check()
    branch = nome_da_branch(head) if head else git(raiz, "branch", "--show-current")[1]
    if branch in INTEGRACAO:
        return  # promoção entre branches de integração
    ref = next((r for r in (head, f"origin/{branch}") if existe(raiz, r)), None) if head else "HEAD"
    if ref is None:
        bloquear("R-REVIEW", f"branch `{branch}` não existe localmente, sem tamanho a conferir. Corrigir: git fetch origin {branch}")
    base =fc.base_da_entrega(raiz, "develop", so_a_pedida=True) or "origin/develop"
    recusa = fc.tamanho_na_abertura(raiz, base, ref, "")
    texto = recusa and corpo_do_pr(raiz, *corpo)
    if texto:  # o corpo só é lido acima do teto
        recusa = fc.tamanho_na_abertura(raiz, base, ref, texto)
    if recusa:
        bloquear("R-REVIEW", recusa.removeprefix("R-REVIEW: "))


def pull_request(hook, pasta, base, head, rascunho, corpo=(None, None)):
    """`corpo`: (pasta do gh ou None, caminho do `--body-file` ou None)."""
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz:
        return
    forge = e_clone_do_forge(raiz)
    if forge and base and nome_da_branch(base) == "develop":
        tamanho_da_abertura(raiz, head, corpo)
    if forge and rascunho:
        return  # no Forge, o PR nasce em rascunho e só sai dele com o parecer (`gh pr ready`)
    atual = git(raiz, "branch", "--show-current")[1]
    branch = nome_da_branch(head) if head else atual
    if not branch or branch in INTEGRACAO:
        return  # HEAD solto ou promoção entre branches de integração
    ref = None
    if head and branch != atual:
        ref = next((r for r in (head, f"origin/{branch}") if existe(raiz, r)), None)
        if ref is None and forge:
            bloquear("R-REVIEW", f"branch `{branch}` não existe localmente, sem parecer a conferir. Corrigir: "
                                 "git fetch, ou abra com gh pr create --draft.")
        if ref is None:
            return  # projeto: a branch não existe localmente, nada a conferir aqui
    candidatas = (base, f"origin/{base}") if base else (b for b in BASES if nome_da_branch(b) != branch)
    verificar(hook, raiz, branch, ref, next((b for b in candidatas if existe(raiz, b)), None),
              "sem parecer aprovado, abra com gh pr create --draft; " if forge else "", gravado=EXIGE)


def pronto_de_pr(hook, pasta, alvo, desfaz):
    """`gh pr ready` no clone do Forge: tirar o PR do rascunho exige o mesmo parecer do merge."""
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz or not e_clone_do_forge(raiz) or desfaz:
        return  # nos projetos, nada muda; `--undo` volta o PR para rascunho
    branch = branch_do_pr(raiz, alvo)
    if not branch:
        bloquear("R-CONTRIB", "PR indicado só por número, sem branch. Corrigir: use o nome da branch "
                              "(gh pr ready <branch>).")
    if branch in INTEGRACAO:
        return  # promoção entre branches de integração
    ref = next((r for r in (branch, f"origin/{branch}") if existe(raiz, r)), None)
    if ref is None:
        bloquear("R-REVIEW", f"branch `{branch}` não existe localmente, sem parecer a conferir. Corrigir: "
                             "git fetch e tente de novo.")
    base = base_do_pr(raiz, branch)
    verificar(hook, raiz, branch, ref, next((b for b in (base, f"origin/{base}") if existe(raiz, b)), None),
              "PR sai do rascunho só com parecer: ", gravado=ATALHO)


def merge(hook, pasta, alvos, branches):
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz:
        return
    chave = raiz.resolve()
    atual = branches[chave] if chave in branches else git(raiz, "branch", "--show-current")[1]
    if atual not in INTEGRACAO:
        return  # atualizar uma branch de trabalho é livre; o portão é a entrada na integração
    for branch, candidatas in alvos:
        if branch in INTEGRACAO or branch in ("HEAD", "FETCH_HEAD"):
            continue
        ref = next((r for r in candidatas if existe(raiz, r)), None)
        if ref:  # base: a branch de integração (o HEAD ainda não trocou se o checkout veio na mesma linha)
            verificar(hook, raiz, branch, ref, atual)


def slug_do_forge():
    """`dono/repo` do Forge, do `repository` do plugin.json (nada fixo no código)."""
    url = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("repository", "")
    return re.sub(r"^.*github\.com[/:]", "", url).removesuffix(".git").strip("/").lower()


def aponta_para_o_forge(texto):
    """True se o texto cita o slug do Forge exato (o GitHub não diferencia maiúsculas), com fronteira nos dois lados:
    `<dono>/Forge-site`, `<dono>/ForgeX` e `<dono>/meu-Forge` são outros repositórios. Aceita `.git` e `/` finais."""
    slug = slug_do_forge()
    if not texto or not slug:
        return False
    return bool(re.search(rf"(?<![\w.-]){re.escape(slug)}(\.git)?(?![\w.-])", texto.lower()))


def desagrupa_i(args):
    """`-iX PUT`, `-iXPUT`, `-if k=v`: o `gh api` lê o `-i` (boolean) e a opção colada como duas (`-i -X`)."""
    saida, valor = [], False
    for a in args:
        if valor:  # o token que segue uma opção valorada (`-p -iX`) é o valor dela: fica como veio
            saida.append(a)
            valor = False
            continue
        while re.match(r"-i[^-]", a):
            saida.append("-i")
            a = "-" + a[2:]
        saida.append(a)
        valor = a in API_COM_VALOR
    return saida


def metodos_pedidos(args):
    """Todo `-X`/`--method` do comando, mesmo como valor de outra opção (`-p -XPUT`): falha fechada."""
    metodos = []
    for i, a in enumerate(args):
        if a in ("-X", "--method"):
            if i + 1 < len(args):
                metodos.append(args[i + 1])
        elif a.startswith("--method="):
            metodos.append(a.split("=", 1)[1])
        elif a.startswith("-X") and len(a) > 2:
            metodos.append(a[2:].removeprefix("="))  # `-XPUT`, `-X=PUT`
    return metodos


def ultimo_metodo_real(args):
    """O último `-X`/`--method` que o `gh` lê de fato: o token depois de outra opção valorada (`-p -XGET`) é valor dela."""
    ultimo, pular = None, False
    for i, a in enumerate(args):
        if pular:
            pular = False
        elif a in ("-X", "--method"):
            ultimo, pular = (args[i + 1] if i + 1 < len(args) else ultimo), True
        elif a.startswith("--method="):
            ultimo = a.split("=", 1)[1]
        elif a.startswith("-X") and len(a) > 2:
            ultimo = a[2:].removeprefix("=")
        elif a in API_COM_VALOR:
            pular = True
    return ultimo


def metodo_mutante(args):
    """True se o `gh api` altera algo: qualquer método diferente de GET (não só o último), ou campos (que viram POST)."""
    args = desagrupa_i(args)
    metodos = metodos_pedidos(args)
    if any(metodo.upper() != "GET" for metodo in metodos):
        return True
    real = ultimo_metodo_real(args)
    if real is not None and real.upper() == "GET":  # só GET de fato: os campos viram consulta, não corpo
        return False
    return any(a in ("-f", "-F", "--field", "--raw-field", "--input")
               or a.startswith(("--field=", "--raw-field=", "--input="))
               or re.match(r"-[fF]", a) is not None  # `-fchave=valor`, `-Fquery=@arq`: o gh aceita o valor colado
               for a in args)


def endpoint_da_api(args):
    args = desagrupa_i(args)
    return (posicionais(args, API_COM_VALOR) or [""])[0]


# GH-MERGE-ADMIN: o que passa por cima da proteção da branch, sem ler o valor nem o papel (aperta; R-MAIN)
MERGE_POR_API = re.compile(r"(^|/)(pulls/[^/]+/merge|repos/[^/]+/[^/]+/merges)\b", re.I)
MERGE_NO_GRAPHQL = re.compile(r"mergePullRequest|enablePullRequestAutoMerge|enqueuePullRequest|mergeBranch", re.I)
ENDPOINT_GRAPHQL = re.compile(r"(^|/)graphql/?([?#]|$)", re.I)


def usa_admin(args):
    """`--admin` ou `--admin=<valor>`, em qualquer posição dos argumentos (até depois de `--` ou como valor de outra opção)."""
    return any(a == "--admin" or a.startswith("--admin=") for a in args)


PROGRAMA_GH = "gh"


def gh_de_merge_ou_api(args):
    """Os argumentos, lidos como se o programa fosse o `gh`, são `pr merge` ou `api`? (programa por expansão: falha fechado)"""
    achado = analisar([PROGRAMA_GH, *args])
    return bool(achado) and achado[0] in ("prmerge", "api")


def base_do_pr(raiz, branch):
    """Base do PR da branch, sem rede: a que o `gh pr create` guardou no git; senão, pelo fluxo do Forge."""
    cod, base = git(raiz, "config", "--get", f"branch.{branch}.gh-merge-base")
    if not cod and base:
        return nome_da_branch(base)
    if branch == "homolog":
        return "main"
    if branch == "develop":
        return "homolog"
    return "develop" if any(existe(raiz, r) for r in ("develop", "origin/develop")) else "main"


def branch_do_pr(raiz, alvo):
    """Branch do PR indicado em `gh pr merge [<alvo>]` (sem alvo, a atual); None se só há número ou URL."""
    if alvo is None:
        return git(raiz, "branch", "--show-current")[1] or None
    return None if NUMERO_OU_URL.match(alvo) else nome_da_branch(alvo.split(":")[-1])


URL_DO_PR = re.compile(r"^https?://[^/]+/([^/]+/[^/]+)/pull/", re.I)
FIM_DO_SLUG = re.compile(r"([^/:\s]+)/([^/:\s]+?)(?:\.git)?/*$")


def repo_da_url(alvo):
    """`dono/repo` da URL do PR (`https://github.com/dono/repo/pull/5`), que o `gh` usa no lugar do `-R`; senão None."""
    achado = URL_DO_PR.match(str(alvo))
    return achado.group(1) if achado else None


def slug(texto):
    """`dono/repo` minúsculo do fim de `-R` ([HOST/]DONO/REPO) ou da URL de um remoto (https, ssh, `git@host:`); senão
    None."""
    achado = FIM_DO_SLUG.search(str(texto))
    return f"{achado.group(1)}/{achado.group(2)}".lower() if achado else None


def remotos(raiz):
    """Os `dono/repo` em que o gh pode agir pelos remotos da cópia de trabalho `raiz`. GH-REMOTO-RESOLVIDO (A6 da E3.13):
    as URLs como o `git remote -v` as mostra (com `insteadOf` e `pushInsteadOf` aplicados, as que o gh lê) e o
    `remote.<nome>.gh-resolved` (o repositório escolhido no gh; `base` não é `dono/repo` e o `slug` o descarta). Sem os
    remotos, o hook não sabe onde o gh age: recusa."""
    codigo, linhas = git(raiz, "remote", "-v")
    if codigo:
        bloquear("R-REVIEW", "gh pr numa cópia cujos remotos o hook não lê (git remote -v falhou). Corrigir: use "
                             "-R <dono/repo> ou rode o gh de dentro do clone (cd <clone>)")
    valores = [url for linha in linhas.splitlines() for url in linha.split()[1:2]]
    resolvidos = git(raiz, "config", "--get-regexp", r"^remote\..*\.gh-resolved$")[1].splitlines()
    return {slug(v) for v in valores + [linha.partition(" ")[2] for linha in resolvidos]} - {None}


def sessao_ou(pasta):
    """A raiz da sessão (`CLAUDE_PROJECT_DIR`); sem ela, a pasta do gh, que não é clone: recusa."""
    return raiz_declarada() or pasta


REPO_INCERTO = "GH_REPO mexido antes na linha"  # GH-REPO-EXPORTADO: repositório indicado que o hook não lê


def repo_indicado(repo, mexidas):
    """GH-REPO-EXPORTADO (A5 da E3.8): sem `-R`, `--repo`, `GH_REPO=` no prefixo nem URL, o GH_REPO que a linha mexeu antes
    (`export`, `declare -x`, `set -a`, atribuição solta) é o repositório do gh, e o hook não lê o valor: REPO_INCERTO."""
    return REPO_INCERTO if repo is None and "GH_REPO" in mexidas else repo


def remotos_incertos(hook, resolvida, mexidas):
    """GH-REMOTO-NA-LINHA (A6 e A7 da E3.17): o motivo pelo qual os remotos que o gh lê podem não ser os que o hook leu
    antes de a linha rodar (D4 a D6 da matriz em docs/hooks.md), ou None."""
    if not resolvida:
        return "pasta do gh que o hook não resolve (variável, crase ou $( ) no cd)"
    if mexe_no_config_do_git(mexidas):
        return "variável que troca o config do git (GIT_*, HOME ou XDG_CONFIG_HOME) mexida na linha"
    if not linha_mantem_os_remotos(hook.campo("tool_input", "command")):
        return "outro programa na linha (git, script, gh fora de pr, redireção que grava) que pode mudar os remotos"
    return None


def pasta_do_gh(hook, pasta, repo, mexidas=frozenset(), resolvida=True):
    """INCIDENTE-HOOK-PARECER-CONTORNADO: a pasta em que o hook confere `gh pr create`, `ready` ou `merge`. Num clone do
    Forge ou num projeto, a do gh, como antes. Noutra pasta (fora de cópia de trabalho ou numa cópia alheia, que qualquer
    um cria com `git init`), o alvo do gh vem do `-R`/`--repo`, de `GH_REPO=`, da URL do PR ou, sem eles, dos remotos da
    cópia: vale o clone da sessão (`CLAUDE_PROJECT_DIR`) com remoto desse repositório. Com repositório indicado e sem
    esse clone, recusa (falha fechada): sem clone não há branch nem parecer a conferir. GH_REPO mexido antes na linha
    (`repo_indicado`) é repositório indicado que o hook não lê: recusa (GH-REPO-EXPORTADO). A cópia alheia sem repositório
    indicado e sem remoto do clone da sessão segue como antes, e também a sessão em que o hook não age (projeto com
    `hooks_desligados`, repositório alheio), salvo o `cd` que o hook não resolve (`resolvida` falso): aí o gh pode estar
    num clone e a pasta da chamada não vale, e recusa (A12 da E3.32)."""
    copia = copia_de_trabalho(pasta)
    if copia is not None and hook.projeto(pasta, clone_do_forge=True) is not None:
        return pasta
    sessao = sessao_ou(pasta)
    clone = hook.projeto(sessao, clone_do_forge=True)
    if clone is None and copia_de_trabalho(sessao) is not None:
        if resolvida:  # A12 da E3.32: sem a pasta do gh, a da chamada não vale (o gh pode estar num clone)
            return pasta
        bloquear("R-REVIEW", "gh pr depois de um cd que o hook não resolve (variável, ~ com HOME mexido, crase ou $( )) "
                             "numa sessão fora de clone: o gh pode estar num clone sem parecer. Corrigir: use o caminho "
                             "literal no cd ou rode o gh de dentro do clone")
    if repo is REPO_INCERTO:  # GH-REPO-EXPORTADO
        bloquear("R-REVIEW", "gh pr fora de um clone com GH_REPO mexido antes na linha (export, declare -x, set -a, source, "
                             "nome por expansão): o hook não lê o repositório indicado. Corrigir: use -R <dono/repo> ou rode "
                             "o gh de dentro do clone (cd <clone>)")
    pedido = slug(repo)
    if copia is not None and pedido is None:  # A2: sem -R, o gh age no repositório dos remotos da cópia
        motivo = clone and remotos_incertos(hook, resolvida, mexidas)
        if motivo:  # GH-REMOTO-NA-LINHA
            bloquear("R-REVIEW", f"gh pr numa cópia alheia sem -R e com {motivo}: o hook lê os remotos antes de a linha "
                                 "rodar. Corrigir: rode o gh pr sozinho na chamada (só o cd literal antes) ou use -R "
                                 "<dono/repo>")
        return clone if clone and remotos(copia) & remotos(clone) else pasta
    if pedido and clone and pedido in remotos(clone):
        return clone
    bloquear("R-REVIEW", f"gh pr fora de um clone do repositório indicado (-R, --repo, GH_REPO ou URL do PR: {repo}) e a "
                         "sessão não é clone dele: sem a branch, não há parecer a conferir. Corrigir: rode o gh de dentro "
                         "do clone (cd <clone>)")


def merge_de_pr(hook, pasta, repo, alvo):
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz:
        return
    if aponta_para_o_forge(repo) and not e_clone_do_forge(raiz):
        bloquear("R-CONTRIB", "projeto não mescla no Forge. Corrigir: abra o PR e deixe o tech-lead mesclar "
                              "a partir de um clone do Forge (~/.forge-contrib).")
    branch = branch_do_pr(raiz, alvo)
    if not branch:
        bloquear("R-CONTRIB", "PR indicado só por número, sem branch. Corrigir: use o nome da branch "
                              "(gh pr merge <branch>).")
    base = base_do_pr(raiz, branch)
    if base in ("main", "master"):
        bloquear("R-MAIN", f"gh pr merge de `{branch}` (base {base}) é do usuário. Corrigir: deixe o PR "
                           "aberto e peça ao usuário que o mescle.")
    if branch in INTEGRACAO:
        return  # promoção entre branches de integração
    ref = next((r for r in (branch, f"origin/{branch}") if existe(raiz, r)), None)
    if ref is None:
        bloquear("R-REVIEW", f"branch `{branch}` não existe localmente, sem parecer a conferir. Corrigir: "
                             "git fetch e tente de novo.")
    verificar(hook, raiz, branch, ref, next((b for b in (base, f"origin/{base}") if existe(raiz, b)), None), gravado=ATALHO)


def merge_por_api(hook, pasta, args):
    if not (ENDPOINT_MERGE.search(endpoint_da_api(args)) and metodo_mutante(args)):
        return
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz:
        return
    if aponta_para_o_forge(endpoint_da_api(args)) and not e_clone_do_forge(raiz):
        bloquear("R-CONTRIB", "projeto não mescla no Forge. Corrigir: abra o PR e deixe o tech-lead mesclar "
                              "a partir de um clone do Forge (~/.forge-contrib).")
    bloquear("R-CONTRIB", "merge por gh api não informa a branch, então não há parecer a conferir. "
                          "Corrigir: use gh pr merge <branch>.")


PRONTO_NO_GRAPHQL = re.compile(r"markPullRequestReadyForReview", re.I)


def graphql_no_clone(hook, pasta, args):
    """`gh api graphql` com método que muda e o clone do Forge como alvo: a pasta do gh ou, fora de clone e de projeto,
    a sessão, porque o graphql não usa a pasta e age no mesmo GitHub de qualquer uma (GRAPHQL-FORA-DO-CLONE). Nos
    projetos, o `conformidade` cuida do PR do Forge (R-CONTRIB)."""
    if not (ENDPOINT_GRAPHQL.search(endpoint_da_api(args)) and metodo_mutante(args)):
        return False
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if raiz is None:  # GRAPHQL-FORA-DO-CLONE
        raiz = hook.projeto(sessao_ou(pasta), clone_do_forge=True)
    return e_clone_do_forge(raiz)


def arquivo_trocado_na_linha(hook, pasta, args, acompanhado):
    """GH-API-ARQUIVO-TROCADO: o hook lê o arquivo da consulta (`=@`, `--input`) antes de a linha rodar; outro comando
    da mesma linha além do `cd` (`acompanhado`: `cp`, `mv`, `>`, `ln -sf`...) pode trocá-lo antes do gh: recusa."""
    if acompanhado and any(a.startswith("--input") or "=@" in a for a in args) and graphql_no_clone(hook, pasta, args):
        bloquear("R-CONTRIB", "gh api graphql que lê arquivo na mesma chamada de outro comando, que pode trocar o arquivo "
                              "depois da leitura do hook. Corrigir: rode o gh api graphql sozinho na chamada (só o cd "
                              "pode vir antes).")


def api_depois_de_cd_sem_resolver(hook, pasta, args, resolvida):
    """A13 da E3.34: a guarda do A12 (`pasta_do_gh`) no `gh api`. Com a sessão fora de clone e de projeto (numa cópia
    alheia ou fora de cópia de trabalho), o `cd` que o hook não resolve deixa a pasta da chamada no lugar da do gh, que
    pode ser um clone sem parecer: recusa o que as regras do clone recusariam, o merge com método que muda
    (`merge_por_api`) e o graphql que muda e que tira o rascunho ou não dá para ler (`pronto_por_graphql`). O GET e o
    graphql de leitura legível seguem."""
    if resolvida or not metodo_mutante(args):
        return
    if hook.projeto(sessao_ou(pasta), clone_do_forge=True) is not None:  # na sessão no clone, valem as regras dele
        return
    endpoint = endpoint_da_api(args)
    if ENDPOINT_MERGE.search(endpoint) or ENDPOINT_GRAPHQL.search(endpoint) and tira_o_rascunho(args, None):
        bloquear("R-REVIEW", "gh api de merge ou de graphql que muda depois de um cd que o hook não resolve (variável, ~ "
                             "com HOME mexido, CDPATH, crase ou $( )) numa sessão fora de clone: o gh pode estar num "
                             "clone sem parecer. Corrigir: use o caminho literal no cd ou rode o gh de dentro do clone")


def tira_o_rascunho(args, base):
    """A consulta do `gh api graphql` tira o PR do rascunho ou não dá para ler (falha fechada; GH-API-LEITURA-UNICA)."""
    textos, legivel = textos_do_gh_api(desagrupa_i(args), base)  # GH-API-LEITURA-UNICA: a leitura do hooks/_gh_api.py
    if not legivel or any(PRONTO_NO_GRAPHQL.search(t) for t in textos):
        return True
    return False


def pronto_por_graphql(hook, pasta, args, base):
    """FILA-27 A2: no clone do Forge, `markPullRequestReadyForReview` tira o PR do rascunho sem dizer a branch, então não
    há parecer a conferir (`pronto_de_pr`); a consulta que não dá para ler recusa (falha fechada). `pasta`: a do `gh`
    (`raiz_gh`); `base`: a que o hook resolveu na linha (None: desconhecida), onde se leem os arquivos relativos."""
    if not graphql_no_clone(hook, pasta, args):
        return
    if tira_o_rascunho(args, base):
        bloquear("R-CONTRIB", "tirar o rascunho pela API não informa a branch, ou a consulta não dá para ler. Corrigir: "
                              "use gh pr ready <branch> (exige os pareceres) ou o forge-fechar.")


def principal(hook):
    comando = hook.campo("tool_input", "command")
    if hook.campo("tool_name") != "Bash" or not isinstance(comando, str):
        return
    textos = textos_da_linha(comando)
    if not any(PREFILTRO.search(g) for g in textos) and not alias_na_linha(textos):  # HOOK-CONTINUACAO-LINHA: e `g\h`, `g'h'`
        return
    ambiente = SEM_AMBIENTE._replace(mexidas=mexidas_do_texto(textos))  # o `conferir` soma os DESVIOS
    conferir_linha(hook, SED_LE.sub(r"cat\2", comando), [(hook.cwd(), {}, ambiente)])


def marcas_da_chamada(original, comando, corpos, leitores):
    """(a chamada tem a marca crítica, `critico_ou_alias`; e fora dos corpos de shell que só leem ou esperam): o corpo
    `python` de `leitores_dos_corpos` e o `dado` (`corpos_de_dado`) não marcam, e o `shell` só marca a primeira. Sem
    eles, as duas são a do texto inteiro."""
    if not any(leitores):
        return (critico_ou_alias(original),) * 2
    def sem(tipos):
        return critico_ou_alias("\n".join([comando, *(c for (_, c), t in zip(corpos, leitores) if t not in tipos)]))
    return sem({"python", "dado"}), sem({"python", "dado", "shell"})


def conferir_linha(hook, comando, estados, nivel=0, so_substituicoes=False, corpo_de_heredoc=False, reavaliacoes=None,
                   acompanhado=False):
    """Confere a linha a partir de cada estado (pasta, branches) e, depois, o que ela roda dentro de uma palavra só: o
    corpo de cada crase (P4: `` echo `gh pr merge …` ``) e a palavra com `$(…)` entre aspas (N2: `echo "$(gh pr merge
    …)"`), esta só pelo conteúdo das substituições. O de dentro roda num subshell, a partir de um dos estados por onde a
    linha passa: é conferido a partir de cada um. `so_substituicoes`: a linha é uma dessas palavras. `corpo_de_heredoc`:
    a linha é o corpo de um heredoc que vai a um programa fora da lista dos que só o leem. `reavaliacoes`: as
    reavaliações pelo shell (`reavaliacao`) achadas em qualquer nível, recusadas no fim do nível 0 com o marcador.
    `acompanhado`: algum nível de cima roda outro comando além do `cd` (GH-API-ARQUIVO-TROCADO)."""
    reavaliacoes = [] if reavaliacoes is None else reavaliacoes
    for forma in formas_que_o_shell_le(comando, corpo_de_heredoc):  # HOOK-CONTINUACAO-LINHA: a que o bash roda
        conferir_linha(hook, forma, estados, nivel, so_substituicoes, corpo_de_heredoc, reavaliacoes, acompanhado)
    if nivel > PROFUNDIDADE:
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull aninhada fundo demais para o hook ler. Corrigir: "
                             "rode o comando direto, sem crase nem $( dentro de outro")
    original = comando
    try:  # o corpo de um heredoc não é comando: com apóstrofo, sem par, ele deixaria a linha ilegível (A1 do review)
        comando, corpos, gravado = tirar_heredocs(comando, com_gravado=True)
    except ValueError:  # `<<` em dúvida com linha depois, ou corpo sem aspas no delimitador com `$(` ou crase (o bash roda)
        if isinstance(corpo_de_heredoc, str):  # outro programa do texto pode rodar o corpo gravado: a causa é essa;
            # o dono que roda o corpo (`sh <<'EOF'`, valor True) segue com o `<<'FIM'` para o heredoc de dentro
            bloquear("R-REVIEW", "corpo de heredoc que a chamada pode rodar e que o hook não lê, com gh pr, gh api, merge "
                                 f"ou pull. Corrigir: {GRAVE_E_RODE_NOUTRA}")
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull com um heredoc que o hook não lê (<< que ele não "
                             "prova ser heredoc, ou corpo sem aspas no delimitador com $( ou crase). Corrigir: use "
                             "<<'FIM' ou separe os comandos")
    leitores = leitores_dos_corpos(original, comando, corpos)
    marcado, marcado_fora_do_shell = marcas_da_chamada(original, comando, corpos, leitores)
    if nivel == 0 and critico_ou_alias(original):  # bloco T da revalidação 10: o orçamento da chamada, antes de ler o resto
        excesso = excede_o_teto(comando)
        if excesso:
            bloquear("R-REVIEW", f"chamada com gh pr, gh api, merge ou pull e {excesso}: o hook não a decide dentro do "
                                 f"prazo. Corrigir: {CONTORNO_DO_TETO}")
    lidas = leituras(comando, com_sinal=True)
    # opção B da revalidação 9: sobre a palavra que o bash recebe, em qualquer posição. A palavra `"$(…)"` não: o texto
    # dela é o do `shlex`, e o nível de fora já leu as substituições dela como escritas
    achada = None if so_substituicoes else reavaliacao(comando)
    if achada and (corpos or not e_shell_c_de_texto(comando)):
        reavaliacoes.append(achada)
    if lidas.ilegivel and isinstance(corpo_de_heredoc, str):  # M2: só o programa do texto o roda
        bloquear("R-REVIEW", f"o texto roda `{corpo_de_heredoc}`, fora da lista dos que não rodam o arquivo gravado, e "
                             f"o corpo do heredoc tem aspa sem par. Corrigir: {GRAVE_E_RODE_NOUTRA}")
    if lidas.ilegivel and corpo_de_heredoc:  # A1 do review, volta 3: <<'FIM' já está na linha
        bloquear("R-REVIEW", "gh pr, gh api, merge ou pull e corpo de heredoc com aspa sem par, a programa que pode "
                             "rodá-lo. Corrigir: grave o texto pelo Write ou Edit e passe-o ao programa "
                             "noutra chamada do Bash")
    if lidas.ilegivel:  # ADR 0013, tabela 2.4: passou no PREFILTRO (gh pr, gh api, merge, pull) e o hook não a lê
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge, pull ou alias do gh que o hook não lê (aspas sem par ou # "
                             "que ele não prova ser comentário). Corrigir: feche as aspas, tire o comentário ou separe os "
                             "comandos")
    internos = [(corpo, False, False) for corpo in conteudos_de_crase(comando, so_os_fechados=True)]
    internos += [(corpo, False, getattr(dono, "rodado", None) or True)  # o dono (ou o programa do texto) pode rodá-lo
                 for (dono, corpo), leitor in zip(corpos, leitores) if leitor not in ("python", "dado") and not corpo_so_lido(dono)]
    vistos, acompanhado_dentro = {}, acompanhado
    for leitura in lidas.partes:  # a fiel e, se diferir, a da develop (I2)
        partes = [(analise_do_comando(palavras), palavras, solto)
                  for (todas, _, sub, _), solto in zip(leitura, soltos(leitura)) if sub or not so_substituicoes
                  for palavras in [sem_chaves(todas)]]
        aqui = acompanhado or sum(1 for parte, _, _ in partes if not (parte and parte[0] == "cd")) > 1
        acompanhado_dentro = acompanhado_dentro or aqui
        for pasta, branches, ambiente in estados:
            for estado in conferir(hook, partes, pasta, branches, ambiente, aqui):
                vistos.setdefault((estado[0], tuple(sorted(estado[1].items())), estado[2]), estado)
        internos += [(p, True, False) for palavras, _, _, _ in leitura for p in palavras
                     if "$(" in p.replace(OPACO["$"], "")]
    for texto, so, de_heredoc in dict.fromkeys(internos):
        conferir_linha(hook, texto, list(vistos.values()), nivel + 1, so, de_heredoc, reavaliacoes, acompanhado_dentro)
    if gravado and marcado:  # M3 (ADR 0011, item 2), depois das regras da linha e do corpo
        bloquear("R-REVIEW", f"heredoc gravado e programa não modelado na mesma chamada (`{gravado}`), com gh pr, gh "
                             f"api, merge ou pull. Corrigir: {GRAVE_E_RODE_NOUTRA}")
    # ADR 0011, item 2 (opção B da revalidação 8), depois das regras da linha e do corpo: com o marcador no nível 0, a
    # reavaliação pelo shell em qualquer nível recusa (o parecer não segue `eval` nem `bash -c`; o texto deles não chega)
    if nivel == 0 and reavaliacoes and critico_ou_alias(original):
        bloquear("R-REVIEW", f"`{reavaliacoes[0]}` na chamada com gh pr, gh api, merge ou pull: "
                             f"{motivo_da_reavaliacao(reavaliacoes[0])}. Corrigir: "
                             f"{contorno_da_reavaliacao(reavaliacoes[0])}")
    # ADR 0011, item 2 (opções D e A), depois das regras da linha e do corpo: sobre o texto do nível 0, com o `<<` que o
    # bash pode formar nele ou num nível de cima (`bash -c`, `eval`, `$(…)`; `tem_heredoc_no_texto`), haja heredoc
    # provado ou não; a marca só no corpo de Python ou de shell que só lê ou espera (`leitores_dos_corpos`) não a liga
    if nivel == 0 and marcado_fora_do_shell and not (SO_CAT.fullmatch(comando) and heredocs_simples(original)):
        sinal = fora_da_gramatica_com_heredoc(ALVO_DO_CAT.sub(r"\1_", original))
        if sinal is not None:
            bloquear("R-REVIEW", f"`{sinal}` na chamada com heredoc e gh pr, gh api, merge ou pull: o hook não modela. "
                                 f"Corrigir: {CONTORNO_DA_GRAMATICA}")


def conferir(hook, partes, pasta, branches, ambiente=SEM_AMBIENTE, acompanhado=False):
    """Os comandos de uma leitura da linha, em ordem (`cd`, atribuição e checkout/switch valem para os seguintes), a
    partir da pasta (None: desconhecida), das branches e do ambiente dados; devolve os estados (pasta, branches,
    ambiente) por onde a leitura passou. `partes`: (`analisar`, palavras, solto) de cada comando; só o `cd` solto (`soltos`)
    muda a pasta dos seguintes, o de subshell, pipeline, segundo plano ou condicional a deixa desconhecida.
    `acompanhado`: a linha roda outro comando além do `cd` (`arquivo_trocado_na_linha`)."""
    branches = dict(branches)  # raiz do projeto -> branch depois de checkout/switch na linha
    mexidas, desviado = ambiente.mexidas, ambiente.desviado
    estados = [(pasta, dict(branches), ambiente)]
    fila = collections.deque(partes)
    while fila:
        parte, palavras, solto = fila.popleft()
        if parte and parte[0] == "alias":  # 0.45.4: cada leitura do alias do gh, com as mesmas regras e a mesma pasta
            if parte[1] not in leitor_do_alias().COMANDOS_DO_GH and CONFIG_DO_GH & mexidas:
                bloquear("R-REVIEW", f"gh {parte[1]}: a linha mudou antes a configuração do gh (GH_CONFIG_DIR, XDG_CONFIG_HOME "
                                     "ou HOME) e o hook não sabe qual alias vale. Corrigir: rode o comando do gh por extenso")
            fila.extendleft(reversed([(lida, palavras, solto) for lida in parte[2]]))
            continue
        mexidas = mexidas | mexidas_na_linha(palavras)
        desviado |= bool(DESVIOS & mexidas)
        sem = sem_atribuicoes(palavras)
        raiz_gh = pasta or hook.cwd()  # o `gh` acha o repositório pelo nome da branch: sem pasta resolvida, vale a da sessão
        gh_na = (mexidas, pasta is not None)  # D4 e D6 da cópia alheia (`remotos_incertos`)
        comando = sem_condicao(sem)
        if comando[:1] in (["pushd"], ["popd"]) or comando[:1] == ["cd"] and len(comando) < len(sem):
            pasta = None  # a pilha o hook não segue; o `cd` de `if`, `while`... roda fora do que ele lê
        elif parte is None:
            pass
        elif parte[0] == "cd":
            pasta = (depois_do_cd(pasta, sem[1:], mexidas) if sem[1:] else resolver("~", mexidas, pasta)) if solto else None
        elif parte[0] == "pr":
            pull_request(hook, pasta_do_gh(hook, raiz_gh, repo_indicado(parte[5], mexidas), *gh_na), parte[2], parte[3], parte[4],
                         (pasta, parte[6]))
        elif parte[0] == "prready":
            pronto_de_pr(hook, pasta_do_gh(hook, raiz_gh, repo_indicado(parte[3], mexidas), *gh_na), parte[1], parte[2])
        elif parte[0] == "prmerge":
            merge_de_pr(hook, pasta_do_gh(hook, raiz_gh, repo_indicado(parte[1], mexidas), *gh_na), parte[1], parte[2])
        elif parte[0] == "api":
            api_depois_de_cd_sem_resolver(hook, raiz_gh, parte[1], pasta is not None)  # A13 da E3.34
            merge_por_api(hook, raiz_gh, parte[1])
            arquivo_trocado_na_linha(hook, raiz_gh, parte[1], acompanhado)
            pronto_por_graphql(hook, raiz_gh, parte[1], pasta)
        elif parte[0] == "branch":
            onde = pasta_do_git(pasta, pastas_do_git(palavras), mexidas, desviado)
            raiz = raiz_de_estado(onde) if onde else None
            if raiz:
                branches[raiz.resolve()] = parte[2]
            desviado |= onde is None  # trocou a branch de uma pasta que o hook não sabe qual é
        else:  # merge ou pull
            onde = pasta_do_git(pasta, pastas_do_git(palavras), mexidas, desviado)
            if onde is None:
                bloquear("R-REVIEW", "merge ou pull numa pasta que o hook não resolve (variável, crase ou $( ) na pasta, "
                                     "`cd` fora do nível de cima da linha, pasta que não existe, pushd, --git-dir, "
                                     "--work-tree ou GIT_DIR). Corrigir: use `cd <caminho literal>` ou `git -C <caminho "
                                     "literal>`, sem variável; o push pode ir na mesma chamada")
            merge(hook, onde, parte[2], branches)
        estados.append((pasta, dict(branches), Ambiente(mexidas, desviado)))
    return estados


if __name__ == "__main__":
    executar("parecer", principal, CriticoOuAlias, clone_do_forge=True, regra_do_prazo="R-REVIEW", prazo_longo=MERGE_DE_PR)
