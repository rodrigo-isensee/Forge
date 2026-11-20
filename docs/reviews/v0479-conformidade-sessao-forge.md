---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: d2358465fafc56c42b396ef7e1efe2c4d0e6e854
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.7, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `fe8607df..d2358465`; no domínio, `changelog.d/v0479-conformidade-sessao-forge.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/test_hooks.py`, `tests/mutantes/v0479-conformidade-sessao-forge{,-2,-3}.json` e as fixtures `e51-*` novas. O aviso do delta sobre o merge 4e768cb fora da `origin/develop` só alarga a lista; o código do intervalo é o da E51.6.

## Achados
- A1 (bloqueante) hooks/conformidade.py:2751 · a recusa do alias da linha (`git -c alias.p=push p origin develop`, R-REVIEW) não é marcada trava: sai 0 na wt real (S7) e 2 no projeto; docs/hooks.md:63 diz que "o alias e o `-c` são trava". Mesma classe do A3 anterior; irmãs sem marca em 2629, 2636, 2639, 2645.
- A2 (recomendado) hooks/conformidade.py:3805 · `X=$(echo push); git $X origin develop` sai 0 na wt e também no projeto (S8): lacuna da guarda base, fora deste item; cartão para a guarda ver a substituição no lugar do subcomando do git.

## Sondas
- S1 · hook desta cópia, CLAUDE_PROJECT_DIR=/workspaces/Forge, cwd nesta wt, forge:tech-lead, `B=develop; git push origin $B` · espera: 2 · obtido: 2 (`$B` com ação crítica)
- S2 · mesmo leiaute, `F=--force; git push $F origin melhoria/x` · espera: 2 · obtido: 2
- S3 · mesmo leiaute, `git push origin ${B:-develop}`, `G=git; $G push origin develop` e `command git push origin $B` · espera: 2 · obtido: 2 nos três
- S4 · mesmo leiaute, `eval "git push origin develop"` e `bash -c "git push origin develop"` · espera: 2 · obtido: 2 (push direto para develop)
- S5 · mesmo leiaute, `gh pr merge $N --admin` e `gh api -X PUT repos/o/r/pulls/$N/merge` · espera: 2 · obtido: 2 (R-MAIN)
- S6 · mesmo leiaute, `git log $REF`, `gh pr view $N`, `cat $F`, `git stash push $X` e `git push origin melhoria/x` · espera: 0 · obtido: 0 nos cinco
- S7 · mesmo leiaute, `git -c alias.p=push p origin develop` · espera: 2, como no projeto (R-REVIEW `git -c alias.p`) · obtido: 0
- S8 · mesmo leiaute e projeto em $TMPDIR com `.forge/versao`, `X=$(echo push); git $X origin develop` · espera: 2 · obtido: 0 nos dois

## Parecer
Reprovado, por um bloqueante (A1). A correção do A3 anterior está certa: a marca vai no `barrar` (`trava=`: `TRAVA`, `TRAVA_OPACA`, `TRAVA_NO_TETO`), o predicado deixa de ler o texto da recusa (resolve o A2 anterior) e a `TRAVA_OPACA` só pesa quando `toca_uma_trava` acha um comando que pode ser trava (programa opaco, `git` fora da lista positiva, `gh` fora da lista de leitura, texto do `eval` ou `sh -c` num nível). S1 a S6 provam as formas do A3 recusadas e a linha de leitura livre (ADR 0009, seção 6). O A1 anterior (`docs/hooks.md`, "Ainda não coberto") está resolvido.

O A1 novo: o alias da linha (`-c alias.*`) chega ao push direto para a integração sem passar por `git_push`; a recusa dele é R-REVIEW sem marca, e a `GuardaDaProva` a engole. Correção sugerida: `trava=TRAVA_OPACA` nas recusas de alias do git (2629, 2636, 2639, 2645, 2751), que `toca_uma_trava` já decide pelo `-c` e pelo subcomando fora da lista, com a fixture `e51-wt-push-alias-c-bloqueia` e um mutante por marca; ou, se o dono preferir o alias fora da trava (`R-DECISAO`), corrigir o texto da `docs/hooks.md:63`.

Tamanho (H1): cerca de 75 linhas de código em `hooks/` no delta, um comportamento. Guardas do delta: M1 a M8 reescritos e M9 a M24 novos (`-2.json`, `-3.json`), um por linha de guarda ou marca, com fixtures `-bloqueia` e `-libera` (27 na classe).

Execução: `python3 -m unittest tests.test_hooks.HookSessaoDoForge -v`, ambiente limpo: 2 testes, OK (6,6 s). Mutação: PQ do autor (V2), sem rerrodar. Suíte completa: CI do PR.

Na volta, revalido pelo `forge-check parecer delta`. O A2 vira cartão depois do merge (`R-REVIEW`).
