"""Forge: o que `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor têm em comum (primeiro uso, F5).

Consulta as releases do Forge por `git` (grátis, R-CUSTO), com as mesmas defesas do `forge-check fontes` (docs/fontes-de-praticas.md):
só https, pasta corrente neutra (nunca o projeto), todos os outros protocolos negados, sem pergunta de senha, sem configuração
do git do usuário. Fixa e troca a versão do plugin pelo `claude plugin ...` (marketplace na tag `vX.Y.Z`, sempre no escopo do usuário). Só biblioteca padrão."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def aviso_de_versao_nova(limite):
    """Uma frase avisando que saiu versão nova do Forge, ou "" (em dia, sem rede, consulta desligada ou endereço inválido)."""
    url, atual = url_do_forge(), versao_do_plugin()
    if url is None or versao_de(atual) is None:
        return ""
    nova, _ = ultima_versao(url, limite)
    if nova is None or versao_de(nova) <= versao_de(atual):
        return ""
    return f"Saiu a versão {nova} do Forge (você usa a {atual}). Para atualizar com ponto de retorno, rode no terminal: `forge atualizar`"


# Plugin ----------------------------------------------------------------------------------------
def claude(args, limite=180):
    """Roda o `claude` numa pasta neutra (nunca dentro do projeto): a troca do plugin não pode tocar nos arquivos dele."""
    try:
        with tempfile.TemporaryDirectory(prefix="forge-claude-") as neutro:
            r = subprocess.run(["claude", *args], capture_output=True, text=True, timeout=limite, stdin=subprocess.DEVNULL, cwd=neutro)
    except (OSError, subprocess.TimeoutExpired) as erro:
        return 1, str(erro)
    return r.returncode, (r.stdout + r.stderr).strip()


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
        return False, "não achei a marketplace do Forge no seu Claude (ela tem de estar instalada pelo endereço do Forge). Não mexi no plugin"
    deu, saida = trocar_marketplace(f"{url}#v{versao}")
    if deu:
        return True, f"o plugin do Forge está fixado na versão {versao}" + restaurar_projeto(projeto, antes)
    devolveu = devolver_original(original)
    aviso = restaurar_projeto(projeto, antes)
    como = (f"Para refazer à mão: `claude plugin marketplace add {original['fonte']} --scope user` e "
            f"`claude plugin install {PLUGIN} --scope user`")
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
