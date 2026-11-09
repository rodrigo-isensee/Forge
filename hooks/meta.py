#!/usr/bin/env python3
"""Forge: objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão.

Stop, com objetivo armado (`forge-check meta --armar <pedido> --checagem "<cmd>"...`, estado em .forge/run/meta.json):
- **espera o dono**: o pedido está em `## Aguardando o dono` do KANBAN.md ou a última linha do dono no pedido é uma
  `PERGUNTA AO DONO` sem `DECISÃO DO DONO` depois; o Stop passa e o objetivo fica armado.
- **entregue e provado**: toda checagem (sem shell, até CHECAGEM_S cada) sai com rc 0; o Stop passa e o objetivo se desarma.
- **ainda não**: bloqueia o Stop dizendo as checagens que falharam. REPETICOES_PARA_PAUSAR "ainda não" iguais seguidos
  pausam o objetivo sozinho (o Stop passa, `pausado` no meta.json): não fica em laço.
Sem objetivo armado, nada muda. Erro interno: libera e vai ao erros.log.
"""
import datetime
import re
import subprocess
from pathlib import Path

from _comum import bloquear, executar, gravar_json, ler_json

CHECAGEM_S = 60
REPETICOES_PARA_PAUSAR = 4


def agora():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def secao(texto, titulo):
    m = re.search(r"^## " + re.escape(titulo) + r"\s*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    return m.group(1) if m else ""


def ler(caminho):
    try:
        return Path(caminho).read_text(encoding="utf-8")
    except (OSError, ValueError):
        return ""


def espera_o_dono(raiz, pedido):
    """O pedido aguarda o dono: no painel do KANBAN.md ou com PERGUNTA AO DONO sem DECISÃO DO DONO depois."""
    if re.search(r"(?<![\w/.-])" + re.escape(pedido) + r"(?![\w/.-])", secao(ler(raiz / "KANBAN.md"), "Aguardando o dono")):
        return True
    linhas = [l for l in ler(raiz / "docs" / "pedidos" / f"{pedido}.md").splitlines() if re.match(r"\s*(?:- )?(PERGUNTA AO|DECISÃO DO) DONO", l)]
    return bool(linhas) and "PERGUNTA AO DONO" in linhas[-1]


def falhas(raiz, checagens):
    """As checagens (argv) que não saíram com rc 0, como texto."""
    saida = []
    for argv in checagens:
        try:
            rc = subprocess.run(argv, cwd=raiz, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=CHECAGEM_S).returncode
        except (OSError, subprocess.TimeoutExpired):
            rc = "erro"
        if rc != 0:
            saida.append(f"`{' '.join(argv)[:80]}` (rc={rc})")
    return saida


def avaliar_meta(hook, raiz):
    arquivo = hook.run() / "meta.json"
    meta = ler_json(arquivo, None)
    if not isinstance(meta, dict) or not meta.get("armado") or meta.get("pausado"):
        return
    pedido, checagens = str(meta.get("pedido", "")), [c for c in meta.get("checagens", []) if isinstance(c, list) and c]
    if espera_o_dono(raiz, pedido):
        gravar_json(arquivo, {**meta, "estado": "espera o dono", "repeticoes": 0, "ultimo": None, "em": agora()})
        return
    falhou = falhas(raiz, checagens)
    if not falhou:
        gravar_json(arquivo, {**meta, "armado": False, "estado": "entregue e provado", "repeticoes": 0, "em": agora()})
        return
    repeticoes = meta.get("repeticoes", 0) + 1 if meta.get("ultimo") == falhou else 1
    if repeticoes >= REPETICOES_PARA_PAUSAR:
        gravar_json(arquivo, {**meta, "pausado": True, "estado": "pausado", "repeticoes": repeticoes, "ultimo": falhou, "em": agora()})
        return
    gravar_json(arquivo, {**meta, "estado": "ainda não", "repeticoes": repeticoes, "ultimo": falhou, "em": agora()})
    bloquear("R-PROVA", f"objetivo do pedido {pedido} ainda não entregue ({repeticoes}/{REPETICOES_PARA_PAUSAR}): falharam "
                        + "; ".join(falhou) + ". Corrija e pare de novo; se espera o dono, registre a PERGUNTA AO DONO.")


def principal(hook):
    if hook.campo("hook_event_name") != "Stop":
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)
    if not raiz:
        return
    avaliar_meta(hook, raiz)


if __name__ == "__main__":
    executar("meta", principal)
