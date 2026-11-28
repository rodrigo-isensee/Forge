---
tipo: revisao-devops
contrato: 1
pedido: release-0.48.0
branch: melhoria/release-0-48-0
commit: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-28
---
# Review de devops: release-0.48.0 (E2.4), leva contra a main

## Resumo
Na leva `origin/main..74d2a59c` só `.github/workflows/ci.yml` e `catraca.yml` mudam (#948, espera amarela). Nenhum Dockerfile, compose ou IaC. Os checks exigidos `bateria` e `catraca` mantêm o nome exato quando há sucesso ou vermelho; o sufixo " (espera ...)" só aparece com a conferência em success e rc 3 do script (falta parecer ou rótulo), e deixa o check exigido pendente, ainda barrando o merge. Nada custa dinheiro (`R-CUSTO`): o job extra do `catraca` roda em repositório público e nada de runner, cache ou serviço pago entrou.

## Detalhes
- ci: 74d2a59cad1d0edf5b69bdaeb191b3cb9cdef2e6 verde
- Caminho da promoção: o `pareceres` roda em PR; em promoção o script devolve rc 0 e o agregador fica com o nome `bateria` em success. O push na `develop` pula o agregador, como antes.
- Falha fechada: se a API não lê o check do head, ou o último `bateria`/`catraca` do head está verde, pulado, neutro ou em andamento, o passo sai vermelho e o verde velho não vale.
- Menor privilégio: só `checks: read` foi acrescentado, nos jobs que leem os check-runs. O token vai por env só ao `gh api`; o script roda com `env -u TOKEN_DE_LEITURA`. O título do PR entra por env (`PR_TITULO`), sem interpolação em `run:`.
- Ações fixadas por SHA, `timeout-minutes` nos jobs novos, `concurrency` mantida, sem `continue-on-error`, `[skip ci]` ou teste pulado (`R-VERIFY`). Nenhum workflow escreve na `main` (`R-MAIN`).
- Nada foi alterado no ruleset ou na proteção por `gh api` (`R-CONFORMIDADE`); os nomes exigidos seguem os mesmos.
- CI do PR 953 no head: bateria, bateria (pareceres), bateria (passos), bateria (python 3.14), verificações longas, catraca, catraca (conferência), instalação, suíte 1 a 5/5, teto de pulados e árvore já provada na develop, todos pass; os pulados são os jobs de push na `develop`.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:1 · `actionlint` e `zizmor` ausentes nesta estação; os workflows não passaram pelos dois localmente. Instalar por `scripts/preparar-estacao.sh` e conferir antes da próxima mudança em workflow; a leitura manual do diff não achou defeito.
