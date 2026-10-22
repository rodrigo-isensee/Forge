# Como fechar A1 e A2 do lote-leitura-hook numa volta só?

Propósito: dar ao implementador (E3.1) e aos pareceres (E3.2 a E3.4) **a mesma lista fechada** do que a leitura de heredoc precisa cobrir, o caminho técnico e o critério de parada da rodada, para o lote chegar ao PR sem uma 6.ª volta. Público: `tech-lead` (revisão em E2.2 e implementação), `security-engineer`, revisor independente, `qa-engineer`. Revisão: 2026-11-22.

Estado: proposta (E2.1 do pedido RET-LEITURA-HOOK). Base: `melhoria/lote-leitura-hook` em `078c9f0` (código de `1b0fb6b`, o sha dos dois pareceres da revalidação 5). Não afrouxa `R-MAIN` nem `R-REVIEW`: toda mudança abaixo recusa mais, menos dois itens marcados (L2 e L3), que voltam ao resultado da `develop` (`ad6d96c`).

Legenda: **[EXE]** resultado de execução registrado nos pareceres da revalidação 5 (`docs/reviews/lote-leitura-hook.md`, tabela "Sondas"); **[INF]** comportamento do bash inferido pela leitura do manual, que o oráculo T6 (seção 4) confirma na implementação. Este desenho não rodou sondas: foi feito por leitura do código e dos pareceres.

## 1. Por que A1 e A2 aconteceram (o padrão, não os casos)
O lote já segue a ADR 0011 na lista dos **programas** (`OUTROS_SEM_O_CORPO`, `GIT_OUTRO_SEM_O_CORPO`, `LEITORES_DO_CORPO`: o que não está na lista faz do corpo comando). Sobraram dois pontos em que a omissão ainda **aceita**:

| Achado | Ponto | Desenho atual | Por que falha |
|---|---|---|---|
| A1 | `GRAVA_REDIRECAO` (`hooks/_comum.py:911`) | enumera as formas que **gravam** (`>`, `>>`, `>\|`, com `(?!&)`) | toda forma que a lista esqueceu conta como "não grava": `>&arquivo` grava no bash [EXE] |
| A2 | `DonosDosHeredocs.montar` (`hooks/_comum.py:891`) | os "outros comandos" e o `grava_arquivo` olham só o **comando lógico** do heredoc | o arquivo gravado continua no disco depois do comando lógico; a quebra de linha separa o comando lógico, e o `./x.sh` da linha seguinte fica fora [EXE] |

Os dois são o mesmo erro da ADR 0011, Contexto: uma enumeração do que é perigoso (redireções que gravam; separadores que encerram o escopo). Tapar só `>&` e só a quebra de linha deixa a classe aberta: a próxima sonda seria `trap ./x.sh EXIT` numa linha **anterior**, um `.gitconfig` gravado e lido pelo `git` com `HOME=.`, ou um corpo em Python rodado por `python3 x.py` (que, conferido como comando de shell, não mostra a ação). Por isso o desenho troca as duas enumerações por regras positivas e acrescenta uma recusa de falha fechada na forma do item 2 da ADR 0011.

## 2. O caminho escolhido (parte b)

### 2.1 Alternativas
| Opção | Custo | Risco | Veredito |
|---|---|---|---|
| (A) Tapar os dois casos: `>&` seguido de não dígito conta como gravação; a quebra de linha deixa de encerrar o escopo | P (duas expressões) | Alto: a classe segue aberta (exemplos da seção 1); 6.ª volta provável | recusada |
| **(B) Correção no lote por construção** (esta): classificação positiva das redireções, escopo do texto inteiro da chamada, recusa de "heredoc gravado com programa fora da lista" como construção não modelada (ADR 0011, item 2), atribuição antes do dono | P a M: cerca de 80 a 120 linhas em `hooks/_comum.py`, cerca de 10 em cada hook, um arquivo de corpus, uma classe de teste, um fixture invertido e um novo, a linha 94 de `docs/hooks.md` | Médio-baixo: falsos positivos novos, listados na seção 5 com o contorno; nenhuma regra afrouxa | **escolhida** |
| (C) Esperar o N-HOOK1 (analisador da ADR 0011 por inteiro) | G: o cartão N-HOOK1 está em "Entrada" no `KANBAN.md`, sem branch nem PR, e a "ADR do N-HOOK1" que os pareceres citam (regras 2.2, 2.3, 3.1, 4 e 5) não existe em nenhuma worktree nem na `develop`; seria ADR nova, analisador novo e re-review de toda a leitura dos hooks | Alto em prazo e escopo; o lote fica parado depois de 5 voltas, contra a decisão do dono de 2026-10-22 ("eu nao posso ficar sem implementar um pedido") | recusada para o lote; o N-HOOK1 herda o corpus da seção 4 como base de aceite |

