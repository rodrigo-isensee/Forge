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

## Medida nova depois da develop (v0478 E41.10)

A integração da develop (004ce869 em 8dee4328 e cf097822 em 686a6e9e) mudou código que o hook roda; mesma máquina,
Python 3.12.3, tmp a 2 níveis, 234 variáveis, subprocessos e execuções iguais:
- head 686a6e9e: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5893967, 'ambiente': 234}` · FAILED contra o teto de 5860121
- o mesmo head com `hooks/agentes.py`, `hooks/conformidade.json` e sem `hooks/_json_raso.py` (como em 8dee4328): `interpretador 5862452` (2331 do `hooks/_comum.py` e do `forge-check` da primeira integração; 31515 do `hooks/agentes.py` da segunda)
- medida nova: 5893967, ruído 0; com ela, `python3 -m unittest tests.test_hooks_volta_corpus` deu 33 testes OK, rc=0 (o teto é a medida exata: um passo a mais reprova)

## Medida nova do v0479-entrega-parecer-mesclado (v0478 E50.25)

O CI do PR #734 (run 44820187609, parte 2/5, Python 3.12) reprovou o teto: `interpretador 4960049` contra 4958965 (tmp a
3 níveis, 133 variáveis), 1084 passos acima. Mesma máquina da medida anterior, Python 3.12.3, tmp a 2 níveis, 234
variáveis, head 42d380a1:
- `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5895051, 'ambiente': 234}` · FAILED contra o teto de 5893967 (os mesmos 1084 passos do CI)
- medida nova: 5895051, ruído 0; subprocessos e execuções iguais
- autorização (v0478 E50.27): o teto subiu +1084 passos (0,02%), autorizado pelo dono em 20/11 19:09 só para este item
  (DECISÃO DO DONO no pedido v0478), não precedente; o índice `docs/hooks-fixtures.md` já confere

## Teto do E51 (v0478 E51.27)

Autorizado pelo dono em 20/11 às 19:55 (+2168 passos, só para o E51; DECISÃO DO DONO no pedido v0478). Mesma máquina,
Python 3.12.3, tmp a 2 níveis, 234 variáveis, head 12e3b7bc:
- `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5896135, 'ambiente': 234}` · FAILED contra o teto de 5893967 (+2168, igual ao CI: 4961133 contra 4958965)
- medida nova: 5896135, ruído 0

## Soma do E50 e do E51 (v0478 E51.30)

O E50 entrou na develop (#734, f96ede50) com o teto em 5895051 (+1084); o E51 media 5896135 (+2168), cada um sobre
5893967. Com a develop mesclada na branch do E51, mesma máquina, Python 3.12.3, tmp a 2 níveis, 234 variáveis,
`python3 -m unittest tests.test_hooks_volta_corpus`:
- `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5897219, 'ambiente': 234}` · FAILED contra o teto de 5895051 da develop
- medida nova: 5897219, ruído 0; total sobre 5893967: +3252 passos (1084 + 2168, sem passo a mais da junção)
- autorizações do dono, cada uma só para o seu item e não precedente (DECISÃO DO DONO no pedido v0478): E50 +1084 em
  20/11 às 19:09; E51 +2168 em 20/11 às 19:55. O total fica abaixo de +3300, o limite do aviso pedido pelo dono

## E63.1 (v0478, CONFORMIDADE-SEGURANCA)

Os três cartões do `hooks/conformidade.py` (pedido e brief da pasta de controle só do jarvis, escrita no índice,
envio com parte vinda de substituição), sobre a develop d4f0b10a. Mesma máquina, Python 3.12.3, tmp a 2 níveis, 234
variáveis, `python3 -I -m unittest discover -s tests -p test_hooks_volta_corpus.py -k test_corpus_nos_dois_hooks`:
- base (o `hooks/conformidade.py` da d4f0b10a): `interpretador` 5897219, igual ao teto
- primeira versão dos cartões: `{'execucoes': 557, 'subprocessos': 4637, 'sono': 0, 'interpretador': 5975100, 'ambiente': 234}` (+77881, 1,32%; +6 subprocessos): acima de 0,1%, refeita
- com os filtros baratos (o `ls-files` só para pasta, curinga ou magia; o `in` do texto antes das chamadas; o marcador crítico numa chamada só): `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5902634, 'ambiente': 234}`
- por cartão, cada um desligado sobre a versão final: escrita no índice +320, envio com substituição +4630 (medidas de uma rodada intermediária), o resto no pedido e brief da pasta de controle
- medida nova: 5902634 (+5415 passos, 0,092%), ruído 0 em duas rodadas; abaixo de 0,1%: o time decide com a confirmação escrita da segurança (brief v0478-tech-lead-481)

## E63.5 (v0478, volta única dos portões da trilha)

Os achados A1 a A9 da segurança (E63.3) e A1 a A4 do QA (E63.4) no head 6c0b0f03. Mesma máquina, Python 3.12.3, tmp a
2 níveis, 234 variáveis, o mesmo comando, só o `hooks/conformidade.py` trocado em cada rodada:
- base (o da d4f0b10a): `interpretador` 5897219; head 6c0b0f03: 5902634 (os dois iguais às medidas anteriores)
- primeira versão da volta: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5906031, 'ambiente': 234}` (+8812 sobre a base, 0,149%): acima de 0,1%, refeita
- por parte, desligada sobre a primeira versão: conjuntos e regex novos no carregamento do módulo cerca de +2800 (uma chamada por execução: 557 execuções), o shell que lê a entrada +335, o filtro barato +304, o `*` da política no texto +78, o `xargs git` +18; a pasta do controle, o `reset` e o `--git-dir` 0 no corpus
- com os conjuntos literais (sem chamada no carregamento), a regex da pasta do controle compilada só quando a pasta corrente é o controle, o `in` do programa antes de chamar a função do shell, o `stdin` no filtro no lugar de `/dev/` (o `2>/dev/null` passava o filtro) e o fim do caminho com `*` antes da busca: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5902697, 'ambiente': 234}`
- o conserto do `bash < arquivo` (a fixture `e51-wt-bash-entrada-de-arquivo-libera`, com o `any` só quando há redireção) mediu de novo 5902697 em duas rodadas
- medida nova: 5902697, ruído 0 em cinco rodadas; +63 sobre o head 6c0b0f03; total sobre 5897219: +5478 passos (0,093%), abaixo de 0,1%

## E63.9 (v0478, segunda volta única da trilha)

Os achados A1 do review (E63.6) e A12 e A13 da segurança (E63.7) no head e48a2e60. Mesma máquina, Python 3.12.3, tmp a
2 níveis, 234 variáveis, `test_corpus_nos_dois_hooks` instrumentado só para imprimir a contagem, cada árvore por
`git archive`:
- base d4f0b10a: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5897219, 'ambiente': 234}`
- head 37fccab8 e de novo no 02589206 (com o nome atribuído no alvo da entrada): `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5902697, 'ambiente': 234}`
- igual ao e48a2e60 (+0): a exceção da cópia de `wt/` só roda no `controle_no_texto` da `GuardaDaProva` (o corpus não
  chega lá), as regex novas são textos compilados só no uso, e o `help.autocorrect` entrou na tupla do `startswith` que já
  existia; total sobre 5897219: +5478 passos (0,093%), abaixo de 0,1%, e `MEDIDA_DO_CORPUS` segue a mesma

