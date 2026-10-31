---
tipo: revisao-seguranca
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c3
commit: e8f5822c32062e84398abf565d6868ddf0f0e2d5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-pre-push (branch c3)

Diff revisado: `234dbe0..e8f5822` (código em `5a89d72`, fragmento em `e945d09`, parecer do code review em `e8f5822`). Análise estática contra o modelo de ameaças `docs/security/ameacas/pre-push.md` (controle C-8).

## Gatilhos
`R-SEGURANCA`: controle do Forge (`.githooks/pre-push`, modo `--status`).

## Item entregue e M14
- Entrega a dica do `--suite` do E2 do pedido (C3 do desenho, SUITE-INICIO-ATOMICO).
- M14: 2 linhas de código e teste (`.githooks/pre-push` 1, `tests/test_pre_push_trava.py` 1); um comportamento só. Cumpre.

## Conferência dos controles
- C-8: `.githooks/pre-push:97` imprime texto fixo, sem dado da trava, só no ramo em que a suíte está rodando (rc 0 inalterado). Aponta `.githooks/pre-push --suite`, que espera a vez ou falha fechado.
- Teste T-C3 em `tests/test_pre_push_trava.py:181`, dentro de `test_status_acompanha_a_trava`.
- Nenhum caminho de push alterado; nada novo a ameaçar.

## Achados

## Detalhe dos achados
Sem achados.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Leitura do diff e do hook no commit revisado. `shellcheck` e `gitleaks` ausentes do PATH nesta máquina (lacuna; o CI roda o `shellcheck` no hook). Nenhuma ferramenta instalada.
