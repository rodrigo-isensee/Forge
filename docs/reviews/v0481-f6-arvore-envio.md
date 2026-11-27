---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: dcd4003c3bbb728d86c2e16a9df0aefad46a2036
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.34, F6 corte do envio, PR #932, volta 1)

Delta lido: `forge-check parecer delta docs/reviews/v0481-f6-arvore-envio.md`, intervalo 1567d509..dcd4003c (docs/protecao-de-branch.md, scripts/arvore-testada.py, tests/test_arvore_testada.py, specs de mutantes 1, 4, 5 e 6).

## Achados
- A4 (bloqueante) scripts/arvore-testada.py:182 · nada liga mais o run ao PR da develop: run mais recente de outro PR aberto, mesmo ramo e head, contra outra base prova com o run da develop vermelho (S3). Recuse o run cuja lista pull_requests, quando não vazia, traga PR que não seja o número contra a develop.

## Sondas
- S3 · falso do teste: runs=[rodada() com job bateria failure, rodada(id=556, pull_requests=[#99 base homolog]) com bateria success] · espera: (False, ...) · obtido: (True, 'árvore 1111111 igual à do head 3333333 do PR #77, run 556, job bateria')

## Parecer
Reprovado, só pelo A4. Os achados da 1.ª rodada estão resolvidos:
- A1 resolvido: S1 de novo na API real (prova_do_pr com o `gh api`) nos 14 últimos merges da develop: prova em 6, entre eles 11fc1867 (#931, run 45959949382) e 2bdf1a2e (#929); os 8 que não provam têm a árvore do merge diferente da do head do PR (conferido um a um), recusa correta.
- S2 de novo: o run 45959949382 do #931 segue com `pull_requests` de tamanho 0 após o merge; a ligação por `head_sha` e `head_branch` não depende dele.
- A2 resolvido: o falso põe `pull_requests: []` no run do caso positivo, no formato real, e prova.
- A3 resolvido: docs/protecao-de-branch.md:31 diz que o `arvore-envio` em falha deixa as partes puladas e o agregador vermelho.

A4 (regressão do A1 do parecer de segurança do #929, que o próprio docs/protecao-de-branch.md:31 promete: "de outra base não prova"): o filtro do run agora é head_sha, head_branch, evento, path, repositório e status; nada liga o run ao PR da develop. O `max(validas)` escolhe o run mais recente, e um PR do mesmo ramo contra a homolog (ou outra base) testa a mescla com outra base, não a árvore do head. Os casos "run do PR contra outra base" e "run de outro PR" saíram do teste sem substituto. A API real deixa a lista vazia só depois do merge do PR; o PR aberto contra outra base aparece nela, então a guarda "lista não vazia só com o número contra a develop" fecha o caso sem quebrar o S1. Volte com o caso no teste e o mutante da guarda.

Resto do delta: base pela `base.sha` do PR com compare ahead/identical, fork pelo `head_repository` e pelo `head.repo` do PR, caso behind (AE-M19) e commit sem pai cobertos; as specs 4 a 6 batem com as guardas.

Verificadores: `python3 -m unittest tests.test_arvore_testada` no head: 31 testes, OK. `bin/forge-mutante --processos 1` com as 6 specs do item: AE-M1 a AE-M35, todos morreram.

- ci: dcd4003c3bbb728d86c2e16a9df0aefad46a2036 verde (`gh pr checks 932`: partes 1 a 5, passos, verificações longas, python 3.14, instalação, árvore e teto em pass; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres)
