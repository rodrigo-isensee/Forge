---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-autoria
commit: f0c380e28827a0c6168b142dd65d3499faef0dd7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E21.2, #914, G2-M9-2-AUTORIA: autoria do parecer a publicar), 1.ª rodada completa

Diff lido: `git diff b4ae1755..f0c380e2` (merge-base com a `develop` = Base-sha), 2 commits do autor (35bc4d11, f0c380e2). Código: `hooks/conformidade.py` (+11/-5, 16 linhas) e `bin/forge-testes` (o módulo novo em `FORGE_CHECK` e `RODAM_OS_HOOKS`); teto H1 dentro.

## Achados
- A1 (recomendado) bin/forge-check:3901 · `recusa_do_publicar` casa só sha256 e papel, não o caminho: texto do tech-lead registrado em docs/reviews/ e copiado sem hook para .forge/pareceres/ publica (rc 0). Mesmo texto do mesmo papel, anterior ao diff; atar ao caminho registrado como defesa em profundidade.
- A2 (recomendado) hooks/conformidade.py:4069 · `PARECER_A_PUBLICAR` repete a regex do caminho de `recusa_do_publicar` (bin/forge-check:3887); hoje iguais, sem teste que as amarre: uma muda e a outra fica. Um teste de paridade ou uma fonte única evita a deriva.

## Leitura
- **Faz o que o cartão pede (E21.1):** o filtro da `autoria()` passa a aceitar o par `(".forge", "pareceres")` e o registro aceita `.forge/pareceres/<pedido>/<tipo>.md` por `fullmatch`; o papel registrado é o `guarda.papel` de quem gravou, como já era para `docs/`. As quatro pastas de `docs/` mantêm o comportamento (a troca `par == ("docs", pasta)` por `par in PASTAS_DE_AUTORIA` é equivalente para elas). Não afrouxa: só um caminho a mais passa a ser registrado, e o `parecer publicar` continua exigindo sha256 e papel do tipo (M9.1).
- **Quem grava:** a regra de papel por caminho do `hooks/conformidade.json` (linhas 79 a 82, desde o #878) limita a escrita de `.forge/pareceres/*/<tipo>.md` ao papel do tipo; se outro papel gravar, o registro leva o papel dele e o publicar recusa (teste `test_ponta_a_ponta_recusa_autoria_de_outro_papel`).
- **Risco apontado pelo autor (A1):** confirmado por sonda (texto gravado pelo hook em `docs/reviews/v9.md`, copiado com `shutil.copy` para `.forge/pareceres/v9/review.md`, publicar rc 0, registros só com o caminho de `docs/`). Não é falsificação: o texto é o do papel certo, com o mesmo `commit:`; e o comportamento é anterior a este diff, que não toca `bin/forge-check`. Fica como cartão.
- **Testes:** 6 testes, 3 deles de ponta a ponta (hook de verdade em subprocesso com `ambiente_limpo()`, `forge-check` em processo, `gh` falso de `test_forge_pareceres`, sem rede); o ramo de falha de cada guarda tem teste de comportamento (subpasta a mais, sem pedido, extensão e pasta erradas, papel trocado, sem registro). Duas fixtures novas do corpus em `tests/hooks/conformidade/`.
- **Mutantes (guardas do diff):** as duas linhas de guarda mudadas (4079, filtro de pasta; 4084, caminho do registro) têm mutante declarado (M1/M5 e M2/M3), mais M4 no papel do registro.
- Registros em dia: `pesos-d4.json` com o módulo novo, fragmento `changelog.d/v0481-g2-autoria.md`, commits em Conventional Commits com o pedido.

## Verificações
- Rodados aqui no f0c380e2: `python3 -I tests/test_conformidade_pareceres.py` (6 testes, OK); `bin/forge-mutante --processos 1 tests/mutantes/v0481-g2-autoria.json` (M1 a M5 morreram, rc 0); `bin/forge-mutante --cobertura --base b4ae1755` (linhas 4079 e 4084 cobertas; rc 0).
- CI do f0c380e2 (run 45846920662 e Catraca 45846920412): suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), instalação e árvore já provada na develop verdes. Falham só os que esperam parecer ou rótulo: `bateria (pareceres)` (R-REVIEW: sem parecer de review aprovado), `bateria` (agrega a de pareceres) e `catraca` (mudança em `hooks/conformidade.py` pede o rótulo `afrouxa-regra` do dono depois do último push).
- ci: f0c380e28827a0c6168b142dd65d3499faef0dd7 verde

## Parecer
Aprovado. A mudança é pequena, faz só o que a E21.1 pede e tira a trava que fazia o `parecer publicar` recusar sempre, sem afrouxar a conferência de sha256 e papel. Os mutantes das guardas morrem e os testes de ponta a ponta exercitam o hook real. A1 e A2 são recomendados e viram cartão depois do merge. A catraca espera o rótulo do dono.
