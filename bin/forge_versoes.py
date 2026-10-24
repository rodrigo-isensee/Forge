"""Forge: o que `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor têm em comum (primeiro uso, F5).

Consulta as releases do Forge por `git` (grátis, R-CUSTO), com as mesmas defesas do `forge-check fontes` (docs/fontes-de-praticas.md):
só https, pasta corrente neutra (nunca o projeto), todos os outros protocolos negados, sem pergunta de senha, sem configuração
do git do usuário. Fixa e troca a versão do plugin pelo `claude plugin ...` (marketplace na tag `vX.Y.Z`, sempre no escopo do usuário). Só biblioteca padrão."""
import contextlib
import datetime
import email.utils
import http.client
import ipaddress
import json
import os
import re
import shutil
import signal
import ssl
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LIMITE_CONSULTA = 15  # segundos para o `git ls-remote` e para o `git clone`
MARKETPLACE = "forge"
PLUGIN = "forge@forge"


def versao_de(texto):
    achou = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", str(texto).strip())
    return tuple(int(x) for x in achou.groups()) if achou else None


def versao_do_plugin():
    try:
        return json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("version", "")
    except (OSError, ValueError):
        return ""


def casa():
    return Path(os.environ.get("HOME") or Path.home())


def pasta_de_estado():
    return Path(os.environ.get("XDG_STATE_HOME") or casa() / ".local" / "state") / "forge"


# Endereço e consulta ---------------------------------------------------------------------------
def url_valida(url, permite_local=False):
    """Só `https://host/caminho`, sem usuário nem senha, sem espaço e sem começar com `-`. Local só nos testes."""
    if not isinstance(url, str) or not url or url != url.strip() or re.search(r"\s", url) or url.startswith("-"):
        return False
    if permite_local and url.startswith("/"):
        return True
    achou = re.fullmatch(r"https://([A-Za-z0-9.-]+)(:\d+)?(/[A-Za-z0-9._~/-]*)?", url)
    return bool(achou)


def permite_local():
    return os.environ.get("FORGE_PERMITE_LOCAL") == "1"  # só os testes


