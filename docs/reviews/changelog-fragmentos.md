---
tipo: review
contrato: 1
pedido: changelog-fragmentos
branch: melhoria/changelog-fragmentos
commit: 99bfff4
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

## Review independente
Escopo: `8374ed9..757ee2e`. Revisor independente (não é o autor do código). `python3 -m unittest discover -s tests`: 330 OK; `scripts/validar-plugin.sh`: passa.

Conferido e correto: `release` agrupa por tipo (Adicionado, Alterado, Corrigido), ordem estável (arquivos ordenados), valida todos os fragmentos antes de escrever e só apaga os que juntou (README fica); `conferir` ignora fragmento que já estava na base (`--diff-filter=A`), fragmento fora de `changelog.d/` e nome com espaço (falha fechada); a linha antiga em `[Não publicado]` segue aceita; o PR de release pula o gate, e o PR para a `main` exige versão, entrada fechada e `changelog.d/` vazio; a emenda da ADR 0006 e as instruções (CLAUDE.md, CONTRIBUTING, skill, tech-lead, modelo de PR, README) são coerentes entre si; o CI passa `BASE` por `env` e não interpola dados do PR em `run:`.

Achados (reproduzidos num repositório temporário):
1. **Bloqueia** · `bin/forge-changelog:conferir` (filtro `novos`) · `changelog.d/sub/x.md` é aceito pelo `conferir` (`p.startswith("changelog.d/")`), mas `release` (`glob("*.md")`) e o gate da `main` (`glob('*.md')`) não o enxergam: o CI fica verde e a entrada nunca chega ao `CHANGELOG.md` nem trava a release. Sugestão: exigir `Path(p).parent == Path(PASTA)` em `conferir` (teste: fragmento em subpasta não conta).
2. **Bloqueia** · `ler_fragmento` · `### Adicionado` + `- ` (marcador sem texto) conta como linha e passa o gate com entrada vazia. Sugestão: exigir texto não vazio após `- ` (`re.fullmatch(r"- \S.*")`) e teste.
3. Recomendado · o gate da `main` em `ci.yml` usa `__import__('pathlib')` inline, duplicando a regra de listagem; melhor reusar `fragmentos()` do `forge-changelog` (ex.: subcomando `conferir-release`), para que as duas listagens nunca divirjam.

Parecer: **reprovado** até corrigir 1 e 2 (com testes); o restante está aprovado.

## Re-review independente
Escopo: `fd4a87b..99bfff4`. Revisor independente. `python3 -m unittest discover -s tests`: 333 OK; `scripts/validar-plugin.sh`: passa.

1. Subpasta: resolvido. `conferir` só aceita fragmento com `Path(p).parent == Path(PASTA)`, o mesmo critério de `release` e do gate; teste `test_fragmento_em_subpasta_nao_conta`.
2. Marcador vazio: resolvido. `ler_fragmento` exige `- \S`; `- ` e `-` caem em formato inválido; teste com `subTest` para as duas formas.
3. Recomendação: atendida. O gate da `main` chama `forge-changelog conferir-release`, que usa `fragmentos()` (a mesma listagem de `release`); o `__import__` saiu do `ci.yml` e um teste o proíbe.

Nenhum desvio novo (o diff só toca `ci.yml`, `bin/forge-changelog` e os testes). Observação menor, sem bloqueio: `-  texto` (dois espaços) é recusado; falha fechada.

Parecer: **aprovado**.
