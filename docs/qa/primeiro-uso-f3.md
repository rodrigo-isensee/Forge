---
tipo: qa
contrato: 1
pedido: primeiro-uso-f3
branch: melhoria/primeiro-uso-f3
commit: 17cdf20
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 2
aceite_usuario: sim
data: 2026-10-13
---

# QA - primeiro uso do Forge, entrega F3 (`forge doutor`)

Testado no HEAD 17cdf20 do PR #103 (último commit só de parecer; código igual ao a032be1), em worktree temporária. Sem rede e sem o `gh` real (um `gh` falso na frente do PATH, com log de chamadas), HOME e git temporários (`GIT_CONFIG_GLOBAL` de arquivo), repositório temporário criado com `forge-init`, `claude` falso. Nada tocou o GitHub. O aviso de sandbox sobre `api.anthropic.com` na saída da suíte é do ambiente.

## Resultado da suíte
`python3 -m unittest discover -s tests`: 404 testes, OK, 71 s. Nenhum `skip`.

Vermelho antes do verde: sem `bin/forge-doutor` e `hooks/doutor.py`, `python3 -m unittest tests.test_doutor` dá 53 testes, 35 falhas e 8 erros.
Mutação manual no diff (sem ferramenta gratuita para este código; o autor também não tem): todos mortos, cada um com falha em `tests.test_doutor`.
- `avisado = False` no `registrar` (aviso repete): 1 falha.
- Conserto sem esperar o "s": 1 falha (`if False:` no lugar da conferência da resposta).
- Conserto sem exigir TTY (`interativo = not rapido`): 1 falha.

## Matriz (arquitetura F3 e decisão "uma vez por dia" → teste → resultado)
| # | Requisito | Teste exploratório | Resultado |
|---|---|---|---|
| 1 | Checagem 1: plugin instalado | `installed_plugins.json` ausente e `enabledPlugins` vazio → aviso; restaurado → silêncio | passou |
| 2 | Checagem 2: `.forge/versao` × plugin | projeto velho (0.1.0), projeto novo (99.0.0) e arquivo ilegível → 3 frases distintas, cada uma com o comando certo; restaurado → silêncio | passou |
| 3 | Checagem 3: proteção do git | `core.hooksPath` trocado + `pre-push` sem `x`; pasta `.githooks` removida. Conserta com "s", religa, restaura a pasta pelo modelo | passou |
| 4 | Checagem 4: `gh` logado (só no modo completo) | `gh` falso sem login → aviso; com login → silêncio. `--rapido` fez 0 chamadas ao `gh` (log) | passou |
| 5 | Checagem 5: identidade do git | `user.name`/`user.email` vazios → uma frase com os dois comandos | passou |
| 6 | Checagem 6: `settings.json` com o Jarvis | sem `agent` (conserta, guarda cópia, preserva chave do usuário); ausente (recria do modelo); quebrado (não mexe, diz para chamar o Jarvis) | passou |
| 7 | Checagem 7: sandbox ligado | sem `sandbox.enabled` → aviso; ligado no `settings` do usuário → silêncio | passou |
| 8 | Checagem 8: `develop` e `homolog` | `homolog` só no remoto → cria a local com "s"; `develop` em lugar nenhum → só instrução | passou |
| 9 | Silêncio total quando tudo está ok | comando sem `-v`, hook `SessionStart` e `Stop`: stdout vazio, exit 0; com `-v` uma linha "tudo em ordem" | passou |
| 10 | No máximo uma linha ao usuário, nada no contexto do modelo | `SessionStart` com problema: 0 bytes no stdout. `Stop`: um único `{"systemMessage": ...}` de até 200 caracteres, nunca `additionalContext` | passou (ver B-02) |
| 11 | Frequência diária | `startup` + `Stop` avisa uma vez; segundo `Stop`, `resume`, `compact`, `clear` e `Stop` depois de cada um: silêncio. Dia seguinte com o mesmo problema: avisa de novo (uma vez) | passou |
| 12 | Problema novo no mesmo dia | `resume` com a versão do projeto alterada: avisa de novo, uma vez | passou |
| 13 | Cache de dia antigo sem `SessionStart` | `Stop` refaz o diagnóstico e avisa uma vez | passou |
| 14 | Conserto com "s", sem "s", backup | "n": nada muda (exit 1). "s": conserta, imprime o que fez e o caminho do backup, reconfere e diz "Tudo em ordem agora" (exit 0). Backup de `settings.json` e do `core.hooksPath` anterior em `~/.local/state/forge/backup/<projeto>/<data>/`, com o valor original | passou |
| 15 | Recusa sem TTY | stdin `/dev/null`: lista o problema, diz "Dá para consertar 1 sozinho: rode `forge doutor` num terminal", não conserta (exit 1). `--rapido` nunca pergunta | passou |
| 16 | Git lento | Todo `git` pendurado: o comando diz "Não consegui checar o git agora..." e nenhuma afirmação falsa (sem "proteção desligada", sem "branch não existe"). Só `config --list` e `for-each-ref` lentos: hook avisa o mesmo texto, 5,4 s no `SessionStart`; o `Stop` seguinte, 30 ms (cache) | passou (ver B-01) |
| 17 | O doutor nunca quebra a sessão | Cache com JSON quebrado, cache que é pasta, cache lista, `problemas` que não é lista, stdin vazio, stdin lixo, `cwd` numérico, `.forge/run` sem permissão: sempre exit 0, erro no `erros.log`, nada no stdout. Fora de projeto do Forge: nada | passou |
| 18 | Desempenho normal | `SessionStart` em 30 a 40 ms (critério: menos de 100 ms) | passou |
| 19 | Atalho `jarvis` | com `claude` falso: tudo ok abre direto; com problema mostra o aviso e abre mesmo assim quando não há TTY | passou |
| 20 | `forge doutor` pelo despachante, `forge-upgrade` e `tech-lead` ("antes de abrir PR", "antes de atualizar") | `forge doutor -v` roda; `forge-upgrade` chama `--rapido`; `agents/tech-lead.md` passo 5 manda rodar `forge doutor --rapido` antes de abrir PR | passou |
| 21 | Mensagens em português claro | Todas lidas: sem jargão, cada uma diz o que fazer; "core.hooksPath" só aparece no texto de backup, junto do valor | passou (ver B-02) |

