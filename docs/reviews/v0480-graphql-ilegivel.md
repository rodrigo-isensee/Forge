---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 7afc147aec89b1efe69e77e63f9e0cc303c42f53
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E168.6 (PR #854, volta E168.5, por delta)

Segunda rodada, por delta. `forge-check parecer delta` lido: intervalo 433c3782..7afc147a, sem o que veio da `develop` (merge 824c3733); no domínio `hooks/conformidade.py`, `hooks/parecer.py`, 14 fixtures novas, `tests/test_hooks.py`, os mutantes `-4` e `-5`, o índice das fixtures e o fragmento do changelog. A primeira rodada (433c3782) fica como estava; aqui só a volta para os A1 a A3 da segurança (021ec802).

## O que a volta faz
- A1: `parecer.ordem_do_gh` põe o subcomando logo depois do `gh`, com a regra do cobra (opção `--x` sem `=` e `-x` de duas letras levam o valor; `--help`, `-h` e `--version` não levam). Vale em `analisar`, `alias_do_gh`, `Guarda.gh` e `gh_rotulo`. As outras leituras do gh (`gh_pr_na_sessao_do_forge` por `analisar`; papel só de leitura, `le_o_corpo`, D5 e `GH_FORA_DAS_TRAVAS` pela chave literal) recusam ou ficam mais estritas com a opção antes. Conferi.
- A2: `/dev/`, `/proc/` (pelo caminho absoluto e pelo real) e o que não é arquivo regular contam como ilegíveis, sem bloquear no FIFO. Conferido pelo teste novo.
- A3: o curinga fora de aspas sobe a palavra ao nível 2. A expansão por chaves (`-f{query=mutation\{merge,x=}PullRequest…`, que o bash monta como `mergePullRequest`) já recusa pela regra das chaves (sonda S5).

## Ordem do gh: a dúvida não falha fechado
O brief pede para conferir que `ordem_do_gh` vale em todas as travas e que falha fechado na dúvida. A primeira parte foi conferida. A segunda não se cumpre. Na leitura incerta (linha 404), a função não recusa: escolhe o primeiro `api` ou `pr` (linha 405). Isso erra nos dois sentidos:
- Quando `api` ou `pr` é o valor de uma opção, a própria regra do cobra que a função usa já acha o subcomando certo, e a troca o substitui pelo errado. `gh -b api pr merge 1 --admin` (`-b` é `--body` do `pr merge`) roda o merge com `--admin`, e o hook o lê como `gh api -b pr merge …`. Na base 433c3782 essa linha saía 2 (R-MAIN) no `conformidade` e no `parecer`; no head sai 0 nos dois. Isto afrouxa.
- Quando há expansão antes do subcomando e nenhum `api` ou `pr` literal adiante, nada recusa: `gh -X $M graphql -f query="$Q"`, com `M="POST api"`, o bash divide em `-X POST api graphql`.

## Regras de leitura
- Tamanho: delta de 43 linhas de código nos hooks, dentro do H1.
- Mutantes: GQ17 a GQ27, um por guarda nova, apontados para testes de comportamento. A cobertura é do autor e não foi refeita. O GQ27 mira a linha 405, que muda com a correção do A1.
- Commits: o 9c474688 (correção) e o 7afc147a (mutantes) seguem Conventional Commits em português e têm o fragmento do changelog. O texto do fragmento ("na dúvida … vale o primeiro `api` ou `pr`") descreve o comportamento do A1 e muda com ele.

## Verificação
- Testes dos arquivos tocados, no head 7afc147a: `python3 -m unittest tests.test_hooks.Hooks.test_ordem_do_gh tests.test_hooks.Hooks.test_graphql_arquivo_que_nao_e_regular_e_ilegivel tests.test_hooks.Hooks.test_fixtures_do_repo_publico` deu OK (3 testes, 22,3 s).
- Sondas: os hooks `conformidade` e `parecer` rodados com a montagem de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), projeto descartável na `feature/x`, nos papéis `forge:node-backend` e `forge:tech-lead` e na sessão principal. A base 433c3782 foi rodada do mesmo jeito, extraída com `git archive`.
- CI do head 7afc147a (run 45393272514): vermelho. `suíte` partes 2, 3 e 4 (3.12 e 3.14) falham, e o `bateria (pareceres)` também (ver A3 e A4). A falha de neutralidade em `docs/security/v0480-graphql-ilegivel.md` (o termo `node-backend`) vem do parecer da segurança, não do código: fica com o `security-engineer`.

