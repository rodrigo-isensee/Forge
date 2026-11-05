---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/release-suite-paralela
commit: 6652f6b1898c91866a18e128ddbd1927c76b0277
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: release-suite-paralela (E24, versao-033)

Escopo: diff `f54d9b7...6652f6b`, em `.github/workflows/release.yml`, `tests/test_ci_local.py` e `changelog.d/release-suite-paralela.md`. Gatilho: CI/CD (`R-SEGURANCA`).

## Gatilhos
CI/CD: o workflow Release muda o passo de testes que roda antes da publicação.

## Achados

## Detalhe dos achados
Sem achado. Conferido item a item:
- Permissões: `contents: write` segue no nível do workflow, sem mudança no diff; é o que o `gh release create` exige. Nenhum escopo novo.
- Gatilho: continua `push` em `main` (só muda pelo PR do usuário); sem `pull_request_target` nem entrada de fork.
- Ação nova: `actions/setup-python` fixada por SHA `6d4fd22b...` (v7.1.0), idêntico ao de `ci.yml` (linhas 32, 52 e 121); `actions/checkout` mantido por SHA.
- Segredos: o `GH_TOKEN` continua só no passo "Tag e release"; o passo de testes não o recebe e o checkout mantém `persist-credentials: false`. `scripts/suite-paralela.py` só usa biblioteca padrão e não abre rede.
- Ordem: os testes rodam antes de tag e release; falha da suíte interrompe a publicação. O passo é o mesmo comando do `ci.yml`, sobre código já revisado e mesclado.
- Teto de 25 min: limita o custo de um job travado; nada pago (`R-CUSTO`).
- Teste: `tests/test_ci_local.py` ganha a guarda positiva (`suite-paralela.py`) e a negativa (sem `unittest discover`) sobre o `release.yml`, sem afrouxar nada. `python3 -m unittest tests.test_ci_local`: 52 testes, OK.
- Recomendação não bloqueante: nenhuma. Os `permissions` poderiam ser por job, mas há um job só.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `zizmor`, `actionlint` e `gitleaks` não estavam no PATH (lacuna registrada; rodam no CI do projeto).
