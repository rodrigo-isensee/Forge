"""G2.1 (pedido v0481, ADR 0019): a escrita do parecer de portão como comentário do PR e status do commit, pelo `gh` da sessão
(grátis; R-CUSTO), e a leitura do G2.2 (`ler`), que nada chama ainda: o `pr` passa a lê-la depois das mitigações cortadas do G2.1.
Erro, saída ilegível ou sem `gh`: `Recusa`, nada a mais se grava (falha fechada)."""
import hashlib
import json
import re
import subprocess

CONTEXTOS = {"review": "parecer-review", "qa": "parecer-qa", "revisao-seguranca": "parecer-seguranca",
             "revisao-devops": "parecer-devops"}  # lista fechada, sem barra (ADR 0019, seção 2; M2.1)
AGREGADO = "pareceres"
ESTADOS = {"aprovado": "success", "riscos-aceitos": "success", "reprovado": "failure"}
TETO_DA_DESCRICAO = 140  # limite do GitHub; acima, recusa (M7.1)
DESCRICAO_APROVADA = re.compile(r"^(aprovado|riscos-aceitos) · sha256 [0-9a-f]{64} · ")
REMOTO = re.compile(r"(?:(?:https?|ssh)://(?:[^@/]+@)?|[^@/:]+@)([^/:@]+)[:/]([^/]+)/([^/]+?)(?:\.git)?/?")  # M18.1
URL_DO_PR = re.compile(r"https://([^/]+)/([^/]+)/([^/]+)/pull/[0-9]+")
URL_DO_COMENTARIO = re.compile(r"https://([^/]+)/([^/]+)/([^/]+)/pull/([0-9]+)#issuecomment-([0-9]+)")  # M6.1
DESCRICAO = re.compile(r"(aprovado|riscos-aceitos|reprovado) · sha256 ([0-9a-f]{64}) · [0-9]+ bloqueantes · [0-9]+ recomendados")


class Recusa(Exception):
    pass


def normalizar(texto):
    """Fim de linha LF e sem espaço nas pontas, como o hook `autoria` mede e o GitHub devolve (M5.3)."""
    return texto.replace("\r\n", "\n").replace("\r", "\n").strip()


def descricao(veredito, texto, bloqueantes, recomendados):
    """`<veredito> · sha256 <64> · <n> bloqueantes · <n> recomendados` (ADR 0019, seção 2: sha256 inteiro); acima de 140, recusa."""
    d = (f"{veredito} · sha256 {hashlib.sha256(normalizar(texto).encode()).hexdigest()} · "
         f"{bloqueantes} bloqueantes · {recomendados} recomendados")
    if len(d) > TETO_DA_DESCRICAO:
        raise Recusa(f"descrição com {len(d)} caracteres, acima de {TETO_DA_DESCRICAO} (M7.1)")
    return d


def gh(raiz, args, corpo=None):
    """O JSON da saída de `gh <args>`, com `corpo` em JSON na entrada (`--input -`); falha, sem `gh` ou ilegível: Recusa."""
    try:
        r = subprocess.run(["gh", *args], cwd=raiz, capture_output=True, text=True, timeout=60,
                           input="" if corpo is None else json.dumps(corpo))
        if r.returncode:
            raise Recusa(f"gh {' '.join(args[:2])} saiu com {r.returncode}: {r.stderr.strip()[:200]}")
        return json.loads(r.stdout)
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        raise Recusa(f"gh {' '.join(args[:2])} sem resposta legível ({type(e).__name__})") from None


def repositorio_do_remoto(raiz):
    """(host, dono, repo) do `origin` da cópia, em minúsculas; sem `origin` ou URL fora das formas https e ssh: Recusa (M18.1)."""
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=raiz, capture_output=True, text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        url = ""  # sem `git` ou sem resposta; sem `origin`, a saída também vem vazia e não casa
    m = REMOTO.fullmatch(url.strip())
    if m is None:
        raise Recusa("o `origin` da cópia não é um repositório lido (https ou ssh); publicar pede o remoto do PR (M18.1)")
    return tuple(x.lower() for x in m.groups())


