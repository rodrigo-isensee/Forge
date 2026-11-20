---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: 618af3034626baf06e90b26a51da716400eb46b2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-corpus-custo (v0478 E41.3)

Gatilhos: teste de controle (corpus que prova a recusa das formas de volta única pelos hooks de controle).

## Escopo lido
Diff `ef186de8..b953cd45`: `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, dois arquivos de mutantes e o fragmento de changelog. Nenhum arquivo de `hooks/`, do corpus (fixtures) nem de `docs/` foi tocado (`git diff --stat`).

## Conferência do pedido
- Fixtures: nenhuma removida nem alterada; o corpus e as marcas `fecha` ficam como estavam.
- Provas de recusa: o diff em `test_hooks_volta_corpus.py` só troca o corpo de `test_corpus_nos_dois_hooks` (CPU por contador) e acrescenta a classe `ContadorDeTrabalhoDoCorpus`. A asserção `executar_em_lote(casos) == len(casos)` e o `executar_fixture` (código e saída esperados por caso) seguem iguais; o conserto só soma o ambiente do contador (`PYTHONPATH` e `FORGE_TESTE_TRABALHO`) ao `extra`, que não muda a decisão do hook.
- A medida de custo ficou mais estrita, não mais frouxa: execuções diferentes das declaradas (a mais ou a menos), mais de 10 subprocessos por execução e qualquer sono do hook reprovam. Falha fechada: se o contador não carregar, as execuções contadas são 0 e o teste reprova.
- Mutantes M1 (driver duplica o caso) e M2 (hook dorme) cobrem as regressões de custo; M3 neutraliza a condição de execuções.

## Sondas e ferramentas
Rodei `ContadorDeTrabalhoDoCorpus` (6 testes, OK) e `test_corpus_nos_dois_hooks` (1 teste, 167 s, OK). A suíte inteira fica para o CI. Sem ferramenta faltando.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

## Revalidação (41db435f..618af303, E41.7)
Lido: `forge-check parecer delta` (intervalo 41db435f..674847bf, sem o que veio da develop em cf097822). Do domínio, só `tests/test_hooks_volta_corpus.py`, e o trecho listado (BP1, `chamadas_do_executar`) já está em cf097822: é da develop, fora desta volta. Leitura anterior: o resto do parecer acima, no head 41db435f.
- Delta próprio da branch: 618af303 troca só `MEDIDA_DO_CORPUS["interpretador"]` de 5860121 para 5893967 (`tests/apoio_volta_unica.py:194`) e registra a medida em `tests/provas/v0479-corpus-custo.md`. Execuções (557), subprocessos (4631), ambiente (234) e profundidade (2) seguem iguais.
- A subida tem origem fora da branch: `git diff cf097822 618af303 -- hooks bin scripts .githooks .github` é vazio; o código de controle que o hook roda é o da develop, e o registro atribui os 33846 passos a `hooks/_comum.py`, `hooks/agentes.py` e `forge-check` da develop. Nenhuma fixture nem asserção de recusa mudou.
- Teto exato continua fechando: `RUIDO_DO_CORPUS` segue 0 nos dois, `teto = medida + ruido` e reprova com `trabalho[nome] > teto` (`tests/apoio_volta_unica.py:261-263`); `test_um_acima_do_teto_reprova` prova que um passo acima reprova. Rodei `ContadorDeTrabalhoDoCorpus` (12 testes, OK). A medida determinística em duas rodadas é prova do QA (E41.8); o corpus inteiro e a suíte ficam para o CI.
Sem achado. Parecer segue `aprovado`.
