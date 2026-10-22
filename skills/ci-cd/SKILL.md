---
name: ci-cd
description: Boas práticas de CI/CD e de entrega (pipeline, containers, infraestrutura como código, ambientes, releases e rollback), com GitHub Actions como padrão. Use ao escrever ou revisar workflows, Dockerfile, compose, IaC, deploy, release, Dependabot ou o tempo do CI.
---

# CI/CD e entrega

Princípios genéricos e o padrão da fábrica (GitHub Actions). O que depende de linguagem (toolchain, chave de cache, comandos de pronto, imagem base) fica em `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`, seção "CI"; provedor de nuvem e ferramenta de IaC ficam na ADR do projeto. Segurança em profundidade está na skill `cyber-security`: aqui só o que é da mecânica da entrega.

## Princípios
- **O pipeline é código:** versionado, revisado e com a mesma barra do código de produto. Mudança nele passa por review (`R-REVIEW`).
- **Verde significa verde:** nada de `continue-on-error`, `[skip ci]`, check desligado ou teste pulado para passar (`R-VERIFY`).
- **Rápido e barato:** o feedback vem em minutos, e o custo de dinheiro é zero sem autorização do dono (`R-CUSTO`). Corte o passo redundante antes de pagar por runner maior.
- **Reprodutível:** mesma entrada, mesma saída. Dependências travadas e instaladas congeladas, bases de imagem fixadas, sem "latest".
- **Imutável e promovido:** constrói-se uma vez; o mesmo artefato sobe de homologação para produção, mudando só a configuração.
- **Reversível:** todo deploy tem caminho de volta escrito e testado; migração sem caminho de volta não vai a produção.
- **Menor privilégio:** cada job com as permissões e os segredos de que precisa, e só.

## GitHub Actions (padrão)
Checklist de workflow:
1. `permissions:` mínimas por job; o padrão é `contents: read` e o que sobe é explícito.
2. Ações de terceiros **fixadas por SHA** de commit, com a tag em comentário; atualização pelo Dependabot.
3. Nenhum `pull_request_target` com checkout de código de fork; entrada não confiável (título de PR, nome de branch) nunca interpolada em `run:`, e sim passada por variável de ambiente.
4. Segredos só no job que precisa e nunca impressos; OIDC no lugar de chave longa quando há nuvem.
5. `concurrency` cancelando a execução obsoleta do mesmo ref; `timeout-minutes` em todo job.
6. Cache com chave derivada do lockfile, sem restaurar cache de fork para a branch principal (envenenamento); matriz só onde agrega.
7. Jobs independentes em paralelo; passo caro só depois do barato (lint antes de teste, teste antes de imagem).
8. Artefatos e logs com retenção curta, dentro da franquia gratuita.
9. Nenhum workflow escreve na `main`, faz auto-merge para ela nem publica release antes do merge do dono (`R-MAIN`).
10. Valide com `actionlint` (e `shellcheck` nos scripts) quando já estiverem instalados; o agente não instala ferramenta.

Quais checks são exigidos para mesclar, proteção de branch, rulesets, segredos e `environments` são do dono (`R-CONFORMIDADE`): proponha, não altere por `gh api`. O token do bot não tem o escopo `workflow`: a mudança de workflow é preparada em branch local e enviada pelo dono.

## Containers
`Dockerfile`: base fixada por digest, multi-stage, usuário não root, `HEALTHCHECK`, `.dockerignore`, segredo nunca na imagem nem em `ARG`/`ENV`. Compose: portas publicadas em `127.0.0.1`, segredos fora da imagem, volumes só do necessário.

## Infraestrutura como código
Dentro da topologia, do provedor e da ferramenta decididos pelo arquiteto em ADR: módulos pequenos, estado fora do repositório, `plan` revisado antes de `apply`, nada de segredo em arquivo de variáveis versionado, recurso pago só com autorização (`R-CUSTO`).

## Ambientes e releases
- Promoção homologação → produção com aprovação do dono (`environments`), paridade de configuração e variáveis por ambiente.
- Pós-deploy: health check e smoke test; versão marcada nos logs.
- Release: tag `vX.Y.Z`, notas a partir do `CHANGELOG`, conferência de que versão e `CHANGELOG` batem. O nível SemVer e o texto são do `tech-lead`.
- Rollback: reimplantar a versão anterior; confira a migração reversível **antes** do deploy.

## Simulação de merge (a base certa)
Para saber como a entrega fica sobre a base de integração, simule o merge fora da árvore de trabalho:
1. Use um clone ou uma worktree **com as refs remotas** e rode `git fetch origin <base>`.
2. Faça `git merge --no-ff refs/remotes/origin/<base>` na cópia descartável.
3. Rode a checagem **contra essa base** (a mesma da validação), nunca contra a base local.

Nunca use um clone sem as refs remotas (por exemplo `git clone --no-tags --single-branch` de outra ref, ou clone local sem `origin/<base>`): a checagem compara com a base errada e sai com rc 0. Confira que `git rev-parse refs/remotes/origin/<base>` responde antes de confiar no resultado.

## Tempo e dependências
- Meça a duração por workflow e os minutos usados (`gh run list`); um checkpoint por release. Subiu mais de 20% ou passou de 80% da franquia gratuita: abra cartão de melhoria.
- Dependabot para ações, imagens e pacotes, com agrupamento e janela; a triagem separa o bump sem quebra (mecânico) do que exige correção de código (dev da stack).
- Modelo do projeto: `templates/projeto/.github/dependabot.yml` (ações, neutro) e o bloco do ecossistema de pacotes em `stacks/<stack>/pronto.md`, seção "CI". Grupos de rotina só com minor e patch; major em grupo à parte, que vira cartão de migração.
- A configuração do Dependabot só vale na branch padrão (`main`), e o alerta de segurança abre contra a branch padrão, não contra o `target-branch`; o conserto segue pela branch de integração.
- Não edite o PR do robô (base, título, corpo) nem o feche por comentário: nada de `@dependabot ignore`, que esconde o major sem prazo. Ignorar é `ignore` versionado no arquivo, por pacote, com o cartão no comentário.
- Sem auto-merge, sem `registries` com credencial em claro e sem `insecure-external-code-execution` (`R-SEGURANCA`: Dependabot não tem isenção).
