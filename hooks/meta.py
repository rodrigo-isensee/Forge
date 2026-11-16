#!/usr/bin/env python3
"""Forge: objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão.

Stop, com objetivo armado (`forge-check meta --armar <pedido> --checagem "<cmd>"...`, estado em .forge/run/meta.json):
- **espera o dono**: o pedido está em `## Aguardando o dono` do KANBAN.md ou a última linha do dono no pedido é uma
  `PERGUNTA AO DONO` sem `DECISÃO DO DONO` depois; o Stop passa e o objetivo fica armado.
- **entregue e provado**: toda checagem (sem shell, até CHECAGEM_S cada) sai com rc 0; o Stop passa e o objetivo se desarma.
- **ainda não**: bloqueia o Stop dizendo as checagens que falharam. REPETICOES_PARA_PAUSAR "ainda não" iguais seguidos
  pausam o objetivo sozinho (o Stop passa, `pausado` no meta.json): não fica em laço.
Sem objetivo armado, nada muda. S6: em todo Stop, só MEDE (nunca bloqueia) a última mensagem ao dono (o campo
last_assistant_message do evento; sem ele, o transcrito): caracteres contra TETO_DA_MENSAGEM, as palavras da tabela "Em vez de"
de skills/modo-iniciante/SKILL.md e, por classe de CLASSES_DE_JARGAO (diretriz 31), quantos termos sem explicação há fora de
bloco de código e de citação; grava uma linha em .forge/run/mensagens.jsonl (só contagens e as palavras da tabela, nunca o
texto nem o termo achado das classes). Erro interno: libera e vai ao erros.log.
"""
import datetime
import json
import os
import re
import subprocess
from pathlib import Path

from _comum import PLUGIN, bloquear, caminhos_extra, executar, gravar_json, ler_json

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


def ambiente_das_checagens(hook, raiz):
    """0.45.4: o ambiente do hook com as pastas de `caminhos_extra` (.forge/config.json) no fim do PATH, como o
    `.githooks/pre-push`: a checagem acha a ferramenta da stack mesmo quando o agente abre sem o PATH do terminal. A pasta que
    não passa na conferência fica de fora, com aviso no erros.log."""
    pastas, avisos = caminhos_extra(raiz)
    for aviso in avisos:
        hook.registrar_escape(aviso)
    ambiente = dict(os.environ)
    if pastas:
        ambiente["PATH"] = os.pathsep.join(filter(None, [ambiente.get("PATH", ""), *pastas]))
    return ambiente


def falhas(raiz, checagens, ambiente=None):
    """As checagens (argv) que não saíram com rc 0, como texto. `ambiente`: o do processo (com o PATH dos `caminhos_extra`)."""
    saida = []
    for argv in checagens:
        try:
            rc = subprocess.run(argv, cwd=raiz, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=CHECAGEM_S, env=ambiente).returncode
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
    falhou = falhas(raiz, checagens, ambiente_das_checagens(hook, raiz))
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
TABELA = re.compile(r"^\|\s*Em vez de\s*\|.*\n\|[-|: ]+\|\n((?:[ \t]*\|.*\n)+)", re.M)


def jargao():
    """As palavras da coluna "Em vez de" da tabela de skills/modo-iniciante/SKILL.md (fonte única); [] sem a tabela."""
    try:
        linhas = TABELA.search(ler(PLUGIN / "skills" / "modo-iniciante" / "SKILL.md").replace("  |", "|")).group(1).splitlines()
    except AttributeError:
        return []
    return [p.strip() for linha in linhas for p in linha.strip().strip("|").split("|")[0].split(",")]


def ultima_mensagem(transcrito):
    """O texto da última mensagem do assistente (com texto) no transcrito JSONL, lido do fim (até LEITURA_MAXIMA bytes)."""
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
            textos = [c["text"] for c in obj["message"]["content"] if c["type"] == "text"] if obj["type"] == "assistant" else []
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        if textos:
            return "\n".join(textos)
    return None


# Classes de jargão (diretriz 31; desenho em docs/arquitetura/visao-de-foco.md, seção 5.3): fonte única das expressões.
CLASSES_DE_JARGAO = {
    "etapa": re.compile(r"(?<![\w.])E\d+\.\d+(?![\w.])"),
    "commit": re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])"),
    "regra": re.compile(r"(?<![\w-])R-[A-Z]{3,}(?![\w-])"),
    "cartao": re.compile(r"(?<![\w-])[A-Z]{2,}[A-Z0-9]*(?:-[A-Z0-9]+)+(?![\w-])"),
    "ferramenta": re.compile(r"(?<![\w/-])(?:forge-[a-z][\w-]*|(?:gh|git) [a-z][\w-]*)|(?:^|(?<=`))forge [a-z][\w-]*", re.M),
    "caminho": re.compile(r"(?<![\w/.-])[\w.-]*/[\w./-]*\.(?:md|py|json|sh)(?![\w-])"),
}
EXPLICACAO = re.compile(r"[^\n(.!?]{0,60}\(\s*[^)\s]")  # parêntese com texto em até 60 caracteres, na mesma frase


def fora_de_codigo_e_citacao(texto):
    """As linhas da mensagem fora de bloco de código cercado e de citação (>): o que entra na conta das classes."""
    linhas, em_codigo = [], False
    for linha in texto.splitlines():
        if linha.lstrip().startswith("```"):
            em_codigo = not em_codigo
        elif not em_codigo and not linha.lstrip().startswith(">"):
            linhas.append(linha)
    return "\n".join(linhas)


def explicado(texto, inicio, fim):
    """O termo vem seguido de parêntese com texto (até 60 caracteres) ou precedido de "o que é" na mesma frase."""
    frase = re.split(r"[.!?\n]", texto[:inicio])[-1]
    return bool(EXPLICACAO.match(texto, fim)) or "o que é" in frase.lower()


def classes_de_jargao(texto):
    """Por classe, quantos termos sem explicação; só as classes achadas (nunca o termo)."""
    texto = fora_de_codigo_e_citacao(texto)
    contagem = {nome: sum(not explicado(texto, m.start(), m.end()) for m in padrao.finditer(texto))
                for nome, padrao in CLASSES_DE_JARGAO.items()}
    return {nome: n for nome, n in contagem.items() if n}


def mensagem_ao_dono(hook):
    """A mensagem final do evento (last_assistant_message); o transcrito só sem ela, que ali pode faltar a final (D13)."""
    texto = hook.campo("last_assistant_message")
    if isinstance(texto, str) and texto.strip():
        return texto
    return ultima_mensagem(hook.campo("transcript_path"))


def medir_mensagem(hook):
    for texto in filter(None, [mensagem_ao_dono(hook)]):
        achados = sorted({p for p in jargao() if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", texto, re.I)})
        linha = {"em": agora(), "caracteres": len(texto), "teto": TETO_DA_MENSAGEM, "passou_do_teto": len(texto) > TETO_DA_MENSAGEM,
                 "jargao": achados, "classes": classes_de_jargao(texto), "iniciante": hook.iniciante()}
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
