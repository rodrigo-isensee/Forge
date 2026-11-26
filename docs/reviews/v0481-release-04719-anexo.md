---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-04719-anexo
commit: da7b59be13063ef51235c1e82f53bfda493cc25f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E12.28, anexo da 0.47.19)

Code review do #907, 1ª rodada completa, no head da7b59be (branch melhoria/v0481-release-04719-anexo, base `develop` 8ae4d6c6, merge-base igual). Diff `8ae4d6c6..da7b59be`: 9 arquivos, +15 −22 (`CHANGELOG.md` e 8 fragmentos apagados de `changelog.d/`), em 75b363ad (E12.26, 7 itens e a linha do anexo), no merge limpo da `develop` 25b6e76e e em da7b59be (E12.27, o #906). A versão inteira tem parecer em `docs/reviews/release-0.47.19.md`.

## Achados
- A1 (bloqueante) CHANGELOG.md:24 · A linha do anexo diz "os 7 itens" e lista #875, #878, #888, #901, #902, #903, #904; o da7b59be anexou o #906 (CHANGELOG.md:36) sem atualizar a linha. A seção da release fica com a contagem e a lista erradas. Corrigir: "os 8 itens" e incluir o #906 (e o E12.27).

## Parecer
Reprovado (A1). O resto confere:

- Fragmentos: as 14 linhas `- ` dos 8 fragmentos apagados (ae2-quadro-anda 4, autorizacoes-fixas 1, d2-no-brief 2, entrega-desde-revisar 1, g2-1-publicar 1, prazo-forge 3, rotulo-base-alheia 1, voltas-alinhada 1) estão idênticas na seção `[0.47.19]`, cada uma na subseção do cabeçalho do fragmento (conferência por script, falta=0). Origem: #875, #901, #903, #904 entre o corte cc4376fe e a marca #905; #878, #902, #888, #906 depois dela (primeiros pais da `develop`).
- Seção `[0.47.19]`: 26 linhas `- ` (11 da marca, 14 do anexo, a do anexo); nenhuma linha da marca saiu (`git diff 020e4af7..da7b59be` no CHANGELOG e nos manifestos sem linha `-`). `[Não publicado]` vazio (linha 5); `[0.47.18]` na linha 38; `changelog.d/` só com o README.
- Versão: `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` em 0.47.19, igual ao `## [0.47.19] - 2026-11-26` (`CHANGELOG.md:7`); o anexo não muda a versão.
- Ferramentas no head: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 8 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.18 | versão da release: 0.47.19" (rc 0); `git diff --check 8ae4d6c6 da7b59be`: limpo.
- Teste do arquivo tocado: `python3 -m unittest tests.test_changelog`: 91 testes, OK. Sem guarda mudada, sem mutante a declarar.
- Commits: Conventional Commits em português; o 75b363ad cita os 7 PRs e a ordem do dono; o merge da base é limpo.
- CI no da7b59be lido pela API dos check-runs: verdes `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `catraca` (2), `instalação (python 3.14)`, `árvore já provada na develop`; 7 `skipped` (push na develop e cobertura informativa); as 10 partes da `suíte` (3.12 e 3.14) ainda em andamento na leitura. Sem linha `- ci:` nesta rodada: o parecer é reprovado e a volta muda o head.
