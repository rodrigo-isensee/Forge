---
tipo: qa
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: f1fdb80
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA: `scripts/ci-local` (bateria do CI rodada localmente sobre um PR)

Ambiente: worktree da branch em f1fdb80 (revalidado após a correção do CL-01 e do C2; a execução dos PQ-1 e PQ-2c foi em e808d6c), `gh` autenticado, sem `--publicar` e sem `actionlint`/`zizmor` no PATH. Nada que custe dinheiro foi executado (`R-CUSTO`).

## Obrigações e resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Resumo por job fiel ao que o CI daria (decisão A, só evidência) | PQ-1: `scripts/ci-local 125` e `126` | PR com mudança legítima barrada pela catraca; PR de release | OK |
| PR inexistente falha com mensagem e rc 1 | PQ-2a: `scripts/ci-local 99999` | PR que não existe | OK (rc 1, "Could not resolve to a PullRequest") |
| `--help` | PQ-2b | n/a | OK (rc 0) |
| PR de fork recusado (`gh` simulado, `isCrossRepository: true`) | PQ-2c | fork sem `--confiar` | OK (rc 1, "Recusado", nenhuma worktree criada) |
| Interrupção limpa a worktree temporária | PQ-2d: `timeout -s INT` | Ctrl-C no meio dos jobs | OK (revalidado em f1fdb80: rc 130, sem traceback) |
| Testes e validação do plugin | PQ-3 | n/a | OK |

## PQ-1: execução real
PR #126 (`chore(release): 0.14.0`, develop), rc 1:
```
testes estruturais OK | shellcheck OK | workflows PULADO (ferramenta ausente: actionlint, zizmor)
validação do plugin OK | instalação de ponta a ponta OK | versão e changelog OK
fluxo de promoção OK | segredos OK | pareceres OK | catraca OK
pr-texto FALHOU (passo 'Seções "Projeto de origem" e "Como medir"' saiu com 1)
ci-local: failure (9 ok / 1 falharam / 1 pulados)
```
Esperado: o corpo do PR não tem as seções "Projeto de origem" e "Como medir", então o `pr-texto` falha igual ao CI real; o resto passa. Confere.

PR #125 (`anti-alucinacao-regras`, develop), rc 1:
```
testes estruturais OK | shellcheck OK | workflows PULADO | validação do plugin OK
instalação de ponta a ponta OK | versão e changelog OK | fluxo de promoção OK
segredos OK | pareceres OK | pr-texto OK
catraca FALHOU (R-CONFORMIDADE: hooks/conformidade.json, hooks/_comum.py, hooks/conformidade.py mudaram; exige o rótulo `afrouxa-regra` do dono)
ci-local: failure (9 ok / 1 falharam / 1 pulados)
```
Esperado: o PR altera hooks que decidem o bloqueio, então só o rótulo do dono libera a catraca. Confere.

## PQ-2: bordas
| Caso | rc | `git worktree list` |
|---|---|---|
| PR 99999 | 1 | inalterada |
| `--help` | 0 | inalterada |
| fork simulado (`gh` falso em PATH próprio) | 1 | nenhuma `ci-local.*` criada |
| `timeout -s INT 25` (rc real do script, `--preserve-status`) | 130 | sem `ci-local.*` e sem pasta em `$TMPDIR`; só ficam as worktrees de trabalho |
| `timeout -s TERM 25` (e808d6c original) | 124 | **vazou** `ci-local.<id>/wt`; removida à mão depois |
| revalidação f1fdb80: `timeout --preserve-status -s INT 25` | 130 | inalterada; sem pasta nova em `$TMPDIR`; 0 "Traceback"; última linha "ci-local: interrompido (a worktree temporária foi removida)." |
| revalidação f1fdb80: `timeout --preserve-status -s TERM 25` | 143 | inalterada; sem pasta nova; 0 "Traceback" |

O vazamento no SIGTERM (C2) e o traceback no Ctrl-C (CL-01) foram corrigidos até f1fdb80 e confirmados na revalidação acima.

## PQ-3
`python3 -m unittest tests.test_ci_local -v | tail -3` em f1fdb80: `Ran 46 tests in 1.372s` / `OK`. `scripts/validar-plugin.sh`: `Validation passed`, rc 0. A suíte completa não foi rodada (o pre-push roda).

## Bugs
- CL-01 (baixo, corrigido em f1fdb80): Ctrl-C imprimia traceback. `docs/qa/bugs/CL-01-ctrl-c-imprime-traceback.md`. Nenhum bug aberto.

## Parecer
Aprovado (`R-QA`), sem bugs abertos; aceite do dono não se aplica. O `ci-local` não vira check exigido (decisão A); o resultado entra no PR como evidência, e o status `ci-local` é autodeclarado. Sem vermelho-antes-do-verde nem mutação a rodar: QA não alterou código; os testes novos são do devops, que registrou o vermelho antes no review.
