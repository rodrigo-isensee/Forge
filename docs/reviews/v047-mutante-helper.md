---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-helper
commit: 6361a7921ce10b98070528690a802801bcc66462
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (MU1, helper de teste na --base do forge-mutante)

Etapa E2.110, classe C, parecer completo (não havia parecer anterior) no head `4d2a9b7d`, base `bf475209`. Revisor: instância que não fez a entrega (E2.76).

## Achados
- A1 (recomendado) bin/forge-mutante:811 · O grep só casa o nome na linha do from/import: `from tests import (` com `test_a,` na linha seguinte não marca tests/test_a.py como apoio (sonda local: nao-apoio). O repositório hoje não usa essa forma; documentar o limite na docstring ou casar o bloco entre parênteses.

## Sondas

## Escopo lido
- Diff `bf475209...4d2a9b7d`: `bin/forge-mutante` (+27 −9), `tests/test_forge_mutante.py` (+42), `tests/mutantes/v047-mutante-helper.json` e `-2.json`, `changelog.d/v047-mutante-helper.md`.
- Tamanho (M14): 78 linhas de código e teste contadas (bin/ e tests/*.py), abaixo de 150; uma classe de comportamento (o que conta como apoio de teste na `--base`).

## Verificação
- Testes do item: `python3 -m unittest tests.test_forge_mutante.MutacaoDirigida`, ambiente limpo: `Ran 11 tests ... OK`. A suíte completa fica no CI do PR (`R-REVIEW`), sem rerrodar aqui.
- Mutantes declarados: `bin/forge-mutante tests/mutantes/v047-mutante-helper.json tests/mutantes/v047-mutante-helper-2.json --base bf475209...`: `base=bf475209... mb=bf475209... rev=4d2a9b7d...`; MH-M1 a MH-M9 `morreu` (linhas 811, 814, 815, 816, 825, 826, 827, 828, 830). Cada linha de guarda mudada tem um mutante; a condição velha isenta (`linha_base 810`) foi absorvida por `apoio(a)`, coberta por MH-M3 a MH-M9.
- A própria saída prova o comportamento novo no repositório real: `apoio de teste no diff: tests/test_forge_mutante.py`, porque `tests/test_testes_tocados.py:1515` o importa.
- Sonda local de leitura (fora do bloco `## Sondas`, que é só para bloqueante): repo temporário com `from tests import (\n    test_a,\n)` → `tests/test_a.py nao-apoio`; `importlib.import_module('tests.test_b')` → `nao-apoio` (fora do alcance declarado, import dinâmico); comentário `# ver test_c` numa linha de import → `apoio` (falso positivo no sentido seguro: mais mutantes rodam).

## Checklist (leitura)
1. Escopo: fecha as sondas S5 e S6 da v046 E7.11 (A5) do cartão MUTANTE-BASE-HELPER-EM-TEST, sem mais.
2. Regras: `R-VERIFY`, `R-NEUTRO` e `R-CUSTO` sem impacto; commits em Conventional Commits em português.
3. Legibilidade: `importado_por_teste` e `apoio` pequenos, nomes claros; docstring e `--help` atualizados juntos.
4. Erros: `git grep` com código > 1 levanta `RuntimeError`, e a chamada passou para dentro do `try` de `dirigir`, que imprime e sai sem traceback; o código 1 (nada achado) não vira erro (MH-M1, MH-M2).
5. Segurança: argumentos do `git grep` em lista, sem shell; o `sha` vem do `rev-parse`; o nome do módulo vai com `re.escape`. O lado frouxo (A1) não é gatilho provado no repositório atual.
7. Testes: S5 e S6 de ponta a ponta (helper enfraquecido sobrevive), as quatro formas de import, prefixo que não é o nome (`test_soma` contra `test_so`), string que não é import e o ramo de falha do grep.
11. Sem teste de ausência novo; o laço de formas afirma a lista exata.
12. Sem falso de `git` ou `gh`: o teste usa um repositório git real.

## Parecer
Aprovado. A mudança passa a tratar como apoio o `test_*.py` que outro teste importa e o `.py` de `tests/mutantes/`, com aviso e todos os mutantes no diff. Os nove mutantes morrem e os testes do item passam. A1 é recomendado: o grep só olha a linha do `from`/`import`, e um import em várias linhas, entre parênteses, escapa. Hoje o repositório não usa essa forma; vale registrar o limite na docstring ou cobrir o caso, sem devolver a entrega.

## Revalidação (E2.514, head `52f0ce3e`)
- Delta lido por `forge-check parecer delta`, de `4d2a9b7d` a `52f0ce3e`: o código do item (`bin/forge-mutante`, `tests/test_forge_mutante.py`) segue o já aprovado; a mudança nova do autor é o commit `78248550`, que realinha M41 (`guarda-sem-mutante-7.json`) e M19 e M20 (`v046-mutacao-bench-3.json`) ao `forge-mutante` alterado (AR-12).
- Mesma mutação em cada um: M41 troca o `errors="replace"` do `git()` (linha 140) por nada, e o `de` novo (`cwd=cwd, capture_output=True, ...`) é só dessa linha, pois a outra ocorrência (linha 921) não leva `cwd=cwd`. M19 troca `return not a.endswith(".json")` por `True` (spec de `tests/mutantes/` virar apoio). M20 troca `return importado_por_teste(a, sha)` por `True` (todo `test_*.py` virar apoio). Cada um é a guarda antiga na forma nova, sem sobrevivente.
- `bin/forge-mutante guarda-sem-mutante-7.json`: M40 a M47 `morreu` (M41 na linha 140). `bin/forge-mutante v046-mutacao-bench-3.json`: M16 a M20 `morreu` (M19 934, M20 936).
- `python3 -m unittest tests.test_forge_mutante` (sem `-I`): `Ran 127 tests ... OK`. Suíte completa no CI.
- A1 segue recomendado, sem mudança. Parecer: aprovado.

## Revalidação (E2.561, head `6361a792`)
- Delta lido por `forge-check parecer delta`, de `52f0ce3e` a `6361a792`: uma linha em código, `linha_base` da isenta de `v047-mutante-helper-2.json` de 810 para 918 (A2 da segurança). Na base `86ac0fcb` a linha 918 é `return sorted(a for a in mudados if a.startswith("tests/")`, a guarda velha; o trecho isento segue o mesmo.
- `bin/forge-mutante --cobertura --base 86ac0fcb`: rc=0, isenta `bin/forge-mutante:918(base)`, demais guardas `coberta`.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas` (sem `-I`): `Ran 4 tests ... OK`. Suíte completa no CI.
- A1 segue recomendado, sem mudança. Parecer: aprovado.
