---
tipo: revisao-devops
contrato: 1
pedido: v047-reverte-576
branch: melhoria/v047-reverte-576
commit: 988ca87aa95f0b9dea54bdb442f0ee5b5b7f0e0f
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: v047-reverte-576

## Achados

## Detalhes
Aprovado. O head 988ca87a reverte o #576 (22f1eaa8, suíte em 5 partes). Conferido: `.github/`, `scripts/suite-partes.py` e `tests/test_catraca.py` ficam byte a byte iguais ao estado anterior ao #576 (`git diff --quiet 22f1eaa8~1 HEAD -- .github scripts/suite-partes.py tests/test_catraca.py` rc=0). Os 28 arquivos tocados pelo #576 voltam ao estado anterior, exceto `docs/engineering/achados-recorrentes.md`, que só difere pelos contadores de commits posteriores (sem relação com o CI). O `ci.yml` volta a casar com a catraca de workflows. Sem workflow novo, sem `continue-on-error`, sem escrita na `main` (`R-MAIN`, `R-VERIFY`).

Ferramentas: `shellcheck` presente; `actionlint` ausente do PATH (lacuna registrada; o `ci.yml` é idêntico ao já validado antes do #576). Teste da catraca: ver Provas do relatório.

## Custo e rollback
Menos jobs que no #576, sem custo novo (`R-CUSTO`). Rollback: reverter este revert (`git revert 988ca87a`).
