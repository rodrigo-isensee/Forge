"""Forge: arma o objetivo que o hook de Stop (hooks/meta.py) confere (siegard S4, 0.44.2). Só biblioteca padrão.

`forge-check meta --armar <pedido> --checagem "<cmd>" [--checagem ...]` grava .forge/run/meta.json (o mesmo lugar do hook:
`Hook.run()`); `--desarmar` o tira; `--estado` imprime o estado (entregue e provado, espera o dono, ainda não, pausado).
"""
import datetime
import json
import re
import shlex
import sys
from pathlib import Path

PEDIDO = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}")


def pasta_run(raiz):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hooks"))
    try:
        import _comum  # noqa: PLC0415
    finally:
        sys.path.pop(0)
    hook = _comum.Hook("meta")
    hook.raiz = raiz
    return hook.run()


def executar(a, raiz):
    arquivo = pasta_run(raiz) / "meta.json"
    if a.desarmar:
        arquivo.unlink(missing_ok=True)
        print("meta: desarmada")
        return 0
    if a.estado:
        try:
            meta = json.loads(arquivo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print("meta: nenhum objetivo armado")
            return 1
        print(f"meta: pedido={meta.get('pedido')} armado={meta.get('armado')} estado={meta.get('estado', '-')} "
              f"repeticoes={meta.get('repeticoes', 0)}")
        return 0
    try:
        checagens = [shlex.split(c) for c in a.checagem]
    except ValueError:
        checagens = []
    if not PEDIDO.fullmatch(a.armar or "") or not checagens or not all(checagens):
        print("meta: uso `forge-check meta --armar <pedido> --checagem \"<cmd>\" [--checagem ...]` (sem shell; ao menos uma)")
        return 2
    arquivo.write_text(json.dumps({"pedido": a.armar, "checagens": checagens, "armado": True, "repeticoes": 0,
                                   "desde": datetime.datetime.now().astimezone().isoformat(timespec="seconds")},
                                  ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"meta: armada para {a.armar} com {len(checagens)} checagem(ns); o Stop confere")
    return 0
