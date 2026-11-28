---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conferencia-merge-pareceres
commit: 0661a9bbba467355bb5175e86c6deeba32b9c815
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-conferencia-merge-pareceres

Etapa E83.2 do pedido v0478, code review no head 0661a9bb (base 2097f9bf). Diff: 4 testes na classe `MergeDeParecerAninhado` (`tests/test_selo_e_entrega.py`, +42) e o fragmento `changelog.d/v0479-conferencia-merge-pareceres.md`. O `bin/forge-check` não muda.

## Achados
- A1 (recomendado) changelog.d/v0479-conferencia-merge-pareceres.md:2 · o conserto que faz os 4 testes passarem é o E62.10 (3092188d), não o E62.19: com o forge-check de 5ec7688e^ os 4 passam; com o de v0.47.11 falham os 2 de liberação. Citar E62.10 (e E62.19 como aperto) no texto.

## Conferência
- Os 4 testes rodados só na classe, em cópia descartável, com três versões do `bin/forge-check` (`python3 -I tests/test_selo_e_entrega.py -v MergeDeParecerAninhado`, ambiente limpo):
  - head (develop, 8a227189): 14 testes OK, os 4 novos passam.
  - 5ec7688e^ (antes do E62.19): os 4 novos passam (falham 3 testes antigos do E62.19, como esperado).
  - v0.47.11 (a cópia vigente que recusou a integração): falham `test_caso_real_outro_pai_sobre_conferido_vale` (linha 2124) e `test_caso_real_merge_de_merge_de_pareceres_vale` (linha 2143); os 2 de recusa passam.
- Leitura: os 2 de liberação reproduzem a recusa real e travam a regressão; os 2 de recusa guardam que o aceite não fica frouxo (conferido tirado da linha reprova), por isso passam em toda versão, como guarda de aperto. As mensagens esperadas batem com `merges_nao_conferidos` e `conferido_mais_novo` (bin/forge-check:2496 e 2522).
- Sem guarda de código mudada: nada a declarar em `tests/mutantes/`. Tamanho (H1): 0 linha de código, só teste e changelog.
- Suíte inteira: fica no CI do PR (`R-REVIEW`), não rerrodada aqui.

## Parecer
Aprovado. Os testes fazem o que o E83.1 pede (fixar os dois formatos reais de merge de pareceres em paralelo, liberação e recusa), são determinísticos e falham com a lógica que causou a recusa (v0.47.11). A1 é só a atribuição do conserto no texto do changelog; não bloqueia e vira cartão depois do merge.
