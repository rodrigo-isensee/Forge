---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-pareceres-release
commit: ef7af7ba5b7ab95788efca91f69ba32f84f89a30
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0475-pareceres-release (v0474, E4.39)

Head `ef7af7ba`, três commits sobre `fc3f2ed8` (`git log fc3f2ed8..ef7af7ba`: 746c04d8 segurança, 11ad49a4 review, ef7af7ba QA). O diff `fc3f2ed8..ef7af7ba` toca só `docs/{qa,reviews,security}/release-0.47.5.md`; nenhum arquivo fora desses três (`git diff --name-only` filtrado: 0). Sem código nem teste novo: mutação e vermelho antes do verde não se aplicam.

Prova da suíte: CI do push na develop em `fc3f2ed8`, run 44255440929: `gh run view` devolve `conclusion: success`, `headSha: fc3f2ed87165a80bb10aef78bd525abd7f53e629`. O head desta branch só soma pareceres; a suíte inteira do PR (check-run `bateria`) cobre o resto. A suíte local não vale como prova (I5).

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Branch só atualiza pareceres | `git diff --name-only fc3f2ed8..ef7af7ba`: 3 arquivos, todos `release-0.47.5.md` | arquivo de código no diff | passou |
| Os três pareceres apontam o commit da develop | `commit: fc3f2ed87165a80bb10aef78bd525abd7f53e629` e `branch: melhoria/v0475-pareceres-release` nos três frontmatters do diff | commit inexistente na promoção | passou |
| Commit referenciado existe no repositório | `git cat-file -t fc3f2ed8`: `commit` | n/a | passou |
| Base verde | CI do push em `fc3f2ed8`, run 44255440929: success | n/a | passou |
| Formato dos pareceres | `bin/forge-check docs`: rc 0 | frontmatter e `## Achados` | passou |
| Este parecer: `docs/qa/v0475-pareceres-release.md` | `forge-check docs` (acima) e PQ-1 | n/a | passou |

## Notas
- Os três pareceres da release declaram a leitura do delta `561ec804..fc3f2ed8` (só changelog, fragmento removido e pareceres); o diff desta branch não contradiz essas afirmações.
- Sem bugs abertos.
