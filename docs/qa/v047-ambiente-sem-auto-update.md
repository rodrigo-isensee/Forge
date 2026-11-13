---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: 93deca84eea3d06142d5f31fb7d26db3361d3cd2
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.98, por delta)

Head 93deca84, base afba389e, delta desde bd282fa7. Sem PR aberto: rodei só os testes afetados, em série (máquina com carga).

## Achados
- A3 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:10 · a ORDEM DO DONO 13/11 17:40 veda cortar texto antigo, e 8 linhas da base afba389e foram encurtadas (ex.: "(serializam)", "e traz a `develop` uma vez", "sem travar; pesa o risco"); restaurar a base.
- A2 (recomendado) bin/forge-testes:103 · a ordem da tupla foi corrigida (módulo no fim); sem pendência.

## Evidência do A3
`git diff afba389e HEAD -- skills/trabalho-em-paralelo/SKILL.md` mostra 8 linhas da base trocadas por versões mais curtas (7 delas sem relação com a Retomada); o arquivo passou de 3044 para 3024 bytes mesmo somando a linha Retomada, ou seja, o ganho de espaço veio de texto antigo. `TetoPorPr` e os demais testes de texto só provam presença de frases-chave e passam, então não detectam o corte: o defeito é de ordem do dono, não de teste vermelho.

A1 do parecer anterior (TetoPorPr) fechado: a linha "Tamanho por risco" voltou e o teste passa.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orientação ao dono no README e no modelo | `AmbienteSemAutoUpdate.test_orientacao_ao_dono...` | frase exata nos 2 arquivos | passou |
| Retomada depois de reinício na skill | `AmbienteSemAutoUpdate.test_retomada_depois_de_reinicio...` | "briefs selados" e "sem refazer o feito" | passou |
| Nenhuma regra perdida (M14) | `tests.test_forge.TetoPorPr` | frase do teto e classe única no Jarvis | passou (A1 anterior fechado) |
| Texto existente preservado (ordem 17:40) | leitura do diff contra a base | n/a | **falhou** (A3) |
| Teste novo lido pelo filtro do pre-push | `LEITORES_DE_TEXTO` | módulo na lista | presente |

## Cenários e resultado real
- Outros módulos afetados: `test_jarvis_nucleo` (17), `test_clareza` (9), `test_modelos_projeto` (17) OK.
- Vermelho antes do verde: não rodei `forge-testes --vermelho` (carga alta); o delta não traz teste novo.
- Mutação: não se aplica (a linha de `bin/forge-testes` só reordena um módulo da lista).

## Provas
- `python3 -m unittest tests.test_forge.TetoPorPr` no head 93deca84 -> Ran 3 tests, OK
- `python3 -m unittest tests.test_ambiente_sem_auto_update` -> Ran 2 tests, OK
- `git diff afba389e HEAD -- skills/trabalho-em-paralelo/SKILL.md` -> 8 linhas da base alteradas (A3)
