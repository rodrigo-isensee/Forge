---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 2806ca57ea41a48ea3e5ecaf1bda785b3f8c8dcb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0480-repo-publico-fix (CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E141.3)

Code review do PR #829 no head `2806ca57`, conserto de A1 e A2 de `docs/security/v0480-repo-publico-diag.md` (branch `melhoria/v0480-repo-publico-diag`). Diff: `hooks/conformidade.py` (+44 linhas de código, dentro do teto H1), 23 fixtures `trava-*`, `tests/test_hooks.py` (+7), dois arquivos de mutantes, índice de fixtures e fragmento do changelog.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3392 · `gh repo new` é alias de `gh repo create` (`gh repo create --help`, ALIASES, gh 2.105.0) e o ramo só casa `sub == "create"`: `gh repo new novo --public --source . --push` sai 0. Casar `sub in ("create", "new")` e uma fixture do alias.
- A2 (bloqueante) hooks/conformidade.py:3429 · a opção colada `-Fprivate=false` ou `-fvisibility=public` (o gh aceita; `metodo_mutante` já a lê) não casa `\bprivate` depois de `-F`: PATCH em `repos/<o>/<r>` torna público com saída 0. Separar `-F`/`-f` do valor antes do regex, com fixture.
- A3 (bloqueante) hooks/conformidade.py:3429 · a criação busca `private=true` em qualquer texto: `gh api user/repos -f name=novo -f "description=private: true"` (ou o mesmo no corpo do `--input`) sai 0 e cria público. Ler a chave do campo (`private`/`visibility` como nome do `-F`/`-f` ou chave do JSON), não o texto todo.
- A4 (recomendado) hooks/conformidade.py:3395 · `gh repo create --help` sai 2 (sem `--private`, falha fechado); a ajuda não cria nada. Liberar `--help` sozinho, com fixture.

## Sondas
- S1 · `gh repo new novo --public --source . --push` (projeto descartável, forge:node-backend) · espera: saída 2, R-CONFORMIDADE tornar o repositório público · obtido: saída 0
- S2 · `gh repo new novo --public` · espera: saída 2 · obtido: saída 0
- S3 · `gh api -X PATCH repos/dono/proj -Fprivate=false` · espera: saída 2 · obtido: saída 0 (no base `216413c9` também 0; a forma separada `-F private=false` sai 2 nos dois)
- S4 · `gh api -X PATCH repos/dono/proj -fvisibility=public` · espera: saída 2 · obtido: saída 0
- S5 · `gh api user/repos -f name=novo -f "description=private: true"` · espera: saída 2 (criação sem campo de visibilidade, padrão público) · obtido: saída 0
- S6 · `gh api user/repos --input corpo-desc.json` (corpo `{"name":"x","description":"private: true"}`) · espera: saída 2 · obtido: saída 0
- S7 · `gh api orgs/org/repos -f name=novo -f homepage=https://x/?private=true` · espera: saída 2 · obtido: saída 0

## Parecer
**Reprovado.** O desenho está certo (fail-closed na criação, leitura do `campo=@arq` pela fonte única `textos_do_gh_api`, GraphQL com `PRIVATE`/`INTERNAL` literal) e as formas 3 a 20 do diagnóstico saem como o diagnóstico pede; mas três formas de criar ou tornar público seguem abertas (A1 a A3), todas de segurança com gatilho e provadas por sonda.

- **A1:** o alias `new` deixa toda a A1 do diagnóstico reproduzível com uma palavra trocada. Correção de uma linha em `gh_trava`.
- **A2:** lacuna anterior ao PR (`VISIBILIDADE_PUBLICA` já não via o colado no base), mas é a mesma classe que o PR diz fechar ("criar e editar recusam o público"), e o `api_publica` novo herda o regex. Mesma classe de AR-11 (leitura de opção do `gh api` difere da do `gh`). Do lado da criação o colado falha fechado (`-fname=novo -Fprivate=true` sai 2), o que é falso positivo tolerável; a correção da A2 resolve os dois.
- **A3:** a exigência "criar pede `private=true`" é um `search` no texto de todos os argumentos e arquivos, então o valor de outro campo satisfaz a guarda. Mesma família de AR-15 (guarda sobre texto cru). Sugestão: montar o dicionário `campo → valor` dos `-f`/`-F` (com o `@arq` já lido) e do JSON do `--input`, e decidir pela chave.

**Falsos positivos em comandos legítimos (o foco pedido):** saem 0, como devem: `gh repo create novo --private`, `--private --source . --push`, `--internal`, `--private -d "nao use --public"`, `--private --description=--public`; `gh api -X PATCH repos/dono/proj -f description=nova`; `gh api -X GET user/repos -f visibility=public`; `gh api graphql` de leitura e `updateRepository` só de descrição (com `visibility` no conjunto de seleção); `gh api -X PUT repos/dono/proj/topics`; `gh api user/repos --input` com `"private":true`; `gh api -X POST /user/repos -f name=x -F private=true`. Falsos positivos achados: `gh repo create --help` (A4); `-fname=x -Fprivate=true` (resolvido pela A2); e `-f "description=visibility: public por engano"` em PATCH, que é do regex anterior ao PR (sem achado).

**Limite aceito pelo autor:** PATCH e PUT em `repos/<o>/<r>` com `$` em qualquer argumento falham fechado, inclusive no endpoint (`gh api -X PATCH repos/$OWNER/proj -f description=nova` sai 2). É coerente com `textos_do_gh_api` (A-F27-2) e com R-CONFORMIDADE; o contorno é o valor literal. Aceito.

**Ferramentas (citadas, não refeitas):** `bin/forge-mutante` nos dois arquivos: 16 de 16 mutantes mortos (8 em `tests/mutantes/v0480-repo-publico-fix.json`, 8 em `-2.json`), um por guarda mudada. Teste do item `tests.test_hooks.Hooks.test_fixtures_do_repo_publico`: OK (1 teste, 23 fixtures, os dois lados). CI do PR #829 no head: suíte 3.12 e 3.14 verdes nas partes listadas; `bateria`, `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres. Suíte inteira não rodada (fica no CI).

**Na volta:** cada uma das A1 a A3 ganha fixture `trava-*` com a descrição `CONFORMIDADE-REPO-CREATE-PUBLICO` e mutante declarado na linha mudada; revalido pelo delta do parecer.
