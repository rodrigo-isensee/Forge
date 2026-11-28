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
  - `entrada-sem-registro`  só no `Stop` da sessão principal (nunca no `SubagentStop`): mensagem do dono no turno com 3 ou mais
                 itens de lista e nenhuma gravação depois dela em `docs/pedidos/`, `docs/kanban/` nem `KANBAN.md` (aviso, nunca
                 bloqueio). Só conta itens: o texto do dono não vai à saída, ao log (só a contagem e o id da mensagem) nem ao
                 parser do `contorno`.
Medida por papel (AV3, etapa 1; só mede, nada passa a ser recusado): cada comando crítico das chamadas do Bash da transcrição
lida vai para `.forge/run/comandos.jsonl`, uma linha `{hora, sessao, agente, papel, forma, barrado}`. `forma` é o programa e o
subcomando (`git push`, `gh pr merge`, `npm install`) com as flags críticas (`--force`, `--no-verify`, `--all`...), nunca o
comando inteiro; `barrado` é a regra do hook que recusou a chamada, ou null. O papel vem de `conformidade.json` pelo
`agent_type` (a transcrição principal fora do `Stop` é da sessão sem `agent_type`).
Cada violação nova vai para `.forge/run/violacoes.jsonl`; havendo alguma, a saída é só
`{"systemMessage": "Forge: <n> violação(ões) - ..."}` com código 0 (nunca `additionalContext`: ADR 0003; a única
exceção é o `reason` fixo do time parado, abaixo).
Sem violação não escreve nada. Erro interno: sai 0 e registra em `erros.log`. Só biblioteca padrão.
Age no projeto e também na sessão do Forge (clone sem `.forge/versao`, `wt/*`), com o estado no `.forge/run/` da cópia
principal do clone (`Hook.run`), como os outros hooks (CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE).
VIGIA-TIME-PARADO (v0478 E105.1, ordem do dono 22/11; emenda da ADR 0003, item 7): só no `Stop` da sessão do Jarvis
(`agent_type` do papel `jarvis` em `conformidade.json`; a sessão que não se identifica cala), com zero agentes vigentes no
registro do R-TETO (`agentes.json`, lido como o `agentes.py` o lê) e cartão na coluna `Pronto para fazer` do quadro
(`KANBAN.md` da raiz; no clone do Forge, o de `~/.forge-contrib`) sem marca de dependência na Obs. e sem Responsável
`usuário`, a saída leva também `{"decision": "block", "reason": "time parado: ..."}`, texto fixo de uma linha: o Jarvis
retoma sem encerrar a vez. Uma vez por vez: com `stop_hook_active` (o Stop que segue o bloqueio) deixa encerrar. Registro
ou quadro ilegível (link, FIFO, não regular) cala e vai ao erros.log (dúvida não bloqueia).
F4 (v0481 E34.6): com agente rodando ou não, conta também os PRs sem agente da lista em disco `prs-abertos.json` (o
`forge-check` a grava; sem rede no hook) e os agentes presos há mais de 10 min; teto de 280 no `reason` (ADR 0003, item 7).
O aviso de agente terminado chega ao Jarvis como turno, que acaba neste mesmo `Stop`; o `SubagentStop` não bloqueia (prenderia o agente).
"""
import hashlib
import json
import os
import re
import shlex
import stat
import sys
import time
from pathlib import Path

from _comum import (LIMITE_LOG, PLUGIN, contrib, copia_de_trabalho, e_clone_do_forge, executar, git, gravar_json,
                    ler_json, marcar_projeto, motivo_da_falha, raiz_declarada, versao_sumiu)

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
GRAVIDADE = {"contorno": (0, "violação(ões)"), "versao-sumiu": (0, "violação(ões)"), "erro-hook": (1, "aviso(s)"), "em-vigor": (2, "mudança(s)"), "git": (2, "mudança(s)"),
            "entrada-sem-registro": (1, "aviso(s)")}
FERRAMENTAS_DE_ARQUIVO = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
# F10: lista do dono sem registro. O texto do aviso é fixo (nada do que o dono escreveu vai à saída).
TEXTO_SEM_REGISTRO = "a lista do turno não foi gravada em docs/pedidos/"
TEXTOS_FIXOS = {"entrada-sem-registro": TEXTO_SEM_REGISTRO}
MINIMO_ITENS = 3
LIMITE_MENSAGEM = 64 * 1024  # bytes lidos de cada mensagem do dono para a contagem
_ITEM = re.compile(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+\S", re.M)  # sem repetição aninhada: tempo linear
DESTINOS_DO_REGISTRO = ("docs/pedidos/", "docs/kanban/", "KANBAN.md")
# AV3 etapa 1: o que conta como comando crítico (os gerenciadores de pacote vêm de `conformidade.json`).
CRITICOS_GIT = {"push", "merge", "rebase", "cherry-pick", "reset", "commit", "revert", "tag", "config", "worktree"}
GH_COM_ACAO = {"pr", "release", "label", "repo", "workflow", "secret", "ruleset"}  # `gh pr merge`; `gh api` fica só `gh api`
CRITICOS_GH = GH_COM_ACAO | {"api"}
OPCOES_COM_VALOR = {"-C", "-c", "-R", "--repo", "--git-dir", "--work-tree"}
FLAGS_CRITICAS = {"--force", "--force-with-lease", "--no-verify", "--all", "--mirror", "--admin", "--delete"}
_SEPARADORES = re.compile(r"\|\||&&|[;|&\n()`]|\$\(")
_ATRIBUICAO = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


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


def forma_do_trecho(palavras, pacotes):
    """`git push --force`, `gh pr merge`, `npm install`... do comando simples em `palavras`; None se não é crítico."""
    while palavras and (_ATRIBUICAO.match(palavras[0]) or palavras[0] in ("env", "command", "exec", "sudo")):
        palavras = palavras[1:]
    if not palavras:
        return None
    programa, resto, pular = os.path.basename(palavras[0]), [], False
    for p in palavras[1:]:
        if pular or p.startswith("-"):
            pular = not pular and p in OPCOES_COM_VALOR
            continue
        resto.append(p)
    criticos = {"git": CRITICOS_GIT, "gh": CRITICOS_GH}.get(programa)
    if criticos is None:
        verbos = pacotes.get(programa) if isinstance(pacotes.get(programa), dict) else {}
        criticos = set(verbos.get("adicionam", [])) | set(verbos.get("congelados", []))
    if not resto or resto[0] not in criticos:
        return None
    acao = resto[:2] if programa == "gh" and resto[0] in GH_COM_ACAO else resto[:1]
    flags = sorted(FLAGS_CRITICAS.intersection(p.split("=")[0] for p in palavras))
    return " ".join([programa, *acao, *flags])


def formas_criticas(comando, pacotes):
    """As formas críticas de cada comando simples da linha (separada por `;`, `&&`, `||`, `|`, `&`, subshell)."""
    formas = []
    for trecho in _SEPARADORES.split(comando):
        try:
            palavras = shlex.split(trecho)
        except ValueError:
            palavras = trecho.split()
        forma = forma_do_trecho(palavras, pacotes)
        if forma:
            formas.append(forma)
    return formas


def comandos_criticos(linhas, pacotes):
    """[(forma, regra que barrou ou None)] das chamadas do Bash da transcrição, na ordem."""
    usos, barrados = [], {}
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
            entrada = bloco.get("input") if isinstance(bloco.get("input"), dict) else {}
            if bloco.get("type") == "tool_use" and bloco.get("name") == "Bash" and isinstance(entrada.get("command"), str):
                usos += [(bloco.get("id"), f) for f in formas_criticas(entrada["command"], pacotes)]
            elif bloco.get("type") == "tool_result":
                barrados[bloco.get("tool_use_id")] = regra_do_bloqueio(bloco)
    return [(forma, barrados.get(id_)) for id_, forma in usos]


def papel_do_agente(politica, agente):
    """O papel de `conformidade.json` (a mesma regra do hook conformidade): sem tipo, a sessão principal."""
    if not agente:
        return politica.get("sem_agent_type", "")
    return next((p for p, tipos in politica.get("papeis", {}).items() if agente in tipos), politica.get("papel_padrao", ""))


def digitado_pelo_dono(registro):
    """Classificador positivo (FALA-DO-DONO-RESUMO-COMPACTADO): o registro `user` só conta se tem a forma do que o dono
    digita. Fica fora: qualquer marca `is*` verdadeira (isMeta, isSidechain, isCompactSummary,
    isVisibleInTranscriptOnly e as que vierem), resultado de ferramenta e `origin` que não seja `{"kind": "human"}`
    (aviso de tarefa, mensagem de outro agente). Sem `origin` valem as outras condições: é a forma antiga do cliente e
    também a atual da extensão de IDE (grava sem `origin`, com `promptId`), então o padrão não é legado a remover.
    Marca é `is` seguido de maiúscula; um campo como `issueRef` não é marca."""
    if not isinstance(registro, dict) or registro.get("type") != "user":
        return False
    marca = re.compile(r"is[A-Z]")
    if any(marca.match(chave) and valor for chave, valor in registro.items()):
        return False
    if registro.get("toolUseResult") or registro.get("sourceToolUseID") or registro.get("sourceToolAssistantUUID"):
        return False
    origem = registro.get("origin", {"kind": "human"})
    return isinstance(origem, dict) and origem.get("kind") == "human"


def texto_do_dono(registro):
    """Texto digitado pelo dono, ou None. Na dúvida (resumo de compactação, resultado de ferramenta, meta, subagente,
    lembrete de sistema, saída de comando) a entrada não conta."""
    if not digitado_pelo_dono(registro):
        return None
    mensagem = registro.get("message")
    conteudo = mensagem.get("content") if isinstance(mensagem, dict) else None
    if isinstance(conteudo, list):
        if not all(isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str) for b in conteudo):
            return None
        conteudo = "\n".join(b["text"] for b in conteudo)
    if not isinstance(conteudo, str) or conteudo.lstrip().startswith("<"):
        return None
    return conteudo.encode("utf-8")[:LIMITE_MENSAGEM].decode("utf-8", "ignore")


def grava_registro(bloco):
    """A chamada escreve em `docs/pedidos/`, `docs/kanban/` ou `KANBAN.md` (Write, Edit ou Bash de escrita)?"""
    entrada = bloco.get("input") if isinstance(bloco.get("input"), dict) else {}
    if bloco.get("name") in FERRAMENTAS_DE_ARQUIVO:
        alvo = entrada.get("file_path") or entrada.get("notebook_path")
        alvo = alvo.replace("\\", "/") if isinstance(alvo, str) else ""
        return any(d in alvo for d in DESTINOS_DO_REGISTRO)
    comando = entrada.get("command")
    return (bloco.get("name") == "Bash" and isinstance(comando, str) and bool(_ESCRITA.search(comando))
            and any(d in comando for d in DESTINOS_DO_REGISTRO))


def entradas_sem_registro(linhas):
    """[(id da mensagem, itens)] das mensagens do dono com `MINIMO_ITENS` ou mais itens de lista e sem gravação depois
    delas no mesmo trecho da transcrição (o turno). Só conta itens: não devolve texto."""
    pendentes = []
    for linha in linhas:
        try:
            registro = json.loads(linha)
        except ValueError:
            continue
        texto = texto_do_dono(registro)
        if texto is not None:
            itens = len(_ITEM.findall(texto))
            if itens >= MINIMO_ITENS:
                id_ = re.sub(r"[^0-9A-Za-z_-]", "", str(registro.get("uuid") or ""))[:64] or "sem-id"
                pendentes.append((id_, itens))
            continue
        mensagem = registro.get("message") if isinstance(registro, dict) else None
        blocos = mensagem.get("content") if isinstance(mensagem, dict) else None
        if any(isinstance(b, dict) and b.get("type") == "tool_use" and grava_registro(b) for b in (blocos if isinstance(blocos, list) else [])):
            pendentes = []  # o turno gravou: as listas anteriores a esta gravação estão registradas
    return pendentes


# Estado e coleta --------------------------------------------------------------------------------
def carregar(hook):
    estado = ler_json(hook.run() / "vigia.json", {})
    estado = estado if isinstance(estado, dict) else {}
    for chave in ("raizes", "transcricoes", "git", "entradas"):
        if not isinstance(estado.get(chave), dict):
            estado[chave] = {}
    for chave in ("contornos", "bloqueios", "listas"):
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
    estado["entradas"] = {t: o for t, o in estado.get("entradas", {}).items() if t in estado["transcricoes"]}


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
            estado["transcricoes"][caminho] = estado["entradas"][caminho] = tamanho(caminho)
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
        achados, com_hash, medidas = [], set(), []
        politica = ler_json(PLUGIN / "hooks" / "conformidade.json", {})
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
            do_agente = chave == "agent_transcript_path" or hook.campo("hook_event_name") == "Stop"
            agente = hook.campo("agent_type") if do_agente else ""
            medidas += [(agente, forma, regra) for forma, regra in comandos_criticos(linhas, politica.get("pacotes", {}))]
            for id_, texto in contornos(linhas, estado, raiz, hook.campo("session_id") or "", time.time(), hook.expira_s()):
                if id_ not in estado["contornos"]:  # a identidade é o evento (id da chamada), não o texto
                    estado["contornos"] = (estado["contornos"] + [id_])[-LIMITE_IDS:]
                    achados.append(("contorno", texto))
        caminho = hook.campo("transcript_path")
        if hook.campo("hook_event_name") == "Stop" and isinstance(caminho, str) and caminho:
            # deslocamento próprio: o `SubagentStop` avança o do `contorno` na transcrição principal e esconderia a mensagem
            linhas, estado["entradas"][caminho] = linhas_novas(caminho, estado["entradas"].get(caminho, tamanho(caminho)))
            for id_, itens in entradas_sem_registro(linhas):
                if id_ not in estado["listas"]:
                    estado["listas"] = (estado["listas"] + [id_])[-LIMITE_IDS:]
                    achados.append(("entrada-sem-registro", f"{TEXTO_SEM_REGISTRO} (itens={itens}, mensagem={id_})"))
        novas = achados
        gravar_json(hook.run() / "vigia.json", estado)
        if medidas:
            rotacionar(hook.run() / "comandos.jsonl")
            with open(hook.run() / "comandos.jsonl", "a", encoding="utf-8") as f:
                for agente, forma, regra in medidas:
                    f.write(json.dumps({"hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "sessao": hook.campo("session_id"),
                                        "agente": agente, "papel": papel_do_agente(politica, agente), "forma": forma,
                                        "barrado": regra}, ensure_ascii=False) + "\n")
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
    hooks se calaram, então o vigia é quem avisa. Raiz que sumiu: o estado vai para a cópia de trabalho da pasta
    corrente, se houver; sem ela, nada é gravado (o aviso do `Stop` basta), para não recriar a raiz antiga nem criar
    `.forge/run/` numa pasta qualquer."""
    motivo = motivo_da_falha()
    hook.raiz = copia_de_trabalho(hook.cwd()) if motivo == "raiz" else raiz_declarada()
    detalhe = {"versao": (".forge/versao sumiu desde o início da sessão: os hooks do Forge só barram as ações críticas "
                          "até o arquivo voltar; peça ao usuário que o restaure"),
               "raiz": ("a pasta da sessão foi movida ou apagada: os hooks do Forge só barram as ações críticas; peça "
                        "ao usuário que a restaure e abra uma sessão nova"),
               "git": (".git da raiz da sessão não se resolve e não há .forge/versao: os hooks do Forge só barram as ações "
                       "críticas; peça ao usuário que repare o .git")}[motivo]
    if hook.raiz is not None:
        with open(hook.run() / "violacoes.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({"hora": time.strftime("%Y-%m-%dT%H:%M:%S"), "evento": hook.campo("hook_event_name"),
                                "sessao": hook.campo("session_id"), "agente": hook.campo("agent_type"),
                                "gravidade": GRAVIDADE["versao-sumiu"][1], "tipo": "versao-sumiu", "detalhe": detalhe},
                               ensure_ascii=False) + "\n")
    return [("versao-sumiu", detalhe)]


