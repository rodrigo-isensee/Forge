---
tipo: qa
contrato: 1
pedido: release-0.47.15
branch: melhoria/v0480-release-04715
commit: a151f1d254124ebb23e4f82f1a8bd44404c53f06
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: release 0.47.15 (E125.7) (versão 0.47.15, head a151f1d2)

Marca sobre o corte f4836717 (base develop). Diff v0.47.14..HEAD: 201 arquivos, 35 commits. A marca (3b6cfad5) só toca os dois `plugin.json`, `CHANGELOG.md`, `docs/engineering/placar-mutacao.md` e apaga os 21 fragmentos de `changelog.d/`; o resto é dos PRs #776 a #799, cada um com os próprios pareceres, mutação e vermelho-antes-do-verde. Sem código novo na marca. O parecer de pedido v0478 (marca) já existe aprovado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.15 (a tag v0.47.14 tinha 0.47.14); `## [0.47.15] - 2026-11-22` com `[Não publicado]` vazio acima | manifestos iguais | passou |
| Entrada em português | leitura da entrada: Adicionado, Alterado, Corrigido, em português | n/a | passou |
| `changelog.d/` sem fragmentos | `ls changelog.d`: só `README.md`; `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | nenhum fragmento sobra | passou |
| Módulos do assunto | `python3 -I -m unittest discover -s tests -p test_changelog.py` (89, OK); `test_conferir_release.py` (17, OK) | n/a | passou |
| Junção | `origin/develop` = f4836717 = corte e é ancestral do head; `git log v0.47.14..HEAD`: 35 commits (PRs #776 a #799 mais marca e pareceres) | corte igual à base | passou |
| Sem teste pulado | `git diff v0.47.14..HEAD -- 'tests/*.py'`: nenhum decorador skip, `skipTest` ou `expectedFailure` novo (as ocorrências de "skip" são texto de specs de mutante e nomes de teste que guardam essa regra) | n/a | passou |

Sem suíte local; a bateria inteira vale pelo check-run `bateria` do mesmo sha no CI do PR.
