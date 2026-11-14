---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: c3f86d7ac652408171ad3f356f4582161e6d9805
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047, lote A (HOOK-ESTADO-ILEGIVEL-LIBERA)

Revalidação por delta `bc129c11..c3f86d7a` (base `7fff73e4`), classe C, `hooks/agentes.py`, pela `forge-check parecer delta`. Plano: `docs/security/v047-serie-hooks-pos-550.md`, lote A (R1 a R6). O parecer anterior (`bc129c11`, reprovado: A1 bloqueante, A2 recomendado) fica substituído por este.

## Gatilhos
`R-SEGURANCA`: guarda em hook de controle (o teto de agentes, `R-TETO`), com leitura de estado que um agente pode corromper.

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado novo no delta.

**A1 anterior (RecursionError), resolvido.** `hooks/agentes.py:287-290`: `except EstadoIlegivel: raise` seguido de `except Exception` converte qualquer falha do leitor (do `os.open` ao `json.loads`) em `EstadoIlegivel`; o `EstadoIlegivel` de dentro (link, FIFO, teto) sai sem ser embrulhado. `RecursionError` e `MemoryError` são `Exception`; `KeyboardInterrupt`/`SystemExit` não, e não são entrada que um agente controle pelo arquivo. Revalidado pelo montador de `tests/test_hooks.py` (fixture `estado-ilegivel-profundo-bloqueia` com o estado trocado), em `$TMPDIR`, PreToolUse Agent Explore:
- S1, `"[" * 200000`: espera 2 (R-TETO), obtido 2, arquivo intacto, `erros.log` com `RecursionError`.
- S2, `'{"agentes":' + "[" * 200000`: espera 2, obtido 2, intacto.
- Família da dimensão "conteúdo que não é o registro", além do pedido: objeto aninhado (`'{"a":' * 150000`), `lapides` aninhado fundo, misto lista/objeto (`'[{"a":' * 80000`) e aninhado fechado de 5000 níveis: todos rc 2, intactos. Controle legítimo `{"agentes":[]}`: rc 0.
Prova no corpus: fixture `tests/hooks/agentes/estado-ilegivel-profundo-bloqueia.json` (S1), teste `LerEstado.test_json_aninhado_fundo_e_ilegivel` (S1 e S2), mutantes M16 (volta à captura estreita) e M17 (tira o `raise` do `EstadoIlegivel`); M5 reescrito para a captura nova.

**A2 anterior (fixture selada), resolvido.** `tests/hooks/agentes/estado-ilegivel-selado-bloqueia.json`: brief selado e em dia, estado `"x"`, espera rc 2 com `R-TETO`, sem `R-BRIEF`, arquivo intacto.

**CONFIG_ILEGIVEL** (`hooks/agentes.py:833`): mensagem fixa, numa linha, sem conteúdo do arquivo nem caminho absoluto; o detalhe segue só no `erros.log`. O `try` de `hooks/agentes.py:940-946` já capturava `Exception` (inclusive `RecursionError` de um `.forge/config.json` aninhado), então a configuração não tem a lacuna do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não conferi o CI deste head (sem acesso ao `gh` no ambiente); o portão de merge segue exigindo o CI verde. Rodei `tests/test_estado_ilegivel.py` (9 testes, OK) e as sondas acima. Varreduras de segredo e de workflow não se aplicam ao delta (só hook, fixtures, testes e docs).
