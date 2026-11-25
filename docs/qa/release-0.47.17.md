---
tipo: qa
contrato: 1
pedido: release-0.47.17
branch: melhoria/marca-0.47.17
commit: d2a9d91914d65aa6eb2daca515c89d0907226c85
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: release 0.47.17 (E12.9) (versão 0.47.17, head d2a9d919)

QA da versão inteira para a promoção: `git diff v0.47.16..d2a9d919` (27 commits, 261 arquivos). Cada item entrou na develop com os próprios pareceres; aqui se confere a junção, a marca, o CHANGELOG e os manifestos. Modelo: `docs/qa/release-0.47.16.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.17; `## [0.47.17] - 2026-11-25` | manifestos iguais | passou |
| CHANGELOG em português, `[Não publicado]` vazio | leitura da seção: 22 linhas de item (12 Adicionado, 6 Alterado, 4 Corrigido), todas em português | seção nova acima da 0.47.16 | passou, ver nota |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` (resta só `README.md`) | nenhum fragmento sobra | passou |
| Junção | `git merge-base --is-ancestor v0.47.16 HEAD`: ok; o último commit d2a9d919 só toca `CHANGELOG.md` (+1) e apaga `changelog.d/v0481-fechar-ci-topo.md` | corte contém a tag anterior | passou |
| Módulos do assunto | `test_changelog.py` (91, OK); `test_conferir_release.py` (17, OK), por `python3 -I -m unittest discover -s tests -p <arquivo>` | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: `Validation passed` (raiz e dev) | n/a | passou |
| Sem teste pulado indevido | `git diff v0.47.16..HEAD -- 'tests/*.py'`: nenhum `skip`, `skipTest` ou `expectedFailure` real novo; os que aparecem são texto de fixture do teste da catraca. Único `skipUnless(hasattr(os, "mkfifo"))`: guarda de plataforma, não decide o que o teste cobre | n/a | passou |

Nota: o brief diz 21 itens; o CHANGELOG tem 22. O 22º é o do #880 (`forge-fechar`, CI do topo), que o commit d2a9d919 acrescentou depois da contagem do brief. Entrada e fragmento apagado batem; não é defeito.

## Execução
- CI do PR #882, mesmo sha: `bateria (pareceres)`, `bateria (passos)` e `bateria (verificações longas)` passaram; as 10 partes de `suíte` (3.12 e 3.14) estavam pendentes na minha leitura. A suíte inteira vale pelo CI do PR: o `tech-lead` só mescla com tudo verde. Sem suíte local.
- Sem código novo nesta junção; a prova de cada item está no parecer do próprio pedido.
