---
tipo: review
contrato: 1
pedido: catraca-ramo-cmd-pr
branch: melhoria/catraca-ramo-cmd-pr
commit: c0124465c1e425a8c799da5ba06dcb4a1b03bd36
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: catraca-ramo-cmd-pr (versao-033, CATRACA-RAMO-CMD-PR, E11)

Revisor: `forge:tech-lead`, outra instância (não é o autor). Diff `origin/develop...c012446`, um commit.

## Achados
- A1 (recomendado) tests/catraca.py:1160 · a dica manda conferir com `forge-check pr <pedido>`, que sem `ramo` ainda escolhe o parecer de outra branch e pode divergir da catraca; passar o ramo quando `--ref` é nome de branch alinha os dois caminhos (cartão à parte).
- A2 (recomendado) tests/test_catraca.py:1549 · falta um caso com `--ramo=` vazio (HEAD_REF ausente); hoje ele falha fechado (nenhum parecer tem `branch:` vazio), mas nenhum teste prende isso.

## Leitura
- Afirmações conferidas: com `ramo`, `cmd_pr` (bin/forge-check:738) e `pareceres_que_nao_aprovam` (tests/catraca.py:1124) filtram por `branch == ramo`; sem candidato, `cmd_pr` emite `sem parecer ... com branch:` (falha fechada); os outros chamadores (bin/forge-check:647, 657, 1146) não passam `ramo`, o caminho manual não muda.
- R-CONFORMIDADE: o filtro só estreita o conjunto. O pedido do PR já vinha de `pedidos_da_branch`, que usa a mesma chave (`branch:`); um PR que adota um nome de branch alheio não ganha nada novo: o parecer tem de estar na árvore do head, com `commit_vale` contra o head e autoria registrada, como antes. Parecer de outra branch com `commit:` desatualizado deixa de travar o PR errado, que é o defeito corrigido.
- Promoções: `_violacoes_de_pareceres` sai antes em PROMOCOES; nada muda para `develop`→`homolog` e `homolog`→`main`.
- Pareceres antigos sem `branch:`: nunca entravam (o `pedidos_da_branch` não os acha, e o contrato exige `branch`); o comportamento segue igual.
- Teto M14: 44 linhas (bin 9, catraca 11, testes 24), um comportamento; toca PROTEGIDOS dentro do teto, sem pedir exceção.
- Testes: os 3 E11 cobrem desempate, reprovado próprio escondido e falha fechada; o primeiro também prova o caminho manual inalterado.

## Parecer
Aprovado. A correção aperta o critério (só conta o parecer da própria branch), não afrouxa controle, e o caminho manual fica igual. A1 e A2 são recomendações.

Provas: `python3 -I -m unittest discover -s tests -p test_catraca.py` rc=0 (OK). `test_forge.py` não rodado (sem vaga de CPU; o QA e o CI cobrem).
