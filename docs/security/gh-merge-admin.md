---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 2e9c621b0f6939f1b82b74d36bfd55957f79f610
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: gh-merge-admin (E1 da 0.33)

Base `928e61b66015f7ee2a2e585dc8178e07dc16be39`. Rodada 1 sobre `6c7e573` (reprovado, A1 a A4 bloqueantes, A5 recomendado). Rodada 2 sobre `9535b63` (reprovado, A6). Rodada 3 sobre `2e9c621` (a volta 2 do autor, contra o A6): revalidação do delta `9535b63..2e9c621` em `hooks/`, `tests/` e `changelog.d/` (`forge-check delta --parecer` sobre este parecer) contra o A6, os controles C-1 a C-8 e as mudanças proibidas T-1 a T-5 de `docs/security/ameacas/versao-033.md` (seção E1).

## Gatilhos
`controles do Forge`: `hooks/conformidade.py` e `hooks/parecer.py` (classificador de comando, `R-MAIN`, `R-CONTRIB`, `R-REVIEW`). Não toca segredo, dependência, workflow nem o pre-push.

## Achados
- A7 (bloqueante) hooks/parecer.py:505 · desagrupa_i desmonta também o valor de opção valorada: `gh api -p -iX repos/o/r/pulls/1/merge -X PUT` (e com -q, --jq, -H, -t) passa nos dois hooks; a base recusava no parecer; contra C-4 e T-4; classe: segurança com gatilho
- A8 (recomendado) hooks/conformidade.py:1608 · gh_trava lê o método com parecer.opcao sem desagrupa_i: `gh api -iX DELETE repos/o/r` passa (igual na base, fora do E1); mesma família, cartão próprio; classe: recomendação

## Rodada 3
Veredito: **reprovado**. O A6 está resolvido nas sete formas da rodada 2, mas a correção abriu uma regressão (A7): um texto que a base recusava passa a ser liberado.

**A6 resolvido.** `hooks/parecer.py:501` (`desagrupa_i`) desmonta `-i<letra><resto>` em `-i` e `-<letra><resto>`, e entra em `metodo_mutante` (`:514`), `endpoint_da_api` (`:525`) e `textos_da_api` (`hooks/conformidade.py:1390`). Sondas na head, como `tech-lead` e `security-engineer` (`conformidade` | `parecer`): `gh api repos/o/r/pulls/1/merge -iX PUT` (2 | 2), `... -iXPUT` (2 | 2), `gh api repos/o/r/merges -iX POST` (2 | 0), `gh api -H 'Accept: x' -iX PUT repos/o/r/pulls/1/merge` (2 | 2), `gh api -iX POST graphql -F query=@q.graphql` (2 | 0), `gh api -if query=@q.graphql graphql` (2 | 0), `gh api -iF query=@q.graphql graphql` (2 | 0), e ainda `-iiX PUT` e `-iX=PUT` (2 | 2). Na base, rc 0 nos dois hooks. O `parecer` só olha `pulls/<n>/merge`, como na base; a recusa do `merges` e do GraphQL vem do `conformidade`, que roda em toda chamada. A troca de `-i?[fF]` por `-[fF]` em `metodo_mutante` (`:520`) não perde forma: o `-if` chega como `-f` depois da desmontagem. Os legítimos `gh api -i repos/o/r/pulls/1`, `... -i` no fim, `-iH Accept:x` e `-iq .x` em GET passam (0 | 0), como na base. Faltam fixtures da sonda com `-H` antes e de `-iiX` (recomendação, sem achado: a desmontagem é a mesma).

