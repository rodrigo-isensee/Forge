r"""`forge-check comparar <base> <head>` (AE7.1, v0478 E58.30): o "só aperta" medido nos hooks da base e do head.

Mede: o veredito dos hooks do `hooks/hooks.json` da raiz sobre o corpus da base mais os casos novos do head, extraídos blob a
blob como o clone do plugin os instala e rodados como o Claude Code os roda (matcher, argv, prazo, stdin, ambiente por lista
positiva), um projeto git novo por caso; cada lado inteiro e sozinho, em temporário, HOME e TMPDIR próprios, a base antes.
Veredito em 4 níveis (recusa < pergunta < sem decisão < allow); o `updatedInput` que muda também conta, salvo no caso
recusado. rc 0 nada liberado a mais; 1 `aceite-novo` ou `corpus-removido`.

Só mede a árvore que cumpre a lista positiva de forma F1 a F7 nos dois lados (emenda AE7.1, E58.52); a lista é deste código,
nunca da árvore medida. Fora dela, rc 2 `nao-verificavel (F<n> ...)` com o item que falhou:
- F1 modos: só blob 100644 e 100755 (e pasta); link 120000 (A11) e submódulo 160000 (A14) saem.
- F2 nomes, em qualquer pasta: nenhum `.gitattributes` (A2) nem `.gitmodules` (A14).
- F3 raiz: nenhuma entrada `.mcp.json`, `.lsp.json`, `settings.json`, `monitors` (A18: arma comando fora do sandbox) nem
  `workflows` (scripts `.js`), arquivo ou pasta: as entradas de convenção da raiz que carregam código ou servidor fora de
  `hooks/hooks.json` e que as outras regras não cobrem. Conferida no Claude Code 2.1.224: a lista de convenção do binário
  (`.claude-plugin`, `commands`, `skills`, `agents`, `hooks`, `themes`, `output-styles`, `monitors`, `workflows`,
  `SKILL.md`, `.mcp.json`, `.lsp.json`) mais o `settings.json`, e a tabela "Standard layout" de
  code.claude.com/docs/en/plugins-reference, lida em 2026-11-21. `.claude-plugin` é F4 e F5; `commands`, `skills`,
  `agents`, `output-styles` e `SKILL.md` são `.md` (F6); `themes` não executa; `bin/` é limite declarado (abaixo).
- F4 `.claude-plugin/plugin.json`: objeto só com as chaves de CHAVES_PLUGIN, sem `hooks` em nível nenhum (A10, A16).
- F5 `.claude-plugin/marketplace.json`: só as chaves de CHAVES_MARKETPLACE; `metadata` só `description` e `version` (sem
  `pluginRoot`, A15); `plugins` com uma entrada só, chaves de CHAVES_ENTRADA e `source` `.` ou `./` (A12).
- F6 cabeçalho YAML de todo `.md`, forma simples, linhas partidas em toda quebra do `splitlines` (`\r` sozinho, `\r\n`,
  `\n`, `\v`, `\f`, `\x1c` a `\x1e`, `\x85`, U+2028 e U+2029; o YAML do Claude Code quebra no `\r` sozinho, A17): a 1ª
  linha de conteúdo na coluna 0; toda linha na coluna 0 que não é comentário é `chave:` com a chave em [A-Za-z0-9_-], e
  a chave não é `hooks` nem `allowed-tools` (A13, A16); linha recuada é valor da chave de cima; o corpo não conta (A6).
- F7 `hooks/hooks.json`: matcher na forma simples (nome, `|`, `*` ou vazio): só nela o `re` do Python casa como o Claude Code
  (A7).
Também rc 2: ref que não é commit deste repositório; corpus ilegível ou vazio; árvore que o git não lista; extração que falha.

Quem consome exige a linha `so-aperta: medido base=<sha> head=<sha>`, não só o rc. Executa o código da base e do head: só
com head deste repositório e sob o sandbox. Limites declarados (não reprovam): liberação que não passa por hook (código de
`bin/` e `scripts/`, instrução de agente, permissão do projeto ou do usuário; `so-aperta: medido` fala dos hooks, não do
plugin inteiro); o que o instalador ou o Claude Code passarem a ler depois da versão sondada; hook que detecta o ambiente
sintético (assunto do code review); o corpus é finito.

AE7.2 (v0478 E107.1): o corpus de cada lado soma as famílias geradas por `tests/comparar/geradores.py` daquele lado, rodado
com `python3 -I - <SEMENTE>` (semente fixa, impressa em `familias: semente=<n> <família>=<casos>`); gerador que falha é
`nao-verificavel`, e o caso gerado que some no head é `corpus-removido`, como o do corpus. Alvo `entrega` (`executar_entrega`;
a opção na CLI é do AE7.3): o `bin/forge-check` da base e do head, cada um extraído inteiro, rodado em cada repositório de
fixture (uma cópia por lado e caso, HOME e TMPDIR próprios); rc 0 é aceite, outro rc, prazo ou erro é recusa."""
import hashlib
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CORPUS = "tests/comparar/corpus.jsonl"
GERADORES, SEMENTE = "tests/comparar/geradores.py", 478  # AE7.2: a semente é deste código, nunca da árvore medida
TETO_GERADOS, TETO_CASOS = 4 << 20, 2000  # A2 (E107.6): bytes da saída do gerador e casos gerados por lado
ENTREGA, PRAZO_ENTREGA = "bin/forge-check", 120
REF = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]{0,199}")
AMBIENTE = ("PATH", "LANG", "LC_ALL", "LC_CTYPE", "USER", "LOGNAME", "SHELL", "TERM")  # HOME e TMPDIR: os do lado
RECUSA, PERGUNTA, ACEITE, ALLOW = 0, 1, 2, 3  # A1: `allow` pula a pergunta ao usuário, libera mais que o silêncio
NOMES = ("recusa", "pergunta", "aceite", "allow")
MATCHER_SIMPLES = re.compile(r"[A-Za-z0-9_|]*|\*")
MODOS = (b"100644", b"100755")  # F1: o `ls-tree -r` não lista pasta
NOMES_FORA = (b".gitattributes", b".gitmodules")  # F2
RAIZ_FORA = (b".mcp.json", b".lsp.json", b"settings.json", b"monitors", b"workflows")  # F3: 1º nome do caminho
CHAVES_PLUGIN = {"name", "version", "description", "author", "repository", "homepage", "license", "keywords", "agents",
                 "skills", "commands"}  # F4
