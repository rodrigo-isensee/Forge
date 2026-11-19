---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 415eaa822c6d3af23dd4d5e9701f2a60821990cf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.25 (melhoria/v0478-guardas-parecer), revalidação do A5 da E3.21

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 9b075525..415eaa82 (E3.24: 415eaa82; os pareceres 72d85312, c105ea2b, bb466960 e o merge 0da1a32b fora do domínio). No domínio: `hooks/parecer.py` (`EXPANSAO_QUE_ATRIBUI`, `mexidas_por_expansao`, `principal`), a linha D4 da matriz em `docs/hooks.md`, o gerador `tests/test_hooks_parecer_matriz.py`, a spec `tests/mutantes/v0478-guardas-parecer-10.json` e o fragmento `changelog.d/`. Nada fora do delta relido.

## Sondas
- S28 · cópia alheia da montagem do gerador, `set -a; : ${GH_REPO:=dono/forge}; gh pr ready feature/x`, com aspas e com `echo` no lugar de `:` · espera: código 2 · obtido: código 2 nas três
- S29 · mesma montagem, `set -a; : ${XDG_CONFIG_HOME:=$PWD/x}; gh pr merge feature/x` e `set -a; : ${GIT_CONFIG_GLOBAL:=g.cfg}; gh pr ready feature/x` · espera: código 2 · obtido: código 2 nas duas
- S32 · mesma montagem, aninhada `: ${A:-${GH_REPO:=dono/forge}}`, em atribuição `x=${GH_REPO:=dono/forge}` e aritmética `: $(( GIT_CONFIG_COUNT=1 ))`, antes de `gh pr ready feature/x` · espera: código 2 · obtido: código 2 nas três
- S33 · mesma montagem, `gh pr ready feature/x` e `set -a; : "${GH_REPO:-dono/forge}"; gh pr ready feature/x` (controles) · espera: código 0 · obtido: código 0 nas duas

## Conferências
- A5 (meu, E3.21) fechado: `mexidas_por_expansao` (hooks/parecer.py:651) soma à D4 o nome de `${N:=v}`, `${N=v}` e `${N[i]:=v}` com a regra de `SENSIVEIS` e `GIT_*`, e a indireta `${!n:=v}` mexe em todos; vale para a linha inteira desde o começo (recusa a mais depois do gh, dita na matriz). S28 e S29 estão no gerador como `SONDAS`.
- Mutação dirigida (`bin/forge-mutante`, 1 processo): spec `-10.json` M58 a M62 `morreu`.
- Cobertura (`bin/forge-mutante --cobertura --base 9b075525`): as guardas de :657 e :660 `coberta`.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_matriz`: 6 testes, OK.
- Leitura (checklist 1 a 4, 7, 11): uma regra por classe, o vizinho que não atribui (`:-`, `:+`, `:?`, `#`, `/`) testado como não mexida; legítimos `${GH_REPO:-…}` e `${PAGER:=less}` no gerador; o texto da matriz descreve o código.
- Tamanho (H1): cerca de 15 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Aprovado: A5 fechado com S28 e S29 em código 2 e os controles em 0; mutantes declarados mortos.
