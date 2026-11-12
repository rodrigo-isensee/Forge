---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: ba35957368421e2e1803e48011839eaa83454463
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.33, melhoria/escopo-ponto no ba359573)

Revisão do diff 8b5a44d5..ba359573 (E23.17 a, b, c e E23.36 d, e), por instância que não fez a entrega. Testes dos arquivos tocados, um módulo por vez: `test_conf_escopo` 14 OK; `test_selo_e_entrega` 52 OK.

## Achados
- A1 (bloqueante) bin/forge-check:2277 · pedido_dos_pareceres troca o slug pelo id se QUALQUER parecer da árvore leva o id, inclusive de outra branch (docs/reviews/v0457.md vem da develop); a branch com parecer pelo slug passa a reprovar na merge-integracao (S1). Filtrar por branch: igual à conferida.
- A2 (recomendado) bin/forge-check:2327 · o commit: revisado só precisa ser ancestral do head; um sha da develop anterior ao Base-sha também passa. Exigir que não seja ancestral da base (commit da própria branch, como diz a docstring).
- A3 (recomendado) bin/forge-check:2273 · falta o teste do caso misto de (c): parecer da branch pelo slug e parecer de outra branch com o id do pedido na mesma árvore; o S1 vira esse teste.

## Sondas
- S1 · test_conf_escopo com docs/reviews/x.md (pedido: x, branch: melhoria/x) e docs/reviews/p1.md (pedido: p1, branch: melhoria/outra), entrega --etapa merge-integracao · espera: rc 0 e escopo ok, como no 8b5a44d5 · obtido: rc 1, sem parecer da branch melhoria/x para o pedido p1

## Casos negativos conferidos
- (b) brief de outra branch, de outro pedido e de outra etapa não entram na união: cobertos (test_selo_e_entrega).
- (c) parecer de outro pedido segue reprovando: coberto; o caso misto não (A1, A3).
- (d) parecer de outra branch, de outro pedido, sem o commit revisado na branch e sem frontmatter seguem fora: cobertos.

## Tamanho (M14)
Pela regra, contam bin/forge-check (87) e tests/*.py (266): 353 linhas, não 546 (mutantes e changelog ficam fora). O motivo basta: são cinco consertos da mesma conferência, o código é 87 linhas e o volume está nos testes dos ramos negativos. O PR precisa trazer `teto: excedido, 353 linhas, <motivo>`.

## Parecer
Reprovado por A1: defeito provado (regressão sobre a base, S1), que reprova na merge-integracao entregas legítimas de pedidos com parecer pelo slug, caso comum nos pareceres existentes. Correção: em pedido_dos_pareceres, só contar o parecer com `branch:` igual à branch conferida, como o cmd_pr faz na branch de trabalho, e acrescentar o teste do S1. A2 e A3 não devolvem. Segurança (anexo do portão, d) fica com o parecer do security-engineer.
