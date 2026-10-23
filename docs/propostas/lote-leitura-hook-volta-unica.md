# Como fechar A1 e A2 do lote-leitura-hook numa volta só?

Propósito: dar ao implementador (E3.1) e aos pareceres (E3.2 a E3.4) **a mesma lista fechada** do que a leitura de heredoc precisa cobrir, o caminho técnico e o critério de parada da rodada, para o lote chegar ao PR sem uma 6.ª volta. Público: `tech-lead` (revisão em E2.2 e implementação), `security-engineer`, revisor independente, `qa-engineer`. Revisão: 2026-11-22.

Estado: proposta, volta 1 do desenho (E2.1 do pedido RET-LEITURA-HOOK), resposta ao parecer `docs/reviews/lote-leitura-hook-desenho.md` (reprovado sobre `d557a37`, caminho B aprovado). Base: `melhoria/lote-leitura-hook` (código de `1b0fb6b`, o sha dos dois pareceres da revalidação 5). Não afrouxa `R-MAIN` nem `R-REVIEW`: toda mudança abaixo recusa mais, menos os itens marcados (L2, L3, L10, L12), que voltam ao resultado da `develop` (`ad6d96c`) ou ao que o bash faz.

Legenda: **[EXE]** resultado de execução registrado nos pareceres (revalidação 5, `docs/reviews/lote-leitura-hook.md`, tabela "Sondas"; revisão do desenho, `docs/reviews/lote-leitura-hook-desenho.md`); **[INF]** comportamento inferido pela leitura do manual do bash ou do código de `1b0fb6b`, que o passo (1) do E3.1 confirma (a marca `fecha` da seção 4 obriga a confirmação: caso marcado que não falha deixa a suíte vermelha). Este desenho não rodou sondas.

## 0. Volta 1: o que mudou em relação a `d557a37`
| Achado | Onde fica | Resumo |
|---|---|---|
| A1 (bloqueante) | M2, item "enumerador positivo"; casos S17, S18, R20; teste T7 | o programa é toda palavra que não se prova redireção completa, atribuição ou palavra de `ANTES_DO_PROGRAMA`; `2>&1` colado não consome a palavra seguinte; dono sem programa provado não só lê |
| A2 (bloqueante) | M1, item "leitor sequencial"; casos R19a a R19e; prefixos do T6 | um leitor só, com um estado para as aspas, usado por M1 e M2; nada de `re.sub` de aspas |
| A3 (bloqueante) | seção 4, "Marca `fecha`" e "Ordem no E3.1" | cada caso que ainda falha leva a regra que o fecha; o teste exige a falha dos marcados; cada commit tira as suas marcas e inverte os fixtures que ele mesmo inverte |
| A4 (bloqueante) | seção 2.3 (promessas) e seção 4, "Critério de parada" | reprova só pelo caso (i) ou por sonda com efeito no bash numa forma que a linha "Promete" de uma regra cobre |
| A5 (bloqueante) | seção 5, F6b, F7a, F7b, F8a, F8b, F9, F10; seção 6 | lista completa dos falsos positivos novos, cada um com caso `F` e contorno |
| A6 (recomendado) | T6 | entra: pula com o motivo quando `BASH_VERSINFO[0] < 4` |
| A7 (recomendado) | seção 4, `corpos` | entra: a linha literal do modelo do `parecer` |
| A8 (recomendado) | M6, mensagens e leituras | entra: M2 e M3 com frase própria na mensagem e linha própria nas leituras da ADR 0011 |

Os três recomendados entram: nenhum muda o caminho. A seção 7 enumera as formas vizinhas de cada classe de achado.

## 1. Por que A1 e A2 aconteceram (o padrão, não os casos)
O lote já segue a ADR 0011 na lista dos **programas** (`OUTROS_SEM_O_CORPO`, `GIT_OUTRO_SEM_O_CORPO`, `LEITORES_DO_CORPO`: o que não está na lista faz do corpo comando). Sobraram pontos em que a omissão ainda **aceita**:

| Achado | Ponto | Desenho atual | Por que falha |
|---|---|---|---|
| A1 (rev. 5) | `GRAVA_REDIRECAO` (`hooks/_comum.py:911`) | enumera as formas que **gravam** (`>`, `>>`, `>\|`, com `(?!&)`) | toda forma que a lista esqueceu conta como "não grava": `>&arquivo` grava no bash [EXE] |
| A2 (rev. 5) | `DonosDosHeredocs.montar` (`hooks/_comum.py:891`) | os "outros comandos" e o `grava_arquivo` olham só o **comando lógico** do heredoc | o arquivo gravado continua no disco depois do comando lógico; o `./x.sh` da linha seguinte fica fora [EXE] |
| A1 (desenho) | `programas_e_atribuicoes` (`hooks/_comum.py:1082`) | troca `2>&1`, `>&-` por um `>` solto, que pula a palavra seguinte | `…⏎EOF⏎2>&1 ./x.sh` devolve só `cat`; o bash roda o `./x.sh` [EXE] |
| A2 (desenho) | `grava_arquivo` (`hooks/_comum.py:920`) | `re.sub(r"'[^']*'", "''", …)` antes de procurar redireção | o apóstrofo entre aspas duplas abre uma "aspa simples" falsa que engole o `> .husky/pre-push` [EXE] |

Os quatro são o mesmo erro da ADR 0011, Contexto: uma enumeração do que é perigoso (redireções que gravam; separadores que encerram o escopo; palavras que não são programa; trechos que não são código). Por isso o desenho troca as enumerações por regras positivas, apoiadas num leitor sequencial único (ADR 0011, item 1: "um estado só para as aspas"), e acrescenta uma recusa de falha fechada na forma do item 2.

## 2. O caminho escolhido (parte b)

### 2.1 Alternativas
| Opção | Custo | Risco | Veredito |
|---|---|---|---|
| (A) Tapar os casos: `>&` seguido de não dígito conta como gravação; a quebra de linha deixa de encerrar o escopo | P (duas expressões) | Alto: a classe segue aberta (as linhas A1 e A2 do desenho, acima, são exatamente o caso ao lado); 6.ª volta provável | recusada |
| **(B) Correção no lote por construção** (esta; aceita na revisão do desenho) | P a M: cerca de 150 a 200 linhas em `hooks/_comum.py` (o leitor sequencial substitui duas leituras por expressão regular), cerca de 10 em cada hook, um arquivo de corpus, uma classe de teste, um fixture invertido e um novo, a linha 94 de `docs/hooks.md` | Médio-baixo: falsos positivos novos, listados na seção 5 com o contorno; nenhuma regra afrouxa | **escolhida** |
| (C) Esperar o N-HOOK1 (analisador da ADR 0011 por inteiro) | G: cartão em "Entrada", sem branch, sem ADR | Alto em prazo; o lote fica parado, contra a decisão do dono de 2026-10-22 | recusada para o lote; o N-HOOK1 herda o corpus e a classe X |

