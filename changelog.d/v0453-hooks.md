### Adicionado
- Hook `conformidade`: `git push --all` e `git send-pack --all` (também `--al`, com `-C` e `GIT_DIR`) recusam para todo papel com "envie uma branch por vez (R-FLUXO)"; o `--mirror` segue recusado e dá a mesma orientação (decisão do dono, 0.45.3).
- Hook `conformidade`: o AQ (`forge-dev:aq`) ganha Bash só de leitura, com a lista própria em `so_leitura.comandos_por_papel` (`forge-check metricas|transcricao|proximo|voltas|esperas`, `git log|show|diff|status|rev-parse`, `ls`, `cat`, `grep`); redirecionamento, commit, push e o resto que grava recusam, e a escrita pelas ferramentas de arquivo segue só em `docs/propostas/`, `docs/arquitetura/` e, novo, `docs/avaliacoes/`.
- Hook `conformidade`: o alias do gh gravado antes da trava (`aliases:` do config.yml em `GH_CONFIG_DIR`, `XDG_CONFIG_HOME/gh`, `~/.config/gh` e `~/.claude/gh`) é lido e a expansão passa pelas mesmas regras, como o alias do git (N1 resto); alias de shell e bloco ilegível recusam.

### Alterado
- Hook `conformidade`: parecer gravado pelo Bash (heredoc, `>`, `>>`, `tee`, `cp`, `mv`, `sed -i`) em `docs/reviews|qa|security|devops|ux/*.md` recusa na hora da escrita (R-REVIEW), com "regrave com a ferramenta Write (o esqueleto sai de `forge-check parecer novo`)"; antes a volta só caía no `forge-check pr`.
- `forge-check pr`: a recusa de autoria do parecer diz como corrigir (ferramenta Write ou `forge-check parecer novo`); a exigência de autoria não muda.
