---
tipo: qa
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: bfd9e70ad2325fd5a04a2104fe041d4346384042
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hk3-parecer-pasta (PR A do HK3: o hook parecer resolve a pasta do git), volta 1

Plano: pedido de correção do controle do Forge, sem especificação de UX; as obrigações são a decisão técnica de 10:40 e 11:49 e os casos P e B de `docs/security/hk3-parecer-ameacas.md` (em `~/.forge-contrib/docs/security/`). Teste de abuso: o corpus `pasta-*` (77 fixtures) e as 8 specs de mutantes. Revalidação do parecer anterior (e5ea17b, sobre 212203a): escopo incremental sobre `212203a..bfd9e70` (`hooks/parecer.py` +78 -29, 23 fixtures novas, specs 5 a 8).

## Achados
- A1 (bloqueante) hooks/parecer.py:160 · `git -C` seguido de palavra que a expansão esvazia (crase vazia, `$(echo)`, `$(true)`, `$EMPTY`) desloca a pasta: o hook lê P como subcomando e não confere nada, o bash roda o merge em P (integração) e passa (rc=0) a partir da worktree de trabalho; idem `git $(echo -C P) merge`. Classe: pasta do -C com substituição (HK3-02, vizinha do HK3-01)
- A2 (recomendado) hooks/parecer.py:555 · invólucros e ofuscação passam (rc=0): `env -C P git merge`, `env GIT_DIR=... git merge`, `command`, `time`, `sudo` e `xargs git -C P merge`; subcomando ou branch por substituição ou variável (`git $(echo merge) x`, `git merge $(echo x)`, `B=x; git merge $B` com HEAD na integração); é a limitação de ofuscação do pedido (A2 do QA anterior, mantido): registrar ou barrar no PR B

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P: cd literal, `pull --rebase` e push, `-C` com til, variável, relativo repetido, cd em subshell, gh depois de pushd | `PastaDoGit.test_corpus_pasta_passa_e_barra` (`pasta-passa-*`, 17 fixtures) | permissão: a pasta resolvida vale a branch dela | passou |
| B: `-C`, cd, variável, `--git-dir`, `--work-tree`, `GIT_DIR`, pushd, atribuição em subshell, if, `\|\|`, `&`, export, read, cd inexistente, cd com 2 argumentos (`pasta-barra-*`, 60 fixtures) | idem | pasta desconhecida, vazio, relativo sem base | passou |
| Volta 1: HOME, CDPATH, GIT_DIR e GIT_WORK_TREE mexidos na linha (atribuição, export, declare, read, printf -v, prefixo) tornam a pasta desconhecida | idem (`pasta-barra-home-*`, `-cdpath-*`, `-git-dir-*`) e sondas próprias (`typeset -x`, `local`, `export -n`, `unset HOME`, `HOME= cd`) rc=2 | desconhecida recusa | passou |
| Volta 1: substituição de comando na pasta (crase com e sem aspas, `$( )`, `cd` com crase) recusa (HK3-01) | idem (`pasta-barra-dash-c-com-crase-sem-aspas`, `-e-pull`, `-e-ponto-ponto`, `pasta-barra-cd-com-crase-sem-aspas`) e sondas (crase com espaço, tab, dupla) rc=2 | substituição com espaço dentro | passou |
| Volta 1: texto entre apóstrofos não expande variável | idem (`pasta-*-entre-apostrofos*`, 8 fixtures) e sondas (apóstrofo escapado, dentro de aspas duplas, `$'..'`) | apóstrofo em aspas, escape | passou |
| Merge e pull de integração sem parecer continuam barrados (`-C`, `cd`, `-C` repetido, `~/..`, barra final, `--no-ff -m`, `pull`, `pull --rebase`) | sondas próprias, rc=2 "nenhum parecer" | integração | passou |
| Pasta desviada por palavra que a expansão esvazia (`-C $EMPTY P`) | sonda própria (HK3-02) | palavra vazia, desloca argumento | FALHOU (A1) |

## Cenários e resultado real
- Corpus: `python3 -m unittest tests.test_hooks_parecer_pasta`: 1 teste, `Ran 1 test in 1.590s`, OK, 77 fixtures `pasta-*` verificadas.
- Mutantes declarados: `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1,2,3,4,5,6,7,8}.json`: rc=0, M1 a M60 todos "morreu", nenhum sobrevivente (`$TMPDIR/qa-engineer-hk3-parecer-pasta/mut.log`).
- Conferência da lista contra o diff da volta 1: as 6 guardas sem mutante do QA anterior estão cobertas pelas specs 5 a 8; somei 6 mutantes meus (Q1 a Q6) sobre as linhas atuais (`hooks/parecer.py:240, 531, 531, 271, 249, 233`): `bin/forge-mutante q-volta1.json` rc=1: Q1, Q2, Q4 e Q6 "morreu"; Q3 e Q5 "sobreviveu".
  - Q3 (`efeito_nas_variaveis(palavras, ...)` no lugar de `juntada`, linha 531): equivalente quanto à decisão. A forma partida em palavras só torna mais variáveis desconhecidas (`X=`echo` vira prefixo e `X` cai em `ruins`), e a forma junta cai na guarda de substituição de `resolver`; nenhuma sonda distingue as duas. Justificativa aceita pelo QA.
  - Q5 (tirar `>(` da guarda, linha 249): equivalente quanto à decisão. `git -C >(echo P) merge` sem a guarda dá pasta inexistente (`/dev/fd/63`) e o hook recusa do mesmo jeito (sonda rc=2 com a guarda; o git falha com "cannot change to '/dev/fd/63'"). Justificativa aceita pelo QA.
- Vermelho antes do verde (rodado por mim, rc=0): `bin/forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_hooks_parecer_pasta`: `vermelho: base=ff3936ae4011 head=bfd9e70ad232 módulos=test_hooks_parecer_pasta (restrito por --modulos)`; `revertidos à base: bin/forge-testes, changelog.d/hk3-parecer-pasta.md, ..., hooks/parecer.py`; `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=falha · prova (asserção)`; `contagem: prova (asserção)=1`.
- Sondas próprias (HEAD de integração em `proj`, worktree `home/wtx` em `melhoria/x`, 4 listas, cerca de 160 comandos): fora o A1 e o A2, os contornos de pasta do modelo ficam barrados (rc=2) e o par do brief (`cd <wt> && git pull --rebase origin melhoria/x && git push origin HEAD:refs/heads/melhoria/x`, `cd ~/wtx`, `-C ~/wtx`, `cd "<wt>"`) passa (rc=0). Passam sem defeito: merge a partir da própria worktree, `git -C '' merge`, `git -C P switch develop && git merge` (o merge roda na worktree).
- HK3-01 (crase no `-C`) fechado: as fixtures de crase passam e os mutantes M217/M221 (`juntar_crases`) e Q2 morrem. Reaberto em forma vizinha: HK3-02 (A1).
- Suíte completa: não rodada por mim (o brief a limita ao pre-push); rodei o módulo do item, o `forge-mutante` e o vermelho.
- PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia. A classe do A1 repete a do achado A1 do parecer anterior (substituição na pasta do `-C`, duas ocorrências no pedido), mas o formato da linha `AR-<n>` só admite `review|seguranca` (`bin/forge-check:2110`), então não gravei a linha; registrado como melhoria vista.
- Bugs: `docs/qa/bugs/HK3-01-dash-c-com-crase-sem-aspas-passa.md` (fechado) e `docs/qa/bugs/HK3-02-dash-c-com-palavra-vazia-desloca-a-pasta.md` (aberto).
