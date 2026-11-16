---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-ja1
commit: 85e46f8a504097c718bbf6574ef1c7b10f0b592d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (lote JA1 do Jarvis, E2.190)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| RESPOSTA-A-TODA-MENSAGEM-DO-DONO (E2.180) | `test_jarvis_nucleo.RespostaATodaMensagemDoDono` (2 testes) | regra presente na skill e `description` com o gatilho "a cada mensagem do dono"; Jarvis cita a skill | passou |
| ETAPA-SO-APOS-CONFERIR-DEVELOP (E2.180), texto | `test_jarvis_nucleo.EtapaSoAposConferirDevelop` | `git log origin/develop --grep` e "sem delegar" na regra | passou |
| ETAPA-SO-APOS-CONFERIR-DEVELOP, trava no `forge-check brief` (backlog) | `test_erros_por_papel.EtapaJaResolvidaNaDevelop` (controle + `expectedFailure`) | develop sem commit da etapa passa (rc 0); com commit, backlog | passou (controle) / backlog esperado |

## Cenários e resultado real
- Diff 4138445e..85e46f8a: 4 arquivos (skill, 2 testes, fragmento de changelog); sem código de produção, sem hook nem `bin/`; sem mutante de controle exigível.
- `python3 -m unittest tests.test_jarvis_nucleo tests.evals.test_erros_por_papel`: 37 testes, OK (expected failures=2; um é o backlog novo, o outro já vinha da base).
- Vermelho antes do verde: `forge-testes --vermelho 4138445e` ficou sem veredito (rc=124, prazo de 560 s na suíte completa; "o mapa não sabe" para o módulo evals); não vale como vermelho. Feito à mão numa cópia do HEAD com a skill da base: os 3 testes novos de `test_jarvis_nucleo` caem (2 ERROR por regra ausente, 1 FAIL por `description` sem o gatilho); com a skill do HEAD passam.
- Mutação: sem ferramenta para texto de skill; o vermelho à mão faz o papel (trocar a skill pela base derruba os 3 testes).
- Teste novo isolado do ambiente: `develop_com` limpa `GIT_*` herdado (AR-4).
- CI: a suíte inteira roda no check-run `bateria` do PR; este parecer não cita `.verde` local.
- Acessibilidade e E2E: n/a (sem interface).
