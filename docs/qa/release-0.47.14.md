---
tipo: qa
contrato: 1
pedido: release-0.47.14
branch: melhoria/v0479-release-04714
commit: d35b56f6087072354d6a25d976a9fa94329d3010
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: release 0.47.14 (E76.4) (marca da versão 0.47.14, head d35b56f6)

Marca sobre o corte 5e3ca873 (base develop). Diff v0.47.13..HEAD: 332 arquivos, 30 commits; o commit da marca (d35b56f6) só toca `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json` e `CHANGELOG.md`. Sem código novo na marca: sem mutação nem vermelho-antes-do-verde nela (cada item trouxe os seus nos PRs).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.14 (a tag v0.47.13 tinha 0.47.13); `## [0.47.14] - 2026-11-21` com `[Não publicado]` vazio acima | manifestos iguais | passou |
| Entrada em português | leitura da entrada: Adicionado, Alterado, Corrigido, em português | n/a | passou |
| `changelog.d/` sem fragmentos | `ls changelog.d`: só `README.md`; `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | nenhum fragmento sobra | passou |
| Módulos do assunto | `python3 -I -m unittest discover -s tests -p test_changelog.py` (89, OK); `test_conferir_release.py` (17, OK) | n/a | passou |
| Junção | `origin/develop` = 5e3ca873 = corte; `git log 5e3ca873..HEAD` = 1 commit (a marca); v0.47.13..HEAD: 30 commits (PRs #745 a #765, com a história do #752 que já trouxe merge da develop e merge de PR); 42 arquivos de parecer em docs/qa, docs/reviews e docs/security no diff | corte igual à base | passou |

Sem suíte local; a bateria inteira vale pelo check-run `bateria` do mesmo sha no CI do PR.
