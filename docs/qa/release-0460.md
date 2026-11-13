---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/release-0460
commit: 0f86e07e71bf8ca8473f689fec645a5b4177a344
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: release 0.46.0 (E23.65)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Entrada 0.46.0 traz os 26 fragmentos, sem perder nem inventar item | comparação por contagem de itens (62 bullets dos 26 fragmentos em a1318e88 contra 62 adicionados no CHANGELOG, multiconjunto igual) | n/a | passou |
| Duas versões batem | diff dos dois plugin.json: só `version` 0.45.5 → 0.46.0, nos dois | n/a | passou |
| Nada além mudou | `git diff --name-status a1318e88..0f86e07e`: M CHANGELOG.md, M os dois plugin.json, 26 D em changelog.d; README.md de changelog.d fica | pasta changelog.d só com README | passou |
| Formato do changelog | `python3 -m unittest tests.test_changelog` (69 testes) e `bin/forge-changelog conferir --base a1318e88` | n/a | passou |

## Cenários e resultado real
- 26 fragmentos apagados (git diff --diff-filter=D); nenhuma linha removida do CHANGELOG (0 linhas `-`); seção `## [Não publicado]` preservada acima de `## [0.46.0] - 2026-11-12`, e `[0.45.5]` logo abaixo.
- Comparação: 62 itens nos fragmentos, 62 no CHANGELOG, perdidos [], inventados []. Linhas dos fragmentos que não são item nem título de seção: nenhuma.
- `bin/forge-changelog conferir --base a1318e88`: rc 0 ("PR de release (versão mudou): o changelog fechado é conferido na promoção para a main").
- Sem vermelho antes do verde: o commit não traz teste novo nem regra nova (só dados de release); sem mutação aplicável (nenhum arquivo de `bin/`, `hooks/`, `.githooks/`).
- CI do PR #508 (`gh pr checks 508`, run 43291439285) no momento da conferência: passando (passos, verificações longas, catraca, instalação 3.14, suíte 3.12 partes 2 e 3, 3.14 partes 2 e 3, árvore já provada na develop); pendentes: suíte 3.12 parte 1/3 e 3.14 parte 1/3. O portão é o CI completo; este parecer não o substitui.

## Provas
- PQ-1: `git log --format=%H -1 0f86e07e71bf8ca8473f689fec645a5b4177a344` saiu `0f86e07e71bf8ca8473f689fec645a5b4177a344`.
