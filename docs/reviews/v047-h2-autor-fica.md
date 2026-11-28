---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 7848dd5cfd55d51a7d8bb1afcef4a7718a8a8d11
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.64, H2-AUTOR-FICA-ATE-O-MERGE, parte de ferramenta), revalidação 6

Delta lido (revalidação 6, E2.82): `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo adf98a9a..7848dd5c. No domínio só `bin/forge-testes` (+ `test_hooks_agentes_autor` em `FORGE_CHECK` e em `REAPROVEITAM_O_LOTE`) e `tests/test_testes_tocados.py` (contagem 92 → 93, com a nota da junção). O módulo novo usa `Hooks.executar_em_lote` pelo lote do test_hooks, então entra em `REAPROVEITAM_O_LOTE` pelo critério do E1.120; a mudança é só de mapa, sem guarda nova. O aviso do delta sobre o merge b942f7c é a junção 32c4832a da branch remota (pareceres), sem código. Fora do domínio, só pareceres. `python3 -m unittest tests.test_testes_tocados tests.test_forge_mutante.ConferirTodas tests.test_hooks_agentes_autor`: 176 testes, OK (skipped=1). CI do PR 639 no head 7848dd5c: suíte verde nas partes concluídas; `bateria (pareceres)` vermelha até os pareceres apontarem o head novo. Não há achado novo; A6 segue recomendado.

Revalidação 5 (histórico):

Delta lido (revalidação 5, E2.76): `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo 981ce8a9..adf98a9a. No domínio só `docs/hooks-fixtures.md`, o índice gerado, regerado pelo script com a fixture `autor-ativo-inicio-repetido-nao-converte` (2886 → 2887; `agentes` 119 → 120, libera 56 → 57; `autor-*` 22 → 23). `python3 -I scripts/indice-fixtures.py --conferir`: "docs/hooks-fixtures.md: em dia". Fora do domínio, só pareceres. Nenhum código do H2 mudou: A6 segue recomendado e não há achado novo.

Revalidação 4 (histórico):

Delta lido (revalidação 4, E2.73): `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo 74e14194..981ce8a9. No domínio: `tests/hooks/agentes/autor-ativo-inicio-repetido-nao-converte.json` (fixture nova) e `tests/mutantes/v047-h2-autor-fica-3.json` (M25). `hooks/` sem mudança. O aviso do delta sobre o merge ca3bf21 é a junção da branch remota (pareceres), sem código. M25 declara a guarda `a.get("tipo") == RETOMADA` de `iniciar` (hooks/agentes.py:987), que a catraca do CI acusou sem mutante. Apliquei M25 à mão: `PeloHook.test_fixtures_do_pedido` falha na fixture nova (o `forge:qa-engineer` ativo vira `forge:software-engineer`), e o arquivo foi restaurado. `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_hooks_agentes_autor`: 14 testes, OK. `python3 -I tests/catraca.py --base origin/develop`: rc=0, sem saída. Não há achado novo; A6 segue recomendado.

Revalidação 3 (histórico):

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
