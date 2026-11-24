---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 64c4dd9ba9c4b3484431167e1b7a42adc7b80ec5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E174.2, rastreio do critério à prova, PR #868)

Base aabc476c, head 64c4dd9b. Mudança: subcomando `forge-check criterios <pedido>` (`cmd_criterios`, `criterios_do_pedido`, `provas_por_criterio`), skill `produto-criterios` (id `C-n`, campo `cobre:`), `tests/test_criterios.py` (7 testes), 3 specs de mutante, `forge-testes` e `pesos-d4.json`. Sem UX nem contrato de API: as obrigações são as da skill e do docstring do comando.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `C-n` com `PQ cobre:` de brief com entrega conferida sai entregue; sem prova, não entregue (rc 1) | `test_criterio_com_prova_conferida_entregue_e_sem_prova_nao_entregue` | selo repetido não duplica; PQ solto fora do início da linha não conta | passou; vermelho na base; mutantes morreram |
| Todos entregues: rc 0, sem linha extra | `test_todos_entregues_sai_com_rc_zero` | `cobre: C-1, C-2` numa PQ | passou; vermelho na base; D717 morreu |
| Brief sem `entrega conferida` não prova | `test_brief_sem_entrega_conferida_nao_prova` | 0 entregues | passou; vermelho na base |
| `cobre:` fora do pedido reprova | `test_cobre_de_criterio_fora_do_pedido_reprova_mesmo_com_todos_entregues` | C-9 inexistente | passou; vermelho na base |
| Id repetido reprova, vale o primeiro | `test_id_repetido_reprova_e_vale_o_primeiro` | duplicata | passou; vermelho na base |
| Linha `id:` dá o nome da tabela | `test_linha_id_do_pedido_da_o_nome_da_tabela` | id diferente do nome do arquivo | passou no HEAD; na base dá erro, sem veredito (A1) |
| Pedido sem `C-n` ou ilegível: rc 2 | `test_pedido_sem_criterio_c_n_ou_ilegivel_sai_nao_verificavel` | sem item; pedido inexistente | passou; vermelho na base |

## Vermelho antes do verde
`bin/forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos test_criterios`, saída não zero:
```
vermelho: base=aabc476c5dba head=64c4dd9ba9c4 módulos=test_criterios (restrito por --modulos)
tests.test_criterios.Criterios.test_linha_id_do_pedido_da_o_nome_da_tabela · H=ok · B=erro · sem veredito
contagem: prova (asserção)=6; sem veredito=1
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
```
Os outros 6 provam por asserção; nenhum cai no HEAD.

## Mutação
`bin/forge-mutante` nas 3 specs (`--processos 3`): D71 a D717 todos `morreu`, nenhum sobrevivente. `--cobertura --base aabc476c`: toda condição mudada em `bin/forge-check` tem mutante (`coberta`); só `tests/pesos-d4.json` sai `não coberto` (dado, sem decisão).

## CI
Run 45487005524 ainda em andamento na minha leitura; `bateria (pareceres)` falhou (sem parecer na branch até este commit) e `catraca` passou. A suíte inteira vale pelo check-run `bateria` do mesmo sha, não rerrodada aqui.

## Achados
- A1 (bloqueante) tests/test_criterios.py:119 · `test_linha_id_do_pedido_da_o_nome_da_tabela` indexa `[1][0]` da saída; na base a saída é vazia e vira erro (IndexError), "sem veredito" no `forge-testes --vermelho` (rc não zero). Afirmar a lista inteira com `assertEqual` (falha por asserção) para provar o vermelho.
