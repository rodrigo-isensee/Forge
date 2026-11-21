---
tipo: qa
contrato: 1
pedido: release-0.47.14
branch: melhoria/v0479-release-04714
commit: 5067fedacf87005b2a96c13e5af4b8d57b32d0fa
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: release 0.47.14 (E76.4) (marca da versão 0.47.14, head 5067feda)

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

## Revalidação no head 5067feda (E76.17)
Delta (`forge-check parecer delta`, d35b56f6..d3c4cbac): no domínio só `CHANGELOG.md` e `docs/engineering/placar-mutacao.md`. A entrada [0.47.14] ganhou os PRs #766 a #775 (K170, cópias em .forge/wt, K339, K152, modelo de pedido, merge de pareceres, forge-pesado, hook agentes), em português; a linha 0.47.14 e a nota do placar entraram no arquivo. Versão 0.47.14 nos dois `plugin.json`, igual à entrada do CHANGELOG, com `[Não publicado]` vazio. `changelog.d/` só com `README.md`. `test_changelog.py` 89 OK; `test_conferir_release.py` 17 OK; `forge-changelog conferir-release` ok; `scripts/validar-plugin.sh` passou nos dois manifestos. Placar `scripts/placar-mutacao.py --desde v0.47.13 --versao 0.47.14`: `placar: 0.47.14 mortos=66 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9`, igual à linha do arquivo. `git diff v0.47.13..5067feda -- tests`: nenhum skip, skipIf ou expectedFailure novo. Sem suíte local; a bateria vale pelo check-run `bateria` do mesmo sha.
