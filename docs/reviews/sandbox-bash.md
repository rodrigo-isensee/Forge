---
tipo: review
contrato: 1
pedido: sandbox-bash
branch: melhoria/sandbox-bash
commit: 4b9a502
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: sandbox obrigatório do Bash no Forge (ADR 0009, seção 5, etapa 1)

Escopo: `.claude/settings.json`, `.gitignore`, `README.md`, `scripts/preparar-estacao.sh`, `tests/test_forge.py` (`SandboxDoBash`), ADR 0009 e `CHANGELOG.md`, diff `origin/develop..4b9a502`.

Conferido: `git ls-files -ci --exclude-standard` vazio (o `.gitignore` não esconde nada versionado); `denyWrite` e `excludedCommands` coerentes com a ADR; `excludedCommands` só de leitura do tmux (nenhum `send-keys`, `new-session` ou `kill-*`); APIs de modelo negadas (`R-CUSTO`); sem nome de projeto (`R-NEUTRO`). `claude plugin validate . --strict` falha neste ambiente, ver B1.

## Bloqueia
- **B1 · `claude plugin validate` quebra por causa do ponto de montagem `.mcp.json`.** O bubblewrap cria `/.mcp.json` vazio (0 byte, somente leitura) na raiz; o validador o lê como manifesto MCP e acusa `Unexpected EOF`. Isso afeta quem trabalha na sessão com sandbox, e o item "Toda mudança passa pela validação do plugin" do `CLAUDE.md` fica impossível de cumprir no diretório de trabalho. Não há como ignorar o arquivo no validador, e ele não pode ser apagado dentro do sandbox. Proposta: (a) o README e o `CLAUDE.md` passam a mandar validar numa cópia limpa (`git worktree add --no-track -d "$TMPDIR/val" HEAD` ou `git archive HEAD | tar -x -C "$TMPDIR/val"`, depois `claude plugin validate "$TMPDIR/val" --strict`); (b) acrescentar um teste que roda esse procedimento sem a chamada de rede, ou ao menos documenta em `tests/` por que a validação local falha; (c) o CI não é afetado (checkout limpo). Documentar antes do merge.
- **B2 · Mudança de fluxo do agente só parcialmente documentada.** O README cobre `--no-track` e push sem `-u`, mas falta: (i) o `CLAUDE.md` do Forge e `agents/tech-lead.md` / `agents/jarvis.md` seguem citando o fluxo antigo (`git push -u`, `claude plugin validate .`); (ii) nenhuma menção a `git branch -u`/`git checkout -b ... origin/develop` sem `--no-track` (o padrão `branch.autoSetupMerge` grava no `.git/config`). Ajustar essas instruções ou deixar explícito no README quais comandos falham. Um grep por `push -u` em `agents/`, `skills/` e `docs/` deve ficar limpo.

## Recomendado
- **R1 · Caches e diretórios do usuário fora do `allowWrite`.** Em `~/.cache` (pnpm, node, ms-playwright, fontconfig), `~/.npm`, `~/.local/share/pnpm`, `~/.config/gh` (o `gh` grava `state.yml` ao checar versão; só `config.yml` existe) e pip `--user` a escrita falha com "somente leitura". O Claude Code libera `~/.npm/_logs`, mas não o cache (`~/.npm/_cacache`). Efeitos esperados no trabalho dos projetos node-react: `pnpm install` e `playwright install` falham fora do cwd; `npm ci` falha no cache. Mitigação sem alargar o sandbox: apontar os caches para `$TMPDIR` ou para o diretório de trabalho (`pnpm config set store-dir`, `npm_config_cache`, `PLAYWRIGHT_BROWSERS_PATH`, `XDG_CACHE_HOME`) e documentar no README e no modelo de projeto (etapa 3). Não liberar `~/.cache` inteiro. `node_modules` dentro do cwd funciona; monorepo com pnpm workspaces dentro do cwd também. Registrar que a etapa 3 precisa tratar isso, já que o Forge em si (Python/shell) não depende deles.
- **R2 · Domínios de rede que a stack node-react vai pedir (etapa 3, não bloqueia a etapa 1).** `objects.githubusercontent.com` e `raw.githubusercontent.com` já estão cobertos por `*.githubusercontent.com`. Faltam, para o modelo de projeto: `nodejs.org` (binários do Node e headers do `node-gyp`), `registry.yarnpkg.com` (se a stack usar yarn), `cdn.playwright.dev` / `playwright.azureedge.net` (browsers do Playwright), `registry.npmjs.org` já está. Para o Forge a lista atual basta; registrar a lista por stack no pacote `stacks/node-react/` na etapa 3 (a ADR já prevê "domínios por stack").
- **R3 · `/tmp/claude-1000` fixa o UID 1000.** Em outra estação, com outro UID, o caminho não existe e a liberação é inútil; o `$TMPDIR` da sessão já é liberado pelo Claude Code, então a entrada talvez seja desnecessária. Verificar se pode sair; se ficar, comentar o motivo no README (que hoje o apresenta como regra).
- **R4 · `tests/neutralidade.py` em `denyWrite` e no `.gitignore`.** O arquivo não existe no repositório (nem a ADR o cita como existente), então o bubblewrap cria um arquivo vazio na raiz de `tests/`; se alguém criar o teste mais tarde, o `.gitignore` o esconderia do git (o teste `git ls-files -ci` só pega o que já é versionado). Remover da lista ou criar o arquivo de fato; a lista `denyWrite` não deveria apontar para o que não existe.
- **R5 · O teste do `.gitignore` não cobre a regra inversa.** Ele confere os padrões e que nada versionado é ignorado, mas não que os caminhos de `denyWrite` realmente existentes (`.githooks/`, `.github/`) continuem versionados. Já coberto indiretamente por `ls-files -ci`; sem ação.
- **R6 · Testes de `SandboxDoBash` não conferem `denyWrite`, `failIfUnavailable` de fato efetivo nem os domínios.** Acrescentar asserts sobre `denyWrite` (os oito caminhos) e sobre `excludedCommands` (sem `send-keys`), para a catraca/CI pegarem afrouxamento. Hoje alguém pode apagar um `denyWrite` sem teste vermelho.

## Veredito
**Reprovado** até B1 e B2 serem tratados (são documentação e um teste, sem mudança de lógica). R1 a R6 podem entrar nesta branch ou virar cartão para a etapa 3. Refazer a revisão sobre o novo HEAD; o restante do desenho (deny de rede, escrita restrita, `excludedCommands` só de leitura) está correto.
