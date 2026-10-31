---
tipo: revisao-seguranca
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: cec2b422dccee2c4c9009e5677aac209b351763a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn7-dolar-interrog (H1-1 da P-N7, `"$?"` modelado, voltas 4 a 7)

Escopo: revalidação por delta do parecer anterior (`836ee2a`, sobre `9001a89`). Usei `forge-check delta --parecer` e `git diff 836ee2a..cec2b42`. O delta segue as decisões do dono de 2026-10-30 (05:14, 06:27 e 07:45): o `$?` vale só entre aspas duplas e, fora de aspas, volta ao comportamento da base 31257c1. Saem `codigo_de_saida_vale`, `codigo_de_saida_solto` e `SUBSTITUICAO`. Entram sondas de extglob e de `>&`, `2>&`, `<&` e `>|` como fixtures `-bloqueia`, e o texto da ADR 0011, de `docs/hooks.md`, do changelog.d e das docstrings ganha a condição do marcador crítico. Como o delta toca um controle do Forge, reli o diff inteiro da branch contra a base em `hooks/` (só `hooks/_comum.py`, 10 linhas a mais e 4 a menos): a nova alternativa de `construcao_nao_modelada` (`hooks/_comum.py:1457`) e o `replace("$?", "")` de `simples_da_gramatica` (`hooks/_comum.py:1574`). Método: leitura estática e sondas locais. Cada sonda roda o hook do commit revisado e o da base 31257c1 sobre uma cópia das fixtures da branch com o `command` trocado, e o bash 5.3.9 roda com um `git` falso no `PATH` que só imprime o argv. Sem rede, sem `git` nem `gh` reais.

## Gatilhos
- Controles do Forge (`R-SEGURANCA`): o diff afrouxa a lista de construções não modeladas dos hooks `conformidade` e `parecer` (gatilho `hooks/`). O PR precisa do rótulo `afrouxa-regra`, que só o dono aplica (`R-CONFORMIDADE`).
- Sem dependência nova, workflow, segredo nem custo (`R-CUSTO`).

## Achados
- A5 (recomendado) hooks/_comum.py:1457 · a saída de um echo com "$?" ainda vira código por `| sh` (`echo "git push origin main $?" | sh` dá rc 0); o mesmo texto sem $? já passava na base; segue no cartão HOOK-SAIDA-CODIGO
- A6 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:43 · o critério de reversão deve comparar com o mesmo texto com o decimal literal no lugar do "$?" (ver A9); segue no cartão HOOK-SAIDA-CODIGO
- A8 (recomendado) hooks/_comum.py:482 · fora do diff, desde a base: com extglob ligado, `git push origin @(zz) --no-verify y` passa no conformidade; segue no pedido HOOK-EXTGLOB, já decidido pelo dono
- A9 (recomendado) hooks/_comum.py:1457 · `IFS=0; git push origin x$(echo "$?")main` dá rc 0 e o bash roda push de x e main; a base dá rc 0 com `x$(echo 0)main` e `$(echo main)`: lacuna antiga do caminho montado (docs/hooks.md:93), sem capacidade nova

## Detalhe dos achados
**A7 do parecer `836ee2a`: resolvido.** No `conformidade` (agente `forge:tech-lead`), todas estas sondas dão rc 2 no cec2b42 e na base, com `$? com ação crítica`. Todas começam com `shopt -s extglob nullglob` numa linha, seguido de:
- `IFS=0; git push origin @(zz)echo x$?main`, e o mesmo com `*(zz)`, `!(*)` e `x@(zz)`;
- `IFS=0; git push origin @(zz)echo --no-verify$?y`.

Com `+(zz)`, o hook recusa pelo R-VERIFY. Só com `shopt -s extglob`, `IFS=0; git push origin ?(zz)echo x$?main` também dá rc 2. As fixtures `pn7-dolar-interrog-extglob-antes-do-codigo-bloqueia` e `pn7-dolar-interrog-extglob-zz-antes-do-codigo-bloqueia` guardam a primeira sonda.

**A2 do review `557d12c` e A1 do review `73bf7fb`: resolvidos nos dois hooks.** Com `IFS=0` e o `$?` solto depois de `x >&2`, `x 2>&1`, `x <&0`, `x >| f` e `$(true)` no argumento de `git push`, o `conformidade` dá rc 2, igual à base. Também dá rc 2 com `export I"FS"=0; git push origin x$?main`. No `parecer`, com `gh pr merge` no lugar do push (extglob, `>&2`, `x$?y`, `"$?"` como alvo, `x$(echo "$?")y`), todas dão rc 2. O alvo `"$?"` cai em branch inexistente: o git não aceita `?` em nome de ref, então ninguém cria essa branch.

**`$?` fora de aspas igual à base.** Rodei as 45 fixtures `pn7-dolar-interrog-*` no cec2b42 e na base. Todas as `-bloqueia` dão rc 2 nos dois, e todas as `-como-na-base-libera` dão rc 0 nos dois. As que só passam no head (`push-echo-rc-entre-aspas`, `commit-heredoc-cita-merge-echo-rc` e `commit-k3-cita-merge-echo-rc`, nos dois hooks) têm o `$?` entre aspas duplas. As sondas avulsas dão o mesmo rc no head e na base:
- `git push origin x; echo rc=$?`: rc 2;
- `git push origin main; echo rc=$?`: rc 2, pelo R-MAIN;
- `git commit -m x; echo rc=$?`: rc 0;
- `IFS=0; git push origin x$?main`: rc 2;
- `gh pr merge feature/x; echo rc=$?`: rc 2.

