---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-h4-atualiza-branch
commit: ecc079920274ff207f217372c8708bef6e990899
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-h4-atualiza-branch (H4, E2.722; código ea5c12c8, head c0126861)

## Achados
- A1 (recomendado) bin/forge-fechar:798 · o recomeço sem `--trazida` sobrevive ao mutante (nenhum teste cai): se a base andasse de novo entre o envio e o recomeço, a cadeia traria a base outra vez. Um teste que faça a base andar no envio e exija um só merge prova a guarda (R-QA).

## Critério → teste → resultado
O pedido não tem especificação de UX; as obrigações vêm do item H4: em `melhoria/*`, base andou sem conflito, o `forge-fechar` traz a base por merge e recomeça a cadeia uma vez (CA-1 a CA-8); fora de `melhoria/*` e com conflito segue o comportamento E8 (CA-9, CA-10).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 base andou sem conflito (arquivo em comum ou código mudado): traz a base e recomeça | `test_h4_arquivo_em_comum_sem_conflito_traz_a_base_e_recomeca`, `test_h4_base_que_mudou_codigo_traz_a_base` | arquivo em comum sem conflito | passou; base falha (asserção) |
| CA-2 a worktree da branch anda junto (ff, só limpa) | `test_h4_worktree_da_branch_anda_junto` | worktree presente | passou; base falha (asserção) |
| CA-3 sem branch local, envia o merge e recomeça | `test_h4_sem_a_branch_local_envia_o_merge_e_recomeca` | `so_remota` | passou; base falha (asserção) |
| CA-4 falha de cada passo do merge para sem PR | `test_h4_falha_de_cada_passo_do_merge_para_sem_pr` | falha de árvore, commit-tree, update-ref | passou; base falha (asserção) |
| CA-5 worktree suja ou ff que falha para sem enviar | `test_h4_worktree_suja_ou_ff_que_falha_para_sem_enviar` | mudança não commitada | passou; base falha (asserção) |
| CA-6 envio recusado para sem PR | `test_h4_envio_recusado_para_sem_pr` | push recusado | passou; base falha (asserção) |
| CA-7 cadeia recomeçada que para sai com o código dela | `test_h4_cadeia_recomecada_que_para_sai_com_o_codigo_dela` | rc propagado | passou; base falha (asserção) |
| CA-8 com `--trazida` não traz de novo | `test_h4_com_trazida_nao_traz_a_base_de_novo` | uma vez por cadeia | passou; base falha (asserção) |
| CA-9 fora de `melhoria/*` segue sem trazer (E8) | `test_e8_fora_de_melhoria_e_o_mesmo_nenhuma_branch_recebe_o_merge` | ref não `melhoria/*` | passou; passa também na base (guarda, morta pelo M1) |
| CA-10 conflito para sem merge, sem envio e sem PR; falha de leitura do merge-tree para | `test_e8_com_conflito_para_sem_merge_sem_envio_e_sem_pr`, `test_e8_conflito_de_pasta_e_arquivo_sem_arquivo_em_comum_para`, `test_e8_git_sem_merge_tree_ou_com_falha_para_no_2b` | conflito real; falha fechada | passou; passa também na base (comportamento mantido) |
| CA-11 `--dry-run` descreve o 2b novo | `test_c5_dry_run_imprime_o_2b_e_nao_le_o_servidor` | só leitura | passou; base falha (asserção) |

