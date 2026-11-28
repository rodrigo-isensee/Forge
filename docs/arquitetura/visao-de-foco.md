---
tipo: plano-tecnico
contrato: 1
pedido: v047
estado: proposta
ux: n/a (sem tela; muda só como o Claude Code mostra a conversa e o texto do Jarvis)
adrs: [0002, 0003, 0009, 0011, 0017]
agentes: [forge:tech-lead, forge:qa-engineer, forge:security-engineer, forge:software-architect]
gatilhos_seguranca: [segredos-e-configuracao (templates/projeto/.claude/settings.json copiado a todo projeto; o atalho lê ~/.claude/settings.json, que pode ter GH_TOKEN no env), controles-do-forge (hooks/meta.py; tests/config.json se ganhar invariante), codigo-executado-fora-do-sandbox (scripts/jarvis e scripts/jarvis-forge rodam no terminal do dono)]
---
# Desenho VISAO-DE-FOCO (E7, diretriz 31)

Gerado em 2026-11-16 pelo forge:software-architect (brief `v047-software-architect-4`, etapa E7.1). Só desenho: sem código. Código lido no clone `~/.forge-contrib/wt/v047-visao-de-foco` (base `4138445e`).

- **Origem:** ORDEM DO DONO 2026-11-16 05:21 (diretriz 31; escopo E7 do pedido v047), reforça a diretriz 24.
- **Afrouxa controle?** Não. Nada sai de `docs/regras/`, de `tests/config.json` nem de `hooks/conformidade.json`; a medida S6 continua só medindo; nenhuma regra do Jarvis é cortada (diretriz 25).
- **R-CUSTO:** zero. Só configuração local, texto e medida em disco; nenhuma chamada paga, nenhuma sessão do Claude aberta pelos testes.
- **Constituição:** o Forge não tem `docs/constituicao.md`; conforme com `docs/regras/` (R-NEUTRO: nada de projeto; R-CONFORMIDADE: nenhuma trava contornada).

## 1. O que a documentação do Claude Code diz

| # | Afirmação | Página |
|---|---|---|
| D1 | No terminal, a chave se chama **`viewMode`**, texto, com os valores `"default"`, `"verbose"` e `"focus"`. `"focus"` mostra "only your last prompt, a one-line summary of tool calls with edit diffstats, and the final response". | https://code.claude.com/docs/en/settings-reference (seção `viewMode`) |
| D2 | Escopo de `viewMode`: **Any file** = `~/.claude/settings.json` (usuário), `.claude/settings.json` (projeto), `.claude/settings.local.json` (local) e managed. | idem (seções `viewMode` e índice "Scope lists the files...") |
| D3 | `viewMode`, quando definido, ganha da escolha guardada pelo `/focus` e da chave `verbose`. Padrão: sem valor (valem `verbose` e o último `/focus`). | idem |
| D4 | **Focus view precisa do renderizador em tela cheia** (chave `tui`, valor `"fullscreen"`). | idem (`viewMode`: "Focus view needs the fullscreen renderer") |
| D5 | Sobrescrita por sessão de `viewMode`: só `--verbose` (que a vence). Não há opção `--focus` nem variável de ambiente própria. | idem; https://code.claude.com/docs/en/cli-reference (linha `--verbose`: "Overrides the viewMode setting for this session") |
| D6 | `--settings <arquivo-ou-json>` vale só para a sessão, fica acima de usuário, projeto e local e abaixo de managed, e "can set any key your user settings file can set". | https://code.claude.com/docs/en/settings (seções "Change a setting for one session" e "Settings precedence"); https://code.claude.com/docs/en/cli-reference (linha `--settings`) |
| D7 | Ordem: managed > linha de comando > local > projeto > usuário. | https://code.claude.com/docs/en/settings ("Settings precedence") |
| D8 | O comando `/focus` liga e desliga a visão e "the setting persists across sessions". | https://code.claude.com/docs/en/fullscreen ("Search and review the conversation") |
| D9 | Renderizador: `tui` (Any file), `"fullscreen"` ou `"default"`; sem valor, o Claude Code escolhe pela tabela "Fullscreen by default" (ex.: tela cheia para quem usou o Claude Code pela primeira vez a partir de 06/05/2026). `CLAUDE_CODE_NO_FLICKER` e `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` ganham da chave; em `tmux -CC` fica o clássico. | https://code.claude.com/docs/en/settings-reference (seção `tui`); https://code.claude.com/docs/en/fullscreen ("Fullscreen by default") |
| D10 | Na **extensão do VS Code** o nome é outro: configuração da extensão **`focusView`** (padrão `false`), com atalho `Ctrl+Alt+F` (Windows/Linux) / `Ctrl+Option+F` (Mac), menu `/` → Settings → Focus view, ou "Claude Code: Toggle Focus view". "The change applies to every open session and persists across sessions." É configuração do VS Code (Settings → Extensions → Claude Code), não do `settings.json` do Claude. | https://code.claude.com/docs/en/vs-code (tabela de configurações da extensão e parágrafo "Focus view") |
| D11 | Na visão de foco do VS Code ficam visíveis a lista de tarefas, a pergunta pendente e os pedidos de permissão. | idem |
| D12 | O sandbox nega escrita nos arquivos de configuração `.claude` do diretório de trabalho e dos diretórios acima, e na maior parte de `~/.claude`, mesmo com `allowWrite`. | https://code.claude.com/docs/en/sandboxing ("Protected paths") |
| D13 | O hook Stop recebe `last_assistant_message` (o texto final do turno) e `stop_hook_active`; o transcrito "isn't guaranteed to include the final message at Stop time". `decision: "block"` e `additionalContext` fazem a conversa continuar. | https://code.claude.com/docs/en/hooks (seção Stop) |

