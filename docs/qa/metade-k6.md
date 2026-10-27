---
tipo: qa
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 6dda8fdf285d5c5c2387c8ac4594fe1d0299a17d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: metade-k6

K6 do pedido METADE-MINUTOS (METADE-MINUTOS-REV, E3.1): `scripts/suite-paralela.py` reaproveita a execução verde sobre a mesma árvore (hash pelo git, sem pareceres e changelog) e a frase nova de `R-QA`. Parecer em paralelo com review e segurança (ACELERA-RODADA "A", item 4); revalidação 2 (volta do K6) sobre o head `6dda8fd`, escopo completo: hash sem só os pareceres, carimbo só com o hash igual no fim, recusa de skip-worktree e assume-unchanged, CI fora do ambiente do teste.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Verde grava o carimbo e a 2ª chamada reusa sem rodar | `test_suite_paralela.test_verde_grava_carimbo_e_a_segunda_chamada_reusa_sem_rodar`, M9 | carimbo ausente | passou, M9 morreu |
| Vermelho não grava carimbo | `test_vermelho_nao_grava_carimbo`, M10 | suíte vermelha | passou, M10 morreu |
| Só `*.md` de parecer e changelog saem do hash; `_modelo`, README e subpasta entram (A1 da segurança) | `test_suite_reuso` (M1, M2, M12) | `_modelo.md`, README, subpasta | passou, mortos |
| Skip-worktree e assume-unchanged não dão hash (A3) | `test_skip_worktree_e_assume_unchanged_nao_dao_hash`, M13 | `ls-files -v` minúscula e `S` | passou, M13 morreu |
| Commit no meio da suíte não grava carimbo (A2) | `test_commit_no_meio_da_suite_nao_grava_carimbo`, M14 | hash do fim ≠ do começo | passou, M14 morreu |
| CI fora do ambiente do teste (A1 do review) | `Brinquedo.setUp` e `AMBIENTE`; as duas suítes com e sem `CI=true` | variável `CI` herdada | passou nos dois modos |
| Árvore suja ou não rastreada, hash, Python, carimbo ilegível, SEM_REUSO, CI e pre-push intocado | `test_suite_reuso`, M3 a M8, M11 | cada guarda | passou, mortos |
| Frase de `R-QA` e fragmento de changelog | leitura do diff | n/a | conforme (cita a decisão de 2026-10-27, K6) |

## Cenários e resultado real
- `python3 -m unittest tests.test_suite_reuso tests.test_suite_paralela`: sem `CI`, Ran 37 tests, OK (12,4 s); com `CI=true`, Ran 37 tests, OK (12,8 s).
- `bin/forge-mutante tests/mutantes/metade-k6.json`: M1 a M8 morreram, rc=0. `bin/forge-mutante tests/mutantes/metade-k6-2.json`: M9 a M14 morreram, rc=0. Conferência da lista contra o diff: FORA_DO_HASH (M2), `fora_do_hash` (M1, M12), árvore suja e erro do git (M3), skip-worktree e assume-unchanged (M13), hash, Python, carimbo ilegível, SEM_REUSO, CI (M4 a M8), gravar só no verde (M9, M10), carimbo só com o hash igual no fim (M14), reuso antes da trava (M11); nenhuma linha de guarda sem mutante.
- À mão, num clone descartável do head (carimbo gravado pelo próprio script sobre a árvore limpa; as chamadas usam `timeout 6` meu): 1ª chamada `suite: reusa 331ac651... de 2026-10-27 15:32:13Z` e `OK`, rc=0, **0,207 s** (a 2ª chamada, que é a medida pedida; a suíte completa leva minutos). Parecer mudado (`docs/qa/metade-k6.md`, commitado): reusa, rc=0. `docs/security/_modelo.md` mudado e commitado: não reusa, entrou na fila do pre-push ("esperando a vez", rc=124 pelo meu `timeout`). Volta ao commit anterior: reusa de novo. Skip-worktree em `scripts/suite-paralela.py` com arquivo editado: não reusa (fila). Assume-unchanged em `bin/forge-init` com arquivo editado: não reusa (fila). Nenhum processo meu ficou vivo.
- Vermelho antes do verde: os mutantes M1 a M14 derrubam cada teste novo e valem como a prova do comportamento; `forge-testes --vermelho` não rodado (a suíte completa fica no pre-push, restrição do pedido).

## Observações (não bloqueiam)
- O carimbo é um só por repositório (`.git` comum): reusa entre worktrees da mesma árvore, a intenção do K6. Arquivo ignorado pelo git (`.gitignore`) não entra no hash nem no status; uma mudança só nele reusaria. Risco baixo, aceito pela decisão K6.
