---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: a437574de2fddeb2f2a40f76b69bb4b5868f5d6a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-leitura-hook

Escopo: a entrega inteira (`git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 a437574de2fddeb2f2a40f76b69bb4b5868f5d6a`), com revalidação por delta desde o parecer anterior (commit dd91909, `forge-check delta --parecer`): 570d684 (barra no fim da linha no heredoc sem aspas), 33f003a (lista positiva `corpo_so_lido` em `hooks/_comum.py`, usada no `parecer` e nos dois lugares do `conformidade`), 61e4a00 (orçamento por caracteres e por tempo), a437574 (docs). O delta toca controle do Forge e foi relido inteiro, com sondas.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega muda a leitura da linha nos hooks `conformidade` e `parecer`, que garantem R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/_comum.py:800 · o dono do heredoc é só a linha física do operador: cat <<'EOF' | com bash depois do fim, bash \ com <<'EOF' na linha seguinte, e done \ antes do << escondem o gh pr merge do corpo, que o bash roda; o parecer libera com review reprovado e a base recusava

## Detalhe dos achados
**A1 (média; regressão de 33f003a e fe14b2e no `parecer`).** Evidência: `hooks/_comum.py:800-802` grava como dono só a linha física que contém o `<<`, e `hooks/_comum.py:845` (`corpo_so_lido`) decide por ela; `hooks/parecer.py:360` deixa o corpo fora da conferência quando essa linha só tem leitores. No bash, quem consome o heredoc pode estar noutra linha física: o pipeline continua depois da linha do delimitador (`cat <<'EOF' |`⏎corpo⏎`EOF`⏎`bash`), a continuação com barra põe o programa antes do operador (`bash \`⏎`<<'EOF'`; `while read -r l; do eval "$l"; done \`⏎`<<'EOF'`) ou depois dele (`cat <<'EOF' | \`⏎`bash`⏎corpo). Confirmado no bash local com `echo` no corpo: as quatro formas rodam o corpo. Sonda (cópias por `git archive` do HEAD e da base em `$TMPDIR`, hook real pela `Fixture` da própria cópia, cenário da fixture `forge-clone-pr-merge-no-corpo-de-ksh-heredoc-bloqueia`, review reprovado, `gh pr merge feature/x --repo … --merge` no corpo): as quatro saem 0 no HEAD e 2 (R-REVIEW) na base. No `conformidade`, `cat <<'EOF' | \`⏎`bash`⏎`gh repo delete d/p --yes` sai 0 no HEAD e 2 na base; as outras já saíam 0 na base (resíduo), e o marcador crítico da ADR 0011 recusa `bash \`⏎`<<'EOF'` com `git push origin main` nos dois.
Caminho de ataque: o mesmo do A1 anterior. A sessão, por erro ou por instrução injetada num texto não confiável, mescla um PR sem review aprovado e monta a linha de modo que o programa que roda o corpo fique fora da linha física do `<<`. O `parecer` é a camada local que segura esse merge, e ele está mais frouxo que na base, o que a decisão do dono de 2026-10-15 veda.
Correção mínima: em `tirar_heredocs`, o dono passa a ser o comando lógico inteiro: da linha física do operador, recuando enquanto a anterior acaba em `\` ímpar, até o fim do pipeline ou da lista depois do corpo (enquanto a linha do dono, ou a que segue o delimitador, acaba em `|`, `|&`, `&&`, `||` ou `\`). Ou, fechando na dúvida, o corpo vale como comando quando a linha do dono acaba em `|`, `|&` ou `\`, ou quando a linha física anterior acaba em `\`. A forma mais simples também serve: aplicar `corpo_so_lido` à linha inteira sem os corpos. Mais uma fixture `-bloqueia` por forma nos dois hooks e os casos em `test_corpo_de_heredoc_so_lido_pela_lista_positiva`. Esforço P. Dono: `tech-lead`.

**Revalidação dos achados anteriores.**
- A1 anterior (lista de donos): resolvido para a linha física. `source /dev/stdin`, `. /dev/stdin`, `ksh` e `eval "$(cat <<'EOF'` (R5) com `gh pr merge` no corpo saem 2 no `parecer` do HEAD; a lista é positiva e única (`hooks/_comum.py:812-862`), e `git -c`, lançador, laço e caminho (`/bin/cat`) contam como quem roda o corpo. A R4 (os dois lugares do `conformidade`) foi atendida pela mesma função: `ksh` com `gh repo delete` sai 2 no HEAD e 0 na base. O que ficou aberto é o A1 acima, a mesma classe por outra linha física.
- A2 anterior (barra no fim da linha): resolvido. `hooks/_comum.py:717-723` junta a linha que acaba em `\` ímpar com a seguinte antes de comparar com o delimitador, só sem aspas; `cat <<X`⏎`foo\`⏎`X`⏎`cat <<Y`⏎`X`⏎`gh pr merge …`⏎`Y` sai 2 no `parecer`, e `foo\\` (barra par) fecha e libera. Os casos da tabela de `heredocs` em `tests/test_hooks.py` cobrem `<<-` com tab e delimitador entre aspas.
- A1 do review (orçamento por caracteres): resolvido. `hooks/conformidade.py:670-686` soma os caracteres conferidos e o tempo, e o teto recusa pelo `barrar` (fecha na dúvida). Sondas: as linhas do teste (20 `cd`, 19 crases de 8 e 20 KB) saem 2 nos dois hooks, em 3,6 s somando quatro linhas no `parecer` e 1,4 s no `conformidade`, com montagem do repositório incluída.
- Risco novo de falso positivo: `git commit -m "$(cat <<'EOF' … EOF)"` com 200 mil caracteres e `echo` de 100 mil caracteres liberam; a recusa só aparece acima de cerca de 300 mil caracteres numa linha, e a mensagem manda gravar o texto num arquivo. É aceitável. O prazo de 3 s sob carga (a suíte em paralelo, R-TETO) também falha fechado: no pior caso, uma linha comum é recusada e a sessão a repete. O prazo é conferido só no começo de cada conferência, e o teto de caracteres limita o custo de cada uma, então a decisão continua saindo antes do timeout de 10 s.
- R1 e R2 anteriores seguem resolvidos. A R3 (HOOK-N4) fica fora deste lote.

**Recomendações (fora do bloco).**
- R6. `cat <<'EOF' > x.sh`⏎`gh pr merge …`⏎`EOF`⏎`bash x.sh` saía 2 em dd91909 e na base e agora sai 0, porque o `cat` é leitor. Isso está no limite documentado em `docs/hooks.md` (script gravado e executado depois), mas é recuo. Com a forma simples da correção do A1 (a linha inteira), o `bash` da linha faz o corpo voltar a ser conferido.
- R7. Resíduo da base, fora da regressão: `eval "$(`⏎`cat <<'EOF'`⏎…⏎`)"` e `bash -c "$(`⏎`cat <<'EOF'`⏎…⏎`)"` saem 0 no HEAD e na base, e `cat <<'EOF' |`⏎`git push origin main`⏎`EOF`⏎`bash` sai 0 no `conformidade` nos dois. A correção do A1 pelo comando lógico ou pela linha inteira fecha esses casos também.
- R8. `sort --compress-program=…` executa um programa com o texto ordenado: tire o `sort` da lista de leitores ou recuse a opção. Risco baixo, porque o programa só roda com temporários.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta --parecer`, leitura do diff, sondas do hook real em cópias por `git archive` do HEAD e da base em `$TMPDIR`, bash local com comandos inofensivos (`echo`) para confirmar a leitura. `gitleaks`, `zizmor` e `actionlint` não se aplicam (a entrega não tem segredo, workflow nem dependência). Nada foi instalado, nada saiu da máquina e nada foi gravado fora de `$TMPDIR`, além deste parecer.