### 2.2 O que muda (requisitos para o E3.1; a forma exata do código é do implementador)
Tudo em `hooks/_comum.py`, usado pelos dois hooks, calculado **uma vez por texto** dentro de `DonosDosHeredocs` (o orçamento de tempo da regra 3.1 continua valendo; os testes de tempo do lote seguem como estão).

**Leitor sequencial (base de M1 e M2).** Uma função só (nome sugerido `palavras_do_texto(resto)`) lê a linha sem os corpos da esquerda para a direita, com **um estado** de contexto, como `construcao_nao_modelada` e `abertos_na_linha` já fazem: `fora`, `simples`, `duplas`, `ansi` (`$'…'`), `subst` (`$(…)`, crase, `<(…)`, `>(…)`, com pilha). Regras:
- em `simples`, tudo é literal até o `'`; em `ansi`, `\` escapa o caractere seguinte (o `\'` não fecha); em `duplas` e `$"…"`, `\` escapa só `$`, crase, `"`, `\`, e `$(` e crase abrem `subst`; em `fora` e `subst`, `\` torna o caractere seguinte literal;
- `#` só abre comentário onde `comentarios(linha)` (ADR 0013) o prova; senão é literal;
- `${…}` e `$((…))` são lidos como texto de nível `fora` (o `$(` e a crase dentro deles abrem `subst`): só torna a leitura mais desconfiada;
- separadores (`;`, `&`, `&&`, `||`, `|`, `|&`, quebra de linha, `(`, `)`) e operadores de redireção só valem em `fora` ou `subst`, nunca dentro de aspas;
- texto que termina com contexto aberto (aspas sem par, `subst` sem fechar) é **leitura em dúvida**: `grava` verdadeiro e `fora_do_texto` com a entrada `"?"` (não vazia).
Nenhuma outra função do lote tira aspas por `re.sub` para decidir gravação ou programa. As duas leituras por expressão regular de hoje (`grava_arquivo:920` e `programas_e_atribuicoes:1085`) passam a usar este leitor.

**M1. Redireções por classificação positiva (classe R, A1 da rev. 5, A2 do desenho).** `grava_arquivo` deixa de usar `GRAVA_REDIRECAO` e lê **todo** operador de redireção que o leitor sequencial dá: prefixo opcional (`\d+`, `&` ou `{nome}`) seguido de `<<<`, `<<-`, `<<`, `<>`, `<&`, `>&`, `>>`, `>|`, `<` ou `>`, e o alvo (colado, ou a palavra seguinte). Uma redireção **não grava** só se estiver nesta lista fechada:
- entrada: `<alvo`, `<<`, `<<-`, `<<<`, `[n]<&m`, `[n]<&-`;
- cópia ou fechamento de descritor: `[n]>&m`, `[n]>&-`, `[n]>&m-`, com `m` só dígitos (espaço entre `>&` e o número aceito);
- saída para exatamente `/dev/null` (`>`, `>>`, `>|`, `&>`, `&>>`, com ou sem número antes; com ou sem aspas duplas no alvo).

Qualquer outra conta como gravação: `>&arquivo`, `>& arquivo`, `[n]>&arquivo`, `&>`, `&>>`, `<>`, `[n]<>`, `{fd}>`, `> >(…)`, `>(…)`, alvo com `$` ou montado. A lista de programas que gravam fica como está (`tee`, `uniq`, `-o`/`--output`/`--out`, `git apply`, `git am`), lida com o enumerador de M2. `grava_arquivo` roda sobre o texto inteiro (`resto`), não sobre o comando lógico.

**M2. Escopo do texto inteiro e enumerador positivo de programas (classe S, A2 da rev. 5, A1 do desenho).**
- *Enumerador positivo* (substitui `programas_e_atribuicoes` e, por ele, `programas_da_linha`, em todos os usos: `fora_do_texto`, `grava_arquivo`, `corpo_so_lido`, `muda_o_ambiente`). Sobre as palavras do leitor sequencial, em cada comando simples (entre separadores, em qualquer nível de `subst`): uma palavra é **programa** a não ser que se prove uma destas três coisas:
  1. redireção completa: operador fora de aspas **e** o alvo dele. O alvo é a parte colada depois do operador; só quando não há parte colada, o alvo é a palavra seguinte. `2>&1`, `>&2`, `>&-`, `3>&1-`, `<&0`, `0<&-`, `>/dev/null`, `{fd}>x` são completos e **não consomem** a palavra seguinte; `>&` sozinho, `2>` sozinho, `<` sozinho consomem a seguinte, como no bash;
  2. atribuição: `^[A-Za-z_][A-Za-z0-9_]*\+?=` sobre o começo da palavra fora de aspas, antes do primeiro programa do comando simples;
  3. palavra de `ANTES_DO_PROGRAMA` (`!`, `{`, `time`, `then`, `do`, `else`, `elif`, `if`, `while`, `until`) fora de aspas.
  O primeiro programa de cada comando simples vem com os argumentos e as atribuições daquele comando simples (não as do comando de fora de uma substituição: em `BODY="$(cat <<'EOF'…)"`, o `cat` não tem atribuição).
- *Dono sem programa não só lê.* `corpo_so_lido` devolve falso quando o dono não tem programa provado (hoje o laço vazio devolve verdadeiro).
- *Escopo do texto.* Os "outros comandos" de um heredoc passam a ser **todos os programas do texto** (`resto`), antes e depois do heredoc, em qualquer nível de substituição, separados por qualquer coisa. Em `DonosDosHeredocs.__init__`: `self.grava = grava_arquivo(resto)` e `self.fora_do_texto` = os programas do enumerador que `outro_sem_o_corpo` recusa (ou todos, com `muda_o_ambiente`, ou o `git`, com `self.grava`); `montar` junta `fora_do_texto` ao dono nos dois ramos (pipeline e comando lógico inteiro), no lugar do `fora_da_lista[lugar]` e do `"\ngit"`.

