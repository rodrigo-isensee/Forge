---
tipo: review
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716
commit: 2b8d11be7024106a2fd96f41633676f45d93595e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: release-0.47.16

Code review da versão 0.47.16 inteira no head 2b8d11be (branch melhoria/v0480-release-04716, corte 35b05bd3 da `develop`, PR #852), v0478 E167.2. Conteúdo: `git diff v0.47.15..2b8d11be`; cada item já entrou na develop com os próprios pareceres, e aqui se confere a junção e a marca. A marca tem parecer em `docs/reviews/v0480-release-04716.md`.

## Parecer
Aprovado.

- Junção: 36 fragmentos novos em `changelog.d/` em 35b05bd3 (e 36 specs novas em `tests/mutantes/` desde a v0.47.15); as 42 linhas `- ` deles estão todas na `[0.47.16]` (`grep -qxF`, falta=0), mais a linha da marca (43 no total).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.16 = `[0.47.16] - 2026-11-24` (`CHANGELOG.md:7`); `[Não publicado]` vazio (linha 5); `[0.47.15]` na linha 55; entrada em português. `changelog.d/` em 2b8d11be só com o README.
- Ferramentas no head 2b8d11be: `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou)" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/develop`: "versão base: 0.47.15 | versão da release: 0.47.16" (rc 0); `git diff --check 35b05bd3 2b8d11be`: limpo.
- Placar: linha 0.47.16 (mortos=59 sobreviveu=0, specs=9) e nota do corte (`docs/engineering/placar-mutacao.md:26` e `:38`).
- Suíte: não rerrodada (sem suíte local); a prova é o CI do PR #852, obrigatório para integrar (`R-REVIEW`). Testes dos arquivos tocados (`tests.test_changelog`, `tests.test_placar_prometido`): 105, OK.
- Integração: a `develop` andou 5 itens depois do corte (6161978d); o merge com ela deixaria 5 fragmentos pendentes sob a 0.47.16, o que o passo 3 do `scripts/promover-homolog.py` recusa. O release é refeito sobre a base trazida (E167.1) e o head novo revalida este parecer por delta.
