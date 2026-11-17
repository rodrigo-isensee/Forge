---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-estado-ilegivel
commit: d2d82ffab0e89a3ac1d1806cca98f51059b6c908
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047, lote A (HOOK-ESTADO-ILEGIVEL-LIBERA)

Revalidação por delta `05d68fce..d2d82ffa` (junção da `origin/develop` `5b1aacd5`, E2.687), pela `forge-check parecer delta`. No domínio, o delta lista `bin/forge-testes`, `docs/hooks.md` e a ADR 0003; tudo o que mudou neles desde `05d68fce` veio da develop (`quem_importa`, as entradas do destino opaco, do heredoc a interpretador e a emenda do SessionStart do `ambiente`), revisado nos pedidos de origem. A contribuição da branch sobre a base nova (`git diff 5b1aacd5 d2d82ffa`) é a mesma das voltas anteriores: `test_estado_ilegivel` em `FORGE_CHECK`, `REAPROVEITAM_O_LOTE` e na regra de `hooks/`, o parágrafo do estado ilegível em `docs/hooks.md` e no item 4 da ADR 0003. `hooks/agentes.py` é idêntico ao de `05d68fce` (`git diff --quiet` rc 0), e a develop não tocou `hooks/agentes.py` nem `hooks/_comum.py` desde `5e74c70e` (`git log` vazio); as mudanças da base em `hooks/` (`ambiente.py`, `conformidade.py`, `parecer.py`, `hooks.json`) não alcançam o leitor do estado. As specs de mutante miram só `hooks/agentes.py`, então nenhuma linha deslocou (AR-12). Fora do domínio no delta: `docs/hooks-fixtures.md`, `tests/test_selo_e_entrega.py`, `tests/test_testes_tocados.py` (lidos: só a contagem 89 e o teste do selo com estado ilegível). Histórico: `bc129c11` reprovado (A1 bloqueante, A2 recomendado); `c3f86d7a`, `b09916f7` e `05d68fce` aprovados; este os substitui.

## Gatilhos
`R-SEGURANCA`: guarda em hook de controle (o teto de agentes, `R-TETO`), com leitura de estado que um agente pode corromper.

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado novo no delta `05d68fce..d2d82ffa`. A resolução da junção em `bin/forge-testes` mantém `test_estado_ilegivel` nas três listas sem perder as entradas da develop (`test_hook_destino_opaco`, `test_conformidade_opaco`, `test_pre_push_patch`, `test_ambiente_hook`); as listas só escolhem módulos de teste a rodar (não decidem permissão), então não há caminho de ataque, e o arquivo compila (`ast.parse` OK). O `quem_importa` e as regras novas de hook que vieram da base são da revisão dos pedidos de origem, não deste item. O texto abaixo é o da volta `c3f86d7a`, ainda válido porque o hook não mudou.

**A1 anterior (RecursionError), resolvido.** `hooks/agentes.py:287-290`: `except EstadoIlegivel: raise` seguido de `except Exception` converte qualquer falha do leitor (do `os.open` ao `json.loads`) em `EstadoIlegivel`; o `EstadoIlegivel` de dentro (link, FIFO, teto) sai sem ser embrulhado. `RecursionError` e `MemoryError` são `Exception`; `KeyboardInterrupt`/`SystemExit` não, e não são entrada que um agente controle pelo arquivo. Revalidado pelo montador de `tests/test_hooks.py` (fixture `estado-ilegivel-profundo-bloqueia` com o estado trocado), em `$TMPDIR`, PreToolUse Agent Explore:
- S1, `"[" * 200000`: espera 2 (R-TETO), obtido 2, arquivo intacto, `erros.log` com `RecursionError`.
- S2, `'{"agentes":' + "[" * 200000`: espera 2, obtido 2, intacto.
- Família da dimensão "conteúdo que não é o registro", além do pedido: objeto aninhado (`'{"a":' * 150000`), `lapides` aninhado fundo, misto lista/objeto (`'[{"a":' * 80000`) e aninhado fechado de 5000 níveis: todos rc 2, intactos. Controle legítimo `{"agentes":[]}`: rc 0.
Prova no corpus: fixture `tests/hooks/agentes/estado-ilegivel-profundo-bloqueia.json` (S1), teste `LerEstado.test_json_aninhado_fundo_e_ilegivel` (S1 e S2), mutantes M16 (volta à captura estreita) e M17 (tira o `raise` do `EstadoIlegivel`); M5 reescrito para a captura nova.

**A2 anterior (fixture selada), resolvido.** `tests/hooks/agentes/estado-ilegivel-selado-bloqueia.json`: brief selado e em dia, estado `"x"`, espera rc 2 com `R-TETO`, sem `R-BRIEF`, arquivo intacto.

**CONFIG_ILEGIVEL** (`hooks/agentes.py:833`): mensagem fixa, numa linha, sem conteúdo do arquivo nem caminho absoluto; o detalhe segue só no `erros.log`. O `try` de `hooks/agentes.py:940-946` já capturava `Exception` (inclusive `RecursionError` de um `.forge/config.json` aninhado), então a configuração não tem a lacuna do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não conferi o CI deste head (sem acesso ao `gh` no ambiente); o portão de merge segue exigindo o CI verde. Nesta volta rodei, no head `d2d82ffa`, `python3 -m unittest tests.test_estado_ilegivel` (9 testes, OK), `tests.test_testes_tocados` (162, OK, 1 skip) e `tests.test_selo_e_entrega.Hook.test_brief_selado_com_estado_ilegivel_recusa_por_r_teto` (OK); o módulo `test_selo_e_entrega` inteiro passou de 900 s nesta máquina e fica com o CI; as sondas acima são da volta `c3f86d7a`, com o hook idêntico. Varreduras de segredo e de workflow não se aplicam ao delta (só a lista de testes e docs; nenhum workflow, segredo ou dependência).
