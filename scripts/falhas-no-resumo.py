#!/usr/bin/env python3
"""Forge: as falhas de uma parte da suíte no resumo do GitHub e em anotações (v047 E2.270).

Uso: python3 -I scripts/falhas-no-resumo.py "<rótulo>" <registro>
Lê o registro do `unittest` (a saída da parte, de `scripts/suite-paralela.py`, de `scripts/suite-partes.py` ou de
`python3 -m unittest`) e escreve:
- no arquivo `$GITHUB_STEP_SUMMARY` (sem a variável, na saída padrão): com falha, uma tabela curta (teste, módulo, linha,
  primeira linha do erro); sem falha, uma linha com a contagem de testes;
- na saída padrão, um `::error file=...,line=...::<teste>: <erro>` por falha (o GitHub mostra as 10 primeiras por passo).
Teto: TETO_TABELA linhas na tabela e TETO_ANOTACOES anotações; o que passa disso vira "e mais N". Só informa: sai sempre
com 0 (o passo da suíte é quem reprova), registro ausente ou ilegível vira uma linha no resumo. Só biblioteca padrão;
nada de rede nem de custo (R-CUSTO). O texto do registro não é confiável: o valor sai sem controle, cortado, sem segredo
e escapado pelas regras dos comandos de workflow (nunca vira comando) e do Markdown (nunca vira tabela quebrada).
"""
import os
import re
import sys
from pathlib import Path

TETO_TABELA = 25
TETO_ANOTACOES = 10
TETO_CELULA = 160
TETO_REGISTRO = 64 * 1024 * 1024
TETO_SOBRAS = 5

CABECALHO = re.compile(r"^(FAIL|ERROR): (\S.*?) \(([A-Za-z_][\w.]*)\)(?: \((.*)\))?\s*$")
QUADRO = re.compile(r'^\s+File "([^"]+)", line (\d+), in (\S+)')
RAN = re.compile(r"^Ran (\d+) tests? in ", re.M)
RAN_PROCESSO = re.compile(r"^Ran (\d+) tests?\s*$", re.M)
SEGREDO = re.compile(r"(?i)(gh[pousr]_\w{20,}|github_pat_\w{20,}|AKIA[0-9A-Z]{12,}|"
                     r"(?:token|senha|secret|password|passwd|chave|api[_-]?key)\w*\s*[=:]\s*\S+)")
SEPARADOR = re.compile(r"^(=|-){20,}\s*$")


def limpar(texto, teto=TETO_CELULA):
    """Sem controle (inclui ESC), sem segredo e cortado em `teto`."""
    texto = SEGREDO.sub("[redigido]", texto)
    texto = "".join(c if c.isprintable() else " " for c in texto).strip()
    return texto if len(texto) <= teto else texto[: teto - 1] + "…"


