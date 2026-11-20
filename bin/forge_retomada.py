"""Forge: `forge-check retomada` (BP3 S4, v0479; E39.33): os agentes interrompidos pela queda da sessão (lista `interrompidos` do
`agentes.json`, S3) e a ação da matriz para cada um. Só leitura, sem rede, só biblioteca padrão; cada git local até 3 s.
`--contar` imprime só o número, no prazo de 3 s no total (para o atalho da S5). Saída 0 leu; 4 registro ilegível ou prazo estourado
(o atalho conta zero e avisa). Remover worktree, branch ou mudança não é com o Forge: pergunta ao dono (P2 de 2026-10-12).
Importado pelo `bin/forge-check`; `ctx` traz dele `caminho_do_pedido`, `PedidoFora`, `entregas_conferidas`, `raizes_de_pedidos` e
`sem_controle`."""
import hashlib
import os
import re
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

PRAZO_S = 3
LIMITE_BRIEF, LIMITE_PEDIDO = 256 * 1024, 4 * 1024 * 1024
NOME = re.compile(r"[A-Za-z0-9-]{1,64}")
PEDIDO = re.compile(r"^Pedido:[ \t]*([A-Za-z0-9][A-Za-z0-9._-]{0,80})[ \t]*$", re.M)
NOTA = "com a nota `continue do estado atual da branch (git log, git status), confira antes de seguir`"
ACOES = {
    "entregue": "nada a relançar: `entrega conferida` do pedido já cobre a branch depois da queda",
    "continua": "`SendMessage` ao id (só se esta sessão é a mesma conversa, `--continue`): o agente segue com o próprio contexto",
    "sem_brief": "brief ausente ou fora de docs/briefs: reselar (`forge-check brief selar`) e relançar",
    "vencido": "selo vencido (o brief mudou): reselar (`forge-check brief selar`) e relançar; o aviso D3 do hook segue valendo",
    "suja": f"worktree com arquivo não commitado: nunca descartar; relançar na mesma worktree com o mesmo brief, {NOTA}",
    "relancar": f"relançar com o mesmo brief, {NOTA}",
}
REMOCAO = "qualquer remoção (worktree, branch, mudança não commitada) o Forge não faz; pergunte ao dono"


