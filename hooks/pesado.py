#!/usr/bin/env python3
"""Forge: tarefa pesada uma de cada vez (ADR 0003, R-TETO).

PreToolUse (Bash): se um comando simples da linha começa com um item de `pesados` (.forge/config.json) e outra
sessão ou agente tem tarefa pesada ativa (trava com PID vivo, com menos de TRAVA_S), bloqueia; senão pega a trava.
Vivo não é o zumbi nem o pid reaproveitado (o início do processo vai na trava); o hook que fica órfão na fila sai dela
(PROCESSO-ORFAO). O comando se lê atrás dos lançadores do `_comum` e por caminho (`/x/bin/forge-mutante`; B4).
PostToolUse, PostToolUseFailure e PermissionDenied (Bash) do mesmo comando soltam a trava.
No clone do Forge (cópia principal e worktrees), que não tem `.forge/config.json`, valem também os PESADOS_DO_FORGE
abaixo: duas suítes completas ao mesmo tempo esgotam a memória (R-TETO); os scripts de PELOS_ARGUMENTOS são
pesados salvo nas formas leves exatas (MAQ-A1b).
Estado em .forge/run/pesado.json.
Orkastery 5 (0.44.2): ocupado, o PreToolUse ESPERA a vez numa fila flock (a mesma ideia do .githooks/pre-push: senha presa
por flock em .forge/run/pesado.fila/, a de processo morto se descarta) até ESPERA_S; a fila anda pela versão da branch (a
versão em curso, a menor, primeiro) e depois pela chegada. Cartão da branch em "Aguardando o dono" recusa na hora. Passado o
teto, bloqueia dizendo a posição na fila.
"""
import fcntl
import os
import re
import subprocess
import time
from pathlib import Path

from _comum import (bloquear, e_clone_do_forge, executar, gravar_json, ler_json, leituras, sem_atribuicoes,
                    separar_lancadores)

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
# MAQ-A1b (C-5): a classe de PELOS_ARGUMENTOS depende dos argumentos; leves só nas formas de `leve_pelos_argumentos`.
PELOS_ARGUMENTOS = ("bin/forge-testes", "./bin/forge-testes", "bin/forge-mutante", "./bin/forge-mutante")
PESADOS_DO_FORGE = ["python3 -m unittest discover", "python -m unittest discover",
                    "python3 scripts/suite-paralela.py", "python scripts/suite-paralela.py",
                    "scripts/suite-paralela.py", "./scripts/suite-paralela.py", ".githooks/pre-push --suite",
                    *PELOS_ARGUMENTOS]


# Orkastery 5: espera na fila em vez de bloquear. O timeout do PreToolUse do pesado em hooks.json fica acima deste teto.
ESPERA_S = 240
PASSO_S = 0.5
SEM_VERSAO = 999999
VERSAO_DA_BRANCH = re.compile(r"(?:^|/)v(\d)(\d{2})(\d{1,2})?(?:\b|-)")


def espera_s():
    """O teto da espera: ESPERA_S, ou FORGE_PESADO_ESPERA_S (0 a ESPERA_S) para os testes."""
    try:
        return max(0, min(ESPERA_S, int(os.environ.get("FORGE_PESADO_ESPERA_S", ESPERA_S))))
    except ValueError:
        return ESPERA_S


