---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.17
commit: 8d9f51d3d8c3ae37afc68618fdd5521e069ee6bf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: marca da 0.47.17 (#882, classe C)

Diff `7e8c9c198..8d9f51d3d`: 3 arquivos modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`) e 20 apagados (os fragmentos de `changelog.d/`). Nenhum arquivo de código, teste ou doc de processo mudou.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os 20 itens estão no CHANGELOG com o texto dos fragmentos | script: cada linha não vazia de cada fragmento da base, lida por `git show 7e8c9c198:<f>`, buscada na seção `[0.47.17]` | 20 fragmentos; `graphql-ilegivel` traz 2 itens, logo 21 linhas `- ` na seção | passou (20/20 fragmentos, 21/21 linhas literais) |
| Fragmentos apagados, README mantido | `ls changelog.d`; `git diff --name-status` (20 D, todos fragmentos) | `changelog.d/README.md` fica (o forge-changelog o ignora) | passou |
| Versão bate nos manifestos | `grep version` nos manifestos | plugin 0.47.17, dev 0.47.17; `marketplace.json` não traz versão, nada a bater | passou |
| Nada de código mudou | `git diff --name-status` | só 2 `plugin.json`, CHANGELOG e fragmentos | passou |
| Data da release | `date -u` = 2026-11-25 02:52; check-run `bateria` terminou 2026-11-25T02:41Z | data UTC do corte | passou (2026-11-25 está certa) |
| Seção no formato e ordem | leitura do diff do CHANGELOG | `## [Não publicado]` vazio, `[0.47.17]` acima da `[0.47.16]`, subseções Adicionado/Alterado/Corrigido | passou |
| Testes do changelog | `python3 -I -m unittest discover -s tests -p 'test_changelog*.py'` | n/a | 91 testes OK |

## Cenários e resultado real
- Prova de CI: check-run `bateria` do sha 8d9f51d3d, concluído com sucesso (https://github.com/rodrigo-isensee/Forge/actions/runs/45533611195/job/138938309416); `bateria (python 3.14)`, `bateria (verificações longas)` e as 10 partes da suíte também verdes. Não rerrodei a suíte inteira.
- Vermelho antes do verde e mutantes: não se aplicam, a marca não traz teste novo nem regra de código.
- Segurança e acessibilidade: sem gatilho, sem tela.
- Parecer anterior da branch: não havia.
- O clone foi feito por `git clone` local porque `git worktree add` é bloqueado no sandbox (`.git/worktrees` só leitura).
