---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/aq3-texto-v2
commit: b18f4ec753a7c76c79c680d0b546950f126c3f01
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: aq3-texto-v2 (versao-033)

Mudança só de texto de agentes e skills; sem interface, API nem código de produção (acessibilidade e E2E: n/a).

## Achados
- A1 (recomendado) tests/test_forge.py:5660 · o npm→pnpm veio do AQ3 original e tem teste próprio (ForgeInit e TextosAQ3Stack); sem pendência.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Arquiteto: gatilhos e afrouxamento | TextosAQ3Arquiteto (2) | lista vazia só com a frase; contagem 1 | passou |
| Coach: marcas, git só leitura, propor/implementar | TextosAQ3AgileCoach (3) | proibição de estimado ausente | passou |
| Stack: parada sem especificação, R-CONFORMIDADE, contrato, pnpm | TextosAQ3Stack (3) | sem `npm run` no pronto | passou |
| UX: frase literal, lido/medido | TextosAQ3Ux (3) | estado nunca aprovado sem frase | passou |
| forge-init com pnpm | ForgeInit.test_stack_padrao | pronto sugerido no CLAUDE.md | passou |

## Cenários e resultado real
- Diff lido contra o merge-base com origin/develop; os testes citam o trecho que o changelog promete.
- Vermelho antes do verde: texto da base mais o teste do head dá 13 falhas (12 testes, com subtestes); o sufixo do pnpm incluso.
- Verde no head b18f4ec753a7c76c79c680d0b546950f126c3f01: TextosAQ3 e ForgeInit, 20 testes OK
- `tests/neutralidade.py` rc=0; `test_conf_escopo` 10 testes OK.
- Mutação e `forge-mutante`: n/a (nada em bin/, hooks/, .githooks/ nem tests/catraca.py).
