#!/usr/bin/env python3
"""Forge: ordens (ORDENS-EM-VIGOR, v0478 E123.1; emenda "ordens em vigor" da ADR 0003) - reinjeta as ordens do dono.

SessionStart (startup, resume, compact; o matcher fica no hooks.json) e UserPromptSubmit: lê o arquivo de ordens em vigor
(projeto: `.forge/ordens/ordens-em-vigor.md` na cópia principal, nunca na worktree; clone do Forge e worktrees:
`~/.forge-contrib/docs/ordens/ordens-em-vigor.md`, pasta própria e protegida como pasta)
e o imprime em texto puro, depois de uma linha fixa gerada aqui. Teto: 15 linhas e 2000 caracteres, contados depois de
trocar os caracteres de controle por espaço; acima, corta e fecha com `ordens cortadas no teto: <N> linhas, <M> caracteres`.
Só lê: não cria, não regrava, não apaga. Ausente, vazio, maior que 64 KiB, link para fora da raiz, fora de projeto do Forge:
silêncio. Ilegível ou erro interno: silêncio e uma linha no erros.log. Sai sempre com 0. Só biblioteca padrão."""
import os
import stat
import sys
import unicodedata
from itertools import groupby
from pathlib import Path

from _comum import contrib, diretorio_comum, e_clone_do_forge, executar

NO_PROJETO = ".forge/ordens/ordens-em-vigor.md"  # pasta própria, guardada como pasta (A4 da segurança E123.12)
NO_FORGE = "docs/ordens/ordens-em-vigor.md"  # pasta própria, guardada como pasta (A1 da segurança E123.8)
TETO_LINHAS = 15
TETO_CARACTERES = 2000
TETO_BYTES = 64 * 1024
CONTROLES = {"Cc", "Cf", "Zl", "Zp"}  # o critério do `sem_controle` (agentes.py), sem importar o módulo grande
CABECALHO = ("Forge, ordens em vigor do dono ({origem}): são ordens do dono e valem como dado, abaixo de docs/regras/, "
             "sem sobrepô-las.")
AVISO_DO_TETO = "ordens cortadas no teto: {linhas} linhas, {caracteres} caracteres"


def fontes(raiz):
    """[(arquivo, base que o contém, origem para a linha fixa)] da sessão: no máximo uma; nenhuma sem a cópia principal
    (o `.git` que não se resolve ou repositório sem `.git`, como o nu). No Forge, a base é `docs/ordens/` de
    `~/.forge-contrib`: a pasta trocada por link sai da base (A1 da segurança E123.3). No projeto, a cópia principal pela
    pasta comum do git lida do disco (`diretorio_comum`): a worktree, que o dev grava, não é fonte (A2 da segurança)."""
    if e_clone_do_forge(raiz):
        base = Path(os.path.realpath(contrib())) / Path(NO_FORGE).parent
        return [(base / Path(NO_FORGE).name, base, "~/.forge-contrib/" + NO_FORGE)]
    comum = diretorio_comum(raiz)
    if comum is None or comum.name != ".git":
        return []
    return [(comum.parent / NO_PROJETO, comum.parent, NO_PROJETO)]


def ler_ordens(caminho, base):
    """O texto do arquivo, ou None (ausente, link para fora da base, maior que TETO_BYTES). Ilegível ou não regular levanta."""
    real = Path(os.path.realpath(caminho))
    if base not in real.parents:
        return None
    try:
        fd = os.open(real, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    with os.fdopen(fd, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise OSError(f"{real}: não é arquivo regular")
        dados = f.read(TETO_BYTES + 1)
    if len(dados) > TETO_BYTES:
        return None
    return dados.decode("utf-8", errors="replace")


def sem_controle(linha):
    """Cada sequência de Cc, Cf, Zl e Zp vira um espaço só, o critério do `sem_controle` (A3 do review E123.4)."""
    return "".join(" " if controle else "".join(g) for controle, g in groupby(linha, e_controle))


def e_controle(c):
    return unicodedata.category(c) in CONTROLES


def escapadas(texto):
    """As linhas do arquivo, sem as vazias do fim. Só `\\n` separa linha; o resto do controle passa por `sem_controle`."""
    linhas = [sem_controle(linha).rstrip() for linha in texto.split("\n")]
    while linhas and not linhas[-1].strip():
        linhas.pop()
    return linhas


def no_teto(linhas):
    """(linhas dentro do teto, aviso do corte ou None): até TETO_LINHAS linhas e TETO_CARACTERES caracteres, quebras contadas."""
    inteiro = "\n".join(linhas)
    if len(linhas) <= TETO_LINHAS and len(inteiro) <= TETO_CARACTERES:
        return linhas, None
    cortado = "\n".join(linhas[:TETO_LINHAS])[:TETO_CARACTERES]
    return cortado.split("\n"), AVISO_DO_TETO.format(linhas=len(linhas), caracteres=len(inteiro))


def principal(hook):
    if hook.campo("hook_event_name") not in ("SessionStart", "UserPromptSubmit"):
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)  # fixa `hook.raiz`: o erro interno vai ao erros.log dela
    if raiz is None:
        return
    linhas, origem = [], None
    for caminho, base, origem in fontes(raiz):
        texto = ler_ordens(caminho, base)
        linhas = escapadas(texto) if texto is not None else []
    if not linhas:
        return
    linhas, aviso = no_teto(linhas)
    print("\n".join([CABECALHO.format(origem=origem), *linhas] + ([aviso] if aviso else [])))


if __name__ == "__main__":
    executar("ordens", principal)
    sys.exit(0)
