---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: 7bf55772445e422b84ac551433ddf1f60e86a9bc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E22.11, #913, revalidação por delta, volta 2)

Delta lido: `forge-check parecer delta docs/reviews/v0481-ci-parecer-nao-cancela.md`, intervalo `8e9f5704..7bf55772`, sem o que veio da base (develop), no domínio: `.github/workflows/obsoletas.yml`, `tests/mutantes/v0481-ci-parecer-nao-cancela.json`, `tests/pesos-d4.json`, `tests/test_ci_nao_cancela_parecer.py`.

## Parecer
Aprovado. A7 e A8 da rodada anterior resolvidos no delta:
- A7: o laço do `obsoletas.yml:51-53` lê o `head_sha` de cada run do ci.yml e só cancela com `sha != HEAD_SHA`, mesma origem e `id < RUN_ID`. O CI do próprio head segue, qualquer que seja o id; o `HEAD_SHA` já vinha só por `env:` (linha 30), sem `${{ }}` no script. O `id -lt RUN_ID` fica como proteção do run de head mais novo e não atrapalha.
- A8: o `gh` falso traz os runs 4 e 8 com o head atual (`def`) e id menor que o `RUN_ID` (10); o teste novo afirma que nenhum dos dois cai, e os testes antigos seguem cancelando só 5 e 6 (head `old`). M15 (`!=` para `=`) declarado e morto.
- `tests/pesos-d4.json`: só os pesos dos módulos que vieram da develop no merge 826dcffe, sem mudança do item.

Prova no run real, head 7bf55772: CI 45861169646 (criado 16:42:04Z) e Obsoletas 45861169690 (16:42:05Z, id maior). O log do Obsoletas não tem nenhum "Request to cancel" (0 ocorrências), e o CI foi até o fim (`completed failure`, só pelos checks que esperam parecer e rótulo).

Provas do review:
- ci: 7bf55772445e422b84ac551433ddf1f60e86a9bc verde
- `gh pr checks 913`: suíte 3.12 e 3.14 (10 partes), instalação, teto de pulados, árvore já provada, bateria (passos), bateria (python 3.14), bateria (verificações longas) e Obsoletas em `pass`; os vermelhos são só `bateria (pareceres)`, `bateria` e `catraca`, que esperam este parecer e o rótulo do dono.
- Local, no clone: `python3 -m unittest tests.test_ci_nao_cancela_parecer tests.test_catraca.Workflows`: 13 testes OK.
- `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json` (rev 7bf55772): M1 a M15 morreram.
