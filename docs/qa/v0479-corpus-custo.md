---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: b953cd459e87c06d6d0a049130505de8b9c8502d
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E41.4, conserto do teste de custo do corpus da volta única)

Código testado: b953cd45 (um commit sobre ef186de8). Sem especificação de UX: o critério é o pedido E41 (o teste de custo do corpus não depende da máquina e uma regressão real de custo o derruba). Suíte inteira não rodada (fica para o CI); rodei o módulo `tests.test_hooks_volta_corpus` e mutantes em cópias descartáveis.

## Achados
- A1 (bloqueante) hooks/_comum.py:2872 · Reproduzido: o hook com `sum(range(20000000))` a cada decisão (CPU a mais por execução, centenas de segundos no lote) passa no `test_corpus_nos_dois_hooks` (OK em 727 s). O contador não vê CPU do Python do hook; o teste antigo via. Regressão real escapa do portão.
- A2 (bloqueante) tests/apoio_volta_unica.py:146 · Reproduzido: `excessos_de_trabalho({'execucoes':557,'subprocessos':4631+557,'sono':0.0},557)` devolve `[]`. O teto 10 por execução tem folga de 20% sobre a medida (8,31); um git a mais por decisão (+12%) passa, e o dono pediu limite sem folga (E41).

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
