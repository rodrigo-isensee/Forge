---
id: R-VERIFY
titulo: Nunca --no-verify nem --force
verificada_por: permissions.deny do modelo de projeto (templates/projeto/.claude/settings.json); invariantes em tests/config.json
---
# R-VERIFY: Nunca --no-verify nem --force

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- Nunca `--no-verify` nem `--force`: hooks e checagens não se contornam. O `--no-verify` é proibido em qualquer comando git; `--force` (e `-f`, `--force-with-lease`) em qualquer push, em qualquer branch.
- Não desative nem troque o caminho dos hooks (`core.hooksPath`).
- Hook ou teste falhou: corrija a causa e rode de novo.
- Confirme com o usuário antes de apagar ou reescrever uma branch já enviada. Exceção (decisão do dono em 2026-10-23), que só vale para a branch de trabalho (`melhoria/*` no Forge; `feature/`, `fix/`, `docs/`, `chore/`, `refactor/` no projeto) e nunca para `main`, `master`, `develop`, `homolog` nem a branch de integração definida no `CLAUDE.md` do projeto, mesmo que tenham sido head de um PR mesclado (promoção, release): a branch de trabalho cujo PR foi mesclado, com o head remoto igual ao `headRefOid` do PR, é apagada depois do merge sem nova confirmação (`R-FLUXO`, "Depois do merge"). Reescrever branch e apagar branch sem PR mesclado continuam pedindo confirmação.
