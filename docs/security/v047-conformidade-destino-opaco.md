---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 2c8a3624c6932063893a5c3dc826a254c2d80b9e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (lote B, destino opaco, junção com a develop)

**Revalidação por delta no head `2c8a3624` (E2.627).** `forge-check parecer delta`, intervalo `73ba49f7..2c8a3624`. No domínio: `bin/forge-testes` e `tests/test_oraculo_v047.py`. `hooks/conformidade.py` e todo `hooks/` sem diferença (`git diff 73ba49f7 HEAD -- hooks` vazio), então as linhas dos achados valem. Em `bin/forge-testes`: `test_pre_push_patch` entra na regra `hooks/.*` do `MAPA` e nasce a regra `docs/devops/pp1-pre-push\.patch` com `test_pre_push_patch`; são listas de módulos do plano dirigido do pre-push, nunca portão de CI, e só acrescentam. O oráculo (blob `a9eddad2`) mudou por ajuste autorizado pelo dono: importa `sem_manutencao` de `tests/ambiente_git.py` para as chamadas ao git e troca o arquivo `README.md` do fixture por `LEIAME.md`; as asserções e os casos de abuso seguem os mesmos, nada afrouxa. Rodei `tests.test_oraculo_v047`, `tests.test_testes_tocados` e `tests.test_pre_push_patch`: 177 testes OK (1 pulado pelo sandbox); a suíte inteira fica no CI. Nenhum achado novo; A17, A18, A19, A11 e A5 seguem recomendados. Oráculo: `tests/test_oraculo_v047.py` blob `a9eddad233156152bc692220fa181eecd1eb6821`.

Revalidação por delta da junção `081473ac` (E2.130): merge de `7294bea3` (a branch, `c22624c5` mais pareceres) com a `develop` `bf475209`. `forge-check parecer delta`, intervalo `c22624c5..081473ac`, sem o que veio da base. No domínio só `bin/forge-testes`; fora, `tests/test_testes_tocados.py`. São os dois arquivos com conflito. Não fiz a junção.

**A junção não muda comportamento.** Em `bin/forge-testes`, o resultado é a `develop` mais o lado da branch (`f4b0c2ae..7294bea3`): `test_hook_destino_opaco` e `test_conformidade_opaco` em `FORGE_CHECK` e na regra `hooks/.*` do `MAPA`, e `test_hook_destino_opaco` em `REAPROVEITAM_O_LOTE`, mantendo o `test_conferencia_dois_pedidos` e o `--texto` da `develop`. São só listas de módulos do plano dirigido (o filtro do pre-push, nunca portão de CI); só acrescentam, nada sai. Em `tests/test_testes_tocados.py`: o `sem_oraculos` da branch e a contagem de 83 para 86. Nos outros 315 arquivos, o diff `bf475209..081473ac` é linha por linha igual ao da branch (`f4b0c2ae..7294bea3`): o merge não trouxe nada além dos dois lados. A `develop` não tocou `hooks/` desde `f4b0c2ae`, por isso o `hooks/conformidade.py` e as linhas citadas nos achados são os de `c22624c5`. O delta não toca o oráculo (`tests/test_oraculo_v047.py` é o da branch).

**Revalidação no head `73ba49f7` (E2.535), depois da junção `81c50342` com a `develop` `86ac0fcb`.** Contra o parecer anterior (`081473ac`), em `hooks/conformidade.py` a única diferença são 9 linhas (`git diff 081473ac HEAD`): a constante `CITA_A_MARCA` ganha `|gravar_resultado_do_pr` (linha 76) e a mensagem de bloqueio da linha 1728 cita a função; vem da `develop` (S2 da E2.142). Só amplia o que é recusado no projeto, sem abrir caminho. Contra a `develop` `86ac0fcb`, o `hooks/conformidade.py` e o `bin/forge-testes` são só o trabalho da branch (`bin/forge-testes`: os módulos `test_hook_destino_opaco` e `test_conformidade_opaco` nas listas do plano dirigido, sem portão de CI). Os pareceres de review e QA (`8e40fe69`, `73ba49f7`) só tocam `docs/`. Rodei `python3 -m unittest tests.test_conformidade_opaco tests.test_hook_destino_opaco` (6 testes, OK) e `tests.test_oraculo_v047` (3 testes, OK); a suíte inteira fica no CI. Nenhum achado novo; A17, A18, A19, A11 e A5 seguem recomendados e A16 segue fechada.

Vale a ordem do dono de 15/11 sobre o lote B: bloqueia só achado antigo aberto ou regressão. A16 segue fechada e a junção não abre regressão. A17 a A19, A11 e A5 continuam recomendados, como no parecer de `c22624c5`.

## Gatilhos
`R-SEGURANCA`: hook de guarda (`conformidade`) que analisa entrada livre (uma linha de Bash) para proteger o `.git` (`config`, `hooks/`, marca da sessão). Bloqueio por `R-CONFORMIDADE`.

