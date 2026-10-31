---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c1
commit: fb306ea2a9f78ab7965ef6500bd1393c8712591c
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c1)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..fb306ea` (`bin/forge-fechar`, `tests/test_fechar_r1_worktree.py`, `docs/fechamento-integrador.md`, fragmento do changelog; mais os pareceres de review e segurança).

## Item entregue e M14
Item E1 do pedido (FECHAR-R1-WORKTREE com o C1-2 do modelo de ameaças): pendência por commit sem merge imprime leitura (`git log --oneline`), não comando que apaga, em `limpar_entrega` e no bloco do `--sem-limpar`. Um comportamento, em dois caminhos. M14 (agents/tech-lead.md:19): 192 linhas de código e teste (55 em `bin/forge-fechar`, 137 no teste), acima do teto; não toca `hooks/` nem `PROTEGIDOS`, então a exceção cabe, aceita no review com a linha `teto: excedido, 192 linhas, <motivo>` no corpo do PR (A3). Cumpre a M14 com essa condição.

## Achados
- A1 (bloqueante) bin/forge-fechar:830 · Mutante sobrevivente: trocar o aviso de leitura da remota do --sem-limpar por `git push origin --delete` passa os 209 testes; falta teste da falha fechada. Teste novo: ls-remote falha e a saída não traz o comando que apaga (R-QA).
- A2 (recomendado) bin/forge-fechar:448 · Mutante sobrevivente: `leitura_dada=0` imprime a mesma linha de leitura duas vezes (worktree e branch) e nenhum teste exige uma só. Efeito só de apresentação; um assertEqual sobre a contagem da linha prende.
- A3 (recomendado) tests/test_fechar_r1_worktree.py:1 · PR acima do teto da M14 (192 linhas): o corpo do PR precisa da linha `teto: excedido, 192 linhas, <motivo>` (pelo --muda do forge-fechar), senão vale o bloqueante da M14.
- A4 (recomendado) tests/mutantes:1 · Pedido que toca bin/ sem spec de mutantes declarada pelo autor; a lista abaixo é do QA (8 mutantes, um por linha de guarda mudada). Declarar em tests/mutantes/impl-fechar-c-c1.json na volta.

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
| C1-2 leitura da remota falha: só comentário | nenhum | falha da API | SEM TESTE (A1) |

## Cenários e resultado real
Vermelho antes do verde, `forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos test_fechar_r1_worktree`:
```
vermelho: base=234dbe0fb90b head=fb306ea2a9f7 módulos=test_fechar_r1_worktree (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/impl-fechar-c-c1.md, docs/fechamento-integrador.md, docs/reviews/impl-fechar-c.md, docs/security/impl-fechar-c.md
mantidos no HEAD: tests/test_fechar_r1_worktree.py
(6 testes) H=ok · B=falha · prova (asserção)
test_sha_mesclado_com_worktree_ocupada_continua_imprimindo_o_comando · H=ok · B=ok · não prova (regressão, declarada)
contagem: não prova (passa na base)=1; prova (asserção)=6
rc=0
```
Mutação (`bin/forge-mutante` sobre spec do QA fora do repositório, 8 mutantes, rev fb306ea2a9f7):
```
M1 · morreu · bin/forge-fechar:396
M2 · morreu · bin/forge-fechar:819
M3 · morreu · bin/forge-fechar:827
M4 · morreu · bin/forge-fechar:527
M5 · sobreviveu · bin/forge-fechar:830
M6 · morreu · bin/forge-fechar:408
M7 · morreu · bin/forge-fechar:383
M8 · sobreviveu · bin/forge-fechar:448
rc=1
```
M5 é o A1 (bloqueante); M8 é o A2.

Suíte: módulos `tests/test_fechar*.py` no head, sem bytecode: `Ran 209 tests` / `OK (skipped=1)` (o skip é `test_shellcheck_fechar_passa_limpo`, que pula sem `shellcheck` no PATH; o CI o roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
