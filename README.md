# Forge

Fábrica de software com agentes para o Claude Code. Um plugin com o **Jarvis** (orquestrador) e o time completo — tech lead, arquiteto, UX, desenvolvedores por stack (pacote inicial: Node + React), QA e agile coach —, o processo de desenvolvimento e os modelos para iniciar projetos.

## O que vem na fábrica
- **Fluxo:** discovery com Design Thinking (UX + arquiteto) → validação do protótipo pelo usuário → desenho técnico → desenvolvimento em paralelo → code review → QA obrigatório → revisão de UX → PR validado pelo usuário → retrospectiva.
- **Regras:** a `main` é do usuário; QA e code review em toda entrega; teto de recursos da máquina; quadro Kanban visível; reuniões de alinhamento; melhoria contínua com autonomia, separando fábrica e projeto.
- **Modelo de projeto:** `CLAUDE.md`, `KANBAN.md`, pastas de pedidos, Kanban, retrospectivas e alinhamentos, práticas, configuração do Claude Code e hook que protege a `main`.

## Usar num projeto
Pré-requisito: acesso ao repositório (privado) pelo git da máquina — chave SSH no GitHub ou `gh auth login` + `gh auth setup-git`.

```bash
cd meu-projeto
claude plugin marketplace add rodrigo-isensee/Forge --scope project
claude plugin install forge@forge --scope project
claude
```
Na sessão, peça: *"inicie este projeto no Forge"* (skill `forge:iniciar-projeto`). Ela cria a estrutura sem sobrescrever o que existe e configura o Jarvis como agente principal (`"agent": "forge:jarvis"` em `.claude/settings.json`).

Atalho opcional para abrir o Jarvis retomando a conversa, com chat remoto e Telegram (se instalado):
```bash
bash ~/.claude/plugins/marketplaces/forge/scripts/instalar-atalho.sh   # ou a partir de um clone do Forge
jarvis            # no diretório do projeto (roda no tmux; --sem-tmux para o modo antigo)
```
A sessão fica num tmux `jarvis-<projeto>`: sobrevive ao fechamento do terminal (volte com o mesmo comando) e aparece em claude.ai/code como "Jarvis - <projeto>".

**`jarvis-forge` e a cópia vigente (ADR 0009, seção 4).** O diretório de trabalho é o `~/Forge` (onde se edita), mas o plugin carregado vem de uma cópia vigente: um clone da `origin/develop` em `${XDG_DATA_HOME:-~/.local/share}/forge/vigente`, criado na primeira vez e **nunca atualizado sozinho**. Assim, editar `hooks/` ou `agents/` numa branch não muda a guarda nem as instruções da sessão em uso. Depois que um PR for mesclado na `develop`, rode `jarvis-forge --atualizar-vigente` (faz `git fetch` e `git reset --hard origin/develop` só na cópia vigente; recusa se ela tiver mudanças ou commits locais, e nunca apaga um diretório que não seja clone do Forge) e reinicie a sessão do tmux (o script avisa se ela estiver aberta). A sessão do modo `--dev` tem nome próprio (`jarvis-Forge-dev`). `jarvis-forge --dev` usa a cópia de trabalho (`--plugin-dir .`), com aviso, para teste manual do dono.

## Preparar uma estação nova (WSL)
1. No PowerShell: `wsl --install -d Ubuntu-24.04 --location <unidade>:\WSL\<nome>`
2. No Ubuntu novo: `sudo apt-get install -y gh && gh auth login && gh repo clone rodrigo-isensee/Forge ~/Forge`
3. `~/Forge/scripts/preparar-estacao.sh` (use `--simular` para só ver o que faria; pode repetir à vontade).

O script instala pacotes, Node 24, pnpm, Claude Code, o plugin e os atalhos `jarvis`/`jarvis-forge`. Credenciais **não** são copiadas entre máquinas: em cada estação faça `gh auth login` e, no `claude`, `/login`.

