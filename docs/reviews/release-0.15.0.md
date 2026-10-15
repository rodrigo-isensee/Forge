---
tipo: review
contrato: 1
pedido: release-0.15.0
branch: melhoria/release-0.15.0
commit: 8b78858404e593e78d7f2e621f759f4b46f28583
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review independente: fechamento da versão 0.15.0 (D-RELEASE)

Escopo: `origin/develop..8b78858` (1 commit, `chore(release): prepara a versão 0.15.0`). Quatro arquivos: `CHANGELOG.md`, `.claude-plugin/plugin.json` e os dois fragmentos apagados.

## Conferido
- Nenhum outro arquivo mudou (`git diff --name-status`: M plugin.json, M CHANGELOG.md, D dois fragmentos). No `plugin.json` mudou só `version` (0.14.0 para 0.15.0).
- Entradas: as 6 de `## [Não publicado]` da develop mais as 2 dos fragmentos (`changelog-fragmentos`, `ci-ubuntu-26`) aparecem as 8, idênticas, em `## [0.15.0] - 2026-10-15` (comparação do texto de cada linha, conjunto ordenado igual). Nada perdido, nada alterado.
- Seções por tipo: um `Adicionado` (4), um `Alterado` (1), um `Corrigido` (3); sem duplicata. `## [Não publicado]` vazio. `changelog.d/` sem fragmentos.
- Ordem das entradas dentro de `Adicionado` mudou (a de `ci-local` desceu para o topo da 0.15.0 e os fragmentos entraram ao fim); não altera conteúdo.

## Provas
- `python3 bin/forge-changelog conferir-release`: rc=0 ("changelog.d/ sem fragmentos pendentes").
- Passo do CI da main "release exige versão nova e changelog fechado", simulado com BASE = origin/main: base 0.14.0, release 0.15.0, entrada `## [0.15.0]` presente (1), `[Não publicado]` vazio: ok.
- Suíte `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests`: 650 testes, OK (158 s, carga 0,2 antes; sem teste intermitente).

## Checklist
Faz o que o pedido pede, sem mais: sim. R-NEUTRO e R-CUSTO: nada novo além de texto de changelog. Regras invioláveis preservadas. Sem achados.

Fora deste parecer: QA, push, PR e promoção (dono, D-ETAPAS = A); `origin` não foi atualizado por `git fetch` (sem credencial no sandbox), então `origin/develop` e `origin/main` são os últimos locais.