def branch_de(pasta):
    return subprocess.run(["git", "-C", str(pasta), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL).stdout.strip()


def prioridade(branch):
    """A versão da branch (`melhoria/v0442` -> 4402, `v0431` -> 4301): a menor é a versão em curso e passa na frente."""
    m = VERSAO_DA_BRANCH.search(branch)
    return int(m.group(1)) * 10000 + int(m.group(2)) * 100 + int(m.group(3) or 0) if m else SEM_VERSAO


def aguardando_o_dono(raiz, branch):
    """O cartão da branch está na seção `## Aguardando o dono` do KANBAN.md (a branch citada lá)."""
    try:
        texto = (Path(raiz) / "KANBAN.md").read_text(encoding="utf-8")
    except (OSError, ValueError):
        return False
    achada = re.search(r"^## Aguardando o dono\s*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    secao = achada.group(1) if achada else ""
    return bool(branch) and re.search(r"(?<![\w/.-])" + re.escape(branch) + r"(?![\w/.-])", secao) is not None


def entrar_na_fila(pasta, prio):
    """Cria e prende (flock) a senha `<prioridade>-<ns>-<pid>`; devolve (caminho, arquivo aberto)."""
    pasta.mkdir(mode=0o700, exist_ok=True)
    caminho = pasta / f"{prio:06d}-{time.time_ns()}-{os.getpid()}"
    f = open(caminho, "w", encoding="utf-8")  # noqa: SIM115 - fica aberto (e preso) enquanto espera
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return caminho, f


def fila_viva(pasta):
    """As senhas vivas, em ordem (prioridade, chegada); a de processo morto (flock livre) sai."""
    vivas = []
    for c in sorted(pasta.glob("[0-9]*")):
        if c.is_symlink():
            continue
        try:
            with open(c, encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            c.unlink(missing_ok=True)
        except BlockingIOError:
            vivas.append(c)
        except OSError:
            continue
    return vivas


def ocupada(hook, trava, uso, agora):
    return isinstance(trava, dict) and trava.get("tool_use_id") != uso and not mesma_sessao(hook, trava) \
        and pid_vivo(trava.get("pid"), trava.get("inicio")) and isinstance(trava.get("desde"), (int, float)) \
        and agora - trava["desde"] < min(hook.expira_s(), TRAVA_S)


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


def processo(pid):
    """(estado, início em tiques desde o boot) do `/proc/<pid>/stat`, ou None se ele não se lê ou se o `/proc` é de outro
    namespace de pid (o do sandbox do Bash: lá o `/proc/<pid>` é de outro processo)."""
    try:
        if int(Path("/proc/self/stat").read_text(encoding="utf-8").split(" ", 1)[0]) != os.getpid():
            return None
        campos = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rsplit(")", 1)[1].split()
        return campos[0], int(campos[19])
    except (OSError, ValueError, IndexError):
        return None


def inicio_de(pid):
    return (processo(pid) or (None, None))[1]


def gravar_a_vez(hook, arquivo, dono, inicio, comando, agora, uso):
    gravar_json(arquivo, {"pid": dono, "inicio": inicio, "agente": hook.campo("agent_id"),
                          "comando": " ".join(comando.split())[:120], "desde": agora, "tool_use_id": uso})


def pid_vivo(pid, inicio=None):
    """PROCESSO-ORFAO (v046): morto também o zumbi (`Z`, `X`, que o `kill -0` ainda acha) e o pid reaproveitado por outro
    processo depois que a sessão dona acabou (o início gravado na trava difere do atual). Sem `/proc`, como antes."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        pass
    lido = processo(pid)
    if lido and lido[0] in ("Z", "X"):
        return False
    return not (lido and isinstance(inicio, int) and lido[1] != inicio)


def inicios(palavras):
    """Textos normalizados do comando simples a partir de cada ponto onde a ferramenta pode começar. B4 (v046): antes,
    os lançadores da tabela do `_comum` com as opções deles (`timeout -s KILL 60`, `nice -n 10`, `env -i -u X`), em cada
    leitura possível, somadas à leitura antiga (o padrão do projeto que começa por lançador, `nice make test`, segue
    pesado); a leitura que o `_comum` recusa (`LancadorDemais`, texto do `env -S` aberto) fica só com a antiga."""
    try:
        simples = [palavras] + [comando for comando, _ in separar_lancadores(palavras)]
    except ValueError:
        simples = [palavras]
    return [texto for comando in simples for texto in inicios_sem_lancador(comando)]


def inicios_sem_lancador(palavras):
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


def pede_opcao(argumento, opcao):
    """O argparse lê `argumento` como `opcao`: inteira, um prefixo dela (`--comp`) ou na forma `=` (`--verm=x`)."""
    nome = argumento.split("=", 1)[0]
    return len(nome) > 2 and opcao.startswith(nome)


def leve_pelos_argumentos(inicio, padrao):
    """O teste dirigido (os dois primeiros de PELOS_ARGUMENTOS) sem `--completa` nem `--vermelho` em posição nenhuma; o
    mutante só com `--listar` sozinho."""
    _, *argumentos = inicio.split()
    if padrao in PELOS_ARGUMENTOS[:2]:
        return not any(pede_opcao(a, o) for a in argumentos for o in ("--completa", "--vermelho"))
    return argumentos == ["--listar"]


def palavra_casa(palavra, molde):
    """B4 (v046): a palavra é a do padrão ou termina nela depois de uma pasta (`/x/bin/forge-mutante`, `./.githooks/…`)."""
    molde = molde.removeprefix("./")
    return palavra == molde or palavra.endswith("/" + molde)


def comeca_com(inicio, padrao):
    palavras, moldes = inicio.split(), padrao.split()
    return len(palavras) >= len(moldes) and all(map(palavra_casa, palavras, moldes))


def casa(inicio, padrao):
    if padrao in PELOS_ARGUMENTOS:
        return comeca_com(inicio, padrao) and not leve_pelos_argumentos(inicio, padrao)
    return comeca_com(inicio, padrao)


def pesado(comando, padroes):
    """O comando tem um comando simples que começa com um dos padrões (citar a ferramenta não conta)."""
    texto = normalizar(comando)
    padroes = [normalizar(p) for p in padroes]
    if not any(all(m in texto for m in p.split()) for p in padroes):
        return False  # pré-filtro barato: a maioria dos comandos para aqui
    # ADR 0013, tabela 2.4: pesado se qualquer leitura (a fiel e, se diferir, a da develop) for; se nenhuma fecha,
    # libera, como na develop (a trava de recurso fica aberta na dúvida).
    partes = [inicios(palavras) for leitura in leituras(comando).partes for palavras, _, _ in leitura]
    return any(casa(t, p) for inicio in partes for t in inicio for p in padroes)


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
        if not ocupada(hook, trava, uso, agora) and not fila_viva(hook.run() / "pesado.fila"):
            dono = pid_da_sessao()
            gravar_a_vez(hook, arquivo, dono, inicio_de(dono), comando, agora, uso)
            return
    esperar_a_vez(hook, raiz, arquivo, comando, uso)


def descricao(trava, agora):
    """` há N min (`comando`)` da trava de outra sessão; vazio se ela já não está lá."""
    try:
        return f" há {int((agora - trava['desde']) // 60)} min (`{str(trava.get('comando'))[:40]}`)"
    except (TypeError, KeyError, AttributeError):
        return ""


def esperar_a_vez(hook, raiz, arquivo, comando, uso):
    """Orkastery 5: ocupado, espera na fila até o teto; cartão em "Aguardando o dono" recusa; o teto vencido recusa com a posição."""
    branch = branch_de(hook.cwd())
    if aguardando_o_dono(raiz, branch):
        registrar_a_recusa(hook)
        bloquear("R-TETO", f"o cartão da branch `{branch}` está em \"Aguardando o dono\" no KANBAN.md; tarefa pesada não roda "
                           "enquanto ele não responde (a vez fica com quem pode andar).")
    pasta = hook.run() / "pesado.fila"
    senha, preso = entrar_na_fila(pasta, prioridade(branch))
    dono = pid_da_sessao()
    inicio = inicio_de(dono)  # lidos uma vez: a vez grava o dono já checado, não um pid relido depois da checagem
    try:
        for _ in range(int(espera_s() / PASSO_S) + 1):
            if pid_da_sessao() != dono:  # PROCESSO-ORFAO (v046): a sessão acabou; a senha sai da fila e a vez não é pega
                bloquear("R-TETO", "a sessão que pediu a tarefa pesada acabou; a vez fica com a próxima da fila.")
            with hook.trava():
                trava, agora = ler_json(arquivo, None), time.time()
                vivas = fila_viva(pasta)
                if not ocupada(hook, trava, uso, agora) and vivas[:1] == [senha]:
                    gravar_a_vez(hook, arquivo, dono, inicio, comando, agora, uso)
                    return
            time.sleep(PASSO_S)
        registrar_a_recusa(hook)
        bloquear("R-TETO", f"tarefa pesada de outra sessão ou agente{descricao(trava, agora)}; se travou, apague .forge/run/pesado.json; "
                           f"fila: posição {vivas.index(senha) + 1} de {len(vivas)} após {espera_s()} s (versão em curso na frente).")
    finally:
        preso.close()
        senha.unlink(missing_ok=True)


if __name__ == "__main__":
    executar("pesado", principal)
