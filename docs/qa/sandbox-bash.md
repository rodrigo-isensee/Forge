---
tipo: qa
contrato: 1
pedido: sandbox-bash
branch: melhoria/sandbox-bash-r1
commit: 0432563
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-13
---

# QA - sandbox obrigatório do Bash (ADR 0009, etapa 1)

Verificação na prática, na sessão com o sandbox ativo e o `.claude/settings.json` desta branch. Cada comando foi rodado com a ferramenta Bash e o resultado é o observado, não o previsto.

Nota sobre o commit: o teste foi feito a partir de 4b9a502. Durante a sessão o HEAD passou a 9e39b8a (`docs: review do sandbox do Bash`), que só altera `docs/reviews/sandbox-bash.md`. Esse diff toca só pareceres, então vale o commit 4b9a502 (ADR 0004, regra de validade 2). O `.claude/settings.json` não mudou entre os dois.

## Escopo
- Coberto: sandbox de escrita (dentro, fora e nos caminhos protegidos), rede (permitida, negada e fora da lista), comandos que o README manda rodar fora do sandbox, git (`.git/config` protegido, worktree sem rastreamento) e a suíte de testes.
- Não coberto: testes de acessibilidade e E2E (não há interface nesta feature); mutação e vermelho-antes-do-verde (não há código de produção alterado neste pedido).
- Limite de ambiente: a verificação foi feita só em Linux/WSL2 com bubblewrap. Não cobre outros sistemas.

## Resultados (comando → esperado → obtido)

### Deve funcionar
| # | Comando | Esperado | Obtido | Veredito |
|---|---|---|---|---|
| 1 | `python3 -m unittest discover -s tests` | suíte verde | `Ran 206 tests ... OK` (38,7 s). A chamada da CLI do Claude gerou `deny network-outbound api.anthropic.com:443`, o esperado (R-CUSTO) | passou |
| 2 | `git status` | funciona | árvore limpa, rc 0 | passou |
| 3 | `git log -1` | funciona | `9e39b8a` (HEAD da sessão; ver nota acima) | passou |
| 4 | `gh api user -q .login` | funciona | `rodrigo-isensee` | passou |
| 5 | `gh pr list --limit 1` | funciona | lista a PR #48 | passou |
| 6 | `git ls-remote origin develop` | funciona | `13e6096...refs/heads/develop` | passou |
| 7 | `curl -sI https://registry.npmjs.org/` | funciona | `HTTP/1.1 200 Connection Established` (linha do túnel do proxy) | passou |
| 8 | `curl -sI https://pypi.org/` | funciona | `HTTP/1.1 200 Connection Established` | passou |
| 9 | escrever e apagar em `$TMPDIR` | funciona | escreveu, leu e apagou | passou |
| 10 | escrever e apagar em `~/.forge-contrib/wt/` | funciona | escreveu e apagou | passou |
| 11 | `git worktree add --no-track -b qa-sbx ~/.forge-contrib/wt/qa-sbx origin/develop` | funciona | criada em 13e6096, rc 0 | passou |
| 12 | `git worktree remove ~/.forge-contrib/wt/qa-sbx` | funciona | rc 0 | passou |
| 13 | `git branch -D qa-sbx` | funciona | rc 0, branch apagada, mas com aviso `could not lock config file .git/config` (ver O-2) | passou com ressalva |
| 14 | `tmux ls` | roda fora do sandbox, lista sessões | `error connecting to /tmp/tmux-1000/default (Operation not permitted)`, rc 1 | **FALHOU: SBX-02** |

