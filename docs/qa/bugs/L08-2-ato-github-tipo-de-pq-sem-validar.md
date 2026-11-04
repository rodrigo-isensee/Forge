# L08-2 - `entrega --etapa ato-github` não valida o tipo da PQ: `(SHA)` não conta como prova de commit (E19)
- Severidade: baixa
- Responsável sugerido: forge:tech-lead (bin/forge-check, provas_do_brief e entrega_ato_github)
- Ambiente: melhoria/lote-l08 @ 874c89e

## Passos para reproduzir
1. Brief com `Tipo: ato-github`, `Branch: —`, e `## Pronto quando` com `- PQ-1 (SHA): o commit` e `- PQ-2 (pr): o PR`.
2. `forge-check entrega p1 --branch — --base develop --base-sha <b> --etapa ato-github --brief <brief>`.

## Resultado esperado
rc 1 (PQ de commit na entrega ato-github).

## Resultado obtido
rc 0; só `confira PQ-2 (pr)`. `PROVAS_DE_COMMIT` compara com minúsculas e a etapa não passa pelo validador de forma do brief (`TIPOS_PROVA`, :4704), que rejeitaria `(SHA)`.

## Evidência
Reproduzido em sessão do QA. Pré-condição: brief com tipo inválido, que `forge-check brief` já recusa antes da delegação; risco baixo.
