---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: fe1f22755cdaf735ba4738b0f59cb7e1b0eb2068
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-limpar-clone-parecer (#890, E14.7, classe C)

Escopo: `limpar_clones` em `bin/forge-fechar` (linhas 692 e 696) e os testes `tests/test_forge_fechar.py`, `tests/test_fechar_limpar_clone.py`. Clone de QA em `/root/.forge-contrib/wt/v0481-limpar-clone-parecer-qa` (`bin/forge-copia clone`, sem `--revisao`: a opção não existe nesta base), no sha revisado.

## Achados
- A1 (bloqueante) bin/forge-fechar:692 · O clone cujo único commit está numa tag local não enviada passa de "fica" a `rm -rf`: o teste invertido prova (commit só na tag, fora da origin, clone apagado). Afrouxa guarda sem R-ID; falta o rótulo `afrouxa-regra` (R-CONFORMIDADE) ou o recorte da tag.
- A2 (recomendado) tests/catraca.py:684 · A catraca não vê a inversão: o teste da base só chamava `fica()` (0 asserções, 0 valores) e `regra_testes_afrouxados` e `valores_para_conferir` saem vazios; o rótulo não será pedido sozinho. Contar `self.fica` como asserção.

## Resposta ao brief: o renome afrouxa?
Sim. `test_commit_so_em_tag_local_fica` garantia que o clone com trabalho só numa tag local ficava; `test_commit_so_em_tag_local_nao_prende_o_clone` garante o contrário (`returncode 0`, `clone=ok`, pasta apagada). Os testes mantiveram a proteção de branch local, stash e commit depois do head mesclado (`test_commit_nao_enviado_em_outra_branch_fica`, `test_stash_fica`, `test_commit_do_clone_depois_do_head_mesclado_fica`), mas o caso "tag local sem a origin" mudou de lado. O código exclui toda `refs/tags/*`, sem distinguir a tag baixada da origin (a `arquivo/*` apagada lá) da tag criada à mão no clone; o `--not --remotes` não alcança o commit desta segunda.

A catraca não vai pedir o rótulo sozinha (A2). Medi com `regra_testes_afrouxados`, `valores_para_conferir` e `perdas_dos_testes` contra a base `8833d0f6` e contra o head aprovado: as três voltam `[]`. O perfil do teste da base é `(0, 0, False, Counter())`, e o do novo `(3, 0, False, ...)`: não há asserção nem valor a perder. A decisão é do dono (`R-DECISAO`): rotular o PR `afrouxa-regra` com o motivo, ou o autor restringir a exclusão (por exemplo, só tags que a leitura da origin mostra apagadas, ou tag sem commit exclusivo). O título do PR e o corpo não citam o rótulo (conferir no #890).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| tag local fora da conta do `rev-list` | `LimparClones.test_commit_so_em_tag_local_nao_prende_o_clone` | tag local sem commit na origin | passou (mas é o caso do A1) |
| ancestral do head MERGED conta como mesclado, sem a ref remota | `LimparCloneNaoListado.test_parecer_ancestral_do_head_mesclado_sai_sem_a_ref_remota` | ref remota apagada | passou |
| commit depois do head mesclado fica | `LimparCloneNaoListado.test_commit_do_clone_depois_do_head_mesclado_fica` | logo fora do limite (um commit além do head) | passou; não prova (passa na base, guarda herdada) |
| stash segue contando | `LimparClones.test_stash_fica` | stash | passou (herdado) |
| branch local sem envio fica | `LimparClones.test_commit_nao_enviado_em_outra_branch_fica` | branch local | passou (herdado) |

## Vermelho antes do verde
`bin/forge-testes --vermelho 8833d0f69953017f4c5947d4c5f8dc33aca55bfa --modulos tests.test_forge_fechar,tests.test_fechar_limpar_clone` saiu 0. Linhas que provam:
```
tests.test_fechar_limpar_clone.LimparCloneNaoListado.test_parecer_ancestral_do_head_mesclado_sai_sem_a_ref_remota · H=ok · B=falha · prova (asserção)
tests.test_forge_fechar.LimparClones.test_commit_so_em_tag_local_nao_prende_o_clone · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=43; prova (asserção)=2
```
O `test_commit_do_clone_depois_do_head_mesclado_fica` passa na base e no head: guarda de borda, aceita sem vermelho (protege contra o mutante M2 ser largo demais, não prova regra nova).

## Mutantes
`bin/forge-mutante tests/mutantes/v0481-limpar-clone-parecer.json` saiu 0:
```
forge-mutante: pedido=v0481-limpar-clone-parecer rev=fe1f22755cda spec=034a39da1747253b8dc21b452d131405978585a114fd9d2de89318588a084a18
M1 · morreu · bin/forge-fechar:692
M2 · morreu · bin/forge-fechar:696
```
Conferência contra o diff: as duas linhas de guarda mudadas (692 e 696) têm um mutante cada. `forge-mutante --cobertura --base 8833d0f6...` saiu `não coberto: bin/forge-fechar` (shell, fora do que a checagem lê); a conferência manual acima cobre. Nenhum sobrevivente. O M1 só morre pelo teste que o A1 questiona: ao corrigir o A1, o mutante precisa de teste novo para o caso da tag que não pode ser apagada.

## Cenários e resultado real
Suíte completa: não rodada localmente (vale o check-run `bateria` do mesmo sha no CI do PR; não conferido por mim). Rodei os dois módulos do item (vermelho acima, H ok). Sem E2E nem acessibilidade (sem tela). Sondas da catraca em `/workspaces/.forge-contrib/qa-v0481-limpar-sonda-cat.py` e `qa-v0481-limpar-sonda-cat2.py`.
