---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 8a4a97077c22308b0a503d4e33f72bb91700e12a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-custo (revalidação por delta)

Escopo: delta `d8e1b09b..8a4a9707` lido por `forge-check parecer delta` (pedido v0474, E3.110). No domínio: `templates/projeto/.github/workflows/ci.yml` (linha 45) e `skills/ci-cd/SKILL.md` (linha 58). Fora do domínio: `tests/test_modelo_ci.py`, `tests/mutantes/v0475-ci-custo-2.json`, `changelog.d/`. As rodadas anteriores (f59f7766, d8e1b09b) ficam no git.

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A1 (recomendado) templates/projeto/.github/workflows/ci.yml:75 · Resolvido no d8e1b09b (estado mantido): um workflow só e um único check `ci`.
- A2 (recomendado) templates/projeto/.github/workflows/ci.yml:21 · Resolvido no d8e1b09b (estado mantido): grupo de concorrência por número do PR ou ref.
- A3 (recomendado) templates/projeto/.github/workflows/ci.yml:45 · Resolvido no 8a4a9707: `git diff --no-renames --name-only`; a renomeação lista origem e destino, e mover código para `docs/` ou para `*.md` não pula mais a suíte (S1, S2).

## Sondas
- S1 · repositório com `src/app.py`; commit `git mv src/app.py docs/app.py`; trecho `run:` do job `mudanca` extraído do head 8a4a9707, com BASE/CABECA dos dois commits · espera: so_documento=false · obtido: so_documento=false (git 2.43.0; o diff lista `docs/app.py src/app.py`)
- S2 · idem com `git mv src/app.py src/app.md` · espera: so_documento=false · obtido: so_documento=false (o diff lista `src/app.md src/app.py`)
- S4 · controle: só `README.md` alterado · espera: so_documento=true · obtido: so_documento=true (a correção não quebra o caso legítimo)

## Detalhe
A3 fechado: `--no-renames` na linha de comando vence `diff.renames` de configuração, então nem a configuração do runner nem a do repositório reabrem o caminho. A skill (`SKILL.md:58`) descreve a flag e o motivo. O teste `test_renomear_codigo_para_documento_roda_a_suite` executa S1 e S2 como caso de abuso e `test_deteccao_usa_no_renames` prende a flag. Nada mais mudou no `run:`: dados do evento seguem por `env:`, nomes de arquivo só passam por `case`, ao `$GITHUB_OUTPUT` vai só o literal.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -m unittest tests.test_modelo_ci`, 19 testes, OK; sondas S1, S2 e S4 rodadas localmente sobre o trecho extraído do head. Sem PR aberto, sem CI a citar: a suíte inteira fica com o CI do PR. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
