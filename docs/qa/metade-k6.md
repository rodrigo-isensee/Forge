---
tipo: qa
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 053f4162e17079a796ee77ef71e5d0b80bf3b261
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: metade-k6

K6 do pedido METADE-MINUTOS (METADE-MINUTOS-REV, E3.1): `scripts/suite-paralela.py` reaproveita a execução verde sobre a mesma árvore (hash pelo git, sem pareceres e changelog) e a frase nova de `R-QA`. Parecer em paralelo com review e segurança (ACELERA-RODADA "A", item 4); head testado `053f416`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Verde grava o carimbo e a 2ª chamada reusa sem rodar | `test_suite_paralela.test_verde_grava_carimbo_e_a_segunda_chamada_reusa_sem_rodar`, M9 | carimbo ausente | passou, M9 morreu |
| Vermelho não grava carimbo | `test_vermelho_nao_grava_carimbo`, M10 | suíte vermelha | passou, M10 morreu |
| Parecer e changelog fora do hash; `bin/` dentro | `test_suite_reuso` (M1, M2) | prefixos de `FORA_DO_HASH` | passou, M1 e M2 morreram |
| Árvore suja ou arquivo novo não rastreado roda | `test_arvore_suja_roda`, `test_arquivo_novo_nao_versionado_roda` (M3) | status não vazio | passou, M3 morreu |
| Hash, Python ou carimbo ilegível diferentes rodam | M4, M5, M6 | carimbo corrompido | passou, mortos |
| `FORGE_SUITE_SEM_REUSO=1` e `CI` forçam a execução | M7, M8 | variáveis de ambiente | passou, mortos |
| Reuso só à mão, antes da trava e da fila (pre-push intocado) | M11 | `FORGE_SUITE_TRAVA` definida | passou, M11 morreu |
| Frase de `R-QA` e fragmento de changelog | leitura do diff | n/a | conforme (a regra cita a decisão de 2026-10-27, K6) |

## Cenários e resultado real
- `python3 -m unittest tests.test_suite_reuso`: Ran 12 tests, OK (0,66 s).
- `python3 -m unittest tests.test_suite_paralela`: Ran 22 tests, OK (11,5 s).
- `bin/forge-mutante tests/mutantes/metade-k6.json`: rc=0, M1 a M8 morreram. `bin/forge-mutante tests/mutantes/metade-k6-2.json`: rc=0, M9 a M11 morreram. Conferência da lista contra o diff: cada guarda nova de `suite-paralela.py` (FORA_DO_HASH e seu uso, árvore suja, hash, Python, carimbo ilegível, SEM_REUSO, CI, gravar só no verde, reuso antes da trava) tem um mutante; nenhuma linha de guarda sem mutante.
- Reprodução à mão no worktree: 1ª chamada (`python3 scripts/suite-paralela.py`) já imprimiu `suite: reusa 464a48a5...fa17c6 de 2026-10-27 14:23:12Z` e `OK`, porque o carimbo do push do autor (mesma árvore, comum a todos os worktrees) existia. A 2ª chamada também reusou: **0,091 s** (contra a suíte completa de minutos).
- Árvore suja, medida chamando `reuso()` do script (a execução real entraria na suíte completa, que não rodo fora do pre-push): arquivo novo não rastreado, `bin/forge-init` mudado, `CI=1` e `FORGE_SUITE_SEM_REUSO=1` dão `None` (rodariam); árvore limpa de volta dá o mesmo hash. `CI=1` na linha de comando foi para o pre-push e entrou na fila ("outra suíte ... esperando a vez"), isto é, não reusou; interrompi pelo `timeout` que iniciei, sem processo órfão.
- Vermelho antes do verde: coberto pelos mutantes M1 a M11 (cada teste cai com o mutante), que valem como o vermelho do comportamento novo; `forge-testes --vermelho` não rodado (a suíte completa fica no pre-push, restrição do pedido).

## Observações (não bloqueiam)
- O carimbo é um só por repositório (`.git` comum): reusa entre worktrees da mesma árvore, o que é a intenção; arquivo ignorado pelo git (`.gitignore`) não entra no hash nem no status, então uma mudança só nele reusaria. Risco baixo, aceito pela decisão K6.
