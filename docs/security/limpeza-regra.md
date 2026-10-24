---
tipo: revisao-seguranca
contrato: 1
pedido: limpeza-regra
branch: melhoria/limpeza-regra
commit: e4616591cabfba0388b7c6db9d716728fbd7ec30
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: limpeza-regra

Revalidação (volta por delta) sobre `e4616591cabfba0388b7c6db9d716728fbd7ec30`. Parecer anterior: `reprovado` em `15dab75` (A1 e A2 bloqueantes). `forge-check delta --parecer docs/security/limpeza-regra.md` aponta `15dab75..e461659`: `R-VERIFY.md:13`, `R-FLUXO.md:18` e `:24`, `agents/jarvis.md:72`, `agents/tech-lead.md:29`, `docs/fechamento-integrador.md:20`, `docs/retomada-de-sessao.md:285`, `docs/propostas/retomada-de-sessao.md:187-188` e o fragmento do changelog (o trecho `15dab75..d1e45a6` são só os pareceres de review e de segurança). Todas as linhas do delta foram relidas, e também as outras menções à exceção no repositório (`grep headRefOid`, "sem nova confirmação").

## Gatilhos
Controles do Forge (`docs/regras/`): a `R-VERIFY` ganha uma exceção que tira a confirmação do dono antes de apagar branch enviada, no Forge e nos projetos.

## Achados
- A3 (recomendado) docs/regras/R-FLUXO.md:18 · conferir e apagar a remota não é atômico; registrar que o `--delete-branch` só se usa junto com `--match-head-commit` e que a remoção manual vem logo depois da conferência (vem do parecer anterior, sem mudança)

## Detalhe dos achados
**A1 (anterior, bloqueante): resolvido.** `R-VERIFY.md:13` limita a exceção à branch de trabalho e exclui, por nome, `main`, `master`, `develop`, `homolog` e a branch de integração do projeto, inclusive quando foram head de PR de promoção ou de release, como o dono decidiu ("A", 2026-10-23). `R-FLUXO.md:18` lista os prefixos (`melhoria/*`; `feature/`, `fix/`, `docs/`, `chore/`, `refactor/`) e aplica a mesma restrição ao `--delete-branch`; `R-FLUXO.md:24` repete para o projeto, "nem como `--delete-branch`"; `tech-lead.md:29`, logo depois da promoção, e `jarvis.md:72` repetem a ressalva. Os dois caminhos do achado ficam fechados: o PR `<integração>` → `main` do projeto e o `--delete-branch` no PR de promoção do Forge voltam a pedir confirmação.

**A2 (anterior, bloqueante): resolvido.** `R-FLUXO.md:18`, passo (2): a remoção da branch local dispensa a pergunta apenas quando o head local coincide com o do PR mesclado; havendo commit local extra, volta a pergunta ao dono. `jarvis.md:72` e `tech-lead.md:29` passam a exigir "head (remoto e local)". `fechamento-integrador.md:20` fica alinhado ao script (head local igual ao `headRefOid` ou já na base; commit a mais fica pendente). Commit feito na branch local depois do merge e não enviado não some mais sem pergunta.

**Caminho novo para apagar trabalho não integrado: nenhum.** A única dispensa continua exigindo PR mesclado, branch de trabalho e os dois heads iguais ao `headRefOid` (o conteúdo desse sha está na base). Head local atrás ou à frente, ou diferente do PR, volta a pedir confirmação. A worktree continua removida sem a opção que força, então mudança não commitada ou arquivo não rastreado a deixa pendente. A linha nova da tabela (`docs/retomada-de-sessao.md:285`) e a nota da proposta (`docs/propostas/retomada-de-sessao.md:187`) só remetem à exceção com o mesmo recorte e não a ampliam. Reescrever branch continua pedindo confirmação, e a proibição de `--force`/`--force-with-lease` não mudou.

**A3 · baixa · esforço P · dono: tech-lead.** Mesma recomendação do parecer anterior (janela de segundos entre a conferência e o `git push origin --delete`; quem fez o push ainda tem a cópia local). Não bloqueia.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do delta e das outras menções à exceção. `gitleaks`, `semgrep`, `actionlint` e `zizmor` não estão no PATH (lacuna). A mudança é só texto, sem segredo nem workflow.
