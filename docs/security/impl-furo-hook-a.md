---
tipo: revisao-seguranca
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a3
commit: f732639d904cea5b959e809467952843a8658a41
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-furo-hook-a, branch a3 (revalidação da volta 3)

Etapa E1.3 do pedido `impl-furo-hook-a` (brief `impl-furo-hook-a-security-engineer-4`). Revalidação pelo delta do parecer anterior (`f21d6d8`, que revisou `1804a43`, reprovado com A1 bloqueante). Modelo de ameaças: `~/.forge-contrib/docs/security/ameacas/furo-hook.md`, §4.3. Não sou o autor.

## Delta lido
`forge-check delta --parecer docs/security/impl-furo-hook-a.md` listou `1804a43..f732639`:
- `hooks/conformidade.py` +4 -5, nas linhas 133 (`CONFIG_COM_VALOR` ganha `--comment` e `--value`), 1252, 1256-1257 (o `set`/`unset` reconhecido antes de entrar em `chaves`) e 1264 (sai o corte posterior do `set`).
- Cinco fixtures novas: `merge-flag-config-comment-valor-bloqueia.json`, `merge-flag-config-set-all-bloqueia.json`, `merge-flag-config-set-append-bloqueia.json`, `merge-flag-config-set-comment-igual-bloqueia.json` e `merge-flag-config-set-value-igual-bloqueia.json`.

Como o delta toca um controle do Forge (o hook `conformidade`), reli `git_config` inteira (`hooks/conformidade.py:1247-1272`) e as constantes que ela usa (`:125-133`). O resto da branch fica como já lido nos pareceres anteriores (`0f870fe`, `f21d6d8`).

## Item entregue e M14
- **Item:** E3, A3 HOOK-MERGE-FLAGS.
- **M14 (`agents/tech-lead.md:19` na develop):** `git diff --numstat --no-renames 234dbe0..f732639` conta `hooks/conformidade.py` (45+9) e `tests/test_hooks.py` (5): 59 linhas, abaixo de 400 (fixtures, mutantes, `.md` e fragmento ficam fora). Uma classe de comportamento em `hooks/` (merge na integração que muda o resultado revisado), com corpus próprio. **Cumpre.**

## Gatilhos
R-SEGURANCA, controles do Forge: o hook `conformidade`, nos portões R-REVIEW e R-CONFORMIDADE.

## Achados
- A1 (recomendado) hooks/conformidade.py:1267 · anterior à branch, segue: `git config remove-section core` e `--remove-section core` saem 0 e apagam o core.hooksPath (o pre-push deixa de rodar); a seção sem ponto não casa CONFIG_PROTEGIDA. Cartão novo ao dono, como o N1.
- A2 (recomendado) hooks/conformidade.py:1250 · segue: `GIT_EDITOR=<script> git config -e|--edit|edit` e as chaves do bash fora da linha crítica gravam sem recusa. Cartão.

## Detalhe dos achados
Sondas: cada uma monta a fixture `merge-flag-config-set-mergeoptions-bloqueia` pelo `Fixture`/`rodar` da própria worktree, troca só o comando e roda o hook real com o papel tech-lead. Nada rodou contra repositório real, rede ou produção.

**A1 anterior (opções do `set`/`unset` antes da chave), corrigido.** Saem 2, com a chave protegida certa na mensagem:
- as oito sondas do parecer anterior: `set --all branch.develop.mergeoptions --squash`, `set --append pull.twohead ours`, `set --comment=x pull.octopus ours`, `set --value=x core.editor vi`, `set --comment x pull.twohead ours`, `set --type=bool core.bare true`, `set --fixed-value core.editor vi`, `unset --all alias.p`;
- a forma antiga apontada pelo review: `git config --comment x pull.twohead ours` e `--value x pull.twohead ours`;
- variações da matriz (posição e combinação): `set --value x core.editor vi`, `--local set …`, `--file .git/config set …`, `set --local --all …`, `set --worktree --all branch.develop.mergeoptions --squash`, `set -f .git/config merge.nos.driver true`, `set --file=… pull.twohead ours`, `set --type bool --all core.bare true`, `set --default x --all core.editor vi`, `set --blob HEAD:x core.editor vi`, `unset --fixed-value --value=x alias.p`, `set -- branch.develop.mergeoptions --squash`, `set --all -- …`, `--comment set pull.twohead ours` e `--type set core.bare true` (o `set` consumido como valor da opção não vira subcomando, e a chave seguinte segue protegida);
- as do A1 da volta 2: `--worktree branch.develop.mergeoptions --squash` e `branch.develop.mergeoptions -- --squash`.

Corpus de legítimos, sai 0: `set --all branch.feature/x.merge refs/heads/develop`, `set --comment x branch.feature/x.merge refs/heads/develop`, `set branch.feature/x.merge refs/heads/develop`, `branch.feature/x.merge refs/heads/develop`, `get --all branch.develop.mergeoptions`, `get --comment x branch.develop.mergeoptions`, `list`, `--get core.editor` e `--worktree core.sparseCheckout true`.

A guarda nova (`:1256`) só reconhece `set`/`unset` enquanto nenhuma chave foi vista, e o `pulo` vem antes dela: um `set` que é valor de `--comment`/`--type`/`--file` não liga o subcomando. Incluir `--comment` e `--value` em `CONFIG_COM_VALOR` só faz a palavra seguinte deixar de ser chave; na forma antiga com só a chave (`--comment x <chave>`) a leitura segue liberada, como antes. Sem regressão no corpus.

**A1, recomendado (era o A2; anterior à branch, fora das chaves do merge).** Sem mudança: o delta não tocou `CONFIG_PROTEGIDA` nem as formas de seção. Correção mínima do parecer anterior, mantida: `remove-section` e `rename-section`, nas duas formas, recusam quando o nome da seção (ou o novo nome) é `core`, `user`, `alias`, `include*`, `commit`, `pull`, `merge.<d>` ou `branch.<b>`. Severidade média, caminho só deliberado. Esforço P. Dono: tech-lead, por cartão novo ao dono junto do N1.

**A2, recomendado (era o A3).** Sem mudança: o delta não tocou `-e`/`--edit`/`edit` nem o marcador `CRITICO`. Cartão, dono tech-lead.

Dimensão para a matriz do modelo (§8), já registrada no parecer anterior e agora coberta por fixture: **Posição, opção do subcomando antes da chave**. Segue aberta, nos cartões: **Mecanismo, seção inteira** (`remove-section`, `rename-section`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta`, leitura do delta e de `git_config` inteira, sondas locais pelo harness de fixtures. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada; o delta não traz segredo, dependência nem workflow).
