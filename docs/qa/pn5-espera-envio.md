---
tipo: qa
contrato: 1
pedido: pn5-espera-envio
branch: melhoria/pn5-espera-envio
commit: bb8a670fa24f0d64acfc641d8f3a6288cc30734f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn5-espera-envio

Escopo (pedido PN5-ESPERA-ENVIO, E1 e E2): regra 4 e seção "O envio longo" da skill `esperar-estado`, texto do tech-lead (linha 21) e do `docs/fechamento-integrador.md` (linha 28), testes novos. Sem gatilho de segurança (`R-SEGURANCA`): texto de skill e de agente, sem hook. O pedido não traz `CA-n` em EARS; as obrigações são os itens E1 e E2 e o cartão BG-MORRE-TURNO.

## Achados
- A1 (recomendado) docs/fechamento-integrador.md:28 · a mudança do fechamento-integrador (cita a skill, espera pelo `rc=`) não tem teste nem mutante: se o texto voltar a "espere a notificação", nada cai.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 laço sai na hora com rc=0 | LacoDoLog.test_envio_que_passa_sai_na_hora | log com rc=0 sem esperar (0 sleeps) | passou; vermelho na base |
| E1 laço sai com rc=1 e mostra | LacoDoLog.test_envio_que_falha_sai_e_mostra_rc_1 | falha do envio vira rc=1 | passou; vermelho na base |
| E1 sem a linha, fim=teto | LacoDoLog.test_log_sem_rc_sai_no_teto_depois_de_17_voltas | log vazio: 17 voltas, código 1 | passou; vermelho na base |
| E1 teto abaixo de 600 s | LacoDoLog.test_laco_do_log_dentro_do_teto | voltas x intervalo <= 540 | passou; vermelho na base |
| E1 tech-lead espera no mesmo turno, sem turno com envio pendente | test_forge.EsperaDoPushEVerificadores.test_push_de_codigo_em_segundo_plano | texto antigo "notificação" ausente | passou |
| E1 fechamento-integrador cita a skill | nenhum | n/a | sem teste (A1, recomendado) |

## Cenários e resultado real
- `python3 -m unittest tests.test_esperar_estado tests.test_forge.EsperaDoPushEVerificadores` sobre bb8a670: 15 testes, OK.
- Vermelho: `bin/forge-testes --vermelho cfc2734e8b1ebf196ec42eba086d80d48348f50f --modulos test_esperar_estado`, rc=0: `vermelho: base=cfc2734e8b1e head=bb8a670fa24f módulos=test_esperar_estado`; `contagem: não prova (passa na base)=9; prova (asserção)=4`; os 4 testes de LacoDoLog com `H=ok · B=falha · prova (asserção)`.
- Mutação: `bin/forge-mutante tests/mutantes/pn5-espera-envio.json`, rc=0: M1 morreu (SKILL.md:43), M2 morreu (SKILL.md:38), M3 morreu (SKILL.md:43), M4 morreu (tech-lead.md:21). Conferência contra o diff: a spec cobre as quatro guardas de comportamento (saída no rc=, rc=1 na falha, teto de 17 voltas, texto do tech-lead); a linha do fechamento-integrador é texto, sem guarda (A1).
- `bin/forge-mutante --cobertura --base cfc2734e8b1ebf196ec42eba086d80d48348f50f`: saída só com a linha `base=… mb=… rev=…`, sem condição Python sem mutante.
- Itens de PA-7 conferidos: teste de lista com mínimo (blocos achados em número exato, um laço e um lançamento); sem `skip`; sem espera fixa (o `sleep` é falso no teste).
