---
tipo: review
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 9001a894b1b08fd016ce3ef4c5539e1bd2c1f1ab
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn7-dolar-interrog

Code review (`R-REVIEW`) do H1-1 da P-N7, volta 3: com `$?` fora de aspas, `construcao_nao_modelada` recusa quando o texto tem `SUBSTITUICAO` (`$(`, `$((`, crase, `<(`, `>(`), e `simples_da_gramatica` recusa com a palavra K3 no resto (decisão técnica de 2026-10-30 02:08). Base `develop` 31257c1, head 9001a89. Revalidação por delta do parecer anterior (73bf7fb, head 3b412fa).

## Achados
- A1 (bloqueante) hooks/_comum.py:1530 · classe lista plana onde o bash aninha (2ª vez): o `(` e o `)` de extglob ficam fora de `SUBSTITUICAO`; `shopt -s extglob nullglob` + `IFS=0; true; git push origin @(x)echo melhoria/x$?main` dá 0 (base 2) e empurra a `main`
- A2 (bloqueante) hooks/_comum.py:1530 · classe operador de redireção lido como separador: o `&` de `>&`/`<&` e o `|` de `>|` abrem comando; `IFS=0; true; git push origin >& echo melhoria/x$?main` dá 0 (base 2) e empurra a `main`; idem `2>&`, `<&`, `>|`

## Revalidação por delta
- **Delta lido:** `forge-check delta --parecer docs/reviews/pn7-dolar-interrog.md` lista 3b412fa..9001a89: `changelog.d/pn7-dolar-interrog.md`:2, ADR 0011:43, `docs/hooks.md`:97, `hooks/_comum.py`:1437-1439, 1456, 1490, 1548-1549, 1592-1593, 1602-1603, 1617, 1623, 1638, as 2 fixtures `-bloqueia` novas (`substituicao-antes-do-codigo`, `aritmetica-antes-do-codigo`), `tests/mutantes/pn7-dolar-interrog.json` (24, 109-110, 144-164) e `tests/test_hooks.py`:1963-1964, 1974-1975, 1986-2000. Li tudo; para os achados reli também o laço de `construcao_nao_modelada` (1460-1546), que o delta não mudou, porque a fronteira do comando sai dele.
- **Já lido (rodada anterior, sem mudança):** as 37 fixtures de 3b412fa, `codigo_de_saida_vale`, `codigo_de_saida_solto`, `hooks/parecer.py` (igual à base) e o resto da ADR.
- **A1 anterior (`$(…)` no meio do comando):** resolvido para as formas da lista. A sonda (harness das fixtures) dá 2 no `conformidade` do head para `IFS=0; git push origin $(true) echo x$?main` e para as variantes da rodada anterior. A retirada do `limites.append(i + 1)` é inócua: com `SUBSTITUICAO` no texto, todo `$?` solto recusa antes de qualquer limite ser lido. O conserto, porém, ataca o sintoma (a lista de formas com `(`) e não a causa (a lista de separadores em 1530); A1 e A2 novos são a mesma causa por outras portas.
- **A2 anterior (propriedade):** resolvido. `LUGARES` ganhou `git push origin $(true) echo {}` e `git push origin $((0)) echo {}`, e o teste novo `test_substituicao_de_comando_recusa_o_codigo_fora_de_aspas` cruza 6 prefixos (`$(…)`, `$((…))`, `<(…)`, `>(…)`, com e sem `IFS=0`) com o `$?` solto (recusa) e entre aspas (passa), mais a K3 em `simples_da_gramatica`.
- **A3 anterior (texto `echo` contra `printf`):** resolvido. A docstring de `simples_da_gramatica` e os dois motivos dizem `echo ou printf`, como `codigo_de_saida_vale`.

