---
tipo: qa
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 4ae417ecff39652c5d439c294ad2e582cf81861f
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hk3-parecer-pasta (PR A do HK3: o hook parecer resolve a pasta do git), volta 3

Plano: pedido de correção do controle do Forge, sem especificação de UX; as obrigações são as decisões técnicas de 10:40, 11:49 e 12:56 (pasta só literal; o que o hook não resolve recusa) e os casos P e B de `docs/security/hk3-parecer-ameacas.md` (em `~/.forge-contrib/docs/security/`). Teste de abuso: o corpus `pasta-*` (129 fixtures: 16 `passa`, 113 `barra`) e as 15 specs de mutantes. Revalidação do parecer anterior (4d5021d, sobre 77b539d): escopo incremental sobre `77b539d..4ae417e` (`hooks/parecer.py` +13 -3: `CONDICAO`, `sem_condicao`, `popd` e o `cd` de condição zeram a pasta; specs 14 e 15; 11 fixtures novas).

## Achados
- A1 (bloqueante) hooks/parecer.py:224 · `time -p cd P` e `if A=1 cd P` (também `!`, `while`, `time A=1 cd`) seguidos de merge passam (rc=0) com P na integração: `sem_condicao` só tira a palavra de abertura. Classe: cd em posição que o hook não lê (HK3-04)
- A2 (recomendado) hooks/parecer.py:581 · envoltório antes do `git` passa (rc=0), igual na base: `time git merge`, `env git merge`, `nice git merge`, `time -p git -C P merge`; também `builtin cd P`, `command cd P`, `env -C P git merge`; ofuscação do pedido, mantida
- A3 (recomendado) hooks/parecer.py:62 · o mutante Q19 (`function` fora de `ABRE`) sobrevive e é equivalente em segurança (só deixa a pasta desconhecida mais cedo: vira recusa de qualquer forma); sem teste novo
- A4 (recomendado) hooks/parecer.py:183 · `analisar` ainda calcula `pasta` e devolve `parte[1]`, que `conferir` já não usa: código morto (herdado do A5 do parecer anterior)

## Detalhe dos achados
- Fechados pela volta 3: o A1 do parecer anterior (bug HK3-03, `cd` em condição): `if cd P`, `if cd P; then :; fi`, `elif cd P`, `while cd P`, `until cd P`, `! cd P`, `! ! cd P`, `time cd P`, `function f { cd P; }; f` e `if [ -d P ]; then cd P; fi` dão rc=2 "não resolve" (sondas próprias `p2/lista6.sh`, `extras.sh` e `extras2.sh`); e o A2 (Q16 `popd`, Q14 troca de branch na pasta resolvida): as fixtures `pasta-barra-popd-depois-de-cd-absoluto` e `pasta-barra-switch-em-outra-pasta-nao-troca-a-branch-da-pasta-do-merge` e os mutantes M99 e M100 os matam.
- A1: `time -p cd /tmp; pwd` e `if A=1 cd /tmp; then :; fi; pwd` imprimem `/tmp` no bash (o `cd` roda no shell de cima). A decisão técnica de 12:56 manda toda forma de `cd` que o hook não lê deixar a pasta desconhecida, e o autor declarou `time`, `if`, `!` e `while` em `CONDICAO`; as variantes com opção do `time` e com atribuição prefixada seguem passando (rc=0 nas 8 sondas de `p2/extras3.sh`; `A=1 cd P` sozinho dá rc=2). `critério mudou:` na rodada anterior o A1 era recomendado; as sondas mostram a mesma classe do HK3-03 (requisito), e o review (A6, A7) e a segurança (A10, A13) o tratam como bloqueante. Conserto: tirar as opções do `time` e as atribuições depois das palavras de condição antes de olhar o `cd`. Bug `HK3-04`.
- A2: lista5 (75 comandos): 59 recusam (rc=2) e 16 passam, todos esperados (o par do brief, `cd`/`-C` na worktree, `git -C '' P`, `git -C ~` fora de repositório, `env -C`, `$(echo merge)` e `-CP` colado, que o git recusa); o resultado não mudou desde o parecer anterior.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P: `cd` literal, `pull --rebase` e push na worktree, `-C` com `~`, `-C` repetido relativo, expansão depois do subcomando, gh depois de pushd, `cd` e `-C` com til, `if` sem `cd` (`pasta-passa-*`, 16 fixtures) | `PastaDoGit.test_corpus_pasta_passa_e_barra` | permissão: a pasta resolvida vale a branch dela | passou |
| B: pasta só literal; `-C`, `cd`, `-C` repetido, `--git-dir`, `--work-tree`, `GIT_DIR`, pushd, popd, `cd` em subshell, bloco, pipeline, segundo plano, `&&`/`\|\|` condicional, variável, crase, `$( )`, HOME, CDPATH, atribuição, export, read, printf -v (`pasta-barra-*`, 113 fixtures) | idem | pasta desconhecida, vazio, relativo sem base, expansão que esvazia | passou |
| HK3-02: `-C` seguido de palavra que a expansão esvazia recusa | idem (7 fixtures `pasta-barra-dash-c-com-*`, `-substituicao-*`) | palavra vazia desloca argumento | passou (fechado desde 77b539d) |
| HK3-03: `cd` em condição (`if`, `elif`, `while`, `until`, `!`, `time`, `function`) deixa a pasta desconhecida | idem (`pasta-barra-cd-em-condicao-de-if`, `-de-elif`, `-de-while`, `-de-until`, `-depois-de-exclamacao`, `-depois-de-time`, `-em-function-com-chaves`, `-em-condicao-de-if-e-merge-depois`) e sondas próprias (rc=2) | `cd` em posição que o hook não lê | passou (HK3-03 fechado em 8f70137), salvo `time -p` e atribuição prefixada (A1, bloqueante) |
| `popd` e a troca de branch em outra pasta (Q16, Q14 do parecer anterior) | idem (`pasta-barra-popd-depois-de-cd-absoluto`, `pasta-barra-switch-em-outra-pasta-...`) | guarda de pasta com teste | passou: M99 e M100 morrem |
| Merge e pull de integração sem parecer continuam barrados (`-C`, `cd`, `-C` repetido, `~/..`, barra final, `--no-ff -m`, `pull`, `pull --rebase`, `checkout` e `switch` seguidos de merge na integração) | sondas próprias (lista5, 75 comandos), rc=2 "nenhum parecer" ou "não resolve" | integração | passou |
| O par do brief passa: `cd <wt> && git pull --rebase origin melhoria/x && git push origin HEAD:refs/heads/melhoria/x`, `cd ~/wtx`, `-C ~/wtx`, `-C <wt> merge` | sondas próprias, rc=0 | falso positivo | passou |
| Cada guarda de pasta tem teste que a derruba | 15 specs (72 mutantes) todos mortos; 5 mutantes meus (Q17 a Q21) sobre as guardas novas | guarda sem teste | passou (Q19 equivalente, A3) |

