---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: b3bc317ac53cdf6f5038421635fd87144cbfcebb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (melhoria/v047-docs-pareceres, E1.315)

## Parecer
Aprovado no b3bc317a. A volta (E1.309) corrige o que o lote de pareceres apontou: o nome da cópia de fora da raiz passa por `sem_controle` antes de virar o `rel` virtual (a regressão que o teste de AST da `SaidaSanitizada`, abuso 18, pegava), os avisos de `conferir_criterio` saem com o caminho dado como as violações (fecha o A1 do parecer anterior), os testes novos falham por asserção na base sem `FC-DOCS-CAMINHO` (o `docs()` do teste devolve uma violação, não `TypeError`) e o M8 segue o texto novo da linha.

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