### 2.2 O que muda (requisitos para o E3.1; a forma exata do código é do implementador)
Tudo em `hooks/_comum.py`, usado pelos dois hooks, calculado **uma vez por texto** dentro de `DonosDosHeredocs` (o orçamento de tempo da regra 3.1 continua valendo; os testes de tempo do lote seguem como estão).

**M1. Redireções por classificação positiva (fecha a classe R, A1).** Trocar `GRAVA_REDIRECAO` por uma leitura de **todo** operador de redireção fora de aspas simples: prefixo opcional (`\d+`, `&` ou `{nome}`) seguido de `<<<`, `<<-`, `<<`, `<>`, `<&`, `>&`, `>>`, `>|`, `<` ou `>`, e o alvo. Uma redireção **não grava** só se estiver nesta lista fechada:
- entrada: `<alvo`, `<<`, `<<-`, `<<<`, `[n]<&m`, `[n]<&-`;
- cópia ou fechamento de descritor: `[n]>&m`, `[n]>&-`, `[n]>&m-`, com `m` só dígitos (espaço entre `>&` e o número aceito);
- saída para exatamente `/dev/null` (`>`, `>>`, `>|`, `&>`, `&>>`, com ou sem número antes; com ou sem aspas duplas no alvo).

Qualquer outra conta como gravação: `>&arquivo`, `>& arquivo`, `[n]>&arquivo`, `&>`, `&>>`, `<>`, `[n]<>`, `{fd}>`, `> >(…)`, `>(…)`, alvo com `$` ou montado. A lista de `tee`, `uniq`, `-o`/`--output`, `git apply` e `git am` fica como está.

**M2. Escopo do texto inteiro da chamada (fecha a classe S, A2).** Os "outros comandos" de um heredoc deixam de ser os do comando lógico e passam a ser **todos os programas do texto** (a linha sem os corpos, `resto`), antes e depois do heredoc, em qualquer nível de substituição, separados por qualquer coisa. `grava_arquivo` também roda sobre o texto inteiro. Na prática: em `DonosDosHeredocs.__init__`, `self.grava = grava_arquivo(resto)` e `self.fora_do_texto` = os programas de `programas_e_atribuicoes(resto)` que `outro_sem_o_corpo` recusa (ou todos, com `muda_o_ambiente`, ou o `git`, com `self.grava`); `montar` junta `fora_do_texto` ao dono nos dois ramos (pipeline e comando lógico inteiro), no lugar do `fora_da_lista[lugar]` e do `"\ngit"`. Com isso a enumeração de separadores some do desenho: quebra de linha, `;`, `&`, `&&`, `||`, `|`, `|&`, `!`, subshell, chaves, `$(…)`, crase, `<(…)`, `coproc`, `if`/`while`/`for` e `trap` deixam de importar, porque o programa entra na conta onde quer que esteja.