**Não confirmado** (a documentação não diz):
- N1: versão mínima do Claude Code para `viewMode` (a página só dá versões da extensão do VS Code: 2.1.221).
- N2: o que acontece com `viewMode: "focus"` no renderizador clássico (ignora calado, aviso ou erro).
- N3: se `viewMode` vale no painel gráfico do VS Code ou no chat remoto (`--remote-control`, claude.ai/code); e se `focusView` vale como configuração de workspace (`.vscode/settings.json`). O identificador completo `claudeCode.focusView` aparece só nos links da página, não no texto.
- N4: se `viewMode` aparece no `/config` ou aceita `/config viewMode=focus`.
- N5: se, com `viewMode` definido, um `/focus` no meio da sessão desliga a visão até o fim dela.

## 2. Onde ligar (o que muda)

### 2.1 Atalho de início (`scripts/jarvis`, `scripts/jarvis-forge`)
Opção escolhida: **`--settings` em linha** só quando nenhum arquivo do dono já decidiu (D6, D7).

- `scripts/jarvis`: logo antes do `exec claude` (linha 42), depois do `cd` do projeto (linha 20), acrescentar a `args` o par `--settings '<json>'`.
- `scripts/jarvis-forge`: depois do `cd "$HOME/Forge"` e do desvio do tmux (linha 203 a 209), junto da montagem de `args` (linhas 212 a 216).
- O JSON é constante, montado no script (nunca de entrada): `{"viewMode":"focus"}` e, se nenhum arquivo define `tui` e não há `CLAUDE_CODE_NO_FLICKER` nem `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN` no ambiente, também `"tui":"fullscreen"` (D4, D9). Em `tmux -CC` o próprio Claude Code mantém o clássico (D9), então ligar `tui` lá não quebra.
- **Respeita o dono:** antes, um `python3 -I` só com `json` lê `${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json`, `./.claude/settings.json` e `./.claude/settings.local.json` e devolve só `sim`/`não` para a presença das chaves `viewMode` e `tui` (nunca imprime valor: o `env` do usuário pode ter `GH_TOKEN`). Se algum define `viewMode`, o atalho não passa `viewMode`; idem para `tui`. Arquivo ilegível conta como "definido" (não decide pelo dono; o próprio Claude Code avisa do arquivo quebrado). Isso é necessário porque `--settings` ganha de usuário, projeto e local (D7) e `viewMode` ganha do `/focus` guardado (D3): sem a conferência, o dono não teria como desligar a visão.
- **Saída para o dono** (texto no `--help` dos dois atalhos e no README): `"viewMode": "default"` no `~/.claude/settings.json` (vale em todo lugar onde o projeto não define) ou no `.claude/settings.local.json` do projeto (ganha do projeto, D7).
- Não se passa `--verbose` (ele venceria `viewMode`, D5); teste confere.
- Duplicação: os dois atalhos já repetem o bloco do Telegram; a função nova repete do mesmo jeito (um `scripts/_comum` só por isso seria mecanismo novo sem ganho medido).
- Conflito de arquivo: `scripts/jarvis` e `scripts/jarvis-forge` também mudam nas frentes das diretrizes 28 (`--permission-mode auto`) e 30 (FORGE-SEMPRE-ATUAL). Pela diretriz 18, esta frente espera a que estiver em voo nesses arquivos ou vai à mesma instância.

