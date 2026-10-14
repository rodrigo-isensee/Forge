---
tipo: revisao-devops
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: b86137d30060ae57ed3f2e76699bf698e4c51149
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-14
---
# Review de devops: ci-local

Parecer de autor (o devops escreveu o script); exige review independente do tech-lead (`R-REVIEW`).

## Parecer
Aprovado, com as lacunas abaixo. `scripts/ci-local <PR> [--publicar]` lê os `run:` de `ci.yml` e `catraca.yml` do PR, roda numa worktree temporária no sha da cabeça, com `env` do passo e `RUNNER_TEMP` próprio por job. Nenhuma lógica do CI foi copiada. Só biblioteca padrão.

Volta 2 (re-review B3, N1, N2): passos sem `shell:` voltaram a `bash -e {0}` como o GitHub (o pipefail da volta 1 era engano meu e do revisor); `shell: bash` declarado usa `-eo pipefail`. `if:` com `github.*` desconhecido ou aninhado demais vira "sem suporte" com aviso, sem `RecursionError`. Testes de regressão vermelhos antes, verdes depois; suíte 587 OK.

Execução real sobre o PR #121 (develop -> homolog), sem `--publicar`: testes estruturais OK (556), shellcheck OK, validação do plugin OK, instalação ponta a ponta OK, fluxo de promoção OK, segredos OK, pareceres OK, catraca FALHOU (legítimo: `bin/forge-check` mudou e falta o rótulo `afrouxa-regra` do dono, igual ao CI real), `workflows` PULADO (sem actionlint/zizmor), `versão e changelog` e `pr-texto` PULADOS (`if` não se aplica a base homolog). Bug achado e corrigido na execução: jobs `pareceres` e `catraca` criavam o mesmo `$RUNNER_TEMP/base`; agora cada job tem subpasta (teste de regressão).

Ferramentas: shellcheck sem achado novo (o script é Python; não há shell tocado); actionlint e zizmor ausentes no PATH.

## O que fica de fora
- Job `workflows` (actionlint, zizmor): o CI os baixa; local só rodam se instalados, e o job é não obrigatório.
- Merge-base no lugar do primeiro pai do merge commit do GitHub: a base dos jobs de diff pode diferir quando a base avançou depois do PR.
- `if:` avaliado por avaliador próprio (sem `eval`), só no subconjunto `github.*`, literais, ==, !=, &&, ||, parênteses; fora dele o job fica "pulado por falta de suporte", com aviso, e conta como falha se for obrigatório.
- Os passos rodam como o GitHub os roda: sem `shell:`, `bash -e {0}` (sem pipefail); com `shell: bash`, `bash --noprofile --norc -eo pipefail {0}`.
- `if:` com contexto `github.*` desconhecido ou aninhado demais deixa o job "pulado por falta de suporte", com aviso.
- **Os testes rodam sobre a cabeça do PR, não sobre o merge com a base** (o CI testa o merge commit). Atualize a branch com a base (`git merge origin/<base>`) antes de rodar.
- Chaves que o leitor ignora geram aviso: `env:` de workflow e de job, `defaults`, `working-directory`, `shell`, `continue-on-error`. Também há aviso se sobrar `HEAD^`/`HEAD~` no passo depois da troca de `git rev-parse HEAD^1`, se o `gh auth token` falhar e se o PR não estiver `OPEN`.
- Passos de preparo (instalação global de CLI, `curl`, `wget`) são ignorados; vale o que há no PATH. Ferramenta ausente em job obrigatório vira `failure`.
- O status `ci-local` é auto-declarado: quem o publica pode publicar `success`. Torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`).

## Segurança (gatilho `R-SEGURANCA` para o security-engineer)
O script executa localmente os `run:` dos workflows do PR: código do PR roda na máquina de quem roda, com o ambiente do usuário (sem `GIT_*`, `GITHUB_TOKEN` e `GH_TOKEN`); o `gh auth token` só chega aos passos que o declaram em `env:` no workflow, como no CI. Risco: PR de terceiro malicioso pode exfiltrar o token ou o ambiente. Mitigações atuais: `if:` sem `eval`; só PRs do próprio repositório, sandbox do Bash, worktree temporária, timeout de 30 min por passo. Recomendado: rodar só sobre PR de autor confiável, e o security-engineer avaliar filtrar o ambiente passado aos passos e limitar o token ao necessário.

## Custo e rollback
Custo zero (`R-CUSTO`): roda na máquina local, sem serviço pago e sem minutos de Actions. Rollback: reverter os dois commits; nada em `.github/`.
