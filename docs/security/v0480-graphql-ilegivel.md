---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 5b04ce1ee7b0c85e591ea6ffb88816983e618dc3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança, 3ª volta: v0480-graphql-ilegivel (PR #854, v0478 E168.16)

Delta lido (`forge-check parecer delta`, `933539c5..5b04ce1e`, sem o que veio da develop): `hooks/parecer.py` (`CHAVES` e `MARCADOR_DO_GH` :395, `chave_incerta` :399, `gh_incerto` :420 com o subcomando e o endpoint do `gh api` :429), `hooks/conformidade.py` (`CHAVES` :344 passa a ser `parecer.CHAVES`, fonte única), as 10 fixtures novas e `tests/test_hooks.py` (`test_gh_incerto_chave`, o mínimo de 133 do lote). Fora do domínio: o fragmento do changelog, `docs/hooks-fixtures.md` e os dois mutantes. A rodada anterior fica no git e não foi relida.

Método: os hooks `conformidade` e `parecer` rodados pela montagem de `tests/test_hooks.py` (`Fixture.montar`, `rodar` com o vigia de produção), na branch `feature/x`, com a sessão principal e os papéis `forge:tech-lead` e `forge:devops-engineer`. A base `933539c5` foi extraída por `git archive` e rodada do mesmo jeito. As sondas ficam em arquivo; a opção proibida pelo dono é montada por partes dentro dele e aparece aqui como `<OP>`; o bash só as expandiu com `printf`.

**Achados anteriores:** A7 fechado: S14 a S18 saem 2 R-CONFORMIDADE (`GH_INCERTO`) no `conformidade` e no `parecer`, nos três papéis (base 0). A6 fechado pela mesma correção: S13 (`gh api {'repos/o/r/pulls/1/merg','-Hx:'}e -X PUT`) sai 2 em todo hook e papel (base 0); o cartão C2 da volta anterior cai.

**Só aperta ou neutro: sim.** `gh_incerto` só ganha um `or` (recusa a mais, nunca libera); `CHAVES` do conformidade é a mesma expressão, agora importada. Nenhuma sonda sai menor no head do que na base. As legítimas seguem 0 no head e na base, em todo hook e papel: `gh api graphql -f query='query{viewer{login,name}}'`, `gh api 'repos/{owner}/{repo}/issues?labels=a,b'`, `gh api repos/{owner}/{repo}/compare/a...b`, `gh -R o/r pr view 1`, `gh pr view 1 -R o/r`, `-H 'Accept: {a,b}'` com consulta literal, `--jq '.[] | {n: .number}'`, `gh --version` e `gh issue list --search '{a,b}'`. A chave entre aspas no endpoint ou antes do subcomando (`gh api 'search/issues?q={a,b}'`) passa a recusar: falso positivo aceito pela opção a do dono (na dúvida, recusa), com o conserto no texto do bloqueio.

**As três formas fora do A7** (vistas pelo autor), head e base iguais, logo não são regressão deste item:
- chave no valor de opção antes do endpoint (`gh api -H {x:y,graphql} -f query="$Q"`, `gh api -X {POST,graphql} …`, `gh api -H {x:y,repos/o/r/pulls/1/merge} -X PUT`): o bash põe `graphql` ou o caminho do merge no lugar do endpoint. `conformidade` 2 nos três papéis (head e base); `parecer` 0 (head e base).
- chave no subcomando do `pr` (`gh pr {merge,1} <OP>`, `gh pr {merge,1,<OP>}`, `gh pr {merge,develop}`): `conformidade` 2 ("`chaves` com ação crítica"); `parecer` 0 (head e base).
- chave escondendo a opção (`gh pr merge 1 {<OP>,--squash}`, `gh api repos/o/r/pulls/1/merge -X PUT {-Hx:y,<OP>}`): `conformidade` 2 e `parecer` 2 (R-CONTRIB/R-MAIN, por outro motivo, não pela opção), head e base.
Sem caminho de ataque hoje: o `conformidade` roda em toda chamada e recusa as três. O que fica é a defesa em profundidade do `parecer` (`usa_admin` :1021 compara a palavra inteira; `endpoint_da_api` :1010 e o subcomando do `pr` :480 não olham chave). Viram cartões (C1 e C2), sem achado.

Testes rodados: `test_gh_incerto_chave`, `test_gh_incerto` e `test_fixtures_do_repo_publico` (o lote de 133, com as 10 fixtures novas) passam. A suíte inteira é do CI: no run 45435519901 sobre `5b04ce1e`, as partes 1 a 5 da versão 3.12 e 1, 2, 4 e 5 da 3.14 passam; a parte 3/5 do 3.14 caiu por processo morto pelo sinal 9 (a mesma parte passa no 3.12), e a bateria dos pareceres espera os pareceres desta volta.

Gatilhos: controle de acesso do agente (hooks de conformidade e de parecer), ação irreversível no GitHub (merge que desvia a proteção da branch).

## Achados

## Sondas

## Detalhe dos achados
Sem achado nesta volta. Sondas executadas (todas em arquivo, `obtido` no head; base entre parênteses):
- S13 a S18 (as da volta anterior): 2 em todo hook e papel (base 0).
- F1a `gh api -H {x:y,graphql} -f query="$Q"`, F1b `gh api -X {POST,graphql} -f query="$Q"`, F1c a mesma com a mutação literal, F1d `gh api -H {x:y,repos/o/r/pulls/1/merge} -X PUT`: conformidade 2, parecer 0 (base igual).
- F2a `gh pr {merge,1} <OP>`, F2b `gh pr {merge,1,<OP>}`, F2c `gh pr {merge,develop}`: conformidade 2, parecer 0 (base igual).
- F3a `gh pr merge 1 {<OP>,--squash}`, F3c `gh api repos/o/r/pulls/1/merge -X PUT {-Hx:y,<OP>}`: 2 nos dois hooks (base igual).

## Plano em cartões
- C1 (tech-lead), baixa, esforço P: no `parecer`, a chave em qualquer palavra do `gh api` até o endpoint inclusive, contando os valores de opção (`-H`, `-X`, `-f`…), e no subcomando do `gh pr` é leitura incerta (`chave_incerta` em `gh_incerto`, `hooks/parecer.py:420`). Fixtures: F1a, F1b, F1d, F2a, F2b e F2c, que hoje só o `conformidade` recusa.
- C2 (tech-lead), baixa, esforço P: `usa_admin` (`hooks/parecer.py:1021`) recusa também a palavra com chave que contém a opção proibida (F3a, F3c), sem depender do motivo lateral (PR por número, R-MAIN).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: os hooks rodados localmente com a montagem do teste, a base extraída por `git archive` e o bash só com `printf`. gitleaks, semgrep e zizmor não se aplicam a este delta.
