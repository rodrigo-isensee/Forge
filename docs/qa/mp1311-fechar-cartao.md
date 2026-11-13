---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: 0884fae230d784f90d6cb0108dfa414ee91707e0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: melhorias-de-projeto-1311 (item 11, fechamento confere o PR pelo nome da branch)

Head testado: `0884fae2` (único commit de código sobre a base `efe7c9e8`; os commits seguintes da branch só somam pareceres). Sem PR aberto, sem check-run `bateria`: rodei só os módulos afetados, por prazo de máquina (carga 13 a 22 em 12 CPUs).

## Achados
- A1 (recomendado) bin/forge-fechar:827 · `ref_check` é o nome nu: tag de mesmo nome da branch faz o git resolver a tag primeiro (ambiguidade) no `forge-check pr`; só a leitura de branch é por `refs/heads`. Não reproduzi; vale um teste com tag homônima (a segurança já apontou).
- A2 (recomendado) tests/mutantes/mp1311-fechar-cartao.json:1 · a linha `ref_dry="$ref"` (dry-run com branch local) não tem mutante declarado; mutante manual (sha no lugar do nome) morreu em `test_dry_run_descreve_o_nome`, então só a spec fica curta.

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

## Cenários e resultado real
- Módulos afetados no head: `test_fechar_ref_por_nome`, `test_fechar_sha_conferido`, `test_fechar_base_andou`: 43 testes, OK; `test_fechar`: 99 testes, OK.
- Vermelho na base (`forge-testes --vermelho efe7c9e8`, em duas levas por prazo; cabeçalho `vermelho: base=efe7c9e83ec2 head=0884fae230d7`): `test_fechar_ref_por_nome` prova 2 (asserção: `test_com_branch_local_o_forge_check_recebe_o_nome`, `test_dry_run_descreve_o_nome`), 2 passam na base por serem regressão; `test_fechar_sha_conferido`, `test_fechar_base_andou` e `test_fechar`: 7 provam (asserção), 131 não provam (já existiam e passam na base); rc=0 nas duas levas, nenhum teste cai no HEAD.
- Mutantes: `bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json` (`rev=0884fae230d7`): `M1 · morreu · bin/forge-fechar:826`, `M2 · morreu · bin/forge-fechar:832`, `M3 · morreu · bin/forge-fechar:769`, rc=0. Mutante manual extra (dry-run local com sha) morreu.
- Caso real do PR 525: clone no head `0884fae2` com mais duas branches locais no mesmo sha (`portao-qa`, `aaa-outro`). `forge-check pr mp1311-fechar-cartao --ref <sha>` acusa `pr: conferência: sem o pedido ... branch da ref, que não foi achada` (o defeito de antes: `branch_do_sha` devolve None com mais de um nome); com `--ref melhoria/mp1311-fechar-cartao` essa violação some (restam só os pareceres ainda por gravar). O `forge-fechar` agora passa o nome, que é o segundo comando.
- Não rodei a suíte completa: ela é do CI do PR (sem PR ainda). Um `forge-testes` com prazo de 450 s morreu por carga e foi refeito por módulos (diretriz 14: 2 tentativas).
