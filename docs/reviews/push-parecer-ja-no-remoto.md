---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/push-parecer-ja-no-remoto
commit: 72bf750632b6cd88b4013a1f582bc9426450dfec
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: versao-035 (E3, PUSH-PARECER-JA-NO-REMOTO)

## Achados
- A1 (bloqueante) .githooks/pre-push:196 · o ls-remote consulta o remoto pelo nome ($1), que lê remote.<n>.url; o push vai ao pushurl ($2). Com pushurl diferente (config ou git -c), o hook pulou a suíte e o destino não tinha o commit (rc=0, real.git vazio). Consultar $2 e prender o caso em teste
- A2 (bloqueante) tests/test_pre_push_ja_no_remoto.py:1 · decisão M14: 239 linhas de código e teste (hook 31, teste 208), acima de 150; o PR mexe em .githooks/, caminho de PROTEGIDOS, onde a exceção não vale. Dividir (o desenho previa 35+90) ou levar ao dono
- A3 (recomendado) .githooks/pre-push:196 · com $2 no lugar de $1, o ls-remote aplica url.insteadOf e o push aplica pushInsteadOf; a divergência entre os dois fica como residual a registrar no PR (afrouxa-regra) ou cartão para o security-engineer

## Parecer
Reprovado. Lido: o escopo do E3 e as decisões do dono em `docs/pedidos/versao-035.md`, a seção E3 do desenho (`docs/arquitetura/versao-035-desenho.md`), o E3 do modelo de ameaças (`docs/security/ameacas/versao-035.md`, C-1 a C-11 e T-1 a T-8) e o diff `origin/develop...72bf750` (5 commits).

O que está certo: a função `ja_no_remoto` fica depois das recusas (main, homolog, develop, não fast-forward) e do PREPUSH-DELETE, fora do `--suite` e do `--status` (C-5, T-5, T-6); compara a ref pelo nome inteiro, linha a linha (C-3, T-2); só `refs/heads/*`, tudo ou nada sobre `n_envios == n_refs` (C-4, T-7); falha fechada com `GIT_TERMINAL_PROMPT=0`, `timeout 20`, sha de 40 ou 64 hex e `cat-file -e` antes do `merge-base --is-ancestor` (C-1, C-6); `--` e aspas, sem `eval` (T-4); não grava `.verde` nem `.dirigida` (C-8, T-1); a segunda consulta vem depois de `fila_sair`, com a trava soltando no `exit` (C-7); mensagem com ref e sha7 (C-9); nenhuma variável `FORGE_*` (C-10). `docs/hooks.md` e o fragmento de `changelog.d/` acompanham. O teste reprova sem a mudança e cobre a matriz do modelo, inclusive o casamento pela cauda com a linha que o `ls-remote` devolve de fato.

A1, defeito provado. O git passa ao hook o nome do remoto em `$1` e a URL de destino do push em `$2`. O `git ls-remote -- "$1"` resolve o nome pela URL de busca (`remote.<n>.url`), e o push vai para a `remote.<n>.pushurl` quando ela existe. Reprodução no scratchpad: `origin` com `url=fake.git`, que tem `melhoria/x` no sha, e `pushurl=real.git`, vazio; o hook chamado com `origin real.git` imprimiu `o remoto já tem o que seria enviado (melhoria/x em 4b1fb06); suíte não roda.` e saiu com 0, e `git ls-remote real.git` devolveu 0 linhas. O gatilho também se monta só pela linha de comando (`git -c remote.origin.url=<clone com o sha> push origin`, com pushurl configurada), que é o "git config alterável por argumento do push" do T-3. Sugestão: consultar `$2` (a URL que o git de fato usa no envio), com a mesma recusa de vazio e de `-*`, e um caso no teste com `pushurl` diferente da `url`, em que a suíte precisa rodar. O desenho e o C-2 pediam `$1`; a intenção dos dois ("o remoto escolhido pelo git, nunca outro") só se cumpre com `$2`. Vira cartão para o security-engineer (E2.5) olhar a correção; não refiz o parecer de segurança.

A2, requisito (decisão M14). `git diff --numstat --no-renames origin/develop...HEAD`: `.githooks/pre-push` 30+1, `tests/test_pre_push_ja_no_remoto.py` 208+0; `docs/hooks.md` e `changelog.d/` ficam fora da conta. `.githooks/` está em `PROTEGIDOS` (`tests/catraca.py:43`), então a linha `teto: excedido` não vale aqui. Um comportamento só (as duas consultas são o mesmo pulo), então a divisão é por tamanho: o hook com o núcleo do teste num PR e os casos de C-1, C-5/T-5/T-6 e C-10 (commit b97fa04, cerca de 100 linhas) em outro, ou enxugar o teste até caber. Se o time preferir não dividir, a dispensa é decisão do dono (há precedentes, como a de 2026-11-03 10:06 do lote-l08); sem ela, o achado fica.

A3, recomendação: depois de trocar para `$2`, o `ls-remote` sobre a URL aplica `url.<x>.insteadOf`, e o push aplica `pushInsteadOf`; registrar como residual no corpo do PR, junto do A10 do modelo.

Ferramentas: `python3 -m unittest tests.test_pre_push_ja_no_remoto` no head 72bf750: 9 testes, OK (26 s). `bin/forge-testes --listar` pede a suíte completa (`.githooks/pre-push sem mapa`); não a rodei (D-5): o push de 72bf750 a rodou. `shellcheck` não está instalado neste ambiente: fica pendência da regra de ferramenta. Segurança: parecer da E2.5 ainda não existe nesta branch. Revalidação por delta (`forge-check delta --parecer docs/reviews/push-parecer-ja-no-remoto.md`) na mesma instância.
