---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-agente-preso-baixa
commit: af5dde244f771d0bf2f1b45e1ddc9c41128e685f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 agente preso sem baixa (#963, classe C, E12.14, volta 1)

Delta 2a310c7c..af5dde24 (`forge-check parecer delta`: `tests/mutantes/trava-agente-morto.json` e `tests/test_agente_preso_baixa.py`). O M6 foi realinhado ao de/para da linha 492 de `hooks/agentes.py` (que termina em ":") e a sonda S9 virou comentário do teste. O mérito do código passou na 1ª rodada (2a310c7c) e não mudou; o A1 daquela rodada está resolvido.

- ci: af5dde244f771d0bf2f1b45e1ddc9c41128e685f verde (run 46162734439: `suíte (python 3.12, partes 1/5 a 5/5)`, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação` e `catraca (conferência)` verdes; fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo)

## Resultado do delta
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_agente_preso_baixa` · Ran 22 tests, OK (a conferência das specs com a fonte, que era o A1, passa).
- `bin/forge-mutante tests/mutantes/trava-agente-morto.json` · `rev=af5dde244f77`; M1 a M8 `morreu`, entre eles `M6 · morreu · hooks/agentes.py:492` pelo teste declarado `C1NotificacaoDoClaudeCode.test_mensagem_do_usuario_nao_libera`. Sem sobrevivente.
- O M6 realinhado guarda a mesma condição (promptSource system); foi realinhado, não retirado.
- Critério → teste → resultado da 1ª rodada segue valendo; a linha "specs conferem com a fonte" agora passa (fronteira: `de` presente na fonte).

## Achados
- A2 (recomendado) hooks/agentes.py:1510 · Mutantes M6, M7 e M12 morrem por erro (exceção sob o mutante), não por asserção; o comportamento guardado só se prova pela exceção. Afirmar a mensagem de stderr no unitário. Da 1ª rodada, fora do delta; vira cartão.
- A3 (recomendado) hooks/agentes.py:481 · No transcript real, 126 de 2801 notificações de agente vêm sem tool-use-id (agente retomado); C2 as recusa e esse caso segue sem baixa. Registrar como limite conhecido. Da 1ª rodada, fora do delta; vira cartão.
