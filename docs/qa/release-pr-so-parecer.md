---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/release-pr-so-parecer
commit: b89f23e82be8ca226e78b9fa81f73513a9fff1e2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: release-pr-so-parecer

Escopo: `bin/forge-changelog conferir` aceita PR só de pareceres (RELEASE-PR-SO-PARECER) e exige fragmento em todo o resto, inclusive `git mv` de código para docs/reviews (A1 do review, `--no-renames`). Suíte completa fica com o CI/pre-push (D-5); aqui rodou tests/test_changelog.py (51 testes, OK).

## Achados
- A1 (recomendado) bin/forge-changelog:228 · PR com parecer e fragmento de changelog.d/ malformado agora passa no conferir (a base rejeitava com "formato inválido"): o fragmento fica fora de CAMINHOS_DA_FABRICA e o atalho de parecer sai antes de validá-lo; o erro só aparece no release.

## Critério → teste → resultado
Cenários de ponta a ponta em repositório descartável (base `develop`, branch `pr`, `conferir --base develop`):

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| só parecer passa | CT-01 docs/reviews + docs/qa | caso feliz | passou: rc 0, "PR só de parecer" |
| só parecer passa | CT-02 docs/devops + docs/security | demais pastas | passou: rc 0 |
| só parecer passa | CT-03 docs/qa/_x/a.md; docs/reviews/sub/a.md | pasta com _, subpasta | passou: rc 0 |
| exceção de modelo/ameaças | CT-04 docs/qa/_modelo.md; security/ameacas; security/aceites | só o nome com _ e as pastas excluídas | passou: rc 1, pede fragmento |
| mistura exige fragmento | CT-05 parecer + agents/a.md; parecer + _modelo | mistura | passou: rc 1 |
| renomeação | CT-06 git mv agents/a.md docs/reviews/a.md | A1 do review | passou: rc 1 |
| resto exige fragmento | CT-07 docs/guia.md; bin/novo | não parecer | passou: rc 1 |
| sem mudança | CT-08 commit vazio | vazio | passou: rc 0 |
| versão mudou | CT-09 plugin.json 1.0.1 + parecer | release | passou: rc 0 (conferido na promoção) |
| fragmento com parecer | CT-10 parecer + changelog.d/f.md malformado | A1 | rc 0 na branch, rc 1 na base (2665b9a~1): ver achado A1 |
| regressão | CT-11 tests/test_changelog.py | n/a | passou: 51 testes, OK |

## Cenários e resultado real
Rodado em `$TMPDIR` (scratchpad) com `python3 bin/forge-changelog conferir --base develop`; 16 cenários, todos como na tabela. Mutantes: sem spec declarada (a mudança é uma flag, coberta por CT-06 e pelo teste novo da branch). Sem teste novo de QA.

Parecer: aprovado sobre b89f23e, com A1 recomendado (não devolve).
