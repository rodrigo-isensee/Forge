# O que os hooks do Forge bloqueiam e como ajustá-los?

Propósito: explicar os hooks do plugin, seus limites e como configurá-los num projeto. Público: quem usa ou mantém o Forge. Revisão: 2026-10-12.

Decisão: [ADR 0003](adr/0003-hooks-deterministicos-e-silenciosos.md). Os hooks ficam em `hooks/` (`hooks.json` e um script Python por hook) e valem em todo projeto com o plugin ativo **e** com `.forge/versao`. São silenciosos: sem violação não escrevem nada; com violação saem com código 2 e uma linha com o ID da regra.

## O que cada hook faz

| Hook (script) | Quando roda | Bloqueia quando | Regra |
|---|---|---|---|
| `agentes` | antes da ferramenta de agentes (`Agent`, ou `Task` em versões antigas); `SubagentStart` e `SubagentStop` mantêm a contagem | os agentes ativos já somam o teto (`R-TETO`), ou já há um ativo com o mesmo tipo e a mesma descrição | `R-TETO` |
| `parecer` | antes de `gh pr create`, e de `git merge <branch>` ou `git pull <remoto> <branch>` feito numa branch de integração (`develop`, `homolog`, `main`, `master`); a branch atual acompanha `cd`, `git checkout` e `git switch` anteriores na mesma linha | a branch não tem parecer de review e de QA aprovado e válido para o commit atual (`forge-check pr`) | `R-REVIEW`, `R-QA` |
| `pesado` | antes e depois de comandos `Bash` com um comando simples que começa com um item de `pesados` | outra sessão, worktree ou subagente tem tarefa pesada ativa (trava com PID vivo, há menos de 10 minutos) | `R-TETO` |
| `quadro` | depois de `Write`/`Edit` do `KANBAN.md` da raiz | o quadro fere o formato ou o WIP (`forge-check kanban`); a edição já foi feita, o agente recebe o motivo | `R-WIP` |

O `parecer` libera: diff só de `.md` contra a base (documentação não passa por QA), PR ou merge entre branches de integração (promoção) e `git merge` que atualiza uma branch de trabalho. O parecer é achado pelo campo `branch:` dos documentos em `docs/reviews/` e `docs/qa/`; num `git merge`, eles são lidos da própria branch a mesclar.

No CI do Forge, o job `pareceres` segue a mesma ideia: o parecer é exigido na entrada de cada PR na `develop`; os PRs de promoção (`develop` → `homolog` e `homolog` → `main`) ficam fora dele, porque já passaram por esse portão e pelas baterias da `homolog` (ADR 0008, seção 3).

## Estado e expiração
O estado fica em `.forge/run/` da cópia de trabalho principal (as worktrees somam no mesmo teto), com `.gitignore` próprio: `agentes.json`, `pesado.json` e `erros.log`. Todo registro expira em `expiracao_horas` (padrão 2), para uma sessão interrompida não travar o projeto; uma reserva de agente que nunca começou expira em 5 minutos e a trava de tarefa pesada, em 10 minutos (sem o `PostToolUse`, como na permissão negada, ela não prende as outras sessões). A trava nunca bloqueia a própria sessão e o próprio agente. Para liberar na hora, apague `.forge/run/pesado.json`. Erro interno de um hook nunca bloqueia: ele libera e grava uma linha em `erros.log`.

## Ajustar num projeto (`.forge/config.json`)

```json
{
  "teto_maximo": 5,
  "pesados": ["minha-ferramenta-pesada", "outro comando --suite lenta"],
  "expiracao_horas": 2,
  "hooks_desligados": []
}
```

