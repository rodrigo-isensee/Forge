---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: 618af3034626baf06e90b26a51da716400eb46b2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E41.4, conserto do teste de custo do corpus da volta única)

Código testado: b953cd45 (um commit sobre ef186de8). Sem especificação de UX: o critério é o pedido E41 (o teste de custo do corpus não depende da máquina e uma regressão real de custo o derruba). Suíte inteira não rodada (fica para o CI); rodei o módulo `tests.test_hooks_volta_corpus` e mutantes em cópias descartáveis.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E41-a: o teste passa sob carga, sem depender da máquina | 22 testes do módulo, rodadas sob carga | 24 laços de CPU mais uma suíte de hooks em paralelo, carga de 1 min de 33 a 44 em 12 núcleos | passou (5 rodadas, ver abaixo) |
| E41-b: regressão de custo por trabalho a mais derruba | M1: driver roda cada fixture duas vezes | execuções = declaradas (557) | passou (o teste caiu) |
| E41-c: regressão de custo por CPU dentro do hook derruba | S1: `sum(range(20000000))` em `hooks/_comum.py` | CPU por execução | falhou (sobreviveu) |
| E41-d: teto sem folga | S2: 4631+557 subprocessos | teto de subprocessos | falhou (`[]`) |
| Contador e teto sem rodar o corpus | `ContadorDeTrabalhoDoCorpus` (6 testes) | teto inclusivo, execuções a mais e a menos, sono | passou |

## Cenários e resultado real
- Rodadas sob carga (`python3 -I -m unittest discover -s tests -p test_hooks_volta_corpus.py`, TMPDIR próprio, 24 laços de CPU mais um laço de `test_hooks_volta_*.py` em paralelo): rodada 1 `Ran 22 tests in 1076.577s OK`; rodada 2 `893.405s OK`; rodada 3 `878.417s OK`; rodada 4 `883.510s OK`. Mais uma rodada com 12 laços de CPU: `Ran 22 tests in 1125.815s OK`. Cinco de cinco verdes. Não cumpri as 10 rodadas: cada uma levou 15 a 18 minutos sob essa carga (a máquina fica 3 a 9 vezes mais lenta) e o laço de 10 segue fora deste parecer; a reprovação não depende dele. O autor registrou 10 verdes (review, "Provas conferidas").
- Módulo inteiro: os 22 testes passam em cada rodada acima (`OK`, nenhum skip).
- Mutante M1 (cópia, driver roda cada fixture duas vezes, `tests/apoio_volta_unica.py`): falhou como deve, `1113 execuções do hook, e o corpus declara 557` e `9262 subprocessos, acima do teto de 5570`, `FAILED (failures=1)` em 658,6 s. A regressão por trabalho a mais derruba o teste.
- Mutante S1 (cópia, `hooks/_comum.py`, linha após `hook = Hook(nome)`): sobreviveu, `Ran 1 test in 726.806s OK`. Sem a medida de CPU, o teste não pega mais a classe que pegava.
- Sonda S2: `[]` (acima).
- `forge-mutante` das duas specs não rodei: o pedido não é de controle, e M1 e S1 manuais dão o veredito.

## Bugs
Sem arquivo em `docs/qa/bugs/`: os dois achados acima são o defeito (alta, perda de cobertura do portão de custo). Quem corrige é o agente da stack de testes do Forge: contar trabalho do interpretador (por exemplo `sys.setprofile` ou `sys.monitoring`) com teto da medida mais o ruído, e apertar o teto de subprocessos.

