---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-vermelho-evals
commit: 8b5d4a5f52add0af2856af46e95e748cb069f301
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E48.1 (VERMELHO-TESTS-EVALS)

Base `004ce869`, head `8b5d4a5f`; diff: `bin/forge-testes` (23 linhas), `tests/test_testes_tocados.py` (+5 testes), spec `tests/mutantes/vermelho-tests-evals.json` (M1 a M11, 2 isentas) e fragmento `changelog.d/v0479-vermelho-evals.md`.

## Achados
- A1 (recomendado) bin/forge-testes:785 · `todos` agora vem do `rglob` e confia em `nome_do_modulo`, cuja docstring (l. 406) promete "toda pasta é pacote" sem conferir `__init__.py`; um `tests/fixtures/**/test_*.py` futuro entraria na suíte completa do `--vermelho`. Hoje só há os 3 de `tests/evals/`.

## Sondas

## Parecer
Aprovado. Faz o que a etapa pede: `--modulos` aceita `evals.test_x`, `tests.evals.test_x` e `tests/evals/test_x.py`; o vermelho sem `--modulos` inclui o módulo de pacote do diff; `testes_da_base` e `da_base` leem a base e a chave de `setUpClass`/`setUpModule` pelo nome com pacote. As grafias tortas seguem recusadas (`tests.tests.test_x` pelo `(?!tests\.)` depois de um corte só).

Ferramentas (citadas, sem refazer a suíte; `R-REVIEW`): os 6 testes do item rodados com ambiente limpo, `Ran 6 tests ... OK`; `forge-mutante --ids M8,M9,M10`: os três morreram (l. 746, 743, 783); `forge-mutante --cobertura --base 004ce869`: toda condição mudada coberta ou isenta com motivo. A suíte inteira fica no CI do PR.

Commits: seis, Conventional Commits em português, um comportamento (dentro do teto H1). A1 vira cartão depois do merge.
