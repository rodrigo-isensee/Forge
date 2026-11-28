---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 68d498057dfd8d376cc63ac4f326b99293656adb
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v0481 BRIEF-SONDA-ESCRITA (#952, E45.63), delta da volta 1 (3c7e53ce..68d49805)

- ci: 68d498057dfd8d376cc63ac4f326b99293656adb verde

Fora `bateria (pareceres)`, `bateria` e `catraca` (esperam os pareceres), todos os checks do `68d49805` concluíram verdes: suíte 1/5 a 5/5, teto de pulados, verificações longas, python 3.14, instalação, passos, árvore já provada.

## Critério → teste → resultado
| Critério (delta) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sonda de parecer de outro pedido não isenta a escrita | `test_sonda_de_parecer_de_outro_pedido_segue_barrada` | pedido do parecer diferente do pedido da sonda | passou; vermelho na base; mortos M8, M9 |
| Parecer que a volta recusa não isenta a escrita | `test_sonda_de_parecer_com_problema_segue_barrada` | parecer com achado fora do formato | passou; vermelho na base; mortos M10, M11 |
| Ref ilegível ou parecer fora da ref segue barrada | `test_ref_ilegivel_ou_parecer_fora_da_ref_segue_barrada` (2 subtestes) | ref sem commit; parecer ausente da ref | passou; vermelho na base; mortos M12, M13 |

## Vermelho antes do verde
`bin/forge-testes --vermelho 3c7e53c --modulos test_brief_sonda_escrita` (log `qa160-vermelho.log`), rc=0:
```
vermelho: base=3c7e53cea2fa head=a6f4cdd14317 módulos=test_brief_sonda_escrita (restrito por --modulos)
...test_ref_ilegivel_ou_parecer_fora_da_ref_segue_barrada · H=ok · B=falha · prova (asserção)
...test_sonda_de_parecer_com_problema_segue_barrada · H=ok · B=falha · prova (asserção)
...test_sonda_de_parecer_de_outro_pedido_segue_barrada · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=4; prova (asserção)=3
```
Os 4 que passam na base são os da 1ª rodada (guardas de limite, já cercadas por M1 a M7). Os 3 novos cobrem os 4 subtestes do delta.

## Mutantes
- `bin/forge-mutante tests/mutantes/v0481-brief-sonda-escrita-2.json --processos 3` (log `qa160-mutantes2.log`), rc=0: M8 a M13 morreram (bin/forge-check:4856, 4856, 4863, 4866, 9446, 4849).
- `bin/forge-mutante tests/mutantes/v0481-brief-sonda-escrita.json` (log `qa160-mutantes1.log`), rc=0: M1 a M7 seguem mortos no head.
- I62 (`v0433-integracao-4.json`): a rodada completa do runner passa de 3 min (9 módulos); conferido à mão numa cópia descartável do head, com o `de`/`para` da spec: `tests.test_brief_forma_aceita` cai com o mutante (FAIL `test_o_branch_do_brief_decide_a_entrada_de_ramo`, 1 falha em 18) e passa sem ele (18 OK). I62 segue morto (logs `qa160-i62-mutado.log`, `qa160-i62-controle.log`).

## Cenários e resultado real
Sem UI, sem acessibilidade aplicável. Sem teste novo do QA, sem bug aberto.
