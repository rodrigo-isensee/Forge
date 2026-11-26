# v0481-s1-status-data-invalida - status cai com ValueError se a pergunta ao dono tem data inexistente
- Severidade: alta
- Responsável sugerido: dev da stack (autor do #910)
- Ambiente: melhoria/v0481-s1-status @ 0b412b4a

## Passos para reproduzir
1. Pedido com `- PERGUNTA AO DONO (2026-02-30 09:00): A ou B?` em docs/pedidos/p.md.
2. `forge-check --raiz <tmp> status --agora 2026-11-26T12:00-03:00 --raiz-pedidos <tmp>`.

## Resultado esperado
rc 0, seis linhas; a das decisões vira `não verificável (...)`.

## Resultado obtido
rc 1, traceback `ValueError: day is out of range for month` em bin/forge_estado.py:100 (fromisoformat sem guarda); linhas 5 e 6 não saem.

## Evidência
Sonda reproduzida pelo QA no head 0b412b4a (a mesma do review).
