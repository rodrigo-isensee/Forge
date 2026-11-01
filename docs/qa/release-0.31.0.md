---
tipo: qa
contrato: 1
pedido: release-0.31.0
branch: melhoria/release-0.31.0
commit: 0e67326671c6c1e9b42785920d44e5a7b6300dde
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: release-0.31.0

Código testado: 0e67326 (24 commits da develop, 91d6cc1, mais o commit de release). O HEAD da branch (92c68c6) difere só por pareceres. Escopo: `git diff 6f8e238...0e67326`, 162 arquivos, sem especificação de UX; vale o critério de integração (`R-QA`). Cada PR da leva tem QA próprio; aqui se revalida o conjunto.

## Achados
- A1 (recomendado) tests/test_hooks_volta_propriedades.py:186 · o teste do vigia (prazo de 10 s) falhou com 11,6 s numa suíte com load 6 a 7 (mutantes em paralelo) e passou isolado (8 testes OK, 70 s); sensível a carga, sem defeito provado no hook.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira sobre a leva | `python3 -m unittest discover -s tests` | n/a | 2390 testes, 27 skipped (skips do próprio repositório), 1 falha (A1); a falha passou isolada, ver abaixo |
| A falha isolada | `python3 -m unittest tests.test_hooks_volta_propriedades` | prazo de 10 s do Claude Code | 8 testes, OK |
| Mutantes declarados da leva | `bin/forge-mutante tests/mutantes/<spec>.json`, uma spec por vez (as specs são de pedidos diferentes e a rodada conjunta sai 2) | uma guarda mudada por mutante | 11 specs (heredoc-rapido, heredoc-rapido-p2, impl-fechar-c-c1, c4, impl-forge-check-a, impl-furo-hook-a, a2, a3, a3-2, a4, a5): todas rc 0, nenhum sobrevivente |
| Release coerente | `python3 scripts/conferir-release.py --base origin/main` | versão e fragmentos | `ok: changelog.d/ sem fragmentos pendentes`; base 0.30.8, release 0.31.0 |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` |
| Docs | `bin/forge-check docs` | formato dos pareceres | rc 0 |
| Escopo P-CORTE-031 = A | `git diff --name-only` | item da 0.32 no diff | nenhum item da 0.32 |

## Cenários e resultado real
- Vermelho antes do verde: cada PR registrou o seu `forge-testes --vermelho` no QA próprio; não refeito no conjunto.
- Falha de suíte e carga: a falha única é de tempo sob carga e passou isolada (sem skip, sem marcação).
- Infra: a leva não toca `.github/`, `Dockerfile`, compose nem IaC (`git diff --name-only` filtrado, vazio); a suposição do pedido sobre devops confere. Toca `scripts/suite-paralela.py` (IMPL-N-CI, com parecer de devops próprio).
- Bugs novos: nenhum; `docs/qa/bugs/` não ganha arquivo.
- Recomendações abertas dos PRs e do review (docs/hooks.md, CONTRIBUTING.md, GIT_CONFIG_COUNT e `--config-env` no merge): texto ou cartão já rastreado, sem defeito provado nesta leva.
