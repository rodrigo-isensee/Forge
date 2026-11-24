---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 7ba9f0bac3d84e0b231995b8e50778404b0ca179
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · conserto do fechamento, --limpar de clone e recusa da integração (E132.11, PR #831)

Head 7ba9f0ba, base 0ed441e9. Sem suíte local: a bateria é o check-run `bateria` do CI do mesmo sha; aqui, só os módulos tocados, o vermelho e os mutantes.

## Achados
- A1 (bloqueante) bin/forge-fechar:610 · mutante sobrevivente: tirar `$merged_heads` da busca de `origem_atual` mantém 38 testes verdes (`LimparCloneNaoListado` e `LimparClones`). Falta teste do clone ancestral cujo head mesclado esta cópia não lê; declare o mutante na spec e escreva o teste.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E132.6 clone com HEAD ancestral do head mesclado é apagado | `test_head_ancestral_do_mesclado_e_apagado` | HEAD atrás do mesclado | passou |
| E132.6/E132.7 commit fora das refs velhas do clone, que a origin alcança, não segura o clone | `test_commit_que_a_origin_tem_com_ref_velha_no_clone_e_apagado` | ref remota velha, tag local | passou |
| Leitura da origin que falha deixa o clone | `test_leitura_da_origin_que_falha_deixa_o_clone` | rede fora | passou |
| `--limpar` recusa clone com commit próprio, não enviado ou não mesclado | `LimparClones.test_commit_nao_enviado_em_outra_branch_fica`, `test_commit_enviado_e_nao_mesclado_fica`, `test_commit_so_em_tag_local_fica` | commit só local | passou |
| Campo `clone=` sempre na linha (`nenhum` sem clone) | `test_sem_clone_o_campo_sai_nenhum` | zero clones | passou |
| E134.2 recusa da branch de integração em LC_ALL=C, POSIX e C.UTF-8, com e sem `--limpar`, duas grafias da linha | `test_branch_de_integracao_e_recusada_fora_de_locale_utf8` | locale sem UTF-8, caixa alta acentuada | passou |
| `--principal` vazio, com `--promover` e com `--limpar` é erro de uso | `test_principal_vazio_e_erro_de_uso`, `test_promover_recusa_principal`, `test_limpar_recusa_principal` | combinação proibida | passou |
| Busca de pareceres por metades (A1 do review E132.2) | `test_sha_ausente_entre_muitos_busca_por_metades` | 15 sha com 1 ausente, 9 fetches | passou |

## Execução
- `python3 -m unittest` em `test_fechar_limpar_clone` (4), `test_fechar_longas` (5), `test_fechar_busca_pareceres` (12) e `test_forge_fechar` (34): todos OK.
- Vermelho (`forge-testes --vermelho 0ed441e9 --modulos test_fechar_limpar_clone,test_fechar_longas,test_fechar_busca_pareceres`, rc 0), cauda:
```
contagem: não prova (passa na base)=12; prova (asserção)=9
```
  Os 9 que provam incluem `test_branch_de_integracao_e_recusada_fora_de_locale_utf8`, `test_head_ancestral_do_mesclado_e_apagado` e `test_commit_que_a_origin_tem_com_ref_velha_no_clone_e_apagado`. `test_leitura_da_origin_que_falha_deixa_o_clone` passa na base por ser guarda negativa (deixar o clone), morta pelo M6.
- `bin/forge-mutante` nas duas specs (`--processos 3`, rc 0): `rev=7ba9f0bac3d8`, M1 a M12 todos `morreu` (linhas 596, 126, 162, 174, 628, 608, 632, 634, 637, 265, 267, 180).
- `forge-mutante --cobertura --base 0ed441e9`: `não coberto: bin/forge-fechar` (shell, a ferramenta não lista) e `spec editada` em dois arquivos de spec antigos; conferi o diff à mão.
- Mutantes meus, à mão em `bin/forge-fechar` (restaurado, árvore limpa): X2 `clone=${copia_st}` sem `nenhum` morreu (3 falhas); X3 inverter `ancestral=0` para `1` morreu (1 falha); X1 sem `$merged_heads` na busca **sobreviveu** (A1).
