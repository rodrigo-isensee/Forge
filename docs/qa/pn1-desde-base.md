---
tipo: qa
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: 23a66bb075998d91fd4ca94642ad9f32d0ec6180
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn1-desde-base (volta 1)

Escopo: `base_sha_como_desde` serve ao `desde_e_a_base` (`forge-check entrega`) e à `mensagem_de_entrega` (`brief mensagem --entrega`), que emite o Base-sha em `Desde:` quando a última `conferida` está fora do head (P-N1; `R-PROVA` sem afrouxar). Base-sha 99315cf, head 23a66bb. Diff conferido contra o pedido: nenhum escopo novo.

## Achados
- A1 (recomendado) bin/forge-check:4692 · com `conferida` fora do head e uma linha "base do delta fixada pelo dono" mais recente, a mensagem emite o Base-sha e não a base do dono (amplia o intervalo, direção segura; sem teste do caso).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: sem conferida, Base-sha vale como Desde | DesdeNoBaseSha.test_sem_conferida_o_base_sha_vale_como_a_branch_inteira | Histórico sem conferida | passou |
| E1: branch nova depois de squash | DesdeNoBaseSha.test_conferida_de_branch_anterior_fora_do_head_aceita_o_base_sha | linha do dono não conta como conferida | passou |
| E1: conferida ancestral do head segue sendo o Desde | DesdeNoBaseSha.test_com_conferida_no_historico_o_base_sha_segue_recusado | não afrouxa R-PROVA | passou |
| E1: branch que não nasce do Base-sha recusada | DesdeNoBaseSha.test_branch_que_nao_nasce_do_base_sha_segue_recusada | Base-sha não ancestral | passou |
| Volta 1: mensagem emite Base-sha com conferida fora do head | DesdeNaBranchNova.test_conferida_fora_do_head_da_o_base_sha | conferida fora do head | passou |
| Volta 1: conferida ancestral segue sendo o Desde | DesdeNaBranchNova.test_conferida_ancestral_do_head_segue_sendo_o_desde | última conferida no head | passou |
| Volta 1: sem conferida, comportamento de hoje (inclui base do dono) | DesdeNaBranchNova.test_sem_conferida_fica_o_comportamento_de_hoje | sem conferida | passou |

## Execução real
- `python3 -m unittest tests.test_mensagem_conferente tests.test_conferencia_base_dono` sobre 23a66bb: Ran 42 tests, OK.
- `bin/forge-mutante tests/mutantes/pn1-desde-base.json`, rc=0: M1 a M10 morreram (M1 :1082; M2, M10 :846; M3, M5 :840; M4 :841; M6 :839; M7 :4688; M8 :4692; M9 :4689).
- `bin/forge-mutante --cobertura --base 99315cf`, rc=0: as 6 linhas de guarda mudadas (839, 840, 846, 1082, 4688, 4692) cobertas por M1 a M10 ("declarado, não provado"); li o diff e nenhuma condição mudada ficou sem mutante.
- Vermelho: `bin/forge-testes --vermelho 4749f3ef4cea2c9487571eb6dc9d348ab7b2e855 --modulos test_mensagem_conferente`, rc=0: `vermelho: base=4749f3ef4cea head=23a66bb07599`, revertido à base `bin/forge-check`; `test_conferida_fora_do_head_da_o_base_sha` H=ok B=falha, "prova (asserção)"; contagem: não prova (passa na base)=13; prova (asserção)=1. Os outros dois testes novos da classe passam na base por guardarem comportamento preservado (regressão), não a regra nova.
- PA-7 conferido: nenhum item de `docs/engineering/achados-recorrentes.md` se repete (AR-1: lista de mutantes cobre as linhas mudadas; AR-2 n/a).
