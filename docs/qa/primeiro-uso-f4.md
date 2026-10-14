---
tipo: qa
contrato: 1
pedido: primeiro-uso-f4
branch: melhoria/primeiro-uso-f4
commit: aa9a304
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 4
aceite_usuario: sim
data: 2026-10-14
---

# QA - primeiro uso do Forge, entrega F4 (travas de atos perigosos, instalação intocável, modo iniciante)

Testado no HEAD aa9a304 do PR #110 (último commit só de parecer; código igual ao 8d99869), em worktree temporária. Sem rede e sem o `gh` real (PATH sem `gh`; nenhum comando de `gh` foi executado, o hook só lê o texto). Projeto temporário criado com `forge-init`, remoto `origin` bare local, `GIT_CONFIG_GLOBAL` de arquivo. O aviso de sandbox sobre `api.anthropic.com` na saída da suíte é do ambiente.

## Resultado da suíte
`python3 -m unittest discover -s tests` (PATH sem `gh`): 404 testes, OK, 85 s. Nenhum `skip`.
Vermelho antes do verde e mutação: não refeitos; valem os do parecer de autor (58 fixtures falhando e 7 erros sem a mudança). A fixture-a-fixture `trava-*` (105) cobre cada recusa; a exploração abaixo é complementar.

## Método
Hook real `hooks/conformidade.py` alimentado por JSON de PreToolUse (como o Claude Code faz), `CLAUDE_PROJECT_DIR` no projeto temporário, papéis `forge:node-backend`, `forge:tech-lead` e `forge:jarvis`, perfil padrão (sem `.forge/perfil`) e iniciante (`iniciante`). Cerca de 380 invocações em 3 baterias: fluxo normal (32 comandos x 2 papéis x 2 perfis), atos perigosos (39 x 2 x 2), falsos positivos e bordas (50 x 2 perfis), mais worktree solta em `$TMPDIR`.

## Matriz
| Critério | Teste | Resultado |
|---|---|---|
| Fluxo normal passa sem pergunta: commit, add, push de `melhoria/*` (e `-u`), `branch -d/-D melhoria/*`, `worktree add/remove [--force]`, `rm` de temporárias e `node_modules`, `claude plugin update/validate/list`, `forge salvar`, `forge desfazer`, `forge doutor`, fetch, stash, `reset --soft/--mixed`, `gh pr view`, `gh api` de leitura | 32 comandos x 4 combinações | passa (só `gh pr create` recusado para `node-backend`, regra de papel anterior) |
| Perfil padrão: nada novo para quem programa (`reset --hard`, `clean -fdx`, `checkout -- .`, `restore .`, `gh repo archive`, `rebase` em branch de trabalho passam) | 5 comandos | passa |
| Apagar o repositório (`gh repo delete`, `gh api -X DELETE`, `-XDELETE`, GraphQL `deleteRepository`) | 4 variantes x 2 perfis x 2 papéis | recusa sempre |
| Tornar público (`--visibility public`, `=public`, `-f private=false`, `-X PATCH --input`) | 4 x 2 x 2 | recusa sempre |
| Force push (`--force`, `-f`, `--force-with-lease`, `--force-if-includes`, `+ref`, `--mirror`, `-c push.default`) | 8 x 2 x 2 | recusa sempre |
| Push na `main` / `develop` (inclusive `HEAD:refs/heads/main`, `--delete develop`) | 5 x 2 x 2 | recusa sempre |
| Reescrever integração: `filter-branch`, `branch -D main/develop`, `update-ref -d`, `rebase`/`switch -C main` estando em `develop`/`main` | 6 x 2 x 2 | recusa sempre |
| Remover `.forge`, `.githooks`, `.claude` (`rm -rf`, `./`, `$PWD/`, `mv`, `bash -c`, a partir de worktree solta, por caminho absoluto) | 10 x 2 x 2 | recusa sempre |
| `.forge/perfil` de iniciante: `>`, `rm`, `sed -i`, Write | 4 | recusa no iniciante; no padrão passa (o arquivo não é de iniciante) |
| Perguntar no iniciante: `reset --hard`, `clean -fdx`, `checkout -- .`, `restore .`, `gh repo archive`, `rebase` de branch enviada, `checkout -B`/`branch -f` de branch enviada | 8 | `ask` (saída 0), com texto simples |
| Worktree solta com cwd nela: `reset --hard` e `clean` na própria cópia livres; `cd <projeto> && reset --hard`, `git -C <projeto> clean`, `switch x && reset --hard`, `gh repo archive` perguntam; `rm -rf <projeto>/.forge` recusa | 8 | passa |
| Falsos positivos: mensagem de commit citando `rm -rf .forge`/`push --force`/`gh repo delete`, `melhoria/main-fix`, `branch -D main-menu`/`melhoria/develop`, `grep "gh repo delete"`, `cat .forge/perfil`, `src/.forge-cache`, `docs/.claude-old`, `.forge-bak`, `git push :melhoria/velha`, `gh repo edit --description`, `--visibility private` | 22 | nenhum falso positivo |
| Mensagens do iniciante em português claro, com consequência e caminho | leitura de todas as variantes | claras, com 4 ressalvas baixas abaixo |

