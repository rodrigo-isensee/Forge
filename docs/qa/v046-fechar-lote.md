---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-fechar-lote
commit: 0b6e6834be6a9df4cdaf5438675b6fb82874f068
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
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

## Revalidação por delta no head 17ae39a3 (E6.7)
Branch: melhoria/v046-fechar-lote. Delta 0be84795..17ae39a3 pelo `forge-check parecer delta` (sem o que veio da base): só `tests/pesos-d4.json` (a junção da develop a986c292 resolveu esse arquivo) e `docs/engineering/achados-recorrentes.md` (AR-1 e AR-13). `bin/forge-fechar` e `bin/forge-doutor` não mudaram no delta; o commit c378a396 sobre o head só toca `docs/security/`.
- `pesos-d4.json` é JSON válido e traz os três pesos novos (`test_doutor_branch_atrasada`, `test_fechar_move_cartao`, `test_fechar_prune_sandbox`); `test_pesos_teto` e `test_suite_partes` passam.
- Sem PR aberto: rodados só os afetados e os testes do pedido (51 testes, OK, carga ~13). Mutantes declarados (3 specs, 17 mutantes): todos morreram, rc 0, nenhum sobrevivente. A1 e A2 anteriores seguem recomendados (A2 parcialmente atendido pelas specs -2 e -3), sem bloqueio.
- Parecer: aprovado, nenhum bug.

## Revalidação por delta no head 2dda228f (E6.15)
Branch: melhoria/v046-fechar-lote. Delta 17ae39a3..2dda228f pelo `forge-check parecer delta` (sem o que veio da base): só `bin/forge-testes` (a regra `bin/forge-doutor` do `MAPA` ganhou `test_doutor_branch_atrasada`; o `test_pr_hook_prazo` da linha do `FORGE_CHECK` é da base) e `tests/test_testes_tocados.py:55` (lista esperada do `bin/forge-doutor`, com o módulo novo). `bin/forge-fechar` e `bin/forge-doutor` não mudaram.
- Rodados em worktree só minha (carga ~16, um módulo por vez): `tests.test_testes_tocados` 150 testes, OK (1 pulado, do próprio módulo); `tests.test_doutor_branch_atrasada` 6 testes, OK. O mapa agora roda o teste do doutor quando `bin/forge-doutor` muda.
- CI do PR 525 no mesmo sha: `catraca`, `instalação` e `árvore já provada` passam; `bateria` falha só em "Parecer de review ... quando o PR toca código que governa os agentes" (`docs/reviews/v046-fechar-lote.md: commit: desatualizado`). É o parecer do review, fora do meu domínio, que o portão paralelo atualiza; a suíte em partes não rodou por isso, então não cito `bateria` como verde.
- A1 e A2 anteriores seguem recomendados, sem bloqueio. Nenhum bug novo.
- Parecer: aprovado.

## Revalidação por delta no head 0b6e6834 (E6.20)
Branch: melhoria/v046-fechar-lote. Delta 2dda228f..0b6e6834 é só a junção com a develop b19a5a94 (PRs 524, 528, 529): `agents/agile-coach.md`, `agents/tech-lead.md`, `bin/forge-check`, `tests/config.json` (invariantes), `tests/test_conf_escopo.py`, `tests/test_prepush_so_docs.py`, skills, changelog.d e pareceres de outros pedidos. `git diff 2dda228f 0b6e6834` em `bin/forge-fechar`, `bin/forge-doutor`, `bin/forge-testes`, `tests/pesos-d4.json`, `tests/test_testes_tocados.py` e `tests/mutantes/v046-fechar-lote*.json` sai vazio: nada da fechar-lote mudou. O commit 92b59dfb sobre o head só toca `docs/security/`.
- Local (worktree só minha, módulo por vez): test_doutor_branch_atrasada 6 OK; test_fechar_move_cartao 12 OK; test_fechar_prune_sandbox 3 OK; test_fechar_forge_check_real 3 OK. Mutantes das 3 specs: 17 de 17 `morreu`, rc 0.
- CI do PR 525, check-runs do sha 0b6e6834: `bateria` success, `bateria (python 3.14)` success, suítes 3.12 e 3.14 partes 1 a 3 success, `teto de pulados` success.
- A1 e A2 anteriores seguem recomendados, sem bloqueio. Nenhum bug novo.
- Parecer: aprovado.
