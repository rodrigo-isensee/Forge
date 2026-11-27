---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: d0f41115599f182b8e57b6b7dcd78f529bdad70f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.42, F6 corte do envio, PR #932, volta 3)

Delta lido: `forge-check parecer delta docs/reviews/v0481-f6-arvore-envio.md`, intervalo 023b0d68..d0f41115 (scripts/arvore-testada.py, tests/test_arvore_testada.py, spec de mutantes 8).

## Parecer
Aprovado no domínio do código. O A1 da segurança da volta 2 (S2, PR empilhado do mesmo ramo e head já mesclado ou fechado) está fechado: `prs_do_ramo_so_para_develop` (scripts/arvore-testada.py:177-189) lista os PRs do ramo com `state=all`, até `LIMITE_DE_PAGINAS` páginas de 100, e só prova se todos tiverem base `develop`; lista que não é lista, item fora do formato (o `campo` devolve None para não-dict, por isso a guarda `type(p) is not dict` saiu sem perda) ou o teto de páginas recusam. A exceção da listagem sobe e o `main` (linhas 251-252) a trata como falta de prova.

- Teste: `test_pr_empilhado_do_mesmo_ramo_ja_mesclado_ou_fechado_nao_prova` cobre empilhado na 1.ª e na 2.ª página, tipo errado, item fora do formato, item sem base, teto de páginas e a falha de rede, com o run próprio vermelho e o alheio verde e mais novo; e o caso positivo com duas páginas contra a develop. O falso da API casa a URL exata (`head=dono:<ramo>`, `state=all`, `page=n`), não prefixo.
- Mutantes: AE-M39, M40, M42 a M45 (spec -8), um por guarda nova; AE-M41 saiu com a guarda redundante. O `forge-mutante` com as specs 7 e 8 confere que o AE-M37 segue casando a linha 209.
- S1 de novo na API real (`prova_do_pr` com o `gh api`, 14 últimos commits da develop em primeiro pai): prova em 6, os mesmos da volta 2, entre eles 11fc1867 (#931, run 45959949382) e 2bdf1a2e (#929, run 45944840829); os 8 restantes seguem recusando.

Verificadores: `python3 -m unittest tests.test_arvore_testada` no head: 33 testes, OK. `bin/forge-mutante --processos 1` com as specs 7 e 8: AE-M36 a AE-M40 e AE-M42 a AE-M45, todos morreram.

CI lido nos check-runs do commit: partes 1 a 5, passos, verificações longas, python 3.14, instalação, teto de pulados e árvore já provada em success; `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres.

- ci: d0f41115599f182b8e57b6b7dcd78f529bdad70f verde