- Teto de agentes ativos ao mesmo tempo (somando todas as sessões do projeto): por padrão é adaptativo e segue as faixas de `R-TETO` (2 a 5, pelo load de `/proc/loadavg` e pela `MemAvailable` de `/proc/meminfo`; sem leitura, 3). O bloqueio informa o load e a memória medidos.
- `teto_agentes`: fixa o teto e sobrepõe o adaptativo (o `3` que o modelo da 0.5.0 gravava é removido pela migração 0.7.0 do `forge-upgrade`; um `3` escrito depois dela é respeitado como escolha do projeto).
- `teto_maximo`: limita o teto adaptativo (não afeta o `teto_agentes` fixo).
- `pesados`: início de comando (sem diferença de maiúsculas e espaços) tratado como tarefa pesada. O `forge-init` grava a lista padrão da stack (`stacks/<stack>/pesados.json`) ao criar o arquivo; o núcleo não traz lista, e sem `pesados` nenhum comando conta como pesado. Vale em qualquer comando simples da linha (`cd web && ...`), depois de variáveis e de lançadores (`sudo`, `env`, `npx`, `<gerenciador> exec|run|dlx`); só citar a ferramenta (`grep ferramenta`, instalar o pacote) não conta.
- `expiracao_horas`: validade dos registros.
- `hooks_desligados`: nomes dos hooks a desligar (`agentes`, `parecer`, `pesado`, `quadro`). É o jeito recomendado de desligar um hook; apagar `.forge/versao` desliga todos e quebra o `forge-upgrade`.

Chave ausente ou com valor inválido usa o padrão do modelo de projeto (`templates/projeto/.forge/config.json`).

## Limites conhecidos
- Guarda de processo, não de segurança: comando pesado com outro nome, `gh pr merge` e merges feitos fora do `Bash` do Claude Code passam. A fronteira continua sendo o hook de git, o CI e a proteção de branch.
- O `parecer` lê só a linha de comando: merge dentro de `bash -c`, `eval`, script, alias ou função, `git pull` sem branch explícita (usa o upstream) e `git checkout -` seguido de merge passam.
- O `parecer` só confere o que existe localmente: `git pull <remoto> <branch>` de uma branch que ainda não foi buscada (sem `refs/remotes/<remoto>/<branch>`) libera, porque não há o que validar; rode `git fetch` antes para o portão valer.
- `git rebase <branch>`, `git reset --hard <branch>` e `git cherry-pick` na branch de integração não passam pelo `parecer`. Ficaram de fora de propósito: o alvo do `cherry-pick` é um commit, sem parecer próprio, e tratá-lo como merge bloquearia correções legítimas (falso bloqueio); `rebase` e `reset` têm formas demais (`--onto`, `-i`, `HEAD~n`) para tratar sem risco. A fronteira continua sendo o `pre-push`, o CI e a proteção de branch.
- A trava de tarefa pesada não bloqueia a própria sessão: ela pode disparar várias tarefas pesadas em paralelo (por exemplo, duas em segundo plano). Cada início sobrescreve a trava com o comando mais recente, e o fim do último a solta enquanto um anterior ainda roda. Dentro de uma sessão, o `R-TETO` é responsabilidade do agente.
- Negação interativa: quando o usuário nega a permissão de um comando pesado no diálogo, não chega `PermissionDenied` (esse evento cobre só a negação do modo automático) nem `PostToolUse`. A trava fica sem par e só é contida pelos 10 minutos e pela regra da mesma sessão; para liberar na hora, apague `.forge/run/pesado.json`.
- Tarefa pesada em segundo plano (`run_in_background`) solta a trava quando o comando é disparado, não quando termina; a que passa de 10 minutos deixa de travar as outras sessões.
- Se o `SubagentStop` não chegar, a vaga só volta quando o registro expira.

## Formato e fontes
`hooks/hooks.json` é carregado pelo Claude Code sem declaração no `plugin.json`. Cada hook usa a forma exec (`command` + `args`, sem shell; `${CLAUDE_PLUGIN_ROOT}` é expandido em cada item de `args`) e `timeout` de 10 s (o padrão seria 600 s). O que os hooks usam está na documentação oficial: matcher `Agent|Task` (só letras e `|`: nomes exatos), eventos `PostToolUseFailure`, `PermissionDenied` (negação no modo automático, com `tool_use_id`), `SubagentStart`/`SubagentStop` com `agent_id` e `agent_type`, `agent_id` também nos eventos de ferramenta dentro de um subagente e saída 2 que bloqueia no `PreToolUse`. Fontes: [hooks](https://code.claude.com/docs/en/hooks.md) e [referência do manifesto](https://code.claude.com/docs/en/plugins/manifest-reference.md), consultadas em 2026-10-12.

## Testar
Cada caso é um fixture em `tests/hooks/<hook>/<caso>.json` (entrada, estado inicial, código e trecho do stderr esperados), rodado por `tests/test_hooks.py`.
