# 0011 - Analisador de comandos: gramática positiva e falha fechada no que não modela

Estado: aceita. Data: 2026-10-14.
Propósito: parar a sequência de brechas no analisador de comandos dos hooks, trocando "recusar o que já se sabe perigoso" por "aceitar só o que se sabe modelar". Público: quem mantém os hooks e quem revisa a segurança deles. Revisão: 2026-11-14.

## Contexto
O analisador comum (`hooks/_comum.py`: `fichas`, `comandos`, `segmentos`) usa o `shlex`, que não é o bash. O papel só de leitura (`checar_so_leitura` em `hooks/conformidade.py`) é uma lista branca de **comandos** em cima de uma lista negra de **construções**. Cada rodada de review achou uma construção nova que o `shlex` lê diferente do bash. A fatia 2 do anti-alucinação já teve duas reprovações por isso (evidência nos `rc` de `docs/reviews/anti-alucinacao-regras.md` e nas sondas de `docs/security/anti-alucinacao-regras.md`, que criaram arquivos de verdade):

| Rodada | Brechas (rc 0 no hook, efeito real no bash) | Papéis |
|---|---|---|
| Volta 1 (review independente) | `git ls-remote --upload-pack`/`-u`/`--exec` e transporte `<x>::`; `--ext-diff` abreviado; `<(...)`/`>(...)` não reconhecidos (a ação crítica de dentro passava, inclusive merge sem parecer) | só leitura; todos |
| Volta 2 (segurança) | S1 `$'...'`, chaves e `${X:-...}` viram opção; S2 a saída de `$(...)` vira argumento; S3 lançadores (`xargs`, `sudo`, `nohup`) repassam o que o hook não vê; `--textconv`/`--filters`; `gh --web` | só leitura |
| Volta 2 (segurança), anterior à fatia | S4 o `)` da substituição separava comandos e o alvo sumia (`rm $(true) <protegido>`); S5 papel só de leitura sem efeito no clone do Forge | todos; só leitura |
| Depois da volta 2 (autor), anterior à fatia, **alta** | O comentário consome a quebra de linha no `shlex`: `echo a #b⏎git push origin main` sai com 0 (e `a#b`, que no bash nem é comentário, também) | todos |
| Depois da volta 2 (autor), limites aceitos | `case ... a)` dentro de `$(...)` fecha o nível cedo; crase sem pilha; `$((...))` lido como comando | todos |

Padrão: toda brecha é uma construção que o analisador não modela e que, por omissão, ele **aceita**. Enquanto a omissão for "aceita", cada rodada acha a próxima. A ADR 0003 (item 4) e a ADR 0009 (seções 5 e 7) já dizem que o hook é guarda de processo e que a fronteira é o sandbox, o pre-push, o CI e a proteção de branch; o papel só de leitura, porém, enfrenta instrução injetada no texto que o conferente lê, que é ameaça adversária.

## Decisão
Trocar a omissão: **o que o analisador não modela é recusado** onde importa, e o uso legítimo passa a ter forma explícita.

