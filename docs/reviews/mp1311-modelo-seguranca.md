---
tipo: review
contrato: 1
pedido: mp1311-modelo-seguranca
branch: melhoria/mp1311-modelo-seguranca
commit: 4b78a54b4ebb700a9c0ac78181b24aff057385e4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: mp1311-modelo-seguranca

Head revisado 4b78a54b (classe C, item 9 do pedido melhorias-de-projeto-1311, E1.7), instância que não fez a entrega.

## Achados
- A1 (recomendado) migrations/0.47.1/migrar:13 · a guarda `if not alvo.exists()` não tem mutante declarado em tests/mutantes/; o teste de não sobrescrever a cobre, falta a spec para a catraca.

## Sondas

## Parecer
Aprovado. A migração 0.47.1 (a versão seguinte à 0.46.0 em curso, pasta na ordem de `forge-upgrade`) copia `templates/projeto/docs/security/_modelo.md` só quando o destino falta: não sobrescreve modelo do projeto e rodar de novo não altera nada (saída vazia, bytes iguais). Os cinco testes novos de `ModeloDeSegurancaNoProjeto` passam (init recebe o modelo; upgrade de projeto em 0.46.0 cria o arquivo, commita "chore(forge): migração 0.47.1" e deixa a árvore limpa; modelo existente intacto; repetição idempotente; LEIA resume o conteúdo). Tamanho: 71 linhas de código e teste, um comportamento só. Fragmento de changelog presente e marcado "requer migração". Os três pareceres (review, QA, segurança) ainda faltam por `forge-check pr`; este é o de review. CI do PR: não há PR; rodei só o teste afetado.
