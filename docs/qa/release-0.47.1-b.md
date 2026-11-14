---
tipo: qa
contrato: 1
pedido: release-0.47.1
branch: melhoria/release-0.47.1-b
commit: 5b10ba818345f45e573d3f148c0b3763d4257bcf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: release 0.47.1 sobre o topo da develop (v047, E2.38)

Head `5b10ba81`, base `067b2a9f` (origin/develop). O intervalo só junta ao `CHANGELOG.md` os 2 fragmentos pendentes (PR 562) e apaga os fragmentos; nenhum código muda. Suíte inteira: check-run `bateria` e as suítes 3.12 e 3.14 do PR 562, todos pass no mesmo sha (headRefOid = Revisar-sha).

## Achados
Nenhum.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os 2 fragmentos (mp1311-pre-envio-fabrica, v047-heredocs-orcamento) estão na entrada 0.47.1 | `git diff origin/develop..HEAD`: a linha de cada fragmento aparece em CHANGELOG.md, em Adicionado e Corrigido | fragmento sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Versão 0.47.1 sobe contra a main | `scripts/conferir-release.py --base origin/main` (0.47.0 → 0.47.1); `plugin.json` = 0.47.1 | versão acima da main | passou |
| Testes do changelog e da release | `unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (91, OK) |
| Docs e pareceres no formato | `bin/forge-check docs` | formato do parecer | passou (rc=0) |
| Mutação e vermelho no diff | n/a: o intervalo não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` (0 arquivos); cada item tem parecer próprio | n/a | n/a |

## Provas
- `git rev-parse HEAD` = 5b10ba818345f45e573d3f148c0b3763d4257bcf = `gh pr view 562 headRefOid`
- CI do PR 562 no sha: bateria, catraca, suítes 3.12 e 3.14 (partes 1 a 3) e teto de pulados: pass
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.0 | versão da release: 0.47.1
- `unittest tests.test_changelog tests.test_conferir_release`: Ran 91 tests, OK
- `bin/forge-check docs`: rc=0
