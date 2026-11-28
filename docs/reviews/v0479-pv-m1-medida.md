---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: 5221863e2d25308ec35dfae91241e01ea6790ece
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.29, PR-VERDE M1, revalidação no head 5221863e)

Revalidação (H3, `R-REVIEW`): lido só `forge-check parecer delta docs/reviews/v0479-pv-m1-medida.md`, intervalo `c5c0a232..5221863e`, domínio código e testes: `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-pv-m1-medida-3.json`, `tests/mutantes/v0479-pv-m1-medida-5.json`. Suíte inteira não rerrodada (brief: sem suíte local; fica com o CI do PR).

## Delta lido
- A1 da segurança (recomendado que voltou) resolvido: o PR do dependabot sai da medida pelo login exato (`AUTORES_DEPENDABOT`, `bin/forge-placar:792`, usado em `:864`), não mais por substring; login que só contém a palavra fica na medida. Docstring (`:75`) atualizada.
- Teste do ramo de falha: `test_dependabot_e_o_login_exato_nao_a_substring` cobre os dois logins aceitos e três que só contêm a palavra (incluindo caixa diferente), conferindo que o PR conta como vermelho.
- Mutantes: M19 (`-3.json`) acompanhou a linha nova; M33 (volta à substring) e M34 (tira `dependabot[bot]`) declarados, um por guarda mudada.
- Rodado pelo revisor: `python3 -m unittest tests.evals.test_placar.CiPrimeira` → 16 testes OK; `bin/forge-mutante --processos 1 --ids M33,M34 tests/mutantes/v0479-pv-m1-medida-5.json` → M33 morreu (`:864`), M34 morreu (`:792`); `--ids M19 tests/mutantes/v0479-pv-m1-medida-3.json` → M19 morreu (`:864`).
- A2 não mexido; segue recomendado (cartão depois do merge).

## Achados
- A2 (recomendado) bin/forge-placar:75 · R1 do desenho pede o vermelho por job, mas `gh run list --json` não traz `jobs`: com a fonte documentada a quebra por job nunca aparece. Documentar a fonte dos jobs (`gh run view --json jobs`) ou registrar a lacuna na saída.

## Parecer
Aprovado. O recomendado da segurança voltou corrigido com teste de comportamento do ramo de falha e um mutante por guarda; os três mutantes morreram. O A2 vira cartão depois do merge.
