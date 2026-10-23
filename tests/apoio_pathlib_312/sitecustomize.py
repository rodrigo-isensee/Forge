"""Falha de caminho igual em toda versão do Python, para os testes de falha fechada dos hooks (FIX-SUITE-LOCAL).

Até a 3.12 (a do CI), `Path.exists`, `is_dir` e `is_file` levantam o `OSError` que não seja ENOENT, ENOTDIR, EBADF ou
ELOOP (pasta sem permissão, nome longo demais); da 3.14 em diante devolvem False para qualquer `OSError`. Os testes
que provocam erro interno no hook por essa via põem esta pasta no `PYTHONPATH` do hook: o Python carrega o
`sitecustomize` na partida e as três funções voltam à semântica da 3.12. Só os testes usam; o hook não muda.
"""
import errno
import os
import pathlib
import stat

_IGNORADOS = {errno.ENOENT, errno.ENOTDIR, errno.EBADF, errno.ELOOP}


def _stat(caminho, seguir):
    try:
        return os.stat(caminho, follow_symlinks=seguir)
    except OSError as erro:
        if erro.errno not in _IGNORADOS:
            raise
    except ValueError:
        pass
    return None


def _exists(self, *, follow_symlinks=True):
    return _stat(self, follow_symlinks) is not None


def _is_dir(self, *, follow_symlinks=True):
    st = _stat(self, follow_symlinks)
    return st is not None and stat.S_ISDIR(st.st_mode)


def _is_file(self, *, follow_symlinks=True):
    st = _stat(self, follow_symlinks)
    return st is not None and stat.S_ISREG(st.st_mode)


pathlib.Path.exists, pathlib.Path.is_dir, pathlib.Path.is_file = _exists, _is_dir, _is_file
