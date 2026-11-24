---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 14c7e31ede621eff8a7b3d3f63044f05bb9ab115
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E140.20), revalidação por delta do #812 no head 14c7e31e

Volta E140.18: o teste do recomendado fora do delta passa a ter o bloqueante repetido ao lado, para o laço de `fora_do_delta` rodar e o FD10 morrer. A rodada anterior (head 55a57bde, reprovada pelo A2) fica no git.

## Achados
- A1 (recomendado) bin/forge-check:4188 · herdado (A7 da g1-2-3): a repetição é reconhecida só por (id, arquivo). Estado: aberto, vira cartão.

## Revalidação (head 14c7e31e)
**Delta lido:** `forge-check parecer delta docs/reviews/v0480-g1-2-delta.md`, intervalo 55a57bde..ca6cf392. No domínio, só `tests/test_parecer_fora_do_delta.py` (+3 −2, em `test_recomendado_fora_do_delta_passa`). Saída: `revalida: sim (este parecer barrou: o último parecer não é aprovado)`. O resto do intervalo são pareceres (QA, segurança e este review, que em ca6cf392 só tirou os ids que a neutralidade recusa). `bin/forge-check` e os mutantes não mudaram.

**A2 da rodada anterior: resolvido.** O teste agora passa `- A1 (bloqueante) src/a.py:5` (repetido da rodada 1) e `- A2 (recomendado) src/a.py:2`. Com o bloqueante, a saída antecipada de :4182 não dispara, o laço chega ao recomendado e a guarda de :4192 o pula. Sob o FD10, o recomendado fora do delta é recusado e o teste cai. É a correção que o A2 pediu, e o caso continua afirmando 0 recusas.

**Verificadores no head ca6cf392 (código igual ao 14c7e31e):**
- `python3 -m unittest tests.test_parecer_fora_do_delta`: 29 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-g1-2-delta-2.json --processos 1`, o arquivo inteiro: rc=0, FD9 a FD16 mortos, **FD10 morto** (bin/forge-check:4192); FD9 e FD16 por erro do teste.
- O delta não muda guarda nenhuma, e por isso não há mutante novo a declarar.
- CI do #812: no head remoto e18aed40, `bateria (passos)`, `verificações longas`, `instalação` e `árvore já provada na develop` passaram. As 10 partes da suíte estão pendentes, e `bateria (pareceres)` falha porque os pareceres ainda estão presos ao head anterior. A integração espera o CI verde.

## Parecer
Aprovado. O A2 foi corrigido só no teste e o FD10 morre. O A1 é recomendado e vira cartão depois do merge.