**M3. Heredoc com gravação e programa fora da lista é construção não modelada.** Entrada nova na lista fechada do item 2 da ADR 0011: o texto tem heredoc provado, `self.grava` é verdadeiro e `fora_do_texto` não está vazio. Com o marcador crítico do hook na linha **com os corpos** (`CRITICO` do `conformidade`, `hooks/conformidade.py:39`; `CRITICO` do `parecer`, `hooks/parecer.py:26`), a linha é recusada depois das regras específicas: `R-CONFORMIDADE` no `conformidade` e `R-REVIEW` no `parecer`. O corpo continua conferido como comando antes (M2), para a regra específica falar primeiro. Exposição sugerida: um atributo de `DonosDosHeredocs` (`gravado_e_rodado`) devolvido por `tirar_heredocs` sob um parâmetro opcional, para não mudar as quatro chamadas atuais. Mensagem (frase própria, para a contagem do A8): "heredoc gravado e programa não modelado na mesma chamada (`<programa>`): grave o arquivo pelo Write ou numa chamada do Bash e rode o programa noutra".

**M4. Atribuição antes do dono (classe V).** `corpo_so_lido` usa as atribuições do enumerador: dono com atribuição no mesmo comando simples, antes do programa (`PATH=/tmp/x cat <<'EOF'`, `GIT_CONFIG_COUNT=1 … git commit -F - <<'EOF'`), não só lê o corpo. É a regra que `outro_sem_o_corpo` já aplica aos outros comandos.

**M5. `echo` e `true` na lista dos outros (L2, L3).** `OUTROS_SEM_O_CORPO = {"cd", "mkdir", "echo", "true"}`. Builtins sem efeito além da saída. Uma função ou alias com esse nome definidos no texto aparece como outro programa (`echo() { ./x.sh; }` põe `./x.sh` em `fora_do_texto`; `alias echo=./x.sh` põe `alias`), e a redireção de saída deles conta em M1. `git log` **não** entra (F2).

**M6. Mensagens, documentação e ADR.**
- `hooks/conformidade.py:725-727` e `hooks/parecer.py:358-360`: o contorno "passe o arquivo ao programa depois (`patch -p1 < arq`)" passa a dizer "**noutra chamada do Bash**". Quando o corpo só foi conferido por causa de `fora_do_texto` (o dono sozinho só leria), a mensagem nomeia o programa com a frase própria "o texto roda `<programa>`, fora da lista dos que não rodam o arquivo gravado" (A8). A frase entra em (3), junto com M2.
- `docs/hooks.md:94`: "os outros programas do texto inteiro da chamada, antes ou depois do heredoc"; a lista fechada das redireções que não gravam (M1); o leitor sequencial; M3 e M4; o contorno "noutra chamada". Seção [B] (linha 92): "gravado e executado noutra chamada, ou na mesma chamada por um comando que não é heredoc (`printf … > x.sh`)" (X1).
- ADR 0011, item 2: acrescentar à lista fechada "heredoc que grava arquivo, com programa fora da lista positiva no texto (`hooks/_comum.py`, `DonosDosHeredocs`)" e a linha "Emendado pelo lote LEITURA-HOOK". Nas **Leituras**, duas linhas novas, à parte da linha atual: "recusas legítimas com a frase de M2" e "recusas legítimas com a frase de M3" (A8). Endurece: sem rótulo `afrouxa-regra`.
- Fragmento `changelog.d/lote-leitura-hook.md`: uma linha para M1 a M5.

### 2.3 O que cada regra promete (a base decidível do critério de parada, A4)
Uma sonda só reprova a rodada se cair numa linha **Promete** (seção 4, "Critério de parada"). O que está em **Não promete** vai a cartão.

| Regra | Promete | Não promete (vai a cartão N-HOOK1, com o ID da classe X) |
|---|---|---|
| Leitor | **critério mudou:** na chamada com heredoc e marcador crítico, só a gramática positiva da opção D (K1 a K3, comandos literais de `git`, `gh`, `cd`, `mkdir`, `echo` e `true`, alfabeto do item 1 da ADR 0011; o que não cabe recusa), provada pelo T8 de mutação; motivo: `docs/propostas/lote-leitura-hook-caminho-leitor.md`, decisão do dono de 2026-10-23. Antes: aspas, `$'…'`, `$"…"`, escape, comentário provado e substituição lidos como o bash; contexto aberto no fim = dúvida, que grava e põe `"?"` em `fora_do_texto` (continua valendo sem marcador) | `case … a)` dentro de `$(…)` e crase aninhada (cartão C2 da ADR 0011; o item 2 já recusa com marcador) |
| M1 | em texto com heredoc, toda redireção fora de aspas, em qualquer posição e nível, com qualquer prefixo, é lida; `grava` falso só se todas estão na lista "não grava" e nenhum programa do texto está na lista dos que gravam | descritor herdado de outra chamada (X2); gravação por programa fora da lista de leitores, que já entra em `fora_do_texto` |
| M2 | toda palavra de programa do texto (enumerador positivo) entra em `fora_do_texto`, salvo `outro_sem_o_corpo`; o dono soma `fora_do_texto`; dono sem programa não só lê | programa que não é palavra do texto: alias, função, `PATH` ou configuração de outra chamada (X2); texto reinterpretado por programa fora da lista (o programa já entra) |
| M3 | heredoc provado + `grava` + `fora_do_texto` não vazio + marcador crítico na linha com os corpos = recusa | marcador ofuscado (X3); texto sem heredoc (X1) |
| M4 | atribuição no comando simples do dono, antes do programa, impede "só lido" | atribuição sozinha, sem programa no mesmo comando simples (X2; ela vale para L9) |
| M5 | `echo` e `true` só passam como builtins sem redefinição no texto | `echo` redefinido em outra chamada (X2) |

## 3. As classes de furo e o corpus (parte a)
Notação: `⏎` é quebra de linha; `{CORPO}` é a linha crítica do modelo de cada hook: `git push origin main` no `conformidade` (modelo `tests/hooks/conformidade/heredoc-outro-comando-make-push-main-bloqueia.json`) e `gh pr merge feature/x --repo rodrigo-isensee/Forge --merge`, com o review reprovado, no `parecer` (modelo `tests/hooks/parecer/forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia.json`). As colunas `conf` e `par` dão o código de saída esperado. "Regra" diz o que fecha o caso. **`fecha`** é a marca do corpus (seção 4): a regra em cujo commit o caso passa a dar o código esperado; "—" quer dizer que o caso já passa em `1b0fb6b` e fica como guarda.

Cuidado de montagem: nas classes S e H, o único programa fora da lista é o que o caso testa. Um `chmod`, um `make` ou um `echo` (antes de M5) a mais faria o caso passar sem provar a regra.

### Classe R: redireções que gravam
Forma única (R1 a R13): `cat <OP> .husky/pre-push <<'EOF' && git push origin feature/x⏎{CORPO}⏎EOF` (o `git` roda o gancho gravado). Onde a forma pede, o alvo vem colado ao operador.

