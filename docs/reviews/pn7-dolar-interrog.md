---
tipo: review
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 312ecf0d01b9072fa17446c87dd6174c65ac3b6b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn7-dolar-interrog

Code review (`R-REVIEW`) do H1-1 da P-N7: o `$?` passa a ser construção modelada nos hooks `conformidade` e `parecer` (ADR 0011, emenda H1-1). Base `develop` 31257c1, head 312ecf0, quatro commits.

## Achados
- A1 (bloqueante) hooks/_comum.py:1456 · classe guarda textual contornável: o `"IFS" not in linha` não vê `export I"FS"=0`; `export I"FS"=0; git push origin x$?main` dá 0 no conformidade (develop dá 2) e o bash roda `git push origin x main` (R-MAIN); idem em 1578 e parecer.py:109
- A2 (recomendado) tests/test_hooks.py:1964 · a propriedade e a fixture ifs-divide só usam o `IFS=0;` literal; acrescentar as grafias com aspas ou `\` no nome (`export I"FS"=0`, `declare I'FS'=0`, `export I\FS=0`, `printf -v IF\S %s 0`) com 2 esperado

## O que foi conferido
- **Escopo:** `construcao_nao_modelada` e `simples_da_gramatica` (`hooks/_comum.py`) e `heredocs_simples` (`hooks/parecer.py`) aceitam o `$?` entre aspas duplas sempre e fora de aspas só sem `IFS` no texto; todo outro `$`, crase, chaves e `case` seguem recusados. Faz o que o pedido pede, nem mais nem menos; o defeito está na forma da guarda (A1).
- **A1, prova:** a sonda roda o hook com o harness das fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`), copiando a fixture `pn7-dolar-interrog-push-main-echo-rc-bloqueia` e trocando o comando. No head 312ecf0 o `conformidade` dá 0 para `export I"FS"=0; git push origin x$?main`, `declare I'FS'=0; …`, `export I\FS=0; …` e `printf -v IF\S %s 0; …`; na base 31257c1 os quatro dão 2 (`$?` com ação crítica). No bash, `export I"FS"=0; printf '<%s>' x$?main` imprime `<x><main>`: o push leva a `main`. É regressão de controle com gatilho (`R-MAIN`) e requisito do pedido ("sem deixar de barrar nenhum merge, pull, `gh pr` ou `gh api` reais"; aqui, o push da `main`). A guarda compara o texto cru, e o bash atribui o `IFS` depois da remoção de aspas e de `\` no argumento de `export`, `declare`, `typeset`, `local`, `readonly`, `printf -v` e `read`. Sugestão: procurar o `IFS` nas palavras reduzidas (`reduzida`, a mesma de `hooks/_comum.py`) ou recusar o `$?` fora de aspas com qualquer desses comandos na chamada; não provado aqui, mas a corrigir junto: a palavra com glob que o bash expande para `IFS=…` (`export I?S=0` com um arquivo `IFS=0` na pasta). Classe próxima da AR-3 (lista negativa em trava de ambiente); sem linha AR nova nesta rodada (decisão técnica de 2026-10-29 15:28, pedido T1-CONF-ESCOPO-REV).
- **Guarda mais estrita em `heredocs_simples`** (decisão técnica de 2026-10-30 00:36): com `IFS` em qualquer ponto do texto, inclusive no corpo, recusa o `$?` também entre aspas. Equivalência conferida por sonda: `git commit -F - <<'EOF'` com `IFS` e `gh pr merge` no corpo e `echo "rc=$?"` dá 0 nos dois hooks, porque o falso de `heredocs_simples` leva a `fora_da_gramatica_com_heredoc`, que aceita o `"$?"`. Só aperta o caminho rápido; o comportamento visível bate com a emenda e com `docs/hooks.md`.
- **Casos:** as 28 fixtures `pn7-dolar-interrog-*` dão o código esperado (rodadas pelo harness): os 5 casos que passam, nos dois contextos (clone do Forge e projeto) e nos dois hooks, dão 0; os 8 barrados dão 2 (6 no `conformidade`, 2 no `parecer`). `python3 -m unittest tests.test_hooks.CodigoDeSaida`: 2 testes, OK.
- **ADR 0011 e `docs/hooks.md`:** a emenda H1-1 traz motivo, alcance, o que não muda, "Afrouxa; rótulo `afrouxa-regra`" e o critério de reversão (sonda em que o `$?` muda o que o bash roda numa ação crítica), com linha de revisão em 2026-11-30. A sonda do A1 atinge esse critério na forma atual da guarda. `docs/hooks.md` tira o `$` da lista do `heredocs_simples` "além do `$?`" e ganha o item "Código de saída `$?`"; ao corrigir o A1, o texto "só se o texto da chamada não cita `IFS`" acompanha a guarda nova.
- **Teto M14:** 57 linhas de código e teste (`hooks/_comum.py` 12+4, `hooks/parecer.py` 5+3, `tests/test_hooks.py` 33+0, por `git diff --numstat --no-renames`); fixtures, spec de mutantes, fragmento e `.md` ficam fora. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto.
- **Ferramentas (citadas, não refeitas):** a spec `tests/mutantes/pn7-dolar-interrog.json` tem 12 mutantes; o resultado da mutação e o `shellcheck` são do autor e não entram como volta de review. Segurança e QA rodam em paralelo (E2.1 e E3.1): o A1 é de segurança com gatilho e segue como cartão para o `security-engineer`.
- **Commits e changelog:** quatro commits em Conventional Commits em português, um por item; fragmento `changelog.d/pn7-dolar-interrog.md` presente, sem tocar o `CHANGELOG.md`.

## Parecer
Reprovado. A1 (bloqueante): a guarda do `IFS` é textual e o bash atribui o `IFS` depois da remoção de aspas, então `export I"FS"=0; git push origin x$?main` passa no `conformidade` e leva ao push da `main`, que a `develop` barrava. Corrigir a guarda nas três funções (`hooks/_comum.py:1456`, `hooks/_comum.py:1578` e `hooks/parecer.py:109`) e cobrir as grafias do A2 na propriedade e numa fixture `-bloqueia`. O resto (escopo, equivalência do `heredocs_simples`, 5 casos que passam e 8 barrados, emenda e `docs/hooks.md`, teto M14) está conforme.
