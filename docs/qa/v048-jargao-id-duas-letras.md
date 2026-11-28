---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-jargao-id-duas-letras
commit: 51c259f8419594b6b077cc42ae7e15f67106627f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: jargão com ID de regra de duas letras (E13.28)

Refeito numa branch limpa (E13.25, substitui o #966). O patch do head é o mesmo já aprovado no #966: `hooks/meta.py:174` passa de `R-[A-Z]{3,}` a `R-[A-Z]{2,}`, mais o teste novo, a spec de mutantes e o fragmento do changelog. Nada além (`git diff 9479650b..HEAD`: 4 arquivos).

- ci: 51c259f8419594b6b077cc42ae7e15f67106627f verde

## Achados
- A1 (recomendado) tests/mutantes/v048-jargao-id-duas-letras.json:2 · o campo `pedido` da spec é `v048-jargao-id-duas-letras`; o brief pedia `v048`, que é a convenção das demais specs. Não afeta a rodada; ajustar no próximo toque.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.351: `R-QA` conta como regra | `test_regra_de_duas_letras_conta_e_uma_letra_nao` (1ª asserção) | mínimo de 2 letras | passou |
| E2.351: `R-X` e `R-Qa` não contam | mesmo teste (2ª asserção) | uma letra; minúscula | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_meta`: 56 testes, OK.
- `bin/forge-mutante tests/mutantes/v048-jargao-id-duas-letras.json` (spec f0301144e931):
  - M1 · morreu · hooks/meta.py:174 (volta a `{3,}`)
  - M2 · morreu · hooks/meta.py:174 (vira `{1,}`)
- Mutante por linha de guarda mudada: 1 linha mudada (174), 2 mutantes, ambos mortos pela asserção nova, o que prova o teste sem a implementação.
- CI do PR #968 no head 51c259f8: todos os checks concluídos e verdes (bateria passos, pareceres, suíte 1 a 5/5, python 3.14, instalação, catraca, teto de pulados); os "skipping" são os jobs de push na develop.
