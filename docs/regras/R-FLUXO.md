---
id: R-FLUXO
titulo: Branches e promoção
verificada_por: job "fluxo de promoção" do CI (.github/workflows/ci.yml); hook .githooks/pre-push do Forge; revisão
---
# R-FLUXO: Branches e promoção

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

## No Forge
- Fluxo: `melhoria/*` → `develop` → `homolog` → `main`. Nada pula degrau (o CI confere) e ninguém envia direto para essas três branches (o hook do Forge bloqueia).
- `develop`: bateria rápida (testes estruturais, shellcheck, validação do plugin, instalação de ponta a ponta). O `tech-lead` mescla com todos os checks verdes.
- `homolog`: a mesma bateria sobre o conjunto que vai para a `main`. O `tech-lead` promove `develop` → `homolog` por PR, também só com todos os checks verdes.
- `main`: **a promoção `homolog` → `main` é um PR que só o usuário mescla** (`R-MAIN`). Depois do merge, a release `vX.Y.Z` é publicada.
- Métodos de merge (decisão do dono em 2026-10-13, ADR 0008): `develop` por **squash** (um PR vira um commit); `homolog` por **merge commit**; `main` por **squash**, mesclado pelo usuário, para que a `main` tenha só commits dele e não os das branches de trabalho. Como o commit da `main` não existe na `homolog` nem na `develop`, depois de cada release abre-se um PR de sincronização `main` → `develop` (merge commit, sem conteúdo novo, mesclado pelo usuário ou pelo `tech-lead`) que mantém a base comum.
- Melhoria de fábrica vinda de qualquer projeto entra por PR na `develop` (skill `contribuir-com-o-forge`).

## No projeto
- Trabalho em branch própria (`feature/`, `fix/`, `docs/`, `chore/`, `refactor/` + slug) criada a partir da branch de integração atualizada; o padrão é a `develop`, e o `CLAUDE.md` do projeto pode definir outra.
- A integração chega à `main` por PR validado e mesclado pelo usuário (`R-MAIN`).
- Só se commita o que está pronto.
