---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: c70dabea04c5ba23513b4b59b99a39bdf2dc7e75
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: v047-ci-falhas-no-resumo

## Achados
- A1 (recomendado) .github/workflows/ci.yml:258 · o passo "Pulados da parte" não usa `!cancelled()`; com a suíte falha, a parte não sobe os pulados (comportamento anterior, fora deste item). Avaliar em cartão.

- A2 (recomendado) .github/workflows/ci.yml:258 · 5 min do PR e 8 da develop são projeção (docs/propostas/ci-rapido.md), sem run medido das 5 partes. Medir no 1º run e abrir cartão se passar do alvo.
- A3 (recomendado) tests/test_falhas_no_resumo.py:226 · A1 e A2 da segurança endossadas (pipefail só por texto; guarda do agregador por lista negativa em test_catraca.py:3515). Dono devops, em cartão.

## Revalidação por delta (head c70dabea, E2.560)
Intervalo 82623453..c70dabea, no domínio: `.github/workflows/ci.yml`, `scripts/pesos-do-ci.py`, `scripts/suite-partes.py`. ci.yml de 5 partes: todos os jobs têm `timeout-minutes` (partes 20 min no PR e 15 na develop contra 2:30 a 5:00 medidos por perna; agregadores e tetos 5); `concurrency` por ref com cancelamento mantida; `permissions: contents: read` em cada job novo; ações fixadas por SHA (as mesmas já usadas). Agregadores `rapida` e `rapida-quatorze` com `always()` e só leem `needs.*.result` (`success` exigido em partes e teto; pulado ou cancelado reprova, J11); nomes dos checks exigidos preservados (`bateria`, `bateria (python 3.14)`, `checagem rápida (push na develop[, python 3.14])`); o teto de pulados corre em job próprio fora do agregador (T3). Sem `continue-on-error` nem `[skip ci]` (`R-VERIFY`); sem custo novo: 10 pernas, artefatos de 1 dia (`R-CUSTO`). Testes: `tests.test_suite_partes tests.test_ci_rapido_guardas tests.test_falhas_no_resumo tests.test_pesos_do_ci` 106 OK; `tests.test_ci_local tests.test_catraca.Workflows` 80 OK. `actionlint` ausente do PATH (lacuna); `shellcheck` presente, sem shell novo. Fila: 10 pernas por run contra o limite de 20 jobs simultâneos da franquia; push na develop corre junto de PR, risco já listado no estudo (S11).

## Detalhes
Aprovado (E2.290, instância que não fez a entrega). O `ci.yml` ganha `set -o pipefail` e `tee "$RUNNER_TEMP/suite.log"` nos quatro passos da suíte (rapida, rapida-quatorze, partes-doze, partes-quatorze); o código de saída da suíte segue reprovando o job. O passo novo roda com `!cancelled()` (cancelado não gera resumo; falha gera) e, nas partes, só quando a árvore não foi provada. Sem `continue-on-error`, sem `[skip ci]`, sem teste pulado (`R-VERIFY`). `permissions` e `timeout-minutes` inalterados; nenhuma ação nova de terceiros; entrada não confiável (rótulo, registro) passa por `env` e argumento, nunca interpolada em `run:`. O script `scripts/falhas-no-resumo.py` roda com `python3 -I`, usa só biblioteca padrão, sai sempre com 0 e escapa controle, segredo, `::`, `%`, `|` e `<` do registro. Os testes do item (`python3 -m unittest tests.test_falhas_no_resumo tests.test_suite_partes tests.test_ci_local`) deram 119 testes OK. Os testes que travavam o texto antigo do passo foram atualizados no mesmo commit. Itens de `achados-recorrentes.md` conferidos: AR-5 (`-I` presente no CI) e AR-12 (spec de mutantes em `tests/mutantes/v047-ci-falhas-no-resumo.json`). Ferramentas: `actionlint` ausente do PATH (lacuna; a validação ficou com os testes que leem o YAML e com o CI); `shellcheck` presente, sem script de shell novo. Como `.github/workflows/ci.yml` é workflow, o envio ao remoto sai do dono (token sem escopo `workflow`) e a catraca pode pedir o rótulo `afrouxa-regra`: avisar o `tech-lead`.

## Custo e rollback
Sem custo novo (`R-CUSTO`): um passo de segundos por job, sem artefato nem cache. Rollback: reverter o commit 82623453; o job volta a rodar a suíte sem o `tee`.
