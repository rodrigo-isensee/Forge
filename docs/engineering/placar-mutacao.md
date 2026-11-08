# Placar de mutação por release (M-5)

Medida periódica da mutação na suíte do Forge, uma linha por release. Não é portão: nada aqui reprova release nem PR.

Como se mede (o `tech-lead`, na release, antes do `forge-changelog release`, dentro da trava da suíte, `R-TETO`):
`scripts/placar-mutacao.py --desde <tag da release anterior> --versao <versão>`.

- A amostra é a spec fixa `tests/mutantes/placar.json` (guardas estáveis de `bin/forge-check` e `hooks/`, copiadas de specs
  que já estavam na `develop`) mais as specs de `tests/mutantes/` adicionadas desde a tag, até 8; as demais saem
  `fora da amostra`.
- O script roda `bin/forge-mutante` uma vez por spec e soma as classes. Um mutante `inválido` por trecho que sumiu
  (spec envelhecida) é dado do placar: mostra guarda que mudou sem a spec acompanhar.

| Release | Linha `placar:` |
|---|---|