**A7** (alta, esforço P, dono `forge:tech-lead`). Evidência: `hooks/parecer.py:505` aplica a desmontagem a todo argumento, inclusive ao valor de uma opção valorada. Com o valor igual a `-iX` (ou `-iH`, `-if`), o resto do grupo vira uma opção que toma o próximo token, o endpoint, e `posicionais` devolve vazio. O `gh` lê o valor como texto e manda a requisição: com `-p`/`--preview` o valor só entra no cabeçalho `Accept`, e com `-q`/`--jq`/`-t` ele só é aplicado à resposta, depois do merge. Sondas, head | base (`conformidade`, `parecer`): `gh api -p -iX repos/o/r/pulls/1/merge -X PUT` (0 0 | 0 2), o mesmo com `-q -iX`, `--jq -iX`, `-t -iH`, `-H -iX`, `-p -iX ... --method PUT` e `-p -iX -X PUT repos/o/r/pulls/1/merge` (0 0 | 0 2). Também passam, na head e na base, `cd /tmp && gh api -p -iX repos/o/r/pulls/1/merge -X PUT`, `gh api --preview -if repos/o/r/merges -f base=main -f head=x` e `gh api -p -iX graphql -F query=@q.graphql` (arquivo com `mergePullRequest`), que o C-4 manda recusar em toda pasta. Com o valor no fim (`... -X PUT -p -iX`) recusa. Ator e ganho: os da rodada 1 (o modelo de qualquer papel, merge que pula checks e review). Fere o C-4 e a T-4 (o `R-CONTRIB` de merge por API, recusado na base, passa a liberar). Correção mínima: em `desagrupa_i`, percorrer por índice e copiar sem desmontar o token que segue toda opção de `API_COM_VALOR` (a lista inteira: `-X`, `--method`, `-H`, `--header`, `-f`, `--raw-field`, `-F`, `--field`, `--input`, `-q`, `--jq`, `-t`, `--template`, `--hostname`, `--cache`, `-p`, `--preview`), inclusive a que fecha um grupo (`-iX` toma o próximo como valor). Fixtures para as dez sondas acima e um mutante que tire o pulo do valor.

**A8** (recomendado, média, esforço P, dono `forge:tech-lead`). Evidência: `hooks/conformidade.py:1608` e `:1626` leem o método com `parecer.opcao(args, "--method", "-X")` sem a desmontagem; `gh api -iX DELETE repos/o/r` passa (0 | 0), na head e na base, enquanto `-X DELETE` recusa (`R-CONFORMIDADE`). Não é regressão nem é do E1 (apagar e tornar público o repositório, `gh_trava`); é a mesma classe do A6 em outro controle. Proposta: cartão próprio para usar a leitura desmontada (com a correção do A7) em `gh_trava` e `input_publica`.

**A5 resolvido.** A matriz da seção E1 do modelo de ameaças ganhou as linhas das dimensões novas da rodada 1 (programa por caminho, `./` e expansão; `-R`/`--repo` entre `pr` e o subcomando; campo colado; `graphql?`), a do A6 (opção curta agrupada ao `-i`) e a do A7 (valor de opção valorada com a forma de um grupo), no commit do modelo neste mesmo passo.

**Controles na head `2e9c621`.**
- C-1: `--admin` em qualquer forma e posição recusa em todo papel; o delta não toca `usa_admin` nem `gh_admin`.
- C-2: a recusa segue antes das saídas antecipadas; o delta não mexe na ordem.
- C-3: as posições da matriz seguem pelo mesmo leitor (`bash -c` com `-q -iX` recusa pelo `R-CONFORMIDADE`); sem parser novo de linha, só a desmontagem dos argumentos do `gh api`.
- C-4: REST e GraphQL, inline, em arquivo, colados e agrupados ao `-i` recusam, menos o valor de opção valorada com a forma de um grupo (A7).
- C-5: os oito legítimos do modelo e os GET com `-i` mantêm o veredito da base nos dois hooks.
- C-6: nada de rede nem `gh` novo; a desmontagem é linear no número de argumentos.
- C-7: os casos de abuso (a) a (g) seguem recusados e (h) passa, pelas fixtures do lote `test_fixtures_do_gh_merge_admin`; faltam os do A7.
- C-8: os mutantes G24 (sem a desmontagem) e G25 (o resto sem o `-`) de `tests/mutantes/gh-merge-admin-2.json` cobrem o A6; falta o do A7.
- T-1 a T-3: sem condição de papel, base, projeto ou repositório; sem leitura do valor de `--admin=`; sem escape por ambiente ou configuração.
- T-4: violada pelo A7 (o `merge_por_api` do `parecer`, `R-CONTRIB`, deixa de recusar as formas da sonda).
- T-5: o alias do `gh` segue fora: risco residual, N1, cartão próprio.

PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-10), conferida de novo: o A7 se aproxima da AR-10 (texto que o leitor desmonta diferente do programa) e é classe nova para a desmontagem de argumentos; AR-1: a lista de mutantes não tem o caso do valor; AR-3, AR-5 e AR-7 não se aplicam ao delta.

## Rodada 2 (histórico, 9535b63)
Achados da rodada 2: A6 (bloqueante, opção curta agrupada ao `-i`), resolvido na rodada 3; A5 (recomendado, linhas da matriz), resolvido na rodada 3.

Veredito: **reprovado**. Os quatro bloqueantes da rodada 1 estão resolvidos e nenhum texto recusado na base passa a ser liberado, mas a varredura da família `gh api` achou o A6 (opção curta combinada), que a rodada 1 também deixou passar: dimensão nova da matriz, levantada em paralelo pelo review (A6 de `docs/reviews/gh-merge-admin.md`) e confirmada aqui por sonda.

**A6** (alta, esforço P, dono `forge:tech-lead`). Evidência: `hooks/parecer.py:503` (`metodo_mutante`) e `:512` (`endpoint_da_api`) leem `-X`, `-f` e `-F` só como token próprio ou colado ao valor. O `-i` (`--include`, a única opção curta booleana do `gh api`) agrupado antes deles (`-iX`, `-if`, `-iF`) não é desmontado: o método fica GET e, com a opção antes do endpoint, o valor `PUT`/`POST` vira o endpoint. O gh lê `-iX` como `-i -X`. Sondas na head, rc 0 nos dois hooks: `gh api repos/o/r/pulls/1/merge -iX PUT`, `... -iXPUT`, `gh api repos/o/r/merges -iX POST`, `gh api -H 'Accept: x' -iX PUT repos/o/r/pulls/1/merge`, `gh api -iX POST graphql -F query=@q.graphql`, `gh api -if query=@q.graphql graphql` e `gh api -iF query=@q.graphql graphql` (arquivo com `mergePullRequest`). Com `-X PUT -i` separados, ou `graphql -iF ...` com o endpoint antes, recusa. Ator e ganho: os da rodada 1 (merge que pula a proteção). Correção mínima: antes de `metodo_mutante`, `endpoint_da_api` e `textos_da_api`, desmontar o grupo `-i<letra><resto>` em `-i` e `-<letra><resto>`, com a letra entre `X`, `f`, `F`, `H`, `q`, `t` e `p`, repetindo enquanto o token começar por `-i`; fixture para as sete sondas acima e um mutante que tire a desmontagem. `-pX PUT` não é desvio (o `-p` toma `X` como valor e o gh recusa dois posicionais).

**A1 resolvido.** `hooks/parecer.py:225` compara `Path(toks[0]).name == "gh"`. Sondas na head (`conformidade` | `parecer`): `/usr/bin/gh pr merge 12 --admin`, `./gh ...`, `~/bin/gh ...`, `/usr/bin/gh api -X PUT repos/o/r/pulls/12/merge`, `./gh api -X PUT ...` como `jarvis`, `env /usr/bin/gh ...`, `command /usr/bin/gh ...`, `echo 12 | xargs /usr/bin/gh pr merge --admin`: rc 2 `R-MAIN` no `conformidade` (na base, rc 0 nos dois). `/usr/bin/gh pr merge melhoria/x --squash` como `developer` volta a recusar (`R-CONFORMIDADE` e `R-REVIEW`).

**A2 resolvido.** `hooks/parecer.py:232` pula `-R <v>`, `--repo <v>`, `--repo=<v>`, `-R<v>` (e `-R=<v>`) entre `pr` e o subcomando, e o valor vale como repositório do merge (`:245`). Sondas: `gh pr -R o/r merge 12 --admin`, `--repo=o/r`, `--repo o/r` sem `agent_type`, `-Ro/r`, `-R=o/r`, `gh -R o/r pr -R o/r merge ...`, `--repo=o/r -R o/r` encadeados: rc 2 `R-MAIN`; `gh pr -R o/r merge melhoria/x --squash` como `developer` recusa. O `-R` no fim da linha sem valor não quebra o leitor (fixture `legitimo-pr-r-sem-valor-libera`). `gh pr -R o/r view 12` continua livre.