def celula(texto):
    """Uma célula de tabela Markdown: nada de `|`, crase, `<`, `&` nem `[`, que quebrariam a tabela ou virariam HTML/link."""
    texto = limpar(texto)
    for velho, novo in (("\\", "/"), ("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ("|", "\\|"), ("`", "'"), ("[", "\\[")):
        texto = texto.replace(velho, novo)
    return texto


def escapar_dado(texto):
    """Dado de comando de workflow: `%`, CR e LF escapados (nunca sobra um `::` que um registro possa usar)."""
    return texto.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def escapar_propriedade(texto):
    return escapar_dado(texto).replace(":", "%3A").replace(",", "%2C")


def relativo(caminho, raiz):
    """O arquivo do quadro relativo à raiz do repositório, ou None (fora dela, inexistente ou com `..`)."""
    try:
        p = Path(caminho)
        if p.is_absolute():
            p = p.resolve().relative_to(raiz.resolve())
        if ".." in p.parts or not (raiz / p).is_file():
            return None
        return p.as_posix()
    except (OSError, ValueError, RuntimeError):
        return None


def modulo_do_id(nome, completo):
    """O módulo do teste: o id pontuado sem a classe e o método (`mod.Classe.metodo` -> `mod`, `pkg.mod.Classe` -> `pkg.mod`)."""
    partes = completo.split(".")
    for i, parte in enumerate(partes):
        if parte[:1].isupper():  # a classe: o módulo é o que vem antes
            return ".".join(partes[:i]) or completo
    return ".".join(partes[:-1] if partes[-1] == nome and len(partes) > 1 else partes)


def blocos(texto):
    """Os blocos `FAIL:`/`ERROR:` do registro: (cabeçalho, linhas até o próximo bloco). Aceita o formato do 3.11 e do 3.12+."""
    linhas = texto.splitlines()
    achados, i = [], 0
    while i < len(linhas):
        m = CABECALHO.match(linhas[i])
        if m and i > 0 and SEPARADOR.match(linhas[i - 1]) and SEPARADOR.match(linhas[i - 1]).group(0)[0] == "=":
            fim = i + 1
            while fim < len(linhas) and not (SEPARADOR.match(linhas[fim]) and linhas[fim][0] == "="):
                fim += 1
            achados.append((m, linhas[i + 1: fim]))
            i = fim
        else:
            i += 1
    return achados


def erro_do_bloco(linhas):
    """A primeira linha do erro: a exceção que fecha o traceback (a última da cadeia), nunca o diff da mensagem."""
    erro, antes_recuada = "", False
    for linha in linhas:
        if not linha.strip():
            continue
        recuada = linha[:1] in (" ", "\t")
        if not recuada and antes_recuada and not linha.startswith(("Traceback", "During handling", "The above exception")):
            erro = linha
        antes_recuada = recuada or linha.startswith("Traceback")
    return erro


def local_do_bloco(linhas, raiz):
    """(arquivo, linha) do último quadro dentro de `tests/` ou, sem ele, do último quadro do repositório."""
    quadros = []
    for linha in linhas:
        m = QUADRO.match(linha)
        if m:
            quadros.append((relativo(m.group(1), raiz), int(m.group(2))))
    do_repo = [q for q in quadros if q[0]]
    dos_testes = [q for q in do_repo if q[0].startswith("tests/") or "/tests/" in q[0]]
    escolha = (dos_testes or do_repo or [(None, 0)])[-1]
    return escolha


def falhas(texto, raiz):
    """Lista de dicts (teste, modulo, arquivo, linha, erro, tipo), sem repetir (teste, subteste, local)."""
    vistas, saida = set(), []
    for m, linhas in blocos(texto):
        tipo, nome, completo, sub = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        arquivo, linha = local_do_bloco(linhas, raiz)
        chave = (completo, nome, sub, arquivo, linha)
        if chave in vistas:
            continue
        vistas.add(chave)
        teste = f"{completo}" if completo.endswith("." + nome) else f"{completo}.{nome}"
        saida.append({"teste": teste + (f" ({sub})" if sub else ""), "modulo": modulo_do_id(nome, completo),
                      "arquivo": arquivo, "linha": linha, "erro": erro_do_bloco(linhas) or tipo, "tipo": tipo})
    return saida


def contar(texto):
    """Testes rodados: a soma dos `Ran N tests` (um por processo da suíte; o do `unittest` puro traz ` in <s>s`)."""
    por_processo = [int(n) for n in RAN_PROCESSO.findall(texto)]
    return sum(por_processo) if por_processo else sum(int(n) for n in RAN.findall(texto))


def resumo(rotulo, texto, achadas):
    rotulo = celula(rotulo)
    if not achadas:
        sobras = []
        for linha in texto.splitlines():
            if linha.startswith(("FAILED", "suite-paralela: causa", "suite-partes: causa")) and len(sobras) < TETO_SOBRAS:
                sobras.append(limpar(linha))
        if sobras:
            return [f"### {rotulo}: falhou sem teste identificado", ""] + [f"- {celula(s)}" for s in sobras]
        n = contar(texto)
        return [f"{rotulo}: {n} testes, sem falhas" if n else f"{rotulo}: sem testes no registro"]
    saida = [f"### {rotulo}: {len(achadas)} teste(s) falharam", "",
             "| Teste | Módulo | Linha | Erro |", "|---|---|---|---|"]
    for f in achadas[:TETO_TABELA]:
        onde = f"{f['arquivo']}:{f['linha']}" if f["arquivo"] else "?"
        saida.append(f"| {celula(f['teste'])} | {celula(f['modulo'])} | {celula(onde)} | {celula(f['erro'])} |")
    if len(achadas) > TETO_TABELA:
        saida += ["", f"e mais {len(achadas) - TETO_TABELA} no registro do passo"]
    return saida


def anotacoes(achadas):
    saida = []
    for f in achadas[:TETO_ANOTACOES]:
        props = ""
        if f["arquivo"]:
            props = f" file={escapar_propriedade(f['arquivo'])},line={f['linha']}"
        saida.append(f"::error{props}::{escapar_dado(limpar(f['teste'] + ': ' + f['erro'], 300).replace('::', ': :'))}")
    return saida


def main(argv, ambiente=None, raiz=None):
    ambiente = os.environ if ambiente is None else ambiente
    raiz = Path(raiz or os.getcwd())
    if len(argv) != 2:
        print("uso: falhas-no-resumo.py <rótulo> <registro>", file=sys.stderr)
        return 0
    rotulo, caminho = argv
    try:
        with open(caminho, "rb") as f:
            texto = f.read(TETO_REGISTRO).decode("utf-8", errors="replace")
    except OSError:
        texto = None
    if texto is None:
        linhas, notas = [f"{celula(rotulo)}: sem registro da suíte (o passo anterior não chegou a rodar)"], []
    else:
        achadas = falhas(texto, raiz)
        linhas, notas = resumo(rotulo, texto, achadas), anotacoes(achadas)
    for nota in notas:
        print(nota)
    destino = ambiente.get("GITHUB_STEP_SUMMARY")
    corpo = "\n".join(linhas) + "\n"
    try:
        if destino:
            with open(destino, "a", encoding="utf-8") as f:
                f.write(corpo)
        else:
            sys.stdout.write(corpo)
    except OSError as e:
        print(f"falhas-no-resumo: resumo indisponível ({type(e).__name__})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