**M3. Heredoc gravado com programa fora da lista é construção não modelada (fecha o que o corpo conferido como shell não mostra).** Entrada nova na lista fechada do item 2 da ADR 0011: o texto tem heredoc, `self.grava` é verdadeiro e `fora_do_texto` não está vazio. Com o marcador crítico do hook na linha **com os corpos** (`CRITICO` do `conformidade`; `CRITICO` do `parecer`), a linha é recusada depois das regras específicas, como as outras construções do item 2: `R-CONFORMIDADE` no `conformidade` e `R-REVIEW` no `parecer`. O corpo continua conferido como comando antes (M2), para a regra específica falar primeiro (`R-MAIN: push direto para main`). Exposição sugerida: um atributo de `DonosDosHeredocs` (`gravado_e_rodado`) devolvido por `tirar_heredocs` sob um parâmetro opcional, para não mudar as quatro chamadas atuais. Mensagem: "a linha grava arquivo por heredoc e roda um programa que o hook não modela; grave o arquivo numa chamada do Bash (ou pelo Write) e rode o programa noutra".

**M4. Atribuição antes do dono (classe V).** `corpo_so_lido` passa a usar `programas_e_atribuicoes`: dono com atribuição antes do programa (`PATH=/tmp/x cat <<'EOF'`, `GIT_CONFIG_COUNT=1 … git commit -F - <<'EOF'`) não só lê o corpo. É a mesma regra que `outro_sem_o_corpo` já aplica aos outros comandos.

**M5. `echo` e `true` na lista dos outros (resolve a recomendação de 7dba2e5, L2 e L3).** `OUTROS_SEM_O_CORPO = {"cd", "mkdir", "echo", "true"}`. São builtins sem efeito além da saída. Uma função com esse nome definida no texto aparece como outro programa (`echo() { ./x.sh; }` põe `./x.sh` em `fora_do_texto`), e a redireção de saída deles conta em M1. Não afrouxa em relação à `develop`, que liberava `&& echo feito` [EXE]. `git log` **não** entra: lê `gpg.program`, pager e `log.showSignature`, superfície maior, e fica como falso positivo conhecido (F2).

**M6. Mensagens, documentação e ADR.**
- `hooks/conformidade.py:725-727` e `hooks/parecer.py:358-360`: o contorno "passe o arquivo ao programa depois (`patch -p1 < arq`)" passa a dizer "**noutra chamada do Bash**". Na mesma chamada, M2 confere o corpo.
- `docs/hooks.md:94`: trocar "os outros comandos do comando lógico (depois de `&&`, `||`, `;` ou noutra linha)" por "os outros programas do texto inteiro da chamada, antes ou depois do heredoc"; trocar a lista de redireções que gravam pela lista fechada das que não gravam (M1); registrar M3 e M4; o contorno passa a ser "noutra chamada". Seção [B] (linha 92): "um script gravado e executado depois" passa a "gravado e executado noutra chamada, ou na mesma chamada por um comando que não é heredoc (`printf … > x.sh`)" (X1).
- ADR 0011, item 2: acrescentar à lista fechada "heredoc que grava arquivo, com programa fora da lista positiva no texto (`hooks/_comum.py`, `DonosDosHeredocs`)" e a linha "Emendado pelo lote LEITURA-HOOK". Endurece, não precisa do rótulo `afrouxa-regra`.
- Fragmento `changelog.d/lote-leitura-hook.md`: uma linha para M1 a M5.

## 3. As classes de furo e o corpus (parte a)
Notação: `⏎` é quebra de linha; `{CORPO}` é a linha crítica do modelo de cada hook: `git push origin main` no `conformidade` (modelo `tests/hooks/conformidade/heredoc-outro-comando-make-push-main-bloqueia.json`) e `gh pr merge feature/x --repo <o do modelo> --merge`, com o review reprovado, no `parecer` (modelo `tests/hooks/parecer/forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia.json`). As colunas `conf` e `par` dão o código de saída esperado. "Regra" diz o que fecha o caso.

### Classe R: redireções que gravam
Forma única: `cat <OP> .husky/pre-push <<'EOF' && git push origin feature/x⏎{CORPO}⏎EOF` (o `git` roda o gancho gravado). Onde a forma pede, o alvo vem colado ao operador.

