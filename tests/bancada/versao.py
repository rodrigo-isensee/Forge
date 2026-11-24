#!/usr/bin/env python3
"""Forge: bench de versões com agentes de verdade (BENCH-VERSAO, E175; desenho do arquiteto E175.1, decisão do dono 24/11).
Uma versão (tag) do Forge entrega o mesmo pedido de referência (romanos, 5 critérios, decisões respondidas) num projeto
descartável, e a nota vem de testes escondidos guardados fora do repositório. Só biblioteca padrão.

Uso: python3 tests/bancada/versao.py --tag v0.47.16 --repo <dono>/<repositório-descartável> [--executar]
     [--bench ~/.forge-bench] [--quadro ~/.forge-contrib/docs/kanban/bench-versao.md] [--forge <clone do Forge>]
     [--remoto-url <url>]
- Sem `--executar` (o padrão): só valida (testes escondidos congelados, marca, tag, nome do repositório) e imprime a
  estimativa da cota; não chama o modelo.
- Com `--executar` (SÓ O DONO, na máquina dele, com a assinatura; R-CUSTO): exporta a árvore da tag, cria o projeto em
  <bench>/rodadas/<id>/projeto (forge-init, stack python), envia `main` e `develop` ao remoto (que precisa estar vazio) e
  roda `claude -p --agent forge:jarvis --plugin-dir <árvore da tag> --permission-mode auto` (nunca bypass) com o pedido.
  Sessão que termina sem PR é retomada com a resposta automática fixa, até 3 voltas. Limites: 20 agentes, 3 voltas,
  4 h e 80 M tokens processados; o que passa encerra a sessão e fica na linha. Depois roda os testes escondidos no commit
  do PR (na `develop`, se integrado), procura a marca no projeto e nos registros, grava <rodada>/rodada.json e acrescenta
  a linha ao quadro, com a fonte de cada medida e a carga da máquina (o tempo é indicativo: o time segue trabalhando).
- Recusa (saída 2) com CI, GITHUB_ACTIONS ou ANTHROPIC_API_KEY definidas: nunca roda no CI nem pela API paga.
Saída: 0 válido (ou rodada concluída e linha gravada); 1 validação, preparação ou avaliação falhou; 2 uso ou recusa."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent.parent
PEDIDO, RESPOSTA = PASTA / "romanos" / "pedido.md", PASTA / "romanos" / "resposta.md"
CONFIG = RAIZ / "tests" / "config.json"
VERSAO_ESCONDIDOS = "romanos-v1"
CONGELADOS = {"test_escondido.py": "8ccf13928cd5a3a62d5c4981640c76897dec611c40b38bf1137e513836d62d0d",
              "marca.txt": "85fe16b718096050ea1de147284b610c56604a1db874c6865398a1a91244334a"}
MARCA_SHA256 = "3d518989252aee08ea77b7d9fc207402e796a1f4bbb71d27343ebcd32fc3de50"  # também em termos_proibidos_hash
LIMITES = {"agentes": 20, "voltas": 3, "segundos": 4 * 3600, "tokens": 80_000_000}
AMBIENTE_PROIBIDO = ("CI", "GITHUB_ACTIONS", "ANTHROPIC_API_KEY")
ESTIMATIVA = ("cota por rodada (E175.1): típico ~1,0 M tokens novos e 1h50 (~28 M processados com cache); mínimo ~0,5 M "
              "e 45 min; máximo ~2,5 M e 3h30")
PRONTO = "python3 -m unittest discover -s tests -t ."
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+")
AGENTE = {"Task", "Agent"}
INTERVALO = 5  # segundos entre as conferências dos limites
CABECALHO = """# Bench de versões com agentes (BENCH-VERSAO)

