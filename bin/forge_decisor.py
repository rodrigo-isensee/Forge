"""Forge: decisão óbvia por regra fixa (orkastery 3, 0.44.2). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um destes roda:
- `decisoes registrar --pedido P --porta "<o quê>" --criterio <R-X|docs/...|ADR n> --fato "<fato>" --porque ... --como-mudar ...
  --custo-reverter ... --irreversivel sim|nao --dinheiro sim|nao --escopo sim|nao --alternativas-piores sim|nao
  --reversivel sim|nao --erro-barato sim|nao --so-aperta sim|nao --seguranca docs/security/<parecer>.md`: o decisor lê SÓ os
  fatos (nunca o objetivo nem a conversa). Porta fechada (irreversível, dinheiro, escopo/produto) ou condição que falta (critério
  escrito, alternativas piores, reversível, erro barato e detectável; D5 da v0480: só aperta e a confirmação escrita no
  parecer da segurança, regra do dono de 24/11) vira pergunta ao dono (rc 1); todas de pé, decidida (rc 0) e a linha
  `decidido:` sai pronta para o commit. A confirmação (A1 a A3 do #863) é o parecer lido pelo git no HEAD da raiz, igual na
  árvore, com frontmatter `tipo: revisao-seguranca`, `parecer: aprovado`, `revisor: forge:security-engineer` e `pedido:` igual
  ao --pedido, e uma linha própria `Só aperta: <porta>` com a porta do --porta; frase solta no texto não confirma.
  Tudo se grava em docs/kanban/decisoes-obvias.jsonl (o quê, porquê, como mudar, custo de reverter).
- `decisoes reverter --id N --porque ...`: a decisão N foi desfeita; conta no placar.
- `decisoes conferir --mensagem ARQ`: a mensagem de commit com linha `decidido:` fora da forma `<porta> — <critério> — <fato>`
  recusa (rc 1); usado pelo .githooks/commit-msg.
O placar (decididas × perguntas × revertidas) sai no `forge-check metricas` (`placar`).
"""
import datetime
import json
import os
import re
import subprocess
from pathlib import Path

REGISTRO = Path("docs") / "kanban" / "decisoes-obvias.jsonl"
PORTAS_FECHADAS = ("irreversivel", "dinheiro", "escopo")  # sempre do dono
CRITERIO_ESCRITO = re.compile(r"(R-[A-Z0-9-]{2,40}|ADR \d{1,4}|docs/[\w./-]{3,120})")
SEP = " — "
LINHA_DECIDIDO = re.compile(r"^\s*(?:- )?decidido:")
FORMA_DECIDIDO = re.compile(r"^\s*(?:- )?decidido: (\S.{0,200}?) — (" + CRITERIO_ESCRITO.pattern + r") — (\S.{0,300})$")
TETO_DO_CAMPO = 300
CONFIRMACAO = re.compile(r"docs/security/[\w.-]{1,120}\.md")  # D5: o parecer da segurança, sem subpasta
LINHA_SO_APERTA = re.compile(r"Só aperta: (\S.{0,299})")  # A2/A3 do #863: linha inteira, de forma fixa, com a porta
QUEM_CONFIRMA = {"tipo": "revisao-seguranca", "parecer": "aprovado", "revisor": "forge:security-engineer"}
CHAVE_DO_FRONTMATTER = re.compile(r"([a-z_][a-z0-9_]*): ?(.*)")  # a forma do `ler_frontmatter` do forge-check docs
TETO_DA_CONFIRMACAO = 1 << 20


def decidir(*, irreversivel, dinheiro, escopo, criterio, alternativas_piores, reversivel, erro_barato, so_aperta, seguranca):
    """O decisor: só os fatos, por nome (não há parâmetro para objetivo nem conversa; um a mais é TypeError).
    Devolve ("decidida", None) ou ("pergunta", motivo)."""
    for nome, valor in (("irreversivel", irreversivel), ("dinheiro", dinheiro), ("escopo", escopo)):
        if valor is not False:
            return "pergunta", f"porta fechada: {nome}"
    if not (isinstance(criterio, str) and CRITERIO_ESCRITO.fullmatch(criterio.strip())):
        return "pergunta", "falta critério escrito (R-*, ADR n ou docs/...)"
    for nome, valor in (("alternativas_piores", alternativas_piores), ("reversivel", reversivel), ("erro_barato", erro_barato),
                        ("so_aperta", so_aperta), ("seguranca", seguranca)):
        if valor is not True:
            return "pergunta", f"condição não atendida: {nome}"
    return "decidida", None


