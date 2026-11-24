---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: 1df3df9ae7715dcf602b6cf7bff8159ecdbc0bf0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0480-bp14-retro (PR #833, E145.7, delta da volta E145.5)

Delta `dbc33e5a..1df3df9a` (`forge-check parecer delta`): `skills/kanban-metricas/SKILL.md`, `docs/retrospectivas/_modelo.md`, `templates/projeto/docs/retrospectivas/_modelo.md`. Os dois achados da rodada anterior (A1 teto da skill, A2 modelos diferentes) foram corrigidos: a tabela virou instrução no comentário do modelo, os dois modelos ficam byte a byte iguais (`cmp` sem diferença) e a skill voltou ao teto. Rodei só os testes dos arquivos tocados, sem suíte local; a suíte inteira é o CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: skill dentro do teto | `test_metricas_texto` (2) | teto de caracteres | passou (era a falha) |
| A2 anterior: modelos igual | `test_retro_pendentes` (20) | igualdade fábrica × projeto | passou (era a falha) |
| Medidas das métricas | `test_medidas_m14b` (73) | n/a | passou |
| Orçamento, modelos | `test_orcamento_instrucao` (8), `test_modelos_projeto` (25), `test_modelos_citados` (3) | n/a | passou |
| Neutralidade | `-k Neutral` (57) | termos proibidos | passou |

## Cenários e resultado real
Comando: `python3 -I -m unittest discover -s tests -p <módulo>.py`.
- `test_retro_pendentes`: Ran 20, OK. `test_metricas_texto`: Ran 2, OK. `test_medidas_m14b`: Ran 73, OK.
- Vermelho antes do verde e mutação: não se aplicam; o delta é só texto e não traz teste novo. Os dois testes que caíam no parecer anterior agora passam.
- Observação sem gravidade: a tabela pedido × não entregue saiu do corpo do modelo e ficou só descrita em comentário HTML (que o `retro --pendentes` não conta como corpo); decisão de forma do autor, não contraria teste nem critério.
