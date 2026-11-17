---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 3da5f24a4bb8aacb7fbf314e12f48ff955b93aba
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
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

## Volta 1 (E1.166): delta 2511f48b..3da5f24a, escopo incremental
Veredito: APROVADO. A1 anterior resolvido (bug V047-PA-01 fechado): `KANBAN.md` com OSError vira aviso e a lista segue (`test_quadro_ilegivel_vira_aviso`). Sem achados novos. Sem PR: sem check-run `bateria` do sha; a suíte inteira fica para o CI do PR.

| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do QA: quadro ilegível vira aviso | test_quadro_ilegivel_vira_aviso | OSError na leitura | passou |
| Review A1: decisão fecha no máximo uma pergunta | test_cada_decisao_fecha_no_maximo_uma_pergunta | duas perguntas, uma decisão | passou |
| Review A1: decisão de outro assunto não fecha | test_decisao_sobre_outro_assunto_nao_fecha_a_pergunta | fala intermediária do dono | passou |
| Review A3: forma antiga `PERGUNTA:` | test_forma_antiga_pergunta_dois_pontos | `nenhuma`, data no corpo | passou |
| Segurança A1: pasta `docs/pedidos` por link recusada | test_pasta_de_pedidos_por_link_e_recusada | link na pasta | passou |
| Segurança A2: linha longa não trava | test_linha_longa_nao_trava | 8 mil espaços | passou |

- `python3 -m unittest tests.test_forge_dono` no head: 79 testes, OK (6 novos).
- Vermelho: `forge-testes --vermelho 2511f48b` estourou o prazo de 500 s sem veredito (só o cabeçalho `vermelho: base=2511f48b990a head=3da5f24a4bb8`, rc 124), nunca vale como vermelho. À mão: `bin/forge_dono.py` da base numa cópia, `PerguntasAbertas` dá 15 testes, `FAILED (failures=5, errors=1)`; os 6 novos caem e os 9 antigos passam. No head, passam.
- Mutação: `bin/forge-mutante` nas 4 specs (`--processos 2`): PA-M1 a PA-M25 `morreu`, rc 0 (PA-M8 e PA-M24 morreram por erro do teste sob o mutante, não por asserção, o mesmo caso aceito antes).
- Sondas à mão: decisão única com duas perguntas deixa uma aberta; `PERGUNTA: nenhuma` não abre; entradas de 20 mil espaços e 20 mil letras em 0,15 s no total.
- Achados: nenhum.
