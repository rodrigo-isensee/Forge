# Forge

Fábrica de software com agentes para o Claude Code. Um plugin com o **Jarvis** (orquestrador) e o time completo — tech lead, arquiteto, UX, desenvolvedores por stack (pacote inicial: Node + React), QA e agile coach —, o processo de desenvolvimento e os modelos para iniciar projetos.

Visão geral com diagramas do fluxo, das integrações e das guardas: [`docs/visao-geral.md`](docs/visao-geral.md).

## O que vem na fábrica
- **Fluxo:** discovery com Design Thinking (UX + arquiteto) → validação do protótipo pelo usuário → desenho técnico → desenvolvimento em paralelo → code review → QA obrigatório → revisão de UX → PR validado pelo usuário → retrospectiva.
- **Regras:** a `main` é do usuário; QA e code review em toda entrega; teto de recursos da máquina; quadro Kanban visível; reuniões de alinhamento; melhoria contínua com autonomia, separando fábrica e projeto.
- **Modelo de projeto:** `CLAUDE.md`, `KANBAN.md`, pastas de pedidos, Kanban, retrospectivas e alinhamentos, práticas, configuração do Claude Code e hook que protege a `main`.

## Começar um projeto novo
Pré-requisitos: Claude Code, `git` e a conta do GitHub entrada no terminal (`gh auth login`; o login é feito no navegador, o Forge nunca vê sua senha nem o token).
```bash
claude plugin marketplace add rodrigo-isensee/Forge
claude plugin install forge@forge
forge novo-projeto
```
O `forge novo-projeto` pergunta o nome e a pasta (padrão `~/<nome>`), cria o repositório **privado** na sua conta, clona, faz o commit inicial na `main` e cria `develop` e `homolog`. Em seguida abre o Jarvis, que conduz o resto numa conversa curta (perfil de experiência, objetivo, stack, regras) e abre o PR "adota o Forge". Se parar no meio, rode o comando de novo e informe o mesmo nome: ele retoma de onde parou. Perfil `iniciante` em `.forge/perfil` (arquivo da pessoa, fora do git): o Jarvis fala sem jargão e leva só as decisões de produto, escopo, custo e acesso. Desenho: `docs/propostas/primeiro-uso/`.

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

**`jarvis-forge` e a cópia vigente (ADR 0009, seção 4).** O diretório de trabalho é o `~/Forge` (onde se edita), mas o plugin carregado vem de uma cópia vigente: um clone da `origin/develop` em `${XDG_DATA_HOME:-~/.local/share}/forge/vigente`, criado na primeira vez e **atualizado sozinho ao abrir, só por fast-forward** para a `origin/develop` (se tiver mudança ou commit local, se não estiver na `develop`, se não houver rede ou se a sessão do tmux já estiver aberta, o script avisa numa linha e segue com a cópia atual; nunca usa a cópia de trabalho, salvo `--dev`). Uma vez por dia (cache em `${XDG_STATE_HOME:-~/.local/state}/forge/fontes-<data>`) ele roda `forge-check fontes` e mostra uma linha se a fonte de harness tiver versão nova (sem o registro local, fica em silêncio). Assim, editar `hooks/` ou `agents/` numa branch não muda a guarda nem as instruções da sessão em uso. Para forçar a atualização sem abrir a sessão, rode `jarvis-forge --atualizar-vigente` (faz `git fetch` e `git reset --hard origin/develop` só na cópia vigente; recusa se ela tiver mudanças ou commits locais, e nunca apaga um diretório que não seja clone do Forge) e reinicie a sessão do tmux (o script avisa se ela estiver aberta). A sessão do modo `--dev` tem nome próprio (`jarvis-Forge-dev`). `jarvis-forge --dev` usa a cópia de trabalho (`--plugin-dir .`), com aviso, para teste manual do dono.

## Preparar uma estação nova (WSL)
1. No PowerShell: `wsl --install -d Ubuntu-24.04 --location <unidade>:\WSL\<nome>`
2. No Ubuntu novo: `sudo apt-get install -y gh && gh auth login && gh repo clone rodrigo-isensee/Forge ~/Forge`
3. `~/Forge/scripts/preparar-estacao.sh` (use `--simular` para só ver o que faria; pode repetir à vontade).

O script instala pacotes, Node 24, pnpm, Claude Code, o plugin e os atalhos `jarvis`/`jarvis-forge`. Credenciais **não** são copiadas entre máquinas: em cada estação faça `gh auth login` e, no `claude`, `/login`.

