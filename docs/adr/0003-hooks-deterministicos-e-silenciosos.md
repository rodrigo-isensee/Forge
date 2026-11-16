# 0003 - Hooks determinísticos e silenciosos

Estado: vigente. Data: 2026-10-12.
Propósito: garantir as regras de processo por código, sem gastar contexto dos agentes. Público: quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
Regras como o teto de agentes simultâneos, "pesado um por vez" e "PR só com parecer de review e de QA" dependem hoje de o modelo lembrar e obedecer. Quando falham, o custo é alto (máquina travada, PR sem QA). O plugin pode trazer hooks em `hooks/hooks.json`, carregados em todo projeto que usa o Forge. No Claude Code: `PreToolUse` com saída 2 bloqueia a ferramenta e entrega o stderr ao agente; `PostToolUse` com saída 2 mostra o stderr, mas a ferramenta já rodou; com saída 0, o stderr não chega ao agente, e o stdout só vira contexto em eventos como `SessionStart` e `UserPromptSubmit`; os hooks também disparam nas ferramentas dos subagentes, com `agent_id` e `agent_type` na entrada; existem `SubagentStart` e `SubagentStop`.

## Decisão
1. **Silenciosos:** um hook nunca injeta contexto. Sem violação, sai com 0 e sem saída (inclusive em `SessionStart`). Com violação, sai com 2 e uma mensagem curta no stderr (uma linha, até ~200 caracteres), com o ID da regra (ADR 0002) e o que fazer. Nada de `additionalContext`.
2. **Determinísticos:** cada hook é um script Python só com biblioteca padrão, chamado em forma exec (sem shell). Ele lê o JSON do stdin e decide só pelo estado em disco e pelo git local: sem rede, sem IA, sem executar nada vindo da entrada.
3. **Só agem em projeto do Forge:** se não existir `.forge/versao` (ADR 0005) na raiz do projeto, saem com 0. Isso evita bloquear quem só tem o plugin ativo.
4. **Falha interna não bloqueia** (emendado pela ADR 0009, seção 7: `parecer` e `conformidade` falham fechado, só com marcador crítico no comando ou no caminho da ação; no `conformidade`, o marcador vem da política, e o prazo vencido segue o mesmo marcador; no `agentes`, a conferência do R-BRIEF falha fechado): erro inesperado do script sai com 0 e é registrado em `.forge/run/erros.log`. Os hooks são proteção de processo, não fronteira de segurança; a fronteira continua sendo o hook de git, o CI e a proteção de branch.
5. **Estado em `.forge/run/`** na cópia de trabalho principal, resolvida por `git rev-parse --git-common-dir` para que as worktrees somem no mesmo teto. O hook cria `.forge/run/.gitignore` com `*` na primeira escrita. Cada registro tem horário e expira (padrão 2 h), para não travar após uma sessão interrompida.
6. **Limites configuráveis** em `.forge/config.json` do projeto (teto de agentes, lista de comandos pesados); sem o arquivo, valem os padrões de `R-TETO`.
7. **Lista inicial:**

| Hook | Evento e matcher | Bloqueia quando | Regra |
|---|---|---|---|
| Teto de agentes | `PreToolUse` na ferramenta de agentes; contagem por `SubagentStart`/`SubagentStop` | já há o teto de agentes ativos | `R-TETO` |
| Relançamento duplicado | `PreToolUse` na ferramenta de agentes | há agente ativo com o mesmo tipo e a mesma descrição | `R-TETO` |
| Parecer antes de PR e merge | `PreToolUse` em `Bash` com `gh pr create` ou `git merge` | falta parecer de review ou de QA válido para a branch (validado pelo `forge-check`, ADR 0004) | `R-REVIEW`, `R-QA` |
| Pesado um por vez | `PreToolUse` em `Bash` com comando da lista de pesados | outro pesado está ativo (trava com PID vivo) | `R-TETO` |
| Quadro após edição | `PostToolUse` em `Write`/`Edit` de `KANBAN.md` | o quadro viola o formato ou o WIP (`forge-check kanban`) | `R-WIP` |

   Mudança só de documentação passa no hook de parecer, coerente com o portão de QA (documentação não passa por QA): o hook libera quando o diff da branch contra a base só toca arquivos `.md`.
8. **Testes por fixture:** `tests/hooks/<hook>/<caso>.json` traz o JSON de entrada, o estado inicial de `.forge/run/` e o resultado esperado (código de saída e trecho do stderr). Um teste roda cada script com o fixture no stdin num diretório temporário. Todo hook novo entra com pelo menos um caso que passa e um que bloqueia.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| Hooks que injetam lembretes no contexto | Orientam o agente antes do erro | Gastam tokens em toda chamada; viram mais texto a ser ignorado |
| Hooks em shell | Sem Python | Parsing de JSON frágil; o `forge-init` já depende de Python 3 |
| Só instruções nos agentes (hoje) | Zero código | Já falhou na prática (memória esgotada por paralelismo sem teto) |
| Bloquear também em erro interno | Mais rígido | Um bug no hook paralisa todos os projetos de uma vez |

## Consequências
- Mais fácil: as regras críticas valem mesmo quando o modelo esquece; o agente recebe o motivo em uma linha.
- Mais difícil: cada hook é código a manter e testar. O nome exato da ferramenta de agentes no matcher precisa ser conferido na versão do Claude Code usada no CI.
- Riscos: a contagem de agentes erra se `SubagentStop` não disparar (mitigado pela expiração); os padrões de comando pesado podem ser contornados por nomes alternativos. Aceito, porque é guarda de processo, não de segurança.
- Os hooks rodam a cada chamada de ferramenta: precisam terminar em menos de 100 ms no caso comum, sem chamar `git` quando o comando não casa com nenhum padrão.

## Emenda: retomada de sessão com pedido aberto (AQ-4; proposta, vale a partir do PR da fase C do lote-unico-032, L29)
Estado da emenda: **proposta**. Nenhum hook injeta contexto até esse PR; o item 1 segue valendo como está escrito. O que a destrava: o hook `retomada` (L29) com fixtures e o parecer de segurança da classe H11.

**Exceção estreita ao item 1.** Um hook só pode escrever contexto no `SessionStart` (matchers `startup`, `resume` e `compact`) quando o projeto tem pedido aberto, e então escreve **a saída curta do `forge-check proximo <pedido>`**: até 40 linhas, com a hora do registro, para a sessão retomar sem reconstruir o estado. Regras:
1. Sem pedido aberto, silêncio total (o item 1, inalterado).
2. O texto injetado é **dado**: toda linha vinda do pedido sai escapada e truncada (`sem_controle`, `nome_seguro`) e nunca vira instrução literal; o veredito vem do parecer validado, não do Histórico; sem registro, a saída é `não verificável`.
3. O `PreCompact` só **avisa** (stderr, uma linha, item 1) quando há decisão do dono fora do disco; não injeta contexto.
4. O hook continua determinístico (item 2): só estado em disco e git local, sem rede nem IA; falha interna sai com 0 (item 4).
5. Registro velho (hora do registro além do prazo do item 5) sai marcado como velho, nunca omitido.

Critério de reversão da emenda: um caso em que o texto do Histórico, injetado, mude o comportamento da sessão (injeção no contexto), ou mais de 2 retomadas por mês com o estado injetado divergente do pedido.
