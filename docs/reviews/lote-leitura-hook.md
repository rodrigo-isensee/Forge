---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: a1a9f846f4c8521b9be147ea1890f407348b7fea
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote-leitura-hook (revalidação 4)

Escopo: a entrega inteira, `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 a1a9f846f4c8521b9be147ea1890f407348b7fea`. Revalidei por delta desde o parecer anterior (af6d910, sobre f8e00ae). `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou o intervalo `f8e00ae..e62b1b6`: 419bcdf, 09d8ce5 e a1a9f84, em `hooks/_comum.py` (839-843, 851-852, 862, 898-936, 938-948, 954-956, 985-1001, 1010), `docs/hooks.md:94`, `tests/test_hooks.py` e as 13 fixtures novas. O e62b1b6 é o parecer da segurança, que não reli como código. Li só esse delta, e os commits até f8e00ae ficam como "já lido". A exceção é a medição de tempo do A1, que também atinge o `pipeline_do_operador` do 66c23b0, já lido. Sou revisor independente, não o autor. A segurança (E1.3) tem parecer próprio em `docs/security/lote-leitura-hook.md`, que não refiz aqui.

## Achados
- A1 (bloqueante) hooks/_comum.py:897 · comando_logico relê o texto do início com abertos_na_linha a cada heredoc (quadrático): 3000 heredocs (77 KB) com git push origin main levam 26,9 s no conformidade (base 1,2 s), acima do timeout de 10 s, em que o hook libera
- A2 (bloqueante) hooks/_comum.py:994 · outro_sem_o_corpo aceita git commit e git push, que rodam os hooks de core.hooksPath: cat > .husky/pre-push <<'EOF' && git push origin feature/x com gh pr merge no corpo passa no parecer (base 2, HEAD 0); confirmado no bash com git commit

## Parecer
**Reprovado.** O A1, o A2 e o A3 da segurança de 3e5d570 estão resolvidos nas sondas abaixo, nos dois hooks. O delta trouxe dois bloqueantes novos, e um deles vem do risco que o autor apontou. O A1 é uma regressão de tempo: passar do timeout de 10 s do `hooks/hooks.json` faz o Claude Code liberar a linha, o que afrouxa R-MAIN e R-VERIFY. O A2 é a mesma classe do A1 da segurança: um comando da lista positiva roda o arquivo que o heredoc grava. A segurança achou na mesma rodada (e62b1b6, A1) outro furo do `git push` na lista, pelas opções. Esta já é a 4.ª volta, aberta como exceção pelo dono e só para A1 a A3. Pelo R-QA, uma 5.ª volta é decisão do dono, e o Jarvis leva a pergunta (R-DECISAO).

### Sondas
As sondas rodaram em cópias por `git archive` da base (ad6d96c), do HEAD anterior (f8e00ae) e do HEAD (a1a9f84) em `$TMPDIR`. O hook real rodou pelo `Fixture`, pelo `montar_proc` e pelo `rodar` de cada cópia. Os modelos foram `conformidade/heredoc-outro-comando-make-push-main-bloqueia` (corpo `git push origin main`) e `parecer/forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia` (corpo `gh pr merge` com review reprovado).

| Caso (hook) | base | f8e00ae | a1a9f84 |
|---|---|---|---|
| `&& chmod +x x.sh && ./x.sh`, `; ./x.sh`, `&& make`, `&& git -c alias.x='!sh x.sh' x` (conformidade) | 2 | 0 | **2** |
| `x=$(cat <<'EOF'`⏎…⏎`EOF`⏎`); eval "$x"`, e com `${z%)}` na linha do operador (conformidade) | 2 | 0 | **2** |
| `sort -S 1k --compress-program=sh <<'EOF'` (conformidade) | 2 | 0 | **2** |
| `./x.sh`, `eval "$x"` e `sort --compress-program` com `gh pr merge` no corpo (parecer) | 2 | 0 | **2** |
| `git add … && git commit -m "$(cat <<'EOF'` com `it's` e `&& git push origin feature/x` (conformidade) | 0 | 0 | 0 |
| `cd src && git add && git commit` com `it's`, `cat > n.md <<'EOF' && git add n.md` com `it's` (conformidade) | 0 | 0 | 0 |
| `cat > .githooks/pre-push <<'EOF' && git push …` e `cat > .git/hooks/pre-push …` (conformidade) | 2 | 2 | 2, pela proteção de pasta |
| `cat > .githooks/pre-push <<'EOF' && git push origin feature/x` com `gh pr merge` (parecer) | 2 | 0 | 0, o conformidade barra a mesma linha |
| **A2:** `cat > .husky/pre-push <<'EOF' && git push origin feature/x` e `cat > .husky/pre-commit <<'EOF' && git commit -m x`, com `gh pr merge` (parecer) | 2 | 0 | **0** |
| os mesmos com `git push origin main` no corpo (conformidade) | 0 | 0 | 0 |
| `git commit -m "$(cat <<'EOF'` com `it's` e `&& git log --oneline -1`, `&& echo feito` ou `; git diff --stat` (conformidade) | 0 | 0 | **2** |
| `gh pr create --draft --body "$(cat <<'EOF'` com `it's` e `&& echo ok` (parecer) | 0 | 0 | **2** |

