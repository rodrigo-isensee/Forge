# HK3-03 - `cd` na condição de `if`, `while` ou depois de `!` muda a pasta e o merge passa o hook parecer
- Severidade: alta
- Responsável sugerido: tech-lead (hooks/parecer.py)
- Ambiente: branch melhoria/hk3-parecer-pasta, commit 77b539d3fb3e9ebde40af8cf36942298c54d7e10

## Passos para reproduzir
1. Repositório de projeto com HEAD em `develop` (pasta P, plugin.json com `"name": "forge"`) e uma worktree de trabalho W em `melhoria/x`, sem parecer da branch.
2. Hook `hooks/parecer.py` com a entrada Bash, cwd = W, em cada uma das formas (P é o caminho literal da integração): `if cd P; then git merge melhoria/x; fi`; `if cd P; then :; fi; git merge melhoria/x`; `while cd P; do git merge melhoria/x; break; done`; `! cd P; git merge melhoria/x`.
3. Comparar com `cd P && git merge melhoria/x` (rc=2, "nenhum parecer") e `(cd P && git merge melhoria/x)` (rc=2, "pasta que o hook não resolve").

## Resultado esperado
rc=2: o `cd` da condição roda no shell de cima, o merge roda em P (integração) e a decisão de 12:56 manda toda forma de `cd` que o hook não lê deixar a pasta desconhecida.

## Resultado obtido
rc=0 nas 4 formas. A palavra que abre a parte (`if`, `while`, `!`) vira a primeira palavra, `analisar` devolve None e o `cd` não muda a pasta; o merge é julgado na worktree. A base `ff3936a` dá o mesmo rc=0 (não é regressão, é contorno aberto). `builtin cd P` e `command cd P` também passam (A3, recomendado).

## Evidência
Sondas próprias em `$TMPDIR/qa-engineer-hk3-parecer-pasta/p2/lista6.sh` (primeiras 4 linhas): `rc=0` nas quatro formas; nas formas `if true; then cd P; fi; git merge ...`, `for ... do cd P; done; git merge ...` e `case ... cd P;; esac; git merge ...` o mesmo hook dá rc=2. Conserto sugerido: palavra de abertura (`if`, `while`, `until`, `!`, `builtin`, `command`) antes de um `cd` deixa a pasta desconhecida, ou o `cd` dessas partes zera a pasta.
