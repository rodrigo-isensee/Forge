---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 1804a4345abfec159ef2990019d7060792265858
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS), revalidação 2

Escopo: revalidação por delta do parecer anterior (`24a8b87`, aprovado sobre `f793398`), depois da volta 2 pelos achados A1 e A2 da segurança (`72b533c`). Commits novos: `6c07217` (três fixtures, vermelhas antes da correção) e `1804a43` (correção). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Delta lido
Saída de `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` (intervalo `f793398..1804a43`):
- `hooks/conformidade.py` +12 -5, linhas 1250 e 1263-1273 (a saída antecipada por `--worktree` sai; o subcomando `set`/`unset`; `--worktree` só libera fora das chaves do merge);
- `tests/hooks/conformidade/merge-flag-config-set-driver-bloqueia.json` +33 (inteiro);
- `tests/hooks/conformidade/merge-flag-config-set-mergeoptions-bloqueia.json` +33 (inteiro);
- `tests/hooks/conformidade/merge-flag-config-worktree-mergeoptions-bloqueia.json` +33 (inteiro).

Já lido, sem mudança desde o parecer anterior: o resto de `234dbe0..f793398` (ramo do merge, `CONFIG_DO_MERGE`, `CONFIG_ESCOPO`, as 26 fixtures anteriores, a spec de mutantes, `tests/test_hooks.py`, `docs/hooks.md` e o fragmento).

## Item entregue
E3 do pedido, item A3 HOOK-MERGE-FLAGS (desenho §2.1), sem mudança de escopo na volta.

## M14
`git diff --numstat --no-renames 234dbe0...1804a43`: `hooks/conformidade.py` 44+7 e `tests/test_hooks.py` 5, total 56, abaixo de 150. Fixtures, spec, `.md` e `changelog.d/` ficam fora. Uma classe em `hooks/` (o merge na integração que muda o que o review leu), com corpus próprio; nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no `1804a43`: `Ran 1 test`, `OK`.

Sondas pelo hook real no `1804a43` (montagem da fixture `merge-flag-config-set-mergeoptions-bloqueia.json`, tech-lead na `develop`, só o comando trocado):
- Saem 2, como devem: `git config set branch.develop.mergeoptions --squash`, `git config --worktree branch.develop.mergeoptions --squash`, `git config set --worktree|--local|--type bool branch.develop.mergeoptions --squash`, `git config unset branch.develop.mergeoptions`. Os A1 e A2 da segurança, na forma das sondas dela, estão fechados.
- Saem 0, como devem: `git config get branch.develop.mergeoptions`, `git config branch.develop.mergeoptions`, `git config --local user.name`.
- Saem 0 e não deviam: `git config set --append branch.develop.mergeoptions --squash`, o mesmo com `--all`, `--comment x`, `--value=x` e `--fixed-value --value=x`; e na forma antiga, `git config --comment x branch.develop.mergeoptions --squash`.

Conferido no git 2.55 real em `$TMPDIR`: esses comandos saem 0 e gravam `--squash` em `branch.develop.mergeoptions` (`set --all pull.twohead ours` grava `ours`). Causa: depois de `set`, o laço de `git_config` já tem uma "chave" (`set`), então a opção seguinte (`--append`, `--all`, `--comment`, `--value=...`) entra como valor e vira `chaves[0]` quando a linha 1263 tira o `set`; `CONFIG_PROTEGIDA` não casa com ela e o hook libera. Na forma antiga, `--comment` (git 2.45) não está em `CONFIG_COM_VALOR`, e o argumento dela vira a chave. É o mesmo comportamento que a volta 2 entrega (o `set` grava), por um caminho vizinho: achado A1, bloqueante.

Também conferido: R-NEUTRO e R-CUSTO sem nada a apontar; não há shell tocado; o Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar; commits em Conventional Commits, com os trailers, e o teste vermelho veio antes da correção.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1263 · `git config set --all branch.develop.mergeoptions --squash` sai 0 e o git grava (idem `--append`, `--comment x`, `--value=x`; e `--comment x` na forma antiga, :133). Tire o `set` antes do laço, `--comment` e `--value` em `CONFIG_COM_VALOR`, fixtures.
- A2 (recomendado) hooks/conformidade.py:1270 · fora das chaves do merge, `--worktree` ainda libera o `git config` (`core.*`, `user.*`), e sem `extensions.worktreeConfig` o git grava no `.git/config` comum; classe anterior, cartão ao security-engineer.
- A3 (recomendado) hooks/conformidade.py:132 · sem mudança: depois da chave o git grava `--local`, `--global`, `--system` e `--worktree` como valor; `git config user.name --global` sai 0. Sem efeito no merge; cartão ao security-engineer.

## Parecer
Reprovado. A volta 2 fecha as sondas A1 e A2 da segurança na forma exata delas, mas o subcomando `set` com qualquer opção antes da chave (e `--comment` na forma antiga) ainda grava `mergeoptions` e as outras chaves do merge com o hook liberando. Volta ao autor pelo A1; A2 e A3 não devolvem.
