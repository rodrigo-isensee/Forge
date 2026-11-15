---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: 13cb874d23ef51f505f3dfcb3248c78c6ffea22c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 integração em lote, release em 1 h e espera do CI da develop (E1.239)

Head `c6b0b788` na `melhoria/v047-integracao-em-lote`, base `f4b0c2ae`. Diff de código: `bin/forge-fechar` (+291), `tests/test_fechar_lote.py` (novo, 50 testes), `tests/test_fechar.py`, 8 specs de mutantes, texto de fluxo (`R-FLUXO`, `docs/fechamento-integrador.md`, tech-lead, skill). Sem PR aberto na leitura: não há check-run `bateria` para citar; rodei os módulos `test_fechar*`.

## Achados
- A1 (recomendado) bin/forge-fechar:1 · a medida do pedido (tempo do PR verde até a develop; do commit da marca até o PR para a main) não está no diff; nenhum `forge-check metricas` mudou. Fora do escopo da etapa; vira cartão se o tech-lead não a cobrir em outra.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Espera do CI da develop antes e depois do merge (`R-FLUXO`) | test_espera_o_ci_do_topo_antes_e_o_do_merge_depois, test_ci_do_topo_em_andamento_espera_e_segue | pendente espera; verde segue | passou |
| Develop vermelha, cancelada, sem execução ou ilegível para sem mesclar | test_develop_vermelha_antes_do_merge_para_sem_mesclar, test_topo_cancelado_nao_prova_e_para, test_sem_execucao_no_prazo_para_sem_mesclar, test_leitura_do_ci_que_falha_para_sem_mesclar, test_topo_ilegivel_ou_vazio_no_6b_para_sem_mesclar | vazio, prazo esgotado, leitura falha | passou |
| CI não verde depois do merge sai 5, com reversão só no vermelho | test_ci_vermelho_no_merge_sai_com_5_e_imprime_a_reversao, test_ci_cancelado_no_merge_sai_com_5_sem_reversao, test_sem_limpar_com_ci_vermelho_no_merge_sai_com_5 | vermelho e cancelado juntos contam como vermelho | passou |
| `--espera-ci` na faixa 0 a 7200, opção sem valor | test_espera_ci_fora_da_faixa_para_antes_do_passo_1, test_opcao_sem_valor_e_pedido_repetido_param_antes_do_passo_1 | mínimo, máximo, fora do limite | passou |
| Lote de 2 ou 3, em ordem, um só CI no último merge (diretriz 26) | test_sem_arquivo_em_comum_fecha_em_ordem_e_espera_um_ci_so, test_quantidade_e_forma_dos_itens | 1 e 4 itens, forma inválida, branch repetida | passou |
| Arquivo em comum recusa o lote sem mesclar | test_arquivo_em_comum_para_sem_mesclar_nenhum, test_branch_ausente_para_no_l1, test_diff_ilegivel_para_no_l1 | interseção de 1 arquivo | passou |
| Lote vermelho reverte o lote inteiro; item que para encerra o lote | test_lote_vermelho_imprime_a_reversao_do_lote_inteiro_e_sai_com_5, test_item_que_para_encerra_o_lote_e_o_ci_dos_mesclados_e_acompanhado, test_develop_vermelha_antes_do_lote_para_sem_item, test_item_com_limpeza_pendente_da_codigo_3_ao_lote | ordem inversa da reversão; código 3 | passou |
| `--lote` e `--item-de-lote` sem opções alheias | test_lote_recusa_opcao_de_item, test_item_de_lote_nao_espera_o_ci_da_develop, test_item_real_e_o_proprio_script | opção de item recusada | passou |
| Promoção pelo sha da marca, nunca o topo (diretriz 27) | test_item_mesclado_depois_da_marca_nao_entra_na_promocao, test_promocao_completa_apaga_o_ramo, test_marca_fora_da_develop_para, test_marca_que_nao_existe_aqui_para, test_sha_fora_da_forma_para_antes_de_tudo, test_marca_sem_versao_para, test_marca_nao_promovivel_para | sha de 39 e 41 hex, fora da develop | passou |
| Retomada após queda (ramo, PR aberto, MERGED) | test_retomada_com_o_pr_ja_mesclado_nao_cria_nem_mescla, test_retomada_com_o_pr_aberto_reusa, test_ramo_com_outro_commit_para, test_pr_aberto_com_outra_base_para, test_dois_prs_abertos_param, test_pr_criado_sem_numero_na_saida_para_para_retomar | 0, 1 e 2 PRs abertos | passou |
| Promoção só vale MERGED na homolog com o head da marca; CI da marca | test_auto_merge_armado_espera_o_merged_e_fecha, test_merge_em_outra_base_nao_e_sucesso, test_pr_que_nao_mescla_no_prazo_para_para_retomar, test_ci_vermelho_na_marca_para_e_cancelado_segue | prazo do merge | passou |
| Dry-run descreve todos os passos | test_dry_run_mostra_as_duas_esperas, test_dry_run_do_lote, test_dry_run_da_promocao, test_promover_recusa_opcao_de_item | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar_lote tests.test_fechar tests.test_fechar_log_check tests.test_fechar_medir tests.test_fechar_orfao`: Ran 187 tests, OK (973 s, máquina disputada).
- Vermelho antes do verde, à mão (o `--vermelho` demoraria acima do prazo): `bin/forge-fechar` da base `f4b0c2ae` sobre o head, `python3 -m unittest tests.test_fechar_lote`: Ran 50 tests, FAILED (failures=65, errors=1). Os testes novos caem sem a implementação.
- Mutação: `bin/forge-mutante --processos 4` nas 8 specs (`tests/mutantes/v047-integracao-em-lote*.json`, 64 mutantes, `pedido=v047`, `rev=c6b0b788c281`): 64 `morreu`, nenhum sobrevivente, nenhum equivalente, rc=0.
- `forge-mutante --cobertura --base f4b0c2ae`: `não coberto: bin/forge-fechar` (shell não é lido pela ferramenta). Conferi à mão a lista contra o diff: cada guarda nova (L1 a L3, P1 a P6, 6b, passo 8, faixa, recusa de opção, `mesclar_auto`, `ci_do_item`) tem mutante nas specs.
- Segurança e review já commitados na branch depois do head testado (`41d7667a`, só docs); não alteram o código revisado.

## Revalidação no head 13cb874d (delta c6b0b788..13cb874d)
Delta lido por `forge-check parecer delta`: `ci.yml` (degrau pela catraca), `bin/forge-fechar` (`FORGE_FECHAR_LOTE_PAI`, topo do lote lido no servidor, `par_de_promocao`, P5 só sem fork), `tests/catraca.py` (tabela única `PROMOCOES`, modo `degrau`), `scripts/arvore-testada.py`, 4 specs de mutantes e testes. Cobre o A1 do review e do devops (promocao/X.Y.Z -> homolog) e o A2 da segurança; o A1 do parecer anterior segue recomendado (fora do escopo). Sem PR aberto: sem check-run `bateria` para citar.

| Critério (R-FLUXO) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| promocao/X.Y.Z -> homolog aceito só com head na develop do servidor | tests.test_catraca_promocao | sha fora da develop, sha não texto, subclasse de str, versão fora de X.Y.Z | passou |
| `degrau` recusa fork e par fora da tabela (melhoria/x -> main) | tests.test_catraca_promocao, `catraca.py --modo degrau` à mão | repositório do head diferente | passou (recusa com R-FLUXO) |
| arvore-testada usa a mesma tabela | tests.test_arvore_testada | par do PR | passou |
| `--item-de-lote` só no `--lote`; topo do lote; P5 sem fork | tests.test_fechar_lote | marca do pai ausente, PR de fork | passou |

- `python3 -m unittest tests.test_catraca_promocao tests.test_arvore_testada`: Ran 32, OK. `tests.test_fechar_lote`: Ran 57, OK (77 s). `tests.test_fechar`: Ran 99, OK.
- Vermelho antes do verde, à mão (`forge-testes --vermelho` estourou 590 s, sem veredito, não vale): `bin/forge-fechar`, `tests/catraca.py` e `scripts/arvore-testada.py` de `c6b0b788` sob os testes do head: test_catraca_promocao+test_arvore_testada Ran 32, FAILED (failures=1, errors=27); test_fechar_lote Ran 57, FAILED (failures=31).
- Mutação: `forge-mutante --processos 4` nas specs `-9`, `-10`, `-11`, `-4` (`pedido=v047`, `rev=13cb874d23ef`): todos `morreu`, nenhum sobrevivente, rc=0. `est-m7-verificador-decisao.json` (pedido versao-040, editada no diff): M1 a M8 `morreu`, rc=0.
- `forge-mutante --cobertura --base c6b0b788`: `ci.yml` e `bin/forge-fechar` `não coberto` (não Python); conferi à mão: cada guarda nova do delta (`FORGE_FECHAR_LOTE_PAI`, `topo_lote`, `par_de_promocao`, filtro `isCrossRepository`) tem mutante (IL-M65 a M71); as condições Python de `catraca.py` e `arvore-testada.py` saem `coberta`.
- Remoto avançou em `2d4c90f5` (só `docs/devops`); trazido por merge, sem efeito no código.