### Deve ser bloqueado
| # | Comando | Esperado | Obtido | Veredito |
|---|---|---|---|---|
| 15 | `touch ~/sonda-sandbox` | bloqueado | `Read-only file system`, rc 1, arquivo não existe | passou |
| 16 | `echo x >> .git/config` | bloqueado e config inalterado | `Read-only file system`, rc 1; `git config --local --list` idêntico antes e depois | passou |
| 17 | `touch .githooks/sonda` | bloqueado | `Read-only file system`, rc 1 | passou |
| 18 | `touch .forge/sonda` | bloqueado | `Not a directory`, rc 1. `.forge` é dispositivo de caractere (ponto de montagem do bubblewrap), então o bloqueio vem do mount e não da regra de escrita (ver O-3) | passou (bloqueio correto, teste pouco discriminante) |
| 19 | `curl -sI https://api.anthropic.com` | bloqueado | `HTTP/1.1 403 Forbidden`, rc 56, `deny ... (host is on the deny list)` | passou |
| 20 | `curl -sI https://api.openai.com` | bloqueado | `HTTP/1.1 403 Forbidden`, rc 56, `deny ... (host is on the deny list)` | passou |
| 21 | `curl -sI https://example.com` | bloqueado (fora de `allowedDomains`) | HTTP 200, corpo servido | **FALHOU: SBX-01** |
| 22 | `git branch --set-upstream-to=origin/develop` | falha, config inalterado | `could not lock config file .git/config: File exists`, rc 1; config idêntico antes e depois | passou |

### Ensaios extras (para SBX-01)
| Comando | Obtido |
|---|---|
| `curl ... https://httpbin.org/get` (host fora da lista) | HTTP 200. Confirma que a allowlist não é aplicada |
| `curl ... https://github.com` (dentro da lista) | HTTP 200, esperado |

## Bugs

Estado na rodada 0 (4b9a502), mantido como histórico. Estado atual na seção "Revalidação (6e0ff68)" abaixo.

| ID | Título | Severidade | Estado (rodada 0) | Estado (6e0ff68) |
|---|---|---|---|---|
| SBX-01 | Sandbox acessa qualquer host; a allowlist não é aplicada | crítica | aberto | limite documentado (não conta como aberto) |
| SBX-02 | `tmux ls` e `tmux has-session` falham mesmo fora do sandbox | média | aberto | limite documentado; verificação ao vivo pendente do reinício |
| SBX-03 | `denyWrite` sem `docs/reviews/`, `docs/qa/` e `CLAUDE.md` | média | (novo) | aberto |

Relatórios em `docs/qa/bugs/SBX-01-rede-sem-allowlist.md`, `docs/qa/bugs/SBX-02-tmux-sem-acesso-ao-socket.md` e `docs/qa/bugs/SBX-03-denywrite-sem-pareceres-e-claude-md.md`.

## Observações (não são bugs pela definição do pedido)
- **O-1. Upstream antigo da branch.** `.git/config` já tinha `branch.melhoria/sandbox-bash.merge=refs/heads/develop`, anterior a esta sessão. Um `git push` sem refspec pode tentar `develop`, que o hook bloqueia, mas é armadilha. Correção pelo dono, fora do Claude: `git branch --set-upstream-to=origin/melhoria/sandbox-bash` ou remover o rastreamento. Não foi alterado.
- **O-2. Aviso do `git branch -D`.** O comando apagou a branch, mas tentou escrever em `.git/config` (para limpar a seção, que não existia por causa do `--no-track`) e imprimiu aviso. Inócuo. Como o sandbox nega a escrita, o aviso é esperado; vale documentar.
- **O-3. Teste de `.forge` pouco discriminante.** O bloqueio de `.forge/` é feito pelo dispositivo montado, então o teste não separa "regra de escrita" de "ponto de montagem". Sugestão: incluir um teste em `.githooks/` (diretório real) como sonda principal.
- **O-4. Dica do git com refspec errado.** A mensagem de `--set-upstream-to` sugere `origin/refs/heads/develop`, que é inválido. É do git, não do sandbox. Cosmético.
- **O-5. Modelo ausente.** `docs/qa/_modelo.md`, citado pela skill `qa-testing`, não existe nesta branch. Este parecer segue os campos da ADR 0004.

## Veredito (rodada 0, 4b9a502)
**Reprovado.** Há um bug crítico aberto (SBX-01, rede sem allowlist) e um médio (SBX-02). Veredito atual na seção abaixo. Os controles de escrita (`.git/config`, `.githooks/`, `~/`), o bloqueio das APIs de modelo (`R-CUSTO`) e o uso do git e do GitHub estão corretos. Correções nas configurações são decisão do dono do Forge (R-DECISAO); não foram alteradas aqui. Aceite do usuário necessário para o médio aberto (`aceite_usuario: sim`).