### 2.2 Modelo de projeto (`templates/projeto/.claude/settings.json`)
- Acrescentar `"viewMode": "focus"` no nível de cima (D1, D2). O `forge-init` já mescla com "valor do projeto fica" (`bin/forge-init:71-100`): projeto que já define `viewMode` não muda. Com `--sem-versionar`, a chave vai ao `settings.local.json` (não é de declaração), como as demais.
- **Não** acrescentar `tui` ao modelo: o arquivo do projeto vale para todos que o clonam (D2, settings "Shared project"), e trocar o renderizador muda seleção de texto, rolagem e mouse de cada pessoa (fullscreen, "What changes"); fica só no atalho, que é do dono.
- Projetos já iniciados: o `forge-upgrade` hoje só grava o bloco `sandbox` (`bin/forge-upgrade:111-122`). O autor confere qual ferramenta leva chave nova do modelo a projeto existente (diretriz 30: por PR na develop do projeto, pelo tech-lead); se nenhuma levar, fica coberto pelo atalho `jarvis` (2.1) e registrado como limite, sem ferramenta nova nesta etapa.
- Saída por pessoa: `"viewMode": "default"` no `.claude/settings.local.json` (D7).

### 2.3 Extensão do VS Code
- O Forge **não grava** configuração do VS Code (`focusView`, D10): ela fica fora dos arquivos do Claude Code, o escopo de workspace não está confirmado (N3) e o modelo não tem `.vscode/`. Em vez disso, uma frase de orientação já pedida pela diretriz 24: "no VS Code, ligue a visão de foco uma vez com Ctrl+Alt+F (Mac: Ctrl+Option+F); ela fica ligada nas próximas sessões". Onde: README (abrir o Jarvis), skill `novo-projeto` (primeira abertura) e a skill `falar-com-o-dono` (3).

## 3. Onde não dá, e por quê (sem contornar a trava)

| Lugar | Por quê | O que fica no lugar |
|---|---|---|
| `~/.claude/settings.json` do dono | Arquivo do dono e caminho protegido pelo sandbox (D12; ADR 0009). Nenhum agente nem ferramenta do Forge o grava. | O atalho passa `--settings` por sessão (2.1); o dono pode, se quiser, rodar `/focus` uma vez (D8). |
| `.claude/settings.json` do próprio Forge (`~/Forge`) | Protegido quando é o diretório de trabalho da sessão (D12); mudar por agente seria contornar. Também não é preciso. | `jarvis-forge` passa `--settings` (2.1). |
| Configuração da extensão do VS Code (`focusView`) | É do VS Code, não do Claude Code (D10); escopo de workspace não confirmado (N3). | Orientação em uma frase (2.3). |
| Managed settings | São da organização (D7); o Forge não as distribui. | Nada. |
| Variável de ambiente ou opção própria | Não existe para `viewMode` (D5). | `--settings`. |
| Renderizador clássico (`tmux -CC`, leitor de tela, `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1`) | Focus view precisa da tela cheia (D4, D9). | Nada a fazer; o atalho não força o que o dono desligou. N2 fica para a prova manual. |
| Chat remoto (claude.ai/code) e Telegram | Não confirmado (N3). | Nada; o texto do Jarvis (4) é o que ajuda em qualquer tela. |

## 4. Texto do Jarvis (linguagem fácil)

