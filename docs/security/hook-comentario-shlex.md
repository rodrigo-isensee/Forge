---
tipo: revisao-seguranca
contrato: 1
pedido: hook-comentario-shlex
branch: melhoria/hook-comentario-shlex
commit: 7013204f54c8e763f15217934f8b68bcaf897e4b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: hook-comentario-shlex

Diff revisado: `10c838f..7013204` (volta 0 sobre `74dc3f6`; voltas 1 e 2 abaixo) (hooks/_comum.py, 7 fixtures de `tests/hooks/conformidade/`, 15 casos em tests/test_hooks.py, fragmento do changelog).

## Gatilhos
Controles do Forge (R-SEGURANCA): a entrega muda a leitura da linha do shell (`fichas`), base de todas as checagens do hook `conformidade` (R-MAIN, R-VERIFY, escrita protegida, `sugerir`).

## Achados
- A3 (bloqueante) hooks/_comum.py:227 · com `((` ou `=~` na linha o comentário vira palavras; um `'` ou `\` nele dá ValueError e conformidade.py:668 libera: `(( 1 )) && git push origin main # it's ok` sai com 0 (a base barra). Regressão da volta 2.
- A4 (bloqueante) hooks/_comum.py:223 · sem `)` o hook lê o comentário de `(true)#'`; a aspa sem par dá ValueError e conformidade.py:668 libera: `git push --force origin main; (true)#'` sai com 0 (a base barra). Regressão desde a volta 0.
- A5 (bloqueante) hooks/_comum.py:227 · padrão extglob (`@(`, `!(`, `+(`, `*(`, `?(`) não entra em SEM_COMENTARIO: `[[ a == @(a|#b) ]]; git push --force origin main` sai com 0; no `[[` o bash lê `#b` como palavra e roda o push. Mesma classe do A1.

## Detalhe dos achados
**A1 (volta 0, resolvido na volta 1).** Evidência: hooks/_comum.py:222 (`ANTES_DE_COMENTARIO` inclui `(`), usado em :243; a guarda da linha crítica faz o mesmo em :388/:459 (`#` depois de `(` encerra a varredura com "comentário até o fim da linha"), então nem o analisador nem a recusa por construção não modelada veem o resto da linha.
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

## Volta 1
Delta revisado: `74dc3f6..ee29c11` (hooks/_comum.py:223 e :391 sem `(`; 4 fixtures `comentario-depois-de-*`; 3 casos na `test_cerquilha_so_abre_comentario_no_inicio_de_palavra`), e de novo a entrega inteira.

**A1: resolvido.** `ANTES_DE_COMENTARIO` (:223) e `INICIO_DE_PALAVRA` (:391) já não têm `(`. Sonda (mesmo método da volta 0, cópia por `git archive` do ee29c11 no diretório temporário, `rodar_dados` da suíte): `((#x)); git push --force origin main`, `[[ a =~ (#b) ]]; git push --no-verify origin feature/x` e `echo $((#x)); git push --force origin main` saem com 2; as fixtures novas e os casos da tabela passam (3 testes do filtro, OK). A recomendação do `$((#x))` virou fixture (`comentario-depois-de-substituicao-aritmetica-push-force-bloqueia`). Efeito colateral só no sentido seguro: `(#x` passa a ser lido como palavra.