def git(raiz, *args):
    """(rc, stdout) de um git local sem as variáveis GIT_*; falha ou prazo estourado devolvem (1, '')."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=PRAZO_S)
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return 1, ""
    return r.returncode, r.stdout.strip()


def ler(caminho, limite):
    """Os bytes do arquivo regular `caminho` (sem seguir link nem esperar FIFO), ou None se não é regular, passa de `limite` ou não abre."""
    try:
        with os.fdopen(os.open(caminho, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW), "rb") as f:
            dados = f.read(limite + 1) if stat.S_ISREG(os.fstat(f.fileno()).st_mode) else None
    except (OSError, ValueError):
        return None
    return dados if dados is not None and len(dados) <= limite else None


def brief_atual(raiz, caminho, ctx):
    """(sha256, texto) do brief achado em `docs/briefs/` de alguma raiz de pedidos (o `realpath` fica dentro dela), ou (None, '')."""
    for base in ctx["raizes_de_pedidos"](raiz):
        real = Path(os.path.realpath(Path(base) / caminho))
        if Path(os.path.realpath(base)) / "docs" / "briefs" in real.parents and (dados := ler(real, LIMITE_BRIEF)) is not None:
            return hashlib.sha256(dados).hexdigest(), dados.decode("utf-8", "replace")
    return None, ""


def ref_da_branch(raiz, branch):
    """A ref local da branch, ou a de `origin/`; None se nenhuma existe (o prefixo `refs/` impede o nome de virar opção do git)."""
    return next((r for r in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}") if git(raiz, "rev-parse", "--verify", "--quiet", r)[0] == 0), None)


def entregue(raiz, item, texto_brief, ctx):
    """True se o `## Histórico` do pedido do brief tem `entrega conferida <sha>` com o sha na branch e commitado depois do `desde`."""
    pedido, desde = PEDIDO.search(texto_brief), item.get("desde")
    if not pedido or isinstance(desde, bool) or not isinstance(desde, (int, float)):
        return False
    try:
        dados = ler(ctx["caminho_do_pedido"](raiz, pedido.group(1)), LIMITE_PEDIDO) or b""
    except (ctx["PedidoFora"], OSError, ValueError):
        return False
    shas = ctx["entregas_conferidas"](dados.decode("utf-8", "replace"))
    for ref in filter(None, (ref_da_branch(raiz, b) for b in item["branches"])):
        for sha in shas:
            rc, hora = git(raiz, "show", "-s", "--format=%ct", sha)
            if git(raiz, "merge-base", "--is-ancestor", sha, ref)[0] == 0 and rc == 0 and hora.isdigit() and int(hora) >= desde:
                return True
    return False


def suja(raiz, branches):
    """True se a worktree de alguma das `branches` tem arquivo não commitado."""
    rc, lista = git(raiz, "worktree", "list", "--porcelain")
    for bloco in (lista.split("\n\n") if rc == 0 else ()):
        campos = dict(l.split(" ", 1) for l in bloco.splitlines() if " " in l)
        if campos.get("branch", "").removeprefix("refs/heads/") in branches and git(campos.get("worktree", ""), "status", "--porcelain")[1]:
            return True
    return False


def com_transcript(item):
    """True se há `subagents/agent-<id>.jsonl` da sessão do item em `~/.claude/projects/` (o `SendMessage` ainda acha o contexto)."""
    sessao, aid = item.get("sessao"), item.get("id")
    if not (isinstance(sessao, str) and NOME.fullmatch(sessao) and isinstance(aid, str) and NOME.fullmatch(aid)):
        return False
    return any(Path.home().glob(f".claude/projects/*/{sessao}/subagents/agent-{aid}.jsonl"))


def acao(raiz, item, atual, texto, ctx):
    """A chave de `ACOES` do item: entregue, continua, sem_brief, vencido, suja ou relancar (nessa ordem)."""
    if entregue(raiz, item, texto, ctx):
        return "entregue"
    if com_transcript(item):
        return "continua"
    if atual is None:
        return "sem_brief"
    if atual != item["briefs"][0]["sha256"]:
        return "vencido"
    return "suja" if suja(raiz, item["branches"]) else "relancar"


def interrompidos(raiz, agentes, agora):
    """Os itens de `interrompidos` dentro do prazo e com brief de forma válida; sem arquivo, nenhum. Levanta `EstadoIlegivel`."""
    arquivo = agentes.arquivo_de_estado(raiz)
    if arquivo is None:
        return []
    hook = agentes.Hook("agentes")
    hook.raiz = Path(raiz)
    vivos, _ = agentes.interrompidos_vigentes(agentes.ler_estado(arquivo), agora, hook.expira_s())
    return [dict(i, briefs=agentes.briefs_validos(i), branches=agentes.textos(i.get("branches"))) for i in vivos if agentes.briefs_validos(i)]


def estourou(*_):
    raise TimeoutError(f"passou de {PRAZO_S} s")


def executar(a, raiz, ctx):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
    try:
        import agentes
    finally:
        sys.path.pop(0)
    if a.contar and hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, estourou)
        signal.alarm(PRAZO_S)
    try:
        itens = interrompidos(raiz, agentes, time.time())
    except (agentes.EstadoIlegivel, ValueError, OSError) as erro:  # OSError inclui o TimeoutError do prazo do --contar
        print(f"retomada: registro de agentes ilegível ou prazo estourado ({ctx['sem_controle'](erro)}); nada lido", file=sys.stderr)
        return 4
    finally:
        signal.alarm(0) if hasattr(signal, "SIGALRM") else None
    if a.contar:
        print(len(itens))
        return 0
    for item in itens:
        brief = item["briefs"][0]
        atual, texto = brief_atual(raiz, brief["caminho"], ctx)
        print(ctx["sem_controle"](f"retomada: {item.get('tipo') or '?'} · id {item.get('id') or 'sem id'} · branch {', '.join(item['branches']) or '—'} · "
                                  f"brief {brief['caminho']} sha256 {brief['sha256']} · ação: {ACOES[acao(raiz, item, atual, texto, ctx)]}"))
    print(f"retomada: {len(itens)} interrompido(s)" + (f"; {REMOCAO}" if itens else ""))
    return 0
