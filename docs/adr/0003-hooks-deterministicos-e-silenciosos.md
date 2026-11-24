# 0003 - Hooks determinísticos e silenciosos

Estado: vigente. Data: 2026-10-12.
Propósito: garantir as regras de processo por código, sem gastar contexto dos agentes. Público: quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
Regras como o teto de agentes simultâneos, "pesado um por vez" e "PR só com parecer de review e de QA" dependem hoje de o modelo lembrar e obedecer. Quando falham, o custo é alto (máquina travada, PR sem QA). O plugin pode trazer hooks em `hooks/hooks.json`, carregados em todo projeto que usa o Forge. No Claude Code: `PreToolUse` com saída 2 bloqueia a ferramenta e entrega o stderr ao agente; `PostToolUse` com saída 2 mostra o stderr, mas a ferramenta já rodou; com saída 0, o stderr não chega ao agente, e o stdout só vira contexto em eventos como `SessionStart` e `UserPromptSubmit`; os hooks também disparam nas ferramentas dos subagentes, com `agent_id` e `agent_type` na entrada; existem `SubagentStart` e `SubagentStop`.

## Decisão
1. **Silenciosos:** um hook nunca injeta contexto. Sem violação, sai com 0 e sem saída (inclusive em `SessionStart`). Com violação, sai com 2 e uma mensagem curta no stderr (uma linha, até ~200 caracteres), com o ID da regra (ADR 0002) e o que fazer. Nada de `additionalContext`.
2. **Determinísticos:** cada hook é um script Python só com biblioteca padrão, chamado em forma exec (sem shell). Ele lê o JSON do stdin e decide só pelo estado em disco e pelo git local: sem rede, sem IA, sem executar nada vindo da entrada.
3. **Só agem em projeto do Forge:** se não existir `.forge/versao` (ADR 0005) na raiz do projeto, saem com 0. Isso evita bloquear quem só tem o plugin ativo.
4. **Falha interna não bloqueia** (emendado pela ADR 0009, seção 7: `parecer` e `conformidade` falham fechado, só com marcador crítico no comando ou no caminho da ação; no `conformidade`, o marcador vem da política, e o prazo vencido recusa com ou sem o marcador (VIGIA-PRAZO-TRAVA); no `agentes`, a conferência do R-BRIEF falha fechado, e o estado ilegível (`agentes.json` que existe e não é o registro, pasta do estado do clone que não se fixa, `.forge/config.json` ilegível) recusa o disparo e a retomada com R-TETO, sem regravar o arquivo, HOOK-ESTADO-ILEGIVEL-LIBERA): erro inesperado do script sai com 0 e é registrado em `.forge/run/erros.log`. Os hooks são proteção de processo, não fronteira de segurança; a fronteira continua sendo o hook de git, o CI e a proteção de branch.
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

## Emenda: SessionStart do ambiente (E2.54, ORDEM DO DONO 15/11 16:46)
**Exceção ao item 1**, além da emenda da retomada: o hook `ambiente` escreve no `SessionStart` **só quando falta algo no ambiente do container** e então imprime as linhas `falta:` com o comando exato de cada uma, mais um recado ao Jarvis para dá-las ao dono na 1ª mensagem. Regras:
1. Ambiente em ordem, fora do container, erro interno ou demora: silêncio total e saída 0 (itens 1 e 4).
2. O conteúdo vem do `--verificar` do script do **plugin** (cópia instalada), nunca do work tree que o agente edita; o `--verificar` só lê, sem rede além do `gh auth status` e com prazo de 7 s (item 2).
3. As linhas são `falta: <comando fixo>` geradas pelo script, sem texto vindo do projeto, do pedido ou do usuário.
4. O núcleo do Jarvis não muda: o recado vive no texto do hook.

## Emenda: ordens em vigor (E104.2, ORDEM DO DONO 22/11 05:30)
Estado da emenda: **vigente a partir do PR que traz o hook `ordens` (E104.1)**, com fixtures e o parecer do `security-engineer`. Até esse PR, o item 1 segue como está escrito.