## Achados
- A17 (recomendado) hooks/conformidade.py:2059 · Redireção com descritor no fim (`2>/dev/null`, `2>&1`, `1>x`, `9</dev/null`) faz `cp`, `install` e `rsync` tomarem o `2` por destino: `cp ev/config .git/config 2>/dev/null` libera e grava .git/config. Já na develop f4b0c2ae; cartão de prioridade alta (R-CONFORMIDADE)
- A18 (recomendado) hooks/conformidade.py:485 · Os parâmetros especiais `$@` e `$*` ficam fora de `VARIAVEL_DO_VALOR`: `set -- .git; cp -rT ev "$@"` libera e o bash copia ev sobre o .git. Já na develop f4b0c2ae: cartão
- A19 (recomendado) hooks/conformidade.py:701 · Referência por nome (`declare -n d=_`, também `local -n` e `typeset -n`): o hook calcula `d` como o literal `_`, o bash o lê como `$_`; `declare -n d=_; : .git; cp -rT ev "$d"` libera. Já na develop f4b0c2ae: cartão
- A11 (recomendado) hooks/conformidade.py:497 · A lista fechada recusa todo programa externo na linha (`python3 gen.py > "$(mktemp)"`, `make check 2>&1 | tee "$(mktemp)"`, `cd docs && …`), mas programa externo não troca a resolução do shell; só embutido, função e atribuição trocam
- A5 (recomendado) hooks/conformidade.py:1494 · Resto com barra que sobe (/../config) depois de opaco dentro do .git libera: "$(mktemp -u -p .git)"/../config e TMPDIR=.git com "$(mktemp -u)"/../config gravam .git/config. Já na develop f4b0c2ae; fora do texto da A9 (sem resto): cartão novo

## Sondas
- S48 · : .gi; cp -rT ev "$_"t (ev/config com [core] hooksPath) · espera: 2 · obtido: 2
- S49 · true .gi && cp -rT ev "$_"t · espera: 2 · obtido: 2
- S50 · : .g; cp -r ev/. "$_"it · espera: 2 · obtido: 2
- S51 · : .gi; cp x "$_"t · espera: 2 · obtido: 2
- S52 · cp ev/config .git/config 2>/dev/null · espera: 2 · obtido: 0
- S53 · cp ev/config .git/hooks/pre-push 2>/dev/null · espera: 2 · obtido: 0
- S54 · d=.git; cp -rT ev "$d" 2>&1 · espera: 2 · obtido: 0
- S55 · set -- .git; cp -rT ev "$@" · espera: 2 · obtido: 0
- S56 · declare -n d=_; : .git; cp -rT ev "$d" · espera: 2 · obtido: 0

## Detalhe dos achados
Como as sondas rodaram: script no meu rascunho que monta o fixture de `tests/test_conformidade_opaco.py` (`dados_do_caso`, ambiente projeto, papel `forge:tech-lead`) com `ev/config` a mais, roda `hooks/conformidade.py` pelo `rodar` de `tests/test_hooks.py`, depois roda a mesma linha no `bash -c` na pasta do caso e compara o `.git` (sem `objects/`) antes e depois. "espera: 2" quer dizer que o bash mudou o `.git`. Rodei o mesmo conjunto no head `c22624c5`, na base `c3cde09f` e na `develop` `f4b0c2ae` (o hook de cada uma, com o harness do head).

**A16 · fechada.** S48 a S51 dão 2 no head (0 na base). Também dão 2: `"${_}"t`, `$_"t"`, `"$_""t"`, `"$_"$'t'`, `"$_"t/`, `"${_:-x}"t`, `"${_%x}"t`, `"${_#x}"t`, `"${_/x/y}"t`, `"${_}t"`, `: .g; … "$_"i"t"`, `cp -rT ev -- "$_"t`, `GIT_X=1 cp -rT ev "$_"t`, `set -- .gi; … "$1"t`, `printf -v d .gi`, `read d <<< .gi`, `for d in .gi`, `export d=.gi` e `x=_; : .git; … "${!x}"`. A15 segue fechada (`: ${d:=.gi}; … "$d"t` e `d=.gi; … "$d"t` dão 2). O legítimo segue em 0: `cp -rT ev "$HOME"t`, `echo a > "$(mktemp)"`, `: ${d:-docs}; echo a > "$d"`. Falsos positivos aceitos, como o parecer anterior previa: `: docs; echo a > "$_"t` e `: .gi; d=t; cp -rT ev "$_$d"`.

**Sem regressão.** A condição nova do laço de prefixos (`nasce_fora_do_ambiente(nome[:k])` ou `nome[:k]=`) contém a antiga. A regex de antes, com `(?![\w])`, é a união da de agora, com `(?![\w=])`, e da busca por `nome[:k]=`, cuja lookbehind (`(?<![\w$])`) é mais larga. A condição nova soma `VARIAVEIS_DO_BASH` e o prefixo `GIT_`, como a correção mínima pedia. Para o nome inteiro, a função extraída tem a mesma lógica. O delta só acrescenta recusa. O mutante 23 (atualizado: tira a chamada do prefixo) e o 24 (O157 e O158) cobrem as condições.

