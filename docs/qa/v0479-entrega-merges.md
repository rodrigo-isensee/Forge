---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 590d1954d4d31881a434ef926530a0bc52e2c711
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 E62.18 (forge-check entrega: merges da develop e merges de pareceres aninhados, head 590d1954)

## Achados
- A1 (bloqueante) bin/forge-check:2853 · `vindos_da_base` redefine a função do E7 (linha 877) com outra assinatura: tests/test_forge_check_base_igual.py passa no Base-sha (13 OK) e cai no head (4 falhas). Log e6218-baseigual.log. Renomeie a nova e ajuste D1 a D7.
- A2 (recomendado) tests/mutantes/v0479-entrega-merges.json:1 · nenhum mutante nem teste do conjunto pega a sobreposição de nome (A1): a rodada D1-D7 e N1-N3 morre toda e o defeito passa. Some um teste que chame `commit_vale` e `parecer delta` com a função nova no módulo.
- A3 (recomendado) bin/forge-check:2528 · os achados A2 do review (blob conferido antigo sobre o mais novo) e A1/A2 da segurança (ls-remote por cauda; merge-base intermediário de PR lateral) não foram reproduzidos por mim; valem como estão nos pareceres e devem voltar com teste e mutante.

## Critério → teste → resultado
O pedido não traz `CA-n` de UX; as obrigações são as regras nomeadas no diff.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| ENTREGA-MERGE-DA-DEVELOP: arquivo igual ao merge-base remoto sai do escopo | MergeDaBaseDepoisDoBrief.test_merge_base_sem_ancora_fica_o_base_sha; JuncaoLimpa.test_juncao_sem_ancora_segue_pendente | merge sem âncora | passou (vermelho na base) |
| Sem rede nada sai | test_sem_rede_o_que_a_develop_trouxe_segue_no_escopo | sem rede | passou |
| Remoto não buscado (sem merge-base) nada sai | test_develop_remota_sem_fetch_nao_tira_nada | commit ausente | passou |
| Aceite do usuário nunca sai | test_aceite_do_usuario_vindo_da_develop_segue_no_escopo | permissão | passou |
| O que o autor mudou por cima segue dele | test_o_que_o_autor_mudou_por_cima_da_develop_segue_dele; test_o_que_a_branch_mudou_e_o_merge_devolveu_a_develop_segue_a_vista | blob diferente | passou |
| Merge de fora da develop segue no escopo | test_merge_de_fora_da_develop_segue_no_escopo | outra base | passou |
| Ref local sem o merge não consulta o remoto | test_ref_local_sem_o_merge_nao_consulta_o_remoto | ref local | passou |
| ENTREGA-MERGE-DE-PARECER-ANINHADO: vale pelo blob conferido | MergeDeParecerAninhado.test_parecer_do_merge_de_pareceres_vale_pelo_blob_conferido | blob igual | passou (vermelho na base) |
| Blob diferente, conferido fora da história, aceite do usuário e pai sem linha reprovam | MergeDeParecerAninhado (4 testes) | blob, história, permissão | passou |
| Não regredir o E7 (`vindos_da_base` antiga) | tests/test_forge_check_base_igual.py | assinatura | FALHOU (4 de 13) |

## Cenários e resultado real
- Vermelho (`bin/forge-testes --vermelho 8ee73d15 --modulos test_selo_e_entrega --prazo 1100`, rc=0, log e6218-verm.log): `vermelho: base=8ee73d156db5 head=590d1954d4d3 módulos=test_selo_e_entrega (restrito por --modulos)`; `contagem: não prova (passa na base)=148; prova (asserção)=3` (JuncaoLimpa.test_juncao_sem_ancora_segue_pendente, MergeDaBaseDepoisDoBrief.test_merge_base_sem_ancora_fica_o_base_sha, MergeDeParecerAninhado.test_parecer_do_merge_de_pareceres_vale_pelo_blob_conferido; H=ok, B=falha). Nenhum cai no head.
- Mutantes (cada spec numa chamada, rev=590d1954d4d3): v0479-entrega-merges.json D1 a D7 morreram, rc=0; v0479-entrega-merges-2.json N1 a N3 morreram, rc=0; revisor-wt-e6a-3.json M1 a M12, M14 a M16 morreram, incluindo o M9 alinhado (bin/forge-check:2514), rc=0. Logs e6218-mut1/2/3.log.
- `forge-mutante --cobertura --base 8ee73d15` (rc=0): `spec editada · tests/mutantes/revisor-wt-e6a-3.json` e as linhas 2528, 2860, 2863, 2866, 2868 (D5, D6), 3277 (D1), 3278 (D7) como coberta · declarado, não provado. Todas as condições mudadas têm mutante. Log e6218-cob.log.
- Caso real A2 (clone v0479-pv-a2-concessao, head 4db0fc78, `entrega --etapa codigo --so-leitura`): com o forge-check do Base-sha, `escopo: fora (o merge 445f198 traz "docs/reviews/v0479-pv-a2-concessao.md" fora dos pareceres conferidos)`, `resultado: não cumpriu`, rc=1; com o forge-check do head, `resultado: cumpriu`. Confere com e6210-a2-antes/depois.log. Logs e6218-a2.log e e6218-a2-base.log.
- Caso real B1: lido em e6210-sonda-b1-depois.log; o merge de pareceres não conferidos segue recusado (`merge de 0356c9d não conferido`), como deve.
- Regressão: `python3 -I -m unittest discover -s tests -p test_forge_check_base_igual.py`: Base-sha 13 OK; head FAILED (failures=4). O vermelho restrito ao módulo do autor não vê isso: o módulo atingido é outro.
- Suíte completa: não rodei (no CI do PR; ainda não há PR, sem check-run `bateria`).

## Parecer
Reprovado: o defeito A1 é provado (regressão numa guarda existente), com o review e a segurança também reprovando por A1 e A2 de cada um. Revalidar com `forge-check parecer delta docs/qa/v0479-entrega-merges.md`.
