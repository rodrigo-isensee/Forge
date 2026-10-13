---
tipo: review
contrato: 1
pedido: sandbox-bash
branch: melhoria/sandbox-bash-r1
commit: efc63e5
parecer: aprovado
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

## Revalidação (8348d61)
Diff `5de4705..8348d61`. `scripts/validar-plugin.sh` rodou na worktree e passou (`Validation passed`); as quatro negações de `api.anthropic.com` no log são a chamada do CLI, esperada (`R-CUSTO`).

| Item | Situação | Nota |
|---|---|---|
| B1 | corrigido | `scripts/validar-plugin.sh` valida cópia limpa em `$TMPDIR`; `CLAUDE.md`, README, `CONTRIBUTING` e skill apontam para ele; o CI segue com o comando direto. Teste estrutural só confere o conteúdo do script (não o executa), aceitável. |
| B2 | corrigido | grep por `push -u` em `agents/`, `skills/`, `docs/` limpo (restam só menções de proibição); `CLAUDE.md`, `tech-lead`, skill e `CONTRIBUTING` atualizados; README e skill citam `git branch -u` e `--no-track`. |
| R1 | parcial | caches via `env` (npm, XDG, pip, Playwright); pnpm documentado (`store-dir`), sem `env`. Etapa 3 trata o resto. |
| R2 | corrigido | `nodejs.org`, `registry.yarnpkg.com` e domínios do Playwright acrescentados. |
| R3 | parcial | entrada de `allowWrite` removida e README explica; o UID 1000 passou para o `env` (ver N1). |
| R4 | parcial | `tests/neutralidade.py` segue em `denyWrite` e no `.gitignore`; agora o README documenta o arquivo vazio criado. Risco de o `.gitignore` esconder o teste futuro continua (ver N3). |
| R5 | sem ação | como no parecer anterior. |
| R6 | corrigido | testes de `denyWrite` (oito caminhos), `excludedCommands` e `deniedDomains` com curinga. |

### Achados novos (não bloqueiam)
- **N1 · `env` com `/tmp/claude-1000` literal.** Em outro UID o caminho não existe e o bubblewrap não permite criá-lo: `npm`, `pip` e Playwright falham. O README avisa ("ajuste o número"), e o `env` do projeto não expande variáveis. Para o Forge (Python e shell) não pesa; resolver na etapa 3 (por exemplo, gerar o `env` por estação, no `preparar-estacao.sh`). Recomendado registrar como cartão.
- **N2 · `scripts/validar-plugin.sh`.** A cópia vem de `git ls-files`: arquivos ignorados e pontos de montagem (`.mcp.json`, `.bashrc`, `.forge` etc.) não vazam, como se quer. Ressalvas: (i) arquivo novo ainda não adicionado ao índice não entra na cópia, e o comentário do script ("mudanças ainda não commitadas") só vale para arquivos já rastreados; avisar no cabeçalho ou usar `git add -N`; (ii) com `pipefail`, se o último arquivo rastreado tiver sido apagado do disco, o `while` sai com status 1 e o script aborta (acrescentar `|| true` ao `[ -e ] && printf`, ou `if`); (iii) symlink quebrado é omitido. Casos de borda, recomendados.
- **N3 · Pendências em `.github/`: não encontrei registro.** Nem o `CHANGELOG`, nem a ADR 0009, nem o README listam que o CI (`.github/workflows/`) ainda precisa de ajuste: o CI deve passar a rodar também a checagem de `denyWrite`/sandbox sem depender do ponto de montagem, e `.github/` está em `denyWrite` (o dono edita). Registrar a pendência na ADR 0009 ("Andamento da seção 5") ou em cartão antes do merge; não altera o código.
- **N4 · Limites de SBX-01 e SBX-02** (`strictAllowlist` só no arquivo do usuário; `excludedCommands` só para o comando exato) estão documentados no README, na ADR e nos bugs. A decisão de ligar `strictAllowlist` é do dono (`R-DECISAO`); até lá a barreira de rede é só `deniedDomains`. O QA revalida em paralelo.

## Veredito da rodada 1
**Aprovado**, com N1 a N3 como recomendados (podem entrar nesta branch ou virar cartão da etapa 3). Quem mescla é o tech-lead depois do parecer do QA.

## Revalidação (49df362)
Diff `901bc91..49df362` (etapa 2 do sandbox e SBX-03). `SandboxDoBash` passa (11 testes) e `forge-check docs` não reclama. Não executei o git com token em rede (QA em paralelo); a análise abaixo é do desenho e do texto dos arquivos.

