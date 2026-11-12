---
tipo: qa
contrato: 1
pedido: release-0.46.0
branch: melhoria/release-0.46.0
commit: 2e45133689fbddb381d134637cc1e5c6569e8b75
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: release-0.46.0

## Achados
- A1 (recomendado) docs/qa/release-0.46.0.md:1 · o check-run do push em 2e451336 (run 43322893005) ainda corria ao parecer e pulou a bateria por "árvore já provada"; vale a bateria verde do PR #513, de árvore idêntica (d770bd01).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Bateria completa sobre o head | PR #513 (head d375f3f7, merge 2e451336): bateria, suítes 3.12 e 3.14 partes 1 a 3, verificações longas, instalação, catraca, tudo SUCCESS | n/a | passou; árvores de d375f3f7 e 2e451336 iguais (d770bd010349e7a4116ecaf024e5e6159966b719) |
| Teto de pulados | jobs "teto de pulados" (3.12 e 3.14) no PR #513 contra `teto_pulados` = 1 em `tests/config.json` | máximo de pulados | SUCCESS |
| Módulos novos na tabela de pesos | 21 módulos `tests/test_*.py` adicionados desde a main, conferidos em `tests/pesos-d4.json` (179 chaves); os 162 módulos de teste também | suíte vazia ou módulo sem peso | nenhum sem peso; `tests/test_pesos_teto.py` guarda o limite de 225 s |
| Versão e changelog | `.claude-plugin/plugin.json` e `CHANGELOG.md` | n/a | `"version": "0.46.0"` e `## [0.46.0] - 2026-11-12` |
| Leva | `git log origin/main..origin/develop`, `git diff --stat` | n/a | 327 commits, 485 arquivos (+23937/-1873), main 4099658f até 2e451336 |

## Cenários e resultado real
Não rodei a suíte na máquina (R-TETO); a prova é o CI. Esta etapa não repete vermelho antes do verde nem mutantes: valem os pareceres de cada PR da leva. Review, devops e segurança são de outras instâncias. Nenhum defeito encontrado; sem bugs abertos.