| ID | `<OP>` ou sonda | conf | par | Regra | fecha | Origem |
|---|---|---|---|---|---|---|
| R1 | `>` | 2 | 2 | M1, M3 | — | regressão (rev. 5: 2 / 2) [EXE] |
| R2 | `>>` | 2 | 2 | M1, M3 | — | regressão |
| R3 | `>\|` | 2 | 2 | M1, M3 | — | regressão [EXE] |
| R4 | `1>` e `2>` | 2 | 2 | M1, M3 | — | descritor numerado |
| R5 | `9>` | 2 | 2 | M1, M3 | — | descritor alto |
| R6 | `&>` | 2 | 2 | M1, M3 | — | |
| R7 | `&>>` | 2 | 2 | M1, M3 | — | |
| R8 | `>&` colado (`>&.husky/pre-push`) | 2 | 2 | M1, M3 | M1 | **A1** rev. 5 (0 / 0) [EXE] |
| R9 | `>& ` com espaço | 2 | 2 | M1, M3 | M1 | A1 rev. 5 [EXE] |
| R10 | `1>&` com alvo não numérico | 2 | 2 | M1 (na dúvida, grava) | M1 | [INF]: o bash não grava; recusar é só mais desconfiado (F9) |
| R11 | `<>` e `1<>` | 2 | 2 | M1, M3 | — | regressão [EXE] |
| R12 | `{fd}>` | 2 | 2 | M1, M3 | M1 | [INF] |
| R13 | `> ".husky/pre-push"` e `> '.husky/pre-push'` | 2 | 2 | M1, M3 | — | regressão [EXE] |
| R14 | `cat <<'EOF' > >(sh)⏎{CORPO}⏎EOF` (sem `git`) | 2 | 2 | M1, `sh` em `fora_do_texto` | — [INF] | substituição de processo |
| R15 | `exec 3>x.sh; cat <<'EOF' >&3; ./x.sh⏎{CORPO}⏎EOF` | 2 | 2 | M1 (`3>`), M2 | — | descritor aberto antes |
| R16 | `cat <<'EOF' \| tee .husky/pre-push && git push origin feature/x` e `tee -a` | 2 | 2 | lista atual, M3 | — | regressão [EXE] |
| R17 | `git apply <<'EOF' && git commit -m x` e `-o`/`--output=` | 2 | 2 | lista atual, M3 | — | regressão [EXE] |
| R18 | `cat >&x.sh <<'EOF' && git add x.sh && git commit -m x` | 2 | 2 | M1, M3 | M1 | A1 rev. 5, 3.ª forma [EXE] |
| R19a | `echo "it's"; cat > .husky/pre-push <<'EOF'⏎{CORPO}⏎EOF⏎echo 'x'; git push origin feature/x` | 2 | 2 | leitor, M1 | — | **A2 do desenho**, forma literal do parecer [EXE nas funções]; em `1b0fb6b` passa porque o `echo` está fora da lista; depois de M5 só o leitor o segura |
| R19b | `mkdir -p "it's"; cat > .husky/pre-push <<'EOF'⏎{CORPO}⏎EOF⏎mkdir -p 'x'; git push origin feature/x` | 2 | 2 | leitor, M1, M2 | M2 | A2, sem depender do `echo` (o `mkdir` já está na lista) [INF] |
| R19c | `mkdir -p it\'s; …` (o resto como R19b) | 2 | 2 | leitor (escape fora de aspas) | M2 | vizinha de A2 [INF] |
| R19d | `mkdir -p $'it\'s'; …` (o resto como R19b) | 2 | 2 | leitor (`ansi`), e o item 2 (`$'`) | — [INF] | vizinha de A2; o item 2 já recusa com marcador, o caso guarda o leitor |
| R19e | `mkdir -p x #it's⏎cat > .husky/pre-push <<'EOF'⏎{CORPO}⏎EOF⏎mkdir -p 'y'; git push origin feature/x` | 2 | 2 | leitor (comentário), e o item 2 (`#` com linha seguinte) | — [INF] | vizinha de A2 |
| R20a | `cat <<'EOF' \| 2>&1 tee .husky/pre-push && git push origin feature/x⏎{CORPO}⏎EOF` | 2 | 2 | M2 (enumerador em `grava_arquivo`), M3 | M2 [INF] | vizinha de A1 do desenho: o `tee` engolido some da lista dos que gravam |
| R20b | `cat <<'EOF' \| >&2 git apply && git commit -m x⏎{CORPO}⏎EOF` | 2 | 2 | M2, M3 | M2 [INF] | idem, `git apply` |
| R20c | `cat <<'EOF' \| 2>&1 uniq - .husky/pre-push && git push origin feature/x⏎{CORPO}⏎EOF` | 2 | 2 | M2, M3 | M2 [INF] | idem, `uniq` |

### Classe N: redireções que não gravam (o `git` segue na lista)
Forma: `cat <OP> <<'EOF' && git push origin feature/x⏎{CORPO}⏎EOF`. O corpo vai só para o `cat`, ninguém o roda: o resultado esperado é 0.

| ID | `<OP>` | conf | par | fecha |
|---|---|---|---|---|
| N1 | `>/dev/null`, `2>/dev/null`, `&>/dev/null`, `>>/dev/null` | 0 | 0 | — |
| N2 | `2>&1`, `>&2`, `1>&2`, `>&-`, `3>&1-`, `>& 2` | 0 | 0 | — |
| N3 | `<&0` e `0<&-` | 0 | 0 | — |

N1 com `>/dev/null` dá 0 / 0 na rev. 5 [EXE]; o N mostra que M1 não recusa a mais.

### Classe S: separadores, e o que roda antes e depois do heredoc na mesma chamada
Forma: `cat > x.sh <<'EOF'` com `{CORPO}`, e o `./x.sh` (ou o `git`) ligado como na coluna. Todas as linhas: conf 2, par 2. Regra: M2 (corpo conferido como comando) e M3.

