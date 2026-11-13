---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-pr-depois-pareceres
commit: a8e80f2e1944aeee27126b3361afde4cb8345b5d
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v047 (E1.3 PR depois dos pareceres)

Head testado: `a8e80f2e`. Diff contra a base `a986c292`: `agents/tech-lead.md`, `skills/trabalho-em-paralelo/SKILL.md`, `changelog.d/v047-pr-depois-pareceres.md`. Sem PR ainda (a regra é essa): só os testes afetados rodaram local.

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:17 · a linha "Tamanho por risco" foi encurtada, fora do escopo da E1.3, e o teste guarda `TetoPorPr` (tests/test_forge.py:6357) cai em 2 subtestes: faltam "150 linhas alteradas de código e teste" e "uma classe de comportamento por PR em `hooks/`" (R-REVIEW). A base passa.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Regra no tech-lead: PR só abre com pareceres da classe aprovados e commitados no head | leitura do diff `agents/tech-lead.md:36-37` (cita `forge-check classe`, `esperar-estado`, `R-REVIEW`, `R-FLUXO`; a skill e o comando existem) | n/a | passa |
| Ponteiro na skill `trabalho-em-paralelo` (D2) coerente com a regra | leitura do diff `SKILL.md:14` | n/a | passa |
| Regras protegidas por teste continuam presentes | `python3 -m unittest tests.test_forge.TetoPorPr` | frase do teto de 150 linhas e classe única em `hooks/` | FALHA (A1) |

## Provas
- `python3 -m unittest tests.test_forge.TetoPorPr` no head: `Ran 3 tests ... FAILED (failures=2)`, subtestes `arquivo='agents/jarvis.md'` (o texto do Jarvis inclui a skill `trabalho-em-paralelo`) para as duas frases.
- Base: `git show a986c292:skills/trabalho-em-paralelo/SKILL.md` contém as duas frases (1 linha); a regressão vem do diff.
- Suíte inteira não rodada local: a prova dela é o CI do PR. Vermelho antes do verde e mutação: n/a (só texto de regra, sem teste novo).

## Correção sugerida
`tech-lead` (autor): restaurar na linha "Tamanho por risco" de `skills/trabalho-em-paralelo/SKILL.md` o texto "cerca de 150 linhas alteradas de código e teste por PR orientam" e "Vale uma classe de comportamento por PR em `hooks/`, com corpus próprio"; depois reteste `TetoPorPr`.
