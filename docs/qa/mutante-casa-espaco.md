---
tipo: qa
contrato: 1
pedido: mutante-casa-espaco
branch: melhoria/mutante-casa-espaco
commit: 572c025c8c6e5078f1f78127b4f864a3b6b42b6e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: mutante-casa-espaco

Sem UX nem API; as obrigações são E1 e E2 do pedido `MUTANTE-CASA-ESPACO` e o desvio aceito na DECISÃO TÉCNICA de 2026-10-30 03:10 (sufixo medido no `de` inteiro, soma limitada ao menor texto, aceita quando uma posição possível cai no nó). Não escrevi o diff. Rodado em `~/.forge-contrib/wt/wt-qa-mutante-casa-espaco`, em paralelo ao review (ACELERA-RODADA).

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 ternário com ` and False` depois da condição conta `coberta` | `Cobertura.test_de_e_para_que_dividem_o_espaco_junto_da_condicao_casam` (1ª asserção); C1, C6 | trecho um byte além do fim do nó | passou |
| E1 `de` e `para` que dividem o espaço (fim do nó de uma comprehension) | mesmo teste (2ª asserção); C3, C5 | fim do nó | passou |
| E1 o portão não afrouxa: fora do nó segue `sem mutante` | mesmo teste (3ª e 4ª asserções); C2, C5 | desliza para fora do nó; remoção maior que o nó | passou |
| E2 mutante comum que já casava segue coberto | `Cobertura.test_casamento_pelo_intervalo_do_no_e_as_travas_do_de` (existente, passa no head); C2, C3, C5 | `de` repetido, 8 caracteres, deslocamento em bytes | passou |
| E2 spec das guardas novas | `tests/mutantes/mutante-casa-espaco.json` (C1 a C6) | uma guarda por linha mudada | passou |

## Execução (resultado real, volta 1: delta 9829a70..572c025)
- Delta: docstring do `casa` (bin/forge-mutante:412-416), C4 da spec de `equivalente` para `testes` e o 4o assert (tests/test_forge_mutante.py:667-671) que converte `SyntaxError` em `self.fail`.
- `python3 -m unittest tests.test_forge_mutante` (572c025): `Ran 68 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/mutante-casa-espaco.json` (rev `572c025c8c6e`): C1, C2, C3, C5, C6 e C4 `morreu`; rc=0. O A1 (9829a70) está resolvido: C4 morre pelo teste declarado.
- Conferência da lista contra o diff: guardas nas linhas 419 (C6), 420 (C4), 423 (C1, C2), 424 (C3) e 425-426 (C5) têm mutante; nenhuma sem mutante; sem equivalente declarado.
- `bin/forge-mutante --cobertura --base 042e5d8f73fc659615a4313c7213a661dfc32ce0` (chamada separada): `coberta · bin/forge-mutante:425 · tests/mutantes/mutante-casa-espaco.json:C5 · declarado, não provado`; rc=0; nenhuma `sem mutante`.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0.
- Vermelho: sem prova nova nesta volta (o código só mudou na docstring); a prova é o C4 morto. O vermelho da rodada anterior (teste novo `H=ok · B=falha`) segue valendo.
- Oráculo da rodada anterior (2.702.464 combinações, 0 divergências) segue valendo: a lógica do `casa` não mudou.
- Lista de PA-7 conferida: lista de mutantes completa (AR-1), ramos de falha com teste (AR-2), sem lista negativa de ambiente, sem `python` sem `-I` em caminho que decide, nada de máscara de shell (AR-6); nenhuma classe AR reaparece.

## Riscos
- Nenhum aberto; a docstring agora descreve o alinhamento inteiro dentro do nó, como o código faz.
