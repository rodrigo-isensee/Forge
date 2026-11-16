---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: b09916f74ca84dea220e316c36a0a960440a93ce
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047, lote A (HOOK-ESTADO-ILEGIVEL-LIBERA)

Revalidação por delta `c3f86d7a..b09916f7` (junção da `origin/develop` `bf475209` ao lote A, E2.133), pela `forge-check parecer delta`, sem o que veio da base. No domínio, só `bin/forge-testes`: a resolução do conflito na tupla `FORGE_CHECK` (linhas 99-105) une os dois lados (`test_estado_ilegivel` da branch; `test_conferida_por_branch` e `test_conferencia_dois_pedidos` da develop). `hooks/agentes.py` é idêntico ao de `c3f86d7a` (`git diff --quiet` rc 0); as specs de mutante da branch (`-`, `-2`, `-3`) miram só esse arquivo, então não há linha deslocada (AR-12). Histórico: `bc129c11` reprovado (A1 bloqueante, A2 recomendado); `c3f86d7a` aprovado; este o substitui.

## Gatilhos
`R-SEGURANCA`: guarda em hook de controle (o teto de agentes, `R-TETO`), com leitura de estado que um agente pode corromper.

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado novo no delta `c3f86d7a..b09916f7`. A tupla resolvida tem 80 nomes, sem repetição, e cada um tem `tests/<nome>.py` na árvore; a lista só escolhe módulos de teste a rodar (não decide permissão), então não há caminho de ataque. O texto abaixo é o da volta `c3f86d7a`, ainda válido porque o hook não mudou.

**A1 anterior (RecursionError), resolvido.** `hooks/agentes.py:287-290`: `except EstadoIlegivel: raise` seguido de `except Exception` converte qualquer falha do leitor (do `os.open` ao `json.loads`) em `EstadoIlegivel`; o `EstadoIlegivel` de dentro (link, FIFO, teto) sai sem ser embrulhado. `RecursionError` e `MemoryError` são `Exception`; `KeyboardInterrupt`/`SystemExit` não, e não são entrada que um agente controle pelo arquivo. Revalidado pelo montador de `tests/test_hooks.py` (fixture `estado-ilegivel-profundo-bloqueia` com o estado trocado), em `$TMPDIR`, PreToolUse Agent Explore:
- S1, `"[" * 200000`: espera 2 (R-TETO), obtido 2, arquivo intacto, `erros.log` com `RecursionError`.
- S2, `'{"agentes":' + "[" * 200000`: espera 2, obtido 2, intacto.
- Família da dimensão "conteúdo que não é o registro", além do pedido: objeto aninhado (`'{"a":' * 150000`), `lapides` aninhado fundo, misto lista/objeto (`'[{"a":' * 80000`) e aninhado fechado de 5000 níveis: todos rc 2, intactos. Controle legítimo `{"agentes":[]}`: rc 0.
Prova no corpus: fixture `tests/hooks/agentes/estado-ilegivel-profundo-bloqueia.json` (S1), teste `LerEstado.test_json_aninhado_fundo_e_ilegivel` (S1 e S2), mutantes M16 (volta à captura estreita) e M17 (tira o `raise` do `EstadoIlegivel`); M5 reescrito para a captura nova.

**A2 anterior (fixture selada), resolvido.** `tests/hooks/agentes/estado-ilegivel-selado-bloqueia.json`: brief selado e em dia, estado `"x"`, espera rc 2 com `R-TETO`, sem `R-BRIEF`, arquivo intacto.

**CONFIG_ILEGIVEL** (`hooks/agentes.py:833`): mensagem fixa, numa linha, sem conteúdo do arquivo nem caminho absoluto; o detalhe segue só no `erros.log`. O `try` de `hooks/agentes.py:940-946` já capturava `Exception` (inclusive `RecursionError` de um `.forge/config.json` aninhado), então a configuração não tem a lacuna do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não conferi o CI deste head (sem acesso ao `gh` no ambiente); o portão de merge segue exigindo o CI verde. Nesta volta rodei `tests.test_testes_tocados` e `tests.test_estado_ilegivel` no head `b09916f7` (OK, 1 skip); as sondas acima são da volta `c3f86d7a`, com o hook idêntico. Varreduras de segredo e de workflow não se aplicam ao delta (só hook, fixtures, testes e docs).
