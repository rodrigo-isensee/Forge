---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: b04f02200f86582e114a45fe233dbb900a184083
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (CI-NAO-CANCELA-ENVIO-SO-DE-PARECER, E22.1)

## Achados
- A1 (bloqueante) tests/test_ci_nao_cancela_parecer.py:20 · mutante `"$id" -lt "$RUN_ID"` para `-le` sobrevive: o gh falso lista 5 6 99 e nunca o RUN_ID (10); o job cancelaria o próprio run e nenhum teste cai. Pôr `10` na lista e esperar ["5","6"].

## Critério → teste → resultado
O pedido não tem `CA-n` de UX; as obrigações vêm do brief (E22.1) e da regra de controle de CI.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Envio só de parecer não cancela | test_envio_so_de_parecer_nao_cancela_nada | docs/reviews, docs/qa, docs/security | passou |
| Envio com código cancela só runs mais antigos | test_envio_com_codigo_cancela_so_os_runs_mais_antigos | id < RUN_ID (99 fica) | passou; mutante `-le` sobrevive (A1) |
| Outros docs não contam | test_outros_docs_e_o_devops_nao_contam_como_parecer | prefixo `docs/reviews-x/` | passou |
| Falha fechada (sem before, outra ação, vazio, erro da API, 300 arquivos) | test_falha_fechada_cancela_quando_nao_prova | 299/300 arquivos, API falha | passou |
| Permissão mínima, sem injeção, fork excluído | test_concorrencia_so_cancela_fora_de_pr_e_o_job_tem_permissao_minima | `actions: write` só no job; sem `${{` no script | passou |
| Checks exigidos sem mudança | leitura do diff: nenhum job existente alterado, `obsoletas` sem `needs` de ninguém; só o bloco `concurrency` mudou | n/a | ok |
| Push em develop/homolog/main segue cancelando | mutante M8 (`cancel-in-progress: true`) morreu | evento != pull_request | passou |

## Cenários e resultado real
- `python3 -I tests/test_ci_nao_cancela_parecer.py`: 5 testes, OK.
- Revisão do job: entradas do evento (head_ref, sha, before, action) passam por `env:`, nunca interpoladas no script; `actions: write` só no job `obsoletas`, `contents: read` no resto; `if` exclui PR de fork; timeout 3 min; `gh api` em condição do `if` (falha cai no ramo que cancela); diff vazio vira nome vazio e cai em `so_parecer=false`.
- Mutantes à mão (cópia descartável, script em scratchpad): M1 `-lt 300`→`-le`, M3 glob `docs/*`, M5 ação, M6 before, M7 `*)`, M8 cancel-in-progress, M9 `if` do fork, M10 `actions: read`, M11 `-gt`: todos morreram. M2 (tirar `[ -n "$arquivos" ]`): equivalente, a linha vazia já vira `so_parecer=false` no laço. M4 (`-le`): sobrevive (A1).
- Vermelho antes do verde: o teste é novo e o `ci.yml` anterior não tem o job `obsoletas` (o `re.search` falha na base); não rodei `forge-testes --vermelho`, só as trocas manuais acima.
- Observação do cancelamento: o envio deste parecer (só `docs/qa/`) é o caso que o job deve deixar passar; o resultado está no relatório do QA.
- ci: não gravado. No momento da leitura, as 10 partes da suíte do head b04f0220 estavam `pending` (fila); `bateria (pareceres)` e `catraca` vermelhos são os que esperam parecer ou rótulo.
