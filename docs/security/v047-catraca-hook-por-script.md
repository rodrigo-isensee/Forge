---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 40faab231edc2a7a4a74e3e60841b10770de18a1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-catraca-hook-por-script

Revalidação por delta `e8499ceb..40faab23` (volta E2.67), etapa E2.83 do pedido v047. A volta põe na chave do hook o tipo e o interpretador e só deixa fora uma lista de opções do Python tidas como inócuas. A1 a A3 do parecer anterior (head `9811ca97`) estão corrigidos: S1 a S4 e a troca de `type` voltam a acusar. Mas a lista nova de opções inócuas e o interpretador reduzido ao último trecho do caminho abrem outras três formas de neutralizar o hook sem acusação, duas delas acusadas na base `cb45a962`.

## Gatilhos
`R-SEGURANCA`: código de controle (`tests/catraca.py`, nos PROTEGIDOS) e a regra que guarda `hooks/hooks.json` (`R-CONFORMIDADE`).

## Achados
- A1 (bloqueante) tests/catraca.py:281 · Corrigido em 40faab23: `-c`, `-m`, `-` e termo antes do script levam a chave à linha inteira; S1 e S2 acusam (fixture sondas.json e test_hook_neutralizado_sem_tirar_o_script_barra).
- A2 (bloqueante) tests/catraca.py:281 · Corrigido em 40faab23: o interpretador entra na chave; S3 (`true`) e S4 (`echo`) acusam. Resta a forma do A6.
- A3 (recomendado) tests/catraca.py:278 · Corrigido em 40faab23: `type` na chave; `"type": "prompt"` acusa. `timeout` segue fora (A7).
- A4 (bloqueante) tests/catraca.py:258 · `I` e `P` estão na lista inócua, mas tiram a pasta do script do sys.path: hooks/conformidade.py:31 importa `parecer` e sai rc=1 (erro que não bloqueia) e a catraca não acusa (S5). Tirar `I` e `P` da lista; a fixture PR565 e test_catraca.py:327 usam `-I`.
- A5 (bloqueante) tests/catraca.py:259 · `-X` e `-W` aceitam qualquer valor: `-X pycache_prefix=<pasta>` com um .pyc forjado (unchecked-hash) troca o `json` e o hook sai rc=0 sem decidir (S6); a base acusava a forma em dois termos. Aceitar só `-X utf8` (`utf8`, `utf8=0`, `utf8=1`); `-W` fora.
- A6 (bloqueante) tests/catraca.py:281 · O interpretador na chave é só o último trecho do caminho: `command` trocado por `${CLAUDE_PLUGIN_ROOT}/hooks/python3` (arquivo do repo que sai 0) não acusa; a base acusava (S7). Manter o 1º termo como escrito, tirando só um `env` à frente.
- A7 (recomendado) tests/catraca.py:296 · `timeout` fora da chave: baixá-lo pode fazer o hook estourar o prazo, o que não bloqueia; sem sonda que prove o tempo do hook real. Incluir `timeout` na chave ou acusar só quando ele diminui.

## Sondas
- S5 · hooks/ em $TMPDIR com .forge/versao; `python3 -s -E -I hooks/conformidade.py` com Bash `git push --force origin main`; chaves_de_hooks com args `-s -E -I <script>` · espera: rc=2 ou 1 removido · obtido: ModuleNotFoundError, rc=1; removidos 0 (idem `-P`)
- S6 · mesmo ambiente; .pyc unchecked-hash de `os._exit(0)` no lugar do json sob `<pasta>`; `python3 -s -E -X pycache_prefix=<pasta> hooks/conformidade.py` · espera: rc=2 ou 1 removido · obtido: rc=0; removidos 0 (1 na base em dois termos)
- S7 · hooks.json real, hook conformidade do PreToolUse com "command": "${CLAUDE_PLUGIN_ROOT}/hooks/python3" (também "./python3") · espera: 1 hook removido (como na base cb45a962) · obtido: removidos 0 no head, 1 na base

