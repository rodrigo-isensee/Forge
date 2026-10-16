"""Ponto único do ambiente de git dos testes: sem manutenção automática.

O git recente dispara `maintenance run --auto --detach` (e o `gc --auto`) depois de um commit; o repack em segundo plano
escreve (`maintenance.lock`, tmp de pack) enquanto o tearDown apaga o repositório temporário, e o `rmtree` falha, só em
worktree. Todo teste que roda `git` num repositório temporário monta o ambiente por `sem_manutencao()`; o teste
`test_ambiente_git.py` falha se um módulo de tests/ chamar `git` sem ele."""
import os

CONFIGURACAO = (
    ("maintenance.auto", "false"),
    ("gc.auto", "0"),
    ("receive.autogc", "false"),
)


def sem_manutencao(env=None):
    """Cópia de `env` (padrão: `os.environ`) com as chaves de `CONFIGURACAO` juntadas às que já houver em
    `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`: nenhuma chave do chamador se perde."""
    novo = dict(os.environ if env is None else env)
    existentes = []
    for i in range(int(novo.get("GIT_CONFIG_COUNT") or 0)):
        chave = novo.pop(f"GIT_CONFIG_KEY_{i}", None)
        valor = novo.pop(f"GIT_CONFIG_VALUE_{i}", None)
        if chave is not None and valor is not None:
            existentes.append((chave, valor))
    nossas = {chave for chave, _ in CONFIGURACAO}
    pares = [(c, v) for c, v in existentes if c not in nossas] + list(CONFIGURACAO)
    novo["GIT_CONFIG_COUNT"] = str(len(pares))
    for i, (chave, valor) in enumerate(pares):
        novo[f"GIT_CONFIG_KEY_{i}"] = chave
        novo[f"GIT_CONFIG_VALUE_{i}"] = valor
    return novo
