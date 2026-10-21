---
tipo: revisao-devops
contrato: 1
pedido: release-0.27.0
branch: melhoria/release-0.27.0
commit: 23ecec1054c2b946d22eaa934c05c93996a92945
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-21
---
# Review de devops: release-0.27.0

## Achados
(nenhum bloqueante)

## Detalhe dos achados
Aprovado. O que a leva mudou no pipeline, contra a base 0f480c8, é uma linha em `.github/workflows/ci.yml:120` (passo "Claude Code CLI", vinda do #251): a instalação global do CLI, que segue fixo em 2.1.296, ganha `--allow-scripts` só para o pacote do próprio CLI. `.githooks/` e `scripts/` não mudaram na leva. O commit da release (23ecec1) não toca `.github/`: só `CHANGELOG.md`, os fragmentos de `changelog.d/` e a versão do plugin.

Conferido:
- O `if:` do passo é o mesmo; nenhum passo saiu nem ficou condicional (`R-VERIFY`); permissões, ações por SHA, `concurrency` e `timeout-minutes` não mudam; a entrada é literal.
- Nenhuma outra dependência ganha permissão de rodar script; sem `latest`.
- O parecer `docs/devops/ci-postinstall-cli.md` (aprovado, sem bloqueante) cobre essa mesma linha e continua válido: o texto do passo é idêntico.
- Nenhum workflow escreve na `main` nem publica release antes do merge do dono (`R-MAIN`); a leva não mexe nisso.

Recomendações (não bloqueiam):
- Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono nos PRs de promoção que carregam essa linha; avise o `tech-lead`.
- Conferência de versão × `CHANGELOG`: 0.27.0 em `dev/.claude-plugin/plugin.json` e a entrada no `CHANGELOG.md` batem no diff (9 linhas novas; 5 fragmentos apagados).

Ferramentas: `actionlint` e `docker build` ausentes do PATH neste ambiente (lacuna registrada); a mudança é uma linha de `run:` sem sintaxe de workflow nova.

## Custo e rollback
Custo: nenhum (`R-CUSTO`); runner gratuito, sem serviço, cache ou artefato novo, minutos de CI iguais. Rollback: reverter o commit da linha em `ci.yml` (volta ao comando anterior); a release em si reverte reimplantando a versão 0.26.0.
