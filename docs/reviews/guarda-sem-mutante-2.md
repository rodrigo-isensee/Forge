---
tipo: review
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 729135968bf674a758e5fd8b88798c7ab0673c02
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 2 (shell, isentas, tetos de T7, A5 e o PQ no `gerar_volta`)

Revalidação por delta (volta 3, corte grosso da decisão do dono de 14:03). Parecer anterior: `a6f5184`, sobre `6b0c95e`. Delta `6b0c95eadd0ab215de40630d9734318a1c33889a..729135968bf674a758e5fd8b88798c7ab0673c02`; o `forge-check delta --parecer docs/reviews/guarda-sem-mutante-2.md` listou `bin/forge-mutante` 19-20, 89, 93-99, 397-426 e 445-455; `tests/test_forge_mutante.py` 517-528, 550-555 e 563; as specs `tests/mutantes/guarda-sem-mutante-12.json` (34, 39-40), `-13.json` (4, 33), `-14.json` e `-15.json` (removidas), `-16.json` e `-17.json` (novas); e a linha AR-1 de `docs/engineering/achados-recorrentes.md`. Li só esse delta. O resto da branch fica como "já lido" nos pareceres `1f394b7`, `fc721f1` e `a6f5184`. Não revejo aqui os pareceres de segurança e de QA do delta.

As sondas rodaram de ponta a ponta, num repositório de 2 commits com `--cobertura --base HEAD~1`. A linha de abertura está na base, e o diff só acrescenta `if [ -d / ]; then echo RODOUn; exit 1; fi` dentro ou depois da região. Em todas o `bash` executa a condição. As mesmas sondas rodaram com o `forge-mutante` de `6b0c95e` para separar o que é regressão.

## Achados
- A1 (bloqueante) bin/forge-mutante:404 · classe mascara-do-shell-esconde-codigo; requisito da decisão de 14:03 e regressão provada: o heredoc fecha em `  EOF`/`EOF `/`EOF\r` (strip), antes do shell; o apóstrofo do resto do corpo esconde o `if` novo, rc 0 (s1 a s3; rc 1 em 6b0c95e)
- A2 (bloqueante) bin/forge-mutante:447 · classe mascara-do-shell-esconde-codigo; requisito da decisão de 14:03 e regressão provada: apagar a linha incerta antes das aspas desfaz o par da string que ela abre; a aspa de fecho casa a seguinte e esconde o `if` novo, rc 0 (s5, s6; rc 1 em 6b0c95e)
- A3 (bloqueante) bin/forge-mutante:413 · classe mascara-do-shell-esconde-codigo; requisito da decisão de 14:03 e defeito provado: com `((` ou `$[` na linha, `<<"$f"` sem palavra lida não abre região; o corpo é lido como código e esconde o `if` novo, rc 0 (s7)
- A4 (recomendado) bin/forge-mutante:93 · `x="$(if ...)"` (substituição de comando entre aspas duplas) é mascarada como string e o shell a executa, rc 0 (s8); fora da lista do corte grosso: declarar no docstring ou pôr `$(` e a crase em `LINHA_INCERTA_SH`