Linhas gravadas por `tests/bancada/versao.py`; o registro completo de cada rodada fica no `rodada.json` citado.
Fontes: testes = `python3 -I test_escondido.py` ({v}) no commit avaliado (linha `resultado:`); PR = `gh pr list --state all`;
tokens = soma do `usage` por mensagem nas transcrições da sessão (`~/.claude/projects`, com subagentes; sem elas, o
`stream-json`), novos = entrada + saída + criação de cache, processados = novos + leitura de cache; agentes = chamadas
`Task`/`Agent` no `stream-json`; voltas = retomadas com a resposta automática; minutos = relógio do roteiro (indicativo);
carga = `os.getloadavg()` de 1 min no início, máxima a cada {i} s e no fim.

| Data | Versão | Testes escondidos | PR | Tokens novos | Tokens processados | Agentes | Voltas | Minutos (indicativo) | Carga (início/máx/fim) | Limite | Marca | Registro |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""


def sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def rodar(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, **kw)


def validar(args):
    """Erros que impedem a rodada (lista vazia = pronta)."""
    erros = [f"falta {p}" for p in (PEDIDO, RESPOSTA) if not p.is_file()]
    if not REPO.fullmatch(args.repo):
        erros.append(f"--repo deve ser <dono>/<nome>: {args.repo!r}")
    pasta = args.bench / "escondidos" / VERSAO_ESCONDIDOS
    for nome, esperado in CONGELADOS.items():
        if not (pasta / nome).is_file():
            erros.append(f"teste escondido ausente: {pasta / nome}")
        elif sha256(pasta / nome) != esperado:
            erros.append(f"teste escondido alterado (sha256 difere do congelado): {pasta / nome}")
    marca = ler_marca(pasta)
    if marca and hashlib.sha256(marca.encode()).hexdigest() != MARCA_SHA256:
        erros.append("a marca não bate com MARCA_SHA256")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if MARCA_SHA256 not in {e.get("sha256") for e in config.get("termos_proibidos_hash", [])}:
        erros.append("a marca não está em termos_proibidos_hash de tests/config.json")
    if rodar(["git", "-C", str(args.forge), "rev-parse", "--verify", "-q", f"refs/tags/{args.tag}^{{commit}}"]).returncode:
        erros.append(f"tag {args.tag} não existe em {args.forge}")
    elif marca and rodar(["git", "-C", str(args.forge), "grep", "-q", "-F", "-i", marca, args.tag]).returncode == 0:
        erros.append(f"a marca aparece na árvore da {args.tag}: os testes escondidos vazaram para o Forge")
    return erros


def ler_marca(pasta):
    try:
        return (pasta / "marca.txt").read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def comando(forge_dir, texto, sessao=None):
    """A sessão da rodada: sempre --permission-mode auto, nunca bypass (decisão do dono 24/11)."""
    return ["claude", "-p", texto, "--agent", "forge:jarvis", "--plugin-dir", str(forge_dir), "--permission-mode", "auto",
            "--output-format", "stream-json", "--verbose"] + (["--resume", sessao] if sessao else [])


def exportar(forge, ref, destino):
    """Árvore da tag em `destino`, por git archive (sem worktree no clone do dono)."""
    destino.mkdir(parents=True)
    arq = subprocess.Popen(["git", "-C", str(forge), "archive", ref], stdout=subprocess.PIPE)
    tar = subprocess.run(["tar", "-x", "-C", str(destino)], stdin=arq.stdout, capture_output=True)
    arq.stdout.close()
    if arq.wait() or tar.returncode:
        raise RuntimeError(f"exportar {ref}: git archive ou tar falhou")


def preparar_projeto(projeto, forge_dir, url):
    if rodar(["git", "ls-remote", url]).stdout.strip():
        raise RuntimeError(f"o remoto {url} não está vazio: use um repositório novo por rodada")
    git = ["git", "-C", str(projeto), "-c", "user.name=forge-bench", "-c", "user.email=forge-bench@localhost"]
    passos([["git", "init", "-q", "-b", "main", str(projeto)],
            ["bash", str(forge_dir / "bin" / "forge-init"), "--nome", "romanos", "--descricao",
             "Conversor de numerais romanos (bench de versões)", "--stack", "python", "--pronto", PRONTO, str(projeto)]])
    so_a_tag(projeto)
    passos([git + ["add", "-A"], git + ["commit", "-q", "-m", "chore: projeto do bench"], git + ["branch", "develop"],
            git + ["remote", "add", "origin", url], git + ["push", "-q", "origin", "main", "develop"]])