## Sandbox do Bash
O `.claude/settings.json` do Forge liga o sandbox do Bash (ADR 0009, seção 5) com `failIfUnavailable` e sem `allowUnsandboxedCommands`: sem `bubblewrap` e `socat` (instalados por `scripts/preparar-estacao.sh`) a sessão não abre.
- **Escrita:** só o diretório de trabalho, o temporário da sessão, `~/.forge-contrib` (clones de contribuição e as worktrees do Forge, em `~/.forge-contrib/wt/<nome>`); o temporário da sessão (`$TMPDIR`, `/tmp/claude-<uid>`) já é liberado pelo Claude Code, sem entrada própria. Fica bloqueado para o Bash, mesmo dentro do diretório de trabalho, só o estado em vigor **não versionado**: `.forge/`. Arquivo versionado fora do `denyWrite` de propósito (decisão N6): o bloqueio travaria `git pull/checkout/merge/rebase` no checkout principal sempre que a `develop` mexesse nele, e nem valeria nas worktrees. Esses arquivos (`.githooks/`, `.claude-plugin/`, `.github/`, `tests/config.json`, `tests/catraca.py`, `tests/neutralidade.py`, `hooks/conformidade.json`, `docs/reviews/`, `docs/qa/`, `.claude/CLAUDE.md`) ficam com o hook `conformidade` (Write/Edit por papel), a catraca do CI (rótulo do dono) e o registro de autoria; o Bash não os bloqueia (limite documentado, SBX-03). Se a ferramenta Write/Edit falhar com "classifier gave no verdict", o agente para e relata ao Jarvis; não grava pelo shell. O Claude Code protege sempre `.claude/settings*.json`, `.claude/{skills,agents,commands,hooks}`, `.git/hooks` e `.git/config`. O sandbox vale só para o Bash: esses arquivos mudam por Write/Edit, numa branch, com PR revisado (é o desejado).
- **Caches:** `~/.cache`, `~/.npm` e afins são somente leitura; rode `scripts/configurar-ambiente-local.sh` uma vez por máquina: ele grava no `.claude/settings.local.json` (ignorado pelo git) o `env` que aponta `npm_config_cache`, `XDG_CACHE_HOME`, `PIP_CACHE_DIR` e `PLAYWRIGHT_BROWSERS_PATH` para `${TMPDIR:-/tmp}/claude-<uid>/cache/`, sem fixar o UID. Para pnpm: `pnpm config set store-dir` num caminho do diretório de trabalho (ou `--store-dir`). Cada pacote de stack (etapa 3) traz o que precisa.
- **Rede:** GitHub, npm, yarn, nodejs.org, PyPI e downloads do Playwright liberados; as APIs de modelo (Anthropic, OpenAI, Google) são negadas (`R-CUSTO`). Só `tmux capture-pane`, `tmux ls` e `tmux has-session` rodam fora do sandbox, e só quando o comando vem exato e sozinho: com pipe, redirecionamento, `cd` ou `&&` a chamada volta ao sandbox e falha no socket (rode `tmux ls` puro, sem `| grep`).
- **Rede restrita de verdade (decisão do dono):** `allowedDomains` no arquivo do projeto só pré-libera domínios; sem ele, um host fora da lista ainda é alcançado. Para bloquear o resto, ligue `sandbox.network.strictAllowlist: true` no seu `~/.claude/settings.json` (um repositório não pode ligá-lo nem desligá-lo; também vale em configuração gerenciada). Fora do Claude: `claude config` não cobre isso; edite o arquivo, por exemplo `jq '.sandbox.network.strictAllowlist=true' ~/.claude/settings.json > /tmp/s && mv /tmp/s ~/.claude/settings.json` (guarde cópia antes). Enquanto não ligar, a barreira de rede é só `deniedDomains` (APIs de modelo, `R-CUSTO`).
- **Identidade do git (ADR 0009, etapa 2):** os agentes usam só a conta de máquina (o bot): o `env` do `settings.local.json` (gerado por `scripts/configurar-ambiente-local.sh`) troca `git@github.com:` por HTTPS (`url.<https://github.com/>.insteadOf`) e usa `gh auth git-credential` como helper, que lê o `GH_TOKEN` do `~/.claude/settings.json` do dono (nunca gravado no repositório). Tudo por variáveis `GIT_CONFIG_*`, sem tocar `.git/config` nem `~/.gitconfig`. `~/.ssh`, `~/.config/gh` e `~/.git-credentials` ficam ilegíveis para o Bash (`denyRead`). Os commits continuam com nome e e-mail do `~/.gitconfig` do dono; só o push é do bot. O PR `homolog` → `main` é aberto e mesclado por ele, por merge commit (`R-FLUXO`, ADR 0012), e assim o commit de merge da `main` leva o autor do dono. Fora do Claude (terminal comum) nada muda: a chave SSH do dono segue valendo.
- **Git:** `.git/config` é protegido: use `git push origin <branch>`, não `-u`, e não rode `git config` nem `git branch --set-upstream`. Worktree: `git worktree add --no-track -b <branch> <dir> origin/develop` (com rastreamento o git grava no `.git/config`).
- **Pasta de contribuição:** o sandbox libera escrita dentro de `~/.forge-contrib/`, mas a pasta pessoal é somente leitura; o usuário cria a pasta uma vez, fora do Claude: `mkdir -p ~/.forge-contrib/wt`.
- **Validar o plugin:** o ponto de montagem `.mcp.json` faz `claude plugin validate .` falhar na raiz; use `scripts/validar-plugin.sh`, que valida uma cópia limpa (arquivos versionados, com as mudanças do disco) em `$TMPDIR`. O CI continua com o comando direto.
- **Pontos de montagem:** o bubblewrap cria, na raiz do diretório de trabalho, arquivos e pastas vazios e somente leitura (`.bashrc`, `.gitconfig`, `.forge`, `.claude/hooks` etc.) para cobrir os caminhos protegidos; o `.gitignore` os ignora.
- **CLI do Claude nos testes:** a chamada tenta `api.anthropic.com` e é bloqueada; é o esperado (`R-CUSTO`).
- **Conferir:** `/sandbox` na sessão.
- **Emergência (só o dono):** edite `.claude/settings.json` no terminal, fora do Claude, e reinicie a sessão.

