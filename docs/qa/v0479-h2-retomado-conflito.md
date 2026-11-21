---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: a98c1a537f12e4c34213c27fa18cd213c8191d05
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 · H2-RETOMADO-CONFLITO (E92.4)

Base fb3b670b, head a98c1a53. Só `test_hooks_agentes_autor` e as fixtures de `tests/hooks/agentes`, sem suíte local.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Retomado tardio cuja branch outra reserva viva escreve fica sem ela e o conflito vai ao erros.log | `autor-retomado-tardio-branch-tomada-avisa` | branch ocupada | passou |
| Branch que ninguém ocupa segue reservada; a reserva viva vale | `autor-retomado-tardio-reserva-viva-vale` | branch livre / reserva viva | passou |
| As fixtures anteriores do retomado tardio não regridem | 129 fixtures de `agentes` + `test_hooks_agentes_autor` (13 testes) | n/a | passou |

## Cenários e resultado real
- `test_hooks_agentes_autor`: 13 testes, OK.
- Vermelho antes do verde (`bin/forge-testes --vermelho fb3b670b --modulos test_hooks_agentes_autor`):
  `vermelho: base=fb3b670b784a head=a98c1a537f12`
  `revertidos à base: changelog.d/v0479-h2-retomado-conflito.md, docs/hooks-fixtures.md, docs/hooks.md, hooks/agentes.py`
  `tests.test_hooks_agentes_autor.PeloHook.test_fixtures_do_pedido · H=ok · B=falha · prova (asserção)`
  O teste agrega as 2 fixtures novas no mesmo lote; na base cai por asserção.
- Mutantes (`bin/forge-mutante tests/mutantes/v0479-h2-retomado-conflito.json`, rc 0): M1 a M5 `morreu` (agentes.py:1304, 1305, 1306, 1309, 1309). `--cobertura --base fb3b670b`: as condições mudadas (linhas 1304 a 1309) têm mutante, nenhuma sem cobertura. Sem sobrevivente.
- Skip: nenhum `skip`, `skipIf` ou `expectedFailure` nos arquivos do pedido. Na pasta `agentes`, 129 fixtures rodadas pelo executor do teste: OK, com 4 puladas pelo próprio harness (sandbox sem leitura do namespace de pid do pai, E1.90); são fixtures de pid ou sessão, não as 2 novas, que não dependem de pid.
