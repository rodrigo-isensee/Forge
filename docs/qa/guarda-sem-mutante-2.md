---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 729135968bf674a758e5fd8b88798c7ab0673c02
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 3
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante-2 (PR 2: shell, isentas, tetos de T7, A5 e o PQ no gerar_volta), volta 3

Base `ff3936ae4011a95f25c37280fe32e4fa5ced0d95`, head `729135968bf674a758e5fd8b88798c7ab0673c02` (delta `6b0c95e..7291359`: corte grosso do shell, decisão do dono de 2026-10-28 14:03). Controle do Forge (`bin/`): a conferência de mutantes vale. Em paralelo com o review e a segurança. Substitui o parecer da volta 2 (commit 6b0c95e, reprovado: A1). O QA A1 da volta 2 e as sondas dos dois pareceres fecharam; o corte grosso abriu três regressões novas, as mesmas que o review 930e596 achou e que reproduzi de forma independente.

## Achados
- A1 (bloqueante) bin/forge-mutante:404 · classe mascara-do-shell-esconde-codigo, requisito de 14:03: `strip()` fecha o heredoc em `  EOF` ou `EOF `; o apóstrofo do resto do corpo esconde o `if` seguinte, rc 0 (rc 1 em 6b0c95e); fechar só na linha exata, com subcaso e mutante
- A2 (bloqueante) bin/forge-mutante:447 · classe mascara-do-shell-esconde-codigo, requisito de 14:03: apagar a linha incerta antes de mascarar desfaz o par da aspa que ela abre e esconde o `if` seguinte (`eval "echo a`/`b"`, `bash -c 'echo a`/`'`); mascarar antes de apagar, com subcaso
- A3 (bloqueante) bin/forge-mutante:413 · classe mascara-do-shell-esconde-codigo, requisito de 14:03: com `((` ou `$[` na linha, `sobra` é falso e `<<"$f"` não abre região; o corpo vira código e esconde o `if` seguinte; contar só o `<<` fora de `$(( ))`, ou marcar o resto incerto, com subcaso
- A4 (recomendado) bin/forge-mutante:19 · `x="$(if ...)"`, `trap '...'`, `source <(...)` e `... | sh` seguem fora do `não coberto`; declarar no docstring ou somar `$(` e a crase à `LINHA_INCERTA_SH`

