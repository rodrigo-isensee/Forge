---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-release-04716-anexo
commit: 51fc24a74534d3ba419d2f7f08c9ae307aa07347
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E167.7, anexo da 0.47.16)

Code review do anexo da 0.47.16 no head 51fc24a7 (branch melhoria/v0480-release-04716-anexo, base `develop` 5f1c6e97), v0478 E167.7. Diff: um commit (51fc24a7, E167.6), 12 arquivos, +12 −22: `CHANGELOG.md` e 11 fragmentos apagados de `changelog.d/`. A versão da release toda tem parecer revalidado em `docs/reviews/release-0.47.16.md`.

## Parecer
Aprovado.

- Fragmentos: os 11 apagados têm a linha `- ` idêntica na seção `[0.47.16]` (`grep -qxF`, falta=0) e na subseção do cabeçalho de cada um (Adicionado 4, Alterado 3 mais a linha do anexo, Corrigido 3). Origem conferida por `git log --diff-filter=A`: os 6 entre o corte 35b05bd3 e a marca #852 (#843, #844, #845, #846, #839, #848) e os 5 depois dela (#805, #812, #847, #851, #853). Bate com a lista da mensagem do commit e da linha do anexo (`CHANGELOG.md:46`).
- Seção `[0.47.16]`: 55 linhas `- ` (43 da marca mais 12 do anexo); nenhuma linha da marca saiu (o diff só acrescenta). `[Não publicado]` vazio; `changelog.d/` só com o README.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.16, igual ao `## [0.47.16] - 2026-11-24` (`CHANGELOG.md:7`); a versão não muda no anexo, como o pedido manda.
- Ferramentas no head: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 11 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.15 | versão da release: 0.47.16" (rc 0); contra `origin/develop` ele pede subir a versão (rc 1), esperado num anexo sem troca de versão, e a promoção compara com a `homolog`; `git diff --check 5f1c6e97 51fc24a7`: limpo.
- Teste do arquivo tocado: `python3 -m unittest tests.test_changelog`: 91 testes, OK. Suíte não rerrodada (sem suíte local, brief); não há PR nem run de CI nesta branch (`gh run list` vazio): a prova da suíte é o CI do PR de promoção.
- Commit: Conventional Commits em português, um commit coerente, mensagem com os 11 PRs e o corte.

## Achados
- A1 (recomendado) docs/engineering/placar-mutacao.md:38 · A nota da 0.47.16 fala só do corte 35b05bd3; as 11 specs de mutação que o anexo trouxe (g1-2-delta 4, ordens-hook 5, limpar-url-git, vigia-trava-critica) não aparecem nela como fora da amostra. Uma frase na nota, sem mudar a linha do placar.
