---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: a437574de2fddeb2f2a40f76b69bb4b5868f5d6a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote-leitura-hook (revalidação 2)

Escopo: a entrega inteira, `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 a437574de2fddeb2f2a40f76b69bb4b5868f5d6a`. Revalidei por delta desde o parecer anterior (dd91909). `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou o intervalo `dd91909..a437574`: 570d684, 33f003a, 61e4a00 e a437574, em `hooks/_comum.py` (717-723, 761-765, 812-862), `hooks/conformidade.py` (28-36, 67-74, 670-686, 749-752, 1384), `hooks/parecer.py` (21-22, 360), `tests/test_hooks.py`, as 8 fixtures novas, `docs/hooks.md:94-95` e o fragmento do changelog. Li só esse delta. Os commits até dd91909 ficam como "já lido", e os pareceres das rodadas anteriores continuam valendo para eles. Sou revisor independente, não o autor. A segurança (E1.3) tem parecer próprio em `docs/security/`, que não refiz aqui.

## Achados
- A1 (bloqueante) hooks/conformidade.py:750 · a lista positiva faz do corpo de patch, kubectl apply -f -, while read…done, sqlite3 e envsubst com <<'EOF' e apóstrofo no corpo uma linha ilegível: sai 2 (base 0), e a correção pede <<'FIM', que já está na linha. Dar a saída certa; fixtures.

## Parecer
**Reprovado**, por um bloqueante. Os dois bloqueantes da rodada anterior (A1 e A2 do review) e os dois da segurança (A1 e A2) estão resolvidos, e as R4 e R5 da segurança também. O A1 novo vem da correção do A1 de segurança. A direção está certa, porque fecha na dúvida, mas a correção trouxe um falso positivo em comandos comuns nos projetos, e a mensagem manda o agente fazer o que ele já fez.

### Sondas
As sondas rodaram em cópias por `git archive` da base (ad6d96c) e do HEAD (a437574) em `$TMPDIR`, com o hook real executado pelo `Fixture`, pelo `montar_proc` e pelo `rodar` da própria cópia. Os modelos foram as fixtures `conformidade/shell-heredoc-no-commit-libera`, `conformidade/crase-aninhada-em-60-pastas-no-verify-bloqueia` e `parecer/forge-clone-pr-ready-sem-parecer-bloqueia`.

| Caso | base | HEAD |
|---|---|---|
| `patch -p1 <<'EOF'` com `-it's` no diff (conformidade) | 0 | **2** |
| `kubectl apply -f - <<'EOF'` com `key: it's` (conformidade) | 0 | **2** |
| `while read l; do echo $l; done <<'EOF'` com `it's` (conformidade) | 0 | **2** |
| `sqlite3 db <<'EOF'` com `-- don't` (conformidade) | 0 | **2** |
| `envsubst <<'EOF' > x` com `it's $HOME` (conformidade) | 0 | **2** |
| `psql`, `python3 -`, `cat > notas.md` com `<<'EOF'` (conformidade) | 0 | 0 |
| `ssh host <<'EOF'` e `sqlite3 db <<'EOF'` com `git push origin main` (conformidade) | 0 | 2, R-MAIN |
| `cat <<'EOF'` com `git push origin main` (conformidade) | 0 | 0 |
| `docker exec -i c sh <<'EOF'` e `cat <<'EOF' \| sh` com `--no-verify` (conformidade) | 2 | 2 |
| `cat <<X⏎a\⏎X⏎cat <<Y⏎X⏎gh pr ready feature/x⏎Y` sem parecer (parecer) | 2 | 2 |
| a mesma forma com `a\\` (barra escapada; o bash não roda o ready) (parecer) | 2 | 0, correto |
| `eval "$(cat <<'EOF'⏎gh pr ready …⏎EOF⏎)"` (parecer, R5 da segurança) | 0 | 2 |
| `kubectl apply -f - <<'EOF'` com apóstrofo e depois `gh pr ready` (parecer) | 2 | 2 |
| 20 cd × 19 crases de 5 KB e de 8 KB, e 5 cd × 10 crases de 25 KB, depois `` `git push --no-verify …` `` (conformidade) | 2 em 1,2 s (8 KB) | 2 em 0,94 a 0,96 s |
| 15 cd × 25 crases de 20 KB, depois a mesma crase (conformidade) | não medido | 2 em 0,11 s (teto de caracteres) |
| uma palavra de 290 KB e `&& git push --no-verify` (conformidade) | 2 em 3,51 s | 2 em 4,19 s |
| `echo` com 145 mil palavras, sem ação (conformidade) | não medido | 0 em 3,40 s |
| `cat > f.txt <<'EOF'` com 200 KB (conformidade) | não medido | 0 em 0,13 s |
| 20 grupos `cd … && x=$(git rev-parse HEAD) && echo \`date\`` (conformidade) | não medido | 0 em 0,10 s |
| 20 cd × 19 crases de 8 KB e 15 × 25 × 20 KB, com `` `gh pr ready …` `` (parecer) | 0 | 2 em 0,88 s e 2,93 s |

