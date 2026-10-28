---
tipo: review
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 43a8cc83559f3e49abffa08447b4bfaf4a04ae6c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 2 (shell, isentas, tetos de T7, A5 e o PQ no `gerar_volta`)

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...43a8cc83559f3e49abffa08447b4bfaf4a04ae6c` (6 commits). Referências: a ata `docs/alinhamentos/2026-10-28-revisao-desenho-guarda-sem-mutante.md` (decisões 1 a 5 e a linha do PR 2), o desenho `docs/propostas/guarda-sem-mutante-desenho.md` (item b4, que a ata mantém "salvo o abaixo"), ambos em `~/.forge-contrib/docs/`, e as decisões técnicas de 09:23, 10:25 e 10:56. Primeira rodada, sem delta.

## Achados
- A1 (bloqueante) bin/forge-mutante:90 · falso negativo: o `#` precedido de `#`, `%`, `/` ou `-` dentro de `${...}` sem aspas vira comentário e mascara o resto da linha; `x=${a##*/}; if [ -n "$x" ]; then exit 1; fi` novo sai rc 0, sem linha
- A2 (bloqueante) bin/forge-mutante:398 · requisito da decisão 1 da ata: `cmd || true  # sem erro` conta como condição (o lado direito é lido do texto original, com o comentário), sai `sem mutante` e rc 1; o `||` só com `true` ou `:` não conta
- A3 (bloqueante) bin/forge-mutante:91 · requisito do desenho (b4, mantido pela ata): falta `until`; `until grep -q pronto log; do sleep 1; done` novo sai rc 0, sem linha; incluir `until` na regex e no docstring
- A4 (recomendado) bin/forge-mutante:455 · `parecidas` é sempre verdadeira entre condições de shell com `if`, `elif` ou `while` (a palavra-chave é comum aos dois) e, em Python, com `None`, `self`, `0` ou `1`; o A5 da segurança segue aberto nesses casos. Não devolve
- A5 (recomendado) bin/forge-mutante:91 · `\[\[[^\n]*?\]\]` e `\[\s[^\n]*?\s\]` são quadráticas numa linha longa sem fecho: 160 KB de `[ a ` levam 33 s de CPU, e o teto é 1 MiB por arquivo (T7, travamento). Cartão para a segurança. Não devolve
- A6 (recomendado) bin/forge-mutante:260 · o `motivo` da isenta aceita quebra de linha e sai cru em `isenta · arq:L · motivo`, o que permite forjar uma linha `coberta` na saída (mesma classe do A4 da segurança do PR 1). Cartão para a segurança. Não devolve
- A7 (recomendado) bin/forge-mutante:90 · `\'` fora de aspas abre uma aspa simples e mascara o resto da linha (falso negativo raro). Declarar no docstring, junto com `case` e `(( ))`, que ficam fora. Não devolve
- A8 (recomendado) bin/forge-mutante:538 · o comentário "binário ou fora do UTF-8 também: só não coberto" ficou velho: `.sh` fora do UTF-8 agora dá rc 2 em `fonte()`, o que fecha a falha e está certo. Não devolve

