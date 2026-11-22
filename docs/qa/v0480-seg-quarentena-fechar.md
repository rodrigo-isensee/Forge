---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-quarentena-fechar
commit: e77f3543f1844065aa66c90e6c1ba3123e66e55c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: QUARENTENA-DIGITO-ASCII e FECHAR-SEM-AUTO-MERGE (v0478 E114.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| QUARENTENA-DIGITO-ASCII: OK do dono só com dígito ASCII | `test_forge_quarentena.Validar.test_autorizacao_so_com_digito_ascii`; sonda própria | `A-١` (árabe-índico), `A-１` (largura total), `A-²`, `A-`, `a-1`, `A-1\n` recusados; `A-1`, `A-12` aceitos | passou |
| FECHAR-SEM-AUTO-MERGE: `--armar` recusado, sem nada feito | `test_fechar_auto_merge.SemAutoMerge.test_armar_recusa_com_o_porque_e_o_comando_certo_sem_nada_feito`; mutante manual (die trocado por shift) derrubou 6 testes | flag removida | passou |
| Merge direto preso ao head, sem `--auto` nem `--admin` | `test_merge_direto_preso_ao_head_sem_auto_nem_admin`, `test_dry_run_mostra_o_merge_direto`, `test_ajuda_sem_merge_automatico` | `--match-head-commit` | passou |
| Check obrigatório pendente ou ausente espera, relê e só então mescla | `test_check_run_pendente_espera_e_relê_antes_do_merge`, `FecharChecksDoHead.test_rodando_ou_ausente_espera_e_para_no_prazo_sem_merge` | pendente, ausente, fim do prazo | passou |
| Check terminado com falha para sem esperar e sem merge | `FecharChecksDoHead.test_terminado_com_falha_recusa_sem_esperar`, `test_execucao_mais_nova_com_falha_recusa_mesmo_com_a_velha_verde` | failure, cancelled, execução mais nova | passou |
| Promoção (P6) confere os check-runs da marca antes do merge direto | mutante FCK-M7 | caminho da release | passou |
| MERGED atrasado ou ausente no prazo | `test_merged_atrasado_espera_e_fecha_sem_repetir_o_merge`, `test_merge_que_nao_consta_merged_no_prazo_para_sem_limpar` | prazo | passou |

## Cenários e resultado real
- Testes dos módulos tocados, `python3 -I -m unittest discover -s tests -p <módulo>.py`, TMPDIR próprio: test_forge_quarentena 29 OK; test_fechar_auto_merge 8 OK; test_fechar_checks_do_head 8 OK; test_fechar_lote 61 OK; test_fechar OK. Suíte inteira não rodada (CI do PR).
- Vermelho antes do verde: `forge-testes --vermelho b0895f6c --modulos test_forge_quarentena,test_fechar_auto_merge,test_fechar_checks_do_head`: `vermelho: base=b0895f6cc03d head=e77f3543f184`; revertidos à base `bin/forge-fechar` e `bin/forge_quarentena.py`; 12 provam (asserção), 33 não provam (já passavam na base, não são do pedido). Entre os que provam: `test_autorizacao_so_com_digito_ascii`, `test_armar_recusa...`, `test_check_run_pendente_...`, `test_check_run_pendente_no_fim_do_prazo_...`.
- Mutação: `forge-mutante tests/mutantes/v0480-seg-quarentena-fechar.json`: `QD1 · morreu · bin/forge_quarentena.py:28`, `FS1 · morreu · bin/forge-fechar:909`. `forge-mutante tests/mutantes/v0478-fechar-checks.json`: FCK-M1 a FCK-M8 todos `morreu` (inclui o P6 e o pendente que espera). `--armar` recusado: mutante em v046-fechar-lote.json e o meu manual, ambos mortos. `--cobertura --base` diz `não coberto: bin/forge-fechar` (shell); conferi à mão: cada linha de guarda mudada (recusa de `--armar`, falha terminada, pendente, prazo, P6, leitura que falha) tem mutante morto.
- Sondas: dígito Unicode recusado (acima); `--armar` sai 1 com o comando certo; check pendente espera e relê; check com falha para antes do merge, sem `gh pr merge`.
- Sem `skip`, `skipIf` nem `expectedFailure` nos testes tocados.
- O remoto avançou com os pareceres de review e segurança (só `docs/`), sem código; rebase sobre eles.
