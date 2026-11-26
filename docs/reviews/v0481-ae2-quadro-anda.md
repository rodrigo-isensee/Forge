---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 59add0136ba78ab707d74575f2325327284126e9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (AE2, #875, E10.15)

Escopo: revalidação por delta, `f45bf805..59add013` (4.ª volta, E10.14). Delta lido: `forge-check parecer delta docs/reviews/v0481-ae2-quadro-anda.md`, com o que veio da `develop` fora. Do domínio, o único commit da branch é `3559c9aa3`: `tests/mutantes/v0481-ae2-quadro-anda-5.json` (ids), `tests/test_sobreposicao_quadro.py:499` (comentário) e o fragmento `changelog.d/v0481-ae2-quadro-anda.md` ("AE35 a AE41"). Os merges `c65fb3a97` e `59add0136` da `develop` (até o #885) entraram sem conflito (`git show --cc` vazio); o `bin/forge-fechar` e o `docs/fechamento-integrador.md` que o delta lista vieram da base e já foram revisados nos PRs de origem.

## Parecer
**Aprovado.** O A1 da rodada anterior (bloqueante) está corrigido: os sete ids de `-5.json` são AE35 a AE41, e as cinco specs do AE2 somam 41 ids sem repetição (AE1 a AE41). Código e testes iguais à rodada anterior; o comentário do teste e o fragmento do changelog acompanham os ids novos.

Conferido no head:
- Sonda S1 da rodada anterior refeita: `forge-mutante --ids AE35,AE33 -5.json -4.json` roda as duas specs juntas, rc 0, AE35 morreu (`bin/forge-check:5336`) e AE33 morreu (`bin/forge-fechar:952`).
- `forge-mutante -5.json`: AE35 a AE41 morreram (7 de 7). `forge-mutante --conferir --base f45bf805`: "o trecho de cada spec do diff está no lugar".
- `tests.test_sobreposicao_quadro`: 77 testes, OK.
- Tamanho (H1): o delta não tem linha de código. Commit em Conventional Commits, em português.

O A2 anterior (recomendado, `bin/forge-fechar:952`, o separador `---` em `coluna_do_cartao`) não foi tocado neste delta e segue como cartão depois do merge.

CI do head `59add013`: suítes 3.12 e 3.14 (partes 1 a 5), passos, verificações longas, instalação, teto de pulados, árvore já provada e `catraca` verdes. Vermelhos só `bateria (pareceres)` e `bateria`, que esperam este parecer.
- ci: 59add0136ba78ab707d74575f2325327284126e9 verde
