"""O `bin/forge-check` por subprocesso, sem recompilar o script a cada chamada (S-SUITE-RAPIDA). Não é módulo de teste.

`python3 bin/forge-check ...` compila as ~8 mil linhas do script em toda chamada (o Python não guarda bytecode do
programa principal): ~0,25 s de CPU por chamada, contra ~0,1 s com o bytecode em `bin/__pycache__/`, o mesmo cache que
os hooks já gravam ao carregar o script (`hooks/_comum.forge_check`). `comando_do_forge_check()` dá o começo da linha de
comando que roda o mesmo arquivo como programa principal: `__name__ == "__main__"`, `sys.argv[0]` e `__file__` com o
caminho do script, `sys.path[0]` com a pasta dele, o mesmo processo novo, ambiente, entrada, saída e código de saída.
Só para o script real do repositório: uma cópia num diretório do teste ganharia um `__pycache__` que o teste não espera.
Os testes de ponta a ponta de cada comando continuam rodando o script direto (`[sys.executable, FORGE_CHECK, ...]`).
"""
import sys
from pathlib import Path

FORGE_CHECK = Path(__file__).resolve().parent.parent / "bin" / "forge-check"

LANCADOR = (
    "import importlib.machinery, importlib.util, os, sys\n"
    "caminho = sys.argv[1]\n"
    "sys.argv = sys.argv[1:]\n"
    "sys.path[0] = os.path.dirname(caminho)\n"
    "carregador = importlib.machinery.SourceFileLoader('__main__', caminho)\n"
    "modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader('__main__', carregador))\n"
    "sys.modules['__main__'] = modulo\n"
    "carregador.exec_module(modulo)\n")


def comando_do_forge_check():
    """O começo da linha de comando (`[python, -c, lançador, caminho]`); os argumentos do forge-check vêm depois."""
    return [sys.executable, "-c", LANCADOR, str(FORGE_CHECK)]