# VIGIA-TIME-PARADO --------------------------------------------------------------------------------
COLUNA_LIVRE = "pronto para fazer"
# Comparadas com a Obs. em minúsculas e com o espaço repetido reduzido a um (`_normal`).
MARCAS_DE_DEPENDENCIA = ("depende de", "espera", "aguardando o dono", "depois do", "decisão do dono", "bloqueado",
                         "pergunta ao dono")
RESPONSAVEL_DONO = "usuário"  # skills/kanban-scrum: Responsável "usuário" quando o cartão depende do dono
LIMITE_QUADRO = 4 * 1024 * 1024  # o quadro do Forge tem ~0,5 MB; acima disso, cala
_ID_DO_CARTAO = re.compile(r"[A-Za-z0-9.-]{1,16}")  # o ID vai ao modelo: lista positiva (emenda da ADR 0003, item 7)


def _normal(texto):
    return " ".join(texto.lower().split())


def sessao_do_jarvis(hook):
    """Só a sessão que se identifica como o Jarvis (`agent_type` do papel `jarvis`); sem `agent_type`, não se sabe: cala."""
    papeis = ler_json(PLUGIN / "hooks" / "conformidade.json", {}).get("papeis", {})
    return hook.campo("agent_type") in papeis.get("jarvis", [])


