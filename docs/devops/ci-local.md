---
tipo: revisao-devops
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 1d7266d7885a54699158d2890adb06fc48996860
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-14
---
# Review de devops: ci-local

Parecer de autor (o devops escreveu o script); exige review independente do tech-lead (`R-REVIEW`).

## Parecer
Aprovado, com as lacunas abaixo. `scripts/ci-local <PR> [--publicar]` lê os `run:` de `ci.yml` e `catraca.yml` do PR, roda numa worktree temporária no sha da cabeça, com `env` do passo e `RUNNER_TEMP` próprio por job. Nenhuma lógica do CI foi copiada. Só biblioteca padrão.

Execução real sobre o PR #121 (develop -> homolog), sem `--publicar`: testes estruturais OK (556), shellcheck OK, validação do plugin OK, instalação ponta a ponta OK, fluxo de promoção OK, segredos OK, pareceres OK, catraca FALHOU (legítimo: `bin/forge-check` mudou e falta o rótulo `afrouxa-regra` do dono, igual ao CI real), `workflows` PULADO (sem actionlint/zizmor), `versão e changelog` e `pr-texto` PULADOS (`if` não se aplica a base homolog). Bug achado e corrigido na execução: jobs `pareceres` e `catraca` criavam o mesmo `$RUNNER_TEMP/base`; agora cada job tem subpasta (teste de regressão).

Ferramentas: shellcheck sem achado novo (o script é Python; não há shell tocado); actionlint e zizmor ausentes no PATH.

## O que fica de fora
- Job `workflows` (actionlint, zizmor): o CI os baixa; local só rodam se instalados, e o job é não obrigatório.
- Merge-base no lugar do primeiro pai do merge commit do GitHub: a base dos jobs de diff pode diferir quando a base avançou depois do PR.
- `if:` e expressões só no subconjunto `github.*`, literais, ==, !=, &&, ||; fora dele o job falha (não passa em silêncio).
- Passos de preparo (`npm install`, `curl`, `wget`) são ignorados; vale o que há no PATH. Ferramenta ausente em job obrigatório vira `failure`.
- O status `ci-local` é auto-declarado: quem o publica pode publicar `success`. Torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`).

## Segurança (gatilho `R-SEGURANCA` para o security-engineer)
O script executa localmente os `run:` dos workflows do PR: código do PR roda na máquina de quem roda, com o `gh auth token` exportado como `GITHUB_TOKEN` e o ambiente do usuário (sem as variáveis `GIT_*`). Risco: PR de terceiro malicioso pode exfiltrar o token ou o ambiente. Mitigações atuais: só PRs do próprio repositório, sandbox do Bash, worktree temporária, timeout de 30 min por passo. Recomendado: rodar só sobre PR de autor confiável, e o security-engineer avaliar filtrar o ambiente passado aos passos e limitar o token ao necessário.

## Custo e rollback
Custo zero (`R-CUSTO`): roda na máquina local, sem serviço pago e sem minutos de Actions. Rollback: reverter os dois commits; nada em `.github/`.
