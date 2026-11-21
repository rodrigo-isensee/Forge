"""`forge-check comparar <base> <head>` (AE7.1, v0478 E58.30): o "só aperta" medido nos hooks da base e do head, extraídos
por `git archive` deste repositório e rodados como o Claude Code os roda (hooks.json da árvore, matcher, argv, prazo, stdin,
ambiente por lista positiva), um projeto git novo por caso, sobre o corpus da base mais os casos novos do head. rc 0 nada
liberado a mais; 1 `aceite-novo` ou `corpus-removido`; 2 `nao-verificavel`. Só leitura, sem rede. Limite: o corpus é finito."""
import hashlib
import io
import json
import os
import re
import subprocess
import tarfile
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CORPUS = "tests/comparar/corpus.jsonl"
REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]{0,199}")
AMBIENTE = ("PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "USER", "LOGNAME", "SHELL", "TERM", "TMPDIR")
RECUSA, PERGUNTA, ACEITE = 0, 1, 2
NOMES = ("recusa", "pergunta", "aceite")
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


def extrair(ctx, raiz, sha, destino):
    cod, tar = ctx["git"](raiz, "archive", "--format=tar", sha, bruto=True)
    try:
        with tarfile.open(fileobj=io.BytesIO(tar)) as arquivo:
            arquivo.extractall(destino, filter="data")  # sem link nem caminho para fora da pasta
    except (tarfile.TarError, OSError):
        return False
    return cod == 0


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
    """Como o Claude Code lê o hook: 2 recusa; 0 com `deny`/`block` recusa, com `ask` pergunta; prazo, erro e o resto liberam."""
    try:
        r = subprocess.run(argv, input=json.dumps(entrada), cwd=projeto, env=ambiente, capture_output=True, text=True, timeout=prazo)
    except (subprocess.TimeoutExpired, OSError):
        return ACEITE
    if r.returncode == 2:
        return RECUSA
    try:
        saida = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {}
        decisao = (saida.get("hookSpecificOutput") or {}).get("permissionDecision")
    except (ValueError, AttributeError):
        return ACEITE
    if decisao == "deny" or saida.get("decision") == "block" or saida.get("continue") is False:
        return RECUSA
    return PERGUNTA if decisao == "ask" else ACEITE


def rodar_caso(ctx, arvore, caso, sessao):
    projeto = Path(tempfile.mkdtemp(dir=arvore.parent))
    arquivos = {"README.md": "projeto\n", ".forge/versao": "0.5.0\n", ".gitignore": ".forge/run/\n", **caso.get("arquivos", {})}
    for rel, texto in arquivos.items():
        (projeto / rel).parent.mkdir(parents=True, exist_ok=True)
        (projeto / rel).write_text(texto, encoding="utf-8")
    for passo in (("init", "-q", "-b", "develop"), ("add", "-A"), (*SEM_HOOKS_DO_USUARIO, "commit", "-q", "-m", "base")):
        ctx["git"](projeto, *passo)
    entrada = json.loads(json.dumps(caso["entrada"]).replace("{raiz}", json.dumps(str(projeto))[1:-1]))
    entrada = {"session_id": sessao, "cwd": str(projeto), "hook_event_name": "PreToolUse", **entrada}
    ambiente = dict({k: os.environ[k] for k in AMBIENTE if k in os.environ}, CLAUDE_PROJECT_DIR=str(projeto), CLAUDE_PLUGIN_ROOT=str(arvore))
    hooks = hooks_de(arvore, entrada["hook_event_name"], str(entrada.get("tool_name", "")))
    return min((veredito(argv, prazo, entrada, projeto, ambiente) for argv, prazo in hooks), default=ACEITE)


def executar(a, raiz, ctx):
    base, head = sha_de(ctx, raiz, a.base), sha_de(ctx, raiz, a.head)
    if base is None or head is None:
        print("so-aperta: nao-verificavel (base ou head não é commit deste repositório)")
        return 2
    corpus_base, corpus_head = corpus_de(ctx, raiz, base), corpus_de(ctx, raiz, head)
    if corpus_base is None or corpus_head is None or not {**corpus_head, **corpus_base}:
        print(f"so-aperta: nao-verificavel ({CORPUS} ilegível ou vazio)")
        return 2
    removidos = sorted(i for i, linha in corpus_base.items() if corpus_head.get(i) != linha)
    casos = {**corpus_head, **corpus_base}
    resumo = hashlib.sha256("\n".join(casos[i] for i in sorted(casos)).encode()).hexdigest()
    sessao = str(uuid.uuid4())
    with tempfile.TemporaryDirectory() as tmp:
        arvores = [Path(tempfile.mkdtemp(dir=tmp)) / "plugin" for _ in range(2)]
        if not all(extrair(ctx, raiz, sha, arvore) for sha, arvore in zip((base, head), arvores)):
            print("so-aperta: nao-verificavel (git archive ou extração falhou)")
            return 2
        lados = lambda i: [rodar_caso(ctx, arvore, json.loads(casos[i]), sessao) for arvore in arvores]
        with ThreadPoolExecutor(min(4, os.cpu_count() or 1)) as fila:  # R-TETO: até 4 hooks por vez
            vereditos = zip(sorted(casos), fila.map(lados, sorted(casos)))
            novos = [f"aceite-novo: {ctx['seguro'](i)} base={NOMES[b]} head={NOMES[h]}" for i, (b, h) in vereditos if h > b]
    print("\n".join([f"so-aperta: medido base={base} head={head} corpus={resumo} casos={len(casos)} aceites-novos={len(novos)}",
                     *novos, *(f"corpus-removido: {ctx['seguro'](i)}" for i in removidos)]))
    return 1 if novos or removidos else 0
