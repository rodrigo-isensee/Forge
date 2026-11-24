---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-desde-marca
commit: 19c1c2a6063d1600c19ef8a88aee1979cda4b15b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E139.10, placar desde a marca; PR #825, revalidação por delta)

Escopo: delta lido por `forge-check parecer delta`, intervalo `752cf974..19c1c2a6`. No domínio entram só três specs: `tests/mutantes/v046-mutacao-bench-2.json`, `tests/mutantes/v047-placar-mutacao.json` e `tests/mutantes/v0480-placar-desde-marca.json`. O código não mudou desde o parecer anterior. Os outros arquivos do intervalo são pareceres (6f2131b4 e 59582674).

Verificado nesta revisão:
- A1 resolvido: o M7 de `v047-placar-mutacao.json` usa `de` e `para` alinhados a `scripts/placar-mutacao.py:95`, e `bin/forge-mutante -- tests/mutantes/v047-placar-mutacao.json` dá rc=0, com o M7 morto na linha 95.
- A2 resolvido: o M10 de `v046-mutacao-bench-2.json` foi realinhado a `[0]) if tags or marca else` (`bin/forge-changelog:285`, ocorrência única) e aponta para o teste renomeado `test_sem_marca_pede_a_marca_anterior_a_mao`. A spec dá rc=0 com 7 mutantes mortos, entre eles o M10 em `bin/forge-changelog:285`.
- A3 resolvido: a isenção da guarda apagada `tag.returncode == 0 and tag.stdout.strip()` traz motivo, e a guarda que a substitui é coberta por PDM4 e M10. `bin/forge-mutante --cobertura --base 0e59c446` dá rc=0, com `isenta · bin/forge-changelog:282(base)` e todas as linhas tocadas cobertas. A catraca no head passou (run 45300763344, success, headSha 19c1c2a6).
- `bin/forge-mutante -- tests/mutantes/v0480-placar-desde-marca.json` dá rc=0, com os mutantes do item mortos.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 testes, OK. É o teste que falhava na suíte parte 4/5 do head anterior.
- CI do PR no head 19c1c2a6 (run 45300763304): a bateria ainda roda e o job de pareceres falta só pelos pareceres. Ela é citada aqui e não foi rerrodada, e o merge segue dependendo dela verde.

## Achados
- A4 (recomendado) scripts/placar-mutacao.py:61 · Segue do parecer anterior, sem mudança. A isenção compara com a marca do HEAD no momento da rodada; depois do commit da marca nova, a marca anterior passada em --desde volta a avisar "não é tag". Vira cartão depois do merge.

## Sondas

## Parecer
Aprovado. Os três bloqueantes da rodada anterior (A1 a A3) foram resolvidos só nas specs, como pedido: as duas specs antigas estão alinhadas à fonte nova e a guarda apagada tem isenção com motivo e substituta coberta. O A4 continua recomendado.
