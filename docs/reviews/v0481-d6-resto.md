---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 200d8b378582bfee881c55ef6e2574bd7f9e9ce3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Code review: hook salvar só grava na cópia local, volta E11.22 (D6 parte a; v0481 E11.23, PR #877)

Revisado por delta: `50a40e28..200d8b37`, lido pelo `forge-check parecer delta` (escopo: sem o que veio da develop). No domínio do review, só `tests/mutantes/v0481-d6-resto-7.json` (commit `200d8b378`). O merge `a50975e89` traz a develop (#898 e afins), já revisada no PR de origem. Parecer anterior: aprovado no `50a40e28`.

- ci: 200d8b378582bfee881c55ef6e2574bd7f9e9ce3 verde

## Parecer
**Aprovado.** A volta fecha a falha da catraca que o parecer anterior registrou: as guardas de `hooks/salvar.py` sem mutante que as provasse.

**M40 (`hooks/salvar.py:127`, `if e` para `if not e`).** O trecho `de` existe uma vez, na linha 127. Com o filtro invertido, a lista a salvar só tem a entrada vazia do fim da saída `-z`, e o arquivo do escopo não vai para o commit. `test_salva_so_o_escopo_na_copia` exige esse commit, então o mutante morre. Não é equivalente, ao contrário do M29, que ficou como estava.

**M41 (`hooks/salvar.py:156`, `__main__` para `if False:`).** Sem o bloco principal, o hook chamado como script não faz nada, e o mesmo teste, que roda o hook por subprocesso, não acha o commit. O mutante morre.

**CI e catraca.** No head `200d8b37` (runs 45708486380 e 45708592802, `headSha` conferido), estão verdes as 10 partes da suíte, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, `teto de pulados`, `árvore já provada` e agora também a `catraca`. Vermelhos só `bateria (pareceres)`, que espera este parecer, e `bateria`, que a agrega.

**Verificadores.** Rodei `bin/forge-mutante --processos 1 tests/mutantes/v0481-d6-resto-7.json` no `200d8b37` com ambiente limpo: `M40 · morreu · hooks/salvar.py:127` e `M41 · morreu · hooks/salvar.py:156`. A suíte inteira é a do CI citado, e não rerrodei o SHA. **Teto:** o delta não muda código de produção, então o excedido já aceito não cresce.