| ID | Ligação | fecha |
|---|---|---|
| S1 | `cat > x.sh <<'EOF' && ./x.sh` (regressão, fixture `heredoc-outro-comando-…`) | — |
| S2 | `; ./x.sh` (regressão) | — |
| S3 | `\|\| ./x.sh` | — |
| S4 | `& ./x.sh` | — [INF] |
| S5 | `…⏎EOF⏎./x.sh` (**A2** rev. 5: 0 / 0) [EXE] | M2 |
| S6 | `cat > x.sh <<'EOF' &&⏎{CORPO}⏎EOF⏎./x.sh` (o `&&` no fim da linha do operador) | M2 |
| S7 | `\| ./x.sh` e `\|& ./x.sh` | — [INF] |
| S8 | `…⏎EOF⏎(./x.sh)` e `…⏎EOF⏎{ ./x.sh; }` | M2 |
| S9 | `…⏎EOF⏎echo $(./x.sh)` e `` …⏎EOF⏎echo `./x.sh` `` | M2 |
| S10 | `…⏎EOF⏎if ./x.sh; then :; fi` e `…⏎EOF⏎while ./x.sh; do break; done` | M2 |
| S11 | `…⏎EOF⏎! ./x.sh` e `…⏎EOF⏎coproc ./x.sh` | M2 |
| S12 | `…⏎EOF⏎diff <(./x.sh) README.md` | M2 |
| S13 | `…⏎EOF⏎bash x.sh`, `sh x.sh`, `source x.sh`, `. x.sh`, `make` | M2 |
| S14 | `trap ./x.sh EXIT⏎cat > x.sh <<'EOF'…` (o programa vem **antes** do heredoc) | M2 |
| S15 | `cat > .husky/pre-push <<'EOF'⏎{CORPO}⏎EOF⏎git push origin feature/x` (**A2** rev. 5, 2.ª forma: 0 / 0) [EXE] | M2 |
| S16 | o mesmo com `git commit -m x` na linha seguinte | M2 |
| S17a a S17f | `…⏎EOF⏎<OP> ./x.sh`, com `<OP>` em `2>&1`, `>&2`, `>&-`, `3>&1-`, `<&0`, `0<&-` (**A1 do desenho**: o enumerador de `1b0fb6b` devolve só `cat` [EXE]) | M2 |
| S18a a S18c | dono sem programa provado: `(2>&1 bash) <<'EOF'⏎{CORPO}⏎EOF`, `(>&- sh) <<'EOF'…`, `(<&0 bash) <<'EOF'…` | M2 [INF] |

S17 vem das classes R e N de forma mecânica: cada operador completo de N2 e N3, seguido de `./x.sh`. S18 é a mesma falha no dono: em `1b0fb6b`, o ramo do comando lógico inteiro (subshell) lê `2>&1 bash` sem programa, e `corpo_so_lido` com laço vazio devolve verdadeiro [INF, leitura de `hooks/_comum.py:1086-1093` e `1144-1153`].

### Classe H: forma do heredoc e o que vem depois dele
Todas: conf 2, par 2.

| ID | Sonda | Regra | fecha |
|---|---|---|---|
| H1 | `cat <<'EOF' > x.sh⏎{CORPO}⏎EOF⏎./x.sh` (redireção depois do operador) | M1, M2 | M2 |
| H2 | `cat > x.sh <<-'EOF'⏎<tab>{CORPO}⏎<tab>EOF⏎./x.sh` | M2 | M2 |
| H3 | dois heredocs: `cat > x.sh <<'A'⏎{CORPO}⏎A⏎cat <<'B'⏎texto⏎B⏎./x.sh` | M2 | M2 |
| H4 | `cat <<'A' <<'B' > x.sh⏎texto⏎A⏎{CORPO}⏎B⏎./x.sh` (só o último vai à entrada) | M2 | M2 |
| H5 | `cat > x.sh <<'EOF'⏎{CORPO}⏎EOF⏎chmod +x x.sh && ./x.sh` (o fixture `…-chmod-e-script-…` tem a forma na mesma linha; esta é na linha seguinte) | M2 | M2 |
| H6 | `x=$(cat <<'EOF'⏎{CORPO}⏎EOF⏎); eval "$x"` | regressão (fixture `…-substituicao-fecha-…-eval-…`) | — |
| H7 | `cat > x.py <<'EOF'⏎import os; os.system('{CORPO}')⏎EOF⏎python3 x.py` | M3: o corpo, lido como shell, pode não mostrar a ação; o marcador mostra | M3 |
| H8 | `cat > .gitconfig <<'EOF'⏎[core]⏎sshCommand = sh -c '{CORPO}'⏎EOF⏎HOME=.⏎git push origin feature/x` | M3 (`git` fora pela gravação, marcador `push`) | M3 |

### Classe V: atribuições e ambiente que mudam o programa
Todas: conf 2, par 2.

| ID | Sonda | Regra | fecha |
|---|---|---|---|
| V1 | `cat > x.sh <<'EOF' && GIT_SSH=./x.sh git push origin feature/x` | regressão (2af1983) [EXE] | — |
| V2 | `export GIT_SSH=./x.sh; cat > x.sh <<'EOF' && git push …` | regressão [EXE] | — |
| V3 | `cat > x.sh <<'EOF' && env GIT_SSH=./x.sh git push origin feature/x` | `MUDAM_O_AMBIENTE` | — |
| V4 | `… && git push --receive-pack='sh x.sh'`, `--rec=`, `git -C . push --exec=` | regressão [EXE] | — |
| V5 | `PATH=/tmp/x:/usr/bin cat <<'EOF'⏎{CORPO}⏎EOF` | **M4** | M4 |
| V6 | `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=.husky git commit -F - <<'EOF'⏎{CORPO}⏎EOF` | **M4** | M4 |
| V7 | `git -c core.hooksPath=.husky commit -F - <<'EOF'⏎{CORPO}⏎EOF` | atual (`-c` tira o subcomando) | — |
| V8 | `alias cat=bash⏎cat <<'EOF'⏎{CORPO}⏎EOF` e `hash -p /bin/bash cat⏎cat <<'EOF'…` | M2 (`alias` e `hash` em `fora_do_texto`) | M2 |
| V9 | `cat() { bash; }⏎cat <<'EOF'⏎{CORPO}⏎EOF` | M2 (`bash` em `fora_do_texto`) | M2 |
| V10 | `export PATH=/tmp/x:/usr/bin; cat <<'EOF'⏎{CORPO}⏎EOF` | regressão: `export` muda o ambiente e não é leitor | — [INF] |

