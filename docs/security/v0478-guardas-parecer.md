---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 460a8a002d27be6089f22eb3452c4d9bc69646f1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.29, revalidação)

Volta por delta. Rodada anterior: `commit 9a20739e` (E3.27, reprovado por A9 e A10), no git. Delta lido (`forge-check parecer delta`, `9a20739e..460a8a00`): no domínio, `hooks/parecer.py` (`ATRIBUICAO_ARITMETICA` e `ABRE_ARITMETICA` em `hooks/parecer.py:132`, `mexidas_por_aritmetica` em `:671`, `mexidas_do_texto` em `:681`, o ambiente inicial em `:1164` sobre `textos_da_linha`), `tests/test_hooks_parecer_matriz.py` (S30 a S34, contextos e operadores aritméticos, legítimo novo) e a linha D4 de `docs/hooks.md:41`. Fora do domínio, não relido: o fragmento do changelog e `tests/mutantes/v0478-guardas-parecer-10.json` a `-12.json`.

Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A11 (recomendado) docs/hooks.md:41 · Limites declarados da D4 seguem abertos: `n=HOME; : "$((${n}=0))"`, `a=HO; b=ME; : "$(($a$b=0))"` e `v=$(printf 'H%sE=0' OM); : "$((v))"` antes de `gh pr ready` dão 0. Aceitos como limite do hook pelo critério da D7; o dono confirma pelo Jarvis.

## Sondas

## Detalhe dos achados
**A11 (baixa, recomendado).** Evidência: `docs/hooks.md:41` declara abertos o nome por expansão dentro da aritmética e o valor avaliado como expressão; conferido no cenário do gerador, as três formas do achado dão 0. As formas literais (`n=HOME; : $(($n=0))` e `v='HOME=0'; : $((v))`) recusam (2), por outras regras (D2 e o `=` com contexto aritmético), então o aberto é mais estreito que o texto da linha D4 sugere. Caminho de ataque: só evasão deliberada, montando o nome ou a expressão por partes numa cópia alheia sem `-R`; não há cópia acidental de trecho que caia nessa forma. Fechar exige recusar toda aritmética com variável antes do gh, o que recusa o legítimo de laço e contador. Posição: aceito como limite declarado, pelo mesmo critério da D7 (decisão do dono de 18/11 22:15, opção b, valendo junto com a A3 da E29); como a decisão do dono nomeia só a D7, a confirmação dele para estes dois vai pelo Jarvis (`R-DECISAO`), sem bloquear este parecer. Correção no hook: nenhuma; a cobertura é a trava da A3. Esforço P (registro). Dono: Jarvis, ao dono.

## Estado dos achados anteriores
- **A9 (fechado):** `mexidas_do_texto` soma as mexidas de cada forma de `textos_da_linha` (`hooks/parecer.py:681`, `:1164`). S30 (`set -a; : ${GH_\` + quebra + `REPO:=dono/forge}; gh pr ready feature/x`) dá 2.
- **A10 (fechado):** S31 a S34 dão 2. Fora do gerador também dão 2: `: "$(( HOME = 0 ))"`, `: "$((HO''ME=0))"`, `: "$((HO\`+quebra+`ME=0))"`, `unset 'A[HOME=0]'`, `: ${#A[HOME=0]}`, `(( 1, HOME=0 ))`, `: "$((GIT_DIR=0))" &&`, `: "$((XDG_CONFIG_HOME*=0))"`, `case $((HOME=0)) in`, `$((HOME =` + quebra + ` 0))`, `declare -n r=HOME; r=0`, todas antes de `gh pr ready` ou do merge.
- **A8 (D7, `PATH`):** decidido pelo dono (opção b); a linha D7 de `docs/hooks.md` registra o limite. Não reaberto.
- **A1 a A7:** fechados antes; sem delta que os toque.
- Corpus de legítimos, 0 neste head e igual ao head anterior: `gh pr ready feature/x`, `export PATH="$HOME/bin:$PATH";`, `: ${PAGER:=less};`, `echo "$((HOME == 0)) $((PAGER = 1))" "$HOME=x";`. `n=$((n+1));`, `for ((i=0; …))` e `x=$((x+=1))` antes do gh dão 2 já no head `9a20739e`, pela D5 (lista positiva), não pelo delta.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer; os limites da D4 estão no A11 e a D7 é decisão do dono. Cenário das sondas: o do gerador (`tests/test_hooks_parecer_matriz.py`, base `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia.json`), por um script local fora do repositório; o head anterior conferido pela cópia de `git archive 9a20739e` em pasta temporária. Teste rodado: `python3 -m unittest tests.test_hooks_parecer_matriz` (OK, 8 testes, 59 s). A suíte inteira roda no CI; o brief não cita CI deste head. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
