---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 6c7e5731a7138e9eaf11e4c216726318091dfd57
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: gh-merge-admin (versao-033, E1.3)

Revisor: `forge:tech-lead`, outra instância (D-ETAPAS-INST); não sou o autor do E1.2. Base `928e61b`, um commit (`6c7e573`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:1667 · segurança com gatilho (C-1, C-2, alvo -R): `gh pr -R dono/repo merge 12 --admin` e `gh pr --repo=dono/repo merge melhoria/x --admin` saem com rc=0. O gh aceita o -R persistente entre `pr` e `merge`, mas `parecer.analisar` só vê `merge` logo após `pr`, e o `gh_admin` não roda.
- A2 (bloqueante) hooks/parecer.py:499 · segurança com gatilho (C-4): `metodo_mutante` não vê as formas coladas que o gh aceita e que viram POST. `gh api graphql --input=q.json` (mergePullRequest no arquivo), `-Fquery=@q.graphql`, `-fquery='mutation{mergePullRequest…}'` e `gh api repos/o/r/merges -fbase=main -fhead=x` saem com rc=0.
- A3 (recomendado) tests/hooks/conformidade/gh-merge-admin-admin-e-bash-c-bloqueia.json:17 · o esperado `R-` (também em em-crase, em-eval e api-merge-sem-papel-em-tmp) aceita qualquer recusa. A sonda mostra que essas linhas já saem com o texto R-MAIN do item: use esse texto no esperado para que só a recusa nova satisfaça a fixture.
- A4 (recomendado) tests/test_hooks.py:2164 · faltam fixtures para pontos da matriz: heredoc para bash, xargs, `--repo=`, papel conferente e base homolog. Na sonda, heredoc, xargs e `--repo=` já recusam com R-MAIN e o conferente recusa com R-CONFORMIDADE. Inclua também as linhas de A1 e A2.
- A5 (recomendado) hooks/conformidade.py:1664 · não há spec de mutação dos 4 mutantes do C-8. Pela leitura, as fixtures b-numero, valor-false, valor-um e g-graphql-arquivo os matam, mas a prova do autor pela ferramenta falta (AR-1).

## O que li
- O diff inteiro: `hooks/conformidade.py` (+24), `hooks/parecer.py` (+11), `tests/test_hooks.py` (+5), `changelog.d/gh-merge-admin.md` e as 41 fixtures `tests/hooks/conformidade/gh-merge-admin-*.json`.
- A seção E1 do modelo de ameaças (matriz, C-1 a C-8, T-1 a T-5).
- `docs/engineering/achados-recorrentes.md` (PA-7). A1 e A2 não repetem uma classe já registrada, então não entra linha AR nova.

## Controles
- **C-1:** cumprido na forma com `merge` logo após `pr`. `usa_admin` pega `--admin` e `--admin=<qualquer>`, inclusive depois de `--` e como valor de `--body`. A forma com `-R`/`--repo` entre `pr` e `merge` não é coberta (A1).
- **C-2:** o `gh_admin` roda antes de `if not parte` e antes do `return` da branch, e não consulta raiz, branch nem base. As fixtures `/tmp`, pasta inexistente, `GH_REPO=` e URL recusam com R-MAIN. A brecha que fica é a mesma de A1.
- **C-3:** reusa `leituras`. Sondei bash -c, crase, eval, heredoc e xargs, e todos chegam ao R-MAIN.
- **C-4:** REST (`pulls/<n>/merge`, `merges`, `{owner}`, URL completa) e GraphQL (inline, `-f query=`, `-F query=@`, `--field=`, `--raw-field`, `--input arq`, `--input -`) recusam. A porta do `metodo_mutante` deixa passar as formas coladas (A2). Um ajuste possível em `metodo_mutante`: tratar `--input=` e `-f`/`-F` com valor colado como mutantes. Isso só aperta e não muda nenhuma recusa existente (T-4).
- **C-5:** os 10 legítimos liberam (fixtures `legitimo-*`). A sonda extra `gh api graphql` de leitura com `mergeable mergeStateStatus` também libera.
- **C-6:** sem rede e sem `gh` novo. A única leitura é o arquivo local do corpo, pela `textos_da_api` que já existia. O teste de tempo segue no mesmo teto.
- **T-1 a T-4:** respeitados. Nada depende de papel, base ou projeto, o valor de `--admin=` não é lido e não há escape. As recusas anteriores não mudam de ordem: o bloco `R-CONFORMIDADE` de API_ADMIN/GRAPHQL_PERIGOSO vem antes do `gh_api_de_merge`.
- **T-5:** `gh alias set m 'pr merge --admin'` passa (rc=0). Fica como risco residual do N1, fora deste item.

## Testes
`python3 -m unittest tests.test_hooks` na worktree, no head `6c7e573`: `Ran 71 tests in 1052.709s`, `OK`. Rodei só os testes dos arquivos tocados (D-5). As sondas usaram a `Fixture` do próprio teste, em `$TMPDIR/tech-lead-gh-merge-admin/`.

## Teto (M14)
`git diff --numstat --no-renames 928e61b...6c7e573`, contando código e teste: `hooks/conformidade.py` 24, `hooks/parecer.py` 11, `tests/test_hooks.py` 5, total de 40 linhas. Fixtures e changelog ficam fora da conta. Uma classe de comportamento em `hooks/` (merge que desvia a proteção), com corpus próprio. Dentro do teto.

## Parecer
**Reprovado.** A estrutura está certa: a checagem roda antes das saídas antecipadas, sem rede, com mensagem R-MAIN e corpus amplo. Há duas brechas com gatilho dentro das dimensões que o próprio modelo lista:
- **A1:** `-R`/`--repo` entre `pr` e `merge`, que o `gh` aceita (`gh pr -R dono/repo merge --help` responde). Sugestão: o `gh_admin` decide pelas palavras (achar `merge` depois de `pr`, pulando `-R`/`--repo` e o valor), sem depender de `parte`.
- **A2:** as formas coladas de `--input=`, `-f` e `-F` no `metodo_mutante`.

Na volta, cada brecha leva a sua fixture `-bloqueia`. A3 a A5 são recomendações e não devolvem a entrega.

Segurança e QA têm parecer próprio (E1.4 e E1.6), que não refaço. A1 e A2 também chegam ao `security-engineer` pelo E1.4.
