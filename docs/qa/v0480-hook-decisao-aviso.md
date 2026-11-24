---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: 2ecd153cf6433fab911a286b4fb5bf19ede4cde6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E172.6 (PR #857, hook decisao só avisa)

Obrigação: o hook `decisao` no Stop do Jarvis avisa o usuário (`systemMessage`, saída 0, nunca bloqueia) quando a mensagem traz mais de um grupo de opções ou um grupo sem "Recomendo" (R-DECISAO), pela regra única de `medir_decisoes`; cala nos demais casos.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Dois grupos avisam, só `systemMessage` (ADR 0003) | `test_dois_grupos_de_opcoes_avisam_e_nao_bloqueiam` | limite de 1 grupo; aviso numa linha até 200 caracteres | passou |
| Grupo sem Recomendo avisa | `test_grupo_sem_recomendo_avisa` | grupo único sem recomendação | passou |
| Um grupo com Recomendo cala | `test_um_grupo_com_recomendo_cala` | limite logo dentro da regra | passou |
| Sem opções cala | `test_lista_de_pendencias_sem_opcoes_cala` | texto sem grupo | passou |
| Sem mensagem nem transcrito cala sem erro | `test_sem_mensagem_nem_transcrito_cala_sem_erro` | vazio | passou |
| Sem o campo, lê o transcrito | `test_sem_o_campo_le_a_ultima_mensagem_do_transcrito` | campo ausente | passou |
| Só o Stop | `test_outro_evento_cala` | outro evento | passou |
| Só o Jarvis | `test_sessao_que_nao_e_do_jarvis_cala`, `test_sessao_sem_agent_type_cala` | permissão por papel | passou |
| Fora de projeto do Forge cala | `test_fora_de_projeto_do_forge_cala` | cwd fora | passou |
| Ligado só no Stop, teto 10 s | `test_hooks_json_liga_o_decisao_so_no_stop_com_teto_de_10_s` | ligação e prazo | passou |

## Cenários e resultado real
Local: `test_hook_decisao.py` 11 testes OK. Vermelho (`forge-testes --vermelho 5f1c6e97 --modulos test_hook_decisao`): `vermelho: base=5f1c6e977230 head=2ecd153cf643`, 11 de 11 provam por asserção (H=ok, B=falha). Mutantes (`bin/forge-mutante tests/mutantes/v0480-hook-decisao-aviso.json`): M1 a M6 mortos; M6 morre por erro do teste declarado, que passa sem o mutante (vale como morte). `--cobertura --base 5f1c6e97`: as 6 condições Python mudadas têm mutante; `hooks.json` sai "não coberto" (JSON), guardado pelo teste de ligação. Documentação (`docs/hooks.md`, índice, changelog) conferida no diff. A suíte inteira fica para o check-run `bateria` do CI do PR.
