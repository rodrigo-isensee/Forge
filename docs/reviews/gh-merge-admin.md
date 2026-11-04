---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: dfcc2b2936bab0980b51b87e6049c1c53aecb74c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: gh-merge-admin (versao-033, E1.3)

Revisor: `forge:tech-lead`, outra instância (D-ETAPAS-INST); não sou o autor do E1.2. Base `928e61b`, um commit (`6c7e573`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:1667 · resolvido na rodada 2: `-R`/`--repo` entre `pr` e `merge` recusa com R-MAIN (parecer.py:231). Rodada 1: `gh pr -R dono/repo merge 12 --admin` saía com rc=0.
- A2 (bloqueante) hooks/parecer.py:499 · resolvido na rodada 2: `--input=`, `-f`/`-F` colados e `merges -fbase=` recusam. Rodada 1: as formas coladas saíam com rc=0.
- A3 (recomendado) tests/hooks/conformidade/gh-merge-admin-admin-e-bash-c-bloqueia.json:17 · resolvido na rodada 2: o esperado das quatro fixtures traz o texto da recusa nova.
- A4 (recomendado) tests/test_hooks.py:2164 · resolvido na rodada 2: heredoc, xargs, `--repo=`, conferente, homolog e as linhas de A1 e A2 têm fixture.
- A5 (recomendado) hooks/conformidade.py:1664 · resolvido na rodada 2: as specs `tests/mutantes/gh-merge-admin.json` e `gh-merge-admin-2.json` cobrem G1 a G23, sem o G13, que caiu com a alternativa morta.
- A6 (bloqueante) hooks/parecer.py:501 · resolvido na rodada 3: `desagrupa_i` separa o `-i` agrupado antes de `metodo_mutante`, `endpoint_da_api` e `textos_da_api`; `-iX PUT`, `-iXPUT`, `merges -iX POST`, `-if` e `-iF query=@arq graphql` recusam com R-MAIN.
- A7 (recomendado) hooks/conformidade.py:1608 · fora do E1 e anterior à base: o `gh_trava` lê `-X` sem `desagrupa_i`, e `gh api -iX DELETE repos/o/r` sai com rc=0 (sem `-i`, recusa). O mesmo vale em :1626. Vira cartão para o `security-engineer`.
- A8 (bloqueante) hooks/parecer.py:505 · resolvido na rodada 4: `desagrupa_i` copia como veio o token que segue uma opção de `API_COM_VALOR`; `-p`, `-q`, `--jq`, `-H`, `-t` e `--preview` antes de `-iX`, `-iH` ou `-if` recusam com R-MAIN.
- A9 (bloqueante) hooks/parecer.py:517 · resolvido na rodada 5: `ultimo_metodo` vale o último `-X`/`--method` (separado, `=`, colado) e pula o valor de `API_COM_VALOR`; `-X GET -X PUT …/merge` e `-X GET -X POST graphql -F query=@q.graphql` recusam com R-MAIN.
- A10 (recomendado) hooks/conformidade.py:1608 · mesma leitura do A9 fora do E1, já na base: `gh api -X GET -X DELETE repos/o/r` e `-X GET -X PUT .../branches/main/protection -f x=y` saem com rc=0; o mesmo em :1626. Segue com o A7, em cartão ao `security-engineer`.
- A11 (bloqueante) hooks/parecer.py:555 · resolvido na rodada 7: o atalho só-GET decide por `ultimo_metodo_real`, que pula o valor de `API_COM_VALOR`. Rodada 6: `-p -XGET -f query=…mergePullRequest… graphql` e `merges -f base=` saíam com rc=0.

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

## Rodada 3
Head `2e9c621`, sobre `9535b63`. Delta lido: `git diff 9535b63..2e9c621 -- hooks/ tests/ changelog.d/`. Ele traz `hooks/parecer.py` +14/-1 (`desagrupa_i` e o seu uso em `metodo_mutante` e `endpoint_da_api`), `hooks/conformidade.py` +1/-1 (`textos_da_api`), 5 fixtures novas `gh-merge-admin-api-opcao-curta-agrupada-*-bloqueia.json`, os mutantes G24 e G25 em `tests/mutantes/gh-merge-admin-2.json` e o changelog. Já lido e não tocado pelo delta: `gh_admin`, `analisar`, `gh_api_de_merge`, `merge_por_api` e as 63 fixtures anteriores.

- **A6, resolvido.** O `gh api` só tem o `-i` como curta booleana, então separar o `-i` do resto agrupado reproduz a leitura do `gh`. Sondas na `Fixture` do teste: as seis formas do brief recusam com R-MAIN, e também `-iX=PUT`, `-iiX PUT`, `-i -XPUT`, `-ifquery=@arq`, `-iFquery=@arq`, `-iX PUT --input q.json graphql` e a forma dentro de shell com `-c`. O bloco do API_ADMIN também fecha (`-iX PUT …/branches/main/protection` recusa com R-CONFORMIDADE).
- **C-5, sem regressão.** `gh api -i …/pulls/1/merge`, `-iX GET …/merge`, `-iq .x …/pulls/1` e `-i graphql -f query='query{…}'` liberam (rc=0). A troca de `-i?[fF]` por `-[fF]` não afrouxa, porque o `-if…` já chega separado.
- **A8, novo e bloqueante (regressão, C-4 e T-4).** `desagrupa_i` também desmonta o valor de uma opção valorada. Com `-p -iX` antes do endpoint, o `-X` desmontado toma o endpoint como valor e `endpoint_da_api` fica vazio. Sonda no hook `parecer`, com `gh api -p -iX repos/o/r/pulls/1/merge -X PUT`: rc=2 (R-CONTRIB) na base e rc=0 na head. O `conformidade` libera nas duas, e o mesmo vale com `-q`, `-H` e `--preview -if … merges`. Eu tinha deixado isso passar no primeiro fechamento desta rodada. O `security-engineer` achou (o A7 do parecer dele) e eu confirmei antes do envio. Sugestão: o mesmo pulo de `posicionais`, sem desmontar o token que segue uma opção de `API_COM_VALOR`, inclusive a que fecha o grupo. Cada forma leva uma fixture `-bloqueia`, e o pulo leva um mutante.
- **C-1 a C-3 e C-6, cumpridos.** Sem rede e sem `gh` novo; `desagrupa_i` é linear no número de palavras. O C-4 cai pelo A8.
- **A7, recomendado.** Mesma classe do A6 num controle fora do E1 (apagar repositório, 2.5), já presente na base `928e61b`. Não devolve a entrega; segue em cartão ao `security-engineer`.
- **Achado recorrente.** A linha AR da classe "forma de opção do `gh` não normalizada" (A2, A6, A7) segue pendente, porque o brief só permite commitar o parecer.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `2e9c621`: `Ran 71 tests in 951.181s`, `OK` (D-5).
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...2e9c621`, só código e teste: `hooks/conformidade.py` 28, `hooks/parecer.py` 58 e `tests/test_hooks.py` 5, total de 91 linhas. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.

**Parecer da rodada 3: reprovado.** A1 a A6 estão resolvidos e o A7 é recomendação. O A8 bloqueia. Segurança e QA têm parecer próprio (E1.4 e E1.6).

## Rodada 4
Head `150f360`, sobre `2e9c621`. Delta lido, pela saída de `bin/forge-check delta 2e9c621 150f360`: `hooks/parecer.py` :503, :505-508 e :513 (o pulo do valor em `desagrupa_i`), as 8 fixtures `gh-merge-admin-api-valor-de-opcao-*-bloqueia.json` e os mutantes G26 e G27 em `tests/mutantes/gh-merge-admin-2.json` :144-163. Já lido e não tocado pelo delta: `gh_admin`, `analisar`, `gh_api_de_merge`, `merge_por_api`, `textos_da_api`, `metodo_mutante`, `endpoint_da_api` e as 68 fixtures anteriores.

- **A8, resolvido.** O token que segue uma opção de `API_COM_VALOR` é copiado como veio, inclusive depois do `-X` que fecha um grupo (`-iX PUT`). É a leitura do `gh`, cujo parser dá o próximo token como valor da opção valorada mesmo quando ele começa com `-`. Sondas na `Fixture` do teste, no `conformidade`: as 8 formas das fixtures recusam com R-MAIN, e também `--template`, `--cache` e `--hostname` antes de `-iX`, `-ip -iX` e as formas do A6 (`-iX PUT`, `-iXPUT`). No `parecer`, as formas REST de `pulls/<n>/merge` voltam a recusar com R-CONTRIB, como na base.
- **Mutantes G26 e G27.** Apliquei cada um numa cópia da head: `gh api -p -iX repos/o/r/pulls/1/merge -X PUT` sai com rc=0 nos dois, então a fixture `-p` os mata.
- **C-5, sem regressão.** `gh api repos/o/r/pulls/12/merge` (GET), `--jq .merged`, `-p x … --jq .merged`, `-H Accept:x -i …`, `-q -iX repos/o/r/pulls/12` e `gh pr view 12 --json mergeStateStatus,mergeable` liberam (rc=0) nos dois hooks.
- **A9, novo e bloqueante (segurança com gatilho, C-4).** `metodo_mutante` lê o primeiro `-X` (`opcao`, parecer.py:135). O `gh` vale o último: `gh api --hostname ghe.invalid -X GET -X PUT repos/o/r/pulls/1/merge --verbose` imprime `> PUT /api/v3/repos/o/r/pulls/1/merge`. Por isso `gh api -X GET -X PUT repos/o/r/pulls/1/merge`, `--method GET --method PUT`, `-XGET -XPUT`, `-X GET <endpoint> -X PUT` e `-X GET -X POST graphql -F query=@q.graphql` saem com rc=0 no `conformidade` e no `parecer`. Já estava em `6c7e573` e passou nas três rodadas anteriores. Não é regressão: a base também libera. Mas é a mesma porta do A6, que o C-4 manda recusar, então classifico pelo mesmo critério. Sugestão: o método vem da última ocorrência de `-X`/`--method`, lida com o pulo de valor de `posicionais`. Cada forma ganha uma fixture `-bloqueia`, e a escolha da última ocorrência ganha um mutante.
- **A10, recomendado.** A mesma leitura do A9, nos controles fora do E1 (`gh_trava`, conformidade.py:1608 e :1626), já na base. `gh api -X GET -X DELETE repos/o/r` sai com rc=0, e sem o `-X GET` recusa. Não devolve a entrega. Segue com o A7, em cartão ao `security-engineer`.
- **C-1 a C-3 e C-6, cumpridos.** Sem rede e sem `gh` novo; `desagrupa_i` continua linear.
- **Achado recorrente.** A classe "leitura de opção do `gh api` diferente da do `gh`" volta pela quarta vez (A2, A6, A8, A9). A linha AR segue pendente, porque o brief só permite commitar o parecer.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `150f360`: `Ran 71 tests in 882.019s`, `OK` (D-5). As sondas e os mutantes ficaram em `$TMPDIR/tech-lead-gh-merge-admin/`.
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...150f360`, só código e teste: `hooks/conformidade.py` 28, `hooks/parecer.py` 63 e `tests/test_hooks.py` 5, total de 96 linhas. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.

**Parecer da rodada 4: reprovado.** A1 a A6 e A8 estão resolvidos. A7 e A10 são recomendações. O A9 bloqueia. Segurança e QA têm parecer próprio (E1.4 e E1.6), e o A9 também vai para o `security-engineer`.

## Rodada 5
Head `75968a9`, sobre `578f6de` (a volta 4 traz `4f7879a`, `a6dc08f` e `75968a9`). Delta lido, pela saída de `bin/forge-check delta --parecer docs/reviews/gh-merge-admin.md`: `hooks/parecer.py` :517-540 (`ultimo_metodo` e a troca em `metodo_mutante`), as 9 fixtures `gh-merge-admin-api-metodo-repetido-*-bloqueia.json` e os mutantes G28 a G36 em `tests/mutantes/gh-merge-admin-3.json`. Já lido e não tocado pelo delta: `gh_admin`, `analisar`, `gh_api_de_merge`, `merge_por_api`, `textos_da_api`, `desagrupa_i`, `endpoint_da_api` e as 76 fixtures anteriores (85 `gh-merge-admin-*` ao todo).

- **A9, resolvido.** O método agora vale a última ocorrência, como no `gh`, e o token que segue uma opção de `API_COM_VALOR` é pulado como valor. Sondas na `Fixture` do teste, no `conformidade`: `-X GET -X PUT`, `--method GET --method PUT`, `--method=`, `-XGET -XPUT`, `-X=GET -X=PUT`, `-X GET <endpoint> -X PUT`, `-X GET -iX PUT`, `-X GET --method=PUT`, `-H -XGET -X PUT` e `-X GET -X POST graphql -F query=@q.graphql` recusam com R-MAIN; no `parecer`, as formas REST recusam com R-CONTRIB.
- **C-5, sem regressão.** Liberam (rc=0), e o `gh` também manda GET: `-X PUT -X GET …/merge`, `-X GET …/merge -q -XPUT` (o `-XPUT` é valor do `-q`), `-XPOST -XGET …/merges -f base=main` (GET com os campos na consulta) e `--jq .merged`. `-X PUT --method= …/merge` libera: o método vazio vira GET no cliente HTTP do `gh`, e com campo cai no ramo dos campos e recusa. `-X POST -X GET graphql -F query=@…` passou a liberar (recusava em `150f360`): o `gh` manda GET, e o GraphQL do GitHub não executa mutação por GET. É a leitura do `gh`, não afrouxa o C-4.
- **Mutantes.** Apliquei G28, G31 e G36 numa cópia da head: `-X GET -X PUT …/merge` (G28) e `-X PUT -H -XGET …/merge` (G31, G36) saem com rc=0, e as fixtures `x-get-x-put` e `x-put-e-h-xget-depois` os matam.
- **A10, recomendado, sem mudança.** `gh api -X GET -X DELETE repos/o/r` segue com rc=0, porque conformidade.py:1608 e :1626 ainda leem o primeiro `-X` por `opcao`. Está fora do E1 e já estava na base. Com `ultimo_metodo` pronto, o ajuste ali fica de uma linha. Segue com o A7, em cartão ao `security-engineer`.
- **C-1 a C-4 e C-6, cumpridos.** Sem rede e sem `gh` novo; `ultimo_metodo` é linear no número de palavras.
- **Achado recorrente.** A classe "leitura de opção do `gh api` diferente da do `gh`" (A2, A6, A8, A9) segue sem a linha AR, porque o brief só permite commitar o parecer.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `75968a9`: `Ran 71 tests in 800.570s`, `OK` (D-5). As sondas e os mutantes ficaram em `$TMPDIR/tech-lead-gh-merge-admin/`.
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...75968a9`, só código e teste: `hooks/conformidade.py` 28, `hooks/parecer.py` 85 e `tests/test_hooks.py` 5, total de 118 linhas. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.

**Parecer da rodada 5: aprovado.** A1 a A6, A8 e A9 estão resolvidos. A7 e A10 são recomendações e não devolvem a entrega. Segurança e QA têm parecer próprio (E1.4 e E1.6).

## Rodada 6
Head `b1991c6`, sobre `75968a9`. A volta 5 (`97e98b6`, `daf71fe`, `03d4ce5`, `07cbbaf`, `ff76815`) e a volta 6 (`85c89f2`, `d4e1b40`, `079a77b`, `b1991c6`) entram juntas. Delta lido, pela saída de `bin/forge-check delta --parecer docs/reviews/gh-merge-admin.md`: `hooks/parecer.py` :517-538 (`metodos_pedidos` no lugar de `ultimo_metodo` e as duas condições novas de `metodo_mutante`), as 7 fixtures novas (`api-p-xput-bloqueia`, `api-valor-de-opcao-parece-x-bloqueia`, as 4 `api-metodo-primeiro-mutante-*-bloqueia` e `legitimo-api-x-get-com-campo-libera`) e `tests/mutantes/gh-merge-admin-3.json` (isenção nova, G28, G29, G31 e G33 trocados, G36 fora, G37). Já lido e não tocado pelo delta: `hooks/conformidade.py`, `desagrupa_i`, `endpoint_da_api`, `gh_api_de_merge`, `merge_por_api`, `textos_da_api` e as 85 fixtures anteriores (92 `gh-merge-admin-*` ao todo, recontadas).

- **A10 da segurança, resolvido no que ele pede.** Todo `-X`/`-XV`/`-X=V`/`--method`/`--method=V` entra em `metodos_pedidos`, inclusive como valor de outra opção de `API_COM_VALOR`, e qualquer um diferente de GET torna o `gh api` mutante. Sondas com a árvore de cada revisão: `-p -XPUT …/pulls/1/merge` e `-H -XPUT -q -XDELETE` recusam.
- **T-4, voltou à base.** `-X PUT -X GET …/pulls/1/merge` e `-X PUT --method= …/pulls/1/merge` recusam no `conformidade` (R-MAIN) e no `parecer` (R-CONTRIB), como o `parecer` da base `928e61b`; em `6d6e7f1` saíam com rc=0. `-X DELETE -X GET repos/o/r` recusa no `conformidade` ("apagar o repositório"), como na base.
- **A11, bloqueante (regressão nova).** A condição `if metodos: return False` (parecer.py:537) trata como GET pedido o `-XGET` que é valor de outra opção. O `gh` lê esse token como valor (`-p`, `-q`, `-t` ou `-H`), não tem método explícito e manda POST com os campos. Saem com rc=0 em `b1991c6` e recusavam em `6d6e7f1`: `gh api -p -XGET -f query='mutation{mergePullRequest(…)}' graphql`, `gh api -t -XGET -f query='mutation{enablePullRequestAutoMerge(…)}' graphql`, `gh api -p -XGET -f base=main -f head=x repos/o/r/merges` e `gh api -q --method=GET -f base=main -f head=x repos/o/r/merges`. É o C-4 com gatilho: o agente mescla por GraphQL ou por `merges`. O mesmo caminho abre o bloco de `API_ADMIN` (`-p -XGET -f … repos/o/r/git/refs` sai com rc=0 e recusava em `6d6e7f1`). A base `928e61b` também liberava, então não fere o T-4. O defeito é a falha fechada que vira aberta no ramo do GET. Uma correção possível, sem afrouxar nada: contar todos os tokens só para recusar e liberar os campos apenas quando o GET vier de um `-X`/`--method` que não seja valor de opção, como lia o `ultimo_metodo`. Junto, a fixture `-p -XGET -f query=…mergePullRequest… graphql` com bloqueio e um mutante que tire essa distinção.
- **C-5.** Os legítimos do modelo seguem liberando: `gh api repos/o/r/pulls/12/merge`, `--jq .merged`, a leitura GraphQL de `mergeable mergeStateStatus` e `-X GET -f q=1 …/merge`. Pela DECISÃO TÉCNICA de 21:37, passam a recusar dois casos que a rodada 5 dava como legítimos: `-X GET …/merge -q -XPUT` e `-XPOST -XGET …/merges -f base=main`. Nenhum dos dois está no C-5, e a recusa é da falha fechada decidida.
- **Mutantes.** A isenção de `metodo.upper() != "GET"` tem motivo e está coberta por G28 e G29. G31 agora guarda o `-p -XPUT`. G37 guarda o `if metodos:`, mas nenhum mutante guarda o caso do A11.
- **A7 e A10 (review), sem mudança.** `gh api -X GET -X DELETE repos/o/r` e `-iX DELETE repos/o/r` seguem com rc=0 em `conformidade.py:1608`. Estão fora do E1 e já na base, em cartão ao `security-engineer`.
- **C-1 a C-3 e C-6, sem mudança.** O delta não toca `gh_admin` nem a leitura da linha. `metodos_pedidos` é linear, sem rede e sem `gh` novo.
- **Achado recorrente.** O A11 é da mesma classe de A2, A6, A8 e A9: a leitura de opção do `gh api` diferente da do `gh`. Segue sem a linha AR, porque o brief só permite commitar o parecer.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `b1991c6`: `Ran 71 tests in 717.560s`, `OK` (D-5). Sondas em `$TMPDIR/tech-lead-gh-merge-admin/`.
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...b1991c6`, só código e teste: `hooks/conformidade.py` 28, `hooks/parecer.py` 87 e `tests/test_hooks.py` 5, total de 120 linhas. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.

**Parecer da rodada 6: reprovado.** O A10 da segurança e o T-4 estão resolvidos. O A11 bloqueia e vai também ao `security-engineer`. A7 e A10 (review) são recomendações. Segurança e QA têm parecer próprio (E1.4 e E1.6).

## Rodada 7
Head `dfcc2b2`, sobre `b1991c6` (volta 7: `14fc4bf..dfcc2b2`). Delta lido, pela saída de `bin/forge-check delta --parecer docs/reviews/gh-merge-admin.md`: `hooks/parecer.py` :531-547 (`ultimo_metodo_real`, novo) e :554-555 (o atalho só-GET de `metodo_mutante`), as 7 fixtures novas (4 `api-metodo-valor-de-opcao-*-bloqueia` e 3 `legitimo-api-*-get-com-campo-libera`), `tests/mutantes/gh-merge-admin-3.json` (isenção fora, G31, G34, G35 e G37 com trecho único, G38 a G44 novos) e a linha AR-11 de `docs/engineering/achados-recorrentes.md`. Já lido e não tocado pelo delta: `hooks/conformidade.py`, `metodos_pedidos`, `desagrupa_i`, `endpoint_da_api`, `gh_api_de_merge`, `textos_da_api` e as 92 fixtures anteriores (99 `gh-merge-admin-*` ao todo, recontadas).

- **A11, resolvido.** A recusa segue pelo `any` sobre `metodos_pedidos`. O atalho que libera os campos só vale quando o último `-X`/`--method` que o `gh` lê de fato é GET, e `ultimo_metodo_real` pula o valor de qualquer opção de `API_COM_VALOR`. Sondei `metodo_mutante` com a árvore de cada revisão (`6d6e7f1`, `b1991c6`, `dfcc2b2`). As 6 formas da rodada 6 (`-p -XGET` e `-t -XGET` com GraphQL, `-p -XGET` e `-q --method=GET` com `merges`, `-p -XGET` com `git/refs`, `-p -XGET -F query=@arq graphql`) eram liberadas em `b1991c6` e voltam a ser mutantes em `dfcc2b2`, como em `6d6e7f1`.
- **Rótulo da recusa.** As fixtures de `merges` e de GraphQL com arquivo recusam com R-MAIN. `git/refs` e `enablePullRequestAutoMerge` recusam antes, no bloco R-CONFORMIDADE de `API_ADMIN`/`GRAPHQL_PERIGOSO`, pela DECISÃO TÉCNICA de 2026-11-04 04:10. O C-4 fica coberto nos dois casos.
- **Sem regressão.** Em 27 sondas, nenhuma forma que `b1991c6` recusava passa a liberar. Os legítimos do C-5 seguem liberando: `repos/o/r/pulls/12/merge`, `--jq .merged`, e `-X GET`, `-XGET`, `-X=GET`, `--method=GET`, `--method GET` e `-iXGET` com `-f`. Também libera `-X GET -p -XGET -f`, em que o `gh` lê GET. `-X` sem valor no fim segue recusando, sem exceção.
- **A10 (segurança) e T-4, como na rodada 6.** `-p -XPUT …/pulls/1/merge` e `-X PUT -X GET …/pulls/1/merge` seguem mutantes, e `hooks/conformidade.py` não muda no delta.
- **A7 e A10 (review), sem mudança.** Estão fora do E1 e já na base, em cartão ao `security-engineer`.
- **C-1 a C-3 e C-6, sem mudança.** `ultimo_metodo_real` é linear, sem rede e sem `gh` novo.
- **Mutantes.** G38 troca o atalho por `metodos[-1]` e cai nas fixtures `-p -XGET`. G39 e G40 guardam o pulo do valor, e G41 a G44, cada forma do método real. G42 cai na fixture `x-final-sem-valor`, que já existia. A isenção saiu, e o trecho dela agora tem mutante. A mutação é do autor (V2) e não a refiz.
- **Achado recorrente.** A linha AR-11 segue o formato do arquivo, com classe, ID, contagem de 5 (A2, A6, A8, A9 e A11) e a linha do defeito da rodada 6. Conferida.
- **Testes.** `python3 -m unittest tests.test_hooks` na worktree, no head `dfcc2b2`: `Ran 71 tests in 752.946s`, `OK` (D-5). Sondas em `$TMPDIR/tech-lead-gh-merge-admin/sonda-r7.py`.
- **Teto (M14).** `git diff --numstat --no-renames 928e61b...dfcc2b2`, só código e teste: `hooks/conformidade.py` 28, `hooks/parecer.py` 105 e `tests/test_hooks.py` 5, total de 138 linhas. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.

**Parecer da rodada 7: aprovado.** O A11 está resolvido, sem regressão. O A10 da segurança e o T-4 seguem resolvidos. A7 e A10 (review) são recomendações fora do E1. Segurança e QA têm parecer próprio (E1.4 e E1.6).