CHAVES_MARKETPLACE = {"$schema", "name", "owner", "metadata", "plugins"}  # F5
CHAVES_ENTRADA = CHAVES_PLUGIN - {"agents", "skills", "commands"} | {"source"}  # F5: uma entrada de `plugins`
CHAVE_SIMPLES = re.compile(r"([A-Za-z0-9_-]+):(?:[ \t].*)?")  # F6
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


def teto_de_arquivo():
    """A2: no filho do gerador, nada escrito passa de TETO_GERADOS + 1 bytes (o excesso o `fstat` acusa)."""
    resource.setrlimit(resource.RLIMIT_FSIZE, (TETO_GERADOS + 1, TETO_GERADOS + 1))


def gerados_de(ctx, raiz, sha):
    """AE7.2: o JSONL das famílias geradas em `sha` (o gerador daquele lado, `python3 -I`, num temporário, com a SEMENTE); ""
    sem o arquivo; None se o git ou o gerador falha, passa do prazo, ou a saída passa de TETO_GERADOS bytes ou TETO_CASOS
    linhas (A2: a saída vai a um arquivo anônimo com RLIMIT_FSIZE, nunca inteira à memória)."""
    if ctx["git"](raiz, "cat-file", "-e", f"{sha}:{GERADORES}")[0] != 0:
        return ""
    cod, codigo = ctx["git"](raiz, "cat-file", "blob", f"{sha}:{GERADORES}", bruto=True)
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryFile() as saida:
        try:
            r = subprocess.run([sys.executable, "-I", "-", str(SEMENTE)], input=codigo, cwd=tmp, stdout=saida,
                               stderr=subprocess.DEVNULL, timeout=60, preexec_fn=teto_de_arquivo,
                               env=dict({k: os.environ[k] for k in AMBIENTE if k in os.environ}, HOME=tmp, TMPDIR=tmp))
        except (subprocess.SubprocessError, OSError):
            return None
        if os.fstat(saida.fileno()).st_size > TETO_GERADOS:
            return None
        saida.seek(0)
        texto = saida.read().decode("utf-8", "replace")
    return texto if cod == 0 and r.returncode == 0 and len(texto.splitlines()) <= TETO_CASOS else None


