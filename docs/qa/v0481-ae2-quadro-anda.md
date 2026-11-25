---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: f45bf805616768db672757c4896fd112fee05534
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 E10.12 (AE2: o quadro anda sozinho com o merge; PR #875, classe C), delta 8087e23..f45bf805

Escopo: 3ª volta (E10.10) sobre o meu parecer anterior (8087e23, reprovado por A1 e A2). Lido o delta próprio do pedido: `tests/test_fechar_move_cartao.py`, `tests/test_sobreposicao_quadro.py`, as specs `tests/mutantes/v0481-ae2-quadro-anda*.json`, `skills/kanban-scrum/movimento.md` e o fragmento do changelog; o resto do diff é a develop trazida (merges 1799f9d e 8b71e90). Sem UI: acessibilidade e E2E de navegador não se aplicam.

## Achados
- A1 (bloqueante) tests/mutantes/v0481-ae2-quadro-anda-5.json:AE33 · os ids AE33 e AE34 existem em `-4.json` (E10.9) e voltam em `-5.json`: passadas juntas, `forge-mutante` sai 1 com "spec inválida; nada foi executado · id de mutante repetido entre as specs: AE33, AE34". O conjunto declarado do pedido não roda numa só rodada (id único no conjunto, skill qa-testing). Renomear os de `-5.json` para AE40..AE46; guardas e `testes` seguem iguais.

## Fechamento dos achados do parecer anterior
| Anterior | Estado | Prova |
|---|---|---|
| A1 AE13 sobrevivia (âncora `^` da linha `Cartão:`) | resolvido | `test_titulo_e_texto_que_so_cita_cartao_nao_movem` agora dá histórico a K-2 e K-3; AE13 morreu |
| A2 AE3, AE5, AE7, AE14 inválidos | resolvido | trechos reescritos; os quatro saíram `morreu` (bin/forge-check:5339, 5344, 5348 e bin/forge-fechar:966) |

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só a linha inteira `Cartão: ID` do corpo move | `test_titulo_e_texto_que_so_cita_cartao_nao_movem` | título, item de lista, texto antes | passou; AE13 morreu |
| Cabeçalho e linha de outra largura não dão coluna ao cartão do corpo | `test_cabecalho_e_linha_de_outra_largura_nao_dao_coluna_ao_cartao_do_corpo` | ID `ID`, linha de 6 células | passou; AE33/AE34 (-4) morreram |
| Aviso de falha ao gravar diz caminho e causa, sem `[Errno n]` | `test_trava_que_nao_abre_avisa_sem_derrubar` (asserção nova) | OSError | passou; AE38 e AE39 morreram |
| Troca de seção, destino e fim da tabela | `test_linha_sai_da_origem_e_entra_no_fim_da_tabela_do_destino`, `test_atributo_dado_troca_a_celula_e_o_resto_fica` | seção `##` e linha de tabela | passou; AE33 a AE37 (-5) morreram |
| Casos de borda do movimento em `movimento.md` | n/a (texto; testes de teto verdes no CI) | n/a | n/a |

## Provas
- Vermelho: `bin/forge-testes --vermelho bbbe2d8871c0ecb4a07c4c065361f14adbe0e1b2 --modulos test_fechar_move_cartao,test_sobreposicao_quadro`: rc=0, árvore limpa. Cabeçalho `vermelho: base=bbbe2d8871c0 head=f45bf8056167`; `contagem: não prova (passa na base)=81; prova (asserção)=16`; nenhum teste cai no HEAD.
- Mutantes, uma spec por vez (`--processos 3`, rc=0 em cada): `v0481-ae2-quadro-anda.json` (AE1 a AE8), `-2` (AE12 a AE18), `-3` (AE20 a AE26), `-4` (AE28 a AE34), `-5` (AE33 a AE39); 41 mortos, nenhum sobrevivente, inválido ou sem veredito. Juntas as cinco specs não rodam (A1).
- Local só os módulos tocados, via o vermelho acima (head verde nos dois módulos); a bateria inteira não foi rodada aqui (G3).
- ci: f45bf805616768db672757c4896fd112fee05534 verde
- Detalhe do CI do mesmo sha (`gh pr checks 875`, com `XDG_CACHE_HOME` gravável): suíte python 3.12 e 3.14 (partes 1 a 5), bateria (passos), (python 3.14), (verificações longas), instalação, teto de pulados e árvore já provada: pass. Fora do que conta: `bateria (pareceres)` e `bateria` esperam este parecer; `catraca` falha por R-CONFORMIDADE ("mudança em bin/forge-check ... só passa com o rótulo `afrouxa-regra` do dono, aplicado depois do último push", log do run 45652484421), decisão do dono, não defeito de teste.

## Revalidação
Volta ao autor só o A1 (renomear ids de `-5.json`). Depois dele o delta é a spec; eu rodo `forge-mutante` das cinco specs numa rodada só.
