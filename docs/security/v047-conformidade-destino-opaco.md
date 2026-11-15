---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 000cd0c8a7f69497fd41b5f64c786ed9df5f5274
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação da volta do contexto aritmético)

Revalidação por delta (`forge-check parecer delta`), intervalo `19df94ed..000cd0c8`. No domínio: `hooks/conformidade.py` (`CONTEXTO_ARITMETICO`, `INDICE_LITERAL`, `LE_INDICE`, `linha_juntada` e o `f ( )` em `linha_conhecida`; `linha_juntada` em `valor_calculado`), `docs/hooks.md` e as fixtures `opaco-u4-v-*` novas. Fora do domínio: mutantes 20 e 21, `tests/test_hook_destino_opaco.py`, `docs/hooks-fixtures.md` e o fragmento. Etapa E1.328, instância que não fez a entrega. Parecer anterior: `19df94ed`, reprovado (A10 bloqueante, A11 e A5 recomendados).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A12 (bloqueante) hooks/conformidade.py:1706 · Contexto aritmético no corpo de heredoc sem aspas de um embutido (`: <<E` com `$[PATH=5]`, `${x[PATH=5]}` ou `${x:PATH=5}`) passa: `linha_conhecida` lê o texto sem os corpos, e o bash os expande no próprio processo; grava .git/config com rc 0 (R-CONFORMIDADE)
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1459 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S39 · mkdir -p 5; install -m 755 s 5/date; : <<E\n$[PATH=5]\nE\necho a > "$(date)" (\n é quebra de linha; s imprime .git/config) · espera: 2 · obtido: 0
- S40 · mkdir -p 5; install -m 755 s 5/date; : <<E\n${x[PATH=5]}\nE\necho a > "$(date)" · espera: 2 · obtido: 0
- S41 · mkdir -p 5; install -m 755 s 5/date; x=1; true <<E\n${x:PATH=5}\nE\necho a > "$(date)" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: `tests/test_oraculo_v047.py` como biblioteca (`montar`, `ambiente`, `LANCADOR`), sem editá-lo, num script no meu rascunho, com o arquivo `s` (executável que imprime `.git/config`) a mais no repositório do caso. Para cada linha: o rc do hook no head `000cd0c8` (papel `forge:tech-lead`, projeto em `melhoria/x`) e a própria linha rodada pelo bash (`--norc --noprofile`) numa cópia do repositório; "espera: 2" é o bash ter gravado `a` em `.git/config`, o que aconteceu nas três.

**A10 · fechada.** S31 a S38 dão 2 no head. Gerador no rascunho: 47 formas de contexto aritmético (`$((`, `$[`, `((`, índice de atribuição e de expansão, `+=`, deslocamento e tamanho, `test -v` e `[ -v` com e sem aspas, índice por variável, `f ( )`, corpo de função, crase e `$(…)`, barra mais quebra no meio) × 7 atribuições (`PATH=5`, `PATH+=5`, `PATH++`, `BASH_CMDS[date]=7`, vírgula, parênteses, espaços), mais 9 formas de descritor nomeado (`{PATH}>`, `>|`, `<>`, `>&2`, `<&0`, `<<<`, dentro de função, `{BASH_CMDS[date]}>`): 329 linhas, 183 atribuem no bash e nenhuma passa em `linha_conhecida`. O `{v}&>` não é descritor nomeado no bash (vira `{v} &`), sem achado. Legítimos seguem 0: `x[0]=1`, `: ${x:-a}`, `x=abc; : ${x:2}`, todos com `echo a > "$(date)"`, e `echo a > "$(date +%F).log"`, `cp config "$(mktemp -d)"`.

