---
tipo: qa
contrato: 1
pedido: vel-p7-teto
branch: melhoria/vel-p7-teto
commit: c0bfa3e8377c686a86627723dbdc4a8e4a2f335d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: vel-p7-teto

Mudança só de texto (agents/jarvis.md:44 e fragmento changelog.d/vel-p7-teto.md), diff 234dbe0...ae10c85 (1.ª rodada) e, na revalidação, 8c07b44..c0bfa3e. Sem spec de mutantes: nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` mudou.

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

## Revalidação no head c0bfa3e (merge da develop na branch)
- Delta lido (`forge-check delta`, ae10c85..c0bfa3e): a lista traz só o que a develop trouxe no merge (hooks, testes, regras, quadro); o que é da branch é `agents/jarvis.md:46` na leitura do delta (o merge não conflitou; a frase do portão está no parágrafo "Trabalho em paralelo") e o fragmento. Li `git diff 8c07b44 c0bfa3e`: 1 linha em `agents/jarvis.md`, o fragmento e os dois pareceres; nada de código nem de teste.
- Frase do portão ao lado do texto novo da develop: o trecho "sem retorno em 53 min" segue inteiro, com "antes de relançar um lento, confira se o anterior ainda roda" e a regra do dono depois; a linha "Quadro com hora real" da develop está intacta; `agents/jarvis.md` com 109 linhas (limite 110).
- Testes de texto que leem o jarvis.md, no head: `test_clareza`, `test_textos_dono_f10`, `test_textos_dono_f7`, `test_medidas_m14b`, `test_sobreposicao_quadro`, `test_changelog`: `Ran 131 tests`, `OK`; `tests.test_forge`: `Ran 453 tests`, `OK`.
- `scripts/validar-plugin.sh`: `Validation passed`; `scripts/verificar-contribuicao.sh origin/develop`: ok.
- M14 (`agents/tech-lead.md:19`): `git diff --numstat --no-renames origin/develop...HEAD` dá 1+1 linhas em `agents/jarvis.md` (texto `.md`, fora da contagem), 0 linhas de código e de teste, um comportamento só. Cumpre a M14.
- Sem mutantes, sem vermelho (sem teste novo nem código), como na 1.ª rodada.
