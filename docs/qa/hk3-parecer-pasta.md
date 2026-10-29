---
tipo: qa
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 94ea85b06b8cdc8645d38e61b98df4bed9899858
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: hk3-parecer-pasta (PR A do HK3: o hook parecer resolve a pasta do git), revalidação do merge da develop 3b94791

Plano: pedido de correção do controle do Forge, sem especificação de UX; as obrigações são as decisões técnicas de 10:40, 11:49 e 12:56 (pasta só literal; o que o hook não resolve recusa) e os casos P e B de `docs/security/hk3-parecer-ameacas.md` (em `~/.forge-contrib/docs/security/`). Teste de abuso: o corpus `pasta-*` (140 fixtures: 17 `passa`, 123 `barra`) e as 16 specs de mutantes. Revalidação do parecer anterior (7f0ce80, sobre 4ae417e): escopo incremental sobre `4ae417e..79d0f6f` (`hooks/parecer.py` +9 -3, só `sem_condicao`; fixtures novas de `cd` em condição com `time -p`, `--` e atribuição, uma fixture `passa` nova, spec 16 com M113 a M119).

## Achados
- A1 (recomendado) hooks/parecer.py:581 · envoltório antes do `git` ou do `cd` passa (rc=0), igual na base: `time -p git -C P merge`, `time git merge`, `env git merge`, `builtin cd P`, `command cd P`; ofuscação do pedido, mantida (AR-8, gravada pelo review)
- A2 (recomendado) hooks/parecer.py:62 · os mutantes Q19 (`function` fora de `ABRE`) e Q23 (`startswith("t")` na linha 224) sobrevivem e são equivalentes: Q19 só antecipa a recusa; Q23 só difere em `then -p cd P`, shell inválido; sem teste novo
- A3 (recomendado) hooks/parecer.py:183 · `analisar` ainda calcula `pasta` e devolve `parte[1]`, que `conferir` já não usa: código morto (herdado do A5 do parecer da volta 2)

## Detalhe dos achados
- Nenhum bloqueante. Fechado pela volta 4: o A1 do parecer anterior (bug HK3-04, `cd` depois de `time -p`, `time --` e de atribuição prefixada em condição). `time -p cd P`, `time -- cd P`, `time -p -- cd P`, `time -p -p cd P`, `time -p time -p cd P`, `time -p A=1 cd P`, `time -p A=1 B=2 cd P`, `if A=1 cd P`, `if A=1 B=2 C=3 cd P` (com `pull`), `! A=1 cd P`, `while A=1 cd P`, `while ! time -p cd P`, `until time -p cd P`, `elif A=1 cd P`, `if ! A=1 time -p cd P`, `time -p A=1 pushd P`, `{ time -p cd P; }` e `time -p cd P && git merge` seguidos de merge ou pull dão rc=2 "não resolve" (sondas próprias `p2/extras2.sh`, `extras3.sh` e 23 formas novas); o controle `A=1 cd P; git merge` segue rc=2 "nenhum parecer" (pasta resolvida, integração sem parecer).
- Sem falso positivo novo: `time -p git merge` e `A=1 git merge` na worktree de trabalho passam (rc=0), e a fixture `pasta-passa-opcao-sem-time-nao-e-do-time` guarda que a opção só sai depois do `time`. `time -p cd W; git pull --rebase ...` e `if A=1 cd W; then git merge ...; fi` (W = worktree) recusam como pasta desconhecida: lado seguro do modelo, aceito pela decisão de 12:56 (`cd` fora do nível de cima não é lido).
- A1: lista5 e lista6 (cerca de 150 comandos) sem mudança de resultado desde o parecer anterior: os rc=0 restantes são os esperados (par do brief, `cd`/`-C` na worktree, `coproc`, `if true; then :; fi; git merge`) e os do A1 (envoltórios).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P: `cd` literal, `pull --rebase` e push na worktree, `-C` com `~`, `-C` repetido relativo, expansão depois do subcomando, gh depois de pushd, `cd` e `-C` com til, `if` sem `cd`, opção sem `time` (`pasta-passa-*`, 17 fixtures) | `PastaDoGit.test_corpus_pasta_passa_e_barra` | permissão: a pasta resolvida vale a branch dela | passou |
| B: pasta só literal; `-C`, `cd`, `-C` repetido, `--git-dir`, `--work-tree`, `GIT_DIR`, pushd, popd, `cd` em subshell, bloco, pipeline, segundo plano, `&&`/`\|\|` condicional, variável, crase, `$( )`, HOME, CDPATH, atribuição, export, read, printf -v (`pasta-barra-*`, 123 fixtures) | idem | pasta desconhecida, vazio, relativo sem base, expansão que esvazia | passou |
| HK3-02: `-C` seguido de palavra que a expansão esvazia recusa | idem (`pasta-barra-dash-c-com-*`, `-substituicao-*`) | palavra vazia desloca argumento | passou (fechado desde 77b539d) |
| HK3-03: `cd` em condição (`if`, `elif`, `while`, `until`, `!`, `time`, `function`) deixa a pasta desconhecida | idem (`pasta-barra-cd-em-condicao-*`, `-depois-de-exclamacao`, `-depois-de-time`, `-em-function-com-chaves`) e sondas próprias | `cd` em posição que o hook não lê | passou (fechado em 8f70137) |
| HK3-04: `time -p`, `time --` e atribuição antes do `cd` em condição deixam a pasta desconhecida | idem (`pasta-barra-cd-condicao-time-p`, `-time-dash-dash`, `-time-p-dash-dash`, `-time-atribuicao`, `-negacao-time-p`, `-if-atribuicao`, `-if-negacao-atribuicao`, `-negacao-atribuicao`, `-while-atribuicao`, `-if-atribuicao-pushd`) e 23 sondas próprias (rc=2) | opção do `time` e atribuição como palavra de abertura | passou (fechado em 374f834) |
| `popd` e troca de branch em outra pasta | idem (`pasta-barra-popd-depois-de-cd-absoluto`, `pasta-barra-switch-em-outra-pasta-...`) | guarda de pasta com teste | passou (M99, M100 morrem) |
| Merge e pull de integração sem parecer continuam barrados (`-C`, `cd`, `-C` repetido, `~/..`, barra final, `--no-ff -m`, `pull`, `pull --rebase`, `checkout`/`switch` seguidos de merge na integração) | sondas próprias (lista5, lista6), rc=2 | integração | passou |
| O par do brief passa: `cd <wt> && git pull --rebase origin melhoria/x && git push origin HEAD:refs/heads/melhoria/x`, `cd ~/wtx`, `-C ~/wtx`, `-C <wt> merge` | sondas próprias, rc=0 | falso positivo | passou |
| Cada guarda de pasta tem teste que a derruba | 16 specs (79 mutantes) todos mortos; 2 mutantes meus (Q22, Q23) sobre `sem_condicao` | guarda sem teste | passou (Q23 equivalente, A2) |

