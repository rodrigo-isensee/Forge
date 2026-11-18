#!/usr/bin/env python3
"""Forge: índice do Forge (arquivo, o que faz e os testes que o cobrem), para o brief citar em vez de colar trechos (H7).

Uso: indice-forge.py              grava docs/indice-forge.md a partir de bin/, hooks/ e scripts/
     indice-forge.py --conferir   não grava; rc 1 se o arquivo não está em dia (o teste do índice usa o mesmo texto)

Os arquivos são os versionados (`git ls-files`) de bin/, hooks/ e scripts/. "O que faz" é a primeira linha da docstring
do módulo (Python) ou do primeiro comentário depois do shebang (shell). Os testes são o plano dirigido do
`bin/forge-testes` para o arquivo sozinho (mapa, convenção de nome e quem importa o hook), sem os oráculos do portão,
que entram em todo plano. Só biblioteca padrão; o índice só lê.
"""
import ast
import functools
import importlib.machinery
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
INDICE = Path("docs/indice-forge.md")
PASTAS = ("bin", "hooks", "scripts")
MAXIMO_DO_TEXTO = 160
MAXIMO_DE_TESTES = 6


def celula(texto):
    """Texto numa célula de tabela Markdown: sem quebra de linha e sem `|` solto."""
    return " ".join(str(texto).split()).replace("|", "\\|")


def carregar_testes(raiz):
    """O `bin/forge-testes` da raiz como módulo, com a leitura dos textos dos testes guardada (é a mesma em todo arquivo)."""
    carregador = importlib.machinery.SourceFileLoader("forge_testes_do_indice", str(raiz / "bin" / "forge-testes"))
    spec = importlib.util.spec_from_loader(carregador.name, carregador)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    modulo.textos_dos_testes = functools.lru_cache(maxsize=None)(modulo.textos_dos_testes)
    return modulo


def arquivos(raiz):
    """Os versionados das PASTAS, um nível só, em ordem. Sem as variáveis GIT_* herdadas: o git lê o da raiz (AR-7)."""
    ambiente = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    saida = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "--", *PASTAS],
                           capture_output=True, text=True, check=True, env=ambiente).stdout
    return sorted(c for c in saida.split("\0") if c and len(Path(c).parts) == 2)


def e_python(caminho, linhas):
    return caminho.endswith(".py") or bool(linhas) and linhas[0].startswith("#!") and "python" in linhas[0]


def primeira_linha_de_doc(raiz, caminho):
    """A primeira linha de doc do arquivo, sem o "Forge: " do começo; "—" se não há."""
    texto = (raiz / caminho).read_text(encoding="utf-8", errors="replace")
    linhas = texto.splitlines()
    doc = ""
    if e_python(caminho, linhas):
        doc = (ast.get_docstring(ast.parse(texto)) or "").strip()
    elif linhas and linhas[0].startswith("#!"):
        for linha in linhas[1:]:
            if not linha.startswith("#"):
                break
            if not linha.lstrip("# ").startswith("shellcheck"):
                doc = linha.lstrip("# ")
                break
    doc = celula(doc.split("\n", 1)[0]).removeprefix("Forge: ")
    if len(doc) > MAXIMO_DO_TEXTO:
        doc = doc[:MAXIMO_DO_TEXTO].rstrip() + "…"
    return doc or "—"


def testes_do_arquivo(testes, raiz, caminho):
    """Os módulos do plano dirigido do arquivo, cortados em MAXIMO_DE_TESTES: o da convenção (`test_<nome>`) primeiro,
    depois os que trazem o nome do arquivo, depois os outros, cada grupo em ordem alfabética."""
    modo, modulos = testes.planejar([caminho], raiz)
    if modo != "dirigido":
        return "suíte completa (" + celula("; ".join(modulos)) + ")"
    nome = Path(caminho).stem.lstrip("_").replace("-", "_")
    lista = sorted(set(modulos) - set(testes.oraculos(raiz)),
                   key=lambda m: (m != "test_" + nome, nome not in m, m))
    texto = ", ".join(f"`{m}`" for m in lista[:MAXIMO_DE_TESTES])
    return texto + (f" e mais {len(lista) - MAXIMO_DE_TESTES}" if len(lista) > MAXIMO_DE_TESTES else "") or "—"


def gerar(raiz=RAIZ, lista=None):
    testes = carregar_testes(raiz)
    lista = arquivos(raiz) if lista is None else lista
    linhas = ["# Índice do Forge", "",
              "<!-- Gerado por scripts/indice-forge.py; não edite à mão. Rode o script depois de mudar bin/, hooks/, "
              "scripts/ ou o mapa de testes. -->", "",
              f"Os {len(lista)} arquivos versionados de `bin/`, `hooks/` e `scripts/`: o que cada um faz (a primeira linha "
              "da doc) e os módulos de `tests/` que o cobrem (o plano dirigido do `bin/forge-testes` para o arquivo, sem os "
              "oráculos do portão). A lista inteira de um arquivo: `bin/forge-testes --listar <arquivo>`."]
    for pasta in PASTAS:
        linhas += ["", f"## `{pasta}/`", "", "| Arquivo | O que faz | Testes |", "| --- | --- | --- |"]
        for caminho in (c for c in lista if c.startswith(pasta + "/")):
            linhas.append(f"| `{Path(caminho).name}` | {primeira_linha_de_doc(raiz, caminho)} | "
                          f"{testes_do_arquivo(testes, raiz, caminho)} |")
    return "\n".join(linhas) + "\n"


def main(argv):
    if argv not in ([], ["--conferir"]):
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    texto = gerar(RAIZ)
    destino = RAIZ / INDICE
    if argv:
        em_dia = destino.is_file() and destino.read_text(encoding="utf-8") == texto
        print(f"{INDICE}: {'em dia' if em_dia else 'desatualizado; rode scripts/indice-forge.py'}")
        return 0 if em_dia else 1
    destino.write_text(texto, encoding="utf-8")
    print(f"{INDICE}: gravado")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
