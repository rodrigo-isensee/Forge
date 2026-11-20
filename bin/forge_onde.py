"""Forge: `forge-check onde <alvo>` (AE1.1, v0478 E58.1): onde está uma versão, um PR, um commit, uma branch ou um cartão, lido
do git e do GitHub, para colar a prova antes de afirmar estado. Só leitura, sem `git fetch`; só biblioteca padrão.

Alvo: `vX.Y.Z` (tag), `#N` ou `pr:N` (PR, pelo `gh pr view`), sha de 7 a 40 hex (commit), `branch:<nome>` ou nome com `/`
(branch: local ou `origin/`, à frente e atrás da develop e o PR pelo `gh pr list --head`), ID em maiúsculas (cartão: o commit
mais novo de cada base que o cita). A presença em `develop`, `homolog` e `main` é `git merge-base --is-ancestor` contra
`origin/<base>`, com o sha lido de cada uma (o clone pode estar atrás: a linha mostra de onde leu).
Saída: linhas `onde: ...` sem caractere de controle. rc 0 lido; 1 alvo não existe; 2 alvo inválido ou leitura que falhou
(`nao-verificavel`, nunca `sim`: o `gh` lento sai pelo teto do `gh_json` do forge-check; o `git` lento, pelo `executar`).
"""
import re
import subprocess

BASES = ("develop", "homolog", "main")
VERSAO = re.compile(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?")
PR = re.compile(r"(?:#|pr:#?)(\d{1,7})")
SHA = re.compile(r"[0-9a-f]{7,40}")
CARTAO = re.compile(r"[A-Z][A-Z0-9]*(?:[-.][A-Z0-9]+)*")
BRANCH = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]{0,199}")
LIDO, NAO_EXISTE, NAO_VERIFICAVEL = 0, 1, 2


def tipo_do_alvo(alvo):
    """(tipo, valor) ou (None, None) se o alvo não é de nenhum formato: nada que comece com `-` nem tenha `..` chega ao git."""
    if alvo.startswith("branch:"):
        nome = alvo[len("branch:"):]
        ok = BRANCH.fullmatch(nome) and ".." not in nome and "//" not in nome and not nome.endswith(("/", ".lock"))
        return ("branch", nome) if ok else (None, None)
    for tipo, forma in (("versao", VERSAO), ("pr", PR), ("commit", SHA), ("cartao", CARTAO)):
        achado = forma.fullmatch(alvo)
        if achado:
            return tipo, achado.group(achado.lastindex or 0)
    return tipo_do_alvo("branch:" + alvo) if "/" in alvo else (None, None)


def sha_de(ctx, raiz, ref):
    """O sha40 do commit de `ref` ou None (ausente ou ambíguo)."""
    cod, saida = ctx["git"](raiz, "rev-parse", "--verify", "--quiet", "--end-of-options", ref + "^{commit}")
    return saida if cod == 0 and SHA.fullmatch(saida) else None


def presenca(ctx, raiz, sha):
    """Uma linha por base: `sim`, `nao`, `sem-branch` ou `nao-verificavel`; e o rc (2 se alguma falhou ou nenhuma base existe)."""
    linhas, rc, achadas = [], LIDO, 0
    for base in BASES:
        ref = sha_de(ctx, raiz, f"refs/remotes/origin/{base}")
        if ref is None:
            linhas.append(f"onde: {base} sem-branch (sem origin/{base} no clone)")
            continue
        achadas += 1
        cod, _ = ctx["git"](raiz, "merge-base", "--is-ancestor", sha, ref)
        estado = {0: "sim", 1: "nao"}.get(cod, "nao-verificavel")
        if estado == "nao-verificavel":
            rc = NAO_VERIFICAVEL
        linhas.append(f"onde: {base} {estado} (origin/{base} @{ref[:12]})")
    return linhas, (rc if achadas else NAO_VERIFICAVEL)


def onde_do_pr(ctx, raiz, numero):
    dados, erro = ctx["gh_json"](raiz, "pr", "view", numero, "--json", "number,state,baseRefName,headRefName,mergedAt,mergedBy,mergeCommit")
    if not isinstance(dados, dict) or str(dados.get("number")) != numero:
        return [f"onde: pr #{numero} nao-verificavel ({erro.strip()[:200] or 'resposta sem o PR'})"], NAO_VERIFICAVEL
    por = (dados.get("mergedBy") or {}).get("login") or "-"
    linhas = [f"onde: pr #{numero} estado={dados.get('state')} base={dados.get('baseRefName')} head={dados.get('headRefName')} "
              f"mesclado={dados.get('mergedAt') or '-'} por={por}"]
    if dados.get("state") != "MERGED":
        return linhas, LIDO
    oid = str((dados.get("mergeCommit") or {}).get("oid") or "")
    sha = sha_de(ctx, raiz, oid) if SHA.fullmatch(oid) else None
    if sha is None:
        return linhas + [f"onde: commit {oid[:12] or '-'} nao-verificavel (ausente no clone; rode git fetch)"], NAO_VERIFICAVEL
    mais, rc = presenca(ctx, raiz, sha)
    return linhas + [f"onde: commit {sha[:12]}"] + mais, rc