def corpus_de(ctx, raiz, sha):
    """{id: linha canônica} do corpus em `sha` mais as famílias geradas (AE7.2); {} sem os dois; None se uma linha não é caso,
    repete um id ou o gerador falha."""
    gerados = gerados_de(ctx, raiz, sha)
    cod, texto = 0, ""
    if ctx["git"](raiz, "cat-file", "-e", f"{sha}:{CORPUS}")[0] == 0:
        cod, texto = ctx["git"](raiz, "cat-file", "blob", f"{sha}:{CORPUS}")
    if cod != 0 or gerados is None:
        return None
    casos = {}
    for linha in filter(str.strip, (texto + "\n" + gerados).splitlines()):
        try:
            caso = json.loads(linha)
        except ValueError:
            return None
        if not caso_valido(caso) or caso["id"] in casos:
            return None
        casos[caso["id"]] = json.dumps(caso, sort_keys=True, ensure_ascii=False)
    return casos


def objeto_na_lista(texto, chaves_da_raiz):
    """O objeto do JSON se ele se lê, tem só chaves de `chaves_da_raiz` na raiz e nenhuma `hooks` em nível nenhum; senão None."""
    chaves = []
    try:
        objeto = json.loads(texto, object_pairs_hook=lambda pares: chaves.extend(k for k, _ in pares) or dict(pares))
    except ValueError:
        return None
    return objeto if isinstance(objeto, dict) and set(objeto) <= chaves_da_raiz and "hooks" not in chaves else None


def plugin_fora_da_lista(texto):
    """F4 (A10, A16): `hooks`, `mcpServers`, `lspServers`, `monitors`, `outputStyles` e chave futura saem."""
    return objeto_na_lista(texto, CHAVES_PLUGIN) is None


def marketplace_fora_da_lista(texto):
    """F5 (A12, A15): `metadata` só `description` e `version`; uma entrada em `plugins`, com `source` `.` ou `./`."""
    try:
        objeto = objeto_na_lista(texto, CHAVES_MARKETPLACE)
        plugins, metadata = objeto["plugins"], objeto.get("metadata", {})
        return not (isinstance(plugins, list) and len(plugins) == 1 and isinstance(plugins[0], dict)
                    and set(plugins[0]) <= CHAVES_ENTRADA and plugins[0].get("source") in (".", "./")
                    and isinstance(metadata, dict) and set(metadata) <= {"description", "version"})
    except (TypeError, KeyError):
        return True


MANIFESTOS = ((".claude-plugin/plugin.json", "F4", plugin_fora_da_lista),
              (".claude-plugin/marketplace.json", "F5", marketplace_fora_da_lista))


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
    """O cabeçalho YAML do `.md`, linhas juntadas por `\n`: do `---` do começo até a próxima linha só `---`; sem fecho, o
    texto inteiro; sem `---` no começo (fora o BOM e linhas em branco), vazio. Quebra em toda quebra do `splitlines` (A17)."""
    linhas = texto.lstrip("\ufeff \t\r\n").splitlines() or [""]
    if not linhas[0].startswith("---"):
        return ""
    fecho = next((i for i, linha in enumerate(linhas[1:], 1) if linha == "---"), len(linhas))
    return "\n".join(linhas[1:fecho])


def cabecalho_simples(texto):
    """F6: o cabeçalho do `.md` cumpre a forma simples (docstring do módulo); sem cabeçalho, cumpre."""
    linhas = [linha for linha in cabecalho(texto).split("\n") if linha.strip()]
    if linhas and linhas[0][0] in " \t":
        return False
    for linha in linhas:
        if linha[0] in " \t#":
            continue
        chave = CHAVE_SIMPLES.fullmatch(linha)
        if not chave or chave.group(1).lower() in ("hooks", "allowed-tools"):
            return False
    return True


