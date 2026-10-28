---
tipo: review
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 6b0c95eadd0ab215de40630d9734318a1c33889a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 2 (shell, isentas, tetos de T7, A5 e o PQ no `gerar_volta`)

Revalidação por delta (volta 2). Parecer anterior: `fc721f1`, sobre `a157116`. Delta `a1571168d78646e8ccdd0ad3a225dfafc3775ffb..6b0c95eadd0ab215de40630d9734318a1c33889a`; o `forge-check delta --parecer docs/reviews/guarda-sem-mutante-2.md` listou `bin/forge-mutante` 95, 397-424 e 434; `tests/test_forge_mutante.py` 516-518, 539-561; as specs `tests/mutantes/guarda-sem-mutante-13.json` (49-50), `-14.json` e `-15.json`. Li só esse delta; o resto da branch fica como "já lido" nos pareceres `1f394b7` e `fc721f1`. Os pareceres de segurança e de QA do delta não são revistos aqui.

## Achados
- A1 (bloqueante) bin/forge-mutante:412 · classe: aritmética que abre heredoc · requisito da decisão de 12:01 (`<<` dentro de `$(( ))` não abre heredoc nem esconde condição) e defeito provado: `prof` zera em toda quebra de linha (o M89 trava esse comportamento), então `x=$((1 +` numa linha e `1<<EOF))` na seguinte abrem heredoc e mascaram até a próxima linha `EOF`; o mesmo vale para a aritmética antiga `x=$[1<<EOF]`, que `prof` não conta. Prova de ponta a ponta (repositório de 2 commits, `--cobertura --base HEAD~1`): `if [ -f /etc/x ]; then exit 1; fi` novo entre a abertura e o `EOF` sai rc 0, sem `sem mutante` nem `não coberto`, nos dois casos; o `bash` executa a condição nos dois (`RODOU1`, `RODOU6`). Sugestão: não zerar `prof` enquanto o `$((`/`((` não fecha (ou, com `((` aberto de linha anterior, declarar a região incerta) e contar `$[`/`]` junto; um subcaso de teste por forma e o mutante da guarda nova.
- A2 (bloqueante) bin/forge-mutante:434 · classe: texto executado por `-c`/`eval` não reconhecido · requisito da decisão de 12:01 ("`eval` ou `-c` em qualquer forma") e defeito provado: a janela de 30 caracteres com `EXECUTA_SH` ancorado no fim só pega a aspa colada ao `-c`/`eval`. Saem rc 0, sem `não coberto`, e o `bash` executa todos (`RODOU2` a `RODOU5`): (a) `eval $"[ -f /etc/x ] && exit 1"` (o `$"` não é ficha; a ficha `"..."` tem `$` antes); (b) `bash -c \` com a string na linha seguinte (o `\` + quebra fica entre os dois); (c) `eval "true;"'[ -f /etc/x ] && exit 1'` (a segunda aspa é colada à primeira); (d) `bash -c -e "[ -f /etc/x ] && exit 1"` (opção depois do `-c`). Sugestão: em vez de olhar só o que precede a aspa, declarar incerta a aspa com condição que esteja no mesmo comando lógico (linhas unidas por `\` + quebra, até `;`, `&`, `|` ou quebra) depois de uma palavra `eval` ou `-\w*c`; um subcaso por forma em `test_shell_que_nao_se_le_com_certeza...` e o mutante da guarda nova.

## Revalidação dos achados do parecer `fc721f1`
- **A1 (heredoc): parcialmente resolvido.** (a) Terminador: resolvido. Só a linha exata fecha o `<<` (`onde` guarda só a linha igual ao seu `strip()`); `  EOF`, `EOF ` e `EOF\r` vão para `recuadas` e, antes do fecho, tornam incerta a região da abertura ao fecho; `<<-` sempre sai incerto e fecha na linha sem os tabs da esquerda (`tabs`). Conferido com os subcasos novos e com sondas próprias (`EOF ` no fim e CRLF saem `não coberto`). (b) `<<` em `$(( ))`: resolvido só quando a aritmética abre e fecha na mesma linha; a forma em várias linhas e o `$[ ]` seguem escondendo código (A1 acima).
- **A2 (`-c`/`eval`): parcialmente resolvido.** `eval $'...'` (`$` no teste da ficha) e `bash -c -- '...'` (`(?:\s+--)?` em `EXECUTA_SH`) saem `não coberto: run.sh:2`, com subcaso e mutantes (M94, M95). As outras formas seguem escapando (A2 acima).
- **A3 (recomendado, teste de tempo): tratado.** O limite foi a 0,1 s (p95 com 4 processos em paralelo, 2×, decisão de 12:01), ainda duas ordens abaixo dos 9 s da versão quadrática.
- O M87 da spec -13 foi retocado para `if m.lastindex:` porque a linha nova `if m.lastindex and prof > 0:` tornou o `de` antigo ambíguo; a guarda e o teste são os mesmos (consequência da mudança, como na decisão de 11:46).

Teto M14: `bin/forge-check` 1 + `bin/forge-mutante` 221 + `tests/test_forge_mutante.py` 148 + `tests/test_volta_por_delta.py` 2 = 372 linhas (`git diff --numstat --no-renames ff3936a...HEAD`), dentro de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS` foi tocado.

Citado, sem refazer: `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta` deu `Ran 126 tests ... OK`. `bin/forge-mutante --cobertura --base ff3936a` no head deu rc 0, com 38 linhas `coberta` e 5 `spec editada`, sem `sem mutante`, `apagada` nem `não coberto`. Segurança e QA têm parecer próprio.

Achados recorrentes (PA-7): a classe "a máscara do shell esconde código e sai rc 0" voltou pela quarta vez neste pedido (A1 de `1f394b7`, A1 da segurança `53ff539`, A1 de `fc721f1` e os dois acima); a linha `AR-1` entra em `docs/engineering/achados-recorrentes.md` neste commit.

Entregar da volta: A1 e A2, cada forma com um subcaso de teste que falha antes da correção e com o mutante da guarda nova.
