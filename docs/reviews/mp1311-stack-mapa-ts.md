---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-stack-mapa-ts
commit: 803c07bf4154f3cb6e5e5315e5bd98509b0d8ba8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: melhorias-de-projeto-1311 (item 10, mapa TypeScript)

Head revisado: 803c07bf (revalidado por delta desde 00cf2d22), classe C, branch `melhoria/mp1311-stack-mapa-ts`. Instância que não fez a entrega.

## Achados
- A1 (recomendado) stacks/node-react/pronto.md:33 · o veredito `sem prova` e o `não verificável` não dizem onde o autor registra a linha; vale apontar o parecer ou o relatório do brief.

## Sondas

## Parecer
Aprovado. A mudança fica só em `stacks/node-react/` (ADR 0001), com teste e fragmento de changelog; sem código de controle, então não há guarda nova nem mutante a declarar. A seção traz mapa (`.ts`/`.tsx` para `.test.*` ou `__tests__/`), prova por stash e três vereditos, com `não verificável` indo ao parecer como pendência. O teste novo `test_vermelho_em_typescript_tem_mapa_e_veredito_explicito` passa (classe `TextosAQ3Stack`, 4 testes OK) e falha com a seção removida (sonda manual: apaguei o título e o bloco, `FAILED (failures=1)`; árvore restaurada). Suíte inteira: CI do PR, não rerrodada. A1 não bloqueia.

## Revalidação (delta 00cf2d22..803c07bf)
Li só `forge-check parecer delta`: `stacks/node-react/pronto.md` e `tests/test_forge.py`. A1 resolvido: o `sem prova` e o `não verificável` vão ao parecer ou, sem parecer, ao relatório do brief. A prova por stash só roda o teste se o `git stash push` criou entrada e faz sempre o `pop`, sem aplicar stash alheio. O teste ganhou os quatro trechos guardados. `tests.test_forge.TextosAQ3Stack`: 4 testes OK. Sem achado novo; segue aprovado.
