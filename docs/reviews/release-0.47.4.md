---
tipo: review
contrato: 1
pedido: release-0.47.4
branch: melhoria/v0474-release-0474
commit: ebe0f56d5436bb205eb12dac97ace114a1c60e29
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: release-0.47.4

## Sondas

## Parecer
Aprovado. Parecer da release contra a main (P-N3, `scripts/promover-homolog.py`), pedido pelo passo 1c do `bin/forge-fechar v0474` no head ebe0f56d; a marca em si já tem parecer em `docs/reviews/v0474-release-0474.md` (aprovado no f198cfbd, delta sem o domínio).

- Base: `git merge-base origin/main HEAD` é 25be7197, a marca da 0.47.3; a main está na 0.47.3 (`.claude-plugin/plugin.json`).
- Leva: `git log --first-parent 25be7197..origin/develop` traz 27 entradas (#607, #608, #611, #612, #615 a #618, #621 a #639), cada uma integrada com os pareceres próprios na develop; as que afrouxam regra (#625, #627, #631, #638) entraram com o rótulo e a liberação do dono citadas no título.
- Marca: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"; `CHANGELOG.md` com a entrada 0.47.4 e `[Não publicado]` vazio; os dois `plugin.json` em 0.47.4 (lido pelo `promover-homolog.py --conferir-ref`: "versão: homolog 0.47.3 | develop 0.47.4").
- Tamanho: 2728 linhas de código contra a main (`forge-check pr release-0.47.4 --base main`); é a soma da leva, já revisada item a item; a release não se corta sem desfazer itens integrados. A linha `teto: excedido` vai no corpo do PR #640.
- Suíte: fica no CI do PR #640 (R-FLUXO); não rerrodada aqui.
