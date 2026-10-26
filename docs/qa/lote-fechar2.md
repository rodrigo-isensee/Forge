---
tipo: qa
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 7c926e42a3a6b333c46bf4967dadac9e18724f5b
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-fechar2

Revalidação da volta 2 (decisão B do dono) sobre o head 7c926e4 (base b6eb84f). Plano antecipado não se aplica (correção sem especificação nova); obrigações: E1 LSREMOTE-EXATO, E2 SHELLCHECK-FECHAR e o A1 do parecer 4b4d286 (laço :526 sobre todos os pontos de partida).

## Achados
- A1 (bloqueante) tests/mutantes/lote-fechar2.json:1 · classe lista de mutantes incompleta (3.ª reincidência): a linha de guarda mudada bin/forge-fechar:530 (cadeia `sort a && sort b && comm` dentro do `if ! { ...; }`) só tem o mutante da mensagem do die (M5, :531); os mutantes QA Y1 (`&&` antes do comm virado `;`), Y2 (`&&` depois do sort b virado `;`) e Y4 (`&&` depois do sort a virado `;`) sobrevivem nos 17 testes de test_fechar_base_andou: falha de `sort` fica mascarada, a lista vazia do lado que falhou vira "sem arquivo em comum" e a entrega segue sem a conferência (o único teste injeta só falha de `comm`, via comm_falha). Reparo: mutante(s) e teste com `sort` falso que falha (um por lado) na spec

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 isca com o mesmo fim (passo 2 e limpeza) | test_lsremote_exato_isca_com_o_mesmo_fim_nao_engana_o_passo_2_nem_a_limpeza | coluna 2 igual ao nome inteiro | passou (M1 morreu) |
| E1 isca na base (2b) e pós-delete | test_lsremote_exato_isca_da_base_...; ..._conferencia_depois_do_delete_que_falhou | idem | passou |
| E1 leitura que falha não vira ausente | test_fechar_orfao...conferencia_da_remota_falhando...; test_ls_remote_da_branch_que_falha_... | falha da leitura | passou (M2, M6 morreram) |
| Segurança: coluna 1 é sha | test_coluna_1_que_nao_e_sha_e_leitura_que_falhou_e_nao_valor | não hex, curto, 40 não hex | passou (M7, M8 morreram) |
| E2 shellcheck na lista do CI | test_shellcheck_fechar_esta_na_lista_do_ci | lista do CI | passou (M3 morreu) |
| 2b vários pontos de partida (contagem :538) | test_varios_pontos_de_partida_entram_todos_na_contagem_da_base | merge-base múltiplo | passou (M4 spec 1 morreu) |
| 2b vários pontos de partida (diffs, laço :526) | test_arquivo_em_comum_so_no_diff_do_segundo_ponto_de_partida_para_e_lista_os_dois | arquivo só no diff do 2.º ponto | passou (M3 spec 2 morreu; X5 fechado) |
| 2b arquivo em comum (:533, :536) | test_c5_base_que_andou_com_arquivo_em_comum_para_antes_do_pr | lista de comuns não vazia | passou (M4, M5 spec 2 morreram) |
| 2b comm que falha (:531) | test_comm_que_falha_para_no_passo_2b_sem_abrir_pr | falha de comm | passou (M5 spec 1 morreu) |
| 2b sort que falha (:530) | nenhum | falha de sort de cada lado | SEM TESTE (Y1, Y2, Y4 sobreviveram) |
| 2b diffs que falham | test_diff_da_base/da_branch_que_falha_sozinho_... | falha de diff | passou (M1, M2 spec 2 morreram) |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar tests.test_fechar_orfao tests.test_ci_local tests.test_fechar_base_andou`: Ran 171 tests, OK. `shellcheck bin/forge-fechar`: rc 0.
- `bin/forge-mutante tests/mutantes/lote-fechar2.json` (rc 0): M1 a M8 todos morreram (forge-fechar:141, 140, ci.yml:238, :538, :531, :600, :141, :141).
- `bin/forge-mutante tests/mutantes/lote-fechar2-2.json` (rc 0): M1 morreu (:527), M2 (:528), M3 (:526, o laço só sobre lista_mb[0]), M4 (:533), M5 (:536).
- A1 do parecer 4b4d286 (X5, laço só sobre lista_mb[0]): fechado, morre pelo M3 da spec 2 e pelo teste novo.
- :530 pela primeira spec: o M5 dela só troca o `die` de :531; não mata a cadeia `&&` de :530. Mutantes à mão em cópia (arquivo restaurado, `git status` limpo): Y1 `&& comm` -> `; comm` sobreviveu (17 OK); Y2 `sort b ... &&` -> `;` sobreviveu; Y4 `sort a ... &&` -> `;` sobreviveu; Y3 (`if false && {`) morreu (5 falhas). Falha de sort deixa o arquivo `.s` vazio e comm sai 0: o conflito deixa de ser detectado.
- Conferência da lista contra o diff: guardas mudadas cobertas: remoto_exato, :459/:472, passo 2 (:600), diffs :527/:528, laço :526, comm/die :531, :533, :536, `--not` :538. Sem mutante: a cadeia de `&&` em :530 (Y1, Y2, Y4).
- Vermelho: os testes novos protegem código que já existia no head; a prova é por mutante (acima), com a saída de `forge-mutante` colada; `forge-testes --vermelho` não se aplica, não há mudança de comportamento em bin/ nesta volta (diff 4b4d286..7c926e4 só em tests/).
- PA-7 (achados-recorrentes): sem itens, nada a conferir. Recomendado do review A3 (mapfile bash 4, :522) não bloqueia.

## Riscos
Falha de `sort` no cruzamento do 2b não protegida; o resto das guardas do lote está provado por mutante.
