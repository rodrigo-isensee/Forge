---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: f732639d904cea5b959e809467952843a8658a41
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a3 (A3 HOOK-MERGE-FLAGS), revalidação 3

Escopo: revalidação por delta do parecer anterior (`6a0b80d`, reprovado sobre `1804a43`), depois da volta 3 pelo A1 (`git config set` com opção antes da chave e `--comment` na forma antiga). Commits novos: `8158b0f` (cinco fixtures) e `f732639` (correção). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Delta lido
Saída de `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` (intervalo `1804a43..f732639`):
- `hooks/conformidade.py` +4 -5, linhas 133, 1252, 1256-1257 e 1264 (`--comment` e `--value` em `CONFIG_COM_VALOR`; o subcomando `set`/`unset` reconhecido dentro do laço, antes de qualquer chave, e não mais tirado de `chaves` depois);
- `tests/hooks/conformidade/merge-flag-config-comment-valor-bloqueia.json`, `-set-all-`, `-set-append-`, `-set-comment-igual-` e `-set-value-igual-bloqueia.json`, +19 cada (inteiros).

Já lido, sem mudança desde o parecer anterior: o resto de `234dbe0..1804a43` (ramo do merge, `CONFIG_DO_MERGE`, `CONFIG_ESCOPO`, a saída por `--worktree`, as fixtures anteriores, a spec de mutantes, `tests/test_hooks.py`, `docs/hooks.md` e o fragmento). Os commits de parecer (`f21d6d8`, `ca26af5`) não são código.

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
- A3 (recomendado) tests/hooks/conformidade/merge-flag-config-set-all-bloqueia.json:2 · as 5 fixtures novas não abrem a descrição com `FURO-HOOK-A`, então `test_fixtures_do_lote_furo_hook_a` (o teste da spec de mutantes) não as roda; só `test_fixtures` as vê.
- A4 (recomendado) tests/mutantes/impl-furo-hook-a-a3.json:46 · `forge-mutante --cobertura` sai 1: `A3-m5` inválido e `git_config` (:1250 a :1271) sem mutante; atualize a spec antes do QA, como na a4 e na a5.

## Parecer
Aprovado. A volta 3 fecha o A1 anterior: o `set`/`unset` é reconhecido antes de qualquer chave, as opções dele não viram chave, e `--comment`/`--value` passam a levar valor também na forma antiga; as sondas do review e da segurança saem 2 e as leituras seguem livres. A1 e A2 seguem como cartões; A3 e A4 não devolvem, mas o A4 deve chegar ao QA resolvido.
