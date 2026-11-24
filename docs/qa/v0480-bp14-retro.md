---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: dbc33e5ab8c11b08e9f14faee40f78e64aa8baeb
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 2
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0480-bp14-retro (PR #833, E145.3)

Diff contra a base 0ed441e9: `skills/kanban-metricas/SKILL.md`, `templates/projeto/docs/retrospectivas/_modelo.md`, fragmento de changelog. Rodei só os testes dos arquivos tocados, sem suíte local; a suíte inteira é o CI do PR.

## Achados
- A1 (bloqueante) skills/kanban-metricas/SKILL.md:34 · a linha nova leva a skill a 4455 caracteres, 160 acima do teto 4295; `test_metricas_texto` cai (R-QA). Enxugar o texto ou mover detalhe, sem subir o teto.
- A2 (bloqueante) docs/retrospectivas/_modelo.md:8 · o modelo do projeto mudou e o da própria fábrica não; `test_retro_pendentes` exige os dois iguais e cai. Aplicar a mesma tabela nos dois.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E145.1: tabela pedido × não entregue na skill e no modelo | `test_metricas_texto.test_nenhuma_metrica_passa_do_teto` | teto de caracteres da skill | falhou (A1) |
| E145.1: modelo do projeto igual ao da fábrica | `test_retro_pendentes.test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais` | igualdade entre os dois modelos | falhou (A2) |
| Orçamento de instrução | `test_orcamento_instrucao` (8) | n/a | passou |
| Modelos de projeto e citados | `test_modelos_projeto` (25), `test_modelos_citados` (3) | n/a | passou |
| Neutralidade dos arquivos tocados | `-k Neutral` (57) | termos proibidos | passou |
| Demais testes de retro e métricas | `test_retro_pendentes` (19 de 20), `test_metricas_texto` (1 de 2) | n/a | passou |

## Cenários e resultado real
Comando: `python3 -I -m unittest discover -s tests -p <módulo>.py` por módulo.
- `test_metricas_texto`: FAILED (failures=1), `skills/kanban-metricas/SKILL.md: caracteres = 4455 passa do teto 4295 em 160`.
- `test_retro_pendentes`: FAILED (failures=1), os textos de `docs/retrospectivas/_modelo.md` e do template diferem pela tabela nova.
- Os dois testes que caem existiam antes; a queda vem do diff, então não é dívida pré-existente.
- Vermelho antes do verde e mutação: não se aplicam, o diff é só texto e não traz teste novo.
