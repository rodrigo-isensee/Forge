---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c1
commit: 6a97b4647f566a32f7df43b8c8cab39b6926eb6c
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c1)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..6a97b46` (`bin/forge-fechar`, `tests/test_fechar_r1_worktree.py`, `docs/fechamento-integrador.md`, fragmento do changelog; mais os pareceres de review e segurança).

## Item entregue e M14
Item E1 do pedido (FECHAR-R1-WORKTREE com o C1-2 do modelo de ameaças): pendência por commit sem merge imprime leitura (`git log --oneline`), não comando que apaga, em `limpar_entrega` e no bloco do `--sem-limpar`. Um comportamento, em dois caminhos. M14 (agents/tech-lead.md:19): 192 linhas de código e teste (55 em `bin/forge-fechar`, 137 no teste), acima do teto; não toca `hooks/` nem `PROTEGIDOS`, então a exceção cabe, aceita no review com a linha `teto: excedido, 192 linhas, <motivo>` no corpo do PR (A3). Cumpre a M14 com essa condição.

## Achados
- A1 (recomendado) bin/forge-fechar:830 · Resolvido na volta: o mutante da falha fechada da leitura da remota (C1-5) agora morre; o teste AB-C1-8 exige só o comentário e nenhum `git push origin --delete`.
- A2 (recomendado) bin/forge-fechar:448 · Segue aberto, só apresentação: `leitura_dada=0` imprime a mesma linha de leitura duas vezes e nenhum teste exige uma só. Não devolve.
- A3 (recomendado) tests/test_fechar_r1_worktree.py:1 · PR acima do teto da M14 (192 linhas): o corpo do PR precisa da linha `teto: excedido, 192 linhas, <motivo>` (pelo --muda do forge-fechar), senão vale o bloqueante da M14.
- A4 (recomendado) tests/mutantes/impl-fechar-c-c1.json:1 · Resolvido: spec declarada pelo autor (7 mutantes), todos morrem.

## Revalidação (volta por delta)
`forge-check delta --parecer docs/qa/impl-fechar-c.md` listou `fb306ea..6a97b46`: `tests/mutantes/impl-fechar-c-c1.json` (1-125, lido inteiro) e `tests/test_fechar_r1_worktree.py` (110-126, o AB-C1-8, lido). Já lido e sem mudança: `bin/forge-fechar` e o resto do diff (`bin/` não mudou na volta).
Conferência da lista contra o diff de `bin/forge-fechar`: uma linha de guarda mudada por mutante (marca de sem_merge, releitura local, releitura remota, ramo da remota por leitura, falha fechada, aviso na worktree, texto da leitura); além disso, dois mutantes meus nos `elif` dos ramos da branch local (linhas 445 e 488) também morreram. `forge-mutante --cobertura` só diz `não coberto: bin/forge-fechar` (shell); a conferência foi à mão.

## Critério → teste → resultado
O pedido não traz `CA-n`; os critérios são os controles C1-1 a C1-3 do modelo de ameaças (`docs/security/ameacas/fechar-c.md`, SEC-FECHARC-2) e os casos AB-C1-1 a AB-C1-7.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1-1/C1-2 worktree com commit novo imprime leitura | AB-C1-1 `test_limpar_com_commit_novo_na_worktree_...` | commit sem merge x sha mesclado | passou (vermelho na base) |
| C1-2 de dentro da worktree sem outra para sair | AB-C1-2 `test_limpar_de_dentro_da_worktree_principal_...` | permissão: única worktree | passou (vermelho na base) |
| C1-1 remota decide pelo sha dela | AB-C1-3 `test_limpar_com_remota_sem_merge_...` | local mesclada x remota não | passou (vermelho na base) |
| C1-2 `--sem-limpar` relê o local | AB-C1-4 `test_sem_limpar_com_commit_local_depois_do_passo_2_...` | commit durante a espera | passou (vermelho na base) |
| C1-2 `--sem-limpar` relê a remota | AB-C1-7 `test_sem_limpar_com_remota_que_andou_...` | remota anda após o passo 2 | passou (vermelho na base) |
| C1-3 ref com caractere do shell escapada | AB-C1-5 `test_ref_com_caractere_do_shell_...` | `$` na ref | passou (vermelho na base) |
| Regressão: sha mesclado ainda imprime o comando | AB-C1-6 `test_sha_mesclado_com_worktree_ocupada_...` | sha mesclado | passou (verde na base, como regressão) |
| C1-2 leitura da remota falha: só comentário | AB-C1-8 `test_sem_limpar_com_leitura_da_remota_que_falha_so_avisa_e_nao_manda_apagar` | falha da API | passou (mata o mutante C1-5) |

## Cenários e resultado real
Vermelho dos testes antigos: parecer anterior (`forge-testes --vermelho 234dbe0...`, 6 provam, 1 regressão declarada, rc=0). O teste novo da volta (AB-C1-8) cobre código que a base já tem na própria branch (a volta só mexeu em `tests/`), então o vermelho dele é o mutante: `forge-testes --vermelho ceca534~1` sai `nenhum teste prova a mudança` (esperado, o código já existia), e a prova é o mutante C1-5, que sobrevivia e agora morre.
Mutação, `bin/forge-mutante tests/mutantes/impl-fechar-c-c1.json`:
```
forge-mutante: pedido=impl-fechar-c-c1 rev=6a97b4647f56 spec=c2b154e0c121f79c9393531d54a131da1d83b3c8531d840985de0255befb7af4
C1-1 · morreu · bin/forge-fechar:396
C1-2 · morreu · bin/forge-fechar:819
C1-3 · morreu · bin/forge-fechar:827
C1-4 · morreu · bin/forge-fechar:527
C1-5 · morreu · bin/forge-fechar:830
C1-6 · morreu · bin/forge-fechar:408
C1-7 · morreu · bin/forge-fechar:383
rc=0
```
Suíte: `tests/test_fechar*.py` no head: `Ran 210 tests` / `OK (skipped=1)` (o skip é o shellcheck, que o CI roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