## Cenários e resultado real
- Corpus: `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 1 test in 3.235s`, `OK`, 129 fixtures `pasta-*` verificadas (mínimo 50 na guarda de suíte vazia).
- Mutantes declarados, as 15 specs numa só rodada: `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1,...,15}.json`: `rc=0`, 72 mutantes, todos `morreu`, nenhum sobrevivente; última linha `M112 · morreu · hooks/parecer.py:224` (log `$TMPDIR/qa-engineer-hk3-parecer-pasta/mut4.log`).
- Conferência da lista contra o diff: as linhas de guarda mudadas na volta 3 (`hooks/parecer.py:60` `CONDICAO`, `sem_condicao` linhas 223-224 e a condição do `popd` e do `cd` na linha 563) têm mutante: M99 (`popd`), M101 e M102 (`cd` de condição), M103 a M110 (cada palavra de `CONDICAO`, `function NOME`) e M111, M112 (`CORPO`). Somei 5 mutantes meus (`$TMPDIR/qa-engineer-hk3-parecer-pasta/q-r4.json`): `bin/forge-mutante q-r4.json` rc=1 só por Q19.
  - morreu: Q17 (`pushd` fora da zera-pasta, linha 563), Q18 (troca de branch em pasta desconhecida sem marcar desvio, 582), Q20 (`cd` não solto resolve a pasta, 568), Q21 (`cd` sozinho não vai ao HOME, 568).
  - sobreviveu: Q19 (`function` fora de `ABRE`, linha 62): equivalente aceito pelo QA, `sem_condicao` já zera a pasta no `cd` da função e fora dela só muda de recusa para recusa (A3).
- Vermelho antes do verde (rodado por mim, rc=0): `bin/forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_hooks_parecer_pasta`: `vermelho: base=ff3936ae4011 head=4ae417ecff39 módulos=test_hooks_parecer_pasta (restrito por --modulos)`; `revertidos à base: bin/forge-testes, changelog.d/hk3-parecer-pasta.md, docs/engineering/achados-recorrentes.md, ...`; `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=falha · prova (asserção)`; `contagem: prova (asserção)=1`.
- Sondas próprias (HEAD de integração em `proj`, worktree `home/wtx` em `melhoria/x`; `p2/lista5.sh`, `lista6.sh`, `extras.sh`, `extras2.sh`, cerca de 175 comandos): fora o A1 e o A2, os contornos de pasta do modelo ficam barrados (rc=2). `coproc cd P` passa e é correto (roda em subshell, o merge vale a worktree); `if true; then :; fi; git merge` passa e é correto (sem `cd`).
- Regressão contra a base `ff3936a`: `time -p ...`, `time git merge` e `env git merge` dão rc=0 na base e no head: contorno herdado, não regressão.
- Suíte completa: não rodada por mim (o brief a limita ao pre-push); rodei o módulo do item, o `forge-mutante` (15 + 1 specs) e o vermelho.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 (`pasta-do-git-diferente-do-bash`) e AR-2 (`cd-escondido-por-involucro`) já gravadas pelo review. O A1 e o A2 deste parecer são da classe da AR-2 (o `cd` ou o `git` escondido por um envoltório: `time -p`, `env`, `builtin`); não gravei linha (só o review grava, decisão de 12:52).
- Bugs: `HK3-01` e `HK3-02` fechados em 77b539d, `HK3-03` fechado em 8f70137 (o arquivo ainda diz "alta", fica como histórico); `docs/qa/bugs/HK3-04-cd-depois-de-time-p-ou-atribuicao-passa.md` aberto, alto (A1).
