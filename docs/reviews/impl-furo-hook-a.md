---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a4
commit: 10192e5f4a04d2ff63dae52af40066b58970eb6e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a4 (A4 FC-SUBCOMANDO-HOOK), revalidação 2

Escopo: revalidação por delta do parecer anterior (`e74f5cc`, reprovado sobre `6a15c2a`). Commits novos: `4b67f82` (fixtures das sondas do A1, vermelhas antes da correção) e `ddf8bf3` (correção). O revisor é uma instância diferente da do autor (D-ETAPAS-INST = A).

## Delta lido
Saída de `forge-check delta --parecer docs/reviews/impl-furo-hook-a.md` (intervalo `6a15c2a..ddf8bf3`):
- `hooks/conformidade.py` +3 -2, linhas 75-77 (ramo do interpretador em `args_do_forge_check`);
- `tests/hooks/conformidade/fc-anotar-por-interpretador-opcao-w-dev-bloqueia.json` e `fc-anotar-por-interpretador-opcao-x-dev-bloqueia.json`, +20 cada (inteiros).

Já lido, sem mudança desde o parecer anterior: o resto de `234dbe0..6a15c2a` (`forge_check_grava`, o ramo do nome opaco, as 20 fixtures, o teste estrutural, a spec de mutantes, `docs/hooks.md` e o fragmento).

## Revalidação 2 (head 10192e5)
`forge-check delta --parecer` sobre o intervalo `ddf8bf3..10192e5` lista só: a fixture `fc-anotar-por-interpretador-sem-forge-check-dev-libera.json` (+19, inteira, contraprova: `python3 anotar ...` sem forge-check sai 0) e `tests/mutantes/impl-furo-hook-a-a4.json` (spec: trechos `de`/`para` realinhados à correção do A1 e o mutante `A4-m14`). Lidos os dois; o JSON da spec é válido. `git diff ddf8bf3 HEAD -- hooks bin tests/test_hooks.py` vazio: código de produção sem mudança (o `10192e5` e o `c83dd9d` só trazem pareceres de QA e segurança, já fora do delta). `tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no head: `Ran 1 test`, `OK`. M14: 61 linhas de código e teste, cumpre. Já lido: o resto de `234dbe0..ddf8bf3`, como acima.

## Item entregue
E4 do pedido, item A4 FC-SUBCOMANDO-HOOK (desenho §2.3), sem mudança de escopo na volta.

## M14
`git diff --numstat --no-renames 234dbe0..ddf8bf3`: `hooks/conformidade.py` 42 e `tests/test_hooks.py` 19, total 61, abaixo de 150. Fixtures, spec, `.md` e `changelog.d/` ficam fora. Uma classe em `hooks/` (o que o `forge-check` grava passa pela política de caminhos), com corpus próprio; nenhum caminho de `PROTEGIDOS`. Cumpre.

## Conferido
`python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_lote_furo_hook_a` no `ddf8bf3`: `Ran 1 test`, `OK`.

A1 anterior, pelo hook real no `ddf8bf3` (modelo: `fc-anotar-por-interpretador-opcao-x-dev-bloqueia.json`, papel `forge:node-backend`): saem 2 `python3 -X utf8 bin/forge-check anotar ...`, `python3 -W ignore ...`, `python3 -u -X dev -W ignore ./bin/forge-check anotar ...`, `python3 -Xutf8 ...`, `env python3 -X utf8 ...` e `python3 -I ...`. Saem 0, como devem: `python3 -X utf8 bin/forge-check pr p1` e `... docs`. A1 fechado.

A correção procura a palavra cujo nome é `forge-check` entre os argumentos do interpretador. Um `forge-check` que apareça como argumento de outro script (`python3 x.py bin/forge-check anotar`) passa a ser lido como o `forge-check`: falha fechada, sem furo novo.

Também conferido: R-NEUTRO e R-CUSTO sem nada a apontar; não há shell tocado; o Forge não tem `docs/engineering/praticas.md`, então não há regra de leitura nem de ferramenta a citar; commits em Conventional Commits, com os trailers, e o teste vermelho veio antes da correção.

## Achado anterior fechado
O A1 do parecer anterior (hooks/conformidade.py:75, opção do interpretador com valor) está fechado e sai do bloco: as duas sondas saem 2 no `ddf8bf3`, com fixture cada. A2 e A3 seguem sem mudança e não devolvem.

## Achados
- A2 (recomendado) hooks/conformidade.py:78 · com nome opaco, `--t decisao` sai 0: o argparse aceita prefixo de uma letra e `abreviacao_de` exige mais de 3 caracteres; conte `anotar` sozinho, ou qualquer prefixo de `--tipo`, como a forma do anotar.
- A3 (recomendado) docs/hooks.md:41 · o texto diz que vale atrás de lançador, mas `find -exec forge-check anotar` e `xargs forge-check` com o subcomando na entrada saem 0; restrinja o texto aos lançadores lidos e leve a classe ao security-engineer, como cartão.

## Parecer
Aprovado. O A1 está fechado, com fixtures vermelhas antes da correção, e a branch segue entregando o A4 dentro da M14. A2 e A3 ficam como recomendação, que não devolve.
