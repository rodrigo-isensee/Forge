---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: d2358465fafc56c42b396ef7e1efe2c4d0e6e854
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.6, parecer E51.8)

Volta por delta (`R-REVIEW`): rodada anterior (E51.4, `commit: fe8607d`, reprovado por A1) no git. Delta lido: `forge-check parecer delta` de `fe8607d..d235846`, no domínio `hooks/conformidade.py` (marca `trava=` no `barrar`, `trava_da_sessao_do_forge`, `toca_uma_trava`, listas positivas `GIT_FORA_DAS_TRAVAS` e `GH_FORA_DAS_TRAVAS`, `GIT_NO_TEXTO`), `docs/hooks.md` (item "Travas na sessão do Forge"), 16 fixtures `e51-*` novas e `tests/test_hooks.py` (`HookSessaoDoForge`, piso 27). Fora do domínio: o fragmento do changelog e os três `tests/mutantes/*.json`.

## Gatilhos
Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Detalhe dos achados
**A1 (anterior, bloqueante): corrigido.** A recusa do alvo opaco com ação crítica agora leva `trava=TRAVA_OPACA` (hooks/conformidade.py:2136, 2143, 2175) e a do teto `trava=TRAVA_NO_TETO` (2033); a `GuardaDaProva.barrar` (3771-3782) as aceita por `trava_da_sessao_do_forge` (3797-3805), que exige um comando da linha que possa ser trava (`toca_uma_trava`, 3808-3830: programa opaco, `git` com subcomando fora da lista positiva, `gh` fora da lista de leitura, texto do `eval`/`sh -c`). As três sondas do A1 (S1 `F=--force; git push $F`, S2 `B=develop; git push origin $B`, S3 `${B:-develop}`) recusam agora no clone e em `wt/*`. A marca deixou de ser o texto da recusa.

## O que foi conferido
- **Matriz de papéis:** 10 linhas × 6 papéis (tech-lead, devops-engineer, dev, security-engineer, jarvis, sessão principal sem `agent_type`) × 2 pastas (clone, `wt/*`), remoto apontando para o Forge: 120 de 120 como esperado. Recusam: `$F` com `--force`, `$B` = develop, `${B:-develop}`, `N=70; gh pr merge $N --squash --admin`, `G=git; $G push origin develop`, `F=--force; $(echo git) push $F`, `T=v9.9.9; git tag $T`. Passam: `X=a; git log $X`, `N=70; gh pr view $N`, `git push origin melhoria/x`.
- **Formas de contorno com variável (dev, clone e `wt/*`):** todas recusam: `eval`/`bash -c`/`sh -c` com o push, `env`, `command`, `nohup`, `timeout`, `xargs` (dos dois jeitos), `git -c x=$Y push`, `git -C $D push`, programa por caminho, `\git`, `"git"`, `GIT_DIR=$X`, `HEAD:$B`, `$B:refs/heads/develop`, `gh pr merge $N --admin`, `gh pr merge 1 $A`, `gh api -X PUT .../$N/merge`, `git config $K core.hooksPath`, `GH=gh; $GH pr merge`, e o push com variável dentro de `$(…)`, `if`, `for`, subshell, grupo, `&&` e `;`.
- **Corpus legítimo:** livre em `wt/*` e no clone: `git log|diff|show|status|rev-parse` com variável ou `$(git merge-base …)`, `gh pr view|checks`, `gh run view`, `echo $HOME`, `ls $TMPDIR`, `git push origin melhoria/x` e `HEAD`, `git commit -m "$MSG"` e com heredoc em `$(cat <<'EOF' …)`, `git worktree add … $TMPDIR/y`, `git fetch|merge|pull` de branch de trabalho, laço `for` sem git. O `gh pr create` do dev segue recusado como antes (FILA-22, conformidade.py:3226-3231; fora do delta).
- **Só aperta:** o delta acrescenta casos de recusa na `GuardaDaProva`; a lista positiva fecha na dúvida (subcomando desconhecido, alias e `-c` são trava).
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge` nesta cópia: 2 testes, OK. Suíte inteira: só no CI; sem PR, a branch não tem execução de CI (`gh run list` vazio); o brief pede o portão sem suíte local, então o CI do PR é a prova que falta, a conferir por quem mescla.

## Fora do achado (igual ao projeto, lacuna antiga do hook)
Passam tanto na sessão do Forge quanto num projeto com `.forge/versao` (sondado lado a lado, mesmo hook): a substituição sem variável que esconde a palavra crítica ou o alvo (`git push origin $(echo develop)`, `git push origin $(git branch --show-current)`, `"$(printf dev)elop"`, `$(echo git) push origin develop`, `git $(echo push) origin develop`), o subcomando por variável (`git ${S} origin develop`, `gh $X`), a flag oculta fora de push (`git commit $NV -m x`), a linha inteira por variável (`eval "$CMD"`, `bash -c "$CMD"`) e `g''it push origin $B`. Causa comum: a recusa do alvo opaco só dispara quando o texto cru casa `CRITICO` (conformidade.py:61-64, `git|gh` seguido de `push|merge|…`) e o alvo da substituição não é tratado como opaco. Não é regressão nem requisito do E51.6 (o pedido é paridade com o projeto), por isso não bloqueia; o sandbox do Claude Code segue a garantia (ADR 0009, seção 5). Vai como melhoria ao Jarvis.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais pelo `rodar` de `tests/test_hooks.py` (scripts no scratchpad da sessão: `sonda_e518.py`, `sonda_e518b.py`, entradas `c1.json` a `c5.json`). Faltaram no PATH: gitleaks, semgrep, zizmor (o delta não toca segredo nem workflow).
