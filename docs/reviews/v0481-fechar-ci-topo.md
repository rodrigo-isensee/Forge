---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: dd2fcada2719cafad4eee2d8e31f3aaec2e8d5c3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481

## Achados
- A1 (recomendado) bin/forge-fechar:1663 · A branch criada fica se o passo 1 para; com o autor reenviando, a rodada seguinte lê o sha velho dela e para no passo 2 com "envie a branch" (bin/forge-fechar:1747), conselho errado (o local está atrás). Sugestão: apagar a branch criada ao parar, ou recriá-la no sha do servidor.
- A2 (recomendado) bin/forge-fechar:1244 · Com o topo vermelho, a reversão impressa é a deste merge, mas o vermelho pode vir de um commit posterior que o topo contém. Sugestão: dizer na mensagem que o vermelho é do topo e conferir o culpado antes de reverter.
- A3 (recomendado) bin/forge-fechar:1687 · A parada da cópia principal na branch vale também com --sem-limpar, em que o passo 7 não roda e o motivo (código 3) não se aplica. Sugestão: pular a parada com --sem-limpar ou dizer no manual que ela vale sempre.

## Sondas

## Parecer
Aprovado. Diff de código: 31 linhas a mais e 8 a menos em `bin/forge-fechar` (dentro do teto H1); três comportamentos pequenos do mesmo fechamento, sem cortar.

O que o brief pede conferir:
- Nenhum caminho mescla sem os checks verdes do head: o FECHAR-CI-TOPO mexe só no passo 8, depois do merge e da limpeza; o 6 e o 6b ficam iguais. O FECHAR-CRIA-BRANCH cria a branch no sha lido do servidor e passa a `so_remota=0` e `ref_check=refs/heads/<ref>`, o caminho já usado com a branch local: o `forge-check pr` confere esse sha, o passo 2 relê o local e o servidor (1739-1747) e o merge sai com `--match-head-commit` nele (teste `test_commit_que_falta_aqui_cria_a_branch_local_no_sha_do_servidor`). O `--dry-run` e o `--limpar` saem antes (bloco anterior a 1643), então não criam branch.
- O CI do topo só vale quando contém o merge: a comparação é sempre contra `$1` (o merge), com `ahead` ou `identical`; topo ilegível, vazio, igual ao sha já lido ou `diverged`/`behind` sai do laço e fica `cancelado`, código 5 (testes `test_topo_que_nao_contem_o_merge_fica_cancelado`, `test_topo_que_nao_andou_fica_cancelado`). O laço termina: cada volta exige um topo novo, e o prazo restante cai a 0 (uma leitura).
- Nada que barra hoje deixa de barrar: vermelho, pendente e ilegível seguem 5; a busca que não traz o commit para no passo 1 como antes (mesma mensagem), e branch que não se cria também para. O FECHAR-COPIA-CERTA só acrescenta parada; a worktree ligada na branch segue como antes (teste `test_worktree_ligada_na_branch_nao_e_a_copia_principal`).
- `buscar_de` busca por sha, sem ref nova nem FETCH_HEAD; `git branch --no-track` não escreve no `.git/config`.

Falsos dos testes (item 12 do checklist): o `gh api .../compare/` falso aceita só dois sha40 e o `--jq .status` exatos (exit 64 fora disso); o `fetch` falso falha por inteiro com `falha_fetch`. Nenhum é mais frouxo que o script.

Verificadores, rodados por mim no Revisar-sha: `tests.test_fechar_ci_topo` e `tests.test_fechar_sha_conferido`, 18 testes, OK. `bin/forge-mutante --processos 1 tests/mutantes/v0481-fechar-ci-topo.json`: M1 a M8 morreram (1235, 1236, 1241, 1687, 1688, 1655, 1662, 1663). `--cobertura --base d49accf8`: `bin/forge-fechar` sai "não coberto" por ser shell; conferi à mão as guardas mudadas (o `while` de 1235-1236, o `if` de 1241, o `if`/`die` de 1655, 1662, 1663, 1687, 1688): uma por linha, cada uma com mutante e teste do ramo de falha. Suíte inteira: fica com o CI do #880 (no head dd2fcada, partes ainda em andamento; `bateria (pareceres)` e `catraca` vermelhas esperam os pareceres e o rótulo).

A1 foi reproduzido por sonda (só recomendado, fora do bloco Sondas): branch só no servidor com commit ausente, primeira rodada com o `forge-check` reprovando (rc 1, a branch local `melhoria/x` fica), novo commit no servidor, segunda rodada: rc 1, "parou no passo 2: o head local (160d77a…) difere do remoto (fa0a675…); envie a branch". Falha fechada, sem merge; o custo é uma rodada a mais, a medida que o item quer baixar.

Manual (`docs/fechamento-integrador.md`) e fragmento do changelog descrevem os três comportamentos como o código faz. A1, A2 e A3 viram cartão depois do merge.
