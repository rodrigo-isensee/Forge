---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 6c5d30e56c862c2c300bd412816ded091f786fd7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E3.42 (melhoria/v0478-guardas-parecer), revalidação da junção com a develop no head 6c5d30e5

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 993b6bb3..6c5d30e5. Na primeira linha da branch, 3f7b32bc, 84231068 e 45725837 só trazem pareceres; o código vem do merge 6c5d30e5 (develop em eca1d21b). O aviso do delta sobre 052fb74 é um merge da própria branch (os dois pais estão em origin/melhoria/v0478-guardas-parecer), por isso a ferramenta listou bin/forge-testes, docs/hooks.md, tests/pesos-d4.json e tests/test_hooks.py inteiros.
- Esses quatro arquivos: `git diff eca1d21b 6c5d30e5` dá o mesmo diff da branch sobre a base de merge (test_hooks_parecer_repo e test_hooks_parecer_matriz em FORGE_CHECK, test_hooks_parecer_repo em REAPROVEITAM_O_LOTE); a junção não mudou o que já estava aprovado.
- Conflito (`git show --remerge-diff 6c5d30e5`): só tests/test_testes_tocados.py:79. A resolução fica com a forma da develop (assertIn de test_indice_forge, contagem sem ele) e conta 104 = 102 da develop + test_hooks_parecer_matriz e test_hooks_parecer_repo, os dois módulos que só esta branch soma ao FORGE_CHECK. Nada fora do delta relido.

## Conferências
- Teste do conflito: `python3 -m unittest tests.test_testes_tocados`: 162 testes, OK (skipped=1), 51 s.
- Tamanho (H1): a junção não soma código; uma linha de teste resolvida.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Achados
- A2 (recomendado) hooks/parecer.py:1162 · herdado da E3.39, sem mudança: a mensagem lista "variável, ~ com HOME mexido, CDPATH, crase ou $( )", mas o `cd` literal em subshell também recusa (S44); incluir "subshell ou condicional" na mensagem e na D6.

## Parecer
Aprovado: a junção com a develop preserva o código aprovado no head 993b6bb3 e a contagem 104 do conflito está certa. A2 segue recomendado (cartão), sem volta.
