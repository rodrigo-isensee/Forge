---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 83a8ce1713df9e363bbd80f93a61ae8e87288579
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E3.45 (melhoria/v0478-guardas-parecer), revalidação no head 83a8ce17

## Revalidação
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
