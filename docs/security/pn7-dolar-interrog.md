---
tipo: revisao-seguranca
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: 9001a894b1b08fd016ce3ef4c5539e1bd2c1f1ab
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn7-dolar-interrog (H1-1 da P-N7, `$?` modelado, volta 3)

Escopo: revalidação por delta do parecer anterior (`1e15939`, sobre `3b412fa`), com `forge-check delta --parecer` e `git diff 4514fdd..9001a89` (`SUBSTITUICAO` e a recusa nova em `construcao_nao_modelada`, a condição K3 em `simples_da_gramatica`, a emenda H1-1 da ADR 0011, `docs/hooks.md:97`, duas fixtures, propriedade e mutantes). Como o delta toca um controle do Forge, reli inteira `construcao_nao_modelada` (`hooks/_comum.py:1452`), em especial os limites do comando simples (`hooks/_comum.py:1530`). Também refiz a sonda do A1 do review `73bf7fb`, que a minha rodada anterior não pegou. Desta vez varri a família inteira, todo parêntese que o bash não trata como fim de comando, e não só o caso do review. Método: leitura estática e sondas locais. Cada sonda roda o hook do commit revisado e o da base 31257c1, sobre uma cópia das fixtures da branch com o `command` trocado. Para ver o que o bash executa, usei o bash 5.3 com um `git` falso no `PATH` que só imprime o argv. Sem rede, sem `git` nem `gh` reais.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): o diff afrouxa a lista de construções não modeladas dos hooks `conformidade` e `parecer` (gatilho `hooks/`). O PR precisa do rótulo `afrouxa-regra`, que só o dono aplica (`R-CONFORMIDADE`).
- Sem dependência nova, workflow, segredo nem custo (`R-CUSTO`).

## Achados
- A5 (recomendado) hooks/_comum.py:1444 · a saída do echo com $? ainda vira código por `(…) | sh`, `exec >` e afins; o mesmo texto sem $? já passava na base; segue no cartão HOOK-SAIDA-CODIGO
- A6 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:43 · o critério de reversão deve comparar com o mesmo texto sem $?; segue no cartão HOOK-SAIDA-CODIGO
- A7 (bloqueante) hooks/_comum.py:1437 · classe A1 do review (parêntese tido como fim de comando): o extglob escapa de SUBSTITUICAO; `shopt -s extglob nullglob` e, na linha seguinte, `IFS=0; git push origin @(zz)echo x$?main` dá rc 0 e o bash roda git push origin x main
- A8 (recomendado) hooks/_comum.py:1530 · fora do diff, desde a base: depois de `shopt -s extglob nullglob`, `git push origin @(zz) --no-verify y` e `git push origin @(zz)echo main` dão rc 0 no conformidade; o R-VERIFY e o R-MAIN não veem o que vem depois do parêntese

## Detalhe dos achados
**Revalidação da sonda do A1 do review `73bf7fb`: resolvida para as formas de substituição.** No `conformidade` (agente `forge:tech-lead`), todas dão rc 2 no 9001a89, com `$? com substituição de comando` (a crase com `crase`):
- `IFS=0; git push origin $(true) echo x$?main`;
- a mesma com `export I"FS"=0`, com `IFS=1` e `$(false)`, com crase, com `$((0))`, com `<(true)` e com `>(true)` antes do `$?`.

Também dão rc 2 as construções aninhadas antes do token, nas quatro posições:
- argumento de `git push`: `$(echo $(true))`, `$(echo "$(true)")` e `<(echo $((0)))`;
- pipe: `echo $(echo $(true)) git push origin x$?main | sh`;
- redireção: `echo $( (true) ) git push origin x$?main > s.sh; sh s.sh` e `echo >(cat $(true)) git push origin x$?main >> s.sh`;
- programa: `IFS=0; (git push origin x$?main)`.

No `parecer`, as mesmas formas com `gh pr merge` (`$(true)`, crase, `$((0))`, `<(true)`, `>(true)` e `$(echo $(true))` antes de `echo x$?y`) dão rc 2. As formas `| sh` e `> s.sh` dão rc 0 no `parecer`, mas também na base sem `$?`: é a classe do A5. Na chamada com heredoc, o `conformidade` recusa as formas com extglob (heredoc gravado e programa não modelado) e o `parecer` recusa o `gh pr merge` com extglob (branch `@` sem parecer). Legítimos com rc 0: `git push origin x; echo rc=$?`, `printf 'rc=%s\n' $?`, `echo "rc=$?"` e o `$?` numa linha própria. `git push origin main; echo rc=$?` segue com rc 2. `python3 -m unittest tests.test_hooks.CodigoDeSaida` roda 3 testes, OK.