### Classe L: usos legítimos que continuam liberados
| ID | Sonda | conf | par | fecha | Nota |
|---|---|---|---|---|---|
| L1 | `git add src/app.js && git commit -m "$(cat <<'EOF'⏎fix: it's done⏎EOF⏎)" && git push origin feature/x` | 0 | — | — | fixture atual |
| L2 | `git commit -m "$(cat <<'EOF'⏎fix: it's done⏎EOF⏎)" && echo feito` | 0 | — | M5 | rev. 5: 2; `develop`: 0 [EXE] |
| L3 | `gh pr create --draft --base develop --title t --body "$(cat <<'EOF'⏎it's ok⏎EOF⏎)" && echo ok` | 0 | 0 | M5 | rev. 5: 2 [EXE] |
| L4 | `mkdir -p notas && cd notas && cat > n.md <<'EOF'⏎it's⏎EOF` | 0 | — | — | fixture atual |
| L5 | `cat <<'EOF' 2>&1 \| git commit -F - && git push origin feature/x⏎feat: x⏎EOF` | 0 | — | — | N2 |
| L6 | `cat > n.md <<'EOF'⏎texto sem apóstrofo nem marcador⏎EOF⏎git add n.md` | 0 | — | — | M2 confere o corpo, que é inofensivo; M3 não age sem marcador |
| L7 | `cat <<-X⏎<tab>corpo⏎<tab>X⏎ls` | 0 | — | — | fixture atual |
| L8 | duas chamadas (`passos` do `Fixture`): `cat > mudanca.diff <<'EOF'⏎-it's⏎+it is⏎EOF` e depois `patch -p1 < mudanca.diff` | 0 e 0 | — | — | o contorno novo das mensagens (M6) |
| L9 | `BODY="$(cat <<'EOF'⏎it's ok⏎EOF⏎)"; gh pr create --draft --base develop --title t --body "$BODY"` | — | 0 | — | fixture atual do `parecer`; guarda de M4 (a atribuição de fora não é do `cat`) |
| L10 | `echo "a > b" && cat <<'EOF' && git push origin feature/x⏎it's⏎EOF` | 0 | — | M5 | leitor: o `>` entre aspas duplas não é operador (hoje grava) [INF] |
| L11 | `git commit -F - <<'EOF'⏎fix: it's done⏎EOF` | 0 | — | — | guarda de M4 sem atribuição |
| L12 | `x="$(cat <<'EOF'⏎it's⏎EOF⏎)"; echo "$x"` | 0 | — | M5 | guarda de M4 (atribuição de fora) e de M5 |

"—" nas colunas `conf`/`par`: o hook não age na linha (no `parecer`, o `PREFILTRO` não casa) ou a coluna não se aplica; o corpus não roda essa célula.

### Classe X: fora do escopo desta volta (não reprova; vai a cartão)
Critério: as linhas "Não promete" da seção 2.3.

| ID | Sonda | Por quê | Destino |
|---|---|---|---|
| X1 | gravação por argumento e execução na mesma chamada, **sem heredoc**: `printf '%s\n' '{CORPO}' > x.sh && sh x.sh`, `echo '{CORPO}' > .husky/pre-push; git push origin feature/x`, `cat > x.sh <<< '{CORPO}'` numa linha só | não há heredoc; a `develop` libera igual; limite [B] (`docs/hooks.md:92`), com o `pre-push` e a proteção de branch como camada. Com qualquer heredoc no mesmo texto, M3 já recusa | N-HOOK1 (M3 sem a condição "heredoc" tem falso positivo alto: `make test > out.txt && git push`) |
| X2 | estado de outra chamada: `PATH=/tmp/x:/usr/bin` sozinho numa linha antes de `cat <<'EOF'`, `read PATH <<'EOF'`, função ou alias definidos antes, descritor herdado, `remote.<r>.receivepack` na configuração | depende de executável, ambiente ou configuração gravados antes (R2 da segurança). Recusar a atribuição sozinha quebraria L9 | N-HOOK1, regra 2.3 (`CONFIG_PROTEGIDA`) |
| X3 | marcador ofuscado: `git p''ush` no corpo, `os.system('gh pr m' + 'erge …')` | o `CRITICO` lê o texto cru | cartão C8 da ADR 0011 |

## 4. Os testes que viram o corpus (parte c)
**Arquivo de dados:** `tests/fixtures/heredoc-volta-unica.json`, ao lado de `tests/fixtures/brief/`, fora de `tests/hooks/` (o `glob("*/*.json")` de `Hooks.setUp` o tomaria por um hook). Formato:

```json
{
  "modelos": {
    "conformidade": "heredoc-outro-comando-make-push-main-bloqueia",
    "parecer": "forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia"
  },
  "corpos": {
    "conformidade": "git push origin main",
    "parecer": "gh pr merge feature/x --repo rodrigo-isensee/Forge --merge"
  },
  "casos": [
    {"id": "R8", "classe": "R", "comando": "cat >&.husky/pre-push <<'EOF' && git push origin feature/x\n{CORPO}\nEOF",
     "conformidade": 2, "parecer": 2, "fecha": "M1", "origem": "A1 rev. 5"},
    {"id": "S17a", "classe": "S", "comando": "cat > x.sh <<'EOF'\n{CORPO}\nEOF\n2>&1 ./x.sh",
     "conformidade": 2, "parecer": 2, "fecha": "M2", "origem": "A1 do desenho"},
    {"id": "L8", "classe": "L", "passos": ["cat > mudanca.diff <<'EOF'\n-it's\n+it is\nEOF", "patch -p1 < mudanca.diff"],
     "conformidade": 0, "parecer": null}
  ]
}
```

Uma entrada por linha das tabelas R, N, S, H, V, L e F. Quando a célula tem variantes ("`1>` e `2>`"), cada variante vira um caso com sufixo (`R4a`, `R4b`). `null` quer dizer que a célula não roda. A classe X **não** entra nos casos.

**Marca `fecha` (A3).** Valor: `"M1"` a `"M5"`, a regra em cujo commit o caso passa a dar o código esperado (o último passo de que ele depende, na ordem abaixo). Caso sem a marca já passa. O teste trata os dois lados:
- caso **sem** `fecha`: o código tem de ser o esperado;
- caso **com** `fecha`: o código tem de ser **diferente** do esperado (o vermelho continua provado; o teste imprime a saída do hook no `subTest`). Caso marcado que já passa falha o teste ("marca sobrando: o caso já passa; tire a marca neste commit").
Cada commit de M1 a M5 tira as marcas da sua regra, e só elas. Reverter o commit devolve as marcas com o código, e a suíte segue verde. Os casos [INF] cuja marca o passo (1) desmentir (já passam, ou não fecham na regra prevista) têm a marca corrigida no próprio passo (1), com a lista na mensagem do commit.

