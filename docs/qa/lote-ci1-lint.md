---
tipo: qa
contrato: 1
pedido: lote-ci1-lint
branch: melhoria/lote-ci1-lint
commit: b59891dd4b621fc6f5b0bdce44a192d1c5ed33a6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-ci1-lint

Pedido LOTE-CI1-LINT (E1: CI-ORDEM-LINT), revalidado em LOTE-CI1-LINT-REV (E3.1). Base `3c66b88`, head `b59891d`. Diff: `.github/workflows/ci.yml` (os três passos de baixar, actionlint e zizmor sobem para antes de todo passo que executa código da branch), `tests/test_ci_local.py` (teste novo) e `changelog.d/lote-ci1-lint.md`.

## Achados

- A1 (recomendado) tests/test_ci_local.py:176 · a lista `executam_codigo` é fechada por nome: um passo novo que execute código da branch e entre antes do zizmor não derruba o teste; a ordem de hoje está correta.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (lint e ferramentas antes da suíte da branch) | `LeituraDosWorkflowsTest.test_bateria_lint_e_ferramentas_antes_de_qualquer_codigo_da_branch` | ordem baixar < actionlint < zizmor < todo passo listado que executa código da branch; passo ausente ou duplicado derruba (`(i,) =`) | passou no head; falha na base |
| PQ-1 (pre-push verde) | pre-push do envio | n/a | a cargo do push |

## Cenários e resultado real
- `python3 -m unittest tests.test_ci_local` no head: 52 testes, OK.
- Vermelho: `bin/forge-testes --vermelho 3c66b88 --modulos test_ci_local --prazo 150`, saída:
  `vermelho: base=3c66b881af31 head=b59891dd4b62 módulos=test_ci_local (restrito por --modulos)`; `revertidos à base: .github/workflows/ci.yml, changelog.d/lote-ci1-lint.md`; `test_bateria_lint_e_ferramentas_antes_de_qualquer_codigo_da_branch · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=51; prova (asserção)=1`; rc=0.
- Mutação à mão (cópia em `$TMPDIR`): mover o passo "Testes do Forge" para antes do actionlint faz o teste cair com `8 not less than 6 : Testes do Forge`. Mutante morto.
- Leitura do ci.yml (job `bateria`), ordem real: checkout (ação) → gate (só `git` e `gh`, sem código da branch) → "Testes que leem pareceres" (só com `pesada != true`, caminho em que lint e demais passos pesados não rodam) → setup-python → setup-node (ações) → baixa actionlint e zizmor com checksum (linha 127) → actionlint (142) → zizmor (145) → Claude Code CLI (148) → `claude plugin validate` → changelog.d → release → Nada pula degrau → Segredo/.env → Parecer de review → Provas cmd → Testes do Forge → shellcheck → Instala o Forge. Nenhum passo que executa código da branch antecede o zizmor no caminho pesado. Os passos movidos são idênticos aos removidos (diff sem mudança de conteúdo).
- Fora do escopo: a suíte completa roda no pre-push e no CI, não aqui.
