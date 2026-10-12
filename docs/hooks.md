# O que os hooks do Forge bloqueiam e como ajustá-los?

Propósito: explicar os hooks do plugin, seus limites e como configurá-los num projeto. Público: quem usa ou mantém o Forge. Revisão: 2026-10-12.

Decisão: [ADR 0003](adr/0003-hooks-deterministicos-e-silenciosos.md). Os hooks ficam em `hooks/` (`hooks.json` e um script Python por hook) e valem em todo projeto com o plugin ativo **e** com `.forge/versao`. São silenciosos: sem violação não escrevem nada; com violação saem com código 2 e uma linha com o ID da regra.

## O que cada hook faz

| Hook (script) | Quando roda | Bloqueia quando | Regra |
|---|---|---|---|
| `agentes` | antes da ferramenta de agentes (`Agent`, ou `Task` em versões antigas); `SubagentStart` e `SubagentStop` mantêm a contagem | os agentes ativos já somam `teto_agentes`, ou já há um ativo com o mesmo tipo e a mesma descrição | `R-TETO` |
| `parecer` | antes de `gh pr create`, e de `git merge <branch>` feito numa branch de integração (`develop`, `homolog`, `main`, `master`) | a branch não tem parecer de review e de QA aprovado e válido para o commit atual (`forge-check pr`) | `R-REVIEW`, `R-QA` |
| `pesado` | antes e depois de comandos `Bash` com um comando simples que começa com um item de `pesados` | outra sessão, worktree ou subagente tem tarefa pesada ativa (trava com PID vivo, há menos de 10 minutos) | `R-TETO` |
| `quadro` | depois de `Write`/`Edit` do `KANBAN.md` da raiz | o quadro fere o formato ou o WIP (`forge-check kanban`); a edição já foi feita, o agente recebe o motivo | `R-WIP` |

O `parecer` libera: diff só de `.md` contra a base (documentação não passa por QA), PR ou merge entre branches de integração (promoção) e `git merge` que atualiza uma branch de trabalho. O parecer é achado pelo campo `branch:` dos documentos em `docs/reviews/` e `docs/qa/`; num `git merge`, eles são lidos da própria branch a mesclar.

## Estado e expiração
O estado fica em `.forge/run/` da cópia de trabalho principal (as worktrees somam no mesmo teto), com `.gitignore` próprio: `agentes.json`, `pesado.json` e `erros.log`. Todo registro expira em `expiracao_horas` (padrão 2), para uma sessão interrompida não travar o projeto; uma reserva de agente que nunca começou expira em 5 minutos e a trava de tarefa pesada, em 10 minutos (sem o `PostToolUse`, como na permissão negada, ela não prende as outras sessões). A trava nunca bloqueia a própria sessão e o próprio agente. Para liberar na hora, apague `.forge/run/pesado.json`. Erro interno de um hook nunca bloqueia: ele libera e grava uma linha em `erros.log`.

## Ajustar num projeto (`.forge/config.json`)

```json
{
  "teto_agentes": 3,
  "pesados": ["playwright", "docker compose up", "pytest -m integration"],
  "expiracao_horas": 2,
  "hooks_desligados": []
}
```

- `teto_agentes`: agentes ativos ao mesmo tempo, somando todas as sessões do projeto.
- `pesados`: início de comando (sem diferença de maiúsculas e espaços) tratado como tarefa pesada; substitui a lista padrão. Vale em qualquer comando simples da linha (`cd web && ...`), depois de variáveis e de lançadores (`sudo`, `env`, `npx`, `<gerenciador> exec|run|dlx`); só citar a ferramenta (`grep ferramenta`, instalar o pacote) não conta.
- `expiracao_horas`: validade dos registros.
- `hooks_desligados`: nomes dos hooks a desligar (`agentes`, `parecer`, `pesado`, `quadro`). É o jeito recomendado de desligar um hook; apagar `.forge/versao` desliga todos e quebra o `forge-upgrade`.

Chave ausente ou com valor inválido usa o padrão do modelo de projeto (`templates/projeto/.forge/config.json`).

## Limites conhecidos
- Guarda de processo, não de segurança: comando pesado com outro nome, `gh pr merge` e merges feitos fora do `Bash` do Claude Code passam. A fronteira continua sendo o hook de git, o CI e a proteção de branch.
- Tarefa pesada em segundo plano (`run_in_background`) solta a trava quando o comando é disparado, não quando termina; a que passa de 10 minutos deixa de travar as outras sessões.
- Se o `SubagentStop` não chegar, a vaga só volta quando o registro expira.

## Testar
Cada caso é um fixture em `tests/hooks/<hook>/<caso>.json` (entrada, estado inicial, código e trecho do stderr esperados), rodado por `tests/test_hooks.py`.
