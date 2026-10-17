---
tipo: revisao-seguranca
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 592098a3b3f6ba38bdb5313c5900c5de89cfcb05
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-17
---
# Review de segurança: bp-1

> **Rodada 6** (`592098a`, depois do retrabalho 5): **aprovado**. A mitigação barata do L e a parte do K pedida no retrabalho 5 (sufixo livre do `-i`, nome com versão, `inplace` do gawk, `W`/`--expression`/`-e` colado do `sed`) funcionam, o R10 não dá falso positivo e nenhuma cadeia das cinco rodadas voltou a calar os hooks (nenhuma linha passou de rc=2 para rc=0). Ficam abertos, com a BP-5: o L por grafia não literal (aspas no meio, curinga, `cd .git`) e por lançadores fora da lista, e um resto do K (endereço `$`/`!` antes do `w` do `sed`, `nawk`, `gawk -l inplace`, `perl5.34-x86_64-linux-gnu`). Detalhes na seção "Revalidação após o retrabalho 5", no fim.
>
> **Rodada 5** (`740d7dd`, depois do retrabalho 4): **aprovado**. I e J estão fechados, sem regressão nas cadeias das quatro rodadas, e a tabela de 1117 linhas do autor confere. O que fica aberto é anterior à entrega, não cala os hooks em uma linha como na base e tem dono (BP-5, BP-2); a cobertura da BP-5 depende de o sandbox negar escrita em `.git/forge/` e `.forge/versao` (condição registrada). Detalhes na seção "Revalidação após o retrabalho 4", no fim.
>
> **Rodada 4** (`7ec8c60`, depois do retrabalho 3): **reprovado**. F, G e H estão fechados, e o `.git/` protegido fecha a classe dos ponteiros. Mas o commit `faa4f06` trouxe uma regressão, o achado I (alta): com `perl -i`, o texto do script deixou de ser conferido, e duas linhas voltam a desligar tudo. Junto vai o J (média, anterior à entrega): `perl -0pi` escreve em caminho em vigor. Detalhes na seção "Revalidação após o retrabalho 3", no fim.
>
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

## Revalidação após o retrabalho 3
Escopo: `git diff 5cfa66153150feecfed36b7b8b01276e43350352...7ec8c60b7a793fb911e8ab6c6230f725a6dffbcc`, commits `96032bd`, `faa4f06` e `7ec8c60`, 19 arquivos (+500 / -55). Mesmo método das rodadas anteriores: os hooks da branch (`conformidade`, `parecer` e `vigia`), rodados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, em repositórios descartáveis (git 2.55.0). A marca foi gravada pelo `SessionStart` do `vigia`, e cada comando só foi executado de verdade quando os dois hooks deram rc=0. Para comparar, usei cópias de `9f3fa2b` e `f636d27`. A worktree não foi tocada, exceto por este arquivo.

### Veredito da rodada 4
**Reprovado.** O F, o G e o H fecham. A proteção do `.git/` inteiro fecha a classe dos ponteiros, e não só a variante do `commondir`: refiz as 698 linhas da busca de classe e todas as cadeias das três rodadas, e nenhuma delas cala o hook sem aviso. O commit `faa4f06` (`perl -i` passa pela conferência de escrita), porém, trocou uma checagem pela outra: com `-i`, o texto do script do `perl` deixou de ser conferido. Com isso, duas linhas com rc=0 voltam a apagar a marca e a desligar tudo (achado I). É a mesma regressão que o review apontou como B3.

### F: fechado
- **A marca vem do disco:** `marca_de_projeto` usa `diretorio_comum` (`hooks/_comum.py:95-116` e `:119`), que lê o `.git` sem chamar o git. Num clone principal com `commondir`, devolve None e a raiz vale como marcada (`:104`). Numa worktree, o `gitdir` de volta e o `commondir` têm de apontar para o `.git` da raiz e para o comum (`:112-116`).
- **As cadeias da rodada 3 deram rc=2 já na escrita:** `echo <outro>/.git > .git/commondir`, `tee`, `cp` e `ln -s`, com e sem o `.forge/versao`. Na worktree, a escrita em `<comum>/worktrees/wt/commondir` dá rc=2 por caminho absoluto e também com `cd ../proj/.git/worktrees/wt && echo … > commondir`. Em todas as cadeias, o push e o `git config core.hooksPath` seguintes dão rc=2, e o `vigia` avisa.
- **Com o `commondir` escrito por fora dos hooks** (por um extrator: `tar xf a.tar -C .git`, `cpio -id` dentro de `.git`, ou no `<comum>/worktrees/wt/`): a linha dá rc=0, como o autor declarou. A busca, porém, falha fechado. Depois do `git sparse-checkout set src`, dão **rc=2**: `git push origin HEAD:melhoria/x`, `rm -rf .git/forge`, `cd .git && rm commondir` e `git config core.hooksPath /dev/null`. O `vigia` avisa com o motivo certo (".git da raiz da sessão não se resolve"). Com o `.forge/versao` presente, a conferência roda inteira do mesmo jeito (`rm -rf .forge` dá rc=2).
- **`commondir` entrou na `CRITICO`** (`hooks/conformidade.py:30`), e o `.git/` está em `caminhos` com `quem: []` (`hooks/conformidade.json:37`).

### G: fechado
`versao_sumiu` falha fechado quando a raiz da sessão não existe mais (`hooks/_comum.py:154-160`). Testei três formas de mover a raiz da sessão: `cd .. && mv <raiz> <raiz>x`, `git worktree move . <outro>` e `mv <wt> <wt>x`. Em todas, a linha dá rc=0 (a raiz fica fora da árvore protegida), mas na pasta nova o push e o `git config core.hooksPath` dão **rc=2**, e o `vigia` avisa "a pasta da sessão foi movida ou apagada", gravando no estado da pasta nova e sem recriar a raiz antiga. Apagar ou mover o clone principal a partir de uma worktree também falha fechado. O que sobra está escrito na ADR 0009: uma raiz recriada no mesmo caminho e sem `.git` não se distingue de uma pasta comum. Isso exige escrever acima do projeto, o que o sandbox (BP-5) nega.

### H: fechado
`docs/hooks.md:81` agora manda apagar a marca à mão (`.git/forge/projeto-*`) e diz que "nada a apaga sozinho, nem o `startup`", o que bate com `:53` e com o código. A ADR 0009, item 2, também bate com o código: o diretório comum vem do disco, o `.git/` inteiro é protegido contra escrita direta, a raiz movida falha fechado e a mensagem diz o motivo (`TEXTO_DA_FALHA`, `hooks/_comum.py:173-181`). A ressalva dos extratores na ADR também confere com o que medi.