| ID | `<OP>` | conf | par | Regra | Origem |
|---|---|---|---|---|---|
| R1 | `>` | 2 | 2 | M1, M3 | regressão (rev. 5: 2 / 2) [EXE] |
| R2 | `>>` | 2 | 2 | M1, M3 | regressão |
| R3 | `>\|` | 2 | 2 | M1, M3 | regressão [EXE] |
| R4 | `1>` e `2>` | 2 | 2 | M1, M3 | descritor numerado |
| R5 | `9>` | 2 | 2 | M1, M3 | descritor alto |
| R6 | `&>` | 2 | 2 | M1, M3 | |
| R7 | `&>>` | 2 | 2 | M1, M3 | |
| R8 | `>&` colado (`>&.husky/pre-push`) | 2 | 2 | M1, M3 | **A1** (rev. 5: 0 / 0) [EXE] |
| R9 | `>& ` com espaço | 2 | 2 | M1, M3 | A1 [EXE] |
| R10 | `1>&` com alvo não numérico | 2 | 2 | M1 (na dúvida, grava) | [INF]: o bash dá erro de redireção e não grava; recusar é só mais desconfiado |
| R11 | `<>` e `1<>` | 2 | 2 | M1, M3 | regressão para `1<>` [EXE] |
| R12 | `{fd}>` | 2 | 2 | M1, M3 | descritor nomeado [INF] |
| R13 | `> ".husky/pre-push"` e `> '.husky/pre-push'` | 2 | 2 | M1, M3 | regressão para aspas duplas [EXE] |
| R14 | `cat <<'EOF' > >(sh)⏎{CORPO}⏎EOF` (sem `git`) | 2 | 2 | M1 e `sh` em `fora_do_texto` | substituição de processo |
| R15 | `exec 3>x.sh; cat <<'EOF' >&3; ./x.sh⏎{CORPO}⏎EOF` | 2 | 2 | M1 (`3>`), M2 | descritor aberto antes |
| R16 | `cat <<'EOF' \| tee .husky/pre-push && git push origin feature/x` e `tee -a` | 2 | 2 | lista atual, M3 | regressão [EXE] |
| R17 | `git apply <<'EOF' && git commit -m x` e `-o`/`--output=` | 2 | 2 | lista atual, M3 | regressão [EXE] |
| R18 | `cat >&x.sh <<'EOF' && git add x.sh && git commit -m x` | 2 | 2 | M1, M3 | A1, 3.ª forma [EXE] |

### Classe N: redireções que não gravam (o `git` segue na lista)
Forma: `cat <OP> <<'EOF' && git push origin feature/x⏎{CORPO}⏎EOF`. O corpo vai só para o `cat`, ninguém o roda: o resultado esperado é 0.

| ID | `<OP>` | conf | par |
|---|---|---|---|
| N1 | `>/dev/null`, `2>/dev/null`, `&>/dev/null`, `>>/dev/null` | 0 | 0 |
| N2 | `2>&1`, `>&2`, `1>&2`, `>&-`, `3>&1-`, `>& 2` | 0 | 0 |
| N3 | `<&0` e `0<&-` | 0 | 0 |

N1 com `>/dev/null` dá 0 / 0 na rev. 5 [EXE]; o N mostra que M1 não recusa a mais.

### Classe S: separadores, e o que roda antes e depois do heredoc na mesma chamada
Forma: `cat > x.sh <<'EOF'` com `{CORPO}`, e o `./x.sh` (ou o `git`) ligado como na coluna. Todas as linhas: conf 2, par 2. Regra: M2 (corpo conferido como comando) e M3.

