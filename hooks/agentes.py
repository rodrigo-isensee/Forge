#!/usr/bin/env python3
"""Forge: teto de agentes, relançamento duplicado (ADR 0003, R-TETO), brief selado do especialista e forma da mensagem ao conferente (R-BRIEF).

P1 (0.43.1) e D2 (0.44.0): todo disparo (fora o conferente e os tipos só de leitura de `TIPOS_SO_DE_LEITURA`: Explore, Plan,
claude-code-guide, web-fetch, que a conformidade põe no papel só de leitura `leitura`) exige no prompt o caminho de um brief em docs/briefs/ com selo no
`## Histórico` do pedido (`- <data> <hora>: brief selado docs/briefs/<nome>.md <sha256>`, gravado só pelo `forge-check brief selar`)
e com o sha256 de agora; sem isso, bloqueia (falha fechada). O conferente é opcional e segue com a forma e o hash da mensagem.
D3 (0.44.0): com o selo em dia, o hook reconfere os campos calculados do brief (`forge-check`, `brief_vencido`) e, se a base andou
ou as decisões do pedido mudaram, só avisa (`systemMessage` e stderr, código 0); nunca barra por isso.

O teto é adaptativo (nproc, load de 1 min e memória lidos de /proc; fallback 3) e `teto_agentes` em
.forge/config.json o fixa; `teto_maximo` limita o adaptativo.
PreToolUse (Agent/Task): bloqueia qualquer disparo com MemAvailable <= o piso de memória (padrão 2 GB; `piso_memoria_gb` em
.forge/config.json o muda), sem trava por load (R-TETO, decisão do dono R-TETO-DISPONIBILIDADE de 2026-11-06 14:26);
bloqueia também se já há o teto de agentes ativos ou um ativo com o mesmo tipo e descrição;
senão reserva a vaga. `FORGE_CARGA_LIVRE=1` no ambiente do processo (só o dono) pula só a trava de memória
(teto e duplicado seguem; o uso fica no erros.log). SubagentStart confirma a reserva com o agent_id; SubagentStop libera a vaga.
Estado em .forge/run/agentes.json; no clone do Forge e nas worktrees dele (onde `.forge` é um arquivo, não uma pasta),
em <diretório comum do git>/forge/run/agentes.json: protegido pela conformidade só nas sessões de projeto, no Forge sem guarda
de escrita; `hooks_desligados` não vale no clone. Registros expiram (reserva sem início: 5 min; agente: expiracao_horas).
O registro leva o PID da sessão do Claude Code, o namespace de PID e o session_id: com a sessão morta (PID inexistente, no mesmo
namespace) a vaga sai na hora, sem esperar o prazo. Qualquer dúvida (tipo, faixa, namespace, erro) mantém o registro.
AG-1a (E10): a reserva grava em `branches` as `Branch:` do cabeçalho dos briefs citados no prompt.
Z10 (0.43.2, AG-1b): uma delegação de escrita vigente por branch (R-TETO). A reserva grava também em `escrita` as branches dos briefs
de escrita (`Etapa:` fora de review, seguranca e qa; sem `Etapa:`, escrita); a segunda delegação de escrita numa branch que outra
reserva vigente escreve é recusada até o SubagentStop dela (ou o prazo). Só passa o brief que traz no próprio arquivo
`paralelo na mesma branch: <motivo>` (10 caracteres ou mais). Registro antigo, sem `escrita`, ocupa todas as `branches` dele.
AG-1a (E10): a reserva grava em `branches` as `Branch:` do cabeçalho dos briefs citados no prompt (só registro, sem recusa).
RN-6 (0.43.3): cada recusa do R-TETO (memória, teto, duplicado) deixa uma linha em `recusas.log`, na pasta do estado
(`registrar_recusa`, que o hook `pesado` também pode chamar); o `forge-check metricas` mede por ela a espera por portão.
RITMO (0.45.7, E3): `ritmo` em .forge/config.json (`forge ritmo <valor>`). `econômico` limita o teto a 1 agente por vez;
`equilibrado` (padrão, também para valor ausente ou inválido) e `acelerado` ficam no teto de sempre. Nenhum ritmo afrouxa
o piso de memória, o duplicado nem a trava `pesado` (tarefa pesada segue uma por vez em qualquer ritmo).
TRAVA-AGENTE-MORTO (0.45.7, E23.60; parecer de segurança da E23.46, C1 a C12): o registro da sessão atual sai na hora, sem o
prazo, só com a notificação terminal do próprio Claude Code no transcript da sessão-mãe (`Liberacao`): cabeçalho lido por
regex ancorada (task-id, tool-use-id igual ao `toolUseId` do `subagents/agent-<id>.meta.json`, status failed, completed ou
killed, carimbo depois do `desde`), do fim do transcript com teto de bytes e de tempo. Não há liberação manual, por mtime nem
por silêncio: agente vivo sem resposta para com o TaskStop e sai pela notificação `killed`. O registro de escrita só sai com a
trava `pesado` livre. Cada liberação vai ao `liberacoes.log` e deixa uma lápide: retomar o id (`SendMessage`) é recusado
enquanto houver relançamento vigente na mesma branch ou com a mesma descrição.
"""
import hashlib
import json
import math
import os
import re
import stat
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from _comum import (LIMITE_LOG, RESERVA, Aviso, Hook, bloquear, diretorio_comum, e_clone_do_forge, executar, forge_check,
                    gravar_json, ler_json, mensagem)
from pesado import CASCAS, TRAVA_S, pid_da_sessao, pid_vivo

FERRAMENTAS = {"Agent", "Task"}
RETOMADA = "SendMessage"  # C8: retomar um agente pelo id
EVENTOS = {"PreToolUse", "SubagentStart", "SubagentStop"}
RESERVA_S = 300  # a reserva sem SubagentStart (lançamento negado ou falho) não prende a vaga por horas


GB_KB = 1024 * 1024
PISO_GB_PADRAO = 2.0  # R-TETO-DISPONIBILIDADE (dono, 2026-11-06 14:26): só o piso de memória disponível; o load não trava


def nucleos():
    """nproc: os.sched_getaffinity(0) (respeita afinidade e cpuset) quando existir, senão os.cpu_count();
    FORGE_NPROC o substitui (usado nos testes). None se não der."""
    try:
        if hasattr(os, "sched_getaffinity"):
            padrao = len(os.sched_getaffinity(0))
        else:
            padrao = os.cpu_count() or 0
        return int(os.environ.get("FORGE_NPROC") or padrao or 0) or None
    except (ValueError, OSError):
        return None


