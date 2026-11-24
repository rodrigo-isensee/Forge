---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 1265fa11ec5e75d16df8402d32664fd2d683538e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0480-repo-publico-fix (CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E141.8)

Revalidação por delta do PR #829 no head `1265fa11` (volta E141.7), contra o parecer anterior no head `2806ca57`. Delta lido: `forge-check parecer delta docs/reviews/v0480-repo-publico-fix.md` (revalida: sim, o parecer anterior barrou) e `git diff 2806ca57 1265fa11`: `hooks/conformidade.py` +94 −18, 34 fixtures `trava-*`, mutantes em seis arquivos, `tests/test_hooks.py` (mínimo de 22 para 57) e índice de fixtures.

## Achados
- A1 (bloqueante) hooks/conformidade.py:345 · o GRAPHQL_SEM_TEXTO não lê a query como o lexer do GraphQL: no bloco `"""`, `\` só escapa `\"""` (o regex fecha em `\\"""`), e o comentário acaba em CR. Com isso, um `visibility:PUBLIC` escondido e um PRIVATE de isca saem 0; no head 2806ca57 saíam 2 (S1, S2). Regressão do delta.
- A2 (recomendado) hooks/conformidade.py:3496 · o `<var>[visibility]` vale de qualquer campo, também de variável que a query não declara (`-f z[visibility]=PRIVATE`, isca de S2). Contar só a variável usada no `input` da mutação.

## Sondas
- S1 · `gh api graphql -F query=@q1.graphql`, q1 = `mutation{createRepository(input:{name:"x", description:"""z\\""" visibility:PRIVATE """, visibility:PUBLIC # """` + LF + `}){repository{id}}}` · espera: saída 2, cria público · obtido: saída 0 (no 2806ca57: 2)
- S2 · `gh api graphql -F query=@q2.graphql -f z[visibility]=PRIVATE`, q2 = `mutation{createRepository(input:{name:"x" #c` + CR + `visibility:PUBLIC` + LF + `}){repository{id}}}` · espera: saída 2 · obtido: saída 0 (no 2806ca57: 2)

## Parecer
**Reprovado.** Os três bloqueantes do parecer anterior estão fechados no delta, mas a leitura nova do GraphQL abriu uma forma de criar repositório público que o head anterior barrava (A1).

**Bloqueantes anteriores, contra o delta (sondas S1 a S7 do parecer de 2806ca57 rerrodadas no 1265fa11, mesma montagem das fixtures, `forge:node-backend`):**
- **A1 anterior (`gh repo new`):** fechado. `REPO_CRIAR = {"create", "new"}` em `gh_trava`; `gh repo new novo --public --source . --push` e `gh repo new novo --public` saem 2; `gh repo new novo --private --source . --push` sai 0. Fixtures `trava-repo-new-*` nos três lados.
- **A2 anterior (opção colada):** fechado. `CAMPO_COLADO` lê `-Fk=v`, `-F=k=v` e `--field=k=v`; `-Fprivate=false`, `-fvisibility=public`, `--field=private=false`, `-F=private=false`, `--raw-field private=false` e `-XPATCH ... -F visibility=public` saem 2; `-fname=x -Fprivate=true` na criação, o falso positivo anterior, agora sai 0. O valor de outra opção (`-H 'X: -Fprivate=false'`) não vira campo, como deve.
- **A3 anterior (texto em vez de campo):** fechado no REST. `privado_rest` decide pela chave: `description=private: true`, o mesmo no `--input` e `homepage=...?private=true` saem 2; `private=true` com `private=false` repetido, `Private=true`, `private=1`, `private[x]=false`, chave repetida no JSON, corpo em lista ou inválido saem 2 (falha fechada). Com `--input`, o campo `-F private=true` vai à query e não ao corpo, e o hook o recusa: certo.

**Novo bloqueante (A1):** `graphql_publica` troca a busca no texto cru (`GRAPHQL_NAO_PRIVADA`, que barrava S1 e S2) por um léxico próprio que diverge da especificação do GraphQL em dois pontos: no bloco `"""`, a barra só é escape antes de `"""` (então `z\\"""` não fecha a string; o regex fecha), e LineTerminator inclui CR (o `#[^\n]*` engole a linha seguinte). Em S1, o hook vê só `visibility:PRIVATE` (dentro da descrição, para o servidor) e não vê `visibility:PUBLIC`; em S2, não vê o PUBLIC e aceita a isca do A2. Sugestão sem lexer novo: decidir o público no texto da query com strings e comentários (como o head anterior, falso positivo tolerável na descrição com `visibility:`) e usar o texto limpo só para exigir o PRIVATE na criação; ou falhar fechado quando a query de mutação do repositório tem `"""`, CR ou `#`. Fixture de cada forma, com mutante na linha. Não testei contra o servidor (seria criar público, `R-CONFORMIDADE`); a prova é a especificação do GraphQL (BlockStringCharacter e LineTerminator) e a saída do hook.

**A4 anterior (`gh repo create --help`):** concordo que fique fora. Hoje falha fechado (falso positivo sem dano); liberar `--help` pela presença da palavra deixaria `gh repo create x --public -- --help` e afins na mão do parser do gh, o que afrouxa a guarda. Segue recomendado, sem cartão novo.

**Falsos positivos (o foco anterior), no head:** saem 0 `gh repo create novo --private`, `gh api -X POST /user/repos -f name=x -F private=true`, `visibility=internal`, `--input` com `"private":true`, PATCH só de descrição (direto, `@arq` e `--input`), `GET user/repos -f visibility=public`, GraphQL de leitura, `updateRepository` só de descrição e `createRepository` com `visibility:PRIVATE` literal. Novo falso positivo aceito: GraphQL com `visibility:$v` e `-f v=PRIVATE` sai 2 (variável fora de `<var>[visibility]` falha fechado, coerente com o limite do item). `API_SEGMENTO_ESTRANHO` (A6 da segurança) barra `user//repos` no endpoint de repositório e não alcança `repos/o/r/issues//`, que sai 0.

**Teto H1:** `hooks/conformidade.py` soma +94 −18 no delta e 120 linhas de código no item contra a base `216413c9` (`git diff --numstat`), dentro de 150; o resto são fixtures, mutantes e teste.

**Ferramentas (citadas, não refeitas):** a mutação é do autor (46 mutantes declarados em seis arquivos, um por guarda mudada, segundo o commit `1265fa11`); não rerrodei. Teste do item `tests.test_hooks.Hooks.test_fixtures_do_repo_publico`: OK (1 teste, 57 fixtures, os dois lados). CI do PR #829 no head: `instalação`, `bateria (passos)` e `bateria (verificações longas)` verdes; suíte 3.12 e 3.14 pendentes; `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres. Suíte inteira não rodada (fica no CI).

**Na volta:** A1 com fixtures `trava-graphql-*` das duas formas (S1 e S2) e mutante declarado na linha mudada; revalido pelo delta do parecer.
