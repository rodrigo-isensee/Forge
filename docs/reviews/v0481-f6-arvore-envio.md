---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: 023b0d68c5f67c64236363d17e5d17f2fdaea770
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.38, F6 corte do envio, PR #932, volta 2)

Delta lido: `forge-check parecer delta docs/reviews/v0481-f6-arvore-envio.md`, intervalo dcd4003c..023b0d68 (scripts/arvore-testada.py, tests/test_arvore_testada.py, specs de mutantes 5 e 7).

## Parecer
Aprovado no domínio do código. O A4 da volta 1 está resolvido como pedido: scripts/arvore-testada.py:190-191 descarta o run cuja lista `pull_requests` traga PR que não seja o `numero` contra a develop, ou que não seja lista; lista vazia segue valendo. O `numero` chega do `prova_do_pr` sem outra mudança de assinatura.

- Teste: `test_run_de_outro_pr_do_mesmo_ramo_e_head_nao_liga_ao_pr_da_develop` cobre outra base, mesmo número com outra base, o próprio junto de outro e tipo errado, com o run próprio vermelho e o alheio verde e mais novo; e o caso positivo com o próprio PR na lista. O ataque da S3 voltou ao teste.
- Mutantes: AE-M36 a AE-M38 (spec -7), um por guarda da linha 191; AE-M23 (spec -5) realinhado à linha seguinte (`ligados`).
- S3 de novo (o mesmo falso da volta 1): `(False, 'nenhum PR mesclado em aaaaaaa ...')`.
- S1 de novo na API real (`prova_do_pr` com o `gh api`, 14 últimos merges da develop): prova em 6, os mesmos da volta 1, entre eles 11fc1867 (#931, run 45959949382) e 2bdf1a2e (#929, run 45944840829); os 8 restantes seguem recusando.
- O caso "o próprio e outro" recusa um run que lista os dois PRs; é falha fechada (a suíte do push roda inteira), sem risco.

Cito sem refazer: o parecer de segurança da volta 2 (2477d634) reprova pelo A1, a lista também se esvazia quando o PR de outra base é mesclado ou fechado, e então o run dele volta a passar. A minha sugestão do A4 ("vazia só depois do merge") partia dessa premissa incompleta; a correção daquele achado é do autor com a segurança e o merge espera o portão dela.

Verificadores: `python3 -m unittest tests.test_arvore_testada` no head: 32 testes, OK. `bin/forge-mutante --processos 1` com as specs 5 e 7: AE-M21 a AE-M27 e AE-M36 a AE-M38, todos morreram.

- ci: 023b0d68c5f67c64236363d17e5d17f2fdaea770 verde (check-runs do commit: partes 1 a 5, passos, verificações longas, python 3.14, instalação, árvore já provada e teto em success; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres)
