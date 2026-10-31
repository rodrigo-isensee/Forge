---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 1804a4345abfec159ef2990019d7060792265858
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a3 (revalidação da volta 2)

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-3`). Revalidação pelo delta do parecer anterior (`24a8b87`, reprovado com A1 e A2 bloqueantes). Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.3. Não sou o autor.

## Delta lido
`forge-check delta --parecer docs/security/impl-furo-hook-a.md` listou `24a8b87..1804a43`:
- `hooks/conformidade.py` +12 -5, nas linhas 1250 e 1263-1273 (`git_config`).
- Três fixtures novas: `merge-flag-config-set-driver-bloqueia.json`, `merge-flag-config-set-mergeoptions-bloqueia.json` e `merge-flag-config-worktree-mergeoptions-bloqueia.json`.

Como o delta toca um controle do Forge (o hook `conformidade`), reli `git_config` inteira (`hooks/conformidade.py:1247-1273`) e as constantes que ela usa (`:125-133`), não só as linhas mudadas.

## Item entregue e M14
- **Item:** E3, A3 HOOK-MERGE-FLAGS.
- **M14 (`agents/tech-lead.md:19` na develop):** contam `hooks/conformidade.py` (44+7) e `tests/test_hooks.py` (5): 56 linhas, abaixo de 150. Uma classe de comportamento em `hooks/` (merge na integração que muda o resultado revisado), com corpus próprio. **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o hook `conformidade`, nos portões R-REVIEW e R-CONFORMIDADE.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1261 · A2 anterior, corrigido em parte: após `set` ou `unset`, toda opção vira chave. `git config set --all branch.develop.mergeoptions --squash`, `set --append pull.twohead ours`, `set --comment=x pull.octopus ours` e `set --value=x core.editor vi` saem 0.
- A2 (recomendado) hooks/conformidade.py:1267 · anterior à branch: `git config remove-section core` e `--remove-section core` saem 0 e apagam o core.hooksPath (o pre-push deixa de rodar); a seção sem ponto não casa CONFIG_PROTEGIDA. Cartão novo ao dono, como o N1.
- A3 (recomendado) hooks/conformidade.py:1250 · segue do parecer anterior: `GIT_EDITOR=<script> git config -e|--edit|edit` e as chaves do bash fora da linha crítica gravam sem recusa. Cartão.

## Detalhe dos achados
Sondas: cada uma monta a fixture `merge-flag-config-set-mergeoptions-bloqueia` pelo `Fixture`/`rodar` da própria worktree, troca só o comando e roda o hook real com o papel tech-lead. A sintaxe do git foi conferida num repositório descartável em `$TMPDIR` (git 2.55.0). Nada rodou contra repositório real, rede ou produção.

**O que a volta 2 fecha (saem 2):**
- **A1 anterior (`--worktree`), corrigido.** `git config --worktree` com `branch.develop.mergeoptions`, `pull.twohead`, `pull.octopus` e `merge.nos.driver`, também com `--add`, `--replace-all` e `--`, e `git config set --worktree branch.develop.mergeoptions --squash`. A recusa dessas chaves não sugere mais `--worktree`. Contraprova `git config --worktree core.sparseCheckout true` sai 0, e `git config set --worktree core.editor vi` também (isenção anterior, fora das chaves do merge, vai com o N1).
- **A2 anterior (`set`/`unset`), na forma simples.** `git config set` com `branch.develop.mergeoptions`, `pull.twohead`, `merge.nos.driver`, `alias.p` e `core.editor`; `set --local …`; `set --type bool core.bare true`; `unset core.bare`. O corpus de legítimos sai 0: `git config get branch.develop.mergeoptions`, `git config list`, `git config --get core.editor`, `git config set branch.feature/x.merge refs/heads/develop` e `git config branch.feature/x.merge refs/heads/develop`.

**A1, bloqueante (requisito C-A3-3 do modelo, segurança com gatilho; é o A2 anterior, corrigido em parte).** Evidência: em `hooks/conformidade.py:1261`, a palavra `set` entra em `chaves` como se fosse a chave; com `chaves` não vazia, toda palavra com traço seguinte conta como chave ou valor. A `:1263-1265` tira só o `set`, e a 1.ª chave passa a ser a opção. Sondas com saída 0, todas da sintaxe aceita pelo git real (as quatro primeiras gravaram a chave no `.git/config` do repositório descartável):
- `git config set --all branch.develop.mergeoptions --squash`
- `git config set --append pull.twohead ours`
- `git config set --comment=x pull.octopus ours`
- `git config set --value=x core.editor vi`
- `git config set --comment x pull.twohead ours`
- `git config set --type=bool core.bare true`
- `git config set --fixed-value core.editor vi`
- `git config unset --all alias.p`

Caminho: o mesmo do A2 anterior, sem intenção: um agente usa a sintaxe de subcomando com uma opção comum (`--all` para trocar todos os valores, `--comment` para registrar o motivo) e grava a estratégia do merge da develop; o merge sem flag passa pelo A3 e pelo `parecer` e vira squash ou no-commit. Severidade alta, pelo mesmo efeito. A correção mínima do parecer anterior já trazia a lista destas opções.

Correção mínima: o `set`/`unset` é reconhecido como subcomando **antes** de entrar em `chaves`, e as palavras com traço que vêm depois dele e antes da chave são opções, não chave (a mesma regra da forma antiga). As opções do subcomando, a lista inteira:
- de escopo: `--local`, `--global`, `--system`, `--worktree`;
- sem valor: `--all`, `--append`, `--fixed-value`;
- com valor, junto (`--x=v`) ou separado (`--x v`): `--file`, `--blob`, `--type`, `--default`, `--value`, `--comment`.

Destas, `--value` e `--comment` faltam em `CONFIG_COM_VALOR` (`:133`) para a forma separada; `-f` já está lá.

Fixtures `-bloqueia`: `set --all branch.develop.mergeoptions --squash`, `set --append pull.twohead ours`, `set --comment=x pull.octopus ours` e `set --value=x core.editor vi`. Contraprovas · 0: `set --all branch.feature/x.merge refs/heads/develop` e `set --comment x branch.feature/x.merge refs/heads/develop`. Esforço P. Dono: tech-lead.

**A2, recomendado (anterior à branch, fora das chaves do merge).** Evidência: `hooks/conformidade.py:1267` casa a 1.ª chave com `CONFIG_PROTEGIDA`, e as alternativas da regex pedem o ponto (`core\.`, `user\.`, `alias\.`). Um nome de seção sem ponto (`core`) não casa. `git config remove-section core` e `git config --remove-section core` saem 0. No git real, depois de `remove-section core`, `git config --get core.hooksPath` volta vazio: o pre-push do repositório deixa de rodar (R-VERIFY). A guarda de `core.hooksPath` em `:1089` procura o nome da chave na linha e não vê a seção. `remove-section pull` e `rename-section pull x` saem 0, sem efeito no merge (tiram a configuração, não a põem). Na base `234dbe0` a regex e a forma `--remove-section` são as mesmas. Caminho: só deliberado. Ninguém apaga a seção `core` por engano, e ela leva junto `repositoryformatversion` e `bare`. Severidade média. Correção mínima (cartão novo ao dono, junto do N1): `remove-section` e `rename-section`, nas duas formas, recusam quando o nome da seção (ou o novo nome) é `core`, `user`, `alias`, `include*`, `commit`, `pull`, `merge.<d>` ou `branch.<b>`. Esforço P. Dono: tech-lead.

**A3, recomendado.** O A3 do parecer anterior segue igual: o delta não tocou `-e`/`--edit`/`edit` nem o marcador `CRITICO`. Cartão, dono tech-lead.

Dimensão nova para a matriz do modelo (§8): **Posição, opção do subcomando antes da chave** (`set --all`, `set --comment=`) e **Mecanismo, seção inteira** (`remove-section`, `rename-section`), além das já registradas.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta`, leitura do delta e de `git_config` inteira, sondas locais pelo harness de fixtures e um repositório descartável para a sintaxe do `git config`. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o delta não traz segredo, dependência nem workflow).
