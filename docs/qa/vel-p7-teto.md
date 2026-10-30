---
tipo: qa
contrato: 1
pedido: vel-p7-teto
branch: melhoria/vel-p7-teto
commit: ae10c85731aacab165aea36f10335e889a89721e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: vel-p7-teto

Mudança só de texto (agents/jarvis.md:44 e fragmento changelog.d/vel-p7-teto.md), diff 234dbe0...ae10c85. Sem spec de mutantes: nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` mudou.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (limite de 53 min dito na mesma linha, com a conferência do anterior mantida) | `grep -c '53 min' agents/jarvis.md` = 1; `grep -n 'confira se o anterior ainda roda'` acha só a linha 44 | n/a | passou |
| E1 (sem linha nova, arquivo em 109 de 110) | `wc -l agents/jarvis.md` = 109 | limite de 110 linhas | passou |
| E2 (invariante só se a fábrica proteger o trecho) | `grep` em `tests/config.json`: o trecho não é invariante; nada a atualizar | n/a | passou |
| E2 (fragmento do changelog) | `tests.test_changelog` | formato do fragmento | passou |
| Estrutura dos agentes e regras | `tests.test_forge` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge tests.test_changelog` sobre ae10c85: `Ran 496 tests in 152.598s`, `OK (skipped=1)` (o skip é anterior ao pedido, não foi introduzido aqui).
- `scripts/verificar-contribuicao.sh origin/develop`: `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.`, rc=0.
- PA-7 conferido: AR-9 (limite antigo no texto): nenhum outro texto de agents, skills, docs/regras ou docs/engineering cita o relançamento ou outro limite de espera para o portão; AR-1 e AR-2 não se aplicam (sem mutante nem guarda); AR-3 a AR-8 e AR-10 não se aplicam (sem código nem hook).
- Vermelho antes do verde: não se aplica, não há teste novo nem regra com teste.
- Observação: o limite de 53 min é texto de processo do Jarvis, sem execução por script; não há comportamento automatizável para testar.
