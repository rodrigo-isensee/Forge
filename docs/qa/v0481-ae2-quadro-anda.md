---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 59add0136ba78ab707d74575f2325327284126e9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 E10.16 (AE2: o quadro anda sozinho com o merge; PR #875, classe C), delta f45bf805..59add013

Escopo: 4ª volta (E10.16) sobre o meu parecer anterior (f45bf805, reprovado por A1). Delta lido: `tests/mutantes/v0481-ae2-quadro-anda-5.json` (ids renumerados para AE35 a AE41), uma linha de comentário em `tests/test_sobreposicao_quadro.py` (AE38/AE39 virou AE40/AE41) e o fragmento do changelog; `bin/forge-fechar` e `docs/fechamento-integrador.md` vêm da develop (#898/#885, já revisados no PR de origem). Sem UI: acessibilidade e E2E de navegador não se aplicam.

## Fechamento dos achados do parecer anterior
| Anterior | Estado | Prova |
|---|---|---|
| A1 ids AE33/AE34 repetidos entre `-4` e `-5` | resolvido | `-5.json` agora AE35 a AE41; as cinco specs juntas rodam numa rodada só |
| (3ª volta) A1 AE13 sobrevivia | resolvido | AE13 morreu |
| (3ª volta) A2 AE3, AE5, AE7, AE14 inválidos | resolvido | os quatro `morreu` |

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só a linha inteira `Cartão: ID` do corpo move | `test_titulo_e_texto_que_so_cita_cartao_nao_movem` | título, item de lista, texto antes | passou; AE13 morreu |
| Cabeçalho e linha de outra largura não dão coluna ao cartão do corpo | `test_cabecalho_e_linha_de_outra_largura_nao_dao_coluna_ao_cartao_do_corpo` | ID `ID`, linha de 6 células | passou; AE33/AE34 (-4) morreram |
| Aviso de falha ao gravar diz caminho e causa, sem `[Errno n]` | `test_trava_que_nao_abre_avisa_sem_derrubar` | OSError | passou; AE40 e AE41 morreram |
| Troca de seção, destino e fim da tabela | `test_linha_sai_da_origem_e_entra_no_fim_da_tabela_do_destino`, `test_atributo_dado_troca_a_celula_e_o_resto_fica` | seção `##` e linha de tabela | passou; AE35 a AE39 (-5) morreram |
| Casos de borda do movimento em `movimento.md` | n/a (texto; testes de teto verdes no CI) | n/a | n/a |

## Provas
- Mutantes, as cinco specs numa só rodada: `bin/forge-mutante tests/mutantes/v0481-ae2-quadro-anda.json tests/mutantes/v0481-ae2-quadro-anda-2.json tests/mutantes/v0481-ae2-quadro-anda-3.json tests/mutantes/v0481-ae2-quadro-anda-4.json tests/mutantes/v0481-ae2-quadro-anda-5.json --processos 4`: rc=0, cabeçalho `rev=59add0136ba7`, 41 `morreu`, nenhum sobrevivente, inválido ou sem veredito (último: `AE41 · morreu · bin/forge-check:5384`).
- Vermelho: código e testes não mudaram desde f45bf805 (vermelho do parecer anterior: `bin/forge-testes --vermelho bbbe2d8871c0ecb4a07c4c065361f14adbe0e1b2 --modulos test_fechar_move_cartao,test_sobreposicao_quadro`, rc=0, 16 provam por asserção, nenhum cai no HEAD); no delta só mudou comentário.
- Local no head: o módulo `tests.test_sobreposicao_quadro` rodou 77 testes, OK. A bateria inteira não foi rodada aqui (G3).
- ci: 59add0136ba78ab707d74575f2325327284126e9 verde
- Detalhe do CI do mesmo sha (`gh pr checks 875`; o run 45730370626 é do head 59add013): suíte python 3.12 e 3.14 (partes 1 a 5), bateria (passos), (python 3.14), (verificações longas), instalação, teto de pulados, árvore já provada e `catraca`: pass. Fora do que conta: `bateria (pareceres)` e `bateria`, que esperam os pareceres.
