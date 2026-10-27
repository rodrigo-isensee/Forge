---
tipo: qa
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: a35a18171fd920286e73c511dfe5c5d0cfb897f6
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-fechar2

Revalidação 5 (voltas 4 e 5: SC2015 em bin/forge-fechar:80, :177, :337, :750 reescrito para `if ! { A && B; }; then C; fi`, teste de fonte `test_fechar_sem_a_e_b_ou_c_solto`, spec lote-fechar2-4 S1..S4) sobre o head a35a181 (base b6eb84f). Delta de código só em bin/forge-fechar (4 linhas) e testes; o resto do parecer anterior (5c6684d: E1, E2, laço :526, cadeia :530) segue valendo, pois :520-540 não mudou.

## Achados
- A1 (bloqueante) bin/forge-fechar:177 · guarda reescrita sem teste do ramo de falha: trocada por `:` sobrevive a toda a suíte do lote; nada prova que pasta do log não-diretório é recusada
- A2 (bloqueante) bin/forge-fechar:337 · mesma classe: sem a linha (`continue` dos checks que não são catraca) todos os testes passam; nenhum teste de comportamento prova que check de outro nome ou run `?` é pulado
- A3 (bloqueante) bin/forge-fechar:750 · mesma classe: sem a guarda "MERGED sem commit de merge" todos os testes passam; nenhum teste prova a recusa com pr_merge vazio ou `-`
- A4 (recomendado) bin/forge-fechar:539 · plural da mensagem sobrevive (linha anterior ao lote); vale teste com 2 commits na base se a mensagem for contrato
- A5 (recomendado) bin/forge-fechar:521 · `|| die` de :521/:522/:524 sobrevivem; linhas anteriores ao lote

## Correção pedida
Um teste de comportamento por linha, no mesmo passe: :177 pasta do log não-diretório recusada; :337 check com nome diferente de catraca (ou run `?`) pulado; :750 PR MERGED com pr_merge vazio e com `-` para no passo 6; com mutante que remova a guarda (S3 e S4 hoje só trocam a forma).

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| SC2015 fora de bin/forge-fechar | test_fechar_sem_a_e_b_ou_c_solto; test_shellcheck_fechar_passa_limpo | forma A && B \|\| C | passou (S1..S4 morreram; shellcheck rc 0) |
| :80 faixa não numérica recusada | test_teto_do_delete_fora_da_faixa_... (v='x'); test_shellcheck_fechar_passa_limpo | valor não inteiro | passou (mutação à mão derrubou 2 testes) |
| :177 pasta do log não-diretório | nenhum de comportamento | n/a | SEM TESTE (A1) |
| :337 pula check não catraca | nenhum de comportamento | n/a | SEM TESTE (A2) |
| :750 MERGED sem commit de merge | nenhum de comportamento | n/a | SEM TESTE (A3) |
| E1, E2, 2b (:520-540) | ver parecer 5c6684d (inalterado) | idem | passou nos 174+ testes e nas specs 1..3 |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar tests.test_fechar_orfao tests.test_ci_local tests.test_fechar_base_andou tests.test_pre_push_shellcheck`: Ran 178 tests, OK. `shellcheck bin/forge-fechar`: rc 0.
- `bin/forge-mutante` (uma spec por chamada), todas rc 0: lote-fechar2 M1..M8 morreram; lote-fechar2-2 M1..M5, Y1, Y2, Y4 morreram; lote-fechar2-3 M1, M2 morreram; lote-fechar2-4 S1 (:337), S2 (:80), S3 (:177), S4 (:750) morreram, todos pelo teste de fonte.
- Mutação à mão (guarda trocada por `:`, rodando test_fechar, test_fechar_orfao, test_fechar_base_andou; 123 testes): :80 morreu (2 falhas); :177 SOBREVIVEU (OK); :337 SOBREVIVEU (OK); :750 SOBREVIVEU (OK). Os mutantes S1..S4 mudam só a forma e morrem pelo teste de fonte, o que não prova o comportamento.
- Conferência da lista contra o diff: as quatro linhas mudadas têm mutante (S1..S4), mas S1, S3, S4 não exercem o ramo de falha; por isso A1..A3.
- Vermelho: sem teste de comportamento novo; o teste de fonte falha nas formas S1..S4 (provado pela spec).
- PA-7 (achados-recorrentes): sem itens, nada a conferir.

## Riscos
A reescrita é equivalente por leitura, mas a equivalência das linhas :177, :337 e :750 não tem teste que a proteja (inclusive a recusa de MERGED sem commit de merge, guarda do passo 6).
