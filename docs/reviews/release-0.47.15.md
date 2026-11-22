---
tipo: review
contrato: 1
pedido: release-0.47.15
branch: melhoria/v0480-release-04715
commit: a151f1d254124ebb23e4f82f1a8bd44404c53f06
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: release-0.47.15

Code review da versão 0.47.15 inteira no head a151f1d2 (branch melhoria/v0480-release-04715, corte f4836717 = `origin/develop`), v0478 E125.6. Conteúdo: `git diff v0.47.14..a151f1d2` (201 arquivos, 10516+/549-); cada item já entrou na develop com os próprios pareceres, e aqui se confere a junção e a marca. A marca 3b6cfad5 tem parecer aprovado em `docs/reviews/v0480-release-04715.md`; de 3b6cfad5 a a151f1d2 só entram os três pareceres da marca (QA, review, segurança).

## Parecer
Aprovado.

- Junção: `git log --first-parent v0.47.14..f4836717` dá 20 itens (19 squash de #780 a #799 e o merge do #776) e 20 fragmentos novos em `changelog.d/`; as 35 linhas `- ` deles estão todas na `[0.47.15]` (`grep -qxF`, falta=0). O merge 27169ed1 (#776) não tem resolução à mão (`git show --cc` sem `@@@`).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.15 = `[0.47.15] - 2026-11-22` (`CHANGELOG.md:7`); `[Não publicado]` vazio (linha 5); `[0.47.14]` na linha 47; entrada em português. `changelog.d/` em a151f1d2 só com o README.
- Ferramentas no head a151f1d2: `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou)" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/develop`: "versão base: 0.47.14 | versão da release: 0.47.15" (rc 0); `git diff --check v0.47.14 a151f1d2`: limpo.
- Placar: linha 0.47.15 (mortos=53 sobreviveu=0, specs=9) e nota do corte (`docs/engineering/placar-mutacao.md:25` e `:35`).
- Suíte: não rerrodada (sem suíte local); a prova é o CI do PR, obrigatório para integrar (`R-REVIEW`).
