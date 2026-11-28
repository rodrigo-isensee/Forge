---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: 702be7ee46494c410965b7b1e1536d14da1172c3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (melhoria/v047-docs-pareceres, E1.315)

## Parecer
Aprovado no b3bc317a. A volta (E1.309) corrige o que o lote de pareceres apontou: o nome da cópia de fora da raiz passa por `sem_controle` antes de virar o `rel` virtual (a regressão que o teste de AST da `SaidaSanitizada`, abuso 18, pegava), os avisos de `conferir_criterio` saem com o caminho dado como as violações (fecha o A1 do parecer anterior), os testes novos falham por asserção na base sem `FC-DOCS-CAMINHO` (o `docs()` do teste devolve uma violação, não `TypeError`) e o M8 segue o texto novo da linha.

## Revalidação no 853e5f30 (E2.500)
Aprovado no 853e5f30. Depois do b3bc317a só entraram merges da develop (86ac0fcb); o código e o teste do autor contra o merge-base da develop seguem `bin/forge-check` 70+13 e `tests/test_forge.py` 114, iguais ao já revisado (sem resolução à mão). Delta lido: `forge-check parecer delta docs/reviews/v047-docs-pareceres.md` (intervalo `b3bc317a..853e5f30`, no domínio `bin/forge-check` e `tests/test_forge.py`; o resto do diff é a develop). No 853e5f30: `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho tests.test_forge.SaidaSanitizada` → `Ran 19 tests ... OK`; `bin/forge-mutante --processos 1 tests/mutantes/v047-docs-pareceres.json` → M1 a M8 `morreu`; `forge-check docs` rc=0. A1 segue recomendado.

## Revalidação no 702be7ee (E2.584)
Aprovado no 702be7ee. Delta lido: `forge-check parecer delta docs/reviews/v047-docs-pareceres.md` (intervalo `853e5f30..702be7ee`; o `bin/forge-check` e os demais testes do intervalo são da develop, #606 e #610). Do autor, só `tests/mutantes/z075-docs-estrito-delta.json`: M1 e M2 passam a `estrito = rel in (delta or ())` (com espaços, como na fonte) e M8 ao recuo de oito espaços do `if delta is None:`; nenhuma guarda de código mudou. `bin/forge-mutante --processos 1 tests/mutantes/z075-docs-estrito-delta.json` → M1 a M8 `morreu` (M1 e M2 na mesma linha, `bin/forge-check:462`; M8 em :459); `python3 -m unittest tests.test_forge_mutante.ConferirTodas` → `Ran 4 tests ... OK` (AR-12). QA e segurança não precisam revalidar: o delta é só spec de mutante, sem comportamento nem superfície nova. A1 segue recomendado.

## Delta lido
`forge-check parecer delta docs/reviews/v047-docs-pareceres.md` (rc=0): intervalo `7d32017c..b3bc317a`; no domínio `bin/forge-check` (+3 −2), `tests/mutantes/v047-docs-pareceres.json` (M8 realinhado) e `tests/test_forge.py` (+10). Os commits entre os dois heads fora disso são só pareceres (QA, segurança, este review) e merges.

## Checklist (regras de leitura que alcançam o delta)
- Faz o que a volta pede, sem mais: sim; três linhas de código, nenhuma guarda nova (o `if tipo in CONTRATOS` só trocou `real.name` por `nome`, e o M8 acompanha).
- Saída sanitizada (E7): o `rel` da cópia de fora nasce sanitizado; o `replace` do aviso troca a primeira ocorrência de `caminho_impresso(rel)`, que é o prefixo `aviso: <rel>:`, por `caminho_impresso(nome)`; dentro da raiz o efeito é o mesmo das violações (o teste novo cobre os dois casos e confere o stderr inteiro).
- Teste de comportamento, não de texto da fonte; commits em Conventional Commits em português.

## Verificadores
- Suíte: sem PR (o brief manda não abrir); o CI do PR decide.
- Rodados aqui no b3bc317a: `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho tests.test_forge.SaidaSanitizada` → `Ran 19 tests ... OK`; `bin/forge-mutante --processos 1 tests/mutantes/v047-docs-pareceres.json` → M1 a M8 `morreu` (M6 e M8 por erro do próprio mutante, não do teste).
- Tamanho (M14): `git diff --numstat --no-renames origin/develop...b3bc317a` dá `bin/forge-check` 70+13 e `tests/test_forge.py` 114, 197 linhas; um comportamento só, sem `hooks/`.

## Achados
- A1 (recomendado) bin/forge-check:407 · 197 linhas de código e teste passam do teto de 150 (M14): o corpo do PR precisa de `teto: excedido, 197 linhas, <motivo>`.