## Detalhe dos achados
Sondas em memória (`condicoes_sh`, `python3 -I`), todas com `if [ -d / ]; then exit 1; fi` depois da região e `echo 'y'` no fim; nenhuma lê a condição nem a marca incerta (só a aspa solta do fim):
- A1: `cat <<EOF`/`x`/`  EOF`/`it's`/`EOF`/`if ...` e a variante `EOF ` (com espaço).
- A2: `eval "echo a`/`b"`/`if ...` e `bash -c 'echo a`/`'`/`if ...`.
- A3: `f=X; (( 1 )) && cat <<"$f"`/`it's`/`if ...`.
Em 6b0c95e as de A1 e A2 saíam rc 1 (regressão do corte grosso). Coincidem com os achados do review 930e596; reproduzi de forma independente. Severidade média (a checagem deixa passar condição sem mutante; não há perda de dados). Registro: `docs/qa/bugs/guarda-sem-mutante-2-mascara-do-shell.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão 14:03: linha com `<<`, `eval`, `-c`, `$((`, `$[` ou `\` no fim sai `não coberto: arq:L` | `test_shell_que_nao_se_le_com_certeza_sai_nao_coberto_...` (ponta a ponta) e `test_shell_por_regex_...` | heredoc (recuado, `<<-`, sem fecho), `eval`/`-c` em qualquer forma, aritmética multilinha, continuação, `<<<` e `<<` de deslocamento que não abrem região | falhou em três formas (A1, A2, A3) |
| QA A1 da volta 2: `-c` com continuação e com opções depois | subcasos `bash -c \` + quebra, `bash -c -e "..."`, e sondas a1, a2, b, b2 | `\`+quebra e outra opção entre `-c` e a aspa | passou: `não coberto` (incertas `(1,2)` e `(1,1)`), sem condição lida |
| Sondas dos dois pareceres (QA A2 heredoc com `$(...)` e crase, A4 `eval $"..."` e `eval "$(cmd)" '...'`) | sondas A2, A2 crase, A4, A4b e subcasos `eval $"` e heredoc com `$(` | corpo de heredoc, string de locale, concatenação | passou: `não coberto` até o fim da região, nenhuma condição lida |
| Specs -12, -13, -16, -17 | `forge-mutante` | cada guarda nova do varredor | passou: 20 `morreu`, 0 sobrevivente |
| `--cobertura` sobre o diff | `forge-mutante --cobertura --base ff3936a` | toda condição mudada tem mutante | passou: rc 0, só `coberta`/`spec editada`, nenhuma `sem mutante`, `apagada` ou `não coberto` |
| Teste de tempo em CPU (volta 2, A3 recomendado) | `test_shell_de_40_kb_sem_fecho_gasta_pouca_cpu` | 40 KB sem fecho | passou na suíte do item |

## Execução (real)
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 126 tests in 60.549s ... OK`. A suíte completa fica com o pre-push.
- `bin/forge-mutante tests/mutantes/guarda-sem-mutante-12.json ... -13 ... -16 ... -17`: rc 0, M75 a M111 (20 mutantes) `morreu`, 0 sobrevivente (M100 a M111 das specs -16 e -17, M75 a M82 e M84 a M86 das specs -12 e -13).
- `bin/forge-mutante --cobertura --base ff3936ae4011a95f25c37280fe32e4fa5ced0d95`: rc 0 (`rev=729135968bf6`), nenhuma linha `sem mutante`, `apagada` ou `não coberto`.
- Minhas sondas da primeira rodada não tinham apóstrofo depois do fecho recuado nem aspa aberta em linha incerta, e por isso passaram; as sondas do review as pegam e as reproduzi (`s1`, `s2`, `s5`, `s6`, `s7`: nenhuma condição lida, rc 0 pela checagem).
- Conferência da lista de mutantes contra o diff: as guardas mudadas na volta (`if pendentes`, `== pendentes[0]`, `continua or prof or LINHA_INCERTA_SH`, `continua =`, `$[` no `prof`, `["\0"] * sobra`, `"((" not in linha`, `\beval`, `trechos[-1][1] == i`, `linha if prof else`, `j >= 0`, `if i in fora`) têm mutante em M100 a M111. As alternativas da regex `LINHA_INCERTA_SH` sem mutante declarado (`-\w*c`, `\$\(\(`, `\$\[`, `\\\s*$`, `<<`) eu mutei à parte, com spec minha em `$TMPDIR` (Q1 a Q5, nos dois testes do shell): os cinco `morreu`. Q6 (`[A-Z]` na palavra do heredoc) sobreviveu por ser equivalente (a palavra minúscula cai em `sobra` e a região sai incerta, só mais conservadora); Q7 (`linha if True else`, a contagem de `((` fora de `$((` ) sobreviveu por ser conservador (só deixa mais linhas incertas, nunca esconde). Sem achado.
- Vermelho: `forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_forge_mutante,test_volta_por_delta` (rc 0): `contagem: não prova (passa na base)=113; prova (API ausente)=3; prova (asserção)=10`; nenhum teste cai no HEAD.
- Sondas da volta 2 (`condicoes_sh` com `incertas`, `python3 -I`): `bash -c \`+quebra, `-- '...'`, `sh -c -e`, `bash -c -x --`, `sh -ec`, `-c` depois de pipe, `find -exec sh -c`, `eval \`+quebra, `eval $"..."`, `eval "$(cmd)" '...'`, `eval "..."'...'`, heredoc com `$(` e com crase, `sh -s <<'E'`: todas sem condição lida e com `incertas` apontando a linha ou a região. Controles: `if [ -f /etc/x ]` comum e `<<<` seguem lidos.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Recomendações (não devolvem)
- Texto executado por outros caminhos fora da lista da decisão 14:03 segue sem marca: `trap '...' EXIT`, `source <(echo '...')`, `echo '...' | sh`; a condição fica dentro de aspas mascaradas. Hoje nada disso passa por `--cobertura` como `não coberto`. Declarar no docstring ou somar ao corte grosso numa próxima volta (`bin/forge-mutante:19`).
- Achados recorrentes (PA-7): a classe `mascara-do-shell-esconde-codigo` voltou pela 5ª vez no pedido (A1 a A3 acima); a linha AR é do review (decisão técnica 2026-10-28 12:52), este parecer não grava AR.

## Casos de abuso e riscos aceitos
A3 e A4 da segurança do PR 1 ficam como risco aceito (decisão técnica 2026-10-28 10:25). Nada do diff é executado: a checagem lê `git show` e só faz `ast.parse` e regex. As sondas rodaram em memória sobre texto, em `$TMPDIR`; nenhum texto das sondas foi executado.