| Foco | Situação | Nota |
|---|---|---|
| `GIT_CONFIG_*` | correto | `insteadOf` só reescreve `git@github.com:` (outros hosts e outras formas de URL não mudam). O helper vazio (`KEY_1`) zera os helpers herdados do `~/.gitconfig` do dono (por exemplo `gh auth setup-git` apontando para as credenciais dele) e só depois entra `!gh auth git-credential` (`KEY_2`), restrito a `https://github.com`. Sem `GH_TOKEN` do bot e com `~/.config/gh` ilegível o helper falha: o push fica negado, não cai nas credenciais do dono (falha fechada). Nenhuma credencial literal; o teste barra `ghp_`, `github_pat_`, `GH_TOKEN` e chave privada. `GIT_TERMINAL_PROMPT=0` evita pedido interativo. Escopo no `env` do projeto, sem gravar `.git/config`. |
| `denyRead` | ok | `~/.ssh`, `~/.config/gh` e `~/.git-credentials` não são usados por testes, `gh` (com `GH_TOKEN`), `git fetch` e `git push` por HTTPS. O README informa que fora do Claude a chave SSH do dono segue valendo. |
| `denyWrite` novo | ok, com ressalva | Coerente com a ADR 0009 e com `hooks/conformidade.json` (`docs/reviews/` só `tech-lead`, `docs/qa/` só `qa`, pela ferramenta Write/Edit, que o hook de autoria registra). O commit pelo `git` não grava nesses caminhos, então `git add`/`commit` seguem funcionando. Ver N5 e N6. |
| Documentação | ok | README e ADR 0009 descrevem a identidade (commit com autor do dono, push do bot), o PR `homolog` → `main` aberto e mesclado pelo dono (o squash leva o autor dele) e a parada em "classifier gave no verdict". CHANGELOG registra as duas entradas e as pendências de `.github/`. Testes cobrem `denyRead`, os três caminhos de `denyWrite` e a configuração do git. |

### Achados novos (não bloqueiam)
- **N5 · `denyWrite` só vale no checkout do Forge, não nas worktrees.** Os caminhos relativos são resolvidos a partir do projeto; as worktrees em `~/.forge-contrib/wt/<nome>` ficam sob `allowWrite` e, nesta sessão (iniciada antes da mudança), o `mountinfo` não mostra `docs/reviews/`, `docs/qa/` nem `.github/` como somente leitura. Se for assim, quem trabalha em worktree consegue gravar parecer pelo shell, e o ganho do SBX-03 vale só para a cópia principal. Confirmar com o QA numa sessão nova e, se confirmado, documentar o limite no README (a barreira real é o hook de autoria e o PR revisado) ou acrescentar `~/.forge-contrib/wt/*/docs/reviews` etc. ao `denyWrite`.
- **N6 · `git checkout`, `merge`, `rebase` e `pull` que alterem esses caminhos falham no sandbox.** Eles passam pelo Bash, e `docs/reviews/`, `docs/qa/` e `.claude/CLAUDE.md` são somente leitura no checkout principal: trocar de branch ou mesclar com mudança de parecer dá "somente leitura". Documentar no README (usar a worktree para isso ou pedir ao dono) ou cobrir com um teste do QA.
- **N7 · Outras credenciais do dono seguem legíveis.** `~/.netrc`, `~/.config/git/credentials`, `~/.npmrc`, `~/.gnupg`, `~/.aws`, `~/.docker/config.json` e o `~/.claude/settings.json` (onde está o token do bot) não estão em `denyRead`. O token do bot é aceito (é a identidade dos agentes), mas o resto das chaves do dono, não. Avaliar acrescentar os que existirem na estação; é decisão do dono quanto ao `~/.claude/.credentials.json`.
- **N8 · Ordem dos pares `GIT_CONFIG_*` não é testada.** O teste monta um conjunto e perde a ordem; se alguém trocar `KEY_1` e `KEY_2`, o helper vazio apagaria o do bot e os testes ficariam verdes. Recomendado conferir que o índice do valor vazio é menor que o do `!gh auth git-credential`.
- **N9 · `insteadOf` não cobre `ssh://git@github.com/`.** Esse formato continua indo por SSH e falha de forma fechada por causa do `denyRead` de `~/.ssh`; só registrar.

## Veredito da revalidação
**Aprovado** para a etapa 2 e a correção do SBX-03. N5 e N6 devem ser confirmados pelo QA antes do merge (podem virar texto no README ou cartão); N7 a N9 são recomendados. Quem mescla é o tech-lead depois do parecer do QA.