## Cenários e resultado real
- Testes do arquivo no head c0126861: `python3 -m unittest tests.test_fechar_base_andou`: 37 testes OK (instância anterior, E2.691, mesmo código; o forge-testes abaixo os roda de novo no head).
- Vermelho: `bin/forge-testes --vermelho 73a0ab81 --modulos test_fechar_base_andou --prazo 900`: `vermelho: base=73a0ab8179b3 head=c012686146c8 módulos=test_fechar_base_andou (restrito por --modulos)`; `revertidos à base: bin/forge-fechar, changelog.d/v047-h4-atualiza-branch.md, docs/fechamento-integrador.md, docs/protecao-de-branch.md, docs/reviews/v047-h4-atualiza-branch.md, docs/security/v047-h4-atualiza-branch.md`; os 9 testes `test_h4_*` mais `test_c5_base_que_andou_sem_conflito_traz_a_base_e_segue` e `test_c5_dry_run_imprime_o_2b_e_nao_le_o_servidor` saem `H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=26; prova (asserção)=11`; rc=0. A rodada sem `--modulos` (64 módulos) passou do prazo de 590 s (rc=124, sem veredito, descartada).
- Mutação, spec do pedido (`bin/forge-mutante tests/mutantes/v047-h4-atualiza-branch.json tests/mutantes/v047-h4-atualiza-branch-2.json --processos 4`): `rev=c012686146c8`, M1 a M12 `morreu`, rc=0. Conferi a lista contra o diff: as linhas de guarda mudadas (`melhoria/*`, `trazida`, árvore do merge-tree, commit-tree, `so_remota`, worktree suja, ff, update-ref, push, recomeço) têm mutante, exceto o recomeço sem `--trazida` (A1).
- Mutação, specs ajustadas pelo pedido: `bin/forge-mutante tests/mutantes/mp1311-fechar-cartao-2.json` (`rev=c012686146c8`, M6 e M8 `morreu`, rc=0) e `tests/mutantes/v0456-e8b.json` (M1 a M6 `morreu`, rc=0). A troca de `testes` bate com a fonte: `test_e8_base_que_mudou_codigo_segue_sem_trazer_a_base` virou `test_h4_base_que_mudou_codigo_traz_a_base` e `test_e8_arquivo_em_comum_sem_conflito_segue_sem_trazer_a_base` virou `test_h4_arquivo_em_comum_sem_conflito_traz_a_base_e_recomeca`; os dois existem em `tests/test_fechar_base_andou.py` (1 definição cada) e o comportamento E8 antigo foi invertido de propósito pelo H4.
- Mutantes próprios da instância anterior: Q2 e Q3 morreram; Q1 (linha 768, `arvore_mt` limpo) é equivalente (a primeira linha da saída já é a árvore); Q4 (`--trazida` no recomeço, linha 798) sobreviveu: A1 recomendado, sem bloqueio (o ciclo exigiria a base andar de novo no intervalo de um envio, e a falha continua fechada nos demais passos).
- Bordas lidas no diff: árvore do merge-tree fora de 40/64 hex para (`die` no 2b); `git push` sem forçar nem pular o pre-push; cadeia recomeçada herda os argumentos originais (`args_originais`).
- Suíte inteira: não rerrodada; vai ao check `bateria` do CI do PR (sem PR, brief). Permissões e acessibilidade: n/a (ferramenta de linha de comando).

## Revalidação por delta (E1.48, head ecc07992)
- `forge-check parecer delta`: intervalo 80679f19..ecc07992, domínio com `bin/forge-fechar` (linha 789: `[ -d ]` trocado por `test -d`, forma equivalente, mesma guarda) e `tests/mutantes/v047-h4-atualiza-branch.json` (`de` do M6 alinhado à nova linha). Sem mudança de teste.
- Testes do arquivo tocado: `python3 -I -m unittest discover -s tests -p test_fechar_base_andou.py`: 37 testes OK (225 s).
- Mutação do delta: `bin/forge-mutante tests/mutantes/v047-h4-atualiza-branch.json tests/mutantes/v047-h4-atualiza-branch-2.json --processos 4 --base 80679f197f587ac0eabbef9991c66d391f802678`: `base=80679f19… rev=ecc07992…`, M1 a M12 `morreu` (M6 em bin/forge-fechar:789 morre com o `de` novo), rc=0. M11 e M12 (linha 798) mortos: o A1 anterior está coberto.
- Parecer permanece aprovado; sem bugs novos.
