---
tipo: qa
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 10c5b7fc05792a515db5c69b9765d35bc540718a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: pr-verde-lote-check (volta 2)

Pedido de controle do Forge (`bin/forge-check`): E1 (G1), E2 (G2), E3 (G6), E4 (D4), head `10c5b7f`, base `1f7bd7f`; delta da volta `041a6f9...10c5b7f` (só testes e a spec de mutantes `-3`; `bin/forge-check` não mudou). Os dois bloqueantes da volta 1 (A1 em `bin/forge-check:423`, A2 em `:1151`) estão resolvidos, cada um com teste e mutante morto. Nenhum defeito de comportamento aberto.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 cobre cortado sem marca, só do papel do destino | `LoteDoBriefG1` (M1, M10) | papel do destino vs. outro | passou |
| E1 caminho de PQ inexistente reprova; curinga não | `LoteDoBriefG1` (M2, M16) | criado pelo Entregar, glob | passou |
| E1 -REV e -PR sem a decisão da origem reprova | `LoteDoBriefG1` (M3, M9) | REV, PR, com e sem decisão | passou |
| E2 escopo pelo primeiro pai, com parecer depois do merge | `IntegracaoNaBranch` (M4, M5, M14) | merge da base, -s ours, outra branch | passou |
| E2 `pr` aceita o id do pedido | `RecusaDoIdDoPedido` (M6, M12) | 0, 1 e 2 slugs | passou |
| E3 parecer reescrito pelo portão do -REV | `EntregasParalelas` (M7, M11) | papel, commit, Branch | passou |
| E4 só o fragmento exato sai do hash | `PortaoDiffProprio` (M8, M13, M15) | `.md.md`, `.mdx/`, `--base` | passou |
| E4 conflito em arquivo livre no merge simulado não invalida (A1) | `PrAposMergeDaBase.test_conflito_em_arquivo_livre_nao_invalida` (M17) | arquivo livre em conflito | passou |
| E4 nome parecido com o livre aparece no delta (A2) | `Delta.test_arquivo_de_nome_parecido_com_o_livre_aparece_no_delta` (M18) | `KANBAN.md.x` vs `KANBAN.md` | passou |

## Cenários e resultado real
- Os dois testes novos: `Ran 2 tests in 0.384s ... OK`, rc=0.
- Módulos de `bin/forge-testes --listar bin/forge-check` (26) com `python3 -m unittest`: `Ran 1262 tests in 395.282s` ... `OK`, rc=0 (a suíte completa fica com o pre-push, corte 1 da decisão de 2026-10-24).
- Mutantes, `bin/forge-mutante` sobre as specs `pr-verde-lote-check.json`, `-2` e `-3`, rc=0: M1 a M18 todos `morreu` (M17 em `bin/forge-check:423`, M18 em `:1151`; os M1 a M16 como na volta 1).
- Vermelho antes do verde: a volta 2 só adiciona testes sobre código que já existia (`bin/forge-check` idêntico ao de `044ef1d`); o teste não cai na base, então a prova de que ele guarda a linha é o mutante: M17 (`if False:`) e M18 (`startswith`) derrubam exatamente o teste novo correspondente. O `forge-testes --vermelho` roda a suíte inteira e estoura o prazo do QA.
- Conferência das guardas do diff contra a lista: a volta 2 não mudou guarda; as guardas de `livre()` mudadas na volta 1 (A1 e A2) agora têm mutante (M17, M18); o recuo `da_base` em `:993` segue só como recomendação da volta 1 (alcançável só com falha do git), sem bloqueio.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem item a conferir.
