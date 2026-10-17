---
tipo: revisao-seguranca
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 9f3fa2b82789421c6657ebd6167184371a4fc35d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-17
---
# Review de segurança: bp-1

> **Rodada 3** (`9f3fa2b`, depois do retrabalho 2): **reprovado**. D, E e B' estão fechados, mas apareceu o achado F (alta): o arquivo `commondir` dentro do `.git/` desvia a busca da marca, e quatro linhas voltam a desligar tudo. Detalhes na seção "Revalidação após o retrabalho 2", no fim.
>
> **Rodada 2** (`99648a3`, depois do retrabalho 1): **reprovado**. Os achados A e B da primeira rodada estão fechados, mas apareceu um achado novo, o D (alta). Detalhes na seção "Revalidação após o retrabalho 1", no fim. O texto da primeira rodada, sobre `95a1140`, ficou como estava.

Escopo: `git diff f636d27c95bd1fdc9137baa830e0f53905863eaf...95a1140b65db1cccc053cdeb627c1f6b830400c1`, 17 arquivos (+370 / -8): `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/vigia.py`, fixtures novas, `tests/test_hooks.py`, ADR 0009 e `docs/hooks.md`. O commit seguinte da branch (`8d8ff69`) só acrescenta `docs/reviews/bp-1.md`, então o código revisado é o mesmo. Revisão estática, com os hooks rodados sobre fixtures descartáveis numa cópia (`git archive`) em `$TMPDIR`, fora da worktree. Não escrevi esta branch.

## Gatilhos
`R-SEGURANCA`: a entrega muda controles do Forge, os hooks `conformidade` e `vigia` e a falha fechada comum (`executar`). Ela corrige o achado 1 (alta) de `docs/security/incidente-bypass-1.md`.

## Veredito
**Reprovado.** As reproduções literais do achado 1 estão fechadas, mas o achado continua aberto: **uma linha ainda desliga todos os hooks e cala o `vigia`** (achado A). O motivo é que a marca que deveria fazer a falha fechar fica em `.forge/run/`, uma pasta que o próprio git apaga. Pela mesma razão, a falha fechada não protege contra as formas de `git rm` que a conferência de caminhos deixa passar (achado B). A marca em `.forge/run/` saiu da proposta P1 do meu parecer do incidente. A falha é do desenho que eu propus, não da implementação.

## O que foi verificado (fechado)
A guarda nova (`hooks/conformidade.py:813-834`) dá rc=2 para:
- `git rm .forge/versao`, `git rm -q --cached .forge/versao` e `git rm -r .forge`;
- `git mv .forge/versao .forge/v` e `git mv .forge .f`;
- `git checkout HEAD~0 -- .forge`, `git checkout HEAD .forge/versao` (sem `--`), `git restore -s HEAD~1 .forge` e `git restore --source=HEAD -- .forge/versao`;
- `git -C .forge rm versao`, `git -C sub rm ../.forge/versao`, `git rm sub/../.forge/versao` e, com cwd em `sub/`, `git rm ../.forge/versao`;
- os curingas que o `glob` do Python alcança: `'.forge/vers*'`, `'.f*/versao'` e `-r '.*'`;
- `':/.forge/versao'`, que o `em_qualquer_lugar` pega.

A marca também não se apaga pelo caminho direto: `rm .forge/run/projeto` dá rc=2 (`.forge/run/` está protegido, `hooks/conformidade.json:32`). Com a marca presente e o `.forge/versao` apagado, `git push --force origin main` dá rc=2 ("sumiu") e o `vigia` avisa `versao-sumiu` no `Stop` (cenário conferido de ponta a ponta).

Falso positivo, sem regressão nos comandos comuns: `git checkout -- src/app.js`, `git restore src/app.js`, `git checkout -- .`, `git restore .`, `git checkout main`, `git checkout -`, `git switch -`, `git checkout -b nova`, `git rm src/app.js` e `git mv src/app.js src/b.js` dão rc=0.

## Achados

### A. A marca em `.forge/run/` é apagada pelo git: uma linha ainda desliga tudo · alta
- **Evidência:** `hooks/_comum.py:91-93`: a marca é `.forge/run/projeto`, e `marcar_projeto` grava `.forge/run/.gitignore` com `*`, então a marca é arquivo ignorado. `hooks/_comum.py:111-116` (`versao_sumiu`): sem a marca, nada falha fechado. A fixture `tests/hooks/conformidade/versao-sumiu-sem-marca-libera.json` confirma esse comportamento. O `git` não passa pela conferência de caminhos nos subcomandos `sparse-checkout`, `clean` e `stash` (`CAMINHOS_NO_GIT`, `hooks/conformidade.py:84`).
- **Reprodução** (cópia descartável, git 2.55.0, depois do `SessionStart` do `vigia` gravar a marca):
  - `git sparse-checkout set src`: o hook dá rc=0 (`conformidade` e `parecer`) e o comando apaga `.forge/versao` **e** `.forge/run/projeto`. Em seguida `git push --force origin main` dá rc=0 nos dois hooks, e o `vigia` no `Stop` dá rc=0 sem aviso.
  - Em duas linhas: `git clean -fdX` (rc=0, apaga a marca e mantém o `.forge/versao`) e depois `git rm '*/versao'` (rc=0, achado B). O resultado é o mesmo: push com rc=0 e `vigia` mudo.
  - `git stash -a` e `git clean -fdx .forge/run` também apagam a marca com rc=0.
