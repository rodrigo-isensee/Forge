---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 77b539d3fb3e9ebde40af8cf36942298c54d7e10
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: hk3-parecer-pasta (HK3-PARECER, PR A, E1 e E3), volta 2

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...77b539d3fb3e9ebde40af8cf36942298c54d7e10`. Revalidação por delta sobre o parecer `4598630` (`forge-check delta --parecer`, intervalo `bfd9e70..77b539d`). O delta traz:
- `hooks/parecer.py` +102 -128: o hook deixa de seguir variável (`expande`, `globais`, `soltos` com `COMECA`, `sem_chaves`, `mexidas_na_linha`); o `resolver` confere o `isdir` do caminho cru e usa `realpath` no `-C`; o `cd` não solto deixa a pasta desconhecida.
- fixtures `pasta-*` novas e as specs de mutantes 9 a 13.

Requisito: o modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E1 e E3) e a DECISÃO TÉCNICA de 2026-10-28 12:56. Ela pede a pasta só literal e o `cd` só no nível de cima da linha; qualquer outra forma deixa a pasta desconhecida.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão R-REVIEW/R-QA na entrada da integração). A mudança não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A10 (bloqueante) hooks/parecer.py:59 · requisito (DECISÃO TÉCNICA 12:56), critério mudou: a regra tornou requisito que o cd em bloco deixe a pasta desconhecida; `if cd`, `elif cd`, `while cd`, `until cd`, `! cd`, `time cd` e `function f { cd` a partir da worktree passam (rc=0) e o bash mescla na integração
- A7 (recomendado) hooks/parecer.py:551 · gh pr com pasta não resolvida (pushd, cd fora do nível de cima) usa o cwd da sessão; igual na base
- A8 (recomendado) hooks/parecer.py:62 · source e . e os invólucros (env, env -C, command, builtin cd, exec git, função chamada) não tornam a pasta nem o GIT_DIR desconhecidos; igual na base; cartão próprio
- A11 (recomendado) hooks/parecer.py:62 · CDPATH e HOME por nameref (`declare -n R=CDPATH; R=<integração>`) não tornam a pasta desconhecida (rc=0, igual na base); ofuscação, fora do lote; o for/select já recusa
- A12 (recomendado) hooks/parecer.py:253 · falso positivo novo, lado seguro: `cd <wt literal> 2>/dev/null && git pull --rebase origin <b>` a partir da integração recusa (rc=2; na base rc=0), porque o redirecionamento conta como argumento do cd; `>/dev/null` passa

## Revalidação dos achados anteriores
- **A3 (cd fora do shell de fora): resolvido.** A partir da integração, dão rc=2 em `77b539d`: `(cd <wt>); git merge`, `cd <wt> | true; git merge` e `cd <wt> & git merge`, nas formas literal e com variável. Na base, a forma literal dava rc=0, e agora também fecha.
- **A4 (atribuição ou cd depois de `&&`/`||`): resolvido.** Dão rc=2: `W=<integração>; test -d /nao && W=<wt>; cd $W && git merge`, `test -d /nao && cd <wt>; git merge` e `false || cd <wt>; git merge`. As duas últimas davam rc=0 na base.
- **A5 (`nao/..`): resolvido.** Dão rc=2: `cd <wt>/nao/..; git merge`, a forma com variável e `git -C <wt>/nao/.. merge`. A literal dava rc=0 na base. O `-C` usa `realpath`, e o `cd` usa o caminho lógico depois do `isdir` do caminho cru, como fazem o git e o bash.
- **A9 (`$` que o bash não expande): resolvido pela regra nova.** Dão rc=2: `cd \$W`, a forma com quebra de linha, `cd \${W}`, `cd "$"W`, `cd $\W` e `cd "$"{W}`. Qualquer `$` ou crase que sobra na palavra deixa a pasta desconhecida (`expande`).
- **A10 (cd depois de palavra-chave): parcial.** Agora recusam (rc=2): `if :; then cd <integração>; fi`, `{ cd <integração>; }`, `for d in 1; do cd <integração>; done`, `select`, `case` e `f() { cd <integração>; }`. Na base, os quatro primeiros davam rc=0. Falta o `cd` na posição de condição e depois de `function NOME {`, `!` e `time` (ver o detalhe).
- **A11 (for/select e nameref): parcial.** Dão rc=2: `for CDPATH in <integração>; do :; done; cd src && git merge` e `for HOME in ...; cd ~`. O nameref fica, como recomendado.

**Regra da DECISÃO TÉCNICA de 12:56, sem contorno novo.** 85 sondas (`p1.json` e `p2.json`) rodaram contra o hook de `77b539d` e contra o da base `ff3936a`. Nenhuma forma que recusa na base passa na branch: não há regressão de segurança contra a base.
- **Recusam:** o `-C` e o `cd` com variável, crase, `$( )`, `$'…'`, glob (`<integração>*`) ou chaves (`{<integração>,}`); o `~` com o HOME mexido na linha (`HOME=`, `export HOME=`, `unset HOME`, `for HOME in`); `--git-dir` (com `=` e separado), `--work-tree`, `-c core.worktree=` e `GIT_DIR=`.
- **São julgados pela pasta certa:** o `-C` repetido (`-C <integração> -C .`, `-C '' -C <integração>`) e o `-C` depois de `-P` ou de `--no-pager`. `source /dev/null; cd ~` continua resolvido com o HOME da sessão.
- **Passam sem dano:** `git -C<pasta>` colado passa no hook, mas o git o recusa ("unknown option"). Barra invertida e aspas parciais em caminho literal (`cd ''<integração>`, `cd "<integração>"`) dão o mesmo caminho no `shlex` e no bash, então resolvê-los não abre contorno.
- **Legítimos do modelo, rc=0:** `cd <wt> && git pull --rebase origin <b> && git push origin HEAD:refs/heads/<b>`, a mesma linha com `;` e com quebra de linha, `git -C <wt> pull --rebase origin <b>`, `git -C <wt> merge develop` e `cd src && git merge` na worktree.

A suíte do item (`python3 -m unittest tests.test_hooks_parecer_pasta`) dá OK.

## Detalhe dos achados
Sondas: `$TMPDIR/security-engineer-hk3-parecer-pasta/sondas3/`. `gen.py` e `gen2.py` geram `p1.json` e `p2.json`, que rodam com `../sondas/sonda.py` sobre a mesma fixture do corpus: `proj` em `develop` e a worktree `home/wtx` em `melhoria/x`, sem parecer. As saídas da branch estão em `novo-p1.txt` e `novo-p2.txt`, e as da base em `base-p1.txt` e `base-p2.txt` (a base foi extraída por `git archive` em `sondas3/base/`). "Integração" é `proj`.

**A10 · cd na condição de bloco e depois de `function`, `!` e `time` (bloqueante, requisito).**

Critério mudou. No parecer `4598630`, o A10 era recomendado: ninguém tinha pedido o `cd` em bloco. A DECISÃO TÉCNICA de 12:56 o tornou requisito: "o `cd` está no nível de cima da linha (fora de subshell, pipeline, segundo plano, `&&` ou `||` condicionais e blocos); qualquer outra forma deixa a pasta desconhecida". O delta cumpriu a regra para o corpo do bloco (`CORPO`, `:59`, e `sem_chaves`, `:210`). Não a cumpriu para a palavra que abre o bloco nem para os prefixos do pipeline.

Evidência: `analisar` recebe `["if", "cd", P]` e devolve None, porque a primeira palavra não é `cd`. A pasta continua a de antes, quando deveria ficar desconhecida. Sondas a partir da worktree, todas com rc=0 em `77b539d` (igual na base, então não é regressão):
- `if cd <integração>; then git merge melhoria/x; fi`
- `if cd <integração>; then :; fi; git merge melhoria/x`
- `if true; then :; elif cd <integração>; then git merge melhoria/x; fi`
- `while cd <integração>; do git merge melhoria/x; break; done`
- `until ! cd <integração>; do :; done; git merge melhoria/x`
- `! cd <integração>; git merge melhoria/x`
- `time cd <integração>; git merge melhoria/x`
- `function f { cd <integração>; }; f; git merge melhoria/x` (a forma `f() { cd ...; }` já recusa)

Em todas, o bash roda o `cd` no shell de fora e mescla na integração sem parecer.

Caminho de ataque: erro honesto de um agente que escreve o `cd` como condição (`if cd X; then ...`) a partir do cwd da sessão. Severidade: baixa, porque o envio segue barrado pelo pre-push e pela proteção de branch. Mesmo assim, é o requisito do controle.

Correção mínima:
- Em `sem_chaves` (`:210`), tirar também as palavras que abrem bloco ou pipeline antes do comando: `if`, `elif`, `while`, `until`, `then`, `do`, `else`, `{`, `!`, `time` (com `-p`) e `function NOME` (com o `{` seguinte).
- Em `soltos` (`:198`), o comando que começa por qualquer uma delas não é solto. `!` e `time` não estão em `ABRE` e precisam entrar na conta.

Assim o `cd` é visto e, por não ser solto, deixa a pasta desconhecida. `coproc cd` roda em subshell e não faz dano.

Fixtures: uma por forma da lista acima, `pasta-barra-cd-em-condicao-de-*`. Esforço: P. Dono: `tech-lead`. Classe (PA-7): `pasta-do-git-diferente-do-bash` (AR-1), a mesma que se repete neste pedido. Só o code review grava a linha AR (DECISÃO TÉCNICA de 12:52).

**A7, A8, A11 e A12 (recomendados, não devolvem).**
- A7: com a pasta desconhecida, `raiz_gh` (`:551`) usa o cwd da sessão. Correção: com a pasta desconhecida, `gh pr create`/`ready` sem `--head` recusa. P.
- A8: `source` e `.` estão em `LE_VARIAVEL` (`:62`) e não tornam o HOME nem o GIT_DIR desconhecidos. Também passam (rc=0, igual na base): `env -C <integração> git merge`, `command cd`, `builtin cd`, `exec git -C <integração> merge` e função chamada. É a classe vizinha da ofuscação e dos invólucros do M3. Cartão próprio. M.
- A11: o nameref (`declare -n`) liga um nome a outro. Fica com a ofuscação, fora do lote. O `for`/`select` foi resolvido.
- A12: `depois_do_cd` (`:253`) exige um argumento só, e o `shlex` entrega `2>/dev/null` como palavra. Por isso a forma legítima `cd <wt> 2>/dev/null && git pull --rebase origin <b>` passou a recusar (na base, rc=0). Não bloqueia aqui: fica do lado seguro e não tem impacto de segurança. O review e o QA julgam se é falso positivo contra a base. Correção: tirar os redirecionamentos (`N>`, `N>>`, `>&N`, `<`) dos argumentos do `cd` antes de contar. P.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. O A10 precisa de correção ou de aceite do dono por `docs/security/aceites/`. Os recomendados não pedem aceite.

Ferramentas: só sondas locais e passivas (Python da biblioteca padrão, o `tests/test_hooks.py` do repositório, o bash e o git locais). Não houve rede, exploit nem sistema externo. `gitleaks`, `semgrep` e `zizmor` não se aplicam a este diff (só Python de hook e JSON de teste, sem segredo nem workflow) e não foram rodadas.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferida. A AR-1 (`pasta-do-git-diferente-do-bash`) é a classe do A10. Pela DECISÃO TÉCNICA de 12:52, este parecer só cita a classe e não grava a linha.
