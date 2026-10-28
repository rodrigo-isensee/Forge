# HK3-02 - `git -C` seguido de palavra que a expansão esvazia desloca a pasta, e o merge passa o hook parecer
- Severidade: alta
- Responsável sugerido: tech-lead (hooks/parecer.py)
- Ambiente: branch melhoria/hk3-parecer-pasta, commit bfd9e70ad2325fd5a04a2104fe041d4346384042

## Passos para reproduzir
1. Repositório de projeto com HEAD em `develop` (pasta P, plugin.json com `"name": "forge"`) e uma worktree de trabalho W em `melhoria/x`, sem parecer da branch.
2. Hook `hooks/parecer.py` com a entrada Bash, cwd = W, em qualquer uma destas formas (P é o caminho literal da integração): `git -C` + crase-echo-crase + P + `merge melhoria/x`; o mesmo com `$(echo)`, `$(true)` e `$EMPTY`/`${EMPTY}` (variável não definida) no lugar da crase; `git` + `$(echo -C P)` + `merge melhoria/x`; `git $(echo) -C P merge melhoria/x`.
3. Comparar com `git -C P merge melhoria/x` (rc=2, "nenhum parecer") e com `git -C $(echo) merge melhoria/x` (rc=2, "pasta que o hook não resolve").

## Resultado esperado
rc=2: o bash descarta a palavra vazia, o `-C` passa a levar P e o merge roda na integração (conferido no shell: `git -C $(echo) P branch --show-current` imprime `develop`, a partir de W em `melhoria/x`). A regra da volta 1 é "o que o hook não resolve na pasta recusa".

## Resultado obtido
rc=0 nas 7 formas. `analisar` (`hooks/parecer.py:158-164`) consome o `-C` mais uma palavra, qualquer que seja, e a palavra seguinte (P) vira o subcomando; como P não é `merge`, nada é conferido. A guarda de substituição em `resolver` nunca é alcançada, porque a chamada nem chega a ser lida como merge. Na base `ff3936a` o resultado era o mesmo para as formas com `$EMPTY`.

## Evidência
Sondas próprias em `$TMPDIR/qa-engineer-hk3-parecer-pasta/p2/` (`probe.sh` monta a entrada do hook; `.qa-hk3-lista4.sh` do QA lista os comandos): as 7 formas saíram `rc=0`; `git -C $(echo) merge melhoria/x` saiu `rc=2 R-REVIEW: merge ou pull numa pasta que o hook não resolve`. Não há fixture no corpus para a forma (as 3 fixtures `pasta-barra-dash-c-com-crase-sem-aspas*` e `-com-substituicao-e-ponto-ponto` só cobrem a pasta que o hook lê como `-C`). Conserto sugerido: palavra com substituição ou variável não resolvida nas opções globais, antes do subcomando, torna a pasta desconhecida e o merge/pull da linha recusa, mesmo que o subcomando não apareça.

## Estado
Fechado em 77b539d3fb3e9ebde40af8cf36942298c54d7e10: a palavra com expansão antes do subcomando deixa as pastas incertas (`globais`, `hooks/parecer.py:135-150`) e a pasta desconhecida recusa; fixtures `pasta-barra-dash-c-com-variavel-vazia`, `-e-chaves`, `-com-substituicao-de-echo`, `-de-true`, `-com-crase-vazia`, `pasta-barra-substituicao-traz-o-dash-c` e `-vazia-antes-do-dash-c` no corpus (118 fixtures `pasta-*`, todas verdes); as 7 formas da sonda dão rc=2.
