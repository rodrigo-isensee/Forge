---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: f61799dd400216033de34e16c09c2c17890e5818
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E60.11 (RESERVA-NAO-CAI-NO-FIM, revalidação no head f61799dd)

Revalidação pelo delta `0998e8ab..f61799dd` (`forge-check parecer delta`). No domínio entrou só `tests/mutantes/v0479-reserva-cai-no-fim.json`, com os mutantes novos M13 a M17. O resto do delta veio da `develop` (f35cd528) ou são pareceres da própria branch (681785b junta o remoto da branch). O parecer anterior (head 0998e8ab) segue valendo.

## Parecer
Aprovado. Cada guarda ganhou um mutante por condição, e o texto `de` de todos existe no head: 1269 tem M13 (`isinstance`) e M14 (`fullmatch`), 1276 tem M15, 1383 tem M16 e 1386 tem M17. Cada mutante aponta para um teste de comportamento do ramo de falha. O M13 usa `fullmatch(str(uso))`, então o mutante morre pelo teste e não por um `TypeError`.

Ferramentas: `bin/forge-mutante --processos 1 --ids M13,M14,M15,M16,M17` (rev f61799dd4002) deu os cinco mortos, em 1269, 1269, 1276, 1383 e 1386. `python3 -I tests/catraca.py --base origin/develop` saiu com rc 0. O código não mudou no delta, então a cobertura de 0998e8ab segue valendo. A suíte inteira fica no CI do PR.