### Rodadas 1 a 3, de novo: sem regressão
- **A** (7 cadeias): `sparse-checkout`, `clean -fdX`, `clean -fdx`, `clean -fdx .forge/run`, `stash -a`, `reset --hard` e `stash push -- .forge/versao`. A marca fica no lugar, e o push seguinte dá rc=2.
- **B** (22 formas) e **B'** (6 formas): todas dão **rc=2** na própria linha, e o `.forge/versao` fica no lugar.
- **D.1 a D.4** (16 cadeias, no clone e na worktree): terminam com o push e o `git config core.hooksPath` em **rc=2** e o `vigia` avisando.
- **Extras com dono (BP-5):** dois mudaram de resultado, porque o caminho agora toca `.git/`. Passaram a dar **rc=2**: `rm -r .git/fo*`, `python3 -c "…remove('.git/'+'forge/x')"` e `rsync -a --remove-source-files .git/forge/ …`. Continuam com rc=0 e calam tudo, como na base: `find .git -name 'projeto-*' -delete` e `rm $(git rev-parse --git-common-dir)/forge/projeto-*`. São as exceções já entregues à BP-5.
- **Alias por `-c` (BP-2):** a linha dá rc=0, e a marca segura o efeito (o push dá rc=2 e o `vigia` avisa).

### A busca de classe do autor confere
Refiz a tabela de forma independente e cheguei ao mesmo número do autor: **698 linhas, 683 com rc=2 e 15 com rc=0**. A tabela cruza 31 formas de escrita, remoção, renomeação e link (`>`, `>>`, `>|`, `&>`, `tee`, `cp`, `mv`, `ln`, `rm`, `sed -i`, `truncate`, `install`, `dd`, `touch`, `perl -pi`…) com 10 grafias de `commondir`, `config`, `HEAD` e `worktrees/wt/{gitdir,commondir}`, mais formas com `cd` e a sessão numa worktree, cada uma com e sem o `.forge/versao`.

Os 15 casos com rc=0 são todos subcomandos do git: `worktree repair|move|remove|prune`, `init --separate-git-dir`, `update-ref HEAD` e `symbolic-ref HEAD`. Rodei cada um em cadeia com o `sparse-checkout`, e todas terminam com o push em **rc=2** e o `vigia` avisando. Isso porque a busca da marca pelo disco não depende do que esses comandos mudam, e o `init --separate-git-dir` transforma o `.git` em arquivo, que falha fechado. Mais 29 escritores fora da tabela (`awk -i inplace`, `ed`, `ex`, `vim -es`, `patch`, `sponge`, `curl -o`, `wget -O`, `rsync`, `git checkout-index --prefix=.git/`, `git diff|log --output=`, `git archive -o`, `git bundle create`, `mkdir`, `chmod`, heredoc) dão **rc=2**. Ficam com rc=0 só `tar -C .git`, `unzip -d .git`, `cpio -id` (o hook não vê o destino) e `git format-patch -o .git`, que só cria arquivos novos.

### O que o `.git/` protegido abre
- **Falso positivo:** não encontrei nenhum. Testei 20 comandos comuns, todos com **rc=0**:
  - git: `commit`, `add`, `fetch`, `gc`, `stash`, `stash pop`, `switch -c`, `worktree add`, `format-patch -o <fora>`, `rev-parse --git-common-dir`, `sparse-checkout list` e `config --worktree`;
  - leitura do `.git/`: `cat .git/HEAD`, `ls .git` e `grep … .git/config`;
  - arquivos vizinhos com nome parecido: `.gitignore`, `.gitattributes`, `.github/workflows/*.yml` e `src/.gitkeep`.

  O que a regra barra é escrever à mão em `.git/info/exclude` ou em `.git/hooks/`, coisa que um agente não precisa fazer. O B4 do review (worktree aberta por link simbólico dá rc=2 falso) falha para o lado fechado e não tem custo de segurança.
- **Lacuna que sobra:** os extratores (`tar -C`, `unzip -d`, `cpio`) gravam qualquer arquivo dentro de `.git/` com rc=0, inclusive o `.git/config`. Para a marca, `commondir` e `gitdir` falham fechado na leitura do disco, como medido acima. Um `.git/config` trocado, porém, só é visto pelo hook quando o comando seguinte passa pela conferência. Isso já acontecia na base, porque o hook nunca modelou extratores, e vale também para os outros caminhos em vigor (`tar -C .claude`). Recomendação (baixa): a BP-5 inclui os extratores no que o sandbox nega em `.git/`, `.claude/` e `.forge/`, ou o hook passa a tratar `tar -C`, `unzip -d` e `cpio` (cwd) como destino de escrita (`SO_DESTINO`).

### I. Com `perl -i`, o script deixa de ser conferido: duas linhas desligam tudo de novo · alta (regressão de `faa4f06`)
- **Evidência:** `hooks/conformidade.py:680` e `:687`. Quando o `perl` tem `-i`, o ramo `elif INTERPRETES.match(prog) and not perl_no_lugar` é pulado, e o `checar_texto` dos argumentos não roda. O ramo de `:697-699` confere só os arquivos como destino de escrita, e o `-e 'unlink …'` não é um caminho. Em `9f3fa2b`, as mesmas linhas davam rc=2.
- **Reprodução** (clone principal, `.forge/versao` presente, uma chamada do Bash por linha):
  1. `perl -i -e 'unlink glob q(.git/forge/projeto-*)' src/app.js`: rc=0, e a marca é apagada.
  2. `git sparse-checkout set src`: rc=0, e o `.forge/versao` some.

  Em seguida, `git push --force origin main` dá rc=0, e o `vigia` no `Stop` fica mudo. Também dão rc=0 com o arquivo presente: `perl -pi -e 'unlink q(.forge/versao)' src/app.js`, `perl -pi -e 'unlink q(.git/forge/x)' src/app.js`, `perl -i -pe 1 -e 'unlink q(.forge/config.json)' src/app.js` e `perl -i -pe 'unlink q(.forge/run/x)' src/app.js`. Sem o `.forge/versao`, a `CRITICO` pega o texto e dá rc=2. Por isso a ordem certa é apagar a marca primeiro.
- **Caminho de ataque:** o mesmo do D, do F e do achado 1 do incidente. Um agente no projeto, depois de um bloqueio ou levado por conteúdo injetado, roda duas linhas com cara de manutenção, e dali em diante nenhum hook age nem avisa. Não é a exceção `python3 -c` da BP-5: o caminho está escrito literalmente no texto, e o hook já o pega no `perl -e` sem `-i` (rc=2).
- **Correção mínima** (esforço P, dono `tech-lead`): o `perl -i` passa pelas **duas** conferências. Basta tirar o `and not perl_no_lugar` de `:687` e, dentro desse ramo, chamar também o `checar_escrita` dos arquivos quando `perl_no_lugar` for verdadeiro (ou trocar o `elif` de `:697-699` por um `if` à parte para o `perl_no_lugar`). Fixtures: `perl-i-unlink-marca-bloqueia` (a linha 1 acima dá rc=2), `perl-i-unlink-versao-bloqueia` e a cadeia com o `sparse-checkout` terminando em push com rc=2.

