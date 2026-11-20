---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: 14c690101de2a9a0442086d9fdad2c1d8deead31
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E39.14, BP3 S2 no head 14c69010)

Escopo: diff `004ce869..14c69010` (5 arquivos, cerca de 28 linhas de código fora testes; H1 dentro do teto). Classe pelo `forge-check classe`: C (review, qa, revisao-seguranca). Suíte inteira fica no CI do PR (sem PR nesta etapa); rodei só os 3 testes novos de `tests/test_forge.py` (`PrepararEstacao`): OK. `bin/forge-mutante --cobertura --base 004ce869`: os três arquivos aparecem como "não coberto", e a regra MUTANTES-SPEC-HOOKS da catraca só alcança Python (`.sh` e `.json` fora), então não há spec exigida. O `shellcheck` não está instalado aqui: fica com o CI.

Conferido contra o brief do autor (E39.5) e as decisões do dono de 20/11 07:47 (BP3 D2 e D3):
- D3: `templates/projeto/.vscode/tasks.json` roda em `folderOpen`, só faz `has-session`/`attach-session` com alvo exato (`=jarvis-<pasta>`), nunca `new-session`; o nome casa com o de `scripts/jarvis:22-23` (`.` e `:` viram `_`). O teste executa o comando literal com tmux falso nos dois ramos (sessão presente e ausente).
- D2: `shutdownAction: none` no devcontainer do modelo, com teste.
- Preparo: `tmux` pelo apt do sistema no modo de fazer e linha `falta:` no `--verificar`; o ramo de falha do apt e o do `--verificar` têm teste de comportamento. O `forge-init` copia `.vscode/` (`find -type f`), e o `/.vscode` do `.gitignore` da raiz é ancorado, então o arquivo do modelo é versionado.
- Fragmento em `changelog.d/`; commit único em Conventional Commits, em português.

## Achados
- A1 (recomendado) templates/projeto/.vscode/tasks.json:7 · A tarefa usa o shell padrão do terminal, mas o teste a roda com `bash -c`; num shell não POSIX (fish) o `if ...; then` quebra. Fixar `options.shell` em bash alinha a tarefa ao teste; sem tmux instalado a mensagem diz "Nenhum Jarvis aberto", vale citar a falta do tmux.
- A2 (recomendado) .devcontainer/devcontainer.json:1 · A D2 do dono (BP3) pede `shutdownAction: none` também no container do Forge e o desenho põe o arquivo no S2, mas o brief da E39.5 limitou o escopo a `templates/`: falta etapa própria para o container do Forge (parecer do devops).

## Sondas

## Parecer
Aprovado. O diff faz o que o item S2 do corte pede, sem tocar arquivo de outro item, com teste de comportamento nos ramos novos. A1 e A2 não bloqueiam (`R-REVIEW`): A1 é robustez do shell da tarefa; A2 é lacuna de escopo vinda do brief, não do código, e vira etapa ou cartão.
