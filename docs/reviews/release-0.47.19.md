---
tipo: review
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo
commit: da7b59be13063ef51235c1e82f53bfda493cc25f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: release-0.47.19

Code review da versão 0.47.19 inteira, revalidado no head da7b59be (branch melhoria/v0481-release-04719-anexo, anexo sobre a `develop` 8ae4d6c6), v0481 E12.28. A rodada anterior (head 9487d956, branch melhoria/marca-0.47.19, E12.23) aprovou a marca, que entrou na `develop` pelo #905 (020e4af7). Conteúdo: `git diff v0.47.18..da7b59be`; cada item já entrou na `develop` com os próprios pareceres, e aqui se confere a junção, a marca e o anexo. O anexo tem parecer em `docs/reviews/v0481-release-04719-anexo.md`.

## Revalidação
Delta lido: `forge-check parecer delta docs/reviews/release-0.47.19.md` responde "9487d95 não é ancestral de da7b59b" (o #905 entrou por squash). Delta conferido à mão: `020e4af7..da7b59be` traz 4 itens da `develop` com pareceres próprios (#878, #902, #888, #906) e o anexo (75b363ad, 25b6e76e, da7b59be); os outros 4 do anexo (#875, #901, #903, #904) entraram entre o corte cc4376fe e o #905. Nada da marca (versões, linhas da `[0.47.19]`) mudou ou saiu.

## Achados
- A1 (bloqueante) CHANGELOG.md:24 · A linha do anexo diz "os 7 itens" e lista 7 PRs; a seção traz 8 (o #906 em CHANGELOG.md:36, anexado no da7b59be). A versão sairia com a nota errada. Mesmo achado do A1 do parecer do anexo.
- A2 (recomendado) CHANGELOG.md:17 · Segue o A1 da rodada anterior: #896 (classe C, bin/forge-copia) sem docs/qa/v0481-copia-base-fechada.md na `develop`; o CI pede QA só na homolog. Cartão.
- A3 (recomendado) CHANGELOG.md:7 · 16 dos 18 itens entraram com o rótulo `afrouxa-regra` (lista abaixo); o PR homolog → main vai pedir o mesmo rótulo ao dono. Cite os 16 no corpo do PR da promoção.

## Parecer
Reprovado (A1). O resto confere:

- Junção: 18 itens, todos `MERGED`. Marca (10): #890, #896, #886, #897, #892, #874, #898, #885, #895, #877. Anexo (8): #875, #901, #903, #904, #878, #902, #888, #906. Pareceres na `develop` (`docs/reviews|qa|security/v0481-<branch>.md`): review, QA e segurança para 17; o #896 tem review e segurança, sem QA (A2). Nenhum código fora da `develop` entra na versão.
- Itens com `afrouxa-regra` (16, todos com o motivo no título e o rótulo posto pela conta do dono, lido nos eventos `labeled` do GitHub): #886, #897, #892, #874, #898, #885, #895, #877, #875, #901, #903, #904, #878, #902, #888, #906. Sem o rótulo: #890 e #896.
- CHANGELOG: `[0.47.19]` com 26 linhas `- ` (11 da marca, 14 dos 8 fragmentos do anexo, a do anexo), cada linha do anexo idêntica ao fragmento e na subseção dele (falta=0); `[Não publicado]` vazio (linha 5); `[0.47.18]` na linha 38; `changelog.d/` só com o README.
- Versão: `0.47.19` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`; patch sobre a 0.47.18 da `homolog`.
- Ferramentas no head da7b59be: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 8 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.18 | versão da release: 0.47.19" (rc 0); `git diff --check 8ae4d6c6 da7b59be`: limpo; `tests.test_changelog`: 91, OK.
- Guardas: o anexo não muda guarda; os itens do anexo têm mutantes declarados (`tests/mutantes/v0481-<branch>*.json` para os 8) e pareceres nos PRs.
- Suíte: não rerrodada (`R-REVIEW`). No da7b59be, as baterias, a catraca e a instalação estão verdes e as 10 partes da `suíte` ainda rodavam na leitura; sem linha `- ci:` nesta rodada, que reprova e muda o head. A prova obrigatória da promoção segue sendo o CI do PR à `homolog`.
