---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-develop-relogio
commit: 76cbce17155b2a769e40155c7fcb47b8bb904f46
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0479-develop-relogio

Code review do head 3298def5 (base develop c720891e, v0478 E33.2): sonda S1 com a parcela de disputa fixa e corpus dos dois hooks pela menor de até 3 medidas. Diff: 4 arquivos, 46+/7-, só testes, spec de mutante e fragmento.

## Achados
- A2 (recomendado) tests/test_hooks.py:1324 · a docstring dá o relógio de 8,15 s e o mínimo de 0,75 s de CPU, mas a constante da linha 109 é 8,34 s, o que dá 0,78 s (0,5 × 4,34 × 0,36). Só texto; corrigir no próximo toque.
- A1 (recomendado) tests/prova_de_carga.py:18 · o comentário diz que a S1 reprova em carga pelo aproveitamento, e a docstring nova (tests/test_hooks.py:1319) registra que com parcela perto de 0,1 o critério aceita a S1; nenhum teste vê mais essa janela. Cartão: piso de parcela no critério ou o texto corrigido.

## Parecer
Aprovado.

- S1 (tests/test_hooks.py:1315): o teste antigo usava a parcela da hora, que não é determinística; vermelho no CI quer dizer que o critério `carga_explica_a_recusa` aceitou a S1 com a máquina muito carregada (a própria docstring nova o diz). Com a parcela fixa de 0,36 (a medida da disputa no review), decidem a CPU e o relógio reais do hook: ele prova, em qualquer carga, que o hook com sono a mais não aproveita a fila (aproveitamento abaixo de 0,5). Na máquina livre o teste antigo parava na parcela (perto de 1) e nem chegava ao aproveitamento; agora sempre chega, e o M1 morre em toda carga. O que se perde é ver, por acaso, a janela de parcela baixa em que o critério mascara a S1: é fraqueza do critério, não do teste, e nenhum teste determinístico a provaria; vai em cartão (A1), sem bloquear (`R-REVIEW`: não há defeito novo no diff).
- Medida local (carga 5 em 12 núcleos), 3 rodadas da S1 com espia em `carga_explica_a_recusa`: parede 8,10 a 8,36 s, CPU do hook 0,27 a 0,46 s, aproveitamento 0,18 a 0,29 contra o mínimo 0,5, recusa nas 3; o limiar fica em 0,78 s de CPU (0,5 × 4,34 × 0,36), folga de 1,7 a 2,9 vezes. A carga só reduz a CPU dentro dos 8 s do vigia e aumenta o relógio, o que afasta do mínimo.
- Corpus (tests/test_hooks_volta_corpus.py:122): reusa `menor_custo` (tests/apoio_volta_unica.py:50, já aprovado no TESTE-HEREDOCS-ORCAMENTO-ESTAVEL), sem mecanismo novo. Prova o mesmo: o custo do código abaixo do limite; a carga só soma CPU, e a regressão que passa do limite passa nas 3 medidas. Afrouxa só a margem do ruído (a menor de 3 em vez de uma); o custo extra (até 2 lotes) só aparece acima do limite. A asserção de casos dentro de `medir` mantém a contagem a cada medida.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0478-develop-relogio.json`: "M1 · morreu · tests/prova_de_carga.py:70". `--cobertura --base c720891e`: sem condição mudada sem mutante (o diff não muda guarda de código).
- Testes tocados, no head: a S1 3 vezes OK; `test_corpus_nos_dois_hooks` 1 vez OK em 38,6 s. A suíte inteira fica no CI do PR.
- Commits: dois, Conventional Commits em português, um por teste. Fragmento em `changelog.d/` coerente; o "sem perder o que os testes provam" vale para o que eles provam de modo determinístico (ver A1).

## Revalidação no head 76cbce17 (E33.7)
Delta lido: `forge-check parecer delta docs/reviews/v0479-develop-relogio.md`, intervalo 3298def5..76cbce17, sem o que veio da develop. No domínio: `changelog.d/v0479-develop-relogio.md`, `tests/mutantes/v0478-develop-relogio.json` (só o texto da guarda do M1) e `tests/test_hooks.py` (constantes `PAREDE_DA_S1_S`, `CPU_DA_S1_S`, `PARCELA_DA_S1` na linha 109 e o teste da S1 na linha 1319). Fora do domínio nada se releu.

- A S1 continua recusada, sem folgar o limite: o hook roda de verdade com 3,8 s de sono a mais, e o teste agora exige uma recusa só, com código 2 e a mensagem "não decidiu em 8 s". Só a medida injetada (relógio, CPU dos filhos e parcela) deixa de vir da hora. Com 8,34 s, 0,13 s e 0,36, as guardas de mensagem, de relógio, de CPU mais sono e de parcela deixam passar, e quem recusa é só o aproveitamento: 0,08 contra o mínimo de 0,5. Nenhum limite do `tests/prova_de_carga.py` mudou. Se o hook não fosse recusado, o `assertRaises` cairia. Se a medida fosse consumida mais de uma vez, o `next` acabaria e o teste daria erro, não verde.
- M1: `bin/forge-mutante --processos 1 tests/mutantes/v0478-develop-relogio.json` deu "M1 · morreu · tests/prova_de_carga.py:70". Também apliquei o M1 numa cópia (`git archive` do head) e rodei só `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`: "AssertionError: AssertionError not raised". O teste da S1 sozinho mata o M1, em qualquer máquina.
- Testes tocados no head: a S1 e `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada` passam (2 testes OK em 10,8 s). A suíte inteira fica no CI do PR.
- O estouro de 120 s em `pesado/mesma-sessao-libera` vem da máquina, não do diff. O diff não toca `hooks/` nem o fixture, e os `mock.patch` da S1 valem só dentro dela. Rodei o fixture sozinho com o `executar_fixture`. No head, a primeira rodada deu "prazo de 120 s estourado" e o tempo de usuário foi de 0,37 s, então o hook estava esperando e não calculando. Depois deu OK em 1,1 s no head e em 2,5 s na develop b23124f8. O `rodar` de `tests/test_hooks.py:617` não isola `FORGE_MAQUINA` e herda o HOME, então o hook `pesado` lê a fila real da máquina (`~/.forge/maquina`, MP4) e espera a vez quando outra sessão tem tarefa pesada. Isso vem de antes do diff e não bloqueia este item; vai como cartão.
- Commits do delta: o 76cbce17 segue o Conventional Commits em português e corresponde ao item E33.6. O fragmento de changelog está coerente.

Parecer mantido: aprovado.
