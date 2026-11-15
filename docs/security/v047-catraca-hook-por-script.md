---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 9811ca977485b35c7c85f6882097a96c8e834141
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-catraca-hook-por-script

Intervalo `origin/develop..9811ca97` (base `cb45a962`), etapa E2.62 do pedido v047. A entrega troca a chave de hook da catraca de (evento, matcher, comando, argumentos sem opção) para (evento, matcher, script), para acabar com o falso positivo do PR 565 (só `-s -E` acrescentados). A ordem do dono (pedido v047, 15/11 07:18) pede comparar "pelo script e pelo evento, e não pela linha inteira". O falso positivo foi resolvido, mas a nova chave aceita hook que não roda mais o script: dá para neutralizar um hook sem ser acusado, o que a base acusava.

## Gatilhos
`R-SEGURANCA`: código de controle (`tests/catraca.py`, que está nos PROTEGIDOS) e a regra que guarda `hooks/hooks.json` (`R-CONFORMIDADE`).

## Achados
- A1 (bloqueante) tests/catraca.py:265 · O script da chave é o 1º termo com sufixo em qualquer posição: `-c pass <script>` ou um termo antes dele (`/dev/null <script>`) faz o hook não rodar o script e a catraca não acusa; a base acusava (S1, S2). Script só como 1º termo que não é opção, sem -c/-m antes.
- A2 (bloqueante) tests/catraca.py:263 · A chave descarta o interpretador: `command` trocado por `true` ou `echo` (args intactos) neutraliza o hook sem acusação; a base acusava (S3, S4). Correção: manter na chave o nome do interpretador normalizado (último trecho do caminho, sem `env`), que segue cobrindo o caso do PR 565.
- A3 (recomendado) tests/catraca.py:276 · A chave ignora `type` e `timeout`; trocar `type` para outro valor neutraliza o hook sem acusação (já era assim na base). Incluir `type` na chave.

## Sondas
- S1 · hooks.json real, hook conformidade do PreToolUse com "args": ["-c","pass","${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py"]; chaves_de_hooks(antes) - chaves_de_hooks(depois) · espera: 1 hook removido (como na base cb45a962) · obtido: [] no head 9811ca97
- S2 · mesmo hook com "args": ["-s","-E","/dev/null","${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py"] · espera: 1 hook removido (como na base) · obtido: []
- S3 · mesmo hook com "command": "true" e args intactos · espera: 1 hook removido (como na base) · obtido: []
- S4 · mesmo hook com "command": "echo", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py"] · espera: 1 hook removido · obtido: []

## Detalhe dos achados
**Pergunta do brief: dá para remover ou trocar um hook sem ser acusado?** Remover e trocar o script, não: `test_script_trocado_barra`, `test_matcher_mudado_barra` e a sonda de controle (args `-s -E x.py`) acusam. Neutralizar, sim, de quatro formas (S1 a S4), todas acusadas na base `cb45a962` (sonda rodada com o `tests/catraca.py` da base: 1 acusação em cada).

**A1** · evidência `tests/catraca.py:263-267`: `script_do_hook` junta `command` e `args` e devolve o primeiro termo que não começa com `-` e termina num sufixo de script, em qualquer posição. Com `-c pass` o interpretador executa `pass` e o script vira só argumento; com um termo antes (`/dev/null`), o interpretador roda esse termo. A docstring promete "o script que o hook roda", e não é. Caminho de ataque: um agente bloqueado pelo hook de conformidade (cenário recorrente na fábrica) edita `hooks/hooks.json` e ajusta o literal de `tests/test_hooks.py:1302` no mesmo PR (troca de literal não reduz asserção, então `regra_controles_enfraquecidos` não acusa); a catraca, única guarda que exige o rótulo do dono, fica muda. Severidade média (resta o review humano). Correção mínima: o script é o primeiro termo depois do interpretador que não começa com `-`; se esse termo não tem sufixo de script, ou se aparece `-c`, `-m` ou `-` antes dele, a chave volta à linha inteira (falha fechada, como já faz o caso sem script). Esforço P. Dono: tech-lead (autor da entrega). Teste: S1 e S2 como casos que barram.

**A2** · evidência `tests/catraca.py:263` e `:276`: o `command` só entra para achar o script e sai da chave. Com `command: true` ou `echo`, o hook sai com 0 e não bloqueia nada. Mesmo caminho de ataque do A1, severidade média. A ordem do dono pede "pelo script e pelo evento"; o defeito do PR 565 foi só o acréscimo de opções, e manter o interpretador normalizado na chave (último trecho do primeiro termo do `command`, pulando `env`) não traz o falso positivo de volta: o próprio `test_mudar_interpretador_opcoes_ou_argumentos_passa` (`/usr/bin/env <interpretador>` e `<interpretador> -I b.py`) continua passando. Se o dono quiser mesmo que a troca de interpretador não acuse, este achado vira risco aceito pela `R-DECISAO`. Esforço P. Dono: tech-lead.

**A3** · `type` fora da chave: `"type": "prompt"` não roda o script. Pré-existente, sem regressão; recomendação. Dono: tech-lead.

**Camada que sobra:** `tests/test_hooks.py:1297` e `:1302` exigem o interpretador e `-s -E` antes do script e barrariam S1 a S4 sozinhos; mas é teste comum, editável no mesmo PR sem rótulo, por isso não substitui a catraca. Os projetos não rodam `regra_hooks` (a regra lê `hooks/hooks.json` do Forge), então o efeito fica no Forge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados localmente: `tests.test_catraca.Hooks` e `tests.test_hook_erro_libera` (17 testes, OK) e as sondas S1 a S4 contra o head e contra a base. Lacuna: a branch não tem PR nem CI (o brief pede sem PR); a suíte inteira não foi conferida. `forge-check proximo v047` não terminou em 120 s neste ambiente.
