---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/v046-mapa-testes
commit: e6565be2d303c831772be74974eb84df2352fb4f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# Parecer de QA - v046 E22.4 mapa do forge-testes (head e6565be2)

Diff conferido (`origin/develop...e6565be2`): `bin/forge-testes` (2 regras de dado no MAPA), `tests/test_testes_tocados.py`, fragmento de changelog; 20 linhas a mais. Nenhuma linha de guarda mudou (o MAPA é tabela de roteamento), então não há spec de mutante (AR-1 conferido: nada a declarar). Leitura por worktree destacada minha; a branch do autor não foi tocada.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| MAPA-FORGE-DOUTOR: `bin/forge-doutor` leva os módulos que o rodam | `Mapa.test_caminhos_conhecidos_rodam_so_os_modulos_do_mapa` (linha `bin/forge-doutor`) | plano exato: 9 módulos, nenhum a mais | passou; cai na base |
| MAPA-FORGE-DOUTOR: módulo novo que roda o doutor não fica de fora | `Mapa.test_modulos_que_rodam_o_forge_doutor_estao_na_regra_dele` | varredura com mínimo (>=6 arquivos, >=5 que rodam); `rodam <= regra` | passou; cai na base |
| TESTE-RITMO-SEM-MAPA: `tests/test_ritmo.py` não cai na suíte completa | mesmo teste, linha `tests/test_ritmo.py` | plano exato de 7 módulos | passou; cai na base |

## Cenários e resultado real
- `python3 -m unittest tests.test_testes_tocados` no head (R-TETO, só este módulo): Ran 150, OK (skipped=1, o do `/proc` do sandbox, pré-existente). 75 s.
- Plano pelo `planejar` (a `--listar` com caminho de teste é "pedir o módulo": diz "sem mapa" e roda só ele, não serve de prova):
  - head: `bin/forge-doutor` -> dirigido (test_atualizar, test_doutor, test_doutor_custo, test_doutor_protecao_gh, test_doutor_relogio, test_forge, test_medidas_m14b, test_novo_projeto, test_qa_doutor_f8); `tests/test_ritmo.py` -> dirigido (test_ambiente_git, test_apoio_sandbox, test_forge, test_hooks, test_pre_push_trava, test_ritmo, test_testes_tocados). Bate com o relatório.
  - base a1318e88: `tests/test_ritmo.py` -> `('completo', ['tests/test_ritmo.py sem mapa'])`; `bin/forge-doutor` -> 5 módulos, sem os 4 novos.
- Vermelho antes do verde (a mão): `forge-testes --vermelho a1318e88` não serve aqui, porque `bin/forge-testes` no diff é `ALTERA_O_MAPA` e a ferramenta cai na suíte completa (contra R-TETO; interrompi). Então: worktree da base a1318e88 com só `tests/test_testes_tocados.py` do head, `python3 -m unittest tests.test_testes_tocados.Mapa` -> `Ran 18 tests ... FAILED (failures=3)`: as duas linhas novas do plano (`tests/test_ritmo.py`: completo != dirigido; `bin/forge-doutor`) e `test_modulos_que_rodam_o_forge_doutor_estao_na_regra_dele`: `{test_doutor, test_qa_doutor_f8, test_doutor_custo, test_doutor_protecao_gh, test_doutor_relogio} not <= {test_doutor, test_atualizar, test_forge, test_medidas_m14b, test_novo_projeto}`.
- Teste novo: lê `tests/test_*doutor*.py`: 6 arquivos; 5 chamam o doutor (`self.doutor(` ou `DOUTOR`); `test_qa_doutor_034` roda o hook, não o script (0 ocorrências), logo fora da regra de propósito. Fica de fora também `test_atualizar`, `test_novo_projeto`, `test_medidas_m14b`, que já estão na regra.
- `test_doutor_branch_atrasada` (origin/melhoria/v046-fechar-lote): 6 ocorrências de `DOUTOR`; o teste novo falha quando ele entrar sem acréscimo na regra, como o brief declara (o autor da outra branch acrescenta ao entrar).
- Suíte inteira: decide o check-run `bateria` do PR neste sha; não rerrodada aqui.

## Bug
Nenhum.