def _git(raiz, *args):
    """(rc, stdout em bytes) do git na raiz, sem as `GIT_*` herdadas (um `GIT_DIR` venceria o -C); (1, b"") se o git não roda."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, env=env, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        return 1, b""
    return r.returncode, r.stdout


def parecer_no_git(raiz, caminho):
    """A1 do #863: o texto de `caminho` no HEAD do repositório cuja raiz é `raiz`, ou None: raiz que não é a do repositório,
    fora do HEAD, link simbólico ou executável (modo diferente de 100644), acima de 1 MiB, ou com diferença no índice ou na árvore."""
    rc, topo = _git(raiz, "rev-parse", "--show-toplevel")
    if rc != 0 or Path(topo.decode("utf-8", "replace").strip()).resolve() != Path(raiz).resolve():
        return None
    rc, linha = _git(raiz, "ls-tree", "-l", "HEAD", "--", caminho)
    campos = linha.decode("utf-8", "replace").split()
    if rc != 0 or len(campos) != 5 or campos[0] != "100644":
        return None
    if not campos[3].isdigit() or int(campos[3]) > TETO_DA_CONFIRMACAO:
        return None
    if _git(raiz, "diff", "--quiet", "HEAD", "--", caminho)[0] != 0:
        return None
    return _git(raiz, "cat-file", "blob", campos[2])[1].decode("utf-8", "replace")


def frontmatter(texto):
    """(campos, corpo) do frontmatter do topo; (None, "") sem ele, sem o `---` que fecha, com linha fora de `chave: valor` ou
    chave repetida (falha fechada, mais estrito que o `ler_frontmatter` do forge-check, que só anota o erro)."""
    linhas = texto.split("\n")
    if linhas[0].strip() != "---":
        return None, ""
    campos = {}
    for n, linha in enumerate(linhas[1:], 1):
        if linha.strip() == "---":
            return campos, "\n".join(linhas[n + 1:])
        m = CHAVE_DO_FRONTMATTER.fullmatch(linha.rstrip())
        if not m or m.group(1) in campos:
            return None, ""
        campos[m.group(1)] = m.group(2).strip()
    return None, ""


def confirmacao_escrita(raiz, caminho, pedido, porta):
    """D5 (A1 a A3 do #863): True só se `caminho` é `docs/security/<nome>.md` lido pelo git (`parecer_no_git`), com o frontmatter
    da segurança aprovado do mesmo `pedido` e uma linha inteira `Só aperta: <porta>` cuja porta, com os espaços normalizados,
    é a registrada. A frase em qualquer outra forma (pergunta, título, negação, recuo) não confirma."""
    if not (isinstance(caminho, str) and CONFIRMACAO.fullmatch(caminho)):
        return False
    texto = parecer_no_git(raiz, caminho)
    campos, corpo = frontmatter(texto) if texto is not None else (None, "")
    if campos is None or any(campos.get(k) != v for k, v in {**QUEM_CONFIRMA, "pedido": pedido}.items()):
        return False
    return any(m is not None and _campo(m.group(1)) == porta for m in map(LINHA_SO_APERTA.fullmatch, corpo.split("\n")))


def linha_decidido(porta, criterio, fato):
    return f"decidido: {porta}{SEP}{criterio}{SEP}{fato}"


def fora_da_forma(texto):
    """As linhas `decidido:` da mensagem que não seguem `<porta> — <critério> — <fato>`."""
    return [l for l in texto.splitlines() if LINHA_DECIDIDO.match(l) and not FORMA_DECIDIDO.match(l.rstrip())]


def ler_registro(raiz):
    arq = raiz / REGISTRO
    if not arq.is_file() or arq.is_symlink():
        return []
    saida = []
    for linha in arq.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            obj = json.loads(linha)
        except ValueError:
            continue
        if isinstance(obj, dict):
            saida.append(obj)
    return saida


def placar(raiz):
    """{"decididas", "perguntas", "revertidas"} do registro."""
    regs = ler_registro(raiz)
    conta = {"decididas": 0, "perguntas": 0, "revertidas": 0}
    for r in regs:
        chave = {"decidida": "decididas", "pergunta": "perguntas", "revertida": "revertidas"}.get(r.get("resultado"))
        if chave:
            conta[chave] += 1
    return conta


def _acrescentar(raiz, obj):
    arq = raiz / REGISTRO
    if arq.is_symlink() or arq.parent.is_symlink():
        raise OSError(f"{REGISTRO} ou a pasta dele é link simbólico")
    arq.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(arq, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _sim_nao(valor):
    return {"sim": True, "nao": False, "não": False}.get(str(valor).strip().lower())


def _campo(valor):
    return " ".join(str(valor).split())[:TETO_DO_CAMPO]


def executar(a, raiz):
    if a.acao == "conferir":
        try:
            texto = Path(a.mensagem).read_text(encoding="utf-8", errors="replace")
        except (OSError, TypeError):
            print("decisoes: conferir: --mensagem ilegível")
            return 2
        ruins = fora_da_forma(texto)
        for l in ruins:
            print(f"decisoes: recusado: linha `decidido:` fora da forma `<porta> — <critério> — <fato>`: {l.strip()[:200]}")
        return 1 if ruins else 0
    agora = datetime.datetime.now().astimezone().isoformat(timespec="minutes")
    if a.acao == "reverter":
        if not a.id or not _campo(a.porque):
            print("decisoes: reverter pede --id e --porque")
            return 2
        ids = {r.get("id") for r in ler_registro(raiz) if r.get("resultado") == "decidida"}
        if a.id not in ids:
            print(f"decisoes: reverter: decisão {a.id!r} não está no registro como decidida")
            return 1
        _acrescentar(raiz, {"id": a.id, "hora": agora, "resultado": "revertida", "porque": _campo(a.porque)})
        print(f"decisoes: revertida {a.id}")
        return 0
    faltam = [n for n in ("pedido", "porta", "criterio", "fato", "porque", "como_mudar", "custo_reverter") if not _campo(getattr(a, n))]
    fatos = {n: _sim_nao(getattr(a, n)) for n in PORTAS_FECHADAS + ("alternativas_piores", "reversivel", "erro_barato", "so_aperta")}
    faltam += [n for n, v in fatos.items() if v is None]
    if faltam:
        print("decisoes: registrar: falta ou inválido (sim|nao): " + ", ".join("--" + n.replace("_", "-") for n in faltam))
        return 2
    seguranca = str(getattr(a, "seguranca", "")).strip()  # ausente ou None não casa com CONFIRMACAO: vira pergunta
    resultado, motivo = decidir(criterio=_campo(a.criterio), seguranca=confirmacao_escrita(raiz, seguranca, _campo(a.pedido), _campo(a.porta)),
                                 **fatos)
    regs = ler_registro(raiz)
    ident = f"D{len(regs) + 1:04d}"
    _acrescentar(raiz, {"id": ident, "hora": agora, "pedido": _campo(a.pedido), "resultado": resultado, "motivo": motivo,
                        "o_que": _campo(a.porta), "criterio": _campo(a.criterio), "fato": _campo(a.fato), "porque": _campo(a.porque),
                        "como_mudar": _campo(a.como_mudar), "custo_reverter": _campo(a.custo_reverter), "seguranca": _campo(seguranca)})
    if resultado == "decidida":
        print(f"decisoes: decidida {ident}")
        print(linha_decidido(_campo(a.porta), _campo(a.criterio), _campo(a.fato)))
        return 0
    print(f"decisoes: pergunta ao dono {ident}: {motivo}")
    return 1
