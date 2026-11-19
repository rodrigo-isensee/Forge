---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: a96a986cc8712f4e469b596dbb8788b403352590
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E3.45 (melhoria/v0478-guardas-parecer), revalidação no head a96a986c

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 6cfebb4c..a96a986c (junção com a develop 153c0152, dois conflitos resolvidos); no domínio: bin/forge-testes, docs/hooks-fixtures.md, docs/hooks.md e tests/test_testes_tocados.py, todos vindos da develop (E18, #695 e #697), nenhum da branch.
- tests/test_testes_tocados.py: a contagem fixa deu lugar ao conjunto mínimo da develop (todo módulo do FORGE_CHECK e dos evals de forma por `assertIn`, sem extras, piso de 90); o diff contra a develop ficou sem diferença nesse teste e o teste passa no head. Cobertura não removida.
- docs/hooks-fixtures.md: `scripts/indice-fixtures.py --conferir` diz "em dia" (3097 fixtures no índice e no corpus).
- Código de hook da branch: `git diff 6cfebb4c a96a986c -- hooks/parecer.py hooks/_gh_api.py` vazio; o que mudou em hooks/ (conformidade, agentes) é da develop. O veredito anterior segue.

## Revalidação anterior (head 6cfebb4c)
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 83a8ce17..6cfebb4c; no domínio: só docs/indice-forge.md, 1 linha a mais (`_gh_api.py` na tabela de hooks). Nenhum código nem teste mudou; o aviso do merge d45bf21 fora da develop local não altera o delta.
- docs/indice-forge.md:58 só documenta o arquivo, em ordem alfabética; o veredito anterior segue.

## Revalidação anterior (head 83a8ce17)
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 650be460..83a8ce17; no domínio: docs/hooks.md e tests/fixtures/heredoc-volta-unica.json, mais o fragmento changelog.d/v0478-guardas-parecer.md. 3 arquivos, 4 inserções, 3 remoções; nenhum código de hook mudou.
- tests/fixtures/heredoc-volta-unica.json:235 e :237: só a expectativa do `parecer` de CN2 e VA2 passa de 0 para 2 (e a `origem` explica); o `conformidade` fica (CN2 0, VA2 2). É a recusa da D2 já aprovada chegando ao corpus: falha fechada que recusa a mais, nada afrouxa.
- docs/hooks.md:39 (D2) descreve o mesmo caso e cita as fixtures; o changelog bate com o diff.

## Conferências
- Sonda (gh falso no PATH, bash chamado do Python): `$(printf bash) -c '<gh pr merge 1 --squash>'` e `"$BASH" -c '<…>'` gravaram as duas `GH-FALSO pr merge 1 --squash`; o corpo roda, a expectativa 2 é a certa.
- Corpus da volta única: `python3 -m unittest tests.test_hooks_volta_corpus`: 16 testes, OK, 307 s.
- Tamanho (H1): sem código; duas linhas de fixture.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Achados
- A2 (recomendado) hooks/parecer.py:1162 · herdado da E3.39, sem mudança: a mensagem lista "variável, ~ com HOME mexido, CDPATH, crase ou $( )", mas o `cd` literal em subshell também recusa (S44); incluir "subshell ou condicional" na mensagem e na D6.

## Parecer
Aprovado: o delta só alinha CN2 e VA2 do corpus à recusa da D2, provada com gh falso, e o corpus passa no head 83a8ce17. A2 segue recomendado (cartão), sem volta.
