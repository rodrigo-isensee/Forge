---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k167-ato-do-dono
commit: b9974f7561240393a660c841699a65fee99064e4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 E74.4 (K167, ato do dono)

Diff contra a base 8caa7f3d: só texto de skill (`skills/ci-cd/SKILL.md`, `skills/modo-iniciante/SKILL.md`) e o fragmento de changelog. Sem código de controle: sem mutantes e sem vermelho-antes-do-verde (nenhum teste novo). Suíte inteira não rodada (fica no CI do PR).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pergunta de ato do dono diz quem aplica (`R-MAIN`, `R-CONFORMIDADE`) | leitura do diff em modo-iniciante:35 | n/a | passou |
| ci-cd lê rulesets além da proteção clássica | leitura do diff em ci-cd:32 | n/a | passou |
| Orçamento e métricas de texto | test_metricas_texto (2), test_orcamento_instrucao (8) | limite de tamanho da instrução | passou |
| Módulos que leem as duas skills | test_clareza (9), test_pergunta_maior_menor (1), test_skills_v0442 (4), test_textos_034 (9), test_qa_doutor_f8 (7), test_modelo_ci (19), test_doutor_protecao_gh (15) | n/a | passou |

Comando: `python3 -I -m unittest discover -s tests -p <modulo>.py`, um por módulo, todos OK.