- **Núcleo `agents/jarvis.md` no teto** (orçamento do núcleo: 37.511 caracteres, `docs/regras/orcamento.json`). Mudança de saldo zero: a linha "Leia `${CLAUDE_PLUGIN_ROOT}/skills/falar-com-o-dono/SKILL.md` antes de perguntar ou diante de ordem ampla" passa a dizer "antes de perguntar, de dar notícia ou diante de ordem ampla"; os caracteres a mais saem por **mudança de lugar** de um trecho de mesmo tamanho para uma skill que o núcleo já manda ler, sem mudar palavra (diretriz 25), provado pelo `tests/test_jarvis_nucleo.py`. Se não houver trecho que se mova sem perda, a frente para e a decisão sobe ao dono (suposição do pedido, linha 661).
- **Skill `falar-com-o-dono`**, parágrafo novo "**Linguagem fácil (diretriz 31):**", com:
  1. Cada mensagem se explica sozinha: quem lê, com a visão de foco, vê só as mensagens, não os comandos nem os relatórios.
  2. Sem sigla, número de etapa (ex.: E7.1), nome de ferramenta (ex.: forge-check), código de commit, ID de regra (R-...), nome de cartão em maiúsculas ou caminho de arquivo soltos. Termo inevitável: o que é, em poucas palavras, na primeira vez da mensagem.
  3. Ficam: número da versão e o link do pedido de revisão para a `main` que o dono mescla (é ação dele), sempre com o que é.
  4. Fala só nos momentos da diretriz 24 (decisão ou ação do dono, erro que muda prazo ou risco, marco fechado; fora disso, no máximo um resumo a cada 30 minutos, uma linha por item que mudou, e nada se nada mudou). Recibo e perguntas, completos.
  5. A frase de orientação da visão de foco (2.3), dita uma vez por projeto, na primeira abertura.
- **Tabela "Em vez de"** de `skills/modo-iniciante/SKILL.md` (a lista de palavras que o S6 já usa): só **acrescentar** linhas (ex.: `worktree`, `sandbox`, `hash`), nunca tirar.
- Vale nos projetos sem passo extra: skill e núcleo vêm no plugin.

## 5. Checagem de jargão nas mensagens

### 5.1 Por que o existente não basta
- Já existe a medida S6 em `hooks/meta.py:102-141` (Stop, só mede): conta caracteres e as palavras da tabela "Em vez de". Evidência de execução: fixture `tests/hooks/meta/mensagem-com-jargao-so-mede.json` (grava `"jargao": [...]` em `.forge/run/mensagens.jsonl`). Falta: (a) não pega etapa, commit, ID de regra, cartão, ferramenta nem caminho, que são os casos da diretriz 31; (b) lê o transcrito, e a documentação diz que no Stop ele pode ainda não ter a mensagem final (D13), então pode medir a mensagem anterior; (c) **ninguém lê** o `mensagens.jsonl` (busca por `mensagens.jsonl` em `bin/` e `hooks/`: só o próprio `meta.py`).
- Já existe a família `forge-check transcricao` com a medida `decisoes` sobre as respostas do Jarvis da sessão principal (`bin/forge_transcricao.py:301-367`, `ler_respostas_do_jarvis`, fora de subagente, sem código nem citação). Ela é o lugar natural da contagem por sessão.
- Nada novo de hook, regra, campo ou agente: amplia-se S6 e acrescenta-se uma medida à tabela `MEDIDAS`.

### 5.2 Onde (comparação)
| Opção | Pega | Custo | Falso positivo | Escolha |
|---|---|---|---|---|
| Stop bloqueando (`decision: block` ou `additionalContext`) | na hora | um turno a mais e **uma segunda mensagem ao dono** (a primeira já apareceu), contra a diretriz 24; laço limitado só por `stop_hook_active` (D13) | trava conversa | **não** |
| Stop só medindo (S6 ampliado) | por mensagem, em disco | zero token | só conta | **sim** |
| `forge-check transcricao jargao` (eval sobre o transcrito) | por sessão, sob pedido e no ritual de melhoria | zero token, só disco | só conta | **sim** |
| `forge-check conferencia` | trata de briefs e entregas, não de mensagens | — | — | não |

