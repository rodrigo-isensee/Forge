#!/usr/bin/env python3
"""Forge: vigia (ADR 0009, seção 8) - detecta o que escapou dos bloqueios e avisa o USUÁRIO, não o modelo.

SessionStart grava em `.forge/run/vigia.json` os hashes dos arquivos em vigor do projeto (caminhos sem dono em
`hooks/conformidade.json`) e o deslocamento atual da transcrição. Stop e SubagentStop comparam e procuram:
  - `em-vigor`   arquivo em vigor alterado, criado ou apagado desde o SessionStart (ou desde o último aviso);
  - `git`        `git status --porcelain` com mudança pendente em caminho em vigor;
  - `erro-hook`  linha nova em `.forge/run/erros.log` (hook que falhou por erro interno), exceto do próprio vigia;
  - `contorno`   na transcrição (linhas novas): uma chamada barrada por `R-CONFORMIDADE` ou `R-MAIN` e, na mesma sessão
                 e dentro de `expiracao_horas`, o mesmo alvo refeito por OUTRA ferramenta (Write barrado e Bash que
                 escreve no caminho), por outro mecanismo de escrita (script, tee, python...) ou, para `R-MAIN`, o mesmo
                 push/merge na integração que passou. Repetir a mesma ferramenta sem a parte barrada não conta.
                 Cada contorno é identificado pelo id da chamada na transcrição (a reincidência é avisada de novo).
Cada violação nova vai para `.forge/run/violacoes.jsonl`; havendo alguma, a saída é só
`{"systemMessage": "Forge: <n> violação(ões) - ..."}` com código 0 (nunca `additionalContext`: ADR 0003).
Sem violação não escreve nada. Erro interno: sai 0 e registra em `erros.log`. Só biblioteca padrão.
"""
import hashlib
import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

from _comum import (LIMITE_LOG, PLUGIN, copia_de_trabalho, executar, git, gravar_json, ler_json, marcar_projeto,
                    motivo_da_falha, raiz_declarada, versao_sumiu)

LIMITE_ARQUIVO = 2 * 1024 * 1024
LIMITE_ARQUIVOS = 3000
LIMITE_IDS = 300
DIA = 24 * 3600
LIMITE_BLOQUEIOS = 30
# Mudados pelo próprio Claude Code com o usuário (aprovações, worktrees): não são violação.
IGNORADOS = {".claude/settings.local.json", ".claude/worktrees", ".claude/scheduled_tasks.lock"}
_MARCA = re.compile(r"\b(R-[A-Z][A-Z0-9-]*):")  # formato das mensagens de bloqueio dos hooks do Forge
REGRAS_DE_CONTORNO = {"R-CONFORMIDADE", "R-MAIN"}  # só nelas o próprio alvo é proibido ao papel; nas demais corrigir é o certo
SUBCOMANDOS_DE_ESCRITA = {"push", "merge", "rebase", "cherry-pick", "reset", "commit", "create"}
_ESCRITA = re.compile(r"(?<![\w.-])(?:tee|cp|mv|install|ln|rm|touch|dd|truncate|sed\s+-\S*i|perl|python3?|ruby|node|"
                      r"sh|bash|zsh|eval|source)(?![\w.-])|>|<<")
PODADOS = {".git", "node_modules"}  # nunca se desce neles
# Gravidade: só o contorno acusa (violação); arquivo em vigor mudado pode ser o usuário ou o `forge-upgrade` (mudança).
GRAVIDADE = {"contorno": (0, "violação(ões)"), "versao-sumiu": (0, "violação(ões)"), "erro-hook": (1, "aviso(s)"), "em-vigor": (2, "mudança(s)"), "git": (2, "mudança(s)")}
FERRAMENTAS_DE_ARQUIVO = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


# Política ---------------------------------------------------------------------------------------
def em_vigor():
    """Caminhos do projeto sem dono (`quem` vazio) em `hooks/conformidade.json`; os de `~` e `.git/` ficam de fora."""
    politica = ler_json(PLUGIN / "hooks" / "conformidade.json", {})
    caminhos = [c["caminho"] for c in politica.get("caminhos", []) if not c.get("quem")]
    return [c for c in caminhos if not c.startswith(("~", ".git/", ".forge/run"))]


