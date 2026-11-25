---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 8087e23dbec99aefc234a9735132c8c5721d164d
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E10.7 (AE2: o quadro anda sozinho com o merge; PR #875, classe C), delta cbf24de..8087e23

Escopo: volta E10.5 sobre o meu parecer anterior (cbf24de, reprovado por A1 a A3). Lido `git diff cbf24de5..8087e23d` (bin/forge-check, bin/forge-fechar, testes, specs de mutante 3 e 4, doc e skill). Sem UI: acessibilidade e E2E de navegador não se aplicam.

## Achados
- A1 (bloqueante) tests/test_fechar_move_cartao.py:145 · AE13 sobreviveu: sem `^[[:space:]]*` em `cartoes_do_corpo` (bin/forge-fechar:951) o teste de "só a linha inteira" segue verde. O guarda novo (cartão sem coluna) engole K-1, K-2 e K-3 antes de o teste ver o movimento. Dar histórico a K-1..K-3 nesse teste.
- A2 (bloqueante) tests/mutantes/v0481-ae2-quadro-anda.json:AE3 · AE3, AE5, AE7 e AE14 saíram `inválido` (trecho 0 vezes: o código mudou). As guardas casamento por ID, atributos da linha achada, remoção da origem e ID fora da forma ficam sem mutante declarado. Reescrever os 4 trechos.

## Fechamento dos achados do parecer anterior
| Anterior | Estado | Prova |
|---|---|---|
| A1 cabeçalho corrompido por ID legal | resolvido | `celulas_de_cartao` único; `test_cartao_com_nome_de_cabecalho_ou_separador_nao_casa_a_moldura` (ID, id, ---); AE19, AE20, AE26, AE27 e AE28 morreram |
| A2 mensagem do `--titulo` | resolvido | `test_recusa_do_titulo_nao_lista_o_ponto_e_a_dos_outros_lista`; AE23 e AE30 morreram |
| A3 ID em duas seções | resolvido | `test_cartao_em_duas_secoes_sai_das_duas`; AE31 e AE32 morreram; a última linha achada é a que anda |

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cabeçalho, separador (inclusive alinhado `:--`) e outra largura não são cartão | `test_cartao_com_nome_de_cabecalho_ou_separador_nao_casa_a_moldura`, `test_separador_alinhado_nao_conta_como_cartao_editado` | nome `ID`/`---` | passou |
| Cartão repetido em duas seções sai de todas | `test_cartao_em_duas_secoes_sai_das_duas` | duplicata | passou |
| UTF-8 inválido só avisa, quadro intacto byte a byte | `test_quadro_com_utf8_invalido_nao_e_reescrito` | byte `\xff` | passou |
| `Cartão:` fora do quadro só avisa e não nasce em Pronto | `test_cartao_do_corpo_sem_coluna_avisa_e_nao_nasce_em_pronto` | ID desconhecido | passou |
| Aviso sem caractere de controle | `test_cartao_do_corpo_fora_da_forma_avisa_e_fecha` (ESC) | `\x1b` | passou; Q7 morreu |
| Só a linha inteira `Cartão: ID` do corpo move | `test_titulo_e_texto_que_so_cita_cartao_nao_movem` | título, item de lista, texto antes | prova fraca (A1): Q5 e AE13 sobrevivem |
| Mensagem de recusa do `--titulo` sem `·` | `test_recusa_do_titulo_nao_lista_o_ponto_e_a_dos_outros_lista` | `--pedido` mantém `·` | passou |

## Provas
- Local no head 8087e23: `test_fechar_move_cartao` 19 testes OK; `test_sobreposicao_quadro` 77 testes OK.
- Vermelho: `bin/forge-testes --vermelho bbbe2d8871c0ecb4a07c4c065361f14adbe0e1b2 --modulos test_fechar_move_cartao,test_sobreposicao_quadro`: saída 0 (árvore limpa; a 1ª rodada, com o parecer ainda sem commit, saiu 2 e não vale). Cabeçalho `vermelho: base=bbbe2d8871c0 head=69dbfb40fa60` (o head é este commit do parecer sobre 8087e23); `contagem: não prova (passa na base)=81; prova (asserção)=15`, todos H=ok e B=falha, nenhum cai no HEAD. Os 15 incluem os testes novos da volta (cabeçalho/separador, duas seções, UTF-8, recusa do `--titulo`, cartão sem coluna).
- Mutantes do autor (4 specs, `--processos 2`): AE1 a AE32. Morreram todos exceto AE13 (`sobreviveu`) e AE3, AE5, AE7, AE14 (`inválido`, trecho 0 vezes). AE19 a AE32 morreram, como diz a volta.
- Mutantes meus, spec fora da árvore, sobre o código novo: Q1 casamento por ID (forge-check:5277), Q2 atributos da linha achada (5282), Q3 remoção da origem (5286), Q4 ID fora da forma (forge-fechar:953), Q6 UTF-8 estrito (5304) e Q7 tira controle (forge-fechar:954) morreram; Q5 (tira a âncora `^` da linha `Cartão:`, forge-fechar:951) sobreviveu, o mesmo mutante do AE13.
- `forge-mutante --cobertura --base bbbe2d8`: sem mutante só 5288 a 5290 (busca da seção de destino, comportamento não mudou na volta) e 5322 (mensagem de erro); `bin/forge-fechar` sai `não coberto` (shell; AE13 a AE18, AE24 e AE25 o cobrem à mão).
- CI: o `CI` do head 8087e23 foi cancelado (supersedido) e a `Catraca` falhou; o PR já tem commits mais novos (4c690aa, d398aff). Não há check-run `bateria` concluído para 8087e23, então não cito verde para ele. `bateria (pareceres)` falha enquanto faltam os pareceres do pedido.

## Revalidação
Voltam ao autor os dois achados. Depois deles o delta é o teste `test_titulo_e_texto_que_so_cita_cartao_nao_movem` e a spec `v0481-ae2-quadro-anda.json` (AE3, AE5, AE7, AE14); eu rodo `forge-mutante --base <novo head>` e o Q5.