### 5.3 Lista de padrões (fonte única: constante em `hooks/meta.py`; `bin/forge_transcricao.py` importa como já faz o `forge-check` com `hooks/`)
Avaliados só fora de bloco de código cercado e de citação (reaproveita `sem_codigo_nem_citacao`); o que estiver entre crases conta (não é fuga).

| Classe | Padrão (ideia, o autor fecha a expressão) |
|---|---|
| `etapa` | `\bE\d+\.\d+\b` |
| `commit` | 7 a 40 caracteres hexadecimais com pelo menos um dígito **e** uma letra, palavra inteira |
| `regra` | `\bR-[A-Z]{3,}\b` |
| `cartao` | palavra em maiúsculas com hífen, 2+ partes (ex.: `VISAO-DE-FOCO`) |
| `ferramenta` | `forge-[a-z]+`, `forge [a-z]+` no início de comando, `gh `, `git <subcomando>` |
| `caminho` | palavra com `/` terminada em extensão (`.md`, `.py`, `.json`, `.sh`) |
| `palavra` | a tabela "Em vez de" (como hoje) |

**Explicado não conta:** termo seguido, em até 60 caracteres, de parêntese com texto (`E7.1 (a etapa de desenho)`), ou precedido de "o que é" na mesma frase; o autor mede isso em fixture.

**Falso positivo previsto e tratamento:** versão `0.47.1` (não casa `etapa`); hash só de letras como `decade` (não casa `commit`); comando que o dono precisa rodar (diretriz 28: vai em bloco de código, fora da conta); número do pedido de revisão para a `main` (`#123` não é classe). Sem lista de exceções por nome (AR-3: lista negativa).

### 5.4 O que grava
- S6: usa `last_assistant_message` quando vier no evento e cai para o transcrito só sem ele (D13). Linha do `mensagens.jsonl` ganha `classes: {"etapa": 2, "commit": 1}`; **nunca o texto nem o termo achado** das classes novas (um caminho ou hash é dado do projeto). Continua: erro interno libera e vai ao `erros.log`; nunca bloqueia.
- `forge-check transcricao jargao [alvo]`: uma linha por sessão `respostas=N com_jargao=M taxa=…` e o total, só números, como `decisoes`.

## 6. Arquivos, testes e mutantes previstos

| Arquivo | Mudança | Teste |
|---|---|---|
| `scripts/jarvis`, `scripts/jarvis-forge` | `--settings` com `viewMode`/`tui` sob a conferência de 2.1; `--help` com a saída | `tests/test_forge.py` (padrão dos testes dos atalhos, com dublê de `claude` no `PATH` gravando o argv): passa quando nenhum arquivo define; não passa `viewMode` quando usuário, projeto ou local define (3 casos); não passa `tui` com a variável de ambiente; arquivo ilegível = não passa; nunca `--verbose`; JSON exato `"viewMode":"focus"` |
| `templates/projeto/.claude/settings.json` | `"viewMode": "focus"` | teste do modelo: chave e valor exatos; `forge-init` em projeto com `viewMode: "default"` mantém `default` |
| `skills/falar-com-o-dono/SKILL.md` | parágrafo "Linguagem fácil (diretriz 31)" | teste de texto (frase-chave presente); `test_jarvis_nucleo` |
| `agents/jarvis.md` | ponteiro ampliado, saldo zero | `test_jarvis_nucleo`, `test_orcamento_instrucao` |
| `skills/modo-iniciante/SKILL.md` | linhas novas na tabela "Em vez de" | `tests/test_meta.py::Jargao` atualizado (só soma) |
| `hooks/meta.py` | classes, `last_assistant_message`, fora de código | fixtures em `tests/hooks/meta/`: uma por classe; termo explicado não conta; bloco de código não conta; versão e hash só de letras não contam; mensagem do evento vence o transcrito; Stop sempre passa; `mensagens.jsonl` sem o termo |
| `bin/forge_transcricao.py` | medida `jargao` em `MEDIDAS` | teste de unidade com transcrito sintético (sessão principal conta, subagente não) |
| README, skill `novo-projeto` | frase do VS Code e a saída do dono | teste de texto |
| `tests/mutantes/v047-visao-de-foco.json` | — | ver abaixo |

