---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: cbf24de557ea23a5bf6a5c7e43942a239b3f8aba
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (AE2, #875, E10.4)

Escopo: diff `bbbe2d88..cbf24de5` (`bin/forge-check` movimento e `linha_movida`/`mover_no_quadro`, `bin/forge-fechar` `cartoes_do_corpo`, testes, docs). Classe C.

## Gatilhos
Gatilhos: controle do Forge que analisa entrada (corpo do PR no fechamento), escrita de arquivo de estado (KANBAN.md) por ferramenta, fechamento pós-merge.

## Resumo
- **`·` no `--titulo` (o caso `a · b` saiu de `tests/test_sobreposicao_quadro.py:398`): neutro.** A troca `·` por `-` (`bin/forge-check:5224`) acontece antes de `erro_dos_atributos`, que continua recusando `·` em todos os atributos; o valor gravado nunca leva `·`, então o título não forja a marca ` · atributos: ` nem um segmento do leitor (C-4, C-7). `--pedido` e `--responsavel` seguem recusando `·` (regex e forma). O teste novo prova o valor gravado (`titulo=AE2 - quadro`). Não afrouxa: a recusa vira normalização com a mesma garantia.
- **Merge confirmado antes de mover: aprovado.** `cartoes_do_corpo` roda em `bin/forge-fechar:1923`, depois das guardas do passo 6 (MERGED, head igual ao conferido, base igual ao alvo, commit de merge presente); com o PR já mesclado por outra via (`ja_mesclado=1`) o corpo não é lido. O ID do corpo passa pela forma `[A-Za-z0-9][A-Za-z0-9._-]{0,79}` e vai como argumento, sem expansão. O teste confere a ordem merge antes do movimento.
- **Escrita do quadro:** trava (C-10), leitura sem seguir link (C-1) e troca atômica (C-2) estão certas e testadas (link, trava que não abre). **Mas o movimento corrompe o quadro** quando o nome do cartão casa a linha de cabeçalho ou de separador da tabela (A1, provado), e o nome `ID` passa pela forma do `forge-fechar`, então uma linha `Cartão: ID` no corpo do PR basta.

## Achados
- A1 (bloqueante) bin/forge-check:5265 · linha_movida casa como linha de cartão o cabeçalho (`| ID | Cartão |...`) e o separador (`|---|...`): cartão `ID` (qualquer caixa) ou `---` tira o cabeçalho ou o separador da última tabela e grava a linha no lugar; o quadro fica sem cabeçalho. `Cartão: ID` no corpo do PR chega aqui.
- A2 (recomendado) bin/forge-fechar:950 · Cartão: do corpo que não existe no quadro (erro de digitação, placeholder, linha dentro de bloco de código) nasce como linha nova em Pronto com `—`: o fechamento deveria mover só cartão que já tem coluna (coluna_do_cartao diferente de `—`) e só avisar o resto.
- A3 (recomendado) bin/forge-check:5275 · Com o cartão duplicado em duas seções, só a última linha sai; a outra fica na coluna velha e o quadro segue dizendo que o cartão está nos dois lugares. Tirar todas as linhas do cartão antes de inserir a nova.
- A4 (recomendado) bin/forge-check:5135 · KANBAN.md com byte UTF-8 inválido é reescrito com U+FFFD no lugar do byte, mudando linhas que o movimento não tocou; recusar com aviso (quadro intacto) quando a decodificação estrita falha.

## Sondas
- S1 · movimento ID --de — --para Pronto (quadro com 3 tabelas) · espera: cabeçalho de Pronto intacto e linha nova do cartão ID · obtido: rc 0, Pronto começa por `|---|` e a linha `| ID | Cartão | Pedido | Responsável | Entrou | <hora> | custo total: lacuna |`
- S2 · movimento --de — --para Pronto -- --- · espera: separador de Pronto intacto · obtido: rc 0, separador de Pronto vira `| --- | --- | --- | --- | --- | <hora> | custo total: lacuna |`

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:5265` (o laço só exige `|` no início, 7 células e `chave_do_cartao(c[0])` igual); `bin/forge-check:5275` apaga a linha achada. Caminho: o autor do PR (ou quem roda `movimento` à mão) cita `Cartão: ID`; `cartoes_do_corpo` aceita (forma alfanumérica), `coluna_do_cartao` devolve uma seção e o `movimento` move o cabeçalho da última tabela; o quadro perde o cabeçalho, sem aviso e com rc 0 (o histórico grava o movimento de um cartão inexistente). Severidade baixa (integridade do quadro, reparável com `kanban --gerar`), mas é defeito provado no ponto que o brief pede ("não pode corromper o quadro"). Correção mínima: no laço, ignorar a linha que é o cabeçalho (`c == COLUNAS`, comparação sem caixa) e a que é separador (todas as células casam `SEPARADOR`), ou só contar linhas depois do separador da tabela; e um teste com os cartões `ID`, `id` e `---`. Esforço P. Dono: autor do #875 (tech-lead).
**A2.** Caminho: texto colado no corpo (um exemplo em bloco de código, um placeholder) move ou cria cartão; afeta métricas, não acesso. Correção: em `cartoes_do_corpo`, avisar e não somar o ID cuja `coluna_do_cartao` é `—`. Esforço P. Dono: tech-lead.
**A3 e A4.** Integridade do quadro em estados já degradados; correção P, dono tech-lead.

Suíte: CI do head `cbf24de5` com a suíte ainda pendente na leitura (bateria de pareceres e catraca vermelhas pela falta dos pareceres); rodei `tests.test_fechar_move_cartao` e `tests.test_sobreposicao_quadro` no head: 90 testes, OK. Sondas em script local (biblioteca padrão), quadro em pasta temporária.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, testes do repositório e sondas locais; varredura de segredos não se aplica ao delta (sem credencial nem configuração nova).
