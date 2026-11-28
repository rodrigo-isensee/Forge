---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-tempo-a15
commit: 9050109479c1f4850cb5b92256b958f8d0eb08b5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-tempo-a15

Item E2.360 (instância que não fez a entrega). Obrigação de origem: E2.311 e E2.317 do pedido v047 (A15 do TEMPO-A): `forge-check voltas --tempo` com minutos por fase, espera do dono e `nao-medido`, fixture do histórico real anonimizada. Não há especificação de UX; os critérios abaixo (CA-n) vêm desse texto.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 minutos por fase (autor, conferência, review, QA, integração) a partir do histórico real | test_fases_do_historico_real_com_parada_fora_e_ultima_coluna_aberta | linha de parada (`-`) fora; última coluna aberta | passou |
| CA-2 espera do dono separada e fora do processo | test_espera_do_dono_na_mesma_linha_e_fora_do_processo | dono dentro da coluna de validação | passou |
| CA-3 `nao-medido` para fase sem trecho ou aberta, sem zero inventado | test_fase_ainda_aberta_e_nao_medido_e_a_razao_tambem | último movimento aberto | passou |
| CA-4 razão processo ÷ entrega só com autor medido e processo medido | test_so_autor_sem_processo_e_autor_zero_nao_dao_razao | autor 0, sem processo | passou |
| CA-5 minutos das rodadas de brief, `nao-medido` com rodada sem hora | test_rodadas_de_brief_medidas_e_rodada_sem_hora | rodada extra sem hora | passou |
| CA-6 sem `--tempo`, saída anterior inalterada | test_sem_tempo_nao_ha_linha_de_tempo | n/a | passou |
| CA-7 fixture anonimizada | HISTORICO_REAL em tests/test_voltas.py (cartões CARTAO-A..D, shas e PRs ausentes) | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_voltas`: Ran 46, OK (skipped=1; o skip é o teste de permissão de arquivo, já existente, fora do diff).
- Bordas por sonda manual (histórico em `$TMPDIR`): movimento fora de ordem é ordenado; linha com hora inválida ignorada sem Traceback; `--pedido` inexistente rc=1 com mensagem; rc=0 nos demais. Sem erro.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha); não rerrodada aqui.
- Vermelho antes do verde: `forge-testes --vermelho` não devolveu veredito neste ambiente (processo ficou preso na fila da suíte mais de 30 min, sem saída); foi feito à mão, em cópia em `$TMPDIR`: código de `1b88640e` (bin/) com os testes do head, `python3 -m unittest tests.test_voltas.VoltasTempo` -> `Ran 6 tests`, `FAILED (failures=5)`: os 5 testes de comportamento caem na base; o sexto (CA-6, negativo) passa nela por desenho.
- Mutação (`bin/forge-mutante tests/mutantes/v047-tempo-a15.json tests/mutantes/v047-tempo-a15-2.json --processos 3`), rev=9050109479c1: M1 a M14 todos `morreu`, nenhum sobrevivente (linhas 109, 112, 113, 115, 117, 123, 131, 132, 144, 202 de bin/forge_voltas.py e 9787 de bin/forge-check).
- Cobertura (`--cobertura --base 1b88640e...`): todas as condições Python mudadas têm mutante declarado, sem `não coberto` nem `só equivalente`.
- Bugs: nenhum.