- **Caminho de ataque:** o mesmo do achado 1 do incidente. Um agente no projeto, depois de um bloqueio ou levado por conteúdo injetado, roda uma linha que parece inofensiva ("reduzir a cópia de trabalho", "limpar ignorados"). Desse ponto em diante nenhum hook do Forge age e o usuário não recebe aviso.
- **Correção mínima:** gravar a marca onde nenhum comando de cópia de trabalho do git alcance, por exemplo `$(git rev-parse --git-common-dir)/forge/projeto`. Nem `clean`, nem `sparse-checkout`, nem `stash`, nem `reset` mexem em `.git/`. Acrescentar esse caminho a `caminhos` em `hooks/conformidade.json` com `quem: []`, como já acontece com `.git/config` e `.git/hooks/`. Fixtures: `sparse-checkout-sem-versao-bloqueia` (a marca sobrevive e o push dá rc=2), `git-clean-X-mantem-marca` e `vigia` avisando depois do `sparse-checkout`. Resolvido isso, toda forma de sumir com o arquivo que a guarda não vê (`sparse-checkout`, `reset --hard`, `read-tree -mu`, `switch`, `restore -s <ref> .`, `checkout --no-overlay <ref> -- .`, todas conferidas com rc=0 e o arquivo apagado) cai no cenário que já funciona: ação crítica com rc=2 e o `vigia` avisando. · Esforço P · Dono: `tech-lead`.

### B. A conferência de caminhos não segue a semântica de pathspec do git · média (alta enquanto A estiver aberto)
- **Evidência:** `hooks/conformidade.py:821,826`: palavra com `-` é descartada, então `--pathspec-from-file` passa. `hooks/conformidade.py:831`: o curinga vai para `glob.glob`, que não casa arquivo oculto com `*` nem atravessa `/`. Para o git, `*` atravessa `/` e casa ponto inicial.
- **Reprodução** (rc=0 no hook, e o `git` real apaga `.forge/versao`): `git rm '*/versao'`, `git rm '*versao'`, `git rm -r '*'`, `git rm ':(top).forge/versao'`, `git rm ':(glob)**/versao'`, `git rm '\.forge/versao'`, `git rm --pathspec-from-file=lista`, `echo .forge/versao | git rm --pathspec-from-file=-`, `git rm -r .` e `git rm -r :/`.
- **Caminho de ataque:** igual ao do A. Hoje a marca segura esses casos (cenário conferido: push com rc=2 e o `vigia` avisa). Combinados com o A, porém, desligam tudo.
- **Correção mínima:** para `rm`/`mv` e para `checkout`/`restore` com origem (`-s`, `<ref> --`, `--no-overlay`), deixar o próprio git resolver os caminhos com `git -C <pasta> ls-files -z -- <pathspecs>` e conferir cada resultado, no lugar do `glob.glob`. É leitura e não roda programa. Também recusar `--pathspec-from-file`, porque o hook não lê o arquivo nem o stdin. Para `checkout -- .` e `restore .` sem origem, deixar como está: o arquivo só muda se já diferir do índice, e isso o `vigia` (`em-vigor`) vê. Fixtures: `git-rm-curinga-oculto-bloqueia` (`'*/versao'`), `git-rm-pathspec-magica-bloqueia`, `git-rm-pathspec-from-file-bloqueia`. · Esforço P · Dono: `tech-lead`.

### C. `git restore --staged <caminho em vigor>` passou a perguntar ou barrar · informativa
- **Evidência:** `git restore --staged .claude/settings.json` dá rc=2. O comando só mexe no índice e não muda o arquivo em disco.
- **Avaliação:** é falso positivo raro (tirar do índice um arquivo em vigor) e não tem custo de segurança. Aceitável como está. Se incomodar, isentar `--staged` sem `--worktree` em `restore`. · Dono: `tech-lead`.

## O que fica aberto e quem cobre
- `git -c alias.x=rm x .forge/versao` dá rc=0 e apaga o arquivo. Isso é o achado 2 do incidente, coberto pela **BP-2** (recusar `-c alias.*` e `--config-env`). Com o achado A corrigido, a marca segura o efeito até lá.
- Ação **não crítica** sem `.forge/versao` passa (limite documentado na ADR 0009, item 2). A marca apagável por quem escreve fora do hook (Bash sem sandbox) depende do sandbox, coberto pela **BP-5** (P5, sandbox obrigatório nos projetos).
- Os achados A e B são desta entrega (escopo E1 da BP-1) e nenhuma BP posterior os cobre. Têm de ser corrigidos aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só os hooks da própria branch, executados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, e `git` 2.55.0 local para conferir o efeito real de cada comando em repositórios descartáveis. Nenhum remoto foi tocado. `gitleaks`, `zizmor` e `actionlint` não se aplicam: a entrega não mexe em workflow nem traz segredo.

