---
tipo: review
contrato: 1
pedido: anti-alucinacao-regras
branch: melhoria/anti-alucinacao-regras
commit: 59b65af
parecer: aprovado
revisor: forge:tech-lead (autor)
data: 2026-10-14
---
# Parecer de autor: regras, prompt e conferente (fatia 2 do anti-alucinação)

Escopo: `git diff origin/develop..34b7538` (f9791e9, fa5c36c, c1ec273, 38fcc3b, 34b7538). Referência: a linha "| 2 |" da seção 11 da proposta anti-alucinação, com as decisões do dono P1 = B, P2 = A, P3 = A e §14 = B. Este é o parecer **de autor**: o review independente e o QA continuam obrigatórios antes do PR.

Parecer: **aprovado como autor**, com as pendências abaixo. **O PR precisa do rótulo `afrouxa-regra`**: o papel só de leitura exigiu código em `hooks/conformidade.py`, que está em `PROTEGIDOS`. A mudança endurece e não remove nenhum invariante. Também exige parecer do `security-engineer` (`R-SEGURANCA`, porque o diff toca `docs/regras/`, `tests/config.json` e `hooks/conformidade.json`), que o `forge-check pr` já cobra.

## Volta 1: bloqueantes do review independente (2b4a3b7, 486038f)
Escopo: `git diff 0c3ef40..486038f`. Os bloqueantes 1 e 2 e os dois recomendados de `anti-alucinacao-regras-independente.md` estão corrigidos, e a falha geral apontada ao `security-engineer` também. Por decisão do time, a correção geral entrou nesta fatia, num commit próprio. O PR precisa destacá-la no título e no corpo.

- **B1 (2b4a3b7):** no papel só de leitura, o `git ls-remote` passa a aceitar só opções de leitura (`--heads`, `--tags`, `--branches`, `-h`, `-t`, `-b`, `--refs`, `-q`, `--quiet`, `--exit-code`, `--symref`, `--get-url`, `--sort=`), e o endereço com transporte `<x>::` é recusado. Nos demais subcomandos git da lista, `--upload-pack`, `--receive-pack`, `--exec`, `--config-env` e `--ext-diff` são recusados, inclusive abreviados, porque o git aceita prefixo único. As opções globais já eram recusadas, com exceção de `-C` e `--no-pager`.
- **Recomendados (2b4a3b7):** o `--output` passa a casar só a própria opção e as abreviações dela, e `--output-indicator-*` é liberado. Entram as fixtures de `tee` e de `xargs`.
- **B2 e falha geral (486038f):** o analisador comum (`hooks/_comum.py`) reconhece a abertura `<(` e `>(`, também depois de `>` e colada a outro sinal. O `conformidade` confere o comando de dentro como um comando próprio, para todos os papéis. O papel só de leitura recusa a substituição em si. O `segmentos`, usado pelo `parecer` e pelo `pesado`, passa a separar o comando de dentro, e por isso um merge sem parecer dentro de `<(...)` agora bloqueia.

### Fixtures antes (0c3ef40) e depois
```
antes:  FAILED (failures=12) em 29 fixtures (conferente-*, subst-*): ls-remote upload-pack/-u/--exec/ext::, log --ext-d,
        output-indicator (falso bloqueio), conferente <(...)/>(...) x3, tech-lead <(...)/>(...)/aninhada
        + parecer/subst-processo-merge-sem-parecer-bloqueia: FAIL (0 != 2)
depois: Ran 1 test ... OK (30 fixtures: conferente-*, *subst-*)
```

### rc do hook `conformidade` (projeto temporário, hooks de 0c3ef40 e depois os de 486038f)
```
antes depois | papel      | comando
  0     2    | conferente | git ls-remote --upload-pack='touch PWNED;' .
  0     2    | conferente | git ls-remote -u 'touch W;' .
  0     2    | conferente | git ls-remote --exec=x .
  0     2    | conferente | cat <(touch x)
  0     2    | conferente | echo >(touch t)
  0     2    | conferente | git status 2>&1 >(touch t)
  0     2    | tech-lead  | cat <(git push --force origin main)
  2     2    | tech-lead  | git push --force origin main
  2     0    | conferente | git log -1 --output-indicator-new=x
  0     0    | conferente | git ls-remote origin develop
  0     0    | tech-lead  | diff <(git log -1) <(git log -2)
```

### Suíte e validação
```
$ python3 -m unittest discover -s tests     (uptime: load average: 0.32)
Ran 562 tests in 177.099s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
```

### Riscos da volta 1
- (Resolvido na volta 2.) Depois do `shlex`, uma palavra entre aspas igual a `"<("` fica idêntica à abertura de verdade, e o hook a trata como substituição. No papel comum, o efeito é conferir como comando o que vem depois dela. No papel só de leitura, o comando é recusado. É um falso bloqueio raro, e a regra é recusar na dúvida.
- (Resolvido na volta 2.) Anterior a esta fatia e fora do escopo: o `)` que fecha `<(...)` ou `$(...)` é separador no analisador. Por isso, o que vem depois dele na mesma linha é lido como outro comando, e o alvo do `rm` escapa da checagem de escrita. Pela sonda, com o papel tech-lead: `rm .forge/versao` sai com 2, mas `rm <(true) .forge/versao` e `rm $(true) .forge/versao` saem com 0. O sandbox continua sendo a garantia. Cartão para o `security-engineer`.

