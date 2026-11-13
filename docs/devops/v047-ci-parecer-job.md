---
tipo: revisao-devops
contrato: 1
pedido: v047-ci-parecer-job
branch: melhoria/v047-ci-parecer-job
commit: 7ba85a056b4eb332362ce5cda7b6efb193b6b017
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-12
---
# Review de devops: v047-ci-parecer-job

## Achados
- A1 (recomendado) .github/workflows/ci.yml:543 · o job `pareceres` não tem `needs`; se a checagem passar a ler algo do job de passos (gate), lembre de declarar. Hoje só stdlib e `contents: read`, sem defeito.

## Detalhes
Aprovado no head 7ba85a05 (E1.4, instância que não fez a entrega). O passo `--modo pareceres` saiu do job `bateria (passos)` para o job `pareceres` (`bateria (pareceres)`), com a mesma `env`, o mesmo script da base (worktree detach) e as mesmas condições (só `pull_request`).

Checklist da skill `ci-cd`:
- `permissions: contents: read` no job novo, sem `checks: read` nem token; `persist-credentials: false`; ações fixadas por SHA iguais às já usadas no arquivo (checkout v4.4.0, setup-python v7.1.0); `timeout-minutes: 10`; `concurrency` do workflow herdado (ci.yml:27-29).
- Entrada não confiável (`head_ref`, autor, repo) passa por `env`, nunca interpolada em `run:` (ci.yml:559-576).
- Agregador `bateria`: `needs` inclui `pareceres`; `always()` mantém falha, cancelamento e pulo reprovando. `skipped` só vale quando o evento não é `pull_request` (push, workflow_dispatch), onde o job não existe, igual ao comportamento anterior do passo. Em PR, só `success` passa. O nome do check exigido (`bateria`) não muda; `bateria (pareceres)` é check novo, que não precisa entrar na proteção porque o agregador o cobre (decisão do dono, `R-CONFORMIDADE`; nada alterado aqui).
- Fora do caminho da suíte: `pareceres` não está em `needs` de nenhum job além do agregador (grep `needs:` no arquivo; teste novo `test_pareceres_e_job_proprio_obrigatorio_e_fora_do_caminho_da_suite`). A suíte e as verificações rodam mesmo com parecer faltando.
- Gate de commit só de parecer: continua lendo o check `bateria` do commit anterior, que é o agregador e agora inclui `pareceres`; o rigor não diminui.
- `R-VERIFY`: nenhum `continue-on-error`, `[skip ci]` ou check desligado.

Ferramentas: rodei `python3 -m unittest tests.test_ci_local` (66 OK), `tests.test_catraca.Workflows` (6 OK) e `tests.test_catraca -k ci` (35 OK, inclui a lista de `timeout-minutes` com o 10 novo). Faltaram no ambiente: `actionlint` e `zizmor` (não instalo; o job `bateria (passos)` do CI os roda); `shellcheck` presente mas não há script novo. Sem PR aberto, não há CI do PR para citar; a bateria completa fica para o CI do PR.

## Custo e rollback
Custo: um job a mais por PR (checkout, Python, script leve, no máximo 10 min, normalmente poucos segundos de execução mais ~30 s de preparo), em runner padrão gratuito; sem serviço pago (`R-CUSTO`). O trabalho sai do job de passos, então o total de minutos sobe pouco; medir no checkpoint da release. Rollback: reverter o commit 7ba85a05 devolve o passo ao job de passos e o `needs` do agregador.
