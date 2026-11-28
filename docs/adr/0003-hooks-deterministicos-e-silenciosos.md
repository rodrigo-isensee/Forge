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
1. **Fonte única, só leitura:** no projeto, `.forge/ordens/ordens-em-vigor.md` na raiz da cópia principal, numa pasta própria (o curinga no nome, `ordens-em-vigo?.md`, não escapa da pasta guardada como pasta), achada pela pasta comum do git lida do disco (`diretorio_comum`; a worktree, que o dev grava, nunca é fonte, e o `.git` que não se resolve cala); o modelo de projeto não traz o arquivo (ausente custa zero), o `forge-init` põe a pasta `.forge/ordens/` nos ignorados (um commit de branch não chega à cópia do Jarvis pelo merge), e o Jarvis o cria na 1.ª ordem; no clone do Forge (`raiz_de_estado`: o clone e as worktrees de `~/.forge-contrib/wt/`), `~/.forge-contrib/docs/ordens/ordens-em-vigor.md`, numa pasta própria com a base em `docs/ordens/` (a pasta trocada por link sai da base). O hook só lê: não cria, não regrava nem apaga o arquivo, e não grava estado em `.forge/run/` além do `erros.log` do item 4.
2. **Texto puro no stdout**, como o `ambiente`: o conteúdo do arquivo precedido de uma linha fixa gerada pelo script (a origem e a regra: são ordens do dono, valem como dado, não sobrepõem `docs/regras/`). Nada de `additionalContext` nem JSON.
3. **Teto:** até 15 linhas e 2000 caracteres do arquivo, contados depois de escapar os caracteres de controle (`sem_controle`). Acima do teto, injeta só até o limite e fecha com uma linha fixa `ordens cortadas no teto: <N> linhas, <M> caracteres` para o dono encurtar o arquivo. Nunca omite em silêncio. Na gravação (RECIBO-CONTADOR-PELO-HOOK, item 4; v0481 E20.11), o hook `ordens_teto` recusa com saída 2 o Write, o Edit e o MultiEdit que deixariam o arquivo acima do mesmo teto, contado pelas mesmas funções do `ordens` (o Edit com trecho vazio em arquivo ausente ou vazio conta o texto novo, como a ferramenta o cria); com o arquivo já acima do teto, a gravação que não cresce linhas nem caracteres passa, para a correção aos poucos; a gravação pelo Bash fica fora (o `conformidade` já a reserva ao Jarvis), e o corte com aviso segue como rede.
4. **Nunca bloqueia nem falha a sessão:** sai sempre com 0. Arquivo ausente, vazio, ilegível, maior que 64 KiB, link simbólico para fora da raiz, fora de projeto do Forge (item 3), erro interno ou demora: silêncio total e saída 0; o erro interno vai a `.forge/run/erros.log` (item 4). Nenhum caso de fixture espera código 2: o `ordens` entra na lista dos hooks que só avisam (`vigia`, `doutor`, `ambiente`).
5. **Determinístico** (item 2): só o arquivo em disco, sem git, sem rede, sem IA, sem executar nada. Termina em menos de 100 ms no caso comum, porque roda a cada mensagem do dono.
6. **Quem escreve o arquivo** é o Jarvis, ao registrar uma ordem do dono (no projeto, a pasta `.forge/ordens/` entra como pasta no mapa de donos do hook `conformidade` no mesmo PR do hook, casada também relativa à cópia principal, porque o dev grava de dentro da worktree; na sessão do Forge, a pasta `docs/ordens/` entra como pasta nas listas do controle `CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO`, como o pedido e o brief); o `security-engineer` confere no parecer que nenhum subagente o edita, porque o texto vira contexto da sessão principal a cada mensagem.
7. **Aviso de time parado do `vigia` (E104.4, ORDEM DO DONO 22/11: o vigia avisa o Jarvis na hora, para retomar sem esperar o dono; vigente a partir do PR do vigia, com fixtures e o parecer E105.4).** No `Stop` da sessão do Jarvis, quando há cartão disponível e nenhum agente ativo, ou, com agente rodando ou não (F4, v0481 E34.6), PR aberto sem agente vigente na branch dele com vaga no teto do R-TETO ou agente da sessão preso há mais de 10 min, o `vigia` impede a parada com `{"decision": "block", "reason": ...}` no stdout e saída 0; o `reason` entra no contexto do modelo, por isso a exceção. Regras:
   - **Só a sessão principal:** só no evento `Stop` (nunca no `SubagentStop` nem no `SessionStart`) e só na sessão do Jarvis; em subagente ou sessão que não se identifica, silêncio.
   - **Texto fixo e curto, gerado pelo script:** `time parado: <partes>; retome sem esperar o dono`, uma linha, com teto de 280 caracteres (item 1; acima dele, a última parte sai inteira e o sufixo fica). As partes, nesta ordem e separadas por `; `: `<N> cartões disponíveis, primeiro <ID>`; `PR sem agente: #<n> <papel>` (até 3 PRs, em ordem de número, e ` e mais <M>`); `preso há mais de 10 min: <tipo> <id> há <n> min` (1 agente, e ` e mais <M>`). `<papel>` sai de uma lista fixa (autor, integração e as junções de review, QA e segurança); `<tipo>` casa `[a-z][a-z0-9:-]` e é cortado em 24 caracteres; `<id>`, o formato do id de agente. `<N>` é inteiro; `<ID>` só entra se casar por inteiro com o formato fixo de ID de cartão (letras, dígitos, ponto e hífen, até 16 caracteres; lista positiva, AR-15); fora do formato, a linha sai sem o `primeiro <ID>`. Nenhum texto livre de arquivo (título do cartão, quadro, pedido, ordens) entra no `reason`.
   - **Uma vez por vez:** com `stop_hook_active` verdadeiro na entrada, o `vigia` não bloqueia de novo e sai com 0 e o aviso de sempre; nunca prende a sessão em laço.
   - **Nunca bloqueia ferramenta nem falha a sessão:** fora de projeto do Forge (item 3), quadro ilegível, erro interno ou demora, silêncio e saída 0 (item 4); o `vigia` continua no grupo que só avisa (códigos `{0}`), e o `decision: block` do `Stop` só adia a parada, não recusa ação.
   - **Determinístico** (item 2): conta pelo estado em disco (`KANBAN.md`, registro de agentes, transcript do agente e a lista `prs-abertos.json`), sem git além do que o `vigia` já usa, sem rede, sem IA. A lista é gravada fora do hook pelo `forge-check status` (sempre) e pelo `proximo` (vencida), ao lado do `agentes.json` (item 5), com o papel calculado por quem grava; o PR de fork (`isCrossRepository` verdadeiro ou ausente), o que espera só o dono (base `main`, rótulo) e o que espera o CI ficam fora. O `vigia` a lê com a guarda do quadro, só com `gravado_em` de até 15 min (e não mais de 60 s no futuro), e revalida cada item por lista positiva; ausente, vencida ou fora da forma, a parte dos PRs cala.