## Revalidação (6e0ff68)
Escopo incremental: rodada 1 de correção (d012adb, ccffdae, ee99903, 8f44b52, 8f78805, 8348d61) e os commits de pareceres 901bc91 e 6e0ff68. HEAD testado: `6e0ff68`. O pedido citava `8348d61`; enquanto a revalidação rodava, a branch recebeu 901bc91 e 6e0ff68, que só tocam `docs/reviews/sandbox-bash.md` e `CHANGELOG.md` (ADR 0004, regra 2). O código testado é o mesmo de 8348d61.

Ambiente: Linux/WSL2, bubblewrap. A sessão roda com a configuração ativa (anterior à branch); o `.claude/settings.json` da branch só vale após merge e reinício. Por isso, o que depende dele ao vivo fica para depois do reinício.

### Verificações da rodada 1
| Verificação | Comando | Resultado |
|---|---|---|
| Suíte unitária | `python3 -m unittest discover -s tests` (na worktree) | `Ran 210 tests ... OK` (34 a 37 s), rc 0 |
| Validação do plugin | `scripts/validar-plugin.sh` | `Validation passed`, rc 0 |
| Shellcheck | `~/.local/bin/shellcheck scripts/validar-plugin.sh` | rc 0, sem avisos |
| JSON do sandbox | `python3 -m json.tool .claude/settings.json` | rc 0 |
| tmux puro | `tmux ls` | **falha**: `error connecting to /tmp/tmux-1000/default (Operation not permitted)`, rc 1 (configuração ativa; ver SBX-02) |
| Escrita por Bash em `docs/qa/` | `printf ... > docs/qa/.sonda-qa` | **escreveu** (rc 0), arquivo removido, árvore limpa (ver SBX-03) |
| Escrita por Bash em `docs/reviews/` | idem | escreveu (rc 0), removido (ver SBX-03) |
| Rede fora da lista | `curl https://example.com` | HTTP 200 (ver SBX-01, limite documentado) |

A chamada da CLI do Claude nos testes gera `deny network-outbound api.anthropic.com:443`, o esperado (R-CUSTO).

### Conferência do `.claude/settings.json` da branch
- **denyWrite:** `.forge/`, `.githooks/`, `.claude-plugin/`, `.github/`, `tests/config.json`, `tests/catraca.py`, `tests/neutralidade.py`, `hooks/conformidade.json`. Igual à lista do README. Mínimo no sentido do README, mas **falta** `docs/reviews/`, `docs/qa/` e `CLAUDE.md`, que o ADR 0009 (seções 3 e 5) manda bloquear (SBX-03).
- **deniedDomains:** `api.anthropic.com`, `*.anthropic.com`, `api.openai.com`, `*.openai.com`, `generativelanguage.googleapis.com`. OK.
- **allowedDomains novos:** `nodejs.org`, `registry.yarnpkg.com`, `files.pythonhosted.org`, `uploads.github.com`, `codeload.github.com`, `playwright.azureedge.net`, `playwright.download.prss.microsoft.com`, `cdn.playwright.dev`. OK; só pré-liberam, não bloqueiam (SBX-01).
- **env de caches:** `npm_config_cache`, `XDG_CACHE_HOME`, `PIP_CACHE_DIR`, `PLAYWRIGHT_BROWSERS_PATH` em `/tmp/claude-1000/cache/`. OK; o UID 1000 é fixo no caminho, documentado no README.
- **excludedCommands:** só `tmux capture-pane *`, `tmux ls`, `tmux has-session *`. Todos de leitura. OK.
- **Sem `strictAllowlist`** no arquivo do projeto. Correto: a decisão de ligar é do dono, no `~/.claude/settings.json` (README, "Rede restrita de verdade").
- **Fixos:** `failIfUnavailable: true`, `allowUnsandboxedCommands: false`, `autoAllowBashIfSandboxed: true`.

### Uso documentado do tmux
`tmux ls` sozinho, sem pipe: **não funcionou** (rc 1, `Operation not permitted`), com a configuração ativa. Ao vivo, o caminho documentado não está provado; fica como pendência (SBX-02).

