---
tipo: revisao-seguranca
contrato: 1
pedido: ci-ubuntu-26
branch: melhoria/ci-ubuntu-26
commit: bbc658f13b9d57fd551f73e17b57975799146fd7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: ci-ubuntu-26

Aprovado. Revisão estática do diff `develop..HEAD`: nos três workflows, as únicas linhas alteradas são `runs-on: ubuntu-latest` para `ubuntu-24.04` (12 jobs: ci.yml 9, catraca.yml 2, release.yml 1). Nenhuma linha de `permissions:`, `on:`, `env:`, `secrets` ou `uses:` mudou.

## Gatilhos
`R-SEGURANCA`: mudança em `.github/` (workflows). Não toca segredo, dado pessoal nem dependência.

## Verificações
- **Token e `pull_request_target`:** nenhum workflow usa `pull_request_target` (grep em `.github/workflows`). `ci.yml:11` e `catraca.yml:10` têm `contents: read` no topo; jobs com escopo extra o declaram (`catraca.yml:21-24`, `pull-requests: read` e `actions: read`). `release.yml:9` tem `contents: write` no topo, só em `push` na main; é preexistente e fora do diff. A troca de rótulo não altera o escopo do token.
- **Actions sem SHA fixo:** todas as 11 ocorrências de `uses:` estão fixadas por SHA de 40 caracteres com comentário de versão (checkout, setup-python, setup-node). Nenhuma sem SHA. actionlint e zizmor são baixados com `sha256sum -c` (`ci.yml:63-66`).
- **Segredos e escopo do token:** a imagem não define o que o `GITHUB_TOKEN` pode fazer nem quais segredos o job vê; isso vem de `permissions:` e `secrets`, ambos intactos. Os jobs de PR usam `persist-credentials: false` e o corpo do PR entra só por `env:` (`catraca.yml`). Sem efeito de segurança da troca.
- **Fixar numa imagem que envelhece:** o rótulo `ubuntu-24.04` continua recebendo atualizações semanais de pacotes e de segurança do GitHub; fixar a versão do SO não congela a imagem. O risco real é prazo: a 24.04 sai de suporte no futuro, e adiar a migração acumula dívida (ferramentas antigas, como shellcheck 0.9). Não há caminho de ataque hoje; é recomendação.

## Achados
1. **Informativa:** a migração para `ubuntu-26.04` precisa de data. Evidência: `docs/devops/ci-ubuntu-26.md` ("janela de migração", antes de 19/11/2026) sem cartão nem prazo. Caminho de ataque: nenhum imediato; com o tempo, runner sem suporte e sem correções. Correção mínima: abrir o cartão da migração e acompanhar o aviso de descontinuação da 24.04. Esforço: P. Dono: `devops-engineer`.
2. **Informativa (preexistente, fora do diff):** `release.yml:9` concede `contents: write` ao workflow inteiro; hoje há um só job, que precisa dele. Correção mínima: ao adicionar jobs, mover a permissão para o job. Esforço: P. Dono: `devops-engineer`.

Nenhum achado bloqueante.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas: grep e leitura do diff. `actionlint`, `zizmor` e `gitleaks` não estavam no PATH (lacuna registrada; o job `workflows` do CI roda actionlint e zizmor). Pendente fora do parecer: o PR altera `.github/`, então exige o rótulo `afrouxa-regra` do dono e o push com escopo `workflow`.