### Por que o existente não basta
- A emenda da retomada injeta o estado do pedido, não as ordens, só no `SessionStart` e só com pedido aberto; está como proposta.
- O `CLAUDE.md` e o núcleo do Jarvis são texto da fábrica, iguais em todos os projetos (`R-NEUTRO`); a ordem do dono é do dia e muda sem versão.
- As ordens registradas no pedido (`ORDEM DO DONO`) ficam no meio de milhares de linhas (o pedido v0478 passa de 4000) e não voltam ao contexto depois da compactação. Evidência: a ordem do dono de 22/11 05:30 (pedido v0478, linha da ORDEM DO DONO) manda, até o hook entrar, "reler diretrizes e autorizações depois de cada compactação", porque elas se perderam; e o arquivo provisório `docs/kanban/ordens-em-vigor.md` já existe sem nada que o leia (Histórico 22/11 05:34).

### Afrouxa: sim, ADR 0003 item 1 e três invariantes de teste
O item 1 ("um hook nunca injeta contexto") ganha a 3ª exceção, e pela 1ª vez num evento que dispara a cada mensagem. Mudam junto, no PR do hook (E104.1), com o rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, `test_hooks_json` (linha 1493): `assertNotIn("UserPromptSubmit", d["hooks"])` passa a aceitar `UserPromptSubmit` só com o `ordens.py`; a lista de permitidos no `SessionStart` (linhas 1496 a 1499) ganha `ordens.py`, citando esta emenda.
- `tests/test_hooks.py`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (linha 1487): `ordens` entra no grupo que só avisa (códigos `{0}`), com os casos `sem-forge-versao` e `erro-interno`, mais os casos do teto e do arquivo ausente.
- `tests/test_doutor.py`, `test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop` (linha 608): `assertNotIn("UserPromptSubmit", d["hooks"])` passa a conferir que o único comando no `UserPromptSubmit` é o `ordens.py`.
- `tests/test_hooks.py`, laço das fixtures: o ramo `contexto` aceita stdout só para o `ordens`, que começa pela linha fixa e é igual ao texto esperado da fixture; os outros hooks seguem sem stdout (A2 do review E123.4).
Nenhum trecho de `invariantes` em `tests/config.json` sai.

