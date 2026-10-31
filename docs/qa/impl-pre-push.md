---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c3
commit: 8f173bb278d0b1f2a31e2f325c1f7047b3c9b53e
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push, branch c3

Diff lido: `234dbe0..8f173bb` (código e testes; os pareceres de review e segurança da worktree ficam fora).

## Achados
- A1 (recomendado) tests/mutantes/impl-pre-push.json:1 · o autor não declarou a spec de mutantes (pedido de controle em .githooks/); o QA escreveu a lista (1 mutante, a linha única) e ele morreu; declarar a spec no próximo pedido de controle.

## O que a branch entrega e a M14
- Item do pedido: E2, parte da dica do --suite (SUITE-INICIO-ATOMICO; C3 do desenho)
- Linhas de código e teste (decisão M14, `git diff --numstat --no-renames`): 2 (hook 1, teste 1). Um comportamento só. Toca `.githooks/`, que é protegido e não admite exceção de teto; está abaixo do teto. Cumpre a M14.
- Escopo conferido contra o pedido: nenhum item de outra branch entrou no diff.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2 / C3: o --status com suíte rodando imprime a dica do .githooks/pre-push --suite | test_status_acompanha_a_trava (assertIn 'pre-push --suite' na saída com a trava tomada) | saída do status rodando; rc 0 e linha de estado mantidos | passou (vermelho na base; mutante C3-M1 morto) |

## Cenários e resultado real
Ambiente: worktree da branch no head acima, 16 CPUs, shellcheck ausente nesta máquina (fica para o CI); `bash -n .githooks/pre-push` sem erro.

Vermelho antes do verde (`bin/forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos ...`):
```
vermelho: base=234dbe0fb90b head=8f173bb278d0 módulos=test_pre_push_trava (restrito por --modulos)
revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c3.md, docs/reviews/impl-pre-push.md, docs/security/impl-pre-push.md
mantidos no HEAD: tests/test_pre_push_trava.py
tests.test_pre_push_trava.PrePushTrava.test_status_acompanha_a_trava · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=28; prova (asserção)=1
rc=0
```


Mutantes (R-QA; a spec é do QA, em arquivo fora da árvore, um mutante por linha de guarda mudada; o autor não declarou `tests/mutantes/impl-pre-push.json`):
```
forge-mutante: pedido=impl-pre-push rev=8f173bb278d0 spec=8d03a72ffbede2e7e20055311c7ad8e131444f68f9e3814554f432dcb0958ff0
C3-M1 · morreu · .githooks/pre-push:97
rc=0
```

## Veredito
Aprovado: todo critério tem teste, o vermelho prova os testes novos e nenhum mutante sobrevive sem justificativa aceita.
