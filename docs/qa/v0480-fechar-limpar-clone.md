---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 5ff5fb4cf68646f8a09fc909df5bc927b9844e1c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA · conserto do fechamento, --limpar de clone e recusa da integração (E132.11 e E132.15, PR #831)

Head 5ff5fb4c, base 0ed441e9. Sem suíte local: a bateria é o check-run `bateria` do CI do mesmo sha; aqui, só os módulos tocados, o vermelho e os mutantes.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E132.6 clone com HEAD ancestral do head mesclado é apagado | `test_head_ancestral_do_mesclado_e_apagado` | HEAD atrás do mesclado | passou |
| E132.6/E132.7 commit fora das refs velhas do clone, que a origin alcança, não segura o clone | `test_commit_que_a_origin_tem_com_ref_velha_no_clone_e_apagado` | ref remota velha, tag local | passou |
| Leitura da origin que falha deixa o clone | `test_leitura_da_origin_que_falha_deixa_o_clone` | rede fora | passou |
| `--limpar` recusa clone com commit próprio, não enviado ou não mesclado | `LimparClones.test_commit_nao_enviado_em_outra_branch_fica`, `test_commit_enviado_e_nao_mesclado_fica`, `test_commit_so_em_tag_local_fica` | commit só local | passou |
| Campo `clone=` sempre na linha (`nenhum` sem clone) | `test_sem_clone_o_campo_sai_nenhum` | zero clones | passou |
| E134.2 recusa da branch de integração fora de locale UTF-8 | `test_branch_de_integracao_e_recusada_fora_de_locale_utf8` | locale sem UTF-8 | passou |
| `--principal` vazio, com `--promover` e com `--limpar` é erro de uso | `test_principal_vazio_e_erro_de_uso`, `test_promover_recusa_principal`, `test_limpar_recusa_principal` | combinação proibida | passou |
| Busca de pareceres por metades (A1 do review E132.2) | `test_sha_ausente_entre_muitos_busca_por_metades` | 15 sha com 1 ausente | passou |
| E132.15 (A1 do QA anterior): a busca da origin inclui os heads mesclados | `test_head_mesclado_que_esta_copia_nao_le_e_buscado_e_o_clone_ancestral_sai` | head mesclado ausente nesta cópia, branch já fora da origin | passou |

## Revalidação por delta (head 5ff5fb4c, volta E132.13)
Intervalo 7ba9f0ba..5ff5fb4c no domínio: `bin/forge-fechar` (renomeia `sem` para `sem_busca`, lógica igual), spec de mutantes (M13), `test_fechar_limpar_clone.py` (teste novo) e `test_fechar_config.py` (só o nome de um teste). O achado A1 do parecer anterior está resolvido.

- Módulos tocados: `test_fechar_limpar_clone` (5) e `test_fechar_config` (7), todos OK.
- Vermelho: `forge-testes --vermelho 7ba9f0ba --modulos test_fechar_limpar_clone,test_fechar_config` saiu com `não prova (passa na base)=12` e `nenhum teste prova a mudança`. É o esperado: a guarda já existia na base 7ba9f0ba, e o teste novo fecha a lacuna do mutante. A prova de que ele cai sem a guarda é o M13, que tira `$merged_heads` da busca e só esse teste mata.
- `bin/forge-mutante` nas duas specs (`--processos 3`, rc 0, `rev=5ff5fb4cf686`): M1 a M13 todos `morreu`, incluindo `M13 · morreu · bin/forge-fechar:610`. O mutante X1 do parecer anterior virou o M13.
- Árvore limpa depois das rodadas.
