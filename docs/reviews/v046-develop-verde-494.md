---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/develop-verde-494
commit: 2e8eb8b5165d9b7fac3eab78fbf9c627cdaebf35
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 (E18.5, develop verde)

## Achados

## Sondas

## Parecer
Aprovado. Diff de 3 arquivos (5 linhas de teste, índice gerado, fragmento de changelog); sem código de controle.

- Corte do passo de pareceres (tests/test_catraca.py:2061): o passo `--modo pareceres` é o último do job `bateria`; sem corte o texto ia até o fim do arquivo e o `env` lido era o do job `verificacoes`. O corte em `\n\n  <job>:\n` com `maxsplit=1` fica na fronteira do job; as duas asserções (HEAD_REPO, BASE_REPO) leem agora o env do próprio passo. Alcance igual ou maior, nenhuma guarda perdeu alcance.
- Lista de timeouts com mais um 20: não é afrouxamento. No `ci.yml` da develop (origin/develop), o job `verificacoes` já existe com `timeout-minutes: 20` (veio com o commit 00e6d430, #493); a lista literal do teste estava defasada. A ordem nova (`... bateria 20, verificacoes 20, agregador 5`) bate com a ordem dos jobs; a igualdade segue exata (sem `<=`), então teto subido ou job sem teto ainda reprova.
- docs/hooks-fixtures.md: `scripts/indice-fixtures.py --conferir` retorna "em dia" (rc 0); contagem 2260 e as linhas `pesado` coerentes com o corpus.
- Mutante/guarda: nenhuma guarda de produção mudou (só teste); dispensa `tests/mutantes/`.
- Tamanho: 5 linhas de teste, abaixo de 150.
