"""Forge: decisão óbvia por regra fixa (orkastery 3, 0.44.2). Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um destes roda:
- `decisoes registrar --pedido P --porta "<o quê>" --criterio <R-X|docs/...|ADR n> --fato "<fato>" --porque ... --como-mudar ...
  --custo-reverter ... --irreversivel sim|nao --dinheiro sim|nao --escopo sim|nao --alternativas-piores sim|nao
  --reversivel sim|nao --erro-barato sim|nao`: o decisor lê SÓ os fatos (nunca o objetivo nem a conversa). Porta fechada
  (irreversível, dinheiro, escopo/produto) ou condição que falta (critério escrito, alternativas piores, reversível, erro barato
  e detectável) vira pergunta ao dono (rc 1); as quatro de pé, decidida (rc 0) e a linha `decidido:` sai pronta para o commit.
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
from pathlib import Path

REGISTRO = Path("docs") / "kanban" / "decisoes-obvias.jsonl"
PORTAS_FECHADAS = ("irreversivel", "dinheiro", "escopo")  # sempre do dono
CRITERIO_ESCRITO = re.compile(r"(R-[A-Z0-9-]{2,40}|ADR \d{1,4}|docs/[\w./-]{3,120})")
SEP = " — "
LINHA_DECIDIDO = re.compile(r"^\s*(?:- )?decidido:")
FORMA_DECIDIDO = re.compile(r"^\s*(?:- )?decidido: (\S.{0,200}?) — (" + CRITERIO_ESCRITO.pattern + r") — (\S.{0,300})$")
TETO_DO_CAMPO = 300


def decidir(*, irreversivel, dinheiro, escopo, criterio, alternativas_piores, reversivel, erro_barato):
    """O decisor: só os fatos, por nome (não há parâmetro para objetivo nem conversa; um a mais é TypeError).
    Devolve ("decidida", None) ou ("pergunta", motivo)."""
    for nome, valor in (("irreversivel", irreversivel), ("dinheiro", dinheiro), ("escopo", escopo)):
        if valor is not False:
            return "pergunta", f"porta fechada: {nome}"
    if not (isinstance(criterio, str) and CRITERIO_ESCRITO.fullmatch(criterio.strip())):
        return "pergunta", "falta critério escrito (R-*, ADR n ou docs/...)"
    for nome, valor in (("alternativas_piores", alternativas_piores), ("reversivel", reversivel), ("erro_barato", erro_barato)):
        if valor is not True:
            return "pergunta", f"condição não atendida: {nome}"
    return "decidida", None


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
    fatos = {n: _sim_nao(getattr(a, n)) for n in PORTAS_FECHADAS + ("alternativas_piores", "reversivel", "erro_barato")}
    faltam += [n for n, v in fatos.items() if v is None]
    if faltam:
        print("decisoes: registrar: falta ou inválido (sim|nao): " + ", ".join("--" + n.replace("_", "-") for n in faltam))
        return 2
    resultado, motivo = decidir(criterio=_campo(a.criterio), **fatos)
    regs = ler_registro(raiz)
    ident = f"D{len(regs) + 1:04d}"
    _acrescentar(raiz, {"id": ident, "hora": agora, "pedido": _campo(a.pedido), "resultado": resultado, "motivo": motivo,
                        "o_que": _campo(a.porta), "criterio": _campo(a.criterio), "fato": _campo(a.fato), "porque": _campo(a.porque),
                        "como_mudar": _campo(a.como_mudar), "custo_reverter": _campo(a.custo_reverter)})
    if resultado == "decidida":
        print(f"decisoes: decidida {ident}")
        print(linha_decidido(_campo(a.porta), _campo(a.criterio), _campo(a.fato)))
        return 0
    print(f"decisoes: pergunta ao dono {ident}: {motivo}")
    return 1