def pr_aberto(raiz, branch, sha):
    """O PR aberto da `branch` (nome exato) cujo head é `sha`, no repositório do `origin` da cópia e com a branch nele (M18.1:
    `GH_REPO` ou outro remoto não desviam o publicar); outro head, outro repositório, nenhum ou mais de um: Recusa."""
    prs = gh(raiz, ["pr", "list", "--head", branch, "--state", "open", "--json",
                    "number,headRefName,headRefOid,url,isCrossRepository"])
    prs = [p for p in prs if isinstance(p, dict) and p.get("headRefName") == branch] if isinstance(prs, list) else []
    if len(prs) != 1:
        raise Recusa(f"{len(prs)} PR aberto(s) da branch {branch}; publicar pede um só")
    if prs[0].get("headRefOid") != sha:
        raise Recusa(f"o commit {sha[:7]} não é o head do PR #{prs[0].get('number')} ({str(prs[0].get('headRefOid'))[:7]})")
    if prs[0].get("isCrossRepository") is not False:
        raise Recusa(f"o PR #{prs[0].get('number')} vem de outro repositório; publicar pede a branch no repositório do PR (M18.1)")
    m = URL_DO_PR.fullmatch(str(prs[0].get("url")))
    if not m or tuple(x.lower() for x in m.groups()) != repositorio_do_remoto(raiz):
        raise Recusa(f"o PR #{prs[0].get('number')} ({prs[0].get('url')}) não é do repositório do `origin` da cópia (M18.1)")
    return prs[0]


def gravar_status(raiz, sha, contexto, estado, texto, url=None):
    corpo = {"state": estado, "context": contexto, "description": texto} | ({"target_url": url} if url else {})
    return gh(raiz, ["api", "-X", "POST", f"repos/{{owner}}/{{repo}}/statuses/{sha}", "--input", "-"], corpo)


def agregado(raiz, sha, exigidos):
    """(estado, descrição): `success` só com o status mais novo de cada contexto exigido, da conta da sessão, em `success` e com a
    descrição do `publicar`; senão `pending` com o que falta (M13.1). Lê todas as páginas (M19.1)."""
    login = gh(raiz, ["api", "user"]).get("login")
    paginas = gh(raiz, ["api", "--paginate", "--slurp", f"repos/{{owner}}/{{repo}}/commits/{sha}/statuses"])
    if not login or not isinstance(paginas, list) or not all(isinstance(p, list) for p in paginas):
        raise Recusa("statuses ou conta da sessão ilegíveis")
    lista, faltam = [s for p in paginas for s in p if isinstance(s, dict)], []
    for tipo in exigidos:
        dela = [s for s in lista if s.get("context") == CONTEXTOS[tipo]
                and (s.get("creator") or {}).get("login") == login]  # filtro antes do mais novo (M1.2)
        if not dela or dela[0].get("state") != "success" or not DESCRICAO_APROVADA.match(dela[0].get("description") or ""):
            faltam.append(CONTEXTOS[tipo])
    return ("pending", f"faltam: {', '.join(faltam)}"[:TETO_DA_DESCRICAO]) if faltam else ("success", "todos os exigidos")


def frontmatter(texto):
    """Os campos `chave: valor` do bloco entre a primeira linha `---` e a seguinte; sem o bloco, {}."""
    linhas = normalizar(texto).split("\n")
    if linhas[0] != "---" or "---" not in linhas[1:]:
        return {}
    return dict(x.split(": ", 1) for x in linhas[1:linhas.index("---", 1)] if ": " in x)


def conferir(raiz, repo, pr, pedido, tipo, status, contas):
    """(veredito, url) do status cujo comentário está íntegro no PR do head; (None, motivo) se não vale. Nunca segue o
    `target_url`: só o id dele vai à API do repositório conferido (M6.1). Erro do `gh`: Recusa (M19.1)."""
    d = DESCRICAO.fullmatch(status.get("description") or "")
    u = URL_DO_COMENTARIO.fullmatch(status.get("target_url") or "")
    if not d or ESTADOS[d[1]] != status.get("state"):
        return None, "descrição fora da forma do publicar ou veredito diferente do estado (M7.1, M8.1)"
    if not u or tuple(x.lower() for x in u.groups()[:3]) != repo or int(u[4]) != pr["number"]:
        return None, "target_url fora de um comentário do PR do head (M6.1)"
    c = gh(raiz, ["api", "--hostname", repo[0], f"repos/{repo[1]}/{repo[2]}/issues/comments/{u[5]}"])
    if not isinstance(c, dict) or c.get("html_url") != u[0] or (c.get("user") or {}).get("login") not in contas:
        return None, "comentário de outro PR ou de conta fora da lista (M5.2, M6.1)"
    if hashlib.sha256(normalizar(str(c.get("body"))).encode()).hexdigest() != d[2]:
        return None, "comentário editado depois do status (M5.1)"
    f = frontmatter(str(c.get("body")))
    if (f.get("commit"), f.get("branch"), f.get("pedido"), f.get("tipo"), f.get("parecer")) != (
            pr["headRefOid"], pr["headRefName"], pedido, tipo, d[1]):
        return None, "commit, branch, pedido, tipo ou veredito do texto diferente do status (M8.1)"
    return d[1], u[0]


