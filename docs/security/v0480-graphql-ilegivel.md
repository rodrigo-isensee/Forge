---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 433c3782d067b58ac85f481f6bd13c085f9704e7
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-graphql-ilegivel (PR #854, v0478 E168.4)

Escopo do diff `95b09785..433c3782` no domínio: `hooks/conformidade.py` (`GRAPHQL_ILEGIVEL` e `expansao_por_palavra` :343 a :381, `consulta_ilegivel` :3474, a chamada em `gh` :3765), as 16 fixtures tocadas em `tests/hooks/conformidade/` e `tests/test_hooks.py`. Relidos `parecer.analisar` (`hooks/parecer.py:389`), `metodo_mutante`/`endpoint_da_api` (:933, :948), `textos_da_api` e `gh_api_de_merge` (`hooks/conformidade.py:3202`, :3671), `aninhado` (:2327) e `alias_do_gh` do hook `parecer` (:550). Fora do domínio: mutantes, `docs/hooks-fixtures.md` e o fragmento do changelog.

Método: os três hooks de PreToolUse do Bash (`conformidade`, `parecer`, `pesado`) rodados direto com a montagem do próprio `tests/test_hooks.py` (`Fixture.montar`, `rodar`, prazo de produção, `PATH=/usr/bin:/bin`), projeto descartável na branch `feature/x`, papéis `forge:node-backend`, `forge:tech-lead` e a sessão principal. A base `95b09785` por `git archive`, rodada do mesmo jeito. O gh real só foi usado para provar o parse (host `localhost.invalid`, sem credencial, rede recusada pelo sandbox): `gh -X POST api graphql -f query=x` e `gh -f query=x api graphql` tentam `POST .../api/graphql`.

**C1 fechado nas formas citadas.** `gh api graphql -f query="$Q"`, ``gh api graphq`printf l` ...``, ``gh api user/re`echo pos` -f name=n``, `"$(cat q)"`, `${Q}`, `$"..."`, `-f "$K=..."`, argumento solto `"$A"`, `-F n=$N` sem aspas, as formas coladas (`-fquery=`, `-F=`, `--field=`, `--raw-field=`, `-iF`) e os envelopes (`env`, `command`, `/usr/bin/gh`, `"gh"`, `g\h`, `time`, `timeout`, `nohup`, `exec`, `xargs`, subshell, pipeline, `$( )`) saem 2 em todo papel. `bash -c`/`sh -c` com `\$` entre aspas duplas passa no `conformidade` (`aninhado` :2338 só troca `` \` ``), mas o `parecer` recusa `bash -c`/`sh -c` com `gh api` em todo papel; o alias do gh e o `GH_CONFIG_DIR` com expansão também ficam no `parecer`. As 16 fixtures tocadas passam (12,9 s).

**Só aperta ou neutro: sim.** 21 entradas na base e no head: tudo que a base barra o head barra; o head barra a mais a consulta em variável, `$( )`, crase e `-F n=$N` sem aspas. As legítimas seguem 0 nos dois: literal entre aspas simples e duplas, `\$` escapado, `-F "n=$N"`, `-H "X: $T"`, `--paginate`, `addStar` literal, REST `repos/$O/proj/pulls` e `issues -f title=$T`.

**Ainda passa sem ser lido (base e head, todos os hooks, todo papel):** A1 a A3 abaixo. Nenhum é regressão; todos são consulta GraphQL que altera o GitHub sem o hook ler, o que a decisão do dono (opção a) manda recusar.

`-X GET` com `-f query="$Q"` sai 0: neutro, o GitHub não executa mutação por GET. `-f "query[]=$Q"` sai 0: o gh manda `query` como lista, que o servidor recusa; sem caminho.

Suíte: a inteira é do CI; na leitura, o run do head remoto `d36a9e97` (só soma o parecer do review) tinha `bateria (passos)`, `instalação` e `verificações longas` verdes, a suíte pendente e `bateria (pareceres)`/`catraca` vermelhas à espera dos pareceres.

## Gatilhos
Gatilhos: controle de acesso do agente (hook de conformidade), ação irreversível no GitHub (merge que desvia a proteção da branch).

## Achados
- A1 (bloqueante) hooks/parecer.py:400 · `analisar` só vê `api` logo depois de `gh`; o gh aceita opção antes do subcomando. `gh -X POST api graphql -f query="$Q"`, a mutação literal `gh -f query='mutation{mergePullRequest...}' api graphql`, REST `gh -X PUT api repos/o/r/pulls/1/merge` e o alias `qp: -X POST api graphql` saem 0.
- A2 (bloqueante) hooks/conformidade.py:3212 · `textos_da_api` lê `/dev/stdin` sem conferir arquivo regular e acha o stdin do próprio hook vazio: `gh api graphql -F query=@/dev/stdin < q.graphql`, `--input /dev/stdin` e `@/proc/self/fd/0` saem 0 com o merge no arquivo.
- A3 (bloqueante) hooks/conformidade.py:368 · `expansao_por_palavra` e `consulta_ilegivel` (:3489) só tratam `$` e crase; o curinga fora de aspas (`*`, `?`, `[`) é expansão do shell: `gh api graphql -f query=mutation*` sai 0 e o bash troca pelo nome de arquivo com a mutação.

## Sondas
- S1 · `gh -X POST api graphql -f query="$Q"` (node-backend, tech-lead, sessão principal; conformidade, parecer, pesado) · espera: 2 R-CONFORMIDADE consulta que o hook não lê · obtido: 0 nos três hooks e nos três papéis (base igual)
- S2 · `gh -f query='mutation{mergePullRequest(input:{pullRequestId:\"PR_x\"}){clientMutationId}}' api graphql` · espera: 2 (R-CONFORMIDADE ou R-MAIN) · obtido: 0 nos três hooks e papéis
- S3 · `gh -X PUT api repos/o/r/pulls/1/merge` · espera: 2 R-MAIN merge por API · obtido: 0 (a mesma ordem, `gh api repos/o/r/pulls/1/merge -X PUT`, sai 2)
- S4 · gh real, sem credencial, host localhost.invalid: `gh -X POST api graphql -f query=x` e `gh -f query=x api graphql` · espera: erro de opção desconhecida · obtido: o gh tenta `POST https://localhost.invalid/api/graphql` (rede recusada pelo sandbox)
- S5 · `gh api graphql -F query=@/dev/stdin < q.graphql` com q.graphql = mutation mergePullRequest · espera: 2 · obtido: 0 nos três hooks e papéis; `--input /dev/stdin < q.json` e `-F query=@/proc/self/fd/0` também 0
- S6 · `gh api graphql -F query=@q.graphql` (mesmo arquivo, caminho comum) · espera: 2 · obtido: 2 R-MAIN (controle: o arquivo legível é lido; só o stdin por caminho escapa)
- S7 · `gh api graphql -f query=mutation*` e `-fquery=mutatio?` · espera: 2 · obtido: 0 nos três hooks; `printf '[%s]' query=mutation*` no bash com o arquivo `query=mutation{mergePullRequest(...)...}` na pasta imprime a mutação inteira
- S8 · `gh qp -f query="$Q"` com `aliases: qp: -X POST api graphql` no config.yml legível · espera: 2 · obtido: 0 nos três hooks e papéis

## Detalhe dos achados
**A1, opção antes do subcomando (alta, esforço P a M, dono: tech-lead, autor do hook).** Evidência: `hooks/parecer.py:400`; S1 a S4, S8. Caminho: um agente de qualquer papel, no Bash, escreve a mesma chamada com uma opção antes de `api`; o gh (pelo parse do cobra, que pula as opções antes de achar o subcomando) roda o `gh api` normalmente; nenhum hook o reconhece como `api`, então `consulta_ilegivel`, `gh_api_de_merge` (R-MAIN), `gh_api_cria_pr` e as travas de repositório público não rodam. Ganho: merge que desvia a proteção da branch, ou qualquer mutação GraphQL, sem leitura. Correção mínima: em `analisar`, achar o subcomando como o gh: pular as opções antes da 1ª posicional (`-X v`, `-f v`, `-H v` e toda opção de duas letras ou longa sem `=` levam o valor seguinte; com `=` ou de uma palavra, não) e, se a 1ª posicional for `api`, devolver `("api", <todas as palavras depois de gh menos o api>)`; na dúvida (opção antes do subcomando que o hook não classifica, com `api` ou `pr` adiante), recusar. O alias do gh volta por `gh_pelo_alias` e herda a correção. Fixtures: S1, S2, S3, S8 (e `--method POST`, `-H x`, `-p x`, `-i` antes de `api`).

**A2, entrada padrão por caminho (alta, esforço P, dono: tech-lead).** Evidência: `hooks/conformidade.py:3212`; S5, S6. O commit diz que "o arquivo e a entrada padrão que o hook não lê já recusavam"; `-` e `@-` recusam, mas `/dev/stdin`, `/dev/fd/0` e `/proc/self/fd/0` são caminhos que o hook abre no próprio processo, cujo stdin (o JSON do evento) já foi lido: o texto vem vazio e passa como legível. Caminho: `gh api graphql -F query=@/dev/stdin < q.graphql`, ou `printf '%s' "$Q" | gh api graphql -F query=@/dev/stdin`. Correção mínima: `textos_da_api` ler pelo `_gh_api.ler_regular` (abre sem bloquear e recusa o que não é arquivo regular: FIFO, dispositivo, `/proc`), e tratar o `OSError` como ilegível, como já faz `textos_do_gh_api`. Fixtures: S5 nas três formas.

**A3, curinga fora de aspas (média, esforço P, dono: tech-lead).** Evidência: `hooks/conformidade.py:368` e :3489; S7. Caminho: o agente grava um arquivo cujo nome é `query=mutation{mergePullRequest(...)...}` (pelo Write, ou montado com `printf` para o texto não aparecer) e roda `gh api graphql -f query=mutation*`; o bash troca a palavra pelo nome do arquivo e o gh manda a mutação. Correção mínima: em `expansao_por_palavra`, `*`, `?` e `[` fora de aspas sobem a palavra ao nível 2, e `consulta_ilegivel` consulta também a palavra que os traz (hoje só `parecer.expande`, :3489). A consulta legível com lista (`[ID!]`) entre aspas segue livre. Fixtures: S7 e a legível `-f query='query($i:[ID!]!){nodes(ids:$i){id}}'`.

Fora do escopo, como cartão (não bloqueia): `aninhado` (`hooks/conformidade.py:2338`) refaz o nível de dentro trocando só `` \` `` por crase; o `\$` entre aspas duplas, que o shell de fora vira `$`, segue literal no `conformidade`. Hoje o `parecer` cobre (recusa `bash -c`/`sh -c` com `gh api`), mas o `conformidade` sozinho não; vale trocar também `\$` na releitura, pelo mesmo motivo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: os hooks rodados localmente com a montagem do teste, a base por `git archive`, o gh real só para provar o parse contra host inválido, sem credencial, e o bash local para o curinga. gitleaks, semgrep e zizmor não se aplicam a este diff.
