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
| 0.47.0 | `placar: 0.47.0 mortos=62 sobreviveu=0 equivalente=0 invalido=1 sem-veredito=0 specs=9` |
| 0.47.12 | `placar: 0.47.12 mortos=54 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9 falhas=1 (tests/mutantes/placar.json)` |
| 0.47.13 | `placar: 0.47.13 mortos=58 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9` |
| 0.47.14 | `placar: 0.47.14 mortos=66 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9` |
| 0.47.15 | `placar: 0.47.15 mortos=53 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9` |
| 0.47.16 | `placar: 0.47.16 mortos=59 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 sem-veredito-pulado=0 specs=9` |

Nota da 0.47.0: o mutante inválido é da spec `v0457-escopo-ponto-2` (M10), cuja guarda foi movida pelo PR 536; a spec não muda nesta versão.

Nota da 0.47.12 (corte 09491a3b): a spec fixa `tests/mutantes/placar.json` saiu com rc=2 e nenhuma linha na rodada do placar, rodada ao lado de outros testes na mesma máquina; rodada de novo sozinha no mesmo commit (`bin/forge-mutante -- tests/mutantes/placar.json`), deu rc=0 e mortos=8, sem sobrevivente. Com ela, a amostra fica em mortos=62 e falhas=0. Das specs novas desde a v0.47.11, 8 entraram na amostra e as outras ficaram fora pelo teto.

Nota da 0.47.13 (corte 178e2601): das specs novas desde a v0.47.12, 8 entraram na amostra (mais a spec fixa `tests/mutantes/placar.json`) e 23 ficaram fora pelo teto; nenhuma falha. Marca refeita com o #746 (b14f2e19): as 5 specs dele (`v0479-pv-a2-concessao*.json`) vêm depois das 8 na ordem de nome e ficam fora pelo teto (28 fora); a amostra e a linha não mudam.

Nota da 0.47.14 (marca final com o #775, sobre ac544ac5): das specs novas desde a v0.47.13, 8 entraram na amostra (mais a spec fixa `tests/mutantes/placar.json`) e 56 ficaram fora pelo teto; nenhuma falha nem aviso.

Nota da 0.47.15 (corte f4836717): das 42 specs novas desde a v0.47.14, 8 entraram na amostra (mais a spec fixa `tests/mutantes/placar.json`) e 34 ficaram fora pelo teto; nenhuma falha nem aviso.

Nota da 0.47.16 (corte 35b05bd3): das 36 specs novas desde a v0.47.15, 8 entraram na amostra (mais a spec fixa `tests/mutantes/placar.json`) e 28 ficaram fora pelo teto; nenhuma falha nem aviso.
