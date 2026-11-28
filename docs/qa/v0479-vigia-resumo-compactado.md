---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 8b7f670d5aa188ec3be78ff7c4e5d4cb63349396
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

## Revalidação no head 9ec21d93 (v0478 E93.8)
Delta (`forge-check parecer delta`, 06a0220a..9ec21d93): `hooks/vigia.py` (marca `is[A-Z]`, docstring), `tests/test_vigia.py` (+2 testes), 2 fixtures novas, spec de mutantes (M7), índice e changelog.
- `test_vigia`: 12 testes, OK. Fixtures vigia e meta (88), harness que filtra `Hooks.test_fixtures`: OK. Sem `skip`, `skipIf` nem `expectedFailure` (grep, 0 ocorrências nos 3 arquivos).
- Vermelho (cópia em `$TMPDIR`, `hooks/vigia.py` de 6c4357b6, testes do head): `test_campo_que_comeca_com_is_sem_maiuscula_nao_e_marca` falha; fixture `vigia/entrada-campo-issue-ref-nao-e-marca-avisa` falha. `test_forma_da_ide_sem_origem_com_prompt_id_conta` e a fixture `entrada-forma-da-ide-sem-origem-avisa` passam na base: são guarda de regressão da forma da IDE (a mudança dela é só a docstring), não provam correção.
- Mutantes (rev=9ec21d93d609): M1 a M7 morreram, rc 0.

```
M1 · morreu · hooks/vigia.py:308
M2 · morreu · hooks/vigia.py:311
M7 · morreu · hooks/vigia.py:310
M3 · morreu · hooks/vigia.py:313
M4 · morreu · hooks/vigia.py:316
M5 · morreu · hooks/vigia.py:315
M6 · morreu · hooks/vigia.py:322
```
- Suíte inteira não rodada (CI do PR).

## Revalidação no head 8b7f670d
Delta (`forge-check parecer delta`): só `docs/hooks-fixtures.md` (índice regenerado) e `docs/hooks.md`, vindos do merge da develop (#775); nenhum código mudou. `scripts/indice-fixtures.py --conferir`: em dia. `tests/test_vigia.py`: 12 testes, OK. Fixtures de `vigia` e `meta`: 88 casos, OK. `bin/forge-mutante tests/mutantes/v0479-vigia-resumo-compactado.json`: M1 a M7 morreram (hooks/vigia.py:308,310,311,313,315,316,322). Parecer mantido.
