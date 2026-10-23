---
tipo: revisao-seguranca
contrato: 1
pedido: limpeza-regra
branch: melhoria/limpeza-regra
commit: 15dab7588a2aa2956584ada289d63afeaf3ea15f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: limpeza-regra

Diff revisado: `origin/develop...15dab7588a2aa2956584ada289d63afeaf3ea15f` (base `daf2ffa`; commits `36cc47e` R-VERIFY, `6c914c3` R-FLUXO, `15dab75` textos e fragmento). Seis arquivos, só texto.

## Gatilhos
Controles do Forge (`docs/regras/`): a `R-VERIFY` ganha uma exceção que tira a confirmação do dono antes de apagar branch enviada, no Forge e nos projetos.

## Achados
- A1 (bloqueante) docs/regras/R-VERIFY.md:13 · a exceção não exclui as branches longas: PR de promoção (head `develop`/`homolog`) ou de release do projeto (head = branch de integração do CLAUDE.md) cumpre "PR mesclado e head igual" e sai sem confirmação
- A2 (bloqueante) docs/regras/R-FLUXO.md:18 · o passo (2) apaga a branch local (`git branch -D`) sem conferir o head local; commit local feito depois do merge e ainda não enviado some, agora sem confirmação (jarvis.md:72 estende a dispensa às três)

## Detalhe dos achados
**O que está certo.** A conferência do head remoto contra o `headRefOid` está escrita nos três lugares que apagam a remota (`R-VERIFY.md:13`, `R-FLUXO.md:18`, `agents/tech-lead.md:29`, `agents/jarvis.md:72`), e o `forge-fechar` já a faz (`docs/fechamento-integrador.md:20`). Ela fecha os casos pedidos: push depois do merge (o `headRefOid` de PR mesclado não anda, então o head remoto difere e volta a pedir confirmação); PR de fork ou nome de branch reaproveitado (o PR achado pelo nome tem outro `headRefOid`; o único caso em que bate é o de uma branch recriada no mesmo sha, sem trabalho novo); PR mesclado em outra base (o conteúdo do sha está na base em que entrou; apagar a branch não perde commit). Reescrever continua pedindo confirmação, e a proibição de `--force`/`--force-with-lease` não muda. `develop`, `homolog` e `main` continuam protegidas no Forge pelo `pre-push` (`.githooks/pre-push:128`, inclusive remoção) e pelo hook (`hooks/conformidade.py:1162`, `:1166`, `:1239`, `INTEGRACAO` em `hooks/_comum.py:29`).

**A1 · média · esforço P · dono: tech-lead (autor do texto).** Evidência: `docs/regras/R-VERIFY.md:13` define a exceção só por "PR mesclado e head remoto igual ao `headRefOid`", sem excluir branch longa; o "Nunca apague `develop`, `homolog` nem `main`" ficou só em `R-FLUXO.md:18` e `jarvis.md:72`; `agents/tech-lead.md:29` ("Depois de cada merge, apague ... com a conferência, sem nova confirmação") vem logo depois da promoção `develop` → `homolog` e não repete a proibição. Caminho: (a) no projeto, a branch de integração pode ter outro nome (`R-FLUXO.md:21`, "o `CLAUDE.md` do projeto pode definir outra"); o usuário mescla o PR `<integração>` → `main`, o Jarvis aplica a limpeza de `R-FLUXO.md:24`, o head bate (ninguém enviou depois) e a branch de integração é apagada sem perguntar; o hook só conhece `main`, `master`, `develop` e `homolog` (`hooks/_comum.py:29`) e o `pre-push` do modelo de projeto só a `main`. (b) no Forge, `gh pr merge --delete-branch` (citado em `R-FLUXO.md:18`) no PR de promoção apaga o head `develop` pela API do GitHub, por fora do `git push --delete` que o hook confere. Nenhum commit se perde (está na base), mas some a linha de trabalho central, com retrabalho de recriação e PRs abertos contra ela ficando órfãos. Antes, a confirmação da `R-VERIFY` era a barreira humana justamente nesses casos. Correção mínima: na exceção da `R-VERIFY.md:13`, "nunca `develop`, `homolog`, `main` nem a branch de integração do projeto (`CLAUDE.md`)"; repetir a ressalva em `R-FLUXO.md:24` e em `tech-lead.md:29`; e dizer que `--delete-branch` não vale em PR cujo head é branch longa.

**A2 · média · esforço P · dono: tech-lead.** Evidência: `docs/regras/R-FLUXO.md:18`, passo (2), "remove a worktree ... e depois a branch local (`git branch -D <branch>`)", sem condição; `agents/jarvis.md:72` diz "branch remota, local e worktree são apagadas" e, na frase seguinte, que "a branch com PR mesclado e head igual ao `headRefOid` sai sem nova confirmação", o que se lê como dispensa para as três com uma conferência só do head remoto (`tech-lead.md:29` também só fala do "head remoto"). Caminho: um agente commita na branch local depois do merge (parecer de volta, correção) e ainda não enviou; a worktree está limpa, então `git worktree remove` passa; `git branch -D` apaga o commit, que só fica recuperável por `git fsck` até o próximo `gc` (o reflog da branch e o da worktree somem com elas). É trabalho que não entrou, apagado sem confirmação. O `forge-fechar` já faz certo (`docs/fechamento-integrador.md:20`: `branch -D` só com o sha do PR mesclado ou já na base); o texto da regra, que vale também na limpeza manual e nos projetos, não. Correção mínima: no passo (2) de `R-FLUXO.md:18`, "apaga a branch local só se o head local é o `headRefOid` ou já está na base; senão, pergunte ao dono"; em `jarvis.md:72` e `tech-lead.md:29`, "head remoto e local".

**Recomendação (não bloqueia).** A conferência e o `git push origin --delete` não são atômicos (a remoção com lease exigiria `--force-with-lease`, proibido pela `R-VERIFY`): um push entre as duas leituras se perde. A janela é de segundos e o autor do push ainda tem a cópia local; basta registrar no texto que o `--delete-branch` só se usa junto com `--match-head-commit` (como o `forge-fechar` faz no merge) e que a remoção manual vem logo depois da conferência. Informativo: `docs/propostas/retomada-de-sessao.md:185` cita a regra antiga; é proposta histórica, não precisa mudar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do diff, dos hooks (`hooks/conformidade.py`, `hooks/_comum.py`, `.githooks/pre-push`) e do `docs/fechamento-integrador.md`. `gitleaks`, `semgrep`, `actionlint` e `zizmor` não estão no PATH (lacuna); a mudança é só texto, sem segredo nem workflow.
