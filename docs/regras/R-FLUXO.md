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
- Métodos de merge (decisão do dono em 2026-10-16, ADR 0012, que substitui a parte da ADR 0008 sobre a `main`): `develop` por **squash** (um PR vira um commit); `homolog` por **merge commit**; `main` por **merge commit**, mesclado pelo usuário. A `main` acumula só os commits de merge do PR `homolog` → `main`, sem conteúdo próprio; por isso **não há PR de sincronização** `main` → `develop`.
- **Fila de integração na `develop`:** PRs prontos (com os pareceres aprovados) entram **um por vez, em ordem de chegada**; o próximo só atualiza a base (merge da `develop`) depois que o anterior entrou, para não revalidar por conflito à toa. PR que não tem arquivo em comum com os da fila, segundo `forge-check sobreposicao`, não espera. Durante a release (versão da `origin/develop` maior que a da `origin/homolog`; a trava lê a `develop` do remoto, depois de `git fetch`, e não a cópia local), o integrador roda `forge-check sobreposicao --ref <branch>` antes de mesclar na `develop` e espera a promoção se ele barrar (só a `melhoria/release-<versão>` passa). A fila só ordena a entrada; nenhum check nem parecer é dispensado.
- Melhoria de fábrica vinda de qualquer projeto entra por PR na `develop` (skill `contribuir-com-o-forge`).
- **Depois do merge, limpe tudo** (decisão do dono em 2026-10-13: ele não consegue saber quais branches ainda têm trabalho). Quem mesclou, ou o autor se o dono mesclou: (1) confere que o head remoto da branch é o `headRefOid` do PR mesclado e, só então, apaga a branch remota, sem pedir nova confirmação (exceção da `R-VERIFY`, só para branch de trabalho: `melhoria/*` no Forge; `feature/`, `fix/`, `docs/`, `chore/`, `refactor/` no projeto; nunca `main`, `master`, `develop`, `homolog` nem a branch de integração do `CLAUDE.md`, mesmo que tenham sido head de PR mesclado; head diferente, ou PR não mesclado, volta a pedir confirmação ao dono) (`git push origin --delete <branch>`, ou `--delete-branch` no `gh pr merge`, com a mesma restrição); (2) remove a worktree (`git worktree remove <caminho>`) e depois a branch local (`git branch -D <branch>`, sem confirmação só se o head local também é o `headRefOid`; com commit local a mais, peça confirmação). **Nunca** apague `develop`, `homolog` nem `main`. Se o sandbox impedir a remoção (erro "Device or resource busy"), avise o dono e passe a ele o comando `git worktree prune` para rodar no terminal.

## No projeto
- Trabalho em branch própria (`feature/`, `fix/`, `docs/`, `chore/`, `refactor/` + slug) criada a partir da branch de integração atualizada; o padrão é a `develop`, e o `CLAUDE.md` do projeto pode definir outra.
- A integração chega à `main` por PR validado e mesclado pelo usuário (`R-MAIN`).
- Só se commita o que está pronto.
- Depois do merge, vale a mesma limpeza do Forge ("Depois do merge", em "No Forge"): a branch de trabalho com PR mesclado e head igual ao do PR é apagada sem nova confirmação; `main`, `master`, `develop`, `homolog` e a branch de integração nunca entram, nem como `--delete-branch`.

## No Forge e no projeto
- **Atualize a branch com a integração só na hora do merge** (`git fetch` + merge da `develop`; no projeto, da branch de integração do `CLAUDE.md`). Antes disso a branch fica na base em que nasceu: os pareceres de review e de QA valem pelo diff da entrega, e o `forge-check pr` confere o merge simulado com a integração atual (conflito que muda o patch continua invalidando os pareceres dos arquivos tocados).
- Merge da base sem conflito não muda o patch da entrega e não invalida parecer. Resolução de conflito que faz o patch divergir invalida os pareceres dos arquivos que ela tocou (`forge-check pr <pedido>`, `commit_vale`). Quem resolveu o conflito não decide o alcance: a ferramenta aponta os pareceres desatualizados, e quem deu o parecer revalida em proporção ao que mudou (revalidação incremental, `R-QA`) e grava o novo.
