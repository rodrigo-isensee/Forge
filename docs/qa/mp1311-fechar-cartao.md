---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: 497d35697715ff0672f69b05ddf3c9d763c61332
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: melhorias-de-projeto-1311 (item 11, fechamento confere o PR pelo nome da branch)

Head testado: `0884fae2` (único commit de código sobre a base `efe7c9e8`; os commits seguintes da branch só somam pareceres). Sem PR aberto, sem check-run `bateria`: rodei só os módulos afetados, por prazo de máquina (carga 13 a 22 em 12 CPUs).

## Achados
- A1 (recomendado) bin/forge-fechar:827 · resolvido em a47ef67b: ref_check usa refs/heads/<branch>, com teste de tag homônima e mutante M4
- A2 (recomendado) tests/mutantes/mp1311-fechar-cartao.json:1 · resolvido em a47ef67b: mutante M5 cobre a linha ref_dry

## Critério → teste → resultado
O pedido não traz `CA-n`; a obrigação é `FECHAR-REF-POR-NOME` (item 11: o `forge-check pr` recebe o nome da branch local; o sha segue preso na cadeia).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| FECHAR-REF-POR-NOME: com branch local, `forge-check pr` recebe o nome | `test_fechar_ref_por_nome.test_com_branch_local_o_forge_check_recebe_o_nome`, `test_fechar.test_para_no_primeiro_erro_forge_check` | nome, não sha | passou; vermelho na base |
| Mesmo, no dry-run | `test_fechar_ref_por_nome.test_dry_run_descreve_o_nome` | texto do passo 1 | passou; vermelho na base |
| Sem branch local, segue pelo sha do servidor | `test_fechar_ref_por_nome.test_sem_branch_local_segue_pelo_sha_do_servidor` | branch só no origin | passou (regressão: passa na base) |
| Sha conferido continua preso (head que anda para; `--match-head-commit`) | `test_fechar_ref_por_nome.test_head_que_anda_durante_a_conferencia_ainda_para`, `test_com_branch_local_o_forge_check_recebe_o_nome` (merge com sha) | head mudou durante o passo 1 | passou (regressão: passa na base) |
| Dry-run sem branch local marca o sha como não lido | `test_fechar.test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido` | branch ausente | passou |
| Caso real (PR 525): worktree de portão no mesmo head | reprodução abaixo | duas branches no mesmo sha | passou |

## Revalidação por delta até `497d3569`
Delta (`forge-check parecer delta`, intervalo `a47ef67b..497d3569`): `bin/forge-testes`, `tests/mutantes/mp1311-fechar-cartao-2.json`, `tests/test_fechar_base_andou.py`, `tests/test_qa_lote_l08.py`. Mudança: o mapa do `forge-testes` ganha a linha `bin/forge-fechar` (todos os `test_fechar_*` e módulos que rodam o script) e `templates/projeto/.forge/config.json`; testes passam a esperar `refs/heads/<branch>` na conferência; novo `test_com_a_branch_local_a_gemea_no_mesmo_sha_nao_confunde_a_conferencia` e o teste das gêmeas passa a valer sem a branch local; spec `-2` com M6 e M8 (M7 retirado pelo autor por ficar vivo na cadeia do origin, sem equivalente aceito necessário: a guarda é a mesma linha 826, coberta por M4, M6 e M8).
- `python3 -m unittest tests.test_qa_lote_l08 tests.test_fechar_base_andou tests.test_fechar_ref_por_nome tests.test_testes_tocados`: 217 testes, OK (1 pulado pelo sandbox, `/proc` de outro namespace; teste do `forge-testes`, fora do delta de regra).
- `bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json tests/mutantes/mp1311-fechar-cartao-2.json` (`rev=497d35697715`): M1 a M6 e M8 morreram, sem sobrevivente (`M6 · morreu · bin/forge-fechar:826`, `M8 · morreu · bin/forge-fechar:826`).
- Vermelho: `forge-testes --vermelho a47ef67b` estourou o prazo (580 s, carga alta; rc 143, sem veredito, não vale como vermelho). Feito à mão: cópia em `$TMPDIR` do head com o `bin/forge-fechar` de `afba389e` (base); `test_com_a_branch_local_a_gemea_no_mesmo_sha_nao_confunde_a_conferencia` e `test_e8_base_que_mudou_codigo_segue_sem_trazer_a_base` falham (`FAILED (failures=2)`: `conferência:` aparece com `--ref <sha>`; `['4af42e83...'] != ['refs/heads/melhoria/x']`). Verdes no head.
- Suíte completa: do check-run `bateria` do CI do PR 539 neste sha (a vermelha era a de pareceres, por este parecer defasado do head).

## Revalidação por delta até `a47ef67b`
Delta (`forge-check parecer delta`): `bin/forge-fechar`, spec de mutantes, `test_fechar`, `test_fechar_ref_por_nome`, `test_fechar_sha_conferido`. Mudança: `ref_check` e `ref_dry` passam a `refs/heads/<branch>`; asserções atualizadas; novo `test_tag_de_mesmo_nome_nao_desvia_a_conferencia` (tag aponta outro commit; confere `forge-check` com `refs/heads/` e `--match-head-commit` do sha da branch).
- `python3 -m unittest tests.test_fechar_ref_por_nome tests.test_fechar`: 104 testes, OK.
- `bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json` (`rev=a47ef67b7080`): M1 a M5 morreram (M4 em :826, M5 em :768), rc=0. M4 prova o teste da tag; M5 prova o dry-run.
- Suíte completa: do CI do PR (sem PR ainda).

## Cenários e resultado real (head anterior `0884fae2`)
- Módulos afetados no head: `test_fechar_ref_por_nome`, `test_fechar_sha_conferido`, `test_fechar_base_andou`: 43 testes, OK; `test_fechar`: 99 testes, OK.
- Vermelho na base (`forge-testes --vermelho efe7c9e8`, em duas levas por prazo; cabeçalho `vermelho: base=efe7c9e83ec2 head=0884fae230d7`): `test_fechar_ref_por_nome` prova 2 (asserção: `test_com_branch_local_o_forge_check_recebe_o_nome`, `test_dry_run_descreve_o_nome`), 2 passam na base por serem regressão; `test_fechar_sha_conferido`, `test_fechar_base_andou` e `test_fechar`: 7 provam (asserção), 131 não provam (já existiam e passam na base); rc=0 nas duas levas, nenhum teste cai no HEAD.
- Mutantes: `bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json` (`rev=0884fae230d7`): `M1 · morreu · bin/forge-fechar:826`, `M2 · morreu · bin/forge-fechar:832`, `M3 · morreu · bin/forge-fechar:769`, rc=0. Mutante manual extra (dry-run local com sha) morreu.
- Caso real do PR 525: clone no head `0884fae2` com mais duas branches locais no mesmo sha (`portao-qa`, `aaa-outro`). `forge-check pr mp1311-fechar-cartao --ref <sha>` acusa `pr: conferência: sem o pedido ... branch da ref, que não foi achada` (o defeito de antes: `branch_do_sha` devolve None com mais de um nome); com `--ref melhoria/mp1311-fechar-cartao` essa violação some (restam só os pareceres ainda por gravar). O `forge-fechar` agora passa o nome, que é o segundo comando.
- Não rodei a suíte completa: ela é do CI do PR (sem PR ainda). Um `forge-testes` com prazo de 450 s morreu por carga e foi refeito por módulos (diretriz 14: 2 tentativas).
