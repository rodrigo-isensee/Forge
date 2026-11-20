---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: e686f2eb464aafc1dc03b9622a1fc45c640ab18f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478, BP3 S1 atalho durável (E39.11, revalidação)

Revalidação pelo delta (`forge-check parecer delta`, intervalo lido `45f429a4..e686f2eb`, base `origin/develop` atualizada de 0f6034e para cf09782): `aqui=` guardada antes do `cd` em `scripts/jarvis` e `scripts/jarvis-forge`, usada no `source`, no `raiz=` da atualização do plugin e no `eu=` da reabertura no tmux; janela de `FORGE_QUEDA_JANELA` só de 1 a 6 dígitos sem zero à esquerda em `scripts/jarvis-comum.sh`; testes `ChamadaPorCaminhoRelativo` (e a variante `Forge`) e `test_janela_so_aceita_de_um_a_seis_digitos_sem_zero_a_esquerda`; M8, M25 e M28 realinhados, M29 a M35 novos; `test_atalho_duravel` na linha do `README.md` do mapa de `bin/forge-testes`; fragmento do changelog.

## Achados
- A2 (recomendado) docs/indice-forge.md:88 · segue de 45f429a4: `jarvis-comum.sh` entra no índice como `—` (sem shebang, o `indice-forge.py` não lê a linha `# Forge:`); vira cartão depois do merge.

## Parecer
Aprovado (`R-REVIEW`). A3 resolvido: a pasta vem de `aqui=` calculada antes do `cd` (scripts/jarvis:15, scripts/jarvis-forge:19) e as três leituras que usavam `BASH_SOURCE` depois do `cd` passaram a ela; os testes da chamada relativa cobrem o projeto com e sem `scripts/jarvis-comum.sh`, a ferramenta de atualização plantada no projeto e o caminho absoluto no `tmux new-session`, nos dois atalhos. A1 resolvido: o `case` de uma linha aceita só `[1-9]` seguido de até 5 dígitos; `08`, `09`, `010`, 20 dígitos, negativo e espaço voltam a 1800, com os limites 1 e 999999 testados. Os falsos de `tmux` e do projeto conferem o caminho exato (`assertIn` do `FORGE_ABERTURA_FEITA=1 <raiz>/scripts/<script>`), não prefixo. O ambiente do subprocesso é montado do zero.

Tamanho (H1): `forge-check pr v0478 --previo --base origin/develop` emite `tamanho: 165 linhas de código` (`--numstat`: `scripts/jarvis` 28+7, `scripts/jarvis-comum.sh` 94+0, `scripts/jarvis-forge` 27+7, `bin/forge-testes` 1+1). As 17 linhas acima de 148 são a correção do A3 nos dois atalhos (bloqueante deste portão), a janela (A4 da segurança) e a linha do mapa que o teste de mapa exige; tirar a correção do A3 do item deixa `ChamadaPorCaminhoRelativo` vermelho e a regressão no lugar. Decisão do tech-lead: passa, e o corpo do PR leva `teto: excedido, 165 linhas, a correção do A3 (pasta do script antes do cd nos dois atalhos) é o mesmo comportamento do item; sem ela a chamada relativa regride`.

Provas lidas: `bin/forge-testes tests/test_atalho_duravel.py` no head, 81 testes, OK; `bin/forge-mutante` M29 a M35 todos `morreu` e M8 e M25 realinhados `morreu`; `--conferir --base 45f429a4`: trechos no lugar; `--cobertura --base 45f429a4` rc=0. `shellcheck` não está instalado neste sandbox: fica com o CI do PR. Suíte inteira: o CI do PR decide.
