---
tipo: qa
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-pareceres-release
commit: fc3f2ed87165a80bb10aef78bd525abd7f53e629
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: release 0.47.5 inteira na develop (v0474, E4.32)

Head `fc3f2ed8` (develop com a 0.47.5 inteira, PR 658). Este parecer substitui o de `74d6ccd9`, anterior ao MP2/MP4, e cobre a versão inteira: a base da release (versão, changelog e fragmentos, antes em `74d6ccd9`) e o MP2/MP4 (antes em `docs/qa/release-0.47.5-b.md`, `bc538cd3`, que fica como está).

Escopo da versão:
- Base da release (revisada em `74d6ccd9`): `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` de 0.47.4 para 0.47.5 e a entrada `## [0.47.5]` no `CHANGELOG.md`, com os 14 fragmentos juntados.
- MP2/MP4 (PR 655, `31b29052`): registro da máquina e fila pesada única; review, QA e segurança próprios aprovados em `docs/{reviews,qa}/v0476-mp2-mp4.md` e `docs/security/v0476-mp2-mp4.md`. A linha dele entra na `[0.47.5]` pelo PR 658.

Delta de `561ec804` (marca da 0.47.5) até o head: `git diff --name-only 561ec804 HEAD` lista `CHANGELOG.md`, `changelog.d/v0476-mp2-mp4.md` (removido) e pareceres em `docs/`; nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`. Por isso mutação e vermelho antes do verde não se aplicam a este head (o código do MP2/MP4 teve os dois no parecer próprio).

Prova da suíte: CI do push na develop em `fc3f2ed8`, run 44255440929 (`gh run list --branch develop`): conclusion `success`, com as suítes python 3.12 e 3.14 (partes 1 a 5), o teto de pulados e a checagem rápida verdes (os jobs de PR saem `skipped`, por ser push). A suíte local não vale como prova (I5).

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.4, release 0.47.5 | versão igual à da base | passou |
| Os dois manifestos batem | `plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.5"`; entrada `## [0.47.5]` no `CHANGELOG.md` | manifesto sem par | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release`: ok | pasta só com README | passou |
| A 0.47.5 inclui o MP2/MP4 | `grep -n 'MP2, MP4' CHANGELOG.md`: linha 18, na `[0.47.5]`; `changelog.d/` sem o fragmento | fragmento sem entrada | passou |
| Nenhum código muda após a marca | `git diff --name-only 561ec804 HEAD`: só changelog, fragmento e `docs/` | n/a | passou |
| Suíte no head | CI da develop em `fc3f2ed8`, run 44255440929 | n/a | passou (success) |
| MP2/MP4 com review, QA e segurança aprovados | `docs/{reviews,qa}/v0476-mp2-mp4.md` e `docs/security/v0476-mp2-mp4.md`: `parecer: aprovado` | portão faltando | passou |

## Provas
- `git rev-parse HEAD` = fc3f2ed87165a80bb10aef78bd525abd7f53e629
- CI do push na develop em fc3f2ed8 (run 44255440929): success; 3.12 e 3.14, partes 1 a 5, teto de pulados e checagem rápida: success
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.4 | versão da release: 0.47.5

## Notas
- Sem bugs abertos.
- `docs/qa/release-0.47.5-b.md` (aprovado) fica como está.
