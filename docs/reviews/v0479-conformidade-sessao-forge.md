---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 29cbd24dc696ec318b4a53eb9322f46f149ae713
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.11, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `d2358465..29cbd24d`; no domínio, `changelog.d/v0479-conformidade-sessao-forge.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/test_hooks.py`, `tests/mutantes/v0479-conformidade-sessao-forge-{3,4,5}.json` e as fixtures `e51-*` novas ou mudadas. O aviso do delta sobre o merge 7d7fda5 fora da `origin/develop` só alarga a lista; o código do intervalo é o da E51.10.

## Sondas
- S1 · hook desta cópia, CLAUDE_PROJECT_DIR=/workspaces/Forge, cwd nesta wt, forge:tech-lead, `git -c alias.p=push p origin develop` · espera: 2 · obtido: 2 (R-REVIEW `git -c alias.p`; A1 anterior)
- S2 · mesmo leiaute, `bash <<< 'git push origin develop'`, `bash <<EOF` com push para develop, `sh <<'X'` com `B=develop; git push origin $B`, `cat <<EOF | bash` com push e `bash -c "$(echo git) push origin develop"` · espera: 2 · obtido: 2 nos cinco
- S3 · mesmo leiaute, `python3 - <<EOF` que só imprime o push, `gh pr edit 12 --body "$B"`, `` bash -c "echo \`git log -1\`" ``, `git log --oneline -3` e `git push origin melhoria/x` · espera: 0 · obtido: 0 nos cinco
- S4 · projeto em $TMPDIR com `.forge/versao`, `gh pr edit 12 --base main` · espera: o mesmo da wt · obtido: 0 nos dois (pôr `gh pr edit` fora das travas não abre o que o projeto fecha)

## Parecer
Aprovado. O A1 anterior está corrigido: as cinco recusas de alias (`hooks/conformidade.py:2630`, `2637`, `2640`, `2647`, `2753`) levam `trava=TRAVA_OPACA`, e `docs/hooks.md:63` diz agora que o alias da configuração e o da linha são trava (S1). As correções do QA E51.9 cabem no mesmo predicado: o corpo de heredoc só vira comando quando o dono o roda (`corpo_so_lido`, o mesmo da conferência da linha), o here-string de shell é relido como o `sh -c`, e `texto_reavaliado` deixa opaca a palavra com substituição do bash de fora e lê a crase escapada como a do bash de dentro (S2, S3). `gh pr edit` entrou na lista fora das travas sem divergir do projeto (S4).

Tamanho (H1): cerca de 30 linhas de código em `hooks/` no delta, um comportamento. Guardas do delta: M25 a M36 (`-4.json`, `-5.json`, até 8 por arquivo), um por marca ou linha de guarda, com M21 e M22 reapontados no `-3.json`; fixtures `-bloqueia` e `-libera` para cada forma.

Execução: `python3 -I -m unittest discover -s tests -p test_hooks.py -k HookSessaoDoForge`, ambiente limpo: 2 testes, OK (7,7 s). Mutante M29 (alias da linha, o A1): `forge-mutante --ids M29`, morreu em `hooks/conformidade.py:2753`. O resto da mutação: PQ do autor (V2), sem rerrodar. Suíte completa: CI do PR.

O A2 anterior (recomendado, `X=$(echo push); git $X origin develop`, também no projeto) segue como cartão depois do merge (`R-REVIEW`).