## Volta 2: parecer de segurança (ae60f03, ea2b636)
Escopo: `git diff 875e9a1..ea2b636`. Corrige S1, S2 e S3 de `docs/security/anti-alucinacao-regras.md` e, por decisão do time, a falha geral S4 (item 3), num commit próprio. **O PR precisa destacar no título as duas correções gerais** (substituição de processo, da volta 1, e o `)` que fecha a substituição, desta volta), além do rótulo `afrouxa-regra`.

- **ae60f03, papel só de leitura:** S1 recusa palavra com `$` que não fecha a palavra (`$'...'`, `$X`, `${X:-...}`; ficam `$?` e o `$(`) e chaves com `,` ou `..` (`HEAD@{1}` fica). S2 aceita `$(...)` e crase só como argumento de `echo`, `test` e `[`. S3 recusa todo lançador (`xargs`, `sudo`, `nohup`, `env`...). `--textconv` e `--filters` entram nas opções que executam programa (`--text` e `--filter` exatos seguem liberados, exceto no `cat-file`, onde são abreviação). O informativo `gh ... --web` também é recusado.
- **ea2b636, analisador comum:** `_comum.fichas` devolve, para cada ficha do `shlex`, se ela é sinal fora de aspas e se está colada na seguinte. `_comum.comandos` usa uma pilha de aninhamento: `$(`, `<(` e `>(` abrem um nível, e o `)` correspondente devolve ao comando de fora a palavra opaca (`$(…)`, `<(…)`, `>(…)`, colada ao que estiver colado). O conteúdo sai antes, como comando próprio, com o identificador da substituição. O `(` de subshell segue separando. O `conformidade` dá a cada substituição um contexto próprio (`cd` e branch lá dentro não valem para a linha), confere só o conteúdo de `$(...)` entre aspas e confere o caminho colado à substituição também a partir da raiz. `segmentos` (do `parecer` e do `pesado`) passa a derivar de `comandos`.

### rc do hook `conformidade` (projeto temporário em `$TMPDIR`; antes = código anterior à volta 2)
```
antes depois | papel      | comando
  0     2    | conferente | git ls-remote $'--upload-pack=touch PWNED1;' .           (S1)
  0     2    | conferente | git ls-remote {--upload-pack='touch PWNED2;',.}          (S1)
  0     2    | conferente | git log -1 $'--output=OUT1'                              (S1)
  0     2    | conferente | git diff {--output=OUT2,HEAD}                            (S1)
  0     2    | conferente | git log -1 ${X:---output=OUT3}                           (S1)
  0     2    | conferente | git ls-remote $(echo --upload-pack=touch\>PWNED12 .)     (S2)
  0     2    | conferente | git log -1 $(cat src/app.js)                             (S2)
  0     2    | conferente | git log -1 $(true) cat --format=x                        (S2)
  0     2    | conferente | echo "'--upload-pack=touch PWNED4;' ." | xargs git ls-remote  (S3)
  0     2    | conferente | sudo -i  /  sudo -s  /  nohup cat src/app.js  /  xargs -a src/app.js cat  (S3)
  0     2    | conferente | git show --textconv ...  /  git cat-file --textconv|--filters|--text ...
  0     2    | conferente | gh pr view 1 --web
  2     0    | conferente | echo "$(git log -1)"          (falso bloqueio resolvido)
  2     0    | conferente | grep -n "<(" src/app.js       (falso bloqueio resolvido)
  0     0    | conferente | echo $?  /  echo $(git log -1)  /  git log -1 HEAD@{1}  /  git diff --text HEAD
  0     0    | conferente | grep -n 'v1$' src/app.js  /  forge-check pr p1  /  cat "<(touch x)"
  2     2    | conferente | diff <(git log -1) <(git log -2)
  0     2    | tech-lead  | rm $(true) .forge/versao  /  rm <(true) .forge/versao
  0     2    | tech-lead  | git push origin $(true) main --force
  0     2    | tech-lead  | rm $(git rev-parse --show-toplevel)/.forge/versao
  0     2    | tech-lead  | echo $((1+2)) && rm $(true) .forge/versao
  2     2    | tech-lead  | cat <(git push --force origin main)  e as demais formas da volta 1
  0     0    | tech-lead  | diff <(git log -1) <(git log -2)  /  paste <(git log -1) <(git show -s)
  0     0    | tech-lead  | echo $(git rev-parse HEAD)  /  x=$(git rev-parse HEAD) && echo $x  /  (cd src && ls) && echo ok
  0     0    | tech-lead  | for f in $(ls src); do echo $f; done  /  if [ "$(git branch --show-current)" = develop ]; ...
  0     2    | dev        | git push origin $(true) main  /  git push origin $(true) HEAD:main  /  ... HEAD:develop
  0     2    | dev        | cp src/app.js $(true) .claude/settings.json  /  cp src/app.js $(true) .forge/versao
  0     2    | dev        | mv src/app.js $(true) docs/reviews/x.md  /  rm $(true) docs/reviews/x.md
  0     2    | dev        | rm <(true) .forge/config.json
  0     2    | dev        | cp src/app.js $(git rev-parse --show-toplevel)/docs/reviews/x.md
  0     2    | dev        | echo ok > $(git rev-parse --show-toplevel)/docs/reviews/x.md
```
`rm $(true) docs/regras/R-X.md` e `rm <(true) tests/config.json` só valem num clone com o manifesto do Forge: as fixtures `subst-comando-rm-regras-dev-bloqueia` e `subst-processo-rm-tests-config-dev-bloqueia` cobrem esse caso.

