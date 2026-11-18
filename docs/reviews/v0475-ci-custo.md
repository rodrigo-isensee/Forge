---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 7c7f6c42b2fc03ebeb781c3f1067520be7d8fb33
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.149, melhoria/v0475-ci-custo), revalidação

## Achados
- A5 (recomendado) tests/test_modelo_ci.py:1 · tamanho (M14): 299 linhas contadas contra a base (`bin/forge-testes` 4, `ci.yml` 94, `tests/test_modelo_ci.py` 196, `tests/test_forge.py` 3, `tests/test_reval_delta.py` 2), um comportamento; o corpo do PR traz `teto: excedido, 299 linhas, <motivo>`.

## Sondas
- S1 · `GIT_DIR=/nonexistent python3 -m unittest tests.test_modelo_ci.Deteccao` · espera: OK (teste isolado do ambiente) · obtido: `OK` (antes, no d8e1b09b, `FAILED (errors=3)`)

## Parecer
Aprovado (`R-REVIEW`). Delta lido: `forge-check parecer delta docs/reviews/v0475-ci-custo.md`, intervalo 8a4a9707..7c7f6c42, domínio código e testes (`tests/test_forge.py`, `tests/test_modelo_ci.py`, `tests/test_reval_delta.py`, `tests/mutantes/v0475-ci-custo-3.json`; a linha de `bin/forge-testes` no delta veio da `develop` pelo merge 96aa5f39, #646, fora do item).

- **Marcador `${{ }}` (CI do PR #651):** `test_forge.ForgeInit` e `test_modelo_ci.Entrega` trocam `assertNotIn("{{")` por `(?<!\$)\{\{`: a expressão do Actions fica, e marcador do modelo sem `$` reprova. O teste do modelo também afirma a presença de `${{`, então o regex não passa no vazio. M30 (`# {{SOBRA}}` no `ci.yml`) morreu.
- **`ambiente_limpo` com `sem_manutencao`:** usa o ajudante comum `tests/ambiente_git.py`, como os outros testes que rodam git em subprocesso.
- **`tests/test_reval_delta.py`:** a citação de `tests/test_modelo_ci.py` no README entra em `_NOME` com a contagem 4.
- Revisões anteriores (A3 da segurança, A4) seguem resolvidas; o delta não toca a detecção.

Ferramentas e provas, rodadas só no diff, no 7c7f6c42:
- `python3 -I tests/catraca.py --base origin/develop`: rc=0.
- `python3 -m unittest tests.test_modelo_ci tests.test_reval_delta tests.test_ambiente_git`: `Ran 49 tests ... OK`.
- `python3 -m unittest tests.test_forge.ForgeInit`: `Ran 11 tests ... OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v0475-ci-custo-3.json`: `M30 · morreu`, rc=0.
- CI: a suíte completa fica no CI do PR #651, obrigatório para o merge.