### J. `perl` com opção numérica junto do `-i` (`-0pi`, `-0777pi`) escreve em caminho em vigor · média (anterior à entrega)
- **Evidência:** a regex `-[a-zA-Z]*i[a-zA-Z.]*` (`hooks/conformidade.py:680`) não casa com um grupo de opções que começa com algarismo.
- **Reprodução:** `perl -0pi -e 's/^/x/' .githooks/pre-push`, `perl -0pi -e 1 .claude/settings.json`, `perl -0777pi -e '…' .git/config` e `perl -0pi -e 1 .forge/versao` dão rc=0 e reescrevem o arquivo. As formas separadas (`perl -0 -i -pe`, `perl -0777 -pi`, `perl -l -pi`) já dão rc=2. Em `9f3fa2b` e em `f636d27`, as quatro também dão rc=0, então não é regressão: é a parte da busca de classe que o `faa4f06` não cobriu. O `ruby -i -pe … <arquivo>` também não é tratado como escrita no lugar (rc=0).
- **Caminho de ataque:** um agente reescreve um arquivo em vigor numa linha. Para `.claude/` e `.githooks/`, o `vigia` (`em-vigor`) avisa no `Stop`. O `.git/config` fica fora dessa comparação: por ali dá para gravar `core.hooksPath` sem escrever a palavra literalmente (`\x50`), o que desliga o `pre-push` do git. O `conformidade` continua barrando push direto para `develop`, `homolog` e `main` por conta própria. Não apaga a marca: um arquivo reescrito no lugar continua existindo.
- **Correção mínima** (esforço P, dono `tech-lead`, junto com o I): aceitar algarismos no grupo de opções, por exemplo `-[0-9a-zA-Z]*i[a-zA-Z.]*`, e tratar `ruby -i` como o `perl -i`. Fixture: `perl-0pi-em-vigor-bloqueia`.

### O que fica aberto e quem cobre (rodada 4)
- **I** (alta) é regressão desta entrega. Nenhuma BP posterior a cobre, então tem de ser corrigida aqui. O **J** (média) custa uma regex no mesmo lugar e deve entrar junto, porque a busca de classe desta entrega se propôs a fechar o `perl -i`.
- Continuam com dono:
  - **BP-5:** `find -delete`, `$(…)`, o curinga do shell fora do `.git/`, interpretador com nome montado (`python3 -c`, e também `ruby -e 'File.delete(…)'`, que a `ESCRITA_NO_TEXTO` não reconhece) e os extratores (`tar -C`, `unzip -d`, `cpio`). A recomendação de negar a escrita em `.forge/versao`, `.git/forge/`, `.git/commondir` e `.git/worktrees/` continua, agora com `.git/config` e os extratores.
  - **BP-2:** o alias por `-c`.
- O C continua informativo. O B4 do review falha para o lado fechado e é do review.