## Bugs abertos
Nenhum bloqueia. Ambos de severidade baixa, responsável sugerido: agente de desenvolvimento da stack da fábrica (shell/Python).

### B-01 - Com o `git` pendurado, o `SessionStart` espera mais do que os 10 s do hook
- Severidade: baixa. Ambiente: 17cdf20.
- Passos: num projeto com `.forge/versao`, coloque na frente do PATH um `git` que faz `sleep 30`; rode `printf '{"hook_event_name":"SessionStart","cwd":"<projeto>"}' | python3 hooks/doutor.py`.
- Esperado: voltar em menos de 10 s (o `timeout` do `hooks.json`), de preferência com o "não consegui checar o git".
- Obtido: 15,4 s no `SessionStart` e 10 s no `Stop`, exit 0, e o erro `TimeoutExpired ... git rev-parse --git-common-dir timed out after 5 seconds` no `erros.log`. O limite de 3 s do doutor não vale para o `git` do `_comum` (`hook.run()`, 5 s por chamada, mais de uma). O Claude encerra o hook aos 10 s, então a pessoa espera até 10 s ao abrir a sessão. Nenhuma afirmação falsa e a sessão não quebra. Quando só o `config --list`/`for-each-ref` ficam lentos, tudo funciona como desenhado (5,4 s).
- Observação: o `_comum.git` é compartilhado com os demais hooks; o conserto pode ser fora do escopo da F3.

### B-02 - O aviso truncado em 200 caracteres corta a instrução no meio
- Severidade: baixa (texto). Ambiente: 17cdf20.
- Passos: com o projeto na versão 0.1.0 e o sandbox desligado, rode `SessionStart` e `Stop` do hook.
- Esperado: a linha única diz o que fazer.
- Obtido: `Forge doutor: 2 coisas para ver — O projeto está na versão 0.1.0 do Forge e o Forge instalado é o 0.12.0: atualize o projeto com `forge-upgrade --simular` (mostra o que muda) e d… (rode: forge doutor)`. Só o primeiro problema aparece e a frase termina em "e d…". Não engana e o "(rode: forge doutor)" sempre fecha a linha, mas a instrução fica cortada e o segundo problema só aparece ao rodar o comando.

## Fora do escopo
Acessibilidade e E2E de navegador não se aplicam (CLI e hooks). `forge doutor` em Windows nativo e o doutor em modo completo contra um `gh` real não foram exercitados (regra: nada de rede).

## Parecer
Aprovado: todos os requisitos da F3 e da decisão "uma vez por dia" cumpridos, suíte verde, mutantes mortos, nenhum bug crítico, alto ou médio. Dois bugs baixos abertos, por isso `aceite_usuario: sim`.