## Sandbox do Bash
O `.claude/settings.json` do Forge liga o sandbox do Bash (ADR 0009, seção 5) com `failIfUnavailable` e sem `allowUnsandboxedCommands`: sem `bubblewrap` e `socat` (instalados por `scripts/preparar-estacao.sh`) a sessão não abre.
- **Escrita:** só o diretório de trabalho, o temporário da sessão, `~/.forge-contrib` (clones de contribuição e as worktrees do Forge, em `~/.forge-contrib/wt/<nome>`) e `/tmp/claude-1000`. Ficam bloqueados para o Bash, mesmo dentro do diretório de trabalho: `.forge/`, `.githooks/`, `.claude-plugin/`, `.github/`, `tests/config.json`, `tests/catraca.py`, `tests/neutralidade.py` e `hooks/conformidade.json`; o Claude Code protege sempre `.claude/settings*.json`, `.claude/{skills,agents,commands,hooks}`, `.git/hooks` e `.git/config`. O sandbox vale só para o Bash: esses arquivos mudam por Write/Edit, numa branch, com PR revisado (é o desejado).
- **Rede:** só GitHub, npm e PyPI; as APIs de modelo (Anthropic, OpenAI, Google) são negadas (`R-CUSTO`). Só `tmux capture-pane`, `tmux ls` e `tmux has-session` rodam fora do sandbox.
- **Git:** `.git/config` é protegido: use `git push origin <branch>`, não `-u`, e não rode `git config` nem `git branch --set-upstream`. Worktree: `git worktree add --no-track -b <branch> <dir> origin/develop` (com rastreamento o git grava no `.git/config`).
- **Pasta de contribuição:** o sandbox libera escrita dentro de `~/.forge-contrib/`, mas a pasta pessoal é somente leitura; o usuário cria a pasta uma vez, fora do Claude: `mkdir -p ~/.forge-contrib/wt`.
- **Validar o plugin:** o ponto de montagem `.mcp.json` faz `claude plugin validate .` falhar na raiz; use `scripts/validar-plugin.sh`, que valida uma cópia limpa (arquivos versionados, com as mudanças do disco) em `$TMPDIR`. O CI continua com o comando direto.
- **Pontos de montagem:** o bubblewrap cria, na raiz do diretório de trabalho, arquivos e pastas vazios e somente leitura (`.bashrc`, `.gitconfig`, `.forge`, `.claude/hooks` etc.) para cobrir os caminhos protegidos; o `.gitignore` os ignora.
- **CLI do Claude nos testes:** a chamada tenta `api.anthropic.com` e é bloqueada; é o esperado (`R-CUSTO`).
- **Conferir:** `/sandbox` na sessão.
- **Emergência (só o dono):** edite `.claude/settings.json` no terminal, fora do Claude, e reinicie a sessão.

## Branches
Os projetos usam **só a `main`**. Melhorias entram por `develop` (testes rápidos), passam pela `homolog` (mesma bateria sobre o conjunto da release; nada que custe uso de API) e chegam à `main` por PR mesclado pelo dono do Forge.

**Hooks `pre-push` (assimetria proposital):** o do Forge bloqueia `develop`, `homolog` e `main`, pois a fábrica tem as três como degraus protegidos; o do modelo de projeto bloqueia só a `main`, porque o projeto usa apenas ela como branch protegida (o resto é livre).

## Hooks
Em projeto com `.forge/versao`, o plugin garante por código, sem gastar contexto, o teto de agentes, o parecer antes de PR e merge, uma tarefa pesada por vez e o quadro válido (ADR 0003). Ajustes e como desligar um hook: [`docs/hooks.md`](docs/hooks.md).

## Atualizar um projeto
O Forge nunca muda um projeto sozinho (ADR 0005). Cada versão está no `CHANGELOG.md`; as marcadas "**requer migração**" mudam arquivos do projeto. No projeto, com a árvore limpa:
1. `claude plugin update forge@forge`
2. `forge-upgrade` (`--simular` mostra o que faria): cria a branch `forge/upgrade-<versão>`, aplica as migrações pendentes (um commit cada) e sugere o `gh pr create`.
3. Revise o PR e mescle; o `forge-upgrade` nunca faz push nem merge.

## Desenvolver o Forge
Ver [`.claude/CLAUDE.md`](.claude/CLAUDE.md): regras, testes, avaliações e versionamento.
