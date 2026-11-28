---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: c7a8ff72300365c64aa699e2301c2ca0c9e1b982
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 conformidade, destino opaco sem resto (A9, A10)

Lote B, classe C, `hooks/conformidade.py` (R-CONFORMIDADE), intervalo `origin/develop..e8c459de`. Não há especificação de UX: as obrigações são o oráculo `tests/test_oraculo_v047.py` (casos A9, A10 e os 9 desvios D2b da E1.170) e as fixtures e mutantes do autor. Sem tela, sem acessibilidade.

oraculo: tests/test_oraculo_v047.py commit 730843a99366f49e7560b32dbd413c15346f8614 blob 535134e940b2af9a3cf9941b7a4d54b661b57c4a

Prova de não edição do oráculo (conferida): `git merge-base --is-ancestor 730843a9 HEAD` ok; `git rev-parse HEAD:tests/test_oraculo_v047.py` = `535134e940b2af9a3cf9941b7a4d54b661b57c4a` (igual ao blob); `git log --format=%H 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio. Rodou `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK, 178 s (os 9 casos D2b e os `plano` da A10 recusados; leituras legítimas liberam).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A9: destino opaco sem resto cai no `.git` pela regra única | `OraculoV047DestinoOpaco.test_hook_concorda_com_o_bash`; `test_conformidade_opaco.test_hook_concorda_com_o_bash`; fixtures `opaco-semresto-*` | destino vazio, curinga, variável, substituição; teto de execuções | passou; vermelho na base |
| A10: operador colado no rev-parse recusa e a liberação de link não se alarga | oráculo (casos `plano`); fixtures `opaco-colado-*` (`;`, `&&`, `\|`, `eval`, `sh -c`, ANSI-C, aninhado) | corpo de 1 comando libera, de 2 recusa | passou; vermelho na base |
| D2b: aspas, concatenação, `${var}` e função (9 casos) | oráculo; `test_hook_destino_opaco.test_fixtures_opaco_d2b`; `opaco-d2b-*` | variável sozinha e sufixo liberam, vazia e duas variáveis recusam | passou; vermelho na base |
| Leituras legítimas continuam liberadas | `OraculoV047DestinoOpaco.test_leituras_legitimas_liberam`; fixtures `*-libera.json` | cat, date, mktemp, mv fora do `.git` | passou (não prova na base, é regressão, esperado) |
| Orçamento do oráculo (até 150 execuções, 10 com prazo de produção) | `test_orcamento_e_cobertura`; `test_gerador_cobre_as_dimensoes_dentro_do_orcamento` | teto de execuções | passou (não prova na base, é guarda) |

