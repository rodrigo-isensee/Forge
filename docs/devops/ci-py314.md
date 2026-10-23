---
tipo: revisao-devops
contrato: 1
pedido: CI-PY314
branch: melhoria/ci-py314
commit: 0d971dae4013452272f307dce7449426a450aec4
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-23
---
# Review de devops: CI-PY314

## Parecer
Aprovado. `.github/workflows/ci.yml`: job novo `bateria-python-tres-quatorze` (nome `bateria (python 3.14)`), ao lado do 3.12.
- Nomes exigidos intactos: `bateria`, `checagem rápida (push na develop)` e `catraca` não mudaram.
- Mesma condição de gatilho da `bateria` (PR, push na homolog e na main; não no push da develop).
- Ações fixadas pelos mesmos SHAs dos jobs atuais; `persist-credentials: false`; `permissions` herda `contents: read` do topo; `timeout-minutes: 15`; `concurrency` do workflow vale para o job.
- Escopo do job: só `python3 scripts/suite-paralela.py` no 3.14 (a parte que depende da versão). shellcheck, actionlint, zizmor, validação do plugin, e2e e gates de PR ficam na `bateria` (não dependem de Python; evita duplicar minutos). Sem o gate de commit só de parecer: o job roda a suíte inteira sempre (mais simples; recomendado reavaliar se o custo pesar).
- Recomendado (não bloqueia): tornar o check novo obrigatório é ação do dono (`R-CONFORMIDADE`).
Ferramentas: `actionlint` e `zizmor` ausentes do PATH local (lacuna; ambos rodam na `bateria` do CI sobre este arquivo). `shellcheck` não se aplica.

## Custo e rollback
`R-CUSTO`: runner ubuntu-24.04 gratuito, repositório público; um job a mais em paralelo, sem cache nem artefato. Rollback: reverter o commit (remove o job).
