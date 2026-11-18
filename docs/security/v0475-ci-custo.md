---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 7c7f6c42b2fc03ebeb781c3f1067520be7d8fb33
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-custo (revalidação por delta)

Escopo: delta `8a4a9707..7c7f6c42` lido por `forge-check parecer delta` (pedido v0474, E3.150), sem o que veio da develop. No domínio: `bin/forge-testes:112` (só acrescenta `test_parecer_delta` e `test_revisar_sha` à tupla `FORGE_CHECK`; não muda execução nem entrada). Fora do domínio, lidos pelo foco do brief: `tests/test_forge.py:790-791`, `tests/test_modelo_ci.py`, `tests/mutantes/v0475-ci-custo-3.json`, `tests/test_reval_delta.py`. O modelo `templates/projeto/.github/workflows/ci.yml` não mudou no delta. Rodadas anteriores ficam no git.

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A4 (recomendado) tests/test_forge.py:791 · O lookbehind `(?<!\$)` deixa passar marcador escrito após `$` (`${{SOBRA}}`, S4); nenhum modelo tem hoje marcador assim. Fechar com `\$\{\{[A-Z_]+\}\}` como segundo padrão, se quiser.

## Sondas
- S1 · `    # {{SOBRA}}` no fim de `templates/projeto/.github/workflows/ci.yml`; `python3 -m unittest tests.test_forge.ForgeInit.test_cria_estrutura_completa` · espera: falha · obtido: FAILED, AssertionError no `.github/workflows/ci.yml` gerado (também `tests.test_modelo_ci`: 1 falha, o M30)
- S2 · `{{SOBRA}}` no fim de `templates/projeto/CLAUDE.md`; mesmo teste · espera: falha · obtido: FAILED, AssertionError no `CLAUDE.md` gerado
- S3 · `    # ${{ {{SOBRA}} }}` no fim do `ci.yml` do modelo (marcador dentro de expressão do Actions); mesmo teste · espera: falha · obtido: FAILED
- S4 · `${{SOBRA}}` no fim de `templates/projeto/CLAUDE.md`; mesmo teste · espera: falha (ideal) · obtido: OK (lacuna do A4)
- S5 · controle: head 7c7f6c42 sem mudança · espera: OK · obtido: OK (`${{ }}` legítimos do `ci.yml` passam)

## Detalhe
Foco do brief confirmado: um `{{X}}` não trocado pelo `forge-init` continua detectado em qualquer arquivo do projeto gerado (S1, S2), inclusive dentro de `${{ }}` (S3), porque o lookbehind só exclui o `{{` imediatamente após `$`. Os marcadores do `forge-init` (`bin/forge-init:163-164`: PROJETO, DESCRICAO, STACK, COMANDO_PRONTO, PRONTO_RAPIDO, DETECCAO) não aparecem após `$` em nenhum modelo (`grep -rnoE '\$\{\{' templates/` só acha expressões do Actions no `ci.yml`, linhas 21, 32, 41, 42, 85-87). A4 é recomendação: é guarda de teste, sem caminho de ataque; o risco é só de regressão silenciosa se um modelo futuro escrever `${{MARCADOR}}`. `test_modelo_ci` agora exige `${{` e a ausência de `{{` solto no `ci.yml` gerado, e o mutante M30 prova a guarda. Achados A1-A3 seguem resolvidos (o `ci.yml` não mudou).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: sondas S1-S5 em worktrees descartáveis do head; `python3 -m unittest tests.test_modelo_ci tests.test_reval_delta tests.test_ambiente_git`, `tests.test_forge.ForgeInit` e `python3 -I tests/catraca.py --base origin/develop`. Sem PR aberto, sem CI a citar: a suíte inteira fica com o CI do PR. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
