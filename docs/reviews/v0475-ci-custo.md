---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 8a4a97077c22308b0a503d4e33f72bb91700e12a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.109, melhoria/v0475-ci-custo), revalidação

## Achados
- A5 (recomendado) tests/test_modelo_ci.py:1 · tamanho (M14): 287 linhas contadas contra a base (`bin/forge-testes` 4, `ci.yml` 94, teste 189), um comportamento; o corpo do PR traz `teto: excedido, 287 linhas, <motivo>`.

## Sondas
- S1 · `GIT_DIR=/nonexistent python3 -m unittest tests.test_modelo_ci.Deteccao` · espera: OK (teste isolado do ambiente) · obtido: `OK` (antes, no d8e1b09b, `FAILED (errors=3)`)

## Parecer
Aprovado (`R-REVIEW`). Delta lido: `forge-check parecer delta docs/reviews/v0475-ci-custo.md`, intervalo d8e1b09b..8a4a9707, domínio código e testes (changelog.d, skills/ci-cd/SKILL.md, ci.yml, `tests/mutantes/v0475-ci-custo-2.json`, tests/test_modelo_ci.py).

- **A3 da segurança (renomeação esconde a origem):** a detecção usa `git diff --no-renames --name-only "$BASE...$CABECA"`; mover `src/app.py` para `docs/app.py` ou para `src/app.md` lista a origem e dá `so_documento=false`. Teste de comportamento `test_renomear_codigo_para_documento_roda_a_suite` roda o script real num repositório descartável; o mutante M21 volta ao diff sem `--no-renames` e morre. Skill e changelog explicam; M22 guarda o texto da skill.
- **A4 (recomendado) resolvido:** `ambiente_limpo()` tira `GIT_*` e `BASH_ENV` de `git()`, da detecção, do agregador e do `forge-init`, como `tests/test_adotar.py`; a sonda S1 agora passa.

Ferramentas e provas, rodadas só no diff:
- `python3 -m unittest tests.test_modelo_ci`: `Ran 19 tests ... OK` no 8a4a9707.
- `bin/forge-mutante --processos 1 tests/mutantes/v0475-ci-custo-2.json`: M17 a M22 `morreu`, rc=0.
- CI: sem PR aberto neste passo; a suíte completa fica no CI do PR, obrigatório para o merge.
