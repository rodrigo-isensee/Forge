"""Repositórios-modelo da suíte (S-SUITE-RAPIDA). Não é módulo de teste.

Muitos testes montam, no setUp, o mesmo repositório de partida (`git init`, `git config`, arquivos e o commit base): cinco
a dez processos do git por teste, repetidos centenas de vezes. Aqui o repositório de partida é montado uma vez por
processo da suíte, numa pasta temporária própria, e cada teste recebe uma cópia (`shutil.copytree`, sem subprocesso). A
cópia é o mesmo repositório: os mesmos objetos, refs, configuração e arquivos; o índice copiado tem outro inode, e o git
relê o conteúdo dos arquivos na primeira leitura, como num clone. O modelo nunca é entregue ao teste: só a cópia.
"""
import atexit
import itertools
import shutil
import tempfile
import threading
from pathlib import Path

_MODELOS = {}
_PASTA = []
_TRAVA = threading.Lock()  # as fixtures de hooks montam em threads (pool): a primeira montagem de cada modelo é uma só
_NUMERO = itertools.count()


def _pasta_dos_modelos():
    if not _PASTA:
        pasta = Path(tempfile.mkdtemp(prefix="forge-modelos-"))
        atexit.register(shutil.rmtree, pasta, True)
        _PASTA.append(pasta)
    return _PASTA[0]


def copiar_modelo(chave, destino, montar):
    """Copia o modelo `chave` para `destino` (pasta inexistente ou vazia) e devolve a pasta do modelo (para quem precisa
    trocar, na cópia, um caminho absoluto que o git gravou). Na primeira vez no processo, `montar(pasta)` monta o modelo
    numa pasta nova; se `montar` falha, o modelo não fica guardado e a falha sobe para o teste."""
    with _TRAVA:
        if chave not in _MODELOS:
            pasta = _pasta_dos_modelos() / f"modelo-{next(_NUMERO)}"
            pasta.mkdir()
            try:
                montar(pasta)
            except BaseException:
                shutil.rmtree(pasta, ignore_errors=True)
                raise
            _MODELOS[chave] = pasta
        modelo = _MODELOS[chave]
    shutil.copytree(modelo, destino, symlinks=True, dirs_exist_ok=True)  # o modelo pronto só é lido: cópias em paralelo
    return modelo
