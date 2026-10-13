---
tipo: qa
contrato: 1
pedido: sandbox-bash
branch: melhoria/sandbox-bash
commit: 4b9a502
parecer: reprovado
escopo: completo
bugs_criticos: 1
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
aceite_usuario: sim
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

| ID | Título | Severidade | Estado |
|---|---|---|---|
| SBX-01 | Sandbox acessa qualquer host; a allowlist não é aplicada | crítica | aberto |
| SBX-02 | `tmux ls` e `tmux has-session` falham mesmo fora do sandbox | média | aberto |

Relatórios em `docs/qa/bugs/SBX-01-rede-sem-allowlist.md` e `docs/qa/bugs/SBX-02-tmux-sem-acesso-ao-socket.md`.

## Observações (não são bugs pela definição do pedido)
- **O-1. Upstream antigo da branch.** `.git/config` já tinha `branch.melhoria/sandbox-bash.merge=refs/heads/develop`, anterior a esta sessão. Um `git push` sem refspec pode tentar `develop`, que o hook bloqueia, mas é armadilha. Correção pelo dono, fora do Claude: `git branch --set-upstream-to=origin/melhoria/sandbox-bash` ou remover o rastreamento. Não foi alterado.
- **O-2. Aviso do `git branch -D`.** O comando apagou a branch, mas tentou escrever em `.git/config` (para limpar a seção, que não existia por causa do `--no-track`) e imprimiu aviso. Inócuo. Como o sandbox nega a escrita, o aviso é esperado; vale documentar.
- **O-3. Teste de `.forge` pouco discriminante.** O bloqueio de `.forge/` é feito pelo dispositivo montado, então o teste não separa "regra de escrita" de "ponto de montagem". Sugestão: incluir um teste em `.githooks/` (diretório real) como sonda principal.
- **O-4. Dica do git com refspec errado.** A mensagem de `--set-upstream-to` sugere `origin/refs/heads/develop`, que é inválido. É do git, não do sandbox. Cosmético.
- **O-5. Modelo ausente.** `docs/qa/_modelo.md`, citado pela skill `qa-testing`, não existe nesta branch. Este parecer segue os campos da ADR 0004.

## Veredito
**Reprovado.** Há um bug crítico aberto (SBX-01, rede sem allowlist) e um médio (SBX-02). Os controles de escrita (`.git/config`, `.githooks/`, `~/`), o bloqueio das APIs de modelo (`R-CUSTO`) e o uso do git e do GitHub estão corretos. Correções nas configurações são decisão do dono do Forge (R-DECISAO); não foram alteradas aqui. Aceite do usuário necessário para o médio aberto (`aceite_usuario: sim`).