| ID | Ligação |
|---|---|
| S1 | `cat > x.sh <<'EOF' && ./x.sh` (regressão, fixture `heredoc-outro-comando-…`) |
| S2 | `; ./x.sh` (regressão) |
| S3 | `\|\| ./x.sh` |
| S4 | `& ./x.sh` |
| S5 | `…⏎EOF⏎./x.sh` (**A2**, rev. 5: 0 / 0) [EXE] |
| S6 | `cat > x.sh <<'EOF' &&⏎{CORPO}⏎EOF⏎./x.sh` (o `&&` no fim da linha do operador) |
| S7 | `\| ./x.sh` e `\|& ./x.sh` |
| S8 | `…⏎EOF⏎(./x.sh)` e `…⏎EOF⏎{ ./x.sh; }` |
| S9 | `…⏎EOF⏎echo $(./x.sh)` e `` …⏎EOF⏎echo `./x.sh` `` |
| S10 | `…⏎EOF⏎if ./x.sh; then :; fi` e `…⏎EOF⏎while ./x.sh; do break; done` |
| S11 | `…⏎EOF⏎! ./x.sh` e `…⏎EOF⏎coproc ./x.sh` |
| S12 | `…⏎EOF⏎diff <(./x.sh) README.md` |
| S13 | `…⏎EOF⏎bash x.sh`, `sh x.sh`, `source x.sh`, `. x.sh`, `make` |
| S14 | `trap ./x.sh EXIT⏎cat > x.sh <<'EOF'…` (o programa vem **antes** do heredoc) |
| S15 | `cat > .husky/pre-push <<'EOF'⏎{CORPO}⏎EOF⏎git push origin feature/x` (**A2**, 2.ª forma, rev. 5: 0 / 0) [EXE] |
| S16 | o mesmo com `git commit -m x` na linha seguinte |

### Classe H: forma do heredoc e o que vem depois dele
Todas: conf 2, par 2.

| ID | Sonda | Regra |
|---|---|---|
| H1 | `cat <<'EOF' > x.sh⏎{CORPO}⏎EOF⏎./x.sh` (redireção depois do operador) | M1, M2 |
| H2 | `cat > x.sh <<-'EOF'⏎<tab>{CORPO}⏎<tab>EOF⏎./x.sh` | M2 |
| H3 | dois heredocs: `cat > x.sh <<'A'⏎{CORPO}⏎A⏎cat <<'B'⏎texto⏎B⏎./x.sh` | M2 |
| H4 | `cat <<'A' <<'B' > x.sh⏎texto⏎A⏎{CORPO}⏎B⏎./x.sh` (só o último vai à entrada) | M2 |
| H5 | `cat > x.sh <<'EOF'⏎{CORPO}⏎EOF⏎chmod +x x.sh && ./x.sh` | regressão (fixture `…-chmod-e-script-…`) |
| H6 | `x=$(cat <<'EOF'⏎{CORPO}⏎EOF⏎); eval "$x"` | regressão (fixture `…-substituicao-fecha-…-eval-…`) |
| H7 | `cat > x.py <<'EOF'⏎import os; os.system('{CORPO}')⏎EOF⏎python3 x.py` | M3: o corpo, lido como shell, pode não mostrar a ação; o marcador crítico mostra |
| H8 | `cat > .gitconfig <<'EOF'⏎[core]⏎sshCommand = sh -c '{CORPO}'⏎EOF⏎HOME=.⏎git push origin feature/x` (atribuição sozinha, que a leitura não vê) | M3 (`git` fora pela gravação, marcador `push`) |

### Classe V: atribuições e ambiente que mudam o programa
Todas: conf 2, par 2.

| ID | Sonda | Regra |
|---|---|---|
| V1 | `cat > x.sh <<'EOF' && GIT_SSH=./x.sh git push origin feature/x` | regressão (2af1983) [EXE] |
| V2 | `export GIT_SSH=./x.sh; cat > x.sh <<'EOF' && git push …` | regressão [EXE] |
| V3 | `cat > x.sh <<'EOF' && env GIT_SSH=./x.sh git push origin feature/x` | `MUDAM_O_AMBIENTE` |
| V4 | `… && git push --receive-pack='sh x.sh'`, `--rec=`, `git -C . push --exec=` | regressão [EXE] |
| V5 | `PATH=/tmp/x:/usr/bin cat <<'EOF'⏎{CORPO}⏎EOF` | **M4** |
| V6 | `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=.husky git commit -F - <<'EOF'⏎{CORPO}⏎EOF` | **M4** |
| V7 | `git -c core.hooksPath=.husky commit -F - <<'EOF'⏎{CORPO}⏎EOF` | atual (`-c` tira o subcomando) |
| V8 | `alias cat=bash⏎cat <<'EOF'⏎{CORPO}⏎EOF` e `hash -p /bin/bash cat⏎cat <<'EOF'…` | M2 (`alias` e `hash` em `fora_do_texto`) |
| V9 | `cat() { bash; }⏎cat <<'EOF'⏎{CORPO}⏎EOF` | M2 (`bash` do corpo da função em `fora_do_texto`) |

