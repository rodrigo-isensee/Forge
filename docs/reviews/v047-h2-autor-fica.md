---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 74e14194c106bdbeb8ed36678654dc27de7cf658
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.64, H2-AUTOR-FICA-ATE-O-MERGE, parte de ferramenta), revalidação 3

Delta lido (revalidação 3): `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo f26b0721..74e14194, escopo sem o que veio da develop. No domínio só ficou `docs/hooks-fixtures.md`, o índice gerado, cujo conflito a junção de bda457e4 resolveu regerando pelo script (`git show --remerge-diff 74e14194`: 1 linha a mais, 5 a menos). `python3 -I scripts/indice-fixtures.py --conferir`: "docs/hooks-fixtures.md: em dia". O aviso do delta sobre o merge 27bdaab trata da junção da própria branch remota (pareceres), sem código. Nenhum código do H2 mudou: A6 segue recomendado e não há achado novo.

Revalidação 2 (histórico):

Delta lido: `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo 482ee7c7..f26b0721: `hooks/agentes.py` (`vigentes` :246, `reservar_retomada` docstring, `iniciar` :987), 2 fixtures `autor-*` novas, `tests/mutantes/{trava-agente-morto-3,v0440-decisoes-2,v047-h2-autor-fica-3}.json`, `tests/test_hooks.py` (harness do aviso e da cauda) e o índice de fixtures.

Achados da rodada 2: A4 resolvido (M19 e A4 com `de` único na fonte; `ConferirTodas` verde). A5 resolvido: o registro com tipo `SendMessage` vale `min(RESERVA_S, expira_s)` em `vigentes` (:246), e o `SubagentStart` do retomado troca o tipo e o `desde` (:987), o que dá à reserva o prazo normal. As fixtures `autor-retomada-reserva-curta-expira` (a sonda S2, agora código 0) e `autor-retomado-inicio-vira-reserva-do-agente` cobrem os dois ramos. Os mutantes são M23 e M24.

## Achados
- A6 (recomendado) hooks/agentes.py:753 · a hora da recusa `R-TETO` usa `expira_s` para registro com id; na reserva `SendMessage` ela mostra a expiração longa, não `min(RESERVA_S, expira_s)`; use a mesma condição de `vigentes` (:246)

## Parecer
Aprovado. O ramo novo de `iniciar` só converte o registro com o mesmo id e com tipo `SendMessage`. Ele mantém `branches` e `escrita`, e o retorno antecipado não duplica o registro. Os demais registros com id seguem com `expira_s`. O harness agora exige stdout no aviso e confere a cauda pela última ocorrência de `; registro em` (`rpartition`). A6 é só a hora exibida e não muda a decisão da trava.

Mutantes: M23 e M24 declarados, um por guarda nova. Rodei os dois numa cópia (`git archive`) contra `PeloHook.test_fixtures_do_pedido`, e os dois morrem. O resto da mutação fica com o autor (V2).

Verificação (este revisor, no 74e14194): `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_hooks_agentes_autor`: 14 testes, OK.

Verificação anterior (no f26b0721):
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_hooks_agentes_autor`: 14 testes, OK.
- A suíte completa fica com o CI do PR (sem PR nesta etapa).
