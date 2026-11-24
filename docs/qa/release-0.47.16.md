---
tipo: qa
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716
commit: 2b8d11be7024106a2fd96f41633676f45d93595e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: release 0.47.16 (E167.4) (versão 0.47.16, head 2b8d11be)

Marca sobre o corte 35b05bd3 (base develop; ancestral do head). A marca (2b8d11be) só toca os dois `plugin.json`, `CHANGELOG.md`, `docs/engineering/placar-mutacao.md` e apaga os 36 fragmentos de `changelog.d/`; o resto é dos PRs anteriores, cada um com os próprios pareceres. Sem código novo. O parecer de pedido v0478 (marca) existe aprovado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.16 (antes 0.47.15); `## [0.47.16] - 2026-11-24` com `[Não publicado]` vazio acima | manifestos iguais | passou |
| Entrada em português | leitura da entrada: Adicionado, Alterado, Corrigido, em português | n/a | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | nenhum fragmento sobra | passou |
| Módulos do assunto | `test_changelog.py` (91, OK); `test_conferir_release.py` (17, OK), por `python3 -I -m unittest discover -s tests -p <arquivo>` | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: `Validation passed` (raiz e dev) | n/a | passou |
| Junção | 35b05bd3 é ancestral do head; `origin/develop` (6161978d) passou do corte, sem conflito | corte igual à Base-sha | passou |
| Sem teste pulado | `git diff v0.47.15..HEAD -- 'tests/*.py'`: nenhum decorador skip, `skipTest` ou `expectedFailure` novo | n/a | passou |

Sem suíte local; a bateria inteira vale pelo check-run `bateria` do mesmo sha no CI do PR.
