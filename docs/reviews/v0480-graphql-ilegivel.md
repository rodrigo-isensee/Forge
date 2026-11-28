---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 5b04ce1ee7b0c85e591ea6ffb88816983e618dc3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E168.14 (PR #854, 3ª volta E168.13, por delta)

Quarta rodada, por delta. `forge-check parecer delta` lido: intervalo 933539c5..5b04ce1e, sem o que veio da `develop` (merge 82a27ed3 de f82c7cc5); no domínio `hooks/parecer.py`, `hooks/conformidade.py`, 10 fixtures novas (7 no `conformidade`, 3 no `parecer`), `tests/test_hooks.py`, os mutantes `-6` (GQ28 e GQ29 reapontados) e `-9` (GQ49 a GQ55), o índice `docs/hooks-fixtures.md` e o fragmento do changelog. As rodadas anteriores ficam no git como estavam.

## O que a volta faz
- A7 da segurança: `gh_incerto` passa a tratar como leitura incerta a chave com `,` ou `..` antes do subcomando, no subcomando e no endpoint do `gh api` (`chave_incerta`), e quem já chamava `gh_incerto` (`Guarda.gh`, `rotulo`, `analise_do_comando`) recusa com `GH_INCERTO`, sem escolher leitura.
- Os marcadores do gh (`{owner}`, `{repo}`, `{branch}`) saem antes do teste. Tirar o marcador não tira vírgula nem `..`, então não esconde uma chave real (`{owner,graphql}` não casa o marcador; `{{owner},graphql}` fica `{,graphql}` e recusa).
- `CHAVES` fica só no `parecer`, e o `conformidade` a importa. Assim as duas leituras usam a mesma regra.

## Regras de leitura
- Tamanho: 25 linhas mudadas nos hooks (23 no `parecer`, 2 no `conformidade`), dentro do H1; um comportamento só (a chave nessas posições recusa).
- Mutantes: uma guarda nova ou mudada por mutante, GQ49 a GQ55, apontados para `test_gh_incerto_chave` e `test_fixtures_do_repo_publico` (testes de comportamento, nenhum lê a fonte). GQ28 e GQ29 foram reapontados para as linhas novas, e GQ28 segue matando `expande` e `api`/`pr` pelo `test_gh_incerto`. O caso `compare/a...b` com `{owner}` mata o GQ53 (sem tirar o marcador, o `..` casaria). A cobertura é do autor e não foi refeita.
- Leitura conservadora: como a palavra chega sem as aspas, uma chave entre aspas nessas posições também recusa. Isso vale a decisão do dono (opção a, recusa na dúvida) e não alcança o uso legítimo das fixtures (`-H 'Accept: {a,b}'` e a consulta literal ficam fora dessas posições).
- Commit: 5b04ce1e segue Conventional Commits em português. O fragmento do changelog descreve o comportamento novo e os marcadores livres.

## Verificação
- Testes dos arquivos tocados, no head 5b04ce1e: `python3 -m unittest` de `test_gh_incerto_chave`, `test_gh_incerto`, `test_fixtures_do_repo_publico` (que inclui as 10 fixtures novas), `test_ordem_do_gh` e `test_expansao_por_palavra_chaves`: OK (5 testes, 30,1 s).
- Sondas pelos hooks reais (`rodar_dados` de `tests/test_hooks.py`, projeto descartável na `feature/x`), no hook `conformidade`, como `forge:tech-lead` e na sessão principal. Procurei a chave no valor de uma opção entre `api` e o endpoint, posição que `gh_incerto` não olha. Todas saem 2, pela recusa que já existia, e o A6 (S13 da segurança) também fecha agora. As legítimas seguem 0.
- CI do head 5b04ce1e (run 45435519901, ainda em andamento): as partes 1 a 5 do 3.12 e as 1, 2, 4 e 5 do 3.14 passam. A parte 3/5 do 3.14 cai porque o processo 2 foi morto pelo sinal 9 (1349 de 1681 testes rodados), uma falha de infraestrutura, já que a mesma parte passa no 3.12. Ela pede um rerun com esse motivo. `bateria (pareceres)` e `catraca` continuam sendo do fechamento (pareceres da rodada e rótulo `afrouxa-regra` do dono), não do código.

## Sondas
- S1 · `gh api -X {POST,graphql} -f query="$Q"` · espera: 2 · obtido: 2 R-CONFORMIDADE nos dois papéis
- S2 · `gh api -H {x:,graphql} -f query="$Q"` · espera: 2 · obtido: 2 nos dois papéis
- S3 · `gh api --method {POST,graphql} -f query="$Q"` · espera: 2 · obtido: 2 nos dois papéis
- S4 · `gh api -X {PUT,repos/o/r/pulls/1/merge}` · espera: 2 · obtido: 2 nos dois papéis
- S5 · `gh api {'repos/o/r/pulls/1/merg','-Hx:'}e -X PUT` (S13 da segurança, A6) · espera: 2 · obtido: 2 nos dois papéis
- S6 · `gh api repos/{owner}/{repo}/pulls` · espera: 0 · obtido: 0 nos dois papéis
- S7 · `gh api graphql -f query='query{viewer{login,name}}'` · espera: 0 · obtido: 0 nos dois papéis

## Parecer
Aprovado. O A7 fecha: a chave antes do subcomando, nele e no endpoint recusa nos dois hooks, sem escolher leitura, e os marcadores do gh seguem livres. O A6 também fecha por esse caminho (S5). No CI, o que falta é o rerun da parte 3/5 do 3.14 (sinal 9, infraestrutura) e os portões do fechamento. Nada disso é do código.
