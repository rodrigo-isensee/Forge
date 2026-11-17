---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-evals-ambiente-git
commit: e02adc7b6f6ed83ac3c0a9bcf7b4adba0aa59a3e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.203, item E2.197 evals-ambiente-git)

Parecer completo (não havia parecer anterior), classe T, instância que não fez a entrega. Diff `4138445e...438838fe`: `tests/ambiente_git.py` (+6), `tests/evals/test_regressao_forma.py` (+18 −6), fragmento `changelog.d/v047-evals-ambiente-git.md`. 30 linhas de código e teste, dentro da orientação M14; um comportamento só.

## O que foi conferido
- Escopo (E2.197): `RaizSintetica.rodar` passa a chamar o forge-check com `-I` e sem `GIT_*` herdadas; `FragmentoDoChangelog.git` e `.conferir` usam o mesmo apoio. Nada além do pedido.
- `sem_git_herdado` tira toda `GIT_*` (inclusive `GIT_CONFIG_COUNT/KEY/VALUE` herdadas) antes de `sem_manutencao`, e os pares de `extra` entram depois do filtro: as chaves de autor e de config do teste sobrevivem. Ponto único em `ambiente_git.py`, coerente com o contrato do módulo.
- Teste de comportamento do ramo de falha: `AmbienteGitHerdado` roda um caso de cada classe sob `GIT_DIR`/`GIT_WORK_TREE=/nonexistent`; restaura o ambiente por `mock.patch.dict`.
- Suíte: a completa fica no CI do PR (`R-REVIEW`); rodei só o módulo do item e o mutante (abaixo).
- Sem lint Python configurado no CI; forma fica como recomendação.
- AR-4 (teste herda o ambiente) voltou neste pedido: linha atualizada em `docs/engineering/achados-recorrentes.md`.

Execuções neste head:
- `python3 -m unittest tests.evals.test_regressao_forma` → `Ran 31 tests ... OK`.
- `GIT_DIR=/nonexistent python3 -m unittest ...AmbienteGitHerdado ...FragmentoDoChangelog` → `Ran 4 tests ... OK`.
- Mutante: filtro `if not k.startswith("GIT_")` trocado por `if True` em `tests/ambiente_git.py:48` → `AmbienteGitHerdado` `FAILED (failures=1)` (morto; restaurado).
- Teste novo sobre o código da base `4138445e` → `FAILED (failures=1)`: falha antes, passa depois.

## Revalidação (E2.227)
Delta lido: `forge-check parecer delta docs/reviews/v047-evals-ambiente-git.md`, intervalo `438838fe..2a223953`. No domínio só `docs/engineering/achados-recorrentes.md`: AR-4 de `vezes: 2` para `vezes: 3`, `última: tests/evals/test_regressao_forma.py:64` (linha de `sem_git_herdado` em `rodar`, conferida). É a linha AR que este review mandou gravar; nenhum código nem teste mudou. Aprovação mantida no head 2a223953.

## Revalidação (E2.568)
Delta lido: `forge-check parecer delta docs/reviews/v047-evals-ambiente-git.md`, intervalo `2a223953..e02adc7b` (junção da develop). No domínio só `docs/engineering/achados-recorrentes.md`, vindo da base (AR-1, AR-12 e AR-14 de outros pedidos); `tests/ambiente_git.py`, `tests/evals/test_regressao_forma.py` e o fragmento não mudaram. `python3 -m unittest tests.evals.test_regressao_forma` no head: `Ran 31 tests ... OK`. Aprovação mantida no head e02adc7b.

## Achados
- A1 (recomendado) tests/ambiente_git.py:50 · uma linha em branco antes de `def remoto_sem_manutencao`; em tests/evals/test_regressao_forma.py:355 três antes da classe nova e uma antes de `if __name__` (PEP 8 pede duas). Só forma; ajuste no próximo toque do arquivo.

## Sondas

## Parecer
Aprovado no head 2a223953 (review completo em 438838fe; revalidado por delta). Faz o que o E2.197 pede, com teste que falha na base e mutante do filtro morto. A1 é só forma e não devolve (`R-REVIEW`). A cópia do filtro de `GIT_*` em outros módulos já tem cartão no pedido (histórico de 2026-11-16 05:42) e fica fora deste item.
