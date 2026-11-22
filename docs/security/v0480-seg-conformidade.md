---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: bf57b17e42a1c6019ac7f4c721f9f4900c51cc4e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E113.13, revalidação da 2ª volta E113.11 do hooks/conformidade.py)

Revalidação por delta (`forge-check parecer delta`, intervalo `14696864..bf57b17e`). No domínio: `hooks/conformidade.py` (`alcance_da_troca` com o primeiro comando do subshell, a pasta de fora de cada `( … )` no `conferir_partes`, `valor_de_fora` e a cópia recursiva no `origem_do_git_no_opaco`), 33 fixtures novas e `tests/test_conformidade_seg_v0480.py`. Fora do domínio, não relidos: changelog, `docs/hooks-fixtures.md`, spec de mutante e `tests/pesos-d4.json`. A rodada anterior (parecer 6c1e911f sobre 14696864) está no git.

Gatilhos: guarda de controle (hook conformidade), R-MAIN, escrita no diretório do git.

Método: 98 sondas minhas (S1 a S10 de novo, 64 variações e 24 de apoio) e as 38 do autor, com o montador das fixtures (`tests/test_hooks.py`), na cabeça e na base 14696864, papel de implementação de uma stack salvo indicação. A semântica do bash (`cd` em `&` e em pipe, `cd -`, `popd`) e do `cp` (`--recur`, `--arch`, `-t` colado) foi conferida num repositório descartável. S7, a prova no bash do A3, fica no parecer anterior. O teste novo `tests/test_conformidade_seg_v0480.py` passa (11 testes). A suíte inteira roda só no CI.

## Achados anteriores
- A3 (troca de branch depois de `exit` ou `exec` no subshell): **fechado**. S1 a S6 recusam. As variações também recusam: `if …; then exit 0; fi;`, quebra de linha, espaços, `builtin exit`, `( ( … ) )`, `checkout -b` e `git merge develop`, todas liberadas na base. O corpus segue livre: `(git switch -c x) && git push origin`, `(exit 0) && (git switch -c x) && …` e `(git switch -c x && git add -A) && …`.
- A4 (`cd` explícito dentro de `( … )`): **fechado** para o `( … )`. S7 a S10 recusam, e também quebra de linha, `2>/dev/null`, `!`, `( … ; )`, `time (…)`, `( (cd /tmp); … )` e `(cd /tmp && (cd /))`. `(cd docs && ls) && git status` segue livre. A dimensão "escopo do subshell" continua aberta pelos subshells implícitos (A6).
- A5 (cópia recursiva para opaco): **parcial**. Recusam `-rT`, `-Tr`, `-rv -T`, `-dR`, `-a`, `--recursive`, `--archive`, `-t "$X"`, `--target-directory[=]`, `/bin/cp`, `command cp`, `env cp`, `$X` sem aspas, `"$X"/`, `"$X/."` e `Y=$X`. Ficam livres as abreviações longas do GNU e o `-t` colado (detalhe). O corpus (`mktemp -d`, `d=docs`, `"$X/sub"`, `cp ev/a "$X"`, `"$TMPDIR/x"`) segue livre.

## Achados
- A6 (bloqueante) hooks/conformidade.py:2286 · `cd` em subshell implícito vaza para fora: `cd /tmp & git push origin`, `cd /tmp | true; git push origin`, `true | cd /tmp; …`, `cd /tmp && true & …`, `cd /tmp |& true; …` e `cd /tmp & git merge develop` na main passam; o bash roda o push e o merge na main
- A7 (bloqueante) hooks/conformidade.py:2467 · A volta de pasta não é seguida: `cd /tmp; cd -; git push origin`, `cd /tmp; cd ~-; …` e `pushd /tmp; popd; …` na main passam; o hook confere o push em /tmp e o bash o roda no projeto, na main
- A5 (recomendado) hooks/conformidade.py:1861 · Cópia para opaco ainda livre: `cp --recur -T ev "$X"`, `cp --arch ev/. "$X"` (abreviação longa do GNU), `cp -rt"$X" ev`, `cp -t"$X" ev/config`, `cp --targ "$X" -r ev` e `cp --target-dir "$X" ev/config` (alvo colado ou abreviado, hooks/conformidade.py:1851)
- A8 (recomendado) hooks/conformidade.py:1174 · Extração para opaco sem resto passa, como a cópia recursiva antes do A5: `tar -xf a.tar -C "$X"`, `unzip -o a.zip -d "$X"` e `rsync -r ev/ "$X"`; o conteúdo do pacote pode ter `config` ou `hooks/`

