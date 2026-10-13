---
tipo: review
contrato: 1
pedido: contrib-externa-so-propoe
branch: melhoria/contrib-externa-so-propoe
commit: c2dda1c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: sessão de outro projeto só propõe ao Forge (`R-CONTRIB`)

Escopo: `origin/develop..d6cc1a6` (1 commit): `docs/regras/R-CONTRIB.md`, `skills/contribuir-com-o-forge/SKILL.md`, `agents/jarvis.md`, `hooks/conformidade.py`, `tests/config.json`, 23 fixtures em `tests/hooks/conformidade/` e `CHANGELOG.md`. O autor é o próprio `tech-lead`: este parecer é de autoria e exige o rótulo `afrouxa-regra` do dono (toca `hooks/conformidade.py` e `docs/regras/`), que é o portão independente.

Aperta a regra, não afrouxa: nenhum invariante saiu; cinco entraram em `tests/config.json`. A política `hooks/conformidade.json` não mudou.

## Garantido por hook
Só em sessão cuja raiz não é o Forge (`e_clone_do_forge` falso), e só quando o alvo é o Forge (pasta em `~/.forge-contrib/` ou `--repo`/`GH_REPO`/endpoint com o slug do Forge):
- `git push` para branch fora de `melhoria/<projeto>-` (`<projeto>` = nome da raiz da sessão), incluindo `HEAD` estando em branch alheia;
- `gh pr merge`, `gh pr edit`, `gh pr close` e `gh label`;
- `gh api` mutante em `pulls/<n>`, `issues/<n>`, `issues/<n>/labels` e `labels`, e mutações GraphQL equivalentes. Criar o PR (`POST pulls`), ler e comentar continuam livres. PR e API de outro repositório (o do projeto) não são afetados.

## Só regra (limites do hook)
- Commitar em branch alheia e resolver conflito ou revalidar parecer de PR alheio: o hook não vê a intenção; o efeito (o push) é barrado, então o dano não chega ao Forge.
- Sessão iniciada com `cwd` dentro do clone de contribuição: o clone do Forge não tem `.forge/versao`, e o `conformidade` só age em projeto com ele (ADR 0009). Não há como distinguir com segurança "outro projeto" de "o Forge" nesse caso; o limite já existia e fica documentado aqui.
- `git push` com `--tags` ou `gh` por script (`python -c`, arquivo `.sh`): o Bash é lido como texto (limite já documentado no hook).
- Vale a identificação por raiz do projeto; uma sessão que se passe pelo Forge criando `.claude-plugin/plugin.json` falso na raiz é um dolo que o hook não cobre (o sandbox e o ruleset do GitHub são a garantia).

## Checklist
1. Pedido atendido, sem extras: sim.
2. Regras e ADRs: `R-CONTRIB` é texto único; skill e `jarvis` citam o ID sem repetir o texto (ADR 0002); `R-CUSTO` e `R-NEUTRO` intactas.
3. Legível: `alvo_do_forge` e `gh_contrib` pequenos, constantes nomeadas.
4. Erros: política e falha fechada inalteradas; o marcador `CRITICO` ganhou `edit|close|label` para falhar fechado em erro interno.
5. Testes: fixtures escritas antes. Vermelho: 14 falhas em `test_hooks` sem a mudança no hook (todas as `bloqueia` de `contrib-*`). Verde: `python3 -m unittest discover -s tests`, 271 testes, e `scripts/validar-plugin.sh` passa.
6. Commits: um commit coerente, `git add` explícito.

Parecer: **aprovado**, condicionado ao rótulo `afrouxa-regra` do dono.

## Review independente (head `83bc98c`)

Testes: `python3 -m unittest discover -s tests` no checkout do PR, 271 testes, OK. Além disso, uma sonda com 70 entradas reais de hook (`HOME` temporário, projeto com `.forge/versao`, clone em `~/.forge-contrib/Projeto`, worktree em `~/.forge-contrib/wt/x`) rodou `hooks/conformidade.py` direto; os resultados abaixo são dela.

### Como o hook acha a raiz
`principal` usa `hook.projeto(hook.cwd())`, e `cwd` é o campo `cwd` da entrada do hook: a pasta corrente **da sessão no momento da chamada**, não `CLAUDE_PROJECT_DIR` (que nenhum hook lê). Dentro de uma linha, o `cd` e o `git -C` são acompanhados (`segmento`, `git`); entre chamadas, não.

