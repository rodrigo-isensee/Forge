---
tipo: qa
contrato: 1
pedido: lote-fechar-031
branch: melhoria/lote-fechar-031
commit: e377173d8da5c6c35b765f3f3fe38fe6bf0a1590
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-fechar-031

Três melhorias do `bin/forge-fechar` (E1 pasta do log ajustada para 700, E2 limpeza de dentro da worktree, E3 `--sem-limpar`), sobre `e377173` (base `d150ec8`). Review (rodada 2) e segurança já aprovados na branch. PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens, nenhum se aplica.

## Achados
- A1 (bloqueante) bin/forge-fechar:156 · FORGE_FECHAR_LOG_DIR relativo com `..` rodado de dentro da worktree: o log vira `$PWD/../x` (sem normalizar), a worktree some no passo 7 e o registrador perde o arquivo; o script morre por SIGPIPE (-13) depois do merge, sem `fim:`. Na base d150ec8 saía 3 com `fim: código 3`. Classe: caminho montado sem normalizar. O mutante L5 (sem a linha) sobrevive: nenhum teste cobre log relativo.
- A2 (bloqueante) bin/forge-fechar:165 · A conferência do modo depois do `chmod` não tem teste: o mutante L4 (`|| die` trocado por `|| true`) sobrevive. Sonda com `chmod` falso (rc 0, modo intacto): o original recusa (rc 1); o mutante avisa "ajustei para 700" com a pasta em 755 e segue. Classe: guarda nova sem teste, testável com um `chmod` falso no PATH.
- A3 (recomendado) bin/forge-fechar:371 · Nenhum teste cobre o ramo "não achei outra para sair" (branch na worktree principal, rodado nela): mutantes W2 (`arv_st=ok`) e W3 (guarda `!= ok` desligada) sobrevivem. Efeito observável igual (git recusa remover a principal; rc 3, mesmo resumo), por isso recomendado. Aceito como equivalente no efeito; um teste da sonda S7 fecha a lacuna.

## Critério → teste → resultado
O pedido não tem `CA-n` (E1 a E3 do pedido LOTE-FECHAR-031 fazem o papel).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 pasta 755/777/2755/0500 vira 700 com aviso | `test_pasta_do_log_do_proprio_usuario_...vira_700_com_aviso`; sonda S1 (755, 2755, 777, fechamento inteiro) | setgid, permissivo, sem escrita | passou |
| E1 link, arquivo, outro dono recusados; sem chmod no alvo | `test_pasta_com_modo_700_...continuam_recusados`; sonda S2 (link, arquivo, `/usr` de root, link para `/usr`) | link, não diretório, dono | passou |
| E1 chmod ineficaz recusa | sonda S8 | modo que não muda | passou no original; sem teste na branch (A2) |
| E2 de dentro da worktree sai, limpa e fecha com 0 | `test_de_dentro_da_worktree_da_branch_sai_...fecha_com_0`; sonda S3 e S3b (subpasta) | cwd na worktree | passou |
| E2 commit não mesclado: pendente, código 3, nada removido | `test_de_dentro_da_worktree_com_commit_nao_mesclado_...`; sonda S4 | sha local fora da base | passou |
| E2 sem outra worktree: pendente com o comando | sonda S7 | branch na principal | passou; sem teste na branch (A3) |
| E2 com log relativo | sonda S9 | `FORGE_FECHAR_LOG_DIR=../x` | falhou (A1) |
| E3 `--sem-limpar`: merge, pula passo 7, código 3, `--limpar` primeiro, `branch -D` só com branch local | `test_sem_limpar_mescla_pula_...`, `test_sem_limpar_sem_branch_local_...`; sonda S5, S5c; S5b roda o `--limpar` impresso e fecha com 0 | branch local ausente | passou |
| E3 com `--limpar`: erro de uso, nenhuma chamada | `test_sem_limpar_com_limpar_e_erro_de_uso_...`; sonda S6 (as duas ordens) | combinação | passou |
| E3 `--dry-run` só descreve | `test_sem_limpar_com_dry_run_so_descreve` | dry-run | passou |

