---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-fechar-lote
commit: 97e0b6e7d860dde35ae33b39c0265ae3f2fdd7a8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 fechar-lote (E15.4)

Quatro cartões do `bin/forge-fechar`: FORGE-FECHAR-CLONE-LIMPAR, TESTE-FECHAR-L5-CORRIDA, FECHAR-HOMOLOG-FRESCA, FECHAR-DRY-RUN-1C. Base `82bb9e57`. Sem suíte local (a suíte inteira é do check `bateria` do CI do PR); rodei só os módulos dos arquivos tocados, com `TMPDIR`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Limpar no clone da própria branch não manda `worktree remove`/`branch -D`, sai com 3 | `test_o_clone_que_roda_o_fechamento_nao_se_apaga_e_diz_o_que_ficou`, `test_branch_na_worktree_principal_rodado_nela_fica_pendente_sem_worktree_remove` | cópia principal = própria branch | passou |
| Clone em `~/.forge-contrib/wt` (inclusive por link) manda o `--limpar` de outra cópia; fora dele, trocar de branch | `test_clone_por_caminho_com_link_ainda_e_de_wt`, `test_o_limpar_de_outra_copia_apaga_o_clone_e_depois_a_remota`, `test_copia_principal_fora_de_wt_troca_de_branch_e_repete` | caminho com link; fora de wt | passou |
| Commit sem merge: só a leitura | `test_clone_com_commit_sem_merge_so_da_a_leitura` | commit fora da base | passou |
| `--help`/`-h` imprime o uso, rc 0, sem log | `test_help_imprime_o_uso_e_sai_0_sem_log` | duas formas da opção | passou |
| L5: parada gravada antes do `fim` com registrador lento | `test_l5_registrador_de_stderr_lento_ainda_grava_a_parada_antes_do_fim` | corrida do log | passou (cartão só de teste, sem código; não há vermelho a provar) |
| 1c busca a homolog do servidor sempre; falha com local avisa o sha | `test_1c_com_origin_homolog_velha_no_clone_busca_a_do_servidor_antes_do_promover`, `test_1c_busca_que_falha_com_a_homolog_local_avisa_que_ela_pode_estar_velha` | local velha; busca falha com e sem local | passou |
| `--dry-run` roda o 1c de verdade, sem busca; recusa para com 1; sem branch local não roda | `test_1c_no_dry_run_roda_o_conferir_ref_contra_a_homolog_local_sem_busca`, `..._que_recusa_para_com_1_e_diz_a_homolog_lida`, `..._sem_a_branch_local_nao_roda`, `test_1c_fora_da_base_develop_nao_roda` | sem branch local; fora de develop | passou |

## Execução (head 97e0b6e7)
- `test_fechar.py`: Ran 111, OK (skipped=1: `skipTest` de shellcheck fora do PATH, já existente, não é do diff).
- `test_forge_fechar.py`: Ran 22, OK. `test_fechar_orfao.py`: Ran 18, OK.

## Vermelho antes do verde
`bin/forge-testes --vermelho <base>` (39 módulos) estourou o prazo local (rc 124, sem veredito; não vale como vermelho). Substituí por cópia em `$TMPDIR` com `bin/forge-fechar` da base e os testes do head, módulos tocados:
- `test_forge_fechar.py`: Ran 22, FAILED (failures=6): clone_por_caminho_com_link, copia_principal_fora_de_wt, help (`--help` e `-h`), clone_que_roda_o_fechamento, limpar_de_outra_copia.
- `test_fechar.py`: Ran 111, FAILED (failures=4, errors=1): os cinco testes de 1c (busca antes do promover, busca que falha, dry-run roda, dry-run recusa, dry-run sem branch).
Todo teste novo de comportamento cai na base e passa no head.

## Mutantes (R-QA)
`bin/forge-mutante --processos 3 tests/mutantes/v0478-fechar-lote.json tests/mutantes/v0478-fechar-lote-2.json`, rc 0:
```
forge-mutante: pedido=v0478-fechar-lote rev=97e0b6e7d860 spec=379d95e2... spec=6a09bcac...
FL-M1 a FL-M13 · morreu (bin/forge-fechar:103, 647, 703, 616, 620, 620, 747, 778, 382, 948, 1221, 1221, 964)
```
Conferi a lista contra o diff: cobre `--help`, detecção da cópia própria, `propria` em `limpar_entrega` (branch local, remota, `rem_st`), `copia_propria` (3 ramos), `fetch` do 1c, `conferir_1c` e o ramo do dry-run. `--cobertura --base` sai `não coberto: bin/forge-fechar` (shell, esperado) e lista as três specs antigas editadas (ajuste de linha/trecho, sem enfraquecer: os testes delas passam).

## Cenários e resultado real
Bordas lidas no diff e cobertas: caminho com link para `~/.forge-contrib`, `--help` sem log, busca da homolog falhando com e sem a local, dry-run sem branch local. Sem bug aberto. Sem E2E, API ou acessibilidade (ferramenta de linha de comando).
