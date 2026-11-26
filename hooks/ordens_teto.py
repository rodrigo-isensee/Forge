#!/usr/bin/env python3
"""Forge: ordens_teto (RECIBO-CONTADOR-PELO-HOOK, item 4; v0481 E20.11) - recusa gravar as ordens em vigor acima do teto.

PreToolUse de Write, Edit e MultiEdit: quando o alvo é o arquivo de ordens em vigor que o hook `ordens` lê (o mesmo
`fontes` dele: no projeto, `.forge/ordens/ordens-em-vigor.md` da cópia principal; no clone do Forge,
`~/.forge-contrib/docs/ordens/ordens-em-vigor.md`), monta o texto que ficaria gravado e o conta como o `ordens` conta
(`escapadas` e `no_teto`, fonte única). Acima de 15 linhas ou 2000 caracteres: saída 2, com as contagens, em vez de o
`ordens` cortar o fim depois. Outro arquivo, outra ferramenta, fora de projeto do Forge, Edit cujo trecho não está no
arquivo (a ferramenta falha sozinha) e a gravação que não cresce um arquivo já acima do teto (a correção aos poucos):
silêncio e saída 0. Erro interno: silêncio, saída 0 e uma linha no erros.log
(ADR 0003, item 4). Não cobre a gravação pelo Bash (o `conformidade` já a reserva ao Jarvis). Só biblioteca padrão."""
import os
from pathlib import Path

from _comum import bloquear, executar
from ordens import TETO_CARACTERES, TETO_LINHAS, escapadas, fontes, ler_ordens, no_teto

FERRAMENTAS = ("Write", "Edit", "MultiEdit")
RECUSA = ("{nome} ficaria com {linhas} linhas e {caracteres} caracteres, acima do teto de {teto_linhas} linhas e "
          "{teto_caracteres} caracteres; o hook ordens cortaria o fim. Corrigir: encurte ou junte ordens antes de gravar")


def alvo(hook):
    """(caminho do arquivo de ordens, base) se a ferramenta grava nele; senão None."""
    caminho = hook.campo("tool_input", "file_path")
    if not isinstance(caminho, str) or not caminho:
        return None
    pedido = os.path.realpath(hook.cwd() / caminho)
    for arquivo, base, _ in fontes(hook.raiz):
        if os.path.realpath(arquivo) == pedido:
            return arquivo, base
    return None


def trocar(texto, edicao):
    """O texto depois de uma edição (old_string, new_string, replace_all), ou None se o trecho não está nele. O trecho
    vazio sobre o texto vazio (arquivo ausente ou vazio) cria o arquivo com o new_string, como a ferramenta."""
    velho, novo = edicao.get("old_string"), edicao.get("new_string")
    if not isinstance(velho, str) or not isinstance(novo, str):
        return None
    if not velho:
        return novo if not texto else None
    if velho not in texto:
        return None
    return texto.replace(velho, novo) if edicao.get("replace_all") is True else texto.replace(velho, novo, 1)


def depois(hook, arquivo, base):
    """O texto que a ferramenta gravaria, ou None (não se sabe: a ferramenta falha ou o arquivo não se lê)."""
    entrada = hook.campo("tool_input")
    if hook.campo("tool_name") == "Write":
        conteudo = entrada.get("content")
        return conteudo if isinstance(conteudo, str) else None
    texto = ler_ordens(arquivo, base) if os.path.lexists(arquivo) else ""
    edicoes = entrada.get("edits") if hook.campo("tool_name") == "MultiEdit" else [entrada]
    if texto is None or not isinstance(edicoes, list):
        return None
    for edicao in edicoes:
        texto = trocar(texto, edicao) if isinstance(edicao, dict) else None
        if texto is None:
            return None
    return texto


def tamanho(linhas):
    return len("\n".join(linhas))


def nao_cresce(linhas, arquivo, base):
    """O arquivo já passa do teto (gravado fora das ferramentas) e o novo texto não tem mais linhas nem mais caracteres:
    a correção aos poucos passa; o `ordens` segue cortando com o aviso até caber."""
    antes = ler_ordens(arquivo, base)
    if antes is None:
        return False
    anteriores = escapadas(antes)
    return len(linhas) <= len(anteriores) and tamanho(linhas) <= tamanho(anteriores)


def principal(hook):
    if hook.campo("hook_event_name") != "PreToolUse" or hook.campo("tool_name") not in FERRAMENTAS:
        return
    if hook.projeto(hook.cwd(), clone_do_forge=True) is None:
        return
    achado = alvo(hook)
    texto = depois(hook, *achado) if achado else None
    if texto is None:
        return
    linhas = escapadas(texto)
    if no_teto(linhas)[1] is None or nao_cresce(linhas, *achado):
        return
    bloquear("R-CONFORMIDADE", RECUSA.format(nome=Path(achado[0]).name, linhas=len(linhas),
                                             caracteres=tamanho(linhas), teto_linhas=TETO_LINHAS,
                                             teto_caracteres=TETO_CARACTERES))


if __name__ == "__main__":
    executar("ordens_teto", principal)
