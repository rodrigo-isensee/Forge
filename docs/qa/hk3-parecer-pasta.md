---
tipo: qa
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 77b539d3fb3e9ebde40af8cf36942298c54d7e10
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hk3-parecer-pasta (PR A do HK3: o hook parecer resolve a pasta do git), volta 2

Plano: pedido de correção do controle do Forge, sem especificação de UX; as obrigações são as decisões técnicas de 10:40, 11:49 e 12:56 (pasta só literal; o que o hook não resolve recusa) e os casos P e B de `docs/security/hk3-parecer-ameacas.md` (em `~/.forge-contrib/docs/security/`). Teste de abuso: o corpus `pasta-*` (118 fixtures: 15 `passa`, 103 `barra`) e as 13 specs de mutantes. Revalidação do parecer anterior (090c220, sobre bfd9e70): escopo incremental sobre `bfd9e70..77b539d` (`hooks/parecer.py` reescrito para pasta só literal, specs 9 a 13, fixtures novas).

## Achados
- A1 (bloqueante) hooks/parecer.py:204 · `cd` na condição de `if`/`while` ou depois de `!` muda a pasta e o hook não o lê: `if cd P; then git merge melhoria/x; fi` passa (rc=0) com P na integração. Classe: cd em posição que o hook não lê (HK3-03)
- A2 (bloqueante) hooks/parecer.py:552 · guardas de pasta sem teste: mutantes Q16 (`popd`, linha 552) e Q14 (troca de branch na pasta resolvida, linha 568) sobrevivem e abrem contorno na cópia mutada. Classe: guarda de pasta sem mutante nem teste
- A3 (recomendado) hooks/parecer.py:552 · `builtin cd P`, `command cd P`, `env -C P git merge` e `git -C P merge $(echo x)` passam (rc=0): limitação de ofuscação do pedido, mantida
- A4 (recomendado) hooks/parecer.py:56 · mutantes Q2, Q6, Q8, Q11 e Q15 sobrevivem sem abrir contorno nas sondas; cada um é fixture que falta
- A5 (recomendado) hooks/parecer.py:183 · `analisar` ainda calcula `pasta` (linhas 183-184) e devolve `parte[1]`, que o `conferir` já não usa: código morto

