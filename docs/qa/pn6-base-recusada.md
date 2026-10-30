---
tipo: qa
contrato: 1
pedido: pn6-base-recusada
branch: melhoria/pn6-base-recusada
commit: fab197c47dabb6714cd86b45a93a62b0962f87ce
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn6-base-recusada

Diff conferido (31257c1...fab197c): `bin/forge-check` (regra única `veredito_do_desde`, `ref_da_base`, `recusa_do_desde`, chamada em `gerar_volta`), 3 testes novos, spec de 11 mutantes e fragmento do changelog. PA-7 conferido: sem classe recorrente aberta no diff.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P-N6: base que o `entrega` recusa não gera brief (rc 1, motivo, nada gerado) | test_base_que_o_entrega_recusa_para_o_gerar_sem_brief | base do dono igual à ref (delta zerado) | passou |
| P-N6: Base-sha como Desde vale como no `entrega` | test_base_do_dono_no_base_sha_passa_como_no_entrega | base no limite do Base-sha | passou (regressão, passa também na base) |
| P-N6/A1: Desde gravado na própria entrega recusa nos dois | test_base_gravada_na_propria_entrega_recusa_como_no_entrega | commit em docs/pedidos/ depois da base | passou |
| Sem base no Histórico segue sem recusa | test_volta_por_delta.BriefDeVolta.test_gera_blocos_copiados_decisoes_achados_e_prova | Histórico vazio | passou |

## Cenários e resultado real
- tests.test_conferencia_base_dono e tests.test_volta_por_delta sobre fab197c: 93 testes, OK (rc=0).
- Mutantes (spec M1 a M11): todos morreram, rc=0 (M1 858, M2 1422, M3 863, M4 1419, M5 1419, M6 1480, M7 1425, M8 865, M9 866, M10 1104, M11 860).
- `--cobertura --base 31257c1`: coberta 860 (M11), 1104 (M10), 1419 (M4, M5), 1423 (M2), 1425 (M7), 1480 (M6); `apagada · bin/forge-check:1084(base) · desde is not None` (rc=1 por essa linha): é a guarda movida para :860 (`if desde is None: return`), coberta pelo M11 que morreu; conferido, sem linha de guarda mudada sem mutante.
- Vermelho: `bin/forge-testes --vermelho 31257c14c8d245d66e7806edb7cd65e22b3aeb04 --modulos test_conferencia_base_dono`, rc=0: `prova (asserção)=2` (test_base_gravada_na_propria_entrega_recusa_como_no_entrega e test_base_que_o_entrega_recusa_para_o_gerar_sem_brief: H=ok, B=falha); 29 não provam (passam na base, esperado: herdados e a regressão do Base-sha); nenhum cai no HEAD.
- Sem bug aberto.