## Bugs (todos baixos, abertos)
Responsável sugerido: `forge:node-backend` (ou o agente do hook em `hooks/conformidade.py`).

**QA-F4-01 (baixa): mensagem de `develop` cita `main`.** Passos: perfil iniciante, `git push origin develop` (ou `push origin --delete develop`). Esperado: texto sobre a `develop`. Obtido: "A linha principal (main) é sua: só você junta nela...", com o prefixo `R-CONFORMIDADE`. Confunde quem não sabe o que é `develop`.

**QA-F4-02 (baixa): recusa de `rebase` na `develop`/`main` diz "para voltar atrás, use forge desfazer".** Passos: iniciante, em `develop`, `git rebase origin/main`. Obtido: recusa (saída 2) com "Isso reescreve o histórico e as outras cópias deixam de bater. Para voltar atrás, use o 'forge desfazer'." Nada foi feito, então não há o que desfazer; falta dizer o que fazer no lugar (pedir ao Jarvis). A mesma frase vale para `filter-branch` e `switch -C main`.

**QA-F4-03 (baixa): o caminho prometido para o perfil não existe.** Passos: iniciante, `echo experiente > .forge/perfil`. Obtido: "Se quiser mudar, peça ao Jarvis como fazer", mas o comando assistido (`forge perfil`) não existe (pendência já documentada em `docs/hooks.md`). O Jarvis também fica recusado. Aceitável até a F6; registrar com prazo.

**QA-F4-04 (baixa): lacunas e atritos menores.**
- `git branch -m|-M develop velho` (e `main`) passa nos dois perfis: renomeia a branch de integração fora do lugar, local e recuperável. Não é `-D`, mas tem o mesmo efeito prático.
- `git rebase --continue` pergunta no iniciante, repetindo a confirmação do `rebase` já aceito (em segundo plano a continuação seria negada e deixaria o rebase pela metade).
- Limites já aceitos pelo desenho e vistos de novo: `python3 -c` escrevendo `.forge/perfil`, `find ... -exec rm`, `cd .. && rm -rf <projeto>`, `rm -rf $TMPDIR/x/.forge` (recusa com variável).

## Pontos de atenção (não são bugs)
- `ask` só protege com alguém para responder; em segundo plano ele vira negado (comportamento do Claude Code, não reproduzido aqui por falta de API). O `rebase` de branch `melhoria/*` enviada para atualizar com a `develop` é fluxo comum e vai perguntar no iniciante.
- O PR precisa do rótulo `afrouxa-regra` (toca `hooks/`); é do dono.

## Critério de pronto
Nenhum bug crítico, alto ou médio; suíte verde; recusas e perguntas se comportaram como a fatia F4 pede em todos os atos perigosos testados; zero falso positivo no fluxo normal. Parecer: aprovado, com 4 baixos abertos e aceite do usuário.
