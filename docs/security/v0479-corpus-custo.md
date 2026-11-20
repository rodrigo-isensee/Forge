---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: 41db435f92eeadb4d16f641857538e77a1ca9657
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

## Revalidação (b953cd45..41db435f)
Lido: `forge-check parecer delta` (único arquivo no domínio: `tests/test_hooks_volta_corpus.py`) e, por pedido, o `sitecustomize` do contador em `tests/apoio_volta_unica.py` (fora do domínio da ferramenta). Nenhum arquivo de `hooks/`, `bin/`, `scripts/`, `.githooks/` nem `.github/` mudou no intervalo (`git diff --name-only`); sem achado novo.
- Fora de produção: o `sitecustomize` é só a string `SITE_DO_CONTADOR`, gravada por `ContadorDeTrabalho.__init__` numa pasta `site/` do tmp do teste e posta no `PYTHONPATH` só do ambiente passado ao hook pelo teste. Não existe `sitecustomize.py` versionado para ele; `grep` de `FORGE_TESTE_TRABALHO` em `hooks/`, `bin/`, `scripts/`, `.githooks/` e `ci.yml` não acha nada. Só liga com `FORGE_TESTE_TRABALHO` no ambiente (`if _pasta:`); o de passos do interpretador também exige `FORGE_TESTE_TRABALHO_CODIGO` e `sys.monitoring`.
- Não muda a decisão: os callbacks só incrementam um contador ou devolvem `DISABLE`; o `time.sleep` embrulhado chama o original; o audit hook só anota. As variáveis do teste só entram no `extra` do fixture; o `HOME` vazio e a entrada de `prazo_de_producao` sem o interpretador mudam o custo, e a decisão segue conferida pelo `esperado` (código e saída) de cada fixture, que o diff não tocou.
- Nada saiu: os fixtures do corpus e os arquivos de recusa não aparecem no diff (só `tests/mutantes/*.json` ganharam mutantes, sem remoção de fixture). No `test_hooks_volta_corpus.py` as quatro asserções retiradas são as do teto antigo de subprocessos, trocadas por asserções mais estritas (teto medida mais ruído 0, execuções a mais ou a menos, um acima do teto, sono); `executar_em_lote(casos) == len(casos)` e o `esperado` por caso ficam.
Não rodei o teste do corpus nesta volta; a suíte inteira fica para o CI. Parecer segue `aprovado`.
