---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-fixtures-gerada
commit: de272439995c2476b465f8978cc9430d9c4e2a78
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 HOOKS-FIXTURES-GERADA (E18.1, #908)

Diff lido contra a base cfd83b72 (merge-base com a develop): `docs/hooks-fixtures.md`, `scripts/indice-fixtures.py`, `tests/test_indice_fixtures.py`, `tests/mutantes/v0481-fixtures-gerada.json`, fragmento de changelog.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Arquivo sem contagem, uma linha por prefixo, ordem alfabética | `test_lista_todo_hook_e_prefixo_do_corpus_sem_contagem`, `test_caso_novo_em_prefixo_existente_nao_muda_o_arquivo` | pelo menos 10 hooks (guarda de suíte vazia); ordem alfabética contra ordem por tamanho; sem `\d+ fixtures` | passou |
| Dois PRs paralelos se juntam sem conflito | `test_dois_prs_com_fixtures_diferentes_se_juntam_sem_conflito` (git real, prefixo existente, prefixo novo e hook novo) | junção limpa e `--conferir` em dia | passou |
| Detalhe só no `--detalhe`, imprime e não grava | `test_detalhe_imprime_sem_gravar`, `test_grupos_contagens_regras_e_celula_segura`, `test_exemplo_sem_termo_de_stack` | arquivo não criado; opções juntas recusadas (rc 2) | passou |
| `--conferir` e teste em dia iguais | `test_indice_esta_em_dia_com_o_corpus`, `test_conferir_da_rc_0_em_dia`, `test_main_grava_confere_e_recusa_opcao` | texto único de `gerar()` | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_indice_fixtures`: 10 testes, OK. `scripts/indice-fixtures.py --conferir`: em dia. `--detalhe` imprime 3603 fixtures e deixa a árvore limpa.
- Vermelho antes do verde (`bin/forge-testes --vermelho cfd83b72e25b4a3b0c8d94aafde6d5d2fc28dc82 --modulos tests.test_indice_fixtures`):
  `vermelho: base=cfd83b72e25b head=de272439995c módulos=test_indice_fixtures (restrito por --modulos)`; contagem: prova (asserção)=4; prova (API ausente)=2; não prova (passa na base)=4. Os 4 que passam na base são testes herdados que guardam comportamento mantido; os 6 do diff provam.
- Mutante: `bin/forge-mutante tests/mutantes/v0481-fixtures-gerada.json` → `M1 · morreu · scripts/indice-fixtures.py:119`. Cobertura: `bin/forge-mutante --cobertura --base cfd83b72e25b4a3b0c8d94aafde6d5d2fc28dc82` → `coberta · scripts/indice-fixtures.py:119 · ...:M1`; única condição mudada no diff, sem linha de guarda sem mutante.
- Limite declarado confirmado: prefixos novos vizinhos ainda conflitam numa linha (aceito pelo pedido).
- Acessibilidade e E2E: n/a (script e documento).
- CI do PR #908 no head de272439: ainda em fila no momento da leitura (`suíte` 3.12 e 3.14 e `catraca` pending; `bateria (pareceres)` fail, que espera este parecer; `instalação`, `bateria (passos)`, `bateria (verificações longas)` pass). A linha `- ci:` não foi gravada por falta de verde; precisa de segunda leitura do `gh pr checks` quando a suíte concluir.
