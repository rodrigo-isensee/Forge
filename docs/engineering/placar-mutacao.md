# Placar de mutação por release (M-5)

Medida periódica da mutação na suíte do Forge, uma linha por release. Não é portão: nada aqui reprova release nem PR.

Como se mede (o `tech-lead`, na release, antes do `forge-changelog release`, dentro da trava da suíte, `R-TETO`):
`scripts/placar-mutacao.py --desde <tag da release anterior> --versao <versão>`.

Uma vez por versão, nunca no PR (decisão do dono, 2026-11-12): nem o CI nem o envio rodam o placar
(`tests/test_changelog.py`, `ReleaseAvisaMedidasDaVersao`). No clone do Forge, o `forge-changelog release` imprime o
comando já com a tag anterior e lembra o bench da versão (`bench-versoes.md` e `metricas-velocidade.md`, na área do Jarvis).

- A amostra é a spec fixa `tests/mutantes/placar.json` (guardas estáveis de `bin/forge-check` e `hooks/`, copiadas de specs
  que já estavam na `develop`) mais as specs de `tests/mutantes/` adicionadas desde a tag, até 8; as demais saem
  `fora da amostra`.
- O script roda `bin/forge-mutante` uma vez por spec e soma as classes. Um mutante `inválido` por trecho que sumiu
  (spec envelhecida) é dado do placar: mostra guarda que mudou sem a spec acompanhar.
- O placar avisa (`aviso:`) quando `--desde` não é tag neste clone ou não é a tag da release imediatamente anterior, e a linha `placar:` ganha `falhas=<n> (<spec>)` quando uma spec sai com rc diferente de zero.

| Release | Linha `placar:` |
|---|---|
