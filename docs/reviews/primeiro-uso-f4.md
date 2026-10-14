---
tipo: review
contrato: 1
pedido: primeiro-uso-f4
branch: melhoria/primeiro-uso-f4
commit: 8d99869
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F4 (instalação intocável e travas)

- **Mudança:** `hooks/conformidade.py` (travas do `git`, do `gh` e do `claude`, `checar_remocao`, confirmação `ask`), `Hook.iniciante()` e `copia_principal()` em `hooks/_comum.py`, `tests/test_hooks.py` (aceita `esperado.pergunta`), 105 fixtures `trava-*` em `tests/hooks/conformidade/`, invariantes novos em `tests/config.json`, `docs/hooks.md`, `skills/modo-iniciante`, uma linha no `agents/jarvis.md`, `CHANGELOG.md`.
- **Já coberto antes (só ganhou fixture e a mensagem simples):** `push --force`, `-f`, `+refspec`, push e merge na `main`, push para `develop`/`homolog` (inclusive `--delete` e `:ref`), caminhos em vigor (`.claude/`, `.githooks/`, `.forge/versao|config.json|run/`, `~/.claude/*`).
- **Acrescentado (recusa para todos):** `gh repo delete`, `gh api -X DELETE repos/<dono>/<repo>` e GraphQL `deleteRepository`; `gh repo edit --visibility public`, `gh api` com `private=false` ou `visibility=public`; `git push --mirror`; `filter-branch`, `filter-repo`, `rebase` com `main`/`develop`/`homolog` em uso e `branch -D|-d|--delete` delas; `claude plugin uninstall|remove|disable|update` e `marketplace add|remove`, `claude config set|add|remove`; `rm`/`mv` de pasta que contém caminho em vigor (`rm -rf .forge`), sem alcançar a raiz do projeto nem as pastas acima dela (limpeza de worktree segue livre).
- **Perfil iniciante (`.forge/perfil`, lido da cópia ou da principal):** a recusa troca o texto técnico pela consequência em linguagem simples e o caminho (site do GitHub, `forge desfazer`, sugestão ao Forge). `reset --hard`, `clean -f`, `checkout -- .`, `restore .`, `gh repo archive` e `rebase` de branch já enviada respondem `permissionDecision: "ask"` (saída 0); se a mesma linha tiver uma recusa, ela vence. No perfil padrão esses cinco ficam como estavam (nada novo para quem programa).
- **Instalação intocável:** a recusa de caminho em vigor passa a sugerir registrar como sugestão ao Forge; o Jarvis e a skill `modo-iniciante` mandam guardar o pedido em `~/.local/state/forge/sugestoes/` (a F6 envia).
- **Pendência documentada (`docs/hooks.md`, `CHANGELOG.md`):** o comando assistido com backup (`forge config`, `forge perfil`) não existe. `.forge/perfil` ficou de fora de `caminhos`: a skill `novo-projeto` o grava hoje e proteger agora quebraria o primeiro uso; entra quando o comando existir.
- **Vermelho antes:** as fixtures e a asserção `pergunta` foram escritas antes do código; sem a mudança falharam 58 fixtures e 7 deram erro. **Verde depois:** 404 testes (`python3 -m unittest discover -s tests`) e `scripts/validar-plugin.sh` passam. Fixtures sem rede (`R-CUSTO`) e sem termo de projeto (`R-NEUTRO`).
- **Atenção ao dono:** toca `hooks/` e `tests/hooks/`: o PR precisa do rótulo `afrouxa-regra`. Nenhuma fixture existente mudou de resultado; nada foi afrouxado (só se acrescentam recusas e confirmações). Atenção de review: o `branch -d/-D` de `develop`/`homolog` e o `rm` de pasta são recusas novas para todos os papéis. Sem mudança de versão (ADR 0006). Depende do #103 e do #102.

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente (tech-lead, HEAD 3e91376)

Parecer: **reprovado**. Revisei o diff a partir de 279bab5 e sondei o hook com cerca de 90 comandos, nos perfis padrão e iniciante, num repositório de teste (papel `tech-lead`, branch `melhoria/x` publicada).