### Bloqueia o merge
1. **`cwd` da chamada no clone de contribuição (o caso que motivou o PR).** A sessão principal do Claude Code mantém a pasta entre chamadas do Bash: o Jarvis do projeto roda `cd ~/.forge-contrib/<projeto>` (a skill manda trabalhar ali) e, nas chamadas seguintes, `git push origin melhoria/outra`, `gh pr merge 70` e `gh pr edit 70 --remove-label afrouxa-regra`. O `cwd` da entrada é o clone, que não tem `.forge/versao`; `raiz_do_projeto` devolve None e o hook sai sem olhar nada. Na sonda, os quatro comandos passam, com ou sem `CLAUDE_PROJECT_DIR` no ambiente. Vale igual para um subagente cujo `cwd` está no clone. Só são barrados `cd <clone> && git push ...` e `git -C <clone> push ...` numa linha que começa no projeto.
   Correção: em `principal`, quando `hook.projeto(hook.cwd())` é None e o `cwd` está em `~/.forge-contrib/`, tomar a raiz de `os.environ["CLAUDE_PROJECT_DIR"]` (o Claude Code define essa variável para os hooks; é a raiz da sessão, também para subagentes) e seguir com `Guarda` usando essa raiz e `pasta = cwd`. Se a raiz for o Forge (`e_clone_do_forge`), a sessão do Forge nas worktrees `wt/*` continua livre. Sem `CLAUDE_PROJECT_DIR`, falhar fechado no `R-CONTRIB`: o prefixo próprio é `melhoria/<nome do clone>-`, porque o clone é por projeto (`~/.forge-contrib/<projeto>`), e push para fora dele é barrado. As fixtures novas são `cwd` = clone com push alheio (bloqueia), com push próprio (libera), com `gh pr merge` e `gh pr edit` (bloqueiam), e `cwd` = `wt/x` com `CLAUDE_PROJECT_DIR` no Forge (libera). O harness precisa aceitar `cwd` e `env` com `{tmp}` (já aceita).
2. **`gh pr merge|edit|close <URL do PR do Forge>` passam** quando chamados da pasta do projeto: `gh_contrib` só olha `-R`/`--repo`/`GH_REPO`. `gh pr edit https://github.com/<slug>/pull/70 --remove-label afrouxa-regra` é exatamente o dano relatado. Correção: considerar alvo também quando algum posicional `aponta_para_o_forge`.
3. **`gh issue edit|close -R <forge>` passam.** No GitHub o PR é uma issue: `gh issue edit 70 -R <slug> --remove-label afrouxa-regra` derruba o rótulo do mesmo jeito. Correção: tratar `issue` com `edit|close|reopen` como `pr` e incluir `issue` em `CRITICO` (hoje `edit|close|label` já entram).

### Recomendado (não bloqueia; texto do Bash, já fora da garantia declarada)
- `cd $HOME/.forge-contrib/...` e `git -C $HOME/...`: o `$HOME` não é expandido e o caminho cai no projeto. Aplicar `os.path.expandvars` nos argumentos do `cd`/`-C`.
- `pushd <clone>; git push ...`, `GIT_DIR=<clone>/.git git push ...` e `git --git-dir[=]<clone>/.git push ...` passam. Tratar `pushd` como `cd`; o `GIT_DIR` e o `--git-dir`, como `-C`.
- Push por URL direta do Forge a partir do projeto (`git push https://github.com/<slug>.git HEAD:melhoria/outra`, também `git@...:refs/heads/...`) passa. Aplicar `aponta_para_o_forge` ao remoto do push.
- `export GH_REPO=<slug>; gh pr merge 70` passa, porque o `export` não é acompanhado, só a atribuição na mesma palavra. Aplicar o mesmo para `gh api repos/{owner}/{repo}/...` com `GH_REPO`.
- GraphQL: `addLabelsToLabelable`, `removeLabelsFromLabelable`, `closePullRequest` e `updatePullRequest` usam IDs globais, sem slug. Fora do clone o alvo nunca é reconhecido e as quatro passam (o `mergePullRequest` é barrado pelo `GRAPHQL_PERIGOSO` antigo). `--input arquivo` e `-F query=@arq` também passam. Sugestão: na sessão de outro projeto, barrar as mutações de `CONTRIB_GRAPHQL` sem exigir alvo e barrar `graphql` mutante com `--input` ou `@arquivo`.
- `gh pr ready|reopen|review --approve -R <forge>` passam. Incluir em `CONTRIB_PR_ALHEIO`.

### Desvios cobertos (conferidos na sonda)
No clone, numa linha que começa no projeto, são barrados `HEAD:refs/heads/<alheia>`, `--all`, `--mirror`, push sem argumentos e `git push origin` com `HEAD` alheia, `própria:alheia`, `--delete` e `:alheia`. O refspec com `+` cai no `R-VERIFY`. `gh pr checkout` seguido de `git push` é barrado pelo push. Também são barrados `gh pr merge -R`/`--repo=`/`GH_REPO=` na mesma palavra, `gh label -R`, `gh api` `PUT .../merge`, `PATCH pulls`, `DELETE labels`, `update-branch` e `reviews` (POST).