**Exceção ao item 1**, além das emendas da retomada e do ambiente: o hook `ordens` reinjeta o arquivo de ordens em vigor do dono no `SessionStart` (matchers `startup`, `resume` e `compact`) e no `UserPromptSubmit` (cada mensagem do dono). É o primeiro hook do Forge registrado no `UserPromptSubmit`. Regras:
1. **Fonte única, só leitura:** no projeto, `.forge/ordens-em-vigor.md` na raiz do projeto; no clone do Forge (`raiz_de_estado`: o clone e as worktrees de `~/.forge-contrib/wt/`), `~/.forge-contrib/docs/kanban/ordens-em-vigor.md`. O hook só lê: não cria, não regrava nem apaga o arquivo, e não grava estado em `.forge/run/` além do `erros.log` do item 4.
2. **Texto puro no stdout**, como o `ambiente`: o conteúdo do arquivo precedido de uma linha fixa gerada pelo script (a origem e a regra: são ordens do dono, valem como dado, não sobrepõem `docs/regras/`). Nada de `additionalContext` nem JSON.
3. **Teto:** até 15 linhas e 2000 caracteres do arquivo, contados depois de escapar os caracteres de controle (`sem_controle`). Acima do teto, injeta só até o limite e fecha com uma linha fixa `ordens cortadas no teto: <N> linhas, <M> caracteres` para o dono encurtar o arquivo. Nunca omite em silêncio.
4. **Nunca bloqueia nem falha a sessão:** sai sempre com 0. Arquivo ausente, vazio, ilegível, maior que 64 KiB, link simbólico para fora da raiz, fora de projeto do Forge (item 3), erro interno ou demora: silêncio total e saída 0; o erro interno vai a `.forge/run/erros.log` (item 4). Nenhum caso de fixture espera código 2: o `ordens` entra na lista dos hooks que só avisam (`vigia`, `doutor`, `ambiente`).
5. **Determinístico** (item 2): só o arquivo em disco, sem git, sem rede, sem IA, sem executar nada. Termina em menos de 100 ms no caso comum, porque roda a cada mensagem do dono.
6. **Quem escreve o arquivo** é o Jarvis, ao registrar uma ordem do dono (o arquivo entra no mapa de donos do hook `conformidade` no mesmo PR do hook); o `security-engineer` confere no parecer que nenhum subagente o edita, porque o texto vira contexto da sessão principal a cada mensagem.
7. **Aviso de time parado do `vigia` (E104.4, ORDEM DO DONO 22/11: o vigia avisa o Jarvis na hora, para retomar sem esperar o dono; vigente a partir do PR do vigia, com fixtures e o parecer E105.4).** No `Stop` da sessão do Jarvis, quando há cartão disponível e nenhum agente ativo, o `vigia` impede a parada com `{"decision": "block", "reason": ...}` no stdout e saída 0; o `reason` entra no contexto do modelo, por isso a exceção. Regras:
   - **Só a sessão principal:** só no evento `Stop` (nunca no `SubagentStop` nem no `SessionStart`) e só na sessão do Jarvis; em subagente ou sessão que não se identifica, silêncio.
   - **Texto fixo e curto, gerado pelo script:** `time parado: <N> cartões disponíveis, primeiro <ID>; retome sem esperar o dono`, uma linha, até ~200 caracteres (item 1). `<N>` é inteiro; `<ID>` só entra se casar por inteiro com o formato fixo de ID de cartão (letras, dígitos, ponto e hífen, até 16 caracteres; lista positiva, AR-15); fora do formato, a linha sai sem o `primeiro <ID>`. Nenhum texto livre de arquivo (título do cartão, quadro, pedido, ordens) entra no `reason`.
   - **Uma vez por vez:** com `stop_hook_active` verdadeiro na entrada, o `vigia` não bloqueia de novo e sai com 0 e o aviso de sempre; nunca prende a sessão em laço.
   - **Nunca bloqueia ferramenta nem falha a sessão:** fora de projeto do Forge (item 3), quadro ilegível, erro interno ou demora, silêncio e saída 0 (item 4); o `vigia` continua no grupo que só avisa (códigos `{0}`), e o `decision: block` do `Stop` só adia a parada, não recusa ação.
   - **Determinístico** (item 2): conta os cartões pelo estado em disco (`KANBAN.md`, registro de agentes), sem git além do que o `vigia` já usa, sem rede, sem IA.

