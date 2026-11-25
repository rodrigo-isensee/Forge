---
tipo: qa
contrato: 1
pedido: release-0.47.18
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: release 0.47.18 (E12.15) (versão 0.47.18, head 217e73ed)

QA da versão inteira para a promoção: `git diff 5fb8e328..217e73ed` (5 commits: #887, #889, #891, #893 e a marca; 49 arquivos, +1914 -88; `5fb8e328` é a marca da 0.47.17 e ancestral do head). Cada item entrou na develop com os próprios pareceres de review, QA e segurança (`docs/{reviews,qa,security}/v0481-{corte-completo,copia-mensagem,catraca-ajudante,g3-testes-uma-vez}.md`, os quatro de QA `aprovado`). Aqui se confere a junção, a marca, o CHANGELOG e os manifestos. Modelo: `docs/qa/release-0.47.17.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.18; `## [0.47.18] - 2026-11-25` | manifestos iguais | passou |
| CHANGELOG em português, `[Não publicado]` vazio | leitura da seção: 4 itens (1 Adicionado, 1 Alterado, 2 Corrigido), todos em português, cada um com o id de origem (E8.1/E8.5, E13.15, E14.14/E14.23, E14.2) | seção nova acima da 0.47.17 | passou |
| Os 4 itens do corte estão na seção | os 4 fragmentos da base (`eeb81062`) buscados literal no CHANGELOG: 8/8 linhas | 4 itens, nenhum a mais, nenhum a menos | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | sobra só `README.md` | passou |
| A marca é reprodutível | clone em `eeb81062` + `bin/forge-changelog release 0.47.18 2026-11-25`: árvore idêntica à de `217e73ed` | n/a | passou |
| Junção | `git merge-base --is-ancestor 5fb8e328 HEAD`: ok; os 4 PRs na ordem #887, #889, #891, #893, a marca por cima | corte contém a marca anterior | passou |
| Módulos do assunto | `test_forge_copia` (85), `test_catraca`, `test_fechar_corte` (29), `test_forge_check_pr` (61), `test_pre_envio_brief` (28), `test_reval_delta` (10), `test_changelog*` (91): todos OK, por `python3 -I -m unittest discover -s tests -p <arquivo>` | n/a | passou |
| Sem teste pulado indevido | `git diff 5fb8e328..HEAD -- 'tests/*.py'`: 0 linhas acrescentadas com `skip` ou `expectedFailure` | n/a | passou |
| Controle com mutantes declarados | `bin/`: `forge-check`, `forge-copia`, `forge-fechar` e `tests/catraca.py` mudaram; 19 specs em `tests/mutantes/` mudaram ou nasceram (`v0481-catraca-ajudante{,-2,-3}`, `v0481-copia-mensagem`, `v0481-corte-completo{,-2,-3}`, `v0481-g3-testes-uma-vez{,-2,-3}` e reajustes das antigas). Os mutantes foram rodados nos pareceres de cada item | n/a | passou (prova no parecer de cada item; não rerrodei) |
| Pareceres dos itens com `commit:` válido | os 4 QA `aprovado` (`e05f8faa`, `7bdd25d5`, `8e814a73`, `55f87ffd`) | n/a | passou |

## Execução
- CI do PR #894: run 45582740158 (sha `be4ff39a`, que só soma os dois pareceres de segurança ao `217e73ed`) `success`, com as 10 partes da `suíte` (3.12 e 3.14) verdes. O run do `217e73ed` (45581199574) teve 15 de 16 partes verdes e `suíte (python 3.14, parte 1/5)` e `teto de pulados (python 3.14)` cancelados pela chegada do commit de segurança. Não há run completo no sha exato; não gravo `- ci: <sha40> verde` do `217e73ed`. A suíte inteira vale pelo CI do PR; sem suíte local.
- Sem código novo nesta junção além dos 4 itens; a prova de cada um está no parecer do próprio pedido.
- Corte de 4 itens, abaixo dos 20, autorizado pela ordem do dono de 24/11 20:46, citada no corpo do #894 com `teto: excedido, 1349 linhas, marca de versão`.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio (`docs/security/release-0.47.18.md`).
