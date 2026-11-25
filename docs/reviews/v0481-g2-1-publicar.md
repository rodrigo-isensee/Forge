---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: dc6bc47efb98f0f017510992325e629f64e29214
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E6.26, #878, G2.1: forge-check parecer publicar; classe C), 3ª volta por delta

Revalidação por delta da rodada que reprovou em 841c14dc (E6.22; texto no git). Delta lido: `forge-check parecer delta` deste arquivo e os 4 commits do autor em `git diff 841c14dc..dc6bc47e` (a370aec9, d109dad5, 0a23ae11, dc6bc47e); o resto do intervalo veio da `develop` (55ee8a5b, 30174222, 0c68c880) e fica fora do domínio.

## Achados
- A2 (recomendado) hooks/conformidade.py:113 · Forma opaca (`python3 $(command -v forge-check)`) do A2 do E6.18, sem mudança neste delta: segue como cartão depois do merge.

## Sondas

## Achados anteriores
- A1 (bloqueante): corrigido. `ultima_raiz` para no `--` (hooks/conformidade.py:1387), como o argparse, que toma o resto como posicional. A fixture `contrib-publicar-raiz-depois-do-separador-no-forge-bloqueia` é a S4 do E6.22 e barra com R-CONTRIB; as fixtures das formas S1 e S2 seguem barrando e o inverso segue liberando.
- A2 (recomendado): segue como cartão (A2 acima).

## Leitura do delta
- **O que deixou de barrar:** nada. A guarda nova só encerra a leitura no `--`; antes dele a leitura é a mesma do 841c14dc.
- **Testes sem enfraquecer:** `test_fixtures_do_publicar` sobe o mínimo de 8 para 9 e mantém os dois lados (item 11 do checklist). `tests/test_forge_pareceres.py` passa o `env` do git pelo `sem_manutencao` (ponto único do ambiente, AR-4), sem tirar asserção.
- **Mutantes:** M37, um para a linha de guarda nova; o dc6bc47e troca só a condição e mantém o comentário, e a spec confere no lugar (AR-12).
- **Índice:** a linha do `forge_pareceres.py` em `docs/indice-forge.md`.
- **Tamanho (H1):** 2 linhas de código no delta.
- **Commits:** Conventional Commits em português, com o pedido e a etapa.

## Verificações
- Rodados aqui no dc6bc47e: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_publicar tests.test_forge_pareceres` (36 testes, OK); `bin/forge-mutante --processos 1 --ids M37` na spec `-6` (morreu, hooks/conformidade.py:1388); `bin/forge-mutante --conferir --base 841c14dc` (trechos no lugar); `--cobertura --base 841c14dc`: nenhuma guarda do item sem mutante (o único `não coberto` é `tests/pesos-d4.json`, vindo da develop).
- CI do dc6bc47e: suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados, bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação e árvore já provada na develop verdes. Falham só os que esperam parecer ou rótulo: `bateria (pareceres)` (R-REVIEW e R-QA sem parecer aprovado no head), `bateria` (agregado: pareceres failure) e `catraca` (log: R-CONFORMIDADE pela mudança em `bin/forge-check` e `hooks/conformidade.py`, controles que pedem o rótulo do dono depois do último push, ADR 0008).
- ci: dc6bc47efb98f0f017510992325e629f64e29214 verde

## Parecer
Aprovado. O delta fecha o A1 do E6.22 com uma guarda, uma fixture e um mutante que morre, e não enfraquece teste. O A2 segue recomendado, como cartão depois do merge. A catraca espera o rótulo do dono.
