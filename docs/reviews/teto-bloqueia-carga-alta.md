---
tipo: review
contrato: 1
pedido: teto-bloqueia-carga-alta
branch: melhoria/teto-bloqueia-carga-alta
commit: bb3dbfc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Parecer de autor: hook `agentes` bloqueia qualquer disparo com carga alta

Escopo: `git diff origin/develop..bb3dbfc`: `hooks/agentes.py` (nova `carga_alta`, chamada em `lancar` antes do teto), fixtures em `tests/hooks/agentes/`, `docs/hooks.md`, `CHANGELOG.md`. `docs/regras/R-TETO.md` não foi tocado: a regra já manda não disparar com load acima de 6 ou menos de 2 GB; só o hook não cumpria.

Parecer: **aprovado** (parecer do próprio autor; o review independente cabe ao revisor do PR).

## Comportamento
- Com load acima de 6 ou menos de 2 GB disponíveis, bloqueia com `R-TETO`, a carga e a memória medidas e "espere a carga baixar", mesmo com 0 ou 1 ativo. `teto_agentes` e `teto_maximo` não desligam. Sem leitura de `/proc` (`None`), `carga_alta` é falso e vale o comportamento de antes.
- Fixtures novas: carga 6,5 com 0 ativos (rc 2), memória 1,5 GB com 1 ativo (rc 2), `teto_agentes` 5 e `teto_maximo` 5 com load 7 (rc 2), carga 5 com 1 ativo (rc 0), sem `/proc` com 0 ativos (rc 0). As duas últimas já passavam antes: são guarda de regressão, não vermelhas.
- Fixtures ajustadas por mudança de comportamento: `adaptativo-2-libera` e `teto-fixo-acima-do-adaptativo` usavam load 7 e esperavam liberar; agora usam load 5. `adaptativo-2-load-bloqueia` e `adaptativo-2-memoria-bloqueia` esperam a nova mensagem.

## Rótulo `afrouxa-regra`
**Não precisa.** `PROTEGIDOS` (`tests/catraca.py`) lista `hooks/conformidade.py`, `hooks/parecer.py`, `hooks/_comum.py`, `bin/forge-check`, workflows e `.githooks/`; `hooks/agentes.py` e `tests/hooks/agentes/` não estão nele, e a mudança endurece a regra. `hooks/` está em `SENSIVEIS`: a catraca exige os pareceres do pedido (este arquivo; o do QA fica a cargo do fluxo).

## Checklist
- Pedido atendido sem extras; reserva de 2 h e o resto do hook intactos. Sem dependência nova, sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).
- `medir()` é chamada uma vez a mais por disparo (duas leituras pequenas de `/proc`): irrelevante frente ao limite de 100 ms.
- Recomendado, não bloqueia: `calcular_teto` ainda tem o ramo `carga > 6 or memoria < 2 -> 2`, agora inalcançável pelo `lancar`; mantido para não alterar a função e seus usos.

## Reversão
Reverter o commit `fix(hooks)`; nenhum estado persistido muda.