def passos(cmds):
    for cmd in cmds:
        r = rodar(cmd)
        if r.returncode:
            raise RuntimeError(f"preparar o projeto: {' '.join(cmd[:6])} falhou: {r.stderr.strip()[-300:]}")


def so_a_tag(projeto):
    """Tira o forge instalado das configurações do projeto: o plugin da sessão é só a árvore da tag (--plugin-dir)."""
    arq = projeto / ".claude" / "settings.json"
    if arq.is_file():
        dados = json.loads(arq.read_text(encoding="utf-8"))
        dados.pop("enabledPlugins", None)
        dados.pop("extraKnownMarketplaces", None)
        arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_evento(linha, medida):
    try:
        ev = json.loads(linha)
    except ValueError:
        return
    if not isinstance(ev, dict):
        return
    if ev.get("session_id"):
        medida["sessao"] = ev["session_id"]
    if ev.get("type") == "system" and ev.get("subtype") == "init":
        medida["plugins"] = [p for p in ev.get("plugins") or [] if isinstance(p, dict) and p.get("name") == "forge"]
    msg = ev.get("message") if ev.get("type") == "assistant" else None
    if isinstance(msg, dict):
        uso = msg.get("usage") if isinstance(msg.get("usage"), dict) else {}
        if msg.get("id") and msg["id"] not in medida["mensagens"]:
            medida["mensagens"].add(msg["id"])
            somar(medida["stream"], uso)
        for bloco in msg.get("content") or []:
            if isinstance(bloco, dict) and bloco.get("type") == "tool_use" and bloco.get("name") in AGENTE:
                medida["agentes"].add(bloco.get("id"))


def somar(total, uso):
    val = {k: v for k, v in uso.items() if type(v) is int}
    novos = sum(val.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens"))
    total["novos"] += novos
    total["processados"] += novos + val.get("cache_read_input_tokens", 0)


def estourou(medida, prazo):
    if len(medida["agentes"]) > LIMITES["agentes"]:
        return "agentes"
    if medida["stream"]["processados"] > LIMITES["tokens"]:
        return "tokens"
    return "tempo" if time.monotonic() > prazo else None


def sessao(cmd, cwd, medida, prazo, log):
    """Roda uma sessão, lê o stream-json enquanto ele chega e a encerra ao passar de um limite."""
    with open(log, "a", encoding="utf-8") as saida:
        proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=saida, stdin=subprocess.DEVNULL,
                                text=True)

        def ler():
            for linha in proc.stdout:
                saida.write(linha)
                ler_evento(linha, medida)

        leitor = threading.Thread(target=ler, daemon=True)
        leitor.start()
        while proc.poll() is None:
            medida["carga"].append(os.getloadavg()[0])
            medida["limite"] = medida["limite"] or estourou(medida, prazo)
            if medida["limite"]:
                proc.terminate()
                break
            time.sleep(INTERVALO)
        proc.wait()
        leitor.join()
    medida["limite"] = medida["limite"] or estourou(medida, prazo)


def pr_da_rodada(repo):
    r = rodar(["gh", "pr", "list", "--repo", repo, "--state", "all", "--base", "develop", "--limit", "1",
               "--json", "number,state,isDraft,headRefOid"])
    try:
        prs = json.loads(r.stdout) if r.returncode == 0 else []
    except ValueError:
        prs = []
    return prs[0] if prs else None