### Falso positivo
A sessão do Forge (raiz `~/Forge` e worktrees `wt/*`) pode fazer push e `gh pr merge|edit`. A sessão do projeto continua podendo abrir o PR (`gh pr create -R`, `cd clone && gh pr create`, `POST pulls`), comentar (`gh pr comment`, `POST issues/<n>/comments`), fazer push da própria branch (`-u` incluído) e mesclar no próprio repositório. Um efeito colateral aceitável: `gh pr edit <n> -R <forge> --body` no **próprio** PR é barrado. Documentar em `R-CONTRIB` que o ajuste do corpo vai por comentário, ou liberar `edit` sem `--add-label`/`--remove-label` quando a head do PR for `melhoria/<projeto>-`, o que exige rede e por isso não recomendo.

Parecer: **reprovado**. Os itens 1 a 3 voltam ao autor, cada um com fixture que falha antes da correção. Os recomendados podem ir junto ou em cartão próprio, registrados na seção "Só regra".

## Re-review independente (head `c2dda1c`)

Testes: `python3 -m unittest discover -s tests` no checkout do PR (worktree destacada em `c2dda1c`), 271 testes, OK. Além disso, uma sonda com 75 entradas reais de hook (`HOME` temporário; projeto com `.forge/versao`; clone do Forge em `~/.forge-contrib/proj` com `origin` no slug; worktree em `~/.forge-contrib/wt/x`; um "Forge" com `.forge` vazio, como o `~/Forge` local) rodou `hooks/conformidade.py` direto, com e sem `CLAUDE_PROJECT_DIR` no ambiente do processo do hook.

### Os três bloqueantes anteriores: resolvidos
1. **`cwd` no clone:** com `CLAUDE_PROJECT_DIR` no projeto e sem ela (falha fechado, prefixo `melhoria/proj-`), são barrados `git push origin melhoria/outra`, `HEAD:develop`, `gh pr merge 70` e `gh pr edit 70 --remove-label`, também numa subpasta do clone; continuam livres o push da própria branch (`-u` incluído), `gh pr create` e `gh pr comment`.
2. **URL do PR:** `gh pr merge|edit|close|ready|reopen|review --approve <URL do Forge>` são barrados; `gh pr edit` com URL do projeto e `--body` que cita a URL do Forge passam.
3. **`gh issue`:** `edit|close|reopen` com `-R`, `--repo=`, URL e número lido no clone são barrados; `gh issue comment -R` e `gh issue close` do projeto passam.

### `CLAUDE_PROJECT_DIR`
O hook lê `os.environ` do **próprio processo**, que o Claude Code cria com a variável definida para os hooks (raiz da sessão, também para subagentes). O shell do Bash é outro processo, filho da mesma sessão: `export CLAUDE_PROJECT_DIR=<forge>; git push ...` e `CLAUDE_PROJECT_DIR=<forge> git push ...` não mudam o que o hook vê (sonda: os dois barrados). Não dá para forjar pela linha de comando. O limite que sobra já está documentado: sessão aberta com a raiz dentro do clone.

### Bloqueia o merge
1. **As worktrees `~/.forge-contrib/wt/*` liberam a sessão de projeto.** `sessao_no_clone_de_contribuicao` devolve False para `wt` antes de olhar `CLAUDE_PROJECT_DIR`, então o hook não age. Com `cwd` = `wt/x` e `CLAUDE_PROJECT_DIR` no projeto, passam `git push origin melhoria/outra`, `gh pr merge 70` e `gh pr edit 70 --remove-label afrouxa-regra` (sonda). Não é teórico: `skills/contribuir-com-o-forge/SKILL.md:19` manda a **sessão de projeto com sandbox** trabalhar justamente em `~/.forge-contrib/wt/<nome>`, e `R-CONTRIB` agora diz que essas worktrees "são da sessão do Forge". A regra e a skill se contradizem, e o caminho documentado para o projeto fica sem guarda.
   Correção: consultar `CLAUDE_PROJECT_DIR` primeiro. Se ela é um projeto do Forge (`hook.projeto`), o hook age com essa raiz e com `pasta = cwd`, esteja o `cwd` em `wt/*` ou não. Se ela é o Forge (sem `.forge/versao`), libera. A isenção de `wt` sem a variável pode ficar, porque é o caso que não se distingue. Ajustar o texto de `R-CONTRIB` ("as worktrees `wt/*` são da sessão do Forge"). Fixtures: `cwd` = `wt/x` com `CLAUDE_PROJECT_DIR` no projeto e push alheio, `gh pr merge` e `gh pr edit` (bloqueiam); a de `wt/x` com o Forge continua liberando.
