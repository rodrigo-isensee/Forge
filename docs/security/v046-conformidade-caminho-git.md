---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: cddc8915fda2dd271907323e1a2c04beebd2bd28
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.19, conformidade-caminho-git, revalidação por delta)

Delta revisado: `c0727411..cddc8915` (volta 2 da E20.6, commit `cddc8915`, E20.16), lido por `forge-check parecer delta` e `git diff`: no domínio, `hooks/conformidade.py` (a regex `_REV_PARSE` saiu; `REV_PARSE_DO_GIT` pega o corpo de `$(…)` e da crase, `valor_do_rev_parse` o lê por palavras com `shlex`, `trocar_rev_parse`) e as 16 fixtures `gitcomum-v2-*` novas. Parecer anterior: reprovado no `c0727411` (E20.13).

Veredito: **aprovado**. O A1 fechou na família que a entrega declara: as 5 sondas da E20.13 (`git -C .`, `git -c a=b`, `\git`, `/usr/bin/git`, `rev-parse -q`, argumento do `--git-path` entre aspas) recusam, e também `"--git-dir"`, `'rev-parse'`, `"--git-path" "config"`, operador separado por espaço (`--git-dir ;`, `&& :`, `2>/dev/null||echo .git`), `cd .&&git …`, alias, `#` e quebra de linha dentro; aninhado entre aspas (`-C "$(pwd)"`, `--git-path "$(echo hooks)"`) recusa, pela troca ou pela regra de aspas sem par. A6 fechou de carona. Fica um resíduo da leitura por palavras (A10) que só aparece com grafia que nenhum agente escreve por engano (operador colado na opção, `eval '…'`, `sh -c '…'`, `$'…'`, `$(…)` aninhado sem aspas, sempre sem resto): para quem ofusca de propósito já existe o A9 (`$(echo .git)`), aberto e em cartão; por proporcionalidade, é cartão com prioridade e não segura o merge. Conferido: 58 fixtures `gitcomum-*` e `tests/test_hook_git_comum.py` OK; o roteiro da E20.13 (78 variantes) dá 10 falhas, todas dos itens em cartão (A4, A5, A7, A8); os 6 legítimos novos liberam.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de escrita em `.git/`), analisador de comando.

## Achados
- A4 (recomendado) hooks/conformidade.py:1001 · cd para o opaco segue passando rc 0 (`cd "$(git rev-parse --git-dir)/hooks" && cp ../../x pre-push`); já existia (AR-7); cartão de segurança
- A5 (recomendado) hooks/conformidade.py:1496 · parcial: `mv x --target-directory=.git/hooks` passa rc 0; `mv` está em TODOS_OS_ARGUMENTOS (linha 124), que pula toda palavra que começa com `-`; cartão de segurança com prioridade
- A7 (recomendado) hooks/conformidade.py:983 · falso positivo segue (`cp x "$(mktemp -d)/config"`, `cp x $TMPDIR/logs/a.log`), com a mensagem que manda usar o caminho literal; limite aceito desta entrega; cartão
- A8 (recomendado) hooks/conformidade.py:1509 · opção de destino colada: `cp -t.git/hooks x`, `cp -t.git/config x`, `install -t.git/hooks x`, `mv -t.git/hooks x` e `cp -t"$(git rev-parse --git-path hooks)" x` passam rc 0; já existia; cartão com prioridade
- A9 (recomendado) hooks/conformidade.py:1001 · destino opaco sem resto cujo valor é o .git por indireção fora da família rev-parse: `cp config "$(echo .git)"` passa rc 0; ofuscação deliberada; cartão
- A10 (recomendado) hooks/conformidade.py:365 · resíduo da leitura por palavras: operador colado (`--git-dir;`, `--git-dir&&:`, `--git-dir|cat`), `eval '…'`, `sh -c '…'`, `$'--git-dir'` e `$(…)` aninhado sem aspas, sem resto, passam rc 0; cartão com prioridade

## Sondas
- S1 · cp config "$(git rev-parse --git-dir;)" · espera: rc 2 R-CONFORMIDADE (.git) · obtido: rc 0, stderr vazio (head cddc8915); o mesmo com `--git-dir&&:`, `--git-dir|cat` e a crase `` `git rev-parse --git-dir;` ``
- S2 · cp config "$(eval 'git rev-parse --git-dir')" · espera: rc 2 R-CONFORMIDADE (.git) · obtido: rc 0, stderr vazio (head); o mesmo com `sh -c '…'`; com `eval "…"` recusa (aspas sem par)
- S3 · cp config "$(git rev-parse $'--git-dir')" · espera: rc 2 R-CONFORMIDADE (.git) · obtido: rc 0, stderr vazio (head)
- S4 · cp pre-push "$(git rev-parse --git-path $(echo hooks))" · espera: rc 2 R-CONFORMIDADE (.git) · obtido: rc 0, stderr vazio (head); o mesmo com `git -C $(echo .) rev-parse --git-dir`; entre aspas recusa
- S5 · cp config "$(echo .git)" · espera: rc 2 R-CONFORMIDADE (.git) · obtido: rc 0, stderr vazio (head)

