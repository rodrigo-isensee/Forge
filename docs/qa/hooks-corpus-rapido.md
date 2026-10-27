---
tipo: qa
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 978d2d648ec19915cc3ac3b8d140669daa442cc5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-10-27
---
# QA: hooks-corpus-rapido

Escopo: E1.1 do pedido HOOKS-CORPUS-RAPIDO (CorpusHeredocVoltaUnica em 3 módulos, decisão em lote com teste de equivalência, teto de 225 s por módulo, mapa do `bin/forge-testes`). Base 363ceee. QA em paralelo com review e segurança (decisão ACELERA-RODADA "A", item 4).

## Achados
- A1 (bloqueante) bin/forge-testes:100 · mutante sobrevivente: tirar `+ VOLTA_UNICA` de qualquer linha do mapa (96, 100, 105, 106) mantém `test_testes_tocados` e `test_pre_push_afetados` verdes; sem `tests/mutantes/hooks-corpus-rapido.json` (guarda de `bin/` sem mutante declarado)
- A2 (recomendado) tests/test_hooks_volta_lancador.py:1 · a soma dos 3 módulos novos mediu 165 a 167 s aqui (autor: 131 s), acima do PQ-1 de 150 s; confirmar no runner, o teto por módulo (225 s) está cumprido

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 mesmo conjunto de textos | contador DECIDIDOS, comparado com 363ceee (abaixo) | 6 testes, 79 a 7152 textos | passou |
| E1 decisão em lote = hook real | `test_decisao_em_lote_igual_ao_subprocesso_do_hook` (>=200 textos, recusa e liberação) | códigos 0 e 2 na amostra | passou; mutação à mão: falha |
| E2 classe em 3 módulos, pesos regravados | `test_hooks_volta_corpus/_lancador/_propriedades` | n/a | passou |
| E3 teto 25% (225 s) | `test_pesos_teto` (2 testes, mínimo de 50 pesos) | 225 e 225,1 s | passou |
| PQ-1 módulos novos <= 150 s | tempos abaixo | total | soma 165 a 167 s nesta máquina: acima de 150 s (A2) |
| Mapa do bin/forge-testes (decisão 11:55) | `test_testes_tocados` | n/a | passou, mas não guarda `VOLTA_UNICA` (A1) |

## Execução (CI=true, </dev/null, worktree do head)
- test_hooks_volta_corpus: 14 testes, OK, 36 s
- test_hooks_volta_lancador: 20 testes, OK, 67 s
- test_hooks_volta_propriedades: 8 testes, OK, 64 s
- test_hooks: 51 testes, OK, 108 s (o pedido registra 87 s; a máquina estava carregada)
- test_pesos_teto: 2 testes, OK, 0 s
- test_testes_tocados: 80 testes, OK, 12 s
- Todos abaixo de 225 s. Em reexecução isolada os três módulos deram 44, 69 e 52 s. A soma passa de 150 s do PQ-1 do pedido (A2, recomendado: a carga da máquina pode explicar).

## Textos decididos (prova de que o corpus não encolheu)
Instrumentei `decisoes_dos_hooks` (em cópias em `$TMPDIR`, sem tocar a árvore) para gravar o conjunto de textos por teste, em 363ceee (`tests.test_hooks.CorpusHeredocVoltaUnica`) e no head. Conjuntos idênticos, comparados por conteúdo (o nome da pasta temporária aleatória `forge-hook-*` normalizado):
- test_lancador_fora_da_tabela_com_efeito_real: 79 = 79
- test_propriedade_da_reavaliacao_com_marcador: 7152 = 7152
- test_propriedade_do_alfabeto_de_escapes_com_marcador: 936 = 936
- test_propriedade_do_alfabeto_de_opcoes_do_lancador: 1782 = 1782
- test_propriedade_do_lancador_que_divide_texto_com_marcador: 2268 = 2268
- test_t9b_oraculo_do_gatilho: 3576 = 3576
O contador `DECIDIDOS` (len do conjunto por teste) bate com esses números. Testes: os 92 `def test_` da base mais 1 novo (`test_decisao_em_lote_igual_ao_subprocesso_do_hook`), nenhum sumiu; `self.assert*` 420 para 425, `subTest` 82 para 83, `self.fail` 4 para 4.

## Mutação à mão da decisão em lote
- M1: no driver do lote, `saida.append(0 if codigo is None else codigo)` vira `saida.append(0)` (devolve 0 para texto que o hook recusa). `test_decisao_em_lote_igual_ao_subprocesso_do_hook` falha em dezenas de subTests: `AssertionError: 0 != 2 : o lote dá 0 e o hook real dá 2: "! 'bash' '-c' 'gh pr create --draft --base develop --title t --body x'"`.
- M2: devolver 0 só para texto com `git push`: o mesmo teste também falha (`o lote dá 0 e o hook real dá 2: ... git push origin feature/x`).
- Mutantes declarados que o diff renomeou (`lote-leitura-hook.json` e `lote-leitura-hook-volta.json`, trocaram só os ids de teste): `bin/forge-mutante` com `CI=true`, todos morreram (X1, X3, X5, X6; B1 a B4, M1, M2, M3, M9).
- Mapa do `bin/forge-testes`: 4 mutantes (tirar `+ VOLTA_UNICA` das linhas 96, 100, 105, 106), todos sobreviveram: A1. Bug em `docs/qa/bugs/hooks-corpus-rapido-1-mapa-sem-teste.md`.

## Vermelho antes do verde
`forge-testes --vermelho` não foi rodado (fora do que o pedido pediu). O vermelho do teste de equivalência está na mutação M1/M2 acima.

## Verificação de PA-7
`docs/engineering/achados-recorrentes.md` não tem achado registrado ("nenhum ainda"): nada a conferir.

## Notas
O `test_forge` tem 4 falhas (SandboxDoBash x2, ValidarPluginAviso x2) em cópia sem `.git` e no sandbox sem rede; são iguais com e sem o diff, ambientais, fora do escopo.
