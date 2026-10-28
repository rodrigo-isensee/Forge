---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 79d0f6f24a8af8753776651c896441e522309570
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: hk3-parecer-pasta (HK3-PARECER, PR A, E1 e E3), volta 4

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...79d0f6f24a8af8753776651c896441e522309570`. Revalidação por delta sobre o parecer `0a4e752` (`forge-check delta --parecer`, intervalo `4ae417e..79d0f6f`, DECISÃO TÉCNICA de 2026-10-28 16:31). O delta traz:
- `hooks/parecer.py` +11 -5: `sem_condicao` (`:219-231`) tira, em qualquer ordem, as palavras de condição e de corpo, as atribuições (`ATRIBUICAO`, `:67`) e, depois de um `time`, o `-p` e o `--`.
- 11 fixtures `pasta-*` novas (10 `pasta-barra-cd-condicao-*` e `pasta-passa-opcao-sem-time-nao-e-do-time.json`) e a spec de mutantes 16.

Requisito: o modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E1 e E3) e a DECISÃO TÉCNICA de 2026-10-28 12:56. Por ela, o `cd` só muda a pasta no nível de cima da linha; qualquer outra forma deixa a pasta desconhecida.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão R-REVIEW/R-QA na entrada da integração). A mudança não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A7 (recomendado) hooks/parecer.py:567 · gh pr com pasta não resolvida (pushd, cd fora do nível de cima) usa o cwd da sessão; igual na base
- A8 (recomendado) hooks/parecer.py:63 · source e . e os invólucros (env, env -C, command, builtin cd, exec git, função chamada) não tornam a pasta nem o GIT_DIR desconhecidos; igual na base; cartão próprio
- A11 (recomendado) hooks/parecer.py:63 · CDPATH e HOME por nameref (`declare -n`) não tornam a pasta desconhecida; igual na base; ofuscação, fora do lote
- A12 (recomendado) hooks/parecer.py:267 · falso positivo, lado seguro: `cd <wt literal> 2>/dev/null && git pull --rebase origin <b>` recusa porque o redirecionamento conta como argumento do cd
- A14 (recomendado) hooks/parecer.py:527 · o merge na posição de condição (`if git -C <integração> merge ...`, `! git ... merge`, `time git ... merge`) não é analisado e passa (rc=0); igual na base; cartão próprio
- A15 (recomendado) hooks/parecer.py:205 · falso positivo, lado seguro: `if true; then echo; fi; cd <wt>; git pull --rebase origin <b>` a partir da integração recusa (na base, rc=0), porque o `aberto` de `soltos` não fecha no `fi`
- A16 (recomendado) hooks/parecer.py:67 · atribuição com índice (`A[0]=1 cd <integração>`, `HOME[0]=<integração>; cd ~`, `GIT_DIR[0]=...; export GIT_DIR`) não é lida como atribuição e passa (rc=0); igual na base; ofuscação, junto do A11

## Revalidação dos achados anteriores
**A10 (opções do `time`): resolvido.** A partir da worktree, estas formas dão rc=2 em `79d0f6f` (rc=0 em `4ae417e` e na base):
- `time -p cd <integração>; git merge melhoria/x`, `time -- cd`, `time -p -- cd` e `! time -p cd`
- variantes: `time -p ! cd`, `! time -p -- cd`, `time -p A=1 cd` e `time -p cd <integração>; git pull --rebase origin melhoria/x`

**A13 (atribuição depois da palavra de condição): resolvido.** A partir da worktree, estas formas dão rc=2 em `79d0f6f` (rc=0 em `4ae417e` e na base):
- `if A=1 cd`, `while A=1 cd`, `! A=1 cd`, `time A=1 cd` e `if A=1 pushd`
- `if HOME=<integração> cd ~` e `if CDPATH=<integração> cd .`
- variantes: `if A=1 B=2 cd`, `if ! A=1 cd`, `until A=1 cd`, `elif A=1 cd`, `if A+=1 cd`, `A+=1 cd` no nível de cima e o `pull --rebase` no lugar do merge

**Nenhum contorno novo.**
- As 85 sondas das voltas 1 e 2 (`sondas3/p1.json` e `p2.json`) dão o mesmo resultado que em `4ae417e`.
- Nas 57 sondas da volta 3 (`sondas4/p4.json`) e nas 19 do A10 e do A13 (`p5.json`), as únicas mudanças contra `4ae417e` são de rc=0 para rc=2. Todas são formas do A10 e do A13.
- O `sem_condicao` só decide se o `cd`, o `pushd` ou o `popd` deixam a pasta desconhecida (`:568-570`). Tirar mais palavras só leva a pasta para desconhecida, e aí o merge ou o pull recusa. Não chega a resolver uma pasta errada.
- A única forma nova que passa é a atribuição com índice (A16). Ela passa igual na base e é ofuscação, que fica fora do lote pela DECISÃO TÉCNICA de 10:40 (Jarvis).

**Legítimos do modelo, rc=0:**
- a partir da integração: `cd <wt> && git pull --rebase origin <b> && git push origin HEAD:refs/heads/<b>`, `cd <wt>; time -p git pull --rebase ...`, `A=1 cd <wt>; git pull --rebase ...` e `git -C <wt> pull --rebase origin <b>`
- na worktree: `time -p git merge develop`, `time -p true; git pull --rebase ...` e `A=1 cd <wt>; git pull --rebase ...`, além dos legítimos da volta 3 (sem mudança)

A suíte do item (`python3 -m unittest tests.test_hooks_parecer_pasta`) dá OK.

## Detalhe dos achados
Sondas: `$TMPDIR/security-engineer-hk3-parecer-pasta/sondas5/`.
- `gen6.py` e `gen7.py` geram `p6.json` e `p7.json`. Eles rodam com `../sondas/sonda.py` sobre a fixture do corpus: `proj` em `develop` e a worktree `home/wtx` em `melhoria/x`, sem parecer. "Integração" é `proj`.
- As saídas da branch estão em `novo-p*.txt`; as da base (`sondas3/base`, `ff3936a`), em `base-p6.txt` e `base-p7.txt`.
- Os efeitos no bash foram conferidos à parte. Imprimem `/tmp`: `bash -c 'A[0]=1 cd /tmp; pwd'`, `if A[0]=1 cd /tmp; then :; fi; pwd` e `HOME[0]=/tmp; cd ~; pwd`.

**A16 · atribuição com índice (recomendado, ofuscação).** Dimensão nova da matriz: forma da atribuição × índice (`NOME[i]=`). Classe (PA-7): `pasta-do-git-diferente-do-bash` (AR-1).
- Evidência: `ATRIBUICAO` (`hooks/parecer.py:67`) e `depois_das_atribuicoes` (`hooks/_comum.py:1751`) não aceitam o `[i]` antes do `=`. Por isso o hook não vê o `cd` e não marca o HOME nem o GIT_DIR como mexidos.
- Sondas a partir da worktree, todas com rc=0 em `79d0f6f` e na base:
  - `A[0]=1 cd <integração>; git merge melhoria/x`
  - `if A[0]=1 cd <integração>; then :; fi; git merge melhoria/x`
  - `A[0]=1 pushd <integração>; git merge melhoria/x`
  - `HOME[0]=<integração>; cd ~; git merge melhoria/x` e `HOME[0]=<integração>; git -C ~ merge melhoria/x`
  - `GIT_DIR[0]=<integração>/.git; export GIT_DIR; git merge melhoria/x`
- O `CDPATH[0]=...; cd proj` já recusa (rc=2).
- Caminho de ataque: só quem escreve de propósito para enganar o hook. Um agente que segue o brief não escreve `A[0]=1 cd` nem `HOME[0]=`. Severidade: baixa, porque o envio segue barrado pelo pre-push e pela proteção de branch. O achado fica com a ofuscação, como o A11, e não devolve.
- Correção mínima: aceitar o índice nos dois padrões, `^([A-Za-z_]\w*)(\[[^]]*\])?\+?=` em `ATRIBUICAO` e o mesmo em `depois_das_atribuicoes`. Fixtures sugeridas: `pasta-barra-atribuicao-com-indice-antes-do-cd.json` e `pasta-barra-home-com-indice-e-cd-til.json`. Esforço: P. Dono: `tech-lead`, no cartão do A11.

**A7, A8, A11, A12, A14 e A15 (recomendados, não devolvem).** Nada mudou desde o parecer `0a4e752`; só as linhas foram atualizadas.
- A7: com a pasta desconhecida, `raiz_gh` (`:567`) usa o cwd da sessão. Correção: com a pasta desconhecida, `gh pr create`/`ready` sem `--head` recusa. P.
- A8: `source` e `.` estão em `LE_VARIAVEL` (`:63`) e não tornam o HOME nem o GIT_DIR desconhecidos. Também passam, igual na base: `env -C`, `command cd`, `builtin cd`, `exec git -C` e função chamada. Cartão próprio. M.
- A11: o nameref (`declare -n`) fica com a ofuscação, fora do lote.
- A12: `depois_do_cd` (`:267`) conta o redirecionamento como argumento. Fica do lado seguro. Correção: tirar `N>`, `N>>`, `>&N` e `<` dos argumentos antes de contar. P.
- A14: `analisar` recebe `sem_chaves(todas)` (`:527`), que não tira as palavras de condição. Dentro de `then` e de `{ }`, o merge já recusa (rc=2). Mas `if`, `!` e `time` na condição seguem sem análise (rc=0), igual na base. Correção: passar `sem_condicao(todas)` em `:527`, que já tira as atribuições e as opções do `time`. P. Cartão próprio.
- A15: o `aberto` de `soltos` (`:205`) não fecha no `fi`, no `done` nem no `}`. Fica do lado seguro e não tem impacto de segurança. M.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Não há bloqueante, e os recomendados não pedem aceite.

Ferramentas: só sondas locais e passivas (Python da biblioteca padrão, o `tests/test_hooks.py` do repositório, o bash e o git locais). Não houve rede, exploit nem sistema externo. `gitleaks`, `semgrep` e `zizmor` não se aplicam a este diff (só Python de hook e JSON de teste, sem segredo nem workflow) e não foram rodadas.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferida. A AR-1 (`pasta-do-git-diferente-do-bash`) é a classe do A10, do A13 e do A16. Pela DECISÃO TÉCNICA de 12:52, este parecer só cita a classe e não grava a linha.
