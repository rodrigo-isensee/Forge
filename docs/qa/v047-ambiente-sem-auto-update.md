---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: 413a922444228ca83ac7842f1cdcab8db66bf75c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.154, por delta)

Código testado 413a9224, base befd4cca, delta desde 4baba3c5 (parecer anterior, reprovado): só `tests/test_reval_delta.py`, que registra a citação nova em `CITACOES_CONHECIDAS`. Os demais commits do intervalo são pareceres e junções.

## Achados
- A5 (bloqueante) tests/test_ambiente_sem_auto_update.py:17 · fechado: `CITACOES_CONHECIDAS` ganhou `("tests/test_ambiente_sem_auto_update.py", "README.md"): (1, "teste-le")`; `test_reval_delta` passa e as partes 3/3 do CI estão verdes no head.
- A4 (recomendado) README.md:51 · segue fechado (sem `trabalho-em-paralelo` no README).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orientação ao dono no README e no modelo | `AmbienteSemAutoUpdate.test_orientacao_ao_dono_no_readme_e_no_modelo` | frase exata nos 2 arquivos | passou |
| Nenhuma regra perdida | `tests.test_forge.TetoPorPr` | frase do teto | passou |
| Citação de caminho de texto só como a lista conhece (A5) | `test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` | citação nova em teste | passou |
| Modelo de projeto íntegro | `tests.test_modelos_projeto` | n/a | passou |

## Cenários e resultado real
- Vermelho antes do verde: o único teste novo só confere presença de frase; o vermelho do A5 foi provado no parecer anterior (falha determinística no head 5e6e245e) e some com o delta. Mutação não se aplica (sem lógica nova).
- `bateria (pareceres)` falhava no run 43589234529 por causa do parecer anterior reprovado; este parecer o substitui.

## Provas
- `python3 -m unittest tests.test_reval_delta tests.test_ambiente_sem_auto_update tests.test_forge.TetoPorPr tests.test_modelos_projeto` -> Ran 31 tests, OK
- CI do PR 545, run 43589234529 (413a9224): `suíte (python 3.12 e 3.14, partes 1/3 a 3/3)` success; só `bateria (pareceres)` falhou, pelo parecer anterior.
