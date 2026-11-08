---
tipo: review
contrato: 1
pedido: release-0.42.0
branch: melhoria/release-0.42.0-devops
commit: b9d6abac3d848d216ddf80f749ea7fa8ac761007
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-07
---
# Review: volta do parecer de devops da release-0.42.0

Review (E1.2) da volta do parecer de devops: `2850bc6..b9d6aba` (commits `333a572` e `b9d6aba`), delta só em `docs/devops/release-0.42.0.md` (+7 -3). Revisor sem autoria na correção nem no parecer original.

## Achados
nenhum

## Parecer
Aprovado no head `b9d6aba`. O delta só muda a forma do parecer de devops, sem mudar o conteúdo.

**Conteúdo preservado.** Frontmatter intocado (`parecer: aprovado`, `commit: 7a189d4...`, `branch: melhoria/release-0.42.0`); `docs/devops/release-0.42.0.md` em `2850bc6` é igual ao de `d9eac67` (diff vazio). A1 e A4 sem mudança; A1 a A4 seguem `recomendado`. A2 encurtado no bloco (260 caracteres) e o texto original inteiro em `## Detalhes`: o texto depois de `- A2 ` em `d9eac67` e o depois de `A2: ` em `b9d6aba` são iguais byte a byte (`cmp`). A3 só troca `:35,38` por `:35-38` (as linhas 35 e 38 de `scripts/verificar-contribuicao.sh` são os dois `git diff --no-color`). A linha `Ferramentas:` vira a seção `## Ferramentas`, com o mesmo texto.

**Ferramenta.** `bin/forge-check pr release-0.42.0 --base origin/main --ref origin/develop` (a develop ainda com o parecer antigo) lista os três erros de formato: A2 com mais de 300 caracteres, A3 e `Ferramentas:` fora do formato. Com `--ref HEAD` (`b9d6aba`) nenhum deles aparece; sobram só os avisos "sem parecer da branch melhoria/release-0.42.0-devops" (review, QA, devops, segurança), lidos antes deste parecer; o que o fechamento exige para um diff só de `.md` é do `forge-check pr` dele.

**Testes:** nenhum rodado; o diff não toca código nem teste (D-5). Teto M14: zero linhas contadas (só `.md`).