**A2 (novo, bloqueante).** Evidência: hooks/_comum.py:391 (`INICIO_DE_PALAVRA` mantém `)`), usado em :462: na guarda `construcao_nao_modelada`, um `#` logo depois de `)` encerra a varredura como comentário. No `fichas`, `)` já está fora de `ANTES_DE_COMENTARIO` (:223), então o analisador lê o resto da linha, mas a guarda não: as construções não modeladas depois do `)#` (`${…}`, `$'…'`, `$X`) não são recusadas e o analisador as lê errado (`${B:-main}` e `$'main'` não viram `main`).
- Reprodução (estática, local, mesma cópia): `echo $(echo a)#b; git push origin ${B:-main}` e `echo $(echo a)#b; git push origin $'main'` saem com 0 (fixture na `feature/x`); os controles `true; git push origin ${B:-main}`, `true; git push origin $'main'` e `echo $(echo a)#b; git push origin main` saem com 2. No bash (`bash -c` só com `echo`): `echo $(echo a)#b; echo R1 ${B:-main}` imprime `a#b` e `R1 main`, ou seja, o `#` colado ao `)` de `$(…)` é parte da palavra e o resto da linha roda. `(true)#x; echo R3` não imprime nada (ali é comentário), então tirar `)` só faz a guarda ler a mais.
- Caminho de ataque: o mesmo do A1 (agente por engano ou instrução injetada monta a linha); R-MAIN deixa de valer naquela chamada. Não é regressão: a base 10c838f e o 74dc3f6 deixam passar as mesmas linhas (na base, todas as sondas da volta 0 e desta passam). Bloqueia pelo mesmo motivo do A1: a entrega é a correção dedicada da leitura do `#`, sai sozinha na 0.27.1, e o comentário de :389 afirma que, na dúvida, a linha é lida por inteiro; com `)` em `INICIO_DE_PALAVRA` a guarda e o `fichas` divergem justo no caso duvidoso. Falha minha na volta 0: conferi o `)` só no `fichas` (seção "Conferido sem achado"), não na guarda.
- Severidade: alta (contorno de R-MAIN local, sem pré-condição além de escrever a linha). Correção mínima: `INICIO_DE_PALAVRA = " \t\n;&|"` (igual a `ANTES_DE_COMENTARIO`; vale considerar uma constante só, para as duas não divergirem de novo), com fixtures de recusa para as duas linhas acima e um caso de `construcao_nao_modelada` para `echo $(echo a)#b; echo ${X}` (espera `${X}` ou equivalente, não None). Esforço P. Dono: tech-lead.

**Conferido sem achado na volta 1:** nenhuma outra mudança de código no delta; as 4 fixtures novas esperam código 2 com a mensagem da regra; os casos novos da tabela registram a leitura esperada (`#x`/`#b` como palavra); o fragmento do changelog e as fixtures da volta 0 não mudaram.

## Volta 2
Delta revisado: `ee29c11..7013204` (constante única `INICIO_DE_PALAVRA` em hooks/_comum.py:223, sem `(` nem `)`; `SEM_COMENTARIO` em :227 e `abre_comentario` em :230, usados em `fichas` e na guarda em :468; 7 fixtures `comentario-*-dentro-de-*` e `comentario-depois-de-substituicao-fechada-*`; teste `test_cerquilha_nao_abre_comentario_com_aritmetica_ou_regex`; fragmento do changelog), e de novo a entrega inteira contra a base 10c838f.

**A2: resolvido.** `)` saiu de `INICIO_DE_PALAVRA`, e a guarda e o `fichas` usam a mesma função. As fixtures `comentario-depois-de-substituicao-fechada-push-expansao-bloqueia` e `-push-ansi-bloqueia` passam (todas as fixtures do hook, OK, em cópia por `git archive` do 7013204 no diretório temporário); os achados do review da volta 1 (`((1 #x))`, `for ((…#x…))`, `[[ a =~ ( #b) ]]`, `(a|#b)`) também saem com 2.

