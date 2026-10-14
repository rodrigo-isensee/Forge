---
tipo: review
contrato: 1
pedido: changelog-fragmentos
branch: melhoria/changelog-fragmentos
commit: 5c7de7e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: changelog por fragmentos (ADR 0006)

Escopo: `melhoria/ci-economia-minutos..5c7de7e` (1 commit): `bin/forge-changelog`, `tests/test_changelog.py`, `.github/workflows/ci.yml`, instruções (tech-lead, skill de contribuição, `CONTRIBUTING.md`, `README.md`, `.claude/CLAUDE.md`, modelo de PR), emenda no ADR 0006 e o fragmento da própria mudança. O autor é o `tech-lead`: parecer de autoria; toca `.github/workflows/` e exige o rótulo `afrouxa-regra` do dono, que é o portão independente.

## Pontos
- **Vermelho antes do verde:** `tests/test_changelog.py` (18 testes) foi escrito primeiro: 11 falhavam sem a ferramenta; depois, todos passam. Cobre `novo`, `release`, e o `conferir` (aceita fragmento, aceita a linha antiga, recusa sem nenhum dos dois, recusa fragmento malformado, não conta fragmento que já estava na base, PR de release passa).
- **Transição:** a linha em `[Não publicado]` segue aceita no PR para a `develop`; a release leva as linhas antigas junto, sem tipo, antes dos grupos tipados.
- **Release:** o PR para a `main` agora também exige `changelog.d/` vazio (além da versão nova e da seção fechada).
- **Limite:** o `conferir` roda `bin/forge-changelog` do próprio PR; a lógica do gate vem do código do PR, como já era com os scripts do repositório. Mudar `bin/` por si só exige fragmento.
- **Verificação:** 330 testes OK, `scripts/validar-plugin.sh` passa, `actionlint` 1.7.12 (checksum do CI conferido) sem achados.
- **Dependência:** a branch está sobre `melhoria/ci-economia-minutos` (ainda não enviada); o PR só faz sentido depois dela.
