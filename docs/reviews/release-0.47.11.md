---
tipo: review
contrato: 1
pedido: release-0.47.11
branch: melhoria/v0479-release-04711
commit: fe752d14857633363b9da383eeeb9321ff67b7fe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: release-0.47.11

Code review da versão 0.47.11 inteira no head fe752d14 (marca da release na branch melhoria/v0479-release-04711, base develop 119aed79), para integrar na develop e promover à homolog (v0478 E42.2). Os dois pareceres, `docs/reviews/v0479-release-04711.md` e `docs/reviews/release-0.47.11.md`, têm o mesmo veredito e o mesmo conteúdo.

## Parecer
Aprovado.

- Itens da versão: o #701 (ef186de8, sonda S1 e corpus sem dependência de relógio e carga) e o #706 (119aed79, forge-placar fases), mais a marca. Cada item entrou na develop com os próprios pareceres (não refeitos, `R-REVIEW`).
- Marca (fe752d14, 5 arquivos, 8+/6-): `git diff --stat 119aed79 fe752d14` mostra só os dois `plugin.json`, o `CHANGELOG.md` e os 2 fragmentos apagados (`v0479-develop-relogio.md`, `v0479-meta85-placar.md`).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.11"` (antes 0.47.10); `CHANGELOG.md` com `[Não publicado]` vazio (linha 5) e `[0.47.11] - 2026-11-20` (linha 7) acima de `[0.47.10]` (linha 13), em português, com Adicionado e Corrigido.
- Fragmentos: os 2 lidos em 119aed79; o texto de cada um aparece idêntico no `CHANGELOG.md` (Corrigido: E33.1; Adicionado: E36.1); nenhum se perdeu; `changelog.d/` só traz o `README.md`.
- Ferramentas no head: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/validar-plugin.sh`: "Validation passed" nos dois manifestos (rc 0; o sandbox nega só api.anthropic.com, sem efeito na validação).
- SemVer: há Adicionado (opções novas, compatíveis) e nada quebra os projetos; a marca sobe o patch (0.47.10 para 0.47.11), como as versões 0.47.x anteriores, sem bloqueio.
- Suíte: a suíte local falha por ambiente (sandbox: /proc e gh) e não foi rerrodada; a prova da marca é o CI do PR para a develop, obrigatório para o integrar.
