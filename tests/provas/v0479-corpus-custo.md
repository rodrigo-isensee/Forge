# Provas: v0479-corpus-custo, volta única (v0478 E41.5)

Conserto dos achados A1 e A2 do review (08db4eab) e do QA (de45abb0) no head b953cd45. Máquina do autor: 12 núcleos,
Python 3.12.3, tmp `/tmp/claude-0` (2 níveis), 234 variáveis no ambiente do hook. Logs brutos em
`~/.forge-contrib/tmp/e415/`; aqui vão as linhas que provam.

## A1: a CPU do Python do hook vira passo contado

O `sitecustomize` do contador liga `sys.monitoring` (só com as variáveis do contador no ambiente do teste) e conta, no
código do repositório, cada chamada (Python ou C), cada função que começa e cada salto para trás (volta de laço).

Fontes de variação achadas e tiradas, por diagnóstico por função (dois lotes iguais comparados):
- `HOME` de quem roda: o `forge-check` lia os 6535 briefs de `~/.forge-contrib/docs/briefs` (cerca de 20 milhões de
  passos, e o CI não os tem; os subprocessos iam de 4631 a 4633). O hook contado roda com `HOME` numa pasta vazia.
- Casos com `prazo_de_producao` (OT1, OT2): andam até o prazo, quanto a máquina deixa (até 860 mil passos de diferença
  entre rodadas). A entrada principal deles roda sem os passos do interpretador.
- Profundidade do tmp: 460 passos por nível (o hook sobe as pastas-mãe). Medido: 2 níveis 5860121, 3 níveis 5860581,
  6 níveis 5861961 (exato, 4 x 460). O teto acerta pela profundidade de quem roda.
- Tamanho do ambiente: o `git` do `forge-check` copia o ambiente variável por variável. Com 1 variável a mais
  (`PYTHONPYCACHEPREFIX`, do `forge-mutante`): 5869383, 9262 a mais (2 x 4631). O teto acerta pelo número de variáveis
  que o hook viu.
- Sem efeito: o comprimento do tmp (`/tmp/claude-0/e415a` e um de 62 caracteres deram 5860581 os dois) e a profundidade
  do clone do Forge (5 e 7 níveis deram 5860121).

Sonda S1 do review (`sum(range(20000000))` depois de `hook = Hook(nome)`), no código final, lote inteiro:
- `TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5861227, "sono": 0, "subprocessos": 4631}`
- `EXCESSOS ["5861227 interpretador, acima do teto de 5860121 (medida 5860121 mais o ruído 0)"]` · FAILED

O que fica fora: o trabalho de dentro de uma chamada C que já existia (a regex que ficou catastrófica no motor `re`, o
mesmo `sum` sobre um iterável maior) não vira passo; vira passo a chamada a mais e a volta de laço a mais.

## A2: teto dos subprocessos na medida mais o ruído

Teto: 4631 + 0 (era 10 por execução, 5570). Sonda S2 do review (um `git --version` a mais em cada decisão), lote inteiro:
- `TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5861227, "sono": 0, "subprocessos": 5188}`
- `EXCESSOS ["5188 subprocessos, acima do teto de 4631 (medida 4631 mais o ruído 0)", "5861227 interpretador, acima do teto de 5860121 (medida 5860121 mais o ruído 0)"]` · FAILED

No teste de unidade, `test_um_acima_do_teto_reprova` cobre a medida mais 1 e a medida mais 557 dos dois.

## Rodadas sob carga (12 laços `while :; do :; done`), commit 67c1ce6c, cópia limpa

- rodada 1 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 210 s · carga 27.84
- rodada 2 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 206 s · carga 4.08
- rodada 3 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 222 s · carga 23.00
- rodada 4 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 221 s · carga 7.98
- rodada 5 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 206 s · carga 3.52
- rodada 6 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 196 s · carga 26.83
- rodada 7 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 209 s · carga 3.60
- rodada 8 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 197 s · carga 25.33
- rodada 9 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 190 s · carga 6.20
- rodada 10 · rc=0 · TRABALHO {"ambiente": 234, "execucoes": 557, "interpretador": 5860121, "sono": 0, "subprocessos": 4631} EXCESSOS []  · relógio 196 s · carga 1.91

Ruído medido: 0 nos subprocessos e 0 nos passos (as 10 iguais). Antes do `HOME` vazio e da exclusão do prazo, com o
contador inicial (8 rodadas do mesmo laço, head de45abb0 com a árvore de trabalho): passos de 28843978 a 30050770 e
subprocessos de 4631 a 4633, por isso as duas exclusões.

## Mutantes (`bin/forge-mutante`, as 4 specs, rev 67c1ce6c, rc=0; M29 na rev 6aafad01, rc=0)

- M1 · morreu · tests/apoio_volta_unica.py:329
- M2 · morreu · hooks/_comum.py:2872
- M3 · morreu · tests/apoio_volta_unica.py:243
- M4 · morreu · tests/apoio_volta_unica.py:257
- M5 · morreu · tests/apoio_volta_unica.py:259
- M6 · morreu · tests/apoio_volta_unica.py:325
- M7 · morreu · tests/apoio_volta_unica.py:147
- M8 · morreu · tests/apoio_volta_unica.py:151
- M9 · morreu · tests/apoio_volta_unica.py:151
- M10 · morreu · tests/apoio_volta_unica.py:218
- M11 · morreu · tests/apoio_volta_unica.py:138
- M12 · morreu · tests/apoio_volta_unica.py:257
- M13 · morreu · tests/apoio_volta_unica.py:158
- M14 · morreu · tests/apoio_volta_unica.py:162
- M15 · morreu · tests/apoio_volta_unica.py:166
- M16 · morreu · tests/apoio_volta_unica.py:170
- M17 · morreu · tests/apoio_volta_unica.py:170
- M18 · morreu · tests/apoio_volta_unica.py:245
- M19 · morreu · tests/apoio_volta_unica.py:249
- M20 · morreu · tests/apoio_volta_unica.py:219
- M21 · morreu · tests/apoio_volta_unica.py:327
- M22 · morreu · tests/apoio_volta_unica.py:213
- M23 · morreu · hooks/_comum.py:2872
- M24 · morreu · hooks/_comum.py:2872
- M25 · morreu · hooks/_comum.py:2872
- M26 · morreu · tests/apoio_volta_unica.py:240
- M27 · morreu · tests/apoio_volta_unica.py:241 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
- M28 · morreu · tests/apoio_volta_unica.py:252
- M29 · morreu · tests/apoio_volta_unica.py:220

M23 é a sonda S1, M24 a S2 e M25 um laço de 1000 voltas por decisão. Cobertura (`--cobertura --base ef186de8`):
nenhuma condição sem mutante, rc=0.
