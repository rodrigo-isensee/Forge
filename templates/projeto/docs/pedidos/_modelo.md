# Pedido NNN: <assunto>

Copie para `docs/pedidos/NNN-<assunto>.md`. O Jarvis registra o pedido antes do discovery; o `forge:conferente` o lê do disco para conferir cada brief (`R-BRIEF`) e cada entrega (`R-PROVA`). Arquivos que começam com `_` são modelos.

- **Modo:** analisar | planejar | implementar
- **Objetivo:** <em uma frase, nas palavras do usuário>

## Escopo
Um item por linha, numerado: é contra esta lista que o conferente pareia o "Entregar" de cada brief e a tabela pedido × entregue do fim.
1. <item>

## Fora do escopo
O que o usuário não pediu, ou o que saiu do escopo depois. Item que estava no escopo e foi cortado leva a marca literal "Retira do escopo original", o trecho do escopo citado, a justificativa, a consequência e a decisão que o autoriza (`R-DECISAO`):
- <item> · Retira do escopo original: "<trecho do escopo>" · motivo: <...> · consequência: <...> · decisão: <linha DECISÃO DO DONO abaixo ou ADR>

## Suposições
- <suposição> · base: <degrau da escada da R-DECISAO>

## Critério de pronto
- PQ-1 <critério verificável> · prova: <sha | push | pr | run | cmd | arquivo | merge>

## Decisões do usuário (registro literal)
DECISÃO DO DONO (AAAA-MM-DD): <decisão, nas palavras do usuário>
