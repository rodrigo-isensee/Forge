---
tipo: review
contrato: 1
pedido: release-0.30.3
branch: melhoria/release-0.30.3
commit: 6f0b82473ac50b4031e73657808604514ce2ae32
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: release-0.30.3

## Achados

## Parecer
Aprovado. Diff de 5 arquivos, só da release (sem código, abaixo do teto M14). O CHANGELOG traz os 2 itens (#319 em Adicionado, #320 em Corrigido) com o texto idêntico ao dos fragmentos. Os 2 fragmentos foram apagados e `changelog.d/` ficou sem eles. A versão é 0.30.3 nos dois `plugin.json` (raiz e `dev/`). O número segue a decisão do dono "C" (só o último número sobe até a 0.30 fechar). O commit é único e só da release. Item PA-7: a lista não tem achados registrados. Nenhum risco novo.
