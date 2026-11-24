---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp11-desenho
commit: 912a571dbf7b7caa93933c671255292b7d9ffc8b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E155.2, desenho BP11, DORA no placar)

Classe T, só documentação: `docs/propostas/bp11-dora-no-placar.md` (63 linhas, novo) e `changelog.d/v0480-bp11-desenho.md`. Nenhum código, hook, teste ou CI tocado (`git diff --stat e15c8566..912a571d`: 2 arquivos, 65 inserções). Teto H1 não se aplica (zero linhas de código).

## O que foi conferido
- **Evidências contra a develop e15c8566:** `bin/forge_dora.py` `releases` 29-39, `esperas_da_mudanca` 42-50, `falhas` 98-115, `calcular` 133-151; `bin/forge-placar` `METRICAS` e `GUARDADAS` 99-100, `cmd_placar` 449-471, `paradas_do_ci` 757, usada por `fases` (785). Batem com a tabela da seção 1.
- **Achado F1 (zero falso), reproduzido:** `docs/kanban/escapes.md` não existe na develop (`git ls-tree` só lista `limpeza-0.28.0.md`); `linhas_do_quadro` lê `ler_texto(arq) or ""` (`forge_dora.py:64`), então a ausência vira lista vazia e `taxa_de_falha` sai `entregas=39 com_falha=0 taxa_pct=0.0`. Rodado: `bin/forge-check dora --desde 2026-10-25` deu as mesmas linhas da seção 1 do desenho. O diagnóstico procede (`R-DECISAO`: dado ausente não é zero).
- **Decisões do dono:** D1 a D4 têm recomendação, cada uma com motivo; nenhuma contradiz linha DECISÃO DO DONO do v0478.
- **Critério de reversão** presente (seção 4); "Como medir" com 5 medidas e metas; custo e neutralidade declarados (`R-CUSTO`, `R-NEUTRO`).
- **Testes dos arquivos tocados:** `python3 -m unittest test_changelog test_citacao test_clareza` (em `tests/`): `Ran 110 tests ... OK`. A suíte inteira fica no CI do PR.

## Achados
- A1 (recomendado) docs/propostas/bp11-dora-no-placar.md:32 · Ausência só como "não existe": `ler_texto` devolve None também para link simbólico, arquivo acima do teto e erro de leitura (forge_governanca.py:94-100). O desenho deve tratar "não lido" (None) como `-`, não só o arquivo inexistente.
- A2 (recomendado) docs/propostas/bp11-dora-no-placar.md:41 · Nome divergente: "Como medir" exige `dora_restaurar_h`, mas a recomendação de D2 (:54) propõe `restaurar_release_h` e `develop_vermelha_min`. Alinhar a medida ao nome que a decisão escolher.
- A3 (recomendado) docs/propostas/bp11-dora-no-placar.md:45 · A medida de efeito usa `comparar --metrica taxa_de_falha`, mas o item 5 (:34) só põe `taxa_de_falha` em `METRICAS` depois de D3; sem D3 o comando não aceita a métrica. Condicionar a medida (e o critério de reversão) a D3.
- A4 (recomendado) docs/propostas/bp11-dora-no-placar.md:3 · A origem `docs/propostas/boas-praticas-1911.md` não existe no repositório, só na pasta de controle; quem lê o PR não acha a linha BP11. Citar onde ela está ou transcrever a linha.
- A5 (recomendado) docs/propostas/bp11-dora-no-placar.md:30 · `modulo_do_bin` é função do `forge-check`, não do `forge-placar`; o placar já importa módulos do bin pelo `sys.path` (forge-placar:95-96). Trocar a menção para o import direto, sem nova dependência entre os dois.

## Sondas

## Parecer
Aprovado. O desenho é só leitura, reusa a conta única do `forge_dora.py`, separa o que é da BP11 do que é do AE2 e corrige um defeito real e reproduzido (ausência que vira 0,0%). Os cinco achados são de precisão do texto e entram como cartão depois do merge ou no pedido de código da BP11; nenhum bloqueia um desenho que não muda comportamento.
