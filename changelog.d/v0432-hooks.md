### Alterado
- Hook `agentes` (Z10, 0.43.2): uma delegação de escrita vigente por branch. A reserva grava em `escrita` as branches dos briefs de escrita (`Etapa:` fora de review, seguranca e qa, ou sem `Etapa:`); a segunda delegação de escrita na mesma branch é recusada (R-TETO) até o `SubagentStop` da primeira ou o prazo. O parecer não ocupa a branch; a exceção `paralelo na mesma branch: <motivo>` vale só no arquivo do brief.
- Hook `agentes` (BRIEF-EXECUTOR-SEM-PORTAO, 0.43.2): o selo do brief vale também para o nome do papel sem o prefixo `forge:` e para o `general-purpose`, o `fork` e o `claude` cujo prompt cita um brief em docs/briefs/; sem brief citado (leitura e pesquisa) eles seguem livres.
- Hook `conformidade` (FILA-22, 0.43.2, Jarvis só interface): o papel jarvis não roda `gh pr create`, `gh pr merge` nem `git merge` na branch de integração; o tech-lead abre o PR e o `bin/forge-fechar` mescla. Na sessão do Forge, `gh pr create` e `gh pr merge` seguem a mesma política.

### Corrigido
- Hooks (HOOK-PARECER-HEREDOC-FALSO-POSITIVO, 0.43.2): a chamada com heredoc e ação crítica aceita `cat > arq <<'FIM'` junto de `cd`, `mkdir`, `echo` e `true` literais (`mkdir -p docs/qa && cat > docs/qa/<pedido>.md <<'FIM'`), que antes era recusada; com `git`, `gh` ou outro programa na mesma chamada, a recusa continua.
- Hooks (FORGE-RUN-INERTE, 0.43.2): no clone do Forge com `.forge` arquivo, o estado dos hooks (trava do `pesado`, erros.log) vai para `<diretório comum do git>/forge/run/`; antes ficava inerte.
