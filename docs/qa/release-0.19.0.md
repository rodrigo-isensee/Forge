---
tipo: qa
contrato: 1
pedido: release-0.19.0
branch: melhoria/release-0.19.0
commit: 700283f958e6b4d42b219b20f95e4c11a13cb2d9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - release-0.19.0 (versão 0.19.0: M-2, TA-5, TA-3, S-9, PA-4, CLAREZA-PACOTE-1)

Sem UX nem API. Diff `27b920f...700283f`: 8 arquivos (`.claude-plugin/plugin.json`, `CHANGELOG.md`, seis fragmentos apagados de `changelog.d/`). O HEAD da branch (e2dada8) só acrescenta o review (`parecer: aprovado`, `commit: 700283f`) sobre o commit testado. Não escrevi o diff. Sem mutação nem vermelho-antes-do-verde: o diff não traz código nem teste novo (versão e texto de changelog).

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-0 | Review aprovado no commit da release | leitura de `docs/reviews/release-0.19.0.md` | portão R-REVIEW | `parecer: aprovado`, `commit: 700283f958e6b4d42b219b20f95e4c11a13cb2d9` |
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 774 testes, OK, 122,0 s |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| V-1 | Nenhum fragmento pendente | `bin/forge-changelog conferir-release` | `changelog.d/` vazio | `ok: changelog.d/ sem fragmentos pendentes`, rc=0; `ls changelog.d` vazio |
| V-2 | Mudança na fábrica com versão nova | `bin/forge-changelog conferir --base origin/develop` | PR de release | base 0.18.0, PR 0.19.0, rc=0 |
| V-3 | Gate da main (`ci.yml:132-153`) contra origin/main | mesma conta em Python: `a > b`, entrada `## [0.19.0]`, `[Não publicado]` vazio | versão não sobe; seção aberta | 0.19.0 > 0.18.0 verdadeiro; entrada existe (1); `[Não publicado]` vazio |
| EX-1 | Seção 0.19.0 na ordem e formato das versões anteriores | leitura do `CHANGELOG.md:7-18` contra 0.18.0 e 0.17.0 | ordem Adicionado, Alterado, Corrigido; data ISO | `## [0.19.0] - 2026-10-16` logo após `[Não publicado]`, antes da 0.18.0; `###` na ordem Adicionado, Alterado, Corrigido, um de cada, sem linha em branco entre cabeçalho e itens, igual às anteriores |
| EX-2 | Cada item da versão uma vez | script: 6 itens `- ` na seção, 6 distintos; cada um bate com um dos seis fragmentos do diff | perda ou duplicação | 6 de 6, sem repetição (clareza, TA-3, TA-5 em Adicionado; PA-4 em Alterado; M-2, S-9 em Corrigido) |
| EX-3 | Versão no `plugin.json` | diff | minor | `0.18.0` -> `0.19.0`, só essa linha |
| EX-4 | Escopo do diff | `git diff --stat` | nada fora dos 8 arquivos | confere; de 700283f a HEAD só `docs/reviews/release-0.19.0.md` |

## Bugs
Nenhum. Sem arquivo em `docs/qa/bugs/`.

## Observações (sem bug)
- A data 2026-10-16 coincide com a da 0.18.0 (mesma data é válida no formato; já anotado no review).
- O gate do `forge-check pr` só passa depois deste parecer commitado (PA-4); a repetição do comando consta no relatório da delegação.
- O stderr do validador mostra tentativas de rede negadas pelo sandbox (host da API e de telemetria); a validação passou assim mesmo.

## Resultado da execução
2026-10-16, WSL2, python 3.10, worktree ~/.forge-contrib/wt/release-0.19.0: 774 testes OK; validação do plugin OK; `conferir-release` e `conferir` OK; gate da main contra origin/main (0.18.0) OK; exploratório do CHANGELOG sem achado. Sem bug aberto, por isso sem `aceite_usuario`.
