# 0011 - Analisador de comandos: gramática positiva e falha fechada no que não modela

Estado: proposta. Data: 2026-10-14.
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

1. **Papel só de leitura: gramática positiva (entra nesta fatia).** A linha só passa se, fora de aspas simples, usar apenas o alfabeto modelado: letras, dígitos, espaço, `_ . / : = @ , + % - ~`, os operadores `&&`, `||`, `;`, `|`. Dentro de aspas duplas vale qualquer caractere, exceto `$`, crase, `\`, `!` e quebra de linha (os únicos que o bash interpreta ali). Todo o resto é recusado antes de qualquer outra checagem: `$` (qualquer forma, inclusive `$?` e `$(`), crase, `\`, `#`, `{` e `}`, `<`, `>`, `(`, `)`, `*`, `?`, `[`, `!` e quebra de linha. A lista branca de comandos e as checagens de opção do git seguem como estão. As regras pontuais de S1 e S2 ficam cobertas pela gramática e podem ser simplificadas.
2. **Demais papéis: falha fechada só com marcador crítico (entra nesta fatia).** Se a linha tiver o marcador crítico da ADR 0009, seção 7 (`merge`, `push`, `pr create`, `--no-verify`, `hooksPath`, `--force` ou prefixo de caminho protegido) **e** uma construção não modelada, o hook recusa. A lista fechada de construções não modeladas: `#` fora de aspas seguido de mais texto na linha seguinte; crase; `case`; heredoc (`<<`); `$'`; `${`; `$` seguido de nome (variável); chaves com `,` ou `..`. Sem marcador crítico, nada muda. O comentário que engole a quebra de linha fica fechado por esta regra, sem mexer no `shlex`.
3. **Critério de parada das rodadas.** A próxima rodada de review de segurança desta fatia reprova só por: (i) fixture dos critérios abaixo com rc errado; (ii) brecha numa construção que a gramática do item 1 aceita ou que a lista do item 2 não cobre **e** que atinge ação crítica sem outra camada (sandbox, pre-push, proteção de branch). Brecha que depende de estado gravado antes (configuração do git) ou fora do escopo dos itens 1 e 2 vira cartão, não reprovação.
4. **Viram cartão:** S5 (fatia 3, já previsto); a pilha da crase e o `case` dentro de `$(...)` no analisador geral (hoje cobertos pelo item 2 só nas linhas com marcador); sonda de globs (`*`) que expandem nome de arquivo começado por `-` em papéis comuns (hipótese, não sondada); simplificação do `fichas` para não depender de `shlex._pushback_chars`.

### Critérios verificáveis para a próxima rodada (fixtures em `tests/hooks/conformidade/`)
- **Só leitura, rc 2:** todas as sondas com rc 0 das tabelas de S1, S2 e S3; `echo a #b⏎git log -1`; `` git log `echo -1` ``; `git log $X`; `cat <<E`; `ls *`; `git log -1 \--output=x`; `git log -1⏎git status`; `echo $?`; `echo $(git log -1)`.
- **Só leitura, rc 0:** `git log -1`; `git ls-remote origin develop`; `grep -n 'v1$' src/app.js`; `git log -1 'HEAD@{1}'`; `git status && git log -1`; `cat src/app.js | head -5`; `forge-check pr p1`; `grep -n "<(" src/app.js`; `grep -n "a#b" src/app.js`.
- **Papel `dev`, rc 2:** `echo a #b⏎git push origin main`; `echo a#b⏎git push origin main`; `git push origin $B`; `` git push origin `echo main` ``; `git push origin {main,x}`; `git push origin $'main'`; `bash <<E⏎git push origin main⏎E`.
- **Papel `dev` e `tech-lead`, rc 0:** `git push origin melhoria/x`; `git log -1 # nota` (comentário no fim, sem linha seguinte); `diff <(git log -1) <(git log -2)`; `echo $(git rev-parse HEAD)`; `for f in $(ls src); do echo $f; done`; `x=$(git rev-parse HEAD) && echo $x`.
- Suíte inteira e `scripts/validar-plugin.sh` verdes; o hook segue abaixo de 100 ms no caso comum (ADR 0003): a gramática é uma expressão regular sobre a linha.

### Efeito nos falsos bloqueios
- **Só leitura:** perde `echo $?`, `echo $(...)`, `HEAD@{1}` sem aspas, globs e comandos em várias linhas. Forma explícita: um comando por chamada, `'HEAD@{1}'` em aspas simples, `git ls-files 'docs/*.md'` no lugar do glob. O conferente lê; nenhuma dessas formas é necessária ao trabalho dele.
- **Demais papéis:** só linhas com marcador crítico e construção da lista. Os casos esperados: `git push origin $BRANCH` e scripts de várias linhas com comentário e `push`. Forma explícita: nome literal da branch (que o fluxo de branches já pede) e um comando por linha, sem comentário entre eles.

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

## Divergência (security-engineer, 2026-10-14)
Concordo com a direção (b) e com o critério de parada. Divirjo só do conteúdo da lista do item 2 e de dois detalhes do item 1. Sondei o hook do HEAD f007b49 como `dev`: `git push origin $"main"`, `git push origin ma\⏎in` e `git push origin $@main` (também `$1main`) saem com rc 0, e o bash entrega `main` ao git nos três. Nenhum deles cabe em `$'`, `${` ou "`$` seguido de nome". Posição:
- **Item 2:** trocar `$'`, `${` e "`$` seguido de nome" por "**todo `$` fora de aspas simples que não abra `$(`**" (cobre `$"`, `$@`, `$*`, `$1`, `$$` e `$-`). Acrescentar "**`\` seguido de quebra de linha**". O `#` vale em qualquer posição da palavra (`a#b`), não só depois de espaço.
- **Item 1:** pôr `^` no alfabeto, porque `git show HEAD^` é leitura comum do conferente e o `^` não tem efeito no bash não interativo. O espaço é o caractere literal (e o tab), nunca a classe `\s` do Python, e os caracteres de controle (`\r` incluído) são recusados. O `&` só entra como `&&`.
- **Os dois itens:** a leitura de aspas é sequencial (um estado só para simples e duplas), nunca "remover as aspas simples e depois olhar o resto". Fixture: `grep -n "'" src/app.js $(touch Z) "'"` como conferente, rc 2 pela gramática.
- O fixture `conferente-leitura-libera` usa `2>/dev/null` e `echo $?` e passa a sair com 2. É endurecimento, não afrouxamento: reescrever o fixture sem abrir exceção para `/dev/null`.
