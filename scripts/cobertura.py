#!/usr/bin/env python3
"""Forge: coletor de cobertura por linha (piso de cobertura, versao-048 E3). Só biblioteca padrão.

O gerador do texto do `sitecustomize.py` que coleta (controles C-3, C-4 e C-6 do modelo de ameaças) e o piso informativo
do CI (0.45.1): o número publica, nunca reprova.

Uso: cobertura.py instalar SITE SAIDA   grava SITE/sitecustomize.py com o coletor (recusa sobrescrever um que não é dele)
     cobertura.py remover SITE          apaga o SITE/sitecustomize.py, só se for o do coletor
     cobertura.py relatorio SAIDA       soma os acertos de SAIDA sobre o Python de bin/, hooks/ e scripts/ e imprime o número
                                        (com GITHUB_STEP_SUMMARY, grava também a tabela no resumo do job); sai 0 sempre que leu
"""
import ast
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MARCA = "# forge-cobertura\n"
PASTAS_MEDIDAS = ("bin", "hooks", "scripts")

# C-4: no topo só sys, os e atexit; nada vai a stdout nem a stderr; toda falha vira contagem no arquivo de acertos.
CORPO = '''_acertos = {}
_estado = {"ligado": False, "motivo": "", "falhas": 0, "chamadas": 0}


def _linha(code, linha):
    try:
        _estado["chamadas"] += 1
        _acertos.setdefault(code.co_filename, set()).add(linha)
    except BaseException:
        _estado["falhas"] += 1
    return _DISABLE


def _ligar():
    global _DISABLE
    m = getattr(sys, "monitoring", None)
    if m is None:
        _estado["motivo"] = "python sem sys.monitoring"
        return
    try:
        m.use_tool_id(m.COVERAGE_ID, "forge-cobertura")
    except ValueError:
        _estado["motivo"] = "id de ferramenta ocupado"
        return
    _DISABLE = m.DISABLE
    m.register_callback(m.COVERAGE_ID, m.events.LINE, _linha)
    m.set_events(m.COVERAGE_ID, m.events.LINE)
    _estado["ligado"] = True


def _gravar():
    try:
        import json
        import secrets
        raiz = _RAIZ + os.sep
        acertos = {}
        for nome, linhas in list(_acertos.items()):
            real = os.path.realpath(nome)
            if real.startswith(raiz):
                acertos[real[len(raiz):]] = sorted(linhas)
        caminho = os.path.join(_SAIDA, f"{os.getpid()}-{secrets.token_hex(8)}.json")
        fd = os.open(caminho, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w") as arquivo:
            json.dump(dict(_estado, acertos=acertos), arquivo)
    except BaseException:
        pass


try:
    atexit.register(_gravar)
    _ligar()
except BaseException:
    _estado["falhas"] += 1
'''


def texto_do_coletor(saida, raiz):
    """O `sitecustomize.py` que anota as linhas executadas sob `raiz` e grava os acertos em `saida` (C-3)."""
    resolvidos = []
    for caminho in (str(saida), str(raiz)):
        if any(c in caminho for c in "\n\r\0"):
            raise ValueError(f"caminho com quebra de linha ou nulo: {caminho!r}")
        resolvidos.append(os.path.realpath(caminho))
    saida, raiz = resolvidos
    return (MARCA + "import atexit\nimport os\nimport sys\n\n"
            f"_SAIDA = {saida!r}\n_RAIZ = {raiz!r}\n_DISABLE = None\n" + CORPO)


def instalar(site, saida, raiz=RAIZ):
    """Grava `site`/sitecustomize.py com o coletor e cria `saida` (700). Recusa atalho e o sitecustomize de outro dono."""
    destino = Path(site) / "sitecustomize.py"
    if destino.is_symlink() or (destino.exists() and not destino.read_text(encoding="utf-8").startswith(MARCA)):
        raise ValueError(f"{destino} existe e não é do coletor")
    Path(saida).mkdir(mode=0o700, parents=True, exist_ok=True)
    destino.write_text(texto_do_coletor(saida, raiz), encoding="utf-8")
    return destino


def remover(site):
    """Apaga o sitecustomize.py do coletor; o de outro dono fica. True se apagou."""
    destino = Path(site) / "sitecustomize.py"
    if destino.is_file() and not destino.is_symlink() and destino.read_text(encoding="utf-8").startswith(MARCA):
        destino.unlink()
        return True
    return False


