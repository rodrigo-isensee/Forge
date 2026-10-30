---
tipo: review
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: cec2b422dccee2c4c9009e5677aac209b351763a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn7-dolar-interrog

Code review (`R-REVIEW`) do H1-1 da P-N7, voltas 4 a 7 (d257466, c0874bd, da92186, cec2b42): pelas decisões do dono de 2026-10-30 (05:14, 06:27 e 07:45), o `$?` vale só entre aspas duplas e, fora de aspas, volta ao comportamento da base 31257c1. Base `develop` 31257c1, head cec2b42. Revalidação por delta do parecer anterior (557d12c, head 9001a89).

## Achados

## Revalidação por delta
- **Delta lido:** `forge-check delta --parecer docs/reviews/pn7-dolar-interrog.md` lista 9001a89..cec2b42 (o mesmo código de 836ee2a..cec2b42, que só soma pareceres): `changelog.d/pn7-dolar-interrog.md`:2, ADR 0011:43 e :104, `docs/hooks.md`:97, `hooks/_comum.py`:1427-1438, 1457-1458, 1498, 1501, 1517, 1556-1559, 1566, 1578-1583, 1593 (a retirada do caminho do `$?` solto), as 6 fixtures `-bloqueia` novas (extglob `@(x)` e `@(zz)`, `>&`, `2>&`, `<&`, `>|`), as 8 fixtures renomeadas (`-libera` com "como na base" e duas que passam a `-bloqueia`), `tests/mutantes/pn7-dolar-interrog.json` (16 mutantes para 4) e `tests/test_hooks.py`:1793-1794, 1955-2004. Li tudo.
- **Já lido (rodadas anteriores, sem mudança):** `hooks/parecer.py` (igual à base), as demais fixtures `pn7-dolar-interrog-*` e o resto da ADR.
- **A1 anterior (extglob antes do `$?`):** resolvido pela causa. Fora de aspas não há mais ramo novo: o `$?` cai no ramo do `$` da base. As fixtures `extglob-antes-do-codigo-bloqueia` e `extglob-zz-antes-do-codigo-bloqueia` dão 2 no head.
- **A2 anterior (`>&`, `2>&`, `<&`, `>|` como separador):** resolvido pela mesma via; as 4 fixtures `redirecao-*-antes-do-codigo-bloqueia` dão 2 no head, e a propriedade `LUGARES` ganhou as 5 formas.
- **Classe dos achados anteriores** (lista plana onde o bash aninha, 3 vezes neste pedido): fechada por retirada do escopo; sem linha AR nesta rodada (decisão técnica de 2026-10-29 15:28, pedido T1-CONF-ESCOPO-REV).

## O que foi conferido
- **Hook fora de aspas igual à base:** `git diff 31257c1 cec2b42 -- hooks/` só toca `hooks/_comum.py` (10+, 4-): o ramo `elif c == "$" and seguinte == "?" and contexto[0] == "duplas"` em `construcao_nao_modelada`, o `.replace("$?", "")` no trecho entre aspas de `simples_da_gramatica` (nas aspas simples não muda nada, porque `$?` não tem caractere de controle) e as docstrings. `codigo_de_saida_vale`, `codigo_de_saida_solto` e `SUBSTITUICAO` não existem mais em `hooks/` nem nos testes. Dentro de `$(…)` entre aspas o contexto é `subst`, então `"$(echo $?)"` segue recusado (sonda: 2 no head e na base).
- **Fixtures, head contra base:** as 45 fixtures `pn7-dolar-interrog-*` do head, rodadas pelo harness (`executar_em_lote`) com os hooks do head: 45 de 45. As mesmas 45 com os hooks da base 31257c1: 39 batem e 6 falham, todas `-libera` com `"rc=$?"` entre aspas (o comportamento novo). As 6 `-libera` com `echo rc=$?` fora de aspas e todas as `-bloqueia` dão o mesmo código na base: confere com a decisão técnica de 2026-10-30 05:45.
- **Sondas próprias (head contra base, harness das fixtures):** iguais à base em `git push origin "$?":main` (2, R-MAIN), `git push "$?" main` (2), `"$$?"` (2), `git push origin x; echo rc=$?` (2), `git commit -m x; echo rc=$?` (0), `gh pr merge 3"$?"` (2) e `gh pr merge feature/x; echo "$?"` (2). Passam a 0 só formas em que o `"$?"` vira dígitos numa palavra que não divide: `IFS=0; git push origin "x$?main"`, `git merge "x$?"`, `git push origin "HEAD:ma$?"`; os literais equivalentes (`git merge x0`, `git push origin HEAD:ma0`) já davam 0, então o veredito acompanha o que o bash roda.
- **Teto de fixtures fora do corpus `bash -n`** (`tests/test_hooks.py`:1794): hoje são 9 (as 7 de antes mais as 2 de extglob, que só se leem depois do `shopt`); o teto 10 mantém a folga de 1 que o 8 tinha, e o comentário diz o motivo.
- **Testes e mutantes:** `python3 -m unittest tests.test_hooks.CodigoDeSaida`: 3 testes, OK. `bin/forge-mutante tests/mutantes/pn7-dolar-interrog.json` (rev cec2b422dcce): D1 a D4 morreram (`hooks/_comum.py`:1457 e :1574), as duas linhas novas de código, cada uma com mutante que afrouxa e que aperta (AR-1 conferido).
- **Textos:** a emenda H1-1 da ADR 0011 (:43 e a linha de Leituras :104), `docs/hooks.md`:97, o fragmento, as docstrings de `construcao_nao_modelada`, `simples_da_gramatica`, `CodigoDeSaida` e `test_codigo_fora_de_aspas_recusa_em_todo_lugar` dizem que fora de aspas o `$?` é recusado com marcador crítico e lido como na base sem ele. O grep por "recusa em todo lugar", "segue recusado", "seguem recusados" e "só o `$?` entre aspas" nos arquivos do diff só acha frases com a condição. Sem limite antigo no texto (AR-9): "16 mutantes", "substituição de comando no texto" e "só como argumento de echo" sumiram.
- **Critério de reversão:** a emenda traz o critério (sonda em que o `"$?"` entre aspas muda o que o bash roda numa ação crítica) e a linha de Leituras de 2026-11-30.
- **Teto M14:** 73 linhas de código e teste (`hooks/_comum.py` 10+4, `tests/test_hooks.py` 58+1), por `git diff --numstat --no-renames 31257c1...cec2b42`; fixtures, spec, fragmento e `.md` fora da conta. Uma classe de comportamento em `hooks/`, com corpus próprio. Dentro do teto (150).
- **Commits e changelog:** d257466 a cec2b42 em Conventional Commits em português, um por volta; fragmento em `changelog.d/`, `CHANGELOG.md` intocado. A emenda afrouxa: o PR espera o rótulo `afrouxa-regra` do dono.
- **Segurança e QA:** gatilho `hooks/`; o parecer do `security-engineer` (E2.1) e o do QA (E3.1) correm em paralelo e não são refeitos aqui.

## Parecer
Aprovado. Fora de aspas o hook voltou ao código da base (o diff de `hooks/` só tem o ramo do `"$?"` entre aspas duplas), o que fecha A1 e A2 de 557d12c pela causa; as fixtures novas e as sondas dão o mesmo veredito da base em tudo que não é `"$?"` entre aspas; textos, propriedade, mutantes (4 de 4 mortos) e teto conformes.
