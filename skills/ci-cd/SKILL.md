---
name: ci-cd
description: Boas práticas de CI/CD e de entrega (pipeline, containers, infraestrutura como código, ambientes, releases e rollback), com GitHub Actions como padrão. Use ao escrever ou revisar workflows, Dockerfile, compose, IaC, deploy, release, Dependabot ou o tempo do CI.
---

# CI/CD e entrega

O que depende de linguagem (toolchain, chave de cache, comandos de pronto, imagem base) fica em `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`, seção "CI"; provedor de nuvem e ferramenta de IaC ficam na ADR do projeto. Segurança em profundidade: skill `cyber-security`.

## Princípios
- **O pipeline é código:** versionado, revisado e com a mesma barra do código de produto. Mudança nele passa por review (`R-REVIEW`).
- **Verde significa verde:** nada de `continue-on-error`, `[skip ci]`, check desligado ou teste pulado para passar (`R-VERIFY`).
- **Rápido e barato:** o feedback vem em minutos, e o custo de dinheiro é zero sem autorização do dono (`R-CUSTO`). Corte o passo redundante antes de pagar.
- **Reprodutível:** mesma entrada, mesma saída. Dependências travadas e congeladas, imagens fixadas, sem "latest".
- **Imutável e promovido:** constrói-se uma vez; o mesmo artefato sobe de homologação a produção, mudando a configuração.
- **Reversível:** todo deploy tem caminho de volta escrito e testado; migração sem caminho de volta não vai a produção.
- **Menor privilégio:** cada job com as permissões e os segredos de que precisa, e só.

## GitHub Actions (padrão)
Checklist de workflow:
1. `permissions:` mínimas por job; o padrão é `contents: read` e o que sobe, explícito.
2. Ações de terceiros **fixadas por SHA** de commit, com a tag em comentário; atualização pelo Dependabot.
3. Nenhum `pull_request_target` com checkout de código de fork; entrada não confiável (título de PR, nome de branch) nunca interpolada em `run:`, e sim passada por variável de ambiente.
4. Segredos só no job que precisa e nunca impressos; OIDC no lugar de chave longa quando há nuvem.
5. `concurrency` cancelando a execução obsoleta do mesmo ref; `timeout-minutes` em todo job.
6. Cache com chave derivada do lockfile, sem restaurar cache de fork para a branch principal (envenenamento); matriz só onde agrega.
7. Jobs independentes em paralelo; passo caro só depois do barato (lint antes de teste, teste antes de imagem).
8. Artefatos e logs com retenção curta, dentro da franquia gratuita.
9. Nenhum workflow escreve na `main`, faz auto-merge para ela nem publica release antes do merge do dono (`R-MAIN`).
10. Valide com `actionlint` e `shellcheck`; ausente é achado do parecer, e quem instala é `scripts/preparar-estacao.sh`.

Checks exigidos, proteção de branch, rulesets, segredos e `environments` são do dono (`R-CONFORMIDADE`): proponha, não altere por `gh api`. Ler a proteção inclui os rulesets (`gh api repos/<dono>/<repo>/rulesets` e `rules/branches/<b>`), além de `branches/<b>/protection`. O token do bot não tem o escopo `workflow`: a mudança de workflow é preparada em branch local e enviada pelo dono.

## Containers
`Dockerfile`: base fixada por digest, multi-stage, usuário não root, `HEALTHCHECK`, `.dockerignore`, segredo nunca na imagem nem em `ARG`/`ENV`. Compose: portas publicadas em `127.0.0.1`, segredos fora da imagem, volumes só do necessário.

## Infraestrutura como código
Dentro da topologia, do provedor e da ferramenta decididos pelo arquiteto em ADR: módulos pequenos, estado fora do repositório, `plan` revisado antes de `apply`, nada de segredo em arquivo de variáveis versionado, recurso pago só com autorização (`R-CUSTO`).

## Ambientes e releases
- Promoção homologação → produção com aprovação do dono (`environments`), paridade de configuração e variáveis por ambiente.
- Pós-deploy: health check e smoke test; versão marcada nos logs.
- Release: tag `vX.Y.Z`, notas a partir do `CHANGELOG`, conferência de que versão e `CHANGELOG` batem. O nível SemVer e o texto são do `tech-lead`.
- Rollback: reimplantar a versão anterior; confira a migração reversível **antes** do deploy.
- PR de release (branch de homologação → `main`): abre-se só com o portão da homologação **verde** no sha do candidato; antes do merge do dono, os checks do PR (entre eles "Nada pula degrau" (a `main` só aceita PR da `homolog`) e o de versão nova e `CHANGELOG` fechado) rodam no sha do candidato, e quem decide é o resultado deles naquele sha. Check em andamento: espere; falha externa: reexecute o **mesmo sha**, nunca marcar como aprovado nem afrouxar o check (`R-CONFORMIDADE`). PR aberto antes do portão: edite e aguarde; não feche e recrie para "limpar" o vermelho. Passo a passo do `tech-lead` (listar, conferir, editar): `R-FLUXO`. O corpo do PR `homolog` → `main` traz a saída do modo `rotulados` da catraca (`tests/catraca.py --modo rotulados`, ADR 0008): os PRs rotulados da leva com a decisão declarada de cada um.

## Ensaio de roteiro
Ensaie roteiro só em alvo provado descartável: confira a conexão antes do
primeiro comando e recuse o valor padrão.

## Simulação de merge (a base certa)
Para saber como a entrega fica sobre a base de integração, simule o merge fora da árvore de trabalho:
1. Use um clone ou uma worktree **com as refs remotas** e rode `git fetch origin <base>`.
2. Faça `git merge --no-ff refs/remotes/origin/<base>` na cópia descartável.
3. Rode a checagem **contra essa base** (a mesma da validação), nunca contra a base local.

Nunca use um clone sem as refs remotas (ex.: `git clone --no-tags --single-branch`, ou clone local sem `origin/<base>`): a checagem compara com a base errada e sai com rc 0. Confira que `git rev-parse refs/remotes/origin/<base>` responde.

## Tempo e dependências
- CI privado: `ci-de-projeto-privado.md`.
- Meça duração e minutos por release (`gh run list`; `forge-cota-ci`, rc 1 acima de 80%). Subiu 20% ou passou de 80%: cartão de melhoria. Sem permissão, não peça escopo.
- Dependabot para ações, imagens e pacotes, com agrupamento e janela; a triagem separa o bump mecânico do que pede código (dev da stack).
- Modelo do projeto: `templates/projeto/.github/dependabot.yml` (ações, neutro) e o bloco do ecossistema de pacotes em `stacks/<stack>/pronto.md`, seção "CI". Rotina só com minor e patch; major à parte, em cartão de migração.
- A configuração do Dependabot só vale na branch padrão (`main`), e o alerta de segurança abre contra a branch padrão, não contra o `target-branch`; o conserto segue pela branch de integração.
- Não edite o PR do robô (base, título, corpo) nem o feche por comentário: nada de `@dependabot ignore`, que esconde o major sem prazo. Ignorar é `ignore` versionado, por pacote, com o cartão no comentário.
- Sem auto-merge, sem `registries` com credencial em claro e sem `insecure-external-code-execution` (`R-SEGURANCA`: Dependabot não tem isenção).