## Revalidação (0432563)
Diff `384df8b..0432563` (decisão N6). `SandboxDoBash` passa (10 testes).

| Foco | Situação | Nota |
|---|---|---|
| Coerência com N6 | ok | `denyWrite` fica só com `.forge/` (nenhum arquivo versionado sob ele). Resolve N6 (git `pull/checkout/merge/rebase` travando no checkout principal) e deixa de lado N5 (não valia nas worktrees). README, CHANGELOG e ADR 0009 (seção 5, tabela e nota "Ajuste da implementação (N6)") dizem o mesmo. |
| Honestidade da ADR | ok, com ressalva | A ADR admite o limite (SBX-03): o Bash pode gravar em `docs/reviews/`, `docs/qa/` e `.claude/CLAUDE.md`. Ressalva (recomendado, N10): as linhas da matriz passaram de [I] para [B], mas o hook `conformidade` age sobre Write/Edit e comandos reconhecidos, não sobre qualquer redirecionamento do shell; o que cobre de fato a escrita por Bash é o registro de autoria e o PR revisado (detecção, [D]) e a catraca do CI só para os arquivos de proteção. Sugiro ajustar o rótulo para "[B] no Write/Edit; [D] no Bash" nas duas linhas afetadas. Não bloqueia: o texto da nota já descreve o limite. |
| Teste novo | ok | `test_deny_write_so_estado_nao_versionado` cruza cada entrada de `denyWrite` com `git ls-files` (arquivo exato ou prefixo de diretório) e falha se cobrir caminho versionado, além de exigir `.forge/`. Substitui os dois testes que travavam o contrário; impede a regressão. |
| Nada mais afrouxado | ok | O diff de `.claude/settings.json` só remove entradas de `denyWrite`; `denyRead`, `deniedDomains`, `allowUnsandboxedCommands` e `failIfUnavailable` intactos, e os testes que os cobrem seguem verdes. |

## Veredito da revalidação (0432563)
**Aprovado.** N10 é recomendado (texto da ADR); N7 a N9 seguem como antes. Quem mescla é o tech-lead depois do parecer do QA.

## Revalidação (efc63e5)
Diff `0432563..efc63e5` (sem `CHANGELOG.md`): 9 arquivos. `SandboxDoBash` e a suíte completa passam (212 testes, OK); `scripts/validar-plugin.sh` passa.

| Foco | Situação | Nota |
|---|---|---|
| N10 (rótulo da matriz) | ok | As duas linhas (parecer em `docs/reviews/` e `docs/qa/`; `CLAUDE.md` do projeto) agora dizem "[B] no Write/Edit (hook `conformidade`); [D] no Bash (autoria e PR revisado)". Confere com a legenda da ADR ("[D] detectado depois"): a escrita por Bash é detectada, não barrada. Só texto de matriz; nenhum comportamento mudou. |
| SBX-03 | ok | Só a linha de status passou a dizer "limite documentado (decisão N6)". Não há mudança no `denyWrite` nem em teste. |
| Merge da `develop` (`ff3101d`) | ok | `.github/workflows/ci.yml` (job `workflows`), `docs/adr/0008-governanca-de-contribuicoes.md`, `docs/regras/R-FLUXO.md`, a linha de sincronização em `agents/tech-lead.md` e `docs/reviews/workflows-auditoria.md` são idênticos aos da `origin/develop`. Os demais arquivos de código e configuração do PR (`scripts/`, `tests/`, `skills/`, `.claude/`) não estão no delta desde `0432563`. |
| Escopo do PR | ok | Fora do delta, a diferença de `agents/tech-lead.md` em relação à `origin/develop` (`git push origin <branch>`, sem `-u`) já vinha de commits anteriores do PR, não deste merge. |

Recomendado, sem bloqueio: o `CHANGELOG.md` (excluído deste delta) traz a entrada do job `workflows` e a da sincronização `main` → `develop`, vindas da `develop`; conferir na release que as entradas do PR continuam sob `## [Não publicado]`.

Ambiente de execução: `validar-plugin.sh` e a suíte geraram avisos `deny network-outbound` (APIs de modelo e telemetria negadas pelo sandbox), esperados pela regra `R-CUSTO`.

## Veredito da revalidação (efc63e5)
**Aprovado.** Sem bloqueio nem achado novo. N10 foi aplicado com o rótulo honesto; o restante do delta é o merge da `develop` sem alteração. Quem mescla é o tech-lead depois do parecer do QA.
