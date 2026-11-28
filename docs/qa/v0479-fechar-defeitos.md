---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-defeitos
commit: e6c1fe8a2e054a09261612232fcb6fd4bb97f780
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 (v0479-fechar-defeitos, E75.5)

Três defeitos do `bin/forge-fechar`: 1c antes do 2b (merge da base sobre o head), 6a (base local velha busca e segue) e check-runs do head verdes antes do merge direto (`--armar` fica como antes). Só os módulos tocados rodaram local; a suíte inteira é do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1c confere o merge da base com o head | test_1c_base_andou_sem_conflito_confere_o_merge_da_base_com_o_head, test_1c_branch_com_versao_velha_e_base_com_a_nova_passa_pelo_merge | base já ancestral do head | passou |
| 1c recusa nomeia a árvore da branch | test_1c_que_recusa_diz_que_e_a_arvore_da_branch_e_nao_a_develop | n/a | passou |
| 6a base local velha busca e segue; conflito ou falha da busca para | test_6a_base_local_velha_busca_a_base_e_segue_sem_conflito, ..._com_conflito_na_base_buscada_para, test_6a_busca_da_base_que_falha_para_e_pede_o_fetch | busca falha | passou |
| Check obrigatório do head verde antes do merge | test_check_runs_verdes_leem_o_head_conferido_e_mesclam, test_exigido_vermelho_rodando_ou_ausente_recusa_o_merge, test_duplicata_do_exigido_precisa_de_todas_verdes, test_nome_mais_longo_verde_nao_vale_pelo_exigido, test_leitura_dos_check_runs_que_falha_para | ausente, rodando, duplicata, prefixo de nome, leitura falha | passou |

## Execução (head 5d383ebf)
- test_fechar: 111 testes OK (1 pulado, já existente); test_forge_fechar: 34 OK; test_fechar_base_andou: 43 OK; test_fechar_checks_do_head: 6 OK.
- forge-mutante, uma chamada por spec, rc 0 nas três: v0478-fechar-1c (F1C-M1..M3 morreram), v0478-fechar-6a (F6A-M1..M3 morreram), v0478-fechar-checks (FCK-M1..M6 morreram). Os 12 mutantes cobrem as linhas de guarda do diff em `bin/forge-fechar`.
- Vermelho (saída abaixo): 11 testes provam, nenhum cai no HEAD, rc 0.

```
vermelho: base=65de25ce7394 head=5d383ebfa624 módulos=test_fechar,test_forge_fechar,test_fechar_base_andou,test_fechar_checks_do_head (restrito por --modulos)
test_fechar_base_andou: 3 testes 1c e 3 testes 6a · H=ok · B=falha · prova (asserção)
test_fechar_checks_do_head: 5 testes · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=182; prova (asserção)=11; pulado=1
```

## Revalidação (head e6c1fe8a, delta desde 5d383ebf)
Delta lido por `forge-check parecer delta`: `bin/forge-fechar` (execução mais recente por check; `--armar` recusa falha já terminada), testes `test_fechar_checks_do_head`, `test_fechar_base_andou`, `test_fechar`, specs de mutantes. Critério novo: com `--armar`, check rodando ou ausente arma; terminado fora de success recusa; catraca velha cancelled ao lado da nova verde mescla.
- test_fechar_checks_do_head: 8 testes OK; test_fechar_base_andou: 44 testes OK (módulos tocados; sem suíte inteira, que é do CI do PR).
- forge-mutante, uma chamada por spec, sem sobrevivente: v0478-fechar-checks (FCK-M1..M8 morreram), v0478-fechar-checks-2 (FCK-M9 morreu, por erro do teste declarado), v0478-fechar-6a (F6A-M1..M4 morreram). O rc impresso no laço foi o do `tail`, não o do `forge-mutante`; o veredito é a ausência de linha `sobreviveu`.
- Vermelho com `--modulos test_fechar,test_fechar_base_andou,test_fechar_checks_do_head`, base 65de25ce: rc 0; 15 testes provam (os 8 de checks, em B=falha, e 7 em test_fechar_base_andou), nenhum cai no HEAD; contagem: não prova (passa na base)=147; prova (asserção)=15; pulado=1.
