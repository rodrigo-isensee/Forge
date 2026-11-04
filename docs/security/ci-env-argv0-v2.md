---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: 3984d0b2721058d8d1d525c12466da2102ecfead
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: ci-env-argv0-v2

## Gatilhos
R-SEGURANCA: CI (.github/workflows/ci.yml, dois passos novos com sudo e instalação de pacote); controles do Forge não tocados.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:55 · apt sem versão fixa e o PATH do job inteiro passa a usar o env do uutils; sem caminho realista de ataque, só deriva de ambiente

## Detalhe dos achados
A1: o pacote rust-coreutils vem do universe do runner, sem versão fixa (cadeia de suprimentos: um pacote comprometido executaria no job). O job tem permissions contents: read, persist-credentials false e gatilho pull_request, sem segredo. Impacto baixo; mitigação opcional é fixar a versão com apt. Esforço P, dono devops-engineer. O passo falha fechado (set -euo pipefail, confere o caminho do env e o `-a`). Os dois passos são idênticos; o segundo só roda com a bateria pesada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática do diff; zizmor, actionlint e gitleaks não rodados aqui (o CI os roda).
