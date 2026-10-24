---
tipo: revisao-devops
contrato: 1
pedido: CI-PY314
branch: melhoria/ci-py314
commit: 491a55acfd36eeab73bdc0ecc173a4396cd42b09
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
- Escopo do job (critério: o passo executa Python do Forge, logo depende da versão). Entraram: `tests/e2e-instalacao.sh` (`python3 -c` na linha 27 e `bin/forge-init`, que roda `python3` em três pontos), com o setup do runtime do CLI e a instalação do Claude Code CLI que ele exige (mesma versão fixada da `bateria`). Ficaram fora: `bin/forge-changelog conferir`, `scripts/conferir-release.py` e `tests/catraca.py --modo pareceres` (executam Python, mas `tests/test_conferir_release.py` trava um passo só de release no `ci.yml`, então duplicar quebra a suíte; a lógica deles tem testes na suíte, que roda no 3.14), `claude plugin validate` (CLI do Claude Code, não Python), shellcheck, actionlint, zizmor e o download delas (binários), "Nada pula degrau" e a varredura de segredos (`verificar-contribuicao.sh`, shell puro; sem Python), "Testes que leem pareceres" (subconjunto da suíte, que já roda inteira). Sem o gate de commit só de parecer: o job roda tudo sempre (mais simples; reavaliar se o custo pesar).
- Recomendado (não bloqueia): tornar o check novo obrigatório é ação do dono (`R-CONFORMIDADE`).
Ferramentas: `actionlint` e `zizmor` ausentes do PATH local (lacuna; ambos rodam na `bateria` do CI sobre este arquivo). `shellcheck` não se aplica.

## Custo e rollback
`R-CUSTO`: runner ubuntu-24.04 gratuito, repositório público; um job a mais em paralelo, sem cache nem artefato. Rollback: reverter o commit (remove o job).