## Detalhe dos achados
- **A1** (`bin/forge-mutante:404`). Classe: mascara-do-shell-esconde-codigo (o heredoc fecha antes do shell). É requisito da decisão do dono de 14:03 ("a região que ela abre sai não coberto") e é defeito provado, com regressão. `linha.strip() == pendentes[0]` fecha o corpo do `<<` em `  EOF`, `EOF ` ou `EOF\r`, e o do `<<-` em `  EOF` com espaços, sendo que o shell só fecha na linha exata (ou sem os tabs da esquerda, no `<<-`). O resto do corpo volta a ser lido como código: um apóstrofo dele (`it's`) se casa com a próxima aspa do arquivo e mascara o código novo depois do fecho real. As sondas s1 (`  EOF`), s2 (`EOF `) e s3 (`<<-` com `  EOF`) saem rc 0, sem `sem mutante` nem `não coberto`. Em `6b0c95e` as três saíam rc 1 (`sem mutante · run.sh:6`). O subcaso `test_forge_mutante.py:563` teve o comentário trocado para aceitar o fecho cedo. Sugestão: fechar só na linha exata (`<<`) ou com `lstrip("\t")` (`<<-`); a linha que só parece o terminador não fecha, e a região segue fora. Cada forma ganha um subcaso com a abertura na base e um mutante da guarda.
- **A2** (`bin/forge-mutante:447`). Classe: mascara-do-shell-esconde-codigo (aspa aberta na linha incerta). É requisito da decisão de 14:03 e é defeito provado, com regressão. A linha incerta é trocada por `_` antes de `mascarar_sh`. A aspa que ela abre some, e a aspa que a fecha numa linha seguinte passa a abrir uma string nova, que se casa com a próxima aspa do arquivo e mascara o código entre as duas. As sondas s5 (`eval "echo a` / `b"`, depois `echo "y"`) e s6 (`bash -c 'echo a` / `'`, depois `echo 'y'`) saem rc 0, sem aviso. Em `6b0c95e` as duas saíam rc 1. Sugestão: mascarar as aspas sobre o texto original e só depois apagar as linhas incertas; a string (ficha de `cobrir`) que começa ou termina numa linha incerta entra inteira na região incerta. Um subcaso de cada forma com a abertura na base e um mutante da guarda.
- **A3** (`bin/forge-mutante:413`). Classe: mascara-do-shell-esconde-codigo (heredoc sem palavra lida não abre região). É requisito da decisão de 14:03 e é defeito provado. `sobra` fica falso quando a linha tem `((` ou `$[`. Assim `f=X; (( 1 )) && cat <<"$f"` não abre região nenhuma, o corpo é lido como código e o apóstrofo dele mascara o `if` novo depois do `$f` (sonda s7, rc 0; já saía rc 0 em `6b0c95e`, mas a linha é nova neste delta). Sugestão: contar como `<<` sem palavra só o que vem fora de `$(( ))`/`$[ ]` na mesma linha (o trecho depois do último `))`/`]`), ou declarar o resto do arquivo incerto sempre que um `<<` seguido de aspa, `\` ou `$` não der palavra. Subcaso e mutante.
- **A4** (`bin/forge-mutante:93`). A condição em `"$(if ...)"` (substituição de comando entre aspas duplas) é mascarada como string, e o shell a executa. A sonda s8 (`x="$(if [ -d / ]; then ...; fi)"`, novo) sai rc 0. A forma não está na lista do corte grosso, o comportamento é o mesmo de antes do delta e fica junto com `trap '...'` e `ssh h '...'` da segurança: declarar no docstring, ou pôr `$(` e a crase na `LINHA_INCERTA_SH`.

## Revalidação dos achados do parecer `a6f5184`
- **A1 (aritmética que abre heredoc): resolvido.** Toda linha com `$((` ou `$[` sai incerta, e `prof` atravessa as quebras até fechar (`x=$((1 +` / `1<<EOF))` e `x=$[1 +` / `1<<EOF]` saem `não coberto: run.sh:2`, com subcaso e os mutantes M101, M103 e M109).
- **A2 (`-c`/`eval` em qualquer forma): resolvido.** A linha com `eval` ou `-\w*c` e a continuação por `\` saem incertas. As quatro formas, `eval $"..."`, `bash -c \` + quebra, `eval "true;"'...'` e `bash -c -e "..."`, têm subcaso (`não coberto: run.sh:2`) e os mutantes M102 e M106. A aspa que atravessa linha a partir dessa linha é o A2 acima.
- As specs -14 e -15 saem porque o código que elas miravam saiu, e as -16 e -17 cobrem as guardas novas (M100 a M111). Os retoques em -12 e -13 tiram os mutantes sem alvo. É consequência da mudança, como na decisão de 11:46.

Teto M14: `bin/forge-check` 1 + `bin/forge-mutante` 221 + `tests/test_forge_mutante.py` 160 + `tests/test_volta_por_delta.py` 2 = 384 linhas (`git diff --numstat --no-renames ff3936a...HEAD`), dentro de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS` foi tocado.

Saídas citadas, sem refazer: `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta` deu `Ran 126 tests ... OK`. `bin/forge-mutante --cobertura --base ff3936a` no head deu rc 0, com 35 linhas `coberta` e 5 `spec editada`, sem `sem mutante`, `apagada` nem `não coberto`. Segurança e QA têm parecer próprio.

Achados recorrentes (PA-7): a classe `mascara-do-shell-esconde-codigo` voltou pela quinta vez neste pedido (A1 a A3 acima). A linha `AR-1` de `docs/engineering/achados-recorrentes.md` passa a `vezes: 5`, `última: bin/forge-mutante:404`, neste commit.

Entregar da volta: A1, A2 e A3. Cada forma leva um subcaso de teste com a linha de abertura na base, que falha antes da correção, e o mutante da guarda nova.
