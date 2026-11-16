---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 66a3a9a4bbcafbd3588f564bd2fc2a81964fe3e6
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-catraca-hook-por-script

Revalidação por delta `40faab23..66a3a9a4` (volta E2.97), etapa E2.114 do pedido v047. A4 a A7 do parecer anterior estão corrigidos: S5 a S7 e a troca de `timeout` acusam no corpus (`tests/fixtures/catraca-hooks/sondas.json`). A releitura de `script_do_hook`, tocado pela volta, contra a documentação oficial dos hooks mostra duas dimensões que a chave não modela, e nelas estão quatro formas de neutralizar o hook de conformidade sem acusação. Três delas a base `cb45a962` acusava. A falha é minha: a matriz das dimensões que entreguei nas voltas anteriores não tinha a forma de execução nem os campos do hook. Estes são os achados da família inteira, juntos.

## Gatilhos
`R-SEGURANCA`: código de controle (`tests/catraca.py`, nos PROTEGIDOS) e a regra que guarda `hooks/hooks.json` (`R-CONFORMIDADE`).

## Achados
- A4 (bloqueante) tests/catraca.py:258 · Corrigido em 66a3a9a4: `I` e `P` saíram da lista inócua; S5 e S5-P acusam no corpus e em test_hook_neutralizado_sem_tirar_o_script_barra.
- A5 (bloqueante) tests/catraca.py:259 · Corrigido em 66a3a9a4: `-X` só com `utf8`, `utf8=0` ou `utf8=1` (junto ou separado); `-W` volta à linha inteira. S6, S6-junto e S6-W acusam.
- A6 (bloqueante) tests/catraca.py:260 · Corrigido em 66a3a9a4: o interpretador é o 1º termo como escrito, e só um `env` do sistema sai da frente. S7 e S7-ponto acusam.
- A7 (recomendado) tests/catraca.py:290 · Corrigido em 66a3a9a4: `timeout` entrou na chave; A7 (`timeout: 1`) acusa no corpus.
- A8 (bloqueante) tests/catraca.py:289 · A chave lê `command` como o shell em toda forma. Com `args` (forma exec) o Claude Code não divide o `command`, e `python3 -s` não existe (S10). Sem `args` (forma sh -c), quebra de linha e espaço não ASCII escapam (S8, S9). A base acusava as três.
- A9 (bloqueante) tests/catraca.py:310 · Campos do hook fora da chave: `"if": "Bash(nunca *)"` faz o hook não rodar, e `"async": true` faz o hook rodar sem bloquear. A catraca não acusa nenhum dos dois (S11), nem `asyncRewake`, `onFailure` e `shell`. Pôr na chave todo campo que não está numa lista fechada de campos inócuos.

## Sondas
- S8 · hook conformidade do PreToolUse sem `args`, `"command": "python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0"`; `bash -c` com Bash `git push --force origin main` · espera: 1 removido (a base dá 1) · obtido: removidos 0; rc do hook 0 (o mesmo comando sem a 2ª linha dá rc=2)
- S9 · igual a S8, com o `command` `python3`, `-s`, `-E` e o script separados por U+00A0 · espera: 1 removido (a base dá 1) · obtido: removidos 0; `bash -c` rc=127
- S10 · com `args` mantido, `"command": "python3 -s"` (também `"'python3'"` e `"python3 -s -E <script>"` com `"args": []`) · espera: 1 removido (a base dá 1) · obtido: removidos 0; o `subprocess.run(["python3 -s", ...])` dá FileNotFoundError
- S11 · hook conformidade do PreToolUse com `"if": "Bash(nunca-casa *)"`, `"async": true` ou `"onFailure": "continue"` acrescentado · espera: 1 removido · obtido: removidos 0 nos três (a base também dá 0)

## Detalhe dos achados
**A4 a A7** · `tests/catraca.py:258-300`: lista `set("bBdEOqsSuv")`, `VALORES_INOCUOS_DE_X`, `ENV_NA_FRENTE` com o 1º termo mantido como escrito, e o `timeout` como 6º elemento da chave. A contagem (`Counter`) também cobre a remoção de um de dois hooks iguais. Rodados aqui: `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`, 10 testes, OK.

