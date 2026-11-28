"""Forge: leitura única dos arquivos que o `gh api` envia (GH-API-LEITURA-UNICA, 0.47.8 E3.1).

O `gh api` manda ao GitHub o texto dos argumentos e o de arquivos: `-F campo=@arq` (o valor do campo) e `--input arq`
(o corpo, JSON). O hook que procura uma mutação nesse texto tem de ler o mesmo arquivo que o `gh` lê; quando não
prova qual é, a leitura é ilegível e a ação crítica falha fechada (ADR 0009, seção 7). Fonte única para os hooks:
`textos_do_gh_api` (e `expande`, a palavra que o bash expande). Nada de rede nem de git aqui; só o disco, sem esperar
(FIFO) e com teto de bytes.
"""
import json
import os
import stat

TETO_DA_CONSULTA = 64 * 1024  # bytes de cada arquivo de `-F campo=@arq` ou `--input arq` (FILA-27 A2)
EXPANSAO = ("$", "`")  # o que o bash expande (`$( )` é `$`): a palavra deixa de ser caminho literal
# O que o bash pode trocar no caminho antes de o gh o ler: `~` no começo (o hook não sabe se veio entre aspas, que o
# bash não expande, nem depois de `=@`, que ele também não expande) e curinga ou chave (`q[X].json` vira `qX.json`).
INCERTO_NO_CAMINHO = ("*", "?", "[", "{")


def expande(palavra):
    return any(o in palavra for o in EXPANSAO)


def ler_regular(caminho):
    """Até `TETO_DA_CONSULTA` + 1 bytes do arquivo regular `caminho`. Abre sem bloquear e confere o tipo no descritor: o
    que não é arquivo regular (FIFO, dispositivo) dá `OSError` sem esperar o escritor (A-F27-1)."""
    descritor = os.open(caminho, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descritor, "rb") as f:
        if not stat.S_ISREG(os.fstat(f.fileno()).st_mode):
            raise OSError(f"não é arquivo regular: {caminho}")
        return f.read(TETO_DA_CONSULTA + 1)


def textos_do_gh_api(args, pasta):
    """(textos, legível) do `gh api` (`args` depois do `api`, com o `-i` já separado): os argumentos e o texto dos
    arquivos de `campo=@arq` (o que vem depois do `=@`) e de `--input arq` (o nome inteiro: `--input=@q` lê `@q`),
    relativos à pasta (None: desconhecida) e até `TETO_DA_CONSULTA`. Não dá para ler: expansão (`$`, crase) em qualquer
    argumento, `-` (entrada padrão), `~` no começo do caminho, curinga ou chave nele, relativo com a pasta None (`cd` que
    o hook não resolve), arquivo ausente, que não é regular ou acima do teto. O corpo de `--input` vai ao GitHub como
    JSON: lido decodificado (escape `\\uXXXX` no nome), e o que não é JSON não dá para ler (AR-11). O campo de
    `--raw-field c=@a` o gh não lê como arquivo; lido a mais, o hook só fica mais estrito."""
    textos = []
    if any(map(expande, args)):  # A-F27-2: `$( )`, `$VAR` ou crase: o gh recebe outro texto, que o hook não lê
        return textos, False
    for i, a in enumerate(args):
        corpo = a == "--input" or a.startswith("--input=")
        if corpo or "=@" in a:
            arq = (args[i + 1] if i + 1 < len(args) else "-") if a == "--input" else a.split("=" if corpo else "=@", 1)[1]
            if arq == "-":
                return textos, False
            if arq.startswith("~") or any(c in arq for c in INCERTO_NO_CAMINHO):  # o bash pode dar outro nome ao gh
                return textos, False
            if pasta is None and not os.path.isabs(arq):  # A-F27-3 (AR-7): o gh o lê numa pasta que o hook não sabe
                return textos, False
            try:
                dados = ler_regular(os.path.join(pasta or "", arq))
            except OSError:
                return textos, False
            if len(dados) > TETO_DA_CONSULTA:
                return textos, False
            textos.append(dados.decode("utf-8", "replace"))
            if corpo:
                try:
                    textos.append(json.dumps(json.loads(dados), ensure_ascii=False))
                except (ValueError, RecursionError):
                    return textos, False
        textos.append(a)
    return textos, True
