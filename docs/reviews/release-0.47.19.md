---
tipo: review
contrato: 1
pedido: release-0.47.19
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: release-0.47.19

Code review da versão 0.47.19 inteira, no head 9487d956 (branch melhoria/marca-0.47.19, sobre a `develop` cc4376fe), v0481 E12.23. Conteúdo: `git diff b224ee09..9487d956` (a marca da 0.47.18, #894, até a marca da 0.47.19; 109 arquivos, +4766 −139). Cada item já entrou na `develop` com os próprios pareceres; aqui se confere a junção, a marca e a versão. A marca tem parecer próprio em `docs/reviews/marca-0.47.19.md`; este é o primeiro parecer da versão inteira, sem rodada anterior nem delta.

## Achados
- A1 (recomendado) CHANGELOG.md:17 · #896 (classe C, bin/forge-copia) entrou por merge manual (5587bb5f) sem docs/qa/v0481-copia-base-fechada.md; o CI só pede QA na homolog (tests/catraca.py:2121). docs/qa/release-0.47.19.md:17 conta o copia-base, que é do #879. QA cobrir o E14.33; cartão.
- A2 (recomendado) CHANGELOG.md:7 · 8 dos 10 itens (todos menos #890 e #896) entraram com o rótulo `afrouxa-regra`; o PR homolog → main da 0.47.19 vai pedir o mesmo rótulo ao dono. Cite-os no corpo do PR da promoção.

## Parecer
Aprovado.

- Junção: `b224ee09` é ancestral do head; a cadeia de primeiros pais `b224ee09..9487d956` é exatamente #890 (ca558906), #896 (5587bb5f), #886, #897, #892, #874, #898, #885, #895, #877 (cc4376fe) e a marca, os dez `MERGED`. Pareceres na `develop`: review, QA e segurança para nove deles (`docs/reviews|qa|security/v0481-<branch>.md`); o #896 tem review e segurança, sem QA (A1). Nenhum código fora da `develop` entra na versão.
- CHANGELOG: a reprodução do `forge-changelog release` na base (parecer da marca) prova que os 10 fragmentos estão na seção `## [0.47.19] - 2026-11-26` (4 Adicionado, 2 Alterado, 5 Corrigido: 11 linhas de 10 fragmentos, o `v0481-perfil-fifo` do #886 com duas, E7.15 e E7.19); nenhuma linha antiga saiu (diff só com `+`); `[Não publicado]` vazio (linha 5), `[0.47.18]` na linha 23.
- Coerência entre os itens: o `- ci: ... via <descendente>` do #895 vale para os pareceres desta versão (a regra está no `bin/forge-check` do head); o `docs: ok` do #892 e o `forge-copia clone` que diz o sha (#896) chegaram nesta revisão pela cópia do head; o `diretorio_comum` sem FIFO (#886) e o texto da recusa sem `git` (#886, E7.15) não conflitam com o `modo_por_grupo` do #885, que mantém todos os grupos em `barrar`. Não vi conflito entre as mudanças de `bin/forge-check`, `bin/forge-fechar`, `bin/forge-copia`, `hooks/` e `tests/catraca.py`.
- Versão: `0.47.19` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`; patch sobre a 0.47.18 da `homolog`.
- Ferramentas no head 9487d956: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.18 | versão da release: 0.47.19" (rc 0); `git diff --check cc4376fe 9487d956`: limpo.
- Suíte: não rerrodada (`R-REVIEW`); vale o CI do #905 no head, linha abaixo. A prova obrigatória da promoção segue sendo o CI do PR à `homolog`, que lá exige também o QA (A1).
- Guardas: a marca não muda guarda nenhuma; as dos itens têm mutantes declarados (`tests/mutantes/v0481-*.json`) e pareceres nos PRs de cada um.
- CI lido pela API dos check-runs no 9487d956: 20 checks `success` e 7 `skipped` (os de push na develop e a cobertura informativa); nenhum vermelho.
- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde
