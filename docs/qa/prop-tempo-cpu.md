---
tipo: qa
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: f0a5194c1254591e29a9346741bb17618b2e4c61
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: prop-tempo-cpu

Parecer sobre o head `f0a5194c1254591e29a9346741bb17618b2e4c61` (base `9620160`), volta 7 (revalidação por delta de `650dbf9`, que só mudou texto em `c3214f1`), volta 6 (limites 90 s por trabalhador, 120 s e 2,0 s, decisão do dono de 2026-10-27 19:13), em paralelo com review e segurança (ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as de E1 do pedido e as decisões dele. Substitui o parecer de `fe9dfb2`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: filho que dorme não conta CPU | test_medida_cpu.test_filho_que_dorme_nao_conta...; M1 | relógio >= 1,4 s com CPU < 0,5 s | passou; M1 morreu |
| E1: CPU dos filhos conta | test_filho_que_gasta_cpu_conta; M2 | filho com 0,8 s de CPU >= 0,7 s | passou; M2 morreu |
| E1: CPU do próprio processo conta | test_o_trabalho_do_proprio_processo_conta; M3 | processo > 0,1 s | passou; M3 morreu |
| Decisão do dono 19:13: corpus 90 s por trabalhador | test_limite_do_corpus_e_90_s_por_trabalhador; M4 | 1, 2, 4, 8 e 64 núcleos (mínimo 1, teto 4 trabalhadores) | passou; M4 morreu |
| Decisão do dono 19:13: lançador 120 s e T 2,0 s de CPU | test_hooks_volta_lancador (2 propriedades), test_hooks_volta_propriedades.test_t_reconhecedor... | limites 120 e 2,0 aplicados (diff: `medida.cpu`, 120, 120, 2.0) | passou (ver folga) |
| Mapa FORGE_CHECK e contagem exata 26 | test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele | contagem exata | passou |
| Texto da medida | test_o_texto_diz_cpu_e_relogio | `CPU x.xx s, relógio y.yy s` | passou |

## Revalidação por delta (650dbf9...f0a5194)
- `git diff 650dbf9...f0a5194` em `tests/` e `changelog.d/`: 3 docstrings (limites 120 s e 2 s) e o fragmento do changelog; comparação das árvores sintáticas sem docstrings das duas fontes: idênticas (nenhum número, asserção ou código mudou). Os 3 achados anteriores (A1 a A3, textos defasados) estão resolvidos por `c3214f1`; o bloco `## Achados` ficou vazio.
- `python3 -m unittest tests.test_medida_cpu tests.test_changelog`: 51 testes, OK (1 skip já existente).
- Os números de CPU, folga e mutantes abaixo valem do head `650dbf9`, cujo código é o mesmo.

## Cenários e resultado real
- `tests.test_medida_cpu` + `tests.test_testes_tocados`: 86 testes, OK (14,0 s).
- `tests.test_medida_cpu`, `test_hooks_volta_corpus`, `test_hooks_volta_lancador`, `test_hooks_volta_propriedades` (sonda em `$TMPDIR` que só imprime a medida de cada `MedidaDeCpu`, sem tocar a árvore): 48 testes, OK, 117,9 s, rc=0.
- `bin/forge-mutante tests/mutantes/prop-tempo-cpu.json`, saída 0: `M1 · morreu · tests/apoio_volta_unica.py:62`, `M2 · morreu · :62`, `M3 · morreu · :62`, `M4 · morreu · :44`.
- Conferência da lista contra o diff: o diff não toca `hooks/`, `.githooks/` nem `tests/catraca.py`; em `bin/` só a linha do mapa FORGE_CHECK (guardada pela contagem exata). Linha de guarda de código (cálculo da CPU, limite por trabalhador) tem um mutante cada. Os números 120 e 2,0 são limites em asserção de teste, não guarda de código de decisão; sem mutante próprio (observação, sem achado).
- Vermelho antes do verde: não rodei `forge-testes --vermelho` (a brief limita a rodada aos módulos do item e esta volta só muda números de limite); a prova dos testes novos são M1 a M4.

### CPU medida e folga contra o limite novo (12 núcleos, 4 trabalhadores)
| Teste | CPU medida | Relógio | Limite | Folga |
|---|---|---|---|---|
| test_corpus_nos_dois_hooks | 56,19 s | 14,22 s | 360 s (90 x 4) | 6,4 x |
| lançador: propriedade do `env -S` etc. | 18,33 s | 17,98 s | 120 s | 6,5 x |
| lançador: propriedade do texto aberto (49559 formas) | 21,28 s | 21,28 s | 120 s | 5,6 x |
| T reconhecedor linear (8 subcasos) | 0,06 a 0,23 s (pior 0,23) | 0,01 a 0,23 s | 2,0 s | 8,7 x |

Contra o runner do CI (dados do pedido, 18:41, não medidos por mim): corpus 121,09 s com 2 trabalhadores contra 180 s (1,5 x) e propriedade 72,66 s contra 120 s (1,65 x). A folga no CI é menor que a local, mas positiva; o limite ainda reprova custo que dobre.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens (`nenhum ainda`).

## Observações (sem achado)
- O corpus segue sem teto de relógio; o travamento fica coberto pelo prazo do processo da suíte.
- A trava está mais frouxa por decisão do dono; o limite de T (2,0 s) tem 8,7 x de folga local, então pega só custo que exploda.