## Branches
Os projetos usam **só a `main`**. Melhorias entram por `develop` (bateria no PR; no push, só a checagem rápida), passam pela `homolog` (mesma bateria sobre o conjunto da release; nada que custe uso de API) e chegam à `main` por PR mesclado pelo dono do Forge.

**Hooks `pre-push` (assimetria proposital):** o do Forge bloqueia `develop`, `homolog` e `main`, pois a fábrica tem as três como degraus protegidos; o do modelo de projeto bloqueia só a `main`, porque o projeto usa apenas ela como branch protegida (o resto é livre).

## Hooks
Em projeto com `.forge/versao`, o plugin garante por código, sem gastar contexto, o teto de agentes, o parecer antes de PR e merge, uma tarefa pesada por vez e o quadro válido (ADR 0003). Ajustes e como desligar um hook: [`docs/hooks.md`](docs/hooks.md).

## Atualizar um projeto
Quem contribui com o Forge não edita o `CHANGELOG.md`: cada PR grava a sua entrada em `changelog.d/<branch>.md` (`bin/forge-changelog novo <tipo> "<texto>"`) e a release junta tudo, sem conflito entre PRs paralelos.

O Forge nunca muda um projeto sozinho (ADR 0005). Cada versão está no `CHANGELOG.md`; as marcadas "**requer migração**" mudam arquivos do projeto. No terminal, dentro do projeto, com a árvore limpa:
- `forge atualizar`: mostra a versão em uso, a nova e o que muda (resumo do CHANGELOG); pede "s"; guarda o **ponto de retorno** (versão do plugin e cópia de `.forge/` e da configuração, em `~/.local/state/forge/retorno/`); roda `forge-upgrade --simular` e, se der certo, troca o plugin e aplica o `forge-upgrade` (branch `forge/upgrade-<versão>`, um commit por migração, sem push nem merge); roda o `forge doutor`; se algo falhar, oferece voltar.
- `forge voltar-versao`: pede "s" e devolve o plugin à versão de antes e os arquivos do projeto (atualização não mesclada: volta à branch de antes e guarda a da atualização; já mesclada: branch `forge/voltar-<versão>` com um registro novo). Nunca usa `--force` nem apaga trabalho.
- **Versão fixada:** o plugin fica fixado na tag `vX.Y.Z` (a marketplace é readicionada como `<endereço>#vX.Y.Z`); nada muda sem você pedir. Uma vez por dia o Jarvis avisa numa linha quando saiu versão nova (consulta grátis às tags por `git ls-remote`, só https; `FORGE_VERIFICAR_VERSAO=0` desliga). `forge atualizar --fixar` só fixa a versão em uso. O `claude plugin update forge@forge` e o `forge-upgrade` soltos continuam valendo para quem prefere o caminho manual.

## Desenvolver o Forge
Ver [`.claude/CLAUDE.md`](.claude/CLAUDE.md): regras, testes, avaliações e versionamento.
