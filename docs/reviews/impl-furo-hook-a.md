---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 9583765906acf550dafb347db140f745d1050968
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS)

Escopo: `234dbe0..9583765` (base 234dbe0fb90b005450d7c2eb59e6241ea9779155). Commits: `38d218a` (teste das fixtures do lote), `facf90f` (correção, com as fixtures e a spec de mutantes) e `9583765` (fragmento). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Item entregue
E3 do pedido, item A3 HOOK-MERGE-FLAGS, pelo desenho §2.1 e pelo C-A3-3 do modelo de ameaças. A entrega tem quatro partes:
- `opcao_de_merge_que_muda_o_resultado`: no `git merge` ou `git pull` de outra branch na integração, recusa com `R-REVIEW`, em todo papel, `-s`, `-X`, `--squash` e `--no-commit`. As opções curtas valem coladas ou agrupadas, e as longas também abreviadas.
- `CONFIG_DO_MERGE` (`branch.*.mergeoptions`, `pull.twohead|octopus`, `merge.*.driver`) entra na `CONFIG_PROTEGIDA` e é recusada também em `git -c`.
- O `git config` passa a ler o que vem depois do `--`.
- O `docs/hooks.md` foi atualizado. São 25 fixtures (4 contraprovas) e a spec de mutantes.

## M14
Linhas que contam: `hooks/conformidade.py` 29+1 e `tests/test_hooks.py` 5, num total de 35. Ficam fora as fixtures, a spec, o `.md` e o `changelog.d/`. O total fica abaixo de 150. Há uma classe em `hooks/` (o merge na integração que muda o que o review leu, pela linha ou pela configuração), com corpus próprio, e nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no HEAD revisado: `Ran 1 test`, `OK`.

Sondas pelo hook real no HEAD revisado, com `conformidade/merge-flag-squash-bloqueia.json` como modelo (tech-lead na `develop`):
- saem 2: `-nsours`, `--strategy ours`, `--strategy-o theirs`, `-S -s ours`, `-e -Xours`, `git -C . merge --squash`, `pull -s ours`, `pull --no-commit`, `env` e `timeout` antes do merge, o segundo merge depois de `&&`, `git -c pull.twohead=ours pull`, `git -c merge.x.driver=true merge`, `config pull.octopus ours` e `config --add branch.develop.mergeoptions -s`;
- saem 0, como devem: `merge --no-ff -m x`, `merge --ff-only`, `git -c color.ui=never merge` e `config --get branch.develop.mergeoptions`;
- saem **0**, e não deviam: `git config branch.develop.mergeoptions --squash`, o mesmo com `--no-commit` e com `-sours`, e com `--global`.

No git real (`git init` em `$TMPDIR`), `git config branch.develop.mergeoptions --squash` sai 0 e grava `--squash`. A forma sem `--` é a que o desenho §2.1(a) e (c) nomeia, e a fixture da branch usa só a forma com `--`. Em `git_config`, o valor que começa com `-` não entra em `chaves`, e com uma chave só o comando é tratado como leitura (achado A1).

Também conferido:
- `git config --worktree branch.develop.mergeoptions --squash` sai 0. Sem `extensions.worktreeConfig`, o git grava no `.git/config` (conferido em `$TMPDIR`). A classe é anterior à branch (vale também para `core.*`) e vira cartão para o security-engineer (achado A2).
- R-NEUTRO e R-CUSTO: nada a apontar. Não há shell tocado. O Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar.
- Commits em Conventional Commits, com os trailers.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1261 · `git config branch.develop.mergeoptions --squash` (sem `--`) sai 0 no hook e o git grava; o valor com `-` não conta como valor e a linha passa como leitura. Conte como valor toda palavra depois da 1.ª chave e ponha essa sonda como fixture (desenho §2.1(c)).
- A2 (recomendado) hooks/conformidade.py:1249 · `--worktree` libera o `git config`, mas sem `extensions.worktreeConfig` o git grava no `.git/config` comum; a classe é anterior (vale para `core.*`) e vai como cartão ao security-engineer, fora desta branch.

## Parecer
Reprovado. A branch entrega o A3 e cumpre a M14. O A1, porém, é furo provado na forma que o próprio desenho nomeia, num controle do Forge, e por isso a branch volta ao autor. O A2 não devolve. Na revalidação, o escopo é o delta (`forge-check delta`).