## Revalidação após o retrabalho 1
Escopo: `git diff 78259ede573b5f4fec7859229bfbddb72e5b88f2...99648a358622b2f75eba5e1210da04d52cfa9670`, commits `75f7ab4`, `c641dee` e `99648a3`, 17 arquivos (+404 / -48). Mesmo método da primeira rodada: os hooks da branch, rodados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, em repositórios descartáveis (git 2.55.0, a marca gravada pelo `SessionStart` do `vigia`). A worktree não foi tocada, exceto por este arquivo.

### Veredito da rodada 2
**Reprovado.** O A e o B fecham como foram escritos. A marca agora está em `<git-common-dir>/forge/projeto` (`hooks/_comum.py:91-105`), e nenhum comando de cópia de trabalho a apaga. Os pathspecs passam a ser resolvidos pelo próprio git (`hooks/conformidade.py:819-895`). O objetivo do achado 1 do incidente, porém, era que **nenhuma sequência curta desligasse todos os hooks e calasse o `vigia`**, e ele continua sem ser cumprido. Depois que o `.forge/versao` some, o modo degradado só olha o texto das ações críticas (a regex `CRITICO`), e a marca nova se apaga por linhas que essa regex não reconhece (achado D).

### A: fechado
Com a marca presente, todos os comandos abaixo deixam a marca no lugar: `git sparse-checkout set src`, `git clean -fdX`, `git clean -fdx`, `git clean -fdx .forge/run`, `git stash -a` e `git reset --hard`. O hook dá rc=0 para cada um, como esperado. Os cenários de ponta a ponta da rodada 1 viraram:
- `git sparse-checkout set src`, depois `git push --force origin main` e `git push origin HEAD:melhoria/x`: os pushes dão **rc=2** ("sumiu"), e o `vigia` avisa `versao-sumiu` no `Stop`.
- `git clean -fdX`, depois `git rm '*/versao'`: o `git rm` já dá **rc=2**. Depois que o arquivo some por outro caminho, o push dá rc=2 e o `vigia` avisa.

A marca também não se apaga nem se falsifica pelo caminho direto. Todos os comandos abaixo dão **rc=2**, porque `.git/forge/` está protegido (`hooks/conformidade.json:33`) e a `CRITICO` passou a incluir `.git/forge`: `rm .git/forge/projeto`, `rm -rf .git/forge`, `rm -rf .git`, `mv .git .g`, `mv .git/forge .git/f`, `echo x > .git/forge/projeto`, `truncate -s0 …`, `cp /dev/null …`, `ln -sf /nada …`, `cd .git && rm -r forge` e `git -C .git rm forge/projeto`. Na worktree, `rm .git`, `mv .git g` e `rm <clone>/.git/forge/projeto` também dão **rc=2**. Falsificar o conteúdo não adianta, porque só a existência da marca conta. `GIT_DIR` e `core.worktree` não enganam a busca da marca: o `git` do hook roda sem as variáveis `GIT_*` herdadas (`bin/forge-check:279-285`), e `.git/config` é protegido.

### B: fechado
Todas as formas da rodada 1 dão **rc=2** agora:
- curingas e o `-r .`: `'*/versao'`, `'*versao'`, `-r '*'`, `-r .`, `-r :/`, `--cached -r .`;
- pathspec mágico: `':(top)…'`, `':(glob)**/versao'`, `':(icase).FORGE/VERSAO'`, `':(literal)…'`;
- escape e classes: `'\.forge/versao'`, `'.forge/vers[a-z]o'`, `'.forge/versa?'`;
- `--pathspec-from-file`, nas formas `=lista`, `=-` pela entrada padrão, `--pathspec-from=lista` abreviada e `--pathspec-file-nul --pathspec-from-file lista`.

O mesmo vale para as variantes novas que testei:
- exclusão: `':!src'`, `-r ':(exclude)src'`, `-r ':^src/app.js'`;
- `git mv '*/versao' src/`;
- `git checkout HEAD -- '*'`, `git checkout HEAD~0 .`, `git checkout --no-overlay HEAD -- .`;
- `git restore -s HEAD~0 .`, `git restore --source=HEAD :/`, `git restore -s HEAD --staged --worktree .`;
- `git -C src rm -r ':/'` e `git -C src rm -r '../*'` (este dá rc=2 pela recusa na dúvida);
- `git --glob-pathspecs rm '*/versao'`, `git --icase-pathspecs rm .FORGE/VERSAO`, `GIT_GLOB_PATHSPECS=1 git rm '**/versao'`;
- `git --git-dir=.git --work-tree=.forge rm -r '*'`.