### Ferramentas (rodada 4)
Só os hooks de `7ec8c60`, `9f3fa2b` e `f636d27`, de cópias `git archive` em `$TMPDIR`, e o `git` 2.55.0 local, em repositórios descartáveis sem `origin`: os `push` liberados pelo hook falharam no próprio git, e nenhum remoto foi tocado. A suíte da branch não foi rodada (R-TETO). `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não mexe em workflow nem traz segredo.

## Revalidação após o retrabalho 4
Escopo: `git diff ae998d119afbab0f1ac5bba181b1284e2f5555fd...740d7dd41b90b78bef891fc6cd6245e27320e7ec`, commits `7a3114a`, `2827834`, `56e8144` e `740d7dd`, 16 arquivos (+292 / -17). Mesmo método das rodadas anteriores: os hooks de `740d7dd` (`conformidade` e `vigia`), rodados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, em repositórios descartáveis (git 2.55.0, sem `origin`); a marca gravada pelo `SessionStart`; cada passo de cadeia só executado de verdade quando o hook deu rc=0. Para comparar, cópias de `7ec8c60` e `f636d27`. `python3 -m unittest tests.test_hooks` na cópia: 19 testes, OK (suíte inteira não rodada, R-TETO). A worktree não foi tocada, exceto por este arquivo.

### Veredito da rodada 5
**Aprovado.** O I (alta) e o J (média) estão fechados, o B4 e o R9 do review conferem, e nenhuma cadeia das quatro rodadas voltou a calar os hooks. Comparei 334 linhas entre `7ec8c60` e `740d7dd`: nenhuma passou de rc=2 para rc=0, e 30 passaram de rc=0 para rc=2. O que sobra (K, L, M abaixo) já existia na base, onde uma linha só desligava tudo; aqui são precisas duas e a segunda camada (a marca) segura tudo o que o hook modela. A classe está escrita na ADR 0009 (item 2, "Resta") e tem dono: BP-5 e BP-2. Ver "Condição" em "O que fica aberto".

### I: fechado
`hooks/conformidade.py:683-697`: o ramo de interpretador roda o `checar_texto` sempre, e o `no_lugar` só soma a conferência de escrita dos alvos. Todas as linhas do I dão **rc=2** na própria linha, e a cadeia com o `git sparse-checkout set src` termina com push e `git config core.hooksPath` em rc=2 e o `vigia` avisando:
- `perl -i -e 'unlink glob q(.git/forge/projeto-*)' src/app.js`, `perl -pi -e 'unlink q(.forge/versao)' src/app.js`, `perl -pi -e 'unlink q(.git/forge/x)' src/app.js`, `perl -i -pe 1 -e 'unlink q(.forge/config.json)' src/app.js`, `perl -i -pe 'unlink q(.forge/run/x)' src/app.js`;
- variantes novas: `perl -0777pi -e 'unlink glob …'`, `perl -i~ -e 'unlink glob …'` (o texto é conferido mesmo quando o `-i` não é reconhecido), `ruby -i -pe 'File.delete(Dir.glob(%q(.git/forge/projeto-*))[0])'`, `gawk -i inplace 'BEGIN{system("rm -rf .git/forge")}'`, `sed -i 's/a/b/w .git/forge/projeto-x'`.

### J: fechado
A regex de `:683` aceita algarismos no grupo, e o `ruby` entrou. Dão **rc=2**: `perl -0pi -e 's/^/x/' .githooks/pre-push`, `perl -0pi -e 1 .claude/settings.json`, `perl -0777pi -e 1 .git/config`, `perl -0pi -e 1 .forge/versao`, `ruby -i -pe 1 .githooks/pre-push`, e também `/usr/bin/perl -pi`, `env perl -pi`, `command perl -pi`, `nice perl -pi`, `exec perl -pi`, `perl -p -i -- <alvo>`, `awk -i inplace 1 <alvo>`, `gawk -i inplace -e '{print}' <alvo>`, e o `w arquivo` do `sed` (`'s/a/b/w<alvo>'`, `-e 'w <alvo>'`, `-n '/x/w <alvo>'`) sobre os cinco alvos (`.githooks/pre-push`, `.claude/settings.json`, `.git/config`, `.forge/versao` e a marca). Na base e em `7ec8c60` essas linhas davam rc=0.

### B4 e R9: conferem
- **B4** (`hooks/_comum.py:116-118`): com a sessão aberta por um link simbólico para uma worktree, a marca é gravada (`projeto-<hash do caminho real>`), `git status`, `ls` e `echo x > src/a.js` dão rc=0, `rm .forge/versao` dá rc=2 e, depois do `sparse-checkout`, o push dá rc=2 e o `vigia` avisa. A comparação só troca o lado do topo pelo caminho real; o `gitdir` de volta continua dentro do `.git/` protegido, então nada novo se abre.
- **R9** (`hooks/vigia.py:324-336`): com a raiz movida e a pasta corrente fora de uma cópia de trabalho, o push dá rc=2, o `vigia` avisa "a pasta da sessão foi movida ou apagada", não cria `.forge/run/` na pasta corrente e não recria a raiz antiga.

### Rodadas 1 a 4, de novo: sem regressão
89 cadeias, executadas de verdade (o mesmo arquivo de cadeias roda contra qualquer cópia):
- **A** (7), **B** (33) e **B'** (3, inclusive `export GIT_ICASE_PATHSPECS=1; git rm .FORGE/VERSAO`) e as quatro formas diretas (`git rm|mv|checkout|restore .forge/versao`): o push seguinte dá **rc=2**; as formas de pathspec dão rc=2 já na linha.
- **D.1 a D.4**: o `SessionStart` à mão não apaga a marca; `cd .git && rm -r forge`, `mv .git .g` e `echo 'gitdir: /nada' > .git` (worktree) dão **rc=2**; o push depois dá rc=2 e o `vigia` avisa.
- **F**: `echo <x>/.git > .git/commondir`, `tee`, `cp`, `ln -s`, e na worktree a escrita em `<comum>/worktrees/wt/commondir` (por caminho absoluto e por `cd`): **rc=2**. Com o `commondir` escrito por fora dos hooks, a busca falha fechado e o `vigia` avisa ".git da raiz da sessão não se resolve" (conferido direto: `git init -q ../x; echo $PWD/../x/.git > .git/commondir; git sparse-checkout set src`, e o `Stop` avisa).
- **G**: `cd .. && mv proj projx`, `git worktree move . <outro>` e `cd .. && mv wt wtx` dão rc=0 na linha, e na pasta nova o push dá **rc=2** e o `vigia` avisa. Apagar o clone principal a partir da worktree mantém o push em rc=2 (o `.forge/versao` da worktree continua lá, então o `vigia` não tem o que avisar; igual em `7ec8c60`).
- **Extras já com dono**: `find .git -name 'projeto-*' -delete` e `rm $(git rev-parse --git-common-dir)/forge/projeto-*` seguidos do `sparse-checkout` continuam calando tudo (BP-5); `git -c alias.x='!rm -rf .git/forge' x` também (BP-2). `rm -r .git/fo*` e `python3 -c "…glob('.git/'+'forge/*')…"` dão rc=2.

**Correção do registro da rodada 4:** escrevi lá que `ed`, `ex`, `vim -es`, `patch`, `sponge` e `chmod` dentro de `.git/` davam rc=2. Refeitos agora na forma simples, com o `.forge/versao` presente, `sponge .git/commondir`, `chmod 000 .git/commondir` e `vim -es -c wq .git/commondir` dão **rc=0**, igual em `7ec8c60`; o rc=2 só aparece com heredoc ou `<<<` (o hook recusa a construção, `nao_modelada`) ou sem o `.forge/versao` (a `CRITICO` pega `.git/`). Não abre a marca: um `commondir` escrito assim faz a busca falhar fechado, como no F. Entra na classe K.

### A busca de classe do autor confere
Rodei o mesmo gerador do autor contra uma cópia nova de `740d7dd`: **1117 linhas, 1076 com rc=2 e 41 com rc=0**, o mesmo número. Os 41, por classe:
- **30, script por arquivo ou pela entrada padrão** (`python3 script.py <alvo>`, `python3 - <alvo> <<'EOF'`, `node script.js <alvo>`, `php script.php <alvo>`, `ruby script.rb <alvo>`, `perl script.pl <alvo>`, × 5 alvos). Sem `-i`, o hook não sabe que o argumento é escrito: é a classe "interpretador" da ADR 0009 e da `docs/hooks.md:36`. **BP-5.** Com `-i`, os alvos são conferidos (`perl -i script.pl <alvo>`: rc=2).
- **6, cadeias git** (`sparse-checkout set src`, `clean -fdX`, `clean -fdx`, `stash -a`, `reset --hard`, `stash push -- .forge/versao`): rc=0 é o esperado, e em cadeia o push dá rc=2 (acima). Fechado pelo desenho da marca.
- **1, `mv proj x`** (a raiz): é o G, rc=0 na linha e falha fechado depois. Fechado.
- **4, `ed -s`, `patch`, `sponge` e `chmod 000` em `.githooks/pre-push`**: rc=0 também em `f636d27` e em `7ec8c60`. **Não entram nesta BP:** não removem a marca nem o `.forge/versao`, e são a classe K (escritor que o hook não modela, sobre caminho em vigor), anterior à entrega. O `vigia` (`em-vigor`) avisa no `Stop` quando o `.githooks/` muda. **BP-5.**

### K. Escritores e formas de edição no lugar que o hook não reconhece, sobre caminho em vigor · baixa (anterior à entrega)
- **Reprodução** (clone principal, `.forge/versao` presente; cada linha dá rc=0 em `740d7dd`, `7ec8c60` e `f636d27`, e reescreve o arquivo):
  - sufixo do `-i` fora de `[0-9a-zA-Z.]`: `perl -i~ -pe 1 .git/config`, `perl -pi~ -e 1 .githooks/pre-push`, `perl -i_bak -pe 1 .claude/settings.json`, `perl -i'*.orig' -pe 1 .forge/versao`, `ruby -i~ -pe 1 .git/config`, `sed -i~ 1d .githooks/pre-push`;
  - nome com versão: `perl5.34.0 -pi -e 1 .githooks/pre-push` (o `INTERPRETES`, `hooks/conformidade.py:47`, aceita `python3.10` mas não `perl5.34.0`, que vem no pacote `perl` do Debian e do Ubuntu);
  - o `inplace` do gawk por outro nome: `gawk -i inplace.awk '{print}' <alvo>`, `gawk -i /usr/share/awk/inplace.awk …`, `gawk --include=/usr/share/awk/inplace.awk …`, `gawk -f /usr/share/awk/inplace.awk -e '{print}' <alvo>`, e `@include "inplace"` dentro do programa;
  - `sed 'W <alvo>' src/app.js` (o `W` maiúsculo também grava), `sed 'e rm <alvo>'` e `sed 's/.*/rm <alvo>/e'` (executam comando);
  - escritores fora do modelo: `ed`, `ex -sc wq`, `vim -es -c wq`, `patch`, `sponge`, `split`, `busybox sed -i`, `php -r 'copy(…)'`, `chmod`, `chown`, `setfacl`;
  - caminho só no argumento: `perl -e 'open F,">",$ARGV[0]' <alvo>`, `awk -v f=<alvo> 'BEGIN{print 1 > f}'`, `awk 'BEGIN{print 1 > ARGV[1]}' <alvo>`, `echo <alvo> | xargs perl -pi -e 1`.
- **Efeito e caminho de ataque:** um agente reescreve um arquivo em vigor numa linha. Para `.githooks/` e `.claude/`, o `vigia` avisa no `Stop`. O `.git/config` fica fora dessa comparação (dá para gravar `core.hooksPath` sem a palavra literal e desligar o `pre-push` do git), mas o `conformidade` continua barrando push direto para `develop`, `homolog` e `main` por conta própria. Nenhuma dessas linhas apaga a marca. Corrigir só o `-i~` não reduz o risco: há uma dúzia de escritores equivalentes com rc=0 desde a base.
- **Cobertura:** **BP-5** (o sandbox nega a escrita em `.githooks/`, `.claude/`, `.git/` e `.forge/`, que é o que fecha a classe). **Correção mínima opcional** (esforço P, dono `tech-lead`, nesta entrega ou na BP-5): para `perl`/`ruby`/`sed`, tratar tudo depois do `i` como sufixo (`-[0-9a-zA-Z]*i.*`), aceitar `perl[\d.]*` e `ruby[\d.]*` no `INTERPRETES`, tratar `inplace` em qualquer valor de `-i`/`--include`/`-f` e no texto do programa como edição no lugar, e `W` como o `w` do `sed`; e incluir `ed`, `ex`, `sponge`, `split`, `chmod`, `chown` e `setfacl` em `TODOS_OS_ARGUMENTOS`. A ADR 0009 e a `docs/hooks.md:36` dizem "`-i` em qualquer combinação de opções agrupadas"; o sufixo não alfanumérico não é opção agrupada, então o texto não é falso, mas convém citar o limite se a regex não mudar.

### L. Programa que o hook não modela apaga a marca pelo caminho literal: duas linhas calam tudo · média (anterior à entrega, mesma classe do `find -delete`)
- **Reprodução** (clone principal, `.forge/versao` presente; uma chamada do Bash por linha):
  1. `busybox rm -rf .git/forge` (rc=0; a marca some; executado, como `perl5.34.0`, `ionice` e `vim -es` abaixo). Também dão rc=0 no hook, com o caminho da marca: `perl5.34.0 -e 'unlink glob q(.git/forge/projeto-*)'`, `ionice rm -rf .git/forge`, `chrt -o 0 rm <marca>`, `taskset 1 rm <marca>`, `flock /tmp/l rm <marca>`, `unshare rm <marca>`, `script -qc 'rm <marca>' /dev/null`, `vim -es -c '!rm -rf .git/forge' -c q`, `ex -sc 'call delete("<marca>")' -c q`, `gdb -batch -ex 'shell rm <marca>'`, `gio remove <marca>`.
  2. `git sparse-checkout set src` (rc=0).

  Depois, `git push --force origin main`, `git config core.hooksPath /dev/null` e `rm -rf .githooks` dão rc=0, e o `vigia` no `Stop` fica mudo. Os lançadores que o hook conhece (`timeout`, `stdbuf`, `nohup`, `setsid`, `nice`) dão rc=2.
- **Não é regressão:** na base `f636d27`, uma linha só (`busybox rm .forge/versao`, `perl5.34.0 -e 'unlink q(.forge/versao)'`, `ionice rm .forge/versao`) calava tudo. Em `740d7dd`, essas mesmas linhas sobre o `.forge/versao` deixam o push em rc=2 e o `vigia` avisando: a marca segura, e é preciso apagá-la primeiro, por um programa fora do modelo. É a classe "quem escreve fora do hook" da ADR 0009 (item 2, "Resta"), a mesma do `find -delete` e do `$(…)`, já atribuída à BP-5.
- **Caminho de ataque:** o do achado 1 do incidente, agora com duas linhas e um programa incomum. Um agente depois de um bloqueio, ou levado por conteúdo injetado.
- **Cobertura e condição:** **BP-5**, **desde que** o sandbox negue a escrita em `.git/forge/` e em `.forge/versao` (`denyWithinAllow`), recomendação que repito desde a rodada 2. Sem isso, o sandbox deixa escrever dentro do projeto e a classe fica aberta. **Mitigação barata recomendada** (esforço P, dono `tech-lead`, não bloqueia): com o `.forge/versao` presente, recusar qualquer linha do Bash que cite `.git/forge` ou `forge/projeto-` fora de leitura pura, como a `CRITICO` já faz no modo degradado; e incluir `ionice`, `chrt`, `taskset`, `flock`, `unshare` e `script` entre os lançadores. Isso fecha a forma literal para qualquer programa; o que monta o caminho em tempo de execução continua com a BP-5.

### M. `chmod 000` em `.forge/` ou `.git/forge/` faz os hooks caírem com erro interno · informativa
`chmod 000 .forge` (ou `chmod 000 .git/forge` seguido do `sparse-checkout`) dá rc=0. Depois, todo comando dá rc=2 com "erro interno" (o `Path.is_file` levanta `PermissionError`), e o `vigia` no `Stop` fica mudo. Falha para o lado fechado; o custo é a sessão travada sem mensagem clara. Correção opcional: tratar `PermissionError` na busca da marca e do `.forge/versao` como "não se resolve" (motivo `git`), com o aviso do `vigia`. Dono `tech-lead`; pode ir com a BP-5.

### O que o retrabalho 4 abre
Nada de segurança. Testei 17 comandos comuns que passam pelos ramos novos (`sed 's/new/old/'`, `sed -i.bak 's/w/x/'`, `sed 's/x/y/w out.txt'`, `perl -pi -e`, `perl -i~ -pe` sobre `src/`, `ruby -i -pe`, `awk '{print $1}'`, `awk -i inplace '{print}' src/app.js`, `awk '{print > "out.txt"}'`, `php -r 'echo fwrite(STDOUT,…)'`, `node -e "…readFileSync…"`, `perl -ne 'print if /system\(/'`, `grep -n inplace`): todos **rc=0**. A ADR 0009 (item 2) e a `docs/hooks.md:36` batem com o código, com a ressalva do K sobre o sufixo.

### O que fica aberto e quem cobre (rodada 5)
- **Fechados nesta rodada:** I, J, B4 e R9. Nenhum achado bloqueia.
- **BP-5:** K (escritores e formas de edição no lugar fora do modelo, inclusive `ed`/`patch`/`sponge`/`chmod` em `.githooks/`, que **não entram nesta BP**), L (programa fora do modelo apaga a marca), M, os 30 de script por arquivo ou pela entrada padrão, `find -delete`, `$(…)`, curinga do shell fora do `.git/` e os extratores (`tar -C`, `unzip -d`, `cpio`). **Condição para a cobertura valer:** a BP-5 nega a escrita em `.git/forge/`, `.forge/versao`, `.git/config`, `.git/commondir`, `.git/worktrees/`, `.githooks/` e `.claude/`. Peço que essa lista entre no requisito da BP-5.
- **BP-2:** o alias por `-c` (`git -c alias.x='!rm -rf .git/forge' x`, que também cala tudo em duas linhas).
- **Recomendado, sem bloquear:** a mitigação do L (recusar a linha que cite `.git/forge` com o `.forge/versao` presente, mais os seis lançadores), que fecha a forma literal agora, a custo de uma regex.
- O C continua informativo.

### Comandos para reproduzir (VV-1)
Numa cópia `git archive 740d7dd` em `$TMPDIR`, num repositório descartável com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/app.js` commitados, e com o `SessionStart` do `vigia` já rodado (`CLAUDE_PROJECT_DIR` na raiz):
- K: `echo '{"tool_name":"Bash","tool_input":{"command":"perl -i~ -pe 1 .git/config"},"agent_type":"forge:dev","hook_event_name":"PreToolUse","tool_use_id":"t","cwd":"'$PWD'"}' | python3 <cópia>/hooks/conformidade.py; echo $?` → 0.
- L: o mesmo com `busybox rm -rf .git/forge` → 0; executar; depois o mesmo com `git sparse-checkout set src` → 0; executar; depois com `git push --force origin main` → 0, e `echo '{"hook_event_name":"Stop","session_id":"s"}' | python3 <cópia>/hooks/vigia.py` sem saída.
- M: o mesmo com `chmod 000 .forge` → 0; executar; depois qualquer comando → 2 com "erro interno" no stderr.

