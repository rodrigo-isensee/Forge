---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 forge-copia origem local (#956, classe C)

Escopo: `bin/forge-copia` (FORGE-COPIA-ORIGEM-LOCAL, falha da worktree sem desfazer, clone D2), `tests/test_forge_copia.py` (+13 testes), specs `v048-forge-copia-origem{,-2,-3}.json` (M1-M20) e os 7 mutantes antigos realinhados. Diff lido contra a Base a90a7a93 no head 6c8fd19c; o commit seguinte da branch (9fd34b12) é só o parecer de segurança, sem código.

- ci: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d verde

## Achados
- A1 (bloqueante) bin/forge-copia:340 · o mutante M6 de tests/mutantes/v0475-copia-pasta.json (`if valor.startswith("-")` para `if False:`) sobrevive (rc 1), também na base a90a7a93. O teste listado não o mata; `Recusa.test_origem_com_cara_de_opcao` mata (rc 1, esperado 2). Listá-lo em `testes`.
- A2 (recomendado) tests/mutantes/v048-forge-copia-origem-2.json:2 · as 3 specs têm `pedido` diferente (`...-origem`, `-2`, `-3`); o forge-mutante recusa a rodada conjunta (rc 2). O padrão pede o mesmo `pedido` e id único no conjunto. Rodei uma a uma.
- A3 (recomendado) tests/test_forge_copia.py:929 · só 12 dos 13 testes novos provam vermelho; `test_branch_que_ja_existia_fica_quando_a_worktree_falha` passa na base (guarda de regressão, coberto por mutante da spec -2). Corrigir a contagem "13 provam" do pedido.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Origem pasta local clona da URL do origin | `OrigemLocal.test_pasta_local_clona_da_url_do_remoto_e_parte_da_develop_dele` | origem velha, remoto à frente | passou (vermelho na base) |
| Branch só no remoto parte do head remoto | `OrigemLocal.test_branch_so_no_remoto_parte_do_head_remoto`, `Worktree.test_branch_que_ja_existe_no_remoto_parte_do_head_dela` | branch ausente no principal | passou (vermelho na base) |
| URL relativa vale a partir da origem | `OrigemLocal.test_url_relativa_vale_a_partir_da_origem` | caminho relativo, cwd diferente | passou (vermelho na base) |
| Pasta sem origin recusada, rc 2, destino não criado | `OrigemLocal.test_pasta_local_sem_remoto_origin_e_recusada` | sem remoto | passou (vermelho na base) |
| Worktree que falha apaga a branch que criou | `Worktree.test_worktree_que_falha_apaga_a_branch_que_criou` | destino inválido | passou (vermelho na base) |
| Branch que já existia fica | `Worktree.test_branch_que_ja_existia_fica_quando_a_worktree_falha` | só a nova sai | passou (não prova na base: A3) |
| Base inexistente: rc 1 com as refs tentadas | `Worktree.test_base_que_nao_existe_sai_1_com_as_refs_tentadas` | base ausente | passou (vermelho na base) |
| D2 destacado na develop, sem branch | `D2.test_clone_d2_nasce_destacado_na_develop_sem_branch` | clone nasce na main | passou (vermelho na base) |
| Branch remota "None" não desvia o D2 | `D2.test_branch_remota_chamada_none_nao_desvia_o_d2` | branch vazia | passou (vermelho na base) |
| D2 sem a base apaga o clone, rc 1 | `D2.test_d2_sem_a_base_apaga_o_clone` | base ausente | passou (vermelho na base) |
| D2 com --branch, --revisao ou worktree recusado | `D2.test_d2_com_branch_revisao_ou_worktree_e_recusado` | 3 combinações | passou (vermelho na base) |
| D2 em destino ocupado sugere nome único | `D2.test_d2_em_destino_ocupado_sugere_nome_unico` | destino ocupado | passou (vermelho na base) |

Acessibilidade e E2E: não se aplicam (CLI).

## Provas
- Vermelho: `bin/forge-testes --vermelho a90a7a93 --modulos tests.test_forge_copia`: `vermelho: base=a90a7a932e0e head=6c8fd19ce267`, revertidos à base `bin/forge-copia`, `changelog.d/v048-forge-copia-origem.md`; `contagem: não prova (passa na base)=91; prova (asserção)=12`, rc=0. Os 12: 4 de OrigemLocal, 3 de Worktree, 5 de D2.
- Mutantes novos (`--processos 3`, uma spec por chamada): spec 1 M1-M8 morreram, rc 0; spec 2 M9-M16 morreram, rc 0; spec 3 M17-M20 morreram, rc 0 (`rev=6c8fd19ce267`).
- Mutantes antigos realinhados: `v0481-copia-base` 7/7 mortos; `v0481-copia-mensagem` 6/6; `v0479-limpeza-fim-item-2` M9-M16 mortos; `v0475-copia-pasta` 13/14, M6 sobrevive (A1).
- Cobertura (`--cobertura --base a90a7a93`, rc 0): toda condição Python mudada tem mutante declarado; `bin/forge-copia:330(base)` isenta (M16 da spec -2). A prova é a rodada acima.
- Classe C (`forge-check classe`: sensível da catraca, `bin/forge-copia`). Catraca: checks `catraca` e `catraca (conferência)` verdes no head. Custo (R-CUSTO): o diff toca só `bin/forge-copia`, testes, specs e changelog; nenhum serviço pago nem passo de CI novo.

## Cenários e resultado real
Sonda do A1 numa cópia do head com `if False:` na linha 340: `test_branch_ou_base_com_cara_de_opcao` passa; `test_origem_com_cara_de_opcao` falha com `repository '--upload-pack=x' does not exist` (rc 1, esperado 2).