## Detalhe dos achados
- A1: provado com `if cd P; then git merge melhoria/x; fi`, `if cd P; then :; fi; git merge melhoria/x`, `while cd P; do git merge melhoria/x; break; done` e `! cd P; git merge melhoria/x`, cwd = worktree em `melhoria/x`, P = integração (`develop`). A palavra de abertura vira a primeira da parte e `analisar` devolve None, então a pasta fica a da worktree. A decisão de 12:56 manda toda outra forma de `cd` deixar a pasta desconhecida. Na base `ff3936a` o resultado é o mesmo (rc=0): contorno que o PR A deveria fechar. Bug `HK3-03`.
- A2: Q16 `pushd P; pushd W; cd W; popd; git merge melhoria/x` passa (rc=0) na cópia mutada e recusa (rc=2) no head; Q14 `cd P; git -C W switch melhoria/y; git merge melhoria/x` idem. Falta fixture `pasta-barra-*` para cada uma. Mesma classe da volta 1 (A1 do QA e5ea17b).
- A3: registrar no PR B ou barrar `builtin` e `command` junto de `cd`.
- A4: Q2 (`&&` com quebra de linha no `SEGUE`, só muda mensagem), Q6 (`GIT_COMMON_DIR` fora de `DESVIOS`, o HEAD segue o da worktree), Q8 (`GIT_DIR` no ambiente da sessão, linha 68, que a chamada não controla), Q11 (`raiz_gh = hook.cwd()`, linha 551), Q15 (`cd ..` com CDPATH, só deixa mais estrito).
- Equivalentes aceitos pelo QA: Q4 (`if` fora de `ABRE`: `analisar` devolve None para a parte e `then` já abre o bloco; o buraco do `cd` da condição é o A1) e Q9 (linha 234: `split("=")` só difere com `=` na palavra, e a linha 232 já trata `NOME=valor`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P: `cd` literal, `pull --rebase` e push na worktree, `-C` com `~`, `-C` repetido relativo, expansão depois do subcomando, gh depois de pushd, `cd` e `-C` com til (`pasta-passa-*`, 15 fixtures) | `PastaDoGit.test_corpus_pasta_passa_e_barra` | permissão: a pasta resolvida vale a branch dela | passou |
| B: pasta só literal; `-C`, `cd`, `-C` repetido, `--git-dir`, `--work-tree`, `GIT_DIR`, pushd, `cd` em subshell, bloco, pipeline, segundo plano, `&&`/`\|\|` condicional, variável, crase, `$( )`, HOME, CDPATH, atribuição, export, read, printf -v (`pasta-barra-*`, 103 fixtures) | idem | pasta desconhecida, vazio, relativo sem base, expansão que esvazia | passou |
| HK3-02: `-C` seguido de palavra que a expansão esvazia (`$EMPTY`, `$(echo)`, `$(true)`, crase vazia, `$(echo -C P)`) recusa | idem (`pasta-barra-dash-c-com-variavel-vazia`, `-e-chaves`, `-com-substituicao-de-echo`, `-de-true`, `-com-crase-vazia`, `pasta-barra-substituicao-traz-o-dash-c`, `-vazia-antes-do-dash-c`) e sondas próprias: as 7 formas dão rc=2 | palavra vazia desloca argumento | passou (HK3-02 fechado) |
| Merge e pull de integração sem parecer continuam barrados (`-C`, `cd`, `-C` repetido, `~/..`, barra final, `--no-ff -m`, `pull`, `pull --rebase`, `checkout` e `switch` seguidos de merge na integração) | sondas próprias (lista5, 70 comandos), rc=2 "nenhum parecer" | integração | passou |
| O par do brief passa: `cd <wt> && git pull --rebase origin melhoria/x && git push origin HEAD:refs/heads/melhoria/x`, `cd ~/wtx`, `-C ~/wtx`, `-C <wt> merge` | sondas próprias, rc=0 | falso positivo | passou |
| `cd` fora do nível de cima ou em forma que o hook não lê deixa a pasta desconhecida | sondas próprias (lista6, 55 comandos): subshell, bloco, pipeline, `&`, `\|\|`, `&&` condicional, `for`, `case`, função, `eval`, `bash -c` rc=2; `if cd P`, `while cd P`, `! cd P` rc=0 | `cd` em condição | FALHOU (A1) |
| Cada guarda de pasta tem teste que a derruba | 13 specs (58 mutantes) todos mortos; mutantes meus Q1 a Q16 sobre as guardas sem mutante | guarda sem teste | FALHOU (A2: Q14, Q16) |

## Cenários e resultado real
- Corpus: `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 1 test in 3.159s`, OK, 118 fixtures `pasta-*` verificadas (mínimo 50).
- Mutantes declarados: `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1,...,13}.json`: rc=0, 58 mutantes, todos "morreu", nenhum sobrevivente (`$TMPDIR/qa-engineer-hk3-parecer-pasta/mut3.log`; última linha `M98 · morreu · hooks/parecer.py:145` e `rc=0`).
- Conferência da lista contra o diff: as linhas de guarda mudadas em `hooks/parecer.py` sem mutante eram 56, 59, 61, 62, 64, 68, 234, 256, 274, 551, 552, 553, 567 a 571; somei 16 mutantes meus (Q1 a Q16, duas specs em `$TMPDIR/qa-engineer-hk3-parecer-pasta/q-r2-{1,2}.json`): `bin/forge-mutante q-r2-1.json q-r2-2.json` rc=1.
  - morreu: Q1 (`&&` fora de `SEGUE`, linha 56), Q3 (`then` fora de `CORPO`, 59), Q5 (`read` fora de `LE_VARIAVEL`, 62), Q7 (`GIT_WORK_TREE` fora de `DESVIOS`, 64), Q10 (`-C` não segue o link, 274), Q12 (`pushd` não zera a pasta, 553), Q13 (troca de branch em pasta desconhecida, 571).
  - sobreviveu: Q2 (56), Q4 (61), Q6 (64), Q8 (68), Q9 (234), Q11 (551), Q14 (568), Q15 (256), Q16 (552). Q4 e Q9 são equivalentes (justificativa acima); Q14 e Q16 são o A2; Q2, Q6, Q8, Q11 e Q15 são o A4.
  - Prova do A2 na cópia mutada (hook de `$TMPDIR/qa-engineer-hk3-parecer-pasta/mq/q14` e `/q16`, com `bin/` copiado): head rc=2 nas duas sondas; q14 rc=0 em `cd P; git -C W switch melhoria/y; git merge melhoria/x`; q16 rc=0 em `pushd P; pushd W; cd W; popd; git merge melhoria/x`.
- Vermelho antes do verde (rodado por mim, rc=0): `bin/forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_hooks_parecer_pasta`: `vermelho: base=ff3936ae4011 head=77b539d3fb3e módulos=test_hooks_parecer_pasta (restrito por --modulos)`; `revertidos à base: bin/forge-testes, changelog.d/hk3-parecer-pasta.md, docs/engineering/achados-recorrentes.md, ...`; `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=falha · prova (asserção)`; `contagem: prova (asserção)=1`.
- Sondas próprias (HEAD de integração em `proj`, worktree `home/wtx` em `melhoria/x`, cerca de 125 comandos em `p2/lista5.sh` e `lista6.sh`): fora o A1, o A2 e o A3, os contornos de pasta do modelo ficam barrados (rc=2). Passam sem defeito (a pasta de verdade é a worktree ou o git falha): `git -C '' P merge`, `git -C$P merge` (o git recusa a opção colada), `git -C ~ merge` fora de repositório, `cd P; cd W; git merge`, `git -C P switch melhoria/x && git -C P merge develop`.
- Regressão contra a base `ff3936a` (sondas rodadas nos dois hooks): `if cd P`, `! cd P` e `builtin cd P` dão rc=0 na base e no head, não é regressão, é contorno que continua aberto; o resto da lista dá rc=2 no head.
- Suíte completa: não rodada por mim (o brief a limita ao pre-push); rodei o módulo do item, o `forge-mutante` (13 + 2 specs) e o vermelho.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 já registrada pelo review (`pasta-do-git-diferente-do-bash`, vezes: 2). A1 e A2 são da mesma classe (a pasta que o bash usa difere da que o hook calcula, e guarda de pasta sem teste); não gravei linha (só o review grava, decisão de 12:52).
- Bugs: `docs/qa/bugs/HK3-01-dash-c-com-crase-sem-aspas-passa.md` e `docs/qa/bugs/HK3-02-dash-c-com-palavra-vazia-desloca-a-pasta.md` (fechados em 77b539d) e `docs/qa/bugs/HK3-03-cd-na-condicao-de-if-passa.md` (aberto, alto; o A2 é lacuna de teste e vai só no parecer).
