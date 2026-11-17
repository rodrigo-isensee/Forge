# v047-resolucao-trocada-nome-citado - RESOLUCAO_TROCADA não vê o nome do comando citado, escapado ou montado
- Severidade: alta
- Responsável sugerido: dev da stack do hook (`hooks/conformidade.py`, R-CONFORMIDADE)
- Ambiente: melhoria/v047-conformidade-destino-opaco, 041c671bbcca2cb1fdee5b9d65304151bbf649a5, bash

## Passos para reproduzir
1. Fixture montada como `opaco-u4-seg3-s10-ponto-bloqueia.json` (tech-lead, branch `melhoria/x`), `f.sh` com `date(){ echo .git/config; }`, só o comando muda.
2. Comando `so""urce ./f.sh; echo a > "$(date)"` (e `\. ./f.sh; …`, `"." ./f.sh; …`, `s=sour""ce; $s ./f.sh; …`).
3. Comando `export PA""TH=./bin:$PATH; echo a > "$(date)"` com `bin/date` executável que imprime `.git/config`.
4. `a=PA; printf -v "${a}TH" ./bin:$PATH; echo a > "$(date)"` e `n=TMP; declare "${n}DIR=.git"; cp config "$(mktemp -u)"`.

## Resultado esperado
Código 2 (R-CONFORMIDADE), como o `. ./f.sh` literal (fixture s10).

## Resultado obtido
Código 0, hook libera. No bash real (cópia em `$TMPDIR` com pasta `.git`), as linhas 2 a 4 gravam `a` em `.git/config`.

## Evidência
Probe com `Fixture`/`rodar` de `tests/test_hooks.py`: `0 | so""urce ./f.sh; echo a > "$(date)"`, `0 | \. ./f.sh; …`, `0 | "." ./f.sh; …`, `0 | s=sour""ce; $s ./f.sh; …`, `0 | export PA""TH=./bin; …`, `0 | a=PA; printf -v "${a}TH" …`; controle: `. ./f.sh; …` sai 2. A regex `RESOLUCAO_TROCADA` (hooks/conformidade.py:496) casa só o nome em texto puro; aspas partidas, barra invertida, aspas em volta e nome montado por variável passam. Fecha com: qualquer aspa, barra invertida ou `$` na palavra de comando ou no nome a atribuir desliga a lista positiva (sobra recusa), ou o hook normaliza a palavra antes de casar.
