---
tipo: revisao-seguranca
contrato: 1
pedido: hook-comentario-shlex
branch: melhoria/hook-comentario-shlex
commit: 74dc3f62f205dc63bc95c13aeeacf7dc72f884a0
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: hook-comentario-shlex

Diff revisado: `10c838f..74dc3f6` (hooks/_comum.py, 7 fixtures de `tests/hooks/conformidade/`, 15 casos em tests/test_hooks.py, fragmento do changelog).

## Gatilhos
Controles do Forge (R-SEGURANCA): a entrega muda a leitura da linha do shell (`fichas`), base de todas as checagens do hook `conformidade` (R-MAIN, R-VERIFY, escrita protegida, `sugerir`).

## Achados
- A1 (bloqueante) hooks/_comum.py:222 · `(` em ANTES_DE_COMENTARIO abre comentário onde o bash não: `((#x)); git push --force origin main` e `[[ a =~ (#b) ]]; git push --no-verify origin x` saem com código 0 no hook e o bash roda o push. Tirar `(` daqui e de INICIO_DE_PALAVRA (:388), com fixtures.

## Detalhe dos achados
**A1.** Evidência: hooks/_comum.py:222 (`ANTES_DE_COMENTARIO` inclui `(`), usado em :243; a guarda da linha crítica faz o mesmo em :388/:459 (`#` depois de `(` encerra a varredura com "comentário até o fim da linha"), então nem o analisador nem a recusa por construção não modelada veem o resto da linha.
- Reprodução (estática, local, em cópia por `git archive` do 74dc3f6 no diretório temporário, pelo `rodar_dados` da suíte, com a fixture `comentario-colado-push-force-bloqueia` como base): `[[ a =~ (#b) ]]; git push --force origin main`, `((#x)); git push --force origin main` e `[[ a =~ (#b) ]]; git push --no-verify origin feature/x` saem com código 0; o controle `true; git push --force origin main` sai com 2. No bash (`bash -c`, com `echo` no lugar do push): `((#x)); echo R1` imprime R1 (erro aritmético não interrompe a lista) e `[[ a =~ (#b) ]]; echo R4` imprime R4; o `#` ali não é comentário.
- Caminho de ataque: um agente (por engano ou por instrução injetada num arquivo lido) monta a linha com o prefixo acima; o hook não vê o `git push --force`/`--no-verify` nem um push direto para branch protegida, e R-VERIFY/R-MAIN deixam de valer naquela chamada. É a mesma classe e o mesmo impacto do furo que motivou o pedido (o escopo E1 diz que o `#` só abre comentário no início de palavra; depois de `((` e do `(` do `=~` não é início de palavra).
- Não é regressão: a base 10c838f deixa passar as mesmas três linhas (lá qualquer `#` escondia o resto). Bloqueia porque a entrega é a correção dedicada desse furo, sai sozinha numa release (0.27.1) e o comentário do código afirma a equivalência com o bash.
- Severidade: alta (contorno de controle local do Forge, sem pré-condição além de escrever a linha). Correção mínima: tirar `(` de `ANTES_DE_COMENTARIO` (:222) e de `INICIO_DE_PALAVRA` (:388); o efeito é só ler mais da linha (`(#x` de subshell, que o bash trata como comentário, passa a ser lido como palavra: no pior caso, recusa a mais). Fixtures de recusa para as duas formas (`((#x)); git push --force origin main` e `[[ a =~ (#b) ]]; git push --force origin main`) e um caso na `test_cerquilha_so_abre_comentario_no_inicio_de_palavra`. Esforço P. Dono: tech-lead.

**Conferido sem achado:**
- `)`, `<`, `>`, `\r` e `#` colado ficam fora de `ANTES_DE_COMENTARIO`: o hook lê mais que o bash (o bash trata `(true)#x; ...` como comentário; o hook lê o resto), direção segura.
- `#` precedido de `;`, `&`, `|`, espaço ou quebra de linha só chega a `pular_comentario` no início de ficha; `;`/espaço escapados ou entre aspas (`a\;#b`, `a\ #b`, `";"#b`) ficam dentro da palavra e não abrem comentário (casos da suíte e sonda).
- `instream.seek(fim)` com `_pushback_chars.clear()`: o `pushback` guarda só o caractere que encerrou a ficha anterior, antes do `#`; o salto para a quebra de linha (que continua sendo sinal e separa comandos) ou para o fim é coerente com a posição em caracteres do leitor em memória.
- Fixtures `nao-modelado-comentario-push-main-dev-bloqueia` e `nao-modelado-cerquilha-no-meio-push-main-dev-bloqueia` passam de "não modela" para R-MAIN com o mesmo código 2: a recusa ficou mais específica porque o push agora é lido; a recusa por construção não modelada continua coberta pelas duas fixtures novas `nao-modelado-*-push-dev-bloqueia` (branch não protegida), e a guarda `# + outra linha` (:458) não mudou. Nada afrouxou.

**Recomendação (não bloqueante):** o `$((#x))` dentro de substituição cai no mesmo `(`; a correção do A1 o cobre, vale um caso na tabela da suíte.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas do hook pela própria suíte em cópia temporária e `bash -c` só com `echo`, em diretório de rascunho. Ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint, osv-scanner; a entrega não toca workflow, dependência nem segredo.
