---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 24a8b873167daa35edfeb9445505ca818034535f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a3

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-2`). Diff lido: `234dbe0..24a8b87`, incluindo a volta 1 (`a0d1dfd`, `f793398`). Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.3. Não sou o autor.

## Item entregue e M14
- **Item:** E3, A3 HOOK-MERGE-FLAGS: flags do merge na integração, chaves de configuração do merge em `CONFIG_PROTEGIDA` e `git -c`.
- **M14 (decisão M14, `agents/tech-lead.md:19` na develop):** contam `hooks/conformidade.py` (32+2) e `tests/test_hooks.py` (5): 39 linhas, abaixo de 150. As fixtures de `tests/hooks/`, `tests/mutantes/`, `docs/hooks.md`, `changelog.d/` e os pareceres ficam fora. Uma classe de comportamento em `hooks/` (merge na integração que muda o resultado revisado, pela linha ou pela configuração), com corpus próprio (24 fixtures `merge-flag-*`). **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o hook `conformidade`, nos portões R-REVIEW e R-CONFORMIDADE.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1250 · `git config --worktree branch.develop.mergeoptions --squash` (e pull.twohead, pull.octopus, merge.<d>.driver) sai 0, e o Corrigir da :1266 manda usar --worktree; o merge sem flag vira squash ou no-commit. --worktree não isenta CONFIG_DO_MERGE.
- A2 (bloqueante) hooks/conformidade.py:1261 · `git config set <chave> <valor>` (git 2.46 ou mais novo; aqui é o 2.55) sai 0 para toda chave protegida: as do merge, alias.*, core.*, user.*. Com `set` ou `unset` como 1.ª palavra livre, a chave é a palavra livre seguinte.
- A3 (recomendado) hooks/conformidade.py:1250 · `GIT_EDITOR=<script> git config -e|--edit|edit` grava qualquer chave sem recusa; chaves do bash fora da linha crítica também saem 0 (`git config {branch.develop.mergeoptions,--squash}`, `git {-c,pull.twohead=ours} pull`). Cartão.

## Detalhe dos achados
Sondas: cada uma monta a fixture `merge-flag-s-ours-bloqueia` (tech-lead na develop) pelo `Fixture`/`rodar` da própria worktree e roda o hook real. A sintaxe do git foi conferida num repositório descartável em `$TMPDIR`. Nada rodou contra repositório real, rede ou produção.

**O que a branch fecha (saem 2):** `-s ours`, `-sours`, `--strategy ours`, `--strategy=ours`, `--strat=ours`, `-X theirs`, `-Xtheirs`, `-nX ours`, `-vs ours`, `--strategy-option=theirs`, `--squash` (também depois da branch e `--squash=yes`), `--squ`, `--no-commit` (também seguido de `--commit`), `--no-comm`, `-m msg -s ours`, `-mx -sours`, `git -C . merge -s ours`, `timeout 5 git merge -s ours` e `env git merge --squash`. Também fecha `pull --squash`, `pull --no-commit`, `pull -Xours`, `git -c pull.twohead=ours pull`, `git config` das quatro chaves (`--local`, `--file .git/config`, `--add`, com maiúsculas, com `--` e com o valor começado por traço) e as formas com chaves do bash na linha do merge (a rede da ADR 0011). O corpus de legítimos sai 0: `git merge --no-ff -m x feature/x`, `git config branch.feature/x.merge refs/heads/develop`, `git config --get …` e `git config --list`. As fixtures do lote passam: `test_fixtures_do_lote_furo_hook_a` deu `OK` no HEAD revisado.

**A1, bloqueante (requisito C-A3-3 do modelo, segurança com gatilho).** Evidência: `hooks/conformidade.py:1250` sai de `git_config` sem conferir nada quando há `--worktree` nos argumentos. As sondas `git config --worktree branch.develop.mergeoptions --squash`, `git config --worktree pull.twohead ours` e `git config --worktree merge.nos.driver true` saem 0. No git, `--worktree` sem `extensions.worktreeConfig` grava no `.git/config` comum (conferido: a chave foi para `.git/config`, sem `config.worktree`). Com a extensão, grava na configuração da própria worktree, que vale para o merge feito nela. Nos dois casos o merge da develop muda. Caminho, por erro e sem intenção: o tech-lead tenta `git merge --squash` e é recusado; tenta `git config branch.develop.mergeoptions --squash` e a recusa da `:1266` responde "use --worktree"; segue a dica e o `git merge melhoria/x` sem flag passa pelo A3 e pelo `parecer`, fazendo squash (perde o vínculo com a branch revisada) ou no-commit (o conteúdo muda antes do commit). Severidade alta: anula o controle que a branch entrega, e a mensagem do próprio hook leva ao furo. Correção mínima: em `git_config`, o `--worktree` só isenta quando a chave não casa `CONFIG_DO_MERGE`, ou seja, as quatro chaves `branch.<b>.mergeoptions`, `pull.twohead`, `pull.octopus` e `merge.<driver>.driver` recusam também com `--worktree`. A recusa dessas chaves não sugere `--worktree` no Corrigir. Fixtures `-bloqueia` com as três sondas e contraprova `git config --worktree core.sparseCheckout true` · 0 (o estado de hoje). Esforço P. Dono: tech-lead. É o A2 do review restrito às chaves do merge. O review o deixou como recomendado porque a isenção é anterior à branch; aqui ele bloqueia porque, para estas chaves, é requisito do item. Para `alias.*` e `core.*` com `--worktree`, a isenção anterior continua e vai com o N1, item novo ao dono.

**A2, bloqueante (requisito C-A3-3, segurança com gatilho).** Evidência: o laço de `hooks/conformidade.py:1253-1262` toma a 1.ª palavra sem traço como chave. Na sintaxe de subcomando do `git config` (git 2.46 ou mais novo; o desta máquina é o 2.55.0), essa palavra é `set` ou `unset`, que não casa `CONFIG_PROTEGIDA`. Sondas com saída 0: `git config set branch.develop.mergeoptions --squash`, `git config set pull.twohead ours`, `git config set merge.nos.driver true`, `git config set --local branch.develop.mergeoptions --squash`, `git config set alias.p push`, `git config set core.editor vi` e `git config unset core.bare`. Na base `234dbe0`, `git config set alias.p push` também sai 0: a falha é anterior, mas anula as chaves novas desta branch na forma que a documentação atual do git usa primeiro. Caminho: um agente usa a sintaxe nova por hábito (sem intenção) e grava a estratégia do merge da develop. Severidade alta, pelo mesmo efeito do A1. Correção mínima: em `git_config`, se a 1.ª palavra livre for um subcomando do `git config`, ela não é a chave. A lista inteira: escrita `set`, `unset`, `rename-section`, `remove-section`, `edit`; leitura `get`, `list`. Em `set` e `unset`, a chave é a palavra livre seguinte. As opções do subcomando não são chave: `--local`, `--global`, `--system`, `--worktree` (com a regra do A1), `--all`, `--append`, `--file`, `--blob`, `--type`, `--default`, `--value`, `--comment`. Destas, `--file`, `--blob`, `--type`, `--default`, `--value` e `--comment` levam valor quando o valor vem separado. `rename-section`, `remove-section` e `edit` contam como escrita, como as formas `--rename-section`, `--remove-section` e `-e` de `CONFIG_ESCRITA`. Fixtures `-bloqueia` com as sete sondas e contraprovas `git config get branch.develop.mergeoptions` · 0, `git config list` · 0 e `git config set branch.feature/x.merge refs/heads/develop` · 0. Esforço P. Dono: tech-lead.

**A3, recomendado.** Evidência:
- `GIT_EDITOR=./ed.sh git config -e`, `--edit` e `edit` saem 0. `-e` está em `CONFIG_ESCRITA`, mas sem chave na linha a recusa da `:1264` não dispara, e o editor grava qualquer chave.
- `git config {branch.develop.mergeoptions,--squash}` e `git {-c,pull.twohead=ours} pull . feature/x` saem 0, porque a linha não tem marcador `CRITICO` e a rede de chaves da ADR 0011 não roda.

Caminho: só deliberado, por injeção, que escreve um editor ou monta a linha com chaves. É a mesma classe de limite do N6 e do [B] de `docs/hooks.md`. Severidade média. Correção mínima (cartão): `git config` com `-e`, `--edit` ou `edit` recusa para todo papel, e a linha com `git config` ou `git -c` entra no marcador `CRITICO`, para a rede das chaves valer. Esforço P. Dono: tech-lead.

**Cartões do review (pergunta do brief):** o A2 do review (`--worktree`) **bloqueia**, restrito às chaves do merge (A1 acima). O A3 do review (valores com cara de opção, como `git config user.name --global`) **não bloqueia**: grava valores literais (`--global`, `--local`) sem efeito no merge nem na identidade útil. Fica como cartão de limpeza, sem caminho de ataque.

Dimensão nova para a matriz do modelo (§8): **Posição, subcomando do `git config`** (`set`/`unset`) e **escopo por worktree** das chaves do merge; **Mecanismo, expansão do shell fora da linha crítica** (chaves), que aparece também nas branches a2, a4 e a5.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais pelo harness de fixtures, um repositório descartável para a sintaxe do `git config` e execução das fixtures do lote. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow).