### Classe L: usos legítimos que continuam liberados
| ID | Sonda | conf | par | Nota |
|---|---|---|---|---|
| L1 | `git add src/app.js && git commit -m "$(cat <<'EOF'⏎fix: it's done⏎EOF⏎)" && git push origin feature/x` | 0 | — | fixture atual |
| L2 | `git commit -m "$(cat <<'EOF'⏎fix: it's done⏎EOF⏎)" && echo feito` | 0 | — | M5 (rev. 5: 2; `develop`: 0) [EXE] |
| L3 | `gh pr create --draft --base develop --title t --body "$(cat <<'EOF'⏎it's ok⏎EOF⏎)" && echo ok` | 0 | 0 | M5 (rev. 5: 2) [EXE] |
| L4 | `mkdir -p notas && cd notas && cat > n.md <<'EOF'⏎it's⏎EOF` | 0 | — | fixture atual |
| L5 | `cat <<'EOF' 2>&1 \| git commit -F - && git push origin feature/x⏎feat: x⏎EOF` | 0 | — | N2 |
| L6 | `cat > n.md <<'EOF'⏎texto sem apóstrofo nem marcador⏎EOF⏎git add n.md` | 0 | — | M2 confere o corpo, que é inofensivo; M3 não age sem marcador |
| L7 | `cat <<-X⏎<tab>corpo⏎<tab>X⏎ls` | 0 | — | fixture atual |
| L8 | duas chamadas (`passos` do `Fixture`): `cat > mudanca.diff <<'EOF'⏎-it's⏎+it is⏎EOF` e depois `patch -p1 < mudanca.diff` | 0 e 0 | — | o contorno novo das mensagens (M6) |
| L9 | `BODY="$(cat <<'EOF'⏎it's ok⏎EOF⏎)"; gh pr create --draft --base develop --title t --body "$BODY"` | — | 0 | fixture atual do `parecer` |

"—": o hook não age na linha (no `parecer`, o `PREFILTRO` não casa) ou a coluna não se aplica; o corpus não roda essa célula.

### Classe X: fora do escopo desta volta (não reprova; vai a cartão)
Critério: ADR 0011, item 3. A sonda não é regressão contra a `develop` e depende de estado gravado antes ou de construção fora dos heredocs.

| ID | Sonda | Por quê | Destino |
|---|---|---|---|
| X1 | gravação por argumento e execução na mesma chamada: `printf '%s\n' '{CORPO}' > x.sh && sh x.sh`, `echo '{CORPO}' > .husky/pre-push; git push origin feature/x`, `cat > x.sh <<< '{CORPO}'` numa linha só | não há heredoc; a `develop` libera igual; limite [B] (`docs/hooks.md:92`), com o `pre-push` e a proteção de branch como camada | N-HOOK1 (a regra M3 sem a condição "heredoc" tem falso positivo alto: `npm test > out.txt && git push`) |
| X2 | `PATH=/tmp/x:/usr/bin` sozinho numa linha antes de `cat <<'EOF'`, `read PATH <<'EOF'`, função exportada no ambiente, `remote.<r>.receivepack` na configuração | depende de executável ou configuração gravados antes (R2 da segurança) | N-HOOK1, regra 2.3 (`CONFIG_PROTEGIDA`) |
| X3 | marcador ofuscado: `git p''ush` no corpo, `os.system('gh pr m' + 'erge …')` | o `CRITICO` lê o texto cru | cartão C8 da ADR 0011 |

