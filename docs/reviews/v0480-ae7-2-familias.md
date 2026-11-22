---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae7-2-familias
commit: cb2043bc55d7cf94bdc4fcaf0f4bfa17f9ee7995
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E107.4, AE7.2 famílias geradas e alvo `entrega`, head cb2043bc)

Revisão completa única (R-REVIEW) do diff `b0895f6c..cb2043bc` (o merge cb2043bc traz a develop sem conflito; o diff contra
a base é só `bin/forge_comparar.py`, `tests/comparar/geradores.py`, `tests/test_comparar.py`, as três specs
`tests/mutantes/v0478-ae7-2-familias*.json`, `tests/pesos-d4.json` e o fragmento `changelog.d/v0480-ae7-2-familias.md`,
o escopo ampliado na E107.2). Critério do item: linha AE7.2 de `docs/propostas/v0479-melhorias-anti-erro.md`.

## Conferido
- Pedido: famílias geradas com semente fixa do comparador (`SEMENTE = 478`, nunca da árvore medida) e impressa na linha
  `familias: semente=<n> ...`; gerador de cada lado roda com `python3 -I -`, ambiente mínimo e HOME/TMPDIR temporários;
  gerador que falha, passa do prazo ou emite caso inválido sai `nao-verificavel`; caso gerado que some é `corpus-removido`
  (inclusive o gerador que ignora a semente, `test_gerador_sem_semente_fixa_e_corpus_removido`). Alvo `entrega` só pela
  API (`executar_entrega`), a CLI fica para o AE7.3, como o pedido separa.
- Caso do E50 (DECISÃO DO DONO 20/11): `CasoDoE50` mede c872be89 (pai do squash do #734) contra f96ede50 com a fixture real
  do `ParecerMescladoNaVolta` e acha `aceite-novo`; no sentido inverso, rc 0. Sonda S1 abaixo: a recusa da base é a regra do
  E50, não um erro de argumento do forge-check antigo. Os dois commits estão na `develop` e os jobs de teste do CI usam
  `fetch-depth: 0`. A herança de `selo.Conferencia` não duplica teste (a classe base não tem `test_`).
- Guardas: um mutante por guarda nas três specs (AE72-1 a AE72-24), cada um com teste de comportamento do ramo de falha.
- Tamanho (H1): `bin/forge_comparar.py` +86/-9 com docstring; o gerador fica em `tests/`; abaixo de 150.
- R-NEUTRO: os núcleos do gerador são comandos do fluxo da fábrica (git, gh), sem nome de projeto.
- Commits em Conventional Commits, fragmento de changelog presente.
- Teste afetado rodado: `python3 -I -m unittest discover -s tests -p test_comparar.py`, 84 testes, os 18 novos verdes.
  Uma falha em `LadosSeparados.test_hook_do_head_nao_alcanca_a_base`, fora do diff: falha igual na árvore da base
  b0895f6c neste sandbox (TMPDIR compartilhado); o CI do PR decide.

## Achados
- A1 (recomendado) bin/forge_comparar.py:336 · o HOME/TMPDIR do alvo entrega é um por lado, comum a todos os casos: o que um forge-check grava no HOME chega ao caso seguinte (ordem por id); crie um HOME por caso, como já se faz com a cópia da fixture.
- A2 (recomendado) tests/test_comparar.py:905 · o caso do E50 afirma só o rc; se a fixture derivar e o forge-check antigo recusar por outro motivo (argumento, formato), o teste segue verde sem medir o E50 (S1 mostra que hoje mede). Fixe o motivo, por exemplo uma fixture de controle que a base aceita.
- A3 (recomendado) bin/forge_comparar.py:93 · o gerador roda mesmo quando o `cat-file blob` falhou (stdin vazio) e só depois o `cod` é lido; confira o `cod` antes do subprocess.
- A4 (recomendado) bin/forge_comparar.py:359 · o `corpus=` do alvo entrega resume id, argv e HEAD da fixture, mas a cópia leva a árvore de trabalho; fixture suja dá o mesmo resumo com entrada diferente. Recuse fixture suja ou some o `status --porcelain` ao resumo.

## Sondas
- S1 · `CasoDoE50` com o `subprocess.run` espiado no prazo de 120 s · espera: base rc 1 pelo escopo do parecer, head rc 0 · obtido: base rc 1 com `escopo: fora do declarado no brief "docs/reviews/x.md"`, head rc 0 com `escopo: ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer)`
