---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: 58852bf22fd6dcd4912d14b65813f701995cb38e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 forge-fechar (CI do topo, branch criada do servidor, cópia certa)

Links: pedido v0481 (E13.1, QA E13.8), `docs/fechamento-integrador.md`, `bin/forge-fechar`. Sem UX nem API. As obrigações são as do brief: nenhum caminho mescla sem os checks verdes do head, o CI do topo só vale quando contém o merge, nada que barra hoje deixa de barrar. Offline, `gh` e `git` falsos (`R-CUSTO`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Passo 8: CI do merge cancelado, topo contém o merge (ahead) e verde, sai 0 | `test_fechar_ci_topo.CiDoTopo.test_topo_verde_que_contem_o_merge_fecha_com_0` | cancelado, topo ahead | passou; M1, M3 morrem |
| Idem com `identical` | `test_topo_identico_ao_merge_tambem_decide` | identical | passou |
| Vermelho de verdade do topo segue 5 e imprime a reversão do merge | `test_topo_vermelho_continua_5_com_a_reversao_do_merge` | vermelho | passou |
| Topo que não contém o merge (diverged) segue 5 e não lê o CI dele | `test_topo_que_nao_contem_o_merge_fica_cancelado` | diverged | passou; M2 morre |
| Topo igual ao merge (develop não andou) segue 5, uma só leitura | `test_topo_que_nao_andou_fica_cancelado` | topo == merge | passou |
| Passo 1: commit falta na cópia, busca por leitura e cria a branch `--no-track` no sha do servidor | `test_fechar_sha_conferido.SoBranchRemota.test_commit_que_falta_aqui_cria_a_branch_local_no_sha_do_servidor` e `test_branch_so_no_servidor_fecha_no_sha_do_servidor` | commit ausente | passou; M6 morre |
| Busca que não traz o commit pede o fetch; branch não criada para no passo 1 | `test_commit_que_a_busca_nao_traz_pede_o_fetch`, `test_branch_local_que_nao_se_cria_para_antes_do_passo_1` | busca falha, criação falha | passou; M7, M8 morrem |
| Cópia principal na própria branch para com 1 antes do passo 1, sem chamar gh | `CopiaCerta.test_copia_principal_na_branch_para_antes_do_passo_1` | permissão da cópia | passou; M4, M5 morrem |
| Worktree ligada na branch não é a cópia principal | `CopiaCerta.test_worktree_ligada_na_branch_nao_e_a_copia_principal` | worktree | passou |
| Nenhum caminho mescla sem checks verdes do head | passo 6b (`ci_antes_do_merge`) e `--match-head-commit` não estão no diff; o diff de bin/forge-fechar só toca `ci_no_merge` (passo 8, depois do merge), o passo 1 e a guarda da cópia | n/a | conferido por leitura do diff |

## Revalidação por delta (dd2fcada..58852bf2)
`forge-check parecer delta` listou no domínio: bin/forge-fechar, specs de mutante (mp1311, v047-integracao-em-lote-3, v0481-fechar-ci-topo, novo `-2`), `test_fechar_ci_topo.py`, `test_fechar_sha_conferido.py`, doc e changelog. O A1 do parecer anterior está resolvido: o `de` do M2 do mp1311 e o IL-M21 agora existem na fonte; o teste devolveu o nome `test_commit_que_falta_aqui_pede_o_fetch`. Obrigações novas do delta, com teste e mutante:
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Branch criada no passo 1 sai se o fechamento para antes do passo 3 | `SoBranchRemota.test_branch_criada_sai_se_o_passo_1_para` | parada no passo 1 | passou; M9 morre; prova (cai na base) |
| Passou do passo 2, a branch criada fica | `test_commit_que_falta_aqui_cria_a_branch_local_no_sha_do_servidor` | passo 3 em diante | passou; M10 morre |
| Vermelho do próprio merge não fala do topo; vermelho do topo avisa | `CiDoTopo.test_vermelho_do_proprio_merge_nao_fala_do_topo` e o reforço do `test_topo_vermelho_continua_5...` | topo == merge | passou; M11 morre (o teste é negativo, passa na base) |
| `--sem-limpar` na cópia principal na branch segue (rc 3 do passo 7 pulado) | `CopiaCerta.test_copia_principal_na_branch_com_sem_limpar_segue` | flag | passou; M12 morre |

## Provas
- `bin/forge-mutante --conferir --todas` no head: rc 1 com 26 linhas, todas pendentes herdadas (nenhuma de mp1311, v047-integracao-em-lote-3 nem v0481); o teste que o CI roda, `test_forge_mutante.ConferirTodas` (4 testes), passou: OK. A causa da falha do parecer anterior sumiu.
- `bin/forge-mutante tests/mutantes/v0481-fechar-ci-topo.json tests/mutantes/v0481-fechar-ci-topo-2.json --processos 4` (rev=58852bf22fd6): M1 :1238, M2 :1239, M3 :1244, M4 :1693, M5 :1694, M6 :1660, M7 :1667, M8 :1668, M9 :444, M10 :1755, M11 :1246, M12 :1693, todos `morreu`. Cada linha de guarda nova do diff (fim, `branch_criada=""`, aviso do topo, `sem_limpar`) tem mutante.
- Pacote `test_fechar*.py` no head: 484 testes, OK (skipped=1), 566 s.
- Sondas minhas (`gh` e `git` falsos): (A) branch local movida por outro agente durante o passo 1 e parada em seguida: o `update-ref -d` com o valor antigo não apaga a branch alheia; (B) `--dry-run` com a branch só no servidor sai 0 sem criar branch; (C) parada no passo 2 (remoto difere) apaga a branch criada e imprime o registro. Sem achado.
- CI: a run 45530565296 do sha 58852bf foi cancelada pelo push seguinte (o parecer do review); `bateria (pareceres)` falhou nela por parecer ainda não regravado no head. A prova de QA é a local acima; a bateria do head final é do CI do PR.

## Vermelho antes do verde
`forge-testes --vermelho dd2fcada2719cafad4eee2d8e31f3aaec2e8d5c3 --modulos test_fechar_ci_topo,test_fechar_sha_conferido`, rc=0, `contagem: não prova (passa na base)=18; prova (asserção)=3`. Provam: `test_branch_criada_sai_se_o_passo_1_para`, `test_topo_vermelho_continua_5_com_a_reversao_do_merge` (o aviso novo do topo) e `test_copia_principal_na_branch_com_sem_limpar_segue`; `test_vermelho_do_proprio_merge_nao_fala_do_topo` passa na base (guarda negativa, provada pelo M11); os 18 restantes guardam o que a base já cumpria e as guardas deles seguem provadas pelos mutantes. Do parecer anterior segue valendo o vermelho contra d49accf8 (6 provas).

## Bugs
Nenhum.

## Veredito
Aprovado em 58852bf: o A1 foi corrigido, as quatro guardas novas têm teste e mutante, 12 mutantes mortos, pacote verde e sondas sem achado.
