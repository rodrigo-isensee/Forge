---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-sem-mapa
commit: aec509298678b0987cc2b3943ca07d9c6a97a584
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (forge-testes-sem-mapa, cartão 15)

## Achados
- A1 (recomendado) bin/forge-testes:11 · A linha de uso `-k PADRAO` do docstring pertence à filtro-k, mas entrou neste commit: nesta branch o `-k` não existe. Não aparece no `--help`, que usa outra `description`. Mover a linha para o commit da filtro-k.

## Parecer
Aprovado. A divisão da pilha resolve o A1 (M14) do parecer de 1d7a02f. A leitura do cartão 15 vem daquele parecer.

- Delta sobre a leitura anterior: `git range-diff b45e40a..1d7a02f b45e40a..704a606` mostra que a1537d1 virou aec5092 com duas mudanças. O `elif` passou a usar `so_modulos := modulos_sem_mapa(pedidos)` (`bin/forge-testes:544`), o que resolve o A2 anterior com a mesma mensagem e o mesmo modo. O fragmento agora é `changelog.d/forge-testes-sem-mapa.md`.
- Comportamento: só vale quando todos os pedidos casam `tests/test_x.py` e existem (`modulos_sem_mapa`, `bin/forge-testes:182`). Pedido inexistente ou misturado com outro arquivo vai a `planejar` (mapa, falha fechada). Os dois testes novos cobrem os dois lados.
- Pre-push: o hook chama `--listar --base` sem CAMINHO, então o plano do diff não muda.
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em aec5092: 88 testes, OK, rc 0.
- M14: `git diff --numstat --no-renames b45e40a aec5092` dá `bin/forge-testes` 13 e `tests/test_testes_tocados.py` 41, 54 linhas, um comportamento. É a base da pilha e entra primeiro na develop.
- QA: aprovado sobre 704a606 (`docs/qa/forge-testes-034.md`, e7e40cd), CT-01 a CT-03. Sem shell no diff.
