---
tipo: revisao-devops
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 5c6684ddd222f18cd82c055f0602e23340720d98
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-27
---
# Review de devops: lote-fechar2

## Parecer
Aprovado, revalidado por delta contra o head 5c6684d (parecer anterior em 03155612). O diff de `.github/` contra a base b6eb84f segue sendo uma linha de `.github/workflows/ci.yml` (passo "shellcheck (scripts e hooks)": `bin/forge-fechar` na lista depois de `bin/forge-init`); `git diff 03155612..5c6684d -- .github scripts` e vazio, então gatilhos, permissões, ações, segredos, `concurrency`, `if:` e `timeout-minutes` não mudaram. A lista do shellcheck (SHELLCHECK-FECHAR) continua cobrindo `bin/forge-fechar` como o arquivo está agora: `shellcheck bin/forge-fechar` no worktree em 5c6684d, shellcheck 0.11.0, rc=0, sem aviso. As voltas 1 a 3 mudaram em `bin/forge-fechar` apenas o ajudante `remoto_exato` (coluna 1 do ls-remote validada como sha hexadecimal de 40 ou 64 caracteres, leitura ruim vira rc 1) e o passo 2b (laço sobre `lista_mb`, cadeia `sort -zu && sort -zu && comm -z -12` com `die` se falhar, contagem `rev-list --count --not "${lista_mb[@]}"`); lidos em :520-540 e sem defeito de comportamento ou de pipeline: o diretório temporário é criado com `mktemp -d` e removido na saída (`rm -rf` guardado por `[ -z "${tmp2b:-}" ]`), nenhuma entrada não confiável vai para `run:`. `mapfile` exige bash 4: o runner `ubuntu-24.04` tem bash 5, então só vale como recomendação já registrada no review (A3). Ferramentas: `git diff`, `shellcheck`. Faltou no ambiente: `actionlint` (lacuna registrada; a mudança é só o argumento de um `run:`).

## Achados

## Detalhe dos achados
(nenhum)

## Custo e rollback
Custo: zero (`R-CUSTO`); um arquivo a mais no shellcheck, sem job novo nem runner pago. Nada escreve na `main` (`R-MAIN`); sem `continue-on-error`, `[skip ci]` ou check desligado (`R-VERIFY`). Rollback: reverter o commit. O PR toca `.github/`: a catraca pede o rótulo `afrouxa-regra` do dono; o tech-lead deve avisar (o autor não aplica).
