---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: 4ddaa68bb20c6f79d68e518b9c7e2ab72aa04782
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.25, H1-ferramenta)

Diff `681d4b33...4ddaa68b`: `bin/forge_tamanho.py` novo, `tamanho_do_pr` e os avisos do `brief gerar` em `bin/forge-check`, `test_forge_tamanho` no `FORGE_CHECK` (91), 19 mutantes em `tests/mutantes/v0474-h1-ferramenta*.json`, M29 e M30 de `lote-l08-e7.json` realinhados.

Conferido: classificação pelo `e_codigo` do T1 (testes, docs e `changelog.d/` fora), como na decisão do dono de 17/11 11:15; o item soma 114 linhas de código (bin/), dentro do teto. Uma guarda por mutante declarado (M1 a M19). `python3 -m unittest tests.test_forge_tamanho tests.test_t1_codigo_sem_teste tests.test_testes_tocados`: `Ran 189 tests in 241.043s`, `OK (skipped=1)`. A suíte inteira fica no CI do PR.

## Achados
- A1 (bloqueante) bin/forge-check:1427 · o pr reprova também com PR CLOSED ou MERGED da branch (gh pr view <branch> devolve o último); o pedido e a docstring dizem só PR aberto. Gatilho: branch com PR antigo fechado. Ajuste: só confere com state OPEN, com teste e mutante (S1, R-REVIEW)
- A2 (recomendado) bin/forge_tamanho.py:13 · LINHA_DE_MOTIVO aceita qualquer <n>: uma linha com 151 deixa passar o item que cresceu para 400; conferir n >= total, ou dizer no texto que o número é livre

## Sondas
- S1 · tamanho_do_pr com item de 151 linhas e gh falso {"state": "CLOSED"} e depois "MERGED", corpo sem a linha do teto · espera: [] e só o aviso · obtido: ['pr: tamanho: 151 linhas de código acima do teto de 150 sem a linha ... no corpo do PR #7'] nos dois

## Parecer
Reprovado por A1: a reprovação do corpo vale só com o PR aberto (requisito do E2.13), e hoje vale com qualquer PR que o gh devolva para a branch. Sugestão: em `tamanho_do_pr`, `if not pr or pr.get("state") != "OPEN": return []` antes do `falta_de_motivo`, com um teste do ramo CLOSED/MERGED e o mutante da guarda nova na spec `-2` ou numa `-4`. A2 não devolve.
