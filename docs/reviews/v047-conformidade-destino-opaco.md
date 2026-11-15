---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 19df94ed5619ae0bb77dbdf5c9abde7d50f04635
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.323)

Revalidação por delta do head 19df94ed (redesenho do lote B da E1.322: `RESOLUCAO_TROCADA` sai e entra `linha_conhecida`, a lista fechada dos comandos da linha lida pelo `shlex`, com falha fechada). Feita por uma instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md`, intervalo `041c671b..19df94ed`, domínio código e testes: `hooks/conformidade.py` (`COMANDOS_INOFENSIVOS` e afins :497 a :517, `linha_conhecida` :520, `na_lista_positiva`, `valores_do_corpo`, troca do `$(pwd)` :1673), `tests/test_hook_destino_opaco.py` (piso do `opaco-u4` 82 → 131), 49 fixtures `opaco-u4-*` novas (`-g-`, `-q-`, `-r-s1` a `-s9`, `-s-s17` a `-s30`, `-red-*`), mutantes `tests/mutantes/v047-destino-opaco-17.json` a `-19.json`, `docs/hooks.md`, `docs/hooks-fixtures.md`, AR-14 em `docs/engineering/achados-recorrentes.md` e o fragmento do changelog.

Verificadores: `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` rodado no 19df94ed: OK (131 fixtures). A mutação das specs 17 a 19 fica com o PQ do autor; o review não a refaz. A suíte completa fica com o CI do PR (ainda não há PR aberto).

Os achados A1 a A3 do review E1.319 fecham: as sondas S1 a S9 viraram as fixtures `opaco-u4-r-s1` a `-s9`, que recusam, e a inversão para lista fechada segue a sugestão daquele parecer. Falso positivo: `find . -name x > "$(mktemp)"` e `echo a > "$(mktemp)" b` seguem livres (fixtures `-red-*`). Um comando fora da lista na mesma linha (`python3 x.py; echo a > "$(date)"`, também `cd docs && …`) recusa, como o `docs/hooks.md` declara.

## Achados
- A4 (bloqueante) hooks/conformidade.py:547 · `linha_conhecida` não lê os argumentos: o contexto aritmético dentro deles atribui `PATH` sem passar por `ATRIBUICAO` nem por `PADRAO_QUE_ATRIBUI` (`$((x=1,PATH=5))`, `${x:PATH=5}`, `${a[PATH=5]}`); o hook dá rc 0 e o bash grava .git/config (S10 a S12, R-CONFORMIDADE)

## Sondas
- S10 · `echo a $((x=1,PATH=5)) > "$(date)"` (5/date imprime .git/config) · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S11 · `x=abc; echo a ${x:PATH=5} > "$(date)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S12 · `echo a ${a[PATH=5]} > "$(date)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S13 · `echo a $((PATH=5)) > "$(date)"` · espera: hook rc 2 · obtido: hook rc 2, controle: o `shlex` corta o `((` e a atribuição cai na posição de comando

## Parecer
Reprovado no 19df94ed: o redesenho fecha as sondas da E1.319 e da segurança E1.320, mas a classe não fecha. A lista fechada confere só a posição de comando. O bash avalia aritmética em qualquer argumento: em `$((…))`, no deslocamento de `${x:…}` e no índice de vetor `${a[…]}`. A vírgula, o deslocamento e o índice tiram a atribuição da posição em que o hook a procura (S10 a S12). O controle S13 recusa por acaso do `shlex`, não por regra. As sondas rodaram pela máquina do `tests/test_hooks.py` (`executar_em_lote`), com a montagem da fixture `opaco-u4-red-argumento-depois-da-redirecao-libera` mais `5/date`. O efeito foi conferido com `bash --norc -c` numa pasta de teste: as três grafias gravam `.git/config`.

Sugestão (o desenho é do autor e da segurança): manter a falha fechada e fazer a linha deixar de ser conhecida quando qualquer palavra, também argumento, traz contexto aritmético: `$((`, `$[`, `((`, ou `${` com `:` ou `[`, salvo `${x:-v}` e `${x:=v}`, que já são lidos. Cada sonda S10 a S12 vira fixture `-bloqueia`, com um mutante por guarda nova.
