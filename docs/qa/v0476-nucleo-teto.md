---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-nucleo-teto
commit: 8a91fe3b46138da9de651979c17a28fa68672a2d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0474 (E3.301, núcleo do Jarvis volta ao teto)

Diff contra a base 038249c5: uma linha de `agents/jarvis.md` (tirou o trecho "(revisão, conserto, teste vermelho)" da frase do teto do time) e o fragmento `changelog.d/v0476-nucleo-teto.md`. Sem código nem teste novo, logo sem vermelho antes do verde nem mutante (nenhuma guarda mudada).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Núcleo dentro do teto (37476 contra 37511) | tests.test_jarvis_nucleo (43) | máximo do núcleo | passou |
| Medição de texto | tests.test_metricas_texto (2) | máximo | passou |
| Orçamento de instrução | tests.test_orcamento_instrucao (8) | máximo | passou |
| Sem sobreposição no quadro | tests.test_sobreposicao_quadro (61) | n/a | passou |
| Regras invioláveis preservadas | tests.test_forge.RegrasInviolaveis (3) | trechos protegidos | passou |

## Cenários e resultado real
Rodados localmente com TMPDIR próprio, só os módulos pedidos; todos OK. A remoção não toca ID de regra nem invariante (R-TETO e R-WIP seguem citados). Suíte inteira: só no CI do PR.