**Validação local** (cota do Actions esgotada): `python3 -m unittest discover -s tests` passou (404 testes, OK). `scripts/validar-plugin.sh` passou. `catraca.py --base origin/develop` (b5e5d3d), no modo `regras`, saiu com 1: só pede o rótulo `afrouxa-regra` para `hooks/_comum.py` e `hooks/conformidade.py`, como o esperado, e o rótulo ainda não foi aplicado. O modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`) passou, avaliado sobre o parecer de autor. O modo `pr-texto` passou. Versão 0.12.0 igual à da base, e há 3 linhas novas em `[Não publicado]` (F2, F3, F4): ok.

**Falsos positivos (fluxo legítimo)**
- Liberados, como deve ser: `git branch -d/-D/--delete melhoria/*`; `rm -rf` de `$TMPDIR`, `/tmp/...` e `../wt/...`; `git worktree remove [--force]`; `claude plugin validate|install|marketplace update`. `reset --hard`, `clean -fd`, `checkout .` e `restore .` continuam livres no perfil padrão. No iniciante, `restore --staged .` e `clean -n` ficam livres.
- `ask` sem TTY: o hook não lê o terminal nem espera resposta. Ele imprime o JSON e sai com 0 na hora (medido). Quem decide é o Claude Code: num subagente em segundo plano, ou com `-p` sem ferramenta de permissão, o que não está pré-aprovado é negado, e o agente recebe a recusa sem travar. Isso segue a documentação do Claude Code. Não reproduzi numa sessão real, porque o sandbox nega a API.

**Brechas**
- Fechadas: `gh api -X DELETE|delete|--method DELETE|--method=DELETE repos/o/r[/]` (também com `{owner}/{repo}` e com o `-X` depois do endpoint); GraphQL `deleteRepository`; `-f/-F/--field private=false|FALSE`, `visibility=public` e `-XPATCH`; `gh repo edit --visibility[=]public|PUBLIC`. No push: `+ref`, `+HEAD:ref`, `+main` com `-c`, `--force-with-lease[=...]`, `--force-if-includes` e `--mirror`. Apagar a `main`: `push origin --delete main`, `--delete origin main`, `-d main`, `:main` e `:refs/heads/main`. Apagar `.forge` por caminho: `rm -rf .forge`, `./.forge`, `.forge/`, `../.forge` (com `cd`), caminho absoluto literal, `mv .forge` e `rm -rf ~/.claude`. No rebase: `switch develop && rebase main`. Em `branch -D|-dr`: `develop` e `origin/main`.
- Ficam como limite aceito (o sandbox é a garantia real, `docs/hooks.md`): `D=.forge; rm -rf $D`, `rm -rf .fo*` e `find ... -exec rm`.

**Ajustes necessários**
1. `hooks/conformidade.py:320` (`claude`): `claude plugin update` é recusado. É assim que os projetos se atualizam: o `agents/jarvis.md:78`, a skill `contribuir-com-o-forge` e o `bin/forge-doutor:109` mandam rodar `claude plugin update forge@forge`. Atualizar o plugin não desinstala nem desliga a proteção. Sugestão: tirar `update` da lista e inverter as duas fixtures `trava-claude-plugin-update-*` para "libera". Severidade: **bloqueia**.
2. `hooks/conformidade.py:309` (`gh_trava`): `gh api -XDELETE repos/o/r` e `gh api -X=DELETE repos/o/r` apagam o repositório sem recusa. O `parecer.opcao` não lê a opção curta colada nem com `=`, embora o `metodo_mutante` leia (o `-XPATCH ... private=false` é recusado). Sugestão: ler o método do mesmo jeito que o `metodo_mutante` lê (`-XDELETE`, `-X=DELETE`, `--method=DELETE`), com fixtures das duas formas. Severidade: **bloqueia**.
3. `hooks/conformidade.py:347` (`checar_remocao`): `rm -rf $PWD/.forge`, `rm -rf "$CLAUDE_PROJECT_DIR"/.forge` e `rm -rf $PWD/.forge/` passam. Para arquivo, o mesmo prefixo é recusado (`rm "$PWD/.forge/versao"` cai em `em_qualquer_lugar`), e esses são os prefixos que um agente usa quando trabalha com caminho absoluto. Sugestão: aplicar à pasta o mesmo casamento em qualquer lugar do caminho que o `caminho_barrado` usa, comparando o fim do caminho com a pasta de um caminho protegido sem dono. Incluir fixtures com `$PWD` e `$CLAUDE_PROJECT_DIR`. Severidade: **bloqueia**.

**Recomendados** (podem virar cartão; não bloqueiam)
4. `.forge/perfil` fora de `caminhos`: `echo experiente > .forge/perfil` e `rm .forge/perfil` passam. Um agente que troca o perfil não ganha nada além do que o perfil padrão já permite, porque as recusas valem para todos os perfis. Mas some a confirmação da pessoa em `reset --hard`, `clean -f`, `checkout/restore .`, `gh repo archive` e `rebase` publicado, e somem também as mensagens simples. O risco é médio: é exatamente a proteção desenhada para o iniciante. Sugestão, sem esperar o `forge perfil`: recusar a escrita e a remoção de `.forge/perfil` quando o arquivo já existe com `iniciante`. A criação pela `novo-projeto` continua livre. Senão, abrir um cartão com prazo antes da F6.
5. `gh api -X PATCH repos/o/r --input body.json` (ou `--input -` com `{"private":false}`) torna o repositório público sem recusa. Sugestão: recusar `--input` em PATCH ou PUT no endpoint do repositório (`REPO_APAGAR`).
6. `ask` de `reset --hard` no iniciante também vale numa worktree temporária de review (o perfil é lido da cópia principal). Em segundo plano, a ação é negada. Nenhuma skill do Forge usa `reset --hard` hoje, então o impacto é baixo. Sugestão: dispensar a confirmação em worktree vinculada com HEAD solto.
7. Limites menores: `git update-ref -d refs/heads/develop` (só local, recuperável) e `git pull --rebase` sobre a branch de integração não são vistos.

Depois de corrigir os itens 1 a 3, com fixtures novas, peça um re-review. O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push.

## Re-review independente (tech-lead, HEAD 2b8970d)

Parecer: **reprovado**. Revisei o diff `c44e32f..2b8970d` e sondei o hook real com cerca de 80 comandos, nos perfis padrão e iniciante, num repositório de teste (papel `node-backend`, `feature/x` publicada), comparando com o `c44e32f` quando o resultado mudou.

**Validação local** (cota do Actions esgotada): `python3 -m unittest discover -s tests` passou (404 testes, OK). `scripts/validar-plugin.sh` passou. `catraca.py --base b5e5d3d` (modo `regras`) saiu com 1, só pedindo o rótulo `afrouxa-regra` para `hooks/_comum.py`, `hooks/conformidade.py` e `hooks/parecer.py`, como esperado. O modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`) saiu com 1, porque o último parecer é reprovado. O modo `pr-texto` (corpo do PR #110) passou. Versão 0.12.0 igual à da base, com 3 linhas novas em `[Não publicado]`: ok.

**Bloqueios do review anterior: os 3 fechados**
1. `claude plugin update forge@forge`, com `--scope project` e `plugins update`: liberados nos dois perfis. `uninstall` continua recusado; `validate` e `marketplace update` continuam livres.
2. `gh api -XDELETE`, `-X=DELETE`, `-Xdelete`, `--method=DELETE` e `-XDELETE` depois do endpoint, em `repos/o/r[/]` e `repos/{owner}/{repo}`: recusados. `-XGET` e `-X GET .../pulls` continuam livres. O `parecer.opcao` agora lê a opção curta colada.
3. `rm -rf $PWD/.forge[/]`, `"$CLAUDE_PROJECT_DIR"/.forge`, `${PWD}/.githooks`, `"${CLAUDE_PROJECT_DIR}/.claude"`, `$HOME/.claude`, `$PWD/.git` e `cd src && rm -rf $PWD/../.forge`: recusados. Com outra variável (`$X`, `$OLDPWD`, `` `pwd` ``, `"$(pwd)"`) antes da pasta protegida, também recusa. `rm -rf $PWD/node_modules|dist`, `rm -f $PWD/src/app.js`, `rm -rf $TMPDIR/<wt>` e `~/.forge-contrib/wt/x` continuam livres.

**Recomendados do review anterior**
4. `.forge/perfil` em `iniciante`: escrita e remoção recusadas por `>`, `rm`, `mv`, `sed -i`, `cp`, `truncate`, Write e Edit, também a partir de uma worktree. A criação no perfil padrão continua livre. Fechado.
5. `gh api -X PATCH repos/o/r --input -` e `--input` com `{"private": false}`: recusados. Um corpo sem visibilidade, e o `POST` em issues ou pulls com `--input`, continuam livres. Fechado.
6. Confirmação em worktree temporária: virou a brecha do item 1 abaixo.
7. `git update-ref -d refs/heads/main|develop`: recusado; `melhoria/x` continua livre. Fechado.

**`claude plugin install` recusado:** nenhum fluxo de agente depende disso. O `grep -rn "plugin install" agents skills bin scripts templates` só encontra comandos do usuário: o texto de ajuda do `bin/forge-doutor:94`, o comentário do `bin/forge-init:41` e o `scripts/preparar-estacao.sh:134`, que a pessoa roda no terminal (README, passo 3). Mesmo que um agente rodasse o script, o hook vê `preparar-estacao.sh`, não o `claude` de dentro. `iniciar-projeto` e `novo-projeto` não instalam o plugin, e não existe skill `forge-upgrade`. Ok.

**Ajustes necessários**
1. `hooks/conformidade.py:225` (`perguntar` e `worktree_temporaria`): com o cwd numa worktree vinculada em `$TMPDIR` ou `/tmp`, o agente escapa das confirmações do modo iniciante. Os atos que passam não são só da cópia temporária:
   - `gh repo archive o/r --yes` age no repositório do GitHub, e não pergunta mais. No `c44e32f` perguntava.
   - Com `git worktree add $TMPDIR/w feature/x` (a branch da pessoa), `git reset --hard HEAD~1` move a `feature/x` sem confirmação, e `git rebase develop` reescreve a branch já enviada, também sem confirmação. Os refs são comuns a todas as cópias.

   Com o cwd no projeto, `git -C $TMPDIR/w reset --hard` e `cd $TMPDIR/w && ...` ainda perguntam. Mas a sessão que já está na worktree passa. Sugestão: dispensar só os atos que mexem apenas nos arquivos da cópia (`reset --hard`, `clean -f`, `checkout -- .`, `restore .`), e só com HEAD solto (`git symbolic-ref -q HEAD` falha), como no recomendado 6. `gh repo archive` e o `rebase` publicado perguntam sempre. Fixtures: `archive` numa worktree temporária pergunta, e `reset --hard` numa worktree temporária com branch pergunta. Severidade: **bloqueia**. É uma regressão da proteção desenhada para o iniciante, introduzida nesta correção.

**Recomendados** (não bloqueiam; podem virar cartão)
2. Sem aspas, `rm -rf $(pwd)/.forge`, `rm -f $(pwd)/.forge/versao` e `rm -rf $(git rev-parse --show-toplevel)/.forge` passam. Isso já acontecia no `c44e32f`, e com aspas o hook recusa. O divisor de comandos parece tratar `$(...)` sem aspas como um subcomando à parte. Sugestão: aplicar o critério de "variável antes de pasta protegida" também a esse caso.
3. Falso positivo leve: `rm -rf $TMPDIR/x/.forge` é recusado, enquanto `/tmp/abc/.forge` passa. Limpar uma worktree inteira (`rm -rf $TMPDIR/x`) continua livre, então o impacto é baixo.

Depois de corrigir o item 1, com as fixtures, peça um re-review. O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push.

## Terceira review independente (tech-lead, HEAD 69d681e)

Parecer: **reprovado**. Revisei o diff `e427a49..69d681e` e sondei o hook real com cerca de 55 comandos, no perfil iniciante e no papel `node-backend`. O cenário tem um projeto com `feature/x` publicada, uma worktree `--detach` em `$TMPDIR` e um link simbólico em `$TMPDIR` apontando para o projeto. Comparei com o `e427a49` quando o resultado mudou.

**Validação local** (cota do Actions esgotada): `python3 -m unittest discover -s tests` passou (404 testes, OK). `scripts/validar-plugin.sh` passou. `catraca.py --base b5e5d3d` (modo `regras`) saiu com 1, só pedindo o rótulo `afrouxa-regra` para `hooks/_comum.py`, `hooks/conformidade.py` e `hooks/parecer.py`, como esperado. O modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`) saiu com 1, porque o último parecer é reprovado. O modo `pr-texto` (corpo do PR #110) passou. A versão 0.12.0 é igual à da base, com 3 linhas novas em `[Não publicado]`: ok.

**O que a correção fechou**
- Com o cwd na worktree temporária, `gh repo archive o/r --yes` volta a perguntar. Com branch na worktree, o `reset --hard` também pergunta, e há fixture para os dois casos.
- `reset --hard`, `clean -fdx`, `checkout -- .` e `restore .` na própria cópia solta ficam livres, como pretendido. Com o cwd no projeto, `git -C $TMPDIR/w reset --hard` e `cd $TMPDIR/w && ...` continuam perguntando.
- Expansão de `$TMPDIR`: com o link `$TMPDIR/lnk` apontando para o projeto, `rm -rf $TMPDIR/lnk/.forge` é recusado, também em `"$TMPDIR"/...` e `${TMPDIR}/.githooks`, porque o alvo é resolvido. `TMPDIR=... rm`, `export TMPDIR=...;`, `declare TMPDIR=...;` e `TMPDIR=... bash -c '...'` também são recusados. `rm -rf $TMPDIR/x/.forge` (o falso positivo do recomendado 3) agora passa.
- `$(pwd)` e `$( pwd )` sem aspas, antes de `.forge`, são recusados.

**Ajustes necessários**
1. `hooks/conformidade.py:230` (`worktree_temporaria`): a dispensa é decidida pela raiz da pasta corrente da chamada (`self.h.raiz`), não pela pasta em que o comando age. Com o cwd na worktree temporária solta, todos estes comandos passam sem confirmação e descartam as mudanças não salvas do **projeto da pessoa**:
   - `cd <projeto> && git reset --hard HEAD~1` e `cd <projeto> && git clean -fdx`;
   - `git -C <projeto> reset --hard` e `git -C <projeto> checkout -- .`;
   - `git --work-tree=<projeto> clean -fdx` e `GIT_DIR=<projeto>/.git GIT_WORK_TREE=<projeto> git reset --hard`.

   O "HEAD solto" também pode ser forjado na mesma linha, porque é lido antes de o comando rodar. `git switch feature/x && git reset --hard HEAD~1`, ou `git checkout feature/x; git reset --hard develop`, passa sem confirmação e move a branch publicada da pessoa.

   No `e427a49`, isso já passava, porque a dispensa valia para tudo. A correção estreitou a lista de atos, mas não a pasta. Sugestão: decidir a dispensa pela `pasta` que o `git_trava` recebe, ou seja, o `cd` e o `-C` já resolvidos. Não dispensar quando houver `--work-tree`, `--git-dir`, `GIT_DIR` ou `GIT_WORK_TREE`, nem quando a linha tiver antes um `switch` ou `checkout` de branch, `checkout -B` ou `branch -f`. O mais simples é dispensar só quando o ato for o único comando git da linha. Fixtures sugeridas, todas com o cwd na worktree solta e a resposta "pergunta": `cd <projeto> && git reset --hard`, `git -C <projeto> checkout -- .`, `git --work-tree=<projeto> clean -fdx` e `git switch feature/x && git reset --hard HEAD~1`. Severidade: **bloqueia**. É dano real para o iniciante: trabalho não salvo no projeto e uma branch publicada.
2. `hooks/conformidade.py:425` (`tmpdir_redefinido`): a redefinição de `TMPDIR` só é reconhecida na forma `TMPDIR=`. Com `read TMPDIR <<< <projeto>; rm -rf $TMPDIR/.forge` e `printf -v TMPDIR %s <projeto>; rm -rf $TMPDIR/.forge`, o hook expande para a `TMPDIR` do próprio processo, e a remoção passa. No `e427a49`, a variável antes de `.forge` era recusada, então isso é uma **regressão** desta correção. `for TMPDIR in <projeto>; do rm -rf $TMPDIR/.forge; done` já passava antes. Sugestão: tratar como redefinição qualquer ocorrência da palavra `TMPDIR` que não seja leitura (`$TMPDIR` ou `${TMPDIR}`). Fixture com `read` e `rm`. Severidade: **bloqueia**, porque reabre a remoção da instalação, que estava fechada.

**Recomendados** (não bloqueiam; podem virar cartão)
3. `rm -rf $(pwd -P)/.forge` e `rm -rf $(git rev-parse --show-toplevel)/.forge` ainda passam. A troca cobre só o `$(pwd)` literal. Sugestão: tratar `$(` sem aspas antes de uma pasta protegida como variável não resolvida, que é recusada.
4. `rm -rf <link>/`, com barra final num link simbólico para o projeto, esvazia o projeto. Conferi com o GNU rm: o conteúdo do alvo é apagado. O hook deixa passar, tanto com `$TMPDIR` quanto com o caminho literal, e isso já acontecia antes. Exige criar o link antes, então o impacto é baixo.
5. `git branch -f feature/x HEAD~1` e `git checkout -B feature/x HEAD` movem a branch publicada sem confirmação, em qualquer pasta, também no projeto. Já acontecia antes e está fora do escopo desta correção, mas cabe na mesma pergunta de "reescreve versões".

Depois de corrigir os itens 1 e 2, com as fixtures, peça um re-review. O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push.

## Quarta review independente (tech-lead, HEAD 78caa1b)

Parecer: **reprovado**, por um achado novo (item 1), que nenhuma das três reviews anteriores tinha visto. Os dois bloqueios da terceira review estão resolvidos. Revisei o diff `a6b2f2e..78caa1b` e sondei o hook real com cerca de 70 comandos, no perfil iniciante e no papel `node-backend`. O cenário tem um projeto do Forge (`.forge/versao`) com mudança não salva, a `feature/x` publicada no `origin` e uma worktree `--detach` em `$TMPDIR`. A sessão (`CLAUDE_PROJECT_DIR`) aponta para o projeto. Quando o resultado mudou, comparei com o `e427a49`, o `69d681e` e a `develop`.

**Validação local** (cota do Actions esgotada), no checkout do `78caa1b`:
- `python3 -m unittest discover -s tests`: 404 testes, OK.
- `scripts/validar-plugin.sh`: passou.
- `catraca.py` da base `b5e5d3d`, modo `regras`: saiu com 1, só pedindo o rótulo `afrouxa-regra` para `hooks/_comum.py`, `hooks/conformidade.py` e `hooks/parecer.py`, como esperado.
- Modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`): saiu com 1, porque o último parecer é reprovado.
- Modo `pr-texto` (corpo do PR #110): passou.
- Versão 0.12.0, igual à da base, com 3 linhas novas em `[Não publicado]`: ok.

**Bloqueios da terceira review: resolvidos**
- **Item 1.** Com o cwd na worktree solta, todos estes comandos agora **perguntam**: `cd <projeto> && git reset --hard HEAD~1`, `cd <projeto> && git clean -fdx`, `git -C <projeto> reset --hard`, `git -C <projeto> checkout -- .`, `git --work-tree=<projeto> clean -fdx`, `git --work-tree <projeto> clean -fdx`, `git --git-dir=<projeto>/.git reset --hard`, `GIT_DIR=... GIT_WORK_TREE=... git reset --hard`, `git switch feature/x && git reset --hard HEAD~1`, `git checkout feature/x; git reset --hard develop`, `git reset --hard; git clean -fdx` e `git -c core.worktree=<projeto> reset --hard`. Opção global entre `git` e o ato não casa com `UM_ATO_SIMPLES`, então pergunta. Tentei também argumentos que apontam para fora da cópia, como `git clean -fdx ..`, `git clean -fdx -- <projeto>` e `git restore --source=HEAD~1 -- <projeto>/src`. O hook deixa passar, mas o próprio git recusa um caminho fora do repositório, então não há dano. O cwd que persiste entre chamadas também não abre brecha: depois de um `cd <projeto>`, a chamada seguinte já roda com a raiz no projeto e pergunta.
- **Item 2.** `read TMPDIR <<< <projeto>; rm -rf $TMPDIR/.forge` e `printf -v TMPDIR %s <projeto>; rm -rf $TMPDIR/.forge` são **recusados**. O mesmo vale para `rm -rf $TMPDIR/.forge`, `"$TMPDIR"/lnk/.forge` e `${TMPDIR}/x/.forge`. `$(pwd -P)/.forge` também é recusado, o que fecha o recomendado 3.
- **Caso legítimo continua dispensado.** Na worktree solta, `git reset --hard`, `git reset --hard HEAD`, `git clean -fdx`, `git checkout -- .`, `git restore .` e `git restore --staged --worktree .` passam sem pergunta. No projeto, `git reset --hard`, `git clean -fdx` e `git -C <worktree> reset --hard` perguntam. `rm -rf <worktree>` e `git worktree remove --force <worktree>` seguem livres.

**Ajustes necessários**
1. `hooks/conformidade.py:380` (`checar_remocao`): com o cwd na worktree temporária, `rm -rf <projeto>/.forge`, `rm -rf ../proj/.forge` e `mv <projeto>/.forge /tmp/x` **passam**, e apagam a `.forge` do projeto da pessoa. Isso inclui o `perfil`, então o modo iniciante deixa de valer. A causa é que a função mede tudo a partir de `self.h.raiz`, que é a raiz da worktree em que o comando roda, e não a do projeto onde fica o alvo. Por isso, `<projeto>/.forge` cai "fora" e não é conferido.

   Os mesmos comandos são recusados com o cwd no projeto, num subdiretório dele ou numa pasta qualquer fora do git. Pela worktree, a escrita em `<projeto>/.forge/perfil`, o `rm -f <projeto>/.forge/versao` e o `rm -rf <projeto>/.githooks` também são recusados. Sobra só a remoção da pasta `.forge` inteira, a partir de outra cópia do projeto.

   Não é regressão desta correção: já passava no `e427a49` e no `69d681e`, e na `develop` nem existia a trava. Mas é exatamente o dano que a F4 promete evitar, e o comando é literal, sem nenhum truque de shell. Basta um agente de review que ficou com o cwd na cópia de review.

   Sugestão: conferir o alvo resolvido também contra a raiz do projeto que **o contém** (`raiz_do_projeto(alvo)`), mantendo de fora essa raiz e as pastas acima dela. A checagem de escrita (`caminho_barrado`) já não depende só de `self.h.raiz`: ela usa `em_qualquer_lugar`, e por isso recusa `<projeto>/.forge/versao`. Fixtures, todas com o cwd em `{tmp}/review-wt` e a resposta "bloqueia": `rm -rf {raiz}/.forge` e `mv {raiz}/.forge {tmp}/x`. Severidade: **bloqueia**.

**Recomendados** (não bloqueiam; podem virar cartão)
2. `for X in <projeto>; do rm -rf $X/.forge; done` passa, inclusive com `for TMPDIR in ...`. O corpo do `for` não é examinado como os comandos soltos. Já acontecia no `e427a49` e na `develop`.
3. `git checkout --ignore-other-worktrees -B feature/x HEAD~1` e `git branch -f feature/x HEAD~1` movem a branch publicada sem confirmação, em qualquer pasta. Isso continua o recomendado 5 da terceira review.
4. `rm -rf $TMPDIR/x/.forge` voltou a ser recusado. É o falso positivo do recomendado 3 da segunda review, mas trocado agora por segurança, e na direção certa: na dúvida, recusa. Se incomodar, basta escrever o caminho sem variável.

Depois de corrigir o item 1, com as fixtures, peça um re-review. O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push.

## Quinta review independente (tech-lead, HEAD 8d99869)

Parecer: **aprovado**. O bloqueio da quarta review está resolvido, e os recomendados 2 e 3 também. Revisei o diff `4cf90c0..8d99869` e sondei o hook real com cerca de 120 comandos, no papel `node-backend` e no `jarvis`. O cenário é o da quarta review: um projeto do Forge (`.forge/versao`, `.forge/perfil` = iniciante, `.githooks/`, `.claude/`) com mudança não salva, a `feature/x` publicada no `origin` e uma worktree `--detach` solta. Rodei com o cwd na worktree, no projeto e numa pasta fora do git; com e sem `CLAUDE_PROJECT_DIR`. Quando o resultado mudou, comparei com o `78caa1b`.

**Validação local** (cota do Actions esgotada), no checkout do `8d99869`:
- `python3 -m unittest discover -s tests`: 404 testes, OK.
- `scripts/validar-plugin.sh`: passou.
- `catraca.py` da base `b5e5d3d`, modo `regras`: saiu com 1, só pedindo o rótulo `afrouxa-regra` para `hooks/_comum.py`, `hooks/conformidade.py` e `hooks/parecer.py`, como esperado.
- Modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`): rodado sobre o commit deste parecer (resultado no comentário do PR).
- Modo `pr-texto` (corpo do PR #110): passou.
- Versão 0.12.0, igual à da base, com 3 linhas novas em `[Não publicado]`: ok.

**Bloqueio da quarta review: resolvido**
- Item 1. Com o cwd na worktree temporária, todos estes comandos agora são **recusados**: `rm -rf <projeto>/.forge`, `rm -rf ../proj/.forge`, `mv <projeto>/.forge <tmp>/x`, `rm -rf <projeto>/.githooks`, `mv <projeto>/.githooks <tmp>/x`, `rmdir <projeto>/.githooks`, `rm -rf <projeto>/.claude`, `mv <projeto>/.claude /tmp/x`, `rm -r ../proj/.claude`, `rm -rf <projeto>/.forge/`, `rm -rf <projeto>/./.forge` e `rm -rf <projeto>/.forge/run`. Também é recusado `rm -rf <link>/.forge`, com um link simbólico já existente que aponta para o projeto. O resultado é o mesmo sem `CLAUDE_PROJECT_DIR`, porque a raiz vem do repositório que contém o alvo (`raiz_git(alvo)`).

**Recomendados novos: conferidos**
- O corpo de `for`, `while`, `until` e `if/then/else` é examinado. `for X in <projeto>; do rm -rf $X/.forge; done` e `for TMPDIR in ...` são recusados, assim como `{ ...; }`, `( ... )`, `! rm ...`, `true && rm ...` e `bash -c 'rm ...'`.
- **Perguntam**, em qualquer pasta: `git checkout -B feature/x HEAD~1`, com ou sem `--ignore-other-worktrees`, e também `checkout -fB`, `switch -C`, `switch -fC`, `switch --force-create`, `branch -f`, `branch --force` e `branch -f --no-track`, sempre sobre branch publicada. São **recusados** `branch -f main`, `branch -f refs/heads/main`, `checkout -B develop` e `switch -C homolog`.

**Sem falso positivo no fluxo normal** (passam sem pergunta, no projeto e na worktree): `rm -rf <worktree>`, `rm -rf $TMPDIR/rv-algo`, `rm -f $TMPDIR/x.json`, `rm -rf node_modules dist`, `rm -rf <projeto>/src`, `mv src/app.js src/b.js`, `for f in a b; do rm -f $f.tmp; done`, `git worktree remove [--force] <worktree>`, `git switch -c` e `checkout -b melhoria/y`, `git branch -D melhoria/y`, `git branch -d feature/q`, `branch -f` e `checkout -B` de branch local não publicada, `git branch -m` e `-c`, `--list` e `-vv`.

**Recomendados** (não bloqueiam; podem virar cartão)
1. `find <projeto> -name .forge -exec rm -rf {} +` passa. É indireto, e já passava no `78caa1b`. Sugestão: tratar `find ... -exec|-execdir rm` e `-delete` como remoção dos caminhos de partida.
2. `git branch -M nova feature/x` e `git update-ref refs/heads/feature/x HEAD~1` movem a branch publicada sem confirmação. Também já passavam no `78caa1b`. Sugestão: estender `branch_movida` para `-M`/`-C` e para o `update-ref` sem `-d`.
3. `ln -s <projeto> L; rm -rf L/.forge`, na mesma chamada, passa: o link ainda não existe quando o hook resolve o caminho. Exige um truque deliberado; o sandbox é a garantia.
4. A trava passou a valer para `.forge`, `.githooks` e `.claude` de **qualquer** repositório, inclusive a própria worktree de review e repositórios de teste em `$TMPDIR` (`rm -rf <outro-repo>/.claude` é recusado). É falso positivo na direção segura, e apagar o repositório inteiro segue livre. Se incomodar, restrinja a repositórios com `.forge/versao`.
5. A raiz do projeto continua de fora por desenho (`rm -rf <projeto>` passa), como diz a docstring. É limite aceito, e o sandbox é a garantia.

O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push. Não mesclei.
