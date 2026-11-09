#!/usr/bin/env python3
"""Forge: objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão.

Stop, com objetivo armado (`forge-check meta --armar <pedido> --checagem "<cmd>"...`, estado em .forge/run/meta.json):
- **espera o dono**: o pedido está em `## Aguardando o dono` do KANBAN.md ou a última linha do dono no pedido é uma
  `PERGUNTA AO DONO` sem `DECISÃO DO DONO` depois; o Stop passa e o objetivo fica armado.
- **entregue e provado**: toda checagem (sem shell, até CHECAGEM_S cada) sai com rc 0; o Stop passa e o objetivo se desarma.
- **ainda não**: bloqueia o Stop dizendo as checagens que falharam. REPETICOES_PARA_PAUSAR "ainda não" iguais seguidos
  pausam o objetivo sozinho (o Stop passa, `pausado` no meta.json): não fica em laço.
Sem objetivo armado, nada muda. S6: em todo Stop, só MEDE (nunca bloqueia) a última mensagem ao dono do transcrito: caracteres
contra TETO_DA_MENSAGEM e as palavras da tabela "Em vez de" de skills/modo-iniciante/SKILL.md; grava uma linha em
.forge/run/mensagens.jsonl (só contagens e as palavras achadas, nunca o texto). Erro interno: libera e vai ao erros.log.
"""
import datetime
import json
import re
import subprocess
from pathlib import Path

from _comum import PLUGIN, bloquear, executar, gravar_json, ler_json

CHECAGEM_S = 60
REPETICOES_PARA_PAUSAR = 4
TETO_DA_MENSAGEM = 1200  # caracteres da mensagem ao dono (S6, só medida)
LEITURA_MAXIMA = 4 * 1024 * 1024  # bytes lidos do fim do transcrito


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


# ---- S6: medida da mensagem ao dono ----
def jargao():
    """As palavras da coluna "Em vez de" da tabela de skills/modo-iniciante/SKILL.md (fonte única)."""
    palavras = []
    for linha in ler(PLUGIN / "skills" / "modo-iniciante" / "SKILL.md").splitlines():
        m = re.match(r"\s*\|\s*([^|]+?)\s*\|\s*[^|]+\|\s*$", linha)
        if m and m.group(1) not in ("Em vez de",) and not set(m.group(1)) <= set("-: "):
            palavras += [p.strip() for p in m.group(1).split(",") if p.strip()]
    return palavras


def ultima_mensagem(transcrito):
    """O texto da última mensagem do assistente no transcrito JSONL (lido do fim, até LEITURA_MAXIMA bytes)."""
    try:
        with open(transcrito, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - LEITURA_MAXIMA))
            linhas = f.read().decode("utf-8", errors="replace").splitlines()
    except (OSError, TypeError, ValueError):
        return None
    for linha in reversed(linhas):
        try:
            obj = json.loads(linha)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("type") == "assistant":
            conteudo = (obj.get("message") or {}).get("content")
            textos = [c.get("text", "") for c in conteudo if isinstance(c, dict) and c.get("type") == "text"] if isinstance(conteudo, list) else []
            if textos:
                return "\n".join(textos)
    return None


def medir_mensagem(hook):
    texto = ultima_mensagem(hook.campo("transcript_path"))
    if texto is None:
        return
    achados = sorted({p for p in jargao() if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", texto, re.I)})
    linha = {"em": agora(), "caracteres": len(texto), "teto": TETO_DA_MENSAGEM, "passou_do_teto": len(texto) > TETO_DA_MENSAGEM,
             "jargao": achados, "iniciante": hook.iniciante()}
    with open(hook.run() / "mensagens.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def principal(hook):
    if hook.campo("hook_event_name") != "Stop":
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)
    if raiz is None:
        return
    try:
        medir_mensagem(hook)
    except Exception as erro:  # noqa: BLE001 - S6 só mede: a falha da medida nunca troca a decisão do Stop
        hook.registrar_erro(erro)
    avaliar_meta(hook, raiz)


if __name__ == "__main__":
    executar("meta", principal)
