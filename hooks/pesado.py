#!/usr/bin/env python3
"""Forge: tarefa pesada uma de cada vez (ADR 0003, R-TETO).

PreToolUse (Bash): se um comando simples da linha começa com um item de `pesados` (.forge/config.json) e outra
sessão ou agente tem tarefa pesada ativa (trava com PID vivo, com menos de TRAVA_S), bloqueia; senão pega a trava.
PostToolUse, PostToolUseFailure e PermissionDenied (Bash) do mesmo comando soltam a trava.
No clone do Forge (cópia principal e worktrees), que não tem `.forge/config.json`, valem também os PESADOS_DO_FORGE
abaixo: duas suítes completas ao mesmo tempo esgotam a memória (R-TETO).
Estado em .forge/run/pesado.json.
"""
import os
import re
import time
from pathlib import Path

from _comum import bloquear, e_clone_do_forge, executar, gravar_json, ler_json, leituras, sem_atribuicoes

CASCAS = {"sh", "bash", "dash", "zsh"}
EVENTOS = {"PreToolUse", "PostToolUse", "PostToolUseFailure", "PermissionDenied"}
# Sem o par Post (permissão negada, outro hook bloqueou), a trava não prende as outras sessões por horas.
TRAVA_S = 600
# Palavras que só lançam a ferramenta: `sudo`, `npx playwright`, `pnpm exec playwright`...
LANCADORES = {"sudo", "env", "time", "nice", "nohup", "exec", "command", "npx", "pnpx", "bunx", "uvx"}
GERENCIADORES = {"npm", "pnpm", "yarn", "bun", "uv", "poetry"}
SUBCOMANDOS_DE_LANCE = {"exec", "run", "dlx", "x"}
# A suíte completa do Forge é tarefa pesada (R-TETO): o `.forge/` do clone é protegido e não traz esta lista.
# scripts/suite-paralela.py é a mesma suíte dividida em processos (D4), que o pre-push e o CI chamam.
PESADOS_DO_FORGE = ["python3 -m unittest discover", "python -m unittest discover",
                    "python3 scripts/suite-paralela.py", "python scripts/suite-paralela.py",
                    "scripts/suite-paralela.py", "./scripts/suite-paralela.py", ".githooks/pre-push --suite"]


def pesados_da_raiz(hook, raiz):
    """`pesados` da config do projeto; no clone do Forge, mais os PESADOS_DO_FORGE."""
    lista = list(hook.config()["pesados"])
    return lista + PESADOS_DO_FORGE if e_clone_do_forge(raiz) else lista


def normalizar(texto):
    return " ".join(texto.split()).lower()