## Revalidação do merge da develop 3b94791 (head d81e848)
Delta `79d0f6f..d81e848`: merge sem conflito; `hooks/parecer.py` não mudou (o delta é de `bin/`, testes e specs da develop). Rodei só o que o brief manda, sobre d81e848:
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_pre_push_parecer`: `Ran 21 tests in 19.520s`, `OK` (o corpus `pasta-*` inclui os 140 fixtures).
- `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1..16}.json`: `rc=0`, 79 mutantes `morreu`, nenhum sobrevivente (log `$TMPDIR/qa-engineer-hk3-parecer-pasta/mut7b.log`; a primeira tentativa estourou 550 s de espera minha, rc=124, e foi refeita sem esse prazo).
- Citações AR atualizadas para a numeração do merge (AR-1 a AR-6 da develop; AR-7 e AR-8 do PR A). Sem achado novo; as seções abaixo valem como estavam (volta 4, sobre 79d0f6f).

## Cenários e resultado real
- Corpus: `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 1 test in 3.203s`, `OK`, 140 fixtures `pasta-*` (mínimo 50 na guarda de suíte vazia).
- Mutantes declarados, as 16 specs numa só rodada: `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1..16}.json`: `rc=0`, 79 mutantes, todos `morreu`, nenhum sobrevivente; M113 a M119 (as 7 guardas de `sem_condicao`: atribuição, `-p`, `--`, opção só depois do `time`, `time` persistente, `time` liga a opção, laço até o fim) todos `morreu` (log `$TMPDIR/qa-engineer-hk3-parecer-pasta/mut5.log`).
- Conferência da lista contra o diff: as linhas de guarda mudadas na volta 4 (`hooks/parecer.py:223` laço, `224` `no_time`, `227` atribuição e opções do `time`) têm mutante (M119, M117 e M118, M113 a M116). A linha 229 (`else: break`) não tinha; somei Q22 (`else: k += 1`): `morreu`. Q23 (`startswith("t")`): `sobreviveu`, equivalente aceito pelo QA (A2). Spec própria: `$TMPDIR/qa-engineer-hk3-parecer-pasta/q-r5.json`, `bin/forge-mutante` rc=1 só por Q23.
- Vermelho antes do verde (rodado por mim, rc=0): `bin/forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_hooks_parecer_pasta`: `vermelho: base=ff3936ae4011 head=79d0f6f24a8a módulos=test_hooks_parecer_pasta (restrito por --modulos)`; `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=falha · prova (asserção)`; `contagem: prova (asserção)=1`.
- Regressão contra a base `ff3936a`: `time -p git ... merge`, `time git merge`, `env git merge` e `builtin cd` dão rc=0 na base e no head: contorno herdado, não regressão (A1).
- Suíte completa: não rodada por mim (o brief a limita ao pre-push); rodei o módulo do item, o `forge-mutante` (16 + 1 specs) e o vermelho.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-7 (`pasta-do-git-diferente-do-bash`) e AR-8 (`cd-escondido-por-involucro`) gravadas pelo review (a AR-1 é da develop, `mascara-do-shell-esconde-codigo`, fora deste pedido); os achados residuais deste parecer (A1) são da classe da AR-8; não gravei linha (só o review grava, decisão de 12:52). Nenhuma classe nova.
- Bugs: `HK3-01`, `HK3-02`, `HK3-03` e `HK3-04` fechados (os arquivos em `docs/qa/bugs/` ficam como histórico); nenhum bug aberto.

## Revalidação do merge da develop 7a9d23c (head 94ea85b)
Delta `bb6eec4..94ea85b`: só `tests/test_erros_no_brief.py` (+1 -1: `test_aq1` olha as 6 primeiras linhas AR, não o total); o merge da develop 7a9d23c não mexeu em `hooks/parecer.py`. Citações AR atualizadas para AR-7 (`pasta-do-git-diferente-do-bash`) e AR-8 (`cd-escondido-por-involucro`); as AR-1 a AR-6 são da develop. Rodado sobre 94ea85b: `python3 -m unittest tests.test_erros_no_brief tests.test_hooks_parecer_pasta`: `Ran 43 tests in 11.178s`, `OK`. As 16 specs `hk3-parecer-pasta-*.json` não foram rodadas de novo (brief: já rodaram sobre bb6eec4, 79 mortos, relatório do autor; `hooks/parecer.py` não mudou no delta). Sem achado novo; os A1 a A3 acima seguem como recomendados.
