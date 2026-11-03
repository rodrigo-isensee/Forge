---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 6c7e5731a7138e9eaf11e4c216726318091dfd57
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: gh-merge-admin (E1 da 0.33)

Base `928e61b66015f7ee2a2e585dc8178e07dc16be39`, head `6c7e573` (1 commit). Primeira rodada: leitura do diff (`hooks/conformidade.py`, `hooks/parecer.py`, `tests/test_hooks.py`, 43 fixtures, fragmento do changelog) e sondas dos dois hooks (`conformidade` e `parecer`) na head e na base, com o montador das fixtures da suíte, contra a matriz, os controles C-1 a C-8 e as mudanças proibidas T-1 a T-5 de `docs/security/ameacas/versao-033.md` (seção E1). Família inteira varrida numa passada; todos os achados vão juntos.

## Gatilhos
`controles do Forge`: `hooks/conformidade.py` e `hooks/parecer.py` (classificador de comando, `R-MAIN`, `R-CONTRIB`, `R-REVIEW`). Não toca segredo, dependência, workflow nem o pre-push.

## Achados
- A1 (bloqueante) hooks/parecer.py:225 · `analisar` só reconhece o programa escrito `gh`: `/usr/bin/gh pr merge 12 --admin`, `./gh pr merge 12 --admin` e `/usr/bin/gh api -X PUT repos/o/r/pulls/12/merge` passam nos dois hooks (rc 0), contra C-1, C-2 e C-4; classe: segurança com gatilho
- A2 (bloqueante) hooks/parecer.py:238 · `gh pr -R o/r merge 12 --admin` e `gh pr --repo=o/r merge 12 --admin` passam nos dois hooks (rc 0, qualquer papel); o gh aceita `-R` entre `pr` e `merge` e o leitor só olha o token logo após `pr`; contra C-1 e C-2; classe: segurança com gatilho
- A3 (bloqueante) hooks/parecer.py:510 · `ENDPOINT_GRAPHQL` exige o fim no `graphql`: `gh api 'graphql?x=1' -F query=@q` (mergePullRequest no arquivo), `--input q.json` e `-f query=` com `enqueuePullRequest` ou `mergeBranch` passam (rc 0); contra C-4; classe: requisito
- A4 (bloqueante) hooks/conformidade.py:964 · programa por expansão: `$(which gh) pr merge 12 --admin` passa nos dois hooks (rc 0); o nome do programa sai da palavra não expandida e o leitor não falha fechado; contra C-1 e C-3; classe: segurança com gatilho
- A5 (recomendado) hooks/conformidade.py:1667 · os achados A1, A2 e A4 viram dimensões novas da matriz (nome do programa: caminho, `./`, expansão; `-R`/`--repo` entre `pr` e o subcomando), com fixture para cada uma no lote `test_fixtures_do_gh_merge_admin`

## Detalhe dos achados
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
Nenhum risco aceito pelo usuário. Residual: o alias do `gh` (N1, cartão próprio). Ferramentas: leitura do diff, sondas locais dos hooks (montador das fixtures, `$TMPDIR`), `gh pr -R ... merge --help` local, sem rede; `python3 -m unittest tests.test_hooks` na head: 71 testes, 1 falha de tempo no `vigia` (`test_varredura_do_vigia_nao_desce_em_pastas_ignoradas`, 1,41 s contra 1,0 s, máquina carregada), que passa sozinho (0,6 s) e não é tocado pelo diff. `gitleaks`, `semgrep`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o diff não toca segredo, dependência nem workflow).
