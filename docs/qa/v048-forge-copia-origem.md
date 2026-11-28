---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 997eb63ab95b171b5829ac901939a138d095df77
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 forge-copia origem local (#956, classe C)

Escopo: `bin/forge-copia` (FORGE-COPIA-ORIGEM-LOCAL, falha da worktree sem desfazer, clone D2), `tests/test_forge_copia.py` (+13 testes), specs `v048-forge-copia-origem{,-2,-3}.json` (M1-M20) e os 7 mutantes antigos realinhados. Diff lido contra a Base a90a7a93 no head 6c8fd19c; o commit seguinte da branch (9fd34b12) é só o parecer de segurança, sem código.

- ci: 997eb63ab95b171b5829ac901939a138d095df77 verde

Volta 1 (delta, 6c8fd19c..997eb63a): `bin/forge-copia` (`worktree()` com `update-ref` atômico e valor antigo vazio antes do `worktree add` sem `-b`; `update-ref -d` só da própria branch na falha), M6 de `v0475-copia-pasta` com `test_origem_com_cara_de_opcao`, as 3 specs com o mesmo `pedido`, corpo do PR com 12 vermelhos. Os achados da volta 0 (A1 bloqueante, A2 e A3 recomendados) foram resolvidos; sem achado novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Origem pasta local clona da URL do origin | `OrigemLocal.test_pasta_local_clona_da_url_do_remoto_e_parte_da_develop_dele` | origem velha, remoto à frente | passou (vermelho na base) |
| Branch só no remoto parte do head remoto | `OrigemLocal.test_branch_so_no_remoto_parte_do_head_remoto`, `Worktree.test_branch_que_ja_existe_no_remoto_parte_do_head_dela` | branch ausente no principal | passou (vermelho na base) |
| URL relativa vale a partir da origem | `OrigemLocal.test_url_relativa_vale_a_partir_da_origem` | caminho relativo, cwd diferente | passou (vermelho na base) |
| Pasta sem origin recusada, rc 2, destino não criado | `OrigemLocal.test_pasta_local_sem_remoto_origin_e_recusada` | sem remoto | passou (vermelho na base) |
| Worktree que falha apaga a branch que criou | `Worktree.test_worktree_que_falha_apaga_a_branch_que_criou` | destino inválido | passou (vermelho na base) |
| Branch que já existia fica | `Worktree.test_branch_que_ja_existia_fica_quando_a_worktree_falha` | só a nova sai | passou (guarda de regressão; não prova na base, e o corpo do PR já diz) |
| Base inexistente: rc 1 com as refs tentadas | `Worktree.test_base_que_nao_existe_sai_1_com_as_refs_tentadas` | base ausente | passou (vermelho na base) |
| D2 destacado na develop, sem branch | `D2.test_clone_d2_nasce_destacado_na_develop_sem_branch` | clone nasce na main | passou (vermelho na base) |
| Branch remota "None" não desvia o D2 | `D2.test_branch_remota_chamada_none_nao_desvia_o_d2` | branch vazia | passou (vermelho na base) |
| D2 sem a base apaga o clone, rc 1 | `D2.test_d2_sem_a_base_apaga_o_clone` | base ausente | passou (vermelho na base) |
| D2 com --branch, --revisao ou worktree recusado | `D2.test_d2_com_branch_revisao_ou_worktree_e_recusado` | 3 combinações | passou (vermelho na base) |
| D2 em destino ocupado sugere nome único | `D2.test_d2_em_destino_ocupado_sugere_nome_unico` | destino ocupado | passou (vermelho na base) |
| Branch criada por outro no meio fica e a worktree sai 1 (S8) | `Worktree.test_branch_criada_por_outro_no_meio_fica_e_a_worktree_sai_1` | corrida entre checagem e add | passou (morre o M9 da spec -2; não existia na base) |

Acessibilidade e E2E: não se aplicam (CLI).

## Provas
- Mutação refeita por mim no head 997eb63a (`--processos 4`), as 3 specs numa só rodada (mesmo `pedido`, A2 resolvido): `forge-mutante: pedido=v048-forge-copia-origem rev=997eb63ab95b`; M1-M21 todos `morreu`, rc 0 (M9 de -2 e M21 de -3 cobrem o update-ref atômico e o apagar só da própria branch).
- `v0475-copia-pasta` inteira: `pedido=v0475-copia-pasta rev=997eb63ab95b`; M1-M14 `morreu`, rc 0; o M6 (`if False:` na guarda de opção, bin/forge-copia:345) morre agora (A1 resolvido).
- Cobertura (`--cobertura --base 21aada57`, rc 0): toda condição mudada tem mutante; só a isenta `bin/forge-copia:330(base)` (M16 da spec -2).
- Suíte do módulo no head: 104 testes de tests.test_forge_copia, OK. Corpo do PR: "14 testes; 12 vermelhos ... guarda de regressão" confere (A3 resolvido).
- Catraca e custo (ordem do dono 28/11): os checks catraca e catraca (conferência) estão verdes no head; o diff só toca bin/forge-copia, testes, specs e changelog, sem serviço pago nem passo de CI novo (R-CUSTO).
