### Alterado
- M16: regra única de marca na R-BRIEF e no `forge-check brief`: toda outra etapa do pedido vai ao Fora do escopo sem a marca, a marca só no corte real; etapa sem menção reprova para qualquer papel, duas etapas no mesmo Entregar reprovam (`etapa: junta delegações`), e o parser lê etapas com sufixo de letra (`E1.3b`) e de qualquer `E<n>` (afrouxa-regra: a marca deixa de ser exigida na etapa do mesmo papel).

### Adicionado
- P2: `forge-check brief gerar --cobre E<n>.<m>` escreve a linha `Etapa: ... Cobre: ...`, abre o Entregar com a etapa coberta e lista no Fora do escopo todas as outras etapas do pedido, sem a marca; sem `--cobre`, deduz a única etapa do destino e recusa (rc 2) quando ele tem mais de uma ou quando a etapa é de outro papel.
