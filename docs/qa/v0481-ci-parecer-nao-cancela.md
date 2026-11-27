---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: bb551ad698124bebf2dcb2511719913434d668a3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (CI-NAO-CANCELA-ENVIO-SO-DE-PARECER, E22.15, delta 8e9f5704..bb551ad6)

- ci: bb551ad698124bebf2dcb2511719913434d668a3 verde

## Revalidação
A1 (anterior) corrigido em 7bf55772: `obsoletas.yml:53` agora exige `sha != HEAD_SHA` além de `id < RUN_ID` e origem igual a REPO. Teste novo `test_nunca_cancela_o_ci_do_proprio_head_mesmo_com_id_menor_que_o_run_id` (o gh falso devolve runs 4 e 8 do head atual com id menor que o RUN_ID 10; nenhum cai). O bb551ad6 é só o merge da develop.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CI do próprio head nunca é cancelado pelo job | test_nunca_cancela_o_ci_do_proprio_head_mesmo_com_id_menor_que_o_run_id | run irmão do mesmo sha com id < RUN_ID | passou |
| Demais (envio só de parecer, código cancela só runs antigos, falha fechada, actions: write único) | os 6 testes anteriores | docs/reviews, docs/qa, docs/security; 299/300 arquivos | passaram |

## Cenários e resultado real
- `python3 -I tests/test_ci_nao_cancela_parecer.py`: 7 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json --base f1e4f478`: M1 a M15 todos `morreu` (base=f1e4f478e4ac mb=f1e4f478e4ac rev=bb551ad69812); M15 cobre a guarda nova da linha 53.
- Vermelho antes do verde: o M15 (guarda removida) derruba o teste novo; `forge-testes --vermelho` não se aplica, pois a base não tem `obsoletas.yml` (falha de carga).
- CI do head (`gh pr checks 913`): tudo verde, e2e incluso, no run 45900693971; falham só `bateria` e `bateria (pareceres)`, que esperam o parecer. O job "cancela runs obsoletos do PR" passou e o ci.yml do head não foi cancelado.