def onde_da_branch(ctx, raiz, nome):
    origem, sha = f"origin/{nome}", sha_de(ctx, raiz, f"refs/remotes/origin/{nome}")
    if sha is None:
        origem, sha = nome, sha_de(ctx, raiz, f"refs/heads/{nome}")
    if sha is None:
        return [f"onde: branch {nome} nao-existe (nem origin/{nome} nem local)"], NAO_EXISTE
    linhas, rc = presenca(ctx, raiz, sha)
    linhas.insert(0, f"onde: branch {origem} @{sha[:12]}")
    cod, contas = ctx["git"](raiz, "rev-list", "--left-right", "--count", f"{sha}...refs/remotes/origin/develop")
    frente_atras = contas.split() if cod == 0 else []
    if len(frente_atras) == 2:
        linhas.append(f"onde: develop frente={frente_atras[0]} atras={frente_atras[1]}")
    prs, erro = ctx["gh_json"](raiz, "pr", "list", "--head", nome, "--state", "all", "--limit", "20",
                               "--json", "number,state,baseRefName,headRefName,mergedAt")
    if not isinstance(prs, list):
        return linhas + [f"onde: pr nao-verificavel ({erro.strip()[:200] or 'resposta ilegível'})"], NAO_VERIFICAVEL
    exatos = [p for p in prs if isinstance(p, dict) and p.get("headRefName") == nome]
    linhas += [f"onde: pr #{p.get('number')} estado={p.get('state')} base={p.get('baseRefName')} mesclado={p.get('mergedAt') or '-'}"
               for p in exatos] or ["onde: pr nenhum"]
    return linhas, rc


def onde_do_cartao(ctx, raiz, cartao):
    """O commit mais novo de cada base cuja mensagem cita o ID inteiro (`AE1` não casa `AE10` nem `AE1.1`)."""
    inteiro = re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(cartao)}(?![A-Za-z0-9_-]|\.[A-Za-z0-9])")
    linhas, rc, achou, lidas = [], LIDO, False, 0
    for base in BASES:
        ref = sha_de(ctx, raiz, f"refs/remotes/origin/{base}")
        if ref is None:
            linhas.append(f"onde: {base} sem-branch (sem origin/{base} no clone)")
            continue
        lidas += 1
        cod, saida = ctx["git"](raiz, "log", "--fixed-strings", f"--grep={cartao}", "--max-count=200", "--format=%H%x1f%B%x1e", ref)
        if cod != 0:
            linhas.append(f"onde: {base} nao-verificavel (git log falhou)")
            rc = NAO_VERIFICAVEL
            continue
        shas = [c.split("\x1f", 1)[0].strip() for c in saida.split("\x1e") if "\x1f" in c and inteiro.search(c.split("\x1f", 1)[1])]
        achou = achou or bool(shas)
        linhas.append(f"onde: {base} sim (commit {shas[0][:12]})" if shas else f"onde: {base} nao (nenhum commit cita {cartao})")
    if not lidas:
        rc = NAO_VERIFICAVEL
    return linhas, rc if achou or rc else NAO_EXISTE


def onde(alvo, raiz, ctx):
    """(rc, linhas) para `alvo`; ctx traz `git`, `gh_json` e `seguro` do forge-check."""
    tipo, valor = tipo_do_alvo(alvo)
    if tipo is None:
        return NAO_VERIFICAVEL, ["onde: alvo inválido (use vX.Y.Z, #N, pr:N, sha, branch:<nome> ou ID de cartão)"]
    if tipo == "pr":
        linhas, rc = onde_do_pr(ctx, raiz, valor)
    elif tipo == "branch":
        linhas, rc = onde_da_branch(ctx, raiz, valor)
    elif tipo == "cartao":
        linhas, rc = onde_do_cartao(ctx, raiz, valor)
    else:
        sha = sha_de(ctx, raiz, f"refs/tags/{valor}" if tipo == "versao" else valor)
        if sha is None:
            return NAO_EXISTE, [f"onde: {tipo} {valor} nao-existe (ausente ou ambíguo no clone)"]
        if tipo == "commit" and not sha.startswith(valor):  # o git prefere a tag ou branch de nome hexadecimal ao objeto
            return NAO_VERIFICAVEL, [f"onde: commit {valor} nao-verificavel (sha ambíguo com ref: leu {sha[:12]})"]
        linhas, rc = presenca(ctx, raiz, sha)
        linhas.insert(0, f"onde: {tipo} {valor} @{sha[:12]}")
    return rc, [ctx["seguro"](linha) for linha in linhas]


def executar(a, raiz, ctx):
    try:
        rc, linhas = onde(a.alvo, raiz, ctx)
    except subprocess.TimeoutExpired:  # leitura que falhou é rc 2; o rc 1 do forge-check diria "alvo não existe"
        print("onde: nao-verificavel (git sem resposta)")
        return NAO_VERIFICAVEL
    print("\n".join(linhas))
    return rc