## O que foi conferido
- **Regex de shell (A1 a A3, A5, A7).** Fiz sondas com `condicoes_sh` e de ponta a ponta com `--cobertura` num repositório descartável. Saem certos: `if !`, `[ "$a" = "b" ]`, `&& b || c`, `|| exit 1`, `|| { ...`, `${#a}`, `$#`, `mytest`, `--test` e `/usr/bin/test`. O texto entre aspas e o comentário comum também saem certos. O heredoc (`if you want`) dá falso positivo; o desenho já o previa e ele fica do lado seguro. No repositório de hoje não há ocorrência dos padrões de A1 e A2 nos 16 arquivos de shell (`bin/forge:18` tem `${f##*/forge-}`, mas entre aspas). Mesmo assim o defeito está provado e é a classe que a checagem existe para fechar. A2 também conta para o critério de reversão do dono (3 falsos positivos).
- **Isentas (decisão 4).** As travas estão todas presentes e cada uma tem teste: `arquivo` com `trecho` exato, 8 ou mais não brancos e o trecho todo dentro do nó; `motivo` com 20 ou mais caracteres depois do `strip`; teto de 8 somadas na execução, além de 8 por spec; a isenta que não cruza condição listada, que cruza uma condição já coberta, que casa duas vezes ou que fica fora do nó dá rc 2 (`soltas`). A isenta de condição apagada casa uma vez no merge-base, e a perda de validade com a linha mudada sai pelo mesmo `soltas`. Vale o A6.
- **Critério nome ou número em comum (A5).** O pareamento por posição no hunk (`zip` das velhas em falta com as novas mudadas) mais `parecidas` resolve o caso do A5 da segurança em Python, com o teste `test_condicao_apagada_e_outra_nova_sem_relacao...`. O critério é mais estrito que a decisão de 09:23, que pede só a posição, e erra para o lado do falso positivo, o lado seguro. O limite está em A4. Outro efeito do pareamento por índice: uma velha apagada antes de uma editada desloca o par, e a editada também sai `apagada`. É falso positivo e fica no lado seguro.
- **Specs antigas reescritas.** Montei uma spec temporária só com M8, M22, M33, M35, M37, M46 e M47, que é a rodada do autor restrita a elas, e todos morreram, rc 0: `M8 · morreu · bin/forge-mutante:477`, `M22 :538`, `M33 :433`, `M35 :475`, `M37 :538`, `M46 :473`, `M47 :473`. As guardas continuam as mesmas. M46 e M47 passaram a cair no teste novo do A5, que exercita o par por hunk. A rodada completa das specs é do QA.
- **Commit único a1c333f.** Aceito. Shell, isentas, tetos e A5 mudam as mesmas `analisar` e `cobertura`, e o commit traz o código com os testes (os testes passam nele). As specs ajustadas vêm em 562d0f0 e 7458ae8. A mensagem lista as quatro partes.
- **skills/qa-testing/SKILL.md:88.** Atualizado: "condição Python ou shell" e as isentas. Bate com o docstring.
- **PQ no `gerar_volta`.** `PQ-{proximo + len(pronto)}` numera certo com e sem o PQ de merge, e os dois casos têm teste em `tests/test_volta_por_delta.py`. O PQ leva o `sha_base` fixo, como no desenho (f).
- **Tetos de T7.** 4 MiB de diff somado e 5000 condições por arquivo dão rc 2, com teste. A conferência do diff acontece depois de ler o corpo de cada arquivo, e o teto de 300 arquivos continua depois do laço (A3 do PR 1, recomendado e ainda aberto).
- **Riscos aceitos (decisão de 10:25):** A3 da segurança do PR 1 (troca de condições entre si com o multiconjunto igual dá rc 0) e A4 (nome de arquivo com quebra de linha sai cru).

Teto M14: `bin/forge-check` 1 + `bin/forge-mutante` 157 + `tests/test_forge_mutante.py` 114 + `tests/test_volta_por_delta.py` 2 = 274 linhas (`git diff --numstat --no-renames origin/develop...HEAD`), dentro do teto de 400. Nenhum arquivo de `hooks/` nem de `PROTEGIDOS` foi alterado. Ficam fora da conta as specs, o `changelog.d/` e o `.md`.

Citado, sem refazer: `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 124 tests ... OK`. `bin/forge-mutante --cobertura --base ff3936a` no head: rc 0, com 22 linhas `coberta` e 5 `spec editada`, e nenhuma `sem mutante`, `apagada` ou `isenta`. Segurança e QA têm parecer próprio, em paralelo.

Fragmento `changelog.d/guarda-sem-mutante-2.md` presente; `R-NEUTRO` e `R-CUSTO` sem achado (nada de projeto, nada pago).

Achados recorrentes (PA-7): conferi `docs/engineering/achados-recorrentes.md`, que está vazio. Não entra linha nova: A1 a A3 são de classe nova neste pedido.

Entregar da volta: A1, A2 e A3, cada um com um teste que falha antes da correção (um subcaso em `test_shell_por_regex...` basta) e o mutante da guarda nova. As correções são pequenas: tirar `#` do comentário quando ele está dentro de `${...}`, ler o lado direito do `||` do texto mascarado e somar `until`.