def medir(proc=None):
    """(load de 1 min, GB disponíveis, GB totais) lidos de /proc; None onde não der (sem /proc, formato inesperado).
    FORGE_PROC aponta para outra raiz (usado nos testes)."""
    proc = Path(proc or os.environ.get("FORGE_PROC") or "/proc")
    try:
        carga = float((proc / "loadavg").read_text(encoding="utf-8").split()[0])
    except (OSError, ValueError, IndexError):
        carga = None
    memoria = total = None
    try:
        linhas = (proc / "meminfo").read_text(encoding="utf-8").splitlines()
        memoria = int(next(l for l in linhas if l.startswith("MemAvailable:")).split()[1]) / GB_KB
        total = int(next(l for l in linhas if l.startswith("MemTotal:")).split()[1]) / GB_KB
    except (OSError, ValueError, IndexError, StopIteration):
        memoria = total = None
    return carga, memoria, total


def piso_de_memoria(config=None):
    """GB de MemAvailable abaixo (ou igual) dos quais nenhum agente sai: `piso_memoria_gb` de .forge/config.json, número positivo;
    ausente ou inválido (booleano, texto, zero ou negativo), o padrão de 2 GB (R-TETO-DISPONIBILIDADE)."""
    valor = (config or {}).get("piso_memoria_gb")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not valor > 0:
        return PISO_GB_PADRAO
    return float(valor)


def carga_alta(carga, memoria, total, nproc, piso=PISO_GB_PADRAO):
    """R-TETO (R-TETO-DISPONIBILIDADE, 2026-11-06): MemAvailable <= `piso` GB. O load de 1 min e o nproc não travam mais (ficam na
    assinatura para quem já chama). Sem a medida de memória (None), nunca é carga alta."""
    if memoria is None:
        return False
    return memoria <= piso


def teto_adaptativo(carga, memoria, total, nproc):
    """R-TETO: teto absoluto de nproc agentes ao mesmo tempo; a carga alta é outra trava (carga_alta) e
    vale antes dele. Sem medida (None), o padrão de 3, nunca acima de nproc quando ele é conhecido."""
    if None in (carga, memoria, total, nproc):
        padrao = RESERVA["teto_agentes"]
        return min(padrao, nproc) if nproc else padrao
    return nproc


RITMOS = ("econômico", "equilibrado", "acelerado")
RITMO_PADRAO = "equilibrado"
TETO_DO_RITMO = {"econômico": 1}  # E3 (0.45.7): só o econômico muda o teto; o acelerado não passa do teto de sempre (R-TETO)


APELIDOS_DO_RITMO = {"economico": "econômico"}  # sem acento também vale (o `forge ritmo` aceita o mesmo)


def ritmo_valido(valor):
    """O ritmo canônico de `valor` (caixa não conta; `economico` vale `econômico`), ou None."""
    if not isinstance(valor, str):
        return None
    chave = valor.strip().lower()
    chave = APELIDOS_DO_RITMO.get(chave, chave)
    return chave if chave in RITMOS else None


