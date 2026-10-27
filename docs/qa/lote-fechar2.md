---
tipo: qa
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 5c6684ddd222f18cd82c055f0602e23340720d98
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-fechar2

Revalidação 4 (decisão B do dono de 2026-10-27) sobre o head 5c6684d (base b6eb84f). Plano antecipado não se aplica (correção sem especificação nova); obrigações: E1 LSREMOTE-EXATO, E2 SHELLCHECK-FECHAR, laço :526 (A1 de 4b4d286) e cadeia :530 (A1 de 4451985). Delta 7c926e4..5c6684d: só tests/ (sort falso, 3 testes, specs lote-fechar2-2 e -3); bin/ não mudou.

## Achados
- A1 (recomendado) bin/forge-fechar:539 · o plural da mensagem (`echo s` virado `echo`) sobrevive à varredura: linha fora das alterações do lote (autoria aaba5605), só texto; vale um teste com 2 commits na base se a mensagem for contrato
- A2 (recomendado) bin/forge-fechar:521 · `|| die` de :521/:522 (merge-base falho ou vazio) e de :524 (mktemp) sobrevivem; linhas anteriores ao lote (aaba5605), fora do diff e da varredura exigida; vira cartão, não devolve a entrega

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 isca com o mesmo fim (passo 2 e limpeza) | test_lsremote_exato_isca_com_o_mesmo_fim_nao_engana_o_passo_2_nem_a_limpeza | coluna 2 igual ao nome inteiro | passou (M1 morreu) |
| E1 isca na base (2b) e pós-delete | test_lsremote_exato_isca_da_base_...; ..._conferencia_depois_do_delete_que_falhou | idem | passou |
| E1 leitura que falha não vira ausente | test_fechar_orfao...conferencia_da_remota_falhando...; test_ls_remote_da_branch_que_falha_... | falha da leitura | passou (M2, M6 morreram) |
| Segurança: coluna 1 é sha | test_coluna_1_que_nao_e_sha_e_leitura_que_falhou_e_nao_valor | não hex, curto, 40 não hex | passou (M7, M8 morreram) |
| E2 shellcheck na lista do CI | test_shellcheck_fechar_esta_na_lista_do_ci | lista do CI | passou (M3 morreu) |
| 2b vários pontos de partida (contagem :538) | test_varios_pontos_de_partida_entram_todos_na_contagem_da_base | merge-base múltiplo | passou (M4 spec 1, M1 spec 3 morreram) |
| 2b contagem que falha (:538) | test_contagem_de_commits_da_base_que_falha_para_no_passo_2b | falha do rev-list | passou (M1 spec 3 morreu) |
| 2b vários pontos de partida (diffs, laço :526) | test_arquivo_em_comum_so_no_diff_do_segundo_ponto_de_partida_para_e_lista_os_dois | arquivo só no diff do 2.º ponto | passou (M3 spec 2 morreu) |
| 2b arquivo em comum (:533, :536) | test_c5_base_que_andou_com_arquivo_em_comum_para_antes_do_pr | lista de comuns não vazia | passou (M4, M5 spec 2 morreram) |
| 2b comm que falha (:531) | test_comm_que_falha_para_no_passo_2b_sem_abrir_pr | falha de comm | passou (M5 spec 1, Y1 morreram) |
| 2b sort que falha (:530) | test_sort_da_lista_da_base_que_falha_...; test_sort_da_lista_da_branch_que_falha_... | sort falho de cada lado | passou (Y2, Y4 morreram) |
| 2b diffs que falham | test_diff_da_base/da_branch_que_falha_sozinho_... | falha de diff | passou (M1, M2 spec 2 morreram) |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar tests.test_fechar_orfao tests.test_ci_local tests.test_fechar_base_andou`: Ran 174 tests, OK. `shellcheck bin/forge-fechar`: rc 0.
- `bin/forge-mutante` (uma spec por vez; aceita uma só), todas rc 0:
  - lote-fechar2.json: M1..M8 morreram (forge-fechar:141, 140, ci.yml:238, :538, :531, :600, :141, :141).
  - lote-fechar2-2.json: M1 (:527), M2 (:528), M3 (:526), M4 (:533), M5 (:536), Y1, Y2, Y4 (:530) morreram.
  - lote-fechar2-3.json: M1 (:538), M2 (:523) morreram.
- A1 do parecer 4451985 (cadeia :530; Y1, Y2, Y4): fechado, os três morrem contra o head, com teste de sort falso por lado.
- Varredura de :520-540 (script próprio, mutantes em cópia, rodando tests.test_fechar_base_andou e tests.test_fechar_orfao; 41 mutantes, um ou mais por linha com código, os de :520/:532/:537/:540 são `fi`/`}` sem comportamento): linhas mudadas pelo lote (:523, :526, :530, :531, :538) e as demais com guarda real (:527, :528, :533, :535 read/printf/redirecionamento, :536): todos morreram, exceto equivalentes. Sobreviventes: `: > a`/`: > b` (:525) e `>>` virado `>>>`-sem-efeito em :530 (`> comuns` vs `>> comuns` em arquivo novo) e a troca dos argumentos de `comm -12` (simétrico): equivalentes. Sobreviventes em linhas que o lote não mudou: :521/:522/:524 (die), :534 (cabeçalho em stderr), :535 `IFS=` (espaço de borda no nome impresso), :539 plural; ver A1 e A2 (recomendados).
- Conferência da lista contra o diff: toda linha de guarda mudada (remoto_exato, :459/:472, :523, :526, :530-532, :538, :600) tem mutante declarado; nenhuma sem mutante.
- Vermelho: os testes novos protegem código que já existe no head (delta só em tests/); a prova é por mutante, com a saída de `forge-mutante` acima; `forge-testes --vermelho` não se aplica.
- PA-7 (achados-recorrentes): sem itens, nada a conferir.

## Riscos
Sobreviventes só em linhas anteriores ao lote (mensagens e mktemp), sem efeito na decisão de arquivo em comum.
