---
id: R-FLUXO
titulo: Branches, integração contínua e promoção
verificada_por: passo "Nada pula degrau" do job `bateria` do CI (.github/workflows/ci.yml); CI obrigatório para o merge; hook .githooks/pre-push do Forge; revisão
---
# R-FLUXO: Branches, integração contínua e promoção

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 61 branches e 8 grupos de pareceres da união na versao-043 (estudo 0.43.1)

## No Forge
- `melhoria/*` → `develop` → `homolog` → `main`. Nada pula degrau; ninguém envia direto a essas três (CI e hook).
- **Fluxo contínuo:** item com pareceres aprovados e CI verde entra na `develop` quando pronto; a versão é uma tag e release sobre um commit da `develop`.
- `develop`: a bateria completa roda no CI do PR, obrigatória para o merge; o `tech-lead` mescla com tudo verde.
- `homolog`: o `tech-lead` promove o commit da versão por PR com merge automático. Só a `homolog`: a `main` segue só com o merge do usuário.
- `main`: **a promoção `homolog` → `main` é um PR que só o usuário mescla** (`R-MAIN`); a tag `vX.Y.Z` e a release saem sozinhas (`release.yml`). O `tech-lead` abre esse PR e para.
- Métodos de merge (ADR 0012): `develop` por **squash**; `homolog` por merge commit e `main` por **merge commit**, mesclado pelo usuário; não há PR de sincronização.
- **Fila de integração na `develop`:** PRs com arquivo em comum (`forge-check sobreposicao`) entram em ordem de chegada; os outros não esperam e vão em lote de até 3. Check e parecer seguem.
- **Depois do merge, limpe tudo**: com os heads remoto e local iguais ao `headRefOid` do PR mesclado, quem mesclou apaga branch remota, worktree e branch local sem nova confirmação (só branch de trabalho: `melhoria/*`; no projeto `feature/`, `fix/`, `docs/`, `chore/`, `refactor/`). Fora disso, confirme. **Nunca** apague `develop`, `homolog` nem `main`, nem a integração do `CLAUDE.md`. Sandbox impediu: o dono roda `git worktree prune`.

## No projeto
- Branch de trabalho a partir da integração (padrão `develop`, ou a do `CLAUDE.md`); a integração chega à `main` por PR do usuário (`R-MAIN`). Mesma limpeza do Forge.

## No Forge e no projeto
- **CI do push na integração:** verde antes do próximo merge, acompanhado até o fim. Promove-se o commit da marca, não o topo.
- **Atualize a branch com a integração só na hora do merge**, salvo conflito ou dependência: antes, o `forge-check pr` confere o merge simulado.
- Merge sem conflito não invalida parecer; o conflito resolvido que muda o patch invalida os pareceres dos arquivos que ela tocou, cada um no seu domínio. Quem resolveu o conflito não decide o alcance: a ferramenta aponta e quem deu o parecer revalida pelo delta (`R-REVIEW`).