def avaliar(projeto, escondidos, pr, destino):
    """Roda os testes escondidos no commit do PR (na develop, se integrado; sem PR, no HEAD local)."""
    rodar(["git", "-C", str(projeto), "fetch", "-q", "origin"])
    ref = "origin/develop" if pr and pr["state"] == "MERGED" else (pr["headRefOid"] if pr else "HEAD")
    commit = rodar(["git", "-C", str(projeto), "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"]).stdout.strip()
    if not commit:
        return {"commit": None, "resultado": "commit não encontrado"}
    try:
        exportar(projeto, commit, destino)
    except (RuntimeError, OSError):
        return {"commit": commit, "resultado": "exportação falhou"}
    try:
        r = rodar([sys.executable, "-I", str(escondidos / "test_escondido.py")], timeout=600,
                  env={"PATH": os.environ.get("PATH", ""), "ROMANOS_PROJETO": str(destino)})
        achado = re.findall(r"^resultado: (\d+/\d+)$", r.stdout, re.M)
    except subprocess.TimeoutExpired:
        achado = []
    return {"commit": commit, "resultado": achado[-1] if achado else "sem resultado"}


def tokens_das_transcricoes(cwd):
    """Soma do usage por mensagem nas transcrições da sessão e dos subagentes; None se não achar."""
    pasta = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(cwd))
    total, vistos = {"novos": 0, "processados": 0}, set()
    for arq in sorted(pasta.rglob("*.jsonl")) if pasta.is_dir() else []:
        for linha in arq.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                msg = json.loads(linha).get("message")
            except (ValueError, AttributeError):
                continue
            if isinstance(msg, dict) and isinstance(msg.get("usage"), dict) and msg.get("id") not in vistos:
                vistos.add(msg.get("id"))
                somar(total, msg["usage"])
    return total if vistos else None


def marca_em(pastas, marca):
    alvo = marca.lower()
    for pasta in pastas:
        for arq in Path(pasta).rglob("*"):
            if arq.is_file() and ".git" not in arq.parts and alvo in arq.read_bytes().decode("utf-8", "ignore").lower():
                return str(arq)
    return None


def linha_do_quadro(r):
    t, c = r["tokens"], r["carga"]
    pr = f"#{r['pr']['number']} {r['pr']['state'].lower()}" if r["pr"] else "sem PR"
    milhar = lambda n: f"{n:_}".replace("_", ".")  # noqa: E731
    return (f"| {r['data']} | {r['tag']} ({r['tag_commit'][:8]}) | {r['avaliacao']['resultado']} | {pr} | "
            f"{milhar(t['novos'])} | {milhar(t['processados'])} | {r['agentes']} | {r['voltas']} | {r['minutos']} | "
            f"{c['inicio']}/{c['max']}/{c['fim']} | {r['limite'] or 'nenhum'} | {r['marca'] or 'ausente'} | "
            f"`{r['registro']}` |\n")


