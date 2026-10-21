---
tipo: review
contrato: 1
pedido: hook-comentario-shlex
branch: melhoria/hook-comentario-shlex
commit: ee29c112923e72d687983d2109b5684c169d5193
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: HOOK-COMENTARIO-SHLEX

Rodada 1 (E1.2), entrega inteira `10c838f..74dc3f6`: 2 commits, 12 arquivos, 251+/8-. Revisor diferente do autor da E1.1 (D-ETAPAS-INST). Segurança (E1.3): parecer próprio do `security-engineer`, não refeito aqui.

Ferramentas rodadas em 74dc3f6: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_cerquilha_so_abre_comentario_no_inicio_de_palavra` → `Ran 2 tests in 31.040s OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos aqui (R-TETO): o pre-push do envio deste parecer roda a suíte, e o QA os refaz no head. O Forge não tem `docs/engineering/praticas.md`; o checklist da skill foi lido sobre o diff.

## Volta 1
Delta lido: `74dc3f6..ee29c11` (1 commit: `hooks/_comum.py` tira `(` de `ANTES_DE_COMENTARIO` e de `INICIO_DE_PALAVRA`; 4 fixtures `comentario-depois-de-*`; 3 casos em `test_cerquilha_so_abre_comentario_no_inicio_de_palavra`), contra o A1 da segurança. Já lido (rodada 1, abaixo): o resto da entrega, sem mudança.

1. **O A1 da segurança está corrigido** nas formas que ele cita: `((#x)); …`, `[[ a =~ (#b) ]]; …` (force e no-verify) e `$((#x))` têm fixture de recusa e caso na tabela. A troca é na direção segura (o `#` depois de `(` passa a ser lido como palavra; `(#x\n…)` de subshell, que o bash trata como comentário, no pior caso recusa a mais). Os comentários das duas constantes passaram a se explicar mutuamente (cobre a minha recomendação 1 da rodada 1).
2. **Correção da minha rodada 1:** o item 4 abaixo (manter `(` no conjunto) estava errado; eu testei só `(#x\n` de subshell e não `((`/`=~`. A segurança acertou.
3. **O furo continua na mesma classe, com espaço antes do `#`.** Dentro de `((…))` (comando aritmético e cabeçalho de `for ((…))`) e na regex do `=~` em `[[ ]]`, o bash não abre comentário nem depois de espaço/`|`; o hook abre. Sonda em cópia por `git archive` de ee29c11 em $TMPDIR, fixtures temporárias rodadas por `test_fixtures`: `((1 #x)); git push --force origin main` e `(( 1 #x )); git push --no-verify origin feature/x` saem com **código 0** (controle `true; git push --force origin main` sai com 2). `comandos()` devolve só `['1']` (o push some); idem `for ((i=0; i<1 #x; i++)); do :; done; git push`, `[[ a =~ ( #b) ]]; git push` e `[[ a =~ (a|#b) ]]; git push`. No `bash -c`, com `echo` no lugar do push, as cinco linhas imprimem o `echo` (erro aritmético e regex não interrompem a lista). Não é regressão (a base 10c838f devolve o mesmo `['1']`), mas é o furo que o pedido corrige (E1: a linha lida como o bash lê) e sai sozinho na 0.27.1; mesmo critério do A1 da segurança. `$(( 1 #x ))` não é explorável na mesma linha (o bash aborta com bad substitution) e na linha seguinte o hook lê o push.
4. **Sugestão de correção (o autor decide a forma):** em vez de enumerar mais um contexto, fechar a classe: com `((` ou `=~` fora de aspas na linha, o `#` não abre comentário em `fichas` nem encerra a varredura em `construcao_nao_modelada` (na dúvida, a linha inteira é lida; no pior caso, recusa a mais). Fixtures de recusa para `((1 #x))`, `(( 1 #x ))` com no-verify, `for ((…#x…))` e `[[ a =~ ( #b) ]]`; casos na tabela.

Ferramentas na volta 1: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures` na cópia de ee29c11 com as 3 sondas: `Ran 1 test in 59.637s FAILED (failures=2)`, as duas falhas sendo só `zz-sonda-1` e `zz-sonda-2` (`AssertionError: 0 != 2`); todas as fixtures da entrega passam. Suíte inteira: fica para o pre-push deste envio e para o QA (R-TETO).

## Achados
- A1 (bloqueante) hooks/_comum.py:223 · `#` depois de espaço dentro de `((…))` abre comentário onde o bash não: `((1 #x)); git push --force origin main` e `(( 1 #x )); git push --no-verify origin feature/x` saem com código 0 e o bash roda o push; idem `for ((…#x…))`. Mesma lacuna em :391.
- A2 (bloqueante) hooks/_comum.py:223 · na regex do `=~` em `[[ ]]`, `#` depois de espaço ou `|` não é comentário no bash: `[[ a =~ ( #b) ]]; git push` e `[[ a =~ (a|#b) ]]; git push` escondem o push do hook (comandos() devolve só `[[ a =~`). Mesma lacuna em :391.

