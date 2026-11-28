---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: 64183ee2507ebfb92ed62ea70a45cd1abf16a826
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA delta: v048 dono dos pesos (#959, classe C), volta 1 (ca3c07bb..64183ee2)

- ci: 64183ee2507ebfb92ed62ea70a45cd1abf16a826 verde

Escopo: só o delta. O A1 do review (`pull_requests` vazio na API real) está corrigido: `pr_unico_valido` acha o PR por `commits/<sha>/pulls`, com sha validado por `[0-9a-f]{40}` antes de virar caminho.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PR achado pelo sha, com `pull_requests` vazio | test_o_pr_e_achado_pelo_sha_mesmo_com_pull_requests_vazio_na_execucao | execução da API real (lista vazia) | passou; vermelho na base (asserção); M5 morto |
| Exatamente um PR válido no sha | test_dois_prs_validos_no_mesmo_sha_descartam_a_execucao_e_o_de_fork_no_sha_nao_conta | 0, 1 e 2 válidos; fork, não mesclado, outra base, outro sha | passou; vermelho na base; M14 morto |
| Guardas de fork e de sha do PR, cada uma sozinha | test_guardas_de_fork_e_de_sha_do_pr_valem_cada_uma_sozinha | fork, sha diferente, sha vazio | passou; M15 M16 mortos |
| Resposta de `commits/<sha>/pulls` que não é lista de PRs | test_resposta_de_prs_que_nao_e_lista_de_prs_validos_nao_entra | objeto, vazia, nulo, texto, só não-objetos | passou; vermelho na base; M9 morto |
| Execução malformada e sha ruim nunca viram caminho | test_execucao_de_pr_malformada_nao_quebra_nem_entra | não objeto, sem sha, tipo errado, curto, `../`, maiúsculas | passou; M7 M8 mortos (passa na base por natureza: a base também descartava) |
| Falso de API na forma real | test_corpus_da_api_real_mostra_pull_requests_vazio_e_o_pr_pela_rota_do_commit | S1: 97 de 100 execuções com `pull_requests` vazio; S2: PR 958 pela rota do commit | passou (dado, passa na base); `api()` e os demais testes usam `pull_requests=[]` e sha de 40 caracteres |
| Teto 2x limite e laço de PR | test_teto_de_execucoes_conta_as_de_pr_ate_2_vezes_o_limite | máximo | passou; vermelho na base; M6 M17 mortos |

## Cenários e resultado real
- `python3 -m unittest tests.test_pesos_do_ci`: 29 testes, OK.
- Vermelho (`forge-testes --vermelho ca3c07bb --modulos test_pesos_do_ci`): `vermelho: base=ca3c07bb5c4e head=64183ee2507e`; prova (asserção)=5, não prova (passa na base)=24 (negativos, corpus de dados e testes antigos, mortos pelos mutantes).
- Mutantes (`bin/forge-mutante tests/mutantes/v048-dono-pesos-1.json tests/mutantes/v048-dono-pesos-2.json --processos 4`, `rev=64183ee2507e`): M1 a M17 `morreu`, nenhum equivalente, nenhum sobrevivente.
- Cobertura (`--cobertura --base ca3c07bb`): linhas 80, 83 e 163 `coberta` (M7 M8, M9 M14, M17); apagadas só as duas guardas antigas de `pull_requests`; sem condição mudada sem mutante.
- Não verificado: leitura real da API (só dublê com corpus gravado, R-CUSTO); o corpus é fotografia de 2026-11-28.
- O A1 (recomendado) da rodada anterior, sobre o vermelho dos testes antigos, não se aplica mais ao delta: os testes novos provam por asserção.