## Cenários e resultado real
- Vermelho antes do verde, `bin/forge-testes --vermelho f4b0c2aeb42b2c08d0d9a1386e77939504b790e8 --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, saída 0: `vermelho: base=f4b0c2aeb42b head=e8c459de79e9 ... revertidos à base: bin/forge-testes, changelog.d/v047-conformidade-destino-opaco.md, docs/hooks-fixtures.md, docs/hooks.md, hooks/conformidade.py`; `contagem: não prova (passa na base)=3; prova (asserção)=5`. Os 3 que passam na base são regressão de liberação e guardas de orçamento. A rodada de suíte completa (sem `--modulos`) estourou o meu prazo de espera sob carga 20 a 30 e não vale como veredito; vale a restrita.
- Mutação: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco*.json` (8 specs, 49 mutantes): 49 `morreu`, nenhum sobrevivente, rc=0. Cabeçalho `forge-mutante: pedido=v047 rev=e8c459de79e9 ...`.
- Cobertura de guardas: `bin/forge-mutante --cobertura --base f4b0c2aeb42b2c08d0d9a1386e77939504b790e8` rc=0, `base=f4b0c2aeb42b... mb=... rev=e8c459de...`; todas as condições mudadas `coberta`, 3 `isenta` com motivo lido (equivalentes pela seção 7 da ADR 0009 ou nome opaco da C18): aceitas.
- Diff conferido: o `test_testes_tocados` e o mapa de `bin/forge-testes` incluem os 2 módulos novos e descontam oráculos nas listas exatas (83); coerente com o oráculo ser incluído em todo plano dirigido.
- CI: `gh` não achou PR nem check-run `bateria` para `e8c459de` (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.

## Revalidação por delta e8c459de..e25f079b (E1.281)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, fixtures `opaco-u4-*` e `opaco-semresto-u3-*`, `tests/test_hook_destino_opaco.py`, `tests/test_conformidade_opaco.py` e os mutantes O83 a O98 (specs `v047-destino-opaco-9` a `-15`). Mudança: U4 (lista positiva do valor calculado: palavras do corpo por regex, crase depois do `of=` do dd). Escopo do plano inalterado (A9, A10, D2b); o delta soma o U4 como obrigação (A1 da segurança E1.206, A1 do review E1.205).
- Oráculo: prova de não edição refeita (ancestral ok; blob `535134e9…` igual; `git log 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio); `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK.
- Vermelho: `bin/forge-testes --vermelho e8c459de79e98bd22a65892b4605c97a7583de58 --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, saída 0: `vermelho: base=e8c459de79e9 head=e25f079b9834`, `revertidos à base: docs/hooks-fixtures.md, docs/hooks.md, …, hooks/conformidade.py`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`, `test_fixtures_opaco_sem_resto` e `test_hook_concorda_com_o_bash` também provam; `contagem: não prova (passa na base)=6; prova (asserção)=3` (regressão e guardas de orçamento, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 --base e8c459de79e98bd22a65892b4605c97a7583de58 tests/mutantes/v047-destino-opaco*.json`, cabeçalho `base=e8c459de79e9… mb=e8c459de79e9… rev=e25f079b9834`: 94 `morreu`, 1 `sobreviveu`: `O18 · sobreviveu · hooks/conformidade.py:1329`, rc=1. O mutante passava no e8c459de (49 de 49); o U4 do delta passou a recusar antes dele. Reproduzido à mão numa cópia: `test_fixtures_opaco_sem_resto` e `test_fixtures_opaco_u4` seguem OK com o mutante. A descrição da fixture `opaco-semresto-u3-variavel-duas-vezes-bloqueia` já diz que o U4 recusa antes do U3. Probável equivalente, mas o autor não o declarou (A1).
- Cobertura: `bin/forge-mutante --cobertura --base f4b0c2aeb42b…` rc=0, todas as condições `coberta`; 4 `isenta` com motivo lido (443, 586, 1316, 1330): aceitas, equivalentes pela seção 7 da ADR 0009 ou pelo U2.
- Fronteiras novas do U4 protegidas: crase partida no `of=` do dd (bloqueia e libera), `printf` com e sem `%s`, função recursiva ou redefinida, variável duas vezes ou do `read`, teto de 64 valores, `$(` sem par.
- CI: sem PR e sem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

## Revalidação por delta e25f079b..85043cc4 (E1.305)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, 20 fixtures `opaco-u4-*` e `opaco-semresto-u3-*`, `tests/test_hook_destino_opaco.py` (contagens 60 e 73) e as specs de mutantes `-7`, `-9` e `-16` (O99 a O104; O45 e O55 realinhados à assinatura nova). Mudança: `na_lista_positiva(corpo, linha)` recusa o comando que a linha redefine como função (U4, U3 e `$(pwd)`); `VARIAVEIS_DO_BASH` devolve None; O18 morto por fixture. O escopo do plano (A9, A10, D2b, U4) não mudou.
- Oráculo: prova de não edição refeita (commit 730843a9 ancestral; blob 535134e9 igual; log vazio); `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK, 29,8 s.
- Vermelho: `bin/forge-testes --vermelho e25f079b9834ba470ac8ccda65e5ad678a426aaa --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, rc=0: `vermelho: base=e25f079b9834 head=85043cc4008c`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=8; prova (asserção)=1`. O `opaco_sem_resto` não prova na base: as contagens e a fixture do O18 só passam no HEAD, mas o O18 tem mutante que a cobre (abaixo); o resto é regressão.
- Mutação do delta: `bin/forge-mutante --processos 4 --base e25f079b9834ba470ac8ccda65e5ad678a426aaa tests/mutantes/v047-destino-opaco*.json`, cabeçalho `base=e25f079b9834… mb=e25f079b9834… rev=85043cc4008c`, 16 specs; nenhuma linha `sobreviveu` nem `sem veredito` (só `morreu`), incluindo O18 e O99 a O104.
- Cobertura: `bin/forge-mutante --cobertura --base f4b0c2aeb42b…` rc=0, `rev=85043cc4008c`; todas as condições `coberta` (as 3 novas: redefinição por função, `VARIAVEIS_DO_BASH`, guarda do `pwd`); 4 `isenta` com motivo lido (443, 596, 1326, 1340), aceitas como no parecer anterior.
- Fronteiras novas protegidas: `date`, `mktemp`, `pwd`, `true` redefinidos por função (bloqueia) e `date` redefinido com saída literal (libera); `REPLY`, `MAPFILE`, `BASH_REMATCH`, `OPTARG`, `OLDPWD` recusam; `HOME` e variável definida na linha liberam.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado: nenhum achado aberto; o A1 da rodada anterior (mutante O18) morreu no 85043cc4 pela fixture `opaco-semresto-u3-mv-target-duas-vezes-bloqueia`; A1 resolvido, sem mutante sobrevivente, sem bug de produto (nada em `docs/qa/bugs/`).

## Revalidação por delta 85043cc4..041c671b (E1.321)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py` (`RESOLUCAO_TROCADA`, `na_lista_positiva`, guarda do `$(pwd)`), `docs/hooks.md`, `docs/hooks-fixtures.md`, 9 fixtures `opaco-u4-seg3-*` (s10 a s16, pwd-carregado, source-destino-literal-libera), `tests/test_hook_destino_opaco.py` e as specs `v047-destino-opaco-16` e `-17` (O105 a O108). Escopo do plano inalterado; o delta soma a obrigação A6 da segurança E1.304.
- Oráculo: prova de não edição refeita (commit 730843a9 ancestral; blob 535134e9; log vazio), 3 testes do oráculo.
- Vermelho: `bin/forge-testes --vermelho 85043cc4008c8d1395412674e3aef71d77c2153e --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, rc=0: `vermelho: base=85043cc4008c head=041c671bbcca`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=8; prova (asserção)=1` (regressão e guardas, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 --base 85043cc4008c8d1395412674e3aef71d77c2153e tests/mutantes/v047-destino-opaco-16.json tests/mutantes/v047-destino-opaco-17.json`, cabeçalho `base=85043cc4008c… mb=85043cc4008c… rev=041c671bbcca`: O99 a O108 todos `morreu`, rc=0. A rodada de todas as specs estourou o prazo de 590 s sob carga (rc=124, sem veredito, não conta).
- Sondas de abuso (Fixture e `rodar` de `tests/test_hooks.py`, fixture s10 com o comando trocado), conferidas no bash real em cópia descartável:
  - libera (rc 0) e grava `.git/config`: `so""urce ./f.sh; echo a > "$(date)"`, `\. ./f.sh; …`, `"." ./f.sh; …`, `export PA""TH=./bin:$PATH; …`, `a=PA; printf -v "${a}TH" ./bin:$PATH; …`.
  - libera sem prova de gravação: `s=sour""ce; $s ./f.sh; …` (gravou), `n=TMP; declare "${n}DIR=.git"; cp config "$(mktemp -u)"`, `read -r PA""TH <<< ./bin; …`.
  - recusa (rc 2): `. ./f.sh`, `builtin . ./f.sh`, `export "GIT_WORK_TREE=.git"`, `GIT_""WORK_TREE=…`, `n=GIT_WORK_TREE; export "$n=.git"`, `e=exp""ort; $e PATH=./bin` (estes por outra regra, não pela A6).
  Causa: a regex testa o texto cru; aspa, barra invertida e `$` dentro da palavra de comando ou do nome atribuído escapam. As fixtures s10 a s16 só têm a forma literal.
- Cobertura de guardas e CI: não rerrodei a `--cobertura`; o diff muda a regex e dois `if` e as specs 16 e 17 os cobrem pelos mutantes acima. Sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer reprovado no 041c671b: A2 bloqueante (bug alto, `docs/qa/bugs/v047-resolucao-trocada-nome-citado.md`; responsável o dev do hook). O A1 anterior segue resolvido. Fecha com: palavra de comando ou nome atribuído com aspa, barra invertida ou `$` desliga a lista positiva, mais uma fixture por forma (`so""urce`, `\.`, `"."`, `PA""TH`, nome montado).

## Revalidação por delta 041c671b..19df94ed (E1.325)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py` (`linha_conhecida`, `COMANDOS_INOFENSIVOS`, `na_lista_positiva`, `valores_do_corpo`, guarda do `$(pwd)`), `docs/hooks.md`, `docs/hooks-fixtures.md`, `docs/engineering/achados-recorrentes.md` (AR-14), o fragmento do changelog, 49 fixtures `opaco-u4-*` (g, r, s, q, red) e as specs de mutantes `-17`, `-18` e `-19` (O109 a O126). Mudança: a lista negativa `RESOLUCAO_TROCADA` sai; a lista positiva, o `echo`/`printf %s` e a troca de `$(pwd)` valem só se todos os comandos da linha, lidos por `shlex`, estão numa lista fechada (falha fechada). Escopo do plano (A9, A10, D2b, U4, A6) inalterado.
- Oráculo: prova de não edição refeita (commit 730843a9 ancestral; `git rev-parse HEAD:tests/test_oraculo_v047.py` = `535134e9…` igual ao blob; `git log --format=%H 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio); o módulo `test_oraculo_v047` roda no plano abaixo.
- Vermelho: `bin/forge-testes --vermelho 041c671bbcca2cb1fdee5b9d65304151bbf649a5 --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, rc=0: `vermelho: base=041c671bbcca head=19df94ed5619`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=8; prova (asserção)=1` (regressão e guardas, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 --base 041c671bbcca2cb1fdee5b9d65304151bbf649a5 tests/mutantes/v047-destino-opaco-17.json …-18.json …-19.json`, cabeçalho `base=041c671bbcca… mb=041c671bbcca… rev=19df94ed5619`: 23 `morreu`, `O126 · equivalente · hooks/conformidade.py:570` (declarado, justificativa lida: o U4 recusa antes pela mesma checagem; aceito), nenhum `sobreviveu`, rc=0.
- Cobertura: `bin/forge-mutante --cobertura --base f4b0c2aeb42b…` rc=0, `rev=19df94ed5619`; todas as condições `coberta`, 5 `isenta` com motivo lido (443, 570, 672, 1402, 1416), aceitas.
- A2 anterior: fechado. As sondas do bug v047-resolucao-trocada-nome-citado (`so""urce`, `\.`, `"."`, `s=sour""ce; $s`, `export PA""TH=`, `printf -v "${a}TH"`, `read -r PA""TH`, `echo(){…}`, `function echo {…}`) recusam (rc 2) no 19df94ed. Também recusam: `{ source … }`, `case`, `for`, `if`, `!`, `time`, `$'source'`, `x=1 source`, redireção antes do comando, `<(source …)`, `${x:-$(source …)}`.
- Sondas novas de abuso (hook por `Fixture`/`rodar` de `tests/test_hooks.py` sobre a fixture s10 com o comando trocado; bash real em cópia descartável com `.git/config` e `f.sh` com `date(){ echo .git/config; }`):
  - A3, libera (rc 0) e grava `.git/config`: `echo \\⏎source ./f.sh⏎echo a > "$(date)"`; `echo "a" \\⏎. ./f.sh⏎echo a > "$(date)"`; `echo a # \⏎source ./f.sh⏎echo a > "$(date)"`. Causa: `linha.replace("\\\n", "")` (linha 523) tira a barra e a quebra de `\\`+quebra, que no bash é uma barra escapada e um separador; o comando da linha seguinte vira argumento do `echo`. No comentário, a barra no fim não continua a linha no bash.
  - A3, libera e troca o PATH (`mkdir 0; install -m755 evil 0/date; <troca>; echo a > "$(date)"`, `evil` imprime `.git/config`; o `echo` redireciona, não precisa de `cp`): `x[PATH=0]=1`, `$[PATH=0]`, `${x[PATH=0]}` gravam `.git/config` com rc 0 do hook. `ATRIBUICAO` aceita qualquer subscrito `[…]` de nome minúsculo e `$[…]` e `${x[…]}` não passam por `EXPANSAO_QUE_ESCONDE`. Recusam: `$((PATH=0))`, `((PATH=0))`, `[ $((PATH=0)) ]`, `test $((PATH=0))`, `${x:(PATH=0)}`.
  - Os 3 liberam também no 041c671b (herdados), mas o pedido é fechar a classe da linha inteira (AR-14, `R-CONFORMIDADE`) e ela não fecha.
- Falso positivo: aceito e documentado em `docs/hooks.md` (comando fora da lista na mesma linha do destino opaco). Medido: recusam `cd /tmp && cat x > "$(mktemp)"`, `npm test > "$(mktemp)"`, `python3 -c 1; cp config "$(mktemp)"`, `curl … | tee "$(mktemp)"`, `awk 1 x > "$(mktemp)"`, `export FOO=1; …`, `FOO=1 cp config "$(mktemp)"`, `for … do echo a > "$(mktemp)"; done`, `echo $((1+1)) > "$(mktemp)"`; liberam `cp config "$(mktemp -u)"`, `echo a > "$(date +%s).log"`, `ls | grep a | tee "$(mktemp)"`, `find . -name x > "$(mktemp)"`, `cd docs && cp ../config "$(pwd)/out"`, `if [ -f x ]; then cp config "$(mktemp)"; fi`. Custo real (sem `cd`, `for`, interpretador na linha), conforme a decisão; sem achado, só o contorno da documentação.
- Bug alto v047-resolucao-lista-fechada-junta-linha (resumo aqui, sem arquivo de bug por ordem do brief, que limita o commit ao parecer; responsável: dev do hook): passos e sondas acima; esperado rc 2; obtido rc 0 com gravação em `.git/config`. Fecha com: o `shlex` ler o texto sem a junção de `\`+quebra (ou recusar `\` seguido de quebra e `#` com `\` no fim da linha), `ATRIBUICAO` recusar subscrito com `=`, `$[` e `${…[…=…]}` entrarem no `EXPANSAO_QUE_ESCONDE`, e uma fixture por forma.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer reprovado no 19df94ed: A3 bloqueante (bug alto). A2 fechado, sem mutante sobrevivente. A lista fechada resolve os nomes citados e montados, mas a classe da linha inteira ainda tem duas fugas (junção de barra+quebra pelo `replace` e subscrito aritmético de nome minúsculo).


## Revalidação por delta 19df94ed..000cd0c8 (E1.329, instância que não fez a entrega)

Fecha o A3 da rodada anterior (aritmética e barra e quebra), resolvido em `000cd0c8` (`R-CONFORMIDADE`).

## Achados


## Sondas do delta (aspas simples no shell; cada uma com `echo a > "$(date)"` no fim e `date` benigno)
Montadas sobre a fixture `opaco-u4-v-qa-barra-dupla-quebra-bloqueia` (hook real, `f.sh` redefine `date`). 77 sondas:
- barra e quebra: 1, 2, 3, 4 e 5 barras antes da quebra, dupla continuação, linha vazia, `\r`+LF, dentro de `$(…)`, após `;` e `&&`: libera exatamente quando o bash junta (1, 3 e 5 barras, dupla continuação) e recusa quando a quebra separa (2, 4, 6+, `\r`); aspa simples e `#` com continuação recusam.
- aritmética: `$[PATH=0]`, `$((PATH=5))`, `x[PATH=0]=1`, `x[1+PATH=2]=1`, `${x[PATH=0]}`, `${x:PATH=5}`, `${x:1:PATH=5}`, `${x:i}`, `${x:$i}`, `${x:1:$[…]}`, `a=(PATH=5)`, `let`, `[[ 1 -eq PATH=5 ]]`, `unset 'x[…]'`, `test -v 'x[PATH=5]'`, `[ -v x[…] ]`, `{fd}>f`, `{PATH}>f`, `$\`+quebra+`[`, `x\`+quebra+`[PATH=5]=1`: todas recusam (rc 2).
- liberam (rc 0, esperado): `${x: 1: 2}`, `${x: -1}`, `${x:-1}`, `${x[@]}`, `${x[*]}`, `${y[3]}`, `"${x[1]}"`, `${#y[0]}`, `x[0]=1 y[12]=2 echo ok`, `echo a \`+quebra+`;`.
- função `f ( )`, `function f ( )`, `f(`+`\`+quebra+`)` e `f( ){` com `date` redefinido recusam.
- 9 sondas de `.git` por variável e barra dupla e quebra (`d=.git\\`, `$(echo .gi\\`+quebra+`t)`): todas recusam.
Fora das posições acima a classe fecha, mas o corpo de heredoc sem aspas (sonda `: <<E`, `$[PATH=5]`, `E`) libera e o bash o expande: A5, bug alto.

## Execução no head 000cd0c8
- `forge-check parecer delta docs/qa/v047-conformidade-destino-opaco.md`, rc 0: domínio = hook, docs, changelog, 1 teste de módulo (`tests/test_hook_destino_opaco.py`, 2 linhas) e as fixtures `opaco-u4-v-*` novas.
- Vermelho: `bin/forge-testes --vermelho 19df94ed5619ae0bb77dbdf5c9abde7d50f04635 --modulos test_hook_destino_opaco --prazo 500`, rc 0: `vermelho: base=19df94ed5619 head=000cd0c8a7f6`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; os outros 3 passam na base (regressão, esperado); `contagem: não prova=3; prova=1`.
- Mutação do delta: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco-20.json tests/mutantes/v047-destino-opaco-21.json`, rc 0, `pedido=v047 rev=000cd0c8a7f6`: 15 `morreu` (O133 a O148), nenhum sobrevivente. `--cobertura --base 19df94ed…`: as 7 condições mudadas `coberta` (532, 534, 543, 557, 574, 585, 1413), nenhuma sem mutante. Uma rodada com as 21 specs e `--base` não terminou neste ambiente (processo morto sem saída, sem veredito); vale a rodada das duas specs do delta.
- Suíte inteira: sem PR nem check-run `bateria` para o sha; fica para o CI do PR. `forge-check docs` rc 0.

Todos os critérios da tabela anterior seguem como estavam; o delta só acrescenta a classe aritmética e barra e quebra, coberta pelas fixtures `opaco-u4-v-*` e pelos mutantes acima.

- Sonda do A5: `: <<E`⏎`$[PATH=5]`⏎`E`⏎`echo a > "$(date)"` rc 0 (deveria recusar); `: <<E`⏎`plain`⏎`E` rc 0 (certo). Responsável: dev da stack do hook.

## Revalidação por delta 000cd0c8..e34924b4 (E1.333, instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py` (`expansao_conhecida`, `corpos_conhecidos`, `corpo_desconhecido`, `valor_calculado`, `textos_do_valor` com `juntar_continuacoes`), `docs/hooks.md`, o fragmento do changelog, 14 fixtures `opaco-u4-h-*`, `tests/test_hook_destino_opaco.py` (piso 159 para 173) e a spec `v047-destino-opaco-22` (O149 a O152). Escopo do plano inalterado; o delta fecha o A5 (A12 da segurança E1.328, A5 do review E1.327) e o A4.
- Oráculo: prova de não edição refeita (commit 730843a9 ancestral; `git rev-parse HEAD:tests/test_oraculo_v047.py` = `535134e9…` igual ao blob; `git log --format=%H 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio); o módulo `test_oraculo_v047` roda no vermelho abaixo.
- Vermelho: `bin/forge-testes --vermelho 000cd0c8a7f69497fd41b5f64c786ed9df5f5274 --modulos test_hook_destino_opaco,test_oraculo_v047 --prazo 500`, rc 0: `vermelho: base=000cd0c8a7f6 head=e34924b4e6d1`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=6; prova (asserção)=1` (os demais são regressão, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco-22.json`, `pedido=v047 rev=e34924b4e6d1`: O149, O150, O151 e O152 `morreu`, nenhum sobrevivente, rc 0. `bin/forge-mutante --cobertura --base 000cd0c8…`: as 4 condições mudadas (555, 564, 1431, 1721) `coberta`, nenhuma sem mutante.
- Sondas de abuso (aspas simples no shell; hook real por `Fixture`/`rodar` de `tests/test_hooks.py`, fixture s15 com o comando trocado, cada uma terminando em `echo a > "$(date)"` com `date` redefinido): 24 sondas com corpo de heredoc sem aspas que atribui recusam (rc 2): `$[PATH=5]`, `$((PATH=5))`, `${PATH:=/x}`, `${a[PATH=5]}`, `${!n}`, `${n@P}`, `<<-E` com tab, `$`+barra+quebra+`[PATH=5]`, dois heredocs na linha (o atribuidor é o segundo), destino na própria linha do heredoc, heredoc dentro de `$(…)`, `{ …; }`, função, pipe, `&&` na linha seguinte, `${PA`+barra+quebra+`TH:=5}`, crase e `$(echo $[PATH=5])` no corpo. Liberam (rc 0, esperado): `<<'E'`, `<<"E"`, `<<\E` (literais), corpo sem expansão, corpo com `$HOME ${x:-1} ${#y}`, `cp config "$(mktemp)"` depois de heredoc simples.
- Falso positivo medido, aceito e coberto pela regra do próprio hook (recusa na dúvida): `\$[PATH=5]` escapado no corpo, `$((1+1))` e `$(date)` no corpo sem aspas recusam. Custo baixo; contorno `<<'E'`. Sem achado.
- A5 e A4 anteriores: fechados (sonda do A5 recusa; `textos_do_valor` usa `juntar_continuacoes`). Classe repetida (AR-14, contexto aritmético na linha inteira) já registrada em `docs/engineering/achados-recorrentes.md`; não gravei linha nova.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local. `forge-check docs` rc 0.

Os fechados: A5 (bloqueante, corpo de heredoc sem aspas) e A4 (recomendado, `textos_do_valor`). Parecer aprovado no e34924b4 (`R-QA`): nenhum bug aberto, sem mutante sobrevivente, sem achado.

## Revalidação por delta e34924b4..74b42c69 (E1.337, volta do lote B: A13 e A14, instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py` (`corpos_conhecidos` recusa corpo de heredoc sem aspas que atribui, A13; `valores_da_variavel` recusa `$d` quando a linha tem `${d:=v}`, `${d=v}` ou `${d[i]:=v}`, A14), `docs/hooks.md`, o fragmento do changelog, 8 fixtures `opaco-u4-*` novas, `tests/test_hook_destino_opaco.py` (piso 173 para 181) e as specs `v047-destino-opaco-22` (O150 reescrito) e `-23` (O153, O154). Escopo do plano inalterado (`R-CONFORMIDADE`).
- Oráculo: `tests/test_oraculo_v047.py` não editado (o delta não o toca; blob `535134e9…` igual ao gravado acima); o módulo roda no vermelho abaixo.
- Vermelho: `bin/forge-testes --vermelho e34924b4e6d1 --modulos test_hook_destino_opaco,test_oraculo_v047 --prazo 500`, rc 0: `vermelho: base=e34924b4e6d1 head=74b42c69d7c1`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=6; prova (asserção)=1` (os demais são regressão, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco-22.json tests/mutantes/v047-destino-opaco-23.json`, `pedido=v047 rev=74b42c69d7c1`: O149 a O154 `morreu` (O153 em `conformidade.py:556`, O154 em `:688`), nenhum sobrevivente, rc 0. `--cobertura --base e34924b4…` (`base=` e `mb=` iguais): condições 556 e 688 `coberta`, a spec 22 `editada` (O150 reescrito para o novo trecho, ainda mata).
- Sondas (aspas simples; hook real pela máquina do `test_hook_destino_opaco`, em cópia em `$TMPDIR`, 17 fixtures `opaco-zz` descartáveis, destino `"$d"`, `"$(date)"` ou `"$(mktemp)"`): head recusa (rc 2) `a=.g; : ${d:=${a}it/config}`, `${d:=.git/config}`, `${d=.git/config}`, `${d[0]:=.git/config}`, `${d:=docs}` (atribuição na linha, recusa na dúvida), `${d:=${a:=.g}it/config}`, `${d:=.g}; … "${d}it/config"`, heredoc sem aspas com `${d:=…}`, `${d=…}`, `${D:=…}` e `<<-E` com tab. Libera (rc 0): `d=docs`, `${d:-docs}`, `<<'E'` literal, `"$(mktemp)"`. Na base e34924b4 as mesmas sondas `${d:=…}` na linha (01, 05, 15) saem rc 0, ou seja, o delta fecha a classe.
- Falso positivo medido, não é regressão (igual na base): `cat <<E`⏎`plain ${x:-1}`⏎`E`⏎`echo a > "$(mktemp)"` recusa com "`${` com ação crítica" (guarda anterior ao delta, recusa na dúvida). Sonda de abuso fora da lista, da classe vizinha (confirma o A16 da segurança E1.340): `: .gi; cp -rT ev "$_"t`, `: .gi; echo a > "$_"t` e `echo a > "$_"t` saem rc 0 (esperado 2; no shell `: .gi; echo "$_"t` imprime `.git`); `"$_"` sozinho recusa. Bug alto, responsável: dev da stack do hook; falta fixture `opaco-u4-*` e mutante para a linha :698.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local. A13 e A14 fechados.

- Sonda de abuso da classe vizinha (confirma a A15 da segurança, fora da lista de sondas acima): `: ${d:=.gi}; cp -rT ev "$d"t` e `: ${d:=.gi}; echo a > "$d"t` saem rc 0 no head (esperado 2); `d=.gi; cp -rT ev "$d"t` recusa; `d=docs; echo a > "$d"` libera. O A14 fechou só a forma direta `"$d"`; a forma com resto colado sem barra segue aberta. Bug alto (escrita em `.git/config` sem recusa), responsável: dev da stack do hook. Falta fixture `opaco-u4-*` e mutante para a linha `:693`.

Parecer reprovado no 74b42c69 (`R-QA`): A13 e A14 fechados, sem mutante sobrevivente, mas A16 bloqueante aberto (mesma classe, forma com resto colado).

## Revalidação por delta 74b42c69..c3cde09f (E1.341, volta A15; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`, rc 0: `hooks/conformidade.py` (`atribui_por_expansao` extraída; a guarda do prefixo colado em `valores_da_variavel` também a consulta), `docs/hooks.md`, 7 fixtures `opaco-u4-*` novas (S44 a S47 e 3 de prefixo), `tests/test_hook_destino_opaco.py` (piso 181 para 188) e a spec `v047-destino-opaco-23` (O154 reescrito, O155 e O156 novos). Escopo do plano inalterado (`R-CONFORMIDADE`). O A16 do parecer anterior está fechado: as duas sondas dele recusam (abaixo); abre o A17.
- Oráculo: o delta não toca `tests/test_oraculo_v047.py`; blob `535134e9…` igual ao gravado; o módulo roda no vermelho abaixo.
- Vermelho: `bin/forge-testes --vermelho 74b42c69d7c1fd98980986104f7e3733dbbbdd5b --modulos test_hook_destino_opaco,test_oraculo_v047 --prazo 500`, rc 0: `vermelho: base=74b42c69d7c1 head=c3cde09fdec3`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=6; prova (asserção)=1` (os demais são regressão, esperado).
- Mutação: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco-23.json`, rc 0, `pedido=v047 rev=c3cde09fdec3`: O153 (:556), O154 (:693), O155 (:698), O156 (:682) `morreu`, nenhum sobrevivente. `--cobertura --base 74b42c69…` (`base=` e `mb=` iguais): condições 682, 693 e 698 `coberta`, a spec 23 `editada`; nenhuma sem mutante.
- Sondas (aspas simples; hook real pela máquina do `test_hook_destino_opaco`, fixture S44 com o comando trocado, em `$TMPDIR`): recusam (rc 2) `: ${d:=.gi}; cp -rT ev "$d"t`, `: ${d:=.gi}; echo a > "$d"t`, `: ${d=.gi}; echo a > "$d"t`, `: ${d[0]:=.gi}; echo a > "$d"t`, `: ${abc:=.gi}; echo a > "$ab"ct` (prefixo de nome longo), `: ${D:=.gi}; echo a > "$D"t`, `: <<< ${d:=.gi}; cp -rT ev "$d"t`, `: ${d:=.gi}; cp -rT ev "${d}t"`, `echo ${d:=.gi} >/dev/null; echo a > "$d"t`. Liberam (rc 0, esperado): `d=docs; echo a > "$d"`, `echo a > "$(mktemp)"`, `: ${d:-docs}; cp x "$(mktemp)"`. Sem achado.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local. `forge-check docs`: ver Provas do relatório.

Parecer reprovado no c3cde09f (`R-QA`): o A16 do parecer anterior (`${d:=v}` com resto colado) está fechado e sem mutante sobrevivente, mas o A17 (`"$_"t`) bloqueia.

## Revalidação por delta c3cde09f..c22624c5 (E1.345, volta A17; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`, rc 0: `hooks/conformidade.py` (`nasce_fora_do_ambiente` extraída; o nome inteiro e cada prefixo passam por ela, o que inclui `VARIAVEIS_DO_BASH`), 5 fixtures `opaco-u4-*` novas (S48 a S51 e `"$HOME"t` libera), `tests/test_hook_destino_opaco.py` (piso 193), mutantes O154/O155 ajustados e `-24` (O157, O158). Regra: `R-CONFORMIDADE`; ordem do dono de 15/11 (bugs já achados fechados; fuga rara nova vira recomendado).
- Vermelho: `bin/forge-testes --vermelho c3cde09fdec39e3d8bed6b8d0e0113216189a7ca --modulos test_hook_destino_opaco --prazo 500`, rc 0: `vermelho: base=c3cde09fdec3 head=c22624c5b274`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=3; prova (asserção)=1`.
- Mutação: `bin/forge-mutante tests/mutantes/v047-destino-opaco-23.json tests/mutantes/v047-destino-opaco-24.json --base c3cde09f…`, rc 0, `rev=c22624c5b274`: O153, O154, O155, O156, O157, O158 `morreu`, nenhum sobrevivente. `--cobertura --base c3cde09f…`: `coberta` em :699 (O157) e :704 (O155, O158), rc 0.
- Sondas (aspas simples; hook real pela máquina de `tests/test_hooks.py`, fixture S51 com o comando trocado): recusam (rc 2) `: .gi; cp x "$_"t`, `: .gi; echo a > "$_"t`, `: .gi; cp x "${_}"t`, `: .gi; cp x "$_"`, `: .g; cp x "$_"it`, `d=.gi; cp x "$d"t`, `echo .gi >/dev/null; cp x "$_"t`, `: .gi; cp x "$__"t`, `: .gi; cp x "$_x"t`, `cp x "$OLDPWD"t`, `cp x "$PWD"t`, `cp x "$RANDOM"t`, `cp x "$REPLY"t`, `cp x "$BASH_COMMAND"t`. Liberam (esperado): `cp -rT ev "$HOME"t`, `cp x "$PPID"t` (número).
- Oráculo: o delta não toca `tests/test_oraculo_v047.py` (blob `535134e9…` igual ao gravado). `python3 -m unittest tests.test_hook_destino_opaco`: 4 testes, OK.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado no c22624c5 (`R-QA`): A17 fechado (as sondas do bug, `: .gi; cp -rT ev "$_"t` e `: .gi; echo a > "$_"t`, recusam), sem regressão, sem mutante sobrevivente, nenhum bug aberto, sem achado novo.

## Revalidação por delta c22624c5..081473ac (E2.131, junção da develop bf475209; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`, rc 0, escopo "sem o que veio da base (develop)": só `bin/forge-testes` e `tests/test_testes_tocados.py`, os dois arquivos que conflitaram na junção. O código de produto (`hooks/conformidade.py`), as fixtures, os mutantes e o oráculo não mudam; o blob do oráculo segue `535134e9…` (o delta não o toca). Escopo do plano (A9, A10, D2b, U4) inalterado.
- Conflito em `bin/forge-testes` (tupla `FORGE_CHECK`): resolvido pela união. Conferi por script nas três versões (`081473ac`, `7294bea3`, `bf475209`): nenhum módulo do nosso lado nem da develop saiu (`perdeu vs ours=set()`, `perdeu vs develop=set()`) e nada foi somado fora dos dois lados (`ganho=set()`). `test_hook_destino_opaco` e `test_conformidade_opaco` ficam, e `test_conferencia_dois_pedidos` (develop, #564) também. Sem mudança de comportamento do mapa além da soma.
- Conflito em `tests/test_testes_tocados.py` (contagem do `forge-check`): 83 passou a 86 (3 módulos de develop somados aos nossos); o comentário junta as duas listas de histórico. Coerente com a tupla.
- `python3 -m unittest tests.test_testes_tocados`: 151 testes, OK (skipped=1, o skip é da base, não meu), 142 s.
- Vermelho e mutação: não rerrodei. O delta não muda guarda nem teste de regra; só a lista de mapeamento de testes, sem condição Python nova (nada para `--cobertura`). O `AR-1` (lista de mutantes incompleta) não se aplica: nenhuma linha de guarda mudou no diff. O último vermelho e a mutação (c22624c5) valem.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado no 081473ac (`R-QA`): a junção não altera comportamento, sem bug aberto, sem achado.

## Revalidação por delta 081473ac..8e40fe69 (E2.512, junção da develop 86ac0fcb; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`: o que veio da base saiu do escopo; o que mudou de nosso lado foi `bin/forge-testes` (tupla `FORGE_CHECK`) e `tests/test_testes_tocados.py` (helper `sem_oraculos`, contagem 88), mais `hooks/conformidade.py`, onde a única diferença contra o 081473ac são as 9 linhas da `CITA_A_MARCA` (E2.142), vindas da develop. Oráculo, fixtures e mutantes do item não mudaram.
- Oráculo: `git rev-parse HEAD:tests/test_oraculo_v047.py` = `535134e9…` (igual ao blob), `730843a9` ancestral, `git log 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio.
- Junção em `bin/forge-testes`: por script, nenhum módulo de teste de `081473ac` nem de `86ac0fcb` saiu do head (`perdeu=[]` nas duas).
- Testes dos arquivos tocados: `python3 -m unittest tests.test_conformidade_opaco tests.test_hook_destino_opaco tests.test_oraculo_v047 tests.test_testes_tocados`: 170 testes, OK (skipped=1, `MedidaDaVagaPesada`, do sandbox: /proc de outro namespace; não é meu), 121,7 s.
- Vermelho e mutação: não rerrodei. O delta não muda guarda nem teste de regra do item (a mudança no hook é da base e não é deste pedido); sem condição Python nova do item para `--cobertura`. Vale o vermelho e a mutação do c22624c5.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado no 8e40fe69 (`R-QA`): a junção não altera o comportamento do item, sem bug aberto, sem achado.

## Revalidação por delta 8e40fe69..1df5245b (E2.609; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`: `tests/mutantes/v046-conformidade-caminho-git-2.json` (G12, G13, G14), `-4.json` (G20) e `tests/test_oraculo_v047.py`. O hook `hooks/conformidade.py` não mudou contra o 81c50342 (`git diff --stat` vazio). Escopo do plano (A9, A10, D2b, U4) inalterado.
- Oráculo editado pela segurança, com autorização do dono (`sem_manutencao` no ambiente git; fixture `README.md` renomeada para `LEIAME.md`). Prova de não edição: o blob mudou de `535134e9…` para `a9eddad2…` por decisão do dono; commit `1df5245b` toca só o oráculo. Diff linha a linha contra o 730843a9: 4 hunks, todos de ambiente (import de `ambiente_git.sem_manutencao`, a chave `LEIAME.md` e as duas chamadas de `subprocess.run` com `env=sem_manutencao(ambiente())`). Asserções: 10 no original e 10 agora, nenhuma removida nem afrouxada; nenhum `skip`, `skipIf` nem `expectedFailure`; `README` não aparece mais no arquivo (o nome só vivia na tabela `ARQUIVOS`).
- Mutantes realinhados: o `de` de G12, G13, G14 e G20 agora é o trecho com o sufixo `# A5`, `# A3`, a atribuição inteira ou o `self.rev_parse_misto or`; o `para` faz a mesma troca de antes (`--target-directory` ignorado, `"`" in a` vira `False`, `m["crase"]` sai, `any(...)` vira `False`). Cada `de` existe uma única vez em `hooks/conformidade.py` (linhas 2059, 2060, 387, 1572) e o teste que deve cair é o mesmo (`test_fixtures_gitcomum`).
- Mutação: `bin/forge-mutante --processos 4 --base 81c503420c2cd99a376ac73a68a7ef7be1181bf2 tests/mutantes/v046-conformidade-caminho-git-2.json tests/mutantes/v046-conformidade-caminho-git-4.json`, cabeçalho `base=81c503420c2c… mb=81c503420c2c… rev=1df5245b257c`: G12, G13, G14 e G20 `morreu`; também `morreu` G9, G10, G11, G15, G16, G21, G22, G23, G24 e G26; `G25 · sobreviveu · hooks/conformidade.py:1947` (ver A1).
- Testes, sem `-I`: `python3 -m unittest tests.test_oraculo_v047 tests.test_ambiente_git tests.test_reval_delta`: 33 testes, OK, 52 s.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado no 1df5245b (`R-QA`): oráculo sem asserção mais fraca, G12, G13, G14 e G20 mortos como antes, 33 testes OK. Sem bug do pedido; o A1 é dívida herdada da v046 e não bloqueia este pedido.

## Revalidação por delta 1df5245b..b9e4d58a (E2.620, junção da develop c7a8ff72; instância que não fez a entrega)
Domínio lido por `forge-check parecer delta`, rc 0, escopo "sem o que veio da base (develop)": `bin/forge-testes`, `tests/test_testes_tocados.py` e uma linha de `docs/engineering/achados-recorrentes.md` (AR-4, `:63` para `:64`; confere com o formato do PA-7). O hook, as fixtures, os mutantes e o oráculo não mudam. Escopo do plano (A9, A10, D2b, U4) inalterado.
- Conflito em `bin/forge-testes`: o mapa `hooks/.*` manteve os quatro testes, entre eles `test_pre_push_patch` (da develop, E2.567); a regra nova `docs/devops/pp1-pre-push.patch` liga o patch ao mesmo teste. Nenhum módulo saiu.
- Oráculo: `git merge-base --is-ancestor 730843a9 HEAD` ok; `git rev-parse HEAD:tests/test_oraculo_v047.py` = `a9eddad2…` (blob autorizado pelo dono no 1df5245b, registrado no delta anterior; o delta atual não o toca); `git log 730843a9..HEAD -- tests/test_oraculo_v047.py` lista só o `1df5245b` (e o merge que o traz), nenhum commit novo.
- Testes, sem `-I`: `python3 -m unittest tests.test_testes_tocados tests.test_oraculo_v047`: 165 testes, OK (skipped=1, `MedidaDaVagaPesada`, do sandbox: /proc de outro namespace; não é meu), 71,6 s.
- Vermelho: `bin/forge-testes --vermelho 1df5245b257c35fe86f49f4278a0beb1e363ba4a --modulos test_testes_tocados --prazo 500`, saída 0: `vermelho: base=1df5245b257c head=b9e4d58a658f`; `Convencao.test_o_patch_do_pre_push_e_o_comum_dos_hooks_levam_ao_test_pre_push_patch · H=ok · B=falha · prova (asserção)`; `MapaCobreOQueOsTestesLeem.test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=159; prova (asserção)=2; pulado=1`.
- Mutação e cobertura: não rerrodei. A mudança em `bin/forge-testes` é dado do `MAPA` (tupla e regex), sem condição Python nova; o teste novo prova a ligação dos dois caminhos. `forge-mutante --cobertura --base 1df5245b…` só lista condições vindas da develop (`bin/forge-mutante`, `tests/ambiente_git.py`) e `não coberto` de arquivos não Python; nada do delta do pedido. Vale a mutação anterior.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado no b9e4d58a (`R-QA`): a junção mantém os quatro testes do mapa `hooks/.*`, o teste novo tem vermelho na base, 165 testes OK, sem bug aberto, sem achado novo.

## Achados
- A1 (recomendado) tests/mutantes/v046-conformidade-caminho-git-4.json:1 · G25 sobrevive (hooks/conformidade.py:1947). Fora do delta: igual no 81c50342 e no develop; o pedido não toca a linha. Vira cartão: teste que mate G25 ou declará-lo equivalente.