### Ferramentas (rodada 5)
Só os hooks de `740d7dd`, `7ec8c60` e `f636d27`, de cópias `git archive` em `$TMPDIR`, e o `git` 2.55.0 local, em repositórios descartáveis sem `origin`: os `push` liberados pelo hook falharam no próprio git, e nenhum remoto foi tocado. `busybox`, `gawk`, `vim`, `gdb` e `gio` só foram usados nesses repositórios. `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não mexe em workflow nem traz segredo.

## Revalidação após o retrabalho 5
Escopo: `git diff bbacc2c8515ef1df0d1c38f16470df3f898f4cc3...592098a3b3f6ba38bdb5313c5900c5de89cfcb05`, commits `b500364` e `592098a`, 10 arquivos (+203 / -9): `hooks/conformidade.py`, seis fixtures novas, ADR 0009 (item 2), `docs/hooks.md:36` e `changelog.d/bp-1.md`. O método é o das rodadas anteriores: os hooks de `592098a` rodados com `python3` a partir de uma cópia `git archive` em `$TMPDIR`, em repositórios descartáveis (git 2.55.0, sem `origin`), com a marca gravada pelo `SessionStart`. Em cada cadeia, um passo só foi executado de verdade quando o hook deu rc=0. Para comparar, usei uma cópia de `740d7dd`. `python3 -m unittest tests.test_hooks` na cópia deu 19 testes, OK, inclusive as seis fixtures novas (a suíte inteira não foi rodada, R-TETO). Na worktree, só este arquivo foi tocado.

### Veredito da rodada 6
**Aprovado.** A mitigação barata do L fecha o que prometia: a forma literal da marca e os seis lançadores. A parte do K pedida no retrabalho 5 também está fechada, e o R10 não dá falso positivo. Nenhuma linha das baterias das rodadas anteriores passou de rc=2 para rc=0. O que sobra é da classe "quem escreve fora do hook" (L) ou "escritor e forma de edição fora do modelo" (K). Essas classes já existiam na base, onde uma linha só desligava tudo, e têm dono na BP-5. Abaixo, por classe, com o comando que reproduz e quem cobre.

### Mitigação do L (marca citada e lançadores): funciona
`hooks/conformidade.py:51-52, 581-583, 718-719`. Com o `.forge/versao` presente, dão **rc=2** na própria linha:
- forma literal, para qualquer programa: `busybox rm -rf .git/forge`, `busybox rm -rf .git/forge/`, `perl5.34.0 -e 'unlink glob q(.git/forge/projeto-*)'`, `busybox sh -c 'rm <marca>'`, `gio remove|trash|move <marca>`, `vim -es -c '!rm -rf .git/forge' -c q`, `ex -sc 'call delete("<marca>")' -c q`, `gdb -batch -ex 'shell rm <marca>'`, `chmod 000 .git/forge`, e também `rm $(git rev-parse --git-common-dir)/forge/projeto-*` e `git -c alias.x='!rm -rf .git/forge' x`, porque a regex pega `forge/projeto-`. As duas últimas eram extras da rodada 5 e fecham na forma literal;
- lançadores: `ionice`, `chrt -o 0`, `taskset 1`, `flock /tmp/l`, `unshare` e `script -qc`, também por `env ionice`, `nice ionice`, `sh -c 'ionice …'`, `bash -c "taskset 1 true"`, `xargs flock …` e `/usr/bin/script`.

Em cadeia (`<linha>`, depois `git sparse-checkout set src`, depois `git push --force origin main`, `git config core.hooksPath /dev/null` e `rm -rf .githooks`), `busybox rm -rf .git/forge`, `ionice rm -rf .git/forge`, `perl5.34.0 -e 'unlink …'`, `vim -es -c '!rm …'`, `gio remove` e `chmod 000 .git/forge` deixam o push em **rc=2** e o `vigia` avisando. Em `740d7dd`, os quatro primeiros calavam tudo, e o `chmod` derrubava os hooks com erro interno.

### K, parte do retrabalho 5: fechada
`hooks/conformidade.py:47-48, 212-246, 734, 754, 765, 784`. Sobre os cinco alvos (`.githooks/pre-push`, `.claude/settings.json`, `.git/config`, `.forge/versao` e a marca), dão **rc=2**; em `740d7dd`, todas davam rc=0:
- **sufixo livre do `-i`:** `perl -i~`, `-i_bak`, `-i-old`, `-i,b`, `-pi~`, `-i'*.orig'`, `-pi'/tmp/*'`, `-s -pi~`, `-l0pi`, `-x -i`, `-C -i`, `-E 'say 1' -i`, `-Mstrict -pi`, `-I lib -pi`, `ruby -i~`, `ruby -W0 -i`, `ruby -rfileutils -i`, `sed -i~`, `sed -E -i~` e `sed --in-place=~`;
- **nome com versão:** `perl5.34.0`, `/usr/bin/perl5.34.0`, `env perl5.34.0`, `ruby3.0`, `ruby3.2` e `python3.12 -c "open(…,'w')"`;
- **`inplace` do gawk:** `-i inplace.awk`, `-i /usr/share/awk/inplace.awk`, `-iinplace`, `-i INPLACE`, `--include inplace`, `--include=…/inplace.awk`, `-f …/inplace.awk -e`, `-f …/inplace.awk -f prog.awk`, `@include "inplace"` no programa e `AWKPATH=… gawk -i inplace`;
- **`sed`:** `'W <alvo>'`, `--expression='W <alvo>'`, `--expression 'W <alvo>'`, `-ne'W <alvo>'`, `-e 1d -e'w <alvo>'` e `-s -n 'W <alvo>'`.

**R10, sem falso positivo.** Dão rc=0, corretamente: `perl -Mstrict -e 'print' .githooks/pre-push` (só leitura), `perl -ne print <alvo>`, `perl -CSDi -pe 1 <alvo>` (o `i` do `-C` é a camada de entrada, não edição no lugar) e `perl -w -- -pi <alvo>` (depois do `--`, `-pi` é o nome do script). Comandos comuns sobre `src/` também dão **rc=0**: `sed 's/a/b/'`, `sed -n '/W/p'`, `sed -e 's/Warn/x/'`, `sed -i 's/w x/y/'`, `awk '{print}'`, `perl -pi -e 's/a/b/'` e `perl -i~ -pe 1`. Os 17 comuns da rodada 5 continuam em rc=0.

### Rodadas 1 a 5, de novo: sem regressão
Usei os mesmos arquivos de comandos e de cadeias da rodada 5, contra `740d7dd` e contra `592098a`:
- **comandos soltos** (bateria da rodada 1, 298; dos lançadores e da marca, 29; da comparação da rodada 5, 332; comuns, 17): nenhuma linha passou de rc=2 para rc=0. Passaram de rc=0 para rc=2: 105 da primeira, 22 da segunda e 126 da terceira. Os 17 comuns seguem em rc=0;
- **89 cadeias** (A, B, B', as quatro formas diretas, D.1 a D.4, F, G, extras): todas iguais a `740d7dd` ou melhores. Mudaram para melhor as sete que citam a marca (acima). O G e o apagamento do clone principal a partir da worktree continuam como na rodada 5;
- **busca de classe do autor** (o mesmo gerador): **1117 linhas, 1082 com rc=2 e 35 com rc=0**, contra 1076 e 41 em `740d7dd`. As seis que saíram são as do alvo "marca" (literal). Os 35 são: 24 de script por arquivo ou pela entrada padrão (BP-5), 6 cadeias git (fechadas pela marca), 1 `mv proj x` (G, falha fechado depois) e 4 de `ed`, `patch`, `sponge` e `chmod 000` em `.githooks/pre-push` (K, BP-5).

### O que fica aberto, por classe
**L, por grafia não literal e lançadores fora da lista · média (não muda; anterior à entrega; BP-5).** A mitigação procura o texto `.git/forge` ou `forge/projeto-` na linha. A mesma marca, escrita de outro jeito, passa. Reprodução: clone principal, `.forge/versao` presente, uma chamada por linha, tudo **rc=0**. Cada uma das cinco cadeias abaixo, seguida de `git sparse-checkout set src`, deixa push, `core.hooksPath` e `rm -rf .githooks` em rc=0 e o `vigia` mudo:
- aspas no meio: `busybox rm -rf '.git/'forge`; também rc=0 na linha: `".git"/forge` e `.git/fo''rge`;
- curinga e caminho equivalente: `busybox rm -rf .git/fo*`; também rc=0 na linha: `.git/fo?ge`, `.git/[f]orge`, `.git//forge` e `.git/./forge`;
- `cd .git && busybox rm -rf forge`;
- `busybox rm -rf "$(git rev-parse --git-common-dir)/forge"` e `busybox find .git -name 'projeto-*' -delete` (rc=0 na linha);
- lançadores fora da lista: `setpriv rm -rf .git/fo*`; também rc=0 na linha: `prlimit`, `setarch x86_64`, `strace -o /dev/null` e `/lib64/ld-linux-x86-64.so.2 /bin/rm`.

