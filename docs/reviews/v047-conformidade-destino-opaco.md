---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 041c671bbcca2cb1fdee5b9d65304151bbf649a5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.319)

Revalidação por delta do head 041c671b (volta da A6 da segurança E1.304, lote B: `RESOLUCAO_TROCADA` tira a lista positiva e a troca `$(pwd)` → `$PWD` quando a linha troca a resolução do comando). Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md`, intervalo `85043cc4..041c671b`, domínio código e testes: `hooks/conformidade.py` (`RESOLUCAO_TROCADA` :496, `na_lista_positiva` :505, troca do `$(pwd)` :1606), `tests/test_hook_destino_opaco.py` (piso do `opaco-u4` 73 → 82), 9 fixtures `opaco-u4-seg3-*`, mutantes `tests/mutantes/v047-destino-opaco-17.json` (novo, O105 a O108) e `-16.json` (O100 realinhado), `docs/hooks.md` e `docs/hooks-fixtures.md`.

Verificadores: `bin/forge-mutante --processos 1 --rev 041c671b` com a spec 17: 4 de 4 morreram (O105 :505, O106 :1606, O107 :496, O108 :497). Os mutantes cobrem as guardas declaradas, mas não as formas das sondas abaixo. Suíte completa: fica com o CI do PR (sem PR aberto ainda).

## Achados
- A1 (bloqueante) hooks/conformidade.py:496 · `RESOLUCAO_TROCADA` casa o texto cru da linha: aspas, barra invertida, aspas vazias e indireção escapam (`"." f.sh`, `\source f.sh`, `so''urce f.sh`, `s=source; $s f.sh`, `export PA''TH=./bin:$PATH`); hook rc 0 e o bash grava .git/config (S1 a S6, R-CONFORMIDADE)
- A2 (bloqueante) hooks/conformidade.py:555 · A via `echo`/`printf %s` do U4 não consulta `RESOLUCAO_TROCADA`: `source g.sh` que define `echo` ou `printf` faz `tee "$(echo docs)"` e `tee "$(printf %s docs)"` gravarem .git/config com hook rc 0 (S7, S8, R-CONFORMIDADE)
- A3 (bloqueante) hooks/conformidade.py:496 · A lista fechada não cobre a saída trocada sem trocar o nome: `set -T; trap 'echo .git/config' DEBUG; echo a | tee "$(true)"` grava .git/config com hook rc 0 (S9, R-CONFORMIDADE)

## Sondas
- S1 · `"." f.sh; echo a | tee "$(date)"` (f.sh: `date(){ echo .git/config; }`) · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S2 · `\. f.sh; echo a | tee "$(date)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S3 · `"source" f.sh; echo a | tee "$(date)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S4 · `\source f.sh; echo a | tee "$(date)"` e `so''urce f.sh; echo a | tee "$(date)"` · espera: hook rc 2 · obtido: hook rc 0 nas duas; bash grava .git/config
- S5 · `s=source; $s f.sh; echo a | tee "$(date)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S6 · `export PA''TH=./bin:$PATH; echo a | tee "$(date)"` (bin/date imprime .git/config) · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S7 · `source g.sh; echo a | tee "$(echo docs)"` (g.sh: `echo(){ builtin printf .git/config; }`) · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S8 · `source h.sh; echo a | tee "$(printf %s docs)"` (h.sh: `printf(){ builtin echo .git/config; }`) · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config
- S9 · `set -T; trap 'echo .git/config' DEBUG; echo a | tee "$(true)"` · espera: hook rc 2 · obtido: hook rc 0; bash grava .git/config

## Parecer
Reprovado no 041c671b: a volta não fecha a classe da A6. As fixtures novas passam porque escrevem cada palavra da lista na forma canônica. O bash tira aspas e barras e expande variáveis antes de resolver o comando, e o regex lê o texto antes disso (A1). A troca do nome também alcança a via de valor calculado (`echo`, `printf %s`), que a guarda nova não consulta (A2), e o `trap` DEBUG herdado com `set -T` muda a saída da substituição sem trocar o nome (A3). Controle: `echo a | tee "$(date +%F).log"` segue rc 0 e não toca o `.git`. As sondas rodaram pelo `rodar` do `tests/test_hooks.py`, com a montagem da fixture `opaco-u4-seg3-s11-source-bloqueia`; o efeito foi conferido com `bash -c` num repositório de teste.

Sugestão (o desenho é do autor e da segurança): inverter a lista. A lista positiva e o `$(pwd)` → `$PWD` valem só quando todos os outros comandos da linha, lidos depois de tirar as aspas, são palavras literais de uma lista fechada de comandos que não mudam a resolução nem a saída. Nome de comando opaco (`$s`), `trap`, `set` e qualquer palavra fora da lista desligam a liberação: quando não sabe o resultado, a linha recusa, como pede o U4, em vez de liberar por uma lista negativa. Cada sonda acima vira fixture `-bloqueia`, com um mutante por guarda nova.