1. **Papel só de leitura: gramática positiva (entra nesta fatia).** A leitura da linha é sequencial, com um estado só para as aspas (nunca "tirar as aspas simples e olhar o resto"). Fora de aspas, a linha só passa se usar apenas o alfabeto modelado: letras, dígitos, espaço e tab literais (o tab é separador no bash, como o espaço; nunca a classe `\s`), `_ . / : = @ , + % - ~ ^`, os operadores `&&`, `||`, `;`, `|` (o `&` só entra como `&&`). O `^` está no alfabeto porque `git show HEAD^` é leitura comum e ele não tem efeito no bash não interativo. Dentro de aspas simples vale qualquer caractere, menos os de controle; dentro de aspas duplas, também fica recusado `$`, crase, `\` e `!` (os únicos que o bash interpreta ali). Aspas sem fechar recusam. Todo o resto é recusado antes de qualquer outra checagem: `$` (qualquer forma, inclusive `$?` e `$(`), crase, `\`, `#`, `{` e `}`, `<`, `>`, `(`, `)`, `*`, `?`, `[`, `!`, quebra de linha e demais caracteres de controle (`\r`, `\v`). A lista branca de comandos e as checagens de opção do git seguem, com estes acréscimos, vindos das voltas 3 e 4:
   - **Análise aninhada recusada:** depois da gramática, só se chega a nível maior que 0 com `$(` ou crase dentro de aspas simples, e o bash só executa esse texto por reavaliação. O papel recusa qualquer análise com nível maior que 0 (defesa em profundidade; custo: `grep '$(x)'` recusa).
   - **`test` só na forma `test -e|-f|-d|-s <um caminho>`,** com exatamente dois argumentos. O `-v` reavalia como código o subscrito de `nome[...]`, inclusive em expressão composta; a forma restrita fecha a classe por enumeração (sondados `-R -o -n -z -a -r -L -nt -eq -lt`: nenhum executa).
   - **`[` e `[[` fora da lista** (a gramática já os recusa pelo `[`; o `[[` também faz aritmética).
   - **`--show-signature` e o formato `%G`** (`%G?`, `%GS`, `%GK`..., também `%+G`, `%-G` e `% G`) **recusados** em qualquer subcomando git da lista, inclusive com a opção abreviada: rodam o `gpg.program`. O valor de opção do `forge-check` que começa com `-` também recusa.
   As regras pontuais de S1 e S2 (`EXPANSAO`, `CHAVES`, `ACEITAM_SUBSTITUICAO`) saem: ficam cobertas pela gramática no nível 0 e pela recusa de nível maior que 0.
2. **Demais papéis: falha fechada só com marcador crítico (entra nesta fatia).** Se a linha tiver o marcador crítico da ADR 0009, seção 7 (`merge`, `push`, `pr create`, `--no-verify`, `hooksPath`, `--force` ou prefixo de caminho protegido) **e** uma construção não modelada, o hook recusa. A regra mais específica (`R-MAIN`, `R-VERIFY`...) fala primeiro; esta vem depois das checagens da linha. A lista fechada de construções não modeladas:
   - `#` em qualquer posição da palavra (`a#b` incluído) quando houver outra linha depois; o comentário no fim da linha, sem linha seguinte, passa;
   - crase e `case`;
   - **chaves (`{` e `}`) recusadas sem condição** (não só com `,` ou `..`), porque o grupo `{ ...; }` também é construção não modelada;
   - **`$` fora de aspas simples que não abra `$(`** (cobre `$'`, `${`, `$"`, `$@`, `$*`, `$1`, `$$`, `$-` e `$nome`);
   - **`\` seguido de quebra de linha**;
   - **heredoc só como `<<'FIM'` exato** (delimitador entre aspas simples, ou duplas, sem `-`, terminado numa linha igual ao delimitador); o corpo dele não é lido. **Qualquer outro `<<` numa linha de várias linhas recusa** (sem aspas, `<<-`, `<<<`, escapado, entre aspas, sem fim, fim com espaço em volta). Isso mantém os usos legítimos (mensagem de commit por `<<'EOF'`, parecer do QA por heredoc) e fecha as formas em que o `tirar_heredocs` tomava por corpo uma linha que o bash executa.
   - **heredoc que grava arquivo, com programa fora da lista positiva no texto** (`hooks/_comum.py`, `DonosDosHeredocs`): o texto tem heredoc provado, grava arquivo (redireção fora da lista fechada das que não gravam, `tee`, `uniq`, `-o`, `git apply`, `git am`) e roda um programa que não está na lista dos outros comandos; o corpo é conferido como comando antes, para a regra específica falar primeiro.
   A linha que o `shlex` não consegue ler (aspas "desbalanceadas" que o bash lê bem) também recusa. Sem marcador crítico, nada muda. O comentário que engole a quebra de linha fica fechado por esta regra, sem mexer no `shlex`.
   Emendado pela [0013](0013-leitura-do-comentario-nos-hooks.md): onde o `#` abre comentário e o que cada hook faz com a linha que não lê.
   Emendado pelo lote LEITURA-HOOK (volta única, `docs/propostas/lote-leitura-hook-volta-unica.md`): a entrada do heredoc que grava arquivo com programa fora da lista. Endurece; sem rótulo `afrouxa-regra`.
   Emendado pelo lote LEITURA-HOOK (opção D, RET-LEITURA-HOOK-D; `docs/propostas/lote-leitura-hook-caminho-leitor.md`): a chamada com heredoc provado **e** marcador crítico só passa numa gramática positiva (`fora_da_gramatica_com_heredoc`, `hooks/_comum.py`): sem os corpos, K1 `cat > arq <<'FIM'` (ou `>>`) sozinha na chamada, K2 `git commit … -F - <<'FIM'` e K3 `"$(cat <<'FIM'⏎…⏎FIM⏎)"` como valor de `-m`, `--body`, `--title` e afins; o resto cabe no alfabeto do item 1, com os separadores `&&`, `;` e quebra de linha, e cada comando simples começa por `git` (sem `-c`, `--config-env` nem `--exec-path`), `gh`, `cd`, `mkdir`, `echo` ou `true`, sem atribuição antes. O que não cabe recusa com o contorno, nos dois hooks, depois das regras específicas; sem marcador, nada muda. Substitui a leitura de aspas e expansões como oráculo da classe "leitor" por um alfabeto verificável (teste T8 de mutação). Endurece; sem rótulo `afrouxa-regra`. Falsos positivos novos, só com heredoc e marcador (FD1 a FD7 e N1 a N3), em `docs/hooks.md`.
   Emendado pelo lote LEITURA-HOOK (opção A, RET-LEITURA-HOOK-A; `docs/propostas/lote-leitura-hook-caminho-rev7.md`, seção 2A): a gramática positiva decide pelo texto que o bash roda, e não por uma leitura do hook. (a) Cada palavra é comparada sem as aspas, como o programa a recebe (`git '-c'` é `git -c`); (b) o gatilho é textual: com o marcador crítico e `<<` no texto da chamada (depois de tirar cada `\` + quebra de linha), a gramática vale sobre o texto inteiro do nível 0, haja heredoc provado ou não, então `bash -c '…'`, `sh -c` e `eval '…'` recusam ali; (c) a linha de corpo que começa pelo delimitador sem ser igual a ele recusa, e dentro de `$(` o `heredocs` a dá como dúvida (o bash 5.3 fecha em `EOF)`). O critério (3) da opção D passa de "por construção" a medido no bash: o teste T9 roda cada texto que a gramática aceita, com registradores de argv no `PATH`, e exige que o bash rode exatamente os comandos que ela listou. Endurece; sem rótulo `afrouxa-regra`. Falsos positivos novos, só com `<<` e marcador (FD9 a FD11), em `docs/hooks.md`, com o contorno. O que um programa da lista faz com as próprias opções (`git push --receive-pack`, `git rebase -x`, `-C`, `--git-dir`, opções e aliases do `gh`) não é promessa desta regra e vai ao cartão N-HOOK1.
3. **Critério de parada das rodadas.** A próxima rodada de review de segurança desta fatia reprova só por: (i) fixture dos critérios abaixo com rc errado; (ii) brecha numa construção que a gramática do item 1 aceita ou que a lista do item 2 não cobre **e** que atinge ação crítica sem outra camada (sandbox, pre-push, proteção de branch). Brecha que depende de estado gravado antes (configuração do git, ou arquivo versionado que o git lê, como S7 e S8) ou fora do escopo dos itens 1 e 2 vira cartão, não reprovação.
4. **Viram cartão:** os da seção "Cartões", abaixo.

### Cartões
Dono de todos: `forge:tech-lead`; o Jarvis abre os pedidos. Nenhum bloqueou o aceite.

| Cartão | O quê |
|---|---|
| C1 | S5 (papel só de leitura sem efeito no clone do Forge), na fatia 3 |
| C2 | pilha da crase e `case` dentro de `$(...)` no analisador geral (cobertos pelo item 2 só nas linhas com marcador) |
| C3 | glob em caminho protegido e em nome de branch nos papéis comuns (sondado, rc 0; severidade baixa, com revisão e CI como camada) |
| C4 | glob que expande arquivo começado por `-` (hipótese, não sondada) |
| C5 | simplificação do `fichas` para não depender de `shlex._pushback_chars` |
| C6 | acompanhar o falso bloqueio por `$TMPDIR`/`$HOME` com marcador e, se pesar na leitura de reversão, permitir variáveis do ambiente sem atribuição na linha |
| C7 | `. /dev/stdin <<'E'` (o `source`/`.` não está entre as consumidoras do corpo do heredoc); o pre-push segura a `main` |
| C8 | marcador ofuscado (`git p''ush ...`) escapa do `CRITICO`, que lê o texto cru; correção: rodar o `CRITICO` também sobre as palavras sem aspas |
| S7 | repositório nu versionado executa configuração com `-C` ou `cd`; correção: `safe.bareRepository=explicit` na configuração global do git (decisão do usuário, levada pelo Jarvis) e, no hook, recusar `-C`/`cd` para pasta que seja repositório nu |
| S8 | `git status` regrava o índice e roda o gancho `post-index-change` versionado (o `core.hooksPath` já vem de fábrica); correção: aceitar `git status` só com `--no-optional-locks` ou tirá-lo da lista. Severidade baixa: a pré-condição já dá execução pelo `pre-commit`/`pre-push` |

Informativos, sem cartão: `gh --jq env` mostra o ambiente que a gramática não deixa ler por `$NOME` (leitura, sem escrita nem execução), e `test -e -v` passa e só testa o arquivo chamado `-v`, sem reavaliar nada.

### Critérios verificáveis para a próxima rodada (fixtures em `tests/hooks/conformidade/`)
- **Só leitura, rc 2:** todas as sondas com rc 0 das tabelas de S1, S2 e S3; `echo a #b⏎git log -1`; `` git log `echo -1` ``; `git log $X`; `cat <<E`; `ls *`; `git log -1 \--output=x`; `git log -1⏎git status`; `echo $?`; `echo $(git log -1)`.
- **Só leitura, rc 0:** `git log -1`; `git ls-remote origin develop`; `grep -n 'v1$' src/app.js`; `git log -1 'HEAD@{1}'`; `git status && git log -1`; `cat src/app.js | head -5`; `forge-check pr p1`; `grep -n "<(" src/app.js`; `grep -n "a#b" src/app.js`.
- **Papel `dev`, rc 2:** `echo a #b⏎git push origin main`; `echo a#b⏎git push origin main`; `git push origin $B`; `` git push origin `echo main` ``; `git push origin {main,x}`; `git push origin $'main'`; `bash <<E⏎git push origin main⏎E`.
- **Papel `dev` e `tech-lead`, rc 0:** `git push origin melhoria/x`; `git log -1 # nota` (comentário no fim, sem linha seguinte); `diff <(git log -1) <(git log -2)`; `echo $(git rev-parse HEAD)`; `for f in $(ls src); do echo $f; done`; `x=$(git rev-parse HEAD) && echo $x`.
- Suíte inteira e `scripts/validar-plugin.sh` verdes; o hook segue abaixo de 100 ms no caso comum (ADR 0003): a gramática é uma expressão regular sobre a linha.

### Efeito nos falsos bloqueios
- **Só leitura:** perde `echo $?`, `echo $(...)`, `2>/dev/null`, `HEAD@{1}` sem aspas, globs, `grep "a\|b"`, comandos em várias linhas, `test` fora da forma `-e|-f|-d|-s`, `grep '$(x)'` e `%G` em `--grep=`. Forma explícita: um comando por chamada, `'HEAD@{1}'` em aspas simples, `grep -n 'v1$' src/app.js` com o texto em aspas simples no lugar de glob, `&& echo contém || echo não contém` no lugar de `echo $?`. O conferente lê; nenhuma dessas formas é necessária ao trabalho dele.
- **Demais papéis:** só linhas com marcador crítico e construção da lista. Os casos esperados: `git push origin $BRANCH`, laço com `push`, `cp $TMPDIR/x docs/reviews/y.md` (C6), `{ ...; }` com `push`, heredoc sem aspas no delimitador e scripts de várias linhas com comentário e `push`. Forma explícita: nome literal da branch (que o fluxo de branches já pede) e um comando por linha, sem comentário entre eles.

## Alternativas
| Opção | Custo | Risco |
|---|---|---|
| (a) Seguir tapando caso a caso | P por rodada, sem fim previsível; cada rodada custa review, segurança e QA de novo | Alto: a classe de brechas é aberta (o bash tem mais construções que o `shlex` modela); três rodadas, ao menos dez brechas, duas anteriores à fatia e de severidade alta |
| (b) Falha fechada por padrão (escolhida, nos itens 1 e 2) | P: uma expressão regular e uma lista fechada, mais fixtures | Médio-baixo: falso bloqueio no papel só de leitura e nas linhas críticas com variável ou comentário; contorno tem forma explícita e a mensagem diz qual |
| (c1) Parser de bash de terceiros (pacote do PyPI, gratuito) | M: dependência nova em todo projeto, quebra o "só biblioteca padrão" da ADR 0003 | Médio: o parser também diverge do bash em casos de borda e passa a ser superfície de ataque e de manutenção |
| (c2) Delegar ao próprio bash (`bash -n`, ou rodar a expansão) | P | Alto: `-n` não expande nada; expandir executa o que vem da entrada, o que a ADR 0003 proíbe |
| (c3) Tirar o `Bash` do conferente e dar a ele um comando único de leitura em forma exec (`forge-check` com subcomandos fixos) | M: novo subcomando e reescrita do modo de trabalho do conferente | Baixo para o papel; não resolve a brecha do comentário nos demais papéis. Fica como evolução se o item 1 gerar falso bloqueio demais |
| (c4) Sandbox por papel | - | Indisponível: o sandbox do Claude Code vale para a sessão, não por subagente |

## Consequências
- Mais fácil: a próxima rodada tem lista fechada do que conferir; brecha nova fora da gramática vira defeito localizado na expressão regular, não um modelo novo do bash.
- Mais difícil: o conferente perde atalhos de shell; quem empurra branch com variável escreve o nome.
- A manter: a gramática do item 1 e a lista do item 2 ficam como constantes em `hooks/_comum.py` ou `hooks/conformidade.json`, cada entrada com fixture. Afrouxar qualquer uma delas exige rótulo `afrouxa-regra` (o arquivo está em `PROTEGIDOS`).
- O hook continua guarda de processo; a fronteira segue no sandbox, no pre-push, no CI e na proteção de branch (ADR 0003, ADR 0009).

## Por que o existente não basta
O existente é o próprio analisador com recusas pontuais. As tabelas de rc das voltas 1 e 2 mostram, a cada rodada, construções novas com rc 0 e efeito real (arquivos `PWNED1`, `PWNED2`, `PWNED4`, `PWNED12`, `OUT1`, `OUT2` criados pelo bash), e depois da volta 2 o autor registrou o comentário que engole a quebra de linha com rc 0 para `git push origin main` como `dev`. O critério de falha fechada da ADR 0009, seção 7, já existe, mas só vale em erro interno do script; esta ADR estende o mesmo marcador ao caso "linha que o analisador não modela". Não cria hook, regra nem campo novo.

## Critério de reversão
Nas quatro semanas seguintes ao merge na `main`, mais de 5 recusas pelo motivo "construção não modelada" (itens 1 e 2) em uso legítimo, contadas nas transcrições pelo verificador (ADR 0007) ou relatadas em PR de retroalimentação. Atingido, avalia-se (c3) para o papel só de leitura e o encurtamento da lista do item 2.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-11-14 | recusas legítimas por "não modelado" desde o merge | pendente |
| 2026-11-14 | recusas legítimas com a frase de M2 do lote LEITURA-HOOK ("o texto roda `<programa>`, fora da lista dos que não rodam o arquivo gravado") desde o merge | pendente |
| 2026-11-14 | recusas legítimas com a frase de M3 do lote LEITURA-HOOK ("heredoc gravado e programa não modelado na mesma chamada") desde o merge | pendente |

## Divergência (security-engineer, 2026-10-14)
Registro histórico. **Resolução:** todos os pontos abaixo foram aceitos e estão incorporados aos itens 1 e 2 da "Decisão" (volta 3, commits 2131fb6 e e98d977, aprovada no re-review de segurança). Dois ajustes vieram depois: o heredoc ficou mais estreito que a lista original (só `<<'FIM'` exato, desvio de autor aceito pela segurança) e a volta 4 fechou o S6 (`test -v` reavalia texto entre aspas simples) com a restrição do `test`, a saída do `[` e a recusa de nível maior que 0, aprovada no re-review da volta 4. O texto abaixo é o original, sem edição.

Concordo com a direção (b) e com o critério de parada. Divirjo só do conteúdo da lista do item 2 e de dois detalhes do item 1. Sondei o hook do HEAD f007b49 como `dev`: `git push origin $"main"`, `git push origin ma\⏎in` e `git push origin $@main` (também `$1main`) saem com rc 0, e o bash entrega `main` ao git nos três. Nenhum deles cabe em `$'`, `${` ou "`$` seguido de nome". Posição:
- **Item 2:** trocar `$'`, `${` e "`$` seguido de nome" por "**todo `$` fora de aspas simples que não abra `$(`**" (cobre `$"`, `$@`, `$*`, `$1`, `$$` e `$-`). Acrescentar "**`\` seguido de quebra de linha**". O `#` vale em qualquer posição da palavra (`a#b`), não só depois de espaço.
- **Item 1:** pôr `^` no alfabeto, porque `git show HEAD^` é leitura comum do conferente e o `^` não tem efeito no bash não interativo. O espaço é o caractere literal (e o tab), nunca a classe `\s` do Python, e os caracteres de controle (`\r` incluído) são recusados. O `&` só entra como `&&`.
- **Os dois itens:** a leitura de aspas é sequencial (um estado só para simples e duplas), nunca "remover as aspas simples e depois olhar o resto". Fixture: `grep -n "'" src/app.js $(touch Z) "'"` como conferente, rc 2 pela gramática.
- O fixture `conferente-leitura-libera` usa `2>/dev/null` e `echo $?` e passa a sair com 2. É endurecimento, não afrouxamento: reescrever o fixture sem abrir exceção para `/dev/null`.
