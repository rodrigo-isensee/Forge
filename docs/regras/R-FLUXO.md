---
id: R-FLUXO
titulo: Branches e promoção
verificada_por: passo "Nada pula degrau" do job `bateria` do CI (.github/workflows/ci.yml); hook .githooks/pre-push do Forge; revisão
---
# R-FLUXO: Branches e promoção

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

## No Forge
- Fluxo: `melhoria/*` → `develop` → `homolog` → `main`. Nada pula degrau (o CI confere) e ninguém envia direto para essas três branches (o hook do Forge bloqueia).
- `develop`: a bateria completa (testes estruturais, shellcheck, validação do plugin, instalação de ponta a ponta) roda **no pull request**; o `tech-lead` mescla com todos os checks verdes. O push na `develop` depois do merge roda só a checagem rápida (testes estruturais), porque o PR já validou o mesmo conteúdo (decisão do dono em 2026-10-13, para poupar minutos do CI).
- `homolog`: a mesma bateria completa, de novo, sobre o conjunto que vai para a `main` (no PR de promoção e no push). O `tech-lead` promove `develop` → `homolog` por PR, também só com todos os checks verdes.
- `main`: **a promoção `homolog` → `main` é um PR que só o usuário mescla** (`R-MAIN`). Depois do merge, a release `vX.Y.Z` é publicada.
- Métodos de merge (decisão do dono em 2026-10-13, ADR 0008): `develop` por **squash** (um PR vira um commit); `homolog` por **merge commit**; `main` por **squash**, mesclado pelo usuário, para que a `main` tenha só commits dele e não os das branches de trabalho. Como o commit da `main` não existe na `homolog` nem na `develop`, depois de cada release abre-se um PR de sincronização `main` → `develop` (merge commit, sem conteúdo novo, mesclado pelo usuário ou pelo `tech-lead`) que mantém a base comum.
- Melhoria de fábrica vinda de qualquer projeto entra por PR na `develop` (skill `contribuir-com-o-forge`).
- **Depois do merge, limpe tudo** (decisão do dono em 2026-10-13: ele não consegue saber quais branches ainda têm trabalho). Quem mesclou, ou o autor se o dono mesclou: (1) apaga a branch remota (`git push origin --delete <branch>`, ou `--delete-branch` no `gh pr merge`); (2) remove a worktree (`git worktree remove <caminho>`) e depois a branch local (`git branch -D <branch>`). **Nunca** apague `develop`, `homolog` nem `main`. Se o sandbox impedir a remoção (erro "Device or resource busy"), avise o dono e passe a ele o comando `git worktree prune` para rodar no terminal.

## No projeto
- Trabalho em branch própria (`feature/`, `fix/`, `docs/`, `chore/`, `refactor/` + slug) criada a partir da branch de integração atualizada; o padrão é a `develop`, e o `CLAUDE.md` do projeto pode definir outra.
- A integração chega à `main` por PR validado e mesclado pelo usuário (`R-MAIN`).
- Só se commita o que está pronto.
