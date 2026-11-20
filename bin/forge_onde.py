"""Forge: `forge-check onde <alvo>` (AE1.1, v0478 E58.1): onde está uma versão, um PR, um commit, uma branch ou um cartão, lido
do git e do GitHub, para colar a prova antes de afirmar estado. Só leitura, sem `git fetch`; só biblioteca padrão.

Alvo: `vX.Y.Z` (tag), `#N` ou `pr:N` (PR, pelo `gh pr view`), sha de 7 a 40 hex (commit), `branch:<nome>` ou nome com `/`
(branch: local ou `origin/`, à frente e atrás da develop e o PR pelo `gh pr list --head`), ID em maiúsculas (cartão: o commit
mais novo de cada base que o cita). A presença em `develop`, `homolog` e `main` é `git merge-base --is-ancestor` contra
`origin/<base>`, com o sha lido de cada uma (o clone pode estar atrás: a linha mostra de onde leu).
Saída: linhas `onde: ...` sem caractere de controle. rc 0 lido; 1 alvo não existe; 2 alvo inválido ou leitura que falhou
(`nao-verificavel`, nunca `sim`: o `gh` lento sai pelo teto do `gh_json` do forge-check; o `git` lento, pelo `executar`).
AE1.2 (E58.19): `prova_do_movimento` confere a `--prova` do `forge-check movimento` para Pronto ou Fechado* com estas leituras;
`pr:` e `commit:` só no clone cujo origin é https ou ssh, com o gh preso a esse repositório (`--repo`), e `rodar:` só com o run.json
do mesmo cartão e da mesma raiz (E58.29).
"""
import json
import re
import subprocess
from pathlib import Path

BASES = ("develop", "homolog", "main")
VERSAO = re.compile(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?")
PR = re.compile(r"(?:#|pr:#?)(\d{1,7})")
SHA = re.compile(r"[0-9a-f]{7,40}")
CARTAO = re.compile(r"[A-Z][A-Z0-9]*(?:[-.][A-Z0-9]+)*")
BRANCH = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]{0,199}")
ORIGEM = re.compile(r"(?:https://(?:[^@/\s]+@)?|ssh://git@|git@)([A-Za-z0-9.-]+)[/:]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?")
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


def onde_do_pr(ctx, raiz, numero, repo=()):
    dados, erro = ctx["gh_json"](raiz, "pr", "view", numero, "--json", "number,state,baseRefName,headRefName,mergedAt,mergedBy,mergeCommit",
                                 *repo)
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


def citacao(cartao):
    """O ID inteiro no texto (`AE1` não casa `AE10` nem `AE1.1`)."""
    return re.compile(rf"(?<![A-Za-z0-9_.-]){re.escape(cartao)}(?![A-Za-z0-9_-]|\.[A-Za-z0-9])")


def onde_do_cartao(ctx, raiz, cartao):
    """O commit mais novo de cada base cuja mensagem cita o ID inteiro."""
    inteiro = citacao(cartao)
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


def onde(alvo, raiz, ctx, repo=()):
    """(rc, linhas) para `alvo`; ctx traz `git`, `gh_json` e `seguro` do forge-check; `repo` (`--repo X`) prende o gh do PR."""
    tipo, valor = tipo_do_alvo(alvo)
    if tipo is None:
        return NAO_VERIFICAVEL, ["onde: alvo inválido (use vX.Y.Z, #N, pr:N, sha, branch:<nome> ou ID de cartão)"]
    if tipo == "pr":
        linhas, rc = onde_do_pr(ctx, raiz, valor, repo)
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


def origem(ctx, raiz):
    """`host/dono/repo` do origin do clone (https ou ssh); None sem origin, com caminho local ou `file://` (segurança A2 do AE1.2)."""
    cod, url = ctx["git"](raiz, "remote", "get-url", "origin")
    achado = ORIGEM.fullmatch(url) if cod == 0 else None
    return "/".join(achado.groups()) if achado else None


