---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-placar-varredura
commit: 3907f4bb628f8a919a6b756ce8db7c321514f776
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (E20.24), varredura linear em `fundo_demais` do `forge-placar`

Escopo: `bin/forge-placar` (`fundo_demais`, regex `STRING_JSON` e `ABRE_FECHA` removidos), `tests/evals/test_placar.py`, mutantes M42 a M49 em `tests/mutantes/v0479-placar-fases-7.json`, fragmento de changelog. Sem suíte local (a suíte inteira é do CI do PR, `R-QA`).

## Critério → teste → resultado
Obrigação lida do diff e da docstring: mesmo resultado do regex (strings com escape, sem fecho, teto), com custo linear.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cada caractere lido uma vez (custo linear), inclusive string sem fecho de 80 mil caracteres | `SemTeste.test_varredura_de_aninhamento_e_de_um_passe_e_trata_escape` (iterável `Contado`) | string sem fecho; entrada balanceada | passou |
| Barra escapada deixa a aspa fechar; aspa escapada não fecha | mesmo teste, casos `["a\\"]`, `"\"[...` e `"\\"[`x65` | escape | passou |
| Teto: 64 aceita, 65 recusa, `[` e `{`, `[]`/`{}` repetidos não acumulam, colchete em string não conta | mesmo teste e `test_aninhamento_no_teto_e_colchete_em_string_passam` | 64 / 65 | passou |

## Cenários e resultado real
`python3 -m unittest tests.evals.test_placar` (TMPDIR, sem suíte): `Ran 40 tests ... OK`.

## Vermelho antes do verde
`forge-testes --vermelho` não aceita módulo em `tests/evals/`; prova manual, cópia em `$TMPDIR` com o HEAD e só `bin/forge-placar` da base `29e8c6fd`:
```
vermelho: base=29e8c6fd head=3907f4bb (à mão)
python3 -m unittest tests.evals.test_placar.SemTeste.test_varredura_de_aninhamento_e_de_um_passe_e_trata_escape
ERROR ... (texto='[[[[[[[[[[]]')   TypeError: expected string or bytes-like object, got 'Contado'
Ran 1 test in 0.071s  FAILED (errors=3)
```
O teste cai na base (3 subtestes) e passa no HEAD. Observação, não é defeito: na base ele cai pela interface (o regex exige `str`), não por comportamento; os casos de escape/teto são regressão e passam nas duas versões, o que é o esperado de uma troca de implementação equivalente.

## Mutação
`bin/forge-mutante tests/mutantes/v0479-placar-fases-7.json` (rev 3907f4bb628f), rc 0:
```
M42 · morreu · bin/forge-placar:212
M43 · morreu · bin/forge-placar:208
M44 · morreu · bin/forge-placar:214
M47 · morreu · bin/forge-placar:201
M45 · morreu · bin/forge-placar:204
M46 · morreu · bin/forge-placar:202
M48 · morreu · bin/forge-placar:206
M49 · morreu · bin/forge-placar:210
```
`--cobertura --base 29e8c6fd...` (rc 0): linhas 201, 202, 204, 206, 208, 214 `coberta` por M47, M46, M45, M48, M43, M44; nenhuma `sem mutante`; M42 e M49 cobrem as linhas 212 e 210. Oito mutantes, nenhum sobrevivente, nenhum equivalente.
