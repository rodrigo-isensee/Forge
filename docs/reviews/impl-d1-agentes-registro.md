---
tipo: review
contrato: 1
pedido: impl-d1-agentes-registro
branch: melhoria/impl-d1-agentes-registro
commit: 195e36ca91db52bb6ce9fd25d8e7a603c130537c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-d1-agentes-registro

Etapa E1.2 do pedido. Diff lido: `c092f1b7abf62037147c068aa3e1208b7b046f92..195e36ca91db52bb6ce9fd25d8e7a603c130537c` (26 arquivos: `hooks/agentes.py`, `docs/hooks.md`, `tests/test_hooks.py`, 22 fixtures em `tests/hooks/agentes/`, fragmento `changelog.d/impl-d1-agentes-registro.md`). Base do desenho: proposta F1 §1 e modelo de ameaças L1 §2.1 com os controles C1-1 a C1-8. O parecer de segurança é do `security-engineer` (`docs/security/impl-d1-agentes-registro.md`); aqui não se refaz.

## Achados

## Parecer
Aprovado. A entrega faz o C1 do desenho e nada além; o C2 ficou fora, como o desenho manda sem a reprodução.

Conferência contra os controles:
- C1-1: `pid_valido` (`hooks/agentes.py:117`) exige inteiro não booleano em `1..pid_max` (lido do `/proc`, padrão 4194304), e `sessao_morta` (`hooks/agentes.py:121`) só devolve True no `ProcessLookupError`; `pid_vivo` cru não decide a saída. Caso do pid_max: acima do limite mantém (fixture `pid-acima-do-limite-mantem`), e o morto dos testes é PID real encerrado (`{pid_morto}`), não um acima do limite.
- C1-2: `vigentes` (`hooks/agentes.py:151`) avalia cada registro num `try` que, no erro, mantém; assinatura igual. O `except Exception` traz o motivo no comentário.
- C1-3: `pidns` gravado e comparado; ausente, de tipo errado ou diferente mantém (três fixtures).
- C1-4: `da_sessao` (`hooks/agentes.py:137`) só grava `pid` vivo, válido e fora de `CASCAS`, com `session_id` presente.
- C1-5: `iniciar` casa só a reserva da mesma sessão; sem `session_id` o confirmado perde `pid`; o registro sem par leva os dados do próprio evento.
- C1-6: nenhuma variável de ambiente nova; vivo é o PID do próprio teste.
- C1-8: teto, duplicado, trava de carga, `expiracao_horas` e `RESERVA_S` intocados.

Legibilidade e estrutura: funções pequenas com docstring de contrato; importa `CASCAS`, `pid_da_sessao` e `pid_vivo` de `pesado` sem mexer em `_comum.py`, como o desenho pede. `docs/hooks.md` e a docstring do módulo foram atualizados na mesma entrega. Fragmento no formato do `bin/forge-changelog` e com o nome da branch sem prefixo. Commits: dois, Conventional Commits em português, cada um coerente.

Testes: 22 fixtures cobrem os casos de abuso do L1 que tocam o código (tipos, faixa, namespace, sessão viva e morta, duplicado, início com e sem sessão), mais o teste unitário de `sessao_morta`, `vigentes` e `da_sessao` (com `PermissionError` e erro por registro simulados). Rodado aqui: `python3 -m unittest tests.test_hooks` → `Ran 42 tests in 74.404s` / `OK`. `forge-check pr impl-d1-agentes-registro` antes deste parecer: só faltavam os pareceres de review e de QA, nada de código. A suíte completa roda no pre-push deste envio.

Recomendações (não bloqueiam):
- `hooks/agentes.py:227`: com a sessão provada, o `SubagentStart` ainda casa a reserva sem `sessao` (registro antigo ou reserva em que `da_sessao` voltou vazio). É seguro, porque o confirmado fica sem `pid` e cai no prazo, mas é mais largo que a letra do C1-5; um comentário dizendo isso evitaria a dúvida na próxima leitura.
- `hooks/agentes.py:117`: `pid_max()` relê o `/proc` a cada registro; custo desprezível com o teto atual, mas cabe ler uma vez por chamada de `vigentes` se o registro crescer.
