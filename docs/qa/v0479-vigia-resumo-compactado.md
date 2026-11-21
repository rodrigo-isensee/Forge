---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 06a0220a908ce4a467361b9935e500b3c0d62af5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: FALA-DO-DONO-RESUMO-COMPACTADO (v0478 E93.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Resumo de compactação (`isCompactSummary`, `isVisibleInTranscriptOnly`) não é fala do dono | `FalaDoDono.test_resumo_de_compactacao_nao_conta`; fixture `vigia/entrada-resumo-de-compactacao-nao-conta` | marca `is*` verdadeira | passou |
| `origin` que não seja `human` (aviso de tarefa, outro agente) não conta | `test_origem_que_nao_e_humana_nao_conta` (4 formas); fixture `vigia/entrada-aviso-de-tarefa-nao-conta` | `kind` outro, sem `kind`, `None`, string | passou |
| Resultado de ferramenta não conta (inclui `sourceToolAssistantUUID`) | `test_resultado_de_ferramenta_nao_conta` | 3 campos | passou |
| Fala digitada continua avisando: origin human, sem origin (forma antiga), blocos de texto | `test_digitado_conta_com_origem_humana_sem_origem_e_em_blocos_de_texto`; fixture `vigia/entrada-digitada-com-origem-humana-avisa` (e `entrada-em-blocos-de-texto-avisa`, `entrada-sem-registro-avisa`, já existentes) | forma antiga sem `origin` | passou |
| Registro que não é `user` ou não é dict não conta | `test_outro_tipo_nao_conta` | tipo e entrada não dict | passou |

## Cenários e resultado real
- Head 06a0220a, `python3 -I -m unittest discover -s tests -p test_vigia.py`: 10 testes, OK. Fixtures de `tests/hooks/vigia` e `meta` (86), por harness que filtra `Hooks.test_fixtures`: OK. Suíte inteira não rodada (CI do PR).
- Sem `skip`, `skipIf` nem `expectedFailure` em `tests/test_vigia.py` nem nas 3 fixtures novas (grep, 0 ocorrências).
- Fluxo real: a fala digitada, com `origin: human` e sem `origin`, segue contando (testes e fixtures acima, verdes no head). Nenhum fluxo perde o aviso.

## Vermelho antes do verde
Cópia em `$TMPDIR` com `hooks/vigia.py` da base fb3b670b e os testes do head:
- `test_vigia`: 10 testes, 6 falhas em 3 testes: `test_origem_que_nao_e_humana_nao_conta` (4 subcasos), `test_resultado_de_ferramenta_nao_conta` (`sourceToolAssistantUUID`), `test_resumo_de_compactacao_nao_conta`.
- Fixtures vigia/meta: 2 falhas, `vigia/entrada-aviso-de-tarefa-nao-conta` e `vigia/entrada-resumo-de-compactacao-nao-conta`.
- Já passam na base, por serem guarda de regressão do comportamento que deve ficar: `test_digitado_conta_...`, `test_outro_tipo_nao_conta`, fixture `entrada-digitada-com-origem-humana-avisa`.
- Observação: `forge-testes --vermelho fb3b670b` completo estourou o tempo da sessão sem saída; o vermelho acima foi feito à mão, na forma da skill, só nos escopos pedidos.

## Mutantes
```
forge-mutante: pedido=v0479-vigia-resumo-compactado rev=06a0220a908c spec=3f571c4f...
M1 · morreu · hooks/vigia.py:306
M2 · morreu · hooks/vigia.py:308
M3 · morreu · hooks/vigia.py:310
M4 · morreu · hooks/vigia.py:313
M5 · morreu · hooks/vigia.py:312
M6 · morreu · hooks/vigia.py:319
```
rc 0, 6 de 6 mortos. `forge-mutante --cobertura --base fb3b670b`: nenhuma condição mudada sem mutante (as 4 linhas "declarado, não provado" têm mutante na spec e morreram na rodada acima).
