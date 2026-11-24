---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 64c4dd9ba9c4b3484431167e1b7a42adc7b80ec5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E174.2, D7, PR #868, `forge-check criterios`)

## Achados
- A1 (bloqueante) skills/produto-criterios/SKILL.md:16 · o passo 6 e a frase nova do passo 2 estouram a linha de base do texto: caracteres 2025>1417, frase_max 45>25, frase_media_x10 180>149, linhas_longas 8>7; test_metricas_texto vermelho no CI (parte 1/5, 3.12 e 3.14) e reproduzido local. Mova o detalhe e deixe o resumo
- A2 (recomendado) bin/forge-check:11113 · `criterios` entra no ramo do `proximo` com um ternário que repete o teste de `a.cmd`; um `if a.cmd == "criterios":` próprio lê melhor e não acopla os dois subcomandos
- A3 (recomendado) skills/produto-criterios/SKILL.md:16 · o campo `cobre: C-n` só aparece nesta skill; o modelo do `## Pronto quando` do brief (`forge-check brief gerar`) e o R-PROVA não o citam, então o Jarvis não o preenche e a tabela sai toda "não entregue"; cartão para levar o campo ao gerador

## Parecer
Reprovado por A1 (defeito provado: suíte vermelha no head revisado).

- Pedido: cumpre o D7 de `docs/anexos/estudo-deterministico-2411.md` (rastreio leve, tabela montada pela ferramenta a partir das provas conferidas, critério sem prova sai "não entregue"). Só leitura e sem rede; não é trava nova, então a regra "trava nova só se outra sair" não se aplica.
- Código: 73 linhas no `bin/forge-check` (abaixo do teto H1), um comportamento. Reaproveita `etapas_conferidas` (A4), `BRIEF_SELADO` (caminho preso a `docs/briefs/` pelo regex, sem travessia), `secoes_por`, `sem_controle` e `caminho_impresso`; texto do pedido sai saneado e cortado em 160. Leitura do `Cobre:` igual à das outras 3 funções.
- Testes: `tests/test_criterios.py`, 7 casos (entregue/não entregue, todos entregues rc 0, sem entrega conferida, `cobre:` fora, id repetido, `id:` do pedido, rc 2). Subprocesso com ambiente limpo e `python3 -I`. Rodei: `Ran 7 tests ... OK`.
- Mutantes: 17 declarados em 3 arquivos (até 8 por arquivo), um por guarda; a catraca do head passou numa das rodadas e o autor relata 17 mortos. Não rerrodei.
- CI do head 64c4dd9b: suíte parte 1/5 vermelha nas duas versões só pelo `test_metricas_texto.MetricasDoTexto.test_nenhuma_metrica_passa_do_teto` (A1); `bateria (pareceres)` vermelha pela falta dos pareceres, esperado neste ponto.
- Correção de A1 (diretriz 25, mensagem do próprio teste): não suba o teto nem resuma a regra; mova o detalhe do passo 6 (quando conta como entregue, formato do `cobre:`) para um arquivo de apoio que a skill manda ler e deixe uma frase curta. Volta pelo delta.

## Sondas
- S1 · `python3 -m unittest test_metricas_texto.MetricasDoTexto.test_nenhuma_metrica_passa_do_teto` (em tests/, head 64c4dd9b) · espera: OK · obtido: FAILED, 4 estouros em skills/produto-criterios/SKILL.md
