---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 85043cc4008c8d1395412674e3aef71d77c2153e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.303)

Revalidação por delta do head 85043cc4 (volta do lote B, E1.288: lista positiva só sem redefinição do comando como função no U4 e no U3, `$(pwd)` redefinido não vira `$PWD`, `VARIAVEIS_DO_BASH` devolve None, O18 morto; mutantes O99 a O104, O45 e O55 realinhados). Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md`, intervalo `e25f079b..85043cc4`, domínio código e testes: `hooks/conformidade.py` (`na_lista_positiva(corpo, linha)` :495, `VARIAVEIS_DO_BASH` :488 e :562, U3 :1344, troca do `$(pwd)` :1597), `tests/test_hook_destino_opaco.py` (pisos 60 e 73), 20 fixtures `opaco-u4-rev2-*`, `opaco-u4-seg2-*` e `opaco-semresto-u3-mv-target-duas-vezes-bloqueia`, mutantes `tests/mutantes/v047-destino-opaco-16.json` (novo), `-7.json` e `-9.json`, `docs/hooks.md` e `docs/hooks-fixtures.md`.

Verificadores: `tests.test_hook_destino_opaco` no head, 4 testes OK (31 s); `bin/forge-mutante --processos 1` com as specs 16, 7 e 9 no rev 85043cc4: 14 de 14 morreram (O99 a O104, O45, O55 entre eles). Suíte completa: fica com o CI do PR (sem PR aberto ainda).

## Achados

## Sondas

## Parecer
Aprovado no 85043cc4. O A1 deste review (E1.279) fecha: a lista positiva só vale quando a linha não define o comando como função, no U4 (:538) e no U3 (:1344), e o `$(pwd)` só vira `$PWD` sem `pwd` redefinido. Rodei 24 sondas pelo harness do corpus, todas com o código esperado: S1 a S3 do parecer anterior e as variantes `date () {`, `function date {`, `function date() {`, `:(){`, `true`, `false`, `mktemp -d`, `$( date )`, crase, `pwd -P` com resto `/config` e `X=$(date)` recusam; `"$(date +%F).log"`, `"$(mktemp)"`, `"$(pwd)/x"` e `"$HOME/x"` seguem livres; `read`/`$REPLY` e `mapfile`/`${MAPFILE[0]}` recusam pela lista nova. O código segue o desenho do U4 (lista positiva, AR-3) e os mutantes cobrem cada guarda nova com teste de comportamento.

Fora deste review: a segurança reprovou o mesmo head pelo A6 (`docs/security/v047-conformidade-destino-opaco.md`, E1.304), em que o nome do comando é trocado sem definir função (`. ./f.sh`, `source`, `hash -p`, `PATH=./bin`, alias, `GIT_WORK_TREE`). É a porta que este review deixou como residual R1 no parecer anterior; cito e não refaço (R-SEGURANCA). A classe só fecha com os dois pareceres aprovados.
