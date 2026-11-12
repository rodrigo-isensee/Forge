---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-fechar-lote
commit: 0be847950094f66ffccdca5fe1ec7c1accd5233a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E6.4, fechar o lote: forge-fechar e forge doutor), head 0be84795

Escopo: diff 8b5a44d5..0be84795, quatro itens: CONFERENTE-PR-ABERTO-CEDO e FECHAR-MOVE-CARTAO (`--cartao` e `--quadro` do `bin/forge-fechar`), WORKTREE-PRUNE-SANDBOX (`podar_orfaos` no passo 7), ATUALIZAR-BRANCH-ATRASADA (`bin/forge-doutor`). Sem custo novo (`R-CUSTO`). Os pareceres de review e segurança (580fb0fe, 9255ef23) só adicionam documentos; o código testado é o do `commit:`.

## Achados
- A1 (recomendado) bin/forge-fechar:1047 · lacuna de teste, não bug: com `--cartao` e PR já MERGED (ou head já na base) o cartão move e o motivo sai `mesclado em develop: head <sha7>` (reproduzido à mão, rc 0); nenhum teste cobre e o mutante do `else` sobrevive. Teste com `lista_extra` MERGED.
- A2 (recomendado) tests/mutantes/v046-fechar-lote.json:1 · `mover_cartoes` das linhas 812 e 1048 e o `podar_orfaos` do ramo de sucesso (541) estão sem mutante declarado; os mutantes meus (tirar a chamada) morrem nos testes, então é só declaração; declare os três (AR-1).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Move o cartão para Pronto só depois do merge provado; coluna do histórico, da seção do quadro ou `—` | tests.test_fechar_move_cartao (merge, seção, sem registro) | cartão sem registro | passou |
| Já em Pronto não grava de novo; falha do movimento vira pendência, código 3 | test_fechar_move_cartao (já em Pronto, falha, limpar com falha) | repetição, falha | passou |
| ID fora da forma ou quadro sem KANBAN.md param antes do passo 1; sem `--cartao` nada muda | test_fechar_move_cartao | ID inválido, quadro ausente, vazio | passou |
| `--limpar` só move com prova de merge; `--dry-run` não grava; `--armar` repete cartão e quadro | test_fechar_move_cartao | sem prova de merge | passou |
| Movimento real do `forge-check` | tests.test_fechar_forge_check_real | forma do histórico | passou |
| Prune também depois de remoção que deu certo; metadados presos viram registro, sem pendência | tests.test_fechar_prune_sandbox | prune negado | passou |
| Branch atrás da develop: o doutor manda o cherry-pick do commit da versão | tests.test_doutor_branch_atrasada | develop ausente, versão igual, sha ilegível | passou |
| PR já MERGED com `--cartao` | nenhum | head já na base | lacuna (A1) |

## Cenários e resultado real
Um módulo por vez (`R-TETO`), na worktree destacada em 0be84795: test_doutor_branch_atrasada 6 OK; test_fechar_move_cartao 12 OK; test_fechar_prune_sandbox 3 OK; test_fechar_forge_check_real 3 OK.

Mutantes (`bin/forge-mutante` das três specs do pedido): 17 de 17 `morreu` (C1 a C9, P1 a P5, D1 a D3). Cobertura (`--cobertura --base`): `forge-doutor:141,146,160` cobertas; `bin/forge-fechar` e `tests/pesos-d4.json` `não coberto` (shell e dado, como previsto).

Mutantes meus, em cópia descartável, contra os dois módulos do fechar (15 testes): tirar `mover_cartoes` do caminho do merge, morre (4 falhas, 1 erro); tirar do `--limpar` (812), morre; tirar `cartao_pend` do código final (1076), morre; tirar `podar_orfaos` do ramo de sucesso, morre; trocar o texto do `else` do motivo (1047) ou tirá-lo, SOBREVIVE (A1). Linha de base da cópia: 15 OK, duas vezes.

Os 3 pontos do review: o ramo MERGED com `--cartao` é lacuna de teste, não bug (provado à mão: cartão movido, limpeza ok, rc 0); das 3 guardas do shell sem mutante, 2 morrem por teste (A2) e 1 é a do A1. Não é defeito provado, então nada bloqueia (`R-REVIEW`).

Vermelho antes do verde: os testes novos são do autor e os 17 mutantes provam que eles caem sem a mudança; não escrevi teste novo, então não rodei `forge-testes --vermelho`.

## Provas
O verde do pedido vale pelo check-run `bateria` do mesmo sha no PR; local rodei só os afetados, como acima.
