---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q0-ameacas
commit: 35f1cbd3d367b88db8812ffca1332089a158e4da
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.47, modelo de ameaças da quarentena BP1 Q0)

Revalidação do parecer reprovado no head 954cae59 (A1 bloqueante, A2 recomendado), agora no head 35f1cbd3 (volta E37.48). Só documento: sem código, sem guarda, sem mutante; sem suíte local (brief).

Delta lido: `forge-check parecer delta docs/reviews/v0479-bp1-q0-ameacas.md` deu `intervalo: 954cae59..35f1cbd3` e `delta: nenhum arquivo do domínio mudou`, porque o domínio do review deixa `docs/security/` de fora (`LIVRES`, `bin/forge-check:190`). Como o objeto deste review é `docs/security/ameacas/bp1-quarentena.md`, o delta lido foi o `git diff 954cae59 35f1cbd3` desse arquivo (+13/-10). O outro arquivo do intervalo é este parecer.

## Conferência dos achados da rodada anterior
- A1 (era bloqueante), resolvido. M11.1 (linha 47) passa a contar só as entradas ativas na data do runner, com as vencidas fora, como mandam D2 e D3. C11 (linha 82) barra todo PR enquanto a vencida e o teto elevado ficam, salvo o PR que tira a vencida e desce o teto, que passa sem rótulo e está no corpus de legítimos de S8 (linha 102). T11, M11.1, C11 e S8 dizem agora a mesma regra. O PR de remoção passa a ser obrigatório, e a trava da fila que isso causa fica explícita e coberta pelo aviso de 2 dias (M16.3).
- A2 (era recomendado), resolvido. T20 (linha 66) reconhece a cobertura existente: `tests/test_hooks_volta_corpus.py:176` (`test_referencia_ao_executar_fora_de_chamada_e_achada`) e `:202` (`test_hooks_reais_e_driver_so_chamam_o_executar_direto`). M20.1 ficou só com a parte nova, os scripts de `bin/` e `scripts/`, e traz um corpus de legítimos conferido na árvore: `bin/forge-check:6813` (`modulo_do_bin("forge_transcricao").executar`), `bin/forge_meta.py:27` e `bin/forge-testes:643` (`def executar`). C17 aponta para a cobertura que já existe. S9 (linha 103) ficou só com C16, e a extensão foi para S11 (linha 106).
- A seção 7 ganhou o mapa de Cn por etapa, com Q1, Q2, Q3 e o cartão. Confere com a tabela da seção 6: C5, C6 e C12 no leitor, C14 e C15 no runner, C1 a C4, C7 a C11, C13 e C16 na catraca.

## Sondas

## Parecer
Aprovado no head 35f1cbd3 (`R-REVIEW`). A contradição de A1 foi resolvida pela regra do dono (D2 e D3), e o requisito da Q3 ficou coerente. A2 foi corrigido no próprio item, por isso não vira cartão. O resto do modelo não mudou desde a leitura de 954cae59.
