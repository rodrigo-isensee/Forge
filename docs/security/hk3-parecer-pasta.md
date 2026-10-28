---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 212203a39fd4419c45dd797ea0737b7d05001d19
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: hk3-parecer-pasta (HK3-PARECER, PR A, E1 e E3)

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...212203a39fd4419c45dd797ea0737b7d05001d19` (`hooks/parecer.py` +173 -29, 52 fixtures `pasta-*`, 4 specs de mutantes, `tests/test_hooks_parecer_pasta.py`, mapa do `bin/forge-testes`). Requisito: a regra que separa do modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, seções E1 e E3).

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão R-REVIEW/R-QA na entrada da integração). A mudança não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A1 (bloqueante) hooks/parecer.py:229 · requisito (regra "CDPATH com cd relativo recusa"): o CDPATH da linha por export, declare -x, read ou prefixo (CDPATH=x cd src) cai em `ruins` e é ignorado; o bash vai a <integração>/src e o merge passa (rc=0)
- A2 (bloqueante) hooks/parecer.py:216 · regressão (defeito provado): `$NOME` entre apóstrofos é substituído; com cwd na integração, W=<wt>; cd '$W'; git merge (ou quebra de linha) passa (rc=0, na base rc=2), e o bash fica na integração porque o cd falha
- A3 (recomendado) hooks/parecer.py:539 · cd fora do shell de fora move a pasta: (cd X); git merge, cd X | true;, cd X & git merge, cd X || git merge com cwd na integração passam (rc=0, já na base); aplicar `soltos` ao cd como às variáveis
- A4 (recomendado) hooks/parecer.py:182 · atribuição depois de && é condicional: W=<integração>; false && W=<wt>; cd $W && git merge passa (rc=0, já na base); tratar como `ruins`
- A5 (recomendado) hooks/parecer.py:221 · normpath antes da existência: cd X/*/.., cd 'X/nao/..' (o bash falha) e git -C <link>/.. (o git segue o link) são julgados em X; conferir a pasta crua e usar realpath no -C
- A6 (recomendado) hooks/parecer.py:189 · `~` e cd sem argumento usam o HOME do hook: HOME=<integração> (ou export, read) e depois cd ~ ou git -C ~ passam (rc=0, já na base); HOME mexido na linha torna o `~` desconhecido
- A7 (recomendado) hooks/parecer.py:533 · gh pr com pasta não resolvida (pushd, cd $UNK) usa o cwd da sessão; já era assim na base; recusar gh pr create/ready sem --head quando a pasta é desconhecida
- A8 (recomendado) hooks/parecer.py:57 · source e . (e invólucros env, env -C, command, exec, builtin cd, função) não tornam a pasta nem o GIT_DIR desconhecidos; já na base; registrar como dimensão nova e recusar na pasta desconhecida

## Detalhe dos achados
Sondas: `$TMPDIR/security-engineer-hk3-parecer-pasta/sondas/` (`sonda.py` monta a mesma fixture do corpus: `proj` em `develop`, worktree `home/wtx` em `melhoria/x`, sem parecer, e roda o `hooks/parecer.py` da branch e o da base `ff3936a`, worktree `~/.forge-contrib/wt/wt-seg-hk3-base`). As saídas estão em `novo*.txt` e `base*.txt`. "wt" é o cwd na worktree de trabalho e "raiz" o cwd na integração. Onde o texto diz que o bash vai a tal pasta, isso foi conferido no shell em `$TMPDIR/security-engineer-hk3-parecer-pasta/b*`.

**A1 · CDPATH fora da atribuição simples (bloqueante, requisito).** Evidência: `depois_do_cd` (`hooks/parecer.py:224-231`) só consulta `variaveis.get("CDPATH")` (atribuição simples fixada) e `os.environ`. `efeito_nas_variaveis` (`:192-207`) põe o CDPATH do `export`, do `declare -x`, do `read` e do prefixo em `ruins`, e `conferir` (`:526-529`) o apaga de `variaveis`. Sondas a partir de wt (rc=0 na branch): `export CDPATH=<raiz>; cd src && git merge melhoria/x`, `declare -x CDPATH=<raiz>; cd src && ...`, `read CDPATH; cd src && ...`, `CDPATH=<raiz> cd src && ...` e a forma em três linhas. O bash, com `CDPATH` exportado, vai a `<CDPATH>/src` (provado no shell: `foi para .../b2/b/src`). O merge entra na `develop` sem parecer. Caminho de ataque: agente com pressa numa worktree de trabalho mescla a feature na integração; o modelo de ameaças pede que a linha recuse. Severidade: baixa (exige montar o CDPATH; a proteção de branch e o pre-push seguem valendo), mas o item está na lista do requisito, e por isso bloqueia. Correção mínima: guardar no `Ambiente` uma marca "CDPATH tocado", ligada quando `CDPATH` está em `fixas | ruins` ou quando `todas` vale, inclusive no prefixo do próprio `cd`. Com a marca, `depois_do_cd` devolve None para o relativo, como já faz com o CDPATH fixado. Fixtures: `pasta-barra-cdpath-exportado`, `-declarado`, `-lido`, `-no-prefixo-do-cd`. Esforço: P. Dono: `tech-lead`.

**A2 · `$NOME` entre apóstrofos (bloqueante, regressão).** Evidência: `resolver` (`:216`) substitui `$NOME` na palavra que o `shlex` já tirou das aspas. O hook não distingue `cd '$W'` de `cd "$W"`. Sondas a partir de raiz: `W=<wtx>; cd '$W'; git merge melhoria/x` e a mesma linha com quebra de linha no lugar do `;` dão rc=0 na branch e rc=2 na base. O bash tenta `cd` para a pasta literal `$W`, falha ("No such file or directory", provado no shell) e roda o merge na integração. Caminho de ataque: erro honesto de aspas com `;` ou quebra de linha, a partir do cwd da sessão (`~/Forge`, na `main`, o caso mais comum). O merge local entra na integração sem parecer. Com `&&` o merge não roda e `git -C '$W'` falha no git, então essas formas não fazem dano. Severidade: baixa (o envio continua barrado pelo pre-push e pela proteção de branch), mas é contorno que este PR abre num caso que a base barrava. Correção mínima: a palavra cujo `$` estava entre apóstrofos no texto cru não é substituída e vira desconhecida (None), e o merge recusa. Para saber disso, uma marca no `leituras`, como o `OPACO`, ou uma segunda tokenização que preserve as aspas. Fixture: `pasta-barra-cd-variavel-entre-apostrofos` (cwd na integração, `;` e quebra de linha). Esforço: P a M. Dono: `tech-lead`.

**A3 a A8 (recomendados, não devolvem).** Todos passam igual na base, então não são regressão e nenhum está na lista do requisito. Ficam como dimensões novas da matriz (skill `cyber-security`). O A3, o A4 e o A5 são da mesma família da regra ("a pasta é calculada como o bash") e saem baratos no mesmo passe do A1 e do A2.
- A3: `conferir` (`:538-539`) aplica o `cd` sem olhar `soltos`. Correção: `cd` não solto não muda a pasta, e depois de `||` o comando seguinte vale na pasta anterior. P.
- A4: `SEGUE` (`:55`) inclui `&&` também para o comando à direita. A regra do modelo de ameaças, que é minha, errou ao listar `&&` sem esse cuidado: a atribuição à direita de `&&` é condicional e deve ir para `ruins`. P.
- A5: `normpath` (`:221`) apaga `*/..`, `nao/..` e `<link>/..` antes do `is_dir` (`:255`). Correção: exigir `os.path.isdir` do caminho cru e, no `-C`, usar `realpath`, porque o git faz `chdir` físico. P.
- A6: `com_til` (`:189`) e `:539` usam o HOME do processo do hook. Correção: HOME mexido na linha torna o `~` e o `cd` sem argumento desconhecidos. P.
- A7: com a pasta desconhecida, `raiz_gh` (`:533`) usa o cwd da sessão. Exemplo: `pushd <wt-sem-parecer> && gh pr create`, a partir de um cwd que tem parecer, é julgado pela branch do cwd. Correção: com a pasta desconhecida, `gh pr create`/`ready` sem `--head` recusa. P.
- A8: `source` e `.` estão em `LE_VARIAVEL` (`:57`) e só limpam as variáveis. Invólucros (`env GIT_DIR=`, `env -C`, `command git`, `exec git`, `builtin cd`, `command cd`, função) nem são reconhecidos: `env git merge` a partir da integração passa já na base. Classe vizinha da ofuscação, que a decisão de 10:40 tirou do lote. Fica para cartão próprio. M.

**Contornos do modelo de ameaças (E1 e E3): todos barrados na branch (rc=2), pelo corpus e pelas sondas.** São eles:
- `V=<wt-dev>; cd $V && git merge`
- `cd "$HOME/..."`
- `cd $(echo …)`
- `pushd <wt-dev> && git merge`
- `git -C ~/…` da integração
- `git -C "$V"`, com a variável fixada e com ela desconhecida
- `git -C <wt> -C <integração>`, absoluto e relativo
- `--git-dir`/`--work-tree`, juntos e separados
- `GIT_DIR=` no prefixo, `export GIT_DIR=`, `declare -x GIT_DIR=` e `GIT_DIR=x;`
- `GIT_WORK_TREE=`
- `-c core.worktree=` (também em maiúsculas)
- `( W=… )`, `true || W=…` e `W=… cd $W`
- pull e pull --rebase na integração, com e sem `&& git push`

Na outra direção, as formas legítimas do corpus passam (rc=0): `cd <literal> && git pull --rebase && git push`, `W=<wt>; cd $W`, `W=~/…`, `git -C ~/wt`, `-C` relativo ao anterior e `cd "$W"; git merge` a partir da integração. A base recusava esta última. A suíte do item (`python3 -m unittest tests.test_hooks_parecer_pasta`) dá OK (rc=0).

**Não fechados, declarados:**
- `false && W=x` (A4).
- `cd` entre apóstrofos. Com `;` ou quebra de linha é o A2, que bloqueia. Com `&&` não faz dano.
- Glob literal. `cd X/wt*` e `git -C X/pro*` recusam, porque a pasta não existe. `X/*/..` passa (A5).
- `gh pr` usa o cwd da sessão quando a pasta não é resolvida (A7).
- A ofuscação do nome do comando e os invólucros (A8) ficam fora, como limitação registrada.

Informativo: `--config-env=core.worktree=…` e `GIT_CONFIG_COUNT/KEY/VALUE` passam, mas o `core.worktree` não troca o HEAD (o repositório continua o do cwd), então o merge não entra na integração. Sem caminho de ataque.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. A2 e A1 precisam de correção, ou de aceite do dono por `docs/security/aceites/`. Os recomendados não pedem aceite.

Ferramentas: só sondas locais e passivas (Python da biblioteca padrão, o `tests/test_hooks.py` do próprio repositório, o bash). Não houve rede, exploit nem sistema externo. `gitleaks`, `semgrep` e `zizmor` não se aplicam a este diff (só Python de hook e JSON de teste, sem segredo nem workflow). Não foram rodadas.

PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia ("nenhum ainda"), então não havia item a conferir. A classe "pasta calculada diferente do bash" aparece aqui pela primeira vez como achado de segurança, e por isso não entra na lista ainda.
