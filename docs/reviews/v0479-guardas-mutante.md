---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-guardas-mutante
commit: b2c7255d6e0013f91c7db551c3ab08bcdd4a8589
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E62.12, melhoria/v0479-guardas-mutante)

Diff revisado: `8ee73d15..b2c7255d` (Base-sha do brief até o Revisar-sha), 4 arquivos, 100 inserções, nenhuma linha de `bin/forge-check` mudada.

## O que foi conferido
- **Escopo (E62.11):** cinco mutantes declarados em `tests/mutantes/v0479-guardas-0-47-12.json` para os trechos que a catraca do #737 apontou (G1 `ref or "HEAD"` dos testes do QA, G2 `ref or "HEAD"` do domínio, G3 base do brief ao `pr`, G4 `parecer_que_aprova`, G5 recusa do commit só de pareceres paralelos), mais dois testes novos de comportamento (`PrLeARefNaoOHead`, `BaseDaEtapa`) e o fragmento de changelog. Faz o que o item pede, sem código de produção.
- **Trecho no lugar:** cada `de` aparece uma vez só em `bin/forge-check` no head; `bin/forge-mutante --conferir --base 8ee73d15` confirma.
- **Mutantes (rodados aqui, 1 processo):** `bin/forge-mutante --processos 1 tests/mutantes/v0479-guardas-0-47-12.json` → G1 `bin/forge-check:2050`, G2 `:2094`, G3 `:8837`, G4 `:2073`, G5 `:2092`, todos `morreu`, rc=0. `--cobertura --base 8ee73d15` sem condição pendente.
- **Testes novos:** `python3 -m unittest tests.test_parecer_conteudo.PrLeARefNaoOHead tests.test_forge_check_pr.BaseDaEtapa` com ambiente limpo (`env -i`) → 4 testes, OK. São testes do ramo de falha por comportamento (HEAD destacado no commit revisado e a ref adiante; `mock` de `pr_da_cli` lendo o `base` passado), nenhum lê o texto da fonte. G4 e G5 usam testes já existentes, que matam o mutante.
- **Suíte:** não rerrodada (brief: sem suíte local; a suíte inteira fica no CI do PR, `R-REVIEW`).
- **Regras:** `R-NEUTRO` sem termo de projeto; `R-VERIFY` e `R-MAIN` sem efeito no diff; tamanho por item (H1) dentro do teto, já que não há linha de código fora de teste e documentação.

## Parecer
Aprovado. Os cinco mutantes morrem com os testes declarados, os trechos estão no lugar e os testes novos passam no head b2c7255d; nada a ajustar.