def url_do_forge():
    """O endereço do Forge publicado (`repository` do plugin.json), ou None se for inválido ou a consulta estiver desligada."""
    if os.environ.get("FORGE_VERIFICAR_VERSAO") == "0":
        return None
    try:
        padrao = json.loads((RAIZ / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("repository")
    except (OSError, ValueError):
        padrao = None
    url = os.environ.get("FORGE_REPO_URL") or padrao
    return url if url_valida(url, permite_local()) else None


def rodar_git(args, limite=LIMITE_CONSULTA):
    """`git` de rede com as defesas: protocolo só https, cwd vazio e neutro, sem pergunta, sem configuração do usuário."""
    local = permite_local()
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_ALLOW_PROTOCOL="file" if local else "https", GIT_TERMINAL_PROMPT="0",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    protocolos = ["-c", "protocol.allow=never", "-c", "protocol.https.allow=always"]
    if local:
        protocolos += ["-c", "protocol.file.allow=always"]
    neutro = tempfile.mkdtemp(prefix="forge-neutro-")
    env["GIT_CEILING_DIRECTORIES"] = os.path.dirname(neutro)  # nenhum repositório acima da pasta neutra (TMPDIR dentro de um) vale
    try:
        r = subprocess.run(["git", *protocolos, "-c", f"core.hooksPath={os.devnull}", *args], cwd=neutro, env=env,
                           capture_output=True, text=True, timeout=limite)
        return r.returncode, (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return None, ""
    finally:
        shutil.rmtree(neutro, ignore_errors=True)


def ultima_versao(url, limite=LIMITE_CONSULTA):
    """(versão mais nova publicada como tag vX.Y.Z, erro). Sem conexão: (None, motivo); sem nenhuma tag: (None, None)."""
    codigo, saida = rodar_git(["ls-remote", "--tags", "--refs", "--", url, "refs/tags/v*"], limite)
    if codigo != 0:
        return None, "sem conexão com o endereço do Forge"
    achadas = []
    for linha in saida.splitlines():
        _, _, ref = linha.partition("\t")
        versao = versao_de(ref.removeprefix("refs/tags/"))
        if versao and ref.removeprefix("refs/tags/").startswith("v"):
            achadas.append(versao)
    if not achadas:
        return None, None
    return ".".join(str(n) for n in max(achadas)), None


def baixar_tag(url, versao, destino):
    """Cópia rasa da tag v<versao> em `destino` (pasta nova). Devolve True se deu certo."""
    codigo, _ = rodar_git(["clone", "--quiet", "--depth", "1", "--branch", f"v{versao}", "--", url, str(destino)])
    return codigo == 0


def resumo_do_changelog(texto, depois_de, ate):
    """Uma linha por novidade das versões entre `depois_de` (exclusive) e `ate` (inclusive): o título em negrito e a primeira
    frase; marca as que pedem migração."""
    linhas, versao_atual = [], None
    for linha in texto.splitlines():
        cabecalho = re.match(r"## \[(\d+\.\d+\.\d+)\]", linha)
        if cabecalho:
            versao_atual = cabecalho.group(1)
            continue
        if linha.startswith("## "):
            versao_atual = None
        if not (versao_atual and linha.startswith("- ")):
            continue
        if not (versao_de(depois_de) < versao_de(versao_atual) <= versao_de(ate)):
            continue
        corpo = re.sub(r"`", "", linha[2:])
        corpo = re.sub(r"\*\*(.+?)\*\*", r"\1", corpo)
        frase = re.split(r"(?<=[.;])\s", corpo, maxsplit=1)[0]
        if len(frase) > 220:
            frase = frase[:217].rstrip() + "..."
        linhas.append(f"{versao_atual}: {frase}" + (" (precisa atualizar os arquivos do projeto)" if "requer migração" in corpo else ""))
    return linhas


SUPERFICIES = {"projeto": "`forge atualizar`", "forge": "`jarvis-forge --atualizar-vigente` e reinicie a sessão do Forge"}


def comando_de_atualizacao(superficie):
    """O comando que a PESSOA roda para atualizar, conforme a superfície (projeto ou sessão do Forge). Nenhum agente o roda (R-CONFORMIDADE)."""
    return SUPERFICIES[superficie]


def consultar_versao(limite):
    """A consulta às releases, com o resultado distinguível: {"estado", "atual", "ultima"}. `estado`: `desligada` (consulta desligada,
    endereço inválido ou versão local ilegível), `falhou` (sem conexão), `em_dia` ou `defasada` (há tag mais nova que o plugin)."""
    url, atual = url_do_forge(), versao_do_plugin()
    if url is None or versao_de(atual) is None:
        return {"estado": "desligada", "atual": atual, "ultima": ""}
    nova, erro = ultima_versao(url, limite)
    if erro:
        return {"estado": "falhou", "atual": atual, "ultima": ""}
    if nova is None or versao_de(nova) <= versao_de(atual):
        return {"estado": "em_dia", "atual": atual, "ultima": nova or ""}
    return {"estado": "defasada", "atual": atual, "ultima": nova}


def texto_de_versao_nova(atual, nova, superficie="projeto"):
    ponto = " com ponto de retorno" if superficie == "projeto" else ""
    return f"Saiu a versão {nova} do Forge (você usa a {atual}). Para atualizar{ponto}, rode no terminal: {comando_de_atualizacao(superficie)}"


def aviso_de_versao_nova(limite, superficie="projeto"):
    """Uma frase avisando que saiu versão nova do Forge, ou "" (em dia, sem rede, consulta desligada ou endereço inválido)."""
    r = consultar_versao(limite)
    return texto_de_versao_nova(r["atual"], r["ultima"], superficie) if r["estado"] == "defasada" else ""


# Relógio ----------------------------------------------------------------------------------------
LIMIAR_RELOGIO = 300  # segundos: abaixo disso a latência e a resolução de 1 s do `Date` explicam a diferença
TETO_RELOGIO = 30 * 24 * 3600  # acima disso o `Date` não é confiável: "não consegui conferir", não "relógio errado por 30 dias"


def host_publico(url):
    """O host de `https://host[:443]/...` se for nome público (com ponto, último rótulo com letra, nunca IP, `localhost` nem
    porta diferente de 443, sem usuário); senão None. Fecha a sondagem de rede interna por `FORGE_REPO_URL` (CR-2)."""
    achou = re.fullmatch(r"https://([A-Za-z0-9.-]+)(?::(\d+))?(?:/.*)?", url) if isinstance(url, str) else None
    if not achou or achou.group(2) not in (None, "443"):
        return None
    host = achou.group(1).lower()
    rotulos = host.split(".")
    if len(rotulos) < 2 or not all(rotulos) or host == "localhost" or rotulos[-1] == "localhost" \
            or not re.fullmatch(r"[a-z][a-z0-9-]*", rotulos[-1]):
        return None
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return host
    return None


def desvio_do_relogio(url, limite):
    """`hora remota - hora local`, em segundos, lida do cabeçalho `Date` do host de `url` (um `HEAD` em https, sem seguir redirecionamento,
    sem corpo, sem credencial, certificado validado, prazo TOTAL de `limite` s); None se não deu para conferir. Só informa: nunca acerta
    o relógio. `FORGE_RELOGIO_REMOTO=<época>` substitui a rede, só com FORGE_PERMITE_LOCAL=1 (os testes)."""
    if url is None or not url_valida(url, permite_local()):
        return None
    injetado = os.environ.get("FORGE_RELOGIO_REMOTO") if permite_local() else None
    if injetado:
        try:
            desvio = float(injetado) - time.time()
        except ValueError:
            return None
        return round(desvio) if abs(desvio) <= TETO_RELOGIO else None
    host = host_publico(url)
    if host is None:
        return None
    cabecalho = []

    def pedir():
        try:
            conexao = http.client.HTTPSConnection(host, 443, timeout=limite, context=ssl.create_default_context())
            conexao.request("HEAD", "/", headers={"User-Agent": "forge-doutor"})
            cabecalho.append(conexao.getresponse().getheader("Date"))
            conexao.close()
        except (OSError, http.client.HTTPException):
            pass

    fio = threading.Thread(target=pedir, daemon=True)
    fio.start()
    fio.join(limite)  # prazo total: conexão, resposta e leitura do cabeçalho
    if fio.is_alive() or not cabecalho or not isinstance(cabecalho[0], str) or len(cabecalho[0]) > 100:
        return None
    try:
        hora = email.utils.parsedate_to_datetime(cabecalho[0])
    except (ValueError, TypeError, IndexError, OverflowError):
        return None
    if hora.tzinfo is None:  # sem fuso explícito não há como comparar
        return None
    try:
        desvio = hora.timestamp() - time.time()
    except (ValueError, OverflowError, OSError):
        return None
    return round(desvio) if abs(desvio) <= TETO_RELOGIO else None


def texto_de_relogio(desvio):
    """A frase do aviso, ou "" (sem desvio medido ou dentro do limiar). O número é de minutos inteiros calculados aqui, nunca o texto do cabeçalho."""
    if desvio is None or abs(desvio) <= LIMIAR_RELOGIO:
        return ""
    estado = "atrasado" if desvio > 0 else "adiantado"
    return (f"O relógio deste computador está {round(abs(desvio) / 60)} min {estado} em relação ao GitHub: os horários dos registros "
            "e do quadro saem errados. Acerte o relógio do sistema (no WSL: `wsl --shutdown` no Windows e abra de novo).")


# Plugin ----------------------------------------------------------------------------------------
def claude(args, limite=180):
    """Roda o `claude` numa pasta neutra (nunca dentro do projeto): a troca do plugin não pode tocar nos arquivos dele.
    Numa sessão própria (`start_new_session`), para o Ctrl-C do terminal não o matar no meio da operação; se o Ctrl-C chegar aqui,
    espera o `claude` terminar e só então relança o `KeyboardInterrupt`."""
    interrompido = False
    try:
        with tempfile.TemporaryDirectory(prefix="forge-claude-") as neutro:
            p = subprocess.Popen(["claude", *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                 stdin=subprocess.DEVNULL, cwd=neutro, start_new_session=True)
            fim = time.monotonic() + limite
            while True:
                try:
                    saida, _ = p.communicate(timeout=max(fim - time.monotonic(), 0.1))
                    break
                except KeyboardInterrupt:
                    interrompido = True
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.communicate()
                    raise
    except (OSError, subprocess.TimeoutExpired) as erro:
        return 1, str(erro)
    if interrompido:
        raise KeyboardInterrupt
    return p.returncode, (saida or "").strip()


def tag_existe(url, versao):
    """A tag v<versao> existe no endereço do Forge (`ls-remote`, com as defesas). Sem conexão: False."""
    codigo, saida = rodar_git(["ls-remote", "--tags", "--refs", "--", url, f"refs/tags/v{versao}"])
    return codigo == 0 and saida.rstrip().endswith(f"refs/tags/v{versao}")


def fonte_para_add(origem):
    """O argumento do `claude plugin marketplace add` que recria a fonte `origem` (dicionário do settings ou da lista)."""
    if not isinstance(origem, dict):
        return None
    tipo = origem.get("source")
    if tipo in ("directory", "file") and isinstance(origem.get("path"), str):
        base = origem["path"]
    elif tipo == "github" and isinstance(origem.get("repo"), str):
        base = origem["repo"]
    elif tipo in ("git", "url") and isinstance(origem.get("url"), str):
        base = origem["url"]
    else:
        return None
    if not base or base.startswith("-") or re.search(r"\s", base):
        return None
    ref = origem.get("ref")
    return f"{base}#{ref}" if isinstance(ref, str) and ref and not ref.startswith("-") else base


def fonte_original():
    """A marketplace do Forge como está agora: {"fonte": argumento do `add`, "escopo": "user" (declarada no settings do usuário)
    ou "outro"}. None se não achar (lida do settings do usuário e, depois, de `claude plugin marketplace list --json`)."""
    try:
        dados = json.loads((casa() / ".claude" / "settings.json").read_text(encoding="utf-8"))
        fonte = fonte_para_add(dados["extraKnownMarketplaces"][MARKETPLACE]["source"])
    except (OSError, ValueError, KeyError, TypeError):
        fonte = None
    if fonte:
        return {"fonte": fonte, "escopo": "user"}
    codigo, saida = claude(["plugin", "marketplace", "list", "--json"], 60)
    try:
        lista = json.loads(saida) if codigo == 0 else []
    except ValueError:
        lista = []
    for item in lista if isinstance(lista, list) else []:
        if isinstance(item, dict) and item.get("name") == MARKETPLACE and fonte_para_add(item):
            return {"fonte": fonte_para_add(item), "escopo": "outro"}
    return None


def instalar_plugin():
    codigo, saida = claude(["plugin", "update", PLUGIN, "--scope", "user"])
    if codigo != 0:
        codigo, saida = claude(["plugin", "install", PLUGIN, "--scope", "user"])
    return codigo == 0, saida


def trocar_marketplace(fonte):
    """Troca a marketplace do usuário por `fonte` e deixa o plugin instalado. (deu certo, saída)"""
    claude(["plugin", "marketplace", "remove", MARKETPLACE, "--scope", "user"])
    codigo, saida = claude(["plugin", "marketplace", "add", fonte, "--scope", "user"])
    if codigo != 0:
        return False, saida
    return instalar_plugin()


def arquivo_da_fonte_original():
    return pasta_de_estado() / "marketplace-original.json"


def gravar_fonte_original(original):
    """Guarda a fonte e o escopo da marketplace ANTES de qualquer remoção (permissão 600): é daqui que `forge voltar-versao` recupera
    a marketplace se a troca for interrompida. Falha de gravação não impede a troca (a recuperação cai nos comandos manuais)."""
    arquivo = arquivo_da_fonte_original()
    try:
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        temporario = arquivo.with_name(arquivo.name + ".tmp")
        descritor = os.open(temporario, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descritor, "w", encoding="utf-8") as saida:
            saida.write(json.dumps({"fonte": original["fonte"], "escopo": original["escopo"]}, ensure_ascii=False, indent=2) + "\n")
        os.replace(temporario, arquivo)
        arquivo.chmod(0o600)
    except OSError:
        pass


def fonte_original_gravada():
    """A fonte guardada por `gravar_fonte_original`, ou None (sem arquivo ou conteúdo inválido)."""
    try:
        dados = json.loads(arquivo_da_fonte_original().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(dados, dict) and isinstance(dados.get("fonte"), str) and dados.get("escopo") in ("user", "outro") \
            and fonte_para_add({"source": "url", "url": dados["fonte"]}):
        return {"fonte": dados["fonte"], "escopo": dados["escopo"]}
    return None


def comandos_manuais(fonte):
    return (f"`claude plugin marketplace add {fonte} --scope user` e `claude plugin install {PLUGIN} --scope user` "
            f"(ou `claude plugin update {PLUGIN} --scope user`)")


def devolver_original(original):
    """Readiciona exatamente a fonte e o escopo de antes (se a marketplace era do escopo do usuário; senão só tira a do usuário)."""
    if original["escopo"] != "user":
        claude(["plugin", "marketplace", "remove", MARKETPLACE, "--scope", "user"])
        return instalar_plugin()[0]
    return trocar_marketplace(original["fonte"])[0]


def arquivos_alterados(projeto):
    """Os arquivos versionados com mudança (`git status --porcelain`, sem os não versionados). Conjunto vazio se `projeto` é None."""
    if projeto is None:
        return set()
    r = subprocess.run(["git", "-C", str(projeto), "status", "--porcelain", "-z", "-uno"], capture_output=True, text=True)
    return {entrada[3:] for entrada in r.stdout.split("\0") if len(entrada) > 3}


def restaurar_projeto(projeto, antes):
    """Defesa extra: devolve (`git checkout -- <arquivo>`) só o que estava limpo em `antes` (a foto de `arquivos_alterados` tirada antes
    da troca) e ficou alterado depois. Nunca toca em arquivo que já estava alterado. Diz quais arquivos e por quê. "" se nada (o texto começa com ". " e não termina com ponto)."""
    if projeto is None:
        return ""
    sujou = sorted(arquivos_alterados(projeto) - antes)
    for arquivo in sujou:
        subprocess.run(["git", "-C", str(projeto), "checkout", "--", arquivo], capture_output=True, text=True)
    return (f". Restaurei {', '.join(sujou)}: o arquivo estava salvo, mudou durante a troca do plugin e não era uma mudança sua, "
            f"então o devolvi ao que estava salvo") if sujou else ""


@contextlib.contextmanager
def _sigterm_como_interrupcao():
    """Durante o trecho crítico, SIGTERM vira `KeyboardInterrupt` (para a marketplace original ser devolvida)."""
    def tratar(_numero, _quadro):
        raise KeyboardInterrupt
    try:
        anterior = signal.signal(signal.SIGTERM, tratar)
    except ValueError:  # fora da thread principal
        yield
        return
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, anterior)


@contextlib.contextmanager
def _sem_interrupcao():
    """Enquanto devolve a marketplace, ignora Ctrl-C e SIGTERM: a recuperação não pode ser cortada."""
    try:
        antigos = [signal.signal(n, signal.SIG_IGN) for n in (signal.SIGINT, signal.SIGTERM)]
    except ValueError:
        yield
        return
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, antigos[0])
        signal.signal(signal.SIGTERM, antigos[1])


def fixar_plugin(url, versao, voltar_para=None, projeto=None):
    """Deixa o plugin do Forge fixado na tag v<versao>, só no escopo do usuário (`--scope user`): marketplace readicionada com
    `<endereço>#v<versao>` e plugin atualizado (ou instalado). Antes de qualquer remoção confirma a tag e guarda a fonte e o escopo
    originais; se algo falhar, readiciona exatamente a fonte original. Depois devolve só o que a troca alterou em arquivo versionado do `projeto` (nunca o que já estava alterado).
    Devolve (deu certo, mensagem em linguagem simples)."""
    antes = arquivos_alterados(projeto)
    if not tag_existe(url, versao):
        return False, f"não consegui confirmar a versão {versao} no endereço do Forge (sem conexão ou ela não existe). Não mexi no plugin"
    original = fonte_original()
    if original is None:
        original = fonte_original_gravada()
        if original is None:
            return False, ("não achei a marketplace do Forge no seu Claude (ela tem de estar instalada pelo endereço do Forge). "
                           f"Não mexi no plugin. Para instalar à mão: {comandos_manuais(url)}")
        if not devolver_original(original):
            return False, ("a marketplace do Forge sumiu do seu Claude e não consegui readicioná-la pela fonte guardada. "
                           f"Para refazer à mão: {comandos_manuais(original['fonte'])}")
    else:
        gravar_fonte_original(original)
    try:
        with _sigterm_como_interrupcao():
            deu, saida = trocar_marketplace(f"{url}#v{versao}")
    except KeyboardInterrupt:
        with _sem_interrupcao():
            devolveu = devolver_original(original)
        print("\nForge: interrompido durante a troca do plugin. " + (
            f"Devolvi a marketplace como estava ({original['fonte']})." if devolveu else
            f"Não consegui devolver a marketplace. Para refazer à mão: {comandos_manuais(original['fonte'])}"), file=sys.stderr)
        raise
    if deu:
        return True, f"o plugin do Forge está fixado na versão {versao}" + restaurar_projeto(projeto, antes)
    devolveu = devolver_original(original)
    aviso = restaurar_projeto(projeto, antes)
    como = f"Para refazer à mão: {comandos_manuais(original['fonte'])}"
    if devolveu:
        return False, (f"não consegui trocar o plugin para a versão {versao} ({saida[:160]}); devolvi a marketplace como estava "
                       f"({original['fonte']}, escopo {original['escopo']}){aviso}")
    return False, f"não consegui trocar o plugin para a versão {versao} ({saida[:160]}) nem devolver o de antes. {como}{aviso or '.'}"


def problemas_do_doutor(pasta_bin, projeto):
    """(lista de problemas, saída) do `forge-doutor --rapido` que está em `pasta_bin`. Sem problema: ([], "")."""
    try:
        r = subprocess.run([str(Path(pasta_bin) / "forge-doutor"), "--rapido", str(projeto)], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as erro:
        return [f"o doutor não rodou ({erro})"], ""
    if r.returncode == 0:
        return [], ""
    saida = (r.stdout + r.stderr).strip()
    return [l[2:].strip() for l in saida.splitlines() if l.startswith("- ")] or [saida or "o doutor terminou com erro"], saida


# Terminal --------------------------------------------------------------------------------------
def tem_terminal():
    return sys.stdin.isatty() and sys.stdout.isatty()


VARIAVEIS_DO_CLAUDE_CODE = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT")  # o Claude Code define as duas nos processos que roda


def _pai_e_nome(pid):
    """(pid do pai, nome do processo) lidos de /proc/<pid>/stat; (0, "") se não der para ler."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
        return int(stat[stat.rfind(")") + 2:].split()[1]), stat[stat.find("(") + 1:stat.rfind(")")]
    except (OSError, ValueError, IndexError):
        return 0, ""


def dentro_do_claude():
    """True se este processo foi chamado de dentro de uma sessão do Claude Code (um agente): variável do Claude Code no ambiente
    ou um processo ancestral chamado `claude`. Vale mesmo com pty, `$(...)` ou `bash <<<`, que escapam do hook `conformidade`."""
    if any(os.environ.get(v) for v in VARIAVEIS_DO_CLAUDE_CODE):
        return True
    pid, vistos = os.getppid(), set()
    while pid > 1 and pid not in vistos:
        vistos.add(pid)
        pai, nome = _pai_e_nome(pid)
        if nome.lower() in ("claude", "claude.exe"):
            return True
        pid = pai
    return False


def recusar_dentro_do_claude(comando):
    """Mensagem (para stderr) se `comando` foi chamado de dentro do Claude; None se pode seguir."""
    if dentro_do_claude():
        return (f"{comando}: isto é com você, não com o Claude. Rode no seu terminal, fora do Claude (a atualização muda o "
                f"seu Forge e pede a sua confirmação). Não mudei nada.")
    return None


def confirmar(pergunta):
    """True só com s ou sim; Enter, outra coisa ou fim da entrada contam como não."""
    try:
        resposta = input(f"{pergunta} [s/N] ")
    except EOFError:
        return False
    return resposta.strip().lower() in ("s", "sim")


# Ponto de retorno ------------------------------------------------------------------------------
def pasta_de_retornos(projeto):
    return pasta_de_estado() / "retorno" / projeto.name


def arquivos_versionados(projeto, pasta):
    """Os arquivos que o git do projeto versiona em `pasta` (caminhos relativos ao projeto)."""
    r = subprocess.run(["git", "-C", str(projeto), "ls-files", "-z", "--", pasta], capture_output=True, text=True)
    return [a for a in r.stdout.split("\0") if a]


def criar_ponto(projeto, meta):
    """Guarda só os arquivos VERSIONADOS de `.forge/` e o `meta.json` (versão do plugin e o resto da volta). Nada que não esteja
    no git: `settings.local.json`, chaves e arquivos locais ficam de fora. A pasta é só do dono (700). Devolve a pasta do ponto."""
    base = pasta_de_retornos(projeto)
    base.mkdir(parents=True, exist_ok=True)
    ponto = base / (time.strftime("%Y%m%d-%H%M%S-") + f"{time.time_ns() % 1_000_000:06d}")
    ponto.mkdir(parents=True)
    for pasta in (ponto, base, pasta_de_estado() / "retorno", pasta_de_estado()):
        pasta.chmod(0o700)
    for arquivo in arquivos_versionados(projeto, ".forge"):
        origem = projeto / arquivo
        if origem.is_file():
            destino = ponto / "forge" / Path(arquivo).relative_to(".forge")
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)
    (ponto / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with open(pasta_de_estado() / "versoes.log", "a", encoding="utf-8") as log:
        log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{projeto.name}\t{meta['plugin_antes']}\t{meta['plugin_depois']}\n")
    return ponto


def ultimo_ponto(projeto):
    """(pasta, meta) do ponto de retorno mais recente DESTE projeto ainda não usado, ou (None, None)."""
    pasta = pasta_de_retornos(projeto)
    for ponto in sorted(pasta.iterdir(), reverse=True) if pasta.is_dir() else []:
        try:
            meta = json.loads((ponto / "meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(meta, dict) and not meta.get("usado") and meta.get("projeto") == str(projeto):
            return ponto, meta
    return None, None


def marcar_usado(ponto, meta):
    meta["usado"] = True
    (ponto / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
