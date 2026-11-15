---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: c22624c5b274546685d4db04ab44236bfafe6f31
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta de A16)

Revalidação por delta (`forge-check parecer delta`), intervalo `c3cde09f..c22624c5`. No domínio: `hooks/conformidade.py` (função nova `nasce_fora_do_ambiente`, usada para o nome inteiro e para cada prefixo em `valores_da_variavel`) e cinco fixtures `opaco-u4-*` novas (S48 a S51 bloqueiam, `"$HOME"t` libera). Fora do domínio: os mutantes 23 e 24 e `tests/test_hook_destino_opaco.py`. Etapa E1.344; não fiz a entrega. Parecer anterior: `c3cde09f`, reprovado (A16 bloqueante, A11 e A5 recomendados).

Vale a ordem do dono de 15/11 sobre o lote B: os achados já feitos têm de estar fechados; fuga rara nova não bloqueia e vira cartão (recomendado, com a sonda e a correção mínima); bloqueia só achado antigo aberto ou regressão da volta. A16 está fechada e a volta não abre regressão. As fugas novas (A17 a A19) já existem na `develop` `f4b0c2ae`, por isso são recomendadas.

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (uma linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A17 (recomendado) hooks/conformidade.py:2059 · Redireção com descritor no fim (`2>/dev/null`, `2>&1`, `1>x`, `9</dev/null`) faz `cp`, `install` e `rsync` tomarem o `2` por destino: `cp ev/config .git/config 2>/dev/null` libera e grava .git/config. Já na develop f4b0c2ae; cartão de prioridade alta (R-CONFORMIDADE)
- A18 (recomendado) hooks/conformidade.py:485 · Os parâmetros especiais `$@` e `$*` ficam fora de `VARIAVEL_DO_VALOR`: `set -- .git; cp -rT ev "$@"` libera e o bash copia ev sobre o .git. Já na develop f4b0c2ae: cartão
- A19 (recomendado) hooks/conformidade.py:701 · Referência por nome (`declare -n d=_`, também `local -n` e `typeset -n`): o hook calcula `d` como o literal `_`, o bash o lê como `$_`; `declare -n d=_; : .git; cp -rT ev "$d"` libera. Já na develop f4b0c2ae: cartão
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1494 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S48 · : .gi; cp -rT ev "$_"t (ev/config com [core] hooksPath) · espera: 2 · obtido: 2
- S49 · true .gi && cp -rT ev "$_"t · espera: 2 · obtido: 2
- S50 · : .g; cp -r ev/. "$_"it · espera: 2 · obtido: 2
- S51 · : .gi; cp x "$_"t · espera: 2 · obtido: 2
- S52 · cp ev/config .git/config 2>/dev/null · espera: 2 · obtido: 0
- S53 · cp ev/config .git/hooks/pre-push 2>/dev/null · espera: 2 · obtido: 0
- S54 · d=.git; cp -rT ev "$d" 2>&1 · espera: 2 · obtido: 0
- S55 · set -- .git; cp -rT ev "$@" · espera: 2 · obtido: 0
- S56 · declare -n d=_; : .git; cp -rT ev "$d" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: script no meu rascunho que monta o fixture de `tests/test_conformidade_opaco.py` (`dados_do_caso`, ambiente projeto, papel `forge:tech-lead`) com `ev/config` a mais, roda `hooks/conformidade.py` pelo `rodar` de `tests/test_hooks.py`, depois roda a mesma linha no `bash -c` na pasta do caso e compara o `.git` (sem `objects/`) antes e depois. "espera: 2" quer dizer que o bash mudou o `.git`. Rodei o mesmo conjunto no head `c22624c5`, na base `c3cde09f` e na `develop` `f4b0c2ae` (o hook de cada uma, com o harness do head).

**A16 · fechada.** S48 a S51 dão 2 no head (0 na base). Também dão 2: `"${_}"t`, `$_"t"`, `"$_""t"`, `"$_"$'t'`, `"$_"t/`, `"${_:-x}"t`, `"${_%x}"t`, `"${_#x}"t`, `"${_/x/y}"t`, `"${_}t"`, `: .g; … "$_"i"t"`, `cp -rT ev -- "$_"t`, `GIT_X=1 cp -rT ev "$_"t`, `set -- .gi; … "$1"t`, `printf -v d .gi`, `read d <<< .gi`, `for d in .gi`, `export d=.gi` e `x=_; : .git; … "${!x}"`. A15 segue fechada (`: ${d:=.gi}; … "$d"t` e `d=.gi; … "$d"t` dão 2). O legítimo segue em 0: `cp -rT ev "$HOME"t`, `echo a > "$(mktemp)"`, `: ${d:-docs}; echo a > "$d"`. Falsos positivos aceitos, como o parecer anterior previa: `: docs; echo a > "$_"t` e `: .gi; d=t; cp -rT ev "$_$d"`.

**Sem regressão.** A condição nova do laço de prefixos (`nasce_fora_do_ambiente(nome[:k])` ou `nome[:k]=`) contém a antiga. A regex de antes, com `(?![\w])`, é a união da de agora, com `(?![\w=])`, e da busca por `nome[:k]=`, cuja lookbehind (`(?<![\w$])`) é mais larga. A condição nova soma `VARIAVEIS_DO_BASH` e o prefixo `GIT_`, como a correção mínima pedia. Para o nome inteiro, a função extraída tem a mesma lógica. O delta só acrescenta recusa. O mutante 23 (atualizado: tira a chamada do prefixo) e o 24 (O157 e O158) cobrem as condições.

**A17 · redireção com descritor depois do destino (dimensão nova da matriz, fora da A9: "redireção com número do descritor na posição do destino").**
- Evidência: `hooks/conformidade.py:2059`. Para `SO_DESTINO` (`cp`, `ln`, `install`, `rsync`), o destino é o último argumento que não começa com `-`. Com `2>/dev/null` no fim, o `2` sobra em `args` e vira o destino. `>/dev/null` sem número não tem esse problema. O `mv` (que confere todos os argumentos) e o `ln` (cuja regra do link lê todos os argumentos) também não.
- Sondas no head e na `develop`: S52, S53 e S54 dão 0. Também dão 0 `cp ev/config .git/config 2>e.txt`, `… 2>&1`, `… 3>/dev/null`, `… 9</dev/null`, `cp -rT ev .git 2>/dev/null`, `install ev/config .git/hooks/pre-push 2>/dev/null` e `rsync ev/config .git/config 2>/dev/null`. As mesmas linhas sem a redireção dão 2.
- Caminho de ataque: um agente de qualquer papel, por injeção de prompt ou por hábito (`2>/dev/null` é o sufixo mais comum de um comando), grava `.git/config` ou `.git/hooks/pre-push`. `core.hooksPath` derruba a `R-VERIFY`, e `core.fsmonitor` ou o gancho rodam código. O sandbox do Bash protege `.git/config` só onde está ativo (ADR 0009) e não cobre `.git/hooks/`. O hook é a guarda de toda sessão.
- Severidade: alta, e fácil de alcançar. Não bloqueia este lote pela ordem do dono, porque já está na `develop` e cai fora da A9. **Recomendo cartão de prioridade alta, logo depois do merge.**
- Correção mínima: antes de escolher o destino em `SO_DESTINO`, tirar de `args` as redireções, de preferência pelo leitor que já as separa (`palavras_do_texto` e `redirecao_grava` em `hooks/_comum.py`). Se isso não der, tirar o número de descritor (`[0-9]+`) seguido de uma palavra que começa por `>`, `<`, `>&` ou `<&`, e as palavras `[0-9]+[<>]&?\S*`. Fixtures: S52 a S54 e as variantes acima bloqueiam, e `cp a b 2>/dev/null` (fora do `.git`) libera. Mutante: devolver o `2` ao `args`. Esforço: P. Dono: tech-lead.

**A18 · `$@` e `$*` (dimensão "parâmetro especial", ao lado da A4 da E1.280).**
- Evidência: `hooks/conformidade.py:485`. `VARIAVEL_DO_VALOR` só reconhece nome (`[A-Za-z_]\w*`). `"$1"t` dá 2, mas `"$@"`, que `set --` grava na mesma linha, libera. S55 dá 0, também na `develop`.
- Caminho de ataque: o mesmo da A16, com `set -- .git` no lugar de `: .git`. Severidade: média (forma rara).
- Correção mínima: o destino com `$@`, `$*`, `${@}`, `${*}`, `$#`, `$$`, `$!`, `$-`, `$?` ou `$0`…`$9` não vale como do ambiente (opaco que o hook não calcula: recusa). Fixture: S55 bloqueia. Esforço: P. Dono: tech-lead.

**A19 · referência por nome (dimensão nova: "atributo da variável").**
- Evidência: `hooks/conformidade.py:701`. `declare -n d=_` conta como a atribuição `d=_`, e o hook calcula o literal `_`. O bash resolve `$d` como `$_` (`.git`). S56 dá 0 no head e na `develop`.
- Correção mínima: com `-n` em `declare`, `typeset` ou `local` na linha (também em grupo, como `-gn`), devolver `None` para o nome. Fixture: S56 bloqueia. Severidade: média (forma rara). Esforço: P. Dono: tech-lead.

**A11 · sem mudança (recomendado).** Como nos pareceres anteriores.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha acompanhou o deslocamento (`resto_no_git`, `:1494`).

### O que foi conferido e está correto
- **Sem afrouxar:** o delta só acrescenta recusa (acima).
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log c3cde09f..c22624c5 -- tests/test_oraculo_v047.py` vazio).

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"). Rodei `tests.test_hook_destino_opaco` (4 testes OK em 37 s no head `c22624c5`) e as sondas. Quando houver PR, o portão pede o CI verde no head desta revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
