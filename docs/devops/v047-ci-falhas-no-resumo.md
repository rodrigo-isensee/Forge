---
tipo: revisao-devops
contrato: 1
pedido: v047-ci-falhas-no-resumo
branch: melhoria/v047-ci-falhas-no-resumo
commit: 8262345394250e8b2f2130950da47af33fac4621
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: v047-ci-falhas-no-resumo

## Achados
- A1 (recomendado) .github/workflows/ci.yml:258 · o passo "Pulados da parte" não usa `!cancelled()`; com a suíte falha, a parte não sobe os pulados (comportamento anterior, fora deste item). Avaliar em cartão.

## Detalhes
Aprovado (E2.290, instância que não fez a entrega). O `ci.yml` ganha `set -o pipefail` e `tee "$RUNNER_TEMP/suite.log"` nos quatro passos da suíte (rapida, rapida-quatorze, partes-doze, partes-quatorze); o código de saída da suíte segue reprovando o job. O passo novo roda com `!cancelled()` (cancelado não gera resumo; falha gera) e, nas partes, só quando a árvore não foi provada. Sem `continue-on-error`, sem `[skip ci]`, sem teste pulado (`R-VERIFY`). `permissions` e `timeout-minutes` inalterados; nenhuma ação nova de terceiros; entrada não confiável (rótulo, registro) passa por `env` e argumento, nunca interpolada em `run:`. O script `scripts/falhas-no-resumo.py` roda com `python3 -I`, usa só biblioteca padrão, sai sempre com 0 e escapa controle, segredo, `::`, `%`, `|` e `<` do registro. Os testes do item (`python3 -m unittest tests.test_falhas_no_resumo tests.test_suite_partes tests.test_ci_local`) deram 119 testes OK. Os testes que travavam o texto antigo do passo foram atualizados no mesmo commit. Itens de `achados-recorrentes.md` conferidos: AR-5 (`-I` presente no CI) e AR-12 (spec de mutantes em `tests/mutantes/v047-ci-falhas-no-resumo.json`). Ferramentas: `actionlint` ausente do PATH (lacuna; a validação ficou com os testes que leem o YAML e com o CI); `shellcheck` presente, sem script de shell novo. Como `.github/workflows/ci.yml` é workflow, o envio ao remoto sai do dono (token sem escopo `workflow`) e a catraca pode pedir o rótulo `afrouxa-regra`: avisar o `tech-lead`.

## Custo e rollback
Sem custo novo (`R-CUSTO`): um passo de segundos por job, sem artefato nem cache. Rollback: reverter o commit 82623453; o job volta a rodar a suíte sem o `tee`.