def fora_da_medida(ctx, raiz, sha):
    """Motivo de `nao-verificavel` na árvore de `sha`, ou None: o item F1 a F7 (docstring do módulo) que ela não cumpre."""
    cod, lista = ctx["git"](raiz, "ls-tree", "-r", "-z", "-l", "--full-tree", sha, bruto=True)
    itens = [re.fullmatch(rb"(\d{6}) \w+ ([0-9a-f]+) +\S+\t(.+)", e, re.S) for e in lista.split(b"\0") if e]
    if cod != 0 or not all(itens):
        return "árvore ilegível"
    itens = [i.groups() for i in itens]
    fora = next((modo for modo, _, _ in itens if modo not in MODOS), None)
    if fora:
        return f"F1 modo {fora.decode()} na árvore"
    if any(os.path.basename(n).lower() in NOMES_FORA for _, _, n in itens):
        return "F2 .gitattributes ou .gitmodules na árvore"
    fora = next((n for _, _, n in itens if n.lower().split(b"/")[0] in RAIZ_FORA), None)
    if fora:
        return f"F3 {fora.decode()} na raiz"
    for manifesto, item, fora_da_lista in MANIFESTOS:
        if ctx["git"](raiz, "cat-file", "-e", f"{sha}:{manifesto}")[0] == 0:
            cod, texto = ctx["git"](raiz, "cat-file", "blob", f"{sha}:{manifesto}")
            if cod != 0 or fora_da_lista(texto):
                return f"{item} {manifesto} fora da lista"
    mds = [o for _, o, n in itens if n.lower().endswith(b".md")]
    if mds:
        cod, lote = ctx["git"](raiz, "cat-file", "--batch", bruto=True, entrada=b"".join(o + b"\n" for o in mds))
        textos = blobs_do_lote(lote, len(mds))
        if cod != 0 or textos is None or not all(cabecalho_simples(t.decode("utf-8", "replace")) for t in textos):
            return "F6 cabeçalho de .md fora da forma simples"
    try:
        grupos = [g for gs in json.loads(ctx["git"](raiz, "cat-file", "blob", f"{sha}:hooks/hooks.json")[1])["hooks"].values() for g in gs]
    except (ValueError, KeyError, TypeError, AttributeError):  # hooks.json ilegível ou ausente: nenhum hook, medido assim
        return None
    if not all(isinstance(g, dict) and isinstance(g.get("matcher", ""), str) and MATCHER_SIMPLES.fullmatch(g.get("matcher", ""))
               for g in grupos):
        return "F7 matcher fora da forma simples em hooks/hooks.json"
    return None


def extrair(ctx, raiz, sha, destino):
    """A árvore de `sha` como o clone a instala (A2): `ls-tree` e `cat-file --batch`; só chega aqui a que cumpre F1 a F7.
    Nome que sai da pasta, modo fora da F1, resposta truncada ou git que falha: False."""
    cod, lista = ctx["git"](raiz, "ls-tree", "-r", "-z", "--full-tree", sha, bruto=True)
    try:
        itens = [re.fullmatch(rb"(\d{6}) blob ([0-9a-f]+)\t(.+)", e, re.S).groups() for e in lista.split(b"\0") if e]
        lido, lote = ctx["git"](raiz, "cat-file", "--batch", bruto=True, entrada=b"".join(o + b"\n" for _, o, _ in itens))
        dentro, pos = Path(os.path.realpath(destino)), 0
        for modo, _, nome in itens:
            alvo, fim = destino / os.fsdecode(nome), lote.index(b"\n", pos)
            tamanho = int(lote[pos:fim].split()[2])
            dados, pos = lote[fim + 1:fim + 1 + tamanho], fim + 2 + tamanho
            if len(dados) != tamanho or not Path(os.path.realpath(alvo)).is_relative_to(dentro):
                return False
            if modo not in MODOS:  # F1: a árvore com link nem chega aqui (fora_da_medida); nada se grava por um link
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


