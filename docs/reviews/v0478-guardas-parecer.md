---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 460a8a002d27be6089f22eb3452c4d9bc69646f1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.30 (melhoria/v0478-guardas-parecer), revalidação do A9 e do A10 da segurança da E3.27

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 415eaa82..460a8a00 (E3.28: 460a8a00; pareceres e merge dfd645ff fora do domínio). No domínio: `hooks/parecer.py` (`ATRIBUICAO_ARITMETICA`, `ABRE_ARITMETICA`, `mexidas_por_aritmetica`, `mexidas_do_texto`, `principal`), a linha D4 e a D7 da matriz em `docs/hooks.md`, o gerador `tests/test_hooks_parecer_matriz.py`, as specs `tests/mutantes/v0478-guardas-parecer-10.json` a `-12.json` e o fragmento `changelog.d/`. Nada fora do delta relido.

## Sondas
- S35 · cópia alheia da montagem do gerador, nome entre aspas na aritmética: `: "$(("HOME"=0))"`, `: "$((HO""ME=0))"`, `(( "HOME"=0 ))`, `let "HO"ME=0`, `: "${A["HOME"=0]}"`, antes de `gh pr ready feature/x` (o bash põe HOME=0 nas cinco, conferido) · espera: código 2 · obtido: código 2 nas cinco
- S36 · mesma montagem, `: $((HO\`⏎`ME=0)); gh pr ready feature/x` (A9 na aritmética) · espera: código 2 · obtido: código 2
- S37 · mesma montagem, `gh pr ready feature/x` e `export PATH="$HOME/bin:$PATH"; gh pr ready feature/x` (controles) · espera: código 0 · obtido: código 0 nas duas

## Conferências
- A9 fechado: `principal` (hooks/parecer.py:1164) soma as mexidas de cada texto de `textos_da_linha`, não do comando cru; S30 está no gerador como posição de `POSICOES_DA_EXPANSAO` e em `SONDAS`.
- A10 fechado: `mexidas_por_aritmetica` (hooks/parecer.py:671) cobre os contextos e operadores que a segurança listou; o `=` simples só conta com contexto aritmético no texto e `==`, `!=`, `<=`, `>=` não contam. Falha fechada declarada na D4 (recusa a mais, como `[ -n x ] && gh pr create --body "HOME=x"`); abertos declarados (nome por expansão e valor avaliado) cobertos pela trava do sandbox.
- D7 (`PATH`): limite declarado por decisão do dono, sem código no delta; o legítimo segue em 0 (S37).
- Mutação dirigida (`bin/forge-mutante`, 1 processo): `-10.json` M58 a M65, `-11.json` M66 a M71 e `-12.json` M72 a M75 `morreu`.
- Cobertura (`bin/forge-mutante --cobertura --base 415eaa82`): guardas de :677 e :678 `coberta`, provadas pela mutação acima.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_matriz`: 8 testes, OK.
- Leitura (checklist 1 a 4, 7, 11): uma regra por classe; vizinhos que não atribuem (`$HOME=x`, `HOMEX=1`, `--title`, `GH_CONFIG_DIR=x gh nova`) testados como não mexidos; legítimo com `$((HOME == 0))` e `$((PAGER = 1))` no gerador; a matriz descreve o código.
- Tamanho (H1): cerca de 25 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Aprovado: A9 e A10 fechados com S30 a S34 no gerador e S35 e S36 em código 2, controles em 0; mutantes declarados mortos; D7 como limite declarado.
