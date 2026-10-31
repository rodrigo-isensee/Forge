---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c2
commit: 71837ac014a2a51ec14c160b5e3d274e8d309b5c
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push, branch c2

Diff lido: `234dbe0..71837ac` (código e testes; os pareceres de review e segurança da worktree ficam fora).

## Achados
- A1 (recomendado) .githooks/pre-push:98 · o mutante C2-M5 (trava_confere || exit 1 no --status) sobrevive: a falha de trava_confere (dono diferente ou troca por link na corrida) não se reproduz sem segundo usuário; QA aceita a justificativa, o ramo espelha os outros três mortos.
- A2 (recomendado) tests/mutantes/impl-pre-push.json:1 · o autor não declarou a spec de mutantes (pedido de controle em .githooks/); o QA escreveu a lista (6 mutantes) e só o C2-M5 sobreviveu, pela razão do A1; declarar a spec no próximo pedido de controle.

## O que a branch entrega e a M14
- Item do pedido: E2, parte do erro do --status (PRE-PUSH-STATUS-RC; C2 do desenho; C-4, C-6 e C-7 do modelo). A dica do --suite (C3) fica na c3.
- Linhas de código e teste (decisão M14, `git diff --numstat --no-renames`): 55 (hook 15, teste 40). Um comportamento só. Toca `.githooks/`, que é protegido e não admite exceção de teto; está abaixo do teto. Cumpre a M14.
- Escopo conferido contra o pedido: nenhum item de outra branch entrou no diff.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2 / C-6: erro do --status (subpasta link, trava link, trava sem leitura) sai com rc 2 e nunca diz 'nenhuma suíte' | test_status_com_erro_sai_com_2 (3 subcasos); test_subpasta_que_e_link_e_recusada (asserção trocada para 2) | três origens de erro; saída sem 'nenhuma suíte' | passou (vermelho na base; mutantes C2-M1 a M4 mortos) |
| E2 / C-7: a mensagem do erro aponta o --suite | test_status_com_erro_sai_com_2 (assertIn 'pre-push --suite') | texto do erro | passou (mutante C2-M6 morto) |
| E2 / C-4: o push segue com rc 1 no mesmo erro, sem rodar a suíte | test_status_com_erro_sai_com_2 (segunda metade de cada subcaso) | rc do push distinto do rc do --status | passou |
| --status 0 (rodando) e 1 (nenhuma) não mudam | test_status_acompanha_a_trava e test_status_nao_cria_subpasta_nem_trava (já existentes) | regressão dos dois rc antigos | passou |

## Cenários e resultado real
Ambiente: worktree da branch no head acima, 16 CPUs, shellcheck ausente nesta máquina (fica para o CI); `bash -n .githooks/pre-push` sem erro.

Vermelho antes do verde (`bin/forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos ...`):
```
vermelho: base=234dbe0fb90b head=71837ac014a2 módulos=test_pre_push_trava (restrito por --modulos)
revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c2.md, docs/reviews/impl-pre-push.md, docs/security/impl-pre-push.md
mantidos no HEAD: tests/test_pre_push_trava.py
tests.test_pre_push_trava.PrePushTrava.test_status_com_erro_sai_com_2 · H=ok · B=falha · prova (asserção)
tests.test_pre_push_trava.PrePushTrava.test_subpasta_que_e_link_e_recusada · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=28; prova (asserção)=2
rc=0
```


Mutantes (R-QA; a spec é do QA, em arquivo fora da árvore, um mutante por linha de guarda mudada; o autor não declarou `tests/mutantes/impl-pre-push.json`):
```
forge-mutante: pedido=impl-pre-push rev=71837ac014a2 spec=3167bda63d7f549034a46a4de3c3be4d0eba39d5e38ebfe16b95e2e0e172b9e3
C2-M1 · morreu · .githooks/pre-push:91
C2-M2 · morreu · .githooks/pre-push:93
C2-M3 · morreu · .githooks/pre-push:94
C2-M4 · morreu · .githooks/pre-push:97
C2-M5 · sobreviveu · .githooks/pre-push:98
C2-M6 · morreu · .githooks/pre-push:90
rc=1
```

## Veredito
Aprovado: todo critério tem teste, o vermelho prova os testes novos e nenhum mutante sobrevive sem justificativa aceita.
