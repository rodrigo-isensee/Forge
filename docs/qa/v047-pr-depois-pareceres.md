---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-pr-depois-pareceres
commit: 2530ab495a98a9521c170aad2a5121d15891f8da
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 (E1.3 PR depois dos pareceres)

Head testado: `2530ab49` (revalidação por delta `a8e80f2e..2530ab49`, volta E1.9; E1.25). Histórico: no head `a8e80f2e` o parecer reprovou por A1. Diff contra a base `a986c292`: `agents/tech-lead.md`, `skills/trabalho-em-paralelo/SKILL.md`, `changelog.d/v047-pr-depois-pareceres.md`. Sem PR ainda (a regra é essa): só os testes afetados rodaram local.

## Achados
Nenhum achado aberto. O A1 do head a8e80f2e (SKILL.md:17) está corrigido: frases do teto restauradas em 2530ab49; `TetoPorPr` passa.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Regra no tech-lead: PR só abre com pareceres da classe aprovados no head | leitura do diff `agents/tech-lead.md:36` (cita `forge-check classe`, `gh pr ready`; comando existe) | n/a | passa |
| Ponteiro na skill `trabalho-em-paralelo` (D2) coerente com a regra | leitura do diff `SKILL.md:14` | n/a | passa |
| Regras protegidas por teste continuam presentes | `python3 -m unittest tests.test_forge.TetoPorPr` | frase do teto de 150 linhas e classe única em `hooks/` | passa (A1 corrigido) |

## Provas
- `forge-check parecer delta`: domínio do QA mudou em `agents/tech-lead.md`, `changelog.d/v047-pr-depois-pareceres.md` e `skills/trabalho-em-paralelo/SKILL.md`. O A4 do review foi revertido: o diff de `tech-lead.md` tira a linha "PR depois dos pareceres" e deixa a do rascunho, com `forge-check classe` e `gh pr ready`.
- `python3 -m unittest tests.test_forge.TetoPorPr` no head: `Ran 3 tests ... OK` (antes: failures=2).
- `python3 -m unittest` em Agentes, Neutralidade, NeutralidadeDoNucleo, RegrasInviolaveis, RegrasComId, Orcamento, TextosDoAgenteEDaRegra: `Ran 23 tests ... OK`.
- Suíte inteira não rodada local (sem PR; a prova é o CI do PR). Vermelho antes do verde e mutação: n/a (só texto de regra, sem teste novo).
