---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-develop-relogio
commit: 3298def50eabb19896d66f0ca22da52af39afdd7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0479-develop-relogio

Code review do head 3298def5 (base develop c720891e, v0478 E33.2): sonda S1 com a parcela de disputa fixa e corpus dos dois hooks pela menor de até 3 medidas. Diff: 4 arquivos, 46+/7-, só testes, spec de mutante e fragmento.

## Achados
- A1 (recomendado) tests/prova_de_carga.py:18 · o comentário diz que a S1 reprova em carga pelo aproveitamento, e a docstring nova (tests/test_hooks.py:1319) registra que com parcela perto de 0,1 o critério aceita a S1; nenhum teste vê mais essa janela. Cartão: piso de parcela no critério ou o texto corrigido.

## Parecer
Aprovado.

- S1 (tests/test_hooks.py:1315): o teste antigo usava a parcela da hora, que não é determinística; vermelho no CI quer dizer que o critério `carga_explica_a_recusa` aceitou a S1 com a máquina muito carregada (a própria docstring nova o diz). Com a parcela fixa de 0,36 (a medida da disputa no review), decidem a CPU e o relógio reais do hook: ele prova, em qualquer carga, que o hook com sono a mais não aproveita a fila (aproveitamento abaixo de 0,5). Na máquina livre o teste antigo parava na parcela (perto de 1) e nem chegava ao aproveitamento; agora sempre chega, e o M1 morre em toda carga. O que se perde é ver, por acaso, a janela de parcela baixa em que o critério mascara a S1: é fraqueza do critério, não do teste, e nenhum teste determinístico a provaria; vai em cartão (A1), sem bloquear (`R-REVIEW`: não há defeito novo no diff).
- Medida local (carga 5 em 12 núcleos), 3 rodadas da S1 com espia em `carga_explica_a_recusa`: parede 8,10 a 8,36 s, CPU do hook 0,27 a 0,46 s, aproveitamento 0,18 a 0,29 contra o mínimo 0,5, recusa nas 3; o limiar fica em 0,78 s de CPU (0,5 × 4,34 × 0,36), folga de 1,7 a 2,9 vezes. A carga só reduz a CPU dentro dos 8 s do vigia e aumenta o relógio, o que afasta do mínimo.
- Corpus (tests/test_hooks_volta_corpus.py:122): reusa `menor_custo` (tests/apoio_volta_unica.py:50, já aprovado no TESTE-HEREDOCS-ORCAMENTO-ESTAVEL), sem mecanismo novo. Prova o mesmo: o custo do código abaixo do limite; a carga só soma CPU, e a regressão que passa do limite passa nas 3 medidas. Afrouxa só a margem do ruído (a menor de 3 em vez de uma); o custo extra (até 2 lotes) só aparece acima do limite. A asserção de casos dentro de `medir` mantém a contagem a cada medida.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0478-develop-relogio.json`: "M1 · morreu · tests/prova_de_carga.py:70". `--cobertura --base c720891e`: sem condição mudada sem mutante (o diff não muda guarda de código).
- Testes tocados, no head: a S1 3 vezes OK; `test_corpus_nos_dois_hooks` 1 vez OK em 38,6 s. A suíte inteira fica no CI do PR.
- Commits: dois, Conventional Commits em português, um por teste. Fragmento em `changelog.d/` coerente; o "sem perder o que os testes provam" vale para o que eles provam de modo determinístico (ver A1).