## Recomendações (não bloqueiam)
- `hooks/_comum.py:249`: um comentário curto dizendo que o `seek` vale porque o `instream` é `StringIO` (linha passada como `str`) deixaria explícita a premissa de que o salto depende (pendente da rodada 1).
- Cartão FICHAS-CORPUS-BASH (já registrado pelo Jarvis): um corpus comparado com `bash -c` teria pego A1 e A2 nesta volta; reforço a prioridade.

## Rodada 1 (74dc3f6, aprovado)

1. **Escopo (E1, E2).** `fichas()` desliga o comentário do `shlex` (`lex.commenters = ""`) e passa a tratar o `#` só no início de palavra (`ANTES_DE_COMENTARIO = " \t\n;&|("`), pulando até a quebra de linha, que segue separando comandos. As três linhas do pedido (`echo a#; git push --force origin main`, `cat a#&&git push origin main`, `grep x f#; forge sugerir --fila`) têm fixture de recusa, o comentário real (`ls # nota: git push --force origin main`) tem fixture que libera, e o fragmento `changelog.d/hook-comentario-shlex.md` existe. Nada além do pedido.
2. **Reprodução do furo na base.** `_comum.comandos` de 10c838f devolve `[['echo', 'a']]`, `[['cat', 'a']]` e `[['grep', 'x', 'f']]` para as três linhas (o push e o `forge sugerir` somem), e junta `ls # nota\ngit push --force ...` num comando só (`['ls', 'git', 'push', ...]`). Em 74dc3f6 os quatro saem separados e lidos.
3. **Paridade com o bash (sonda própria em $TMPDIR, 19 linhas).** Para cada linha comparei as palavras do hook com o que o `bash -c` executa (com `git` trocado por uma função). Em todos os casos em que o bash executa o `git`, o hook enxerga o `git push`: `a|#x\n`, `(#x\n`, `a&#b\n`, `{#x`, `${#x}`, `x=#y`, `'a'#b`, `"a"#b`, `a#b#c`, `<(#x\n)`, `$(#x\ngit push)`, comentário só com espaços antes e linha começando por `\n#`. Onde o hook diverge do bash (`)#b`, `2>#x`, `a \\\n#b`), ele lê mais que o bash, nunca menos: a dúvida cai para o lado de ler a linha inteira, como diz o comentário de `hooks/_comum.py:220`.
4. **`#` depois de `(`.** Abre comentário, igual ao bash (o `(` é metacaractere; `(#x\ngit push)` executa o push no bash, e o hook o lê). Correto manter no conjunto.
5. **`instream.seek`.** O `shlex` recebe a linha como `str`, então `instream` é um `StringIO` e o `seek` é seguro. O salto só ocorre entre fichas (logo depois de um `get_token`, com `token` vazio e estado `' '`), e o `_pushback_chars.clear()` descarta só o caractere já coberto pelo salto (caso `ls;#nota`, que o teste cobre). O uso de atributo privado do `shlex` já existia (`_pushback_chars` em `posicao`), não é dependência nova.
6. **Duas fixtures existentes trocaram o motivo da recusa** (`nao-modelado-cerquilha-no-meio-push-main-dev-bloqueia`, `nao-modelado-comentario-push-main-dev-bloqueia`: de "não modela" para R-MAIN, código 2 nos dois). Aceito: o resultado (recusa, código 2) não mudou, o motivo novo é mais forte e decorre justamente da correção (o push na main, antes escondido, agora é lido), e a cobertura do ADR 0011, item 2 foi preservada pelas duas gêmeas novas com push para `feature/x` (`nao-modelado-*-push-dev-bloqueia`), que seguem recusando por "não modela". `construcao_nao_modelada` não foi tocada. As descrições das fixtures alteradas explicam a troca e apontam a gêmea.
7. **Testes.** O teste novo `test_cerquilha_so_abre_comentario_no_inicio_de_palavra` cobre 15 casos (colado, início de palavra depois de espaço, `;`, `&&`, `|`, linha só de comentário, quebra de linha, apóstrofo dentro do comentário, `\ #`, `"#"`, `$#`, `$(…)#`, `>#`, `\r#`). Falha na base (item 2) e passa na entrega.
8. **Regras.** Nada afrouxa controle (endurece um existente); sem custo (R-CUSTO); nada específico de projeto (R-NEUTRO); `invariantes` não tocados.
9. **Commits.** Dois commits, Conventional Commits em português, um para o código e os testes e outro para o changelog.
