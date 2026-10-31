---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a5
commit: caae6a663ca509a07ea3ff0e015fa316dd2fc7f0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a5 (A5 ROTULO-VARIAVEL)

Escopo: `234dbe0..dc3762c` (base 234dbe0fb90b005450d7c2eb59e6241ea9779155), commits `38d218a` (teste das fixtures do lote), `fc151f4` (correção, com a spec de mutantes) e `dc3762c` (fragmento). Revisor em instância diferente do autor (D-ETAPAS-INST = A).

## Item entregue
E5, item A5 ROTULO-VARIAVEL do pedido, pelo desenho §2.7. `aplica_afrouxa_regra` passa a exigir o dono nestes casos:
- valor de rótulo com `$` ou crase;
- opção de rótulo no fim da linha;
- `xargs` antes do `gh` com rótulo pedido;
- `gh alias set|import` e `alias` do shell que citam o rótulo;
- `\uXXXX` decodificado no `gh api`, com o resto contando como ilegível.

São 16 fixtures, com 3 contraprovas que liberam e R7 e R8 como regressão. Há 9 mutantes na spec, e o `docs/hooks.md` foi atualizado.

## M14
Linhas que contam: `hooks/conformidade.py` 25+9 e `tests/test_hooks.py` 5, num total de 39. Ficam fora as fixtures, a spec, o `.md` e o `changelog.d/`. São 39 linhas, abaixo de 150. Há uma classe em `hooks/` (o rótulo que o hook não vê exige o dono), com corpus próprio, e nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
Sondas pelo hook real no HEAD revisado, com o fixture `conformidade/rotulo-variavel-por-xargs-bloqueia.json` como modelo (sessão do Forge, conta que não é a do dono):
- `echo afrouxa-regra | xargs gh pr edit 1 --add-label` sai 2;
- `echo afrouxa-regra | xargs gh pr edit 1 --add-label bug` sai 2;
- `echo --add-label afrouxa-regra | xargs gh pr edit 1` sai **0**;
- `printf "%s\n" 1 --add-label afrouxa-regra | xargs gh pr edit` sai **0**;
- `cat r.txt | xargs gh pr edit 1` sai **0**.

No bash, o `xargs` junta a entrada aos argumentos, e o `gh` recebe `--add-label afrouxa-regra`. Por isso o rótulo passa sem o dono quando a opção vem da entrada padrão. O desenho §2.7(b) conta como pode aplicar todo comando que estava atrás de `xargs`. A implementação só conta se já houver rótulo pedido na linha (achado A1).

Também conferido:
- R-NEUTRO e R-CUSTO: nada a apontar. Não há shell tocado. O Forge não tem `docs/engineering/praticas.md`.
- Commits em Conventional Commits, com os trailers.

## Revalidação (volta 1, 2026-10-31)
Rodei `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` na worktree da a5. Intervalo: `dc3762cd5d9caf6f339d76864cb9196a26ae3ae1..caae6a663ca509a07ea3ff0e015fa316dd2fc7f0`. O delta lido:
- `hooks/conformidade.py:1367`, +1 -1: `por_xargs and bool(pedidos)` passou a `por_xargs`;
- as fixtures novas `rotulo-variavel-por-xargs-echo-bloqueia.json`, `-printf-` e `-cat-` (1-29 cada), com `codigo` 2 e conta que não é a do dono. São as três sondas do A1 da rodada anterior.

O resto ficou como "já lido": a revisão de `dc3762c` acima.

`python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no HEAD `caae6a6`: `Ran 1 test`, `OK`.

Sondas pelo hook real no HEAD `caae6a6`, com o mesmo modelo de antes:
- saem 2: `echo --add-label afrouxa-regra | xargs gh pr edit 1`, `printf "%s\n" 1 --add-label afrouxa-regra | xargs gh pr edit`, `cat r.txt | xargs gh pr edit 1`, `echo 1 | xargs gh issue edit` e `echo x | xargs -I{} gh pr create --title {}`;
- saem 0, como devem: `echo 1 | xargs gh pr view` e `gh pr edit 1 --title x`.

A M14 segue cumprida: `hooks/conformidade.py` continua com 25+9 linhas, e o total da branch, com 39.

## Achados

## Parecer
Aprovado no HEAD `caae6a6`. O achado A1 da rodada anterior (`dc3762c`, reprovada), em `hooks/conformidade.py:1367`, está resolvido. Agora todo `gh pr|issue edit|create` atrás de `xargs` exige o dono, como pede o desenho §2.7(b), e a correção tem fixture. O delta não traz achado novo.