## E63.13 (v0478, terceira volta da trilha)

Os achados A16 e A17 da segurança (E63.11) sobre o head 0f4facab. Mesma máquina, Python 3.12.3, tmp `/tmp/claude-0`,
233 variáveis, `test_corpus_nos_dois_hooks` instrumentado só para imprimir a contagem (o `custo.py` das sondas da
segurança), a base e o 0f4facab por `git archive`:
- base d4f0b10a: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5887957, 'ambiente': 233}`
- head 0f4facab: `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5893435, 'ambiente': 233}`
- volta nova (árvore de trabalho com o conserto): `{'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5893435, 'ambiente': 233}`
- +0 sobre o 0f4facab: a regex nova é texto compilado só no uso, e a `GuardaDaProva.bash` e o `sem_copia_de_wt` não rodam
  no corpus; os absolutos daqui diferem dos de antes (233 variáveis), a diferença não: +5478 sobre a base, 0,093% sobre
  5897219 (5478 / 5897219) e sobre 5887957; abaixo de 0,1%, e `MEDIDA_DO_CORPUS` segue a mesma

## C1b-3 (v0481 E45.13 e E45.19, pasta de controle do Forge com quem vazio)

A entrada nova da pasta de controle em `hooks/conformidade.json` e a linha em `CAMINHOS_DO_CONTROLE` do
`hooks/conformidade.py` (PR #940, head 0bad4b32, base develop 50e5b609):
- CI do #940 (run 46028204382, suíte Python 3.12, parte 4/5): `test_corpus_nos_dois_hooks` reprovou com o
  `interpretador` 865 passos acima do teto de 5902697 (0,015%); subprocessos e execuções dentro do teto
- máquina do autor, outra que a das medidas acima (Python 3.12.3, tmp `/tmp/claude-0` a 2 níveis, 237 variáveis, 4508
  subprocessos; absolutos não comparáveis ao teto), cada árvore por `git archive`, o teste instrumentado só para
  imprimir a contagem: base 50e5b609 `{'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 5894127, 'ambiente': 237}`;
  head 0bad4b32 `{'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 5905764, 'ambiente': 237}`
- medida nova: 5903562 (5902697 + 865, a do CI), ruído 0; total sobre 5897219: +6343 passos (0,108%), acima de 0,1%
- autorização (v0481 E45.19): o dono autorizou o custo a mais da proteção em 27/11 às 14:11 (+865 passos, acumulado
  +0,108%; DECISÃO DO DONO no pedido v0481), só para este item e não precedente; a prova do teto novo é o CI do PR no
  head, com a parte 4/5 verde

## C1b-3 com o #938 (v0481 E45.30)

Com a develop (o #938, 319a968d) mesclada no #940 (head 4f6fd019, E45.29):
- CI do #940 (run 46049072145, suíte Python 3.12, parte 4/5): `test_corpus_nos_dois_hooks` reprovou com
  `{'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 4971301, 'ambiente': 133}` contra o teto de
  4968560 (+2741 passos); subprocessos e execuções dentro do teto
- medida nova: 5906303 (5903562 + 2741, a do CI), ruído 0; total sobre 5897219: +9084 passos (0,154%)
- autorização (v0481 E45.30): o dono autorizou o total de 0,154% em 27/11 às 15:39 (DECISÃO DO DONO no pedido v0481)
  e deu ao time a decisão até 0,5% no total sobre 5897219, registrando cada aumento aqui; acima disso, pergunta ao dono.
  Cartão para reduzir o custo do hook depois do F1. A prova do teto novo é o CI do PR no head, com a parte 4/5 verde

## C1b-3 com a develop em e950baeb (v0481 E45.68)

Com a develop mesclada no #940 (head e950baeb, sem conflito):
- CI do #940 (run 46113149896, suíte Python 3.12, parte 4/5): `test_corpus_nos_dois_hooks` reprovou com o
  `interpretador` em 4962285 contra o teto de 4962039 (+246 passos); subprocessos e execuções dentro do teto
- medida nova: 5906549 (5906303 + 246, a do CI), ruído 0; total sobre 5897219: +9330 passos (0,158%)
- decisão do time (v0481 E45.68): abaixo do limite de 0,5% no total que o dono deu ao time em 27/11 às 15:39
  (DECISÃO DO DONO no pedido v0481). A prova do teto novo é o CI do PR no head, com a parte 4/5 verde

## Ambiente fixo (v0481 E45.73, teto uma vez só para o #940 e o #944)

O run 46134894622 do #940 (head 51815962, CI no merge com a develop 1ced5c09, o #952) reprovou com
`{'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 4973152, 'ambiente': 133}` contra o teto de
4971547. O acerto por variável (`PASSOS_POR_VARIAVEL_POR_SUBPROCESSO` x 4631) dava 9262 passos por variável, e a
inclinação real é 2 x 4508 = 9016 (máquina do autor, mesmo código, 242 e 243 variáveis no teste: 5910356 e 5919372; 252:
6000516, +90160): o teto andava com o número de variáveis do runner, não com o código.
- correção: o contador completa o ambiente do hook (só o dele; os filhos herdam) até 256 variáveis
  (`FORGE_TESTE_TRABALHO_AMBIENTE`), anota esse número, e outro número é excesso; o acerto por variável sai
- máquina do autor (Python 3.12, tmp `/tmp/claude-0` a 2 níveis), árvore 51815962 com a develop 1ced5c09 mesclada,
  o lote do corpus com 242, 243 e 137 variáveis no teste (log sem edição):
  - {'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 6081660, 'ambiente': 256}
  - {'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 6081660, 'ambiente': 256}
  - {'execucoes': 557, 'subprocessos': 4508, 'sono': 0, 'interpretador': 6081660, 'ambiente': 256}
- medida nova: 6081660 com 256 variáveis e tmp a 2 níveis; no CI (tmp a 3 níveis, pelo teto de 4971547 do run) o
  teto é 6082120. Ruído 0
- aumento do código: o teto anterior (5906549) saiu do run 46113149896 (e950baeb, 132 variáveis, 4962285); o mesmo
  código com 133 dá 4962285 + 9016 = 4971301, e o run 46134894622 deu 4973152: +1851, o código da develop nova
  (o #948, a 0.48.0 e o #952) com o #940. Total sobre 5897219: +11181 passos (0,190%)
- decisão do time (v0481 E45.73): abaixo de 0,5% no total, o limite que o dono deu ao time em 27/11 às 15:39 (DECISÃO
  DO DONO no pedido v0481); correção única para o #940 e o #944 (ordem do dono 28/11 07:20, item 1). A prova do teto
  novo é o CI do PR no head, com a parte 4/5 verde

## C1b-2 (v0481 E45.44, o #944 com a develop em ed6e6dbf)

O código do #944 (C1b-2: `bin/forge_pareceres.py` pela cópia e a guarda dormente do parecer de item) com a develop
em ed6e6dbf (o #940 e o #956) mesclada, no teto do "Ambiente fixo" (6081660):
- máquina do autor (Python 3.12, tmp a 2 níveis), `python3 -m unittest tests.test_hooks_volta_corpus`, log sem edição:
  - `'6089793 interpretador, acima do teto de 6081660 (medida 6081660 mais o ruído 0)'`
  - `{'execucoes': 557, 'subprocessos': 4510, 'sono': 0, 'interpretador': 6089793, 'ambiente': 256}`, em 556 casos
- a mesma contagem (+8133) que o autor mediu às 09:3x do mesmo dia: o contador é determinístico
- medida nova: 6089793 (+8133, 0,138% sobre 5897219); total sobre 5897219: +11181 + 8133 = +19314 passos (0,328%)
- decisão do dono em 28/11 às 10:06 (opção A, DECISÃO DO DONO no pedido v0481): o #944 sobe o teto só o que o código
  dele mede, dentro de 0,5%. Os subprocessos (4510) seguem abaixo do teto de 4631 e não mudam
- remedido com a develop em c11e3809 (o #947 e o #957 mesclados), no teto 6081660, log sem edição:
  `{'execucoes': 557, 'subprocessos': 4510, 'sono': 0, 'interpretador': 6089793, 'ambiente': 256}`, em 556 casos;
  a mesma medida: o #947 e o #957 não somam passo ao corpus, e o teto segue 6089793
- remedido com a develop em ae194fa9 (o #958 mesclado), no teto 6081660, log sem edição:
  `{'execucoes': 557, 'subprocessos': 4510, 'sono': 0, 'interpretador': 6089793, 'ambiente': 256}`, em 556 casos;
  a mesma medida: o #958 não soma passo ao corpus, e o teto segue 6089793 (+19314 sobre 5897219, 0,328%)