## O que foi conferido
- **A1, prova:** harness das fixtures (`Fixture.montar` e `rodar`), a partir de `pn7-dolar-interrog-push-main-echo-rc-bloqueia`, trocando o comando: no head, `shopt -s extglob nullglob`, quebra de linha e `IFS=0; true; git push origin @(x)echo melhoria/x$?main` dá 0 no `conformidade`; na base 31257c1, 2. Na ferramenta Bash (o `eval` lê a segunda linha depois do `shopt`), `printf '<%s>'` com `@(x)echo HEAD$?main` imprime `<git><push><origin><HEAD><main>`; com o `git` real, num clone em `$TMPDIR` com remoto local, o push cria `main` e `melhoria/x` no remoto. Causa: o `)` de `@(x)` é limite em 1530, o hook lê `echo melhoria/x$?main` e o bash apaga a palavra `@(x)echo` (nullglob). Vale também para `?(`, `*(`, `+(` e `!(`. Classe repetida neste pedido (A1 de 73bf7fb); sem linha AR nesta rodada (decisão técnica de 2026-10-29 15:28, pedido T1-CONF-ESCOPO-REV).
- **A2, prova:** a mesma sonda dá 0 no head e 2 na base para `IFS=0; true; git push origin >& echo melhoria/x$?main`, `IFS=0; git push origin 2>& echo melhoria/x$?main`, `IFS=0; git push origin <& echo melhoria/x$?main` e `IFS=0; git push origin >| echo melhoria/x$?main`. No clone de `$TMPDIR`, `bash -c` com a primeira forma grava o arquivo `echo` e o push cria `main` no remoto. Sem `shopt` nem substituição: a forma mais curta. Causa: o `&` e o `|` entram em `limites` (1530) mesmo quando fazem parte de `>&`, `<&` ou `>|`, e `codigo_de_saida_solto` só procura `<`/`>` dentro do trecho, que começa depois do `&`. Já estava em 3b412fa e não o vi na rodada anterior. Classe nova.
- **Sugestão para A1 e A2 (uma correção só):** com `$?` solto, recusar se houver `(` ou `)` fora de aspas no texto (cobre `SUBSTITUICAO` sem a crase, extglob, subshell e aritmética) e contar `&`/`|` como fim de comando só quando não vêm logo depois de `<` ou `>`; acrescentar a `LUGARES` `@(x)echo {}`, `>& echo {}` e `>| echo {}`, e uma fixture `-bloqueia` por classe. Segurança com gatilho: segue como cartão para o `security-engineer`, que revalida em paralelo (E2.1).
- **`simples_da_gramatica` com K3 (desvio declarado):** só recusa a mais, e o teste afirma os três casos (K3 com `"rc=$?"` aceita, K3 com `rc=$?` recusa, sem K3 aceita). A gramática não tem `(`, `>&` nem `>|` (alfabeto do item 1), então os achados não a alcançam.
- **Os 5 casos que precisam passar e o aperto:** as 39 fixtures `pn7-dolar-interrog-*` dão o código esperado pelo harness (39 de 39). `python3 -m unittest tests.test_hooks.CodigoDeSaida`: 3 testes, OK.
- **Mutantes:** a spec fica em 16 (`D3` e `D13` saem; `D17` e `D19` entram), no limite de 16 por spec; a mutação é do autor e fica citada, não refeita.
- **ADR 0011, `docs/hooks.md` e fragmento:** a emenda H1-1 diz que o `$?` solto só vale sem substituição de comando no texto, com o motivo e a sonda de 3b412fa; `docs/hooks.md`:97 e o fragmento acompanham. A correção de A1 e A2 deve ajustar esse texto (parêntese fora de aspas e o `>&`).
- **Teto M14:** 118 linhas de código e teste (`hooks/_comum.py` 57+6, `tests/test_hooks.py` 55+0), por `git diff --numstat --no-renames 31257c1...9001a89`. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto (150).
- **Commits e changelog:** 75cea9e e 9001a89 em Conventional Commits em português; fragmento atualizado, `CHANGELOG.md` intocado.

## Parecer
Reprovado. A1 e A2 (bloqueantes, mesma linha 1530): a lista plana de limites aceita como início de comando o `)` de extglob e o `&`/`|` de `>&`, `<&` e `>|`, e nas duas formas o `$?` esconde o push da `main` que a base barrava, provado com push real num remoto local. A1, A2 e A3 anteriores resolvidos; delta, K3, fixtures, mutantes, emenda e teto conformes.