2. **A raiz ainda sai do `cwd` fora do clone.** Com `cwd` em qualquer pasta que não seja projeto nem `~/.forge-contrib/<nome>/...` (o próprio `~/.forge-contrib`, `~`, outra pasta), o hook sai sem olhar nada, mesmo com `CLAUDE_PROJECT_DIR` no projeto. Passam `gh pr merge 70 -R <forge>`, `gh pr edit <URL> --remove-label afrouxa-regra`, `git -C proj push origin melhoria/outra` (de `~/.forge-contrib`), `cd .forge-contrib/proj && git push origin melhoria/outra` (de `~`) e até `git -C <projeto> push origin main` (`R-MAIN`). É o bloqueante 1 anterior por outra porta: um `cd ~/.forge-contrib` (o pai do clone, onde a skill clona) basta. O limite já existia antes do PR, mas o PR passa a declarar a raiz por `CLAUDE_PROJECT_DIR` e só a usa dentro do clone.
   Correção: a mesma do item 1. Em `principal`, quando `hook.projeto(cwd)` é None, usar `CLAUDE_PROJECT_DIR` (absoluta e projeto do Forge) para **qualquer** `cwd`, e para Bash, Write e Edit. A falha fechada sem a variável continua só para `~/.forge-contrib/<nome>`. Isso também resolve o recomendado sobre Write e Edit abaixo. Fixtures: `cwd` = `~/.forge-contrib` e `cwd` = `HOME`, com `CLAUDE_PROJECT_DIR` no projeto, em `gh pr merge -R` e push alheio (bloqueiam).
3. **`env GH_REPO=<forge> gh pr merge 70` passa** (e `env -i PATH=... GH_REPO=... gh ...`). `sem_lancadores` descarta as atribuições que vêm depois do `env`, e `da_atribuicao` só vê as que vêm antes. É a forma canônica de passar variável a um comando, não ofuscação, e o PR declara cobrir `GH_REPO`. Correção: juntar às `atribuicoes` as que `sem_lancadores` tira depois de um lançador (ou tratar `env` como `export` para a palavra seguinte). Fixture: `env GH_REPO=<forge> gh pr merge 70` (bloqueia).

### Recomendado (não bloqueia)
- **Write e Edit não ganharam o caminho novo** (`principal` passa `False` para quem não é Bash). Com `cwd` no clone ou em `~`, `Write <projeto>/.claude/settings.json` e `Write <projeto>/docs/reviews/x.md` por `forge:dev` passam; com `cwd` no projeto, são barrados. No clone, o Bash `echo > <projeto>/.claude/settings.json` já é barrado. O limite já existia, e o item 2 de bloqueio resolve junto. Não sendo feito, registrar em "Só regra".
- `declare -x GH_REPO=<forge>; gh pr merge 70` passa. Tratar `declare -x`/`typeset -x` como `export`, ou registrar como limite.
- `docs/regras/R-CONTRIB.md`: espaço duplo em "sandbox;  o resto".

### GraphQL: o falso positivo não bloqueia
As mutações de `CONTRIB_GRAPHQL` passam a ser barradas em toda sessão de projeto, inclusive no repositório do próprio projeto. `grep -rn "gh api graphql" agents skills stacks templates` não encontra nada; em todo o repositório, `graphql` só aparece no hook, nas fixtures e neste parecer. O CI do Forge e o dos projetos (`templates/`) não usam GraphQL. Os fluxos dos agentes rotulam, editam e fecham PR do próprio projeto por `gh pr edit|close` e `gh label`, que continuam livres no projeto (sonda: `gh pr edit` com URL do projeto passa). Consultas GraphQL e mutações fora da lista (`addComment`) passam. O custo é que um agente que improvise `removeLabelsFromLabelable` no próprio repositório recebe o bloqueio com a orientação, e o caminho `gh pr edit` está aberto. O texto de `R-CONTRIB` já diz isso. Restringir ao Forge exigiria resolver o ID global pela rede, que o hook não faz (ADR 0003). Aceito como está.

### Sem regressão na sessão do Forge
Raiz do Forge (`.forge` vazio, como o `~/Forge`): push, `gh pr merge`, `gh pr edit --add-label` e GraphQL de rótulo liberam (o hook não age fora de projeto). `wt/x` com `CLAUDE_PROJECT_DIR` no Forge: push alheio, merge, `edit --remove-label`, `gh issue close -R` e GraphQL liberam. Clone `~/.forge-contrib/proj` com `CLAUDE_PROJECT_DIR` no Forge e `~/.forge-contrib/fontes` também. A correção proposta mantém esses casos: com `CLAUDE_PROJECT_DIR` no Forge, o hook continua liberando.

Parecer: **reprovado**. Os bloqueantes 1 a 3 voltam ao autor, cada um com a fixture que falha antes. Os dois primeiros têm uma correção só, em `principal`: `CLAUDE_PROJECT_DIR` antes da isenção de `wt` e para qualquer `cwd`. Depois, o rótulo `afrouxa-regra` do dono segue obrigatório.
