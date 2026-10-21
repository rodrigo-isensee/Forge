---
tipo: revisao-seguranca
contrato: 1
pedido: conformidade-leitura
branch: melhoria/conformidade-leitura
commit: f6cd7ae74ab4389fedbb4d440d3673a5e9baed1c
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: conformidade-leitura

Escopo: `git diff f911dfa0b2ebd9692d45c374f9ff4bab8523ed6b f6cd7ae74ab4389fedbb4d440d3673a5e9baed1c` (hooks/conformidade.py, 13 fixtures `tests/hooks/conformidade/leitura-*.json`, fragmento `changelog.d/conformidade-leitura.md`), contra a decisão M1 do dono (registrada no pedido) e o cartão GREP-OPCOES-EXEC.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega estreita o alcance de um bloqueio do hook `conformidade` (F6, `R-CONFORMIDADE`).

## Achados
- A1 (bloqueante) hooks/conformidade.py:179 · so_leitura confia em comandos(), cujo shlex lê # colado à palavra como comentário (o bash não): `grep x f#; forge sugerir --fila` passa o hook (rc 0) e o bash roda o forge; na base f911dfa recusa. Correção: recusar # em so_leitura, com fixture.

## Detalhe dos achados
**A1.** Evidência: `hooks/conformidade.py:179` (`so_leitura` só exclui `$`, crase e quebra de linha antes de chamar `comandos()`); a divisão vem de `fichas()` em `hooks/_comum.py:223`, `shlex.shlex(posix=True)` com o `commenters` padrão (`#`). O `shlex` corta a linha no primeiro `#`, mesmo no meio de uma palavra; o bash só abre comentário com `#` no início de palavra (`bash -c 'echo a#; echo b'` imprime `a#` e `b`). Resultado: para `grep x f#; forge sugerir --fila`, `comandos()` devolve um segmento só (`grep x f`), `so_leitura` responde verdadeiro e a F6 é pulada; o bash executa `grep x f#` e depois `forge sugerir --fila`. Sonda ponta a ponta numa cópia em `$TMPDIR` (o executor de fixtures do `tests/test_hooks.py` com fixtures extras, sem tocar a worktree): no commit revisado, `grep x f#; forge sugerir --fila`, `cat README.md#;forge sugerir --fila` e uma variante com `#&&` saem com código 0; na base `f911dfa` as três saem com código 2 e a mensagem da F6. Caminho de ataque: o agente (ou um texto injetado no contexto dele) monta a linha com um leitor na frente e `#` colado, e envia a sugestão no lugar do usuário, o que a F6 existe para impedir; nenhuma fixture de ofuscação pega o caso. Severidade: alta (contorna por inteiro o controle que a decisão M1 mandou preservar; a decisão só libera linha em que todos os segmentos são de leitura, e aqui há um segmento que não é). Correção mínima: em `so_leitura`, recusar a linha com `#` (por exemplo, `[$`\n#]` na regex da linha 179) e uma fixture `leitura-cerquilha-colada-bloqueia.json` com `grep x f#; forge sugerir --fila` esperando código 2. Esforço: P. Dono: `tech-lead` (autor da E1.1).

**Recomendações (não bloqueiam):**
- R1. `hooks/conformidade.py:179`: `>&2`, `2>&1` e `<<<` passam em `so_leitura` (não são destino de arquivo em `comandos()`). Não executam nada nem gravam arquivo, então não há caminho de ataque; mas a decisão M1 diz sem redirecionamento, e recusar qualquer `<`/`>` na linha deixaria a letra igual à decisão. Dono: `tech-lead`.
- R2. Argumento com glob (`grep -rn forge docs/*.md`, agora liberado) pode expandir para nome de arquivo com forma de opção (`--pre=...` no `rg`). Não é capacidade nova: a mesma linha sem a palavra `forge` nunca passou pela F6. Fica como nota para o M2/M3, se ampliarem a lista de leitores.
- R3. `git log|show|diff` aplicam `diff.external`/`textconv` da configuração do git; a configuração é protegida (ADR 0009) e o efeito não depende da F6. Sem ação.

Conferido e sem achado: `LEITORES_SEM_EXEC` deixa de fora `source`, `.`, `less`, `more`, `bat` e `xxd`; opções longas só por nome exato (abreviações como `--pr`, `--fil` recusam); `--pre`, `--pre-glob`, `--hostname-bin`, `-z`/`--search-zip`, `--filter`, `--ext-diff`, `--textconv`, `--output`, `--exec`, `--no-index` e `+cmd` recusam; atribuição de variável antes do programa (`GIT_EXTERNAL_DIFF=`, `PAGER=`), `git -c`, `git -C`, `command`, `exec`, `time`, `xargs`, `bash -c`, subshell, chaves, `<(...)`, `>(...)`, extglob, `\r`, `\v`, `\f`, NBSP e NUL como separador recusam ou não executam; `\;` escapado é literal nos dois lados. Nenhuma fixture existente foi removida nem alterada (o diff só acrescenta arquivos em `tests/`). As 13 fixtures novas passam. A exceção só pula a F6: as demais checagens da linha continuam rodando.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais em cópia (`git archive` em `$TMPDIR`). `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `shellcheck` não estão no PATH (lacuna; a entrega não toca dependência, workflow nem segredo).

Fora do delta, para o Jarvis levar ao dono: a mesma divergência do `#` em `fichas()` (`hooks/_comum.py:223`) é anterior a esta entrega e esconde de todas as checagens o que vem depois do `#` colado; na base, `echo a#; git push --force origin main` sai do hook com código 0, enquanto `git push --force origin main` sozinho é recusado por `R-VERIFY`. Pede um cartão próprio (correção no analisador comum, com fixtures), fora deste PR.
