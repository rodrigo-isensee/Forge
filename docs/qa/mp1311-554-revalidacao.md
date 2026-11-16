---
tipo: qa
contrato: 1
pedido: release-0.47.1
branch: melhoria/mp1311-554-revalidacao
commit: 6e837bf759ebc43e4f960d6cf348ef1e42e7d1d4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: release 0.47.1, delta 5b10ba81..6e837bf7 (v047, E2.42)

Revalidação incremental desde 5b10ba81, o head que `docs/qa/release-0.47.1-b.md` aprovou (escopo completo, o resto da release está lá). O delta até 6e837bf7 traz só pareceres: `docs/qa/mp1311-pre-envio-fabrica.md`, `docs/reviews/mp1311-pre-envio-fabrica.md`, `docs/reviews/release-0.47.1-b.md`, `docs/security/release-0.47.1-b.md` e `docs/qa/release-0.47.1-b.md`. Nenhum código, teste, spec de mutante nem changelog mudou, então nada a rodar de vermelho ou mutação. O parecer existe porque o passo 1c da promoção pede parecer da release com a branch de trabalho do sha promovido.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nada fora dos pareceres mudou desde o head aprovado | `forge-check parecer delta docs/qa/release-0.47.1-b.md`: "delta: nenhum arquivo do domínio mudou" | código ou teste entrando sem parecer | passou |
| Formato dos pareceres | `bin/forge-check docs` | frontmatter do parecer | passou (rc=0) |

## Provas
- `forge-check parecer delta docs/qa/release-0.47.1-b.md`: intervalo 5b10ba81..48f028e7, "delta: nenhum arquivo do domínio mudou".
- `git diff --stat 5b10ba81 6e837bf7`: 5 arquivos, todos em `docs/qa`, `docs/reviews`, `docs/security`.
