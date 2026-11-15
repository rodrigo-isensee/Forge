---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 477dbefe80ed35a590dc2f689eea32cd39177fcd
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# Parecer de QA - v047 E1.273 mapa de testes por citação e import (head 477dbefe)

Diff conferido (`origin/develop..477dbefe`, base c5c3a449): `bin/forge-testes` (`quem_importa`, `IMPORTAVEL`, `APOIO_NA_COMPLETA`, `VARRE_TESTS`, ramo em `planejar` e `planejar_afetados`), `tests/test_testes_tocados.py` (classe `QuemImporta`), duas specs de mutantes e o fragmento de changelog. Leitura por clone meu; a branch do autor não foi tocada. Obrigação nomeada: TESTE-RITMO-SEM-MAPA e os apoios sem mapa (E1.253); sem `CA-n` de UX.

## Achados
- A1 (bloqueante) bin/forge-testes:341 · Defeito provado (R-TETO): o fecho não segue teste que importa teste. `planejar(['tests/ambiente_git.py'])` dá dirigido com 99 módulos e deixa 35 que importam um módulo do plano, 21 deles test_fechar_* (importam test_fechar); falso verde no dirigido.
- A2 (recomendado) bin/forge-testes:278 · A decisão 7 do dono sobre a opção C da M8 e o ponto do review (apoio sai da completa) seguem com o review (A1 dele); a mudança só vale com reabertura pelo dono, ou o ramo apoio sai.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1.253: apoio da raiz leva a quem o cita, também pelo apoio que o cita | `QuemImporta.test_apoio_leva_a_quem_o_cita_pela_palavra_e_pelo_apoio_que_o_cita` | `apoio_ab`, `meu_apoio_a`, `apoio_a-x` não casam; pasta `apoio_pasta.py` não é apoio | passou; cai na base |
| E1.253: ciclo entre apoios termina | `test_apoios_que_se_citam_em_ciclo_terminam` | ciclo a<->b, prazo de 30 s | passou; cai na base |
| E1.253: quem varre tests/ por glob que casa o apoio entra | `test_quem_varre_tests_com_glob_que_casa_o_apoio_entra` | `glob("test_*.py")` não casa | passou; cai na base |
| E1.253: apoio sem leitor, catraca e neutralidade seguem na completa | `test_apoio_sem_leitor_catraca_e_neutralidade_seguem_na_completa` | os três caminhos | passou; já valia na base (guarda de não regressão) |
| E1.253: hook leva a quem o importa, no plano e nos afetados | `test_hook_leva_a_quem_o_importa_no_plano_e_nos_afetados` | `import agentes_x` e a string `'agentes'` não casam | passou; cai na base |
| E1.253: apoios reais e `--listar` saem da completa | `test_no_repositorio_os_apoios_e_o_test_ritmo_saem_da_suite_completa` | mínimo por caminho; `--listar` abre com `dirigido (` | passou; cai na base |
| M8 opção C (decisão 7): módulo de teste no diff segue na completa | `Mapa.test_promover_e_portoes_de_tests_seguem_na_completa` e verificação direta abaixo | `scripts/promover-homolog.py`, catraca, neutralidade | passou |

## Ponto do review (apoios e a opção C da M8)
A opção C diz que módulo de teste (`tests/test_*.py`) no diff roda a suíte inteira. `IMPORTAVEL` exclui `test_` por lookahead, então `quem_importa` devolve vazio para ele. Provado com `planejar` no head: `['tests/test_ritmo.py']` e `['tests/test_conferida_por_branch.py']` -> `completo`; `['tests/apoio_jarvis.py','tests/test_ritmo.py']` -> `completo`; `['tests/hooks/x.py']` -> `completo`. Apoio sozinho sai dirigido: `apoio_jarvis` 10 módulos, `apoio_volta_unica` 9, `hooks/agentes.py` 29. Logo a opção C fica intacta; o que muda é só o apoio que não é módulo de teste. A troca do teste `test_promover_e_apoio_seguem_na_completa` tira `apoio_volta_unica` da lista da completa, o que é a mudança pedida; o julgamento de que isso respeita a decisão 7 é do review (A2 aqui; o review reprova por isso).

## Cenários e resultado real
- Mutantes: `bin/forge-mutante tests/mutantes/v047-mapa-testes.json tests/mutantes/v047-mapa-testes-2.json` -> `forge-mutante: pedido=v047-mapa-testes rev=477dbefe80ed ...`, M1 a M14 `morreu` (14 de 14,  nenhum sobrevivente nem equivalente), 1m42s.
- Cobertura: `forge-mutante --cobertura --base c5c3a449...` -> todas as condições mudadas `coberta · ... declarado, não provado`, nenhuma `não coberta`; as linhas de guarda mudadas (278, 280, 324 a 341, 417) têm mutante.
- Vermelho antes do verde (à mão, porque `bin/forge-testes` no diff é `ALTERA_O_MAPA` e `--vermelho` cairia na completa, contra R-TETO): árvore da base c5c3a449 com o `tests/test_testes_tocados.py` do head, `python3 -m unittest tests.test_testes_tocados.QuemImporta tests.test_testes_tocados.Mapa` -> `Ran 24 tests`, `FAILED (failures=8, errors=1)`: os 5 testes novos de comportamento e as 4 linhas reais do teste de repositório (apoio_jarvis, apoio_volta_unica, ambiente_git, hooks/agentes) caem; o hook novo erra por falta de `quem_importa`.
- `python3 -m unittest tests.test_testes_tocados` no head (só este módulo, R-TETO, nice): `Ran 157 tests in 122.668s`, `OK (skipped=1)` (o do `/proc`, pré-existente).
- Suíte inteira: decide o check-run `bateria` do PR no mesmo sha; não rerrodada aqui.

## Defeito achado depois da primeira leitura (reprova)
Sonda no head: `planejar(['tests/ambiente_git.py'])` -> `dirigido`, 99 módulos; dos `tests/test_*.py` fora do plano, 35 têm `import <módulo do plano>`, 21 deles `test_fechar_*` (`import test_fechar as base`, que herda o `setUp` com `ambiente_git`). Mudar o apoio e rodar o dirigido deixa de fora quem herda dele. Os 14 mutantes morrem porque nenhum teste cobre a cadeia teste->teste; não há equivalente. O mesmo achado vem do review (A2 dele, E1.271); confirmado de forma independente. Corrigir é do `python-developer` (ou fecho por import entre testes, ou apoio volta à completa).

## Bug
Médio ou baixo: nenhum. Alto: o A1 acima (`docs/qa/bugs/` não aberto; o achado cobre).