**A17 · redireção com descritor depois do destino (dimensão nova da matriz, fora da A9: "redireção com número do descritor na posição do destino").**
- Evidência: `hooks/conformidade.py:2059`. Para `SO_DESTINO` (`cp`, `ln`, `install`, `rsync`), o destino é o último argumento que não começa com `-`. Com `2>/dev/null` no fim, o `2` sobra em `args` e vira o destino. `>/dev/null` sem número não tem esse problema. O `mv` (que confere todos os argumentos) e o `ln` (cuja regra do link lê todos os argumentos) também não.
- Sondas no head e na `develop`: S52, S53 e S54 dão 0. Também dão 0 `cp ev/config .git/config 2>e.txt`, `… 2>&1`, `… 3>/dev/null`, `… 9</dev/null`, `cp -rT ev .git 2>/dev/null`, `install ev/config .git/hooks/pre-push 2>/dev/null` e `rsync ev/config .git/config 2>/dev/null`. As mesmas linhas sem a redireção dão 2.
- Caminho de ataque: um agente de qualquer papel, por injeção de prompt ou por hábito (`2>/dev/null` é o sufixo mais comum de um comando), grava `.git/config` ou `.git/hooks/pre-push`. `core.hooksPath` derruba a `R-VERIFY`, e `core.fsmonitor` ou o gancho rodam código. O sandbox do Bash protege `.git/config` só onde está ativo (ADR 0009) e não cobre `.git/hooks/`. O hook é a guarda de toda sessão.
- Severidade: alta, e fácil de alcançar. Não bloqueia este lote pela ordem do dono, porque já está na `develop` e cai fora da A9. **Recomendo cartão de prioridade alta, logo depois do merge.**
- Correção mínima: antes de escolher o destino em `SO_DESTINO`, tirar de `args` as redireções, de preferência pelo leitor que já as separa (`palavras_do_texto` e `redirecao_grava` em `hooks/_comum.py`). Se isso não der, tirar o número de descritor (`[0-9]+`) seguido de uma palavra que começa por `>`, `<`, `>&` ou `<&`, e as palavras `[0-9]+[<>]&?\S*`. Fixtures: S52 a S54 e as variantes acima bloqueiam, e `cp a b 2>/dev/null` (fora do `.git`) libera. Mutante: devolver o `2` ao `args`. Esforço: P. Dono: tech-lead.

**A18 · `$@` e `$*` (dimensão "parâmetro especial", ao lado da A4 da E1.280).**
- Evidência: `hooks/conformidade.py:485`. `VARIAVEL_DO_VALOR` só reconhece nome (`[A-Za-z_]\w*`). `"$1"t` dá 2, mas `"$@"`, que `set --` grava na mesma linha, libera. S55 dá 0, também na `develop`.
- Caminho de ataque: o mesmo da A16, com `set -- .git` no lugar de `: .git`. Severidade: média (forma rara).
- Correção mínima: o destino com `$@`, `$*`, `${@}`, `${*}`, `$#`, `$$`, `$!`, `$-`, `$?` ou `$0`…`$9` não vale como do ambiente (opaco que o hook não calcula: recusa). Fixture: S55 bloqueia. Esforço: P. Dono: tech-lead.

**A19 · referência por nome (dimensão nova: "atributo da variável").**
- Evidência: `hooks/conformidade.py:701`. `declare -n d=_` conta como a atribuição `d=_`, e o hook calcula o literal `_`. O bash resolve `$d` como `$_` (`.git`). S56 dá 0 no head e na `develop`.
- Correção mínima: com `-n` em `declare`, `typeset` ou `local` na linha (também em grupo, como `-gn`), devolver `None` para o nome. Fixture: S56 bloqueia. Severidade: média (forma rara). Esforço: P. Dono: tech-lead.

**A11 · sem mudança (recomendado).** Como nos pareceres anteriores.

**A5 · sem mudança (recomendado, fora do lote).** Cartão novo, decisão ao usuário pelo Jarvis (`R-DECISAO`). A linha acompanhou o deslocamento (`resto_no_git`, `:1494`).

### O que foi conferido e está correto
- **Sem afrouxar:** o delta só acrescenta recusa (acima).
- **Oráculo (EXT-1):** `tests/test_oraculo_v047.py` sem commit no intervalo (`git log c3cde09f..c22624c5 -- tests/test_oraculo_v047.py` vazio).

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Suíte inteira: **sem CI no head** `081473ac` (a branch não tem PR; o brief diz "sem PR"). Rodei no head `tests.test_testes_tocados`, `tests.test_oraculo_v047`, `tests.test_hook_destino_opaco`, `tests.test_conformidade_opaco` e `forge-testes --texto`: 160 testes OK em 315 s (1 pulado pelo sandbox: /proc de outro namespace) e `--texto` rc=0. Quando houver PR, o portão pede o CI verde no head desta revalidação.

Faltaram no ambiente: gitleaks, Semgrep, osv-scanner, zizmor e actionlint (`R-CUSTO`, não instalo). A entrega não traz segredo, dependência nem workflow; a análise foi manual e por sonda.
