#!/usr/bin/env python3
"""Forge: parecer de review e de QA antes de PR e de merge (ADR 0003, R-REVIEW, R-QA).

PreToolUse (Bash) com `gh pr create`, `gh pr merge`, `gh api .../pulls/<n>/merge`, ou `git merge <branch>` e
`git pull <remoto> <branch>` na branch de integração: exige parecer aprovado e válido para a branch (validado pelo
forge-check, ADR 0004); com pipeline, contêiner ou IaC no diff, também o de devops (R-REVIEW); com gatilho de segurança, o
de segurança (R-SEGURANCA). A branch atual acompanha `cd`, `git checkout` e `git switch` anteriores na mesma linha.
A isenção é a regra única do forge-check (`isencoes_da_entrega`, M13): diff só de `.md` comum dispensa o QA e exige o
review; `.md` de controle (`agents/`, `skills/`, `stacks/*/agents|skills/`, `stacks/*/seguranca.md` e `pronto.md`, `docs/regras/`, `templates/projeto/`, `CLAUDE.md`) não tem isenção. Libera
atualização a partir de uma branch de integração e promoção entre branches de integração. O merge de PR (ADR 0008, 4.3) é resolvido sem rede, pela branch: base `main` é `R-MAIN`;
PR só por número, `gh api` de merge e merge no Forge a partir de projeto são `R-CONTRIB`.
No clone do Forge (`raiz_de_estado`: `~/Forge` e as worktrees de `~/.forge-contrib/wt/`) age também, sem
`hooks_desligados`, e o PR fica em rascunho até o parecer: `gh pr create --draft` passa sem parecer e `gh pr ready`
exige o parecer, como o merge (o GitHub não mescla PR em rascunho).
Falha fechado nas ações críticas (ADR 0009, seção 7), também no clone do Forge.
"""
import json
import re
from pathlib import Path
from types import SimpleNamespace

from _comum import (INTEGRACAO, PLUGIN, bloquear, e_clone_do_forge, executar, forge_check, git, nome_da_branch,
                    leituras, raiz_de_estado, sem_atribuicoes, separar_regra)

PREFILTRO = re.compile(r"\bgh\b.*\bpr\b.*\b(create|merge|ready)\b|\bgh\b.*\bapi\b|\bgit\b.*\b(merge|pull)\b", re.S)
CRITICO = re.compile(r"\bpr\b.*\b(create|merge|ready)\b|\bapi\b|\b(merge|pull)\b", re.S)
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
BASES = ("develop", "origin/develop", "main", "origin/main", "master", "origin/master")


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
    i, pasta = 1, None
    while i < len(toks) and toks[i].startswith("-"):
        if toks[i] in GIT_COM_VALOR:
            pasta = toks[i + 1] if toks[i] == "-C" and i + 1 < len(toks) else pasta
            i += 2
        else:
            i += 1
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
    lidas = leituras(comando)
    if lidas.ilegivel:  # ADR 0013, tabela 2.4: passou no PREFILTRO (gh pr, gh api, merge, pull) e o hook não a lê
        bloquear("R-REVIEW", "linha com gh pr, gh api, merge ou pull que o hook não lê (aspas sem par ou # que ele "
                             "não prova ser comentário). Corrigir: feche as aspas, tire o comentário ou separe os comandos")
    for leitura in lidas.partes:  # a fiel e, se diferir, a da develop (I2)
        conferir(hook, [analisar(palavras) for palavras, _, _ in leitura])


def conferir(hook, partes):
    """Os comandos de uma leitura da linha, em ordem (`cd` e checkout/switch valem para os seguintes)."""
    pasta, branches = hook.cwd(), {}  # branches: raiz do projeto -> branch depois de checkout/switch na linha
    for parte in partes:
        if parte is None:
            continue
        if parte[0] == "cd":
            pasta = pasta / Path(parte[1]).expanduser() if parte[1] else Path.home()
        elif parte[0] == "pr":
            pull_request(hook, pasta, parte[2], parte[3], parte[4])
        elif parte[0] == "prready":
            pronto_de_pr(hook, pasta, parte[1], parte[2])
        elif parte[0] == "prmerge":
            merge_de_pr(hook, pasta, parte[1], parte[2])
        elif parte[0] == "api":
            merge_por_api(hook, pasta, parte[1])
        elif parte[0] == "branch":
            raiz = raiz_de_estado(pasta / parte[1] if parte[1] else pasta)
            if raiz:
                branches[raiz.resolve()] = parte[2]
        else:
            merge(hook, pasta / parte[1] if parte[1] else pasta, parte[2], branches)


if __name__ == "__main__":
    executar("parecer", principal, CRITICO, clone_do_forge=True)
