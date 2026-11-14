---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 2511f48b990a871fd4700a67ddd00942174edcba
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 E1.135 (perguntas abertas ao dono, `cmd_abertas`)

Veredito: REPROVADO por 1 achado bloqueante (A1, defeito provado). Intervalo origin/develop..2511f48b (2 commits: feat e mutantes). Sem especificação de UX nem contrato de API (ferramenta de linha de comando); as obrigações são a diretriz 29 do pedido e o texto da E1.135. Sem PR aberto: sem check-run `bateria` para citar; a suíte inteira fica para o CI do PR.

## Achados
- A1 (bloqueante) bin/forge_dono.py:547 · `KANBAN.md` com OSError na leitura (permissão, E/S) derruba `cmd_abertas` com traceback e perde a lista dos pedidos; os pedidos têm try/except e o quadro não. Bug V047-PA-01, reproduzido; falta teste.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aberta sai com pedido, hora, pergunta, recomendada | test_aberta_sai_com_pedido_hora_pergunta_e_recomendada | n/a | passou |
| Respondida sai; decisão anterior não responde | test_respondida_sai_e_decisao_anterior_nao_responde | decisão antes da pergunta | passou |
| Painel `Aguardando o dono` entra, resto do quadro não | test_painel_do_quadro_entra_e_o_resto_do_quadro_nao | seção errada | passou |
| Sem pendência: linha única | test_sem_pendencia_uma_linha | vazio | passou |
| Ordem por peso, depois a mais antiga | test_ordem_por_peso_e_depois_a_mais_antiga | empate de peso | passou |
| Formas do registro (prefixo, aspas, sem parênteses) | test_formas_do_registro_com_prefixo_aspas_e_sem_parenteses | variantes de data | passou |
| Pergunta longa cortada | test_pergunta_longa_sai_cortada_numa_linha | máximo 200 | passou |
| Cartão sem data: traço | test_cartao_sem_data_sai_com_traco | data vazia | passou |
| Link simbólico e arquivo ilegível fora | test_link_e_arquivo_ilegivel_ficam_fora | link, UnicodeDecodeError | passou |
| KANBAN.md com OSError | (nenhum) | permissão | FALHA: A1 |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_dono`: 73 testes, OK (9 novos em `PerguntasAbertas`).
- Vermelho antes do verde (à mão: `forge-testes --vermelho` foi barrado pelo R-TETO, tarefa pesada de outra sessão, sem veredito): com `bin/forge_dono.py` de origin/develop numa cópia, os 9 testes novos dão erro (`FAILED (errors=9)`, falta `cmd_abertas`); com o do head, passam.
- Mutação: `bin/forge-mutante tests/mutantes/v047-perguntas-abertas.json tests/mutantes/v047-perguntas-abertas-2.json --processos 2`: PA-M1 a PA-M15 todos `morreu`, saída 0 (PA-M8 morreu por erro do teste sob o mutante, não por asserção). `--cobertura --base e60183d0`: todas as condições novas listadas como cobertas (declarado, não provado); as linhas 547 a 551 de leitura do quadro não têm mutante de tratamento de erro, coerente com A1.
- Reprodução de A1: `read_text` de `KANBAN.md` levantando `PermissionError` dá `EXC PermissionError` (sem aviso nem lista).
