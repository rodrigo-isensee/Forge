---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-serie
commit: 2a0bebc2e9924a9fc0335e0d476ed1b0d8b3aa75
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 série de CI (E1.86)

Head `2a0bebc2` na branch `melhoria/v047-ci-serie`, base `b27f6985`. Diff: `.github/workflows/ci.yml` (só comentários), `tests/test_ci_local.py` (guarda e dois testes), fragmento de changelog. Sem PR aberto: não há check-run `bateria` para citar; rodei só o módulo afetado.

## Achados
- A1 (recomendado) tests/test_ci_local.py:403 · os testes dos dois cartões sem mudança de comportamento fixam trechos de comentário do ci.yml; reescrever o comentário derruba o teste. Aceitável: o motivo registrado é o entregável.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CI-GUARDA-PERMISSOES-ENV | test_guarda_de_permissoes_ve_env_do_job_e_token_sem_permissao | valor com espaço no env do job; GH_TOKEN no passo; permissions declarada não acusa | passou |
| CI-GUARDA-PERMISSOES-ENV (job real) | LeituraDosWorkflowsTest (pareceres: só contents: read, sem env) | job pareceres sem env e sem token | passou |
| CI-ATALHO-COMMIT-SO-PARECER | test_gate_do_commit_so_de_parecer_le_o_agregador_e_registra_o_motivo | gate lê o check `bateria` do app github-actions | passou |
| CI-PARECERES-SEM-NEEDS | test_job_pareceres_so_roda_em_pr_e_sem_needs | needs vazio, if só PR | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_ci_local`: Ran 73 tests, OK (5 s).
- Mutação 1 (GH_TOKEN no env do job `pareceres`, sem permissions próprio): morreu em test_pareceres_e_job_proprio_obrigatorio_e_fora_do_caminho_da_suite (a regex antiga não veria; a nova vê). É o vermelho do teste novo.
- Mutação 2 (gate passa a filtrar outro check que não `bateria`): morreu em test_gate_do_commit_so_de_parecer_le_o_agregador_e_registra_o_motivo e nos testes de hash do gate (10 falhas).
- Mutação 3 (`needs` no job `pareceres`): morreu em test_job_pareceres_so_roda_em_pr_e_sem_needs e test_cada_perna_roda_uma_vez_e_a_igual_reaproveita (2 falhas).
- Árvore restaurada após cada mutante (`git status` limpo).

## Julgamento dos dois cartões sem mudança de comportamento
- Atalho do commit só de parecer: manter o gate no agregador está correto. O custo (uma suíte a mais no commit que traz o parecer) não abre merge indevido, e o agregador é o único check que reúne pareceres e suíte e falha fechado. Aceito.
- Job `pareceres` sem needs: manter está correto. Roda em paralelo, custa menos de um minuto, e o `skipped` já é reprovado pelo agregador em PR; `needs` só adiaria o aviso ao autor. Aceito.
