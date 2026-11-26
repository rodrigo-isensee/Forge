---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-fixtures-gerada
commit: de272439995c2476b465f8978cc9430d9c4e2a78
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E18.3, HOOKS-FIXTURES-GERADA, PR #908)

1ª rodada completa. Diff lido contra o merge-base `cfd83b72`: `scripts/indice-fixtures.py`, `docs/hooks-fixtures.md` (regerado), `tests/test_indice_fixtures.py`, `tests/mutantes/v0481-fixtures-gerada.json` e o fragmento `changelog.d/v0481-fixtures-gerada.md`.

## Verificação
- ci: de272439995c2476b465f8978cc9430d9c4e2a78 verde (suíte 3.12 e 3.14 partes 1 a 5, bateria passos e verificações longas, instalação e árvore provada em `pass`; `catraca` e `bateria (pareceres)` esperam os pareceres)
- `python3 -m unittest tests.test_indice_fixtures`: 10 testes, OK.
- `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`; `--detalhe` imprime `# Detalhe das fixtures dos hooks (3603 fixtures)` e não grava.
- `bin/forge-mutante tests/mutantes/v0481-fixtures-gerada.json --base cfd83b72…`: M1 morreu (`scripts/indice-fixtures.py:119`). A spec antiga `v0454-indice.json` segue com os 13 mutantes mortos depois que o código foi para `detalhe()`.
- Tamanho (H1): 31 linhas de código, um comportamento.

## Leitura
- Faz o que a E18.1 pede: o arquivo versionado só tem hooks e prefixos em ordem alfabética, sem número; o detalhe saiu para o `--detalhe`, que só imprime; `--conferir` e o teste "em dia" usam o mesmo `gerar()`. Opções juntas (`--detalhe --conferir`) caem no uso com rc 2, testado.
- O teste dos dois PRs simulados monta um repositório git real com ambiente limpo (`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`) e o script com `-I`; cobre caso em prefixo existente, prefixo novo no mesmo hook e hook novo, e afirma junção limpa e índice em dia.
- O teste de presença afirma mínimo de 10 hooks e compara a lista de prefixos de cada seção com o corpus (item 11 do checklist).
- `tests/test_prepush_unico.py` (IndiceEPulos) segue válido: a fixture `b-1` é prefixo novo sobre `a-1`, então o índice ainda muda e o envio sem regerar ainda reprova.
- O limite declarado no PR (prefixos novos vizinhos no mesmo hook conflitam numa linha) é aceitável: resolve-se regerando, e o caso comum não toca o arquivo. Reversão: reverter o PR.

## Parecer
Aprovado, sem achados.
