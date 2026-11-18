---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: 322798df5b7bd991ddf6a955c00a92363e13e1b3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.170, branch melhoria/v0475-ci-cota)

Revalidação pelo delta `19e7b93f..322798df` (`forge-check parecer delta`). O delta toca só `tests/test_cota_ci.py`: importa `sem_manutencao` e passa `env=sem_manutencao()` ao `git init` e ao `git remote add`. Li só o delta.

## Achados
- A2 (recomendado) changelog.d/v0475-ci-cota.md:2 · o fragmento ainda diz que "o Jarvis a roda no marco (skills ci-cd e esperar-estado)" e fala em "comando para o dono". A skill não diz mais isso. Alinhe o texto ao que a skill diz agora.
- A3 (recomendado) bin/forge-cota-ci:92 · o endpoint legado `settings/billing/actions` pode não existir nas contas da cobrança nova. Não conferi contra a API, porque não há rede aqui. Registre no PR.

## Revalidação
- A1 anterior (git sem o ponto único): resolvido. `python3 -m unittest tests.test_ambiente_git tests.test_cota_ci` deu `Ran 46 tests ... OK`. O `env=` vale só para o `git`. O script sob teste segue com o `env` do `gh` falso, então o comportamento testado não mudou.
- `python3 -I tests/catraca.py --base origin/develop` deu `OK`, rc 0. O delta não muda guarda.
- A2 e A3 seguem abertos como recomendados, porque o delta não os tocou. A observação "a regra continua dita?" do parecer anterior também segue em aberto.

## Parecer
Aprovado no 322798df. Para o PR: o corpo leva `teto: excedido, 312 linhas, <motivo>` (M14). Ele também registra A2 e A3.
