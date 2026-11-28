---
tipo: review
contrato: 1
pedido: release-0.47.11
branch: melhoria/v0479-release-04711
commit: 45b77250141751c88bac5fd7e4b5f3b109256748
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

## Revalidação (head 45b77250)
`forge-check parecer delta` não se aplica à forma da marca; li o delta de a14d6c80 a 45b77250 (a junção da develop e o fragmento anexado). Veredito mantido: aprovado.

- Junção: o merge 490b7c14 trouxe da develop o #708 (a99c67b1, quarentena da sonda S1): `tests/test_hooks.py` (+3, `@unittest.skip` com motivo "quarentena", corpo do teste intacto), `tests/config.json` (`teto_pulados` 1 para 2), `tests/quarentenas.py`, `tests/test_catraca.py` (`TetoDaQuarentena`), as specs de mutantes e os pareceres QA, segurança e review do próprio #708 (não refeitos, `R-REVIEW`).
- Anexo (45b77250, `forge-changelog release --anexar`): `git diff --stat 490b7c14 45b77250` mostra só `CHANGELOG.md` (+2) e o fragmento `changelog.d/v0479-quarentena-s1.md` apagado (-3). As 2 linhas de Corrigido (quarentena da S1 e `teto_pulados`) são as do fragmento lido em a99c67b1, em português, dentro da `[0.47.11]`, sem duplicar nem perder texto.
- Versão: os dois `plugin.json` seguem em `"version": "0.47.11"`; a 0.47.11 passa a ser #701, #706 e #708.
- Ferramentas no head: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base a99c67b1`: "versão base: 0.47.10 | versão da release: 0.47.11" (rc 0); `scripts/validar-plugin.sh`: "Validation passed" nos dois manifestos (rc 0; o sandbox nega só api.anthropic.com, sem efeito).
- Acompanhamento (não bloqueia): a quarentena vence em 2026-11-26 e o PR que a tirar devolve `teto_pulados` a 1, como o CHANGELOG já registra.
- Suíte: a local falha por ambiente (sandbox: /proc e gh) e não foi rerrodada; a prova é o CI do PR para a develop, obrigatório para o integrar.
