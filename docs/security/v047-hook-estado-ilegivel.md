---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: bc129c11739dbaa9a3d0d12951adcbb7fe9bcae9
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047, lote A (HOOK-ESTADO-ILEGIVEL-LIBERA)

Intervalo `origin/develop..bc129c11` (base `7fff73e4`), classe C, `hooks/agentes.py`. Plano: `docs/security/v047-serie-hooks-pos-550.md`, lote A (R1 a R6).

## Gatilhos
`R-SEGURANCA`: guarda em hook de controle (o teto de agentes, `R-TETO`), com leitura de estado que um agente pode corromper.

## Achados
- A1 (bloqueante) hooks/agentes.py:286 · agentes.json com JSON aninhado fundo (~200 KB de `[`, abaixo do teto de 1 MiB) lança RecursionError, que não é OSError/ValueError: escapa do ler_estado e do except EstadoIlegivel (:960), o executar libera e o disparo sai com rc 0, sem teto; R-TETO
- A2 (recomendado) tests/hooks/agentes/estado-ilegivel-texto-bloqueia.json:1 · falta a fixture estado-ilegivel-selado-bloqueia do plano (disparo com brief selado e estado ilegível: R-TETO, não R-BRIEF); o caminho no código é o mesmo do Explore, mas fica sem prova própria

## Sondas
- S1 · agentes.json = "[" repetido 200000 vezes; PreToolUse Agent Explore, montador de tests/test_hooks.py · espera: 2 (R-TETO) · obtido: 0, erros.log "agentes RecursionError: maximum recursion depth exceeded"
- S2 · agentes.json = '{"agentes":' seguido de "[" repetido 200000 vezes; mesmo disparo · espera: 2 (R-TETO) · obtido: 0, erros.log RecursionError

## Detalhe dos achados
**A1.** Evidência: `hooks/agentes.py:286` captura só `(OSError, ValueError)` em torno do `json.loads`; o decodificador da biblioteca padrão lança `RecursionError` (subclasse de `RuntimeError`) com aninhamento fundo, e isso cabe em bem menos que `LIMITE_DO_ESTADO`. A exceção atravessa o `except EstadoIlegivel` de `hooks/agentes.py:960` e chega ao `executar` (`hooks/_comum.py:2839`), que, sem marcador crítico no `agentes`, libera. Controles no mesmo montador: `"x"` dá rc 2 com a mensagem do R-TETO; `{}` dá rc 0.
Caminho de ataque: o mesmo G2 do plano. Um agente que consegue escrever o `agentes.json` (no clone, até a AGENTES-JSON-SEM-GUARDA) troca o `"x"` que agora recusa por um arquivo aninhado e volta a disparar sem teto, sem duplicado e sem Z10; o arquivo nem é regravado, então o furo persiste até o dono olhar o `erros.log`. É exatamente a dimensão "conteúdo que não é o registro" da matriz do R1, numa forma que a lista de exceções não cobre.
Severidade: média (ator interno, controle de recurso, sem vazamento).
Correção mínima: em `ler_estado`, capturar também `RecursionError` (ou, mais simples e fechado, `Exception` em torno do `os.open` ao `json.loads`) e converter em `EstadoIlegivel`; fixture `estado-ilegivel-profundo-bloqueia` (estado `"[" * 200000`, Explore, rc 2, `R-TETO: registro de agentes ilegível`, arquivo intacto) e um mutante que tira o `RecursionError` da captura. Esforço: P. Dono: o autor do lote A (tech-lead).
**A2.** Recomendação ao `qa-engineer`: a linha `estado-ilegivel-selado-bloqueia` da tabela do plano (lote A) não tem fixture nem teste em `tests/test_estado_ilegivel.py`. Não bloqueia: o código recusa pelo mesmo ramo (`recusa is None` e `atualizar_estado` lança).

## Conferido sem achado
- R1: `O_NOFOLLOW | O_NONBLOCK` com `fstat`/`S_ISREG` (link, pasta e FIFO recusam), teto de 1 MiB lido com `read(LIMITE + 1)`, raiz objeto, `agentes` e `lapides` listas; ausente vale `{"agentes": []}`.
- R2: mensagem numa linha, abaixo de 200 caracteres, sem conteúdo do arquivo; o detalhe vai só ao `erros.log` (o `JSONDecodeError` cita posição, não o texto). R-BRIEF segue antes (`errointerno-estado-corrompido-sem-brief-bloqueia`).
- R3: nenhum evento grava com o estado ilegível (a exceção sai antes do `gravar_json`); `SubagentStart` e `SubagentStop` saem com 0.
- R4: exceção em `fixar_estado_do_clone` recusa com R-TETO depois do R-BRIEF; o `return False` legítimo segue liberando.
- R5: `.forge/config.json` ilegível ou com raiz não objeto (e o erro de `hook.projeto`) recusa com a mensagem da configuração; valor inválido de chave cai no padrão do modelo, sem derrubar o hook.
- R6: ADR 0003 item 4 e `docs/hooks.md` no diff.
- Elementos de `agentes` que não são objeto são descartados por `vigentes`; equivale a o agente gravar `{"agentes": []}`, que é a guarda de escrita (AGENTES-JSON-SEM-GUARDA), fora deste lote.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não conferi o CI deste head (sem acesso ao `gh` no ambiente). Rodei `tests/test_estado_ilegivel.py` (8 testes, OK) e as sondas S1 e S2 pelo montador de `tests/test_hooks.py`, em `$TMPDIR`. Varreduras de segredo e de workflow não se aplicam ao diff (só hook, testes e docs).
