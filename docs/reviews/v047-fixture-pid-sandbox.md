---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-pid-sandbox
commit: b645e83c35c7dc51a125ccdca2401b5d73800bb9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (E1.108, fixture-pid-sandbox)

## Achados
- A1 (recomendado) tests/test_hooks.py:699 · o pulo por subTest não passa por `exigir` nem por PODEM_PULAR (lista fechada de apoio_sandbox); está atrás de `sinais_de_ci()`, mas o afrouxamento merece o mesmo parecer de segurança da lista.
- A2 (recomendado) tests/mutantes/v047-fixture-pid-sandbox.json:1 · só o M1 está declarado; as guardas de CI (`None if sinais_de_ci()`, `motivo and not sinais_de_ci()`) e `if not motivo` não têm mutante; só se provam com CI definido.

## Sondas

## Parecer
Aprovado. Classe C, 58 linhas de código e teste, um comportamento só (abaixo do teto M14). O hook não muda. O pulo só vale quando `/proc/<pid>/ns/pid` do pai não se lê, e nunca com `CI` ou `GITHUB_ACTIONS` definidos.

Lido e executado no head:
- O teste de unidade do pulo passa: 4 puladas com motivo, as outras seguem, sem motivo nada pula.
- Com `CI=1` e o ns ilegível, o teste do caso legível reprova (4 falhas, as fixtures rodam), então não pula: confere a nota do brief.
- Sem CI, esse teste sai pulado com motivo. O M1 dá "controle vermelho" no sandbox, o esperado pelo brief: só morre no CI, que roda a suíte inteira.
- Os motivos de A1 e A2 não são defeito provado, por isso ficam recomendados.
- Suíte inteira: CI do PR (não há PR; sem rerrodar o SHA).

## Revalidação (E1.122, delta b47610cc..b645e83c)
Delta lido por `forge-check parecer delta`: `bin/forge-testes`, `tests/mutantes/v047-fixture-pid-sandbox.json`, `tests/test_hooks.py`, `tests/test_testes_tocados.py`. Aprovado, sem achado novo; A1 e A2 seguem recomendados (A2 ganhou o M2).
- O pulo virou função do módulo (`pular_sem_ns_de_pid(teste, casos, motivo)`), mesma lógica; as classes que reaproveitam `Hooks.executar_em_lote` sem herdar de `Hooks` já não quebram. `test_hook_ansi_c` (reaproveita o lote) passa: 12 testes OK.
- O pulo segue só sem `/proc` legível e nunca com CI (`None if sinais_de_ci()`); o teste de unidade do pulo passa.
- Mapa: `JUNTO_DO_MODULO` leva `REAPROVEITAM_O_LOTE` quando `tests/test_hooks.py` é pedido pelo caminho; o teste novo varre os módulos reais com mínimo de 8. Passa; com o M2 aplicado (`JUNTO_DO_MODULO = {}`) reprova (mutante morto).
- Mudanças de passagem: `nucleos_do_processo` e `fator_de_carga` vêm de `apoio_volta_unica` (import no fim por causa do ciclo) e o teto do teste do `gh` pendurado escala com a carga; sem guarda nova.
- Suíte inteira: CI do PR (não há PR; sem rerrodar o SHA).
