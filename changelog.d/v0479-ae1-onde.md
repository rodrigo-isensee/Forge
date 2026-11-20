### Adicionado
- forge-check: subcomando `onde <alvo>` diz onde está uma versão (`vX.Y.Z`), um PR (`#N`), um commit, uma branch (`branch:<nome>`, com à frente e atrás da develop e o PR de nome exato) ou um cartão (o commit mais novo que cita o ID inteiro) em develop, homolog e main, lido do git (`merge-base --is-ancestor` contra `origin/<base>`, com o sha lido) e do gh, só leitura e sem fetch, para colar a prova antes de afirmar estado; alvo com `..`, opção ou formato desconhecido sai rc 2 sem chegar ao git, e o gh lento ou fora do ar sai `nao-verificavel` e rc 2, nunca `sim` (v0478 E58.1, AE1.1).

### Corrigido
- forge-check `onde`: sha curto que o git lê de uma tag ou branch de mesmo nome sai `nao-verificavel` e rc 2, em vez de responder sobre outro commit; o `git` que passa do tempo limite sai `nao-verificavel (git sem resposta)` e rc 2, não o rc 1 reservado a alvo inexistente (v0478 E58.13, A1 e A2 da segurança do AE1.1).
