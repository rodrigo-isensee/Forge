---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: dd9190992bbd107347a9cc8c206da73694fa8b72
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-leitura-hook

Escopo: a entrega inteira (`git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 dd9190992bbd107347a9cc8c206da73694fa8b72`), com revalidação por delta desde o parecer anterior (commit 8c4b7b5, `forge-check delta --parecer`): f3e1267 (memória e teto de conferências no `conformidade`), fe14b2e (o `parecer` tira os heredocs), 8f9fbd7 (fim do heredoc como no bash, `<<-` só com tab, `expandido()`), dd91909 (corpus). O delta toca controle do Forge e foi relido inteiro, com sondas.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega muda a leitura da linha nos hooks `conformidade` e `parecer`, que garantem R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/parecer.py:360 · o parecer passou a tirar o corpo de heredoc e só o relê com dono bash/sh/zsh/dash: source /dev/stdin, . /dev/stdin e ksh com <<'EOF' e gh pr merge no corpo liberam com review reprovado; a base os recusa
- A2 (bloqueante) hooks/_comum.py:717 · no heredoc sem aspas o bash junta barra mais quebra antes de achar o fim; o hook não: cat <<X, foo\, X, cat <<Y, X, gh pr merge, Y esconde o merge, que o bash roda; o parecer libera e a base recusava

## Detalhe dos achados
**A1 (média; regressão de fe14b2e).** Evidência: `hooks/parecer.py:350` tira os corpos (`tirar_heredocs`), e `hooks/parecer.py:360` só devolve à conferência o corpo cujo dono casa `\b(bash|sh|zsh|dash)\b`. Antes, o `parecer` lia a linha inteira e o `gh pr merge` do corpo era comando. Sonda (cópias por `git archive` do HEAD e da base em `$TMPDIR`, hook real pela `Fixture` da própria cópia, com o cenário da fixture `forge-clone-pr-merge-no-corpo-de-bash-heredoc-bloqueia`, review reprovado): `source /dev/stdin <<'EOF'⏎gh pr merge feature/x --repo … --merge⏎EOF`, a mesma com `. /dev/stdin` e com `ksh` saem 0 no HEAD e 2 (R-REVIEW) na base; `bash <<'EOF'`, `cat <<'EOF' | bash` e o script gravado e rodado continuam 2.
Caminho de ataque: a sessão, por erro ou por instrução injetada em texto não confiável, mescla um PR sem review aprovado montando a linha com um leitor do stdin que não está na lista; o portão de R-REVIEW/R-QA do `parecer` é a camada local que segura esse merge. É afrouxamento de controle (vedado pelo dono, decisão de 2026-10-15 no pedido).
Correção mínima: inverter a lista, no `parecer`: o corpo é conferido como comando, a menos que a linha do dono seja só de leitores que não executam o stdin (por exemplo `cat`/`tee` para arquivo ou para `$(…)` usado como texto, sem shell nem `source`/`.`/`eval`/`exec` na linha); ou, no mínimo, incluir `source`, `.`, `ksh`, `mksh`, `fish`, `busybox` e `/dev/stdin` na lista. Mais uma fixture `-bloqueia` por forma. Esforço P. Dono: `tech-lead`.

