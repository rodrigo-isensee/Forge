---
tipo: review
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo
commit: 0157977e02dc38058c1b762b01d301985f85573f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: release-0.47.19

Code review da versão 0.47.19 inteira, revalidado no head 0157977e (branch melhoria/v0481-release-04719-anexo, anexo sobre a `develop` 8ae4d6c6), v0481 E12.32. A rodada anterior (E12.28, head da7b59be) reprovou pelo A1 (linha do anexo com 7 itens). Conteúdo: `git diff v0.47.18..0157977e`; cada item já entrou na `develop` com os próprios pareceres, e aqui se confere a junção, a marca e o anexo. O anexo tem parecer em `docs/reviews/v0481-release-04719-anexo.md`.

## Revalidação
Delta lido: `forge-check parecer delta docs/reviews/release-0.47.19.md`, intervalo `da7b59be..0157977e`, no domínio só `CHANGELOG.md` (+1 −1, 0157977e, E12.31). A1 resolvido: CHANGELOG.md:24 diz "os 8 itens", lista #875, #878, #888, #901, #902, #903, #904, #906 e cita E12.26 e E12.27, igual às 8 origens do anexo. Nada da marca (versões, demais linhas da `[0.47.19]`) mudou.

## Achados
- A2 (recomendado) CHANGELOG.md:17 · Segue o A1 da rodada de 9487d956: #896 (classe C, bin/forge-copia) sem docs/qa/v0481-copia-base-fechada.md na `develop`; o CI pede QA só na homolog. Cartão.
- A3 (recomendado) CHANGELOG.md:7 · 16 dos 18 itens entraram com o rótulo `afrouxa-regra` (#886, #897, #892, #874, #898, #885, #895, #877, #875, #901, #903, #904, #878, #902, #888, #906); o PR homolog → main vai pedir o mesmo rótulo ao dono. Cite os 16 no corpo do PR da promoção.

## Parecer
Aprovado. A junção (18 itens, todos `MERGED`), a seção `[0.47.19]` (26 linhas `- `, falta=0 contra os fragmentos), a versão 0.47.19 nos dois manifestos e as guardas foram conferidas na rodada E12.28 e o delta não as toca.

- Ferramentas no head 0157977e: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 8 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `git diff --check da7b59be 0157977e`: limpo; `tests.test_changelog`: OK.
- ci: 0157977e02dc38058c1b762b01d301985f85573f verde via 9dfbc65f22b831fdc981654e0215228dea38c754
