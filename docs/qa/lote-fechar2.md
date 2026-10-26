---
tipo: qa
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 68f100685208dfccefde80f81e43ac5eb6aff224
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-fechar2

Revalidação da volta 1 sobre o head 68f1006 (base b6eb84f). Plano antecipado não se aplica (correção sem especificação nova); obrigações: E1 LSREMOTE-EXATO, E2 SHELLCHECK-FECHAR, mais o A1 do parecer 1473646 (mutantes das guardas do passo 2 e 2b).

## Achados
- A1 (bloqueante) tests/mutantes/lote-fechar2.json:1 · classe lista de mutantes incompleta (reincidência do A1 de 1473646): a linha de guarda mudada bin/forge-fechar:526 (`for mb in "${lista_mb[@]}"`) segue sem mutante e sem teste; o mutante QA X5 (laço só sobre `lista_mb[0]`) sobrevive nos 16 testes de test_fechar_base_andou

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 isca com o mesmo fim (passo 2 e limpeza) | test_lsremote_exato_isca_com_o_mesmo_fim_nao_engana_o_passo_2_nem_a_limpeza | coluna 2 igual ao nome inteiro | passou (M1 morreu) |
| E1 isca na base (2b) e pós-delete | test_lsremote_exato_isca_da_base_..._2b; ..._conferencia_depois_do_delete_que_falhou | idem | passou |
| E1 leitura que falha não vira ausente | test_fechar_orfao...conferencia_da_remota_falhando_fica_pendente... ; test_ls_remote_da_branch_que_falha_para_no_passo_2... | falha da leitura | passou (M2, M6 morreram) |
| Segurança: coluna 1 é sha | test_coluna_1_que_nao_e_sha_e_leitura_que_falhou_e_nao_valor | não hex, curto, 40 não hex | passou (M7, M8 morreram) |
| E2 shellcheck na lista do CI | test_shellcheck_fechar_esta_na_lista_do_ci | lista do CI | passou (M3 morreu) |
| 2b vários pontos de partida (contagem) | test_varios_pontos_de_partida_entram_todos_na_contagem_da_base | merge-base múltiplo | passou (M4 e X3 morreram) |
| 2b vários pontos de partida (diffs, laço :526) | nenhum | merge-base múltiplo | SEM TESTE (X5 sobreviveu) |
| 2b comm/diffs que falham | test_comm_que_falha_...; test_diff_da_base/da_branch_que_falha_sozinho_... | falha de comm e de diff | passou (spec 1 M5; spec 2 M1, M2 morreram) |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar tests.test_fechar_orfao tests.test_ci_local tests.test_fechar_base_andou`: Ran 170 tests, OK. `shellcheck bin/forge-fechar`: rc 0.
- `bin/forge-mutante tests/mutantes/lote-fechar2.json` (rc 0): M1 a M8 todos morreram (forge-fechar:141, 140, ci.yml:238, :538, :531, :600, :141, :141).
- `bin/forge-mutante tests/mutantes/lote-fechar2-2.json` (rc 0): M1 morreu (:527), M2 morreu (:528).
- X3 à mão (`--not "${lista_mb[0]}"`): test_fechar_base_andou FAILED (failures=1), morreu; fecha a parte do A1 anterior (o M4 da spec é o mesmo mutante).
- Conferência da lista contra o diff: guardas mudadas cobertas: remoto_exato (`|| return 1`, `$2 == r`, 40/64, hex), :459 e :472 pelo ajudante, passo 2 (:600), diffs :527/:528, sort/comm :531, `--not` :538. Sem mutante: o laço :526 (X5 sobrevive, o criss_cross do teste não tem diferença de arquivo entre os pontos de partida, então o laço sobre só o primeiro dá o mesmo resultado). Efeito: arquivo tocado dos dois lados desde o segundo ponto de partida não seria detectado. Extra: `mapfile` sem `-t` (X6) morreu (7 falhas).
- Reparo sugerido ao autor (`backend`/agente de desenvolvimento da stack): um mutante `for mb in "${lista_mb[0]}"` na spec e um teste criss-cross em que o arquivo em comum aparece só no diff a partir do segundo ponto de partida.
- Vermelho: os testes novos desta volta provam por mutante (acima); a árvore do autor não foi tocada, mutantes X em cópia do arquivo restaurada (`git status` limpo).
- PA-7 (achados-recorrentes): sem itens, nada a conferir. Recomendado do review A3 (mapfile bash 4, :522) não bloqueia.

## Riscos
Só o laço :526 sem proteção; o resto das guardas do lote está provado por mutante.
