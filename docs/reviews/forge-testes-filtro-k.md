---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-filtro-k
commit: 704a60655e092b56eb3d2b7ac5c1745978c90ef7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (forge-testes-filtro-k, cartão 20)

## Achados
- A1 (recomendado) bin/forge-testes:627 · No modo completo, `comando` é a própria lista global `SUITE_COMPLETA`, e `comando += ["-k", filtro]` a altera no lugar. Hoje não muda nada, porque `main` roda uma vez por processo e nenhum teste a chama dentro do processo. Use `comando = comando + [...]` ou copie a lista antes.

## Parecer
Aprovado. A divisão da pilha resolve o A1 (M14) do parecer de 1d7a02f. A leitura do cartão 20 vem daquele parecer.

- Delta sobre a leitura anterior: `git range-diff b45e40a..1d7a02f b45e40a..704a606` mostra que 1d7a02f e 704a606 têm o mesmo código. Só o fragmento mudou, agora `changelog.d/forge-testes-filtro-k.md`.
- Comportamento: `-k` repetível (`bin/forge-testes:554`) é anexado ao comando nos dois modos. No completo, ele vai para o `unittest discover`, que aceita `-k`. O `-k` é recusado com `--vermelho` (`:569`). Os testes cobrem o filtro, a soma de padrões e a recusa.
- `-k` sem correspondência sai com o rc 5 do unittest e sem mensagem do forge-testes. É herdado e o QA já registrou.
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em 704a606: 94 testes, OK, rc 0.
- M14: `git diff --numstat --no-renames 7d20b39 704a606` dá `bin/forge-testes` 7+1 e `tests/test_testes_tocados.py` 12, 20 linhas, um comportamento. A branch está empilhada sobre a aviso-mapa e a sem-mapa, que entram antes na develop.
- QA: aprovado sobre 704a606 (`docs/qa/forge-testes-034.md`, e7e40cd), CT-05 a CT-07. Sem shell no diff.
