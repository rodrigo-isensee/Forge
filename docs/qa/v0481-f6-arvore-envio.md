---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: dcd4003c3bbb728d86c2e16a9df0aefad46a2036
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E32.30, #932, F6: o envio na develop pula a suíte com a árvore provada no PR)

- ci: dcd4003c3bbb728d86c2e16a9df0aefad46a2036 verde

Volta 1 (delta 1567d509..dcd4003c). `gh pr checks 932` no head: verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, suíte 3.12 partes 1 a 5, teto de pulados e `árvore já provada na develop`; fora `bateria`, `bateria (pareceres)` e `catraca` (esperam parecer ou rótulo). Os jobs do push na develop saem `skipping`.

A1 resolvido: a cobertura lista as linhas L145 a L232 de `arvore-testada.py` como `coberta` (specs -3 a -6); só `não coberto: .github/workflows/ci.yml` (YAML, coberto pelas AE-M9 a M12). A2 resolvido: AE-M19 (`behind`) morre; o falso da API usa `pull_requests: []` como a API real (teste `ProvaDoPr`, linha 231).

## Critério → teste → resultado
O pedido não traz `CA-n` para o corte do envio; a obrigação é a decisão do dono do F6 e o A1 da segurança do #929 (prova do run do ci.yml do próprio PR, base develop, compare, job `bateria` na última tentativa).
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Prova completa (PR mesclado, mesma árvore, run verde) pula a suíte | `ProvaDoPr.test_pr_mesclado_com_a_mesma_arvore_e_o_run_do_pr_verde_prova` | n/a | passou |
| Run mais recente decide (vermelho depois do verde reprova; verde depois do vermelho prova) | `test_o_run_mais_recente_verde_prova_apesar_de_um_anterior_vermelho`, AE-M5 | tentativa e ordem dos runs | passou |
| Falha fechada: fork, outra base, PR não mesclado, sem número, outra árvore, job ausente, duplicado, pulado, de outro sha ou run | `test_qualquer_falta_da_prova_roda_a_suite_inteira` | vazio, duplicado, tipo | passou (Q4 a Q9 morreram) |
| Ambiente ausente ou de tipo errado não lança | `test_ambiente_sem_campo_ou_com_tipo_errado_nao_prova_e_nao_lanca`, AE-M13 | vazio, tipo | passou |
| Fora do push na develop do próprio ci.yml não lê a API | `test_fora_do_push_na_develop_do_proprio_ci_nao_le_a_api` | evento, ref, workflow | passou (Q1 a Q3 morreram) |
| Casos de abuso A1 (check solto, outro workflow, run de fork) | `test_casos_de_abuso_do_parecer_de_seguranca_a1`, AE-M1 a M8 | origem da prova | passou |
| Fiação do ci.yml: needs, `if` por `provada`, agregador exige skipped nas duas só com prova, token só no passo | `FiacaoDoCI.test_f6_arvore_envio_*`, `test_agregador_da_develop_*`, AE-M9 a M12 | permissões mínimas, `-I` | passou |
| rc do `--do-pr` (0 só com prova) | `test_prova_completa_sai_0_e_usa_o_token`, `test_sem_prova_sai_1_e_a_suite_roda` | rc | passou |

## Cenários e resultado real
- Vermelho antes do verde: `bin/forge-testes --vermelho 11fc1867d8165dbc00ec2d9322d2df0dec93aa6a --modulos test_arvore_testada,test_suite_partes` rc=0, linha `vermelho: base=11fc1867d816 head=1567d5094521 módulos=test_arvore_testada,test_suite_partes (restrito por --modulos)`; contagem: não prova (passa na base)=76; prova (API ausente)=7; prova (asserção)=6. Nenhum teste cai no HEAD.
- Mutantes do autor: `bin/forge-mutante tests/mutantes/v0481-f6-arvore-envio.json tests/mutantes/v0481-f6-arvore-envio-2.json tests/mutantes/v0481-f6-arvore-envio-3.json --processos 3`: AE-M1 a AE-M13 todos `morreu` (13 de 13).
- Cobertura: `bin/forge-mutante --cobertura --base 11fc1867d8165dbc00ec2d9322d2df0dec93aa6a` lista `não coberto: .github/workflows/ci.yml` e as linhas `sem mutante` do A1, mais `por quê · arvore-testada.py:199 · AE-M6 · a troca sai do nó da condição`.
- Mutantes do QA (spec própria, 10 trocas nas guardas do A1, rodada sobre commit local descartado): Q1 a Q9 `morreu`; Q10 `sobreviveu` (`scripts/arvore-testada.py:165`, `ahead/identical` mais `behind`).
- Leitura do diff (ci.yml): `arvore-envio` com `actions: read` e `pull-requests: read`, token só no passo da prova, `python3 -I`, falha fechada em erro de API; agregador exige `ARVORE=success` e, sem prova, partes e pulados `success`. Sem defeito achado.
- Acessibilidade e E2E de produto: n/a (CI e script).

## Revalidação (volta 1)
- `python3 -I tests/test_arvore_testada.py`: 31 testes, OK.
- `bin/forge-mutante --processos 4` nas specs -1, -4, -5, -6: AE-M1 a M8 e M14 a M35 todos `morreu`, rc=0 (a spec -5 inteira e o AE-M1 rodados aqui). Specs -2 e -3 (AE-M9 a M13): `morreu`, rc=0. Total 35 de 35, nenhum sobrevivente.
- `forge-mutante --cobertura --base 11fc1867`: sem `sem mutante` em guarda Python; `docs/protecao-de-branch.md` conferido contra o código (head_sha e head_branch, base do PR, fork não prova).