### Limites documentados (não contam como bug aberto)
- **SBX-01 (rede sem allowlist):** o README (seção "Sandbox do Bash", item Rede) diz que `allowedDomains` só pré-libera e que a rede só fica restrita com `strictAllowlist: true` no `~/.claude/settings.json`. A documentação está correta para a configuração da branch. O `strictAllowlist` em si não foi testado ao vivo (exige alterar a configuração do usuário e reiniciar; não foi feito aqui).
- **SBX-02 (tmux):** a documentação diz que `tmux ls` puro funciona e que pipe, `cd` e `&&` voltam ao sandbox. A correção só vale após o reinício; o teste ao vivo com a configuração ativa falhou (ver acima). Se falhar com a configuração da branch, reabre como média.

### Verificado só ao vivo, depois do merge e do reinício
1. `tmux ls` sozinho lista as sessões (SBX-02); `tmux ls | grep ...` volta ao sandbox e falha, como documentado.
2. Com `strictAllowlist: true` no `~/.claude/settings.json` do dono: `example.com` e `httpbin.org` bloqueados; `github.com`, `registry.npmjs.org` e `pypi.org` continuam acessíveis.
3. As APIs de modelo continuam negadas (`api.anthropic.com`, `api.openai.com`) com a configuração nova.
4. `/sandbox` na sessão mostra o `denyWrite` da branch; escrita por Bash em `.githooks/`, `.forge/` e `tests/config.json` continua bloqueada.
5. Escrita por Bash em `docs/qa/` e `docs/reviews/` (SBX-03): bloqueada se o dono decidir incluir os caminhos; caso contrário, o limite fica registrado no ADR 0009 e no README.
6. `npm` e `pip` gravam no cache de `/tmp/claude-1000/cache/` sem erro de somente leitura.
7. Existência da chave `strictAllowlist` na versão do Claude Code instalada: não verificada aqui; a documentação do README depende dela.

### Observações da rodada 0 não reverificadas
O-1 (upstream antigo da branch), O-2 (aviso do `git branch -D`), O-3 (teste de `.forge` pouco discriminante), O-4 (dica do git) e O-5 (modelo `docs/qa/_modelo.md` ausente) continuam como estavam. Não foram reverificadas nesta rodada.

### Veredito (6e0ff68)
**Aprovado com aceite do usuário.** Bugs abertos: 0 críticos, 0 altos, 1 médio (SBX-03), 0 baixos. SBX-01 e SBX-02 são limites documentados; SBX-02 tem verificação ao vivo pendente do reinício. O aceite do usuário é necessário para SBX-03 (`aceite_usuario: sim`). Ressalva: este parecer aceita a documentação dos limites; não verifica ao vivo a configuração da branch, que só entra em vigor após o merge e o reinício.

## Revalidação (49df362)
Escopo completo da configuração proposta: etapas 1 e 2 (inclui o git dos agentes pelo token do bot) e a correção de SBX-03. HEAD testado: `49df362`. A branch tem ainda `63d8531` (`docs: re-review do sandbox`), que só altera pareceres (ADR 0004, regra 2); o código testado é o mesmo. Verificação estática e simulada: esta sessão roda a configuração anterior, e a proposta só vale após merge e reinício.

### Verificações automáticas
| Cenário | Comando | Resultado real |
|---|---|---|
| Suíte unitária | `python3 -m unittest discover -s tests` | `Ran 213 tests ... OK` (37,8 s). Os `deny network-outbound api.anthropic.com:443` são esperados (R-CUSTO) |
| Validação do plugin | `scripts/validar-plugin.sh` | `Validation passed`, rc 0 |
| JSON do sandbox | `python3 -m json.tool .claude/settings.json` | rc 0 |
| Shellcheck | `shellcheck` em `scripts/*.sh`, `scripts/jarvis`, `scripts/jarvis-forge`, `bin/forge-init` | rc 0, sem avisos |

### Simulação do git pelo bot (subshell, só `GIT_CONFIG_*` e `GIT_TERMINAL_PROMPT` do `env` do settings; ambiente da sessão intacto)
| Cenário | Resultado real |
|---|---|
| `git ls-remote --get-url git@github.com:<dono>/Forge.git` | reescrito para `https://github.com/<dono>/Forge.git`: `insteadOf` funciona |
| `git config --get-all credential.https://github.com.helper` | lista o helper global e, depois do valor vazio (reset), `!gh auth git-credential`: o reset está presente |
| `git credential fill` (host github.com, valores mascarados) com `GIT_TRACE=1` | executa `gh auth git-credential get` e devolve `username` e `password` (mascarados); sem prompt |
| `git ls-remote origin develop` | **não concluído nesta sessão**: `CONNECT tunnel failed, response 403`; `deny network-outbound github.com:443 (host is not on the allow list)`. A sessão de QA tem rede estrita sem `github.com`, diferente da sessão da rodada anterior (onde funcionava). Limite de ambiente, não defeito da proposta. O `origin` desta worktree já é HTTPS, então a chamada passaria por helper e `insteadOf` sem mudança |

