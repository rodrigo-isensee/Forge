---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae7-2-familias
commit: 22ca54c6464d3f29361f246623a97620e564a622
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E107.12, revalidação da volta de CI do AE7.2, head 22ca54c6)

Revalidação (H3, R-REVIEW) pelo delta: `forge-check parecer delta docs/reviews/v0480-ae7-2-familias.md`, intervalo
`62d27eb6..22ca54c6` sem o que veio da develop. No domínio: `tests/mutantes/v0478-ae7-comparar{,-3,-4,-6}.json` e
`tests/pesos-d4.json` (a linha `test_ambiente_recriacao` veio da develop, 7c4ee3c1; nada da branch). O parecer anterior
(62d27eb6, aprovado) vale para o resto.

## Conferido no delta
- O commit 22ca54c6 muda só `de` e `para` de nove mutantes do AE7.1 (CMP7, CMP8, CMP22, CMP26, CMP31, CMP42 a CMP45);
  nenhum mutante sai, nenhum teste declarado muda. Cada `de` ocorre uma vez na fonte (`bin/forge_comparar.py`), e a troca
  segue a guarda que o `guarda` descreve (CMP7 e CMP8 acompanham a condição reescrita, `== 0` e `cod != 0 or ...`).
- `forge-mutante --conferir --base 62d27eb6`: o trecho de cada spec do diff está no lugar.
- Mutantes: 8 de 9 `morreu` (CMP26 e CMP31 por erro do teste declarado, com o controle verde). CMP43 deu `controle
  vermelho` duas vezes na cópia do `forge-mutante`; isolado, o mesmo teste passa (ver A1): é o ambiente, não o mutante.
- Suíte inteira: CI do PR #797 (run 45033801166, pendente na leitura); nada rerrodado aqui.

## Achados
- A1 (recomendado) tests/test_comparar.py:701 · o hook envenenado varre `parents[3]`, que é o TMPDIR de quem chama; com 246 mil entradas em /tmp/claude-0 o teste falha a frio (2 de 4 cópias novas, e o controle do CMP43); com TMPDIR vazio, 2 de 2 verdes. Fixar TMPDIR próprio no teste.

## Provas
- `forge-mutante --conferir --base 62d27eb6`: `conferidas: o trecho de cada spec do diff está no lugar`
- `forge-mutante --processos 1 --ids ...` (rev 22ca54c6464d), nas 4 specs: CMP7, CMP8, CMP22, CMP26, CMP31, CMP42, CMP44,
  CMP45 `morreu`; CMP43 `controle vermelho`.
- `test_hook_do_head_nao_alcanca_a_base` em clone novo de 22ca54c6: com TMPDIR=/tmp/claude-0, `FAILED` na 1ª execução e
  `OK` nas seguintes; com TMPDIR vazio próprio, `OK` em 2 de 2 clones novos; no 62d27eb6 (mesma fonte e teste), `OK`.
