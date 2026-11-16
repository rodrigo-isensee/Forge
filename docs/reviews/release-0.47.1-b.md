---
tipo: review
contrato: 1
pedido: release-0.47.1
branch: melhoria/release-0.47.1-b
commit: 5b10ba818345f45e573d3f148c0b3763d4257bcf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: release-0.47.1

Release 0.47.1 sobre o topo da develop (067b2a9f, decisão do dono de 14/11), no head 5b10ba81 (E2.36): o PR 562 junta à entrada [0.47.1] os fragmentos do #554 (mp1311-pre-envio-fabrica) e do #561 (v047-heredocs-orcamento), que entraram na develop depois da primeira marca (#560).

## Achados

## Sondas

## Parecer
Aprovado. O intervalo `origin/develop..5b10ba81` é um commit só: `CHANGELOG.md` (+2) e a remoção dos dois fragmentos de `changelog.d/`. Cada fragmento aparece uma vez na entrada 0.47.1, na seção do seu tipo (o #554 em Adicionado, o #561 em Corrigido), com o texto idêntico ao do fragmento; `[Não publicado]` fica vazio e `changelog.d/` só traz o README (`forge-changelog conferir-release`: ok).

Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.1, iguais ao título da entrada. Cobertura da entrada: os 12 PRs de primeiro pai desde a v0.47.0 fora as marcas (#547, #539, #545, #550, #555, #556, #557, #553, #554, #558, #561 e o commit do #551) têm uma linha cada na 0.47.1, inclusive a correção do #558 (mapa do `forge-testes`). `tests.test_changelog`: 74 testes, OK.

CI do PR 562 no head 5b10ba81 todo verde (`gh pr checks 562`: bateria, catraca, instalação, suíte 3.12 e 3.14 em 3 partes, teto de pulados, árvore já provada; só os jobs de push na develop e a cobertura informativa pulados); a suíte não foi rerrodada (`R-REVIEW`).

Domínio contra a main: 155 arquivos, revisados nos PRs de origem; o delta deste head é só changelog, sem código novo. Sem achado bloqueante nem recomendado.
