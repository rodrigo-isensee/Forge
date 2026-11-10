# O que só o Forge exige no brief

Propósito: lista local do Forge que a skill `checagem-do-brief` confere em cada brief, além da lista neutra (fecha a SK-1, brief-do-forge). Público: o Jarvis e o conferente no repositório do Forge. Revisão: 2026-11-06.

Um item por linha, no formato `- [ ] <item> (quando: <tipo de brief>) · <cartão de origem>`. O item só acrescenta checagem: nunca dispensa portão, review, QA, segurança nem rótulo do dono. Item que o `forge-check` passar a cobrir sai daqui no mesmo PR.

## Itens
- [ ] O status do pre-push é lido pelo hook da develop (`~/Forge/.githooks/pre-push --status`), nunca pelo da branch, que numa branch antiga roda a suíte inteira (quando: código, review, QA) · STATUS-HOOK-DEVELOP
- [ ] Diff de revisão a posteriori se pede por `git show <sha>` do commit revisado, não pelo HEAD da worktree (quando: review, QA, segurança) · BRIEF-DIFF-COMMIT
- [ ] Simular o merge usa as refs remotas (`origin/<branch>` e `origin/develop`), não as locais (quando: QA, devops, merge) · ROTEIRO-SIMULACAO-MERGE
- [ ] Merge e retomada citam a branch, nunca o número do PR (o hook `parecer` exige `gh pr merge <branch>`) (quando: merge, retomada) · RETOMADA-MERGE-BRANCH
- [ ] Entregar que toca `.github/workflows/` confere antes o escopo `workflow` da credencial; sem ele, o envio é ato do dono no brief (quando: código, devops) · WORKFLOW-SCOPE
- [ ] Invariante novo em `tests/config.json` já nasce com a etapa de segurança no pedido (quando: código) · INVARIANTE-GATILHO
- [ ] Brief que pede saída de hook cita a ADR 0003 (código 0 sem saída) (quando: código em `hooks/`) · HOOK-STDERR-ADR
- [ ] `gh run view --log-failed` roda com `XDG_CACHE_HOME=$TMPDIR` no sandbox (quando: QA, devops, merge) · GH-LOG-CACHE
- [ ] Arquivo em `PROTEGIDOS` (`tests/catraca.py`) no diff: o brief avisa que a catraca vai pedir o rótulo `afrouxa-regra` do dono e diz se a mudança afrouxa de fato (quando: código, merge) · ROTULO-PROTEGIDOS
- [ ] O Entregar do brief de implementação cobre cada ponto da opção escolhida pelo dono (quando: código) · BRIEF-OPCAO-COMPLETA
- [ ] Release e promoção seguem o roteiro fixo: fragmentos de `changelog.d/` juntados por `bin/forge-changelog release`, versão nos dois `plugin.json`, os briefs de review, devops, segurança e QA, o PR `develop` → `homolog` por `scripts/promover-homolog.py` (`docs/promocao-integrador.md`), o rótulo pedido junto da abertura do PR e o reinício da cópia vigente só depois do "Concluído" (quando: release, promoção) · ROTEIRO-DA-RELEASE
