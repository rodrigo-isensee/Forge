---
tipo: revisao-seguranca
contrato: 1
pedido: release-timeout
branch: melhoria/release-timeout
commit: 5aacdcdb6cafc7606300a78b7912deb5f70759be
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: release-timeout

Diff revisado: 991cd09...5aacdcd (CI/CD). Aprovado, sem achado.

## Gatilhos
Controle do Forge (workflow `.github/workflows/release.yml`, CI/CD), `R-SEGURANCA`.

## Achados

## Detalhe dos achados
- Mudança de segurança relevante: só `timeout-minutes` de 10 para 20 em `.github/workflows/release.yml:16` (mais comentário, fragmento do changelog e parecer de devops). Nenhuma outra linha do workflow mudou.
- Permissões: `permissions: contents: write` (`release.yml:9-10`) intacta, nem ampliada nem estendida a outro escopo.
- Token: `persist-credentials: false` no checkout intacto; `GH_TOKEN` segue só no `env` do passo "Tag e release", fora do passo "Testes antes de publicar". O código dos testes não recebe o token, então o teto maior não amplia a exposição dele.
- Gatilho: `on: push` em `main` intacto; nenhum `pull_request_target` nem gatilho novo; a main só muda por merge do dono (`R-MAIN`).
- Ações: `actions/checkout` continua fixada por SHA (`release.yml:18`).
- Controle: a suíte continua rodando antes de publicar; a opção (b), que mudaria o controle, ficou fora.
- Risco residual (informativo): um passo travado ou malicioso ocupa o runner por até 20 min em vez de 10. Sem caminho de ataque novo (só código já mesclado pelo dono roda ali, sem token nos testes); custo dentro da franquia (`R-CUSTO`).
- Parecer de devops (5aacdcd, sobre 5ebbfd0): conferido, aprovado, coerente com o diff; a recomendação dele (reavaliar o tempo da Release no próximo checkpoint) é de capacidade, não de segurança.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem item cadastrado ("nenhum ainda"); nada a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `zizmor`, `actionlint` e `gitleaks` não estão no PATH (lacuna registrada); revisão manual do diff de uma linha de valor, sem segredo envolvido.
