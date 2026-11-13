---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-changelog-base
commit: b5d501257b67e9be2bce4051c26a7555d3d3f02f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (E1.53, correção do passo do changelog no CI, E1.52)

## Achados

## Sondas

## Parecer
Aprovado no head 136cf316 (classe C). O passo `develop - mudança na fábrica exige fragmento em changelog.d` passa a calcular `BASE=$(git rev-parse HEAD^1)` (primeiro pai do merge do checkout, `fetch-depth: 0` no job), igual à catraca e aos passos de pareceres (ci.yml:538, 556, 603; catraca.yml:39); a ponta velha de `base.sha` deixa de acusar fragmento de outro PR (CI-CHANGELOG-BASE).

Conferido:
- Não abre caminho para pular a checagem: o `forge-changelog conferir` segue chamado com `--base` e o mesmo `if`; `HEAD^1` que falhe aborta o passo (bash -e) e o `git` do script sai com 2. O diff `HEAD^1..HEAD` do merge é exatamente o do PR, então PR sem fragmento continua reprovado.
- Teste `test_changelog_compara_com_o_pai_do_commit_de_juncao_e_nao_com_a_base_do_evento` roda o `run` real do passo num repo temporário com develop andando e BASE velho no ambiente; espera o pai da junção. `tests.test_ci_local.MatrizNeedsEAgregadorTest`: 11 testes OK.
- Mutante M1 (guarda única do diff): morreu (`bin/forge-mutante tests/mutantes/v047-ci-changelog-base.json`).
- Fragmento `changelog.d/v047-ci-changelog-base.md` presente. Diff de código e teste: 38 linhas, abaixo do teto.
- Não rodei a sonda ponta a ponta de "PR sem fragmento barra" com o script real (o hook R-REVIEW recusou o merge em pasta temporária); vale a equivalência com a catraca e o CI do PR. Suíte inteira: no CI.

## Revalidação (E1.67)
Delta lido por `forge-check parecer delta` (136cf316..b5d50125, domínio: `tests/test_ci_local.py`, 1 linha): o `git()` do teste do changelog passa a usar `env=sem_manutencao(env)` (E1.66), o ponto único de `tests/ambiente_git.py` (já importado na linha 11), que preserva as chaves `GIT_CONFIG_*` do chamador e junta as de manutenção. Só o ambiente do subprocesso muda; a guarda e o comportamento testados seguem iguais, sem achado novo.
`tests.test_ci_local` e `tests.test_ambiente_git`: 86 testes, OK (42 s). Aprovado no head b5d50125. Suíte inteira: no CI do PR.