**Mutantes (cada um precisa morrer):** chave `viewMode` trocada por `focusView`; valor `focus` trocado por `verbose`; conferência do atalho invertida (passa sempre / nunca passa); arquivo local esquecido na conferência; `tui` passado mesmo com `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN`; cada classe de 5.3 removida; exclusão de bloco de código removida; regra do "explicado" invertida; ordem `last_assistant_message`/transcrito trocada; gravação do termo achado no `mensagens.jsonl`; `return` antes da medida no `principal`; medida `jargao` contando subagente.

**Gatilhos de segurança** (frontmatter): o `security-engineer` confere a leitura do `~/.claude/settings.json` pelo atalho (só presença de chave, `python3 -I`, nada impresso, AR-5), a chave nova no modelo de todos os projetos e o `hooks/meta.py` (S6 nunca bloqueia; nada de texto do dono em disco).

**Prova manual (sem custo):** o dono, no terminal, abre `jarvis-forge` e vê a visão de foco; responde N2 se estiver no clássico.

## 7. Divisão de tarefas
1. tech-lead (autor), uma instância: 2.1 + 2.2 + README (um commit por item). Espera a frente em voo em `scripts/jarvis*` (diretriz 18).
2. tech-lead (autor), outra instância, em paralelo: 4 (textos) e 5 (`meta.py`, `forge_transcricao.py`). `agents/jarvis.md` e `falar-com-o-dono` também mudam em outras frentes do v047: uma por vez.
3. Em paralelo no head de cada uma: review (tech-lead que não escreveu), QA, segurança.

## Critério de parada
- bloqueia: nada; a checagem de jargão só mede e conta, e nenhuma mensagem nem parada do Jarvis é segurada por ela.
- etapa · `E<n>.<n>` fora de código e sem explicação · oráculo: fixture `tests/hooks/meta/jargao-etapa.json`
- commit · 7 a 40 hexadecimais com dígito e letra · oráculo: fixture `tests/hooks/meta/jargao-commit.json` (e o caso `decade` que não conta)
- regra · `R-` + maiúsculas · oráculo: fixture `tests/hooks/meta/jargao-regra.json`
- cartao · maiúsculas com hífen, 2+ partes · oráculo: fixture `tests/hooks/meta/jargao-cartao.json`
- ferramenta · `forge-*`, `gh`, `git <sub>` fora de bloco de código · oráculo: fixture `tests/hooks/meta/jargao-ferramenta.json`
- caminho · palavra com `/` e extensão · oráculo: fixture `tests/hooks/meta/jargao-caminho.json`
- palavra · tabela "Em vez de" de `modo-iniciante` · oráculo: `python3 -m unittest tests.test_meta`
- gatilho · oráculo: `python3 -m unittest tests.test_hooks tests.test_meta` (todas as fixtures de `tests/hooks/meta/` passam e o Stop sai 0 em todas)

## Critério de reversão e leituras
- Reverte a visão no atalho e no modelo se: o dono relatar que deixou de ver algo de que precisa (ex.: pedido de permissão), ou se `viewMode: "focus"` no renderizador clássico der erro na abertura (N2).
- Reverte a ampliação de S6 se: `forge-check transcricao jargao` der taxa de falso positivo acima de 20% numa amostra de 30 mensagens lida pelo QA.
- Meta medida: taxa de respostas do Jarvis com jargão, por sessão, abaixo de 10% depois de uma semana (`forge-check transcricao jargao`); mensagens por hora ao dono seguem a meta da diretriz 24 (até 4).

| Leitura | O que mostrou |
|---|---|
| settings-reference (`viewMode`, `verbose`, `tui`, escopos) | D1 a D5, D9 |
| settings (precedência, `--settings`, por sessão) | D6, D7 |
| cli-reference (`--settings`, `--verbose`) | D5, D6 |
| fullscreen (`/focus`, tela cheia por padrão) | D8, D9 |
| vs-code (extensão, `focusView`, atalho) | D10, D11 |
| sandboxing (caminhos protegidos) | D12 |
| hooks (Stop) | D13 |
| `hooks/meta.py`, `bin/forge_transcricao.py`, `bin/forge-init`, `bin/forge-upgrade`, `scripts/jarvis*`, `templates/projeto/.claude/settings.json` | seções 2 e 5 |
