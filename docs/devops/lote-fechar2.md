---
tipo: revisao-devops
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: a35a18171fd920286e73c511dfe5c5d0cfb897f6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-27
---
# Review de devops: lote-fechar2

## Parecer
Aprovado, revalidado por delta contra o head a35a181 (parecer anterior em 137c359, sobre 5c6684d). `git diff 5c6684d..a35a181 -- .github scripts` e vazio: gatilhos, permissões, ações, segredos, `concurrency`, `if:` e `timeout-minutes` não mudaram; o diff de `.github/` contra a base b6eb84f segue sendo a linha do passo "shellcheck (scripts e hooks)" com `bin/forge-fechar` (ci.yml:238). Em `bin/forge-fechar` o delta são quatro linhas (80, 177, 337 e 750) reescritas de `A && B || C` para `if ! { A && B; }; then C; fi`, equivalentes em comportamento (o `die` e o `continue` disparam nas mesmas condições). `shellcheck bin/forge-fechar` no worktree em a35a181, shellcheck 0.11.0, rc=0, sem aviso: o SC2015 sumiu e o job do CI cobre o arquivo como está agora. Run 40507619168 (pull_request, CI): passos "Testes do Forge" e "shellcheck (scripts e hooks)" success no job `bateria`, e "Testes do Forge (Python 3.14)" success. Ressalva de SHA: o run é de a356288, pai de a35a181; o delta a356288..a35a181 é só `tests/mutantes/lote-fechar2-4.json` (20 linhas), então o código e o CI cobertos são os mesmos. O job `bateria` consta failure por causa do passo de gate de parecer ("Parecer de review ... quando o PR toca código que governa os agentes"), que é do fluxo de pareceres do tech-lead e não de pipeline; o passo "Testes que leem pareceres" ficou skipped (commit só de parecer). Ferramentas: `git diff`, `shellcheck`, `gh run view`. Faltou `actionlint` no ambiente (lacuna; nenhuma mudança de workflow nesta volta).

## Achados

## Detalhe dos achados
(nenhum)

## Custo e rollback
Custo: zero (`R-CUSTO`); um arquivo a mais no shellcheck, sem job novo nem runner pago. Nada escreve na `main` (`R-MAIN`); sem `continue-on-error`, `[skip ci]` ou check desligado (`R-VERIFY`). Rollback: reverter o commit. O PR toca `.github/`: a catraca pede o rótulo `afrouxa-regra` do dono; o tech-lead deve avisar (o autor não aplica).
