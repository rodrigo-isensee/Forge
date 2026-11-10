---
id: R-VERIFY
titulo: Nunca --no-verify nem --force
verificada_por: permissions.deny do modelo de projeto (templates/projeto/.claude/settings.json); invariantes em tests/config.json
---
# R-VERIFY: Nunca --no-verify nem --force

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: sem medida (vale por permissão negada, sem custo de processo)

- Nunca `--no-verify` nem `--force`: hooks e checagens não se contornam. O `--no-verify` é proibido em qualquer comando git; `--force` (e `-f`, `--force-with-lease`) em qualquer push, em qualquer branch.
- Não desative nem troque o caminho dos hooks (`core.hooksPath`).
- Hook ou teste falhou: corrija a causa e rode de novo.
- Confirme com o usuário antes de apagar ou reescrever uma branch já enviada. Exceção: a limpeza da branch de trabalho depois do merge (`R-FLUXO`), nunca de `main`, `master`, `develop`, `homolog` nem da integração.
