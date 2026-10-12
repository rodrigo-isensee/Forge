---
tipo: review
contrato: 1
pedido: release-0.5.0
branch: develop
commit: 0c19c90
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-12
---
# Code review: release 0.5.0 (origin/main 0.2.1 até develop 0c19c90)

Escopo: os commits 7a62cf0..0c19c90 (ADRs 0001-0007), com prioridade para o código que roda nos projetos: `hooks/`, `bin/forge-check`, `bin/forge-upgrade`, `bin/forge-init`, `migrations/0.5.0/`, `scripts/`, os dois `pre-push`, `.github/workflows/` e `.claude-plugin/plugin.json`. Leitura do código, mais execução local dos hooks `parecer` e `pesado` num repositório temporário e `claude plugin validate --strict` (verde).

Parecer: **aprovado**. Não há achado crítico nem alto. Os achados médios devem virar cartão de correção na próxima versão; nenhum deles trava um projeto de forma permanente nem fere `R-MAIN`.

## O que está correto
- **Hooks:** forma exec, sem shell; nada da entrada é executado. O `shlex` só serve para separar palavras. `bloquear` usa `SystemExit` e fica fora do `except Exception`, e erro interno libera e vai para `erros.log` com rotação. Os hooks só agem com `.forge/versao`, então projetos atuais não mudam nada sem migrar. O caminho comum não chama `git`.
- **Injeção em git:** refs que começam com `-` são descartadas no `merge`, e `--base`/`--head` só seguem adiante depois de `rev-parse --verify`. Testei `gh pr create --base '--output=<arquivo>'` e nenhum arquivo foi criado. O `commit` do frontmatter passa pelo regex hexadecimal antes de chegar ao git.
- **Migração:** a 0.5.0 é idempotente e só acrescenta: não sobrescreve `.forge/*` e só acrescenta linha ao `.gitignore`. O `forge-upgrade` recusa cópia suja e base `main`/`master`/HEAD solto, trabalha numa branch `forge/upgrade-<versão>` e nunca faz push nem merge.
- **CI:** ações fixadas por SHA, `permissions: contents: read` em `ci.yml`, sem `pull_request_target`, sem segredo e sem `ANTHROPIC_API_KEY`, ou seja, custo zero (`R-CUSTO`). O `e2e` isola o `HOME`, então não há credencial e não há chamada paga.
- **Compatibilidade:** os nomes `forge:node-backend` e `forge:react-frontend` continuam valendo, e o teste confere a lista de `agents` do manifesto.

## Achados

### Crítico
Nenhum.

### Alto
Nenhum.

### Médio
1. `hooks/pesado.py:296-307`: a trava fica presa à própria sessão quando o `PostToolUse` não chega. Isso acontece quando o usuário nega a permissão do comando pesado ou quando outro hook `PreToolUse` o bloqueia. Reproduzido: depois de um `PreToolUse` sem o par `Post`, o próximo comando pesado da **mesma** sessão é bloqueado, e até `grep -r playwright package.json` é barrado, por até `expiracao_horas` (2 h). A mensagem não diz como sair. Sugestão: não bloquear quando a trava é do mesmo PID de sessão (a guarda serve entre sessões e worktrees), ou dar prazo curto à trava sem `Post`, como já existe para a reserva de agente. Em último caso, incluir na mensagem "apague `.forge/run/pesado.json`" ou citar `hooks_desligados`.
2. `hooks/parecer.py:202-205`: o merge na integração escapa do hook quando o checkout vem na mesma linha. O hook confere a branch atual **antes** do comando, então `git checkout develop && git merge feature/x`, rodado a partir da `feature/x`, passa sem parecer (reproduzido: exit 0). `git pull <remoto> <branch>` na `develop` também passa. Sugestão: acompanhar `git checkout`/`git switch` nos segmentos, como o `cd` já é acompanhado (o `reduzir_comando` do forge-check já faz isso para transcrições), e tratar `git pull` com ref explícita como merge. Registrar o caso em `docs/hooks.md`, "Limites conhecidos".
3. `migrations/0.5.0/migrar` contra a ADR 0004, "Consequências": a ADR diz que a migração dá frontmatter mínimo ou `contrato: 0` aos documentos antigos, e ela não faz isso. Num projeto migrado, `forge-check docs` acusa "sem frontmatter" em todo review e QA antigo e quebra o "pronto" de quem o usar. Hook e `pr` não são afetados, porque ignoram documentos sem frontmatter. Sugestão: nova migração (ou ajuste antes da release) que acrescente `---\ncontrato: 0\n---` só a arquivos de `docs/reviews/`, `docs/qa/` e `docs/architecture/features/` sem frontmatter, sem mexer no resto. Outra saída é registrar a divergência na ADR.
4. `hooks/hooks.json` (todas as entradas): nenhum teste exercita o formato exec (`command` + `args`) nem a expansão de `${CLAUDE_PLUGIN_ROOT}` dentro de `args` no Claude Code real. Os testes rodam os scripts direto, e o `validate --strict` passou mas não prova a execução. Se a versão do CLI não aceitar `args`, os hooks ficam inertes, sem bloquear nada (falham abertos). Sugestão: antes do merge na `main`, conferência manual numa sessão de projeto com `.forge/versao`: lançar um agente e ver `.forge/run/agentes.json` ser criado. Registrar o resultado no PR.

