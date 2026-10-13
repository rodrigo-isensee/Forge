---
tipo: review
contrato: 1
pedido: contrib-identidade-sessao
branch: melhoria/contrib-identidade-sessao
commit: 0238198
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Review independente: identidade da sessão pela raiz (`R-CONTRIB`, PR #84)

Escopo: `origin/develop...0238198`: `hooks/conformidade.py` (`identificar_sessao`, `separar_lancadores`, `exporta`), `tests/test_forge.py` (`ambiente_limpo` sem `CLAUDE_PROJECT_DIR`), 24 fixtures novas em `tests/hooks/conformidade/`, `docs/regras/R-CONTRIB.md`, `skills/contribuir-com-o-forge/SKILL.md`, `CONTRIBUTING.md` e `CHANGELOG.md` (`## [Não publicado]`). É a terceira review da trava de contribuição. Responde à re-review reprovada do #78 (`docs/reviews/contrib-externa-so-propoe.md`).

## Como foi verificado
- `python3 -m unittest discover -s tests` numa worktree destacada em `0238198`: **281 testes, OK** (84 s).
- Sonda com o hook real (`hooks/conformidade.py` lendo o JSON do stdin), `HOME` temporário, `GIT_CONFIG_GLOBAL=/dev/null`, com estes elementos: projeto com `.forge/versao` (origin `acme/proj`, branch `feature/x`); clone do Forge em `~/.forge-contrib/proj` (`plugin.json` `forge`, origin no slug, branch `melhoria/proj-tema`); worktree `~/.forge-contrib/wt/x` (branch `melhoria/outra`); e um "Forge" fora do contrib, sem `.forge/versao`, como o `~/Forge` local. Foram 52 entradas, com e sem `CLAUDE_PROJECT_DIR` no processo do hook. A mesma sonda rodou na `develop` (`d8766d0`) como base de comparação.

## Desvios da re-review: todos resolvidos
| Desvio | develop | PR |
|---|---|---|
| `wt/x` com raiz no projeto: push alheio, `gh pr merge 70`, `gh pr edit 70 --remove-label` | passam | barrados (`R-CONTRIB`) |
| `cwd` = `~/.forge-contrib`: `gh pr merge 70 -R <forge>`, `git -C proj push origin melhoria/outra` | passam | barrados |
| `cwd` = `~`: `gh pr edit <URL> --remove-label`, `cd .forge-contrib/proj && git push ...` | passam | barrados |
| `cwd` = `~`: `git -C <projeto> push origin main` | passa | barrado (`R-MAIN`) |
| `env GH_REPO=...`, `env -i PATH=... GH_REPO=...`, `env -u X`, `env --`, `sudo -u x env GH_REPO=...` | passam | barrados |
| `declare -x` / `typeset -x GH_REPO=...; gh pr merge 70` | passam | barrados |
| Write `<projeto>/.claude/settings.json` (cwd no clone) e `<projeto>/docs/reviews/x.md` por `dev` (cwd `~`) | passam | barrados |
| Espaço duplo em `R-CONTRIB` | presente | corrigido |

Também barrados: `bash -c 'GH_REPO=... gh ...'`, `sh -c 'cd <clone> && git push ...'`, `eval gh pr merge 70 -R <forge>`, `export GH_REPO=...; bash -c 'gh ...'` e, sem `CLAUDE_PROJECT_DIR`, o push alheio no clone (falha fechado).

## Falsos positivos: nenhum
- **Sessão do Forge** (raiz no "Forge"): no `~/Forge`, push, `gh pr merge` e `gh pr edit --add-label` liberam. Em `wt/x`, push alheio, merge, `--remove-label` e Write em `hooks/` liberam. Sem `CLAUDE_PROJECT_DIR`, o `~/Forge` libera.
- **Sessão de projeto, no próprio repositório:** liberam push da própria branch (com `-u`), `gh pr create`, `gh pr merge 3`, `gh pr edit 3 --add-label`, `gh issue close` e Write em `src/`.
- **Sessão de projeto, no PR próprio no Forge:** liberam push de `melhoria/proj-tema` no clone, `gh pr create -R <forge>`, `gh pr comment 84 -R <forge>` (de `~`) e Write no clone.
- Sem `CLAUDE_PROJECT_DIR`, `wt/x` falha fechado (prefixo vazio). Está documentado e é o caso que não se distingue. O Claude Code define a variável para os hooks, então isso só acontece fora dele.

## Bloqueia o merge
1. **`falhar_fechado` ainda decide pela pasta corrente** (`hooks/_comum.py`, `falhar_fechado`: `raiz_do_projeto(hook.cwd()) is None` → libera). O PR estende a guarda a qualquer `cwd` por `CLAUDE_PROJECT_DIR`, mas fora do projeto um erro interno libera, em vez de bloquear (ADR 0009, seção 7). Reproduzido em `wt/x` (branch `melhoria/outra`) com raiz no projeto: `cd <nome de 300 caracteres>; git push origin HEAD` passa. O `cd` falha no shell e o push roda na worktree. No hook, `ramo_em` → `raiz_do_projeto` → `Path.exists()` levanta `ENAMETOOLONG`. O mesmo comando com `cwd` no projeto é barrado ("erro interno do hook conformidade diante de uma ação crítica"). Isso contradiz o texto novo de `R-CONTRIB` ("nunca da pasta corrente"). Correção: em `falhar_fechado`, considerar também a raiz declarada (`CLAUDE_PROJECT_DIR` com `.forge/versao`) e a falha fechada de `~/.forge-contrib`. Na prática, usar a mesma decisão de `identificar_sessao`, sem depender de nada que possa levantar exceção. Fixture: `cwd` em `wt/x`, raiz no projeto, `cd <300×a>; git push origin HEAD` (bloqueia).
2. **A identidade "Forge" é forjável pelo próprio projeto.** `identificar_sessao` testa primeiro `parecer.e_clone_do_forge(raiz)`, que só lê `<raiz>/.claude-plugin/plugin.json` com `"name": "forge"`. No projeto, `.claude-plugin/` é `so_forge` na política e fica sem proteção. Assim, um Write de qualquer papel (`forge:dev`), sem ofuscação, cria o arquivo, e a sessão passa a ser "do Forge". Depois disso passam `gh pr merge 70 -R <forge>` (cwd no projeto), `git push origin melhoria/outra` no clone e `git -C <projeto> push origin main` de `~`. Ou seja: o PR reabre o desvio de `R-MAIN` que acabou de fechar, além de toda a guarda de `R-CONTRIB`. Na `develop`, o caso com `cwd` no projeto já existia; o PR torna esse teste o primeiro portão da sessão. Correção: o projeto vem antes do Forge. Raiz com `.forge/versao` nunca é Forge, nem em `identificar_sessao` nem em `Guarda.clone_do_forge`. O Forge não versiona `.forge/` (`git ls-files .forge` vazio), então a ordem não afeta a sessão do Forge. Fixtures: projeto com `.claude-plugin/plugin.json` `forge` → `gh pr merge 70 -R <forge>`, push alheio no clone e push na `main` de `~` (bloqueiam).
3. **Um clone do Forge fora de `~/.forge-contrib` não é reconhecido como alvo.** `alvo_do_forge(pasta)` só olha `em_contrib(pasta)`. Com raiz no projeto, passam `git -C ~/Forge push origin melhoria/outra`, `cd ~/Forge && gh pr merge 70` (o `gh` resolve o repositório pelo origin da pasta) e, com `cwd` no `~/Forge`, `gh pr edit 70 --remove-label afrouxa-regra`. Só o push para a `develop` é barrado, e por `R-CONFORMIDADE`. O `~/Forge` é o caminho padrão do Forge na máquina do usuário, então basta um `cd`. É a mesma classe do bloqueante 2 da re-review: o alvo decidido pela pasta. O texto novo de `R-CONTRIB` promete as regras "em qualquer pasta". Correção: `alvo_do_forge(pasta)` também deve valer quando a cópia de trabalho que contém a pasta é clone do Forge (`e_clone_do_forge` na raiz git dela, só disco). Fixtures: as três acima (bloqueiam). Mais uma, de controle: o mesmo `~/Forge` com a raiz no Forge (libera).

## Recomendado (não bloqueia)
- **Variável antes de shell aninhado:** `GH_REPO=<forge> bash -c 'gh pr merge 70'`, `env GH_REPO=<forge> sh -c '...'` e `GH_REPO=<forge> eval gh pr merge 70` passam. As atribuições do comando externo não chegam à análise do interno. Basta repassá-las como `ambiente` na chamada recursiva de `bash`. Esses casos já passavam antes do PR.
- **`env -S '<comando>'` / `--split-string`:** o valor é tratado como opção e descartado, então `env -S 'git push origin main'` e `env -S 'gh pr merge 70 -R <forge>'` passam sem análise. Tratar o valor de `-S` como comando aninhado, como o `bash -c`. Também já passava antes.
- **Remoto nomeado:** no projeto, `git remote add forge <URL do Forge>` seguido de `git push forge HEAD:melhoria/outra` passa. `aponta_para_o_forge` só lê o nome do remoto, e a regra diz que cobre o push "por remoto". Resolver a URL com `git remote get-url` (git local, ADR 0003). Já passava antes. Se não for corrigido aqui, abrir cartão.
- **Scripts `.sh`** (`bash push.sh` com `git push` alheio) passam. É o limite já documentado em `R-CONTRIB` (o hook lê só o texto do Bash, e a garantia é o sandbox). Nada a fazer.

## Pontos conferidos sem achado
- **`CLAUDE_PROJECT_DIR` nos subagentes:** pela documentação do Claude Code, a variável vai para o processo de cada hook, com a raiz da sessão, e os subagentes rodam na mesma sessão. A sonda não tem como provar isso. O Bash desta sessão de subagente não tem a variável, o que é esperado: ela é do processo do hook. Forjar pela linha de comando não funciona (o Bash é outro processo), como a re-review já mostrou.
- **`MultiEdit`/`NotebookEdit`** seguem o mesmo caminho do Write (`FERRAMENTAS_DE_ARQUIVO`).
- **O `hooks_desligados` do projeto** cai na pasta corrente. É coerente, porque `.forge/config.json` é protegido.

## Parecer
**Reprovado.** O PR fecha os três bloqueantes e os dois recomendados da re-review, os testes passam e não há falso positivo. Mas os bloqueantes 1 a 3 acima voltam ao autor, cada um com a fixture que falha antes. O 2 é o mais grave: um Write sem ofuscação desliga `R-CONTRIB` e reabre `R-MAIN` fora do projeto. Os três se corrigem em `identificar_sessao`/`clone_do_forge` (o projeto vem antes do Forge), em `alvo_do_forge` (clone do Forge em qualquer pasta) e em `falhar_fechado` (a mesma decisão de sessão). Depois disso, o rótulo `afrouxa-regra` do dono continua obrigatório, porque o PR toca `hooks/conformidade.py` e `docs/regras/`.