**Classe de teste:** `CorpusHeredocVoltaUnica` em `tests/test_hooks.py`, que reusa `Fixture`, `executar_em_lote` e `rodar`:
- `test_corpus_nos_dois_hooks`: para cada caso e hook com valor, monta o `Fixture` do modelo daquele hook com o `command` trocado (`{CORPO}` pelo corpo do hook; `passos` vira os `passos` do `Fixture`, com a última entrada como principal) e confere o código, com a regra da marca `fecha`. O `stderr` só é conferido para `2` sem marca, pelo prefixo `R-`. Roda em paralelo, como os fixtures, abaixo de 30 s.
- `test_oraculo_das_redirecoes` (T6, fecha M1 por construção): pula com `self.skipTest("bash ausente ou anterior ao 4 (BASH_VERSINFO=…): {fd}> e &>> não existem")` quando `bash` não está no `PATH` ou `BASH_VERSINFO[0] < 4` (o bash do macOS é 3.2; A6). Para cada operador das classes R e N e para cada prefixo P0 a P4 (P0 nenhum; P1 `echo "it's" >/dev/null; `; P2 `echo it\'s >/dev/null; `; P3 `echo $'it\'s' >/dev/null; `; P4 `: "a > b"; `), roda `bash --noprofile --norc -c "<P>cat <OP>alvo <<'EOF'⏎x⏎EOF"` numa pasta temporária, com o ambiente limpo e o `PATH` só com `/usr/bin:/bin`, e passa o mesmo texto por `tirar_heredocs` e `grava_arquivo`. Afirma: se o bash criou ou mudou um arquivo na pasta, `grava_arquivo` dá verdadeiro; para todo operador da classe N, com todo prefixo, `grava_arquivo` dá falso. Só roda `cat` e `echo`, sem rede e sem custo (`R-CUSTO`). R10 confirma o [INF]: o bash não grava e `grava_arquivo` dá verdadeiro (permitido: só a implicação é exigida). Os pares que só passam depois de M1 levam `fecha: "M1"` na mesma tabela de dados.
- `test_enumerador_nao_engole_programa` (T7, fecha a classe do A1 do desenho por construção): para cada operador completo de N2 e N3 e para cada redireção de R com o alvo colado, o enumerador de `texto = "<redireção> ./x.sh"`, `"X=1 <redireção> ./x.sh"` e `"! <redireção> ./x.sh"` tem `./x.sh` como programa; para cada operador que pede alvo separado (`>`, `2>`, `>&`, `<`), `"<op> alvo ./x.sh"` tem `./x.sh` como programa e `alvo` não. `fecha: "M2"` até o passo (3).
- `test_corpus_cobre_as_classes`: as classes R, N, S, H, V, L e F têm pelo menos o número de casos destas tabelas (`minimo`), e os IDs R8, R9, R18, R19a a R19e, R20a a R20c, S5, S15, S17a a S17f, S18a a S18c, F7a, F7b, F8a e F8b estão presentes. Todo valor de `fecha` está em `{"M1", …, "M5"}`. No passo (7), o teste passa a exigir **nenhuma** marca `fecha`. O corpus não encolhe sem aparecer no diff do teste.

**Ordem no E3.1**, um commit por passo; em **cada** commit, a suíte inteira (`python3 -m unittest discover -s tests -v`) e `scripts/validar-plugin.sh` verdes:
1. o corpus, as marcas e a classe de teste (com T6 e T7). Os casos marcados falham como previsto; a mensagem do commit traz a saída do vermelho e as marcas corrigidas pelo [INF].
2. M1 e o leitor sequencial: tira as marcas `M1`.
3. M2 (enumerador positivo, dono sem programa, escopo do texto, frase própria da mensagem): tira as marcas `M2`. **No mesmo commit**, inverte o fixture `heredoc-apostrofo-gravado-em-arquivo-e-patch-depois-libera` para `…-patch-na-mesma-chamada-bloqueia` (F3), cria o `-libera` em duas chamadas (L8) e inverte qualquer outro `tests/hooks/*/*-libera.json` que M2 vire, com a lista na mensagem.
4. M3 e a mensagem dele: tira as marcas `M3`; inverte os `-libera` que M3 vire, no mesmo commit.
5. M4: tira as marcas `M4`; idem.
6. M5: tira as marcas `M5`.
7. M6 (mensagens de contorno, `docs/hooks.md`, emenda da ADR 0011, fragmento do changelog) e a exigência de "nenhuma marca". Os fixtures cujo `stderr` esperado mude com o texto das mensagens são atualizados aqui.
Dependências para reverter: (3) depende de (2) (usa o leitor); (4) depende de (3) (`fora_do_texto`); (5) e (6) dependem de (3). Reverter um passo com dependentes pede reverter antes os dependentes; cada mensagem de commit declara "depende de".

**Critério de parada da rodada (A4)** (o que E3.2 e E3.3 usam; é o item 3 da ADR 0011 aplicado a este lote, sem regra nova). O parecer reprova só por:
- (i) caso do corpus (inclusive T6 e T7) com código ou afirmação errada. Os dois pareceres rodam `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica -v` inteiro e citam a saída, sem refazê-lo à mão;
- (ii) sonda que sai 0 no hook, com efeito provado no bash (arquivo criado ou comando do corpo executado, numa pasta em `$TMPDIR`), numa forma que a linha **Promete** de uma regra da seção 2.3 cobre. O parecer nomeia a regra e cita o trecho da promessa. A sonda entra no corpus no mesmo commit da correção.
O que nenhuma linha "Promete" cobre, ou o que uma linha "Não promete" descreve, é cartão (N-HOOK1), não reprovação. Recomendação promovida a bloqueante de um parecer para o seguinte leva `critério mudou:` com o motivo.

## 5. Falsos positivos conhecidos (parte d)
Todos recusam com a mensagem que dá o contorno. Entram no corpus como casos de classe `F` com o código 2: o falso positivo fica medido, e a sua correção futura aparece como mudança de teste. Contam para o critério de reversão da ADR 0011, cada um na linha da regra que o gera (A8).

