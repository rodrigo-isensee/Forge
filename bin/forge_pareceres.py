"""G2.1 (pedido v0481, ADR 0019): só a escrita do parecer de portão como comentário do PR e status do commit, pelo `gh` da sessão
(grátis; R-CUSTO); a leitura que decide é o G2.2. Erro, saída ilegível ou sem `gh`: `Recusa`, nada a mais se grava (falha fechada)."""
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


def pr_aberto(raiz, branch, sha):
    """O PR aberto da `branch` (nome exato) cujo head é `sha`; outro head, nenhum ou mais de um: Recusa."""
    prs = gh(raiz, ["pr", "list", "--head", branch, "--state", "open", "--json", "number,headRefName,headRefOid,url"])
    prs = [p for p in prs if isinstance(p, dict) and p.get("headRefName") == branch] if isinstance(prs, list) else []
    if len(prs) != 1:
        raise Recusa(f"{len(prs)} PR aberto(s) da branch {branch}; publicar pede um só")
    if prs[0].get("headRefOid") != sha:
        raise Recusa(f"o commit {sha[:7]} não é o head do PR #{prs[0].get('number')} ({str(prs[0].get('headRefOid'))[:7]})")
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
