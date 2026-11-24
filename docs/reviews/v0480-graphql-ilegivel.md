---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 433c3782d067b58ac85f481f6bd13c085f9704e7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E168.2 (PR #854, gh api graphql com consulta ilegível recusa)

Primeira rodada. Base 95b09785, head revisado 433c3782 (um commit, E168.1). Diff: 69 linhas de código em `hooks/conformidade.py` (dentro do H1, um comportamento), 15 fixtures novas, 1 fixture alterada, 3 arquivos de mutantes (24 mutantes), índice das fixtures regerado e fragmento de changelog.

## Decisão do dono
A decisão de 24/11, opção (a), manda a trava recusar a alteração no GitHub feita por consulta que ela não lê (GraphQL em variável ou expansão do shell), cartão GRAPHQL-CONSULTA-EM-VARIAVEL. O diff faz isso e só aperta: a recusa nova entra por último no ramo `api` de `gh()` (hooks/conformidade.py:3765), só com `metodo_mutante`, em todo papel e também na sessão do Forge (`trava=TRAVA`). Nenhuma recusa anterior some.

Fixture alterada `trava-gh-leitura-graphql-variavel-libera`: passa de `-F n=$N` para `-F n="$N"`. Segue a decisão: sem aspas, o bash divide o valor e pode trazer outro `-f query=…`, e a consulta deixa de ser legível. A forma sem aspas virou a fixture de recusa `trava-graphql-consulta-valor-nu-bloqueia`. O que a fixture prova (a leitura com valor entre aspas segue livre) continua provado, e a descrição dela segue certa.

## Leitura GraphQL legível segue livre
Conferido pelo próprio hook (harness `Fixture.montar` + `rodar` de tests/test_hooks.py), nos papéis `forge:node-backend` e `forge:tech-lead`, no head 433c3782:
- saem 0: `-f query='query{viewer{login}}'`; `-f query='query($n:Int!){…}' -F n="$N"`, `-F"n=$N"`, `--field "n=$N"`; `-f "variables=$V"`; `-H "X: $H"`; `--jq ".data.$X"`.
- saem 2 (R-CONFORMIDADE, a mensagem nova): `-f query="$Q"`, `-f "query=$Q"`, `-f Query="$Q"`, `-fquery="$Q"`, `--raw-field=query="$Q"`, `-f query=${Q}`, `-f query="$(cat q)"`, `-F n=$N`, `-F "$K=x"`, argumento solto `"$X"`, endpoint `/graphql` e `https://api.github.com/graphql`, `-X "$M"`, e `-X GET -X POST`.
- saem 2 por regra anterior (R-CONTRIB): `-F query=@arquivo`, `--input`, `query=@-` com here-string, endpoint `"$E"`.
- `-X GET` com campos sai 0: o `gh` manda a consulta na URL, sem corpo, e o GraphQL não aceita mutação por GET; fica fora do cartão (alteração), como já era na base.

## Regras de leitura
- Código: `expansao_por_palavra` relê a linha e marca o nível de expansão por palavra; a palavra que a releitura não reproduz cai no nível 2 (`vistas.get(a, 2)`), e a dúvida recusa (falha fechada). Nomes e docstrings dizem o cartão e a decisão.
- Guardas: as 24 condições do diff têm um mutante cada (`tests/mutantes/v0480-graphql-ilegivel{,-2,-3}.json`, até 8 por arquivo), todos apontando para teste de comportamento (`test_fixtures_do_repo_publico`), sem teste que lê a fonte. A cobertura dos mutantes é do autor (`forge-mutante --cobertura --base 95b09785`: rc 0, no PR) e não foi refeita.
- O mínimo do lote subiu de 83 para 98 (tests/test_hooks.py:3073), igual às 15 fixtures novas.
- Commit único, Conventional Commits em português, com o fragmento `changelog.d/v0480-graphql-ilegivel.md` e sem editar o CHANGELOG.

## Verificação
- `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico` no head: OK (1 teste, 30,4 s).
- `scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- Suíte inteira: só no CI do PR (em andamento no head 433c3782; `catraca` e `bateria (pareceres)` esperam os pareceres). Não rerrodada aqui.

## Parecer
Aprovado. Cumpre a decisão do dono (opção a) e só aperta: a consulta ilegível recusa em todo papel, também na sessão do Forge, e a leitura legível e os valores entre aspas de outros campos seguem livres. A fixture alterada segue a decisão.
