---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: 1a7d0044c2c06149febad637179499ed729c2438
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E39.14, BP3 S2 no head 14c69010, revalidado em ed21f2bd, c0087a7a e 1a7d0044)

Escopo: diff `004ce869..14c69010` (5 arquivos, cerca de 28 linhas de código fora testes; H1 dentro do teto). Classe pelo `forge-check classe`: C (review, qa, revisao-seguranca). Suíte inteira fica no CI do PR (sem PR nesta etapa); rodei só os 3 testes novos de `tests/test_forge.py` (`PrepararEstacao`): OK. `bin/forge-mutante --cobertura --base 004ce869`: os três arquivos aparecem como "não coberto", e a regra MUTANTES-SPEC-HOOKS da catraca só alcança Python (`.sh` e `.json` fora), então não há spec exigida. O `shellcheck` não está instalado aqui: fica com o CI.

Conferido contra o brief do autor (E39.5) e as decisões do dono de 20/11 07:47 (BP3 D2 e D3):
- D3: `templates/projeto/.vscode/tasks.json` roda em `folderOpen`, só faz `has-session`/`attach-session` com alvo exato (`=jarvis-<pasta>`), nunca `new-session`; o nome casa com o de `scripts/jarvis:22-23` (`.` e `:` viram `_`). O teste executa o comando literal com tmux falso nos dois ramos (sessão presente e ausente).
- D2: `shutdownAction: none` no devcontainer do modelo, com teste.
- Preparo: `tmux` pelo apt do sistema no modo de fazer e linha `falta:` no `--verificar`; o ramo de falha do apt e o do `--verificar` têm teste de comportamento. O `forge-init` copia `.vscode/` (`find -type f`), e o `/.vscode` do `.gitignore` da raiz é ancorado, então o arquivo do modelo é versionado.
- Fragmento em `changelog.d/`; commit único em Conventional Commits, em português.

## Revalidação (head ed21f2bd)
Delta lido: `forge-check parecer delta docs/reviews/v0479-bp3-s2-container.md`, intervalo `14c69010..ed21f2bd` (volta da segurança, E39.17), 8 arquivos no domínio:
- `hooks/conformidade.json`: duas entradas `quem: []` com o arquivo exato (`.vscode/tasks.json`, `.devcontainer/devcontainer.json`), na mesma forma das de `.githooks/` e `.forge/versao`; cobre a A1 e a A2 da segurança sem fechar os vizinhos.
- `.devcontainer/devcontainer.json` do Forge com `shutdownAction: none` e a asserção no teste que já percorria os dois devcontainers: fecha a A2 deste parecer, que sai da lista.
- `tests/test_conformidade_vscode_container.py`: 30 casos de bloqueio (2 arquivos × 3 papéis × Write, Edit e três formas de Bash) e 10 de controle nos vizinhos, pelo executor de fixtures de `test_hooks`; teste de comportamento do ramo de falha, não leitura de fonte.
- `tests/mutantes/v0479-bp3-s2-container.json`: um mutante por guarda mudada (M1, M2 e M4) e o M3 de controle (a pasta inteira no lugar do arquivo).
- `docs/engineering/v0479-bp3-s2-container.{md,patch}`: o `denyWrite` do modelo vai como patch ao dono, porque `templates/projeto/.claude/settings.json` é arquivo em vigor; `git apply --check` limpo neste head; o documento diz o que fazer se a A3 entrar antes.
- `changelog.d/`: entrada em `### Segurança`.

Rodei: `tests.test_conformidade_vscode_container` e `PrepararEstacao.test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree`, 3 testes OK; `bin/forge-mutante tests/mutantes/v0479-bp3-s2-container.json --base 14c69010`: M1, M2, M3 e M4 morreram. Nenhum shell tocado no delta (sem `shellcheck`). Código no delta: 4 linhas (H1 dentro do teto). Suíte inteira fica no CI do PR.

## Revalidação (head c0087a7a)
Delta lido: `forge-check parecer delta docs/reviews/v0479-bp3-s2-container.md`, intervalo `ed21f2bd..c0087a7a` (volta da A2 deste parecer e da A3 da segurança, E39.21), 6 arquivos no domínio:
- `changelog.d/v0479-bp3-s2-container.md`: a entrada saiu de `### Segurança` para `### Alterado`, tipo aceito; `bin/forge-changelog conferir --base origin/develop`: "ok: 1 fragmento(s) novo(s) em changelog.d/". Fecha a A2, que sai da lista.
- `hooks/conformidade.json`: entrada `.vscode/settings.json` com `quem: []` e o arquivo exato, na forma das vizinhas; o controle do teste passa a `.vscode/extensions.json`, que segue gravável.
- `tests/test_conformidade_vscode_container.py`: o arquivo entra em `PROTEGIDOS`, então Write, Edit e as três formas de Bash nele passam pelo mesmo executor de fixtures (ramo de falha por comportamento).
- `tests/mutantes/v0479-bp3-s2-container.json`: M5 para a guarda nova (um mutante por linha).
- `docs/engineering/v0479-bp3-s2-container.{md,patch}`: o `denyWrite` do modelo ganha a terceira linha; `git apply --check` limpo neste head.

Rodei: `tests/test_conformidade_vscode_container` (2 testes OK); `bin/forge-mutante tests/mutantes/v0479-bp3-s2-container.json --base ed21f2bd`: M1 a M5 morreram. Nenhum shell tocado no delta. Código no delta: 1 linha (H1 dentro do teto). Suíte inteira fica no CI do PR.

## Revalidação (head 1a7d0044)
Delta lido: `forge-check parecer delta docs/reviews/v0479-bp3-s2-container.md`, intervalo `c0087a7a..1a7d0044`, base `origin/develop` atualizada para 0f6034e e o que veio dela fora do escopo (merge do `forge-fechar`); 1 arquivo no domínio:
- `bin/forge-testes`: `test_conformidade_vscode_container` entra em `FORGE_CHECK` e em `REAPROVEITAM_O_LOTE`. As duas entradas batem com o módulo: ele importa `test_hooks` e reaproveita `Hooks.executar_em_lote` (`tests/test_conformidade_vscode_container.py:46`), que é o critério do comentário de E1.120; `forge-testes --listar tests/test_hooks.py` e `--listar bin/forge-check` passam a listá-lo.

Rodei: `tests.test_testes_tocados`: 164 testes OK (1 pulado), com `TMPDIR` herdado; sem ele, 2 testes de `ExecucaoAfetados` caem porque o `tempfile` grava na árvore e a guarda de `git status` reprova (ambiente, não o delta). Nenhum shell tocado; nenhuma guarda mudada (só tupla de nomes), sem mutante novo. Código no delta: 2 linhas (H1 dentro do teto). Suíte inteira fica no CI do PR.

## Achados
- A1 (recomendado) templates/projeto/.vscode/tasks.json:7 · A tarefa usa o shell padrão do terminal, mas o teste a roda com `bash -c`; num shell não POSIX (fish) o `if ...; then` quebra. Fixar `options.shell` em bash alinha a tarefa ao teste; sem tmux instalado a mensagem diz "Nenhum Jarvis aberto", vale citar a falta do tmux.

## Parecer
Aprovado no head 1a7d0044 (revalidado sobre c0087a7a pelo delta). A A2 (seção do changelog) está fechada; a guarda nova do `.vscode/settings.json` (A3 da segurança) tem teste de comportamento e mutante morto. O `denyWrite` do modelo depende do patch que o dono aplica. A A1 não bloqueia (`R-REVIEW`) e vira cartão depois do merge.
