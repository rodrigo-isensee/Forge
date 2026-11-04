---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: 3984d0b2721058d8d1d525c12466da2102ecfead
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (ci-env-argv0-v2)

## Achados
- A1 (recomendado) .github/workflows/ci.yml:23 · O job rapida (push na develop) roda a suíte sem o passo env com -a e segue com o env do runner; a prova viva de 20 formas cai ali. Duplicar o passo ou extrair ação local.
- A2 (recomendado) .github/workflows/ci.yml:55 · O corpo do passo está copiado nos dois jobs da bateria (19 linhas); mudar um e esquecer o outro diverge. Extrair para scripts/ ou ação composta.

## Parecer
Aprovado. Lido o diff inteiro (39 linhas em ci.yml, abaixo do teto M14, uma classe de comportamento). Passo seguro: pacote do apt do runner (assinado pelo apt, sem download avulso nem checksum a verificar, sem ação de terceiros), sem entrada não confiável em run:, permissions inalteradas. Fica no lugar certo, antes da suíte e sob o mesmo if do gate na bateria. Falha fechado (set -euo pipefail, conferência de which, -a e env X=1). Pinagem de versão do rust-coreutils não é necessária com runner fixado em ubuntu-24.04 (parecer de devops). Não quebra o job rapida, que não foi alterado. Teste: test_ci_local, rc=0. Segurança: CI é gatilho de R-SEGURANCA, mas o parecer de devops não cobre segurança; peça ao security-engineer parecer curto (instalação de pacote com sudo no runner, sem segredo).