**A7 (bloqueante; classe: fronteira do comando simples com parênteses, a mesma do A1 do review; lista negativa numa trava, AR-3).**
- Evidência: `SUBSTITUICAO` (`hooks/_comum.py:1437`) só lista `$(`, `<(`, `>(` e a crase. Os limites do comando simples continuam contando todo `(` e `)` fora de aspas (`hooks/_comum.py:1530`). Com `extglob` ligado, `@(…)`, `?(…)`, `*(…)`, `+(…)` e `!(…)` são parte de uma palavra, não fim de comando. O `$?` que vem depois do `)` cai num "comando" que começa por `echo` e passa por `codigo_de_saida_vale`, mas no bash ele é argumento do `git push`.
- Sondas no 9001a89, todas com rc 0 no `conformidade` e rc 2 na base 31257c1. Todas começam com `shopt -s extglob nullglob` numa linha, seguido de:
  - `IFS=0; git push origin @(zz)echo x$?main`
  - `IFS=0; git push origin *(zz)echo x$?main`
  - `IFS=0; git push origin !(*)echo x$?main`
  - `IFS=0; git push origin x@(zz)echo x$?main`
  - `IFS=0; git push origin @(zz)echo --no-verify$?y`

  Só `shopt -s extglob` (sem `nullglob`) seguido de `IFS=0; git push origin ?(zz)echo x$?main` também dá rc 0. No bash 5.3, o `shopt` de uma linha vale para a linha seguinte, também por `eval`, como o Bash da sessão roda. A primeira sonda executa `git push origin x main` e a última executa `git push origin --no-verify y`.
- Por que bloqueia: o requisito da emenda H1-1 (`docs/hooks.md:97`, ADR 0011:43) é que fora de aspas o `$?` só vale como argumento de `echo` ou de `printf`. Aqui ele é aceito como argumento do `git push`, e o critério de reversão da emenda é atingido: o `$?` muda o que o bash roda numa ação crítica. É a classe que o time já tratou como bloqueante no A1 do review `73bf7fb`. Severidade baixa quanto à capacidade nova: o mesmo efeito sem `$?` já passa na base (A8), e o envio à `main` ainda esbarra no pre-push e na proteção do servidor.
- Correção mínima (dono: tech-lead, esforço P): trocar a lista de aberturas por uma regra positiva. Com um `$?` fora de aspas, recusar o texto que tenha qualquer `(` ou crase, por exemplo `SUBSTITUICAO = re.compile(r"[(`]")`. Isso cobre de uma vez `$(`, `$((`, `<(`, `>(`, `@(`, `?(`, `*(`, `+(`, `!(`, o subshell `( … )`, `a=( … )` e `f()`. O custo para os legítimos é pequeno: só o `$?` solto em texto com parêntese, como `git commit -m 'fix (x)'; echo rc=$?`, passa a recusar, e o contorno `echo "rc=$?"` continua valendo. Na matriz `CodigoDeSaida`, a dimensão nova é o parêntese que não fecha comando: as cinco formas de extglob, com `shopt -s extglob` e com `shopt -s extglob nullglob` na linha anterior, nas posições argumento de `git push`, argumento antes de `--no-verify`, pipe e redireção. Isso entra junto com uma fixture `bloqueia` da primeira sonda e com o mutante que volta à lista antiga.

**A8 (recomendado; fora do diff, anterior à branch; classe: parêntese de extglob esconde o resto do comando).**
- Evidência: com `shopt -s extglob nullglob` na linha anterior, estas sondas dão rc 0 na base 31257c1 e no 9001a89: `git push origin @(zz)echo main`, `git push origin @(zz) echo main` e `git push origin @(zz) --no-verify y`. O bash roda `git push origin main` e `git push origin --no-verify y`, porque o padrão sem arquivo some com `nullglob`. O R-MAIN e o R-VERIFY do `conformidade` param de ler no `(` (`hooks/_comum.py:1530`). O `--no-verify` antes do `@(` é recusado, assim como o `+(…)`, que é lido como `+` de força.
- Caminho de ataque: o próprio agente, por erro ou por injeção de prompt, monta o push assim e pula o pre-push num envio para `melhoria/*`. Na `main`, o pre-push e a proteção do servidor seguem barrando. Severidade média para o R-VERIFY e baixa para o R-MAIN.
- Correção mínima (dono: tech-lead, esforço P), em cartão próprio, HOOK-EXTGLOB, porque é anterior ao diff: em `construcao_nao_modelada`, com marcador crítico, tratar como não modelado o `(` fora de aspas logo depois de `@`, `?`, `*`, `+` ou `!`, e também o `shopt` na mesma chamada que tem ação crítica. A correção do A7 não cobre este caso, porque aqui não há `$?`.

**A5 e A6:** sem mudança desde `1e15939`. A classe da saída de comando que vira código segue no cartão HOOK-SAIDA-CODIGO. O delta não toca a regra do pipe (`hooks/_comum.py:1444`). A emenda (ADR 0011:43) ganhou só a lista de substituições.

**Item 1 da ADR 0011 inalterado:** `hooks/conformidade.py`, `hooks/conformidade.json` e `hooks/parecer.py` não diferem da base. O ramo do papel só de leitura (`hooks/conformidade.py:667`) não chama a regra do `$?`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` está no PATH, mas não foi usado (o diff não toca shell). `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente (lacuna registrada). O diff não tem segredo, dependência nem workflow. O A7 repete a classe AR-3 de `docs/engineering/achados-recorrentes.md`. A linha não foi atualizada aqui porque a delegação limita o commit ao parecer.
