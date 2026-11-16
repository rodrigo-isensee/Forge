---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-stack-mapa-ts
commit: 803c07bf4154f3cb6e5e5315e5bd98509b0d8ba8
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: melhorias-de-projeto-1311 (item 10, mapa TypeScript e veredito explícito)

branch: melhoria/mp1311-stack-mapa-ts · head 803c07bf (revalidação por delta de 00cf2d22) · base efe7c9e8. Diff: seção nova em `stacks/node-react/pronto.md`, um teste em `tests/test_forge.py`, fragmento de changelog. Só stack (ADR 0001), sem nome de projeto (R-NEUTRO).

## Achados
- A1 (recomendado) tests/test_forge.py:6886 · o teste só prova que as frases existem na seção; não prova comportamento (nenhum código roda). Aceitável, pois o entregável é texto de stack. `git stash push` e a linha da Prova não têm trecho guardado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Item 10: mapa .ts/.tsx → .test.ts/.test.tsx/__tests__ | `test_vermelho_em_typescript_tem_mapa_e_veredito_explicito` | seção ausente ou duplicada (len == 2) | passou |
| Item 10: veredito explícito, inclusive não verificável | mesmo teste (`veredito: não verificável`, `nunca termina sem veredito`) | n/a | passou |
| Item 10: comando de prova `pnpm vitest run <teste>` | mesmo teste | n/a | passou (ver mutante 4) |

## Cenários e resultado real
- Classe `TextosAQ3Stack` no head: `Ran 4 tests ... OK`.
- Vermelho antes do verde (manual, em cópia de `git archive` em `$TMPDIR`, com o `pronto.md` da base efe7c9e8 e o teste do head): `Ran 1 test ... FAILED (failures=1)`. Com o `pronto.md` do head: OK. `forge-testes --vermelho efe7c9e8` não terminou no prazo (suíte grande, máquina carregada); fica sem veredito da ferramenta, e o vermelho acima é a prova substituta.
- Mutação de texto (cópia, 5 trechos trocados por `x`): `nunca termina sem veredito`, `__tests__/<nome>.test.ts` e `veredito: não verificável` morreram (3/3). `` `pnpm vitest run <teste>` `` sobreviveu porque o trecho aparece 2 vezes no arquivo e o `replace` pegou a ocorrência fora da seção (mutante mal posicionado, não furo provado). `git stash push` sobreviveu (sem guarda, ver A1).
- Conferência: a premissa "forge-testes só mapeia Python" confere (`bin/forge-testes`: `TESTE_DO_DIFF` só `test_*.py`). O texto não pede mudança de código do Forge.
- Suíte inteira: CI do PR (ainda sem PR); não rodada local.
- Acessibilidade/permissões/API: n/a (texto de documentação).

## Revalidação por delta (00cf2d22..803c07bf)
`forge-check parecer delta`: domínio com `stacks/node-react/pronto.md` e `tests/test_forge.py` (E3.6: stash só se criar entrada, pop sempre, `sem prova` e relato ao brief). Sem achado novo; o A1 (trechos sem guarda) foi resolvido: `git stash push`, o pop e `sem prova` ganharam trecho guardado.
- `TextosAQ3Stack` no head: `Ran 4 tests ... OK`.
- Vermelho: `pronto.md` de 00cf2d22 com o teste do head: `FAILED (failures=1)` (`'só se ele criar entrada' not found`); com o do head: OK.
- Mutação de texto na seção (4 trechos novos trocados por `x`, cópia em `$TMPDIR`): 4/4 morreram (`FAILED (failures=1)`).
- A conferência do texto: o `git stash pop` incondicional após o push com entrada fecha o risco de produção presa no stash; o texto não cobre o caso "push sem entrada" além de pular a prova, o que é o pretendido.
- Suíte inteira: CI do PR (ainda sem PR); não rodada local.
