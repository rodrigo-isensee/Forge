---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde
commit: cc266228af35cfd870a34ab71cb4b3c3e3299f9f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 (develop verde, E1.82)

Head testado: cc266228 (branch: melhoria/v047-develop-verde). Diff sobre a base b27f6985: `skills/esperar-estado/SKILL.md` (2 trechos) e o fragmento de changelog. Sem código de produção e sem guarda: mutação e `forge-mutante` não se aplicam.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pedido E1.79: a frase "pasta gravável (por exemplo, `${TMPDIR:-/tmp}`)" volta à skill | `test_forge.TmpdirComRecuo.test_formas_do_recuo` | texto exato da skill | passou no head; falha na base b27f6985 |
| Texto cabe no teto (skills/*/SKILL.md só desce) | `test_metricas_texto` | teto de métricas do texto | passou (4367 → 4334 bytes) |
| Skill segue guardada | `test_esperar_estado` (15), `test_skills_v0442`, `test_clareza`, `test_jarvis_nucleo`, `test_pesos_teto`, `test_textos_dono_f7`, `test_textos_dono_f10` | laços e regras da skill | passaram |

## Cenários e resultado real
- Vermelho antes do verde: na base b27f6985, `TmpdirComRecuo` sai `FAIL: test_formas_do_recuo`, `FAILED (failures=1)`; no head, `Ran 2 tests ... OK`. É a mesma falha do CI da develop (run 43475743291).
- Os blocos de código do laço do PR não mudaram; só a prosa ("rode na pasta do repositório" saiu).
- Suíte inteira: no CI do PR 538 (sha cc266228) bateria (pareceres), (passos), instalação, catraca e árvore já provada passaram; as partes da suíte estavam pendentes na hora do parecer. Local, só os módulos afetados (54 testes, OK), com carga ~18.