### Baixo
5. `bin/forge-check:192-194`: o `git` não tem `timeout` nem limpa `GIT_*`, ao contrário do `git` de `hooks/_comum.py:148-152`, que ele substitui quando carregado pelos hooks (`pedidos_da_branch`, `cmd_pr`). Se o git demorar, o limite de 10 s do Claude Code corta o hook. Sugestão: mesmo `timeout` e mesmo ambiente limpo, de preferência numa função só.
6. `bin/forge-init:81`: grava `.forge/versao` com a versão atual sempre que o arquivo falta. Rodar o `forge-init` de novo num projeto antigo marca o projeto como atualizado e esconde migrações futuras que alterem arquivos existentes. Hoje não faz diferença, porque a 0.5.0 faz o mesmo que o init. Sugestão: em projeto que já tem `CLAUDE.md` ou `KANBAN.md` e não tem `.forge/versao`, gravar `0.0.0` ou mandar rodar `forge-upgrade`.
7. `hooks/pesado.py:289-290`: o casamento por substring pega comandos leves que só mencionam a ferramenta (`npm i -D @playwright/test`, `grep playwright`) e eles passam a disputar a trava. Sugestão: casar no início de um segmento do comando.
8. `bin/forge-check` (`main`): `--raiz` só é aceito antes do subcomando, e `forge-check docs --raiz X` falha com erro do argparse. Por isso a conferência deste parecer rodou com `forge-check --raiz /home/rodrigoisensee/Forge docs`. Sugestão: aceitar `--raiz` também nos subparsers. A ADR 0005 prevê ainda que o `forge-check` avise de migração pendente; isso não foi implementado.
9. `bin/forge-check:424-428`: em `transcricao verificar`, uma linha inválida ou sem `ev` gera traceback em vez de violação legível. No `anonimizar`, o campo `t` copia o `timestamp` sem validar o formato. Sugestão: validar ISO 8601 e tratar linha malformada como violação.
10. `migrations/0.5.0/migrar:21-24`: regrava o `.gitignore` inteiro, normalizando CRLF para LF e o fim de arquivo. Não apaga conteúdo, mas pode gerar diff grande. Sugestão: só acrescentar (`open(..., "a")`) com quebra de linha prévia, se faltar.
11. `docs/regras/README.md:11-14`: `R-WIP`, `R-TETO`, `R-QA` e `R-REVIEW` aparecem como "Verificada por: revisão", mas agora também são verificadas por hook. Sugestão: atualizar a coluna e o `verificada_por` das páginas.
12. `templates/projeto/.forge/config.json:3` e `hooks/_comum.py:134`: os padrões de `pesados` citam ferramentas específicas (`playwright`, `pytest`) no núcleo. Isso é aceitável como exemplo neutro de "comando pesado", mas pela ADR 0001 o lugar mais coerente seria o `pronto.md` de cada stack. Sugestão: deixar a lista padrão vir do pacote da stack no `forge-init`.
13. `.github/workflows/release.yml:9`: `contents: write` com `persist-credentials` padrão enquanto os testes rodam. Roda só na `main`, com código já revisado, mas `persist-credentials: false` no checkout custa pouco.