def ignorado(rel):
    return any(rel == i or rel.startswith(i + "/") for i in IGNORADOS) or any(p in PODADOS for p in rel.split("/"))


def arquivos_em_vigor(raiz):
    """Arquivos em vigor existentes, sem descer em pasta ignorada (worktrees, `.git`, `node_modules`) e até o limite."""
    achados = []
    for item in em_vigor():
        alvo = raiz / item
        if alvo.is_file():
            achados.append(alvo)
        elif alvo.is_dir():
            for pasta, subpastas, nomes in os.walk(alvo):
                base = Path(pasta)
                subpastas[:] = sorted(d for d in subpastas if not ignorado((base / d).relative_to(raiz).as_posix()))
                achados += [base / n for n in sorted(nomes)]
                if len(achados) >= LIMITE_ARQUIVOS:
                    return achados
    return achados


def hashes(raiz):
    """{caminho relativo: sha256} dos arquivos em vigor que existem (pastas, recursivamente)."""
    saida = {}
    for arq in arquivos_em_vigor(raiz):
        rel = arq.relative_to(raiz).as_posix()
        if len(saida) >= LIMITE_ARQUIVOS:
            break
        if ignorado(rel) or not arq.is_file() or arq.stat().st_size > LIMITE_ARQUIVO:
            continue
        saida[rel] = hashlib.sha256(arq.read_bytes()).hexdigest()
    return saida


# Transcrição ------------------------------------------------------------------------------------
def linhas_novas(caminho, inicio):
    """(linhas completas depois do deslocamento `inicio`, novo deslocamento); arquivo menor que o deslocamento recomeça."""
    try:
        tamanho = os.path.getsize(caminho)
        with open(caminho, "rb") as f:
            f.seek(inicio if inicio <= tamanho else 0)
            dados = f.read()
    except OSError:
        return [], inicio
    fim = dados.rfind(b"\n") + 1  # só linhas completas: a última pode estar sendo gravada
    base = inicio if inicio <= tamanho else 0
    return dados[:fim].decode("utf-8", "replace").splitlines(), base + fim


def tamanho(caminho):
    try:
        return os.path.getsize(caminho)
    except OSError:
        return 0


def perfil_da_chamada(nome, entrada, raiz):
    """{alvo, sub, verbos} da chamada (ver docstring): `alvo` são os caminhos resolvidos a partir da raiz (e, em git/gh,
    a referência); `sub` é o subcomando de escrita do git/gh (push, merge...); `verbos` são os mecanismos de escrita do
    Bash (redirecionamento, tee, cp, sed -i, python, bash -c, eval...). Sem alvo reconhecível, `alvo` vem vazio."""
    vazio = {"alvo": [], "sub": "", "args": [], "verbos": []}
    if not isinstance(entrada, dict):
        return vazio
    if nome in FERRAMENTAS_DE_ARQUIVO:
        c = entrada.get("file_path") or entrada.get("notebook_path")
        alvo = {os.path.normpath(os.path.join(raiz, c))} if isinstance(c, str) and c else set()
        return {**vazio, "alvo": sorted(alvo)}
    comando = entrada.get("command")
    if nome != "Bash" or not isinstance(comando, str):
        return vazio
    try:
        palavras = shlex.split(comando, comments=False)
    except ValueError:
        palavras = comando.split()
    alvo = {os.path.normpath(os.path.join(raiz, p)) for p in palavras if not p.startswith("-") and ("/" in p or "." in p)}
    alvo.discard(os.path.normpath(raiz))
    sub, args = "", []
    if palavras and palavras[0] in ("git", "gh"):
        resto = [p for p in palavras[1:] if not p.startswith("-")]
        sub = next((p for p in resto if p in SUBCOMANDOS_DE_ESCRITA), "")
        args = resto[resto.index(sub) + 1:] if sub else []
        if len(resto) > 1:
            alvo.add(resto[-1].split(":")[-1])  # `HEAD:main` e `main` têm o mesmo alvo
    return {"alvo": sorted(alvo), "sub": sub, "args": args, "verbos": sorted({m.group(0) for m in _ESCRITA.finditer(comando)})}


