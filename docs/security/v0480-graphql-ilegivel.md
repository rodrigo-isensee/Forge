---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 7afc147aec89b1efe69e77e63f9e0cc303c42f53
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança, volta: v0480-graphql-ilegivel (PR #854, v0478 E168.8)

Delta lido (`forge-check parecer delta`, `433c3782..7afc147a`, sem o que veio da develop): `hooks/parecer.py` (`ordem_do_gh` :389 a :408, as chamadas em `analisar` :416 e `alias_do_gh` :578), `hooks/conformidade.py` (`expansao_por_palavra` :369, `textos_da_api` :3212 a :3221, `gh_rotulo` :3339, `consulta_ilegivel` :3496, `gh` :3737), as 14 fixtures novas de `tests/hooks/conformidade/` e `tests/test_hooks.py`. O que já tinha sido lido na rodada anterior não foi relido. O que veio da develop (`hooks/ordens.py`, `hooks.json`) fica fora: tem parecer próprio no E123.

Método: o mesmo da rodada anterior. Os hooks `conformidade`, `parecer` e `pesado` rodados direto pela montagem de `tests/test_hooks.py` (`Fixture.montar`, `rodar` com o vigia de produção), na branch `feature/x`, com os papéis `forge:node-backend` e `forge:tech-lead` e com a sessão principal. A base `433c3782` foi extraída por `git archive` e rodada do mesmo jeito. O gh real 2.105.0 só serviu para provar o parse, com `GH_DEBUG=api`, host `localhost.invalid`, token falso e a rede recusada pelo sandbox.

**Achados anteriores:** A1 fechado nas formas citadas (S1, S2, S3, S8 e mais `--method POST`, `-i`, `-H x:y`, `-X=PUT`, `-XPUT`, `--method=PUT`, `-X PUT --`, `gh -R o/r qp`). A2 fechado: S5 sai 2 em `/dev/stdin`, `/dev/fd/0`, `/proc/self/fd/0` e `--input /dev/stdin`. A3 fechado: S7 sai 2 em `*`, `?` e `[`. A troca em `ordem_do_gh` reabre um desvio do A1 (A4 abaixo).

**Só aperta ou neutro: não.** Num corpus de 18 comandos com opção antes do subcomando (`repo create --public`, `pr merge/create/ready/edit/review`, `api` de refs e proteção, `release`, `secret`, `label`, `ruleset`, `issue`), base e head dão o mesmo resultado em todo hook e todo papel. `gh -iXPUT api …/merge` passa a sair 2: aperta. As legítimas seguem 0 nos dois: `query{viewer{login}}` entre aspas simples e duplas, `[ID!]` entre aspas, `-F n="$N"`, `--paginate`, `gh -R o/r pr view 1` e `gh --help`. **Afrouxa:** `gh -b api pr merge 1 --admin` e `gh -t api pr merge feature/x --admin` saem 2 R-MAIN na base e 0 no head, em todo hook e todo papel (S9). É o A1 do tech-lead (E168.6), confirmado aqui com o parse do gh real (S10).

**Chave sem aspas `{a,b}`:** é bloqueante deste item. A expansão de chaves é da mesma família do A3: uma expansão do shell fora de aspas na palavra da consulta. A decisão do dono (opção a) manda recusar a consulta que o hook não lê, e o gh real recebe a mutação remontada (S12, S14). Na forma REST (`gh api {'…/merg','-Hx:'}e -X PUT`) fica como recomendado: o caso é anterior, está fora da consulta GraphQL e a correção é a mesma.

Formas sem caminho real (neutras): `gh -iX POST api …` (S4 da volta) e `gh -R o/r api …` (o gh recusa `-R` no `api`) saem 0 no hook, mas o gh real para com `unknown command`/`unknown shorthand flag`. Em `gh -f query={a,b}`, a chave repetida faz o gh parar com `unexpected override existing field`.

Testes rodados: as 14 fixtures tocadas, `test_ordem_do_gh` e `test_graphql_arquivo_que_nao_e_regular_e_ilegivel` passam. A suíte inteira roda no CI: o run do head `7afc147a` foi cancelado (45393272514), e o do `5a1d320a`, que só soma o parecer do review, estava na fila durante a leitura.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), ação irreversível no GitHub (merge que desvia a proteção da branch).

## Achados
- A4 (bloqueante) hooks/parecer.py:405 · na leitura incerta, ordem_do_gh escolhe o 1º api/pr em vez de recusar: `gh -b api pr merge 1 --admin` sai 0 (base 2 R-MAIN, afrouxa); `gh -t pr api graphql -f query="$Q"` (gh api tem -t) e `gh -X $M graphql …` saem 0. Na dúvida, recusar.
- A5 (bloqueante) hooks/conformidade.py:369 · a expansão de chaves fora de aspas não sobe o nível: `gh api graphql {'-fquery=mutation{mergePull','-Hx:'}'Request(…)…}'` sai 0 em todo hook e papel; o bash remonta `mergePullRequest` e o gh a envia (S12, S14). `{` com `,` ou `..` fora de aspas vale como o curinga.
- A6 (recomendado) hooks/conformidade.py:3678 · o endpoint REST com chaves fora de aspas escapa de gh_api_de_merge: `gh api {'repos/o/r/pulls/1/merg','-Hx:'}e -X PUT` sai 0 (base igual); o bash gera `…/pulls/1/merge` mais um cabeçalho. Mesma correção do A5, aplicada às palavras do `gh api`.

