---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: f45bf805616768db672757c4896fd112fee05534
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (AE2, #875, E10.13), volta por delta

Delta lido: `8087e23d..f45bf805`. Pelo `forge-check parecer delta` (sem o que veio da develop), o domínio tem `bin/forge-fechar` (`coluna_do_cartao`, commit `8bb4da7b`), `tests/test_fechar_move_cartao.py`, `skills/kanban-scrum/SKILL.md` e `movimento.md` (`75bdf0dc`) e `docs/fechamento-integrador.md`. Fora do domínio: os mutantes (`8bb4da7b`, `1799f9d5`, `996c05e1`), uma asserção em `tests/test_sobreposicao_quadro.py:499` e o fragmento do changelog. Nas duas fusões da develop, só `docs/fechamento-integrador.md` teve conflito (`0fc65e4d`). A resolução guarda o texto da develop (LIMPAR-CLONE-PARECER) e o do AE2, sem perder nada. Em `bin/`, a única diferença para a develop é a do AE2. A rodada anterior (aprovada em `8087e23d`) está no git. Classe C.

Gatilhos: controle do Forge que analisa entrada (corpo do PR no fechamento), escrita do KANBAN.md por ferramenta, fechamento depois do merge.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta: `coluna_do_cartao` (bin/forge-fechar:949-952).** No KANBAN.md, a coluna só vem de uma linha de 7 células que não é o cabeçalho `COLUNAS`, o mesmo critério do `celulas_de_cartao`. `Cartão: ID` e o cartão em linha de outra largura no corpo do PR só avisam e não criam o cartão fantasma em Pronto (S2 refeita). O separador não casa porque a forma do ID (`bin/forge-fechar:969`) exige que o primeiro caractere seja letra ou número. Linha com CRLF: o awk não tira o `\r`, então dá 8 células, coluna `—` e só aviso. A guarda falha fechada aqui, mesmo que diferente do filtro em Python: é neutro.
- **Aperta: os testes.** `test_cabecalho_e_linha_de_outra_largura_nao_dao_coluna_ao_cartao_do_corpo` (tests/test_fechar_move_cartao.py:171) e a âncora da linha inteira `Cartão:`, que volta a ser provada com K-2 e K-3 no histórico. A asserção do caminho e da causa no aviso de erro de disco (tests/test_sobreposicao_quadro.py:499) e os mutantes AE33 a AE39 (AE12 realinhado) também apertam.
- **Neutro: o texto.** Os casos de borda saem do parêntese do `SKILL.md` e vão para `skills/kanban-scrum/movimento.md`, com os mesmos sete itens e nenhum a menos. A conferência foi item por item. O changelog e a resolução de conflito do `docs/fechamento-integrador.md` também são neutros.
- **Afrouxa: nada.** Nenhuma guarda que barrava deixou de barrar.

Achados anteriores: A5 (recomendado) resolvido (bin/forge-fechar:952, teste da linha 171, S2).

## Achados

## Sondas

## Detalhe
S2 refeita no head, `coluna_do_cartao` extraída do bin/forge-fechar, quadro numa pasta temporária com cabeçalho, separador `|---|` e `|:--|`, uma linha de 6 células e uma linha com CRLF: `ID`→`—`, `id`→`—`, `K-1`→`Em andamento`, `K-5` (6 células)→`—`, `K-7` (CRLF)→`—`, `Cartão`→`—`.

Suíte: no head, `python3 -m unittest tests.test_fechar_move_cartao tests.test_sobreposicao_quadro` deu 97 testes, OK. Não rodei os mutantes, porque o hook de tarefa pesada pôs a fila de outra sessão na frente; eles são do QA. O CI do head está verde nas partes que contam: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, bateria (python 3.14), instalação, teto de pulados e árvore provada. Três checks estão vermelhos só por espera:
- `catraca`: R-CONFORMIDADE, mudança em `bin/forge-check` sem o rótulo `afrouxa-regra`.
- `bateria (pareceres)`: os pareceres de review e de segurança estão desatualizados e o de QA está reprovado.
- `bateria`: é o agregador e falha porque `pareceres: failure`.

## Parecer
- ci: f45bf805616768db672757c4896fd112fee05534 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, testes dos módulos tocados, sonda local (bash), logs do CI pelo `gh`. A varredura de segredos não se aplica: o delta não traz credencial nem configuração nova.
