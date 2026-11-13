---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: 4baba3c520cd6de5aed906fa3c03b72ed8ec2a9f
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.113, por delta)

Código testado 4baba3c5 (o head da branch, 5e6e245e, só soma dois pareceres sobre ele), base befd4cca, delta desde baf1bee6: a retomada dos agentes sai do README e do modelo, mais a junção da develop. O CI do PR 545 está vermelho nas partes 3/3 (3.12 e 3.14); reproduzi a parte 3/3 inteira local e a falha vem desta branch, não da develop.

## Achados
- A4 (recomendado) README.md:51 · fechado: a frase que mandava à skill `trabalho-em-paralelo` saiu do README e do modelo; `grep -c trabalho-em-paralelo README.md` dá 0.
- A5 (bloqueante) tests/test_ambiente_sem_auto_update.py:17 · o teste novo cita README.md e o `test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` reprova ("README.md: 1 linhas, a lista diz 0"); registre a citação em `CITACOES_CONHECIDAS` ou tire o caminho do teste. Reproduzido; derruba a parte 3/3.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orientação ao dono no README e no modelo | `AmbienteSemAutoUpdate.test_orientacao_ao_dono_no_readme_e_no_modelo` | frase exata nos 2 arquivos | passou |
| Retomada fora do README e do modelo (A4) | `grep` por `trabalho-em-paralelo` e `retoma` | n/a | passou |
| Nenhuma regra perdida | `tests.test_forge.TetoPorPr` | frase do teto | passou |
| Citação de caminho de texto só como a lista conhece | `test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` | citação nova em teste | **falhou** (A5) |
| Teste novo lido pelo filtro do pre-push | `MapaCobreOQueOsTestesLeem` (`test_testes_tocados`) | módulo na lista | passou |

## Cenários e resultado real
- Origem da falha da parte 3/3: 1430 testes, 11 falhas. Dez são do ambiente desta máquina (`proc` e `chown` indisponíveis no sandbox com `CI=1` forçado, `tests/apoio_sandbox.py:104`; `test_prepush_so_docs`, `test_testes_tocados.MedidaDaVagaPesada`): no CI não ocorrem e a develop (befd4cca) está verde. A única falha de conteúdo é a A5, determinística, e só existe porque a branch criou o teste.
- Vermelho antes do verde: o teste só confere presença de frase em 2 arquivos; não rodei `forge-testes --vermelho` (carga ~20 em 12 núcleos). A5 é o oposto: teste existente que cai com o diff.
- Mutação não se aplica (sem lógica nova; o delta em `bin/forge-testes` é só quebra de linha).

## Provas
- `CI=1 python3 scripts/suite-partes.py --parte 3/3` (no head 5e6e245e) -> `Ran 1430 tests in 1837.711s (2 processos, parte 3/3)`, `FAILED (failures=11, skipped=26, guarda=2)`; a falha `test_reval_delta ... AssertionError: ['(a) tests/test_ambiente_sem_auto_update.py · README.md: 1 linhas, a lista diz 0']`.
- `python3 -m unittest tests.test_ambiente_sem_auto_update tests.test_forge.TetoPorPr tests.test_modelos_projeto` -> Ran 21 tests, OK
- `python3 -m unittest tests.test_testes_tocados tests.test_governanca tests.test_aq1_texto tests.test_medidas_m14b` -> Ran 268 tests, OK (skipped=1)
- CI do PR 545: jobs `suíte (python 3.12, parte 3/3)` e `suíte (python 3.14, parte 3/3)` com falha nos runs 43512356348 (4baba3c5) e 43514511264 (5e6e245e); CI push da develop befd4cca (run 43499703356) verde.