Dois comandos dão rc=0 sem erro do hook: `git --literal-pathspecs rm '*'` e `--noglob-pathspecs rm '*/versao'`. Conferi que o git real não apaga nada nesses casos.

Não houve regressão nos falsos positivos: `git checkout -- src/app.js`, `git restore src/app.js`, `git checkout -- .`, `git restore .`, `git checkout main|-|melhoria/x`, `git switch -`, `git checkout -b nova`, `git checkout HEAD -- src`, `git rm src/app.js`, `git rm -r src`, `git rm --cached src/app.js` e `git mv src/app.js src/b.js` dão rc=0. O C (`git restore --staged .claude/settings.json`, rc=2) continua informativo e aceitável.

### D. No modo degradado, a marca nova se apaga por linhas que a `CRITICO` não reconhece: duas linhas ainda desligam tudo · alta
- **Evidência:**
  - `hooks/_comum.py:674-681` e `697`: sem `.forge/versao`, o `executar` só barra o que casa com a regex `CRITICO` (`hooks/conformidade.py:28-31`). O resto do `conformidade` não roda, porque `raiz_do_projeto` exige o `.forge/versao` (`hooks/_comum.py:44-47`).
  - `hooks/_comum.py:108-119`: um `SessionStart` com `source: startup` e sem `.forge/versao` **apaga** a marca.
  - `hooks/_comum.py:91-98`: se o `git rev-parse` falha e o `.git` não é pasta (worktree com o arquivo `.git` adulterado, ou `.git` renomeado), a marca vira `None`, e `versao_sumiu` (`:122-130`) devolve False.
- **Reprodução** (cada linha é uma chamada separada do Bash; o hook, `conformidade` e `parecer`, dá rc=0 em todas):
  1. `git sparse-checkout set src` e depois `echo '{"hook_event_name":"SessionStart","source":"startup"}' | python3 <plugin>/hooks/vigia.py`. O `vigia`, chamado à mão, apaga a própria marca. Em seguida `git push --force origin main` dá rc=0, e o `vigia` no `Stop` fica mudo.
  2. `git sparse-checkout set src` e depois `cd .git && rm -r forge`. Com o `.forge/versao` presente, essa linha dá rc=2; sem ele, dá rc=0. Em seguida `git push --force origin main` e `git config core.hooksPath /dev/null` dão rc=0, e o `vigia` fica mudo.
  3. `git sparse-checkout set src`, `mv .git .g` e depois `GIT_DIR=.g git push --force origin main`: rc=0 em tudo, e o `vigia` fica mudo.
  4. Numa worktree, **mesmo com o `.forge/versao` presente**, `echo 'gitdir: /nada' > .git` dá rc=0, porque o arquivo `.git` não é protegido. Depois, `git --git-dir=<clone>/.git/worktrees/w --work-tree=. sparse-checkout set src` e `git --git-dir=… push --force origin main` também dão rc=0, e o `vigia` fica mudo.
  - Também apagam a marca com rc=0, **mesmo com o `.forge/versao` presente**: `find .git -name projeto -delete`, `rm -r .git/fo*` (curinga do shell), `rm $(git rev-parse --git-common-dir)/forge/projeto` e `python3 -c "…remove('.git/'+'forge/projeto')"`. É a mesma classe de lacuna que já existe para o próprio `.forge/versao`: `rm .forge/vers*` e `find .forge -name versao -delete` dão rc=0 também na base `f636d27`, então não é regressão desta entrega.
- **Caminho de ataque:** o mesmo do A e do achado 1 do incidente. Um agente no projeto, depois de um bloqueio ou levado por conteúdo injetado, roda duas linhas com cara de manutenção ("reduzir a cópia de trabalho", "reiniciar o vigia"). Dali em diante nenhum hook age e o usuário não recebe aviso. O sandbox (BP-5) não fecha isso, porque `.git/forge/` e o arquivo `.git` ficam dentro do projeto, onde o sandbox deixa escrever.
- **Correção mínima** (esforço P/M, dono `tech-lead`):
  1. **Com a marca presente, a sessão continua sendo projeto.** Quando `versao_sumiu()` é verdadeiro, o `conformidade` roda a conferência inteira (caminhos protegidos, remoção, `git`), não só a `CRITICO`. Basta que o "só age em projeto" aceite a raiz da sessão com marca. Com isso, a linha 2 (`cd .git && rm -r forge`) e o `mv .git .g` caem nas mesmas checagens que já dão rc=2 com o arquivo presente.
  2. **O `SessionStart` não apaga a marca.** Só o usuário a remove, à mão, ao tirar o Forge do projeto, e a mensagem de bloqueio e o `docs/hooks.md` dizem como. Se a marca existe e o arquivo não, ela fica, e a ação crítica falha fechado, como o dono decidiu ("ausência de `.forge/versao` na sessão falha fechado"). Isso fecha a linha 1.
  3. **Na dúvida, falha fechado também quanto ao git.** Sem `.forge/versao`, se existe `.git` (pasta ou arquivo) mas o `rev-parse` falha, `versao_sumiu` devolve True. Proteger também o arquivo `.git` da raiz (`caminhos`, `quem: []`). Isso fecha a linha 4 e o fim da linha 3.
  4. **Fixtures:** `sessionstart-a-mao-nao-apaga-marca` (rc=2 no push depois), `degradado-rm-marca-pelo-cd-bloqueia` (`cd .git && rm -r forge` sem `.forge/versao`: rc=2), `degradado-mv-git-bloqueia`, `worktree-arquivo-git-adulterado-bloqueia`, e o `vigia` avisando nos quatro cenários.