| ID | Sonda | conf | par | fecha | Novo em relação a `1b0fb6b`? | Regra | Contorno |
|---|---|---|---|---|---|---|---|
| F1 | `cat > n.md <<'EOF'⏎it's⏎EOF` `&& git add n.md` | 2 | — | — | não (rev. 5: 2; `develop`: 0) [EXE] | grava + `git` | gravar pelo Write, ou o `cat` numa chamada e o `git add` noutra |
| F2 | `git commit -m "$(cat <<'EOF'⏎it's⏎EOF⏎)" && git log -1` | 2 | — | — | não [EXE] | lista positiva | `git log` noutra chamada; fora de M5 pela superfície (`gpg.program`, pager) |
| F3 | `cat > mudanca.diff <<'EOF'⏎…it's…⏎EOF⏎patch -p1 < mudanca.diff` na mesma chamada | 2 | — | M2 | **sim** (M2) | M2 | duas chamadas (as mensagens de M6 já dizem isso) |
| F4 | `cat > notas.md <<'EOF'⏎…⏎EOF⏎git add notas.md && git commit -m x && git push origin melhoria/x` | 2 | — | M3 | **sim** (M3: grava, `git` fora, marcador `push`) | M3 | gravar pelo Write e deixar a chamada do Bash só com `git` |
| F5 | `python3 -m unittest && git commit -F - <<'EOF'⏎it's⏎EOF` | 2 | — | — | não (o `&&` já punha `python3` no comando lógico) | lista positiva | `git commit -m "$(cat <<'EOF'…)"` numa chamada sem outro programa fora da lista |
| F6a | heredoc com apóstrofo no corpo e outro programa fora da lista **numa linha depois** (`…⏎EOF⏎ls`) | 2 | — | M2 | **sim** (M2) | M2 | o mesmo de F3 |
| F6b | o mesmo com o programa **numa linha antes**: `git diff --stat⏎git commit -F - <<'EOF'⏎it's⏎EOF` | 2 | — | M2 | **sim** (M2) | M2 | o mesmo de F3 |
| F7a | `cat > docs/reviews/x.md <<'EOF'⏎texto⏎EOF⏎git add docs/reviews/x.md` (sem apóstrofo; marcador de caminho do `CRITICO` do `conformidade`: `docs/reviews`, `docs/qa`, `docs/security`, `CLAUDE.md`, `.claude/`, `tests/hooks`…) | 2 | — | M3 | **sim** (M3) | M3 | gravar o parecer pelo Write e dar `git add` noutra chamada |
| F7b | marcador só no corpo: `cat > notas.md <<'EOF'⏎rodar git pull antes⏎EOF⏎git add notas.md` (o `PREFILTRO` do `parecer` casa `git … pull`) | — | 2 | M3 | **sim** (M3) | M3 | o mesmo de F7a |
| F8a | `LC_ALL=C cat <<'EOF'⏎it's⏎EOF` | 2 | — | M4 | **sim** (M4) | M4 | tirar a atribuição (o `cat` não depende dela) ou gravar pelo Write |
| F8b | `GIT_AUTHOR_DATE=2026-10-22T10:00:00 git commit -F - <<'EOF'⏎fix: it's done⏎EOF` | 2 | — | M4 | **sim** (M4) | M4 | a opção do programa (`git commit --date=…`, `--author=…`) ou a mensagem pelo Write e `git commit -F <arquivo>` |
| F9 | `cat 1>&x <<'EOF' && git push origin feature/x⏎it's⏎EOF` (R10: o bash não grava) | 2 | — | M1 | **sim** (M1) | M1 | forma correta do descritor (`>&2`) |
| F10 | dono sem programa: `(2>&1) <<'EOF'⏎it's⏎EOF` | 2 | — | M2 | **sim** (M2) [INF] | M2 | não há uso legítimo; o heredoc sem programa não tem leitor |

F3 e F6 são a forma exata do A2 da rev. 5: o `patch` e o `ls` não estão na lista positiva. Afrouxar M2 para eles (pôr `patch`, `ls`, `git diff` e afins na lista) fica de fora: o `patch` com diff no estilo `ed` já executou comando (CVE-2018-1000156), e cada nome novo é uma entrada a defender. Os fixtures `-libera` que M2, M3 ou M4 invertam são procurados e invertidos no commit da regra (seção 4, passos 3 a 5), não depois.

## 6. Riscos e o que fica em aberto
- **Falsos positivos novos:** F3, F4, F6a, F6b, F7a, F7b, F8a, F8b, F9 e F10, mais os `-libera` que os passos 3 a 5 inverterem (listados nas mensagens dos commits). Medida: as linhas próprias de M2 e M3 nas leituras da ADR 0011 (A8) e a linha atual do "não modelado". Se uma delas passar de 5 em quatro semanas, a saída é ampliar a lista positiva por programa, com caso no corpus, não voltar ao escopo do comando lógico.
- **Menos recusa que `1b0fb6b`:** L2, L3 e L12 (M5, iguais à `develop`) e L10 (o leitor deixa de tomar `>` entre aspas duplas por operador; o bash não grava). Nenhum executa o corpo.
- **Tempo:** M2 troca uma conta por comando lógico por uma conta por texto, e o leitor sequencial é uma passada linear; M3 é uma checagem por texto. Os testes de tempo e de custo do lote (3000 e 5000 heredocs) seguem como teto, em cada commit.
- **Inferências:** R10, R12, R14, R19b a R19e, R20a a R20c, S4, S7, S18, H4, H7, H8, V10, L10, F10 são [INF]. T6 e T7 confirmam o leitor e o enumerador; os demais, a marca `fecha` obriga o passo (1) a mostrar o vermelho previsto ou corrigir a marca.
- **Dependência:** nenhuma de outro lote. O N-HOOK1 recebe este corpus e a classe X.
- **Segurança:** o `security-engineer` recebe A1 e A2 do desenho pelo corpus no E3.3, sem cartão à parte; o critério (ii) vale para o parecer dele.

## 7. Formas vizinhas de cada classe de achado (o que mais a mesma regra cobre ou deixa aberto)
- **A1 do desenho (palavra engolida pelo enumerador).** Mesma regra fecha: toda redireção completa antes do programa (S17, T7), no meio de um pipeline (R20: o `tee`, o `uniq` e o `git apply` engolidos somem da lista dos que gravam), no dono (S18: dono sem programa) e depois de atribuição ou `!` (T7). Também fecha a palavra com operador entre aspas (`'2>&1' ./x.sh`: o operador entre aspas não é redireção, e a palavra vira programa). Deixa aberto: nada na enumeração; programa que não é palavra do texto fica em X2.
- **A2 do desenho (leitura de aspas fora de sequência).** Mesma regra fecha: apóstrofo entre aspas duplas (R19a, R19b, P1 do T6), apóstrofo escapado fora de aspas (R19c, P2), `$'…'` com `\'` (R19d, P3), apóstrofo num comentário provado (R19e), `>` entre aspas duplas (L10, P4), separador entre aspas (não cria programa). Fora do lote, porque só aumentam a desconfiança: `hooks/conformidade.py:760` e `:816` tiram as aspas por `re.sub` e partem em mais palavras; nenhuma esconde programa. Deixa aberto: `case` e crase aninhada (C2), já recusados pelo item 2 com marcador.
- **A3 (suíte vermelha entre commits).** Além do corpus: T6 e T7 (marcas na mesma tabela), os fixtures `-libera` invertidos (no commit da regra), o `stderr` esperado dos fixtures quando a mensagem muda (no passo 7), os testes de tempo (em cada commit) e a exigência de "nenhuma marca" (só no passo 7).
- **A4 (critério indecidível).** Toda pertença se decide pela tabela 2.3: a sonda cai numa linha "Promete" ou não. O que a revisão achar sem linha vira cartão, inclusive formas de X1 a X3 que alguém ache novas.
- **A5 (falsos positivos omitidos).** Cada regra tem a sua linha F: M1 (F9), M2 (F3, F6a, F6b, F10), M3 (F4, F7a, F7b), M4 (F8a, F8b), M5 (nenhum: só libera). O marcador do M3 vale também quando está só no corpo (F7b), porque o `CRITICO` lê a linha com os corpos.
