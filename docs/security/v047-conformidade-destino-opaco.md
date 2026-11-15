---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 19df94ed5619ae0bb77dbdf5c9abde7d50f04635
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (lote B, destino opaco, revalidação do redesenho da lista fechada)

Revalidação por delta (`forge-check parecer delta`), intervalo `041c671b..19df94ed`. No domínio: `hooks/conformidade.py` (`linha_conhecida` e `COMANDOS_INOFENSIVOS` no lugar de `RESOLUCAO_TROCADA`, chamada em `na_lista_positiva`, `valores_do_corpo` e na troca de `$(pwd)`), `docs/hooks.md` e as fixtures `opaco-u4-*` novas. Fora do domínio: mutantes 17 a 19, `tests/test_hook_destino_opaco.py`, `docs/hooks-fixtures.md`, `achados-recorrentes.md` e o fragmento. Etapa E1.324, instância que não fez a entrega. Parecer anterior: `041c671b`, reprovado (A7 e A8 bloqueantes, A9 e A5 recomendados).

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A10 (bloqueante) hooks/conformidade.py:502 · Contexto aritmético atribui sem a forma NOME=: `x[PATH=5]=1`, `: ${x[PATH=0]}`, `: $[PATH=0]`, `x=12; : ${x:PATH=0}`, `test -v 'x[PATH=0]'` e `x[BASH_CMDS[date]=7]=1` trocam o `date` e gravam .git/config com rc 0 (R-CONFORMIDADE)
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `npm test 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1431 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S31 · mkdir 5; install -m 755 s 5/date; x[PATH=5]=1; echo a > "$(date)" (s: script que imprime .git/config) · espera: 2 · obtido: 0
- S32 · x[PATH=0]=1; echo a > "$(date)" (0/date executável que imprime .git/config) · espera: 2 · obtido: 0
- S33 · : ${x[PATH=0]}; echo a > "$(date)" · espera: 2 · obtido: 0
- S34 · : $[PATH=0]; echo a > "$(date)" · espera: 2 · obtido: 0
- S35 · x=12; : ${x:PATH=0}; echo a > "$(date)" · espera: 2 · obtido: 0
- S36 · test -v 'x[PATH=0]'; echo a > "$(date)" · espera: 2 · obtido: 0
- S37 · [ -v 'x[PATH=0]' ]; echo a > "$(date)" · espera: 2 · obtido: 0
- S38 · x[BASH_CMDS[date]=7]=1; echo a > "$(date)" (7: executável que imprime .git/config) · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: `tests/test_oraculo_v047.py` como biblioteca (`montar`, `rodar_hook`, `ambiente`), sem editá-lo, num script no meu rascunho, com arquivos a mais no repositório do caso (`s`, `7`, `0/date`, `f.sh`, `e.sh`, `d`, `bin/date`, `bin/echo`) e `config` com uma marca. Para cada linha: o rc do hook no head `19df94ed` (papel `forge:tech-lead`, projeto em `melhoria/x`) e a própria linha rodada pelo bash (`--norc --noprofile`) numa cópia do repositório; "espera: 2" é o bash ter gravado em `.git/config` (a marca ou `a`).

**A7, A8 e A9 · fechadas.** S17 a S30 do parecer anterior dão 2 no head (as catorze, também `P\ATH=./bin`), e os legítimos seguem 0: `echo a > "$(date)"`, `echo a > "$(date +%F).log"`, `cp config "$(mktemp -d)"`, `find . -name x > "$(mktemp)"`, `ls -la . > "$(date +%F).log"`. A troca da lista negativa pela lista fechada lida pelo `shlex` fecha as formas da palavra (aspas, barra, `$s`, `eval`, `declare`, `read`, `BASH_CMDS[…]=`). Conferi também que a função de nome entre aspas ou com barra (`'date'(){ …; }`) não é definida pelo bash (`not a valid identifier`): sem achado.

**A10 · contexto aritmético (dimensão nova da matriz: atribuição fora da forma `NOME=`).**
- Evidência: `hooks/conformidade.py:502` (`ATRIBUICAO`) só olha o nome antes do `[`, e o `[…]` de um vetor indexado é avaliado como aritmética, que atribui (`x[PATH=5]=1`). `PADRAO_QUE_ATRIBUI` (`:504`) só casa `${NOME:=`/`${NOME=`; `${x[PATH=0]}`, `${x:PATH=0}` (deslocamento) e `$[PATH=0]` passam como argumento de `:`, e `test -v`/`[ -v` avaliam o índice. `$((…))` já recusa, porque o corpo passa por `linha_conhecida`. A aritmética só grava número, mas `PATH=5` faz o bash procurar o `date` em `./5/`, e `BASH_CMDS[date]=7` aponta o `date` para `./7`.
- Caminho de ataque: o da A6. Um agente de qualquer papel, levado por injeção, grava com o Write o script `s` e roda a S31 numa chamada só (`mkdir`, `install` e a atribuição estão na lista): o `date` da substituição imprime `.git/config`, e o destino grava `core.hooksPath` (derruba a `R-VERIFY`) ou `core.fsmonitor` (roda código em todo `git status`).
- Severidade: alta (contorno do portão que guarda o `.git`, sem privilégio). Bloqueante: requisito do próprio delta (`docs/hooks.md`: "atribuições só de nome minúsculo"; "o que o hook não reconhece recusa") provado como não cumprido (`R-REVIEW`).
- Correção mínima (lista inteira; vale em `linha_conhecida` e, com isso, nos três pontos que a chamam): recusar a linha que tem (1) `$[`; (2) índice `[…]` em palavra de atribuição ou em `${nome[…]}` com algo além de dígitos, letras, `_`, `@` e `*`; (3) `${nome:` seguido de algo que não seja `-`, `=`, `+`, `?`, nem só dígitos, espaço e `-` até o `}` (deslocamento e tamanho são aritmética); (4) `test` ou `[` com argumento que traz `[`; (5) `let`, `((` e `$((` seguem recusando como hoje. Fixtures que bloqueiam: S31 a S38. Mutantes: tirar cada um dos itens 1 a 4. Legítimos que seguem: `x[0]=1; echo a > "$(date)"`, `: ${x:-a}; echo a > "$(date)"`, `: ${x:2}; echo a > "$(date)"`. Esforço: P. Dono: tech-lead (autor do lote B).
- Fora: `x[PATH++]=1` (o bash quebra o `PATH`, sem gravar) e `x[TMPDIR=0]=1` com `mktemp` (nome aleatório no diretório numérico; com `0` ligado ao `.git`, só sobra o resto `/../config` da A5).

**A11 · falso positivo da lista fechada (recomendado).** A lista recusa todo comando fora de `COMANDOS_INOFENSIVOS`, também o programa externo (`python3`, `npm`, `make`, `sed`) e o `cd` com destino literal, que são o caso comum de `cmd > "$(mktemp)"` (rc 2 nas três linhas do achado, `cd docs && echo a > "$(date +%F).log"` a terceira; o bash não grava no `.git`). Programa externo roda em processo filho e não troca função, alias, hash nem variável do shell; a troca de arquivo num diretório do `PATH` herdado já é o residual R1. Correção possível: a lista fechada vale só para os embutidos e palavras reservadas (`EMBUTIDOS_DO_BASH`), e o nome de programa passa quando é palavra simples (sem `$`, crase, `{`, `*`, `?`, `[`, `~`, `=` nem `/`, lido antes de tirar aspas, porque `'source'` vira o embutido). Esforço: P. Dono: tech-lead. Não bloqueia: sobra recusa, nunca falta, e o falso positivo está declarado em `docs/hooks.md`.

**A5 · sem mudança (recomendado, fora do lote).** Como no parecer anterior; cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`).

### O que foi conferido e está correto
- **Sem afrouxar:** `linha_conhecida` é mais estrita que a `RESOLUCAO_TROCADA` em todas as sondas antigas; o único ponto que liberou a mais foi o `.` como argumento (A9), sem caminho de troca de resolução.
- **Falha fechada:** aspa sem par (`ValueError`) devolve `False`; a recursão de `$(` aninhado estoura em `RecursionError`, que o tratador de `hooks/conformidade.py:3105` recusa.
- **Orçamento:** 64 KB de comandos em sequência em 0,05 s; 300 `$(` aninhados em 0,6 s; 8000 aninhados levam 48 s até o `RecursionError`, acima do prazo de 3 s da decisão (`PRAZO_DA_DECISAO_S`), que recusa a linha vigiada. Sem achado: a falha é fechada.
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log 041c671b..19df94ed -- tests/test_oraculo_v047.py` vazio). Local: `python3 -m unittest tests.test_oraculo_v047 tests.test_conformidade_opaco` deu 5 testes OK em 24 s; `tests.test_hook_destino_opaco` deu 4 OK em 18 s.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** (a branch não tem PR; o brief diz "sem PR"). Rodei o oráculo, os testes do destino opaco e as sondas, citados acima. Quando houver PR, o portão pede o CI verde no head da revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
