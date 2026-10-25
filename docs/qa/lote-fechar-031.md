---
tipo: qa
contrato: 1
pedido: lote-fechar-031
branch: melhoria/lote-fechar-031
commit: 6d73534288b4921cd06e80ac77df9ce45c643575
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-fechar-031

Três melhorias do `bin/forge-fechar` (E1 pasta do log ajustada para 700, E2 limpeza de dentro da worktree, E3 `--sem-limpar`), revalidadas depois da volta 3, head `6d73534` (base `d150ec8`). Review e segurança já aprovados. PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens, nenhum se aplica. Revalidação por delta sobre o parecer anterior (`fe9cc38`, reprovado: A1 e A2 bloqueantes, A3 recomendado); delta `fe9cc38..6d73534` = `bin/forge-fechar` (+2 −1) e dois arquivos de teste.

## Achados

## Revalidação dos achados da rodada anterior
| Achado | Correção no delta | Prova | Resultado |
|---|---|---|---|
| A1 log relativo com `..` de dentro da worktree | `logdir="$(cd "$logdir" && pwd -P)"` depois do `mkdir` (bin/forge-fechar:161); sai a forma `$PWD/$logdir` | `test_de_dentro_da_worktree_com_log_relativo_com_ponto_ponto_fecha_com_fim_e_codigo_0`: `FORGE_FECHAR_LOG_DIR=../x/../logrel`, cwd na worktree; código 0, resumo `remota=ok worktree=ok branch=ok`, pasta do log absoluta e normalizada, última linha `fim: código 0`; vermelho no código anterior (`B=falha · prova (asserção)`) | corrigido |
| A2 conferência do modo após o `chmod` | teste novo com `chmod` falso (rc 0, modo intacto): código 1, mensagem "precisa ter modo 700", sem "ajustei", pasta segue 755 | mutante L4 morreu | corrigido |
| A3 ramo "não achei outra para sair" | teste novo: branch na worktree principal, rodado nela, `--limpar`: código 3, resumo `pendente/pendente`, nenhum `worktree remove` nem `branch -D` | mutantes W2 e W3 morreram | corrigido |

## Critério → teste → resultado
O pedido não tem `CA-n` (E1 a E3 do pedido LOTE-FECHAR-031 fazem o papel).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 pasta 755/777/2755/0500 vira 700 com aviso | `test_pasta_do_log_do_proprio_usuario_...vira_700_com_aviso` | setgid, permissivo, sem escrita | passou |
| E1 link, arquivo, outro dono recusados; sem chmod no alvo | `test_pasta_com_modo_700_...continuam_recusados` | link, não diretório, dono | passou |
| E1 chmod ineficaz recusa | `test_chmod_que_sai_0_sem_mudar_o_modo_faz_o_script_recusar` | modo que não muda | passou |
| E1 log relativo com `..` de dentro da worktree | `test_de_dentro_da_worktree_com_log_relativo_com_ponto_ponto_...` | caminho relativo, cwd removido no passo 7 | passou |
| E2 de dentro da worktree sai, limpa e fecha com 0 | `test_de_dentro_da_worktree_da_branch_sai_...fecha_com_0` | cwd na worktree | passou |
| E2 commit não mesclado: pendente, código 3, nada removido | `test_de_dentro_da_worktree_com_commit_nao_mesclado_...` | sha local fora da base | passou |
| E2 sem outra worktree: pendente com o comando | `test_branch_na_worktree_principal_rodado_nela_...` | branch na principal | passou |
| E3 `--sem-limpar`: merge, pula passo 7, código 3, `--limpar` primeiro, `branch -D` só com branch local | `test_sem_limpar_mescla_pula_...`, `test_sem_limpar_sem_branch_local_...` | branch local ausente | passou |
| E3 com `--limpar`: erro de uso, nenhuma chamada | `test_sem_limpar_com_limpar_e_erro_de_uso_...` | combinação | passou |
| E3 `--dry-run` só descreve | `test_sem_limpar_com_dry_run_so_descreve` | dry-run | passou |

## Cenários e resultado real
- Suíte dirigida sobre o head: `python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao` → `Ran 99 tests in 38.646s`, `OK` (eram 96; +3 testes do delta).
- Vermelho antes do verde sobre o delta (`bin/forge-testes --vermelho fe9cc38983ccee55b4a939ad8262d6d0f94fd8ad --modulos test_fechar,test_fechar_log_check,test_fechar_orfao`, saída 0): `revertidos à base: bin/forge-fechar`; o teste do A1 sai `H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=98; prova (asserção)=1`. Os testes de A2 e A3 testam código já existente no `fe9cc38` (a lacuna era a falta de teste), então passam na base e a prova deles é a mutação abaixo. O vermelho do lote inteiro contra `d150ec8` está no parecer anterior (7 testes provam, saída 0) e a lógica do lote não mudou.
- Mutantes (`bin/forge-mutante`, spec minha em `$TMPDIR/qa-engineer-lote-fechar-031/m5.json`, rev `6d73534288b4`; a única linha de guarda mudada no delta é a normalização do `logdir`, coberta por L5 e L5b; L4, W2 e W3 são os sobreviventes da rodada anterior), saída 0:
```
L4 · morreu · bin/forge-fechar:166
L5 · morreu · bin/forge-fechar:161
L5b · morreu · bin/forge-fechar:161
W2 · morreu · bin/forge-fechar:372
W3 · morreu · bin/forge-fechar:376
```
  L5 remove a normalização; L5b a troca pela forma antiga `$PWD/$logdir`. Nenhum sobrevivente. Os mutantes L1 a L3, U1 a U3, W1, W4, P1 a P3, D1, A1 e A2 da rodada anterior morreram sobre `e377173`, e o delta não toca as linhas deles.
- Não rodados por serem fora do pedido: suíte completa, shellcheck e `validar-plugin.sh` (pre-push e CI).

## Responsável
Sem defeito aberto; nada a corrigir.
