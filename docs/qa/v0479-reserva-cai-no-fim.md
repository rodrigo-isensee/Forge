---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 50e06ac60ee54707c6a089a2b6e9a261fd649150
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-reserva-cai-no-fim

## Achados
- A1 (bloqueante) hooks/agentes.py:1295 · mutante meu sobrevive: trocar `in (uso, None)` por `== uso` mantém verdes test_agentes_interrompidos e test_hooks_agentes*; o ramo "reserva sem tool_use_id casa" (R-TETO, compatibilidade) não tem teste nem mutante declarado
- A2 (recomendado) hooks/agentes.py:1210 · mutante meu sobrevive: tirar a validação de forma (`USO_DE_AGENTE.fullmatch`) de uso_do_disparo e de uso_do_agente deixa tudo verde; sem teste de id malformado

## Critério → teste → resultado
Sem especificação de UX; critério = comportamento do brief E60.1 (RESERVA-NAO-CAI-NO-FIM).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fim de um agente solta só a branch dele (ids trocados) | FimDoAgente.test_o_fim_de_um_solta_a_branch_dele_e_nao_a_do_outro_vivo | dois agentes do mesmo tipo | passou |
| Agente sem reserva própria não leva a de outro disparo | FimDoAgente.test_agente_sem_reserva_propria_nao_leva_a_de_outro_disparo | reserva alheia | passou |
| Sem meta no início, o fim ainda solta a própria | FimDoAgente.test_sem_meta_no_inicio_o_fim_ainda_solta_a_reserva_do_proprio_agente | meta ausente | passou |
| Sem tool_use_id vale o id de antes | FimDoAgente.test_sem_tool_use_id_vale_o_id_de_antes | registro antigo | passou |
| Reserva antiga sem tool_use_id casa no início | nenhum | compatibilidade | sem teste (A1) |

## Cenários e resultado real
- test_agentes_interrompidos (33) e test_hooks_agentes_autor (10): OK, com TMPDIR; sem suíte local.
- Vermelho: `forge-testes --vermelho ed5bfa02 --modulos test_agentes_interrompidos`: `vermelho: base=ed5bfa0284c3 head=50e06ac60ee5 módulos=test_agentes_interrompidos (restrito por --modulos)`; `prova (asserção)=3`, `não prova (passa na base)=30` (inclui test_sem_tool_use_id_vale_o_id_de_antes, de regressão, esperado).
- forge-mutante v0479-reserva-cai-no-fim.json: M1, M3, M4, M5 morreram, rc 0. v047-h2-autor-fica-2.json: M9 a M16 morreram, rc 0.
- `forge-mutante --cobertura --base ed5bfa02`: condições sem mutante declarado em 1210, 1266, 1269, 1276, 1294, 1295, 1383, 1386. Mutantes meus em cópia em $TMPDIR: `if uso:`→`if False:` morreu; `any(a is p ...)`→filtro por id morreu; validação de forma (1210, 1269) e `in (uso, None)` sobreviveram (A1, A2).
