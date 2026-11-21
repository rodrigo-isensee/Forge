---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: 83d3b07d479ddc5ade6c4fdffc331aea7602e845
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 · H2-RETOMADO-CONFLITO (E92.8, revalidação)

Base fb3b670b, head 83d3b07d (delta desde a98c1a53). Só `test_hooks_agentes_autor` e as fixtures de `tests/hooks/agentes`, sem suíte local. O contrato mudou: o retomado tardio mantém todas as branches no registro, como na base, e o conflito vai ao `erros.log`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Retomado tardio com a branch tomada por reserva viva a mantém, o conflito vai ao erros.log e o disparo seguinte é recusado | `autor-retomado-tardio-branch-tomada-avisa` (rc 2) | branch ocupada | passou |
| Reserva viva sem id na branch do retomado: as duas ficam | `autor-retomado-tardio-reserva-viva-vale` | reserva viva | passou |
| Duas branches, uma tomada e outra livre: o erros.log cita só a tomada | `autor-retomado-tardio-branch-mista` (nova) | mista | passou |
| As demais fixtures do retomado não regridem | 130 fixtures de `agentes` + `test_hooks_agentes_autor` (13 testes) | n/a | passou |

## Cenários e resultado real
- `test_hooks_agentes_autor`: 13 testes, OK. Fixtures de `agentes`: 130 verificadas, OK (4 puladas pelo próprio harness, sem leitura do namespace de pid do pai, E1.90; são de pid ou sessão, não as 3 do pedido).
- Vermelho antes do verde, `bin/forge-testes --vermelho fb3b670b --modulos test_hooks_agentes_autor`, rc 0: `vermelho: base=fb3b670b784a head=83d3b07d479d`; `tests.test_hooks_agentes_autor.PeloHook.test_fixtures_do_pedido · H=ok · B=falha · prova (asserção)`. Idem contra a98c1a53 (`base=a98c1a537f12`), rc 0, mesma linha.
- Por fixture (hooks/agentes.py de cada base sobre o head, em cópia): contra fb3b670b e contra a98c1a53 caem as três, `branch-mista`, `branch-tomada-avisa` e `reserva-viva-vale`; no head, todas passam.
- Mutantes (`bin/forge-mutante tests/mutantes/v0479-h2-retomado-conflito.json`, rc 0): M1 morreu (agentes.py:1304), M2 morreu (1305), M3 morreu (1306), M4 refeito morreu (1309), M5 trocado morreu (1305). Sem sobrevivente. `--cobertura --base fb3b670b`, rc 0: linhas 1305 e 1306 cobertas (M2, M3).
- Skip: nenhum `skip`, `skipIf` ou `expectedFailure` no teste, nas fixtures nem na spec do pedido.
