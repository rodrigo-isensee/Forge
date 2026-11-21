"""`forge-check comparar <base> <head>` (AE7.1, v0478 E58.30): o "só aperta" medido nos hooks da base e do head.

Mede: os hooks do `hooks/hooks.json` da raiz, extraídos blob a blob deste repositório como o clone do plugin os instala e
rodados como o Claude Code os roda (matcher, argv, prazo, stdin, ambiente por lista positiva), um projeto git novo por caso,
sobre o corpus da base mais os casos novos do head; cada lado inteiro e sozinho, em temporário, HOME e TMPDIR próprios, a
base antes. Veredito em 4 níveis (recusa < pergunta < sem decisão < allow); o `updatedInput` que muda também conta, salvo no
caso recusado. rc 0 nada liberado a mais; 1 `aceite-novo` ou `corpus-removido`.

Dá rc 2 `nao-verificavel` (em qualquer lado): ref que não é commit deste repositório; corpus ilegível ou vazio; árvore que o
git não lista; `.gitattributes` em qualquer pasta (o checkout aplica atributos que a extração não aplica); link simbólico em
qualquer pasta (A11: o clone e o Claude Code o atravessam, a leitura pelo git não); chave `hooks` em qualquer nível de
`.claude-plugin/plugin.json` ou `marketplace.json`, ou manifesto ilegível (A10); marketplace com mais de um plugin ou com
`source` que não é `.` nem `./` (A12: o Claude Code instala a pasta de `source`, e a medida roda a raiz); no cabeçalho YAML de
qualquer `.md`, `hooks` seguido de `:` em qualquer recuo ou em fluxo, `? hooks`, barra invertida, âncora, alias ou tag (A13,
leitura conservadora sem YAML; o corpo do `.md` não conta, A6); matcher fora da forma simples (premissa: só nela o `re` do
Python casa como o Claude Code, A7); extração que falha.

Quem consome exige a linha `so-aperta: medido base=<sha> head=<sha>`, não só o rc. Executa o código da base e do head: só
com head deste repositório e sob o sandbox. Limites: o corpus é finito, a medida pega o afrouxamento honesto (hook que
detecta o ambiente sintético, como o autor do commit ou `.forge/versao`, é assunto do code review), e hook declarado por
outro caminho que o Claude Code venha a ler (fora de `hooks/hooks.json`, dos dois manifestos e do cabeçalho de `.md`) não é
visto."""
import hashlib
import json
import os
import re
import subprocess
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CORPUS = "tests/comparar/corpus.jsonl"
REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]{0,199}")
AMBIENTE = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "USER", "LOGNAME", "SHELL", "TERM")  # HOME e TMPDIR: os do lado
RECUSA, PERGUNTA, ACEITE, ALLOW = 0, 1, 2, 3  # A1: `allow` pula a pergunta ao usuário, libera mais que o silêncio
NOMES = ("recusa", "pergunta", "aceite", "allow")
MATCHER_SIMPLES = re.compile(r"[A-Za-z0-9_|]*|\*")
MANIFESTOS = (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json")  # A10: o campo `hooks` também declara hook
# A13: no cabeçalho YAML, `hooks` seguido de `:` em qualquer recuo ou em fluxo, chave explícita `? hooks`, barra invertida
# (escape entre aspas) e âncora, alias ou tag (`&`, `*`, `!`: a chave sai de outro lugar). Leitura conservadora, sem YAML.
CABECALHO_SUSPEITO = re.compile(r"""hooks['"]?\s*(?:#[^\n]*\n\s*)?:|\?\s*['"]?hooks|\\|(?:^|[\s\[{,:?-])[&*!][^\s,\[\]{}]""",
                                re.I | re.M)
SEM_HOOKS_DO_USUARIO = "-c core.hooksPath=/dev/null -c commit.gpgsign=false -c user.name=forge -c user.email=forge@localhost -c gc.auto=0".split()


def sha_de(ctx, raiz, ref):
    """O sha do commit de `ref` neste repositório, ou None: nada que comece com `-` nem tenha `..` chega ao git."""
    if not REF.fullmatch(ref) or ".." in ref:
        return None
    cod, saida = ctx["git"](raiz, "rev-parse", "--verify", "--quiet", "--end-of-options", ref + "^{commit}")
    return saida if cod == 0 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", saida) else None


def caso_valido(caso):
    arquivos = caso.get("arquivos", {}) if isinstance(caso, dict) else None
    return (isinstance(caso, dict) and isinstance(caso.get("id"), str) and isinstance(caso.get("entrada"), dict)
            and isinstance(arquivos, dict) and all(isinstance(t, str) and Path(r).parts and not Path(r).is_absolute()
                                                   and ".." not in Path(r).parts for r, t in arquivos.items()))


def corpus_de(ctx, raiz, sha):
    """{id: linha canônica} do corpus em `sha`; {} sem o arquivo; None se uma linha não é caso ou repete um id."""
    if ctx["git"](raiz, "cat-file", "-e", f"{sha}:{CORPUS}")[0] != 0:
        return {}
    cod, texto = ctx["git"](raiz, "cat-file", "blob", f"{sha}:{CORPUS}")
    if cod != 0:
        return None
    casos = {}
    for linha in filter(str.strip, texto.splitlines()):
        try:
            caso = json.loads(linha)
        except ValueError:
            return None
        if not caso_valido(caso) or caso["id"] in casos:
            return None
        casos[caso["id"]] = json.dumps(caso, sort_keys=True, ensure_ascii=False)
    return casos


def declara_hooks(texto):
    """True se o JSON tem a chave `hooks` em qualquer nível ou não se lê (A10: na dúvida, fora da medida)."""
    chaves = []
    try:
        json.loads(texto, object_pairs_hook=lambda pares: chaves.extend(k for k, _ in pares) or dict(pares))
    except ValueError:
        return True
    return "hooks" in chaves


def plugin_fora_da_raiz(texto):
    """True se o marketplace.json instala outra pasta que não a raiz (A12): `plugins` que não é uma lista de uma entrada só,
    ou `source` que não é a string `.` nem `./` (pasta, repositório de fora, objeto); JSON ilegível também."""
    try:
        plugins = json.loads(texto).get("plugins")
        return not (isinstance(plugins, list) and len(plugins) == 1
                    and plugins[0].get("source") in (".", "./"))
    except (ValueError, AttributeError):
        return True


def blobs_do_lote(lote, quantos):
    """Os `quantos` blobs da saída do `cat-file --batch`, lidos pelo tamanho do cabeçalho; None se ela não fecha."""
    blobs, pos = [], 0
    try:
        for _ in range(quantos):
            fim = lote.index(b"\n", pos)
            tamanho = int(lote[pos:fim].split()[2])
            blobs.append(lote[fim + 1:fim + 1 + tamanho])
            pos = fim + 2 + tamanho
    except (ValueError, IndexError):
        return None
    return blobs if pos == len(lote) else None


def cabecalho(texto):
    """O cabeçalho YAML do `.md`: do `---` do começo até a próxima linha só `---`; sem fecho, o texto inteiro; sem `---` no
    começo (fora o BOM e linhas em branco), vazio."""
    linhas = texto.lstrip("\ufeff \t\r\n").split("\n")
    if not linhas[0].startswith("---"):
        return ""
    fecho = next((i for i, linha in enumerate(linhas[1:], 1) if linha.rstrip("\r") == "---"), len(linhas))
    return "\n".join(linhas[1:fecho])


def fora_da_medida(ctx, raiz, sha):
    """Motivo de `nao-verificavel` na árvore de `sha`, ou None. A2: `.gitattributes` em qualquer pasta (ident, eol, filter,
    working-tree-encoding mudam o que o clone instala; a extração grava o blob cru). A11: link simbólico em qualquer pasta (o
    clone e o Claude Code o atravessam; a leitura pelo git, não). A10, A12, A13: hook declarado fora do `hooks/hooks.json` da
    raiz. A7: matcher de hooks.json fora da forma simples (nome, `|`, `*` ou vazio): fora dela, o motor de regex do Claude
    Code pode casar diferente do `re` do Python."""
    cod, lista = ctx["git"](raiz, "ls-tree", "-r", "-z", "-l", "--full-tree", sha, bruto=True)
    itens = [re.fullmatch(rb"(\d{6}) \w+ ([0-9a-f]+) +\S+\t(.+)", e, re.S) for e in lista.split(b"\0") if e]
    if cod != 0 or not all(itens):
        return "árvore ilegível"
    itens = [i.groups() for i in itens]
    if any(os.path.basename(n).lower() == b".gitattributes" for _, _, n in itens):
        return "atributos de checkout: .gitattributes na árvore"
    if any(modo == b"120000" for modo, _, _ in itens):
        return "link simbólico na árvore"
    for manifesto in MANIFESTOS:
        if ctx["git"](raiz, "cat-file", "-e", f"{sha}:{manifesto}")[0] == 0:
            cod, texto = ctx["git"](raiz, "cat-file", "blob", f"{sha}:{manifesto}")
            if cod != 0 or declara_hooks(texto):
                return f"hooks declarados em {manifesto}"
            if manifesto.endswith("marketplace.json") and plugin_fora_da_raiz(texto):
                return "plugin fora da raiz: source no marketplace.json"
    mds = [o for _, o, n in itens if n.lower().endswith(b".md")]
    if mds:
        cod, lote = ctx["git"](raiz, "cat-file", "--batch", bruto=True, entrada=b"".join(o + b"\n" for o in mds))
        textos = blobs_do_lote(lote, len(mds))
        if cod != 0 or textos is None or any(CABECALHO_SUSPEITO.search(cabecalho(t.decode("utf-8", "replace"))) for t in textos):
            return "hooks declarados no cabeçalho de agente ou skill"
    try:
        grupos = [g for gs in json.loads(ctx["git"](raiz, "cat-file", "blob", f"{sha}:hooks/hooks.json")[1])["hooks"].values() for g in gs]
    except (ValueError, KeyError, TypeError, AttributeError):  # hooks.json ilegível ou ausente: nenhum hook, medido assim
        return None
    if not all(isinstance(g, dict) and isinstance(g.get("matcher", ""), str) and MATCHER_SIMPLES.fullmatch(g.get("matcher", ""))
               for g in grupos):
        return "matcher fora da forma simples em hooks/hooks.json"
    return None


def extrair(ctx, raiz, sha, destino):
    """A árvore de `sha` como o clone a instala (A2): `ls-tree` e `cat-file --batch`, sem atributo nem link (quem os tem nem
    chega aqui). Nome que sai da pasta, link, resposta truncada ou git que falha: False."""
    cod, lista = ctx["git"](raiz, "ls-tree", "-r", "-z", "--full-tree", sha, bruto=True)
    try:
        itens = [re.fullmatch(rb"(\d{6}) blob ([0-9a-f]+)\t(.+)", e, re.S).groups() for e in lista.split(b"\0")
                 if e and not e.startswith(b"160000 ")]  # submódulo: o clone sem --recursive deixa a pasta vazia
        lido, lote = ctx["git"](raiz, "cat-file", "--batch", bruto=True, entrada=b"".join(o + b"\n" for _, o, _ in itens))
        dentro, pos = Path(os.path.realpath(destino)), 0
        for modo, _, nome in itens:
            alvo, fim = destino / os.fsdecode(nome), lote.index(b"\n", pos)
            tamanho = int(lote[pos:fim].split()[2])
            dados, pos = lote[fim + 1:fim + 1 + tamanho], fim + 2 + tamanho
            if len(dados) != tamanho or not Path(os.path.realpath(alvo)).is_relative_to(dentro):
                return False
            if modo == b"120000":  # A11: a árvore com link nem chega aqui (fora_da_medida); nada se grava por um link
                return False
            alvo.parent.mkdir(parents=True, exist_ok=True)
            alvo.write_bytes(dados)
            alvo.chmod(0o755 if modo == b"100755" else 0o644)
    except (AttributeError, ValueError, IndexError, OSError):
        return False
    return cod == 0 and lido == 0


def hooks_de(arvore, evento, ferramenta):
    try:
        grupos = json.loads((arvore / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"].get(evento, [])
        troca = lambda s: str(s).replace("${CLAUDE_PLUGIN_ROOT}", str(arvore))
        saida = []
        for grupo in grupos:
            matcher = grupo.get("matcher", "")
            if matcher not in ("", "*") and not re.fullmatch(matcher, ferramenta):
                continue
            for h in grupo.get("hooks", []):
                argv = [troca(h["command"]), *map(troca, h["args"])] if "args" in h else ["sh", "-c", troca(h["command"])]
                saida.append((argv, h.get("timeout", 60)))
        return saida
    except (OSError, ValueError, KeyError, TypeError, AttributeError, re.error):  # hooks.json ilegível: nenhum hook
        return []


def veredito(argv, prazo, entrada, projeto, ambiente):
    """Como o Claude Code lê o hook: 2 recusa; 0 com `deny`/`block` recusa, com `ask` pergunta, com `allow` libera sem
    perguntar; prazo, erro e o resto: sem decisão. Devolve (nível, `updatedInput` em JSON canônico ou None)."""
    try:
        r = subprocess.run(argv, input=json.dumps(entrada), cwd=projeto, env=ambiente, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=prazo)  # A8: byte inválido vira U+FFFD, como o Claude Code lê a saída
    except (subprocess.TimeoutExpired, OSError):
        return ACEITE, None
    if r.returncode == 2:
        return RECUSA, None
    try:
        saida = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
        especifico = (saida.get("hookSpecificOutput") or {})
        decisao, reescrita = especifico.get("permissionDecision"), especifico.get("updatedInput")
        decisao = decisao or ("allow" if saida.get("decision") == "approve" else None)  # A1: a forma antiga vale allow
    except (ValueError, AttributeError):
        return ACEITE, None
    if decisao == "deny" or saida.get("decision") == "block" or saida.get("continue") is False:
        return RECUSA, None
    nivel = PERGUNTA if decisao == "ask" else ALLOW if decisao == "allow" else ACEITE
    return nivel, None if reescrita is None else json.dumps(reescrita, sort_keys=True)


def rodar_caso(ctx, arvore, caso, sessao):
    """(nível, reescritas) do caso: recusa vence pergunta, que vence allow, que vence o silêncio; nas reescritas, a raiz do
    projeto vira `{raiz}` (cada lado tem o seu projeto), e o caso recusado não tem reescrita (A9: nada roda)."""
    projeto, home = Path(tempfile.mkdtemp(dir=arvore.parent)), arvore.parent / "home"
    arquivos = {"README.md": "projeto\n", ".forge/versao": "0.5.0\n", ".gitignore": ".forge/run/\n", **caso.get("arquivos", {})}
    for rel, texto in arquivos.items():
        (projeto / rel).parent.mkdir(parents=True, exist_ok=True)
        (projeto / rel).write_text(texto, encoding="utf-8")
    for passo in (("init", "-q", "-b", "develop"), ("add", "-A"), (*SEM_HOOKS_DO_USUARIO, "commit", "-q", "-m", "base")):
        ctx["git"](projeto, *passo)
    raiz_json = json.dumps(str(projeto))[1:-1]
    entrada = json.loads(json.dumps(caso["entrada"]).replace("{raiz}", raiz_json))
    entrada = {"session_id": sessao, "transcript_path": str(home / ".claude" / "projects" / f"{sessao}.jsonl"),
               "cwd": str(projeto), "permission_mode": "default", "hook_event_name": "PreToolUse", **entrada}
    ambiente = dict({k: os.environ[k] for k in AMBIENTE if k in os.environ}, HOME=str(home), TMPDIR=str(arvore.parent / "tmp"),
                    CLAUDE_PROJECT_DIR=str(projeto), CLAUDE_PLUGIN_ROOT=str(arvore))
    hooks = hooks_de(arvore, entrada["hook_event_name"], str(entrada.get("tool_name", "")))
    lidos = [veredito(argv, prazo, entrada, projeto, ambiente) for argv, prazo in hooks]
    nivel = min((n for n, _ in lidos), key=lambda n: (n == ACEITE, n), default=ACEITE)
    return nivel, [] if nivel == RECUSA else sorted(r.replace(raiz_json, "{raiz}") for _, r in lidos if r is not None)


def medir(ctx, raiz, sha, casos, sessao):
    """{id: (nível, reescritas)} de um lado (A3, A5): extraído e rodado inteiro num temporário próprio, com HOME e TMPDIR próprios,
    apagado antes de o outro lado começar; None se a extração falha."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        arvore = Path(tmp) / "plugin"
        if not extrair(ctx, raiz, sha, arvore):
            return None
        (Path(tmp) / "home").mkdir()
        (Path(tmp) / "tmp").mkdir()
        with ThreadPoolExecutor(min(4, os.cpu_count() or 1)) as fila:  # R-TETO: até 4 hooks por vez
            return dict(zip(sorted(casos), fila.map(lambda i: rodar_caso(ctx, arvore, json.loads(casos[i]), sessao), sorted(casos))))


def executar(a, raiz, ctx):
    base, head = sha_de(ctx, raiz, a.base), sha_de(ctx, raiz, a.head)
    if base is None or head is None:
        print("so-aperta: nao-verificavel (base ou head não é commit deste repositório)")
        return 2
    corpus_base, corpus_head = corpus_de(ctx, raiz, base), corpus_de(ctx, raiz, head)
    if corpus_base is None or corpus_head is None or not {**corpus_head, **corpus_base}:
        print(f"so-aperta: nao-verificavel ({CORPUS} ilegível ou vazio)")
        return 2
    motivo = fora_da_medida(ctx, raiz, base) or fora_da_medida(ctx, raiz, head)
    if motivo:
        print(f"so-aperta: nao-verificavel ({motivo})")
        return 2
    removidos = sorted(i for i, linha in corpus_base.items() if corpus_head.get(i) != linha)
    casos = {**corpus_head, **corpus_base}
    resumo = hashlib.sha256("\n".join(casos[i] for i in sorted(casos)).encode()).hexdigest()
    sessao = str(uuid.uuid4())
    lado_base = medir(ctx, raiz, base, casos, sessao)
    lado_head = None if lado_base is None else medir(ctx, raiz, head, casos, sessao)
    if lado_head is None:
        print("so-aperta: nao-verificavel (extração da árvore falhou)")
        return 2
    novos = []
    for i in sorted(casos):
        (b, reescrita_b), (h, reescrita_h) = lado_base[i], lado_head[i]
        reescreve = h != RECUSA and reescrita_h != reescrita_b  # A9: o caso recusado no head não roda, nada reescreve
        if h > b or reescreve:
            novos.append(f"aceite-novo: {ctx['seguro'](i)} base={NOMES[b]} head={NOMES[h]}"
                         + (" entrada-reescrita" if reescreve else ""))
    print("\n".join([f"so-aperta: medido base={base} head={head} corpus={resumo} casos={len(casos)} aceites-novos={len(novos)}",
                     *novos, *(f"corpus-removido: {ctx['seguro'](i)}" for i in removidos)]))
    return 1 if novos or removidos else 0
