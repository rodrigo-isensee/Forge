---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 9535b63a7908ae1578f998ef5e1978734aacb82f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: gh-merge-admin (versao-033, E1.3)

Revisor: `forge:tech-lead`, outra instância (D-ETAPAS-INST); não sou o autor do E1.2. Base `928e61b`, um commit (`6c7e573`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:1667 · resolvido na rodada 2: `-R`/`--repo` entre `pr` e `merge` recusa com R-MAIN (parecer.py:231). Rodada 1: `gh pr -R dono/repo merge 12 --admin` saía com rc=0.
- A2 (bloqueante) hooks/parecer.py:499 · resolvido na rodada 2: `--input=`, `-f`/`-F` colados e `merges -fbase=` recusam. Rodada 1: as formas coladas saíam com rc=0.
- A3 (recomendado) tests/hooks/conformidade/gh-merge-admin-admin-e-bash-c-bloqueia.json:17 · resolvido na rodada 2: o esperado das quatro fixtures traz o texto da recusa nova.
- A4 (recomendado) tests/test_hooks.py:2164 · resolvido na rodada 2: heredoc, xargs, `--repo=`, conferente, homolog e as linhas de A1 e A2 têm fixture.
- A5 (recomendado) hooks/conformidade.py:1664 · resolvido na rodada 2: as specs `tests/mutantes/gh-merge-admin.json` e `gh-merge-admin-2.json` cobrem G1 a G23, sem o G13, que caiu com a alternativa morta.
- A6 (bloqueante) hooks/parecer.py:503 · segurança com gatilho (C-4), opção curta combinada: `gh api repos/o/r/pulls/1/merge -iX PUT`, `-iXPUT` e `gh api -if query=@q.graphql graphql` saem com rc=0. O gh lê `-iX` como `-i -X` (`gh api -iX` responde "flag needs an argument: 'X' in -X").

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

## Rodada 2
Head `9535b63`, sobre `6c7e573`. Revalidei só o delta: `git diff 6c7e573..9535b63 -- hooks/ tests/ changelog.d/`. Ele traz conformidade.py com +4/-1, parecer.py com +29/-7, 22 fixtures novas, 4 com o esperado apertado, duas specs de mutação e o changelog. O que já tinha lido na rodada 1 e que o delta não toca: o resto de `gh_admin`, `gh_api_de_merge` e `textos_da_api`, e as 41 fixtures.

- **A1, resolvido.** `analisar` agora pula `-R`, `-R<valor>`, `--repo` e `--repo=` entre `pr` e o subcomando. Também reconhece o programa chamado por caminho (`Path(...).name`). Sondei `gh pr -R dono/repo merge 12 --admin`, `--repo=`, `-Rdono/repo`, `-R` junto com `--repo`, `/usr/bin/gh`, `command gh` e `env gh`, e todos recusam com R-MAIN. Sem `--admin`, `gh pr -R o/r merge 1` e `gh pr -R o/r view 1` liberam.
- **A2, resolvido nas formas da rodada 1.** `--input=q.json`, `-Fquery=@q.graphql` e `merges -fbase=main -fhead=x` recusam com R-MAIN. `-fquery='mutation{mergePullRequest…}'` é recusado antes, com R-CONFORMIDADE, pelo bloco do GRAPHQL_PERIGOSO.
- **A6, novo.** A regex `-i?[fF]` (parecer.py:508) mostra que o autor considerou o `-i` combinado, mas só para o campo:
  - `opcao(args, "--method", "-X")` não vê `-iX`;
  - `endpoint_da_api` toma o valor de `-iX` ou `-if` como endpoint;
  - por isso passam o merge REST sem corpo (`-iX PUT`) e o GraphQL com `-if` antes do endpoint.

  A forma já existia em `6c7e573` e eu não a vi na rodada 1, mas a porta é a mesma que o delta altera. Sugestão: antes de `metodo_mutante`, `endpoint_da_api` e `textos_da_api`, normalizar o `-i` combinado (`-iX…`, `-if…`, `-iF…`) em `-i` mais o resto. Isso só aperta (T-4). Na volta, cada forma leva a sua fixture `-bloqueia`. O bloco do API_ADMIN usa a mesma leitura e tem a mesma brecha.
- **C-1 a C-3, cumpridos.** A6 é do C-4. A expansão no lugar do programa (`$G pr … merge`, `"$(which gh)" api …`) recusa com R-MAIN, em falha fechada. Isso também recusa `"$(which gh)" api user`, que é só leitura: é o custo aceito do C-3, e a mensagem diz como corrigir.
- **C-4, cumprido salvo A6.** `graphql?x=1` e `graphql#…` casam o endpoint, e `-F query=@-` recusa.
- **C-6, cumprido.** Sem rede e sem `gh` novo. A troca de `pasta or Path(os.devnull)` por `pasta` é segura, porque `segmento` e `caminho` sempre devolvem `Path`. A fixture da pasta inexistente segue recusando.
- **Regressão: nenhuma no módulo.** A mudança em `analisar` também aperta `gh pr -R x create` e `ready`, que antes saíam sem análise. Os dois casos têm fixtures próprias.
- **Achado recorrente.** A classe "forma de opção do `gh` que o leitor não normaliza (colada ou combinada)" volta neste pedido, em A2 e A6. O PA-7 pede a linha AR em `docs/engineering/achados-recorrentes.md`, mas este brief só permite commitar o parecer. Fica pendente.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `9535b63`: `Ran 71 tests in 924.730s`, `OK` (D-5). As sondas usaram a `Fixture` do próprio teste, em `$TMPDIR/tech-lead-gh-merge-admin/`.
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...9535b63`, contando só código e teste: `hooks/conformidade.py` 26, `hooks/parecer.py` 45 (37+8) e `tests/test_hooks.py` 5, total de 76 linhas. É uma classe de comportamento em `hooks/` (merge que desvia a proteção), com corpus próprio. Dentro do teto.

**Parecer da rodada 2: reprovado.** A1 a A5 estão resolvidos. A6 bloqueia. Segurança e QA têm parecer próprio (E1.4 e E1.6). A6 também vai para o `security-engineer`.