def e_python(caminho):
    """Arquivo .py, ou sem extensão com shebang de python na primeira linha."""
    if caminho.suffix == ".py":
        return True
    if caminho.suffix or not caminho.is_file():
        return False
    with open(caminho, "rb") as arquivo:
        primeira = arquivo.readline(200)
    return primeira.startswith(b"#!") and b"python" in primeira


def arquivos_medidos(raiz=RAIZ):
    """Os caminhos relativos do Python de bin/, hooks/ e scripts/ (só o primeiro nível), em ordem."""
    raiz = Path(raiz)
    return sorted(str(p.relative_to(raiz)) for pasta in PASTAS_MEDIDAS for p in (raiz / pasta).glob("*")
                  if p.is_file() and not p.is_symlink() and e_python(p))


def _docstring(no):
    return isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str)


def linhas_executaveis(texto):
    """As linhas que abrem um comando (ast.stmt), menos a docstring do módulo, da classe e da função, que não roda."""
    arvore = ast.parse(texto)
    fora = set()
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and corpo and _docstring(corpo[0]):
            fora.add(id(corpo[0]))
    return {no.lineno for no in ast.walk(arvore) if isinstance(no, ast.stmt) and id(no) not in fora}


def somar_acertos(saida):
    """({arquivo relativo: linhas}, processos lidos, processos com o coletor ligado). Arquivo ilegível não conta."""
    acertos, processos, ligados = {}, 0, 0
    for caminho in sorted(Path(saida).glob("*.json")):
        try:
            dados = json.loads(caminho.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(dados, dict) or not isinstance(dados.get("acertos"), dict):
            continue
        processos += 1
        ligados += dados.get("ligado") is True
        for nome, linhas in dados["acertos"].items():
            if isinstance(linhas, list):
                acertos.setdefault(nome, set()).update(x for x in linhas if isinstance(x, int))
    return acertos, processos, ligados


def relatorio(saida, raiz=None):
    """{"por_arquivo": {arq: (cobertas, executáveis)}, "cobertas", "executaveis", "processos", "ligados"}; raiz padrão: RAIZ."""
    raiz = RAIZ if raiz is None else raiz
    acertos, processos, ligados = somar_acertos(saida)
    por_arquivo = {}
    for nome in arquivos_medidos(raiz):
        try:
            executaveis = linhas_executaveis((Path(raiz) / nome).read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            continue
        por_arquivo[nome] = (len(executaveis & acertos.get(nome, set())), len(executaveis))
    return {"por_arquivo": por_arquivo, "cobertas": sum(c for c, _ in por_arquivo.values()),
            "executaveis": sum(e for _, e in por_arquivo.values()), "processos": processos, "ligados": ligados}


def percentual(cobertas, executaveis):
    return f"{100 * cobertas / executaveis:.1f}%" if executaveis else "sem linhas"


def texto_do_relatorio(r):
    """A linha do número e a tabela em Markdown, do arquivo menos coberto ao mais."""
    linha = (f"cobertura informativa: {percentual(r['cobertas'], r['executaveis'])} ({r['cobertas']} de {r['executaveis']} "
             f"linhas em {len(r['por_arquivo'])} arquivos; {r['processos']} processos, {r['ligados']} com o coletor ligado)")
    tabela = ["| arquivo | cobertura | linhas |", "|---|---|---|"]
    for nome, (c, e) in sorted(r["por_arquivo"].items(), key=lambda x: (x[1][0] / x[1][1] if x[1][1] else 1, x[0])):
        tabela.append(f"| `{nome}` | {percentual(c, e)} | {c}/{e} |")
    return linha, "\n".join(tabela)


def main(argv):
    if len(argv) == 3 and argv[0] == "instalar":
        print(f"coletor em {instalar(argv[1], argv[2])}")
        return 0
    if len(argv) == 2 and argv[0] == "remover":
        print("coletor removido" if remover(argv[1]) else "nada a remover")
        return 0
    if len(argv) == 2 and argv[0] == "relatorio":
        linha, tabela = texto_do_relatorio(relatorio(argv[1]))
        print(linha)
        resumo = os.environ.get("GITHUB_STEP_SUMMARY")
        if resumo:
            with open(resumo, "a", encoding="utf-8") as arquivo:
                arquivo.write(f"## Cobertura (informativa, não reprova)\n\n{linha}\n\n{tabela}\n")
        return 0
    print(__doc__.split("\n\n", 2)[-1].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