### Fixtures antes e depois
```
commit A, antes (875e9a1): FAILED (failures=10)  conferente-ansi-c, -chaves, -expansao-padrao, -filters-abreviado, -gh-web,
                           -subst-comando-argumento, -subst-comando-arquivo, -sudo, -textconv, -xargs-git
commit B, antes (ae60f03): FAILED (failures=12)  conferente-subst-entre-aspas-libera, subst-comando-caminho-colado-dev,
                           -cp-claude-dev, -mv-reviews-dev, -push-force-tech-lead, -push-head-main-dev, -push-main-dev,
                           -push-main-tech-lead, -rm-regras-dev, -rm-tech-lead, subst-processo-rm-tech-lead, -rm-tests-config-dev
depois (ea2b636):          fixtures: 758 / Ran 1 test in 73.453s / OK   (todas as de tests/hooks/)
```
A fixture `conferente-xargs-bloqueia` passa a esperar a recusa do lançador, que vem antes da do `touch`.

### Suíte e validação
```
$ uptime → load average: 3.21 (início), 3.97 (fim)
$ python3 -m unittest discover -s tests
Ran 562 tests in 168.479s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
```

### Riscos da volta 2
- (Resolvido na volta 3.) **Comentário engole a quebra de linha (anterior, fora do escopo, alta):** o `shlex` lê o comentário até o fim da linha e consome o `\n`, então a linha seguinte vira argumento do comando do comentário. Com o papel dev, `echo a #b⏎git push origin main` sai com 0 antes e depois desta volta (e `a#b`, sem espaço, também, embora no bash não seja comentário). Cartão para o `security-engineer`; a correção cabe em `_comum.fichas`.
- **Limites aceitos do analisador:** `case ... a)` dentro de `$(...)` fecha o nível cedo; a crase continua sem pilha (só a recursão por palavra); `$((...))` confere `1+2` como comando (no papel só de leitura, falso bloqueio). Na dúvida, recusa; o sandbox continua sendo a garantia.
- **Falso bloqueio no papel só de leitura:** `$X` em qualquer palavra e chaves com vírgula (um `--jq` com `{a,b}`) são recusados, como o parecer de segurança previu.
- `fichas` lê `shlex._pushback_chars` (interno da biblioteca padrão, estável desde o Python 3.6) para saber o que está colado. Se sumir, o hook falha fechado nas ações críticas (ADR 0009, seção 7).

## Volta 3: ADR 0011, opção (b), com os ajustes do aceite de segurança (2131fb6, e98d977)
Escopo: `git diff b88089a..e98d977`. Implementa os itens 1 e 2 da ADR 0011 com os ajustes da seção "Divergência" e do "Aceite de segurança" de `docs/security/anti-alucinacao-regras.md`. Os cartões C1 a C6 não entram. **O PR precisa destacar no título a terceira correção geral** (comentário `#` e construções não modeladas, em todos os papéis), além do rótulo `afrouxa-regra`.

