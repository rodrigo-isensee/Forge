---
tipo: qa
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: fe9dfb26221b1de4f68e8efd43899a663d1a52c0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: prop-tempo-cpu

Parecer sobre o head `fe9dfb26221b1de4f68e8efd43899a663d1a52c0` (base `9620160`), em paralelo com review e segurança (ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as de E1 do pedido PROP-TEMPO-CPU e as decisões técnicas dele.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: filho que dorme não conta CPU (relógio sobe, CPU não) | test_medida_cpu.test_filho_que_dorme_nao_conta... ; mutante M1 | relógio >= 1,4 s com CPU < 0,5 s | passou; M1 morreu |
| E1: CPU dos filhos conta | test_filho_que_gasta_cpu_conta; M2 | filho com 0,8 s de CPU >= 0,7 s | passou; M2 morreu |
| E1: CPU do próprio processo conta | test_o_trabalho_do_proprio_processo_conta; M3 | processo > 0,1 s | passou; M3 morreu |
| Decisão 16:07: limite do corpus = 60 s x trabalhadores | test_limite_do_corpus_e_60_s_por_trabalhador; M4 | 1, 2, 4, 8 e 64 núcleos (mínimo 1, teto 4 trabalhadores) | passou; M4 morreu |
| E1: os 4 testes medem CPU com o mesmo limite (60 s; 1,0 s) | test_hooks_volta_corpus/lancador/propriedades (diff: `medida.cpu` com 60, 60 e 1.0) | limite igual ao anterior, sem asserção tirada | passou (43 testes) |
| Decisão 17:39 e 17:45: mapa FORGE_CHECK e contagem exata 26 | test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele | contagem exata, não afrouxada | passou |
| Texto da medida | test_o_texto_diz_cpu_e_relogio | formato `CPU x.xx s, relógio y.yy s` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_medida_cpu tests.test_testes_tocados`: 86 testes, OK (18,4 s).
- `tests.test_hooks_volta_corpus`, `test_hooks_volta_lancador` e `test_hooks_volta_propriedades`: 43 testes, OK (171 s), rc=0 (`[propriedade do texto aberto] 49559 formas: CPU 30.48 s, relógio 30.48 s`).
- `bin/forge-mutante tests/mutantes/prop-tempo-cpu.json`, saída 0:
  `M1 · morreu · tests/apoio_volta_unica.py:62`, `M2 · morreu · :62`, `M3 · morreu · :62`, `M4 · morreu · tests/apoio_volta_unica.py:44`.
- Conferência da lista contra o diff: o diff não toca `hooks/`, `.githooks/` nem `tests/catraca.py`; em `bin/` só entra a linha do mapa FORGE_CHECK, guardada pela contagem exata em `test_testes_tocados`. As linhas de guarda da medida (cálculo da CPU, limite por trabalhador) têm um mutante cada. Sem linha de guarda sem mutante.
- Vermelho antes do verde: não rodei `forge-testes --vermelho` (a brief limita a rodada aos módulos do item); a prova de que os testes novos falham sem a implementação é a dos mutantes M1 a M4, que desfazem cada ramo da medida.
- Carga (processo de duração fixa, 36 laços com `timeout 40` em 12 núcleos), sonda com os 3 casos mais pesados do teste de 1,0 s:
  sem carga: CPU 0,08 / 0,10 / 0,11 s, relógio igual;
  com carga: CPU 0,13 / 0,14 / 0,15 s e 0,13 / 0,13 / 0,19 s contra relógio 0,42 / 0,48 / 0,52 s e 0,45 / 0,46 / 0,77 s.
  O relógio subiu 4 a 7 vezes e passaria de 1,0 s em casos de pior tempo; a CPU subiu menos de 2 vezes e ficou a 0,2 s do limite de 1,0 s. A medida de CPU fica estável quando o relógio sobe.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens (`nenhum ainda`).

## Observações (sem achado)
- O corpus perdeu o teto de relógio; o travamento fica coberto pelo prazo do processo da suíte, como diz o pedido.
- A CPU sob carga cresce um pouco (cache e contenção); a folga observada (0,2 s contra 1,0 s; 30 s contra 60 s x trabalhadores) cobre isso.
