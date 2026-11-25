---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: dd2fcada2719cafad4eee2d8e31f3aaec2e8d5c3
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 forge-fechar (CI do topo, branch criada do servidor, cópia certa)

Links: pedido v0481 (E13.1, QA E13.8), `docs/fechamento-integrador.md`, `bin/forge-fechar`. Sem UX nem API. As obrigações são as do brief: nenhum caminho mescla sem os checks verdes do head, o CI do topo só vale quando contém o merge, nada que barra hoje deixa de barrar. Offline, `gh` e `git` falsos (`R-CUSTO`).

## Achados
- A1 (bloqueante) tests/mutantes/mp1311-fechar-cartao.json:16 · o M2: o diff reescreve o `ref_check="$sha_conferido"` de bin/forge-fechar (agora dentro de `else`); o `de` do M2 deixou de existir e a bateria do CI (dd2fcad) cai em ConferirTodas (AR-12). Alinhe a spec no mesmo commit.

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

## Provas
- Pacote `test_fechar*.py` no head dd2fcad: 481 testes, OK (skipped=1), 440 s.
- `bin/forge-mutante tests/mutantes/v0481-fechar-ci-topo.json`: M1 (:1235), M2 (:1236), M3 (:1241), M4 (:1687), M5 (:1688), M6 (:1655), M7 (:1662), M8 (:1663), todos `morreu`. A lista cobre cada linha de guarda mudada no diff.
- Sondas minhas (arquivo, `gh` e `git` falsos): `--dry-run` na cópia principal na branch sai 0 sem parar; o topo cujo CI também é cancelado sai 5 com o aviso do topo novo (o laço não gira sem fim); `--sem-limpar` na cópia principal na branch agora para com 1 antes do passo 1 (antes mesclava e saía 3): barra mais, não menos.
- CI do mesmo sha: run 45527336208, check `bateria` = failure. Causa: `suíte (python 3.14, parte 4/5)`, `test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes`; reproduzido aqui com `bin/forge-mutante --conferir --todas`: `tests/mutantes/mp1311-fechar-cartao.json: M2 · o trecho aparece 0 vezes em bin/forge-fechar`.

## Vermelho antes do verde
`forge-testes --vermelho d49accf8c5d7575bc02354a1bd0014d8c954600c --modulos test_fechar_ci_topo,test_fechar_sha_conferido`, rc=0:
```
vermelho: base=d49accf8c5d7 head=dd2fcada2719 módulos=test_fechar_ci_topo,test_fechar_sha_conferido (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0481-fechar-ci-topo.md, docs/fechamento-integrador.md, tests/pesos-d4.json
contagem: não prova (passa na base)=12; prova (asserção)=6
```
Provam (caem na base): `test_topo_verde_que_contem_o_merge_fecha_com_0`, `test_topo_vermelho_continua_5_com_a_reversao_do_merge`, `test_topo_identico_ao_merge_tambem_decide`, `test_copia_principal_na_branch_para_antes_do_passo_1`, `test_commit_que_falta_aqui_cria_a_branch_local_no_sha_do_servidor`, `test_branch_local_que_nao_se_cria_para_antes_do_passo_1`. Os 12 que passam na base guardam o que já barrava (diverged, topo igual, worktree, servidor que anda) ou o ramo que a base já cumpria; as guardas novas deles são provadas pelos mutantes M2, M6 e M7.

## Bugs
Nenhum de comportamento do `forge-fechar`; o único defeito é o A1 (spec de mutante desalinhada, bateria vermelha).

## Veredito
Reprovado em dd2fcad só pelo A1: a lógica nova do passo 8, do passo 1 e da cópia certa está correta e protegida; falta alinhar a spec `mp1311-fechar-cartao.json` M2 (o `de` de `ref_check="$sha_conferido"` no novo `else`, com 4 espaços de indentação) e ver a bateria verde. Na volta, `forge-check parecer delta docs/qa/v0481-fechar-ci-topo.md`.
