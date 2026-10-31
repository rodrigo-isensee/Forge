---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: f79339827638132560ea01fb39105b891b70e11c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS), revalidação 1

Escopo: revalidação por delta do parecer anterior (`0a6d65d`, reprovado sobre `9583765`). Commits novos: `a0d1dfd` (fixture da sonda do A1, vermelha antes da correção) e `f793398` (correção). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Delta lido
Saída de `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` (intervalo `9583765..f793398`):
- `hooks/conformidade.py` +5 -3, linhas 132 e 1258-1262 (`CONFIG_ESCOPO` e o laço de `git_config`);
- `tests/hooks/conformidade/merge-flag-config-mergeoptions-valor-com-traco-bloqueia.json` +33 (inteiro).

Já lido, sem mudança desde o parecer anterior: o resto de `234dbe0..9583765` (ramo do merge, `CONFIG_DO_MERGE`, as 25 fixtures, a spec de mutantes, `tests/test_hooks.py`, `docs/hooks.md` e o fragmento).

## Item entregue
E3 do pedido, item A3 HOOK-MERGE-FLAGS (desenho §2.1), sem mudança de escopo na volta.

## M14
`git diff --numstat --no-renames 234dbe0..f793398`: `hooks/conformidade.py` 32+2 e `tests/test_hooks.py` 5, total 39, abaixo de 150. Fixtures, spec, `.md` e `changelog.d/` ficam fora. Uma classe em `hooks/` (o merge na integração que muda o que o review leu), com corpus próprio; nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no `f793398`: `Ran 1 test`, `OK`.

A1 anterior, pelo hook real no `f793398` (modelo: a fixture nova, tech-lead na `develop`): saem 2 `git config branch.develop.mergeoptions --squash`, o mesmo com `--no-commit`, com `-sours`, com `--global` antes da chave e com `-- --squash`. Saem 0, como devem: `config --get branch.develop.mergeoptions`, `config branch.develop.mergeoptions` (só a chave), `config --local user.name` e `config --local --list`. A1 fechado.

Isenção de `--local`, `--global`, `--system` e `--worktree` (`CONFIG_ESCOPO`, desenho §2.1(c)), conferida no git 2.55 real em `$TMPDIR`:
- Antes da chave, as quatro escolhem o arquivo, e o laço já as pula por começarem com `-`; a isenção só age depois da chave.
- Depois da chave, o git as grava como valor: `git config core.editor --local` grava `--local`. O comentário da linha 132 (não são valor) não confere com o git.
- Para a classe do A3 o efeito é nulo: com `mergeoptions` igual a `--local`, `git merge x` sai 129 (`unknown option`) e não mescla. O caminho só falha fechado.
- Fora da classe, o hook deixa gravar `core.*`, `user.*` e `include.path` com esses quatro valores literais e com `--type`, `--default`, `--file` e `--blob` (de `CONFIG_COM_VALOR`, também tomados como opção depois da chave): `git config user.name --global` e `git config core.editor --type bool` saem 0 e gravam. Já era assim na base (todo valor com `-`); a volta reduziu o furo. `core.hooksPath` tem trava própria (sai 2), e gravar em `.git/--local` para usar o `include.path` sai 2. Sem cadeia provada, vira o achado A3, recomendado, com cartão ao security-engineer.
- O `--worktree` em `CONFIG_ESCOPO` não tem efeito: a linha 1249 já retorna quando ele aparece (o A2 anterior segue em aberto como cartão).

Também conferido: R-NEUTRO e R-CUSTO sem nada a apontar; não há shell tocado; o Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar; commits em Conventional Commits, com os trailers, e o teste vermelho veio antes da correção.

## Achado anterior fechado
O A1 do parecer anterior (hooks/conformidade.py:1261, `mergeoptions --squash` sem `--`) está fechado e sai do bloco: sai 2 no `f793398`, com a fixture `merge-flag-config-mergeoptions-valor-com-traco-bloqueia.json`.

## Achados
- A2 (recomendado) hooks/conformidade.py:1249 · sem mudança: `--worktree` libera o `git config`, mas sem `extensions.worktreeConfig` o git grava no `.git/config` comum; classe anterior, cartão ao security-engineer.
- A3 (recomendado) hooks/conformidade.py:132 · depois da chave o git grava `--local`, `--global`, `--system` e `--worktree` (e `--type`, `--default`) como valor; `git config user.name --global` sai 0. Sem efeito no merge; remova a isenção e leve a classe ao security-engineer, como cartão.

## Parecer
Aprovado. O A1 está fechado, com fixture vermelha antes da correção, e a branch segue entregando o A3 dentro da M14. A isenção de escopo não reabre o merge; o furo que sobra é anterior à branch e fica como recomendação (A3), que não devolve.
