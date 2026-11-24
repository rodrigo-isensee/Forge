---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d4-corte-contador
commit: c9b5d269018c90f24d6414aa5e523adb88fbd41e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-d4-corte-contador (E174.4, PR #869)

Sem especificação de UX nem contrato de API: as obrigações são a ordem do dono de 24/11 (corte ao chegar a 20 itens) e `R-MAIN` (o merge da main é só do dono), lidas em `docs/fechamento-integrador.md` e no cabeçalho do `bin/forge-fechar`.

## Revalidação (delta bf598d2f..c9b5d269, escopo incremental)
O A1 do parecer anterior (main à frente da homolog) foi corrigido: guarda no V1 (bin/forge-fechar:1490) e test_main_a_frente_da_homolog_para. Os achados A1 e A2 do review (SC2015 e README.md sintético) estão corrigidos; o A3 do review (PR fechado sem mesclar) é do review e segue recomendado, fora deste parecer.
- forge-check parecer delta: base bf598d2f872d; domínio com bin/forge-fechar, doc, specs 2 e 5, test_fechar_corte.py e test_reval_delta.py; reteste só disso.
- test_fechar_corte (18 testes, com -I): OK. Os dois testes que o review viu vermelhos (test_fechar_sem_a_e_b_ou_c_solto e test_caminho_de_texto_so_e_citado_como_a_lista_conhece): OK.
- Vermelho antes do verde (forge-testes --vermelho aabc476c5dba --modulos test_fechar_corte,test_fechar_laco): contagem: não prova (passa na base)=11; prova (asserção)=18. O teste novo test_main_a_frente_da_homolog_para entra nos que provam.
- Mutação (forge-mutante --base bf598d2f872d --processos 4, 5 specs): rc 0, 36 mutantes morreu, nenhum sobrevivente; M35 (:1484), M36 (:1490) e M37 (:1491) cobrem as 2 guardas novas; conferi as linhas de guarda do delta contra a lista.
- sem_merge() (R-MAIN) nos testes de PR da main: nenhuma chamada pr merge nem --auto.
- shellcheck não existe nesta máquina: o SC2015 foi conferido pelo teste estrutural do repositório; o CI do mesmo sha segue pendente na hora da leitura (só catraca verde), então este parecer não o cita como verde.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Abaixo do teto nada faz | test_abaixo_do_teto_nada_faz | N = teto - 1 | passou |
| No teto grava a marca e abre PR em rascunho para a develop | test_no_teto_grava_a_marca_e_abre_o_pr_em_rascunho | N = teto; worktree removida | passou |
| Ramo da marca já no origin: retoma sem repetir | test_ramo_da_marca_ja_no_origin_nada_faz | ramo existente | passou |
| Marca que não grava ou PR que não abre para com erro | test_marca_que_nao_grava_para_sem_pr, test_pr_da_marca_que_nao_abre_para | falha de changelog e de gh | passou |
| Marca mesclada promove (rc 0 e 3) e abre o PR da main | test_marca_mesclada_promove_e_abre_o_pr_da_main | rc 0 e 3 | passou |
| Promoção que para sai com o código dela | test_promocao_que_para_sai_com_o_codigo_dela | rc 1 e 5 | passou |
| PR da main aberto: espera o dono (R-MAIN) | test_pr_da_main_aberto_espera_o_dono | PR aberto | passou |
| PR da main aberto uma vez só; falha ao abrir para | test_homolog_promovida_abre_so_o_pr_da_main_e_uma_vez, test_pr_da_main_que_nao_abre_para | repetição | passou |
| Homolog à frente da develop para | test_homolog_a_frente_da_develop_para | ordem de versões | passou |
| Leitura que falha, versão ilegível, ramo ausente, contador com erro ou sem contagem param | test_leituras_que_falham_param, test_versao_ilegivel_ou_ramo_ausente_param, test_contador_que_falha_ou_sem_contagem | vazio, ilegível | passou |
| --dry-run só lê | test_dry_run_le_e_nao_age | n/a | passou |
| Recusa o que não é do corte | test_recusa_o_que_nao_e_do_corte | opção estranha | passou |
| Fluxo do item intacto | test_sem_corte_o_fluxo_do_item_segue | n/a | passou (guarda de regressão, não prova na base) |
| --laco sem pendência roda o --corte; pendência não corta | test_volta_sem_pendencia_roda_o_corte_no_fim | rc 0, 1, 3 e dry-run | passou |

## Cenários e resultado real
Provas locais no head bf598d2f (cópia /root/.forge-contrib/wt/v0480-d4-corte-contador-qa). Suíte inteira: CI do PR; na hora da leitura só `bateria (passos)`, `catraca` e `instalação` estavam verdes, as suítes 1 a 5/5 pendentes e `bateria (pareceres)` vermelha pelos pareceres ainda faltantes; este parecer não cita CI como verde.

Vermelho antes do verde (`forge-testes --vermelho aabc476c5dba --modulos test_fechar_corte,test_fechar_laco`):
```
vermelho: base=aabc476c5dba head=bf598d2f872d módulos=test_fechar_corte,test_fechar_laco (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0480-d4-corte-contador.md, docs/fechamento-integrador.md, tests/pesos-d4.json
contagem: não prova (passa na base)=11; prova (asserção)=17
```
Os 16 testes novos de comportamento (15 do `Corte` e o do laço) provam: falham na base por asserção. Os 11 que passam na base são os de regressão do `--laco` e `test_sem_corte_o_fluxo_do_item_segue`, como esperado.

Mutação (`bin/forge-mutante --processos 4` sobre as 5 specs `v0480-d4-corte-contador*.json`): rc=0, 33 mutantes (M1 a M34, sem M7), todos `morreu` (bin/forge-fechar:185 a 1539). `--cobertura --base`: `não coberto: bin/forge-fechar` (shell, fora do alcance da checagem; conferi a lista de 33 contra o diff: recusa, laço, V1 a V5) e `spec editada` nas duas specs do D1 (trecho `de` reajustado por causa do deslocamento do código).

Sem mutante sobrevivente, sem teste com `skip`.
