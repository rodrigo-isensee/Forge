---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae7-2-familias
commit: 62d27eb6ca7c576d9040e5ee7f230ba192798a58
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E107.8, revalidação do AE7.2 na volta única, head 62d27eb6)

Revalidação (H3, R-REVIEW) pelo delta: `forge-check parecer delta docs/reviews/v0480-ae7-2-familias.md`, intervalo
`cb2043bc..62d27eb6` sem o que veio da develop. No domínio: `bin/forge_comparar.py`, `tests/test_comparar.py`,
`tests/mutantes/v0478-ae7-2-familias{,-3,-4}.json`, `tests/pesos-d4.json`, `changelog.d/v0480-ae7-2-familias.md`.
O parecer anterior (cb2043bc, aprovado) vale para o resto; os recomendados A2 a A4 dele viraram cartão.

## Conferido no delta
- A1 da segurança (E107.3, sonda S1): a linha `familias:` passa pelo `ctx["seguro"]`; o id gerado com quebra de linha
  vira espaço e não forja outra linha `so-aperta:` (`test_id_gerado_com_quebra_de_linha_nao_forja_linha_da_saida`).
- A2: a saída do gerador vai a um arquivo anônimo com `RLIMIT_FSIZE` de `TETO_GERADOS + 1` no filho; o `fstat` acusa o
  excesso mesmo quando o gerador engole o `EFBIG` (o CPython ignora `SIGXFSZ`), e acima de `TETO_CASOS` linhas é `None`.
  O `except` passa a `SubprocessError`, que cobre a falha no `preexec_fn`. Bordas exatas de bytes e casos com teste.
- A3 (e o meu A1 anterior): HOME e TMPDIR próprios por caso no alvo `entrega`, pastas distintas
  (`test_cada_caso_tem_home_e_tmpdir_proprios`).
- Guardas: linhas 109 e 113 cobertas por AE72-25 a AE72-28 e AE72-3/4 (`forge-mutante --cobertura --base cb2043bc`);
  linha 423 por AE72-29; specs antigas ajustadas ao texto novo (AE72-2, -3, -4, -8, -18).
- Tamanho (H1): +27 linhas de código no delta, um comportamento por achado; fragmento de changelog atualizado.
- Teste afetado rodado: os 5 testes novos verdes; 10 mutantes do delta mortos (abaixo). Suíte inteira: CI do PR
  (o PR ainda não existe; nada rerrodado aqui).

## Provas
- `python3 -I -m unittest discover -s tests -p test_comparar.py -k teto -k forja -k home_e_tmpdir`: `Ran 5 tests ... OK`
- `bin/forge-mutante --processos 1 --ids AE72-2,AE72-3,AE72-4,AE72-8,AE72-18,AE72-25,AE72-26,AE72-27,AE72-28,AE72-29`
  (rev 62d27eb6ca7c): os 10 `morreu`.