### E. A marca é uma só por clone, compartilhada pelas worktrees · baixa
- **Evidência:** `hooks/_comum.py:101-105`: a marca fica em `--git-common-dir`, que é o mesmo para todas as worktrees do clone.
- **Reprodução:** a sessão está no clone principal. Um `SessionStart` (`startup`) numa worktree irmã sem `.forge/versao` apaga a marca da sessão (conferido: a marca some). O contrário também acontece: uma sessão numa worktree sem Forge herda a marca do clone e passa a ter as ações críticas barradas (falso positivo).
- **Caminho de ataque:** com o D.2 corrigido, sobra só o falso positivo. É informativo/baixo.
- **Correção mínima:** uma marca por raiz, por exemplo `<git-common-dir>/forge/projeto-<hash do realpath da raiz>`, ou `$(git rev-parse --git-dir)/forge/projeto`, que é por worktree. Neste segundo caso, proteger também `.git/worktrees/*/forge/`. · Esforço P · Dono: `tech-lead`.

### B': `GIT_ICASE_PATHSPECS=1` antes do git · baixa (defesa em profundidade)
- **Evidência e reprodução:** `GIT_ICASE_PATHSPECS=1 git rm .FORGE/VERSAO` e `env GIT_ICASE_PATHSPECS=1 git rm -q .FORGE/VERSAO` dão rc=0 e apagam o `.forge/versao` num sistema de arquivos sensível a maiúsculas. O `ls-files` do hook roda sem essa variável. A forma de opção (`--icase-pathspecs`) já dá rc=2.
- **Avaliação:** com a marca, cai no modo degradado (push com rc=2 e o `vigia` avisa), como o `sparse-checkout`. Não bloqueia sozinho.
- **Correção mínima:** tratar as atribuições `GIT_*_PATHSPECS=` antes de `git` (ou depois de `env`) como as opções `--*-pathspecs`, repassando-as ao `ls-files`, ou recusá-las. · Esforço P · Dono: `tech-lead`.

### O que fica aberto e quem cobre (rodada 2)
- **D** (alta) e **E** (baixa) são do desenho da marca desta entrega. Nenhuma BP posterior os cobre, então têm de ser corrigidos aqui. O **B'** (baixa) pode entrar junto.
- Curinga do shell em `rm`/`mv` (`rm .forge/vers*`), `find -delete`, substituição `$(…)` e interpretador (`python3 -c`) apagando arquivo em vigor: são anteriores a esta entrega (rc=0 também na base `f636d27`). Com o D corrigido, os efeitos caem no modo degradado (ação crítica com rc=2 e o `vigia` avisando). A **BP-5** (sandbox obrigatório) só cobre isso se a configuração do sandbox negar a escrita em `.forge/versao` e `.git/forge/`. Recomendo que a BP-5 inclua esses dois caminhos na lista de escrita negada.
- O alias por `-c` (`git -c alias.x=rm x .forge/versao`) continua com a **BP-2**.

