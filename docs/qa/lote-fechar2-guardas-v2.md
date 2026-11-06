---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-fechar2-guardas-v2
commit: b822d22cc790e7f01882e632ebb3c932d925bd54
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote-fechar2-guardas-v2 (testes do ramo de falha do forge-fechar)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1 a G7 falham sem a guarda | forge-mutante lote-fechar2-5.json | ramo de falha de cada guarda | 7 morreram, rc=0 |
| Pasta do log, PR sem merge, plural, merge-base | test_fechar_base_andou (40) | vazio, traço, saída parcial | passou |
| Catraca com link válido | test_fechar_espera_catraca (17) | check de outro nome, link fora do padrão | passou |

## Cenários e resultado real
O diff só soma testes e a spec (bin/ intacto), então não há linha de guarda mudada sem mutante. A saída do forge-mutante foi G1 a G7 morreu, rc=0. Os dois módulos passaram (40 e 17 testes). Cobertura com base dc615c2: sem pendência.