def prova_git(ctx, raiz, cartao, tipo, ref):
    """`pr:#N` mesclado na develop ou `commit:<sha>` ancestral da develop, e o PR ou o commit cita o cartão; lidos no clone de origin
    https ou ssh, com o gh no mesmo repositório (`--repo`), e a linha leva a origem."""
    alvo = f"pr:{ref}" if tipo == "pr" else ref
    if tipo_do_alvo(alvo)[0] != tipo:
        return "recusa", f"{tipo}:{ref} fora da forma"
    repo = origem(ctx, raiz)
    if repo is None:
        return "recusa", f"{tipo}:{ref} lido em clone sem origin https ou ssh (caminho local ou file:// não prova)"
    rc, linhas = onde(alvo, raiz, ctx, ("--repo", repo))
    if rc == NAO_VERIFICAVEL:
        return "nao-verificavel", next((l for l in linhas if "nao-verificavel" in l), linhas[-1])
    na_develop = next((l for l in linhas if l.startswith("onde: develop sim")), None)
    if rc != LIDO or na_develop is None or (tipo == "pr" and " estado=MERGED base=develop " not in linhas[0]):
        return "recusa", f"{tipo}:{ref} não está na develop ({linhas[0]})"
    sha = next(l.split()[-1].lstrip("@") for l in linhas if l.startswith("onde: commit "))
    if tipo == "pr":
        dados, erro = ctx["gh_json"](raiz, "pr", "view", tipo_do_alvo(alvo)[1], "--json", "number,title,body", "--repo", repo)
        if not isinstance(dados, dict) or str(dados.get("number")) != tipo_do_alvo(alvo)[1]:
            return "nao-verificavel", f"pr {ref} sem título lido ({erro.strip()[:200]})"
        texto = f"{dados.get('title') or ''}\n{dados.get('body') or ''}"
    else:
        cod, texto = ctx["git"](raiz, "log", "-1", "--format=%B", sha)
        texto = texto if cod == 0 else ""
    if not citacao(cartao).search(texto):
        return "recusa", f"{tipo}:{ref} não cita o cartão {cartao}"
    return "ok", f"{tipo}:{ref} {sha} origem={repo} ({na_develop})"


def prova_do_movimento(prova, cartao, raiz, ctx):
    """(estado, texto) da `--prova <tipo>:<ref>`: `ok` com o texto conferido para a linha, `recusa` (nada gravado) ou
    `nao-verificavel` (o cartão fica em Aguardando sua validação). `ruleset:` espera o leitor do AE8."""
    tipo, _, ref = prova.partition(":")
    try:
        if tipo in ("pr", "commit"):
            return prova_git(ctx, raiz, cartao, tipo, ref)
    except subprocess.TimeoutExpired:
        return "nao-verificavel", "git sem resposta"
    if tipo == "rodar":
        lida = Path(raiz).resolve()
        arq = lida / ".forge" / "run" / ref / "run.json"
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,60}", ref) or not arq.is_file() or arq.resolve() != arq:
            return "recusa", f"rodar:{ref} sem run.json nesta raiz (ou link simbólico)"
        try:
            dados = json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return "recusa", f"rodar:{ref} run.json ilegível"
        if not isinstance(dados, dict):
            return "recusa", f"rodar:{ref} run.json fora da forma"
        if dados.get("cartao") != cartao:  # E58.29 (segurança A1): o run é do cartão (`forge-check rodar <slug> --cartao <ID>`)
            return "recusa", f"rodar:{ref} não é do cartão {cartao} (grave com forge-check rodar --cartao {cartao} <slug> -- ...)"
        if dados.get("raiz") != str(lida):  # e desta raiz: o slug de outro clone não prova
            return "recusa", f"rodar:{ref} gravado em outra raiz, não em {lida}"
        rc = dados.get("rc")
        return ("ok", f"rodar:{ref} rc=0 head={str(dados.get('head'))[:40]} raiz={lida}") if rc == 0 else ("recusa", f"rodar:{ref} rc={rc}")
    if tipo == "juntado":
        coluna = ctx["coluna"](ref) if CARTAO.fullmatch(ref) and ref.casefold() != cartao.casefold() else None
        if coluna is None or ctx["final"](coluna):
            return "recusa", f"juntado:{ref} não é outro cartão ativo no histórico"
        return "ok", f"juntado:{ref} (em {coluna}, no quadro desde {ctx['desde'](ref)})"  # segurança A3: o destino e a entrada dele, para a auditoria
    return "recusa", f"tipo {tipo or '-'} sem leitor (use pr:#N, commit:<sha>, rodar:<slug> ou juntado:<ID>)"


def executar(a, raiz, ctx):
    try:
        rc, linhas = onde(a.alvo, raiz, ctx)
    except subprocess.TimeoutExpired:  # leitura que falhou é rc 2; o rc 1 do forge-check diria "alvo não existe"
        print("onde: nao-verificavel (git sem resposta)")
        return NAO_VERIFICAVEL
    print("\n".join(linhas))
    return rc