### Conferência estática do `.claude/settings.json`
- **denyWrite (11):** `.forge/`, `.githooks/`, `.claude-plugin/`, `.github/`, `tests/config.json`, `tests/catraca.py`, `tests/neutralidade.py`, `hooks/conformidade.json`, `docs/reviews/`, `docs/qa/`, `.claude/CLAUDE.md`. Igual ao README e inclui os três itens de SBX-03. OK.
- **denyRead (3):** `~/.ssh`, `~/.config/gh`, `~/.git-credentials`. OK.
- **allowedDomains (13):** `github.com`, `api.github.com`, `*.githubusercontent.com`, `codeload.github.com`, `uploads.github.com`, `registry.npmjs.org`, `registry.yarnpkg.com`, `nodejs.org`, `pypi.org`, `files.pythonhosted.org`, `playwright.azureedge.net`, `playwright.download.prss.microsoft.com`, `cdn.playwright.dev`. OK.
- **deniedDomains (5):** `api.anthropic.com`, `*.anthropic.com`, `api.openai.com`, `*.openai.com`, `generativelanguage.googleapis.com`. OK.
- **excludedCommands (3):** `tmux capture-pane *`, `tmux ls`, `tmux has-session *`; só leitura. OK.
- **env:** caches em `/tmp/claude-1000/cache/` e as chaves `GIT_CONFIG_*` e `GIT_TERMINAL_PROMPT=0`. Busca por `ghp_`, `github_pat_`, `gho_`, `token`, `password`: nenhuma ocorrência; sem credencial literal. OK.
- **Fixos:** `failIfUnavailable`, `allowUnsandboxedCommands: false`, `autoAllowBashIfSandboxed`; sem `strictAllowlist` (decisão do dono, README).

### Bugs
| ID | Estado em 49df362 |
|---|---|
| SBX-01 | limite documentado (README); `strictAllowlist` só ao vivo |
| SBX-02 | limite documentado; `tmux ls` só ao vivo |
| SBX-03 | corrigido na configuração (verificado estaticamente); efeito só ao vivo |

Nenhum bug novo. Observações O-1 a O-5 inalteradas (O-5, `_modelo.md`, não reverificado).

### Só verificável ao vivo, depois do merge e do reinício
1. Rede estrita (`strictAllowlist: true` ligado pelo dono): `example.com` e `httpbin.org` bloqueados; `github.com`, `registry.npmjs.org`, `pypi.org` acessíveis; APIs de modelo seguem negadas.
2. `denyRead` efetivo: `cat ~/.ssh/*`, `~/.config/gh/hosts.yml` e `~/.git-credentials` falham no Bash.
3. Push e leitura remota pelo bot: `git ls-remote origin develop` por HTTPS; `git push` de `melhoria/*` com o helper `gh auth git-credential`, e o push para `develop`, `homolog` e `main` continua bloqueado pelo hook; confirmar que `gh` lê o token sem `~/.config/gh` (via `GH_TOKEN` ou outro caminho do bot).
4. `denyWrite` efetivo: escrita por Bash em `docs/qa/`, `docs/reviews/`, `.claude/CLAUDE.md`, `.githooks/`, `tests/config.json` bloqueada; Write/Edit continua gravando em `docs/qa/` e `docs/reviews/`.
5. `tmux ls` sozinho lista as sessões; com pipe, `cd` ou `&&` falha, como documentado (SBX-02).
6. `npm` e `pip` gravam no cache de `/tmp/claude-1000/cache/` sem erro de somente leitura.
7. Existência da chave `strictAllowlist` na versão instalada do Claude Code.

### Veredito (49df362)
**Aprovado**, sem bugs abertos (0 críticos, 0 altos, 0 médios, 0 baixos), condicionado ao teste ao vivo acima. Ressalva: `git ls-remote` pela rede não pôde ser exercitado nesta sessão (limite de ambiente); `insteadOf` e helper foram provados por simulação.


