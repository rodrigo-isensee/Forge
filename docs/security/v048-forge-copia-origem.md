---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 997eb63ab95b171b5829ac901939a138d095df77
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (PR #956), volta 1 (delta)

Esta é a revalidação por delta (E4.8) no head 997eb63a, feita em paralelo ao review e ao QA. O delta lido com `forge-check parecer delta` vai de 6c8fd19c a 997eb63a. No domínio do parecer só mudou `bin/forge-copia`: a função `worktree`, nas linhas 181-196, e a docstring do topo. Ficaram fora do domínio os mutantes, as specs, o changelog e `tests/test_forge_copia.py`, mas rodei o teste novo da sonda S8. A rodada anterior continua no git (parecer do commit 6c8fd19c).

Gatilhos: apagar ref (desfazer da worktree), criação concorrente de ref no mesmo repositório.

CI do head 997eb63a (run 46143981499): suíte 1-5/5, bateria (passos), bateria (python 3.14), verificações longas, instalação e teto de pulados estão verdes. Só a bateria (pareceres) está vermelha, porque espera os pareceres deste head. A catraca está verde (runs 46143981491 e 46144033235). Pela ordem do dono de 28/11 07:41 (o diff toca `bin/`), rodei no computador `tests.test_forge_copia` e o teste de custo `tests.test_hooks_volta_corpus`: 138 testes, OK.

## Achados anteriores
- A1 (recomendado) da rodada 6c8fd19c, a janela entre a checagem e o `worktree add -b`: **corrigido**. Em `bin/forge-copia:188`, `git update-ref <ref> <sha> ""` cria `refs/heads/<branch>`. Com o valor antigo vazio, o comando falha se a branch já existe, e aí sai 1 sem apagar nada. Em `:191`, `git worktree add -- <destino> <branch>` roda sem `-b`. Em `:193`, a branch só é apagada na falha e só se o valor antigo for igual ao sha: a branch que andou nesse meio tempo fica. Teste: `Worktree.test_branch_criada_por_outro_no_meio_fica_e_a_worktree_sai_1`.

A mesma S8 no `bin/forge-copia` do 6c8fd19c deu rc 1, a mensagem "apaguei a branch melhoria/alheia que ela criou" e a branch apagada: é o A1 reproduzido. Mutação: troquei a `worktree()` nova pela do 6c8fd19c, e a classe `Worktree` falhou em `test_branch_criada_por_outro_no_meio_fica_e_a_worktree_sai_1` (e em `test_branch_que_ja_existia_fica_quando_a_worktree_falha`, pela mensagem). Com a função nova, a classe passa.

## Sondas
- S8 · `forge-copia worktree <dest> --branch melhoria/alheia --base origin/develop`, `git` de embrulho cria a branch antes do `update-ref -m` · espera: rc 1, a branch fica, sem "apaguei" · obtido: rc 1, "a branch já existe", a branch fica

## Pontos conferidos sem achado
- Nome da branch: o `update-ref` recebe `refs/heads/<branch>` com o nome já aprovado por `git check-ref-format --branch` (`bin/forge-copia:347`). Nomes de borda como `@` e `a/HEAD` se comportam como antes da mudança (o `-b` antigo também os aceitava). O add sem `-b` faz checkout da branch recém-criada, sem rastreio e no sha do ponto.
- O `--` antes do destino continua no lugar. O argumento seguinte é a branch validada, que não pode começar com `-`.
- Se o ponto não resolve e o `sha` fica vazio, o `update-ref` falha (`fatal: : not a valid SHA1`) e a função sai 1 sem criar nada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: sondas locais em HOME descartável e os testes. Varredor de segredos, SAST e linter de workflow não estão no PATH: lacuna registrada. Pela leitura, o delta não toca workflow nem traz segredo.
