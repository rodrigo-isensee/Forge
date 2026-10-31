---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c4
commit: 14b155bb3e1d8ade8a15200679101bd8c0f2a624
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push, branch c4

Diff lido: `234dbe0..d34b6c7` mais o delta até 14b155b (código e testes; os pareceres de review e segurança da worktree ficam fora).

## Achados
- A1 (recomendado) tests/test_pre_push_trava.py:535 · resolvido no head 14b155b: o subcaso "comum link pendente" prova o -L do C-9 e o mutante C4-M4 morre. Sem achado aberto.

## Revalidação no head 14b155b (delta lido)
`forge-check delta --parecer` (intervalo `d34b6c7..14b155b`): só `tests/test_pre_push_trava.py` (+5 -1, linhas 535-538 e 540), o subcaso do link pendente. Li só isso.
- Suíte dos cinco módulos do hook no head: `Ran 108 tests ... OK`.
- Mutante C4-M4 (spec do QA fora da árvore, `[ -L "$comum" ]` removido), no head: `C4-M4 · morreu · .githooks/pre-push:18`, rc=0.
- O hook não mudou no delta (só teste acrescentado): o vermelho antes do verde e os demais mutantes abaixo valem como estão.
- M14 no head: 150 linhas de código e teste (hook 20, testes 130), no teto de 150. Um comportamento só.

## O que a branch entrega e a M14
- Item do pedido: E3, parte da trava comum e do HOME temporário (TRAVA-SANDBOX; C4 do desenho; C-9 a C-13 do modelo). O texto limitado a imprimíveis (C-14) está na c6, que precisa entrar antes ou junto (condição já registrada no parecer de segurança).
- Linhas de código e teste (decisão M14, `git diff --numstat --no-renames`): 146 (hook 20, testes 126), dentro do teto de 150. Um comportamento só. Toca `.githooks/`, que é protegido e não admite exceção de teto; está abaixo do teto. Cumpre a M14.
- Escopo conferido contra o pedido: nenhum item de outra branch entrou no diff.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3 / C-9: dentro e fora do sandbox usam a mesma trava (pasta comum, sem recuo) | test_dentro_e_fora_do_sandbox_usam_a_mesma_trava | XDG sem escrita num lado; segunda suíte espera | passou (vermelho na base; mutantes C4-M2 e M3 mortos) |
| E3 / C-9, C-10: pasta comum presente e recusada (subpasta link, subpasta arquivo, comum sem escrita, comum arquivo, comum link pendente) não recua | test_pasta_comum_presente_e_recusada_nao_recua (5 subcasos, push e --suite) | quatro formas de recusa; XDG e TMPDIR continuam vazios | passou (vermelho na base); 5 subcasos, com o link pendente (A1 resolvido) |
| E3 / C-11: --status com a pasta comum e sem subpasta não cria nada | test_status_com_pasta_comum_e_sem_subpasta_nao_cria_nada | ausência da subpasta; árvore intocada | passou |
| E3 / C-12 (Q-S1 = B): prova de um lado não dispensa a suíte no outro | test_prova_de_um_lado_nao_dispensa_a_suite_no_outro | provas fora da pasta comum (mutante C4-M1 morto) | passou |
| E3 / C-13: todo teste que roda o hook usa HOME temporário | TodoTesteDoHookUsaHomeTemporario (mínimo de 5 módulos) mais o HOME nos quatro módulos tocados | suíte vazia (mínimo afirmado) | passou |
| Sem pasta comum, a ordem de sempre vale (T-C4d) | os testes antigos do módulo, agora com HOME temporário | ausência de ~/.forge-contrib | passou |

## Cenários e resultado real
Ambiente: worktree da branch no head acima, 16 CPUs, shellcheck ausente nesta máquina (fica para o CI); `bash -n .githooks/pre-push` sem erro.

Vermelho antes do verde (`bin/forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos ...`):
```
vermelho: base=234dbe0fb90b head=d34b6c73aea2 módulos=test_pre_push_trava,test_pre_push_afetados,test_pre_push_parecer,test_pre_push_parecer_curto,test_suite_paralela (restrito por --modulos)
revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c4.md, docs/reviews/impl-pre-push.md, docs/security/impl-pre-push.md
mantidos no HEAD: tests/test_pre_push_afetados.py, tests/test_pre_push_parecer.py, tests/test_pre_push_parecer_curto.py, tests/test_pre_push_trava.py, tests/test_suite_paralela.py
tests.test_pre_push_trava.PrePushTrava.test_dentro_e_fora_do_sandbox_usam_a_mesma_trava · H=ok · B=falha · prova (asserção)
tests.test_pre_push_trava.PrePushTrava.test_pasta_comum_presente_e_recusada_nao_recua · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=106; prova (asserção)=2
rc=0
```


Mutantes (R-QA; a spec é do QA, em arquivo fora da árvore, um mutante por linha de guarda mudada; o autor não declarou `tests/mutantes/impl-pre-push.json`):
```
forge-mutante: pedido=impl-pre-push rev=d34b6c73aea2 spec=76458fc35f3b8c74f9db0aefd3156ed4d7bc900f4d9148040a3c142f8315b6f6
C4-M1 · morreu · .githooks/pre-push:18
C4-M2 · sobreviveu · .githooks/pre-push:21
C4-M3 · morreu · .githooks/pre-push:19
C4-M4 · sobreviveu · .githooks/pre-push:18
C4-M5 · sobreviveu · .githooks/pre-push:18
C4-M6 · sobreviveu · .githooks/pre-push:332
C4-M7 · sobreviveu · .githooks/pre-push:46
C4-M8 · sobreviveu · .githooks/pre-push:179
rc=1
```

Rodada de reforço (as `testes` dos mutantes M4 a M8 ampliadas aos quatro módulos do hook; M2 passa a morrer pelo teste da prova):
```
forge-mutante: pedido=impl-pre-push rev=d34b6c73aea2 spec=4ae836fa98b2306693831c9c2eea112733e1c31d8d2491855170615ab17491b9
C4-M1 · morreu · .githooks/pre-push:18
C4-M2 · morreu · .githooks/pre-push:21
C4-M3 · morreu · .githooks/pre-push:19
C4-M4 · sobreviveu · .githooks/pre-push:18
C4-M5 · sobreviveu · .githooks/pre-push:18
C4-M6 · sobreviveu · .githooks/pre-push:332
C4-M7 · sobreviveu · .githooks/pre-push:46
C4-M8 · sobreviveu · .githooks/pre-push:179
rc=0

[exited with code 0]
```

## Mutantes sobreviventes sem teste (c4)
- C4-M4 (guarda -L do C-9): morto no head 14b155b pelo subcaso novo (era o A1).
- C4-M5 (`-n HOME`): equivalente nos testes, porque só difere com `/.forge-contrib` na raiz do disco, que o teste não cria; aceito.
- C4-M6 (`-n "$1"` do `anotar`) e C4-M8 (recuo quando a pasta das provas falha): só diferem quando a pasta de recuo falha logo depois de a comum ter funcionado, o que exige XDG, TMPDIR e /tmp sem escrita ao mesmo tempo; aceito. Recomenda-se um teste com `/tmp` simulado se o hook ganhar um ponto de injeção.
- C4-M7 (texto da mensagem sem pasta): cosmético; aceito.

## Veredito
Aprovado no head 14b155b. O bloqueante A1 foi resolvido pelo subcaso do link pendente; nenhum bug aberto; a branch cumpre a M14 (150 linhas, um comportamento). A condição do parecer de segurança (c6 antes ou junto, C-14) segue valendo para a ordem de entrada.
