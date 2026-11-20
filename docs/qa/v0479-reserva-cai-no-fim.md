---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 0998e8ab569bf2d5eff92324dc3811365d179ba6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-reserva-cai-no-fim

Revalidação pelo delta 50e06ac6..0998e8ab (hooks/agentes.py, tests/test_agentes_interrompidos.py, tests/mutantes/v0479-reserva-cai-no-fim.json). A1 e A2 da rodada anterior estão fechados: M6 cobre a reserva antiga sem tool_use_id; M8, M9 e M10 cobrem a validação de forma.

## Critério → teste → resultado
Sem especificação de UX; critério = comportamento do brief E60.1 (RESERVA-NAO-CAI-NO-FIM).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fim de um agente solta só a branch dele | FimDoAgente.test_o_fim_de_um_solta_a_branch_dele_e_nao_a_do_outro_vivo | dois agentes do mesmo tipo | passou, vermelho na base |
| Agente sem reserva própria não leva a de outro disparo | test_agente_sem_reserva_propria_nao_leva_a_de_outro_disparo | reserva alheia | passou, vermelho na base |
| Sem meta no início, o fim solta a própria | test_sem_meta_no_inicio_o_fim_ainda_solta_a_reserva_do_proprio_agente | meta ausente | passou, vermelho na base |
| Sem tool_use_id vale o id de antes | test_sem_tool_use_id_vale_o_id_de_antes | registro antigo | passou |
| Reserva antiga sem tool_use_id casa no início (M6) | test_reserva_antiga_sem_tool_use_id_casa_no_inicio | compatibilidade | passou |
| Reserva do próprio disparo vem antes da antiga (M7) | test_reserva_do_proprio_disparo_vem_antes_da_antiga_sem_tool_use_id | ordem | passou, vermelho na base |
| tool_use_id do disparo fora da forma não entra (M8) | test_tool_use_id_do_disparo_fora_da_forma_nao_entra_na_reserva | forma: vazio, número, `../` | passou |
| agent_id fora da forma não lê o meta (M9) | test_agent_id_fora_da_forma_nao_le_o_meta | forma do id | passou |
| toolUseId do meta fora da forma cai na ordem (M10) | test_tool_use_id_do_meta_fora_da_forma_deixa_o_casamento_pela_ordem | forma: texto, número, None | passou |
| Fim sem agent_id não solta nada (M12) | test_fim_sem_agent_id_nao_solta_reserva_nenhuma | id ausente | passou |

## Cenários e resultado real
- test_agentes_interrompidos (39) e test_hooks_agentes* (10): OK, local; sem suíte inteira (vale o check-run `bateria` do CI).
- Vermelho: `forge-testes --vermelho ed5bfa02 --modulos test_agentes_interrompidos`: `vermelho: base=ed5bfa0284c3 head=0998e8ab569b módulos=test_agentes_interrompidos (restrito por --modulos)`; `prova (asserção)=4`, `não prova (passa na base)=35`. Os testes de forma (M8, M9, M10), M6 e M12 passam na base porque as guardas já existiam ou são de regressão; a prova deles é o mutante, que morre (abaixo).
- `forge-mutante tests/mutantes/v0479-reserva-cai-no-fim.json --base 50e06ac6`: `base=50e06ac60ee54707c6a089a2b6e9a261fd649150 mb=50e06ac60ee54707c6a089a2b6e9a261fd649150 rev=0998e8ab569bf2d5eff92324dc3811365d179ba6`; M1, M3, M4, M5, M6, M7, M8, M9, M10, M11, M12 morreram, rc 0.
