---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: baf1bee6aa7f6a7efad97b44cc409a576f8a7762
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.106, por delta)

Head baf1bee6, base afba389e, delta desde 93deca84. Sem PR aberto: rodei só os testes afetados, em série (máquina com carga).

## Achados
- A3 (recomendado) skills/trabalho-em-paralelo/SKILL.md:10 · fechado: `git diff afba389e HEAD` e `git diff origin/develop HEAD` do arquivo saem vazios; texto da base restaurado.
- A4 (recomendado) README.md:1 · o README manda ver a skill `trabalho-em-paralelo` para a retomada dos agentes, mas a skill já não traz esse passo (cortado na E1.103); ajustar a frase ou voltar a retomada à skill.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orientação ao dono no README e no modelo | `AmbienteSemAutoUpdate.test_orientacao_ao_dono_no_readme_e_no_modelo` | frase exata nos 2 arquivos | passou |
| Texto existente preservado (ordem 17:40) | diff da skill contra a base e a develop | n/a | passou (0 linhas) |
| Nenhuma regra perdida | `tests.test_forge.TetoPorPr` | frase do teto | passou |
| Teste novo lido pelo filtro do pre-push | `LEITORES_DE_TEXTO` + `MapaCobreOQueOsTestesLeem` | módulo na lista | passou (6 testes) |

## Cenários e resultado real
- Delta em `bin/forge-testes`: só quebra de linha da tupla; mesmos itens. Mutação não se aplica.
- Vermelho antes do verde: o teste de retomada saiu com a skill; o que resta é só presença de frase nos 2 arquivos, sem lógica nova; não rodei `forge-testes --vermelho` (carga alta).

## Provas
- `python3 -m unittest tests.test_ambiente_sem_auto_update tests.test_forge.TetoPorPr tests.test_jarvis_nucleo tests.test_clareza tests.test_modelos_projeto` -> Ran 47 tests, OK
- `python3 -m unittest tests.test_testes_tocados.MapaCobreOQueOsTestesLeem` -> Ran 6 tests, OK
- `git diff afba389e HEAD -- skills/trabalho-em-paralelo/SKILL.md | wc -l` -> 0