## 4. Os testes que viram o corpus (parte c)
**Arquivo de dados:** `tests/fixtures/heredoc-volta-unica.json`, ao lado de `tests/fixtures/brief/`, fora de `tests/hooks/`: o `glob("*/*.json")` de `Hooks.setUp` o tomaria por um hook. Formato:

```json
{
  "modelos": {
    "conformidade": "heredoc-outro-comando-make-push-main-bloqueia",
    "parecer": "forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia"
  },
  "corpos": {"conformidade": "git push origin main", "parecer": "<a linha do modelo do parecer>"},
  "casos": [
    {"id": "R8", "classe": "R", "comando": "cat >&.husky/pre-push <<'EOF' && git push origin feature/x\n{CORPO}\nEOF",
     "conformidade": 2, "parecer": 2, "origem": "A1 rev. 5"},
    {"id": "L8", "classe": "L", "passos": ["cat > mudanca.diff <<'EOF'\n-it's\n+it is\nEOF", "patch -p1 < mudanca.diff"],
     "conformidade": 0, "parecer": null}
  ]
}
```

Uma entrada por linha das tabelas R, N, S, H, V e L. Quando a célula tem variantes ("`1>` e `2>`"), cada variante vira um caso com sufixo (`R4a`, `R4b`). `null` quer dizer que a célula não roda. A classe X **não** entra nos casos: fica só neste documento e no cartão.

**Classe de teste:** `CorpusHeredocVoltaUnica` em `tests/test_hooks.py`, que reusa `Fixture`, `executar_em_lote` e `rodar`:
- `test_corpus_nos_dois_hooks`: para cada caso e hook com valor, monta o `Fixture` do modelo daquele hook com o `command` trocado (`{CORPO}` pelo corpo do hook; `passos` vira os `passos` do `Fixture`, com a última entrada como principal) e confere o código. O `stderr` só é conferido para `2`, pelo prefixo `R-`. Roda em paralelo, como os fixtures, abaixo de 30 s.
- `test_oraculo_das_redirecoes` (T6, fecha M1 por construção): para cada operador das classes R e N, roda `bash --noprofile --norc -c "cat <OP>alvo <<'EOF'⏎x⏎EOF"` numa pasta temporária, com o ambiente limpo e o `PATH` só com `/usr/bin:/bin`. Afirma: se o bash criou ou mudou um arquivo na pasta, `grava_arquivo` dá verdadeiro; para todo operador da classe N, `grava_arquivo` dá falso (M1 não recusa a mais). Só roda `cat`, sem rede e sem custo (`R-CUSTO`). R10 confirma o [INF]: o bash não grava, e `grava_arquivo` dá verdadeiro (permitido: só a implicação é exigida).
- `test_corpus_cobre_as_classes`: as classes R, N, S, H, V e L têm pelo menos o número de casos destas tabelas (`minimo`), e os IDs R8, R9, R18, S5 e S15 (A1 e A2) estão presentes. O corpus não encolhe sem aparecer no diff do teste.

**Ordem no E3.1**, um commit por passo, para a reversão por commit: (1) o corpus e a classe de teste, vermelhos em R8, R9, R12, R18, S5, S6, S14 a S16, H1 a H4, H7, H8, V5, V6, L2 e L3, com a saída do vermelho na mensagem; (2) M1; (3) M2; (4) M3; (5) M4; (6) M5; (7) M6 e o fixture invertido (seção 5, F3). A suíte inteira e `scripts/validar-plugin.sh` verdes no fim.

**Critério de parada da rodada** (o que E3.2 e E3.3 usam; é o item 3 da ADR 0011 aplicado a este lote, sem regra nova): o parecer reprova só por (i) caso do corpus com código errado; (ii) sonda numa das classes R, S, H ou V que sai 0 com efeito no bash **e** que a `develop` barrava, ou que fura `R-MAIN` ou `R-REVIEW` sem outra camada. Nesse caso, a sonda entra no corpus no mesmo commit da correção. Sonda da classe X, ou fora das seis classes, vira cartão (N-HOOK1), não reprovação. O `tech-lead` registra na revisão do desenho (E2.2) se aceita este critério.

