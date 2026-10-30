---
tipo: review
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 3b412fa65d473b33ddd8bc61504db97046cdf510
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn7-dolar-interrog

Code review (`R-REVIEW`) do H1-1 da P-N7, volta 2: fora de aspas, o `$?` só vale como argumento de `echo` ou de `printf` (decisão técnica de 2026-10-30 01:04), por posição, em `codigo_de_saida_vale` e `codigo_de_saida_solto` (`hooks/_comum.py`); a guarda textual do `IFS` saiu e `heredocs_simples` voltou à regra da base. Base `develop` 31257c1, head 3b412fa. Revalidação por delta do parecer anterior (head 312ecf0).

## Achados
- A1 (bloqueante) hooks/_comum.py:1488 · classe lista plana onde o bash aninha: o `(` e o `)` de `$(…)` contam como fim de comando; `IFS=0; git push origin $(true) echo x$?main` dá 0 no conformidade (base dá 2) e o bash roda `git push origin echo x main` (R-MAIN); idem 1529
- A2 (recomendado) tests/test_hooks.py:1961 · a propriedade não tem `$(…)` antes do `$?` no mesmo comando; acrescentar a `LUGARES` `git push origin $(true) echo {}` (recusa) e a variante com `$((0))`
- A3 (recomendado) hooks/_comum.py:1588 · a docstring de `simples_da_gramatica` e o motivo `$? fora de echo` (1618, 1633) dizem só `echo`, mas `codigo_de_saida_vale` aceita também o `printf` depois do formato; alinhar o texto ao código

## Revalidação por delta
- **Delta lido:** `forge-check delta --parecer` sobre o parecer anterior lista o intervalo 312ecf0..3b412fa: `changelog.d/pn7-dolar-interrog.md`:2, ADR 0011:43, `docs/hooks.md`:96-97, `hooks/_comum.py`:1428-1633 (as duas funções novas e os trechos de `construcao_nao_modelada` e `simples_da_gramatica`), `hooks/parecer.py`:98-108, as 9 fixtures `-bloqueia` novas, `tests/mutantes/pn7-dolar-interrog.json` e `tests/test_hooks.py` (classe `CodigoDeSaida`). Li o delta inteiro de c6eb028..3b412fa.
- **Já lido (rodada anterior, sem mudança):** as 20 fixtures `-libera` e as 8 `-bloqueia` de 312ecf0 e o resto da ADR.
- **A1 anterior (guarda textual do `IFS`):** resolvido. O `"IFS" not in` saiu das três funções e a regra decide pela posição do `$?`; as quatro grafias da sonda anterior (`export I"FS"=0`, `declare I'FS'=0`, `export I\FS=0`, `printf -v IF\S %s 0`, cada uma com `git push origin x$?main`) dão 2 no head. O A1 novo é outro defeito: a fronteira do comando simples, não o `IFS`.
- **A2 anterior (grafias na propriedade):** resolvido. `CodigoDeSaida.IFS` traz 9 formas (literal, aspas, barra, `printf -v`, `read`, `source`, `$(…)`) cruzadas com 12 lugares; as fixtures `ifs-com-aspas-no-nome`, `ifs-com-barra-no-printf-v`, `ifs-por-read`, `ifs-por-source`, `ifs-por-substituicao` e `ifs-divide-o-codigo` cobrem o caso no hook inteiro.

