---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 22a57afc418542f52f1e306f0ddc4e51ed213f57
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 prazo-forge (#888, classe C), delta ecb13af6..22a57afc (E7.56)

Escopo: resolução do merge da develop 020e4af7 (22a57afc). Conflito só em `docs/hooks-fixtures.md` (índice gerado); `tests/test_hooks.py` mesclou sozinho. O código do item (`prazo_vencido`, `hooks/_comum.py`, spec `v0481-prazo-forge.json`) não mudou neste delta (`git diff ecb13af6 22a57afc` sem linha neles). O que veio da develop foi revisado no PR de origem.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guarda do `prazo_vencido` | M1 a M8 de `tests/mutantes/v0481-prazo-forge.json` | PostToolUse, critico None | morreram todos, rc=0 (`rev=22a57afc4185`) |
| Índice gerado entrou igual | `scripts/indice-fixtures.py --conferir` | n/a | "docs/hooks-fixtures.md: em dia" |

## Resultado real
- Mutantes rodados no head: M1..M8 mortos (M4 por erro do teste declarado, com controle verde).
- Duas falhas locais por prazo de 120 s em pesado/mesma-sessao-libera sob carga: passam isoladas nos dois lados (relato do autor), sem relação com o diff.
- CI no head exato: `bateria (passos)`, `bateria (verificações longas)`, `instalação` e `árvore já provada` verdes; `bateria (pareceres)` e `catraca` vermelhos por esperarem os pareceres (excluídos pelo G3); as 10 partes da suíte (3.12 e 3.14) ainda pendentes na leitura. Por isso este parecer não grava a linha de CI verde; ela entra quando as partes fecharem verdes.
