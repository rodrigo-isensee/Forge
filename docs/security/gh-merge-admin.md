---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 9535b63a7908ae1578f998ef5e1978734aacb82f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: gh-merge-admin (E1 da 0.33)

Base `928e61b66015f7ee2a2e585dc8178e07dc16be39`. Rodada 1 sobre `6c7e573` (reprovado, A1 a A4 bloqueantes, A5 recomendado). Rodada 2 sobre `9535b63` (a volta do autor, 7 commits): revalidação do delta `6c7e573..9535b63` em `hooks/`, `tests/` e `changelog.d/` (`forge-check delta --parecer` sobre este parecer) contra os achados, os controles C-1 a C-8 e as mudanças proibidas T-1 a T-5 de `docs/security/ameacas/versao-033.md` (seção E1).

## Gatilhos
`controles do Forge`: `hooks/conformidade.py` e `hooks/parecer.py` (classificador de comando, `R-MAIN`, `R-CONTRIB`, `R-REVIEW`). Não toca segredo, dependência, workflow nem o pre-push.

## Achados
- A5 (recomendado) tests/test_hooks.py:2164 · as dimensões novas da rodada 1 (programa por caminho, `./` e expansão; `-R`/`--repo` entre `pr` e o subcomando; campo colado; `graphql?`) já têm fixture no lote; falta só a linha na matriz do modelo de ameaças, que é do security-engineer

## Rodada 2
Veredito: **aprovado**. Os quatro bloqueantes estão resolvidos, sem regressão nova; nenhum texto recusado na base passa a ser liberado.

**A1 resolvido.** `hooks/parecer.py:225` compara `Path(toks[0]).name == "gh"`. Sondas na head (`conformidade` | `parecer`): `/usr/bin/gh pr merge 12 --admin`, `./gh ...`, `~/bin/gh ...`, `/usr/bin/gh api -X PUT repos/o/r/pulls/12/merge`, `./gh api -X PUT ...` como `jarvis`, `env /usr/bin/gh ...`, `command /usr/bin/gh ...`, `echo 12 | xargs /usr/bin/gh pr merge --admin`: rc 2 `R-MAIN` no `conformidade` (na base, rc 0 nos dois). `/usr/bin/gh pr merge melhoria/x --squash` como `developer` volta a recusar (`R-CONFORMIDADE` e `R-REVIEW`).

**A2 resolvido.** `hooks/parecer.py:232` pula `-R <v>`, `--repo <v>`, `--repo=<v>`, `-R<v>` (e `-R=<v>`) entre `pr` e o subcomando, e o valor vale como repositório do merge (`:245`). Sondas: `gh pr -R o/r merge 12 --admin`, `--repo=o/r`, `--repo o/r` sem `agent_type`, `-Ro/r`, `-R=o/r`, `gh -R o/r pr -R o/r merge ...`, `--repo=o/r -R o/r` encadeados: rc 2 `R-MAIN`; `gh pr -R o/r merge melhoria/x --squash` como `developer` recusa. O `-R` no fim da linha sem valor não quebra o leitor (fixture `legitimo-pr-r-sem-valor-libera`). `gh pr -R o/r view 12` continua livre.

**A3 resolvido.** `hooks/parecer.py:519` aceita `?` e `#` depois de `graphql`. Sondas: `graphql?x=1` com `-F query=@arq`, `--input arq`, `-f query=` com `enqueuePullRequest` e `mergeBranch`; `https://api.github.com/graphql?a=b`; `graphql#x`; `graphql/?x`; `GRAPHQL`: rc 2 `R-MAIN`. A volta também fecha as formas coladas (`hooks/parecer.py:506-508`): `-Fquery=@arq`, `-fquery=`, `--input=arq`, `--raw-field=query=`, `-fmerge_method=` e `-Fbase=` no REST passam a contar como método mutante e recusam; `--input=-` passa a recusar (`R-CONTRIB`, falha fechada).