**A8** · evidência `tests/catraca.py:289`: `str(hk.get("command", "")).split()` com `_sem_aspas`, e os `args` somados depois. Pela documentação oficial ([hooks, "Exec form and shell form"](https://code.claude.com/docs/en/hooks.md), consultada em 2026-11-15), com `args` presente, mesmo vazio, o `command` é um executável e roda sem shell: "No shell tokenization happens on any platform". Sem `args`, o `command` vai a `sh -c`. A chave lê as duas formas como texto de shell, e Python e shell discordam (AR-13). Os casos são três. (1) Forma exec: `command` `python3 -s`, `'python3'` ou a linha inteira com `args: []` dão a mesma chave do hook real, mas o executável não existe. O hook não roda e, sem `onFailure`, a ação segue (S10). (2) Forma shell: `str.split()` corta em `\n`, e `CONTROLE_DO_SHELL` (`:261`) não tem `\n`, então `…conformidade.py⏎exit 0` roda o hook e sai 0 (S8). (3) `str.split()` também corta em U+00A0, U+0085, `\x1c`-`\x1f`, `\v` e `\f`, que o shell não corta: o shell recebe uma palavra só, o comando não existe e o rc é 127 (S9). Caminho de ataque: o do parecer anterior. Um agente barrado pelo hook de conformidade edita `hooks/hooks.json` no PR, e a catraca, a única guarda que pede rótulo do dono, fica muda. A base `cb45a962` acusava as três formas porque o `command` inteiro estava na chave. Os casos legítimos de `tests/test_catraca.py:326-327` e a sonda `PR565` (`sondas.json:20`, `command` `/usr/bin/env python3` com `args`) descrevem um hook que não roda na forma exec. Severidade média (resta o review humano). Correção mínima: (a) com a chave `args` presente, os termos são `[command] + args`, sem dividir o `command` e sem tirar aspas; (b) sem `args`, a linha inteira volta como chave (falha fechada) quando o `command` tem qualquer caractere fora do ASCII imprimível (0x20 a 0x7E); senão, divide-se só em espaço; (c) corrigir os legítimos para a forma que roda: exec com `command` `env` ou `/usr/bin/env` e `python3` no 1º item de `args`, ou forma shell sem `args`; (d) entrar no corpus S8, S9 e S10 (as três grafias). Esforço P. Dono: tech-lead.

**A9** · evidência `tests/catraca.py:310`: a chave é evento, matcher, tipo, interpretador, script e `timeout`, e os outros campos do hook ficam fora. Pela mesma documentação, quatro campos mudam o que o hook faz. `if` filtra quando o hook roda, e uma regra que nunca casa o desliga. `async: true` roda o hook em segundo plano sem bloquear, e o `timeout` deixa de valer. `asyncRewake` também roda o hook em segundo plano. `onFailure` decide se a ação segue quando o hook falha. `shell` troca o shell da forma sem `args`. S11 mostra 0 removidos com `if`, `async` e `onFailure`. A base também não acusava, então não é regressão. Mesmo assim, o objetivo do item é acusar o hook neutralizado sem tirar o script, e o caminho de ataque é o do A8. É bloqueante pela mesma régua do A4. Correção mínima: um conjunto fechado de campos que não entram na chave, `statusMessage` e `once`, além dos lidos à parte (`type`, `command`, `args`, `timeout`). Qualquer outro campo entra na chave como par nome e valor, em JSON canônico: `if`, `async`, `asyncRewake`, `onFailure`, `shell` e os campos que o Claude Code criar depois. Assim o campo novo falha fechado (lista positiva, AR-3). Entram no corpus `if`, `async`, `asyncRewake`, `onFailure` e `shell`. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados aqui: os 10 testes citados no A4 a A7, as sondas S8 a S11 contra `tests/catraca.py` do head e da base `cb45a962`, e o `hooks/conformidade.py` real por `bash -c` e por `subprocess.run` em forma exec. Fonte da semântica de `args`, `if`, `async` e `onFailure`: a documentação oficial dos hooks, lida em 2026-11-15. Lacuna: a branch não tem PR nem CI (o brief pede sem PR), então a suíte inteira não foi conferida. Também não rodei o Claude Code: o rc que o hook neutralizado daria lá vem da documentação, não de uma execução.
