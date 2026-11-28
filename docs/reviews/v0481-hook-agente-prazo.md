---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-agente-prazo
commit: fda308676fa86cd79217b7c2fe725889375ace04
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E50.2), #950 HOOK-AGENTE-PEDIDO-GRANDE

1ª rodada completa sobre `319a968d..fda30867`: `hooks/agentes.py` (+54, abaixo do teto H1), `tests/test_hooks_agentes_autor.py` (classe `PedidoGrande`), duas specs de mutantes e o fragmento em `changelog.d/`.

- ci: fda308676fa86cd79217b7c2fe725889375ace04 verde
  (run CI 46075222405: suíte 1-5/5, teto de pulados, instalação, bateria (passos, python 3.14, verificações longas) e árvore provada verdes; falham só `bateria (pareceres)` e `bateria`, que esperam o parecer; Catraca 46075222432 verde)
- testes do diff: `python3 -m unittest tests.test_hooks_agentes_autor`: 17 testes, OK (25 s)
- mutantes: `forge-mutante tests/mutantes/v0481-hook-agente-prazo.json`: os 8 morreram (hooks/agentes.py:1095 a 1123); `tests/mutantes/v0481-hook-agente-prazo-2.json`: o 1 morreu (hooks/agentes.py:1107); `forge-mutante --cobertura --base 319a968d`: toda condição mudada coberta, rc=0

## Achados
- A1 (recomendado) tests/test_hooks_agentes_autor.py:219 · a restauração das originais só é afirmada na saída normal do `with`; falta um teste com exceção dentro do `GitEmLote` (a sonda do review mostra que restaura e encerra o cat-file, mas nenhum teste segura isso).
- A2 (recomendado) hooks/agentes.py:1113 · o `readline` do cat-file não tem limite de tempo, ao contrário do `git` do forge-check (`GIT_TIMEOUT_S`); um cat-file travado só cai no vigia de 8 s, que recusa o disparo em vez de só perder o aviso.

## Sondas

## Parecer
Aprovado.

O que o brief pediu conferir:
- **Restauração em toda saída:** a troca está em `__enter__`/`__exit__` e o `__exit__` devolve as originais na primeira linha, antes de matar os cat-file, e não engole a exceção, que sobe ao `except` de `avisos_de_brief_vencido` (registra e devolve []). Sonda própria (`python3 -I`, `brief_vencido` trocado por função que levanta): saída `[]`, `registrar_erro` 1 vez, originais restauradas; com exceção depois de abrir um lote, originais restauradas e o cat-file com `returncode` (encerrado). Vai em A1 só como teste que falta.
- **Aviso D3 idêntico:** `test_o_aviso_e_o_mesmo_com_processos_que_nao_crescem_com_o_pedido` compara a lista com e sem o lote num pedido de 312 linhas `conferida` (com a linha de hash das decisões); sonda própria com 4 briefs reais do v0481 deu lista igual nos 4.
- **Mesma resposta por pergunta:** `e_ancestral` lote = rev-list da ponta sha40 (inclui a própria ponta, como o `--is-ancestor` de a em a); fora dele, só objeto que não resolve ao próprio sha (tag anotada) volta à original; commit ausente ou árvore resolvem a None/False nos dois caminhos. `sha_do_commit` com `^{commit}` no cat-file dá o mesmo sha40 que o `rev-parse --verify`; `missing` e saída vazia dão None. Ponta ou ref fora de sha40 minúsculo (nome, `a..b`, quebra de linha) vai às originais. O teste cobre a matriz refs x pontas contra as originais.
- **Ambiente:** o Popen tira GIT_* como o `git()` do forge-check (o mutante da guarda em hooks/agentes.py:1107 morre).

Leitura (R-REVIEW): um comportamento só, sem tirar checagem nem mudar o prazo; docstrings citam o ID; commit único `fix(hooks)` em Conventional Commits; fragmento de changelog presente. Os dois achados são recomendados e viram cartão depois do merge.
