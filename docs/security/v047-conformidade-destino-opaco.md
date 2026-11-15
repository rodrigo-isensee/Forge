---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: c3cde09fdec39e3d8bed6b8d0e0113216189a7ca
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta de A15)

Revalidação por delta (`forge-check parecer delta`), intervalo `74b42c69..c3cde09f`. No domínio: `hooks/conformidade.py` (função nova `atribui_por_expansao`, usada para o nome inteiro e agora também para cada prefixo em `valores_da_variavel`), `docs/hooks.md` e sete fixtures `opaco-u4-*` novas. Fora do domínio: o mutante 23 e `tests/test_hook_destino_opaco.py`. Etapa E1.340; não fiz a entrega. Parecer anterior: `74b42c69`, reprovado (A15 bloqueante, A11 e A5 recomendados).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (uma linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A16 (bloqueante) hooks/conformidade.py:698 · O prefixo colado não passa por `VARIAVEIS_DO_BASH`: `"$_"t` chega como `$_t`, `_t` vale como do ambiente e libera; `: .gi; cp -rT ev "$_"t` dá rc 0 e o bash copia ev/config sobre .git/config (`$_` = último argumento) (R-CONFORMIDADE)
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1488 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S48 · : .gi; cp -rT ev "$_"t (ev/config com [core] hooksPath) · espera: 2 · obtido: 0
- S49 · true .gi && cp -rT ev "$_"t · espera: 2 · obtido: 0
- S50 · : .g; cp -r ev/. "$_"it · espera: 2 · obtido: 0
- S51 · : .gi; cp x "$_"t · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: script no meu rascunho que monta o fixture de `tests/test_conformidade_opaco.py` (`dados_do_caso`, ambiente projeto, papel `forge:tech-lead`) com `ev/config` a mais, roda `hooks/conformidade.py` do head `c3cde09f` pelo `rodar` de `tests/test_hooks.py`, depois roda a mesma linha no `bash -c` na pasta do caso e compara o `.git` (sem `objects/`) antes e depois. "espera: 2" quer dizer que o bash mudou o `.git`, o que aconteceu nas quatro. Controles: `: .git; cp -rT ev "$_"` e `cp -rT ev $_` dão 2 (o nome inteiro `_` já está na lista); `: docs; echo a > "$_"t` dá 0 e não toca o `.git`.

**A15 · fechada.** S44 a S47 dão 2 no head. Também dão 2: `: ${d[0]:=.gi}; cp -rT ev "$d"t`, `: ${dg:=.g}; … "$dg"it`, `: ${d:=.}; … "$d"git`, `: ${d:=.}; : ${dg:=g}; … "$d"gi"t"`, o aninhado `: ${x:-${d:=.gi}}; …`, `true "${d:=.gi}" && …`, `"${d}"t`, `$d"t"`, `"$d""t"`, `"$d"t/`, `"$D"t` (maiúsculo) e `"$d"$'t'`. O legítimo segue em 0: `: ${d:-docs}; echo a > "$d"`, `cp -rT ev "$HOME"t`, `echo a > "$(mktemp)"`. A correção só acrescenta recusa (`or atribui_por_expansao(nome[:k], linha)`), e o mutante 23 a cobre.

**A16 · prefixo colado que o próprio bash grava (dimensão "variável do bash", A4 da E1.280, × forma "variável com resto colado sem barra", A15).**
- Evidência: `hooks/conformidade.py:698`. Com `"$_"t`, o `shlex` entrega `$_t`. A linha 690 só confere o nome inteiro (`_t`) contra `VARIAVEIS_DO_BASH`, e `_t` não está na lista. Na linha 693, `(?<![\w${{])_t` não acha `_t` na linha. Na linha 698, o prefixo `_` aparece só depois de `$`, e a lookbehind o exclui; `atribui_por_expansao("_")` não acha nada. Resultado: `_t` vale como do ambiente (`SEM_VALOR`), e o destino passa. O bash grava em `$_` o último argumento do comando anterior (`.gi`), e o destino vira `.git`. O defeito já existia na base `74b42c69` (linha 693 dela) e cai na mesma busca por prefixo que a A15 mandava varrer.
- Caminho de ataque: um agente de qualquer papel, por injeção de prompt, roda S48 numa chamada só. `:` e `true` estão em `COMANDOS_INOFENSIVOS`, então a linha passa pela `linha_conhecida`. A origem tem nome neutro, então o U3 não age, e sem `.git` literal o `CRITICO` não dispara. `cp -rT` ou `cp -r ev/.` copia o conteúdo da pasta sobre o `.git`: `.git/config` com `core.hooksPath` derruba a `R-VERIFY`, e `core.fsmonitor` roda código. Com origem `x` simples, grava `.git/x`.
- Severidade: alta. É bloqueante: defeito provado no portão, na mesma busca por prefixo que esta volta mexeu (`R-CONFORMIDADE`, `R-REVIEW`).
- Correção mínima: no laço de prefixos da linha 698, devolver `None` também quando `nome[:k] in VARIAVEIS_DO_BASH`. A lista inteira hoje: `_ REPLY MAPFILE BASH_REMATCH OPTARG OPTIND PWD OLDPWD DIRSTACK COPROC BASH_ARGV BASH_ARGV0 BASH_ARGC BASH_COMMAND BASH_SOURCE BASH_LINENO FUNCNAME PIPESTATUS READLINE_LINE READLINE_POINT READLINE_MARK COMP_WORDS COMP_CWORD COMP_LINE COMP_POINT COMPREPLY BASH_EXECUTION_STRING EPOCHREALTIME EPOCHSECONDS RANDOM SRANDOM LINENO SECONDS`. O mesmo vale para o prefixo que começa com `GIT_`, como a linha 690 já faz com o nome inteiro. Fixtures: S48 a S51 bloqueiam; `: docs; echo a > "$_"t` também recusa (falso positivo aceitável); `cp -rT ev "$HOME"t` libera. Mutante: tirar a condição nova. Esforço: P. Dono: tech-lead.

**A11 · sem mudança (recomendado).** Como no parecer anterior.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha acompanhou o deslocamento (`resto_no_git`, `:1488`).

### O que foi conferido e está correto
- **Sem afrouxar:** o delta só acrescenta recusa (a função extraída mantém a regex da A14 e ganha um uso por prefixo).
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log 74b42c69..c3cde09f -- tests/test_oraculo_v047.py` vazio). `docs/hooks.md` descreve a A15 como foi feita.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"). Rodei `tests.test_hook_destino_opaco` (4 testes OK em 28 s no head `c3cde09f`) e as sondas. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
