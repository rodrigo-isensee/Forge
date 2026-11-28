---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sai-quarentena-s1
commit: 0e1e73639b761a4a4400dc1fd41a9281e57e61be
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E37.54), sonda S1 sai da quarentena

Escopo: `tests/test_hooks.py` (remove o `@unittest.skip` de `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`), `tests/config.json` (`teto_pulados` 2 para 1), prova em `tests/provas/` e fragmento do changelog. Sem suíte local (a suíte inteira é do CI do PR, `R-QA`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A S1 volta a rodar e passa sob carga | 12 laços de CPU; `python3 -m unittest tests.test_hooks.Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1 tests.test_hooks.SondaS1ComRelogioFalso`, 3 rodadas | carga de CPU no limite do vigia de 8 s | passou: 3/3, `Ran 3 tests` em 10,6 a 12,0 s, `OK` (load 9 a 10 no fim) |
| Nenhum pulo incondicional restante | `grep unittest.skip(` em `tests/` fora de `test_catraca.py` (fixtures) | 0 quarentenas abertas | passou: vazio |
| `teto_pulados` volta ao original | `git diff` de `tests/config.json`: 2 para 1; `python3 -m unittest tests.test_catraca.TetoDaQuarentena` | teto = `TETO_PULADOS_ORIGINAL` (1) sem quarentena | passou: 15 testes, `OK` |
| Prova de 10 rodadas anexa | leitura de `tests/provas/v0479-sai-quarentena-s1.md` | 10/10 | conferida: 10 verdes, load 29,96; meu reteste é menor (3 rodadas, load ~10) |
| Push igual ao head | `git ls-remote` | n/a | passou |

Vermelho antes do verde e mutação: não se aplicam (nenhum teste ou regra nova; só remove o skip e baixa o teto). O vermelho da S1 sob carga foi o motivo da quarentena anterior.

Limite: as 10 rodadas de `tests/provas/` são do autor (não reproduzi as 10); o CI do PR confirma no `bateria` do mesmo sha.
