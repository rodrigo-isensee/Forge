---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-pid-sandbox
commit: b47610cc2b843b1873c09489abc80bde29cad89d
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
