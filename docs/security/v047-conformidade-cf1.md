---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-cf1
commit: 0121b3b2e7fd4aeafdf9b773d441f428af662d3b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (CF1, A17 a A19 do hook conformidade)

Revalidação por delta, head `fbc41e6c` (E2.545). A cf1 parte do parecer `docs/security/v047-conformidade-destino-opaco.md` (commit `081473ac`, aprovado, com A17 a A19, A11 e A5 recomendados). Não existe parecer próprio da cf1: li `forge-check parecer delta` desse parecer, intervalo `081473ac..fbc41e6c`, e li o código do domínio por inteiro. No domínio: `hooks/_comum.py`, `hooks/conformidade.py`, `bin/forge-testes`, `docs/hooks.md` e 32 fixtures `opaco-cf1-*`. O resto do delta (`hooks/meta.py`, `hooks/parecer.py`, o texto de `forge-testes`) veio da `develop` pelo merge `0121b3b2`, não é do item, e eu não o revi aqui; os dois pareceres de volta (review `6f8bd39e`, QA `fbc41e6c`) já aprovaram a cf1.

## Gatilhos
Gatilhos: hook de guarda (`conformidade`) que analisa entrada livre (uma linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão), bloqueio por `R-CONFORMIDADE` (`R-SEGURANCA`).

## O que a cf1 fecha (lido e sondado no hook real)
- **A17** (`hooks/_comum.py:615`, `DESCRITOR_DA_REDIRECAO`): o número ou `{nome}` colado antes de `>`/`<` deixa de ser palavra. As 17 formas de descritor que sondei (`2>`, `2>>`, `1>`, `12>`, `{fd}>`, `2>|`, `2<>`, `2>&-`, `22>&1`, antes, no meio e depois do destino) com `cp`, `install`, `rsync` e `git config` dão 2; `a2>x` e `2 >x` seguem como palavra e o legítimo (`grep foo docs 2>/dev/null`, `cat a 2>&1 | head`, `echo 2 > docs/a.md`) dá 0.
- **A18** (`hooks/conformidade.py:327`, `SO_VARIAVEL` com `$@` e `$*`): `set -- .git; cp -rT ev "$@"`, `"$*"`, `$@`, `"${@}"`, `"${@:1}"`, `"$1"`, `for x; do …`, e os destinos de `mv`, `ln -sf` e `cp -t` dão 2. `$#` e `$$` seguem literais, como o comentário diz, e dão 0 com valor fora do `.git`.
- **A19** (`hooks/conformidade.py:702`, `atribui_como_argumento`): `declare|typeset -n d=_`, em grupo (`-nr`, `-rn`), depois de `--`, com `e=x` antes ou depois, atrás de `builtin` e `command`, em função, `if`, `&&` e chave, ou por `$c -n` e `declare $o`, dão 2; `declare -r d=docs` e `local d=docs` liberam e o bash concorda.

## Método e resultado das sondas
Oráculo pelo bash real: cada linha rodou num repositório temporário descartável (cópia do `.git` de teste) e comparei se o `.git` mudou com o código de saída do hook (`conformidade.py` no head, lançado pelo `Fixture` e `rodar` de `tests/test_hooks.py`). 130 linhas (A17, A18, A19 e legítimos). **Nenhuma fuga das três classes da cf1.** As recusas sem mudança no `.git` (falso positivo) são `declare +n`, `declare -- -n`, `export -n`, `readonly -n`, `local -n` fora de função e `set -- docs; cp -rT ev "$@"`: a falha fechada que o desenho prevê.

Pesquisa fora das dimensões do item achou um furo antigo, do mesmo hook, que a cf1 não toca nem agrava (A20). Rodei também no head `tests.test_hook_destino_opaco` (4 testes) e `tests.test_conformidade_opaco` (2 testes, 150 execuções contra o oráculo do bash): OK. Não rodei a suíte inteira (ordem do dono de 16/11, brief) e não há CI no head: o CI do PR é o portão da suíte.

Vale a ordem do dono de 15/11: bloqueia só achado antigo aberto ou regressão. A17, A18 e A19 estão fechados. A20 existe idêntico na `develop` `86ac0fcb` e no `081473ac`, e fica fora do texto da cf1; entra como cartão novo, recomendado.

## Achados
- A17 (recomendado) hooks/_comum.py:615 · Fechado: o descritor colado (`2>x`, `9<y`, `{fd}>x`) não é mais palavra; `cp ev/config .git/config 2>/dev/null` (S52), install (S53) e rsync (S54) dão 2.
- A18 (recomendado) hooks/conformidade.py:327 · Fechado: `$@` e `$*` entram em `SO_VARIAVEL`; `set -- .git; cp -rT ev "$@"` (S55) dá 2.
- A19 (recomendado) hooks/conformidade.py:702 · Fechado: `declare -n d=_` e os declaradores com `-n` não dão valor à variável; S56 dá 2; `declare -r d=docs` segue liberado.
- A20 (recomendado) hooks/conformidade.py:1464 · Resto com barra depois de variável ou substituição que vale `.git` e que não é nome da lista do git libera: `d=.git; cp -rT ev "$d/."`, `"$(echo .git)/."`, `set -- .git; cp ev/config "$@"/c` gravam no `.git`. Igual na develop 86ac0fcb; cartão
- A11 (recomendado) hooks/conformidade.py:500 · Segue aberto, sem mudança: a lista fechada recusa programa externo na linha, que não troca a resolução do shell.
- A5 (recomendado) hooks/conformidade.py:1522 · Segue aberto, sem mudança: resto com barra que sobe (`/../config`) depois de opaco dentro do `.git` libera; é da mesma família do A20.

## Sondas

## Detalhe dos achados
**A20.** Evidência: `hooks/conformidade.py:1464` (`resto_colado`, que só decide o resto sem barra; o resto com barra é do `resto_no_git`, que olha só os nomes protegidos). Caminho de ataque: um agente com a linha livre grava `d=.git; cp -rT ev "$d/."` (ou `"$(echo .git)/."`, `"$@/."`, `"$_/."` depois de `: .git`); `ev/` traz `config` com `hooksPath` ou `hooks/pre-push`; o bash copia tudo sobre o `.git` e o hook libera com 0, enquanto o literal `cp -rT ev .git/.` dá 2 (`/.` é o próprio diretório). Mesmo com o `.git/c` (nome fora da lista) o literal dá 2 e `"$(echo .git)"/c` libera. Idêntico em `develop` `86ac0fcb`, em `081473ac` e na cf1: não é regressão. Severidade: alta (grava `config` e `hooks/` do repositório). Correção mínima: com valor que cita o `.git` (U1) e resto com barra, recusar o resto vazio, `.`, `./` e todo componente fora de uma lista positiva, no `resto_colado`, em vez de pedir o nome da lista do git; fixture por forma de `$d/.`, `$@/.`, `$(…)/.` e `"$@"/c`. Esforço: P. Dono: `software-engineer`. Cartão de prioridade alta junto do A5.

Os achados A17 a A19 mudam de aberto para fechado no head `fbc41e6c`; os 32 fixtures `opaco-cf1-*` cobrem as mesmas formas que sondei, com os falsos negativos de descritor, `$@`/`$*` e `-n` nos nomes dos arquivos.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