**Barra mais quebra (A3 do QA) · a classe fecha.** O bash não junta `\` + quebra em três lugares: aspa simples, comentário e corpo de heredoc com delimitador entre aspas. Os dois primeiros recusam (`linha_juntada` devolve `None`). O terceiro testei com o delimitador terminado em barra (`cat <<"x=\\"`, corpo `x=\`, depois `PATH=5; echo a > "$(date)"`): a forma juntada esconde o `PATH=5` em `x=PATH=5` e `linha_conhecida` dela dá `True`, mas o hook confere também a forma escrita (`formas_que_o_shell_le`), onde `tirar_heredocs` tira o corpo e o `PATH=5` aparece: rc 2. Sem achado; vale como dimensão da matriz (posição: delimitador de heredoc com barra no fim).

**A12 · corpo de heredoc sem aspas (dimensão nova da matriz: posição "corpo de heredoc expandido pelo shell").**
- Evidência: `hooks/conformidade.py:1706` grava em `texto_da_linha` o comando depois de `tirar_heredocs`, e `:1702` chama `linha_conhecida(comando)` no mesmo texto; `CONTEXTO_ARITMETICO` (`:542-543`) nunca vê o corpo. O corpo com `$(` já recusa (`ValueError` de `tirar_heredocs`, HEREDOC-FURO-HOOK), por isso `$((PATH=5))` no corpo dá 2; `$[`, `${a[…]}` e `${x:…}` não têm `$(` e passam. Com comando externo (`cat <<E`) o bash expande o corpo no processo filho e o pai não muda (conferi: não grava); com embutido (`:`, `true`, `echo`, `printf`, `test`, todos em `COMANDOS_INOFENSIVOS`) a expansão é no próprio shell, e a atribuição vale para o `$(date)` seguinte.
- Caminho de ataque: o da A6 e da A10. Um agente de qualquer papel, levado por injeção, grava `s` com o Write e roda a S39 numa chamada só: o `date` da substituição vem de `./5/date`, imprime `.git/config`, e o destino grava `core.hooksPath` (derruba a `R-VERIFY`) ou `core.fsmonitor` (roda código em todo `git status`).
- Severidade: alta (contorno do portão que guarda o `.git`, sem privilégio). Bloqueante: o requisito do próprio delta (`docs/hooks.md`: "Também recusa o contexto aritmético em qualquer palavra") provado como não cumprido (`R-REVIEW`).
- Correção mínima: aplicar as buscas de texto de `linha_conhecida` (`CONTEXTO_ARITMETICO`, `PADRAO_QUE_ATRIBUI` e `EXPANSAO_QUE_ESCONDE`) também aos corpos de heredoc cujo delimitador não tem aspas nem barra, ou passar a ela o texto antes de `tirar_heredocs` só para essas buscas. Lista inteira do que a correção cobre no corpo: `$[`, `((`, `=(`, `${…[…]}` com índice que não é número, `@` nem `*`, `${…:…}` de deslocamento que não é só número, `${NOME:=v}`/`${NOME=v}` com nome fora de `NOME_INOFENSIVO`, `${!…}` e `${…@P}`. Fixtures que bloqueiam: S39, S40, S41. Legítimos que seguem: `: <<'E'` e `: <<"E"` com `$[PATH=5]` no corpo (o bash não expande), `cat <<E` com texto sem `$`. Mutante: tirar a busca nos corpos. Esforço: P. Dono: tech-lead (autor do lote B).
- Fora: `${PATH:=5}` no corpo (o `PATH` já tem valor; com `PATH` vazio o caso cai na mesma correção, pelo `PADRAO_QUE_ATRIBUI`).

**A11 · sem mudança (recomendado).** Como no parecer anterior: sobra recusa, nunca falta, e o falso positivo está declarado em `docs/hooks.md`.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha da evidência acompanhou o deslocamento do arquivo.

### O que foi conferido e está correto
- **Sem afrouxar:** o delta só acrescenta recusas a `linha_conhecida`; `valor_calculado` passou a recusar quando `linha_juntada` devolve `None`. O `f ( )` lido como `f()` só faz o corpo da função passar pela lista, sem liberar nada a mais.
- **Falha fechada:** `linha_juntada` com `None` em `valor_calculado` cai no `barrar`.
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log 19df94ed..000cd0c8 -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_oraculo_v047 tests.test_hook_destino_opaco` deu 7 testes OK em 112 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"). Rodei o oráculo, os testes do destino opaco, o gerador e as sondas, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