- **2131fb6, item 1 (papel só de leitura):** `_comum.fora_da_gramatica_de_leitura` lê a linha uma vez, com um estado só para as aspas. Fora de aspas, aceita letras e dígitos (`isalnum`), espaço e tab literais, `_ . / : = @ , + % - ~ ^`, `&&`, `||`, `;` e `|`; o `&` sozinho recusa. Entre aspas simples, tudo menos caractere de controle; entre duplas, também recusa `$`, crase, `\` e `!`. Aspas sem fechar recusam. A checagem roda no nível 0, antes de qualquer outra, e a mensagem diz a forma explícita. Saem as regras pontuais de S1 e S2 (`EXPANSAO`, `CHAVES`, `ACEITAM_SUBSTITUICAO`) e a recusa de `<(`/`>(` do papel, todas inalcançáveis depois da gramática. `agents/conferente.md` troca `; echo $?` por `&& echo contém || echo não contém` e ganha a forma da linha.
- **e98d977, item 2 (demais papéis):** `_comum.construcao_nao_modelada` devolve a primeira construção da lista fechada: `#` com outra linha depois (em qualquer posição da palavra), crase, `case`, `$` fora de aspas simples que não abra `$(`, `\` seguido de quebra de linha e chaves. O `\` escapa o caractere seguinte, e `$(` abre um contexto novo de aspas, como no bash. O `conformidade` só a consulta quando a linha casa com `CRITICO` (ADR 0009, seção 7) e recusa depois das checagens da linha, para que a regra mais específica (`R-MAIN`, `R-VERIFY`...) fale primeiro. Também recusa quando o `shlex` não consegue ler a linha: `git push origin main $'\''` saía com 0 por aspas "desbalanceadas" que o bash lê bem.
- **Heredoc (ajuste de autor dentro do item 2):** a lista da ADR diz "heredoc". Aplicada ao pé da letra, ela quebra dois fixtures de uso legítimo que já existiam: `shell-heredoc-no-commit-libera` (mensagem de commit por `<<'EOF'`) e `parecer-por-bash-qa-libera` (QA grava o parecer por heredoc). Além disso, a sonda mostrou que o próprio `tirar_heredocs` tira como corpo linhas que o bash executa: `cat \<<'EOF'⏎git push origin main⏎EOF`, `echo "<<'EOF'"⏎...` e `cat <<E'OF'⏎EOF⏎git push origin main⏎E` saíam com 0 antes e continuavam com 0 na primeira versão do item 2. A regra entregue: só o heredoc de delimitador entre aspas (`<<'FIM'` ou `<<"FIM"`), sem `-`, terminado numa linha igual ao delimitador, é modelado, e o corpo dele não é lido. Todo outro `<<` numa linha de várias linhas (sem aspas, `<<-`, `<<<`, escapado, entre aspas, sem fim, fim com espaço em volta) recusa. **Pede confirmação do `security-engineer`.**

### rc do hook `conformidade` (projeto temporário em `$TMPDIR`; antes = hooks de b88089a, depois = e98d977)
```
antes depois | papel      | comando
  0     0    | conferente | git log -1 'HEAD@{1}' && git diff --text HEAD && grep -n 'v1$' src/app.js
  0     0    | conferente | grep -n 'v1$' src/app.js
  0     0    | conferente | grep -n "a#b" src/app.js
  0     0    | conferente | git show HEAD^
  0     0    | conferente | git status && git log -1
  0     0    | conferente | forge-check pr p1
  0     0    | conferente | git log -1
  0     0    | conferente | git ls-remote origin develop
  0     0    | conferente | cat src/app.js | head -5
  0     0    | conferente | git log -1 'HEAD@{1}'
  0     0    | conferente | grep -n "<(" src/app.js
  0     0    | conferente | cd {raiz} && git --no-pager -C {raiz} log -1 ... | head -1; ...; forge-check pr p1; grep ...  (conferente-leitura-libera)
  0     2    | conferente | grep -n 'v1 src/app.js
  0     2    | conferente | grep -n "a\|b" src/app.js
  0     2    | conferente | echo a #b⏎git commit -m x
  0     2    | conferente | echo a #b⏎git log -1
  0     2    | conferente | git log -1 2>/dev/null
  0     2    | conferente | git log -1⏎git status
  0     2    | conferente | git log -1 & git status
  0     2    | conferente | echo $(git log -1)
  0     2    | conferente | grep -n "a!b" src/app.js
  0     2    | conferente | ls *
  0     2    | conferente | git log -1 HEAD@{1}
  0     2    | conferente | cat <<E
  0     2    | conferente | git log -1␍git status
  0     2    | conferente | echo $?
  0     2    | conferente | echo "$(git log -1)"
  2     2    | conferente | git log -1 $'--output=OUT1'
  2     2    | conferente | git ls-remote $'--upload-pack=touch PWNED1;' .
  2     2    | conferente | grep -n "'" src/app.js $(touch Z) "'"
  2     2    | conferente | git log -1 \--output=x
  2     2    | conferente | git diff {--output=OUT2,HEAD}
  2     2    | conferente | git ls-remote {--upload-pack='touch PWNED2;',.}
  2     2    | conferente | git log `echo -1`
  2     2    | conferente | nohup cat src/app.js
  2     2    | conferente | git log -1 $(cat src/app.js)
  2     2    | conferente | git log -1 $(true) cat --format=x
  2     2    | conferente | git ls-remote $(echo --upload-pack=touch\>PWNED12 .)
  2     2    | conferente | sudo -i
  2     2    | conferente | git log $X
  2     2    | conferente | xargs -a src/app.js cat
  2     2    | conferente | echo "'--upload-pack=touch PWNED4;' ." | xargs git ls-remote
  0     0    | dev        | x=$(git rev-parse HEAD) && echo $x
  0     0    | tech-lead  | x=$(git rev-parse HEAD) && echo $x
  0     0    | dev        | git log -1 # nota
  0     0    | tech-lead  | git log -1 # nota
  0     0    | dev        | echo $(git rev-parse HEAD)
  0     0    | tech-lead  | echo $(git rev-parse HEAD)
  0     0    | dev        | for f in $(ls src); do echo $f; done
  0     0    | tech-lead  | for f in $(ls src); do echo $f; done
  0     0    | dev        | git push origin melhoria/x
  0     0    | tech-lead  | git push origin melhoria/x
  0     0    | dev        | diff <(git log -1) <(git log -2)
  0     0    | tech-lead  | diff <(git log -1) <(git log -2)
  0     2    | dev        | git push origin main $'\''
  0     2    | dev        | git push origin $'main'
  0     2    | dev        | git push origin $@main
  0     2    | dev        | git push origin $"main"
  0     2    | dev        | case x in x) git push origin melhoria/x;; esac
  0     2    | dev        | echo a#b⏎git push origin main
  0     2    | dev        | git push origin {main,x}
  0     2    | tech-lead  | echo a #b⏎git push origin melhoria/x
  0     2    | dev        | echo a #b⏎git push origin main
  0     2    | dev        | git push origin ma\⏎in
  0     2    | dev        | git push origin `echo main`
  0     2    | dev        | git push origin $1main
  0     2    | dev        | git push origin $B
  2     2    | dev        | bash <<E⏎git push origin main⏎E
  0     0    | dev        | git commit -m "$(cat <<'EOF'⏎docs: parecer em docs/reviews/p1.md (#12)⏎EOF⏎)"
  0     2    | dev        | cat <<E'OF'⏎EOF⏎git push origin main⏎E
  0     2    | dev        | echo "<<'EOF'"⏎git push origin main⏎EOF
  0     2    | dev        | cat \<<'EOF'⏎git push origin main⏎EOF
  0     2    | dev        | cat <<EOF⏎$(git push origin main)⏎EOF
  0     0    | qa-engineer | cat > docs/qa/p1.md <<'EOF'⏎parecer: aprovado⏎EOF
  0     0    | tech-lead  | git commit -m "$(cat <<'EOF'⏎feat: x⏎⏎não use git push --force nem echo x > .forge/versao⏎EOF⏎)"
```
`⏎` é quebra de linha, e `␍` é o `\r`. Todas as linhas batem com o `esperado` do fixture. Os comandos com rc 2 nas duas colunas mudam de motivo: agora a gramática (ou o lançador, no S3) recusa antes da regra pontual.

### Fixtures antes e depois
```
commit A, antes (b88089a): 39 fixtures conferente-gramatica-* → FAILED (failures=25)
                           (16 com rc 0 em vez de 2; 9 já com rc 2, mas pela regra pontual, e não pela gramática)
commit B, antes (2131fb6): 26 fixtures nao-modelado-* → FAILED (failures=13), todas com rc 0 em vez de 2
heredoc,  antes (1ª versão do item 2): 4 fixtures nao-modelado-heredoc-*-bloqueia → rc 0 em 2 delas
                           (escapado, entre aspas), e parecer-por-bash-qa-libera e shell-heredoc-no-commit-libera com rc 2
depois (e98d977):          688 fixtures de conformidade → Ran 1 test in 90.251s / OK
```
Fixtures reescritos: `conferente-leitura-libera` sem `2>/dev/null` e sem `echo $?` (endurecimento, sem exceção para `/dev/null`); `conferente-expansao-legitima-libera` na forma explícita (`'HEAD@{1}'`); `conferente-subst-entre-aspas-libera` vira `-bloqueia`, porque o `$` entre aspas duplas é expandido. Dez fixtures de bloqueio do papel trocam o trecho esperado do stderr para "fora da gramática".

### Suíte, validação e tempo
```
$ uptime → load average: 3.88 (início), 1.07 (fim)
$ python3 -m unittest discover -s tests
Ran 562 tests in 136.175s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
hook inteiro, mediana de 15 chamadas, linha `git push origin melhoria/x && git log -1` como dev:
  b88089a 130 ms, e98d977 96 ms (com load acima de 5, então é ruído)
as duas varreduras juntas, no mesmo processo: 0,09 ms por linha
```

### Riscos e pendências da volta 3
- **Falso bloqueio previsto pela ADR:** no papel só de leitura, `echo $?`, `$(...)`, `2>/dev/null`, `HEAD@{1}` sem aspas, glob, várias linhas e `grep "a\|b"`. Nos demais papéis, só com marcador: `git push origin $BRANCH`, laço com `push`, comentário entre linhas, `cp $TMPDIR/x docs/reviews/y.md` (C6) e heredoc sem aspas no delimitador. O critério de reversão da ADR mede isso.
- **A redação da ADR e o código divergem em dois pontos.** (1) Heredoc, como acima. (2) Chaves: o código recusa qualquer `{` ou `}` fora de aspas, como o brief pediu, e não só "com `,` ou `..`". O `{ ...; }` com `push` passa a recusar. A ADR ainda diz "Estado: proposta" e cita `git ls-files 'docs/*.md'`, que não está na lista do conferente (no agente, o exemplo é `grep -n 'v1$' src/app.js`). Cabe ao arquiteto ajustar o texto.
- **Inertes no papel só de leitura:** a lista `saidas` de `hooks/conformidade.json` e a checagem de redirecionamento do papel, porque a gramática recusa `<` e `>` antes. Ficaram, porque a validação da política exige a chave. Candidato a cartão de limpeza.
- **Limites que continuam:** glob em caminho protegido nos papéis comuns (C3) e a pilha da crase e o `case` dentro de `$(...)` no analisador geral (C2), que o item 2 cobre só nas linhas com marcador.

## Volta 4: S6 do re-review de segurança da volta 3 (59b65af)
Escopo: `git diff beb9940..59b65af` (`hooks/conformidade.py`, `hooks/conformidade.json`, 15 fixtures novas). Decisão do time: correção pequena e auditoria. Se o papel só de leitura reprovar de novo, o passo seguinte é a (c3) da ADR 0011, sem outro remendo. Os demais papéis e o heredoc ficam como estavam. C3, C7, C8 e S7 continuam cartões.

### O que mudou
- `test` só passa na forma `test -e|-f|-d|-s <um caminho>` (`TESTE_LEITURA`), com exatamente dois argumentos. O caminho é literal, porque a gramática já recusa expansão fora de aspas, e `-f`/`-e`/`-d`/`-s` não reavaliam o texto entre aspas.
- `[` sai de `so_leitura.comandos`. `[[` não estava na lista, e a gramática recusa os dois pelo `[`.
- Papel só de leitura com `nivel > 0` recusa no começo de `bash()`. Depois da gramática, esse nível só aparece com `$(` ou crase entre aspas simples, e o bash só executa esse texto por reavaliação.
- Auditoria: `--show-signature` entra em `GIT_EXECUTA`, abreviado inclusive. O formato `%G` (`FORMATO_ASSINATURA`, também com `%+G`, `%-G` e `% G`) recusa em qualquer subcomando git da lista. Valor de opção do `forge-check` que começa com `-` também recusa.

### Auditoria da lista branca do papel só de leitura
Sondas: bash 5.2.21 e git 2.43.0 num repositório descartável em `$TMPDIR`, com `gpg.program` falso que cria um arquivo ao rodar.

| Comando | Forma que reavalia argumento ou executa programa | Tratamento |
|---|---|---|
| `test` (interno) | `-v 'a[$(...)]'`, também em `x = y -o -v` e `'!' -v` (sondado: só `-v` executa; `-f -e -d -s -R -o -nt -eq -lt` não) | só `-e\|-f\|-d\|-s <caminho>`; o resto recusa |
| `[`, `[[` | as mesmas do `test`; o `[[` também faz aritmética no `-eq` | `[` sai da lista; a gramática recusa os dois |
| qualquer comando | `$(...)` ou crase entre aspas simples, que só roda por reavaliação | análise aninhada recusada no papel |
| `git log`/`show`/`diff` | `--show-signature` e `%G?`/`%GS`/`%GK`... no `--format`/`--pretty` rodam o `gpg.program` (sondado: o gpg falso rodou nos dois; `git show <tag assinada>`, `cat-file -p` e `%(describe)` não o rodam) | recusa, também abreviado e com modificador |
| `git` (todos) | `--output` grava; `--ext-diff`, `--textconv`, `--filters`, `--upload-pack`, `--receive-pack`, `--exec` e `--config-env` executam | já recusados (voltas 1 a 3), também abreviados |
| `git` (opção global) | `-c` (`core.pager`, `alias.*`, `gpg.program`), `-p`/`--paginate`, `--exec-path`, `--git-dir` | já recusados: só `-C` e `--no-pager` passam antes do subcomando |
| `git` (alias) | alias não sobrepõe subcomando nativo, e a chave tem de ser um dos subcomandos da lista | nada a fazer |
| `git ls-remote` | `--upload-pack`, `-u`, `--exec` e transporte `<x>::` executam | já recusados: só as opções de leitura passam |
| `git` com configuração do repositório | `diff.<x>.textconv`/`command` via `.gitattributes`, `core.fsmonitor`, `core.pager` com tty, `remote.<x>.uploadpack`, `pretty.<x>` e `log.showSignature` | depende de configuração gravada antes: é a classe S7 (cartão e `safe.bareRepository`), fora desta volta |
| `gh pr`/`gh run` | `--web`/`-w` abre o navegador; o pager só roda com tty e `GH_PAGER`, que é variável recusada; `--jq` (gojq) e `--template` (Go) não executam programa; o pflag não aceita abreviação | `--web` já recusado; o resto não reavalia |
| `forge-check pr`/`docs` | `--ref=-...`/`--base=-...` chegariam como opção ao git interno (`ls-tree`, `diff`, `show`). Hoje é inalcançável, porque o `ls-tree` falha antes do `diff` | recusa por defesa (valor que começa com `-`) |
| `echo`, `pwd`, `cd`, `true` (internos) | nenhuma (sondado com `'a[$(touch X)]'`: nada criado) | nada a fazer |
| `ls`, `grep`, `cat`, `head`, `tail`, `wc`, `cut`, `tr` (externos) | recebem o argumento sem aspas e não o passam ao shell. Nenhuma opção do GNU executa programa (o `--pre` é do `rg`, que está fora da lista) | nada a fazer |
| fora da lista | `printf -v`, `-exec` (`find`), `--pager`/`less`, `--open-files-in-pager` (`git grep`), `-e` de interpretador, `eval`, `bash -c`, `unset`/`declare` com índice | já recusados pela lista branca: não entram |

### rc do hook `conformidade` (conferente; antes = beb9940, depois = 59b65af)
```
antes depois
  0     2  test -v 'a[$(git diff {--output=PWN7,HEAD})]'                                      (PWN7)
  0     2  test -v 'a[$(git ls-remote $'"'"'--upload-pack=touch PWN8;'"'"' .)]'              (PWN8)
  0     2  test -v 'a[$(git ls-remote {--upload-pack=touch\ PWN9\;,.})]'                      (PWN9)
  0     2  test -v 'a[$(git log -1 $X)]'    test x = y -o -v 'a[$(git log -1)]'    test '!' -v 'a[...]'    test -v x
  0     2  grep -n '$(git log -1)' src/app.js                                                 (nível 1)
  2     2  grep -n '`git log -1`' src/app.js            (antes: "``git` fora da lista"; agora: "substituição dentro de aspas")
  2     2  [ -e src/app.js ]    [[ -e src/app.js ]]                                           (gramática)
  0     2  git log -1 --show-signature    git log -1 --show-sig    git log -1 --format=%GS    git log -1 --pretty=format:%+GK
  0     2  forge-check pr p1 --ref=--output=PWNF
  0     0  test -f src/app.js && test -e src/app.js && test -d src && test -s src/app.js
  0     0  git log -1    grep -n x src/app.js    git log -1 --format=%h%n%s%n%gd && git rev-parse --show-toplevel && git status --show-stash
  0     0  forge-check pr p1 --ref=HEAD --base=develop
```

### Fixtures antes e depois
```
antes (hooks de beb9940): 15 fixtures novas → FAILED (failures=12)
        (11 com rc 0 em vez de 2; crase entre aspas simples já com rc 2, mas por outro motivo;
         conferente-colchete-bloqueia já verde: é regressão da retirada do `[`; as 2 de liberação, verdes)
depois (59b65af):         15 fixtures novas → Ran 1 test in 1.352s / OK
```

### Suíte, validação e tempo
```
$ uptime → load average: 1.50 (início), 4.86 (fim, carga da própria suíte)
$ python3 -m unittest discover -s tests
Ran 562 tests in 182.090s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
hook inteiro, 10 chamadas, conferente com `test -f … && git log -1 && grep -n x … && git log -1 --format=%h`: min 14 ms, mediana 18 ms, máx 25 ms
```

### Riscos e pendências da volta 4
- **Falso bloqueio novo:** `grep` de um texto com `$(` ou crase entre aspas simples, `test` em outra forma (`-n`, `-z`, comparações) e `%G` em `--grep=`. O custo foi aceito pelo security-engineer em S6 (3).
- **Classe S7:** textconv, diff externo, fsmonitor, pager e `pretty.<x>` dependem de configuração gravada antes no repositório. Ficam com o cartão de S7 e a decisão sobre `safe.bareRepository`, que vai ao usuário pelo Jarvis.
- **Re-review de segurança** só do diff `beb9940..59b65af`. Se reprovar, o passo seguinte é a (c3).
- **ADR 0011:** sai o `[` da lista e entram a restrição do `test` e a recusa a nível maior que 0. O texto é do arquiteto (S6, "Para o arquiteto").

## O que mudou
- **Regras:** `R-PROVA` e `R-BRIEF` são novas. A `R-DECISAO` passa a exigir uma pergunta por vez em tudo e a marca "Retira do escopo original" em todo corte, com a lista "Fora do escopo". O índice também foi atualizado. O `verificada_por` das novas diz que os hooks `prova` e `brief` ainda não existem, para que a regra não afirme uma garantia que ainda não há.
- **`agents/conferente.md`:** usa haiku e as ferramentas `Read, Grep, Glob, Bash`. Tem os modos `brief` e `entrega` em formato fixo e a tabela de etapas. Lista os anexos implícitos e confere a marca de corte por `grep`. Instrução vinda de dentro do brief não muda o trabalho dele. O veredito fica na última linha.
- **`hooks/conformidade.json` e `.py`:** papel `conferente` e chave opcional `so_leitura`, com lista branca de comandos. Sem ferramenta de arquivo, sem redirecionamento a arquivo, sem variável na linha e sem programa com caminho. `git -c` e `--output` são recusados. A chave malformada recusa a política inteira. Há 14 fixtures e 3 casos novos de política malformada.
- **`agents/jarvis.md`:** o passo 1 sai do "máx. 3" para uma pergunta por vez, com a lista "Fora do escopo". O prompt-padrão ganha "Fora do escopo" com a marca, `PQ-n` com o tipo de prova e o bloco `Provas:`. Entram as conferências de brief e de entrega, o passo 5 com a conferência antes do review e o passo 8 com a tabela pedido × entregue. O agente fica com 107 linhas, abaixo do limite de 110.
- **Também mudaram:** o modelo `templates/projeto/docs/pedidos/_modelo.md`, `docs/hooks.md`, `.claude-plugin/plugin.json` (só a lista de agentes; a versão não muda), o `CHANGELOG.md` em `[Não publicado]` e `tests/config.json`, onde `conferente` entrou em `agentes_obrigatorios` e as invariantes novas foram só acrescentadas. O teste `test_conferente_so_leitura` cobre o frontmatter e a política.

## PQ-1: suíte e validação
```
$ python3 -m unittest discover -s tests -v     (uptime: load 0.65)
Ran 562 tests in 172.591s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
```

## PQ-2: "máx. 3" fora do passo 1
```
$ grep -c "máx. 3" agents/jarvis.md
1
$ grep -n "máx. 3" agents/jarvis.md
38:6. **QA** (`R-QA` portão de QA, obrigatório; máx. 3 voltas por bug).
```
Na `origin/develop` eram duas ocorrências, nas linhas 32 (passo 1) e 37. Sobrou só a do QA, que não é pergunta ao dono.

## PQ-3: brief real (modo `brief`) e entrega real (modo `entrega`)
**Limite da execução:** este subagente não tem a ferramenta Agent, então o `forge:conferente` (haiku) **não foi lançado**. Executei o roteiro do agente à mão, com os comandos da lista dele, e colei a saída no formato das seções 5.2 e 7.1. Esses mesmos comandos passaram pelo hook `conformidade` com `agent_type: forge:conferente` num projeto temporário: todos saíram com 0, e os dois de fora da lista (`python3 -m unittest`, `git push`) saíram com 2. **A rodada com o agente de verdade fica para o Jarvis**, antes do review independente.

**Brief real** (o brief desta delegação; pedido = linha "| 2 |" da seção 11 e decisões do dono da proposta):
```
$ grep -c "Retira do escopo original" brief-aa2.txt     → 1 (é o nome da marca no item 2, não um corte)
$ grep -c "anexos implícitos" brief-aa2.txt             → 0 (a linha "| 2 |" da §11 pede "anexos implícitos" em agents/conferente.md)
$ grep -n "P1=B, P2=A, P3=A, §14=B" brief-aa2.txt       → 15 (as decisões batem com o último registro; "P1 = A" foi reaberto para B)
$ grep -nE "PQ-[0-9] .*(sha|push|pr|run|cmd|arquivo|merge)" brief-aa2.txt → sem saída (PQ-1..4 sem tipo de prova)
conferencia-brief: anti-alucinacao-regras → forge:tech-lead
fidelidade: ok | decisões: ok | corte: sem marca "anexos implícitos" (§11, linha 2) | forma: PQ-1..PQ-4 sem tipo de prova | etapa: ok (codigo; "Não abra o PR")
veredito-brief: reprovado
```
O item foi entregue mesmo assim, porque a proposta o pede. Observação fora do formato: a seção 13 da proposta prevê a ADR 0011 "a criar na fatia 2", mas ela não está na linha "| 2 |" nem no brief. Não foi criada (ver pendências).

**Entrega real** (PR #122, `melhoria/anti-alucinacao-medicao-fix`). Os PQs vêm da linha "| 1 |" da seção 11, porque o brief literal do #122 não está disponível. O `forge-check pr` rodou num clone local descartável no head do PR (2251ad5), com base `f2dbe3a^1`.
```
conferencia: anti-alucinacao-medicao-fix forge:tech-lead modo=entrega
PQ-1 cumpriu | forge-check pr anti-alucinacao-medicao-fix → sem saída, rc=0 (controle: pedido inexistente → 2 violações, rc=1)
PQ-2 não verificável | python3 -m unittest tests.test_forge.MedirAlucinacao → fora da lista do conferente (o hook recusa, rc=2)
PQ-3 não cumpriu | test -e docs/kanban/entregas.md; echo $? → 1 (a linha de base está em docs/melhoria-continua.md:22-23)
PQ-4 não cumpriu | grep -c "M3b" bin/forge-check docs/melhoria-continua.md → 0 e 0 (medir_decisoes conta grupos, não perguntas soltas)
escopo: ok (anexo) | git diff --name-only f2dbe3a^1...2251ad5 → bin/forge-check, tests/test_forge.py, docs/melhoria-continua.md; anexos CHANGELOG.md, docs/reviews/, docs/qa/
etapa: fora de ordem | gh pr checks 122 → 11 checks "fail" em 2s; gh pr view 122 --json labels → [] (diff toca bin/forge-check, em PROTEGIDOS, sem afrouxa-regra)
veredito: não cumpriu
```
Ordem dos pareceres: review aprovado (`commit: ac3d698`, gravado às 15:33-03:00) e QA aprovado (`dab099a`, às 16:10-03:00), ambos antes de `createdAt` 20:05Z e de `mergedAt` 20:07Z. Nessa parte, a ordem está certa.

## PQ-4: brief de teste com corte sem marca
Pedido de teste com o escopo 1 (CSV), 2 (PDF) e 3 (agendamento semanal). Os dois briefs entregam 1 e 2 e põem o 3 em "Fora do escopo".
```
brief-sem-marca.txt: "- Agendamento semanal por e-mail (fica para depois)"
$ grep -n "Retira do escopo original" brief-sem-marca.txt → sem saída, rc=1
conferencia-brief: 900-exportar-relatorio → forge:node-backend
fidelidade: ok | decisões: ok | corte: sem marca "3. Agendar o envio semanal por e-mail" | forma: ok | etapa: ok
veredito-brief: reprovado

brief-com-marca.txt: "- Agendamento semanal · Retira do escopo original: "3. Agendar..." · motivo · consequência · decisão: DECISÃO DO DONO (2026-10-14)"
$ grep -n "Retira do escopo original" brief-com-marca.txt → 8:..., rc=0
$ grep -c "^DECISÃO DO DONO" pedido-teste.md → 0 (corte: decisão citada sem registro: reprovado); com a linha gravada → 8:DECISÃO DO DONO ...
veredito-brief: aprovado (só depois do registro da decisão)
```

## Pendências e riscos
1. **No próprio Forge, o papel só de leitura não vale.** Com a raiz da sessão num clone do Forge, o `conformidade` só age dentro de um projeto (`identificar_sessao`). No Forge, o mesmo roteiro saiu com 0 inclusive em `git push`. Ali, o conferente fica contido só pelo frontmatter (sem Write e sem Edit) e pela definição. Nos projetos, a trava vale (fixtures). Isso é para o `security-engineer`; candidata à fatia 3, que já leva o `parecer` ao clone do Forge.
2. **O #122 foi mesclado com 11 checks em `fail` (2s cada) e sem o rótulo `afrouxa-regra`.** O caso se parece com o do #120. Vale levar ao dono e investigar a falha de 2s, que parece de runner ou de cota e não de teste.
3. **PQ-3 sem o agente de verdade** (ver acima). O Jarvis precisa rodar o `forge:conferente` nos dois modos e colar a saída no PR.
4. **A ADR 0011 (seção 13) não foi criada**, porque não está na linha "| 2 |" nem no brief. Ela é o lugar das leituras e do critério de reversão do conferente. Até lá, o critério está na seção 13 da proposta.
5. **A lista branca do conferente** recusa `for`, `$(...)` com comando de fora da lista, `sed` e `awk`. Na dúvida, recusa. O falso bloqueio custa um comando refeito.
6. **`docs/visao-geral.md` não lista o conferente.** É recomendado acrescentar, mas fica fora do escopo da fatia.

## Recomendados do re-review
Itens 3 a 7 do re-review independente (`docs/reviews/anti-alucinacao-regras-independente.md`), só textos e formatação; a lógica de decisão do hook não mudou e nenhuma fixture mudou (as mensagens mantêm o trecho que elas conferem).
- 3: `agents/conferente.md` lista `test -e|-f|-d|-s <caminho>`, avisa que `%G`, `--show-signature` e `$(`/crase (até entre aspas) são recusados e dá a forma que passa.
- 4: mensagens do nível > 0, de `%G` e de `--show-signature` trazem a forma que passa; a da gramática avisa que `$(` e crase não passam nem entre aspas.
- 5: `descricao` do `so_leitura` alinhada à gramática da ADR 0011. A limpeza de `saidas` segue no cartão proposto.
- 6: `CHANGELOG.md` cita os endurecimentos das voltas 2 a 4.
- 7: `import` de `hooks/conformidade.py` reagrupado.
- 1 (`shlex` ilegível) vira cartão; 2 é só registro.
