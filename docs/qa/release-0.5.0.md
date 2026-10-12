---
tipo: qa
contrato: 1
pedido: release-0.5.0
branch: develop
commit: 0c19c90
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: nao
data: 2026-10-12
---
# QA: release 0.5.0 (develop 0c19c90 para main 0.2.1)

Execução real em diretórios temporários (nenhum projeto da máquina tocado, nenhuma sessão `claude` aberta, sem custo). Git de teste com configuração isolada.

## Suíte
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests` | 75 testes, OK |
| `shellcheck` (scripts/*.sh, `jarvis`, `jarvis-forge`, `bin/forge-init`, `tests/*.sh`) | sem achados |
| `claude plugin validate . --strict` | Validation passed |
| `bash tests/e2e-instalacao.sh` | ok (8 agentes, 9 skills, projeto inicializado) |

## Cenários de ponta a ponta
| ID | Cenário | Resultado |
|---|---|---|
| CT-01 | `forge-init --stack node-react` em projeto novo | OK: 15 arquivos; `.forge/versao` = 0.4.1 (igual ao plugin); `.forge/config.json`; seção "Stack" com `node-react`; `core.hooksPath=.githooks`; `.forge/run/` no `.gitignore`; sem `{{marcador}}` sobrando; comando "pronto" vem da stack. `--stack naoexiste` recusa com código 2 e não cria nada. |
| CT-02 | Projeto antigo (sem `.forge/`), `forge-upgrade --simular --ate 0.5.0` | OK: mostra 0.0.0 para 0.5.0 e a branch `forge/upgrade-0.5.0` a partir de `develop`; nada gravado, branch inalterada. |
| CT-03 | `forge-upgrade --ate 0.5.0` real | OK: branch `forge/upgrade-0.5.0`, um commit "migração 0.5.0"; diff só adiciona 3 itens (`.forge/versao`, `.forge/config.json`, 1 linha no `.gitignore`); nada apagado; sem push nem merge. |
| CT-04 | Idempotência | OK: de novo na branch ou após o merge, "já está na versão 0.5.0" (código 0, sem commits novos). Partindo da `develop` sem merge, recusa porque a branch já existe (código 2). |
| CT-05 | Árvore suja | OK: recusa, código 2, nada criado. |
| CT-06 | Nunca parte da main | OK: tanto `--simular` quanto real recusam quando a integração seria `main` (código 2). Sem `--ate`, usa a versão do plugin (0.4.1). |
| CT-07 | Hooks em projeto com `.forge/versao` | OK: `agentes` (teto 3 e duplicado) exit 2 com uma linha `R-TETO`; `parecer` (`gh pr create` sem parecer) exit 2 `R-REVIEW`; `pesado` com outra tarefa viva exit 2 `R-TETO`, comando leve exit 0; `quadro` com quadro inválido exit 2 `R-WIP`. Sem saída no stdout. |
| CT-08 | Hooks em projeto sem `.forge/versao` | OK: todos exit 0, sem saída, sem criar `.forge/`. |
| CT-09 | `forge-check docs/kanban/pr` | OK: parecer válido exit 0; `parecer: talvez`, bugs médios sem `aceite_usuario` e `data` ausente exit 1 com mensagem e R-ID; pedido inexistente exit 1; commit desatualizado detectado também com `--ref`. `--raiz` precisa vir antes do subcomando (conforme o `--help`). |
| CT-10 | `forge-check transcricao verificar` nos fixtures | OK: `ok.jsonl` exit 0; `viola-main` 2 violações R-MAIN; `viola-teto` R-TETO. |
| CT-11 | `transcricao anonimizar` com sessão sintética cheia de segredos (senha, e-mail, token, domínio interno, branch de cliente, agente não `forge:*`) | OK: saída sem nenhum dos termos; branch vira `<branch>`, agente vira `<agente>`; verificador acusa PROMPT-PADRAO e R-MAIN. |
| CT-12 | `preparar-estacao.sh --simular` | OK: exit 0, só imprime `[simular]`, nada alterado. |
| CT-13 | `jarvis --sem-tmux` e com tmux (claude e tmux substituídos por stubs) | OK: chama `claude --continue --remote-control "Jarvis - <projeto>"`; com tmux chama `new-session -A -s jarvis-<projeto>`. Projeto inexistente falha com código 1. |
| CT-14 | `verificar-contribuicao.sh` em clone descartável | OK: branch limpa exit 0; com sk-, ghp_, AKIA, `senha =`, `.env` (forçado), `/home/<usuario>/` exit 1, sem imprimir os valores; `forge:exemplo` ignorado; base inexistente exit 2. |

## Bugs
### B-01 (baixa, responsável: node-backend/qualquer mantenedor de scripts) `jarvis --help` não existe
Passos: `scripts/jarvis --help`. Esperado: uso do atalho (o cabeçalho documenta `jarvis [--sem-tmux] [projeto]`). Obtido: `--help` é tratado como nome de projeto e falha com `cd: /home/<usuario>/--help: No such file or directory`, exit 1. Sem dano; contorno simples (ler o cabeçalho). Observação: o README não promete `--help`.

## Observações (não são bugs)
- `forge-init` e `forge-upgrade` gravam 0.4.1 na `develop` porque `plugin.json` só sobe para 0.5.0 na release; `--ate 0.5.0` funciona. Conferir que a versão e o CHANGELOG sobem juntos no PR para a `main`.
- `forge-upgrade` num projeto só com `main` recusa e pede a `develop` (por desenho, R-MAIN).
- O hook `pesado` trata duas chamadas sem `tool_use_id` como a mesma; no Claude Code o campo sempre existe.

## Veredito
Aprovado: nenhum bug crítico, alto ou médio; 1 baixo aberto, que pede `aceite_usuario: sim` do usuário para entrar na release (por isso o campo está `nao`).
