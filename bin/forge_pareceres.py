"""G2.1 (pedido v0481, ADR 0019): a escrita do parecer de portão como comentário do PR e status do commit, pelo `gh` da sessão
(grátis; R-CUSTO), a leitura do G2.2 (`ler`, no head) e a do C2a (`vigentes`, nos commits do PR), que nada chama ainda (o C2b
liga). A conta aceita é a dona do `origin` (M1.4), e cada publicação fica registrada na pasta de controle da máquina (M4.1). Erro, saída ilegível ou sem `gh`:
`Recusa`, nada a mais se grava (falha fechada)."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

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
REGISTRO = "pareceres-publicados.jsonl"  # M4.1, na pasta de controle


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


def login(objeto):
    """O `login` em minúsculas do `creator` ou do `user` da API (o GitHub não distingue caixa); sem login de texto: None. Objeto
    que não é dict: AttributeError, que a leitura trata como resposta fora do contrato."""
    nome = (objeto or {}).get("login")
    return nome.lower() if isinstance(nome, str) else None


def contas_aceitas(raiz):
    """M1.4: a conta aceita é a dona do repositório do `origin` (o do PR, M18.1), nunca a de `gh api user`: outro `GH_TOKEN` no
    ambiente não vira aprovador."""
    return frozenset({repositorio_do_remoto(raiz)[1]})


def e_o_forge(pasta):
    """Cópia do Forge: o manifesto dele e nenhum `.forge/versao` (como `e_o_forge` do `forge-check`)."""
    try:
        manifesto = json.loads((pasta / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(manifesto, dict) and manifesto.get("name") == "forge" and not (pasta / ".forge" / "versao").exists()


def pasta_de_controle(raiz):
    """M4.1: a pasta de controle da máquina, uma só para todos os clones: no Forge, `~/.forge-contrib/.forge/run/`; no projeto, o
    `.forge/run/` da cópia que contém `.forge/wt/` (ou o da própria cópia principal). Nunca o `.forge/run/` de um clone. `.forge`
    ou `run` por link, ou a pasta ausente: Recusa."""
    real, contrib = Path(os.path.realpath(raiz)), Path.home() / ".forge-contrib"
    wt = [i for i in range(len(real.parts) - 1) if real.parts[i:i + 2] == (".forge", "wt")]
    if real.is_relative_to(os.path.realpath(contrib)) or e_o_forge(real):
        base = contrib
    else:
        base = Path(*real.parts[:wt[0]]) if wt else real
    run = base / ".forge" / "run"
    if (base / ".forge").is_symlink() or run.is_symlink() or not run.is_dir():
        raise Recusa(f"pasta de controle {run} ausente ou por link; o registro de publicação mora nela (M4.1)")
    return run


def publicados(raiz):
    """{(sha, contexto, sha256, id do comentário)} do registro da pasta de controle; sem o arquivo, vazio; linha ilegível fica de
    fora; o registro por link: Recusa (M4.1)."""
    try:
        with open(os.open(pasta_de_controle(raiz) / REGISTRO, os.O_RDONLY | os.O_NOFOLLOW), encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except FileNotFoundError:
        return set()
    except OSError as e:
        raise Recusa(f"registro de publicação ilegível ou por link ({type(e).__name__}) (M4.1)") from None
    lidos = set()
    for linha in linhas:
        try:
            r = json.loads(linha)
            lidos.add((r["sha"], r["contexto"], r["sha256"], r["comentario"]))
        except (ValueError, KeyError, TypeError):
            continue
    return lidos


def registrar(pasta, sha, contexto, sha256, comentario):
    """Acrescenta a publicação ao registro da pasta de controle, sem seguir link; falha: Recusa (M4.1)."""
    linha = json.dumps({"sha": sha, "contexto": contexto, "sha256": sha256, "comentario": comentario}) + "\n"
    try:
        with open(os.open(pasta / REGISTRO, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o644), "a",
                  encoding="utf-8") as f:
            f.write(linha)
    except OSError as e:
        raise Recusa(f"registro de publicação não gravado ({type(e).__name__}) (M4.1)") from None


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
    """(estado, descrição): `success` só com o status mais novo de cada contexto exigido, da conta aceita (M1.4), em `success` e
    com a descrição do `publicar`; senão `pending` com o que falta (M13.1). Lê todas as páginas (M19.1)."""
    contas = contas_aceitas(raiz)
    paginas = gh(raiz, ["api", "--paginate", "--slurp", f"repos/{{owner}}/{{repo}}/commits/{sha}/statuses"])
    if not isinstance(paginas, list) or not all(isinstance(p, list) for p in paginas):
        raise Recusa("statuses ilegíveis")
    lista, faltam = [s for p in paginas for s in p if isinstance(s, dict)], []
    for tipo in exigidos:
        dela = [s for s in lista if s.get("context") == CONTEXTOS[tipo]
                and login(s.get("creator")) in contas]  # filtro antes do mais novo (M1.2)
        if not dela or dela[0].get("state") != "success" or not DESCRICAO_APROVADA.match(dela[0].get("description") or ""):
            faltam.append(CONTEXTOS[tipo])
    return ("pending", f"faltam: {', '.join(faltam)}"[:TETO_DA_DESCRICAO]) if faltam else ("success", "todos os exigidos")


def frontmatter(texto):
    """Os campos `chave: valor` do bloco entre a primeira linha `---` e a seguinte; sem o bloco, {}."""
    linhas = normalizar(texto).split("\n")
    if linhas[0] != "---" or "---" not in linhas[1:]:
        return {}
    return dict(x.split(": ", 1) for x in linhas[1:linhas.index("---", 1)] if ": " in x)


def conferir(raiz, repo, pr, pedido, tipo, status, contas, registro):
    """(veredito, url) do status registrado pelo `publicar` (M4.1) cujo comentário está íntegro no PR do head; (None, motivo) se
    não vale. Nunca segue o `target_url`: só o id dele vai à API do repositório conferido (M6.1). Erro do `gh`: Recusa (M19.1)."""
    d = DESCRICAO.fullmatch(status.get("description") or "")
    u = URL_DO_COMENTARIO.fullmatch(status.get("target_url") or "")
    if not d or ESTADOS[d[1]] != status.get("state"):
        return None, "descrição fora da forma do publicar ou veredito diferente do estado (M7.1, M8.1)"
    if not u or tuple(x.lower() for x in u.groups()[:3]) != repo or int(u[4]) != pr["number"]:
        return None, "target_url fora de um comentário do PR do head (M6.1)"
    if (pr["headRefOid"], CONTEXTOS[tipo], d[2], int(u[5])) not in registro:
        return None, "status sem registro do `publicar` na pasta de controle (M4.1)"
    c = gh(raiz, ["api", "--hostname", repo[0], f"repos/{repo[1]}/{repo[2]}/issues/comments/{u[5]}"])
    if not isinstance(c, dict) or c.get("html_url") != u[0] or login(c.get("user")) not in contas:
        return None, "comentário de outro PR ou de conta fora da lista (M5.2, M6.1)"
    if hashlib.sha256(normalizar(str(c.get("body"))).encode()).hexdigest() != d[2]:
        return None, "comentário editado depois do status (M5.1)"
    f = frontmatter(str(c.get("body")))
    if (f.get("commit"), f.get("branch"), f.get("pedido"), f.get("tipo"), f.get("parecer")) != (
            pr["headRefOid"], pr["headRefName"], pedido, tipo, d[1]):
        return None, "commit, branch, pedido, tipo ou veredito do texto diferente do status (M8.1)"
    return d[1], u[0]


def ler(raiz, branch, sha, pedido):
    """G2.2, a leitura (ADR 0019, seção 3): {tipo: (veredito, url) ou (None, motivo)} do status mais novo de cada contexto da
    lista, entre os da conta aceita (o filtro vem antes do mais novo; M1.1, M1.2, M1.4, M2.1), no `sha` head do PR aberto da
    `branch`, só com o registro do `publicar` (M4.1). Contexto sem status da conta fica de fora. Todas as páginas; resposta
    ilegível ou fora do contrato: Recusa (M19.1)."""
    contas, registro = contas_aceitas(raiz), publicados(raiz)
    repo, pr = repositorio_do_remoto(raiz), pr_aberto(raiz, branch, sha)
    paginas = gh(raiz, ["api", "--hostname", repo[0], "--paginate", "--slurp", f"repos/{repo[1]}/{repo[2]}/commits/{sha}/statuses"])
    if not isinstance(paginas, list) or not all(isinstance(p, list) for p in paginas):
        raise Recusa("statuses ilegíveis (M19.1)")
    lista, lidos = [s for p in paginas for s in p if isinstance(s, dict)], {}
    try:
        for tipo, contexto in CONTEXTOS.items():
            dela = [s for s in lista if s.get("context") == contexto and login(s.get("creator")) in contas]
            if dela:
                lidos[tipo] = conferir(raiz, repo, pr, pedido, tipo, dela[0], contas, registro)
    except (KeyError, TypeError, AttributeError, ValueError) as e:  # como o `publicar`
        raise Recusa(f"resposta do gh fora do contrato ({type(e).__name__}) (M19.1)") from None
    return lidos


def statuses_de(raiz, repo, sha):
    """Os statuses do `sha`, todas as páginas, o mais novo primeiro; resposta ilegível: Recusa (M19.1)."""
    paginas = gh(raiz, ["api", "--hostname", repo[0], "--paginate", "--slurp", f"repos/{repo[1]}/{repo[2]}/commits/{sha}/statuses"])
    if not isinstance(paginas, list) or not all(isinstance(p, list) for p in paginas):
        raise Recusa(f"statuses de {sha[:7]} ilegíveis (M19.1)")
    return [s for p in paginas for s in p if isinstance(s, dict)]


def quando(status):
    """(created_at, id) do status: a ordem entre os commits do PR; sem os dois, fora do contrato."""
    if not isinstance(status["created_at"], str) or type(status["id"]) is not int:
        raise TypeError("status sem created_at ou id")
    return status["created_at"], status["id"]


def ancestral(raiz, origem, head):
    """`origem` é ancestral de `head` na cópia (C0-2); commit ausente ou `git` sem resposta: Recusa."""
    try:
        rc = subprocess.run(["git", "merge-base", "--is-ancestor", origem, head], cwd=raiz, capture_output=True,
                            timeout=30).returncode
    except (OSError, subprocess.TimeoutExpired):
        rc = 128
    if rc not in (0, 1):
        raise Recusa(f"o commit {origem[:7]} ou {head[:7]} não está na cópia; a origem não se confere (C0-2)")
    return rc == 0


def tem_status(registrada, statuses):
    """A linha (sha, contexto, sha256, comentário) do registro tem o status do `publicar` entre os `statuses` do commit dela."""
    _, contexto, sha256, comentario = registrada
    for s in statuses:
        d = DESCRICAO.fullmatch(s.get("description") or "")
        u = URL_DO_COMENTARIO.fullmatch(s.get("target_url") or "")
        if s.get("context") == contexto and d and d[2] == sha256 and u and int(u[5]) == comentario:
            return True
    return False


def vigentes(raiz, pr, head, pedido):
    """C2a (herança na leitura, ADR 0019 emendada): {tipo: (veredito, url, origem) ou (None, motivo, origem)} do status mais
    novo de cada contexto, das contas aceitas, entre os commits do PR aberto `pr` cujo head é `head`. C0-1: o índice é o status;
    o `failure` mais novo barra; comentário sumido ou que não confere não volta a um anterior. C0-2: a origem é ancestral do
    head e está entre os commits do PR; o domínio da origem ao head fica com quem lê (C2b). Linha do registro (M4.1) de um
    commit do PR sem o status correspondente: Recusa (CONTROLE-RUN-GRAFIA). Erro ou resposta fora do contrato: Recusa."""
    contas, registro, repo = contas_aceitas(raiz), publicados(raiz), repositorio_do_remoto(raiz)
    p = gh(raiz, ["pr", "view", str(int(pr)), "--json", "number,headRefName,url,commits"])
    try:
        aberto = pr_aberto(raiz, p["headRefName"], head)
        if (aberto["number"], aberto["url"]) != (p["number"], p["url"]):
            raise Recusa(f"o PR #{pr} não é o PR aberto da branch {p['headRefName']} com o head {head[:7]}")
        commits = [c["oid"] for c in p["commits"]]
        if not all(re.fullmatch(r"[0-9a-f]{40}", c) for c in commits) or head not in commits:
            raise ValueError("commits do PR fora da forma ou sem o head")
        do_pr = {c: [s for s in statuses_de(raiz, repo, c) if login(s.get("creator")) in contas] for c in commits}
        for linha in registro:
            if linha[0] in do_pr and linha[1] in CONTEXTOS.values() and not tem_status(linha, do_pr[linha[0]]):
                raise Recusa(f"registro de {linha[0][:7]} {linha[1]} sem o status no GitHub (CONTROLE-RUN-GRAFIA)")
        lidos = {}
        for tipo, contexto in CONTEXTOS.items():
            dela = [(quando(s), c, s) for c, lista in do_pr.items() for s in lista if s.get("context") == contexto]
            if dela:
                _, origem, s = max(dela, key=lambda x: x[0])
                lido = (conferir(raiz, repo, aberto | {"headRefOid": origem}, pedido, tipo, s, contas, registro)
                        if ancestral(raiz, origem, head) else (None, "origem do status fora da história do head (C0-2)"))
                lidos[tipo] = (*lido, origem)
    except (KeyError, TypeError, AttributeError, ValueError) as e:
        raise Recusa(f"leitura do PR: resposta do gh fora do contrato ({type(e).__name__}) (M19.1)") from None
    return lidos


def publicar(raiz, tipo, veredito, texto, sha, branch, bloqueantes, recomendados, exigidos):
    """Comentário no PR, releitura do corpo, o agregado em `pending`, o status do contexto do papel e o agregado recalculado:
    falha em qualquer passo nunca deixa um `success` velho no agregado. Recusa depois do PR diz o que já ficou gravado.
    Devolve (url do comentário, agregado)."""
    if tipo not in CONTEXTOS or veredito not in ESTADOS or not re.fullmatch(r"[0-9a-f]{40}", sha or ""):
        raise Recusa(f"tipo `{tipo}`, veredito `{veredito}` ou commit fora da lista")
    desc = descricao(veredito, texto, bloqueantes, recomendados)  # antes de gravar qualquer coisa
    pr, gravado, controle = pr_aberto(raiz, branch, sha), "nada", pasta_de_controle(raiz)
    if login(gh(raiz, ["api", "user"])) not in contas_aceitas(raiz):
        raise Recusa("a conta da sessão (`gh api user`) não é a dona do `origin`; nada gravado (M1.4)")
    try:
        criado = gh(raiz, ["api", "-X", "POST", f"repos/{{owner}}/{{repo}}/issues/{pr['number']}/comments", "--input", "-"],
                    {"body": texto})
        gravado = f"o comentário no PR #{pr['number']}"
        lido = gh(raiz, ["api", f"repos/{{owner}}/{{repo}}/issues/comments/{int(criado['id'])}"])
        if normalizar(str(lido.get("body"))) != normalizar(texto):
            raise Recusa("o corpo devolvido pela API difere do arquivo local; status não gravado (M5.3)")
        if (url := lido.get("html_url")) != f"{pr['url']}#issuecomment-{int(criado['id'])}":
            raise Recusa(f"o comentário não é do PR #{pr['number']}: {url}")
        registrar(controle, sha, CONTEXTOS[tipo], DESCRICAO.fullmatch(desc)[2], int(criado["id"]))
        gravar_status(raiz, sha, AGREGADO, "pending", f"recalculando depois de {CONTEXTOS[tipo]}")  # QA A1 do #878
        gravado += f", {AGREGADO} pending"
        gravar_status(raiz, sha, CONTEXTOS[tipo], ESTADOS[veredito], desc, url)
        gravado += f", {CONTEXTOS[tipo]} {ESTADOS[veredito]}"
        estado = agregado(raiz, sha, exigidos)
        gravar_status(raiz, sha, AGREGADO, *estado)
    except (Recusa, KeyError, TypeError, AttributeError, ValueError) as e:
        raise Recusa(f"{e}; já gravado: {gravado}") from None
    return url, estado
