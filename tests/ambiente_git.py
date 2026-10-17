"""Ponto único do ambiente de git dos testes: sem manutenção automática.

O git recente dispara `maintenance run --auto --detach` (e o `gc --auto`) depois de um commit; o repack em segundo plano
escreve (`maintenance.lock`, tmp de pack) enquanto o tearDown apaga o repositório temporário, e o `rmtree` falha, só em
worktree. Todo teste que roda `git` num repositório temporário monta o ambiente por `sem_manutencao()`; o teste
`test_ambiente_git.py` falha se um módulo de tests/ chamar `git` sem ele.

Limite: no push para um repositório local, o git limpa `GIT_CONFIG_COUNT`/`GIT_CONFIG_PARAMETERS` antes de chamar o
`receive-pack` do outro lado, então as chaves do ambiente não chegam ao repositório que recebe. Todo repositório bare
criado por um teste chama `remoto_sem_manutencao()` logo depois do `init --bare`/`clone --bare`, que grava as mesmas
chaves no config dele; `test_ambiente_git.py` também confere isso."""
import os
import subprocess

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


def remoto_sem_manutencao(repositorio):
    """Grava as chaves de `CONFIGURACAO` no config local de `repositorio` (o que recebe push): o `receive-pack` não
    herda as `GIT_CONFIG_*` do ambiente. Sem as `GIT_*` herdadas (um hook exporta `GIT_DIR`, que venceria o `-C` e
    gravaria no repositório real) e sem config global e de sistema."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    for chave, valor in CONFIGURACAO:
        subprocess.run(["git", "-C", str(repositorio), "config", chave, valor], env=sem_manutencao(env),
                       check=True, capture_output=True, text=True, timeout=30)