### Por que o existente não basta
- A emenda da retomada injeta o estado do pedido, não as ordens, só no `SessionStart` e só com pedido aberto; está como proposta.
- O `CLAUDE.md` e o núcleo do Jarvis são texto da fábrica, iguais em todos os projetos (`R-NEUTRO`); a ordem do dono é do dia e muda sem versão.
- As ordens registradas no pedido (`ORDEM DO DONO`) ficam no meio de milhares de linhas (o pedido v0478 passa de 4000) e não voltam ao contexto depois da compactação. Evidência: a ordem do dono de 22/11 05:30 (pedido v0478, linha da ORDEM DO DONO) manda, até o hook entrar, "reler diretrizes e autorizações depois de cada compactação", porque elas se perderam; e o arquivo provisório `docs/kanban/ordens-em-vigor.md` já existe sem nada que o leia (Histórico 22/11 05:34).

### Afrouxa: sim, ADR 0003 item 1 e três invariantes de teste
O item 1 ("um hook nunca injeta contexto") ganha a 3ª exceção, e pela 1ª vez num evento que dispara a cada mensagem. Mudam junto, no PR do hook (E104.1), com o rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, `test_hooks_json` (linha 1493): `assertNotIn("UserPromptSubmit", d["hooks"])` passa a aceitar `UserPromptSubmit` só com o `ordens.py`; a lista de permitidos no `SessionStart` (linhas 1496 a 1499) ganha `ordens.py`, citando esta emenda.
- `tests/test_hooks.py`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (linha 1487): `ordens` entra no grupo que só avisa (códigos `{0}`), com os casos `sem-forge-versao` e `erro-interno`, mais os casos do teto e do arquivo ausente.
- `tests/test_doutor.py`, `test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop` (linha 608): `assertNotIn("UserPromptSubmit", d["hooks"])` passa a conferir que o único comando no `UserPromptSubmit` é o `ordens.py`.
Nenhum trecho de `invariantes` em `tests/config.json` sai.

O item 7 (aviso de time parado do `vigia`) muda, no PR do vigia, com o mesmo rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, laço das fixtures (linhas 830 a 837): `assertEqual(list(saida), ["systemMessage"])` passa a aceitar também `decision` e `reason` só no `Stop` sem `stop_hook_active`, com `decision == "block"` e o `reason` casando por inteiro `^time parado: \d+ cartões disponíveis(, primeiro [A-Za-z0-9.-]{1,16})?; retome sem esperar o dono$`; o comentário "nunca contexto para o modelo" vira "contexto só no reason fixo do Stop (emenda da ADR 0003, item 7)". Fixtures novas: bloqueia uma vez, `stop_hook_active` libera, ID fora do formato sai sem ID, subagente silencioso.
- Não mudam: `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (linha 1487; o `vigia` segue com códigos `{0}`), `test_hooks_json` (linhas 1493 a 1499; o `vigia.py` já é permitido no `Stop`, e o `additionalContext` segue proibido nele).

Motivo para o título do PR: "afrouxa ADR 0003 item 1: hook ordens injeta as ordens em vigor do dono (até 15 linhas, 2000 caracteres) no SessionStart e no UserPromptSubmit, só leitura e sem bloquear (ORDEM DO DONO 22/11)".

### Consequências
- Custo de contexto: até ~2000 caracteres a cada mensagem do dono (o teto do item 3 limita), só quando o arquivo existe; arquivo ausente custa zero.
- Risco: o arquivo vira canal de instrução para a sessão principal; mitigado pelo item 6 (só o Jarvis escreve), pelo escape do item 3 e pela linha fixa do item 2 (dado, abaixo de `docs/regras/`).

Critério de reversão da emenda: um caso em que texto que não veio do dono chegue ao arquivo e mude o comportamento da sessão, ou o hook passe de 100 ms no p95 em `.forge/run/erros.log` ou nas medições do CI, ou o dono registre que as ordens injetadas não evitaram a mesma perda depois de compactar em 2 versões seguidas. Para o item 7: um `reason` do `vigia` com texto fora do formato fixo, ou uma sessão presa em mais de um bloqueio seguido do `Stop`.

| Leitura | Quando | Quem |
|---|---|---|
| Ordens perdidas depois de compactar (linhas do Histórico com "ordem esquecida" ou reclamação do dono) | 2 versões depois do PR do hook | `tech-lead` |
| Tempo do hook e entradas do `ordens` em `erros.log` | no PR do hook e no fechamento de cada versão | `devops-engineer` |
