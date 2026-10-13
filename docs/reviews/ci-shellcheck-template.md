---
tipo: review
contrato: 1
pedido: ci-shellcheck-template
branch: melhoria/ci-shellcheck-template
commit: c5ff6a0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: ci-shellcheck-template

Escopo: lista do job `shellcheck` em `.github/workflows/ci.yml` (+2 scripts), comentários do `.github/pull_request_template.md` e linha no CHANGELOG.

- `shellcheck` nos dois scripts novos: sem achados, nada a corrigir.
- O modelo já tinha os nomes exatos exigidos pela catraca (`Projeto de origem`, `Como medir`); os comentários agora dizem que são obrigatórias e o mínimo de 20 caracteres. `Situação observada` e `O que muda` ficam: não são lidas pela catraca, mas orientam o review e não são redundantes.
- Nenhuma alteração em `tests/catraca.py` nem em hooks.
- Afrouxa regra? Mexe em `.github/`, protegido: exige o rótulo `afrouxa-regra` do dono.
