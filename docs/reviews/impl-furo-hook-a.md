---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: 351040ddb778ebba181230484f8272264df899e4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS), revalidação 4

Escopo: revalidação por delta do parecer anterior (`6a0b80d`, reprovado sobre `1804a43`), depois da volta 3 pelo A1 (`git config set` com opção antes da chave e `--comment` na forma antiga). Commits novos: `8158b0f` (cinco fixtures) e `f732639` (correção). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Delta lido
Saída de `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` (intervalo `1804a43..f732639`):
- `hooks/conformidade.py` +4 -5, linhas 133, 1252, 1256-1257 e 1264 (`--comment` e `--value` em `CONFIG_COM_VALOR`; o subcomando `set`/`unset` reconhecido dentro do laço, antes de qualquer chave, e não mais tirado de `chaves` depois);
- `tests/hooks/conformidade/merge-flag-config-comment-valor-bloqueia.json`, `-set-all-`, `-set-append-`, `-set-comment-igual-` e `-set-value-igual-bloqueia.json`, +19 cada (inteiros).

Já lido, sem mudança desde o parecer anterior: o resto de `234dbe0..1804a43` (ramo do merge, `CONFIG_DO_MERGE`, `CONFIG_ESCOPO`, a saída por `--worktree`, as fixtures anteriores, a spec de mutantes, `tests/test_hooks.py`, `docs/hooks.md` e o fragmento). Os commits de parecer (`f21d6d8`, `ca26af5`) não são código.

## Revalidação 4 (head 351040d)
Escopo: delta `f732639..351040d`, depois do review anterior (`bb78ecd`, aprovado sobre `f732639`). Entraram `dbea044`, `221f8e5`, `044bf31` e `336c43f` (fixtures e mutantes, só `tests/`) e `351040d` (parecer de QA). Instância diferente da do autor (D-ETAPAS-INST = A).

Delta lido (`forge-check delta --parecer docs/reviews/impl-furo-hook-a.md`): cinco fixtures `merge-flag-config-*` com a descrição ajustada (+1 -1 cada), cinco fixtures novas (`depois-dos-tracos-opcao-vira-valor`, `dica-da-chave-do-merge`, `get-com-valor-libera`, `set-value-separado`, `unset-so-a-chave`, todas com a descrição aberta por `FURO-HOOK-A`), `tests/mutantes/impl-furo-hook-a-a3-2.json` (nova, 46 linhas) e `tests/mutantes/impl-furo-hook-a-a3.json` (+67 -7). Já lido, sem mudança: `hooks/conformidade.py`, `tests/test_hooks.py`, `docs/hooks.md` e o fragmento (`git diff --stat f732639 HEAD -- hooks bin` vazio); os pareceres de QA e de segurança não são código.

Achados anteriores: A3 e A4 resolvidos. As descrições das fixtures abrem com `FURO-HOOK-A`, e `bin/forge-mutante --cobertura --base 234dbe0` sai 0 (rc lido em comando próprio): todas as linhas `coberta`, nenhuma "sem mutante" nem inválida. A1 e A2 seguem como cartões ao security-engineer, sem mudança de código.

M14: `git diff --numstat --no-renames origin/develop...HEAD` em código e teste (`hooks/conformidade.py` 45+9, `tests/test_hooks.py` 5) soma 59, abaixo de 150; fixtures, specs, `.md` e fragmento ficam fora; uma classe em `hooks/` com corpus próprio; nenhum caminho de `PROTEGIDOS`. Cumpre.

Parecer deste delta: aprovado; a mudança é só de teste e não enfraquece nenhuma fixture anterior.

## Item entregue
E3 do pedido, item A3 HOOK-MERGE-FLAGS (desenho §2.1), sem mudança de escopo na volta.

## M14
`git diff --numstat --no-renames 234dbe0...f732639`, só código e teste: `hooks/conformidade.py` 45+9 e `tests/test_hooks.py` 5, total 59, abaixo de 150. Fixtures, spec, `.md` e `changelog.d/` ficam fora. Uma classe em `hooks/` (o merge na integração que muda o que o review leu), com corpus próprio; nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no `f732639`: `Ran 2 tests in 329.578s`, `OK`.

Sondas pelo hook real no `f732639` (montagem das fixtures do delta, tech-lead, só o comando trocado):
- Saem 2 com R-CONFORMIDADE, como devem: as sondas do A1 anterior (`set --all`, `--append`, `--comment x`, `--comment=x`, `--value=x`, `--fixed-value --value=x`) e a forma antiga `git config --comment x branch.develop.mergeoptions --squash`; também `set --value x`, `--local set`, `--worktree set --all pull.twohead`, `set --type bool --all merge.x.driver`, `unset --all`, `unset --value=x`, `set -z`, `set --file .git/config`, `set -- <chave> <valor>`, `set --comment x user.name y`. `git config set --all core.hooksPath ...` sai 2 por R-VERIFY.
- Saem 0, como devem: `git config get <chave do merge>`, `git config <chave do merge>`, `git config --local user.name`, `git config set --worktree user.name y`, `git config --type bool set.x`, `git config branch.develop.description set`, `git config list`.
- `git config -- set branch.develop.mergeoptions --squash` sai 0 no hook, mas o git 2.55 real recusa (`key does not contain a section: set`, código 2) e nada grava: não é furo.

Ferramenta (`bin/forge-mutante --cobertura --base 234dbe0`, código 1): `A3-m5` tem `de` que não existe mais no código (inválido desde a volta 1) e as condições de `git_config` (1250 a 1271) aparecem "sem mutante". É pendência do autor para o QA, citada no A4; não refeita aqui.

Também conferido: R-NEUTRO e R-CUSTO sem nada a apontar; não há shell tocado; o Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar; commits em Conventional Commits, com os trailers, teste antes da correção.

## Achados
- A1 (recomendado) hooks/conformidade.py:1269 · sem mudança: fora das chaves do merge, `--worktree` ainda libera o `git config` (`core.*`, `user.*`), e sem `extensions.worktreeConfig` o git grava no `.git/config` comum; classe anterior, cartão ao security-engineer.
- A2 (recomendado) hooks/conformidade.py:132 · sem mudança: depois da chave o git grava `--local`, `--global`, `--system` e `--worktree` como valor; `git config user.name --global` sai 0. Sem efeito no merge; cartão ao security-engineer.
- A3 (recomendado) tests/hooks/conformidade/merge-flag-config-set-all-bloqueia.json:2 · resolvido na revalidação 4: as fixtures abrem a descrição com `FURO-HOOK-A`.
- A4 (recomendado) tests/mutantes/impl-furo-hook-a-a3.json:46 · resolvido na revalidação 4: `forge-mutante --cobertura` sai 0.

## Parecer
Aprovado. A volta 3 fecha o A1 anterior: o `set`/`unset` é reconhecido antes de qualquer chave, as opções dele não viram chave, e `--comment`/`--value` passam a levar valor também na forma antiga; as sondas do review e da segurança saem 2 e as leituras seguem livres. A1 e A2 seguem como cartões; A3 e A4 não devolvem, mas o A4 deve chegar ao QA resolvido.
