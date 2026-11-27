---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-devcontainer-sem-gh
commit: 046cd9a1b142deccbcf9717b566154cca9f1933d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E35.2 (DEVCONTAINER-SEM-GH, #926), 1ª rodada completa

Escopo lido: `ee05ee84..046cd9a1` (3 commits: `44f3c2b4`, `1a4b56e3`, `046cd9a1`). Código: 24 linhas (`.devcontainer/devcontainer.json` 7, `scripts/preparar-estacao.sh` 17), dentro do H1; um comportamento só. Classe C pelo `forge-check pr` (sensível da catraca: `scripts/preparar-estacao.sh`).

## Verificação
- ci: 046cd9a1b142deccbcf9717b566154cca9f1933d sem verde: o run CI 45920974522 do head foi cancelado pelo envio do parecer de segurança (`e1c3ba7c`, diff só em `docs/security/`); o run 45921629423 do descendente estava em andamento na hora deste parecer (catraca, instalação, bateria passos e verificações longas, e parte das suítes verdes). O parecer reprova pelos achados, não pelo CI.
- Local (flock trava-teste-b): `python3 -m unittest tests.test_forge.PrepararEstacao tests.test_ambiente_recriacao.ConfiguracaoDoContainer`: 31 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-devcontainer-sem-gh.json`: M1 a M5 mortos. `tests/mutantes/v047-ambiente-sobrevive-1.json`: M3 a M13 mortos (o realinhamento do E35.5 está certo).
- `bin/forge-mutante --conferir --base ee05ee84`: trechos no lugar. `--cobertura`: `não coberto` nos dois arquivos (shell e JSON não são analisados); as guardas foram listadas à mão abaixo.
- Guardas do diff em `scripts/preparar-estacao.sh`: L439 (M5), L457 (sem mutante; sonda S4 morreu), L458 (M2), L466 (M1), L467, L468 e L469 sem mutante e sem teste do ramo de falha (S1 a S3 sobrevivem). Em `.devcontainer/devcontainer.json:26`: `exit 1` (M3) e `FORGE_PREPARO_ESSENCIAL=1` (M4), mortos só por teste que lê o texto do JSON.

## Achados
- A1 (bloqueante) scripts/preparar-estacao.sh:467 · o cartão pede acusar falta de tmux, ~/.config/gh e do link ~/.forge-contrib, mas L467, L468 e L469 não têm mutante nem teste do ramo de falha: trocar cada guarda por true deixa a suíte verde (S1 a S3). Declarar M6 a M8 e um teste de rc 1 com a linha erro: para cada falta
- A2 (bloqueante) tests/test_forge.py:1999 · M3 (exit 1) e M4 (FORGE_PREPARO_ESSENCIAL=1) só morrem por teste que lê o texto do postStartCommand, o que não conta como teste de guarda; rodar o comando literal com /workspaces/Forge trocado por um script falso (como o _poststart faz) e afirmar rc 1 e o env

## Sondas
- S1 · forge-mutante com `tem tmux || ausentes+=(...)` trocado por `tem tmux || true` (L467), testes PrepararEstacao e ConfiguracaoDoContainer · espera: morreu · obtido: sobreviveu
- S2 · forge-mutante com `[ -d "$HOME/.config/gh" ] || ausentes+=(` trocado por `true || ausentes+=(` (L468), mesmos testes · espera: morreu · obtido: sobreviveu
- S3 · forge-mutante com `if [ -d "$real" ] && [ "$(readlink` trocado por `if false && [ "$(readlink` (L469), mesmos testes · espera: morreu · obtido: sobreviveu
- S4 · forge-mutante com `[ "$simular" = 1 ] || container_essenciais` trocado por `true || container_essenciais` (L457), mesmos testes · espera: morreu · obtido: morreu

## Parecer
Reprovado. A troca do postStart faz o que o cartão pede: roda o preparo da cópia presente, sem clonar a main com o gh. Cria `~/.config/gh` antes dos pacotes e acaba com o `; true` que engolia a falha. A conferência final (`container_essenciais`) é simples e idempotente, e a simulação não a roda.

Os dois bloqueios são de prova da classe C. A1: três das quatro conferências que o cartão exige (tmux, `~/.config/gh`, link) podem sumir sem a suíte notar. A2: as duas guardas do comando só são provadas pela leitura do texto. A correção é de teste e de spec. Não muda o código, salvo o que a segurança decidir.

A decisão de rodar o script do work tree como root é da segurança (A1 de `docs/security/v0481-devcontainer-sem-gh.md`, bloqueante). Este parecer não a refaz. Se o desenho mudar por causa dela, a volta vale para os dois portões. O cabeçalho de `scripts/preparar-estacao.sh:8`, que ainda descreve o clone raso, já está no A3 da segurança e não se repete aqui.