No bash, o A2 se confirma assim: num repositório com `core.hooksPath .husky`, `cat > .husky/pre-commit <<'EOF' && git commit -q -m x` com `echo RODOU-NO-HOOK` no corpo imprime `RODOU-NO-HOOK` e faz o commit. O husky é comum nos projetos de stack node. A proteção de `.git/` e de `.githooks/` não cobre um `core.hooksPath` noutra pasta. O `git commit` entra na lista pelo `corpo_so_lido`, porque está em `GIT_LE_O_CORPO`.

Tempo do `conformidade`, com N vezes `cat > fN <<'EOF'`⏎`x`⏎`EOF`:

| N (tamanho) | base | f8e00ae | a1a9f84 |
|---|---|---|---|
| 1000 (25 KB) | 0,42 s | 1,35 s | 3,34 s |
| 2000 (51 KB) | 0,79 s | 4,30 s | **12,33 s** |
| 3000 (77 KB) + `git push origin main` | 1,21 s (2) | 8,72 s (2) | **26,85 s** (2 só fora do timeout) |
| 5000 (129 KB) + `git push origin main` | 1,97 s | 22,08 s | 75,39 s |

O `cProfile` de `tirar_heredocs` com 2000 heredocs mostra a origem. O `abertos_na_linha` é chamado 2.001.000 vezes, por `comando_logico`, e soma 9,6 s de 14,6 s. O `pipeline_do_operador` (66c23b0) soma mais 5,6 s e já era quadrático em f8e00ae: o parecer anterior não mediu isso. O orçamento de 3 s do `conformidade` não alcança esse custo, porque `tirar_heredocs` roda antes dele.

### Delta lido, por commit
- **419bcdf (A1 de segurança):** a lista negativa `RODA_TEXTO` deu lugar a uma lista positiva (`OUTROS_SEM_O_CORPO`, `GIT_OUTRO_SEM_O_CORPO` e os leitores). A direção está certa e fecha as quatro formas da segurança. Extrair `subcomando_do_git` tirou a duplicação com `corpo_so_lido`. O `" ".join([programa, *argumentos])` relido por `corpo_so_lido` pode desfazer as aspas de um argumento, mas aí a leitura só fica mais desconfiada. O furo está na escolha do conteúdo da lista: `git push` e `git commit` rodam hooks (A2 deste parecer) e aceitam opções que rodam programa (A1 da segurança em e62b1b6).
- **09d8ce5 (A2 de segurança):** `abertos_na_linha` lê aspas, escape, `$(` dentro de aspas duplas, crase e comentário, e na dúvida a pilha cresce, o que fecha na dúvida. As quatro formas do teste, inclusive `# )` e `")"`, saem 2. Na sonda, o `${z%)}`, que a pilha lê errado, também sai 2. Só que `comando_logico` agora percorre o texto do começo, caractere a caractere, para cada heredoc (A1 deste parecer). Correção sugerida: calcular os limites dos comandos lógicos uma vez por texto, em `tirar_heredocs`, e achar o de cada operador por busca. Valem o mesmo para o `pipeline_do_operador` e um teste de tempo com milhares de heredocs, como o de orçamento que já existe.
- **a1a9f84 (A3 de segurança):** o `sort` sai de `LEITORES_DO_CORPO`, com comentário do porquê e caso novo em `executados`. Resolvido.
- **Docs:** `docs/hooks.md:94` descreve a lista positiva dos outros comandos e a junção por `(`, aspa ou crase sem par. Precisa mudar junto com a correção do A2.
- **Testes:** o mínimo de `noutra_linha` subiu de 11 para 21, e há 12 fixtures `-bloqueia` e uma `-libera` para a forma comum do commit. O teste de ausência continua com mínimo afirmado.

### Recomendações (fora do bloco)
- **Falso positivo novo:** `git commit -m "$(cat <<'EOF'` com apóstrofo e `&& git log --oneline -1`, `&& echo feito` ou `; git diff --stat` recusam, e a base liberava. O mesmo vale para `gh pr create --body "$(cat <<'EOF'` com `&& echo ok` no `parecer`. A mensagem dá a saída por arquivo, e apóstrofo é raro em texto em português, por isso não bloqueia. Para a correção do A2: o heredoc cujo dono não grava arquivo (sem `>` nem `tee`), como `git commit -F -` ou `"$(cat <<'EOF'`, não deixa nada para outro comando rodar. Aí `echo`, `printf`, `git log`, `git diff`, `git show`, `git push` e `git commit` poderiam ficar na lista sem risco. Quando o dono grava arquivo, ficam só `cd`, `mkdir`, `git add`, `git status` e os leitores.
- Continua valendo o que o parecer anterior pediu ao integrador (E1.5): R6 na descrição do PR, rótulo `afrouxa-regra` e o cartão HOOK-N4 no quadro antes do merge.
- Os commits estão limpos, um por achado, em Conventional Commits em português, com o porquê na mensagem.

### Invariantes e ferramentas
O delta não toca em `tests/config.json`. Rodei só os testes da área que mudou, na cópia do HEAD: `python3 -m unittest tests.test_hooks -k heredoc -k fixture -k corpo` deu 4 testes OK em 35 s. Não refiz a suíte. O pre-push deste parecer roda as classes dos pareceres.
