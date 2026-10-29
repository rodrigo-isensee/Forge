---
tipo: qa
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: 0c2ef9ca9453736aecefad78a48c284dc599025e
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: t6t3-mensagem

Lote E1, E2, E4 e E5 do pedido T6T3-MENSAGEM (o E3 foi para o pedido T6T3-RODADA). Sem `CA-n` (pedido técnico): os critérios são os itens do escopo. Base d14a7133.

## Achados
- A1 (bloqueante) bin/forge-check:4605 · mutante sobrevivente (R-QA): a guarda `etapa and branch and base and base_sha` só tem teste para `branch`; tirar `base`, `base-sha` ou `etapa` da condição (X1, X2, X3) passa em todos os testes; classe AR-2 (ramo de falha de guarda sem teste), e a mensagem sairia sem Base-sha para o conferente
- A2 (bloqueante) bin/forge-check:4635 · mutante sobrevivente (R-QA, R-SEGURANCA): a recusa de caractere de controle em `--worktree` (a linha entra em `campos`) não tem teste; tirar o par (X4) passa; o valor vai impresso na mensagem ao conferente, então é entrada para injetar linha; classe AR-2
- A3 (recomendado) tests/test_mensagem_conferente.py:55 · o teste de recusa agrega cinco ramos num só e passa na base (argparse recusa `--entrega` com rc 2); separar um teste por ramo e afirmar a mensagem de recusa, não só o rc

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 etapa lida do brief | test_a_etapa_sai_da_linha_etapa_do_brief | `--etapa` ausente ou igual | passou (M1 a M4 mortos) |
| E1 `--etapa` diferente recusado | test_etapa_diferente_da_do_brief_e_recusada_com_a_etapa_certa | etapa divergente | passou |
| E1 `Arquivo:` absoluto | test_entrega_traz_tudo_do_arquivo... (linha Arquivo) | n/a | passou |
| E2 mensagem de entrega e Desde da última `conferida` | test_entrega_traz_tudo_do_arquivo_e_o_desde_da_ultima_conferida | duas conferidas (pega a última) | passou (M10, X5 mortos) |
| E2 sem `conferida`, sem linha Desde | test_sem_conferida_no_historico_a_linha_desde_nao_sai | histórico sem conferida | passou (M11) |
| E2 `--worktree` ausente, relativo, inexistente; `--ref`; brief sem Branch | test_entrega_recusa_worktree_ausente_relativa_ou_inexistente_e_brief_sem_branch | permissão e vazio | passou, mas Base, Base-sha, Etapa e controle em `--worktree` sem prova (A1, A2) |
| E4 textos de conferente.md e jarvis.md | leitura do diff (sem teste de comportamento) | n/a | conferido, coerente com E1 e E2 |
| E3 rodada -REV numa mensagem | fora deste lote (T6T3-RODADA) | n/a | não avaliado |

## Cenários e resultado real
- `python3 -m unittest tests.test_mensagem_conferente`: 5 testes, OK.
- `forge-testes --vermelho d14a713` completo estourou o prazo de 590 s (rc=124, sem veredito: o diff em `agents/` manda rodar 75 módulos). Refeito com `--modulos test_mensagem_conferente,test_testes_tocados`: rc=0, `prova (asserção)=6`; 4 dos 5 testes novos caem na base; o de recusa de worktree passa na base (A3).
- Mapa do forge-check (29 módulos, test_testes_tocados:61): coerente com o módulo novo em bin/forge-testes.
- `forge-mutante tests/mutantes/t6t3-mensagem.json`: M1 a M11 morreram, rc=0.
- `forge-mutante --cobertura --base d14a713`: as 7 condições mudadas (4605, 4607, 4611, 4616, 4666, 4668, 4669) têm mutante declarado.
- Conferência da lista contra o diff, com sondas minhas (spec em $TMPDIR): X1 (sem `base`), X2 (sem `base_sha`), X3 (sem `etapa`) e X4 (sem `--worktree` em `campos`) sobreviveram; X5 (`conferidas[0]`) e X7 (sem `a.worktree`) morreram; X6 inválido (trecho repetido), não avaliado. O `except OSError` do pedido ilegível não tem teste (A3 cobre a separação).
- Carga conferida antes de cada rodada (abaixo de 7,2). Suíte completa não rodada (fica no pre-push).

## Veredito
Reprovado por A1 e A2: a lista de mutantes cobre a linha, não todas as condições dela. Correção: um teste por condição (brief sem Base, sem Base-sha, sem Etapa; `--worktree` com caractere de controle) e mutante para cada uma. Responsável: tech-lead (código de teste do lote).