## Sondas
- S1 · `gh -X POST api graphql -f query="$Q"` · espera: 2 · obtido: 2 R-CONFORMIDADE no conformidade, nos três papéis
- S2 · `gh -f query='mutation{mergePullRequest(…)}' api graphql` · espera: 2 · obtido: 2 R-CONFORMIDADE (refs, regras, merge), nos três papéis
- S3 · `gh -X PUT api repos/o/r/pulls/1/merge` · espera: 2 · obtido: 2 R-MAIN no conformidade e 2 R-CONTRIB no parecer, nos três papéis
- S4 · gh real: `gh -iX POST api graphql …` · espera: sem caminho · obtido: `unknown command "POST" for "gh"`
- S5 · `gh api graphql -F query=@/dev/stdin < q.graphql`, `--input /dev/stdin`, `@/proc/self/fd/0`, `@/dev/fd/0` · espera: 2 · obtido: 2 R-CONTRIB nos três papéis
- S6 · `gh api graphql -F query=@q.graphql` · espera: 2 · obtido: 2 R-MAIN (controle)
- S7 · `-f query=mutation*`, `-fquery=mutatio?`, `-f query=mutation[{]*` · espera: 2 · obtido: 2 R-CONFORMIDADE nos três papéis
- S8 · `gh qp -f query="$Q"` e `gh -R o/r qp -f query="$Q"` com `qp: -X POST api graphql` · espera: 2 · obtido: 2 R-CONFORMIDADE nos três papéis
- S9 · `gh -b api pr merge 1 --admin` e `gh -t api pr merge feature/x --admin` · espera: 2 R-MAIN · obtido: 0 em todo hook e papel (base: 2 R-MAIN no conformidade e 2 no parecer)
- S10 · gh real: `gh -q api pr view 1 --json number -R localhost.invalid/o/r` · espera: o gh pula `-q api` e roda `pr view` · obtido: `POST /api/graphql` (o `pr merge` tem `-b` e `-t`, então S9 roda o merge com `--admin`)
- S11 · `gh -t pr api graphql -f query="$Q"` e `gh -X $M graphql -f query="$Q"` · espera: 2 · obtido: 0 em todo hook e papel (base igual)
- S12 · `gh api graphql {'-fquery=mutation{mergePull','-Hx:'}'Request(input:{pullRequestId:"PR_x"}){clientMutationId}}'` · espera: 2 · obtido: 0 em todo hook e papel; o gh real remonta a consulta (S14)
- S14 · gh real: `gh api graphql {'-fquery=query{viewer{log','-Hx:'}'in}}'` · espera: o bash remonta a consulta · obtido: corpo `"query": "query{viewer{login}}"` e cabeçalho `X: in}}`
- S13 · `gh api {'repos/o/r/pulls/1/merg','-Hx:'}e -X PUT` · espera: 2 · obtido: 0 em todo hook e papel (base igual)

## Detalhe dos achados
**A4: a leitura incerta escolhe em vez de recusar.** Severidade alta, esforço P, dono: o autor do hook (tech-lead). Evidência: `hooks/parecer.py:405`; sondas S9, S10 e S11. Caminho de ataque: um agente de qualquer papel escreve `gh -b api pr merge 1 --admin`. O gh pula `-b api`, roda `pr merge 1 --admin --body api` e desvia a proteção da branch. O hook lê `gh api -b pr merge …`, uma chamada `api` sem endpoint de merge, e libera. Com `-t pr` antes de `api`, o mesmo acontece com a consulta ilegível (`gh api` aceita `-t`). Correção mínima: quando `ordem_do_gh` não tem certeza (expansão antes do subcomando, ou `api`/`pr` como valor de opção), a função sinaliza a dúvida e o chamador (`analisar`, `Guarda.gh`, `gh_rotulo`, `alias_do_gh`) recusa com R-CONFORMIDADE, sem escolher uma leitura. Fixtures: as entradas de S9 e S11.

**A5: chaves fora de aspas na consulta.** Severidade média, esforço P, dono: tech-lead. Evidência: `hooks/conformidade.py:369` e :3496; sondas S12 e S14. O marcador `chaves` com ação crítica (:2292) só dispara quando `merge` aparece como palavra inteira. Partido pelas chaves, o nome não aparece, e o gh recebe a mutação remontada. Correção mínima: em `expansao_por_palavra`, `{` fora de aspas com `,` ou `..` antes do `}` correspondente sobe a palavra ao nível 2, e `consulta_ilegivel` faz a mesma conferência na palavra. A consulta legível entre aspas (`'query{viewer{login}}'`) e a literal sem vírgula seguem livres. Fixtures: S12 e a legível `-f query='query{a{b,c}}'`.

**A6: chaves no endpoint REST.** Severidade média, esforço P, dono: tech-lead. Evidência: `hooks/conformidade.py:3678`; sonda S13. A correção é a mesma do A5, aplicada a toda palavra do `gh api` antes de `gh_api_de_merge` e das travas de refs e regras.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: os hooks rodados localmente com a montagem do teste, a base extraída por `git archive` e o gh real só contra host inválido. gitleaks, semgrep e zizmor não se aplicam a este delta.