Com o `rm` simples, todas essas grafias dão rc=2, porque o `.git/` é protegido. O que escapa é a combinação de programa fora do modelo com grafia não literal. É a classe que eu já tinha descrito na rodada 5 ("o que monta o caminho em tempo de execução continua com a BP-5"), agora com grafias mais simples que o `$(…)`. A ADR 0009 (item 2) diz "a forma literal da marca fecha para qualquer programa". O texto é verdadeiro se "literal" for lido como a grafia exata. Para não ler mais do que o código faz, convém escrever "a grafia `.git/forge` ou `forge/projeto-` na linha" (informativa). **Cobertura:** BP-5, com a condição da rodada 5: o sandbox nega a escrita em `.git/forge/` e `.forge/versao`. Mais regex no hook não fecha a classe, porque cada grafia nova pede outra. Não recomendo uma rodada 7 por isso.

**K, resto · baixa (anterior à entrega; BP-5).** Reprodução nas mesmas condições: dão **rc=0** e, executados numa pasta descartável, reescrevem o arquivo-alvo (conferido):
- `w`/`W` do `sed` precedido de endereço `$`, `!` ou `,`, ou da flag `M`: `sed -n '$w .githooks/pre-push' src/app.js`, `sed -n '1,$w …'`, `sed -n '1!W …'`, `sed '\,a,w …'` e `sed 's/a/b/Mw …'`. A classe antes do `[wW]` em `SED_ESCREVE` (`hooks/conformidade.py:54`) não inclui `$`, `!`, `,` nem `M`. A `docs/hooks.md:36` e a ADR 0009 dizem que "o `w`/`W arquivo` do `sed` conta como escrita, no script solto"; com esses endereços, não conta. **Correção mínima** (P, `tech-lead`): incluir `$!,M` na classe, ou ressalvar o texto;
- `nawk -i inplace '{print "X"}' .githooks/pre-push`: aqui o `nawk` é o `gawk` (alternativa do Debian), e `AWKS` não o lista;
- `gawk -l inplace 'BEGINFILE{inplace::begin(FILENAME,"")} ENDFILE{inplace::end(FILENAME,"")} 1' <alvo>`, e o mesmo com `--load=inplace` ou com `@load "inplace"` no programa. O `awk_no_lugar` olha só `-i`, `--include`, `-f` e `@include`, e a documentação também cita só esses;
- `perl5.34-x86_64-linux-gnu -pi -e 1 <alvo>`: o binário está em `/usr/bin` no Debian e no Ubuntu, e o nome com sufixo não casa com `^(perl|ruby)[\d.]*$`;
- o que já estava na rodada 5 e a documentação já entrega à BP-5: `ed`, `ex`, `vim -es`, `patch`, `sponge`, `split`, `chmod`, `chown`, `busybox sed -i`, `chmod 000 .forge` (M). E também: `sed 'e …'` e `s/…/…/e` (executam comando, por exemplo `sed 'e rm .forge/versao' src/app.js`, que dá rc=0 e cuja remoção a marca segura), caminho só no argumento (`awk -v f=<alvo> 'BEGIN{print 1 > f}'`, `awk 'BEGIN{print 1 > ARGV[1]}' <alvo>`, `perl -e 'open F,">",$ARGV[0]' <alvo>`), alvo pela entrada padrão (`echo <alvo> | xargs perl -pi -e 1`), `gawk -E prog.awk <alvo>`, `setfacl`, `php -r 'copy(…)'` e `git apply`/`patch -p1 < x.diff`. Estes não são citados um a um na `docs/hooks.md:36` (lá está "`busybox` e afins"). Convém acrescentar "`sed` com `e`, caminho só no argumento ou na entrada padrão" à lista da BP-5 (informativa).