## Sondas
- S1 · na main: `(exit 0; git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S2 · na main: `(exec true; git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S3 · na main: `(true || exit 0; git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S4 · na main: `(exit 0 && git switch -c x) && git push origin` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S5 · na main: `(exit 0; git switch -c x) && git reset --hard HEAD~1` · espera: código 2, R-REVIEW · obtido: 2 R-REVIEW (base 0)
- S6 · na main, papel forge:tech-lead: `(exit 0; git switch homolog) && git merge homolog` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S8 · na main: `(cd /tmp); git push origin` e `(cd /tmp) && git push origin` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S9 · na main: `(cd /) ; git merge develop` · espera: código 2, R-MAIN · obtido: 2 R-MAIN (base 0)
- S10 · na main: `(cd /tmp; true); git reset --hard HEAD~1` · espera: código 2, R-REVIEW · obtido: 2 R-REVIEW (base 0)
- S11 · na main: `cd /tmp & git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S12 · na main: `cd /tmp | true; git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S13 · na main: `cd /tmp & git merge develop` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S14 · na main: `cd /tmp | cat` + quebra + `git reset --hard HEAD~1` · espera: código 2, R-REVIEW · obtido: 0 (cabeça e base)
- S15 · na main: `cd /tmp && true & git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S16 · repositório descartável na main: `(cd /tmp & wait; pwd)` e `(cd /tmp | true; pwd)` · espera: a pasta do repositório · obtido: a pasta do repositório nas duas
- S17 · na main: `cd /tmp; cd -; git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S18 · na main: `cd /tmp; cd ~-; git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S19 · na main: `pushd /tmp; popd; git push origin` · espera: código 2, R-MAIN · obtido: 0 (cabeça e base)
- S20 · repositório descartável: `bash -c 'cd /tmp; cd - >/dev/null; pwd'` e `bash -c 'pushd /tmp >/dev/null; popd >/dev/null; pwd'` · espera: a pasta do repositório · obtido: a pasta do repositório nas duas

## Detalhe dos achados
**A6.** Evidência: hooks/conformidade.py:2286. O contexto recebe a pasta devolvida pelo `segmento` qualquer que seja o sinal depois do comando. O A4 só restaura a pasta no `)`. O bash, porém, roda num subshell também a lista que termina em `&` e cada lado de um pipe (`|`, `|&`), e o `cd` lá dentro não muda a pasta do resto da linha (S16).

Caminho de ataque: na `main`, o agente escreve `cd /tmp & git push origin`. O hook confere o push em `/tmp`, fora de qualquer repositório, e libera. O bash roda o push no projeto, na `main`. O mesmo acontece com `git merge develop` (R-MAIN) e `git reset --hard` (R-REVIEW). A base faz igual, mas é a dimensão "escopo do subshell" do A4 que a volta fechou só pela metade. Severidade: alta.

Correção mínima: a lista and-or que termina em `&` e cada comando de um pipeline (`|`, `|&`, nos dois lados) rodam com uma cópia da pasta e das branches, como o `( … )` do A4. Depois do `&` ou do fim do pipeline, a pasta volta à de antes. Fixtures: S11 a S15 recusam. `cd docs & ls` e `cd /tmp && git status` seguem livres. Esforço: P. Dono: quem implementou E113.11.

**A7.** Evidência: hooks/conformidade.py:2467 e 2464. `cd -` vira `pasta/-`, `cd ~-` vira o caminho `~-` sem expansão e `popd` não muda a pasta, então o hook fica em `/tmp`. O bash volta à pasta anterior (S20).

Caminho de ataque: o mesmo do A6, com `cd /tmp; cd -; git push origin`. Severidade: alta. Nenhuma das três formas é rara; `cd -` é idioma comum.

Correção mínima: o hook guarda a pasta anterior (OLDPWD) e a pilha do `pushd`. `cd -` e `cd ~-` voltam à anterior e `popd` desempilha. Como alternativa que falha fechado: depois de `cd -`, `cd ~-`, `popd` ou `pushd` sem argumento (`pushd +N`), a ação crítica é conferida na pasta inicial da linha e na atual, e vale a regra mais dura (como o `por_dureza`). Fixtures: S17 a S19 recusam; `cd docs; cd -; git status` segue livre. Esforço: P. Dono: quem implementou E113.11.

**A5 (resto).** Evidência: hooks/conformidade.py:1861 (o padrão só aceita `--recursive` e `--archive` por inteiro) e 1851 (o alvo só sai de `-t`, `--target-directory` e `--target-directory=`). O GNU `cp` aceita a abreviação de opção longa sem ambiguidade (`--recur`, `--arch`, `--targ`, `--target-dir`) e o argumento colado no curto (`-t"$X"`, `-rt"$X"`), conferido no bash. Com o alvo colado, o hook toma `ev` como destino e não vê o opaco. Isso também abre a regra A9 de base: `cp -t"$X" ev/config` passa, e `cp ev/config "$X"` recusa. Caminho: X vem de fora da linha, apontando para `.git`, como no A5 anterior. Severidade: média, porque o estado do shell não persiste entre chamadas. Correção mínima: o padrão recursivo aceita todo prefixo de `--recursive` (a partir de `--r`) e de `--archive` (a partir de `--ar`). O alvo sai também de `-t<valor>` colado (em qualquer agrupamento de curtas terminado em `t`) e de todo prefixo de `--target-directory` (a partir de `--ta`), com ou sem `=`. Esforço: P.

**A8.** Evidência: hooks/conformidade.py:1174 (`tar`), 1183 (`unzip`) e 127 (`rsync`). Com o destino opaco sem resto, a extração e a cópia sincronizada gravam nomes que o hook não vê, o mesmo motivo do A5. Severidade: média, pela mesma razão do A5. Correção mínima: para `tar` (`-C`, `--directory`), `unzip -d`, `bsdtar` e `rsync` com destino de valor de fora (`valor_de_fora`), aplicar a mesma recusa da cópia recursiva. Pela matriz, entra a dimensão "programa que grava nomes do conteúdo". Esforço: P.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Os bloqueantes A6 e A7 são da família do A4, o escopo da pasta. Eu devia tê-los achado já na primeira rodada; registro a falha da varredura. Ferramentas: o delta do `forge-check`, o montador das fixtures e o bash num repositório descartável. Nenhuma varredura externa. As tabelas das sondas ficaram só na área de rascunho desta sessão.