def executar(args):
    marca = ler_marca(args.bench / "escondidos" / VERSAO_ESCONDIDOS)
    rodadas = args.bench / "rodadas"
    rodadas.mkdir(parents=True, exist_ok=True)
    trava = rodadas / ".trava"
    try:
        os.close(os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        print(f"versao: outra rodada em curso ({trava}); uma por vez. Se nenhuma roda, apague a trava.", file=sys.stderr)
        return 2
    try:
        return rodada(args, rodadas, marca)
    finally:
        trava.unlink(missing_ok=True)


def rodada(args, rodadas, marca):
    pasta = rodadas / f"{args.tag}-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    forge_dir, projeto, log = pasta / "forge", pasta / "projeto", pasta / "sessao.jsonl"
    url = args.remoto_url or f"https://github.com/{args.repo}.git"
    try:
        exportar(args.forge, args.tag, forge_dir)
        preparar_projeto(projeto, forge_dir, url)
    except (RuntimeError, OSError) as e:
        print(f"versao: {e}", file=sys.stderr)
        return 1
    medida = {"mensagens": set(), "agentes": set(), "stream": {"novos": 0, "processados": 0}, "carga": [],
              "sessao": None, "plugins": None, "limite": None}
    inicio, carga0 = time.monotonic(), os.getloadavg()[0]
    prazo, voltas, pr = inicio + LIMITES["segundos"], 0, None
    texto = PEDIDO.read_text(encoding="utf-8")
    while True:
        sessao(comando(forge_dir, texto, medida["sessao"] if voltas else None), projeto, medida, prazo, log)
        pr = pr_da_rodada(args.repo)
        if pr or medida["limite"] or not medida["sessao"]:
            break
        if voltas == LIMITES["voltas"]:
            medida["limite"] = "voltas"
            break
        voltas, texto = voltas + 1, RESPOSTA.read_text(encoding="utf-8")
    minutos = round((time.monotonic() - inicio) / 60, 1)
    registro = {"data": datetime.now().strftime("%Y-%m-%d %H:%M"), "tag": args.tag,
                "tag_commit": rodar(["git", "-C", str(args.forge), "rev-parse", f"{args.tag}^{{commit}}"]).stdout.strip(),
                "pedido_sha256": sha256(PEDIDO), "resposta_sha256": sha256(RESPOSTA), "escondidos": VERSAO_ESCONDIDOS,
                "repo": args.repo, "pr": pr, "avaliacao": avaliar(projeto, args.bench / "escondidos" / VERSAO_ESCONDIDOS,
                                                                    pr, pasta / "avaliado"),
                "tokens": tokens_das_transcricoes(projeto) or medida["stream"], "tokens_stream": medida["stream"],
                "agentes": len(medida["agentes"]), "voltas": voltas, "minutos": minutos, "limite": medida["limite"],
                "carga": {"inicio": carga0, "max": max(medida["carga"] + [carga0]), "fim": os.getloadavg()[0]},
                "plugin_forge": medida["plugins"], "sessao": medida["sessao"],
                "marca": marca_em([projeto, log], marca) if marca else None, "registro": str(pasta / "rodada.json")}
    registro["carga"] = {k: round(v, 2) for k, v in registro["carga"].items()}
    (pasta / "rodada.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.quadro.parent.mkdir(parents=True, exist_ok=True)
    novo = not args.quadro.is_file()
    with open(args.quadro, "a", encoding="utf-8") as q:
        q.write((CABECALHO.format(v=VERSAO_ESCONDIDOS, i=INTERVALO) if novo else "") + linha_do_quadro(registro))
    print(linha_do_quadro(registro), end="")
    return 0


def principal(argv=None, env=None):
    env = os.environ if env is None else env
    ap = argparse.ArgumentParser(prog="versao", description="Bench de versões com agentes (só o dono roda).",
                                 allow_abbrev=False)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--repo", required=True, help="<dono>/<nome> do repositório público descartável, vazio")
    ap.add_argument("--executar", action="store_true", help="roda de verdade (cota da assinatura do dono; R-CUSTO)")
    ap.add_argument("--bench", type=Path, default=Path.home() / ".forge-bench")
    ap.add_argument("--quadro", type=Path, default=Path.home() / ".forge-contrib" / "docs" / "kanban" / "bench-versao.md")
    ap.add_argument("--forge", type=Path, default=RAIZ)
    ap.add_argument("--remoto-url", help="URL do remoto no lugar de https://github.com/<repo>.git")
    args = ap.parse_args(argv)
    proibidas = [v for v in AMBIENTE_PROIBIDO if v in env]
    if proibidas:
        print(f"versao: recusado com {', '.join(proibidas)} definida(s): só o dono roda, fora do CI e sem API paga",
              file=sys.stderr)
        return 2
    erros = validar(args)
    for erro in erros:
        print(f"versao: {erro}", file=sys.stderr)
    if erros:
        return 1
    print(f"versao: pronta para {args.tag} em {args.repo}; {ESTIMATIVA}; limites: {LIMITES['agentes']} agentes, "
          f"{LIMITES['voltas']} voltas, {LIMITES['segundos'] // 3600} h, {LIMITES['tokens'] // 1_000_000} M tokens")
    if not args.executar:
        print("simulação: nada foi chamado; --executar roda de verdade (só o dono, R-CUSTO)")
        return 0
    if not shutil.which("claude"):
        print("versao: claude não está no PATH", file=sys.stderr)
        return 1
    return executar(args)


if __name__ == "__main__":
    sys.exit(principal())