**A3 resolvido.** `hooks/parecer.py:519` aceita `?` e `#` depois de `graphql`. Sondas: `graphql?x=1` com `-F query=@arq`, `--input arq`, `-f query=` com `enqueuePullRequest` e `mergeBranch`; `https://api.github.com/graphql?a=b`; `graphql#x`; `graphql/?x`; `GRAPHQL`: rc 2 `R-MAIN`. A volta também fecha as formas coladas (`hooks/parecer.py:506-508`): `-Fquery=@arq`, `-fquery=`, `--input=arq`, `--raw-field=query=`, `-fmerge_method=` e `-Fbase=` no REST passam a contar como método mutante e recusam; `--input=-` passa a recusar (`R-CONTRIB`, falha fechada).

**A4 resolvido.** `hooks/conformidade.py:969` recusa, com `R-MAIN` e falha fechada, o comando cujo programa é expansão e cujos argumentos, lidos como `gh` (`hooks/parecer.py:530`), são `pr merge` ou `api`. Sondas: `$(which gh) pr merge 12 --admin`, crase, `$GH`, `"$GH" api -X PUT ...`, `${GH} -R o/r pr merge 12`, `$(echo /usr/bin)/gh ...`, `$GH pr -R o/r merge ...`, `bash -c '$(which gh) pr -R o/r merge 12 --admin'`: rc 2. O recorte segura os legítimos: `$EDITOR src/app.js`, `$(which python3) -c ...`, `$X pr list` e `$X api.md` passam (mutante G23).

**Refatoração `1363cd6`** (`hooks/conformidade.py:1679`, sai `pasta or Path(os.devnull)`): a `pasta` vem sempre de `caminho` (`hooks/conformidade.py:537`), que devolve `Path`; a mesma `pasta` já ia sem alternativa à `graphql_perigoso`. Sondas com `cd /tmp`, `cd /nao/existe` e `cd "$(mktemp -d)"` antes de `gh api graphql -F query=@q.graphql`: rc 2, sem exceção. Sem regressão.

**Controles.** C-1 e C-2: `--admin` recusa em `tech-lead`, `developer`, `jarvis` e sem `agent_type`, por caminho, `-R` e expansão, antes das saídas antecipadas; `conferente` segue recusado (`R-CONFORMIDADE`). C-3: `sh -c`, `bash -c`, `xargs`, `env`, `command`, aspas e `g\h` chegam à mesma recusa. C-4: REST e GraphQL, inline, em arquivo e colados, recusam, menos o grupo com `-i` (A6); GET e `--jq` passam. C-5: os oito legítimos do modelo e os acima mantêm o veredito da base nos dois hooks (comparação uma a uma, 73 sondas, head e base). C-6: nada de rede nem `gh` novo. C-8: os mutantes G1 a G23 de `tests/mutantes/gh-merge-admin.json` e `-2.json` cobrem os quatro do modelo e as dimensões novas. T-1 a T-4: sem condição de papel, base, projeto ou repositório; sem leitura do valor de `--admin=`; sem escape por ambiente ou configuração; as recusas antigas ficam iguais ou mais cedo (só muda a mensagem onde a nova vem antes). T-5: o alias do `gh` segue fora (risco residual, N1, cartão próprio).

Observação sem achado: no hook `parecer` sozinho, `$(which gh) pr merge 12 --admin` e `g\h pr merge 12 --admin` seguem rc 0; a recusa vem do `conformidade`, que roda em toda chamada do Bash, como o C-2 pede.

PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-10), conferida de novo: a volta fecha os casos próximos da AR-8 e da AR-10 (programa por caminho e por expansão); o A6 é classe nova (opção curta agrupada). AR-3, AR-5 e AR-7 não se aplicam ao delta.

