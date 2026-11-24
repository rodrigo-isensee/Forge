---
tipo: qa
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716-anexo
commit: 51fc24a74534d3ba419d2f7f08c9ae307aa07347
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: release 0.47.16 (E167.8) (versão 0.47.16, head 51fc24a7)

Revalidação da release com o anexo: marca 2b8d11be sobre o corte 35b05bd3 mais o commit 51fc24a7, que só toca `CHANGELOG.md` (12 linhas na seção `[0.47.16]`) e apaga 11 fragmentos de `changelog.d/`. Sem código novo. O parecer de pedido v0478 do anexo está em `docs/qa/v0480-release-04716-anexo.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.16; `## [0.47.16] - 2026-11-24` | manifestos iguais | passou |
| Entrada em português, com o anexo | leitura do diff do CHANGELOG: 12 linhas novas em Adicionado, Alterado e Corrigido, em português | n/a | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | nenhum fragmento sobra | passou |
| Módulos do assunto | `test_changelog.py` (91, OK); `test_conferir_release.py` (17, OK), por `python3 -I -m unittest discover -s tests -p <arquivo>` | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: `Validation passed` (raiz e dev) | n/a | passou |
| Junção | `git merge-base --is-ancestor 35b05bd3 HEAD`: ok | corte igual à Base-sha | passou |
| Sem teste pulado | `git diff v0.47.15..HEAD -- 'tests/*.py'`: nenhum skip, skipTest ou expectedFailure adicionado | n/a | passou |

Sem suíte local; a bateria inteira vale pelo check-run `bateria` do mesmo sha no CI do PR.
