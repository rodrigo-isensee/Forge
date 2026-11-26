---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: 8e9f5704f52b32e0419ab0b7bbc066f17e6f013a
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (CI-NAO-CANCELA-ENVIO-SO-DE-PARECER, E22.8, delta b04f0220..8e9f5704)

## Achados
- A1 (bloqueante) .github/workflows/obsoletas.yml:52 · o job cancela o ci.yml do próprio head: RUN_ID é do obsoletas (id maior que o do ci irmão), então `-lt` o derruba. Provado: ci run 45847608038 (8e9f5704) cancelled pelo bot. Filtrar por head_sha != HEAD_SHA e testar run do mesmo sha com id menor.

## Critério → teste → resultado
Sem `CA-n` de UX; obrigações do brief (E22.1/E22.8).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Envio só de parecer não cancela | test_envio_so_de_parecer_nao_cancela_nada | docs/reviews, docs/qa, docs/security | passou |
| Código cancela só runs mais antigos | test_envio_com_codigo_cancela_so_os_runs_mais_antigos | id < RUN_ID | passou (ver A1: o RUN_ID do fake não reproduz o do obsoletas.yml) |
| Nunca cancela o próprio run nem run de fork | test_nunca_cancela_o_proprio_run_nem_run_de_outro_repositorio | RUN_ID, head_repository | passou; não cobre run irmão do mesmo sha (A1) |
| Falha fechada (299/300 arquivos, API falha, vazio) | test_falha_fechada_cancela_quando_nao_prova | 299/300 | passou |
| actions: write só em obsoletas.yml; ci.yml sem escrita; fork excluído | ObsoletasEstatico e Workflows (test_catraca) | 1 ocorrência de `actions: write` | passou |
| ci.yml: concurrency por run em PR, push segue cancelando | mutante M14 | evento != pull_request | morreu |

## Cenários e resultado real
- `python3 -I tests/test_ci_nao_cancela_parecer.py`: 6 testes, OK; `tests/test_catraca.py Workflows`: 6 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json`: M1 a M14 todos `morreu` (rev=8e9f5704f52b). Os mutantes não pegam A1: a classe "run irmão do mesmo sha" não está na lista.
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; o teste novo depende de `obsoletas.yml`, que a base não tem (falha de carga na base).
- Observação do cancelamento (pedida no brief): envio só de parecer não foi observado neste head; observou-se o oposto, o ci.yml do próprio head cancelado pelo job (A1). O run obsoletas terminou success e o ci.yml inteiro aparece em fail por `cancelled`, não por teste.
- ci: não gravado. Os checks do head 8e9f5704 estão vermelhos por cancelamento (causa em A1; o log não abre no sandbox, a causa vem da anotação "The run was canceled by @github-actions[bot]"). Reenviar o mesmo sha não resolve sem corrigir A1.
