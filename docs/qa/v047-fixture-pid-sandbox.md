---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-fixture-pid-sandbox
commit: b47610cc2b843b1873c09489abc80bde29cad89d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 (fixtures de pid puladas fora do CI, E1.90 / E1.110)

Head testado: b47610cc. Diff contra a base afba389e: `tests/test_hooks.py`, `tests/mutantes/v047-fixture-pid-sandbox.json` e o fragmento de changelog; o hook `hooks/agentes.py` não muda. Sem PR e sem check-run no sha no momento do parecer; a máquina estava com carga ~21 em 12 CPUs, então a execução local ficou nos testes leves e afetados.

## Achados
- A1 (recomendado) tests/mutantes/v047-fixture-pid-sandbox.json:1 · o M1 só dá veredito onde o ns de pid se lê (CI): local sai 2 (controle vermelho, o teste pula). Cite o check-run `bateria` do mesmo sha como prova da morte do M1 antes do merge.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem ns de pid do pai legível e sem CI, as 4 fixtures de pid/sessão saem puladas com motivo | test_sem_ns_de_pid_do_pai_as_fixtures_de_pid_e_sessao_saem_puladas_com_motivo | ns ilegível (PermissionError) x legível; só as 4 da lista pulam; motivo no skip | passou |
| Com ns legível (ou CI) as 4 rodam e gravam | test_com_ns_de_pid_do_pai_legivel_as_fixtures_de_pid_e_sessao_rodam_e_gravam | CI definido nunca pula | sandbox sem CI: pulou (esperado); com CI=1: passou |
| Nunca pula com CI ou GITHUB_ACTIONS | mesmo teste, ramo `sinais_de_ci()` | CI definido | passou com CI=1 |
| Hook inalterado; M1 mata a perda da gravação de pid e sessão | M1 em tests/mutantes | linha `return {"pid"...}` | sem veredito local (rc 2); só no CI |

## Cenários e resultado real
- Os dois testes novos: sem CI, 1 ok e 1 skipped com motivo; com `CI=1`, o segundo roda as 4 fixtures sob mock e passa.
- `tests.test_apoio_sandbox`: 22 testes, OK.
- `test_fixtures` completo (com e sem CI): não concluiu em 550 s por causa da carga; fica para o CI do PR.
- `forge-testes --vermelho afba389e`: estourou o prazo (rc 124), sem veredito; a base não tem os helpers nem os dois testes, então eles falham por ausência (vermelho por inspeção, não por saída da ferramenta).
- `forge-mutante`: rc 2, `M1 · controle vermelho · hooks/agentes.py` (sem veredito, nunca "morreu"). Há um mutante para a única guarda de código ligada ao diff (o hook não mudou).