## Detalhe dos achados
**A1 a A3** · `tests/catraca.py:273-288`: o laço só pula opções da lista; qualquer outra opção, termo sem sufixo de script ou interpretador que não começa com `python` volta à linha inteira sem interpretador (falha fechada). A fixture `tests/fixtures/catraca-hooks/sondas.json` roda S1 a S4 e A3 sobre o `hooks/hooks.json` real; `tests.test_catraca.Hooks`, `CorpusDasSondasDeHook` e `tests.test_hook_erro_libera` rodados aqui: 19 testes, OK.

**A4** · evidência `tests/catraca.py:258` (`set("bBdEIOPqsSuv")`, comentário "não ... tiram o script do lugar") e `hooks/conformidade.py:31-32` (`import parecer`, `from _comum import`). `-I` implica `-P`, que não põe a pasta do script no `sys.path`; todo hook do Forge que importa os vizinhos cai no `ModuleNotFoundError`, sai rc=1, e no Claude Code saída diferente de 2 não bloqueia. Caminho de ataque: o mesmo do parecer anterior (agente barrado pelo hook de conformidade acrescenta `-I` ao `args` de `hooks/hooks.json` e ajusta o literal de `tests/test_hooks.py`); a catraca, única guarda com rótulo do dono, fica muda e a guarda inteira desliga. A base também não acusava (filtrava toda opção), mas a lista nova declara `-I` inócua e a fixture `PR565` o consagra como legítimo. Severidade média (resta o review humano). Correção mínima: lista `set("bBdEOqsSuv")`; trocar `-I` por outra opção da lista em `sondas.json` (`PR565`) e em `tests/test_catraca.py:327`; caso novo que barra com `-I` e `-P`. Esforço P. Dono: tech-lead.

**A5** · evidência `tests/catraca.py:259` e `:270` (`op[:2] in OPCOES_COM_VALOR_DO_PYTHON` aceita qualquer valor, junto ou separado). `-X pycache_prefix` faz o Python carregar bytecode de uma pasta escolhida; um .pyc com invalidação `unchecked-hash` não é conferido contra a fonte, então o `json` da biblioteca padrão, importado em `hooks/conformidade.py:17`, vira `os._exit(0)` (S6, rodado com o hook real: rc=0 onde o normal é rc=2). Exige commitar o .pyc no PR, visível no diff, mas a catraca não acusa; a base acusava `-X pycache_prefix=p` em dois termos (o valor ficava na chave). `-W error` transforma qualquer aviso em exceção (rc=1, não bloqueia); sem sonda, fica junto pela mesma correção. Correção mínima: `-X` só com o valor `utf8`, `utf8=0` ou `utf8=1` (junto, `-Xutf8`, ou separado); `-W` sai da lista (volta à linha inteira). Esforço P. Dono: tech-lead.

**A6** · evidência `tests/catraca.py:281` (`_ultimo_trecho(interp)`). Fui eu que sugeri o último trecho no A2 do parecer anterior; a sonda S7 mostra que ele deixa trocar o `python3` do sistema por um arquivo do próprio repositório chamado `python3` que sai 0, sem acusação; a base acusava (o `command` inteiro estava na chave). Caminho de ataque igual ao do A4, com um arquivo novo no PR. Correção mínima: o interpretador na chave é o 1º termo como escrito, depois de tirar um `env` (com ou sem caminho) à frente; `python3` → `/usr/bin/python3` passa a acusar (falso positivo raro, falha fechada) e o caso do PR 565 (`-s -E` acrescentados) e `/usr/bin/env python3` → `python3` seguem passando. Esforço P. Dono: tech-lead.

**A7** · `timeout` é o prazo do hook; estourar não bloqueia. Sem medir o tempo do hook real, sem caminho provado: recomendação. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados localmente: os 19 testes citados no A1 a A3 e as sondas S5 a S7 contra o head e contra o `tests/catraca.py` da base `cb45a962`. Lacuna: a branch não tem PR nem CI (o brief pede sem PR); a suíte inteira não foi conferida.