def quadro_do(raiz):
    """O `KANBAN.md` que vale para a sessão: no clone do Forge, o de `~/.forge-contrib`; no projeto, o da raiz."""
    return contrib() / "KANBAN.md" if e_clone_do_forge(raiz) else Path(raiz) / "KANBAN.md"


def ler_quadro(caminho):
    """Texto do quadro, ou None se não há quadro ou se passa de LIMITE_QUADRO. Abre como `agentes.ler_estado`, sem seguir
    link nem esperar FIFO; o que não é arquivo regular levanta (o chamador cala e registra o erro)."""
    try:
        fd = os.open(caminho, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise OSError(f"{caminho}: não é arquivo regular")
        dados = f.read(LIMITE_QUADRO + 1)
    if len(dados) > LIMITE_QUADRO:
        return None
    return dados.decode("utf-8", errors="replace")


def cartoes_livres(texto):
    """IDs dos cartões da coluna `Pronto para fazer` que não dependem do dono (`depende_do_dono`), na ordem do quadro."""
    livres, na_coluna, responsavel = [], False, None
    for linha in texto.splitlines():
        if linha.startswith("## "):
            na_coluna = linha[3:].strip().lower().startswith(COLUNA_LIVRE)
            continue
        if not na_coluna or not linha.lstrip().startswith("|"):
            continue
        celulas = [c.strip() for c in linha.replace("\\|", "").strip().strip("|").split("|")]
        if celulas[0] == "ID":  # cabeçalho: a posição do Responsável nesta tabela
            nomes = [_normal(c) for c in celulas]
            responsavel = nomes.index("responsável") if "responsável" in nomes else None
            continue
        if len(celulas) < 2 or celulas[0] == "" or set(celulas[0]) <= set("-: "):
            continue
        if depende_do_dono(celulas, responsavel):
            continue
        livres.append(celulas[0])
    return livres


def depende_do_dono(celulas, responsavel):
    """Marca de dependência na Obs. (última coluna) ou Responsável `usuário` (posição achada no cabeçalho)."""
    if any(marca in _normal(celulas[-1]) for marca in MARCAS_DE_DEPENDENCIA):
        return True
    dono = celulas[responsavel] if responsavel is not None and responsavel < len(celulas) else ""
    return _normal(dono) == RESPONSAVEL_DONO


def agentes_rodando(hook, raiz):
    """Registros vigentes do R-TETO (reserva ou agente iniciado), pela mesma leitura do `agentes.py`; ilegível levanta.
    AGENTE-PRESO-SEM-BAIXA (v048 E12.2): sem o agente que a notificação terminal prova parado (`agentes.Liberacao`), que
    não conta como rodando nem como preso; a baixa no arquivo fica com o próximo evento do `agentes.py`."""
    import agentes  # só no Stop: o módulo é grande
    arquivo = agentes.arquivo_de_estado(raiz)
    estado = agentes.ler_estado(arquivo)  # sem diretório comum (None), o TypeError é a dúvida
    leitor = agentes.Hook("agentes")  # a trava `pesado` da Liberacao é a da pasta do agentes.json, não a do vigia
    leitor.entrada, leitor._run, agora = hook.entrada, arquivo.parent, time.time()
    return agentes.vigentes(estado["agentes"], agora, hook.expira_s(), agentes.Liberacao(leitor, agora))


# F4 (v0481 E34.1 e E34.6): PR aberto sem agente e instância presa, sem rede ----------------------------
PRESO_S = 600  # sem escrita no transcript do agente há mais de 10 minutos
NOME_DA_LISTA = "prs-abertos.json"  # gravada por `forge-check status` e `proximo` (bin/forge_estado.py); nenhum hook a escreve
PRAZO_DA_LISTA_S = 900  # 15 min a partir do `gravado_em`; vencida, a parte dos PRs cala
LIMITE_DA_LISTA = 64 * 1024
TETO_DO_AVISO = 280  # emenda da ADR 0003, item 7 (E34.6)
_HEAD = re.compile(r"[A-Za-z0-9._/-]{1,100}")
PAPEIS = {"autor", "integração", "review", "QA", "segurança", "review/QA", "review/segurança", "QA/segurança",
          "review/QA/segurança"}  # o papel vai ao modelo: lista positiva, os valores do `papel_do_pr` de bin/forge_estado.py
_TIPO = re.compile(r"[a-z][a-z0-9:-]{0,39}")  # o tipo do agente vai ao modelo: lista positiva, como o ID do cartão


def lista_de_prs(raiz):
    """O `prs-abertos.json` ao lado do `agentes.json` da raiz (item 5 da ADR 0003), ou None sem diretório de estado."""
    import agentes
    estado = agentes.arquivo_de_estado(raiz)
    return None if estado is None else estado.parent / NOME_DA_LISTA


def ler_prs_abertos(raiz, agora):
    """[(número, head, papel)] da lista em disco, em ordem de número; ausente, vencida, no futuro (mais de 60 s) ou fora da
    forma: []. Cada item passa pela lista positiva; o que não é arquivo regular levanta, pela guarda do `ler_quadro`."""
    caminho = lista_de_prs(raiz)
    texto = None if caminho is None else ler_quadro(caminho)
    dados = json.loads(texto) if texto and len(texto) <= LIMITE_DA_LISTA else {}
    gravado = dados.get("gravado_em") if isinstance(dados, dict) else None
    if type(gravado) is not int or not -60 <= agora - gravado <= PRAZO_DA_LISTA_S:
        return []
    prs = dados.get("prs") if isinstance(dados.get("prs"), list) else []
    return sorted((p["number"], p["head"], p["papel"]) for p in prs[:100] if isinstance(p, dict)
                  and type(p.get("number")) is int and 1 <= p["number"] <= 9999999
                  and isinstance(p.get("head"), str) and _HEAD.fullmatch(p["head"]) and p.get("papel") in PAPEIS)


def prs_parados(hook, raiz, vivos, agora):
    """`#<n> <papel>` de cada PR da lista sem registro vigente na branch dele, com vaga livre no teto do R-TETO."""
    import agentes
    prs = ler_prs_abertos(raiz, agora)
    if not prs or len(vivos) >= agentes.calcular_teto(agentes.ler_config(hook), ritmo=agentes.ritmo_do_projeto(raiz))[0]:
        return []
    ocupadas = {b for a in vivos for b in agentes.textos(a.get("branches")) + agentes.textos(a.get("escrita"))}
    return [f"#{n} {papel}" for n, head, papel in prs if head not in ocupadas]


def ate(nome, itens, quantos):
    """`<nome>: <até `quantos` itens>[ e mais <M>]`, ou nada sem itens."""
    resto = f" e mais {len(itens) - quantos}" if len(itens) > quantos else ""
    return [f"{nome}: {', '.join(itens[:quantos])}{resto}"] if itens else []


def instancias_presas(hook, vivos, agora):
    """`<tipo> <id> há <n> min` de cada agente da sessão cujo transcript não muda há mais de PRESO_S."""
    import agentes
    real = agentes.transcript_da_sessao(hook)
    if real is None:
        return []
    presos = []
    for a in vivos:
        aid = a.get("id")
        if not (isinstance(aid, str) and agentes.ID_DE_AGENTE.fullmatch(aid)):
            continue
        try:
            parado = agora - os.lstat(real.with_suffix("") / "subagents" / f"agent-{aid}.jsonl").st_mtime
        except OSError:
            continue
        if parado > PRESO_S:
            tipo = a["tipo"][:24] if isinstance(a.get("tipo"), str) and _TIPO.fullmatch(a["tipo"]) else "agente"
            presos.append(f"{tipo} {aid} há {int(parado // 60)} min")
    return presos


def calado(hook, funcao, *args):
    """A parte do aviso que falha cala sozinha e vai ao erros.log; as outras seguem."""
    try:
        return funcao(*args)
    except Exception as erro:  # noqa: BLE001 - dúvida não bloqueia
        hook.registrar_erro(erro)
        return []


def aviso_time_parado(hook, raiz):
    """O aviso do time parado para o `Stop`, ou None. Nunca levanta: o erro vai ao erros.log e cala."""
    if hook.campo("hook_event_name") != "Stop":
        return None
    if hook.campo("stop_hook_active") is True:
        return None
    try:
        if not sessao_do_jarvis(hook):
            return None
        vivos = agentes_rodando(hook, raiz)  # só objetos: `agentes.dentro_do_prazo` exige dict
        livres = [] if vivos else cartoes_livres(ler_quadro(quadro_do(raiz)) or "")
    except Exception as erro:  # noqa: BLE001 - nunca falha a sessão; dúvida não bloqueia o encerramento
        hook.registrar_erro(erro)
        return None
    partes = []
    if livres:
        primeiro = f", primeiro {livres[0]}" if _ID_DO_CARTAO.fullmatch(livres[0]) else ""
        partes.append(f"{len(livres)} cartões disponíveis{primeiro}")
    agora = time.time()
    partes += ate("PR sem agente", calado(hook, prs_parados, hook, raiz, vivos, agora), 3)
    partes += ate("preso há mais de 10 min", calado(hook, instancias_presas, hook, vivos, agora), 1)
    while len(partes) > 1 and len(f"time parado: {'; '.join(partes)}; retome sem esperar o dono") > TETO_DO_AVISO:
        partes.pop()  # o teto corta a última parte inteira; o sufixo fixo fica
    if not partes:
        return None
    return f"time parado: {'; '.join(partes)}; retome sem esperar o dono"


def principal(hook):
    evento = hook.campo("hook_event_name")
    if evento == "SessionStart" and raiz_declarada() is not None:
        marcar_projeto(raiz_declarada())
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)  # a sessão do Forge também (CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)
    parado = None
    if versao_sumiu() and evento in ("Stop", "SubagentStop"):
        novas = avisar_versao_sumiu(hook)
    elif raiz is None or evento not in ("SessionStart", "Stop", "SubagentStop"):
        return
    elif evento == "SessionStart":
        return iniciar(hook, raiz)
    else:
        novas = verificar(hook, raiz)
        parado = aviso_time_parado(hook, raiz)
    saida = {}
    if novas:
        novas = sorted(novas, key=lambda n: GRAVIDADE[n[0]][0])  # o resumo é do mais grave (a ordenação é estável)
        contagem = {}
        for tipo, _ in novas:
            contagem[GRAVIDADE[tipo]] = contagem.get(GRAVIDADE[tipo], 0) + 1
        partes = ", ".join(f"{n} {nome}" for (_, nome), n in sorted(contagem.items()))
        resumo = " ".join(f"{novas[0][0]}: {TEXTOS_FIXOS.get(novas[0][0], novas[0][1])}".split())[:120]
        saida["systemMessage"] = f"Forge: {partes} — {resumo} (.forge/run/violacoes.jsonl)"
    if parado:
        saida.update({"decision": "block", "reason": parado})
    if saida:
        print(json.dumps(saida, ensure_ascii=False))


if __name__ == "__main__":
    executar("vigia", principal)
