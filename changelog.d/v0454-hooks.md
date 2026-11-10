### Adicionado
- **`caminhos_extra` no hook `meta`:** as checagens do objetivo armado (`forge-check meta --checagem`) rodam com as pastas de `caminhos_extra` do `.forge/config.json` no fim do PATH, com a mesma conferência do `.githooks/pre-push` (absoluta, real, sem `:`, existente); a pasta ruim fica de fora com aviso no `erros.log`.

### Corrigido
- **Alias do gh no `parecer`:** `gh <nome>` com alias gravado que esconde `gh pr create`, `gh pr merge`, `gh pr ready` ou `gh api` passa pelas regras do parecer (review e QA antes do PR e do merge), com o mesmo leitor do `conformidade`; alias de shell, configuração ilegível e configuração do gh mudada antes na linha recusam.