Na chamada com heredoc, `echo rc=$?` depois de `git commit -F -` dá rc 0 nos dois.

**`"$?"` entre aspas duplas não monta programa, caminho nem branch.** No bash, `IFS=0; git push origin "x$?main"` e `x"$?"main` rodam `git push origin x0main`, uma palavra só. `git push "$?" main` e `git push origin "$?" --no-verify` seguem recusados pelo R-MAIN e pelo R-VERIFY. `git push origin x --no-verify"$?"` passa, mas o bash entrega `--no-verify0`, que não é a opção. `git "$?" push origin main` passa, mas o bash roda `git 0 …`, e o alias `0` precisa de configuração gravada antes ou de `-c alias.0=…`. Esta última forma passa, mas `git -c alias.zz="push origin main" zz` também passa na base (cartão N-HOOK1). A redução da gramática não abre outro `$`: com `"$$?"`, `"$$??"` e `"$?$x"`, o `$` que sobra recusa (`hooks/_comum.py:1574`). Os casos `${?}`, `$#`, `$@`, `$1`, `$x`, `$'…'` e `$"…"` seguem fora (propriedade `CodigoDeSaida`).

**A9 (recomendado; classe: substituição de comando fora de aspas no argumento crítico, anterior à branch).**
- Evidência: o `"$?"` dentro de `$(…)` vale (`hooks/_comum.py:1457`), mas a saída da substituição fora de aspas é dividida pelo `IFS`. No head, estas duas formas dão rc 0, e o bash roda `git push origin x main`:
  - `IFS=0; git push origin x$(echo "$?")main`
  - `IFS=0; git push origin x$(("$?"))main`
- Na base, o mesmo efeito sem `$?` também dá rc 0: `x$(echo 0)main`, `x$((0))main` e `git push origin $(echo main)`. O `"$?"` só troca um `0` literal por um decimal de 0 a 255, então não dá capacidade nova. A lacuna é a do caminho montado em tempo de execução, já registrada (`docs/hooks.md:93`). A `main` segue protegida pelo pre-push e pelo servidor, de modo que, pelo item 3 da ADR 0011, isso não reprova.
- Por que registro: lido ao pé da letra, o critério de reversão da emenda (ADR 0011:43, `"$?"` que muda o que o bash roda numa ação crítica) é atingido por essa sonda. Severidade informativa quanto ao diff.
- Correção mínima (dono: tech-lead, esforço P), no cartão HOOK-SAIDA-CODIGO, junto com o A6: dizer no critério que a sonda conta só quando o mesmo texto com o decimal literal no lugar do `"$?"` é recusado. Para quem quiser fechar a classe antiga: com marcador crítico, recusar `$(` e `$((` fora de aspas numa palavra de `git push` ou de `gh pr merge`. Isso fica num cartão próprio, porque aperta a base e pede o dono.

**A5 e A6:** sem mudança de classe desde `1e15939`. Com o `$?` solto de novo recusado, o A5 só sobra com o `"$?"` entre aspas, e o mesmo texto sem `$?` já passava na base (`docs/hooks.md`, limitação do pipe para shell).

**A8:** fora do diff e inalterado (o `(` do extglob segue contando como fim de comando nos limites do comando simples). O dono decidiu corrigir no pedido HOOK-EXTGLOB, na 0.30.8.

**Teto de fixtures fora do corpus `bash -n` (8 para 10):** conferi a lista excluída no cec2b42. São 9 fixtures: as 7 da base mais as duas de extglob, que o `bash -n` não aceita porque não roda o `shopt` da primeira linha. A folga de 1 fica igual à da base, e nenhuma fixture de recusa nova saiu do corpus por outro motivo. A mudança está em `tests/test_hooks.py:1793`.

**Item 1 da ADR 0011 inalterado:** `hooks/conformidade.py`, `hooks/conformidade.json` e `hooks/parecer.py` não diferem da base. O papel só de leitura passa por `gramatica_de_leitura` e não chama `construcao_nao_modelada` (`hooks/conformidade.py:667`). Tanto a função quanto o texto da emenda (ADR 0011:43) dizem que ele segue recusando `echo $?`.

**Textos (PA-7, AR-9):** nenhum arquivo do diff, fora dos pareceres, traz as frases antigas: "recusa em todo lugar" sem a condição do marcador crítico, "segue recusado" ou "argumento de `echo` ou". O nome do teste `test_codigo_fora_de_aspas_recusa_em_todo_lugar` ficou, mas a docstring dele restringe o domínio ao marcador crítico. Isso não muda comportamento.

**Mutantes:** a spec `tests/mutantes/pn7-dolar-interrog.json` cobre as duas guardas novas: D1 e D2 em `hooks/_comum.py:1457`, D3 e D4 em `hooks/_comum.py:1574`. `python3 -m unittest tests.test_hooks.CodigoDeSaida` roda 3 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` está no PATH, mas não foi usado, porque o diff não toca shell. `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente (lacuna registrada). O diff não tem segredo, dependência nem workflow. A classe AR-3 de `docs/engineering/achados-recorrentes.md` (lista negativa numa trava) não volta: a lista de aberturas saiu, e a regra nova é positiva (só o `"$?"`).
