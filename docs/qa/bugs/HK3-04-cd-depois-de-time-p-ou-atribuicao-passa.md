# HK3-04 - `cd` depois de `time -p` ou de atribuição prefixada depois de `if`, `!`, `while` passa o hook parecer
- Severidade: alta
- Responsável sugerido: tech-lead (hooks/parecer.py)
- Ambiente: branch melhoria/hk3-parecer-pasta, commit 4ae417ecff39652c5d439c294ad2e582cf81861f

## Passos para reproduzir
1. Repositório de projeto com HEAD em `develop` (pasta P) e uma worktree de trabalho W em `melhoria/x`, sem parecer da branch.
2. Hook `hooks/parecer.py` com cwd = W e, para cada comando: `time -p cd P; git merge melhoria/x`; `time -- cd P; git merge melhoria/x`; `if A=1 cd P; then :; fi; git merge melhoria/x`; `! A=1 cd P; git merge melhoria/x`; `while A=1 cd P; do :; break; done; git merge melhoria/x`; `time A=1 cd P; git merge melhoria/x`.
3. Controle: `cd P; git merge melhoria/x` e `A=1 cd P; git merge melhoria/x` dão rc=2.

## Resultado esperado
rc=2: o `cd` roda no shell de cima e o merge roda em P (integração); a decisão de 12:56 manda toda forma de `cd` que o hook não lê deixar a pasta desconhecida.

## Resultado obtido
rc=0 nas formas do passo 2 (`sem_condicao` só tira a palavra de abertura, não as opções do `time` nem as atribuições). A base `ff3936a` dá o mesmo rc=0 (contorno aberto, não regressão).

## Evidência
Sondas próprias `p2/extras2.sh` e `p2/extras3.sh` (em `$TMPDIR/qa-engineer-hk3-parecer-pasta/`): rc=0 nas formas acima; `bash -c 'time -p cd /tmp; pwd'` e `bash -c 'if A=1 cd /tmp; then :; fi; pwd'` imprimem `/tmp`.
