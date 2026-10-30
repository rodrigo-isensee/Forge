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
A isenção é a regra única do forge-check (`isencoes_da_entrega`, M13): diff só de `.md` comum dispensa o QA e exige o
review; `.md` de controle (`agents/`, `skills/`, `stacks/*/agents|skills/`, `stacks/*/seguranca.md` e `pronto.md`, `docs/regras/`, `templates/projeto/`, `CLAUDE.md`) não tem isenção. Libera
atualização a partir de uma branch de integração e promoção entre branches de integração. O merge de PR (ADR 0008, 4.3) é resolvido sem rede, pela branch: base `main` é `R-MAIN`;
PR só por número, `gh api` de merge e merge no Forge a partir de projeto são `R-CONTRIB`.
No clone do Forge (`raiz_de_estado`: `~/Forge` e as worktrees de `~/.forge-contrib/wt/`) age também, sem
`hooks_desligados`, e o PR fica em rascunho até o parecer: `gh pr create --draft` passa sem parecer e `gh pr ready`
exige o parecer, como o merge (o GitHub não mescla PR em rascunho).
Falha fechado nas ações críticas (ADR 0009, seção 7), também no clone do Forge.
"""
import collections
import json
import os
import re
from pathlib import Path
from types import SimpleNamespace

from _comum import (CONTORNO_DA_GRAMATICA, CONTORNO_DO_TETO, INTEGRACAO, OPACO, OPCAO_DE_REAVALIACAO, PLUGIN,
                    PROFUNDIDADE, SHELLS_DA_REAVALIACAO, bloquear,
                    contorno_da_reavaliacao, conteudos_de_crase, corpo_so_lido, depois_das_atribuicoes, e_clone_do_forge,
                    excede_o_teto, executar,
                    fora_da_gramatica_com_heredoc, forge_check, git, nome_da_branch, leituras, motivo_da_reavaliacao,
                    palavras_do_texto, raiz_de_estado, reavaliacao, reavaliacao_das_palavras, reduzida, sem_atribuicoes,
                    separar_regra, tirar_heredocs)

MERGE = r"merge(?!-base\b)"  # `git merge-base` só lê o grafo (HK3-PARECER, E2): não é merge
PREFILTRO = re.compile(rf"\bgh\b.*\bpr\b.*\b(create|{MERGE}|ready)\b|\bgh\b.*\bapi\b|\bgit\b.*\b({MERGE}|pull)\b", re.S)
CRITICO = re.compile(rf"\bpr\b.*\b(create|{MERGE}|ready)\b|\bapi\b|\b({MERGE}|pull)\b", re.S)
# A palavra crítica só no texto (HK3-PARECER, E2). `sed -n <N,Mp> <arquivos>` só imprime: vale `cat <arquivos>` (só números,
# sem metacaractere: a troca não muda o que o bash lê). `sh -c` cujo texto só usa estes programas não roda merge, pull nem gh pr.
SED_LE = re.compile(r"(?<![^\s;&|(])sed -n (['\"]?)\d+(?:,\d+)?p\1((?: +[\w./~@:+%,][\w./~@:+%,=-]*)*)(?=[ \t]*(?:[;&|)\n]|$))")
# Chamada só de `cat` (sem aspa, `$`, `#`, `;`, `&`, `|` nem parêntese: nada que mude como o bash lê as linhas): os corpos de
# heredoc dela são texto, e a gramática positiva do D (a rede contra o que o leitor não vê) não tem o que recusar.
SO_CAT = re.compile(r"(?:[ \t]*cat(?:[ \t]+>{0,2}[ \t]*[\w./~@:+%,-]+)*[ \t]*(?:\n|$))+")
# `<<`/`<<-` seguido de `'PALAVRA'`, `"PALAVRA"` ou `PALAVRA` (só \w): o bash e o hook cortam o corpo no mesmo ponto.
HEREDOC_SIMPLES = re.compile(r"(?<!<)<<(-?)[ \t]*(?:'(\w+)'|\"(\w+)\"|(\w+))(?=[ \t]|$)")
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
EXPANSAO = ("$", "`")  # o que o bash expande (`$( )` é `$`): a palavra deixa de ser caminho literal
CORPO = {"{", "then", "do", "else"}
CONDICAO = {"if", "elif", "while", "until", "!", "time", "function"}  # abrem a parte; o `cd` depois delas roda
SUBCOMANDOS = {"merge", "pull", "checkout", "switch"}
ABRE = {"if", "while", "until", "for", "case", "select", "then", "do", "else", "elif", "{", "function", "coproc"}
LE_VARIAVEL = {"source", ".", "eval", "read", "mapfile", "readarray", "getopts", "for", "select", "let", "declare",
               "typeset", "local", "readonly", "unset", "set", "printf"}  # mexem em variável sem `NOME=` na palavra
DESVIOS = {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
SENSIVEIS = DESVIOS | {"HOME", "CDPATH"}  # o bash e o git os leem sozinhos: mexidos na linha, a pasta fica desconhecida
ATRIBUICAO = re.compile(r"^([A-Za-z_]\w*)\+?=")
Ambiente = collections.namedtuple("Ambiente", "mexidas desviado")  # mexidas: os SENSIVEIS que a linha mexeu (frozenset)
SEM_AMBIENTE = Ambiente(frozenset(), bool(DESVIOS & set(os.environ)))
BASES = ("develop", "origin/develop", "main", "origin/main", "master", "origin/master")


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


def expande(palavra):
    return any(o in palavra for o in EXPANSAO)


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


def analisar(toks):
    """('cd', dir) | ('pr', None, base, head, rascunho) | ('prmerge', repo, alvo) | ('prready', alvo, desfaz) | ('api', args)
    | ('merge', dir, [(branch, [refs candidatas])]) | ('branch', dir, nome) | None."""
    sem = sem_atribuicoes(toks)
    atribuicoes, toks = toks[: len(toks) - len(sem)], sem
    if not toks:
        return None
    if toks[0] == "cd":
        return ("cd", toks[1] if len(toks) > 1 else None)
    if toks[0] == "gh":
        if toks[1:2] == ["api"]:
            return ("api", toks[2:])
        if "pr" not in toks:
            return None
        i = toks.index("pr")
        args = toks[i + 2:]
        if toks[i + 1: i + 2] == ["create"]:
            return ("pr", None, opcao(args, "--base", "-B"), opcao(args, "--head", "-H"),
                    bandeira(args, CREATE_COM_VALOR, {"--draft", "-d"}))
        if toks[i + 1: i + 2] == ["ready"]:
            return ("prready", (posicionais(args, READY_COM_VALOR) or [None])[0],
                    bandeira(args, READY_COM_VALOR, {"--undo"}))
        if toks[i + 1: i + 2] == ["merge"]:
            repo = opcao(args, "--repo", "-R") or next((a.split("=", 1)[1] for a in atribuicoes
                                                        if a.startswith("GH_REPO=")), None)
            alvo = (posicionais(args, MERGE_PR_COM_VALOR) or [None])[0]
            return ("prmerge", repo, alvo)
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


def mexidas_na_linha(palavras):
    """Os SENSIVEIS que o comando mexe: por prefixo (`HOME=x cd`), atribuição (`HOME=x`, `export HOME=x`) ou nome em `read`,
    `printf -v`, `declare`, `unset`... A pasta que depende deles fica desconhecida."""
    k = depois_das_atribuicoes(palavras)
    comando = palavras[k:]
    nomes = {ATRIBUICAO.match(a).group(1) for a in palavras[:k]}
    nomes |= {m.group(1) for m in map(ATRIBUICAO.match, comando) if m}
    if comando and comando[0] in LE_VARIAVEL:
        nomes |= {p.split("=", 1)[0] for p in comando[1:]}  # `read HOME`, `printf -v GIT_DIR`
    return SENSIVEIS & nomes


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


def verificar(hook, raiz, branch, ref, base, dica=""):
    """Bloqueia se a branch não tem os pareceres exigidos aprovados e válidos. A isenção é a do `forge-check` (M13,
    `isencoes_da_entrega`): só o QA, em diff só de `.md` fora dos de controle; o review vale sempre. `dica` abre o motivo."""
    fc = forge_check()
    guarda_de_versao(fc, raiz)
    sha_base = git(raiz, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}")[1] if base else ""
    base = sha_base or None  # o sha: `HEAD` ou um nome local não viram `origin/<nome>` na resolução da base
    pedidos = fc.pedidos_da_branch(raiz, branch, ref)
    if not pedidos:
        so_review = "qa" in fc.isencoes_da_entrega(raiz, ref, base)
        bloquear("R-REVIEW", f"{dica}nenhum parecer em docs/reviews/{'' if so_review else ' e docs/qa/'} com `branch: {branch}`; "
                             + ("faça o code review antes do PR ou do merge (só .md comum: isento de QA, R-QA)." if so_review else
                                "faça o code review e o QA (R-QA) antes do PR ou do merge (devops e segurança, "
                                "quando há gatilho, ficam em docs/devops/ e docs/security/)."))
    for pedido in pedidos:
        violacoes = fc.cmd_pr(raiz, pedido, ref)  # modo estrito, sem base: o merge da base depois do parecer o invalida
        if violacoes:
            rid, texto = separar_regra(violacoes[0], "R-REVIEW")
            extra = f" (e mais {len(violacoes) - 1})" if len(violacoes) > 1 else ""
            bloquear(rid, f"{dica}{texto}{extra}; confira com forge-check pr {pedido}.")


def pull_request(hook, pasta, base, head, rascunho):
    raiz = hook.projeto(pasta, clone_do_forge=True)
    if not raiz:
        return
    forge = e_clone_do_forge(raiz)
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
              "sem parecer aprovado, abra com gh pr create --draft; " if forge else "")


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
              "PR sai do rascunho só com parecer: ")


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
            verificar(hook, raiz, branch, ref, atual if chave in branches else "HEAD")


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


def metodo_mutante(args):
    """True se o `gh api` altera algo: método diferente de GET, ou campos (que viram POST)."""
    metodo = opcao(args, "--method", "-X")
    if metodo:
        return metodo.upper() != "GET"
    return any(a in ("-f", "-F", "--field", "--raw-field", "--input") or a.startswith(("--field=", "--raw-field="))
               for a in args)


def endpoint_da_api(args):
    return (posicionais(args, API_COM_VALOR) or [""])[0]


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
    verificar(hook, raiz, branch, ref, next((b for b in (base, f"origin/{base}") if existe(raiz, b)), None))


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


def principal(hook):
    comando = hook.campo("tool_input", "command")
    if hook.campo("tool_name") != "Bash" or not isinstance(comando, str) or not PREFILTRO.search(comando):
        return
    conferir_linha(hook, SED_LE.sub(r"cat\2", comando), [(hook.cwd(), {}, SEM_AMBIENTE)])


def conferir_linha(hook, comando, estados, nivel=0, so_substituicoes=False, corpo_de_heredoc=False, reavaliacoes=None):
    """Confere a linha a partir de cada estado (pasta, branches) e, depois, o que ela roda dentro de uma palavra só: o
    corpo de cada crase (P4: `` echo `gh pr merge …` ``) e a palavra com `$(…)` entre aspas (N2: `echo "$(gh pr merge
    …)"`), esta só pelo conteúdo das substituições. O de dentro roda num subshell, a partir de um dos estados por onde a
    linha passa: é conferido a partir de cada um. `so_substituicoes`: a linha é uma dessas palavras. `corpo_de_heredoc`:
    a linha é o corpo de um heredoc que vai a um programa fora da lista dos que só o leem. `reavaliacoes`: as
    reavaliações pelo shell (`reavaliacao`) achadas em qualquer nível, recusadas no fim do nível 0 com o marcador."""
    reavaliacoes = [] if reavaliacoes is None else reavaliacoes
    if nivel > PROFUNDIDADE:
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull aninhada fundo demais para o hook ler. Corrigir: "
                             "rode o comando direto, sem crase nem $( dentro de outro")
    original = comando
    try:  # o corpo de um heredoc não é comando: com apóstrofo, sem par, ele deixaria a linha ilegível (A1 do review)
        comando, corpos, gravado = tirar_heredocs(comando, com_gravado=True)
    except ValueError:  # `<<` em dúvida com linha depois, ou corpo sem aspas no delimitador com `$(` ou crase (o bash roda)
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull com um heredoc que o hook não lê (<< que ele não "
                             "prova ser heredoc, ou corpo sem aspas no delimitador com $( ou crase). Corrigir: use "
                             "<<'FIM' ou separe os comandos")
    if nivel == 0 and CRITICO.search(original):  # bloco T da revalidação 10: o orçamento da chamada, antes de ler o resto
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
                             "o corpo do heredoc tem aspa sem par. Corrigir: grave numa chamada do Bash e rode o "
                             "programa noutra")
    if lidas.ilegivel and corpo_de_heredoc:  # A1 do review, volta 3: <<'FIM' já está na linha
        bloquear("R-REVIEW", "gh pr, gh api, merge ou pull e corpo de heredoc com aspa sem par, a programa que pode "
                             "rodá-lo. Corrigir: grave o texto num arquivo e passe-o ao programa noutra chamada do "
                             "Bash")
    if lidas.ilegivel:  # ADR 0013, tabela 2.4: passou no PREFILTRO (gh pr, gh api, merge, pull) e o hook não a lê
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull que o hook não lê (aspas sem par ou # que ele "
                             "não prova ser comentário). Corrigir: feche as aspas, tire o comentário ou separe os comandos")
    internos = [(corpo, False, False) for corpo in conteudos_de_crase(comando, so_os_fechados=True)]
    internos += [(corpo, False, getattr(dono, "rodado", None) or True)  # o dono (ou o programa do texto) pode rodá-lo
                 for dono, corpo in corpos if not corpo_so_lido(dono)]
    vistos = {}
    for leitura in lidas.partes:  # a fiel e, se diferir, a da develop (I2)
        partes = [(analisar(palavras), palavras, solto)
                  for (todas, _, sub, _), solto in zip(leitura, soltos(leitura)) if sub or not so_substituicoes
                  for palavras in [sem_chaves(todas)]]
        for pasta, branches, ambiente in estados:
            for estado in conferir(hook, partes, pasta, branches, ambiente):
                vistos.setdefault((estado[0], tuple(sorted(estado[1].items())), estado[2]), estado)
        internos += [(p, True, False) for palavras, _, _, _ in leitura for p in palavras
                     if "$(" in p.replace(OPACO["$"], "")]
    for texto, so, de_heredoc in dict.fromkeys(internos):
        conferir_linha(hook, texto, list(vistos.values()), nivel + 1, so, de_heredoc, reavaliacoes)
    if gravado and CRITICO.search(original):  # M3 (ADR 0011, item 2), depois das regras da linha e do corpo
        bloquear("R-REVIEW", f"heredoc gravado e programa não modelado na mesma chamada (`{gravado}`), com gh pr, gh "
                             "api, merge ou pull. Corrigir: grave o arquivo pelo Write ou numa chamada do Bash e rode "
                             "o programa noutra")
    # ADR 0011, item 2 (opção B da revalidação 8), depois das regras da linha e do corpo: com o marcador no nível 0, a
    # reavaliação pelo shell em qualquer nível recusa (o parecer não segue `eval` nem `bash -c`; o texto deles não chega)
    if nivel == 0 and reavaliacoes and CRITICO.search(original):
        bloquear("R-REVIEW", f"`{reavaliacoes[0]}` na chamada com gh pr, gh api, merge ou pull: "
                             f"{motivo_da_reavaliacao(reavaliacoes[0])}. Corrigir: "
                             f"{contorno_da_reavaliacao(reavaliacoes[0])}")
    # ADR 0011, item 2 (opções D e A), depois das regras da linha e do corpo: sobre o texto do nível 0, com o `<<` que o
    # bash pode formar nele ou num nível de cima (`bash -c`, `eval`, `$(…)`; `tem_heredoc_no_texto`), haja heredoc
    # provado ou não
    if nivel == 0 and CRITICO.search(original) and not (SO_CAT.fullmatch(comando) and heredocs_simples(original)):
        sinal = fora_da_gramatica_com_heredoc(original)
        if sinal is not None:
            bloquear("R-REVIEW", f"`{sinal}` na chamada com heredoc e gh pr, gh api, merge ou pull: o hook não modela. "
                                 f"Corrigir: {CONTORNO_DA_GRAMATICA}")


def conferir(hook, partes, pasta, branches, ambiente=SEM_AMBIENTE):
    """Os comandos de uma leitura da linha, em ordem (`cd`, atribuição e checkout/switch valem para os seguintes), a
    partir da pasta (None: desconhecida), das branches e do ambiente dados; devolve os estados (pasta, branches,
    ambiente) por onde a leitura passou. `partes`: (`analisar`, palavras, solto) de cada comando; só o `cd` solto (`soltos`)
    muda a pasta dos seguintes, o de subshell, pipeline, segundo plano ou condicional a deixa desconhecida."""
    branches = dict(branches)  # raiz do projeto -> branch depois de checkout/switch na linha
    mexidas, desviado = ambiente.mexidas, ambiente.desviado
    estados = [(pasta, dict(branches), ambiente)]
    for parte, palavras, solto in partes:
        mexidas = mexidas | mexidas_na_linha(palavras)
        desviado |= bool(DESVIOS & mexidas)
        sem = sem_atribuicoes(palavras)
        raiz_gh = pasta or hook.cwd()  # o `gh` acha o repositório pelo nome da branch: sem pasta resolvida, vale a da sessão
        comando = sem_condicao(sem)
        if comando[:1] in (["pushd"], ["popd"]) or comando[:1] == ["cd"] and len(comando) < len(sem):
            pasta = None  # a pilha o hook não segue; o `cd` de `if`, `while`... roda fora do que ele lê
        elif parte is None:
            pass
        elif parte[0] == "cd":
            pasta = (depois_do_cd(pasta, sem[1:], mexidas) if sem[1:] else resolver("~", mexidas, pasta)) if solto else None
        elif parte[0] == "pr":
            pull_request(hook, raiz_gh, parte[2], parte[3], parte[4])
        elif parte[0] == "prready":
            pronto_de_pr(hook, raiz_gh, parte[1], parte[2])
        elif parte[0] == "prmerge":
            merge_de_pr(hook, raiz_gh, parte[1], parte[2])
        elif parte[0] == "api":
            merge_por_api(hook, raiz_gh, parte[1])
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
    executar("parecer", principal, CRITICO, clone_do_forge=True, regra_do_prazo="R-REVIEW")