## Achados
- A1 (bloqueante) hooks/parecer.py:405 · na dúvida, ordem_do_gh troca o subcomando pelo 1º api/pr em vez de recusar. Com api ou pr como valor de opção, escolhe o errado: `gh -b api pr merge 1 --admin` e `gh -t api pr merge feature/x --admin` saem 0 (na base, 2 R-MAIN: afrouxa). `gh -t pr api graphql -f query="$Q"` também sai 0.
- A2 (bloqueante) hooks/parecer.py:404 · expansão antes do subcomando sem api/pr literal adiante não recusa: `gh -X $M graphql -f query="$Q"` (o bash divide M="POST api") sai 0 no conformidade e no parecer. Correção para A1 e A2: na leitura incerta, recusar (R-CONFORMIDADE), sem escolher uma leitura.
- A3 (bloqueante) tests/hooks/conformidade/trava-graphql-stdin-input-sessao-do-forge-bloqueia.json:1 · esta fixture e a `…-stdin-proc-sessao-do-forge-bloqueia` falham no CI (python 3.12 e 3.14): sai R-CONTRIB (afrouxa-regra, conta do gh ilegível) antes do R-MAIN esperado. Dependem do ambiente; local passam.
- A4 (bloqueante) tests/mutantes/v0480-graphql-ilegivel-2.json:49 · o `de` de GQ21 (:49) e o de GQ24 (:79) saíram da fonte com as linhas mudadas em hooks/conformidade.py:3496 e :368. O CI (`test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes`) acusa também RP41 e RP42 em tests/mutantes/v0480-repo-publico-fix-6.json. Alinhar no mesmo commit.

## Sondas
- S1 · `gh -b api pr merge 1 --admin` (node-backend, tech-lead, sessão principal) · espera: 2 R-MAIN · obtido: 0 no conformidade e no parecer (na base 433c3782: 2 R-MAIN nos dois)
- S2 · `gh -t api pr merge feature/x --admin` (node-backend) · espera: 2 R-MAIN · obtido: 0 no conformidade e no parecer (na base: 2 R-MAIN)
- S3 · `gh -t pr api graphql -f query="$Q"` (node-backend, tech-lead, sessão principal) · espera: 2 R-CONFORMIDADE (consulta ilegível) · obtido: 0 no conformidade e no parecer (base igual)
- S4 · `gh -X $M graphql -f query="$Q"` (node-backend) · espera: 2 · obtido: 0 no conformidade e no parecer (base igual)
- S5 · `gh api graphql -f{query=mutation\{merge,x=}PullRequest\(input:\{pullRequestId:\"P\"\}\)\{clientMutationId\}\}` (node-backend, sessão principal) · espera: 2 · obtido: 2 R-CONFORMIDADE (chaves); controle: `printf '[%s]\n'` no bash monta `-fquery=mutation{mergePullRequest(…)…}`

## Parecer
Reprovado. A2 e A3 da segurança estão fechados, e o A1 fecha a forma direta (`gh -X POST api …`, `gh -R o/r pr merge …`, o alias). Falta a dúvida: ela escolhe uma leitura em vez de recusar, e com isso solta o `--admin` que a base barrava (A1, afrouxa) e a consulta ilegível atrás de uma expansão antes do subcomando (A2). O CI do head está vermelho por duas fixtures que dependem do ambiente (A3) e por specs de mutante fora da fonte (A4).