def medir_entrega(ctx, raiz, sha, casos):
    """AE7.2, alvo `entrega`: {id: nível} do `bin/forge-check` de `sha` em cada fixture de `casos` ({id: (pasta, argv)}): a árvore
    extraída inteira e uma cópia própria de cada fixture, num temporário do lado, com HOME e TMPDIR próprios de cada caso; rc 0 é aceite,
    outro rc, prazo ou erro é recusa. None se a extração falha."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        arvore = Path(tmp) / "plugin"
        if not extrair(ctx, raiz, sha, arvore):
            return None
        niveis = {}
        for n, i in enumerate(sorted(casos)):  # A3 (E107.6): HOME e TMPDIR de cada caso, nada passa de um caso ao seguinte
            pasta, argv = casos[i]
            copia, home, temp = (Path(tmp) / f"{nome}-{n}" for nome in ("fixture", "home", "tmp"))
            home.mkdir()
            temp.mkdir()
            ambiente = dict({k: os.environ[k] for k in AMBIENTE if k in os.environ}, HOME=str(home), TMPDIR=str(temp))
            try:
                shutil.copytree(pasta, copia, symlinks=True)
                r = subprocess.run([sys.executable, "-I", str(arvore / ENTREGA), "--raiz", str(copia), *argv], cwd=copia,
                                   env=ambiente, capture_output=True, timeout=PRAZO_ENTREGA)
                niveis[i] = ACEITE if r.returncode == 0 else RECUSA
            except (subprocess.TimeoutExpired, OSError, shutil.Error):
                niveis[i] = RECUSA
        return niveis


def executar_entrega(ctx, raiz, base, head, casos):
    """AE7.2: o alvo `entrega` sobre `casos` ({id: (pasta do repositório de fixture, argv do forge-check)}), a base antes; rc 0
    nada aceito a mais, 1 `aceite-novo`, 2 `nao-verificavel` (sem caso, fixture que não é repositório, extração que falha)."""
    heads = {i: ctx["git"](Path(p), "rev-parse", "--verify", "--quiet", "HEAD") for i, (p, _) in casos.items()}
    if not casos or any(cod != 0 for cod, _ in heads.values()):
        print("so-aperta: nao-verificavel (alvo entrega sem fixture ou com fixture que não é repositório)")
        return 2
    resumo = hashlib.sha256(json.dumps([[i, list(casos[i][1]), heads[i][1]] for i in sorted(casos)]).encode()).hexdigest()
    lado_base = medir_entrega(ctx, raiz, base, casos)
    lado_head = None if lado_base is None else medir_entrega(ctx, raiz, head, casos)
    if lado_head is None:
        print("so-aperta: nao-verificavel (extração da árvore falhou)")
        return 2
    novos = [f"aceite-novo: {ctx['seguro'](i)} base={NOMES[lado_base[i]]} head={NOMES[lado_head[i]]}"
             for i in sorted(casos) if lado_head[i] > lado_base[i]]
    print("\n".join([f"so-aperta: medido alvo=entrega base={base} head={head} corpus={resumo} casos={len(casos)} "
                     f"aceites-novos={len(novos)}", *novos]))
    return 1 if novos else 0


def executar(a, raiz, ctx):
    base, head = sha_de(ctx, raiz, a.base), sha_de(ctx, raiz, a.head)
    if base is None or head is None:
        print("so-aperta: nao-verificavel (base ou head não é commit deste repositório)")
        return 2
    alvo = getattr(a, "alvo", "hooks")  # AE7.2: a opção `--alvo` na CLI é do AE7.3
    if alvo == "entrega":
        return executar_entrega(ctx, raiz, base, head, getattr(a, "fixtures", None) or {})
    if alvo != "hooks":
        print(f"so-aperta: nao-verificavel (alvo {ctx['seguro'](str(alvo))} desconhecido)")
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
    familias = sorted({i.split("/")[1] for i in casos if i.startswith("gerada/") and i.count("/") == 2})
    # A1 (E107.6): o nome da família vem do id gerado pelo head; nada dele imita outra linha da saída
    cobertura = ctx["seguro"](" ".join(f"{f}={sum(i.startswith(f'gerada/{f}/') for i in casos)}" for f in familias))
    print("\n".join([f"so-aperta: medido base={base} head={head} corpus={resumo} casos={len(casos)} aceites-novos={len(novos)}",
                     *([f"familias: semente={SEMENTE} {cobertura}"] if familias else []), *novos, *(f"corpus-removido: {ctx['seguro'](i)}" for i in removidos)]))
    return 1 if novos or removidos else 0