O item 7 (aviso de time parado do `vigia`) muda, no PR do vigia, com o mesmo rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, laço das fixtures (linhas 830 a 837): `assertEqual(list(saida), ["systemMessage"])` passa a aceitar também `decision` e `reason` só no `Stop` sem `stop_hook_active`, com `decision == "block"` e o `reason` casando por inteiro `^time parado: \d+ cartões disponíveis(, primeiro [A-Za-z0-9.-]{1,16})?; retome sem esperar o dono$`; o comentário "nunca contexto para o modelo" vira "contexto só no reason fixo do Stop (emenda da ADR 0003, item 7)". Fixtures novas: bloqueia uma vez, `stop_hook_active` libera, ID fora do formato sai sem ID, subagente silencioso.
- Não mudam: `test_cada_hook_tem_caso_que_passa_e_que_bloqueia` (linha 1487; o `vigia` segue com códigos `{0}`), `test_hooks_json` (linhas 1493 a 1499; o `vigia.py` já é permitido no `Stop`, e o `additionalContext` segue proibido nele).

O item 7 muda de novo no PR do F4 (v0481 E34.6, #931), com o rótulo `afrouxa-regra`: o aviso passa a contar PR aberto sem agente e agente preso também com agente rodando, e o `reason` ganha as duas partes novas com teto de 280 (antes ~200). Em `tests/test_hooks.py`, a regex do laço das fixtures casa as três partes e confere `len <= 280`. O item 2 (sem rede) não muda: o hook lê a lista em disco; quem chama o `gh` é o `forge-check`. Reversão do F4: mais de 2 casos numa semana de PR parado que o aviso não viu por lista vencida sem `proximo` nem `status` no intervalo (aí outras ferramentas do Jarvis passam a renovar a lista; nenhum hook).

Motivo para o título do PR: "afrouxa ADR 0003 item 1: hook ordens injeta as ordens em vigor do dono (até 15 linhas, 2000 caracteres) no SessionStart e no UserPromptSubmit, só leitura e sem bloquear (ORDEM DO DONO 22/11)".

### Consequências
- Custo de contexto: até ~2000 caracteres a cada mensagem do dono (o teto do item 3 limita), só quando o arquivo existe; arquivo ausente custa zero.
- Risco: o arquivo vira canal de instrução para a sessão principal; mitigado pelo item 6 (só o Jarvis escreve), pelo escape do item 3 e pela linha fixa do item 2 (dado, abaixo de `docs/regras/`).

Critério de reversão da emenda: um caso em que texto que não veio do dono chegue ao arquivo e mude o comportamento da sessão, ou o hook passe de 100 ms no p95 em `.forge/run/erros.log` ou nas medições do CI, ou o dono registre que as ordens injetadas não evitaram a mesma perda depois de compactar em 2 versões seguidas. Para o item 7: um `reason` do `vigia` com texto fora do formato fixo, ou uma sessão presa em mais de um bloqueio seguido do `Stop`.

| Leitura | Quando | Quem |
|---|---|---|
| Ordens perdidas depois de compactar (linhas do Histórico com "ordem esquecida" ou reclamação do dono) | 2 versões depois do PR do hook | `tech-lead` |
| Tempo do hook e entradas do `ordens` em `erros.log` | no PR do hook e no fechamento de cada versão | `devops-engineer` |

## Emenda: salvar ao parar (D6-SESSAO-NAO-PERDE, parte a; v0481 E11.2, ORDEM DO DONO 24/11)
Estado da emenda: **vigente a partir do PR que traz o hook `salvar`**, com fixtures, mutantes e o parecer do `security-engineer`. O item 2 segue valendo sem exceção (DECISÃO DO DONO de 25/11, opção b do #877): o hook só usa o git local, sem rede.

O hook `salvar`, só no `SubagentStop`: ao parar, o trabalho em andamento do agente é gravado num commit WIP na cópia local dele, na branch do brief, sem envio; o envio, com o `pre-push` e a varredura de segredo dele, fica com o fechamento (`bin/forge-fechar`) ou com o próximo envio do autor. Regras:
1. **Só o que o brief diz:** o prompt do agente (primeiro registro `user` do transcrito dele) cita exatamente um brief de escrita em `docs/briefs/` (os de review, segurança e QA não escrevem a branch); dele saem a `Branch:`, o escopo (linha `- arquivos:`, caminho exato ou pasta com `/`) e a cópia citada, dentro da pasta das cópias (`~/.forge-contrib/wt/` no Forge, `<projeto>/.forge/wt/` no projeto) e nessa branch. Qualquer falta ou ambiguidade: nada acontece.
2. **Só o escopo:** o commit leva só os arquivos rastreados mudados fora de commit dentro do escopo (`git commit --only`); arquivo não rastreado fica de fora (o agente não o escolheu), e o resto da cópia fica como está. Sem nada no escopo, nem commit.
3. **Sem rede:** nem `push`, nem `fetch`, nem `ls-remote`; o commit fica só na cópia, nunca em `main`, `master`, `develop` ou `homolog` (`R-MAIN`, `R-FLUXO`). Como nada sai da cópia, nenhum run de CI é gasto (`R-CUSTO`) e o segredo que o agente tenha gravado é barrado pelo `pre-push` no envio de sempre. Prazo total de 50 s para todos os comandos, descontado a cada chamada, dentro dos 60 s do hook no `hooks.json`; esgotado, o comando para e a linha vai ao `erros.log`.
4. **Sem código do agente fora do sandbox:** o hook roda fora do sandbox, e os hooks do git da cópia (o `.git/hooks/` e o `.githooks/` versionado) são código que o agente escreve; o git do `salvar` roda com `core.hooksPath` vazio, sem `core.fsmonitor`, com `--literal-pathspecs`, sem as `GIT_*` herdadas (nem `GIT_CONFIG_*`) nem `XDG_CONFIG_HOME`, e sem pedir senha: a config global e a de sistema são as do dono. O `.git/config` da cópia também é do agente (o sandbox o deixa gravar nas cópias): antes de qualquer outro git nela, o hook lê a config local sem includes (ler não executa nada) e não age se houver chave fora da lista positiva (`core.repositoryformatversion`, `core.filemode`, `core.bare`, `core.logallrefupdates`, `core.ignorecase`, `core.precomposeunicode`, `core.symlinks`, `extensions.objectformat`, `remote.origin.url`, `remote.origin.fetch`, `branch.<nome>.remote`, `branch.<nome>.merge`, `user.name`, `user.email`) ou `remote.origin.url` diferente da cópia principal; assim filtro, `core.sshCommand`, `gpg.program`, `credential.helper`, `remote.origin.receivepack`, `pushurl`, `insteadOf` e `include` não chegam ao git deste hook. A guarda das branches de integração está no próprio hook (regra 3); o `pre-push` roda inteiro no envio, fora deste hook, e o CI do PR continua o portão. Não é o `--no-verify` de um agente: o agente não escolhe nada disso; o `pre-commit` do projeto (lint, por exemplo) não roda no commit WIP, e o `pre-push` e o CI o cobrem.
5. **Não mexe em operação pela metade:** conflito no índice, mesclagem, rebase, cherry-pick ou revert em andamento: nada acontece.
6. **Nunca bloqueia nem escreve no stdout:** sai sempre com 0; o resultado vai a `.forge/run/salvar.log` (branch, commit, arquivos salvos na cópia); erro interno, à linha do `erros.log` (item 4).

### Por que o existente não basta
- O `forge salvar` (`bin/forge-salvar`) é do terminal do dono: grava tudo o que mudou, não sabe o escopo do brief e só roda se alguém o chamar; o agente que cai (sessão encerrada, teto, compactação) não o chama.
- O `R-FLUXO` manda o agente commitar e enviar, mas a regra em texto não cobre a parada fora do roteiro. Evidência: o estudo determinístico de 24/11 (D6) registra retomadas manuais e trabalho refeito depois de sessão que caiu com mudança só na cópia.

### Afrouxa: sim, R-VERIFY e dois invariantes de teste; o item 2 não
O item 2 ("sem rede", decisão só pelo estado em disco e pelo git local) segue sem exceção. O `R-VERIFY` ("não desative nem troque o caminho dos hooks") ganha a exceção escrita aqui, na regra 4, só para este hook e só para o commit na cópia; o `docs/regras/R-LIMITES.md` não muda, porque o núcleo do Jarvis (decisão 11 do dono, `docs/regras/orcamento.json`) não tem folga para ela. O título do PR traz o destaque. Mudam junto, no PR do hook, com o rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: `salvar` entra no grupo que nunca bloqueia (códigos `{0}`), com os casos `sem-forge-versao` e `erro-interno`.
- `tests/test_hooks.py`, `test_hooks_json`: o `salvar.py` no `SubagentStop` tem `timeout` 60 (os outros seguem com 10, menos os 300 do `pesado` e do `meta`).
Nenhum trecho de `invariantes` em `tests/config.json` sai.

Critério de reversão da emenda: um commit do `salvar` fora da branch do brief ou com arquivo fora do escopo, um commit WIP que leve marca de conflito, um comando vindo da config da cópia rodando no hook, qualquer chamada de rede dele, ou o hook passar dos 60 s no `erros.log`; também, se em 2 versões o `salvar.log` não registrar nenhum trabalho salvo que evitou retomada manual (a medida não se move, o hook sai).

| Leitura | Quando | Quem |
|---|---|---|
| Linhas do `salvar.log` (trabalho salvo na cópia) e voltas por trabalho perdido no Histórico dos pedidos | 2 versões depois do PR do hook | `tech-lead` |
| Tempo do hook e entradas do `salvar` em `erros.log` | no PR do hook e no fechamento de cada versão | `devops-engineer` |

## Emenda: estado na pergunta do dono (S1-ESTADO-PELA-FERRAMENTA, 2ª parte; v0481 E20.11, ORDEM DO DONO 25/11 21:40)
Estado da emenda: **vigente a partir do PR que traz o hook `estado`**, com fixtures, mutantes e o parecer do `security-engineer`. Até esse PR, os itens 1 e 2 seguem como estão escritos.

**Exceção aos itens 1 e 2**, além das emendas anteriores: o hook `estado`, só no `UserPromptSubmit`, quando a mensagem do dono pergunta o estado, roda o `forge-check status` (S1a, `bin/forge_estado.py`) e imprime a saída dele no contexto. Regras:
1. **Só a pergunta do estado:** um dos termos da lista fixa `TERMOS` de `hooks/estado.py` (estado, status, andamento, como está, como estão, como anda, como andam, o que falta, e agora, onde estamos), palavra inteira, sem acento e sem caixa, numa mensagem de até 200 caracteres (mensagem longa é ordem). Outra mensagem: silêncio, sem rodar nada, custo zero.
2. **Comando fixo do plugin:** `python3 -I <plugin>/bin/forge-check status --raiz <raiz>`, da cópia instalada (o agente não a grava), nunca do work tree; nada da mensagem vai ao comando.
3. **Rede só de leitura, com prazo (exceção ao item 2):** o `forge-check status` lê o GitHub pelo `gh` (último merge, PRs abertos, última release), como o `gh auth status` da emenda do ambiente; prazo de 8 s, abaixo dos 10 s do hook no `hooks.json`. Sem IA, sem escrita, sem custo (`R-CUSTO`: a API do GitHub de leitura não é cobrada).
4. **Texto puro no stdout:** uma linha fixa gerada pelo script e só as linhas `status:` do comando, até 10 linhas de até 300 caracteres, com os caracteres de controle trocados por espaço (`sem_controle`). Sem resposta no prazo, rc diferente de 0 ou nenhuma linha `status:`: uma linha fixa manda rodar o comando antes de responder, nunca estado de memória.
5. **Nunca bloqueia:** sai sempre com 0; fora de projeto do Forge (item 3), hook desligado na config ou erro interno: silêncio, e o erro vai a `.forge/run/erros.log` (item 4). O `estado` entra no grupo que só avisa (códigos `{0}`).

### Por que o existente não basta
- O `forge-check status` (S1a, #910) só vale se o Jarvis o rodar; a regra em texto não segura. Evidência: o estudo de campo de um projeto que usa o Forge (S1, ordem do dono de 25/11): em 24 e 25/11 o Jarvis afirmou estado de memória e errou (20 itens contados quando eram 17, sessão parada achada viva, o merge da 0.47.18 não visto).
- O `ordens` injeta as ordens do dono, não o estado, e é só leitura de arquivo.

### Afrouxa: sim, ADR 0003 itens 1 e 2 e três invariantes de teste
Mudam junto, no PR do hook, com o rótulo `afrouxa-regra`:
- `tests/test_hooks.py`, `test_hooks_json`: o `UserPromptSubmit` aceita o `ordens.py` e o `estado.py`.
- `tests/test_hooks.py`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: `estado` entra no grupo que nunca bloqueia (códigos `{0}`), com os casos `sem-forge-versao` e `erro-interno`.
- `tests/test_doutor.py`, `test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop`: os comandos do `UserPromptSubmit` são o `ordens.py` e o `estado.py`.
Nenhum trecho de `invariantes` em `tests/config.json` sai.

Critério de reversão da emenda: o hook passar dos 10 s ou aparecer mais de 5 vezes por versão no `erros.log`; texto que não veio do `forge-check status` entrar no contexto; ou, em 2 versões, o Histórico registrar afirmação de estado errada do Jarvis depois de o hook injetar o estado (a medida não se move, o hook sai).

| Leitura | Quando | Quem |
|---|---|---|
| Afirmações de estado erradas no Histórico dos pedidos (a medida do E20) | 2 versões depois do PR do hook | `tech-lead` |
| Tempo do hook e entradas do `estado` em `erros.log` | no PR do hook e no fechamento de cada versão | `devops-engineer` |
