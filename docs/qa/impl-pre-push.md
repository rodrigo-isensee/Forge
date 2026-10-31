---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c1
commit: d9532609530bbb335db14c34bc177150013d8540
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push, branch c1

Diff lido: `234dbe0..d953260` (código e testes; os pareceres de review e segurança da worktree ficam fora).

## Achados
- A1 (recomendado) tests/mutantes/impl-pre-push.json:1 · o autor não declarou a spec de mutantes (pedido de controle em .githooks/); o QA escreveu a lista (5 mutantes, um por linha de guarda mudada) e todos morreram; declarar a spec no próximo pedido de controle.

## O que a branch entrega e a M14
- Item do pedido: E1 (TRAVA-MODO-SUBPASTA; C1 do desenho; C-1 e C-2 do modelo)
- Linhas de código e teste (decisão M14, `git diff --numstat --no-renames`): 56 (hook 11, teste 45). Um comportamento só. Toca `.githooks/`, que é protegido e não admite exceção de teto; está abaixo do teto. Cumpre a M14.
- Escopo conferido contra o pedido: nenhum item de outra branch entrou no diff.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 / C-1: subpasta forge-<uid> com escrita de grupo ou de outros é recusada (push, --suite, --status) | test_subpasta_gravavel_por_grupo_ou_outros_e_recusada (modos 777, 770, 702, 1777) | bit de escrita de grupo; bit de escrita de outros; sticky | passou (vermelho na base, mutantes C1-M1, M2, M4, M5 mortos) |
| E1 / C-1: contraprova, modos sem escrita alheia seguem aceitos | test_subpasta_sem_escrita_de_grupo_ou_outros_segue_aceita (700, 750, 755) | limite logo abaixo do recusado | passou |
| E1 / C-2: erro ao ler o modo (find falha) é recusa, nunca aceite | test_conferencia_do_modo_que_falha_recusa (find falso com saída 1) | leitura do modo falha | passou (vermelho na base, mutante C1-M3 morto) |

## Cenários e resultado real
Ambiente: worktree da branch no head acima, 16 CPUs, shellcheck ausente nesta máquina (fica para o CI); `bash -n .githooks/pre-push` sem erro.

Vermelho antes do verde (`bin/forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155`):
```
vermelho: base=234dbe0fb90b head=d9532609530b módulos=test_agentes_clone,test_agentes_hash_brief,test_ambiente_git,test_anotar,test_atualizar,test_brief_gravar,test_catraca,test_changelog,test_ci_local,test_citacao,test_clareza,te
revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c1.md, docs/reviews/impl-pre-push.md, docs/security/impl-pre-push.md
mantidos no HEAD: tests/test_pre_push_trava.py
tests.test_hooks.Hooks.test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento · H=ok · B=falha · prova (asserção)
tests.test_pre_push_trava.PrePushTrava.test_conferencia_do_modo_que_falha_recusa · H=ok · B=falha · prova (asserção)
tests.test_pre_push_trava.PrePushTrava.test_subpasta_gravavel_por_grupo_ou_outros_e_recusada · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=2305; prova (asserção)=3; pulado=28
rc=0
```
A rodada completa (todos os módulos afetados pelo hook, 2336 testes) terminou sem regressão; uma primeira rodada, feita ao mesmo tempo que outra no mesmo disco, acusou 1 regressão por carga, não repetida na rodada limpa.

Mutantes (R-QA; a spec é do QA, em arquivo fora da árvore, um mutante por linha de guarda mudada; o autor não declarou `tests/mutantes/impl-pre-push.json`):
```
forge-mutante: pedido=impl-pre-push rev=d9532609530b spec=b41facf1fd522d92388f014ba1bce3a738ef4d10eb37905d5f9701ba58e7b7d1
C1-M1 · morreu · .githooks/pre-push:14
C1-M2 · morreu · .githooks/pre-push:14
C1-M3 · morreu · .githooks/pre-push:14
C1-M4 · morreu · .githooks/pre-push:39
C1-M5 · morreu · .githooks/pre-push:40
rc=0
```

## Veredito
Aprovado: todo critério tem teste, o vermelho prova os testes novos e nenhum mutante sobrevive sem justificativa aceita.