**A4 resolvido.** `hooks/conformidade.py:969` recusa, com `R-MAIN` e falha fechada, o comando cujo programa é expansão e cujos argumentos, lidos como `gh` (`hooks/parecer.py:530`), são `pr merge` ou `api`. Sondas: `$(which gh) pr merge 12 --admin`, crase, `$GH`, `"$GH" api -X PUT ...`, `${GH} -R o/r pr merge 12`, `$(echo /usr/bin)/gh ...`, `$GH pr -R o/r merge ...`, `bash -c '$(which gh) pr -R o/r merge 12 --admin'`: rc 2. O recorte segura os legítimos: `$EDITOR src/app.js`, `$(which python3) -c ...`, `$X pr list` e `$X api.md` passam (mutante G23).

**Refatoração `1363cd6`** (`hooks/conformidade.py:1679`, sai `pasta or Path(os.devnull)`): a `pasta` vem sempre de `caminho` (`hooks/conformidade.py:537`), que devolve `Path`; a mesma `pasta` já ia sem alternativa à `graphql_perigoso`. Sondas com `cd /tmp`, `cd /nao/existe` e `cd "$(mktemp -d)"` antes de `gh api graphql -F query=@q.graphql`: rc 2, sem exceção. Sem regressão.

**Controles.** C-1 e C-2: `--admin` recusa em `tech-lead`, `developer`, `jarvis` e sem `agent_type`, por caminho, `-R` e expansão, antes das saídas antecipadas; `conferente` segue recusado (`R-CONFORMIDADE`). C-3: `sh -c`, `bash -c`, `xargs`, `env`, `command`, aspas e `g\h` chegam à mesma recusa. C-4: REST e GraphQL, inline, em arquivo e colados, recusam; GET e `--jq` passam. C-5: os oito legítimos do modelo e os acima mantêm o veredito da base nos dois hooks (comparação uma a uma, 73 sondas, head e base). C-6: nada de rede nem `gh` novo. C-8: os mutantes G1 a G23 de `tests/mutantes/gh-merge-admin.json` e `-2.json` cobrem os quatro do modelo e as dimensões novas. T-1 a T-4: sem condição de papel, base, projeto ou repositório; sem leitura do valor de `--admin=`; sem escape por ambiente ou configuração; as recusas antigas ficam iguais ou mais cedo (só muda a mensagem onde a nova vem antes). T-5: o alias do `gh` segue fora (risco residual, N1, cartão próprio).

Observação sem achado: no hook `parecer` sozinho, `$(which gh) pr merge 12 --admin` e `g\h pr merge 12 --admin` seguem rc 0; a recusa vem do `conformidade`, que roda em toda chamada do Bash, como o C-2 pede.

PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-10), conferida de novo: a volta fecha os casos próximos da AR-8 e da AR-10 (programa por caminho e por expansão). AR-3, AR-5 e AR-7 não se aplicam ao delta.

## Rodada 1 (histórico, 6c7e573)
Achados da rodada 1, todos resolvidos na rodada 2: A1 (bloqueante, programa por caminho), A2 (bloqueante, `-R` entre `pr` e o subcomando), A3 (bloqueante, `graphql?`), A4 (bloqueante, programa por expansão), A5 (recomendado, dimensões novas da matriz; segue acima).

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
Nenhum risco aceito pelo usuário. Residual: o alias do `gh` (`gh alias set`, `gh <alias>`), com o N1 de `furo-hook.md` (cartão próprio). Ferramentas na rodada 2: `forge-check delta --parecer` sobre este parecer, leitura do delta, 73 sondas locais dos dois hooks na head e na base (montador das fixtures da suíte, `$TMPDIR`), sem rede; `python3 -m unittest tests.test_hooks` na head: 71 testes, OK (764 s, máquina com outros pushes; a primeira tentativa parou no limite de 900 s do comando, sem falha). `gitleaks`, `semgrep`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o delta não toca segredo, dependência nem workflow).
