---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: 6c709157b28682ed39bab0663bdd8989753e9790
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E14.89), #902 por delta `e871982c..6c709157` (R-QA)

Classe C, sem UX. Domínio conferido (`forge-check parecer delta`): a correção de uma linha em `bin/forge-check` e a spec `tests/mutantes/v0480-g1-1-uma-volta-3.json`. O merge da develop (98c9dfde) só se conferiu por entrar igual: o diff `98c9dfde..6c709157` toca só esses dois arquivos (+1 -21), sem mexer no que veio da base.

- ci: 6c709157b28682ed39bab0663bdd8989753e9790 verde

## Achados da rodada anterior
- A1 (spec -3 fora da fonte): resolvido. M21 e M23 saíram de `v0480-g1-1-uma-volta-3.json`; o código que eles guardavam (`voltas_autorizadas`) já tinha saído na volta anterior. `test_forge_mutante` confere a spec com a fonte e passa.
- A2 (f-string crua em `bin/forge-check:4751`): resolvido. `real` e `texto_da_volta` passam por `sem_controle`; `test_forge.SaidaSanitizada` passa (8 testes).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Specs de mutante conferem com a fonte | `test_forge_mutante.ConferirTodas...` | `de` de toda spec presente na fonte | passou (local e CI) |
| Valor de caminho em f-string passa pelo sanitizador | `test_forge.SaidaSanitizada...` | caractere de controle na mensagem da volta | passou (local e CI) |
| Comportamento da volta intacto | `test_volta_por_delta`, `test_volta_alinhada` | volta 3 e volta 4 | passou |

## Cenários e resultado real
- Local no head `6c709157`: `bin/forge-testes tests/test_volta_por_delta.py tests/test_volta_alinhada.py` -> `Ran 120 tests ... OK`; `python3 -m unittest tests.test_forge.SaidaSanitizada` -> `Ran 8 tests ... OK`; `tests.test_forge_mutante` mais `SaidaSanitizada` -> `Ran 164 tests ... OK`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-g1-1-uma-volta-3.json` -> `forge-mutante: pedido=v0478 rev=6c709157b286 ...`; M16, M18, M19, M20 e M22 `morreu`, nenhum sobrevivente.
- Vermelho antes do verde: não se aplica ao delta; a correção de A2 é coberta por teste estrutural que já existia e falhava no head anterior (e871982c), como registrado na rodada anterior.
- CI (`gh pr checks 902`, head `6c709157`, confirmado por `gh pr view`): verdes as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, instalação, teto de pulados e árvore já provada. Vermelhos, fora do que conta (G3): `bateria`, `bateria (pareceres)` e `catraca`, que esperam os pareceres.

## Parecer
Aprovado. Os dois bloqueantes da rodada anterior estão corrigidos, o mutante da spec corrigida morre e o CI está verde no head nas partes que contam.
