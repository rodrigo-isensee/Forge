---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 prazo-forge (#888, classe C), delta 22a57afc..07a1bf5c (E7.60)

Escopo: nova resolução do conflito com a develop (merge 39d6f4f4, entrou o #878) e o merge do parecer ec272bb6. Conflito só em `docs/hooks-fixtures.md` (índice gerado). `hooks/conformidade.py` e `tests/test_hooks.py` juntaram sozinhos; o que entrou delas é o `parecer publicar` do #878 (`ultima_raiz`, `forge_check_publica`, `test_fixtures_do_publicar`), igual ao da develop (22ceb2c8): as linhas acrescentadas de `conformidade.py` no delta e as do commit do #878 coincidem. O item (`prazo_vencido`, `_comum.py`, spec) não mudou no delta.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guarda do `prazo_vencido` | M1 a M8 de `tests/mutantes/v0481-prazo-forge.json` | PostToolUse, critico None | morreram todos, rc=0 (`rev=07a1bf5c6420`; M4 por erro do teste declarado) |
| Junção guardou o #878 | `tests.test_hooks.Hooks.test_fixtures_do_publicar` | lote com os dois lados (0 e 2), mínimo 9 | OK |
| Teste do vigia citado pela catraca | `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada` | n/a | OK |
| Índice gerado entrou igual | `python3 scripts/indice-fixtures.py --conferir` | n/a | "docs/hooks-fixtures.md: em dia" |

## O teste que a catraca aponta
`test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada` é mudança do item, não da junção: o delta 22a57afc..07a1bf5c não toca o teste. A catraca compara com a base da develop (604f3069) e vê o que o #888 fez desde a origem: o vigia de 8 s virou o do prazo longo (7,5 s, `PRAZO_DO_MERGE_S`), com a docstring e o `sleep 4` virando `sleep 3.5` nos testes de prazo. É o valor esperado trocado pela própria mudança do prazo, já aprovada nas voltas anteriores; passa no head.

## Resultado real
- CI no head exato: verdes `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `árvore já provada`, `teto de pulados` (3.12 e 3.14) e as 10 partes da suíte (3.12 e 3.14). Vermelhos `bateria`, `bateria (pareceres)` e `catraca`, os três excluídos pelo G3: `bateria` e `bateria (pareceres)` esperam os pareceres; `catraca` falha pelo rótulo `afrouxa-regra` ausente em `hooks/_comum.py` e `hooks/conformidade.py` (R-CONFORMIDADE, decisão do dono) e traz o aviso do teste acima.
- ci: 07a1bf5c6420ea060b517927cf06cb8090e7bb6f verde
