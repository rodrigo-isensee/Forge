---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: b953cd459e87c06d6d0a049130505de8b9c8502d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
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
