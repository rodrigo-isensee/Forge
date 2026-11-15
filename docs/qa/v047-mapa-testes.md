---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 2263bc0d9d032d4d79d42c4e57641b073108f4dc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# Parecer de QA - v047 E1.286 mapa de testes, volta (delta 477dbefe..2263bc0d)

Delta conferido (`forge-check parecer delta`, domínio código e testes): `bin/forge-testes` (`quem_importa` só para hook, com fecho por `importados`/`IMPORTA`; ramo do apoio e `fnmatch` removidos), `tests/test_testes_tocados.py`, as duas specs de mutantes e o fragmento de changelog. Escopo do plano (CA do E1.253, decisão 7 do dono sobre a opção C da M8, R-TETO) não mudou. Instância que não fez a entrega.

## Situação dos achados anteriores

Sem achado novo. Os anteriores A1 (fecho sem teste que importa teste) e A2 (apoio fora da completa, decisão 7) estão resolvidos no delta, provados abaixo.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1.253: hook leva a quem o importa, pelo fecho (hook, apoio, teste que importa teste), no plano e nos afetados | `QuemImporta.test_hook_leva_a_quem_o_importa_pelo_fecho_no_plano_e_nos_afetados` | `import agentes_x`, string `'agentes'`, `reimport`, `import a, x as b`, `import` dentro de string de subprocesso, pasta com nome de módulo | passou; cai em 477dbefe |
| E1.253: ciclo entre hooks termina | `test_hooks_que_se_importam_em_ciclo_terminam` | ciclo a<->b, prazo 30 s | passou; cai em 477dbefe |
| Decisão 7 (M8 opção C): apoio de tests/ no diff segue na completa | `test_apoio_de_tests_importado_segue_na_completa`, `Mapa.test_promover_e_apoio_seguem_na_completa` | `tests/apoio_*.py`, `scripts/promover-homolog.py` | passou; cai em 477dbefe |
| R-TETO: nenhum teste que importa hook ou módulo do plano fica fora, em todos os hooks reais | `test_no_repositorio_o_plano_do_hook_traz_todo_teste_que_importa_um_modulo_do_plano` | mínimo de 9 hooks; `--listar` abre com `dirigido (` | passou; cai em 477dbefe (10 subtestes) |
| Oráculo continua no plano do hook, sem mudar a contagem | `Oraculos.test_oraculo_entra_no_plano_sem_mudar_a_contagem` | cópia dos textos reais que o fecho lê | passou |

## Cenários e resultado real
- Vermelho antes do verde: árvore de 477dbefe com o `tests/test_testes_tocados.py` do head, `python3 -m unittest tests.test_testes_tocados.QuemImporta tests.test_testes_tocados.Mapa` -> `Ran 22 tests`, `FAILED (failures=14)`: os quatro testes novos (os de repositório em 10 subtestes) e `test_promover_e_apoio_seguem_na_completa [tests/apoio_volta_unica.py]`. (À mão: `bin/forge-testes` no diff é `ALTERA_O_MAPA`, o `--vermelho` cairia na completa.)
- Mutantes: `bin/forge-mutante tests/mutantes/v047-mapa-testes.json tests/mutantes/v047-mapa-testes-2.json` -> `rev=2263bc0d9d03`, M1 a M13 `morreu`, nenhum sobrevivente nem equivalente, 1m47s. M1 morreu por erro do teste declarado sob o mutante (passa sem ele): vale como morte, é prova fraca, sem bloqueio.
- Delta de mutantes: `--base 477dbefe...` -> `base=477dbefe80ed35a590dc2f689eea32cd39177fcd mb=477dbefe80ed... rev=2263bc0d9d03`, mesmo resultado.
- Cobertura: `forge-mutante --cobertura --base c5c3a449...` -> rc=0, `coberta` em 318, 328, 332, 335, 337, 340 e 416 ("declarado, não provado"), nenhuma `não coberta`.
- `nice python3 -m unittest tests.test_testes_tocados` no head: `Ran 155 tests in 114.494s`, `OK (skipped=1)` (o do `/proc`, pré-existente).
- Suíte inteira: decide o check-run `bateria` do PR no mesmo sha; não rerrodada aqui.
- Merge do remoto: `67d6142c` só trouxe `docs/security/v047-mapa-testes.md`, sem efeito no código.

## Bug
Nenhum aberto (crítico 0, alto 0, médio 0, baixo 0).