## Revalidação (head 41db435f, delta de b953cd45)
Código testado: 41db435f (o remoto está em 17cb7616, só pareceres de review e segurança sobre ele). Suíte inteira não rodada (CI do PR). O parecer anterior (b953cd45) reprovava por A1 (CPU do hook invisível) e A2 (teto com folga); o autor trocou o teto por medida mais ruído, contou passos do interpretador (`sys.monitoring`) e adicionou os mutantes M23 a M29.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E41-b: trabalho a mais derruba | `test_corpus_nos_dois_hooks` | execuções = declaradas (557) | passou (M1 anterior, mutantes do autor) |
| E41-c: CPU dentro do hook derruba (A1) | sonda S1 `sum(range(20000000))` por decisão | passos do interpretador no hook | passou: o teste caiu, `5862147 interpretador, acima do teto de 5861041` |
| E41-d: teto sem folga (A2) | sonda S2 `git --version` a mais por decisão | subprocessos | passou: o teste caiu, `5188 subprocessos, acima do teto de 4631 (medida 4631 mais o ruído 0)` |
| E41-a: passa sob carga | módulo inteiro (28 testes), 3 rodadas | 12 laços de CPU, carga de 1 min entre 11 e 14 | passou, 3 de 3 |
| Mutantes M23 a M29 | `forge-mutante` | cada linha de guarda mudada | todos morreram |

- Sondas (cópias descartáveis do head 41db435f, inserção após `hook = Hook(nome)` em `hooks/_comum.py`, `python3 -I -m unittest discover -s tests -p test_hooks_volta_corpus.py -k test_corpus_nos_dois_hooks`): S1 `FAILED (failures=1)`, rc=1, 95,7 s, `trabalho do corpus: {'execucoes': 557, 'subprocessos': 4631, 'sono': 0, 'interpretador': 5862147, ...}`; S2 `FAILED (failures=1)`, rc=1, 67,6 s, excessos de subprocessos (5188 > 4631) e de interpretador. Os dois achados antigos estão fechados: a classe que escapava agora reprova.
- Módulo inteiro sob carga de 12 laços de CPU (TMPDIR próprio): rodada 1 `Ran 28 tests in 647.303s OK`; rodada 2 `494.901s OK`; rodada 3 `502.207s OK`; cada uma rc=0, sem skip. Não rodei as 10 rodadas do autor.
- `forge-mutante` (5 specs, `--ids M23,M24,M25,M26,M27,M28,M29 --processos 2`, rev=17cb76168c2c): M23, M24, M25 (`hooks/_comum.py:2872`), M26 (`tests/apoio_volta_unica.py:240`), M27 (`:241`, morreu por erro com o controle verde), M28 (`:252`), M29 (`:220`), todos `morreu`, rc=0. Nenhum sobrevivente.
- Delta de domínio lido por `forge-check parecer delta`: `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, as cinco specs de mutantes, `tests/provas/v0479-corpus-custo.md` e o changelog; nenhum arquivo de produção mudou além do que as sondas tocam em cópia.
- Limite: o teto vale para o Python 3.12 da medida (declarado pelo autor); outra versão fica fora desta prova.

## Revalidação (head 618af303, delta de 41db435f; v0478 E41.8)
Código testado: 618af303 (o remoto está nele). Entraram a develop por merge e a medida nova do corpus. Suíte inteira não rodada (CI do PR). Delta lido por `forge-check parecer delta` (base atualizada, sem o que veio da develop): `tests/apoio_volta_unica.py`, `tests/provas/v0479-corpus-custo.md`, `tests/test_hooks_volta_corpus.py`.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E41-d: teto exato, sem folga | `MEDIDA_DO_CORPUS` nova (interpretador 5893967, subprocessos 4631, execuções 557, ruído 0) | passo a mais reprova | passou |
| Medida determinística | módulo inteiro, 2 rodadas | mesma medida nas duas | passou, 2 de 2 |

- `python3 -I -m unittest discover -s tests -p test_hooks_volta_corpus.py` (cópia em 618af303, árvore limpa): rodada 1 `Ran 33 tests in 213.283s OK`; rodada 2 `Ran 33 tests in 111.367s OK`. Sem skip. O teto é exato (ruído 0): duas rodadas verdes com tempos bem diferentes mostram que a medida não depende de tempo nem de carga.
- A diferença da medida (5860121 para 5893967) vem do código da develop (`hooks/_comum.py`, `hooks/agentes.py`, `forge-check`), explicada em `tests/provas/v0479-corpus-custo.md`; não foi regressão do pedido.
- Não rodei de novo os mutantes M23 a M29: o delta não muda guarda, só a constante da medida e testes de AST do `executar`; as sondas S1 e S2 do parecer anterior seguem válidas porque o teto exato fica ainda mais apertado.
- Limite mantido: o teto vale para o Python 3.12 da medida.