## 5. Falsos positivos conhecidos (parte d)
Todos recusam com a mensagem que dá o contorno. Entram no corpus como casos de classe `F` com o código 2: assim o falso positivo fica medido, e a sua correção futura aparece como mudança de teste. Contam para o critério de reversão da ADR 0011 ("recusas legítimas por construção não modelada").

| ID | Sonda | conf | Novo em relação a `1b0fb6b`? | Contorno |
|---|---|---|---|---|
| F1 | `cat > n.md <<'EOF'⏎it's⏎EOF` `&& git add n.md` | 2 | não (rev. 5: 2; `develop`: 0) [EXE] | gravar pelo Write, ou o `cat` numa chamada e o `git add` noutra. O `git add` roda filtros e `fsmonitor` lidos de arquivos (letra c da regra 2.2 citada pelo review), e o corpo com apóstrofo não se lê como comando |
| F2 | `git commit -m "$(cat <<'EOF'⏎it's⏎EOF⏎)" && git log -1` | 2 | não [EXE] | `git log` noutra chamada; fica fora de M5 pela superfície (`gpg.program`, pager) |
| F3 | `cat > mudanca.diff <<'EOF'⏎…it's…⏎EOF⏎patch -p1 < mudanca.diff` na mesma chamada | 2 | **sim** (M2): o fixture `heredoc-apostrofo-gravado-em-arquivo-e-patch-depois-libera` passa a `…-patch-na-mesma-chamada-bloqueia`, e L8 é o novo `-libera` em duas chamadas | duas chamadas (as mensagens de M6 já dizem isso). É a forma exata do A2: o `patch` não está na lista positiva |
| F4 | `cat > notas.md <<'EOF'⏎…⏎EOF⏎git add notas.md && git commit -m x && git push origin melhoria/x` | 2 | **sim** (M3: grava, `git` fora, marcador `push`) | gravar pelo Write (o caminho normal dos agentes) e deixar a chamada do Bash só com `git` |
| F5 | `python3 -m unittest && git commit -F - <<'EOF'⏎it's⏎EOF` | 2 | não (o `&&` já punha `python3` no comando lógico) | `git commit -m "$(cat <<'EOF'…)"` numa chamada sem outro programa fora da lista |
| F6 | qualquer chamada com heredoc cujo corpo tem apóstrofo e outro programa fora da lista **noutra linha** (`…⏎EOF⏎ls`) | 2 | **sim** (M2) | o mesmo de F3 |

Antes do passo (7) da ordem acima, o implementador procura outros `-libera` que M2 e M3 invertam (`tests/hooks/*/*-libera.json` com `<<'` e outro programa no texto) e os lista no commit. Afrouxar M2 para F3 ou F6 (pôr `patch`, `ls` e afins na lista positiva) fica de fora: o `patch` com diff no estilo `ed` já executou comando (CVE-2018-1000156), e cada nome novo é uma entrada a defender.

## 6. Riscos e o que fica em aberto
- **Falsos positivos F3, F4 e F6** são os únicos novos. Medida: o critério de reversão da ADR 0011 já conta "não modelado". Se passar de 5 em quatro semanas, a saída é ampliar a lista positiva por programa, com caso no corpus, não voltar ao escopo do comando lógico.
- **Tempo:** M2 troca uma conta por comando lógico por uma conta por texto (menos trabalho), e M3 é uma checagem por texto. Os testes de tempo e de custo do lote (3000 e 5000 heredocs) seguem como teto.
- **Bash inferido:** R10, R12, R14, S4, S7, H4, H7 e H8 são [INF]. O T6 confirma as redireções; os demais, o passo (1) do E3.1 mostra vermelhos e o passo correspondente os deixa verdes.
- **Dependência:** nenhuma de outro lote. O N-HOOK1 recebe este corpus e a classe X.
