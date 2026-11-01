---
tipo: qa
contrato: 1
pedido: release-0.31
branch: melhoria/release-031
commit: 0e67326671c6c1e9b42785920d44e5a7b6300dde
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: release-0.31

Código testado: 0e67326 (commit de release). O HEAD da branch (4d1deb7) difere só pelo parecer de review (`docs/reviews/release-0.31.md`). Escopo: `git diff 91d6cc1 0e67326`, 27 arquivos, sem especificação de UX; vale o critério de integração (`R-QA`). Cada PR da leva já tem QA próprio.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só CHANGELOG, changelog.d/ e manifestos mudam | `git diff --name-only 91d6cc1 0e67326` fora de changelog.d/ | arquivo extra no commit de release | 3 arquivos: `.claude-plugin/plugin.json`, `CHANGELOG.md`, `dev/.claude-plugin/plugin.json` (o dev entra pela decisão técnica do Jarvis, 2026-11-01 14:48, como no 57baeb6) |
| 24 fragmentos fechados | `git ls-tree 91d6cc1 changelog.d` (24) contra `ls changelog.d` na branch (0); cada linha `- ` de cada fragmento buscada na seção 0.31.0 | fragmento perdido ou duplicado | 24 de 24 presentes, 24 itens na seção, nenhum faltando |
| Manifestos em 0.31.0 | `grep version` nos dois plugin.json | manifesto defasado | os dois dizem 0.31.0 |
| Conferência da release | `python3 scripts/conferir-release.py --base origin/develop` | base 0.30.8, release 0.31.0 | `ok: changelog.d/ sem fragmentos pendentes`, rc 0 |
| Testes do changelog | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | 56 testes, OK |
| Plugin válido | `scripts/validar-plugin.sh` em 0e67326 | n/a | `Validation passed`, rc 0 (o aviso de ícone e as sondas de rede negadas pelo sandbox não mudam o resultado) |
| Suíte inteira (`R-VERIFY`) | roda no pre-push do envio deste parecer | n/a | a mudança não toca código; o envio só passa com o pre-push verde |

## Cenários e resultado real
- Vermelho antes do verde e mutação: não se aplicam, a release não muda `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` nem traz teste novo.
- M14 (agents/tech-lead.md:19): a branch cumpre, com versão e CHANGELOG batendo, fragmentos fechados e só os arquivos da release alterados.
- Bugs novos: nenhum; `docs/qa/bugs/` não ganha arquivo.
