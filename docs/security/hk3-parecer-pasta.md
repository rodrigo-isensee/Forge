---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 4ae417ecff39652c5d439c294ad2e582cf81861f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: hk3-parecer-pasta (HK3-PARECER, PR A, E1 e E3), volta 3

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...4ae417ecff39652c5d439c294ad2e582cf81861f`. Revalidação por delta sobre o parecer `f4bd012` (`forge-check delta --parecer`, intervalo `77b539d..4ae417e`). O delta traz:
- `hooks/parecer.py` +15 -4: `CONDICAO` (`:60`), `sem_condicao` (`:219-225`) e, em `conferir` (`:562-564`), três casos que deixam a pasta desconhecida: o `cd` depois de palavra de condição ou de corpo, o `pushd` e o `popd`.
- 11 fixtures `pasta-*` novas, as specs de mutantes 14 e 15 e o ajuste da 3.

Requisito: o modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E1 e E3) e a DECISÃO TÉCNICA de 2026-10-28 12:56. Por ela, o `cd` só muda a pasta no nível de cima da linha; qualquer outra forma deixa a pasta desconhecida.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão R-REVIEW/R-QA na entrada da integração). A mudança não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A10 (bloqueante) hooks/parecer.py:224 · requisito (DECISÃO TÉCNICA 12:56), parcial: `time -p cd`, `time -- cd`, `time -p -- cd` e `! time -p cd` a partir da worktree passam (rc=0) e o bash mescla na integração; `sem_condicao` não tira as opções do `time`
- A13 (bloqueante) hooks/parecer.py:562 · requisito (DECISÃO TÉCNICA 12:56): `cd` com atribuição prefixada depois da palavra de condição (`if A=1 cd`, `while A=1 cd`, `! A=1 cd`, `time A=1 cd`, `if A=1 pushd`) passa (rc=0); `sem_atribuicoes` roda antes de `sem_condicao`, e não depois
- A7 (recomendado) hooks/parecer.py:561 · gh pr com pasta não resolvida (pushd, cd fora do nível de cima) usa o cwd da sessão; igual na base
- A8 (recomendado) hooks/parecer.py:63 · source e . e os invólucros (env, env -C, command, builtin cd, exec git, função chamada) não tornam a pasta nem o GIT_DIR desconhecidos; igual na base; cartão próprio
- A11 (recomendado) hooks/parecer.py:63 · CDPATH e HOME por nameref (`declare -n`) não tornam a pasta desconhecida; igual na base; ofuscação, fora do lote
- A12 (recomendado) hooks/parecer.py:263 · falso positivo, lado seguro: `cd <wt literal> 2>/dev/null && git pull --rebase origin <b>` recusa porque o redirecionamento conta como argumento do cd
- A14 (recomendado) hooks/parecer.py:521 · o merge na posição de condição (`if git -C <integração> merge ...`, `! git ... merge`, `time git ... merge`) não é analisado e passa (rc=0); igual na base; cartão próprio
- A15 (recomendado) hooks/parecer.py:205 · falso positivo, lado seguro: `if true; then echo; fi; cd <wt>; git pull --rebase origin <b>` a partir da integração recusa (na base, rc=0), porque o `aberto` de `soltos` não fecha no `fi`

## Revalidação dos achados anteriores
**A10 (cd na condição de bloco, depois de `function`, `!` e `time`): parcial.** As formas listadas no parecer `f4bd012` recusam agora (rc=2 em `4ae417e`; na base, rc=0):
- `if cd <integração>; then git merge melhoria/x; fi` e `if cd <integração>; then :; fi; git merge melhoria/x`
- `elif cd`, `while cd`, `until cd`, `until ! cd`, `! cd` e `time cd`
- `function f { cd <integração>; }; f; git merge melhoria/x`

As variantes também recusam:
- `! ! cd`, `! time cd`, `time ! cd`, `if ! cd` e `while ! cd`
- `if { cd ...; }` e `if ( cd ... )`
- `if` com quebra de linha antes e depois do `cd`
- `function f() {` e `function f` com o `{` na linha seguinte
- `if` dentro de `{ }` e dentro de outro `if`
- `if cd ... && true`, `if true && cd` e `if cd -P`
- `! pushd`, `if pushd` e `popd`
- o `pull --rebase` no lugar do merge

Falta a opção do `time` (ver o A10 no detalhe). A correção mínima do `f4bd012` já pedia "`time` (com `-p`)".

**Sem regressão contra a base.** As 85 sondas das voltas anteriores (`sondas3/p1.json` e `p2.json`) rodaram de novo contra `4ae417e`. As que mudaram foram todas de rc=0 para rc=2, e são formas do A10. Nas 57 sondas novas (`sondas4/p4.json`), as diferenças contra a base são de dois tipos: formas do A10 que agora recusam e o falso positivo A15.

**Legítimos do modelo, rc=0:**
- `cd <wt> && git pull --rebase origin <b> && git push origin HEAD:refs/heads/<b>`, e a mesma linha com `;` e com quebra de linha
- `git -C <wt> pull --rebase origin <b>` e `git -C <wt> merge develop`
- na worktree: `cd src && git merge`, `if true; then :; fi; git merge`, `time git merge`, `! true; git merge`, `while false; do :; done; git merge`, `if true; then git merge; fi` e `function f { echo; }; f; git merge`

A suíte do item (`python3 -m unittest tests.test_hooks_parecer_pasta`) dá OK.

## Detalhe dos achados
Sondas: `$TMPDIR/security-engineer-hk3-parecer-pasta/sondas4/`.
- `gen4.py` e `gen5.py` geram `p4.json` e `p5.json`. Eles rodam com `../sondas/sonda.py` sobre a fixture do corpus: `proj` em `develop` e a worktree `home/wtx` em `melhoria/x`, sem parecer. "Integração" é `proj`.
- As saídas da branch estão em `novo-p*.txt`; as da base (`sondas3/base`, `ff3936a`), em `base-p*.txt`.
- Os efeitos no bash foram conferidos à parte. Imprimem `/tmp`: `bash -c 'time -p cd /tmp; pwd'`, `time -- cd /tmp`, `if A=1 cd /tmp; then :; fi` e `! A=1 cd /tmp`.

**A10 · opções do `time` (bloqueante, requisito, parcial).** Classe (PA-7): `pasta-do-git-diferente-do-bash` (AR-1).
- Evidência: `sem_condicao` (`hooks/parecer.py:222-225`) tira o `time` e para em `-p` ou `--`. O comando que sobra não começa por `cd`, e a pasta continua a da worktree.
- Sondas a partir da worktree, todas com rc=0 em `4ae417e` (igual na base): `time -p cd <integração>; git merge melhoria/x`, `time -- cd <integração>; ...`, `time -p -- cd <integração>; ...` e `! time -p cd <integração>; ...`. O bash roda o `cd` no shell de fora e mescla na integração sem parecer.
- Caminho de ataque: erro honesto de um agente que mede o `cd` com `time -p`. Severidade: baixa, porque o envio segue barrado pelo pre-push e pela proteção de branch.
- Correção mínima: em `sem_condicao`, tirar também o `-p` e o `--` que vêm depois de `time`. Pelo lado seguro, pode tirar qualquer palavra começada por `-` logo depois de `time`.
- Fixtures: `pasta-barra-cd-depois-de-time-p.json` e `pasta-barra-cd-depois-de-time-traco-traco.json`. Esforço: P. Dono: `tech-lead`.

**A13 · atribuição prefixada depois da palavra de condição (bloqueante, requisito).** Dimensão nova da matriz: condição × atribuição prefixada. Classe (PA-7): `pasta-do-git-diferente-do-bash` (AR-1).
- Evidência: em `conferir`, `sem = sem_atribuicoes(palavras)` (`:560`) tira as atribuições do início da parte. Mas, se a parte começa por `if`, a atribuição não está no início. Depois, `comando = sem_condicao(sem)` (`:562`) devolve `["A=1", "cd", P]`, e a conferência `comando[:1] == ["cd"]` falha.
- Sondas a partir da worktree, todas com rc=0 em `4ae417e` (igual na base): `if A=1 cd <integração>; then :; fi; git merge melhoria/x`, `while A=1 cd <integração>; do break; done; ...`, `! A=1 cd <integração>; ...`, `time A=1 cd <integração>; ...` e `if A=1 pushd <integração>; then :; fi; ...`.
- `if HOME=<integração> cd ~` e `if CDPATH=<integração> cd .` também passam no hook, mas no bash não chegam à integração: o `~` expande com o HOME antigo, e o `cd .` não usa o CDPATH. A mesma correção os cobre.
- No corpo do bloco, `{ A=1 cd ...; }` e `if :; then A=1 cd ...; fi` já recusam.
- Caminho de ataque e severidade: os mesmos do A10.
- Correção mínima: `comando = sem_atribuicoes(sem_condicao(sem))` em `:562`. Basta uma passada (condição, depois atribuições): com atribuição antes (`! A=1 time cd`), o `time` já é o programa externo, e o `cd` roda num processo filho, sem dano.
- Fixtures: `pasta-barra-cd-com-atribuicao-em-condicao-de-if.json` e `pasta-barra-cd-com-atribuicao-depois-de-exclamacao.json`. Esforço: P. Dono: `tech-lead`.

**A7, A8, A11, A12, A14 e A15 (recomendados, não devolvem).**
- A7: com a pasta desconhecida, `raiz_gh` (`:561`) usa o cwd da sessão. Correção: com a pasta desconhecida, `gh pr create`/`ready` sem `--head` recusa. P.
- A8: `source` e `.` estão em `LE_VARIAVEL` (`:63`) e não tornam o HOME nem o GIT_DIR desconhecidos. Também passam, igual na base: `env -C`, `command cd`, `builtin cd`, `exec git -C` e função chamada. Cartão próprio. M.
- A11: o nameref (`declare -n`) fica com a ofuscação, fora do lote.
- A12: `depois_do_cd` (`:263`) conta o redirecionamento como argumento. Fica do lado seguro. Correção: tirar `N>`, `N>>`, `>&N` e `<` dos argumentos antes de contar. P.
- A14: `analisar` recebe `sem_chaves(todas)` (`:521`), que tira `then`, `do`, `else` e `{`, mas não as palavras de condição. A partir da worktree, estas formas nem chegam a ser analisadas (rc=0, igual na base): `if git -C <integração> merge melhoria/x; then :; fi`, `! git -C <integração> merge ...` e `time git -C <integração> merge ...`. O problema não é a pasta: é o merge, que o hook não lê. Fica fora do requisito do PR A, mas a correção usa a função que este PR criou: passar `sem_condicao(todas)` em `:521`, com o A13 aplicado. P. Cartão próprio, ou junto com o A10 e o A13, se o dono preferir.
- A15: o `aberto` de `soltos` (`:205`) não fecha no `fi`, no `done` nem no `}`. Assim, qualquer bloco antes deixa de ser solto o `cd` do nível de cima. Fica do lado seguro e não tem impacto de segurança. O review e o QA julgam se é falso positivo contra a base. M.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. O A10 e o A13 precisam de correção ou de aceite do dono por `docs/security/aceites/`. Os recomendados não pedem aceite.

Ferramentas: só sondas locais e passivas (Python da biblioteca padrão, o `tests/test_hooks.py` do repositório, o bash e o git locais). Não houve rede, exploit nem sistema externo. `gitleaks`, `semgrep` e `zizmor` não se aplicam a este diff (só Python de hook e JSON de teste, sem segredo nem workflow) e não foram rodadas.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferida. A AR-1 (`pasta-do-git-diferente-do-bash`) é a classe do A10 e do A13. Pela DECISÃO TÉCNICA de 12:52, este parecer só cita a classe e não grava a linha.
