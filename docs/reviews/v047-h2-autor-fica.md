---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: f26b0721cc27c5460c37e910544587bf742126ef
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.64, H2-AUTOR-FICA-ATE-O-MERGE, parte de ferramenta), revalidação 2

Delta lido: `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo 482ee7c7..f26b0721: `hooks/agentes.py` (`vigentes` :246, `reservar_retomada` docstring, `iniciar` :987), 2 fixtures `autor-*` novas, `tests/mutantes/{trava-agente-morto-3,v0440-decisoes-2,v047-h2-autor-fica-3}.json`, `tests/test_hooks.py` (harness do aviso e da cauda) e o índice de fixtures.

Achados da rodada 2: A4 resolvido (M19 e A4 com `de` único na fonte; `ConferirTodas` verde). A5 resolvido: o registro com tipo `SendMessage` vale `min(RESERVA_S, expira_s)` em `vigentes` (:246), e o `SubagentStart` do retomado troca o tipo e o `desde` (:987), o que dá à reserva o prazo normal. As fixtures `autor-retomada-reserva-curta-expira` (a sonda S2, agora código 0) e `autor-retomado-inicio-vira-reserva-do-agente` cobrem os dois ramos. Os mutantes são M23 e M24.

## Achados
- A6 (recomendado) hooks/agentes.py:753 · a hora da recusa `R-TETO` usa `expira_s` para registro com id; na reserva `SendMessage` ela mostra a expiração longa, não `min(RESERVA_S, expira_s)`; use a mesma condição de `vigentes` (:246)

## Parecer
Aprovado. O ramo novo de `iniciar` só converte o registro com o mesmo id e com tipo `SendMessage`. Ele mantém `branches` e `escrita`, e o retorno antecipado não duplica o registro. Os demais registros com id seguem com `expira_s`. O harness agora exige stdout no aviso e confere a cauda pela última ocorrência de `; registro em` (`rpartition`). A6 é só a hora exibida e não muda a decisão da trava.

Mutantes: M23 e M24 declarados, um por guarda nova. Rodei os dois numa cópia (`git archive`) contra `PeloHook.test_fixtures_do_pedido`, e os dois morrem. O resto da mutação fica com o autor (V2).

Verificação (este revisor, no f26b0721):
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_hooks_agentes_autor`: 14 testes, OK.
- A suíte completa fica com o CI do PR (sem PR nesta etapa).
