---
tipo: review
contrato: 1
pedido: CI-PY314
branch: melhoria/ci-py314
commit: a7d88f262ab43040f9070bee90e307e8b586d9ef
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: CI-PY314

## Achados
- A1 (recomendado) .github/workflows/ci.yml:37 · o job 3.14 roda tudo também em commit só de parecer (a bateria pula pelo gate); custo extra pequeno, reavaliar se pesar.

## Parecer
Aprovado. Diff lido: `ci.yml` (job novo `bateria-python-tres-quatorze`), `changelog.d/ci-py314.md`, `docs/devops/ci-py314.md`. Run 39979644068: success (`bateria (python 3.14)`, `bateria` success; `checagem rápida` skipped, como esperado em PR).

- Escopo por versão do Python: o job roda `scripts/suite-paralela.py` e `tests/e2e-instalacao.sh` (usa `python3 -c` e `bin/forge-init`), com Node e Claude Code CLI na mesma versão fixada que o e2e exige. Os demais passos Python da `bateria` (`forge-changelog conferir`, `conferir-release.py`, `catraca.py --modo pareceres`) ficaram fora; a justificativa é válida: `tests/test_conferir_release.py` trava um passo só de cada no `ci.yml` e a suíte cobre a lógica deles no 3.14. shellcheck, actionlint, zizmor, `claude plugin validate` e a varredura de segredos não executam Python. Conclusão: o que depende da versão do Python está coberto.
- Nomes dos checks exigidos intactos: `bateria`, `checagem rápida (push na develop)` e `catraca` não mudaram; o novo se chama `bateria (python 3.14)`.
- Ações fixadas por sha, os mesmos dos jobs atuais (checkout, setup-python, setup-node), com comentário de versão; `persist-credentials: false`; `permissions` herda `contents: read`; `timeout-minutes: 15`; mesma condição de gatilho da `bateria`.
- `R-CUSTO`: runner gratuito em repositório público. Tornar o check obrigatório é ação do dono, fora do pedido.
- Pendência herdada do parecer de devops: `actionlint` e `zizmor` não rodaram localmente; rodam na `bateria` do CI (verde).
- Documentação e changelog: fragmento presente; sem outra doc afetada.
