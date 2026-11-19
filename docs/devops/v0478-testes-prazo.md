---
tipo: revisao-devops
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: 318721dbbb87ab4db3db719d6f0207e8def10423
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-18
---
# Review de devops: v0478

## Achados

## Detalhes
Aprovado. A mudança em `.github/workflows/ci.yml` é um passo novo ("Recusas por carga no resumo") repetido nos 4 jobs de partes (ci.yml:93, 211, 399, 476), logo depois de "Falhas no resumo".

- Roda com a suíte falhando: o passo vem depois de "Testes do Forge (parte)" e tem `if: ${{ !cancelled() }}` (nos 2 jobs de suíte completa, `&& needs.arvore.outputs.provada != 'true'`, o mesmo guarda do passo da suíte). Com a suíte vermelha, `!cancelled()` vale e o passo executa; cancelada, pula, como o passo vizinho. Lido, não executado no CI.
- Não barra: `grep -c ... || true`, e o `grep -o | sed || true` termina em 0 mesmo sem linha. Sem casamento, o `grep -c` imprime 0 e o `|| true` absorve o rc 1. O passo só escreve em `$GITHUB_STEP_SUMMARY`. Sem `continue-on-error` e sem check desligado (`R-VERIFY`).
- Entrada do log: o texto vem do stderr do teste (`tests/test_hooks.py:1215`, impresso com `file=sys.stderr`, que o `2>&1 | tee` leva ao `suite.log`). Não há interpolação de `${{ }}` em `run:`; só `$RUNNER_TEMP` e `$GITHUB_STEP_SUMMARY`.
- Permissões: nenhuma mudança; o workflow (ci.yml:27) e os jobs (ci.yml:40, 113) seguem em `contents: read`. Nenhum segredo, ação nova ou escrita fora do resumo (`R-MAIN`).
- Custo (`R-CUSTO`): sem runner, serviço, cache ou artefato novo. Um grep sobre um log pequeno, na ordem de milissegundos por job. Sem run extra, pois entra no mesmo push.
- Tempo: desprezível, sem alteração do caminho crítico nem do `needs`.
- Ferramentas: `actionlint` e `shellcheck` não estão no PATH do clone, então não rodaram; fica registrada a lacuna. O YAML foi lido à mão: indentação e `if` coerentes com os passos vizinhos.

## Custo e rollback
Custo de CI: 0 minutos adicionais mensuráveis e nenhum recurso novo. Rollback: reverter o commit remove os 4 passos; nada além do resumo depende deles.
