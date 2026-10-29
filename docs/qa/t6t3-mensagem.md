---
tipo: qa
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: e31bf9dc10c1eb8f5693c4b71f3beb44d010f264
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: t6t3-mensagem

Revalidação da volta 1 (0c2ef9c..e31bf9d) sobre os achados do parecer 5b9724f. Lote E1, E2, E4 e E5 (o E3 está no T6T3-RODADA). Sem `CA-n` (pedido técnico): os critérios são os itens do escopo. Base d14a7133.

## Achados
(nenhum aberto)

Fechados: A1 (guarda `etapa and branch and base and base_sha`: um teste com subTest por campo e mutantes M12, M13, M14 mortos), A2 (controle em `--worktree`: teste com a mensagem exata e M15 morto), A3 (um teste por ramo de recusa, com a mensagem afirmada; `--ref`, `--anterior` e `--parecer` num teste só, por subTest). A mudança de comportamento da volta (Desde = linha mais recente do Histórico, também a base fixada pelo dono) tem teste e M16.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 etapa lida do brief | test_a_etapa_sai_da_linha_etapa_do_brief | `--etapa` ausente ou igual | passou (M1 a M4 mortos) |
| E1 `--etapa` diferente recusado | test_etapa_diferente_da_do_brief_e_recusada_com_a_etapa_certa | etapa divergente | passou |
| E2 mensagem de entrega e Desde | test_entrega_traz_tudo_do_arquivo_e_o_desde_da_ultima_conferida | duas conferidas | passou (M5, M10 mortos) |
| E2 Desde: conferida ou base do dono, a mais recente | test_desde_e_a_linha_mais_recente_entre_conferida_e_base_do_dono | três ordens do Histórico | passou (M16) |
| E2 sem base no Histórico, sem linha Desde | test_sem_conferida_no_historico_a_linha_desde_nao_sai | histórico vazio | passou (M11) |
| E2 recusa: sem, relativo, inexistente, com controle em `--worktree` | test_entrega_sem_worktree..., _relativo..., _inexistente..., _controle_no_worktree... | permissão e vazio | passou (M7, M8, M15) |
| E2 recusa: `--ref`, `--anterior`, `--parecer` | test_entrega_com_ref_anterior_ou_parecer_e_recusada | combinação inválida | passou (M9) |
| E2 recusa: brief sem Etapa, Branch, Base ou Base-sha | test_brief_sem_etapa_branch_base_ou_base_sha_recusa_a_entrega | campo ausente | passou (M6, M12 a M14) |
| E4 textos de conferente.md e jarvis.md | leitura do diff | n/a | conferido, coerente com E1 e E2 |
| E3 rodada -REV numa mensagem | fora deste lote | n/a | não avaliado |

## Cenários e resultado real
- Carga conferida antes de cada rodada (0,4 a 1,4, abaixo de 7). Suíte completa não rodada (fica no pre-push).
- `python3 -m unittest test_mensagem_conferente test_testes_tocados` (em tests/): 92 testes, OK.
- `forge-testes --vermelho d14a713 --modulos test_mensagem_conferente`: rc=0, `vermelho: base=d14a7133eb60 head=e31bf9dc10c1`; 11 de 11 testes `H=ok · B=falha · prova (asserção)` (os 5 de recusa agora caem na base). Com `test_testes_tocados`: rc=0, `prova (asserção)=13`.
- `forge-testes --listar`: suíte completa pedida porque o diff altera `bin/forge-testes` (mapa); o módulo novo está no mapa (29 módulos).
- `forge-mutante tests/mutantes/t6t3-mensagem.json`: M1 a M16 morreram, rc=0.
- `forge-mutante --cobertura --base d14a713`: todas as condições mudadas (4605, 4607, 4616, 4666, 4668, 4669) com mutante declarado; o 4635 (controle em `--worktree`) por M15. Lista conferida contra o diff: uma linha de guarda mudada sem mutante, nenhuma.
- Achados recorrentes (PA-7) conferidos: AR-2 (ramo de falha sem teste) fechado nesta volta.

## Veredito
Aprovado sobre e31bf9d: A1, A2 e A3 fechados, mutantes mortos, vermelho provado. Nenhum bug aberto.
