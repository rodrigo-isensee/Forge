---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-release-0475b
commit: bc538cd3e72db368f73681ed9031c9ce4d5c7063
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: release 0.47.5 com o MP2/MP4, por delta (v0474, E4.28)

Head `bc538cd3`, base `561ec804` (develop, marca da 0.47.5, PR 657). Revalidação curta por delta: o código da release foi revisado em `74d6ccd9` (QA aprovado em `docs/qa/release-0.47.5.md`); depois entraram na develop o PR 655 (MP2/MP4, com review, QA e segurança próprios em `docs/*/v0476-mp2-mp4.md`, todos aprovados) e a marca (PR 657). `git diff --stat 561ec804..bc538cd3`: 2 arquivos, 1 inserção e 2 remoções: uma linha em `CHANGELOG.md`, na entrada `[0.47.5]`, e a remoção de `changelog.d/v0476-mp2-mp4.md`. Nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` muda (0 arquivos), então mutação e vermelho antes do verde não se aplicam; o código do MP2/MP4 já teve os dois no parecer próprio.

Prova da suíte: CI do push na develop em `561ec804` (run 44252339056, `gh run list --branch develop`): success, com as suítes python 3.12 e 3.14 (partes 1 a 5), o teto de pulados e a checagem rápida verdes. A árvore do head difere de `561ec804` só no changelog e no fragmento, que o check-run `bateria` do PR cobre no mesmo sha. A suíte local não vale como prova (sandbox sem `/proc` e `gh`).

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A 0.47.5 passa a incluir o MP2/MP4 | `git diff 561ec804..bc538cd3 -- CHANGELOG.md`: a linha "Registro da máquina e fila pesada única (MP2, MP4)" entra em `### Adicionado` da `[0.47.5]`, igual ao fragmento apagado | fragmento sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.4, release 0.47.5; os dois `plugin.json` em 0.47.5 | versão igual à da main | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (106, OK) |
| Docs e pareceres no formato | `bin/forge-check docs` | formato do parecer | passou (rc=0) |
| O MP2/MP4 tem os pareceres de review, QA e segurança aprovados | `docs/{reviews,qa}/v0476-mp2-mp4.md` (commit 4bb3b48e) e `docs/security/v0476-mp2-mp4.md` (commit d7ad2a42): `parecer: aprovado` | portão faltando | passou |
| Nenhum código muda no delta | `git diff --name-only 561ec804..bc538cd3` lista só `CHANGELOG.md` e o fragmento | n/a | passou |

## Provas
- `git rev-parse HEAD` = bc538cd3e72db368f73681ed9031c9ce4d5c7063; `git diff --stat 561ec804..bc538cd3`: 2 files changed, 1 insertion(+), 2 deletions(-)
- CI do push na develop em 561ec804 (run 44252339056): conclusion success; suítes 3.12 e 3.14 (partes 1 a 5), teto de pulados e checagem rápida: success
- O run 44251731313 (31b29052, PR 655) saiu `cancelled` por ser superado pelo push seguinte; vale o do 561ec804, que contém o MP2/MP4
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.4 | versão da release: 0.47.5
- `unittest tests.test_changelog tests.test_conferir_release`: Ran 106 tests, OK
- `bin/forge-check docs`: rc=0

## Notas
- Sem bugs abertos.