## Detalhe dos achados
Método: o montador de `tests/test_hooks.py` (`Fixture.montar`, `rodar`), papel `forge:tech-lead`, projeto em `melhoria/x` (e worktree em `melhoria/w`), com `x`, `config` e `pre-push` na raiz; só repositórios temporários, nada escrito em `.git` real. A árvore do head saiu por `git archive cddc8915`. Rodei de novo o roteiro da E20.13 (48 variantes da E20.8, 2 de worktree, 18 de dimensões novas, 10 legítimos): 10 falhas, só A4 (2), A5 (1), A7 (2) e A8 (5). Roteiro novo da leitura por palavras: 26 casos que devem recusar (aspas aninhadas, `;`, `&&`, `|`, `||`, `eval`, `sh -c`, `$'…'`, alias, aninhado com e sem aspas, `#`, quebra de linha, crase) e 6 legítimos (`cat "$(git rev-parse --git-dir;)/HEAD"`, `git log -1 "$(git rev-parse --abbrev-ref HEAD)"`, `--show-toplevel` para docs, `git commit -m "$(printf %s rev-parse --git-dir)"`, `--git-dir)/../docs/a`, `--short HEAD`): os 6 liberam; dos 26, 15 recusam e 11 passam, 10 do A10 e 1 do A9.

**A1 (fechado).** A leitura por palavras cobre o que a correção mínima da E20.13 pedia: qualquer prefixo antes de `rev-parse`, opções entre ele e a do diretório, aspas no argumento e redirecionamento dentro. O que falha fechado (argumento do `--git-path` que não é caminho simples, `-C` de outro repositório) recusa a mais, o lado seguro.

**A10 (média, recomendado; dimensão nova "tokenização do corpo", não é recomendação promovida).** Evidência: `hooks/conformidade.py:365`: `shlex.split(corpo)` sem `punctuation_chars` deixa `--git-dir;` e `--git-dir|cat` como uma palavra, que não está em `OPCOES_DO_DIR_DO_GIT`; `eval '…'` e `sh -c '…'` viram uma palavra só (AR-10, texto executado por outro caminho); `$'--git-dir'` vira `$--git-dir`; e `REV_PARSE_DO_GIT` (`hooks/conformidade.py:334`) exige corpo sem `(`, `)` nem crase, então o aninhado sem aspas nem chega à leitura. Só vale sem resto depois do `)`: com resto (`…)/config`), a regra do opaco recusa. Caminho de ataque: um agente que quer gravar em `.git/config` ou `.git/hooks/` e ofusca de propósito; esse agente já tem o A9 (`$(echo .git)`), que nenhuma leitura por palavras fecha, então o A10 não abre caminho novo. Por engano, nenhuma dessas grafias é natural (as naturais, com espaço antes do operador ou aninhado entre aspas, recusam). Por isso cartão, não bloqueante (proporcionalidade). Correção mínima: em `valor_do_rev_parse`, `shlex.shlex(corpo, posix=True, punctuation_chars=True)` para separar `;`, `&`, `|`, `<`, `>`, `(`, `)`; tirar `$'` antes; com `eval`, `sh -c` ou `bash -c` no corpo, ler também as palavras do argumento; casar parênteses por profundidade no lugar de `[^()`]*`, com a substituição interna como argumento não legível (o `.git`). Fixtures: S1 a S4 e as variantes. Esforço P. Dono: tech-lead.

**A9 (baixa, recomendado; já existia).** Destino opaco sem resto cujo valor só a execução sabe (`$(echo .git)`, `$(printf %s .git)`, função, variável no corpo). O hook não prova o valor de execução arbitrária. Correção mínima: com destino opaco sem resto, conferir também `<raiz>/.git/<nome da origem>` quando o nome da origem é do diretório do git (`config`, `hooks`, `HEAD`, `index`, `forge`), com o custo de falso positivo do A7. Cartão. Esforço P. Dono: tech-lead.

**A4 (média, recomendado; já existia).** Sem mudança. `cd`/`pushd` para `$(…)`, crase ou variável lida como `.git` muda a pasta da escrita seguinte; na dúvida, escrita relativa depois de `cd` opaco recusa. Cartão. Esforço M. Dono: tech-lead.

**A5 (média, recomendado; parcial).** Sem mudança. `mv` está em `TODOS_OS_ARGUMENTOS` (`hooks/conformidade.py:124`) e o ramo de `hooks/conformidade.py:1496-1498` pula toda palavra que começa com `-`. Correção mínima: nesse ramo, ler `--target-directory=<pasta>` e `-t<pasta>` como destino (comandos que os aceitam: `cp`, `mv`, `install`, `ln`). Cartão com prioridade. Esforço P. Dono: tech-lead.

**A6 (fechado).** `ln -s "$(git rev-parse --git-dir)" g && cp x g/config` recusa no head.

**A7 (baixa, recomendado).** Sem mudança; limite aceito desta entrega. Cartão para não aplicar a regra a `$TMPDIR` e `$(mktemp …)`. Esforço P. Dono: tech-lead.

**A8 (média, recomendado; já existia).** Sem mudança. `hooks/conformidade.py:1509` só reconhece `-t` como palavra própria. Correção mínima: `-t<pasta>` colado é o destino, junto da correção do A5. Cartão com prioridade. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `git archive`, o montador de fixtures do repositório e `tests/test_hook_git_comum.py` (OK, 58 fixtures). Mutantes G15 a G19 e cobertura não rodados por mim (são do QA, que os conferiu na E20.20). `gitleaks`, `semgrep`, `zizmor` e `actionlint` não foram usados (o delta não toca workflow nem segredo; nada instalado, `R-CUSTO`).