def ler(raiz, branch, sha, pedido, contas):
    """G2.2, a leitura (ADR 0019, seção 3): {tipo: (veredito, url) ou (None, motivo)} do status mais novo de cada contexto da
    lista, entre os das `contas` (o filtro vem antes do mais novo; M1.1, M1.2, M2.1), no `sha` head do PR aberto da `branch`.
    Contexto sem status das contas fica de fora. Todas as páginas; resposta ilegível ou fora do contrato: Recusa (M19.1)."""
    if not isinstance(contas, (set, frozenset)) or not all(isinstance(x, str) and x for x in contas):
        raise Recusa("contas fora de um conjunto de logins não vazios; o filtro é igualdade exata (M1.1)")
    repo, pr = repositorio_do_remoto(raiz), pr_aberto(raiz, branch, sha)
    paginas = gh(raiz, ["api", "--hostname", repo[0], "--paginate", "--slurp", f"repos/{repo[1]}/{repo[2]}/commits/{sha}/statuses"])
    if not isinstance(paginas, list) or not all(isinstance(p, list) for p in paginas):
        raise Recusa("statuses ilegíveis (M19.1)")
    lista, lidos = [s for p in paginas for s in p if isinstance(s, dict)], {}
    try:
        for tipo, contexto in CONTEXTOS.items():
            dela = [s for s in lista if s.get("context") == contexto and (s.get("creator") or {}).get("login") in contas]
            if dela:
                lidos[tipo] = conferir(raiz, repo, pr, pedido, tipo, dela[0], contas)
    except (KeyError, TypeError, AttributeError, ValueError) as e:  # como o `publicar`
        raise Recusa(f"resposta do gh fora do contrato ({type(e).__name__}) (M19.1)") from None
    return lidos


def publicar(raiz, tipo, veredito, texto, sha, branch, bloqueantes, recomendados, exigidos):
    """Comentário no PR, releitura do corpo, o agregado em `pending`, o status do contexto do papel e o agregado recalculado:
    falha em qualquer passo nunca deixa um `success` velho no agregado. Recusa depois do PR diz o que já ficou gravado.
    Devolve (url do comentário, agregado)."""
    if tipo not in CONTEXTOS or veredito not in ESTADOS or not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        raise Recusa(f"tipo `{tipo}`, veredito `{veredito}` ou commit fora da lista")
    desc = descricao(veredito, texto, bloqueantes, recomendados)  # antes de gravar qualquer coisa
    pr, gravado = pr_aberto(raiz, branch, sha), "nada"
    try:
        criado = gh(raiz, ["api", "-X", "POST", f"repos/{{owner}}/{{repo}}/issues/{pr['number']}/comments", "--input", "-"],
                    {"body": texto})
        gravado = f"o comentário no PR #{pr['number']}"
        lido = gh(raiz, ["api", f"repos/{{owner}}/{{repo}}/issues/comments/{int(criado['id'])}"])
        if normalizar(str(lido.get("body"))) != normalizar(texto):
            raise Recusa("o corpo devolvido pela API difere do arquivo local; status não gravado (M5.3)")
        if (url := lido.get("html_url")) != f"{pr['url']}#issuecomment-{int(criado['id'])}":
            raise Recusa(f"o comentário não é do PR #{pr['number']}: {url}")
        gravar_status(raiz, sha, AGREGADO, "pending", f"recalculando depois de {CONTEXTOS[tipo]}")  # QA A1 do #878
        gravado += f", {AGREGADO} pending"
        gravar_status(raiz, sha, CONTEXTOS[tipo], ESTADOS[veredito], desc, url)
        gravado += f", {CONTEXTOS[tipo]} {ESTADOS[veredito]}"
        estado = agregado(raiz, sha, exigidos)
        gravar_status(raiz, sha, AGREGADO, *estado)
    except (Recusa, KeyError, TypeError, AttributeError, ValueError) as e:
        raise Recusa(f"{e}; já gravado: {gravado}") from None
    return url, estado
