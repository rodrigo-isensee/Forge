---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: cbf24de557ea23a5bf6a5c7e43942a239b3f8aba
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 1
data: 2026-11-24
---
# QA: v0481 E10.3 (AE2: o quadro anda sozinho com o merge; PR #875, classe C)

Escopo: `forge-check movimento` move a linha do cartão no `KANBAN.md` e aceita `·` no `--titulo`; `forge-fechar` move para Pronto, depois do merge provado, o cartão de cada linha `Cartão: <ID>` do corpo do PR. Sem UI: acessibilidade e E2E de navegador não se aplicam. Revisado o diff `bbbe2d8..cbf24de` (9 arquivos).

## Achados
- A1 (bloqueante) bin/forge-check:5265 · o casamento por ID também pega a linha de cabeçalho: `movimento ID --para Pronto` (ou `Cartão`) leva o cabeçalho da tabela para Pronto e deixa a seção de origem sem cabeçalho. O quadro sai corrompido por ID legal. Pular o cabeçalho e o separador.
- A2 (recomendado) bin/forge-check:5204 · a mensagem de recusa do `--titulo` ainda lista `·` como proibido, mas o `·` agora vira `-` antes da checagem e o texto engana. Tirar o `·` da frase (vale para `--pedido` e `--responsavel`, que seguem recusando).
- A3 (recomendado) bin/forge-check:5265 · com o mesmo ID em duas seções, só a última ocorrência move; a outra fica no quadro e o cartão aparece duplicado. Sondado (ID em Em andamento e Code review). Mover todas, ou avisar da duplicata.

## Critério → teste → resultado
| Critério (do brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A linha move de seção e entra no fim da tabela do destino | `MovimentoMoveALinha.test_linha_sai_da_origem_e_entra_no_fim_da_tabela_do_destino` | nota depois da tabela; outro cartão fica | passou |
| Cartão novo e seção sem tabela | `test_cartao_novo_nasce_na_secao_sem_tabela_e_aceita_titulo_com_ponto` | seção vazia | passou |
| Estado fora do quadro e sem seção | `test_estado_fora_do_quadro_vai_a_secao_do_estado`, `test_sem_secao_nem_bloqueado_avisa_e_o_quadro_fica` | quadro intacto | passou |
| Não corrompe o quadro | `test_quadro_por_link_nao_e_escrito`, `test_trava_que_nao_abre_avisa_sem_derrubar`, sonda de cabeçalho | link, trava, cabeçalho | falhou na sonda (A1) |
| Não move cartão errado | `test_atributo_dado_troca_a_celula_e_o_resto_fica`, sonda de duplicata | caixa do ID, duplicata | passou nos testes; sonda mostra A3 |
| `·` no título vira `-` | `test_cartao_novo_nasce...` e sonda `a · atributos: pedido=zz` (recusado por `=`) | marca `· atributos:` não forjável | passou |
| forge-fechar move só depois do merge | `test_corpo_com_cartao_move_para_pronto_com_a_prova_do_merge` (ordem `gh pr merge` antes do movimento), `test_pr_ja_mesclado_nao_le_o_corpo` | PR já mesclado, `--armar` | passou |
| Corpo: só a linha inteira `Cartão: ID` | `test_titulo_e_texto_que_so_cita_cartao_nao_movem`, `test_cartao_do_corpo_fora_da_forma_avisa_e_fecha`, `test_cartao_do_corpo_sem_quadro_avisa_e_fecha`, `test_cartao_do_corpo_e_do_argumento_move_uma_vez` | título, item de lista, ID com `;`, duplicata | passou |

## O caso "a · b" saiu da lista de recusas
Não afrouxa nada que importe. A recusa existia porque `·` separa a marca `· atributos:` no histórico; o valor agora troca `·` por `-` antes de `erro_dos_atributos` e só no `titulo`. `;`, `=`, `|`, controle e invisível seguem recusados (testes mantidos), `--pedido` e `--responsavel` seguem recusando `·` pela forma, e a sonda `a · atributos: pedido=zz` sai rc 1. O caso novo (`AE2 · quadro` vira `AE2 - quadro`, com `atributos: ...` íntegro no histórico) o cobre, e o mutante AE12 morre. Só a mensagem ficou velha (A2).

## Provas
- Local: `test_fechar_move_cartao` 18 testes OK; `test_sobreposicao_quadro` 72 testes OK.
- Vermelho: `bin/forge-testes --vermelho bbbe2d8871c0ecb4a07c4c065361f14adbe0e1b2 --modulos test_fechar_move_cartao,test_sobreposicao_quadro` abriu com `vermelho: base=bbbe2d8871c0 head=cbf24de557ea`; 10 testes "prova (asserção)" (H=ok, B=falha), nenhum cai no HEAD; os demais 80 já existiam e passam nos dois.
- Mutantes do autor: `bin/forge-mutante tests/mutantes/v0481-ae2-quadro-anda.json tests/mutantes/v0481-ae2-quadro-anda-2.json` rodou AE1 a AE18, todos `morreu`.
- A `--cobertura --base` lista como "sem mutante" as linhas 5224, 5261, 5263, 5270, 5276 a 5278 e 5310. Somei 4 mutantes meus (spec fora da árvore): Q1 fim da seção (`bin/forge-check:5277`), Q2 `del` da linha achada (5274), Q3 troca do `·` (5224), Q4 tabela da seção (5279): todos `morreu`. Sem sobrevivente.
- CI do head `cbf24de`: `bateria (passos)` e `bateria (verificações longas)` success; `catraca` e `bateria (pareceres)` failure (faltam pareceres do pedido, esperado antes deste); as suítes python 3.12 e 3.14 estavam em andamento na leitura. O `bateria` final do mesmo sha fica para a volta.

## Cenários e resultado real
Sondas em arquivo, quadro descartável: ID duplicado (A3), ID `ID` e `Cartão` (A1; `---` nem chega ao subcomando, rc 2 do argparse), título com `·` e `•` (o `•` passa como já passava). Medida que o item espera mover (tempo por item): não medida aqui; o ganho é a remoção do `kanban --gerar` manual, sem custo medido.
