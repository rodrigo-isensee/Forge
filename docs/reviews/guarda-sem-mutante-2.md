---
tipo: review
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: a1571168d78646e8ccdd0ad3a225dfafc3775ffb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 2 (shell, isentas, tetos de T7, A5 e o PQ no `gerar_volta`)

Revalidação por delta (volta 1). Parecer anterior: `1f394b7`, sobre `43a8cc8`. O delta é `43a8cc83559f3e49abffa08447b4bfaf4a04ae6c..a1571168d78646e8ccdd0ad3a225dfafc3775ffb`. O `forge-check delta --parecer docs/reviews/guarda-sem-mutante-2.md` listou estes trechos: `bin/forge-mutante` 18-20, 89-97, 394-447, 451, 518-519 e 542; `tests/test_forge_mutante.py` 10, 511-516 e 535-554; e as specs `tests/mutantes/guarda-sem-mutante-11.json` (9-10), `-12.json` e `-13.json`. Li só esse delta. O resto da branch fica como "já lido" no parecer `1f394b7`: isentas, tetos de T7, pareamento A5, PQ no `gerar_volta`, specs antigas reescritas e o commit único. Os outros arquivos do delta são os pareceres de segurança e de QA, que não reviso.

## Achados
- A1 (bloqueante) bin/forge-mutante:399 · falso negativo: o heredoc novo de `mascarar_sh` abre e fecha onde o shell não abre nem fecha, e o código entre os dois pontos é mascarado sem aviso. São dois casos. (a) O terminador é procurado com `linha.strip()`. No `<<` o terminador tem de ser a linha exata, e no `<<-` só se tiram tabs à esquerda. Por isso `  EOF` indentado fecha o corpo antes do shell e um apóstrofo do resto do corpo engole o código seguinte. (b) Em `FICHA_SH` (linha 93), o `<<nome` dentro de `$(( ))` vira heredoc e esconde as linhas até a próxima linha igual ao nome. Prova de ponta a ponta: `if [ -f /etc/x ]; then exit 1; fi` novo sai rc 0, sem `sem mutante` nem `não coberto`, nos dois casos, e o `bash` roda a condição nos dois. Correção: comparar a linha exata no `<<` e a linha com só os tabs da esquerda tirados no `<<-`; não abrir heredoc dentro de `(( ))`, ou declarar o caso como incerto. Cada caso com um subcaso em `test_shell_por_regex...`.
- A2 (bloqueante) bin/forge-mutante:423 · requisito da decisão de 11:16 e do próprio docstring (linha 20, "texto de `-c`/`eval` com condição sai `não coberto`"): `eval $'[ -f /etc/x ] && exit 1'` e `bash -c -- '[ -f /etc/x ] && exit 1'` saem rc 0 sem `não coberto`. Só `bash -c '...'` sai certo (`não coberto: run.sh:2`). O primeiro caso escapa porque a ficha `$'...'` começa com `$` e o teste é `m[0][0] in "'\""`. O segundo escapa porque `EXECUTA_SH` não aceita o `--` antes da aspa. Correção: aceitar `$'` no teste e `(?:\s+--)?` em `EXECUTA_SH`, com os dois casos em `test_shell_que_nao_se_le_com_certeza...`
- A3 (recomendado) tests/test_forge_mutante.py:547 · numa de 8 rodadas de `tests.test_forge_mutante tests.test_volta_por_delta` saiu `FAILED (failures=1)`, e as outras 7 deram OK. Não consegui reproduzir a falha e não sei qual teste falhou. O único teste do delta que depende de tempo é o de CPU, com limite de 0,05 s (15 rodadas isoladas, todas OK). Sugestão: limite com folga maior, por exemplo 0,5 s. O retrocesso quadrático antigo levava 9 s, então a folga continua separando os dois casos. Não devolve

## Revalidação dos achados do parecer `1f394b7`
- **A1 (`#` dentro de `${...}`): resolvido.** O comentário só abre depois de espaço, `;&|()<>` ou no começo do texto. `x=${a##*/}; if [ -n "$x" ]` e `${a%%#*}` saem com a condição, e `echo a#b` não abre comentário, como no shell. Há subcaso no teste e o mutante está na spec -12.
- **A2 (`|| true  # comentário`): resolvido.** O comentário sai do lado direito antes da comparação. `cmd || true # x || exit 1` e `cmd || : #c` não contam, e `cmd || echo "#x"` conta. Há subcaso no teste.
- **A3 (`until`): resolvido.** `until` está em `CONDICAO_SH`, em `COM_CONDICAO_SH` e no docstring. `until grep -q pronto log` e `until [ -f x ]` saem como condição.
- **A4 a A8 (recomendados):** ficam como estão (decisão de 11:16). O A5 e o A7 foram tratados na volta. A regex ficou linear: com 1 MiB numa linha, 16 padrões (entre eles `"\"`, `[[ `, `[ `, `$'\'`, `'`, `<<A`, `bash -c '` e `||`) levam no máximo 1,2 s de CPU. `\'` fora de aspas agora é escape. Os aspectos de segurança (T5 e T7) são do parecer `docs/security/guarda-sem-mutante-2.md`, que eu cito sem refazer.

## O que foi conferido no `mascarar_sh` novo
- É um laço só, sem retrocesso. As aspas atravessam linhas, como no shell. A aspa solta e o heredoc sem terminador entram em `incertas`, e só saem como `não coberto: arq:L` quando caem num hunk novo (`a < h[1].stop and h[1].start <= b`, intervalo fechado contra `range`, certo). A `incertas` só é lida no `depois`, o que basta: a velha não precisa dela. Saem certos: `cat <<A <<B`, `<<-EOF` com tab, `<<<`, `$((1<<3))`, `echo "it's"`, `'a"b'`, a string em duas linhas e o `sh -ec '...'`.
- `sem_fecho` é linear (um `rfind` e um `finditer` por linha). Ele só apaga o `[` que não tem fecho depois na linha, e a condição válida não muda.
- M72 da spec -11 foi retocado para o `de` novo (`if py else (condicoes_sh(depois`). A guarda e o teste são os mesmos (decisão de 11:46).

Teto M14: `bin/forge-check` 1 + `bin/forge-mutante` 210 + `tests/test_forge_mutante.py` 140 + `tests/test_volta_por_delta.py` 2 = 353 linhas (`git diff --numstat --no-renames ff3936a...HEAD`), dentro de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS` foi tocado.

Citado, sem refazer: `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta` deu `Ran 126 tests ... OK` em 7 de 8 rodadas (A3). `bin/forge-mutante --cobertura --base ff3936a` no head deu rc 0, com 32 linhas `coberta` e 5 `spec editada`, sem `sem mutante`, `apagada` nem `não coberto`. Segurança e QA têm parecer próprio.

Achados recorrentes (PA-7): `docs/engineering/achados-recorrentes.md` está vazio. A classe "a máscara do shell esconde código real e sai rc 0" voltou neste pedido: A1 de `1f394b7`, A1 da segurança `53ff539` e o A1 acima. Pela skill, ela pede a linha `AR-1 · review · máscara do shell esconde código · R-REVIEW · vezes: 3 · última: bin/forge-mutante:399`. O brief limita este commit ao parecer, então a linha fica para a volta do autor ou para uma delegação própria.

Entregar da volta: A1 e A2, cada caso com um subcaso de teste que falha antes da correção e com o mutante da guarda nova.
