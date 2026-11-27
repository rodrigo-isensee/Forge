---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-mitigacoes
commit: d1c2d815f94d240bd5962a056824e8f81cdaa4a7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481, 1º corte das mitigações do G2 (M18.1, #919)

Etapa E26.2, 1ª rodada completa, base 707fea56. O diff são 2 commits: `feat(parecer)` (1d9f952f) e `test(parecer)` (d1c2d815). Toca `bin/forge_pareceres.py` (25 linhas de código), os testes, a spec de mutantes e o fragmento do changelog.

- ci: d1c2d815f94d240bd5962a056824e8f81cdaa4a7 verde

O run 45867204640 roda no head d1c2d815. As 5 partes da suíte passam em 3.12 e em 3.14, e também `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os dois `teto de pulados` e `árvore já provada`. Só falham `bateria (pareceres)`, `bateria` e `catraca`, que esperam o parecer e o rótulo.

## O que foi lido
- **Pedido (E26.1):** o plano de corte e o 1º corte estão no corpo do PR. O corte faz só a M18.1: recusa o PR de fork e o PR de outro repositório que não o do `origin`, e recusa o `origin` ausente ou fora das formas aceitas. É um comportamento só, dentro do teto H1 (25 de 150 linhas).
- **Correção:** a recusa vem em `pr_aberto`, antes de qualquer POST. O `{owner}/{repo}` das gravações é resolvido pelo `gh`, e a URL do PR casar com o `origin` já amarra o repositório consultado ao da cópia. `isCrossRepository is not False` falha fechado quando o campo está ausente ou nulo. O `fullmatch` recusa caminho a mais e `file://`.
- **Testes:** os testes novos cobrem o remoto diferente, o PR de outro repositório do mesmo dono, o fork (verdadeiro, nulo e ausente), o `origin` ausente e as formas inválidas, além das formas válidas e de maiúsculas e minúsculas. Os falsos conferem a mesma regra do código (checklist 12): a URL exata pelo `fullmatch` e o `isCrossRepository` lido como no `gh`.
- **Commits:** seguem o Conventional Commits em português, com mensagens claras. O fragmento está em `changelog.d/`.

## Verificações rodadas (só o que o diff toca)
- `python3 -m unittest tests.test_forge_pareceres` com ambiente limpo: 40 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-g2-mitigacoes.json`: M50 (linha 70), M51 (linha 73), M52 (linha 55) e M53 (linha 54) morreram.
- `bin/forge-mutante --cobertura --base 707fea56…`: as três condições mudadas (linhas 55, 70 e 73) estão cobertas por M52, M50 e M51.
- Sonda da regex `REMOTO` (só leitura). O alias ssh `git@github-trabalho:dono/repo.git` resulta em `('github-trabalho', 'dono', 'repo')` e cai na recusa. `ssh://git@ssh.github.com:443/...` é recusado. `http://github.com/dono/repo.git` é aceito. É disso que tratam A1 e A2.

## Achados
- A1 (recomendado) bin/forge_pareceres.py:74 · origin com alias de host ssh (git@github-trabalho:dono/repo) ou ssh.github.com:443 recusa com "não é do repositório do origin", que engana: falha fechada certa, mas a mensagem deveria citar o host lido e o esperado, ou dizer que alias ssh não vale.
- A2 (recomendado) bin/forge_pareceres.py:14 · a regex aceita http:// (`https?`), mas a docstring da linha 49, a recusa e o changelog dizem "https ou ssh". Sem efeito de segurança, porque a URL do PR é https e host, dono e repo são comparados; alinhe o texto ou tire o `?`.

## Parecer
Aprovado. O corte faz o que a M18.1 pede, só aperta, falha fechado e tem um mutante morto por guarda. Os dois achados são recomendados (mensagem e texto) e viram cartão depois do merge, sem devolução.