def pid_da_sessao():
    """PID do Claude Code que chamou o hook (pula uma casca intermediária, se houver)."""
    pid = os.getppid()
    try:
        if Path(f"/proc/{pid}/comm").read_text(encoding="utf-8").strip() in CASCAS:
            pid = int(Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return pid


def pid_vivo(pid):
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def inicios(palavras):
    """Textos normalizados do comando simples a partir de cada ponto onde a ferramenta pode começar."""
    palavras, saida, i = sem_atribuicoes([p.lower() for p in palavras]), [], 0
    while i < len(palavras):
        saida.append(" ".join(palavras[i:]))
        if palavras[i] in LANCADORES or re.match(r"^[a-z_][a-z0-9_]*=", palavras[i]):
            i += 1
        elif palavras[i] in GERENCIADORES and palavras[i + 1: i + 2] and palavras[i + 1] in SUBCOMANDOS_DE_LANCE:
            i += 2
        else:
            break
    return saida


def pesado(comando, padroes):
    """O comando tem um comando simples que começa com um dos padrões (citar a ferramenta não conta)."""
    texto = normalizar(comando)
    padroes = [normalizar(p) for p in padroes]
    if not any(p in texto for p in padroes):
        return False  # pré-filtro barato: a maioria dos comandos para aqui
    # ADR 0013, tabela 2.4: pesado se qualquer leitura (a fiel e, se diferir, a da develop) for; se nenhuma fecha,
    # libera, como na develop (a trava de recurso fica aberta na dúvida).
    partes = [inicios(palavras) for leitura in leituras(comando).partes for palavras, _, _ in leitura]
    return any(t == p or t.startswith(p + " ") for inicio in partes for t in inicio for p in padroes)


def comando_vivo(padroes):
    """Algum processo da máquina roda um dos `padroes` (MAQ-C1). Só compara e devolve bool: o `cmdline` lido nunca é
    gravado, impresso nem posto em mensagem. Compara a partir do argv[0], do argv[0] sem pasta (`/usr/bin/python3`) e do
    argv[1] (o script do shebang: `python3 ./scripts/suite-paralela.py`). Limites aceitos, que abrem na dúvida como
    hoje: processo de outro namespace de pid, `/proc` ausente ou ilegível e script chamado por caminho absoluto no
    argv[1]. Padrão vazio é ignorado; lê até 4096 bytes por processo e para no primeiro casamento."""
    padroes = [p for p in map(normalizar, padroes) if p]
    if not padroes:
        return False
    try:
        pids = [d for d in os.listdir("/proc") if d.isdigit()]
    except OSError:
        return False
    for pid in pids:
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as arquivo:
                argv = arquivo.read(4096).decode("utf-8", errors="replace").split("\0")
        except OSError:
            continue
        for inicio in (argv, [os.path.basename(argv[0])] + argv[1:], argv[1:]):
            texto = normalizar(" ".join(inicio)) + " "
            if any(texto.startswith(p + " ") for p in padroes):
                return True
    return False


def mesma_sessao(hook, trava):
    """A trava é desta sessão e deste agente: a guarda serve entre sessões, worktrees e agentes."""
    return trava.get("pid") == pid_da_sessao() and trava.get("agente") == hook.campo("agent_id")


def registrar_a_recusa(hook):
    """RN-6: a recusa do R-TETO daqui também vai ao `recusas.log` (motivo `pesado`), pelo `registrar_recusa` do hook `agentes`.
    O import fica aqui dentro (o `agentes` importa este módulo) e nenhuma falha dele troca a recusa por liberação."""
    try:
        from agentes import registrar_recusa
        registrar_recusa(hook, "pesado")
    except Exception:  # noqa: BLE001 - registrar nunca troca a recusa por liberação
        pass


def principal(hook):
    if hook.campo("tool_name") != "Bash":
        return
    comando = hook.campo("tool_input", "command")
    evento = hook.campo("hook_event_name")
    if not isinstance(comando, str) or evento not in EVENTOS:
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)
    if not raiz or not pesado(comando, pesados_da_raiz(hook, raiz)):
        return
    uso = hook.campo("tool_use_id")
    with hook.trava():
        arquivo = hook.run() / "pesado.json"
        trava = ler_json(arquivo, None)
        if evento != "PreToolUse":
            if isinstance(trava, dict) and (not uso or trava.get("tool_use_id") in (uso, None)):
                arquivo.unlink()
            return
        agora = time.time()
        if isinstance(trava, dict) and trava.get("tool_use_id") != uso and not mesma_sessao(hook, trava) \
                and pid_vivo(trava.get("pid")) and isinstance(trava.get("desde"), (int, float)) \
                and agora - trava["desde"] < min(hook.expira_s(), TRAVA_S):
            minutos = int((agora - trava["desde"]) // 60)
            registrar_a_recusa(hook)
            bloquear("R-TETO", f"tarefa pesada de outra sessão ou agente há {minutos} min (`{str(trava.get('comando'))[:40]}`); "
                               "espere ela terminar ou, se travou, apague .forge/run/pesado.json.")
        gravar_json(arquivo, {"pid": pid_da_sessao(), "agente": hook.campo("agent_id"),
                              "comando": " ".join(comando.split())[:120], "desde": agora, "tool_use_id": uso})


if __name__ == "__main__":
    executar("pesado", principal)