## Cenários e resultado real
- Suíte dirigida: `python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao` → `Ran 96 tests in 63.825s`, `OK`.
- Sonda de ponta a ponta: repositório em `$TMPDIR/qa-lote-fechar-031/` com remoto local e `gh` falso (o harness de `tests/test_fechar.py`), script da branch, sem GitHub nem `~/Forge`. Resultado de cada caso na tabela acima; a pasta 755, 2755 e 777 fecharam com 0, modo final 0o700 e aviso; o fechamento de dentro da worktree saiu para a principal e fechou com 0; commit não mesclado ficou pendente com código 3 sem `worktree remove`.
- Controle da regressão A1: o mesmo cenário S9 no script da base `d150ec8` sai com código 3 e `fim: código 3` (log inteiro); no script da branch sai com -13 e o log termina no meio.
- Observação sem achado (S3c): log relativo sem `..` de dentro da worktree cai dentro dela e a deixa suja; a worktree fica pendente (comportamento seguro).
- Vermelho antes do verde (`bin/forge-testes --vermelho d150ec87b004f6f5561a65aa130bb16cf454473c --modulos test_fechar,test_fechar_log_check,test_fechar_orfao`, saída 0):
```
vermelho: base=d150ec87b004 head=e377173d8da5 módulos=test_fechar,test_fechar_log_check,test_fechar_orfao (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/lote-fechar-031.md, docs/fechamento-integrador.md, docs/reviews/lote-fechar-031.md, docs/security/lote-fechar-031.md
...pasta_do_log_do_proprio_usuario_com_modo_diferente_de_700_vira_700_com_aviso · H=ok · B=falha · prova (asserção)
...de_dentro_da_worktree_com_commit_nao_mesclado_continua_pendente_sem_apagar · H=ok · B=falha · prova (asserção)
...de_dentro_da_worktree_da_branch_sai_para_a_principal_remove_e_fecha_com_0 · H=ok · B=falha · prova (asserção)
...sem_limpar_com_dry_run_so_descreve / sem_limpar_com_limpar_e_erro_de_uso / sem_limpar_mescla_pula_o_passo_7 / sem_limpar_sem_branch_local · B=falha · prova (asserção)
contagem: não prova (passa na base)=89; prova (asserção)=7
```
- Mutantes declarados (`bin/forge-mutante`, specs em `$TMPDIR/qa-lote-fechar-031/m1.json` a `m4.json`, escritas por mim, uma por guarda nova do diff; o autor não declarou lista). Saídas coladas:
```
m1 (rev=e377173d8da5): L1 morreu :164 (chmod simbólico/setgid) · L2 morreu :166 (aviso) · L3 morreu :163 (só ajusta se != 700)
  L4 SOBREVIVEU :165 (confere o modo depois do chmod) · L5 SOBREVIVEU :156 (logdir absoluto)
  U1 morreu :59 (--limpar x --sem-limpar) · U2 morreu :719 (pula o passo 7) · U3 morreu :728 (exit 3)   rc=1
m2: W1 morreu :368 (cd para a principal) · W2 SOBREVIVEU :371 (fallback pendente) · W3 SOBREVIVEU :375 (guarda != ok)
  W4 morreu :377 (guarda de sha) · P1 morreu :725 (worktree remove impresso) · P2 sobreviveu por erro meu (troca para "nunca imprime", que o teste do ramo ausente não cobra)
  P3 morreu :724 (--limpar primeiro) · D1 morreu :514 (dry-run)   rc=1
m3: A1 morreu :50 (parse --sem-limpar) · A2 morreu :727 (push --delete impresso)   rc=0
m4: P2b morreu :726 (branch -D impresso sempre; o mutante certo de P2)   rc=0
```
Sobreviventes que valem: L4 e L5 (A1, A2, bloqueantes) e W2 e W3 (A3, equivalentes no efeito, recomendado). P2 original foi mutante mal escrito; P2b, o certo, morreu.
- Não rodados por serem fora do pedido: suíte completa, shellcheck e `validar-plugin.sh` (pre-push e CI).

## Responsável
Correção do A1 e testes de A2 e A3: `tech-lead` (autor do `bin/forge-fechar`). Sugestão de correção do A1 (não aplicada, QA não corrige produção): normalizar com `cd "$logdir" && pwd -P` depois do `mkdir`, em vez de `$PWD/$logdir`.