## Revalidação (0432563)
Escopo incremental: commit `0432563` (`fix(sandbox): denyWrite só para estado não versionado (N6)`), aplicado sobre `49df362`. HEAD testado: `0432563`. Durante a revalidação a branch recebeu `c4438fc` (`docs: re-review do sandbox (N6)`), que só altera `docs/reviews/sandbox-bash.md` (ADR 0004, regra 2); o código testado é o mesmo. Worktree `~/.forge-contrib/wt/sandbox-r1`, branch `melhoria/sandbox-bash-r1`.

Ambiente: Linux/WSL2, bubblewrap. A sessão roda a configuração anterior à branch; o `.claude/settings.json` novo só vale após merge e reinício.

### Verificações automáticas
| Verificação | Comando | Resultado real |
|---|---|---|
| Suíte unitária | `python3 -m unittest discover -s tests` | `Ran 212 tests ... OK` (43,2 s), rc 0. Os `deny network-outbound api.anthropic.com:443` são esperados (R-CUSTO) |
| Validação do plugin | `scripts/validar-plugin.sh` | `Validation passed`, rc 0 |
| JSON do sandbox | `python3 -m json.tool .claude/settings.json` | rc 0 |

### Conferência do `.claude/settings.json` (0432563)
| Item | Esperado | Obtido | Veredito |
|---|---|---|---|
| `denyWrite` | só `.forge/` (N6) | `['.forge/']` | ok |
| Arquivos versionados sob `denyWrite` | nenhum (causa do N6) | `git ls-files .forge` = 0 | ok |
| `denyRead` | 3 caminhos | `~/.ssh`, `~/.config/gh`, `~/.git-credentials` | ok |
| `deniedDomains` | 5 entradas | `api.anthropic.com`, `*.anthropic.com`, `api.openai.com`, `*.openai.com`, `generativelanguage.googleapis.com` | ok |
| `allowUnsandboxedCommands` | `false` | `false` | ok |
| `failIfUnavailable` | `true` | `true` | ok |
| `autoAllowBashIfSandboxed` / `excludedCommands` | inalterados (leitura do tmux) | `true` / 3 entradas de leitura | ok |
| `strictAllowlist` | ausente no projeto (decisão do dono) | ausente | ok |

### Bugs
| ID | Estado em 0432563 |
|---|---|
| SBX-01 | limite documentado (README); `strictAllowlist` só ao vivo |
| SBX-02 | limite documentado; `tmux ls` só ao vivo |
| SBX-03 | limite documentado (decisão N6): o Bash pode gravar em `docs/reviews/`, `docs/qa/` e `.claude/CLAUDE.md`; a barreira é o hook `conformidade`, a catraca do CI e o registro de autoria |

Bugs abertos: 0 críticos, 0 altos, 0 médios, 0 baixos. Nenhum bug novo. Observações O-1 a O-5 da rodada 0 não reverificadas.

### Ressalvas
- **N6 não reproduzido ao vivo.** O argumento (`git pull`, `checkout`, `merge` e `rebase` falham quando um arquivo versionado está sob `denyWrite`) foi conferido por análise: nenhum arquivo versionado está sob `.forge/`. O efeito real só pode ser visto depois do merge e do reinício.
- **SBX-03 virou limite por decisão.** Escrita de parecer ou de `CLAUDE.md` por Bash não é barrada pelo sandbox. A ADR 0009 (seções 3, 5 e nota N6) e o README registram isso. Se o dono quiser o bloqueio de volta, o caminho é reabrir como médio e rever o `denyWrite` junto com a regra de versionamento.
- **Ao vivo, depois do merge e do reinício:** rede estrita com `strictAllowlist` (SBX-01); `tmux ls` sozinho (SBX-02); escrita por Bash em `.forge/`, `.githooks/` e `tests/config.json` bloqueada; `denyRead` efetivo; `git pull`/`checkout` no checkout principal com `develop` alterando um parecer (N6).

### Veredito (0432563)
**Aprovado**, escopo incremental. Bugs abertos: 0 em todas as severidades; `aceite_usuario` não é exigido. A aprovação depende de a decisão N6 ser confirmada pelo dono (limite de SBX-03) e das verificações ao vivo acima.
