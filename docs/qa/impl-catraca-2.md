---
tipo: qa
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c1
commit: 03b8633721eadc9abd20e10f29cbcaddab0e4800
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-catraca-2 (branch c1)

## Achados

## Critério → teste → resultado
Item entregue: E1 (FIXTURE-DATA-GIT). Diff lido: `234dbe0..03b8633`; só `tests/test_catraca.py` (55 linhas contadas, mais fragmento e pareceres). M14 (`agents/tech-lead.md:19`): abaixo de 150, um comportamento, sem `hooks/` nem `PROTEGIDOS`. Cumpre.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: datas fixas, iguais e crescentes | `AmbienteDeGitDasFixtures.test_traz_as_duas_datas_iguais_e_crescentes` | ordem entre duas chamadas | passou |
| E1: `GIT_*` herdado filtrado antes das datas, manutenção desligada | `test_nao_devolve_o_git_herdado_do_processo` | `GIT_DIR` e afins no ambiente | passou |
| E1: commit da fixture sem relógio | `test_commit_da_fixture_nao_depende_do_relogio` | data de 2025 no `git log` | passou |
| E1: sem a espera de 1,2 s, SHAs distintos | `RotuloDePrSquash.test_dois_squash_do_mesmo_conteudo_sem_espera_dao_shas_diferentes` e b8 | mesmo conteúdo no mesmo segundo | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_catraca tests.test_ambiente_git` no head: OK. A suíte completa fica com o pre-push e o CI.
- Vermelho: `forge-testes --vermelho 234dbe0…` saiu rc=1 ("nenhum teste prova a mudança"), esperado: a implementação (`ambiente_de_git`) mora no próprio arquivo de teste, que o ferramental mantém no HEAD; os testes novos passam na base. Prova manual, em cópia em `$TMPDIR`: sem a linha que fixa as datas, 5 falhas e 2 erros em `AmbienteDeGitDasFixtures` e `RotuloDePrSquash` (SHA repetido no b8); sem o filtro de `GIT_*`, `test_nao_devolve_o_git_herdado_do_processo` cai (`GIT_DIR` presente).
- Mutação com `forge-mutante`: não se aplica, o diff não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`.
- Bugs: nenhum.
