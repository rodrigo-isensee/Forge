---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-espera-longa
commit: b51d34bc0ae398f75f1a4fa571ab2abd3f459f80
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: mp1311-espera-longa

## Achados
- A1 (recomendado) skills/esperar-estado/SKILL.md:12 · a regra 2 ainda proíbe `run_in_background` para esperar, sem ressalva; a regra 6 o manda na sessão principal. Acrescente "salvo a regra 6". Atendido em b51d34bc.

## Sondas

## Parecer
Aprovado, head af4bd16f (classe C, item 8). Decisão do autor conferida: o laço sem teto fica só na sessão principal em segundo plano (regra 6) e o subagente segue a regra 2, chamadas de 170 s repetidas até o estado terminal; o texto diz isso e o teste de texto o fixa. O laço sem teto sai nos mesmos estados do laço com teto (`fim=MERGED|CLOSED|checks:<c>|erro`), sem `fim=teto`.

Teste novo rodado (`tests/test_esperar_estado.py`, 15 testes OK): o laço longo passa de 5 leituras (13 leituras, sai em MERGED); `laco()` ganhou o filtro `seq 1` para não confundir os dois blocos. Guardas: o diff não muda código de controle do Forge (só o bloco de exemplo da skill, coberto por teste de comportamento), então não há mutante a declarar. Tamanho: 33 linhas de teste, um comportamento. Suíte inteira: CI do PR. Sem PR ainda.

A1 é só de coerência de texto; não devolve.

## Revalidação por delta (af4bd16f..b51d34bc)
Lido `forge-check parecer delta`: só `skills/esperar-estado/SKILL.md`, texto enxugado. As 6 regras seguem presentes (espere o estado, teto de 170 s, PR, envio longo em subagente, trava `pesado`, CI longo); nenhuma saiu. A regra 2 ganhou "salvo a regra 6" (A1 atendido), `fim=teto` segue com código 1, a tabela de saídas e os dois laços ficam iguais. Rodados `tests.test_esperar_estado` e `tests.test_metricas_texto`: 17 testes OK. Aprovado, head b51d34bc.