## Rodada 1 (histórico, 6c7e573)
Achados da rodada 1, resolvidos na rodada 2: A1 (bloqueante, programa por caminho), A2 (bloqueante, `-R` entre `pr` e o subcomando), A3 (bloqueante, `graphql?`), A4 (bloqueante, programa por expansão); A5 (recomendado, dimensões novas da matriz) segue acima.

### Detalhe dos achados da rodada 1
Ator de todos: o modelo de qualquer papel, por erro ou por instrução injetada, com o token do `gh` que pode ser de administrador (ativo e ator do modelo de ameaças, seção E1). Ganho: um merge que pula checks e review e chega à `develop`, à `homolog` ou à `main`. Severidade comum: alta (desvio total do controle novo e, em A1 e A2, também das recusas antigas de `gh pr merge`).

**A1** (alta, esforço P, dono `forge:tech-lead`). Evidência: `hooks/parecer.py:225` compara `toks[0] == "gh"`; `hooks/conformidade.py:964` já usa o nome base (`prog = Path(...).name`) e chama `self.gh`, mas `parte` vem de `parecer.analisar` (`:968`), que devolve `None`, e `gh_admin` (`hooks/conformidade.py:1667`) e o ramo `api` saem sem decidir. Sondas, head e base iguais (pré-existente, mas derruba o C-1 e o C-4 deste item): `/usr/bin/gh pr merge 12 --admin`, `./gh pr merge 12 --admin`, `/usr/bin/gh api -X PUT repos/dono/repo/pulls/12/merge`, e ainda `/usr/bin/gh pr merge melhoria/x --squash` como `developer` (passa `pr_merge_integracao` e o parecer). Correção mínima: em `analisar`, comparar `Path(toks[0]).name == "gh"` (o mesmo critério do `prog`), o que alcança as duas leituras (`conformidade` e `parecer`) sem parser novo.

**A2** (alta, esforço P, dono `forge:tech-lead`). Evidência: `hooks/parecer.py:230-238` toma `toks.index("pr")` e exige `merge` em `i + 1`. O `gh` 2.102.0 local aceita `gh pr -R dono/repo merge --help` (mostra a ajuda do merge, sem rede). Sondas, head e base: `gh pr -R dono/repo merge 12 --admin`, `gh pr --repo=dono/repo merge 12 --admin`, `gh pr --repo dono/repo merge 12 --admin` sem `agent_type`, e `gh pr -R dono/repo merge melhoria/x --squash` como `developer`, todos rc 0 nos dois hooks. Correção mínima: entre `pr` e o subcomando, pular `-R <valor>`, `--repo <valor>`, `--repo=<valor>` e `-R<valor>` (as opções persistentes do `gh pr`) antes de ler `create`, `ready` e `merge`.

**A3** (média, esforço P, dono `forge:tech-lead`). Evidência: `hooks/parecer.py:510` (`(^|/)graphql/?$`) e o uso em `hooks/conformidade.py:1675`. Com `graphql?x=1` (ou `https://api.github.com/graphql?a=b`), o `gh` trata o caminho como REST e manda os campos como corpo JSON `{"query": ...}` por POST, o formato que o endpoint GraphQL lê. Sondas na head: `gh api -X POST 'graphql?x=1' -F query=@q.graphql` (arquivo com `mergePullRequest`), `gh api 'graphql?x=1' --input q.json`, `gh api 'graphql?x=1' -f query='mutation { enqueuePullRequest(...) }'` e o mesmo com `mergeBranch`: rc 0 nos dois hooks. O inline com `mergePullRequest` cai no `GRAPHQL_PERIGOSO` antigo, e o `--input -` cai no `R-CONTRIB`, então só o texto fora do inline escapa. Correção mínima: o padrão do endpoint aceitar sufixo de consulta ou fragmento, `(^|/)graphql/?([?#]|$)`, com fixture para os três casos.

**A4** (alta, esforço P, dono `forge:tech-lead`). Evidência: `hooks/conformidade.py:964` (`prog` da palavra literal) e `hooks/parecer.py:225`. Sonda, head e base: `$(which gh) pr merge 12 --admin`, rc 0 nos dois hooks. Correção mínima: comando simples cujo programa é expansão (`$(...)`, crase, `$VAR`) e que traz `pr` seguido de `merge`, ou `api`, entre os argumentos é recusado com o marcador do hook (falha fechada, como o `parecer` já faz com o lançador que não lê). Sem esse recorte a recusa geral pega `$EDITOR arq` e outros legítimos.

