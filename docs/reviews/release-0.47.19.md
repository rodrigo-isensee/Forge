---
tipo: review
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo-2
commit: 17395e4d905fdbf24bbe21451050873b77261ba6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: release-0.47.19

Code review da versão 0.47.19 inteira, renovado no head 17395e4d (branch melhoria/v0481-release-04719-anexo-2, segundo anexo sobre a `develop` 53e879cf), v0481 E12.41. A rodada anterior (E12.32) aprovou no head 0157977e com 18 itens; depois dela entrou o #908 (índice das fixtures, `docs/hooks-fixtures.md` e `scripts/indice-fixtures.py`) e o seu fragmento, que este anexo junta. Conteúdo: `git diff v0.47.18..17395e4d`; cada item já entrou na `develop` com os próprios pareceres, e aqui se confere a junção, a marca e os dois anexos. O segundo anexo tem parecer em `docs/reviews/v0481-release-04719-anexo-2.md`.

## Revalidação
Delta lido: o `forge-check parecer delta` não lê o intervalo ("commit 0157977e… não existe": o #907 foi mesclado por squash e o head antigo saiu do remoto). No lugar dele, `git log --first-parent 8ae4d6c6..17395e4d` traz só d1ffc325 (#908), 53e879cf (#907, o anexo já aprovado) e 17395e4d (este anexo).
- #908 (d1ffc325): `docs/hooks-fixtures.md`, `scripts/indice-fixtures.py`, `tests/test_indice_fixtures.py`, `tests/mutantes/v0481-fixtures-gerada.json`, fragmento e os três pareceres aprovados (`docs/{reviews,qa,security}/v0481-fixtures-gerada.md`, `commit:` de272439). No head: `python3 scripts/indice-fixtures.py --conferir`: "docs/hooks-fixtures.md: em dia" (rc 0); `python3 -m unittest tests.test_indice_fixtures`: 10 testes, OK.
- Anexo 2 (17395e4d): a linha do #908 entra na `[0.47.19]` e a linha do anexo passa a 9 itens; conferido no parecer do anexo.
- Junção: 19 itens (#874, #875, #877, #878, #885, #886, #888, #890, #892, #895, #896, #897, #898, #901, #902, #903, #904, #906, #908), todos `MERGED`; seção `[0.47.19]` com 27 linhas `- ` (26 + a do #908); `plugin.json` em 0.47.19.

## Achados
- A2 (recomendado) CHANGELOG.md:17 · Segue o A1 da rodada de 9487d956: #896 (classe C, bin/forge-copia) sem docs/qa/v0481-copia-base-fechada.md na `develop` (ausente no head 17395e4d); o CI pede QA só na homolog. Cartão.
- A3 (recomendado) CHANGELOG.md:7 · 17 dos 19 itens entraram com o rótulo `afrouxa-regra` do dono (#874, #875, #877, #878, #885, #886, #888, #892, #895, #897, #898, #901, #902, #903, #904, #906, #908; o #908 sem a marca no título); #890 e #896 sem. O PR homolog → main vai pedir o rótulo: cite os 17 no corpo.

## Parecer
Aprovado. A junção, a seção `[0.47.19]`, a versão e as guardas conferidas nas rodadas E12.28 e E12.32 seguem iguais; o que entrou depois (#908 e o segundo anexo) tem pareceres aprovados e ferramentas verdes no head.

- Ferramentas no head 17395e4d: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 1 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `git diff --check 53e879cf 17395e4d`: limpo; `tests.test_changelog`: OK.
- ci: 17395e4d905fdbf24bbe21451050873b77261ba6 verde