def eh_contorno(nova, bloqueio):
    """A nova chamada, aceita, refaz o que `bloqueio` barrou por OUTRO caminho (ADR 0009, seção 8)? Repetir a mesma
    ferramenta sem a parte barrada (`git push` sem `--no-verify`) é a correção esperada, não contorno."""
    if not set(nova["alvo"]) & set(bloqueio["alvo"]):
        return False
    if nova["nome"] != bloqueio["nome"]:  # outra ferramenta: Write barrado e Bash que escreve no mesmo caminho
        return nova["nome"] in FERRAMENTAS_DE_ARQUIVO or bool(nova["verbos"])
    if nova["nome"] != "Bash":
        return False
    if bloqueio["regra"] == "R-MAIN" and nova["sub"] and nova["sub"] == bloqueio["sub"]:
        # o mesmo push/merge na integração passou: o bloqueio foi contornado, não corrigido. Só o push tem a `main` como
        # destino pelo comando (`HEAD:main`); merge, rebase e `gh pr merge` precisam repetir os mesmos argumentos, senão
        # `git merge main` (trazer a main para a branch de trabalho) seria acusado depois de `git merge x main` barrado.
        return nova["sub"] == "push" or nova["args"] == bloqueio.get("args")
    return bool(nova["verbos"]) and nova["verbos"] != bloqueio["verbos"]  # outro mecanismo de escrita (script, tee...)


def texto_do_resultado(bloco):
    conteudo = bloco.get("content")
    if isinstance(conteudo, list):
        conteudo = " ".join(x.get("text", "") for x in conteudo if isinstance(x, dict))
    return conteudo if isinstance(conteudo, str) else ""


def regra_do_bloqueio(bloco):
    """ID da regra (`R-MAIN`...) se a chamada foi barrada por hook (resultado com erro e a marca da regra); senão None."""
    if not bloco.get("is_error"):
        return None
    achou = _MARCA.search(texto_do_resultado(bloco))
    return achou.group(1) if achou else None


def contornos(linhas, estado, raiz, sessao, agora, expira):
    """Varre a transcrição; `estado["bloqueios"]` guarda os bloqueios da sessão (expiram em `expira` s e não valem em
    outra sessão). Devolve [(id da chamada, texto)] das chamadas que contornam um bloqueio."""
    achados, usos = [], {}
    bloqueios = estado["bloqueios"] = [b for b in estado["bloqueios"] if isinstance(b, dict) and agora - b.get("em", 0) < expira]
    for linha in linhas:
        try:
            registro = json.loads(linha)
        except ValueError:
            continue
        mensagem = registro.get("message") if isinstance(registro, dict) else None
        blocos = mensagem.get("content") if isinstance(mensagem, dict) else None
        for bloco in blocos if isinstance(blocos, list) else []:
            if not isinstance(bloco, dict):
                continue
            if bloco.get("type") == "tool_use":
                usos[bloco.get("id")] = {"nome": bloco.get("name"), **perfil_da_chamada(bloco.get("name"), bloco.get("input"), raiz)}
            elif bloco.get("type") == "tool_result" and bloco.get("tool_use_id") in usos:
                uso = usos[bloco["tool_use_id"]]
                if not uso["alvo"]:
                    continue
                regra = regra_do_bloqueio(bloco)
                if regra:
                    if regra in REGRAS_DE_CONTORNO:
                        bloqueios.append({**uso, "regra": regra, "sessao": sessao, "em": agora})
                        del bloqueios[:-LIMITE_BLOQUEIOS]
                    continue
                for b in bloqueios:
                    if b.get("sessao") == sessao and eh_contorno(uso, b):
                        comum = sorted(set(uso["alvo"]) & set(b["alvo"]))[0]
                        achados.append((bloco["tool_use_id"], f"{uso['nome']} em {(os.path.relpath(comum, raiz) if os.path.isabs(comum) else comum)} depois de {b['nome']} barrado no mesmo alvo"))
                        break
    return achados


# Estado e coleta --------------------------------------------------------------------------------
def carregar(hook):
    estado = ler_json(hook.run() / "vigia.json", {})
    estado = estado if isinstance(estado, dict) else {}
    for chave in ("raizes", "transcricoes", "git"):
        if not isinstance(estado.get(chave), dict):
            estado[chave] = {}
    for chave in ("contornos", "bloqueios"):
        if not isinstance(estado.get(chave), list):
            estado[chave] = []
    estado.pop("vistos", None)  # versão anterior: deduplicava pelo texto e escondia a reincidência
    return estado


