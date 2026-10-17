# Pedido NNN: <assunto>

Copie para `docs/pedidos/NNN-<assunto>.md`. O Jarvis registra o pedido antes do discovery; o `forge:conferente` o lê do disco para conferir cada brief (`R-BRIEF`) e cada entrega (`R-PROVA`). Arquivos que começam com `_` são modelos.

- **Modo:** analisar | planejar | implementar
- **Objetivo:** <em uma frase, nas palavras do usuário>
- **Clareza:** <itens por marca: N confirmado, N delegado, N suposição, N técnico, N no-protótipo; quantas perguntas já foram feitas>

## Escopo
Um item por linha, com ID estável (`E1`, `E2`…): é contra esta lista que o conferente pareia o "Entregar" de cada brief (que cita o ID, `(E1)`) e a tabela pedido × entregue do fim.
- E1. <item> · `confirmado`

### Marcas de clareza
Todo item de `## Escopo`, `## Fora do escopo` e `## Critério de pronto` termina com uma marca, preenchida pelo Jarvis no passo 1 e conferida com o usuário no recibo ("vou fazer / não vou fazer; é isso?"):
- `confirmado`: o usuário disse ou aceitou no recibo (a decisão vai gravada em "Decisões do usuário").
- `delegado`: o usuário respondeu "tanto faz" ou "decidam vocês"; grave a frase literal e a recomendação adotada. Custo, acesso, exceção a regra e ato irreversível nunca são delegáveis assim (`R-DECISAO`).
- `suposição`: o time supôs; vale a linha em "Suposições", com a base.
- `técnico`: decisão do time, registrada em ADR ou relatório; não vira pergunta.
- `no-protótipo`: detalhe de interface que o protótipo vai mostrar e o usuário valida depois.

### Tags de registro
Uma linha por ocorrência, em `## Registro de clareza` no fim do pedido, no mesmo turno em que acontece; o `forge:agile-coach` as lê na retrospectiva:
- `PERGUNTA: <data> · <resumo>`: pergunta feita ao usuário.
- `NAO-ENTENDI: <data> · <resumo>`: o usuário disse que não entendeu ou devolveu uma pergunta.
- `ESCOPO+: <data> · <item>` e `ESCOPO-: <data> · <item>`: item acrescentado ou retirado depois do primeiro brief.
- `DEVOLVIDA: <data> · <entrega> · <motivo>`: entrega devolvida por "não era isso".
- `PERGUNTA: nenhuma` (ou a tag equivalente): registra zero ocorrência. Seção presente sem a tag também conta zero; sem a seção, é "não medido".
- Tag e resumo nunca levam segredo nem dado de pessoa (token, senha, CPF, e-mail): se o usuário colou um por engano, o resumo diz só "colou um segredo" e o segredo não é copiado.

## Etapas
O que pertence a outro papel ou momento (review, QA, push pelo dono). Um item por linha, `E1.1 (papel): ...`, onde o papel é o agente ou `dono`. Etapa de outro papel não é corte de escopo: no brief do agente destino aparece em "Fora do escopo" sem a marca.
- E1.1 (<agente>): <etapa>
- E1.2 (dono): <etapa>

## Fora do escopo
O que o usuário não pediu, ou o que saiu do escopo depois. Item que estava no escopo e foi cortado leva a marca literal "Retira do escopo original", o trecho do escopo citado, a justificativa, a consequência e a decisão que o autoriza (`R-DECISAO`):
- <item> · Retira do escopo original: "<trecho do escopo>" · motivo: <...> · consequência: <...> · decisão: <linha DECISÃO DO DONO abaixo ou ADR> · `confirmado`

## Suposições
- <suposição> · `suposição` · base: <degrau da escada da R-DECISAO>

## Critério de pronto
- PQ-1 <critério verificável> · prova: <sha | push | pr | run | cmd | arquivo | merge> · `técnico`

## Decisões do usuário (registro literal)
DECISÃO DO DONO (AAAA-MM-DD): <decisão, nas palavras do usuário>

## Registro de clareza
<uma tag por linha, na forma acima; sem ocorrência, `PERGUNTA: nenhuma`>