**A2 (média; regressão no `parecer`, resíduo no `conformidade`).** Evidência: `hooks/_comum.py:716-717` compara a linha física com o delimitador. Para delimitador sem aspas, o bash remove `\`⏎ antes de procurar o fim (confirmado no bash local: `cat <<X⏎foo\⏎X⏎cat <<Y⏎X⏎echo RODOU⏎Y` imprime `fooX`, `cat <<Y` e roda `echo RODOU`). O hook fecha o primeiro heredoc no `X` que o bash junta, lê `cat <<Y` como operador e esconde a linha seguinte como corpo. Sonda: com `gh pr merge feature/x --repo … --merge` nessa linha, o `parecer` sai 0 no HEAD e 2 na base (que não tirava heredocs). No `conformidade`, com `gh repo delete d/p --yes`, sai 0 no HEAD e na base (resíduo anterior, mesma classe do R2 anterior); com marcador crítico, a rede da ADR 0011 recusa nos dois.
Caminho de ataque: o mesmo do A1 (merge sem review aprovado pelo `parecer`) e, no `conformidade`, ação sem marcador crítico escondida. A correção do R2 (8f9fbd7) fechou o fim com espaço, mas não esse caso, que também faz o hook fechar antes do bash.
Correção mínima: em `heredocs()`, para delimitador sem aspas, juntar a linha que termina em `\` ímpar com a seguinte antes de comparar com o delimitador (como o bash), ou tratar como dúvida o corpo sem aspas com `\`⏎ (recusa). Fixture `-bloqueia` nos dois hooks e o caso na tabela de `heredocs` em `tests/test_hooks.py`. Esforço P. Dono: `tech-lead`.

**Revalidação dos achados anteriores.**
- A1 anterior (orçamento): resolvido. `hooks/conformidade.py:653-672`: a memória é gravada só depois da conferência terminar (uma chamada em curso não dá acerto falso), a chave inclui corpo, pasta, nível, `so_substituicoes` e o ambiente, e o acerto devolve o ambiente que a primeira deixou; `lancador_recusado` e as perguntas já ficaram no objeto. O teto recusa pelo `barrar` (saída 2), fechando na dúvida. Sondas: a linha da fixture sai 2 em 0,17 s (antes 10,9 s); a forma com `git push origin main`, 0,28 s; 19 `cd` × 20 crases distintas (`git push`, `git -C … merge`, `gh pr merge`, `bash -c` aninhado) e 399 crases de `git push` numa linha saem 2 em no máximo 0,85 s. O teto de 400 é razoável: abaixo dele o custo medido fica bem longe do timeout de 10 s, e linhas comuns (`cd a && cd b && echo \`ls\` \`date\``, laço com duas crases) ficam em uma dezena de conferências e liberam. O teste `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento` lê o limite do `hooks.json` e exige metade dele.
- R1 resolvido: `expandido()` (`hooks/_comum.py:754-769`) trata `\` antes de `$`, crase, `\` e quebra como o bash; `\\$(`, `$\`⏎`(` e `\\` mais crase recusam; `\$(x)` e três barras continuam literais e liberam.
- R2 resolvido nos casos do parecer anterior: ` X`, `X ` e `<<-X` com espaços não fecham, e `<<-` com tab fecha; o resto da linha volta a ser conferido (sondas saem 2 no HEAD e 0 na base). O caso do A2 é outro caminho para o mesmo desencontro.
- R3 (HOOK-N4) segue como estava, fora deste lote.

**Recomendações (fora do bloco; resíduos anteriores à entrega).**
- R4. `hooks/conformidade.py:732` e `:1366` têm a mesma lista de donos do A1: `source /dev/stdin`, `. /dev/stdin` e `ksh` com `gh repo delete` no corpo liberam no HEAD e na base; com marcador crítico a rede recusa. A correção do A1 vale para os três lugares, de preferência numa função única em `hooks/_comum.py`.
- R5. `eval "$(cat <<'EOF'⏎gh pr merge …⏎EOF⏎)"` libera no `parecer` no HEAD e na base: o corpo vira comando pelo `eval`. Pode entrar na mesma correção do A1 (dono com `eval` na linha).
- O fragmento do changelog e `docs/hooks.md:94-95` descrevem o fim do heredoc como no bash; com o A2 corrigido, o texto passa a valer também para a barra no fim da linha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta --parecer`, leitura do diff, sondas do hook real em cópias por `git archive` do HEAD e da base em `$TMPDIR`, bash local com comandos inofensivos (`echo`) para confirmar a leitura do heredoc. `gitleaks`, `zizmor` e `actionlint` não se aplicam (sem segredo, workflow ou dependência na entrega). Nada foi instalado, nada saiu da máquina e nada foi gravado fora de `$TMPDIR`, além deste parecer.