def podar(estado, agora, expira):
    """Estado sem crescimento: raízes e transcrições que sumiram (ou passaram de um dia) e bloqueios vencidos saem."""
    estado["raizes"] = {r: h for r, h in estado["raizes"].items() if os.path.isdir(r)}
    estado["git"] = {r: g for r, g in estado["git"].items() if r in estado["raizes"]}
    estado["transcricoes"] = {t: o for t, o in estado["transcricoes"].items()
                              if os.path.isfile(t) and agora - os.path.getmtime(t) < DIA}
    estado["bloqueios"] = [b for b in estado["bloqueios"] if isinstance(b, dict) and agora - b.get("em", 0) < expira]


def rotacionar(arquivo):
    """Como o `erros.log`: passou do limite, vira `.1` (substituindo o anterior)."""
    try:
        if os.path.getsize(arquivo) > LIMITE_LOG:
            os.replace(arquivo, str(arquivo) + ".1")
    except OSError:
        pass


def iniciar(hook, raiz):
    """Ponto de partida. Em `resume`/`compact`/`clear` (ou raiz já conhecida) a base e o deslocamento NÃO são
    reiniciados: a compactação automática acontece no meio do trabalho e apagaria o que mudou antes dela."""
    with hook.trava():
        estado = carregar(hook)
        podar(estado, time.time(), hook.expira_s())
        continuacao = hook.campo("source") in ("resume", "compact", "clear")
        if not (continuacao and str(raiz) in estado["raizes"]):
            estado["raizes"][str(raiz)] = hashes(raiz)
        caminho = hook.campo("transcript_path")
        if isinstance(caminho, str) and caminho and not (continuacao and caminho in estado["transcricoes"]):
            estado["transcricoes"][caminho] = tamanho(caminho)
        if not (continuacao and "erros" in estado):
            estado["erros"] = tamanho(hook.run() / "erros.log")
        gravar_json(hook.run() / "vigia.json", estado)


def violacoes_de_erros(hook, estado):
    novas, estado["erros"] = linhas_novas(hook.run() / "erros.log", estado.get("erros", 0))
    return [("erro-hook", linha[:150]) for linha in novas
            if len(linha.split(" ", 2)) > 1 and linha.split(" ", 2)[1] != "vigia"]


def caminho_da_linha(linha):
    """'M  caminho', '?? "caminho"' ou 'R  a -> b' do `git status --porcelain` -> 'caminho' ('b')."""
    caminho = linha.strip().split(None, 1)[-1]
    return caminho.split(" -> ")[-1].strip('"')  # renomeação: 'R  antigo -> novo' vale o novo


def violacoes_de_git(hook, raiz):
    paths = [p for p in em_vigor() if not ignorado(p.rstrip("/"))]
    codigo, saida = git(raiz, "status", "--porcelain", "--", *paths)
    if codigo:
        return []
    return [("git", linha.strip()) for linha in saida.splitlines() if not ignorado(caminho_da_linha(linha))]