**A5** (recomendado). As formas acima não estavam na matriz (o modelo traz `env` e `command` antes, que passam a recusar, e `-R` antes de `pr`, que recusa). Pela skill `cyber-security`, achado fora das dimensões vira dimensão: proponho ao dono do modelo acrescentar à linha "Posição" o nome do programa (caminho absoluto, `./`, expansão) e à linha "Alvo" o `-R`/`--repo` entre `pr` e o subcomando.

Verificado e de acordo:
- C-1: `--admin`, `--admin=true`, `--admin=false`, `--admin=1`, depois de `--`, como valor de `-b`: recusa `R-MAIN` em `tech-lead`, `developer`, `jarvis`, sem `agent_type`; o `conferente` já recusava antes (`R-CONFORMIDADE`). `parecer.usa_admin` (`hooks/parecer.py:514`) não lê o valor (T-2 ok).
- C-2: `gh_admin` roda antes do `if not parte: return` e do `return` da branch não resolvida (`hooks/conformidade.py:1688`); número, URL, `cd /tmp`, `-R` antes de `pr`, `GH_REPO=` e pasta inexistente recusam.
- C-3: `sh -c`, `bash -c`, heredoc para `bash`, `eval`, `$(...)`, crase, `env`, `command`, `exec`, `nohup`, `time`, `timeout`, `\gh` e `xargs` recusam pelo leitor existente.
- C-4: REST `pulls/<n>/merge` (com `?`, `#` e `/` finais, `-XPUT`, `--method=PUT`, só campos) e `repos/<o>/<r>/merges`, e GraphQL no endpoint `graphql` inline, em `-F query=@arq`, `--input arq` e `--input -`, recusam; GET e `--jq` passam.
- C-5: os oito legítimos do modelo mantêm o veredito da base nos dois hooks; também `PATCH repos/o/r/pulls/12`, `PUT .../update-branch` e comentário de issue com a palavra `mergePullRequest`.
- C-6: nada de rede nem `gh` novo; `conta_do_gh` não entra no caminho novo.
- C-8: `test_fixtures_do_gh_merge_admin` (`tests/test_hooks.py:2164`) cobre os quatro mutantes do modelo (número, `--admin=false`, fixtures do `conformidade`, GraphQL em arquivo).
- T-1 a T-4: sem condição de papel, base, projeto ou repositório; sem leitura de valor; sem escape por ambiente ou configuração; nenhuma linha das recusas antigas foi removida ou reordenada. Nenhum texto recusado na base passa a ser liberado na head (as sondas da base comparadas uma a uma; só muda a mensagem onde a recusa nova vem antes, como no heredoc para `bash`).
- T-5: o alias do `gh` (`gh alias set`, `gh <alias>`) não é coberto: risco residual, com o N1 de `furo-hook.md` (cartão próprio).

PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-10): conferida item a item. A1 e A4 se aproximam da AR-8 (o leitor de `hooks/parecer.py:224` decide pelo token literal do programa) e da AR-10 (texto recusado executado por outro caminho); A2 e A3 são classe nova. AR-3, AR-5 e AR-7 não se aplicam ao diff (sem trava de ambiente, sem python novo no caminho que decide, sem leitura nova da pasta do git).

## Riscos aceitos e ferramentas
Nenhum risco aceito pelo usuário. Residual: o alias do `gh` (`gh alias set`, `gh <alias>`), com o N1 de `furo-hook.md` (cartão próprio). Ferramentas na rodada 3: `forge-check delta --parecer` sobre este parecer, leitura do delta, 33 sondas locais dos dois hooks na head e na base, como `tech-lead` e `security-engineer` (montador das fixtures da suíte, `$TMPDIR`), sem rede; `python3 -m unittest tests.test_hooks` na head: 71 testes, OK (959 s). `gitleaks`, `semgrep`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o delta não toca segredo, dependência nem workflow).