## O que foi conferido
- **A1, prova:** sonda com o harness das fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`), a partir de `pn7-dolar-interrog-push-main-echo-rc-bloqueia`, trocando o comando. No head 3b412fa o `conformidade` dá 0 para `IFS=0; git push origin $(true) echo x$?main`, `export I"FS"=0; git push origin $(true) echo x$?main`, `IFS=1; git push origin $(false) echo x$?main` e `git push origin $((0)) echo x$?main`; na base 31257c1 os três primeiros dão 2 (`$?` com ação crítica). No bash, `IFS=0; printf '<%s>' git push origin $(true) echo x$?main` imprime `<git><push><origin><echo><x><main>`: o push leva a `main`. Causa: `limites` é uma lista plana; `$(` grava o `(` (linha 1488) e o `)` que fecha a substituição grava outro limite (linha 1529), então o `$?` depois de `$(…)` tem como início do comando o `)`, e o trecho lido é ` echo x$?main`, que `codigo_de_saida_vale` aceita. Contraria a decisão de 01:04 e a emenda H1-1 (o `$?` nunca no comando com o marcador crítico) e atinge o critério de reversão da própria emenda. Sugestão: pilha de inícios de comando junto da pilha de contextos; ao fechar a substituição, voltar ao início do comando de fora, e o fim do comando de fora pula o intervalo `$(…)`. O mesmo defeito explica o aperto declarado `echo "$(cmd)" rc=$?`; com a pilha, ele volta a passar. Classe nova (lista plana onde o bash aninha), sem linha AR nesta rodada (decisão técnica de 2026-10-29 15:28, pedido T1-CONF-ESCOPO-REV). É segurança com gatilho e segue como cartão para o `security-engineer`, que revalida em paralelo.
- **Fora do escopo, pré-existente:** `git push origin $(echo x main)` dá 0 também na base (sem `$?`); não é regressão deste PR e fica como cartão de segurança, na linha "Não promete" da ADR 0011 (palavra com `$(…)`).
- **Regra por posição contra a decisão de 01:04 (onde aceita menos):** a decisão vale `echo` e `printf` sem `-v`; o código recusa também o `printf` com qualquer opção (`printf -- '%s\n' $?`), o `$?` fora de aspas no formato do `printf`, o `echo` ou `printf` com redireção (`echo rc=$? >&2`) ou com `|` para o seguinte, o `echo` depois de palavra reservada (`if true; then echo $?; fi`) ou de atribuição e, pelo defeito do A1, o `echo` com `$(…)` antes do `$?`. Só aperta; a redireção e o pipe estão no objetivo do brief, o resto é escolha do autor descrita na ADR e em `docs/hooks.md`. `echo -n $?`, `printf '%s\n' $?`, `|| echo falhou $?` e `&& echo $?` dão 0, por sonda.
- **Aperto declarado e os 5 casos que precisam passar:** `x=$?` e `echo "$(git status)" rc=$?` dão 2 com o push na chamada, por sonda. As 20 fixtures `-libera` (5 casos, clone do Forge e projeto, nos dois hooks) dão 0 e as 17 `-bloqueia` dão 2: 37 fixtures `pn7-dolar-interrog-*`, todas com o código esperado pelo harness. `python3 -m unittest tests.test_hooks.CodigoDeSaida`: 2 testes, OK.
- **`heredocs_simples`:** voltou à regra da base (nenhum `$` na linha de comando); a propriedade afirma `False` em todas as combinações e o `"$?"` entre aspas segue aceito por `fora_da_gramatica_com_heredoc` (equivalência da decisão de 01:45; sonda com `IFS` no corpo e `echo "rc=$?"` dá 0 nos dois hooks).
- **ADR 0011 e `docs/hooks.md`:** a emenda H1-1 troca a guarda por texto pela regra de posição, com o "Critério mudou" e o motivo; `docs/hooks.md`:97 e o fragmento acompanham. A correção do A1 não muda esse texto.
- **Teto M14:** 96 linhas de código e teste (`hooks/_comum.py` 52+6, `tests/test_hooks.py` 38+0; `hooks/parecer.py` volta à base), por `git diff --numstat --no-renames`. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.
- **Ferramentas (citadas, não refeitas):** a spec `tests/mutantes/pn7-dolar-interrog.json` foi refeita para as guardas novas; mutação e `shellcheck` são do autor. Segurança e QA rodam em paralelo (E2.1 e E3.1).
- **Commits e changelog:** 3b412fa em Conventional Commits em português; fragmento atualizado, `CHANGELOG.md` intocado.

## Parecer
Reprovado. A1 (bloqueante): o `$(…)` no meio do comando faz o hook ler só o pedaço depois do `)`, então `IFS=0; git push origin $(true) echo x$?main` passa no `conformidade` e leva ao push da `main`, que a base barrava. Corrigir a fronteira do comando em `construcao_nao_modelada` (`hooks/_comum.py:1488` e `:1529`) e cobrir com o A2 na propriedade e numa fixture `-bloqueia`. A1 e A2 anteriores resolvidos; o resto (5 casos que passam, aperto declarado, emenda, `docs/hooks.md`, teto M14) está conforme.