Nenhuma linha do K apaga a marca: só na grafia literal ela é alvo, e essa grafia dá rc=2 pela mitigação. Para `.githooks/` e `.claude/`, o `vigia` avisa no `Stop` (conferido com `nawk` e com `sed '$w'`).

**Falso positivo da mitigação · informativa.** Com o `.forge/versao` presente, também dão rc=2: `ls .git/forge`, `cat .git/forge/projeto-*`, `grep -rn '.git/forge' docs`, `git log --grep=forge/projeto-`, `ionice -c3 git status` e `./script` (um programa local de nome `script`). Isso está de acordo com a decisão do Jarvis ("a linha que cite `.git/forge` … é recusada"). Falha para o lado fechado, e o custo é só atrito. Se incomodar, a correção é liberar a leitura pura, como eu tinha sugerido na rodada 5.

### O que fica aberto e quem cobre (rodada 6)
- **Fechados nesta rodada:** a mitigação do L na forma literal e com os seis lançadores; do K, o sufixo livre, o nome com versão, o `inplace` por `-i`/`--include`/`-f`/`@include` e o `W`/`--expression`/`-e` colado; e o R10. Nenhum achado bloqueia.
- **BP-5:** o L por grafia não literal e por lançadores fora da lista; o resto do K acima; o M (`chmod 000 .forge`); os 24 casos de script por arquivo ou pela entrada padrão; `find -delete`; `$(…)`; os extratores. **Condição, repetida:** a BP-5 nega a escrita em `.git/forge/`, `.forge/versao`, `.git/config`, `.git/commondir`, `.git/worktrees/`, `.githooks/` e `.claude/`. A ADR 0009 e a `docs/hooks.md:36` já trazem essa lista.
- **BP-2:** o alias por `-c` com grafia não literal (`git -c alias.x='!rm -rf .git/fo*' x`). A forma literal agora dá rc=2.
- **Recomendado, sem bloquear** (P, `tech-lead`, nesta entrega ou na BP-5): `$!,M` na classe do `SED_ESCREVE`, `nawk` em `AWKS`, `-l`/`--load`/`@load` no `awk_no_lugar`, e `^(perl|ruby)[\d.]*(-[\w-]+)?$` no `PERL_OU_RUBY` e no `INTERPRETES`. A alternativa é ressalvar o texto da `docs/hooks.md:36` e da ADR 0009 sobre o `sed`, que hoje promete um pouco mais do que o código cobre.
- O C continua informativo.

