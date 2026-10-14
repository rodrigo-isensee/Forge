"""Forge: o que `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor têm em comum (primeiro uso, F5).

Consulta as releases do Forge por `git` (grátis, R-CUSTO), com as mesmas defesas do `forge-check fontes` (docs/fontes-de-praticas.md):
só https, pasta corrente neutra (nunca o projeto), todos os outros protocolos negados, sem pergunta de senha, sem configuração
do git do usuário. Fixa e troca a versão do plugin pelo `claude plugin ...` (marketplace na tag `vX.Y.Z`). Só biblioteca padrão."""
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
    return f"Saiu a versão {nova} do Forge (você usa a {atual}). Para atualizar com ponto de retorno, rode: forge atualizar"


# Plugin ----------------------------------------------------------------------------------------
def claude(args, limite=180):
    try:
        r = subprocess.run(["claude", *args], capture_output=True, text=True, timeout=limite, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired) as erro:
        return 1, str(erro)
    return r.returncode, (r.stdout + r.stderr).strip()


def fixar_plugin(url, versao, voltar_para=None):
    """Deixa o plugin do Forge fixado na tag v<versao>: marketplace readicionada com `<endereço>#v<versao>` e plugin atualizado
    (ou instalado, se a troca da marketplace o tirou). Se falhar, devolve o plugin à versão `voltar_para`.
    Devolve (deu certo, mensagem em linguagem simples)."""
    def trocar(alvo):
        claude(["plugin", "marketplace", "remove", MARKETPLACE])
        codigo, saida = claude(["plugin", "marketplace", "add", f"{url}#v{alvo}"])
        if codigo != 0:
            return False, saida
        codigo, saida = claude(["plugin", "update", PLUGIN])
        if codigo != 0:
            codigo, saida = claude(["plugin", "install", PLUGIN])
        return codigo == 0, saida

    deu, saida = trocar(versao)
    if deu:
        return True, f"o plugin do Forge está fixado na versão {versao}"
    if voltar_para and voltar_para != versao:
        devolveu, _ = trocar(voltar_para)
        if devolveu:
            return False, f"não consegui trocar o plugin para a versão {versao} ({saida[:160]}); devolvi o plugin à versão {voltar_para}"
    return False, (f"não consegui trocar o plugin para a versão {versao} ({saida[:160]}). Para refazer à mão: "
                   f"`claude plugin marketplace add {url}#v{voltar_para or versao}` e `claude plugin install {PLUGIN}`")


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


def criar_ponto(projeto, meta):
    """Guarda `.forge/` (sem `run/`), os `settings*.json` do projeto e o `meta.json`. Devolve a pasta do ponto."""
    ponto = pasta_de_retornos(projeto) / (time.strftime("%Y%m%d-%H%M%S-") + f"{time.time_ns() % 1_000_000:06d}")
    ponto.mkdir(parents=True)
    if (projeto / ".forge").is_dir():
        shutil.copytree(projeto / ".forge", ponto / "forge", ignore=shutil.ignore_patterns("run"))
    (ponto / "claude").mkdir()
    for nome in ("settings.json", "settings.local.json"):
        if (projeto / ".claude" / nome).is_file():
            shutil.copy2(projeto / ".claude" / nome, ponto / "claude" / nome)
    (ponto / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with open(pasta_de_estado() / "versoes.log", "a", encoding="utf-8") as log:
        log.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\t{projeto.name}\t{meta['plugin_antes']}\t{meta['plugin_depois']}\n")
    return ponto


def ultimo_ponto(projeto):
    """(pasta, meta) do ponto de retorno mais recente ainda não usado, ou (None, None)."""
    pasta = pasta_de_retornos(projeto)
    for ponto in sorted(pasta.iterdir(), reverse=True) if pasta.is_dir() else []:
        try:
            meta = json.loads((ponto / "meta.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(meta, dict) and not meta.get("usado"):
            return ponto, meta
    return None, None


def marcar_usado(ponto, meta):
    meta["usado"] = True
    (ponto / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