def verificar(hook, raiz):
    with hook.trava():
        estado = carregar(hook)
        podar(estado, time.time(), hook.expira_s())
        achados, com_hash = [], set()
        antes = estado["raizes"].get(str(raiz))
        agora = hashes(raiz)
        if antes is not None:
            for rel in sorted(set(antes) | set(agora)):
                if antes.get(rel) != agora.get(rel):
                    com_hash.add(rel)
                    achados.append(("em-vigor", f"{rel} {'criado' if rel not in antes else 'apagado' if rel not in agora else 'alterado'}"))
        estado["raizes"][str(raiz)] = agora
        sujos = violacoes_de_git(hook, raiz)
        antes_git = set(estado["git"].get(str(raiz)) or [])  # o git status é estado, não evento: só a linha nova é dita
        estado["git"][str(raiz)] = [d for t, d in sujos][:LIMITE_BLOQUEIOS]
        achados += [(t, d) for t, d in sujos if d not in antes_git and caminho_da_linha(d) not in com_hash]
        achados += violacoes_de_erros(hook, estado)
        for chave in ("transcript_path", "agent_transcript_path"):
            caminho = hook.campo(chave)
            if not isinstance(caminho, str) or not caminho:
                continue
            inicio = estado["transcricoes"].get(caminho, 0 if chave == "agent_transcript_path" else tamanho(caminho))
            linhas, estado["transcricoes"][caminho] = linhas_novas(caminho, inicio)
            for id_, texto in contornos(linhas, estado, raiz, hook.campo("session_id") or "", time.time(), hook.expira_s()):
                if id_ not in estado["contornos"]:  # a identidade é o evento (id da chamada), não o texto
                    estado["contornos"] = (estado["contornos"] + [id_])[-LIMITE_IDS:]
                    achados.append(("contorno", texto))
        novas = achados
        gravar_json(hook.run() / "vigia.json", estado)
        if novas:
            rotacionar(hook.run() / "violacoes.jsonl")
            with open(hook.run() / "violacoes.jsonl", "a", encoding="utf-8") as f:
                for tipo, detalhe in novas:
                    f.write(json.dumps({"hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": hook.campo("hook_event_name"),
                                        "sessao": hook.campo("session_id"), "agente": hook.campo("agent_type"),
                                        "gravidade": GRAVIDADE[tipo][1], "tipo": tipo, "detalhe": detalhe}, ensure_ascii=False) + "\n")
        return novas


def avisar_versao_sumiu(hook):
    """Sessão marcada como projeto sem `.forge/versao`, com a raiz movida ou com o `.git` que não se resolve: os outros
    hooks se calaram, então o vigia é quem avisa. Raiz que sumiu: o estado vai para a pasta corrente, para não recriar
    a raiz antiga."""
    motivo = motivo_da_falha()
    hook.raiz = (copia_de_trabalho(hook.cwd()) or hook.cwd()) if motivo == "raiz" else raiz_declarada()
    detalhe = {"versao": (".forge/versao sumiu desde o início da sessão: os hooks do Forge só barram as ações críticas "
                          "até o arquivo voltar; peça ao usuário que o restaure"),
               "raiz": ("a pasta da sessão foi movida ou apagada: os hooks do Forge só barram as ações críticas; peça "
                        "ao usuário que a restaure e abra uma sessão nova"),
               "git": (".git da raiz da sessão não se resolve e não há .forge/versao: os hooks do Forge só barram as ações "
                       "críticas; peça ao usuário que repare o .git")}[motivo]
    with open(hook.run() / "violacoes.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": hook.campo("hook_event_name"),
                            "sessao": hook.campo("session_id"), "agente": hook.campo("agent_type"),
                            "gravidade": GRAVIDADE["versao-sumiu"][1], "tipo": "versao-sumiu", "detalhe": detalhe},
                           ensure_ascii=False) + "\n")
    return [("versao-sumiu", detalhe)]


def principal(hook):
    evento = hook.campo("hook_event_name")
    if evento == "SessionStart" and raiz_declarada() is not None:
        marcar_projeto(raiz_declarada())
    raiz = hook.projeto(hook.cwd())
    if versao_sumiu() and evento in ("Stop", "SubagentStop"):
        novas = avisar_versao_sumiu(hook)
    elif raiz is None or evento not in ("SessionStart", "Stop", "SubagentStop"):
        return
    elif evento == "SessionStart":
        return iniciar(hook, raiz)
    else:
        novas = verificar(hook, raiz)
    if novas:
        novas = sorted(novas, key=lambda n: GRAVIDADE[n[0]][0])  # o resumo é do mais grave (a ordenação é estável)
        contagem = {}
        for tipo, _ in novas:
            contagem[GRAVIDADE[tipo]] = contagem.get(GRAVIDADE[tipo], 0) + 1
        partes = ", ".join(f"{n} {nome}" for (_, nome), n in sorted(contagem.items()))
        resumo = " ".join(f"{novas[0][0]}: {novas[0][1]}".split())[:120]
        print(json.dumps({"systemMessage": f"Forge: {partes} — {resumo} (.forge/run/violacoes.jsonl)"}, ensure_ascii=False))


if __name__ == "__main__":
    executar("vigia", principal)
