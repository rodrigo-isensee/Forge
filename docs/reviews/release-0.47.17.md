---
tipo: review
contrato: 1
pedido: release-0.47.17
branch: melhoria/marca-0.47.17
commit: d2a9d91914d65aa6eb2daca515c89d0907226c85
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: release-0.47.17

Code review da versão 0.47.17 inteira, no head d2a9d919 (branch melhoria/marca-0.47.17, sobre a `develop` 6959cec2), v0481 E12.8. Conteúdo: `git diff v0.47.16..d2a9d919` (tag ad55cd9c; 261 arquivos). Cada item já entrou na `develop` com os próprios pareceres (#854 a #881, 21 PRs); aqui se confere a junção, a marca e a versão. A marca tem parecer próprio em `docs/reviews/marca-0.47.17.md` (E12.3); este é o primeiro parecer da versão inteira, sem rodada anterior nem delta.

## Achados
- A1 (recomendado) docs/engineering/placar-mutacao.md:26 · A marca da 0.47.17 não traz a linha do placar de mutação nem a nota do corte, que a 0.47.16 trouxe (`ritmo-e-corte.md:50`, medida e não portão). Rode `scripts/placar-mutacao.py --desde v0.47.16 --versao 0.47.17` e leve ao Jarvis.

## Parecer
Aprovado.

- Junção: a `develop` (6959cec2, o Base-sha) é ancestral do head; `origin/develop..d2a9d919` muda só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`, os 3 pareceres da marca e apaga 21 fragmentos de `changelog.d/`. Nenhum código fora da `develop` entra na versão.
- CHANGELOG: os 21 fragmentos criados em `v0.47.16..d2a9d919` somam 22 linhas de item (o `v0480-graphql-ilegivel.md` traz duas), e cada uma está literal na seção `## [0.47.17] - 2026-11-25` (`grep -qxF`, falta=0); a seção tem 22 itens, nenhum além dos fragmentos. O brief fala em 21 itens: a conta é anterior ao #880, que a E12.6 juntou (A1 do parecer da marca, resolvido). Nenhuma linha antiga do `CHANGELOG.md` saiu (diff só com `+`). `[Não publicado]` vazio (linha 5), `[0.47.16]` na linha 34.
- Versão: `0.47.17` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`, antes `0.47.16` na tag; patch coerente com a versão anterior da série.
- Ferramentas no head d2a9d919: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.16 | versão da release: 0.47.17" (rc 0); `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou)" (rc 0); `git diff --check v0.47.16 d2a9d919`: limpo.
- Suíte: não rerrodada (`R-REVIEW`). O CI do push da `develop` em 6959cec2 está `success`; o do PR #882 no head d2a9d919 estava com 6 pass, 7 skipping e as 10 partes da suíte pendentes na leitura, nenhum vermelho. A prova obrigatória é o CI do PR de promoção à `homolog`.
- Guardas: a marca não muda guarda nenhuma; as guardas dos itens têm mutantes e pareceres nos PRs de cada um.