### Comandos para reproduzir (VV-1)
Use uma cópia `git archive 592098a` em `$TMPDIR` e um repositório descartável com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/app.js` commitados. Antes, rode o `SessionStart` do `vigia` (`CLAUDE_PROJECT_DIR` na raiz). Para cada linha `<L>`: `echo '{"tool_name":"Bash","tool_input":{"command":"<L>"},"agent_type":"forge:dev","hook_event_name":"PreToolUse","tool_use_id":"t","cwd":"'$PWD'"}' | python3 <cópia>/hooks/conformidade.py; echo $?`.
- Mitigação: `busybox rm -rf .git/forge` → 2; `ionice rm -rf .git/forge` → 2.
- K fechado: `perl -i~ -pe 1 .git/config` → 2; `perl5.34.0 -pi -e 1 .githooks/pre-push` → 2; `gawk --include=/usr/share/awk/inplace.awk '{print}' .githooks/pre-push` → 2; `sed --expression='W .githooks/pre-push' src/app.js` → 2.
- R10: `perl -Mstrict -e 'print' .githooks/pre-push` → 0.
- L aberto: `busybox rm -rf .git/fo*` → 0; execute; `git sparse-checkout set src` → 0; execute; `git push --force origin main` → 0; e `echo '{"hook_event_name":"Stop","session_id":"s"}' | python3 <cópia>/hooks/vigia.py` não imprime nada.
- K aberto: `sed -n '$w .githooks/pre-push' src/app.js` → 0; `nawk -i inplace 1 .githooks/pre-push` → 0; `perl5.34-x86_64-linux-gnu -pi -e 1 .githooks/pre-push` → 0.

### Ferramentas (rodada 6)
Usei só os hooks de `592098a` e de `740d7dd`, de cópias `git archive` em `$TMPDIR`, os arquivos de comandos e de cadeias da rodada 5, o gerador de classe do autor e o `git` 2.55.0 local, em repositórios descartáveis sem `origin`: os `push` liberados pelo hook falharam no próprio git, e nenhum remoto foi tocado. `busybox`, `gawk`/`nawk`, `perl5.34-x86_64-linux-gnu` e `setpriv` só rodaram nesses repositórios. `gitleaks`, `zizmor` e `actionlint` não se aplicam: a entrega não mexe em workflow nem traz segredo.
