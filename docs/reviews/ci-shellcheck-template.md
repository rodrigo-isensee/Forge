---
tipo: review
contrato: 1
pedido: ci-shellcheck-template
branch: melhoria/ci-shellcheck-template
commit: 10b192c
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

## Review independente

Revisor: `forge:tech-lead`, sobre o HEAD `10b192c` (diff contra `origin/develop`). Parecer: **aprovado**.

- Job `shellcheck`: a única mudança no `ci.yml` é a lista, com `scripts/validar-plugin.sh` e `scripts/configurar-ambiente-local.sh` acrescentados; o restante do job não mudou.
- `shellcheck` nos dois scripts: saída 0, sem achados.
- Modelo de PR: as seções `Projeto de origem` e `Como medir` coincidem com as que `violacoes_do_texto` exige (`tests/catraca.py`, modo `pr-texto`), e os comentários indicam o mínimo de caracteres. Só os comentários mudaram.
- Sem alteração em scripts, hooks nem `tests/catraca.py`. Mexe em `.github/` (protegido): precisa do rótulo `afrouxa-regra` do dono.
- Achados: nenhum que bloqueie.
