### Corrigido
- Quarentena de teste: o OK do dono (`A-<n>`) só aceita dígito ASCII; `A-١` e afins deixam de valer (QUARENTENA-DIGITO-ASCII).
- `bin/forge-fechar` sem merge automático (FECHAR-SEM-AUTO-MERGE, decisão do dono de 21/11): o passo 6 e o P6 da promoção mesclam direto, preso ao head (`gh pr merge --squash|--merge --match-head-commit <sha>`), só depois de todo check-run obrigatório do head verde, catraca incluída (falha terminada para; pendente espera até `--espera` e relê logo antes do merge); o `--armar` recusa com o porquê e o comando certo.
