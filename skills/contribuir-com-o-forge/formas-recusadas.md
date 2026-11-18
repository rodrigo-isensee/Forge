# Formas que o hook recusa na sessão de projeto (R-CONTRIB, diretriz 36)

Detalhe do trecho `R-CONTRIB` de `docs/regras/R-LIMITES.md`. O hook `conformidade` decide pela raiz da sessão; a sessão do Forge não é afetada. Cada recusa diz a forma aceita: `forge sugerir --guardar "<texto>"`.

## No clone do Forge
- Gravar commit ou ref: commit, merge, cherry-pick, revert, am, rebase, pull, `commit-tree`, `update-ref`, `subtree`, reset, stash, notes e `symbolic-ref`. Na dúvida grava: `git stash list` e `git notes show` também são recusados.
- Criar branch: `branch <nome>`, `switch -c`, `checkout -b`, `--track`, `--orphan` e `worktree add`.
- `fetch` com destino (`origem:destino`).

## Envio com o destino trocado na linha
- `git -c remote.<n>.url=`, `-c remote.<n>.pushurl=`, `-c url.<base>.insteadOf=` e `pushInsteadOf`; também `-c branch.<b>.pushRemote=`, `-c branch.<b>.remote=` e `-c remote.pushDefault=` com o Forge ou variável.
- `git config` que grava a URL de um remoto com o Forge ou com variável, ou qualquer reescrita de URL (`insteadOf`, `pushInsteadOf`): o envio da mesma linha iria ao Forge antes que o hook leia o disco.
- `git config` com as mesmas chaves do remoto do envio (`branch.<b>.pushRemote`, `branch.<b>.remote`, `remote.pushDefault`) e o Forge; `git config -e` (também agrupada, `-ze`, `-ez`; não quando o `e` é o valor de `-f` ou `-t`), `--edit` e `edit` sempre (o editor grava o que o hook não vê).
- `git push` sem remoto com uma dessas chaves já gravada no disco com o Forge, ou com a configuração ilegível.
- Envio para caminho local ou `file://` em `~/.forge-contrib` ou num clone do Forge, direto, pela URL do remoto ou pelas chaves do envio na linha (`-c` ou `git config`).
- `push --repo`, `-C` encadeado, `--git-dir`, `subtree push` e `remote add|set-url` com o Forge.

## gh no Forge
- Todo `gh` que não só lê: PR, issue, comentário, rótulo, release e workflow.
- `gh api` que muda algo, também pela URL completa e pelo `api/v3/`.

## Na dúvida sobre o alvo, falha fechado
- ID numérico do repositório (`repositories/<n>`), variável no endpoint ou na URL e reescrita de URL.
- Mutação do GraphQL que comenta, cria ou edita: o ID é global, então vale também no próprio projeto.