O bash local confirma a leitura do A2. `printf 'cat <<X\na\\\nX\ncat <<Y\nX\necho RODOU\nY\n' | bash` roda `RODOU`. Com `a\\` no lugar de `a\`, ele imprime `echo RODOU` como texto e não o roda.

### A1: falso positivo da lista positiva, com uma correção que não se aplica
O 33f003a inverte a lista. Agora o corpo de heredoc é conferido como comando, salvo quando todo comando da linha do dono está em `LEITORES_DO_CORPO` ou é `git` ou `gh` com subcomando que lê (`hooks/_comum.py:812-862`). A segurança pediu isso, e é o certo para os donos que rodam o corpo (`source /dev/stdin`, `.`, `ksh`, `eval`, `ssh`, `sudo`).

O efeito colateral aparece com os donos que só leem o corpo e não estão na lista, como `patch`, `kubectl apply -f -`, `sqlite3`, `mysql`, `envsubst`, `sed` e o `done` de um `while read`. Nesses casos, o corpo passa por `Guarda.bash`. Se ele não se lê como shell, o que basta um apóstrofo num diff ou num texto em inglês para causar, a linha cai na recusa de `hooks/conformidade.py:723`. A correção dessa recusa é "use heredoc só com <<'FIM'", e a linha já usa `<<'EOF'`. O agente do projeto fica sem saída e tende a repetir a tentativa. O `conformidade` roda em todos os projetos, e a base liberava essas cinco formas.

Na sessão do Forge, o `parecer` só é alcançado com `gh pr`, `gh api`, `merge` ou `pull` na linha, e ali o efeito é pequeno: a base já recusava o caso do kubectl pelo apóstrofo.

Sugestões (o autor decide, com a segurança):
- **mínimo:** quando a recusa vem de um corpo de heredoc conferido como comando, ela precisa ter mensagem própria, com uma correção que funcione: gravar o texto num arquivo (`cat > arquivo <<'EOF'`, que é leitor) e passar o arquivo ao programa (`patch -p1 < arquivo`, `kubectl apply -f arquivo`). Com isso a recusa continua fechando na dúvida e deixa de ser um beco;
- **opcional:** o corpo ilegível de um dono fora da lista que não é shell conhecido recusa só pela rede da ADR 0011 (marcador crítico). Isso afrouxa em relação ao HEAD, então só com o aval da segurança;
- fixtures `-bloqueia` (ou `-libera`, conforme a escolha) para `patch -p1 <<'EOF'` e `while read … done <<'EOF'` com apóstrofo, e uma linha no `docs/hooks.md:94` dizendo que o dono fora da lista faz do corpo comando, com o apóstrofo no corpo recusado e a saída pelo arquivo.

### Delta lido, por commit
- **570d684 (A2 do review e da segurança):** resolvido. `heredocs` junta a linha física que acaba em barra ímpar com a seguinte antes de comparar, só com o delimitador sem aspas. A tab da linha juntada fica, como no bash com `<<-`. `barra_impar_no_fim` é pequena e tem nome claro. Os cinco casos novos de `test_heredocs` cobrem `a\`, `\` sozinha, `a\\`, o delimitador entre aspas e `<<-`. As duas fixtures do `parecer` (ready e merge) e a do `conformidade` saem 2. O caso `a\\` passa de 2 para 0, e isso está certo, porque o bash não roda o ready.
- **33f003a (A1 e R4 da segurança, cobre a R5):** a lista ficou numa fonte única, usada em `parecer.py:360`, `conformidade.py:750` e `conformidade.py:1384`. Os três pontos que a R4 apontou agora estão iguais. `programas_da_linha` tira aspas e barras e pula redireções, atribuições e palavras reservadas, o que só deixa a leitura mais desconfiada. O `git -c` interrompe a lista, porque pode definir um alias `!sh`, e o `-C` pula o argumento. O teste `test_corpo_de_heredoc_so_lido_pela_lista_positiva` afirma um mínimo de 10 donos executores e testa o `tambem`. No `conformidade`, o `interprete` virou função, e o corpo de `python3 -` vai ao `checar_texto` e não ao `bash`. A troca do `elif` por `if` faz `sudo python3 - <<EOF` passar pelos dois, o que está certo. O A1 acima nasce aqui.
- **61e4a00 (A1 do review):** resolvido. O orçamento agora conta 400 conferências, 300 mil caracteres somados e 3 s medidos com `time.monotonic()` desde o nível 0. A recusa usa R-CONFORMIDADE com uma mensagem que cita o texto longo. Os três eixos do teste variam o corpo (5, 8 e 20 KB) e exigem metade do timeout lido do `hooks.json`. As linhas legítimas que medi ficam em 0,10 a 0,13 s, cerca de 30 vezes abaixo do prazo de 3 s, então o risco de recusa por carga é baixo. Esse tipo de recusa fecha na dúvida e diz como corrigir.
- **a437574 (docs):** `docs/hooks.md:94-95` e o fragmento acompanham as três correções. Falta o efeito do A1 (ver acima).

### Recomendações (fora do bloco)
- **Prazo de uma conferência só (anterior à entrega):** o prazo de 3 s é medido na entrada de cada conferência, e uma conferência sozinha tem custo superlinear no tamanho. Uma palavra de 290 KB leva 4,19 s no HEAD (3,51 s na base). Com a máquina carregada pela suíte, isso se aproxima dos 10 s do `hooks.json`. Um `TETO_DE_CARACTERES` de cerca de 150 mil daria margem, mas o valor fica a critério do autor. O `parecer` não tem orçamento de caracteres (500 KB levam 2,93 s). Hoje o `conformidade` recusa a mesma linha pelo teto, e por isso isso não é bloqueante.
- Continua aberta: o cartão HOOK-N4 entra no quadro antes do merge, para o `skipTest` do T1 ter dono.
- O fragmento do changelog continua numa linha de cerca de 700 caracteres. Vale dividir em dois itens na volta.
- Os commits continuam limpos, um por achado, com Conventional Commits em português e o porquê na mensagem.

### Invariantes e ferramentas
O delta não toca em `tests/config.json`. O rótulo `afrouxa-regra` do dono continua necessário no merge (E1.5), porque o diff toca em `hooks/conformidade.py`. Não refiz as ferramentas: a entrega relata 1319 OK, e o pre-push deste parecer roda a suíte sobre o mesmo patch.