def ritmo_do_projeto(raiz):
    """`ritmo` do .forge/config.json da raiz; ausente, inválido ou ilegível, o padrão `equilibrado` (o teto de antes)."""
    try:
        dados = json.loads((Path(raiz) / ".forge" / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return RITMO_PADRAO
    return (ritmo_valido(dados.get("ritmo")) if isinstance(dados, dict) else None) or RITMO_PADRAO


def calcular_teto(config, proc=None, ritmo=RITMO_PADRAO):
    """(teto, explicação para a mensagem). `teto_agentes` fixo sobrepõe o adaptativo; `teto_maximo` limita
    os dois; o ritmo `econômico` limita tudo a 1 (hook e forge-check usam esta função)."""
    maximo = config.get("teto_maximo")
    if config.get("teto_agentes"):
        teto, origem = config["teto_agentes"], "fixo em .forge/config.json: teto_agentes"
    else:
        carga, memoria, total = medir(proc)
        nproc = nucleos()
        teto = teto_adaptativo(carga, memoria, total, nproc)
        origem = f"adaptativo sem leitura de /proc: padrão {teto}" if None in (carga, memoria, total, nproc) \
            else f"adaptativo: load {carga:.1f} de {nproc} núcleos, {memoria:.1f} GB disponíveis"
    limitado = bool(maximo) and teto > maximo
    if limitado:
        teto = maximo
    origem += f", limitado por teto_maximo {maximo}" if limitado else ""
    if ritmo in TETO_DO_RITMO and teto > TETO_DO_RITMO[ritmo]:
        teto = TETO_DO_RITMO[ritmo]
        origem += f", ritmo {ritmo}: {teto} agente por vez (`forge ritmo equilibrado` muda)"
    return teto, origem


PID_MAX_PADRAO = 4194304  # teto do Linux de 64 bits, quando /proc/sys/kernel/pid_max não pode ser lido


def namespace_de_pid():
    """Identificador do namespace de PID do processo (`pid:[...]`), ou None onde não der (sem /proc, Windows)."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except (OSError, ValueError):
        return None


def pid_max():
    try:
        return int(Path("/proc/sys/kernel/pid_max").read_text(encoding="utf-8").split()[0])
    except (OSError, ValueError, IndexError):
        return PID_MAX_PADRAO


def pid_valido(pid):
    return isinstance(pid, int) and not isinstance(pid, bool) and 1 <= pid <= pid_max()


def sessao_morta(registro):
    """True só com a prova de que a sessão que fez o registro não existe mais: `pid` inteiro na faixa do sistema, o mesmo
    namespace de PID gravado e `os.kill(pid, 0)` com ProcessLookupError. Qualquer outro caso (registro antigo sem pid, tipo
    errado, outro namespace, PermissionError, erro de leitura, Windows) é False: o registro fica e segue o prazo (R-TETO)."""
    try:
        pid, gravado = registro.get("pid"), registro.get("pidns")
        if os.name == "nt" or not pid_valido(pid) or not isinstance(gravado, str) or gravado != namespace_de_pid():
            return False
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except (OSError, OverflowError, ValueError, TypeError, AttributeError):
        return False
    return False


def da_sessao(hook):
    """`pid`, `pidns` e `sessao` do evento atual para o registro; vazio se faltar o session_id, se o PID não estiver vivo
    ou se for uma casca (o hook foi chamado por um intermediário que some logo depois): a vaga fica no prazo."""
    sessao = hook.campo("session_id")
    try:
        pid, ns = pid_da_sessao(), namespace_de_pid()
        comm = Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return {}
    if not (isinstance(sessao, str) and sessao and ns and pid_valido(pid) and pid_vivo(pid) and comm not in CASCAS):
        return {}
    return {"pid": pid, "pidns": ns, "sessao": sessao}


def nenhum_morto(_registro):
    return False


def vigentes(agentes, agora, expira_s, morto=nenhum_morto):
    """Registros dentro do prazo e de sessão que não está provadamente morta. Cada registro é avaliado à parte: o erro
    num deles mantém o registro e nunca derruba o hook (a exceção liberaria o lançamento sem reserva). `morto` (C5,
    `Liberacao`) tira o registro cujo agente a notificação terminal prova parado; o forge-check conta sem ele."""
    saida = []
    for a in agentes:
        try:
            if not (isinstance(a, dict) and isinstance(a.get("desde"), (int, float))
                    and agora - a["desde"] < (expira_s if a.get("id") else min(RESERVA_S, expira_s))):
                continue
            if sessao_morta(a) or morto(a):
                continue
        except Exception:  # noqa: BLE001 - dúvida mantém o registro (falha para o lado seguro)
            pass
        saida.append(a)
    return saida


# TRAVA-AGENTE-MORTO (E23.60): a notificação terminal do Claude Code no transcript da sessão-mãe (C1 a C4, C9).
ID_DE_AGENTE = re.compile(r"a[0-9a-f]{16}")
ID_CITADO = re.compile(r"(?<![0-9A-Za-z])a[0-9a-f]{16}(?![0-9A-Za-z])")
SESSAO_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
# C1: só o cabeçalho, do início; nada depois do status (o `<result>` traz texto do agente).
NOTIFICACAO = re.compile(r"<task-notification>\n<task-id>(a[0-9a-f]{16})</task-id>\n<tool-use-id>(toolu_[0-9A-Za-z]{1,64})"
                         r"</tool-use-id>\n(?:<output-file>[^<>\n]{1,4096}</output-file>\n)?<status>(failed|completed|killed)</status>\n")
CARIMBO = re.compile(r"(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3}(?:\d{3})?)?)Z")
LIMITE_DO_TRANSCRIPT = 2 * 1024 * 1024  # C4: bytes lidos do fim do transcript
PRAZO_DA_LEITURA_S = 2.0  # C4: tempo da leitura; estourou, o registro fica
LIMITE_DO_META = 64 * 1024
LAPIDES_MAX = 64


def ler_o_fim(caminho, limite):
    """C3 e C4: os últimos `limite` bytes do arquivo regular `caminho`, a partir da primeira linha inteira, aberto sem seguir
    link nem esperar FIFO. Outro tipo de arquivo levanta OSError: a dúvida mantém o registro (`vigentes`)."""
    fd = os.open(caminho, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as arquivo:
        info = os.fstat(arquivo.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise OSError(f"{caminho}: não é arquivo regular")
        inicio = max(0, info.st_size - limite)
        arquivo.seek(inicio)
        dados = arquivo.read(limite)
    return dados.partition(b"\n")[2] if inicio else dados


def transcript_da_sessao(hook):
    """C3: o transcript da sessão do evento, real, em `~/.claude/projects/<projeto>/<session_id>.jsonl`; None fora disso. Sai do
    `transcript_path` do evento, nunca de campo do registro."""
    sessao, caminho = hook.campo("session_id"), hook.campo("transcript_path")
    if not (isinstance(sessao, str) and SESSAO_UUID.fullmatch(sessao) and isinstance(caminho, str) and os.path.isabs(caminho)):
        return None
    real = Path(os.path.realpath(caminho))
    base = Path(os.path.realpath(Path.home() / ".claude" / "projects"))
    return real if real.parent.parent == base and real.name == f"{sessao}.jsonl" else None


def notificacao_terminal(entrada):
    """C1: (task-id, tool-use-id, carimbo em segundos, status) da entrada do transcript que é a notificação do próprio Claude
    Code (type user, promptSource system, fora de sidechain); None para o resto. O content que não é texto (o tool_result é
    lista), o cabeçalho ou o carimbo que não casam (None.group) e a entrada fora da forma levantam TypeError, KeyError ou
    AttributeError, que `notificacoes` pula."""
    if not (entrada.get("type") == "user" and entrada.get("promptSource") == "system" and entrada.get("isSidechain") is False):
        return None
    cabecalho, quando = NOTIFICACAO.match(entrada["message"]["content"]), CARIMBO.fullmatch(entrada["timestamp"])
    segundos = datetime.fromisoformat(quando.group(1)).replace(tzinfo=timezone.utc).timestamp()
    return cabecalho.group(1), cabecalho.group(2), segundos, cabecalho.group(3)


def notificacoes(real, prazo):
    """C1 e C4: {task-id: [(tool-use-id, carimbo, status)]} das notificações terminais do fim do transcript. Passou do `prazo`
    (monotônico), levanta TimeoutError: o registro fica."""
    achadas = {}
    for linha in ler_o_fim(real, LIMITE_DO_TRANSCRIPT).split(b"\n"):
        if time.monotonic() > prazo:
            raise TimeoutError("C4: a leitura do transcript passou do prazo")
        if b"<task-notification>" in linha:
            try:
                nota = notificacao_terminal(json.loads(linha))
            except (ValueError, TypeError, KeyError, AttributeError):
                continue
            if nota is not None:
                achadas.setdefault(nota[0], []).append(nota[1:])
    return achadas


def tool_use_do_meta(real, aid):
    """C2: o `toolUseId` de `<sessão>/subagents/agent-<aid>.meta.json`, ao lado do transcript; link no caminho, arquivo ausente
    ou fora da forma levantam (o registro fica)."""
    meta = real.with_suffix("") / "subagents" / f"agent-{aid}.meta.json"
    if os.path.realpath(meta) != str(meta):
        raise OSError(f"{meta}: link no caminho")
    return json.loads(ler_o_fim(meta, LIMITE_DO_META))["toolUseId"]


def pesado_livre(hook, agora):
    """C9: a trava `pesado` da pasta do estado está livre: sem arquivo, ou com dono morto ou vencido (o critério do `pesado`).
    Trava que não é objeto levanta AttributeError (`.get`): o registro fica."""
    trava = ler_json(hook.run() / "pesado.json", {})
    desde = trava.get("desde")
    return not (isinstance(desde, (int, float)) and agora - desde < TRAVA_S and pid_vivo(trava.get("pid"), trava.get("inicio")))


class Liberacao:
    """C5: o `morto` de `vigentes`. Lê o transcript uma vez, só com registro candidato; qualquer dúvida (inclusive exceção,
    que `vigentes` cala) mantém o registro. Os liberados ficam em `soltos` (registro, status), para a lápide (C8) e o log (C11)."""

    def __init__(self, hook, agora):
        self.hook, self.agora, self.soltos = hook, agora, []
        self.prazo = time.monotonic() + PRAZO_DA_LEITURA_S
        self.real = transcript_da_sessao(hook)
        self._notas = None

    @property
    def notas(self):
        """C4: o transcript é lido uma vez só. A falha da leitura (prazo, arquivo sumido) fica guardada como nenhuma nota:
        o primeiro registro cai na exceção, que `vigentes` cala, e os seguintes ficam sem reler o transcript."""
        if self._notas is None:
            self._notas = {}
            self._notas = notificacoes(self.real, self.prazo)
        return self._notas

    def status(self, registro):
        """C2, C3 e C9: o status da notificação que prova o agente parado, ou None."""
        aid, desde = registro.get("id"), registro.get("desde")
        if not (self.real and isinstance(aid, str) and ID_DE_AGENTE.fullmatch(aid)
                and registro.get("sessao") == self.hook.campo("session_id")):
            return None
        depois = [nota for nota in self.notas.get(aid, []) if nota[1] > desde]
        if not depois:
            return None
        uso = tool_use_do_meta(self.real, aid)
        if any(nota[0] != uso for nota in depois):
            return None
        if escritas_do_registro(registro) and not pesado_livre(self.hook, self.agora):
            return None
        return depois[-1][2]

    def __call__(self, registro):
        status = self.status(registro)
        if status:
            self.soltos.append((registro, status))
        return bool(status)


def textos(valor):
    """Os textos de uma lista; o resto fica de fora."""
    return [v for v in valor if isinstance(v, str)] if isinstance(valor, list) else []


def lapide(registro, agora):
    """C8: o que fica do registro liberado: id, hora, descrição e `branches` (que contêm as de escrita), para achar o relançamento."""
    return {"id": registro["id"], "desde": agora, "descricao": registro.get("descricao"),
            "branches": sorted(set(textos(registro.get("branches"))))}


def lapides_vigentes(estado, agora, expira_s):
    """C8: as lápides gravadas, dentro do prazo do registro (expiracao_horas)."""
    lista = estado.get("lapides")
    return [l for l in (lista if isinstance(lista, list) else [])
            if isinstance(l, dict) and isinstance(l.get("desde"), (int, float)) and agora - l["desde"] < expira_s]


def relancado(morto, agentes):
    """C8: há registro vigente, de outro id, com a descrição da lápide `morto` ou numa branch dela."""
    ramos = set(textos(morto.get("branches")))
    return any(a.get("id") != morto.get("id") and ((morto.get("descricao") and a.get("descricao") == morto["descricao"])
                                                  or ramos & set(textos(a.get("branches"))))
               for a in agentes)


def recusar_retomada(hook, agentes, lapides):
    """C8: recusa retomar (SendMessage) o id liberado enquanto houver relançamento dele. Vale qualquer id citado em qualquer
    campo da entrada; erro recusa (falha fechada)."""
    try:
        citados = set(ID_CITADO.findall(json.dumps(hook.campo("tool_input"))))
        presos = [l["id"] for l in lapides if l.get("id") in citados and relancado(l, agentes)]
    except Exception as erro:  # noqa: BLE001 - C8: sem prova, a retomada não sai
        hook.registrar_erro(erro)
        presos = ["?"]
    if presos:
        bloquear("R-TETO", f"o agente {presos[0]} foi liberado como morto e tem relançamento vigente (mesma branch ou "
                           "descrição); não o retome: espere o relançamento terminar.")


def pasta_de_estado_do_clone(raiz):
    """`<diretório comum>/forge/run/` do clone do Forge (cópia principal ou worktree), ou None sem diretório comum."""
    comum = diretorio_comum(raiz)
    return None if comum is None else comum / "forge" / "run"


def arquivo_de_estado(raiz):
    """Caminho do `agentes.json` da `raiz` (topo de uma cópia de trabalho): num clone do Forge, o do diretório comum do git
    (`pasta_de_estado_do_clone`; None se não houver); num projeto, o `.forge/run/` da cópia principal. Só consulta o disco e o git."""
    raiz = Path(raiz)
    if e_clone_do_forge(raiz):
        pasta = pasta_de_estado_do_clone(raiz)
        return None if pasta is None else pasta / "agentes.json"
    hook = Hook("agentes")
    hook.raiz = raiz
    return hook.copia_principal() / ".forge" / "run" / "agentes.json"


def fixar_estado_do_clone(hook, raiz):
    """No clone do Forge, o `Hook.run()` (`<cópia principal>/.forge/run`) não existe: `.forge` é um arquivo. O estado vai
    para o diretório comum (pasta 0700, com `.gitignore` de `*`), que as worktrees dividem. False sem diretório comum."""
    pasta = pasta_de_estado_do_clone(raiz)
    if pasta is None:
        return False
    hook._run = pasta  # antes do mkdir: se falhar, o erro ainda tenta o erros.log na mesma pasta
    pasta.mkdir(mode=0o700, parents=True, exist_ok=True)
    ignorar = pasta / ".gitignore"
    if not ignorar.exists():
        ignorar.write_text("*\n", encoding="utf-8")
    return True


CONFERENTE = "forge:conferente"
MODO_DA_MENSAGEM = re.compile(r"modo: (brief|entrega)[ \t]*")
ARQUIVO_DA_MENSAGEM = re.compile(r"^Arquivo:[ \t]*.*docs/briefs/\S.*$", re.M)
HASH_DA_MENSAGEM = re.compile(r"^Brief-sha256:[ \t]*[0-9a-f]{64}(?![0-9A-Za-z])", re.M)
LINHA_DE_CABECALHO = re.compile(r"^(modo|Arquivo|Brief-sha256):", re.M)  # B9: qualquer valor conta para "um brief"
# EJ 64 (0.43.3): a `Nota:` da mensagem ao conferente só traz fato; verbo de ordem no início ou opção de linha de comando é instrução.
# B1 do review da 0.43.3: a opção `--` vale na nota que só relata o que já rodou (verbo no passado antes da opção) e não tem, em lugar
# nenhum, verbo de ordem nem de norma; qualquer dúvida segue recusada como no EJ 64 ("o brief vale com --raiz /r" continua barrada).
NOTA_DO_CABECALHO = re.compile(r"^[ \t]*nota[ \t]*:(.*)$", re.I | re.M)
ORDEM_NO_INICIO = re.compile(r"[ \t]*(?:rode|rodar|execute|use|chame|ignore|aceite|aprove|pule|considere)\b", re.I)
OPCAO_NA_NOTA = re.compile(r"(?<![\w-])--[a-z]", re.I)
RELATO_NO_PASSADO = re.compile(r"(?<!\w)(?:rodou|rodei|rodaram|rodamos|usou|usei|usaram|executou|executei|executaram|chamou|chamei|"
                               r"chamaram|saiu|saíram|passou|passaram|falhou|falharam)(?!\w)", re.I)
ORDEM_OU_NORMA = re.compile(r"(?<!\w)(?:rode|rodem|rodar|execute|executar|use|usem|usar|chame|chamar|ignore|ignorar|aceite|aceitar|"
                            r"aprove|aprovar|pule|pular|considere|considerar|confira|conferir|verifique|verificar|compare|comparar|"
                            r"valide|validar|leia|ler|deve|devem|precisa|precisam|vale|valem|basta|tem de|tem que)(?!\w)", re.I)


def nota_com_ordem(cabecalho):
    """EJ 64 e B1: True se alguma linha `Nota:` do cabeçalho dá ordem ao conferente: verbo de ordem no início, ou opção `--` fora de
    um relato no passado (relato = verbo no passado antes da opção e nenhum verbo de ordem ou de norma na linha)."""
    for achado in NOTA_DO_CABECALHO.finditer(cabecalho):
        corpo = achado.group(1)
        if ORDEM_NO_INICIO.match(corpo):
            return True
        opcao = OPCAO_NA_NOTA.search(corpo)
        if opcao and not (RELATO_NO_PASSADO.search(corpo[:opcao.start()]) and not ORDEM_OU_NORMA.search(corpo)):
            return True
    return False


VALOR_DO_HASH = re.compile(r"Brief-sha256:[ \t]*([0-9a-f]{64})(?![0-9A-Za-z])")
ABRE_BLOCO = "<<<BRIEF"
LIMITE_DO_BRIEF = 256 * 1024  # limite técnico: o mesmo do `forge-check brief mensagem`


def mensagem_sem_forma(prompt):
    """R-BRIEF, só a forma: o que falta no cabeçalho da mensagem ao conferente (primeira linha `modo: brief|entrega`, uma linha
    `Arquivo:` em docs/briefs/ e uma `Brief-sha256:` de 64 hex), ou None. Não lê o arquivo nem recalcula o hash. HASH-BRIEF (B9): no
    prompt inteiro, mais de uma linha que comece por `modo:`, `Arquivo:` ou `Brief-sha256:`, qualquer que seja o valor, é falta (um
    brief por mensagem); citação recuada ou entre crases não conta."""
    linhas = str(prompt or "").splitlines()
    faltas = []
    texto = "\n".join(linhas)
    achadas = LINHA_DE_CABECALHO.findall(texto)
    contagens = tuple(achadas.count(chave) for chave in ("modo", "Arquivo", "Brief-sha256"))
    if any(n > 1 for n in contagens):
        faltas.append("um brief por mensagem (mais de uma linha `modo:`, `Arquivo:` ou `Brief-sha256:`)")
    if not (linhas and MODO_DA_MENSAGEM.fullmatch(linhas[0])):
        faltas.append("`modo: brief` ou `modo: entrega` na primeira linha")
    if not ARQUIVO_DA_MENSAGEM.search("\n".join(linhas)):
        faltas.append("uma linha `Arquivo:` com o caminho em docs/briefs/")
    if not HASH_DA_MENSAGEM.search("\n".join(linhas)):
        faltas.append("uma linha `Brief-sha256:` com 64 hex")
    if nota_com_ordem(texto.split("<<<BRIEF", 1)[0]):  # EJ 64: só o cabeçalho; o corpo do brief citado não conta
        faltas.append("a `Nota:` só traz fato, nunca instrução ao conferente (verbo de ordem ou opção `--`)")
    return "; ".join(faltas) or None


def raizes_de_brief(hook):
    """`docs/briefs/` (caminho real) da raiz da sessão e de `~/.forge-contrib`, onde o Jarvis do Forge guarda os briefs."""
    return [Path(os.path.realpath(base)) / "docs" / "briefs" for base in (hook.raiz, Path.home() / ".forge-contrib")]


def ler_brief(hook, caminho):
    """Bytes do brief `caminho` (relativo ao cwd do evento), ou None: fora de `docs/briefs/` (`realpath`, com atalhos e `..`
    resolvidos), não é arquivo regular (FIFO, dispositivo) ou passa de 256 KiB. Confere o tipo antes de abrir, abre sem bloquear
    e confere de novo no descritor; lê no máximo o limite mais 1 byte."""
    real = os.path.realpath(hook.cwd() / caminho)
    if not any(base in Path(real).parents for base in raizes_de_brief(hook)):
        return None
    if not stat.S_ISREG(os.lstat(real).st_mode):
        return None
    descritor = os.open(real, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descritor, "rb") as arquivo:
        if not stat.S_ISREG(os.fstat(arquivo.fileno()).st_mode):
            return None
        dados = arquivo.read(LIMITE_DO_BRIEF + 1)
    return dados if len(dados) <= LIMITE_DO_BRIEF else None


def hash_do_brief_diverge(hook, prompt):
    """R-BRIEF, o hash: por que a mensagem ao conferente não bate com o arquivo, ou None. Só o CABEÇALHO (antes da primeira
    linha `<<<BRIEF`) vale: exatamente uma `Arquivo:` e uma `Brief-sha256:`; `Arquivo:` e `Brief-sha256:` no corpo e nos
    blocos seguintes não contam (o Jarvis manda um brief só). Erro ao ler o arquivo bloqueia, só nesta mensagem."""
    cabecalho = []
    for linha in str(prompt or "").splitlines():
        if linha.startswith(ABRE_BLOCO):
            break
        cabecalho.append(linha)
    arquivos = [l[len("Arquivo:"):].strip() for l in cabecalho if l.startswith("Arquivo:")]
    hashes = [l for l in cabecalho if l.startswith("Brief-sha256:")]
    if len(arquivos) != 1 or len(hashes) != 1 or not VALOR_DO_HASH.match(hashes[0]):
        return "o cabeçalho precisa de uma só linha `Arquivo:` e uma só `Brief-sha256:`"
    try:
        dados = ler_brief(hook, arquivos[0])
    except (OSError, ValueError, RuntimeError):  # RuntimeError: sem HOME para achar ~/.forge-contrib
        dados = None
    if dados is None:
        return "o brief não está em docs/briefs/, não é arquivo regular, passa de 256 KiB ou não abriu"
    if hashlib.sha256(dados).hexdigest() != VALOR_DO_HASH.match(hashes[0]).group(1):
        return "o hash do brief não bate com o arquivo"
    return None


CAMINHO_DE_BRIEF = re.compile(r"docs/briefs/[^\s`'\"]+?\.md\b")
SEPARADOR_DE_TOKEN = re.compile(r"[\s`'\"]+")
MAIOR_TOKEN = 4096  # A1 da segurança g2: token maior fica fora da busca, que é quadrática nele (base64, JSON compacto)
MAXIMO_DE_BRIEFS = 4  # AG-1/C-2: acima disso, aviso e a regra fica sem efeito no lançamento
SEM_BRANCH = ("nenhuma", "\u2014")


def caminhos_de_brief(prompt):
    """Os caminhos de docs/briefs/*.md do prompt, token a token, com o prefixo do token (`~/`, absoluto); sem o prefixo
    na expressão, a busca é linear no token, e o token de mais de MAIOR_TOKEN caracteres é pulado."""
    for token in SEPARADOR_DE_TOKEN.split(prompt):
        if len(token) > MAIOR_TOKEN:
            continue
        inicio = 0
        while achado := CAMINHO_DE_BRIEF.search(token, inicio):
            yield token[inicio:achado.end()]
            inicio = achado.end()


EXCECAO_DE_BRANCH = re.compile(r"^(?:[-*] )?paralelo na mesma branch:(.*)$", re.M)
MOTIVO_MINIMO = 10  # AG-1/C-3: caracteres do motivo depois de sem_controle
CONTROLES = {"Cc", "Cf", "Zl", "Zp"}
CORTE_DO_NOME = 80
ETAPAS_DE_PARECER = ("review", "seguranca", "qa")  # Z10: o parecer não escreve a branch; o resto (e a falta de `Etapa:`) escreve


def sem_controle(texto):
    """O critério do `sem_controle` do forge-check: Cc, Cf, Zl e Zp viram um espaço só por sequência (a mensagem não forja linha)."""
    saida, anterior = [], False
    for c in str(texto):
        controle = unicodedata.category(c) in CONTROLES
        if not (controle and anterior):
            saida.append(" " if controle else c)
        anterior = controle
    return "".join(saida).strip()


def tem_excecao(texto):
    """AG-1b (AG-1/C-3): o texto do brief traz `paralelo na mesma branch: <motivo>` com motivo de 10 caracteres ou mais."""
    return any(len(sem_controle(motivo)) >= MOTIVO_MINIMO for motivo in EXCECAO_DE_BRANCH.findall(texto))


def de_escrita(fc, cabecalho):
    """Z10: o brief é de escrita na branch? `Etapa:` do cabeçalho fora de ETAPAS_DE_PARECER, ou ausente (na dúvida, escreve)."""
    etapa = re.search(fc.ETAPA_DO_CABECALHO, cabecalho, re.M)
    return not (etapa and etapa.group(1) in ETAPAS_DE_PARECER)


def branches_dos_briefs(hook, prompt, escrita=None, a_conferir=None):
    """AG-1a (E10): as `Branch:` do cabeçalho de cada brief em docs/briefs/ citado no prompt, sem `nenhuma` e `—`, em ordem.
    Brief ausente ou recusado pela `ler_brief` fica fora; outro erro sobe (quem chama registra e grava a lista vazia).
    Z10: a branch de brief de escrita (`de_escrita`) entra também em `escrita` e, sem a exceção no próprio arquivo, em `a_conferir`."""
    caminhos = list(dict.fromkeys(caminhos_de_brief(str(prompt or ""))))
    if len(caminhos) > MAXIMO_DE_BRIEFS:
        print(f"aviso: {len(caminhos)} briefs citados (máximo {MAXIMO_DE_BRIEFS}); a reserva não grava branch.", file=sys.stderr)
        hook.registrar_erro(Aviso(f"agentes: {len(caminhos)} briefs citados no prompt; a reserva saiu sem branch"))
        return []
    branches, fc = set(), None
    for caminho in caminhos:
        if caminho.startswith("~/"):
            caminho = str(Path.home() / caminho[2:])
        try:
            dados = ler_brief(hook, caminho)
        except FileNotFoundError:
            continue
        if dados is None:
            continue
        fc = fc or forge_check()  # carregado uma vez, só com brief lido
        texto = dados.decode("utf-8", "replace")
        cabecalho = fc.cabecalho_do_brief(texto)
        achada = re.search(fc.CABECALHO_DE_BRIEF_CAMPOS["Branch"], cabecalho)
        if achada and achada.group(1) not in SEM_BRANCH:
            branches.add(achada.group(1))
            if escrita is not None and de_escrita(fc, cabecalho):
                escrita.add(achada.group(1))
                if a_conferir is not None and not tem_excecao(texto):
                    a_conferir.add(achada.group(1))
    return sorted(branches)


def escritas_do_registro(registro):
    """Z10: as branches que a reserva vigente escreve: `escrita`; no registro sem a chave (anterior à 0.43.2), todas as `branches`."""
    lista = registro.get("escrita", registro.get("branches"))
    return lista if isinstance(lista, list) else []


def recusar_branch_ocupada(hook, agentes, branches):
    """Z10 (AG-1b, R-TETO): bloqueia se outra reserva vigente escreve uma das `branches` (igualdade exata)."""
    for a in agentes:
        ocupadas = escritas_do_registro(a)
        for branch in branches:
            if branch in ocupadas:
                prazo = hook.expira_s() if a.get("id") else min(RESERVA_S, hook.expira_s())
                try:
                    hora = time.strftime("%H:%M", time.localtime(a["desde"] + prazo))
                except (OverflowError, ValueError, OSError, TypeError):  # `desde` absurdo: a recusa sai do mesmo jeito
                    hora = "?"
                tipo = sem_controle(a.get("tipo"))[:CORTE_DO_NOME]
                bloquear("R-TETO", f"{sem_controle(branch)[:CORTE_DO_NOME]} ocupada por {tipo} (uma delegação de escrita por branch): "
                                   f"espere o `SubagentStop` ou a expiração às {hora}",
                         cauda=f"; registro em {sem_controle(hook.run() / 'agentes.json')}")


# BRIEF-EXECUTOR-SEM-PORTAO (0.43.2): os tipos de fora do plugin que escrevem como um especialista (todas as ferramentas); o
# brief deles vale para qualquer papel (`destino_diferente` não compara).
EXECUTORES_GENERICOS = {"general-purpose", "fork", "claude"}
# D2 (decisão do dono de 09/11, M2 do review de segurança da 0.43.1): o selo vale para todo tipo que escreve; só estes, que não têm
# Write nem Edit no repositório (pesquisa, leitura, guia, busca na web, linha de status), e o conferente seguem sem ele.
# Review da 0.44.1 (B1): estes tipos vão ao papel `leitura` de hooks/conformidade.json (só de leitura); o statusline-setup edita
# arquivo e por isso exige o selo.
TIPOS_SO_DE_LEITURA = frozenset({"Explore", "Plan", "claude-code-guide", "web-fetch"})


def exige_selo(tipo):
    """P1 (0.43.1) e D2 (0.44.0): todo disparo sai com brief selado (falha fechada), menos o conferente (opcional, segue com a forma e
    o hash da mensagem, com ou sem o prefixo `forge:`) e os tipos de `TIPOS_SO_DE_LEITURA`. Tipo de outro plugin, o `general-purpose`
    sem brief e o tipo desconhecido pedem o selo: na dúvida, escreve."""
    return tipo not in (CONFERENTE, "conferente") and tipo not in TIPOS_SO_DE_LEITURA


def destino_diferente(fc, tipo, dados):
    """M3 (review de segurança da 0.43.1, 0.43.2): o motivo, se o `Agente destino:` do brief não é o papel disparado; None se é. O
    executor genérico (`EXECUTORES_GENERICOS`) faz o trabalho de qualquer papel e não tem o que comparar."""
    if tipo is None or tipo in EXECUTORES_GENERICOS:
        return None
    texto = dados.decode("utf-8", errors="replace")
    destino = (fc.grupo(r"^\s*Agente destino:\s*(\S+)", fc.cabecalho_do_brief(texto)) or "").lower().removeprefix("forge:")
    if destino != tipo.lower().removeprefix("forge:"):
        return f"o brief é para `{sem_controle(str(destino))[:CORTE_DO_NOME]}`, não para `{sem_controle(tipo)[:CORTE_DO_NOME]}`"
    return None


def selo_ausente(hook, prompt, tipo, lidos):
    """P1 (0.43.1, R-BRIEF): por que o disparo de especialista não pode sair, ou None. O prompt cita ao menos um brief em docs/briefs/
    (até MAXIMO_DE_BRIEFS); cada um citado precisa de selo com o sha256 de agora no `## Histórico` do pedido dele (`selo_do_brief`
    do forge-check, a mesma função que o `brief selar` usa para gravar). Linha `Brief-sha256:` no prompt, se houver, precisa ser o hash
    de um brief citado. Erro na leitura é falta (falha fechada, só nesta mensagem). Cada brief selado entra em `lidos` (citado, real,
    bytes), que o aviso de brief vencido (D3) relê sem abrir o arquivo de novo."""
    texto = str(prompt or "")
    caminhos = list(dict.fromkeys(caminhos_de_brief(texto)))
    if not caminhos:
        return "o prompt não cita o brief (docs/briefs/<pedido>-<papel>-<n>.md)"
    if len(caminhos) > MAXIMO_DE_BRIEFS:
        return f"{len(caminhos)} briefs citados (máximo {MAXIMO_DE_BRIEFS})"
    fc, hashes = forge_check(), set()
    for caminho in caminhos:
        real = str(Path.home() / caminho[2:]) if caminho.startswith("~/") else caminho
        try:
            dados = ler_brief(hook, real)
        except (OSError, ValueError, RuntimeError):
            dados = None
        if dados is None:
            return f"{caminho}: o brief não abriu, não está em docs/briefs/ ou passa de 256 KiB"
        motivo = fc.selo_do_brief(os.path.realpath(hook.cwd() / real), dados) or destino_diferente(fc, tipo, dados)
        if motivo:
            return motivo
        lidos.append((caminho, os.path.realpath(hook.cwd() / real), dados))
        hashes.add(hashlib.sha256(dados).hexdigest())
    citados = set(VALOR_DO_HASH.findall(texto))
    if citados - hashes:
        return "a linha `Brief-sha256:` do prompt não é o hash de um brief citado"
    return None


def avisos_de_brief_vencido(hook, lidos):
    """D3 (0.44.0): para cada brief selado (`lidos`, de `selo_ausente`: caminho citado, caminho real e bytes), as correções que o
    `brief selar` faria hoje (`brief_vencido` do forge-check). Só avisa: qualquer erro registra e devolve [], nunca barra o disparo."""
    try:
        fc = forge_check()
        return [f"{caminho}: {linha}" for caminho, real, dados in lidos for linha in fc.brief_vencido(hook.raiz, real, dados)]
    except Exception as erro:  # noqa: BLE001 - o aviso nunca troca o disparo por recusa
        hook.registrar_erro(erro)
        return []


def avisar_brief_vencido(avisos):
    """D3: uma linha `R-BRIEF: aviso` no stderr e no `systemMessage` (código 0), com o caminho de volta: selar de novo."""
    if avisos:
        texto = mensagem("R-BRIEF", f"aviso: brief vencido depois do selo ({sem_controle('; '.join(avisos))}); o disparo segue. "
                                    "Rode `forge-check brief selar` de novo para o especialista ler a base e as decisões de agora.")
        print(texto, file=sys.stderr)
        print(json.dumps({"systemMessage": texto}, ensure_ascii=False))


MOTIVOS_DA_RECUSA = frozenset({"memoria", "teto", "duplicado", "pesado"})  # conjunto fechado: nunca texto do disparo


def numero_da_recusa(valor, forma):
    """Número finito na `forma` (`%.2f`, `%d`); ausente, texto, bool, NaN ou infinito saem `-` (RN-6)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
        return "-"
    return forma % valor


def anexar_ao_log(hook, nome, linha):
    """Uma linha ASCII em `nome`, na pasta do estado, sem seguir link nem esperar FIFO, girando em `<nome>.1` no limite do
    `erros.log`. Quem chama cala a falha."""
    pasta = hook.run()
    log = pasta / nome
    estado = os.lstat(log) if os.path.lexists(log) else None
    if estado and stat.S_ISREG(estado.st_mode) and estado.st_size > LIMITE_LOG:
        os.replace(log, pasta / f"{nome}.1")
    fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        if stat.S_ISREG(os.fstat(fd).st_mode):
            os.write(fd, linha.encode("ascii"))
    finally:
        os.close(fd)


def registrar_liberacao(hook, aid, status):
    """C11: a liberação vira uma linha em `liberacoes.log`: hora, id, status e motivo, nunca a descrição. Cala a falha."""
    try:
        anexar_ao_log(hook, "liberacoes.log", f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {hook.nome} R-TETO id={aid} "
                                              f"status={status} motivo=notificacao\n")
    except Exception:  # noqa: BLE001 - o log nunca devolve o registro nem barra o hook
        pass


def registrar_recusa(hook, motivo, campos=None):
    """RN-6: a recusa do R-TETO vira uma linha em `recusas.log` da pasta do estado (`hook._run` do clone ou `.forge/run/`):
    hora, hook, regra, números (`mem_gb=`, `nproc=`, `ativos=`) e o motivo de `MOTIVOS_DA_RECUSA`, nunca a descrição nem o
    comando. Abre sem seguir link nem esperar FIFO, gira em `recusas.log.1` no limite do `erros.log` e cala qualquer falha:
    registrar nunca troca a recusa por liberação."""
    try:
        if motivo not in MOTIVOS_DA_RECUSA:
            return
        campos = campos or {}
        numeros = " ".join(f"{chave}={numero_da_recusa(campos.get(chave), forma)}"
                           for chave, forma in (("mem_gb", "%.2f"), ("nproc", "%d"), ("ativos", "%d")))
        anexar_ao_log(hook, "recusas.log", f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {hook.nome} R-TETO {numeros} motivo={motivo}\n")
    except Exception:  # noqa: BLE001 - registrar a recusa nunca a troca por liberação
        pass


def lancar(hook, agentes, agora):
    entrada = hook.campo("tool_input") or {}
    tipo = str(entrada.get("subagent_type") or "general-purpose")
    faltas = mensagem_sem_forma(entrada.get("prompt")) if tipo == CONFERENTE else None
    if faltas:
        bloquear("R-BRIEF", "gere a mensagem ao conferente com `forge-check brief mensagem` e envie-a (cabeçalho, caminho e hash); "
                            f"faltou: {faltas}.")
    divergencia = hash_do_brief_diverge(hook, entrada.get("prompt")) if tipo == CONFERENTE else None
    if divergencia:
        bloquear("R-BRIEF", f"{divergencia}; gere de novo com `forge-check brief mensagem` e envie-a.")
    lidos = []
    if exige_selo(tipo):
        try:
            sem_selo = selo_ausente(hook, entrada.get("prompt"), tipo, lidos)
        except Exception as erro:  # noqa: BLE001 - falha fechada: sem prova do selo, o especialista não sai
            hook.registrar_erro(erro)
            sem_selo = "erro ao conferir o selo (registrado no erros.log)"
        if sem_selo:
            bloquear("R-BRIEF", f"{sem_selo}; sele o brief com `forge-check brief selar --arquivo <brief> --pedido <id>` e cite o "
                                "caminho dele no prompt (o selo vale para o sha256 de agora).")
        vencido = avisos_de_brief_vencido(hook, lidos)
    else:
        vencido = []
    descricao = " ".join(str(entrada.get("description") or "").split())
    for a in agentes:
        if descricao and a.get("tipo") == tipo and a.get("descricao") == descricao:
            registrar_recusa(hook, "duplicado", {"ativos": len(agentes)})
            bloquear("R-TETO", f"já há um agente {tipo} ativo com a descrição \"{descricao[:60]}\"; "
                               "não relance, espere o resultado dele.")
    carga, memoria, total = medir()
    nproc = nucleos()
    for variavel in ("FORGE_NPROC", "FORGE_PROC"):  # substituem a medida real: ficam registrados
        if os.environ.get(variavel):
            hook.registrar_escape(f"{variavel}={os.environ[variavel]} substitui a medida real do teto de agentes")
    piso = piso_de_memoria(hook.config())
    if carga_alta(carga, memoria, total, nproc, piso):  # vale para qualquer teto: teto_agentes e teto_maximo não desligam
        if os.environ.get("FORGE_CARGA_LIVRE") == "1":  # escape só do dono: pula só a trava de memória
            hook.registrar_escape(f"FORGE_CARGA_LIVRE=1 liberou o disparo com memória baixa ({memoria:.1f} GB disponíveis, piso {piso:.1f} GB)")
        else:
            registrar_recusa(hook, "memoria", {"mem_gb": memoria, "nproc": nproc, "ativos": len(agentes)})
            bloquear("R-TETO", f"memória baixa ({memoria:.1f} GB disponíveis; piso {piso:.1f} GB, `piso_memoria_gb` em .forge/config.json): "
                               "nenhum agente novo; espere memória liberar; só o dono: FORGE_CARGA_LIVRE=1.")
    teto, motivo = calcular_teto(hook.config(), ritmo=ritmo_do_projeto(hook.raiz))
    if len(agentes) >= teto:
        registrar_recusa(hook, "teto", {"mem_gb": memoria, "nproc": nproc, "ativos": len(agentes)})
        bloquear("R-TETO", f"{len(agentes)} agentes ativos, teto {teto} ({motivo}); "
                           "espere um terminar antes de lançar outro.")
    escrita, a_conferir = set(), set()
    try:  # AG-1a (G-3): depois do teto e só calcula; o erro registra e a reserva sai com a lista vazia
        branches = branches_dos_briefs(hook, entrada.get("prompt"), escrita, a_conferir) if tipo != CONFERENTE else []
    except Exception as erro:  # noqa: BLE001 - a exceção não pode levar a reserva (o executar liberaria sem ela)
        hook.registrar_erro(erro)
        branches, escrita, a_conferir = [], set(), set()
    recusar_branch_ocupada(hook, agentes, sorted(a_conferir))  # Z10: fora do try, sobre a lista pronta
    agentes.append({"id": None, "tipo": tipo, "descricao": descricao, "desde": agora, "branches": branches,
                    "escrita": sorted(escrita), **da_sessao(hook)})
    avisar_brief_vencido(vencido)


def iniciar(hook, agentes, agora):
    aid, tipo = hook.campo("agent_id"), str(hook.campo("agent_type") or "")
    if not aid or any(a.get("id") == aid for a in agentes):
        return
    dono = da_sessao(hook)
    # Com sessão provada, só a reserva da mesma sessão (ou a antiga, sem sessão) casa: o agente de outra sessão não herda o
    # pid dela. Sem sessão provada, casa como antes, mas o registro perde o pid (abaixo).
    reservas = sorted((a for a in agentes if not a.get("id") and (not dono or not a.get("sessao") or a["sessao"] == dono["sessao"])),
                      key=lambda a: a["desde"])
    # O tipo informado pode vir com ou sem o prefixo do plugin; na dúvida, a reserva mais antiga.
    par = next((a for a in reservas if str(a.get("tipo")) == tipo), None) \
        or next((a for a in reservas if str(a.get("tipo")).split(":")[-1] == tipo.split(":")[-1]), None) \
        or (reservas[0] if reservas else None)
    if par is None:
        agentes.append({"id": aid, "tipo": tipo, "descricao": "", "desde": agora, **dono})
    else:
        par.update(id=aid, desde=agora)
        if not dono:  # sem como provar de que sessão é o evento: o pid da reserva não vale para este agente
            for chave in ("pid", "pidns", "sessao"):
                par.pop(chave, None)


def principal(hook):
    evento, ferramenta = hook.campo("hook_event_name"), hook.campo("tool_name")
    if evento not in EVENTOS or (evento == "PreToolUse" and ferramenta not in FERRAMENTAS | {RETOMADA}):
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)
    if raiz is None or (e_clone_do_forge(raiz) and not fixar_estado_do_clone(hook, raiz)):
        return
    with hook.trava():
        arquivo = hook.run() / "agentes.json"
        agora = time.time()
        estado = ler_json(arquivo, {"agentes": []})
        liberacao = Liberacao(hook, agora)
        agentes = vigentes(estado.get("agentes", []), agora, hook.expira_s(), liberacao)
        lapides = (lapides_vigentes(estado, agora, hook.expira_s()) + [lapide(r, agora) for r, _ in liberacao.soltos])[-LAPIDES_MAX:]
        if liberacao.soltos:  # C5: a liberação se grava antes de qualquer recusa abaixo
            gravar_json(arquivo, {"agentes": agentes, "lapides": lapides})
            for registro, status in liberacao.soltos:
                registrar_liberacao(hook, registro["id"], status)
        if evento == "PreToolUse" and ferramenta == RETOMADA:
            recusar_retomada(hook, agentes, lapides)
        elif evento == "PreToolUse":
            lancar(hook, agentes, agora)
        elif evento == "SubagentStart":
            iniciar(hook, agentes, agora)
        else:
            aid = hook.campo("agent_id")
            agentes = [a for a in agentes if not aid or a.get("id") != aid]
        gravar_json(arquivo, {"agentes": agentes, "lapides": lapides})


if __name__ == "__main__":
    executar("agentes", principal)