**A suposição do autor (`((` e `=~` em qualquer ponto, mesmo entre aspas, desligam o comentário; falha fechada) não se sustenta.** Ler a mais só é seguro se tudo o que o hook não consegue ler for recusado. Não é: quando `comandos` levanta ValueError (aspa sem par, `\` no fim), conformidade.py:668 chama `nao_modelada(achado)` e retorna, sob a premissa de que o shell vai recusar a linha; e `construcao_nao_modelada` termina dentro de aspas sem acusar nada (devolve None). Quando a aspa sem par está num comentário de verdade, o bash roda a linha, e o hook não confere nada dela.

**A3 (novo, bloqueante, regressão da volta 2).** Evidência: hooks/_comum.py:227 e :232 (`SEM_COMENTARIO` desliga todo comentário da linha), hooks/conformidade.py:668-672 (ValueError libera).
- Reprodução (pelo `rodar_dados` da suíte, em cópias por `git archive` de 10c838f, ee29c11 e 7013204, com a fixture `comentario-espaco-dentro-de-regex-push-force-bloqueia` como base, branch `feature/x`): `(( 1 )) && git push origin main # it's ok`, `git push --force origin main # don't (( x`, `git push --no-verify origin feature/x # it's ((`, `git push --force origin main # ) =~ '`, `git push origin main # "=~` e `git push --force origin main # x (( \` saem com 0 no 7013204 e com 2 na base e no ee29c11. No bash (`bash -c` só com `echo`): `echo R1 # don't (( x` e `echo R1 # x \` imprimem R1; o resto é comentário.
- Caminho de ataque: um agente (por engano ou por instrução injetada num arquivo lido) escreve um comentário comum com apóstrofo numa linha que tenha `((` ou `=~`; a primeira forma acima nem parece contorno. R-MAIN e R-VERIFY deixam de valer naquela chamada. Severidade: alta.

**A4 (novo, bloqueante, regressão desde a volta 0).** Evidência: hooks/_comum.py:223 (sem `)`, decisão correta pelo A2) com o mesmo conformidade.py:668. O bash abre comentário em `(true)#x`; o hook lê `#x` como palavra (a mais, o que conferi na volta 0 como direção segura: falha minha, não considerei a aspa).
- Reprodução (mesmo método): `git push --force origin main; (true)#'` e `git push --force origin main; (true)#\` saem com 0 no ee29c11 e no 7013204 e com 2 na base; `(true)#x` sem aspa sai com 2. No bash, `echo R1; (true)#'` imprime R1. Severidade: alta (mesmo caminho do A3).

**Correção mínima de A3 e A4 (uma causa):** a linha crítica que o hook não consegue ler é recusada. No `except ValueError` de hooks/conformidade.py:668, com `CRITICO` na linha, recusar mesmo sem `achado` (por exemplo, `nao_modelada(achado or "aspas ou \\ sem fechar")`), ou fazer `construcao_nao_modelada` devolver um achado quando a varredura termina dentro de aspas ou num `\` final. Com isso, a suposição do autor passa a ser falha fechada de fato. Fixtures de recusa para `(( 1 )) && git push origin main # it's ok`, `git push --force origin main # x (( \` e `git push --force origin main; (true)#'`, e uma de liberação para comentário com apóstrofo sem ação crítica. Esforço P. Dono: tech-lead.

**A5 (novo, bloqueante, não é regressão).** Evidência: hooks/_comum.py:227 (`SEM_COMENTARIO` só tem `((` e `=~`). Dentro de `[[ … ]]`, o bash lê padrões extglob mesmo com `extglob` desligado; com `extglob` ligado (perfil do usuário), também fora dele.
- Reprodução (mesmo método): `[[ a == @(a|#b) ]]; git push --force origin main`, `[[ a == @(a| #b) ]]; …`, `[[ a = @(a&#b) ]]; git push --no-verify origin feature/x` e `[[ a != +(a;#b) ]]; …` saem com 0 no 7013204 (e na base). No bash: `[[ a == @(a|#b) ]]; echo R4` imprime R4 (o mesmo com `+(`, `&#b`, `;#b`); `bash -O extglob -c 'echo @(a|#b); echo R1'` imprime R1.
- Bloqueia pelo motivo do A1 e do A2: a entrega é a correção dedicada da leitura do `#` e sai sozinha na 0.27.1. Correção mínima: incluir `[@!+*?]\(` em `SEM_COMENTARIO` (lê-se a mais; depende da correção do A3 para ser fechada). Fixtures para `[[ a == @(a|#b) ]]; git push --force origin main` e `echo @(a|#b); git push --force origin main`. Esforço P. Dono: tech-lead.

**Conferido sem achado na volta 2:** `abre_comentario` é a única decisão de comentário em `fichas` e na guarda (as duas não divergem mais); a guarda `# + outra linha` (:466) continua antes dela, então comentário seguido de outra linha segue recusado com `SEM_COMENTARIO` ou sem; `ls # nota $X; git push` continua lido como comentário (caso da suíte); `$(( 1 #x ))` e `for ((…))` saem com 2; o fragmento do changelog descreve a mudança sem afrouxar nada. As fixtures antigas não mudaram de resultado (todas OK).

**Recomendação (não bloqueante):** o cartão FICHAS-CORPUS-BASH (corpus fixo comparado com `bash -c` nos testes) teria pegado A3 a A5; vale incluir nele linhas com aspa ou `\` dentro do comentário.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas do hook pela própria suíte em cópia temporária e `bash -c` só com `echo`, em diretório de rascunho. Ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint, osv-scanner; a entrega não toca workflow, dependência nem segredo.
