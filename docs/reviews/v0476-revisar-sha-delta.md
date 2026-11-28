---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-revisar-sha-delta
commit: e4191c1b4546d4c12962aed79d7652faba1a44cb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 E3.75 (código de E3.49 e E3.73)

## Achados
- A1 (recomendado) bin/forge-check:2387 · ref de rastreio velha (branch apagada no remoto, sem `fetch --prune`) ainda vence a local; vale conferir com `git ls-remote` ou documentar que o fetch com prune vem antes do brief.
- A2 (recomendado) bin/forge-check:3255 · só `docs/devops/` volta ao delta; documento sem frontmatter em `docs/security/` (postura) segue fora, e o teste trava isso. Se for decisão, citar no docstring o motivo.

## Sondas

## Parecer
Aprovado. Escopo de E3.49 cumprido: `ref_publicada` faz o `Revisar-sha:` sair de `origin/<branch>` quando publicada (local, `HEAD` e `None` seguem como antes, sem cair no `origin/HEAD`); a recusa do `brief gerar` com PR mesclado diz como continuar; o `parecer delta` mantém o `.md` de `docs/devops/` sem frontmatter (e o apagado). E3.73: mapa do `forge-testes` e contagem 95 no `test_testes_tocados`.

Verificado por mim: `tests.test_revisar_sha` e `tests.test_parecer_delta` (8 testes, OK); `forge-mutante` na spec do pedido, M1 a M6 mortos; AF-M3 (spec editada) morto; `--cobertura --base 3d8ad440`: as quatro linhas de guarda cobertas. As specs I31, I32 e AF-M3 só acompanham o texto novo, sem afrouxar. Tamanho (M14): 126 linhas de código e teste, abaixo do teto. Suíte completa: fica com o CI do PR (`R-REVIEW`).