### Ferramentas (rodada 2)
Só os hooks da branch (`python3`) e o `git` 2.55.0 local, em repositórios descartáveis em `$TMPDIR`. Para comparar com a base, usei uma cópia `git archive` de `f636d27`. Nenhum remoto foi tocado: os `push` foram avaliados só pelo hook, sem rodar o git. `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não mexe em workflow nem traz segredo.

## Revalidação após o retrabalho 2
Escopo: `git diff 7594a24a64b9a4d35b1ed67711c0f94bf7a4ad9f...9f3fa2b82789421c6657ebd6167184371a4fc35d`, commits `086dcca` e `9f3fa2b`, 22 arquivos (+505 / -40). Mesmo método das rodadas anteriores: os hooks da branch (`conformidade`, `parecer` e `vigia`), rodados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, em repositórios descartáveis (git 2.55.0). A marca foi gravada pelo `SessionStart` do `vigia`. Cada comando só foi executado de verdade quando os dois hooks deram rc=0. A worktree não foi tocada, exceto por este arquivo.

### Veredito da rodada 3
**Reprovado.** Os achados D, E e B' fecham como foram escritos. Todas as cadeias das rodadas 1 e 2 agora terminam barradas, com o `vigia` avisando. Só que a marca continua sendo procurada onde o `git rev-parse --git-common-dir` aponta, e um arquivo comum dentro do `.git/` muda esse ponteiro (achado F). Com isso, quatro linhas de Bash com rc=0 voltam a desligar todos os hooks e a calar o `vigia`.

### D: fechado
- **D.1** (`SessionStart` `startup` chamado à mão): depois do `git sparse-checkout set src`, a chamada à mão do `vigia` dá rc=0, mas a marca continua lá (`marcar_projeto` não apaga mais, `hooks/_comum.py:117-124`). `git push --force origin main`, `git push origin HEAD:melhoria/x` e `git config core.hooksPath /dev/null` dão **rc=2**, e o `vigia` avisa `versao-sumiu` no `Stop`.
- **D.2** (`cd .git && rm -r forge` sem o `.forge/versao`): **rc=2** pela conferência inteira ("marca de sessão dos hooks"). `rm -rf .git/forge` e `rm .git/forge/projeto-*` também dão rc=2. No modo degradado, a conferência inteira também barra o que a `CRITICO` não via: `echo x > .claude/settings.json`, `mkdir -p .forge && echo 9 > .forge/versao`, `echo x > .githooks/pre-push`, `docs/security/…` e `git commit --no-verify` dão rc=2. `echo ok > src/c.js` dá rc=0, sem falso positivo.
- **D.3** (`mv .git .g` e depois `GIT_DIR=.g`): `mv .git .g`, `mv .git/ .g`, `cp -r .git .g && rm -rf .git`, `cd . && mv .git .g` e `mv -t /x .git` dão **rc=2**, com o `.forge/versao` presente ou ausente (`hooks/conformidade.json:34`).
- **D.4** (arquivo `.git` falso na worktree): `echo 'gitdir: /nada' > .git`, `tee`, `rm`, `mv`, `cp /dev/null`, `sed -i`, `truncate` e `ln -sf` sobre o `.git` dão **rc=2**. Com um `.git` falso escrito por fora (simulado), `projeto_marcado` cai no ramo de falha fechada (`hooks/_comum.py:127-136`): o push dá rc=2, `rm -rf .forge` dá rc=2 e o `vigia` avisa. Também falham fechado o clone principal apagado ou movido a partir da worktree (`cd .. && rm -rf <clone>`, `mv ../<clone> ../x`) e `rm -rf <comum>/worktrees`.
- Os extras da rodada 2 (`find .git -name 'projeto-*' -delete`, `rm -r .git/fo*`, `rm $(…)/forge/…`) continuam com rc=0, como na base. São da classe que a BP-5 cobre. `python3 -c "…'.git/'+'forge/…'"` passou a dar rc=2, efeito da proteção do `.git`.

### E: fechado
A marca é `<comum>/forge/projeto-<sha256 do caminho real da raiz>[:16]` (`hooks/_comum.py:105-115`). Com uma worktree irmã sem Forge, `startup` e `resume` na irmã mantêm a marca da sessão principal. Na irmã, `git push --force origin main` e `git push origin HEAD:melhoria/y` dão rc=0, ou seja, ela não herda a marca, e o falso positivo da rodada 2 sumiu. Na sessão principal, depois do `sparse-checkout`, o push continua com rc=2 e o `vigia` avisa. Numa sessão de worktree **com** Forge, apagar ou mover a marca no diretório comum por caminho absoluto ou relativo (`rm -rf <clone>/.git/forge`, `rm <clone>/.git/forge/projeto-*`, `cd <clone>/.git && rm -r forge`, `mv …/forge …/f`) dá **rc=2**.

### B': fechado
Estas formas dão **rc=2** e o `.forge/versao` fica no lugar:
- atribuição: `GIT_ICASE_PATHSPECS=1 git rm -q .FORGE/VERSAO`, também com o valor `yes`;
- `env`, inclusive `env -i PATH=… GIT_ICASE_PATHSPECS=1 git …` e `env -S 'GIT_ICASE_PATHSPECS=1 git' rm …`;
- `export` com `;` ou `&&`, `VAR=1; export VAR; git …`, `declare -x`, `set -a; VAR=1; git …`, subshell `( export …; git … )` e `bash -c '…'`;
- as outras variáveis: `GIT_GLOB_PATHSPECS=1 git rm '**/versao'` (atribuição e `export`), `GIT_LITERAL_PATHSPECS=1` e `GIT_NOGLOB_PATHSPECS=1`;
- e as mesmas variáveis com `git mv` e `git checkout HEAD~0 -- .FORGE`.

`GIT_ICASE_PATHSPECS=0 git rm .FORGE/VERSAO` dá rc=0, e o git real também não apaga nada. `GIT_ICASE_PATHSPECS=1 git rm src/app.js` dá rc=0, sem falso positivo. O `GIT_LITERAL_PATHSPECS=1 git rm -q .forge/versao` dá rc=2 porque o caminho literal é o próprio arquivo em vigor.

### Rodadas 1 e 2, de novo: sem regressão
- **A:** `git sparse-checkout set src`, `git clean -fdX`, `git clean -fdx`, `git clean -fdx .forge/run`, `git stash -a` e `git reset --hard` dão rc=0, e a marca fica no lugar em todos.
- **B:** as 19 formas a seguir dão **rc=2**, e o `.forge/versao` fica no lugar:
  - curingas e o `-r`: `'*/versao'`, `'*versao'`, `-r '*'`, `-r .`, `-r :/`;
  - pathspec mágico: `':(top)…'`, `':(glob)**/versao'`, `':(icase)…'`, `-r ':!src'`;
  - escape: `'\.forge/versao'`;
  - `--pathspec-from-file`, com arquivo e pela entrada padrão;
  - `git mv '*/versao' src/`;
  - `git checkout HEAD -- '*'` e `git checkout --no-overlay HEAD -- .`;
  - `git restore -s HEAD~0 .`;
  - `git --glob-pathspecs rm '*/versao'`, `git --git-dir=.git --work-tree=.forge rm -r '*'` e `git -C src rm -r ':/'`.
- `git -c alias.x=rm x .forge/versao` continua com rc=0 e apaga o arquivo. Esse caso é da BP-2, e a marca segura o efeito: o push seguinte dá rc=2 e o `vigia` avisa.

### F. O arquivo `commondir` dentro do `.git/` desvia a busca da marca: quatro linhas desligam tudo de novo · alta
- **Evidência:**
  - `hooks/_comum.py:95-102` (`dir_do_git`): a marca é procurada no que `git rev-parse --git-common-dir` devolver. O git lê esse valor do arquivo `<gitdir>/commondir`, se ele existir.
  - `hooks/conformidade.json:33-36`: dentro do `.git/`, só `.git/forge/`, o próprio `.git`, `.git/config` e `.git/hooks/` são protegidos. O `.git/commondir` e o `<comum>/worktrees/<n>/commondir` (e `gitdir`) ficam livres, e a regex `CRITICO` também não os cita (`hooks/conformidade.py:28-31`).
  - Quando o `commondir` aponta para outro repositório válido, o `rev-parse` dá certo. `projeto_marcado` então procura a marca lá, não a encontra e devolve False, sem chegar ao ramo de falha fechada.
- **Reprodução** (clone principal; cada linha é uma chamada separada do Bash; os dois hooks dão rc=0 em todas):
  1. `git sparse-checkout set src` apaga o `.forge/versao`; a marca segura.
  2. `git init -q /tmp/x` cria um repositório qualquer. Basta um que já exista, então esta linha é opcional.
  3. `echo /tmp/x/.git > .git/commondir`: rc=0 mesmo com a conferência inteira ligada. Daqui em diante o `rev-parse` aponta para `/tmp/x/.git`, a marca some da vista, `git push --force origin main` dá rc=0 e o `vigia` no `Stop` fica mudo.
  4. `rm -rf .git/forge` e depois `rm .git/commondir`: rc=0, porque a sessão já não é projeto. O repositório volta ao normal, mas sem marca: `git push --force origin main` e `git config core.hooksPath /dev/null` dão rc=0, e o `vigia` fica mudo de vez.
  - **Com o `.forge/versao` presente**, o passo 3 também dá rc=0 (seja com `echo >`, `tee`, `cp` ou `ln -s`), e pode vir antes. Na worktree, basta uma escrita fora da raiz, em `<comum>/worktrees/<n>/commondir`, que dá rc=0 do mesmo jeito; depois do `sparse-checkout`, o push dá rc=0 e o `vigia` fica mudo.
- **Caminho de ataque:** o mesmo do D e do achado 1 do incidente. Um agente no projeto, depois de um bloqueio ou levado por conteúdo injetado, roda poucas linhas que parecem manutenção, e dali em diante nenhum hook age nem avisa. A BP-5 não cobre isso: o sandbox deixa escrever no `.git/` do projeto, e o `git` precisa dessa escrita.
- **Correção mínima** (esforço P, dono `tech-lead`):
  1. **Não depender do `rev-parse` para achar a marca da raiz principal.** Se `<raiz>/.git` é pasta, o diretório comum **é** essa pasta: um clone principal nunca tem `commondir`. Se `<raiz>/.git/commondir` existir nesse caso, falhar fechado (a raiz vale como marcada). Na worktree, conferir que o `commondir` de `<gitdir>` aponta para o comum de onde o `gitdir` saiu (`.../worktrees/<n>` → `..`/`..`), como `diretorio_comum` (`hooks/conformidade.py:1265-1285`) já faz, só pelo disco, com o `gitdir`; o caminho mais curto é a marca usar esse resolvedor no lugar do `rev-parse`. Se não apontar, falhar fechado.
  2. **Proteger os ponteiros.** Incluir em `caminhos` (`quem: []`) o `.git/commondir` e o `.git/worktrees/`, ou `.git/` inteiro: agente não escreve à mão no `.git/`, e os comandos do `git` não passam pela conferência de escrita. Incluir também `commondir` na `CRITICO`.
  3. **Fixtures:** `f-commondir-desviado-bloqueia` (a escrita em `.git/commondir` dá rc=2, com e sem o `.forge/versao`), `f-commondir-por-fora-falha-fechado` (com o `commondir` escrito fora dos hooks, o push dá rc=2), `f-worktree-commondir-bloqueia`, e o `vigia` avisando no segundo caso.

### G. Mover ou apagar a raiz da sessão deixa a marca sem dono · média
- **Evidência:**
  - `hooks/_comum.py:113` e `:138-143`: a chave da marca é o caminho real da raiz, e `versao_sumiu` usa o `CLAUDE_PROJECT_DIR`.
  - Se a raiz sai do lugar, esse caminho deixa de existir: `projeto_marcado` devolve False, porque não há `.git` ali.
  - Na pasta nova, `raiz_do_projeto(cwd)` calcula outra chave e também não acha marca.
  - A conferência protege caminhos **dentro** da raiz, não a raiz e as pastas acima dela.
- **Reprodução:**
  - Depois do `git sparse-checkout set src`, `cd .. && mv <raiz> <raiz>x` dá rc=0. Na pasta nova, `git push --force origin main`, `git config core.hooksPath /dev/null` e `rm -rf .git/forge` dão rc=0, e o `vigia` fica mudo.
  - Numa sessão de worktree, `git worktree move . <outro>` dá o mesmo resultado.
  - Na base `f636d27`, `cd .. && mv <raiz> <raiz>x` e `git worktree move .` também dão rc=0, e na rodada 2 a marca por clone também se perdia. Por isso não é regressão da marca por raiz: a marca por raiz só herda a lacuna.
- **Caminho de ataque:** igual ao do F, mas o sandbox obrigatório (BP-5) já o fecha, porque renomear a raiz exige escrever na pasta acima do projeto, fora da área permitida. Sem o sandbox, são duas linhas.
- **Correção mínima** (esforço P, dono `tech-lead`; recomendada nesta entrega por ser barata, ou fica com a BP-5):
  - Em `versao_sumiu`, falhar fechado quando o `CLAUDE_PROJECT_DIR` não existir mais ou não tiver `.git`: a raiz da sessão sumiu.
  - Na conferência, tratar `mv` e `rm` da raiz ou de uma pasta acima dela, e `git worktree move|remove` da raiz da sessão, como remoção do `.forge/versao` e do `.git`.

### H. `docs/hooks.md:81` ficou com o comportamento antigo · informativa
- **Evidência:** a linha ainda diz que a marca é `<git-common-dir>/forge/projeto` e que, "para tirar o Forge de um projeto", basta apagar o arquivo e abrir uma sessão nova, porque o "`startup` apaga a marca". O código de `9f3fa2b` não faz mais isso, e `docs/hooks.md:53` já descreve o comportamento novo.
- **Efeito:** o usuário que seguir a linha 81 fica com as ações críticas barradas sem saber por quê. Não tem custo de segurança: falha para o lado fechado.
- **Correção mínima:** alinhar a linha 81 com a 53 (a marca é `projeto-<hash da raiz>` e se apaga à mão em `.git/forge/projeto-*`). · Esforço P · Dono: `tech-lead`.

### O que a marca por raiz abre
Com o F e o G fora da conta, nada de novo. A chave usa `os.path.realpath`, então um link simbólico para a raiz não muda a marca. Uma marca que sobra de uma pasta antiga não é lida por nenhuma outra raiz. E o falso positivo da irmã sem Forge (achado E) sumiu. Fica um custo de uso: quem tira o Forge de um projeto tem de apagar `.git/forge/projeto-*` à mão, o que já está escrito em `docs/hooks.md:53`. A lacuna real é a do G (a chave depende do caminho), que já existia antes.

### O que fica aberto e quem cobre (rodada 3)
- **F** (alta) é do desenho da marca desta entrega. Nenhuma BP posterior o cobre, então tem de ser corrigido aqui.
- **G** (média) é anterior à entrega e fica coberto pela **BP-5** (sandbox obrigatório). Recomendo corrigir já, porque custa uma linha em `versao_sumiu`.
- Continuam com dono:
  - **BP-5:** curinga do shell, `find -delete`, `$(…)`, `python3 -c` e também `rsync --remove-source-files`, que move o conteúdo do `.git/` ou do `.forge/` com rc=0 (o hook não modela `rsync` como remoção, nem na base). A recomendação da rodada 2 continua: a BP-5 deve negar a escrita em `.forge/versao` e `.git/forge/`, e com o F também em `.git/commondir` e `.git/worktrees/`.
  - **BP-2:** o alias por `-c`.
- O C e o H são informativos. O H pode entrar junto com o F.

### Ferramentas (rodada 3)
Só os hooks da branch e os de `f636d27` para comparar, ambos de cópias `git archive` em `$TMPDIR`, e o `git` 2.55.0 local, em repositórios descartáveis. Nenhum remoto foi tocado: os repositórios de teste não têm `origin`, então os `push` liberados pelo hook falharam no próprio git. `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não mexe em workflow nem traz segredo.
