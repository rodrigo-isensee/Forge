---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 6b0c95eadd0ab215de40630d9734318a1c33889a
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante-2 (PR 2: shell, isentas, tetos de T7, A5 e o PQ no gerar_volta), volta 2

Base `ff3936ae4011a95f25c37280fe32e4fa5ced0d95`, head `6b0c95eadd0ab215de40630d9734318a1c33889a` (delta `a157116..6b0c95e`). Controle do Forge (`bin/`): a conferência de mutantes vale. Em paralelo com o review e a segurança. Substitui o parecer da volta 1 (commit 8ae2bd2, reprovado).

## Achados
- A1 (bloqueante) bin/forge-mutante:95 · requisito da decisão de 12:01 ("`eval` ou `-c` em qualquer forma"): o texto executado por `-c` ou `eval` ainda sai rc 0, sem `não coberto`, em formas reais do shell; classe `mascara-do-shell-esconde-codigo` ("execução de texto não analisado passa calada", 4ª vez no pedido). Sondas ponta a ponta com `--cobertura` (condição nova `[ -f /etc/x ] && exit 1`, e o `bash` executa cada uma): (a) `bash -c \` + quebra + `  '...'` (continuação de linha) e `bash -c  \` + `-- '...'`; (b) `sh -c -e '...'` e `bash -c -x -- '...'` (outra opção depois do `-c`). `EXECUTA_SH` exige o `-c`/`eval` (com `--` opcional) colado à aspa, na janela de 30 caracteres, sem `\` nem outra opção entre os dois. Correção: tratar como incerta a aspa que vem depois de `-c`/`eval` na mesma instrução (até `;`, `&`, `|` ou quebra sem `\`), com opções e `\`+quebra no meio, e um subcaso de cada em `test_shell_que_nao_se_le_com_certeza...` com o mutante da guarda nova
- A2 (recomendado) bin/forge-mutante:424 · o corpo de heredoc sem aspas no terminador executa `$(...)` e crase, e a máscara o esconde calada: `cat <<EOF` / `$(if [ -f /etc/x ]; then exit 1; fi)` / `EOF` sai rc 0 só com a condição de fora listada. Não está no docstring nem na decisão de 12:01; declarar no docstring ou tratar `$(`/crase no corpo como incerto
- A3 (recomendado) tests/test_forge_mutante.py:561 · o limite de 0,1 s do teste de tempo tem folga de 1,3x na máquina do QA: com 4 processos em paralelo (40 medidas por unidade) o p95 de `"\"` foi 0,075 s e o máximo 0,078 s (0,076 com 8 em paralelo); 2x o p95 pedido pela decisão de 12:01 daria 0,15 s. Hoje passa (60 de 60 com 4 laços paralelos de 15), mas uma máquina mais lenta ou o CI pode cruzar 0,1 s; subir para 0,15 s ainda fica longe dos 9 s da versão quadrática
- A4 (recomendado) bin/forge-mutante:19 · `eval $"..."` (string de locale) e `eval "$(cmd)" '...'` seguem fora do `não coberto`; mesmo remédio do A1

## Revalidação dos achados da volta anterior
| Achado | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| QA A1 (volta 1): teste de tempo instável | `test_shell_de_40_kb_sem_fecho_gasta_pouca_cpu` (limite 0,1 s) | CPU de 40 KB sem fecho, três unidades | passou: 4 laços paralelos de 15 execuções, 60 de 60 (antes 43 de 60 falhavam); ver A3 |
| Review A1: terminador recuado fecha o heredoc antes do shell | sonda h1 (`  EOF` e `it's` depois) e subcaso no teste | terminador exato no `<<` | passou: `não coberto: run.sh:3` e a condição seguinte sai `sem mutante` (rc 1) |
| Review A1: `<<-` | sonda h3 e subcaso | `<<-` com tabs e com `EOF` sem tab | passou: `não coberto` até o fim da região, rc 1 pela condição depois |
| Review A1(b): `<<` dentro de `$(( ))` | sondas h2, h10, h11, h12 | `$((1<<EOF))`, `$(( 1 << 2 ))` com heredoc real depois, `$(( (1) ))` | passou: a condição aparece `sem mutante`, heredoc real mascarado |
| Review A2: `eval $'...'` e `bash -c -- '...'` | sondas e1, e2, e13 | `$'`, `--` | passou: `não coberto: run.sh:3` |
| Heredoc legítimo: `<<"E"`, `<<\E`, `<<E >f`, dois heredocs na linha, CRLF | sondas h4 a h9, h13, h6 | forma do terminador | passou (CRLF sai `não coberto`, conservador) |
| `-c`/`eval` em outras formas | sondas e3 a e9, e11, e12, e20, e22, e24 | `-ec`, `-lc`, `eval  `, `--norc -c`, `--login -c`, `xargs ... sh -c`, aspas duplas | passou (`não coberto`) |
| `-c`/`eval` com continuação de linha ou outra opção depois | sondas e16, e17, e19, e23 | `\`+quebra, `-c -e`, `-c -x --` | **falhou** (A1) |

## Execução (real)
- 15 specs (`bin/forge-mutante tests/mutantes/guarda-sem-mutante*.json`, M1 a M99): rc 0, 99 `morreu`, 0 sobrevivente, 73 s. (O brief diz 14; a pasta tem 15: a base sem sufixo mais `-2` a `-15`.)
- `bin/forge-mutante --cobertura --base ff3936ae4011a95f25c37280fe32e4fa5ced0d95` sobre o próprio diff: rc 0, 38 `coberta ... declarado, não provado`, 5 `spec editada`, nenhuma `sem mutante`, `apagada` ou `não coberto`. Lista conferida contra o diff: cada linha de guarda mudada na volta (`prof > 0`, `(0 if quebra else prof)`, `- linha.count("))")`, `tabs if m[0].startswith("<<-")`, `<<-` ou `k == len(achadas)`, `r[j] <= fecha`, `m[0][0] in "'\"$"`, `(?:\s+--)?`, `linha == linha.strip()`, `k < len(achadas)`) tem mutante nas specs -13 a -15 (M83 a M99); o diff de `bin/forge-check` é uma linha que não é condição.
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: `Ran 126 tests ... OK` (46 s). A suíte completa fica com o pre-push.
- Teste de tempo em CPU, de novo com 4 processos em paralelo: 40 medidas por unidade; `"\"` max 0,078 s e p95 0,075 s; `[[ ` e `[ ` max 0,020 s. O próprio teste, 4 laços de 15: 15, 15, 15 e 15 passaram. Com 8 em paralelo: p95 0,076 s.
- Vermelho, `forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_forge_mutante,test_volta_por_delta` (rc 0): abre com `vermelho: base=ff3936ae4011 head=6b0c95eadd0a`; `contagem: não prova (passa na base)=113; prova (API ausente)=3; prova (asserção)=10`. Dos subcasos novos da volta: com o `bin/forge-mutante` de `fc721f1` e os testes do HEAD, `test_shell_por_regex...` falha em `x=$((1<<EOF))` e `test_shell_que_nao_se_le_com_certeza...` falha em cinco subcasos (`cat <<EOF` recuado, `<<-EOF`, `cat <<EOF` sem fecho recuado, `eval $'...'`, `bash -c -- '...'`): 6 falhas, saída `FAILED (failures=6)`.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Recomendações (não devolvem)
- `case` e `(( ))` isolado seguem fora e declarados no docstring.
- Achados recorrentes (PA-7): a classe `mascara-do-shell-esconde-codigo` voltou no pedido (review 1f394b7 A1, segurança 53ff539 A1, review fc721f1 A1 e este A1). A linha `AR-1` em `docs/engineering/achados-recorrentes.md` é do review (commit a6f5184); este parecer não grava AR (decisão técnica 2026-10-28 12:52).

## Casos de abuso e riscos aceitos
A3 e A4 da segurança do PR 1 ficam como risco aceito (decisão técnica 2026-10-28 10:25). Nada do diff é executado: a checagem lê `git show` e só faz `ast.parse` e regex. As sondas rodaram em repositórios descartáveis em `$TMPDIR`; nenhum texto das sondas foi executado.
