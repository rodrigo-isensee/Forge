---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 230dfb01ddde3b7e84d47fdad161c8dbfc93ffc5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61; revalidações E2.82, E2.113, E2.146 e E2.166)

Revalidação por delta da volta 4 (E2.160, A10 da segurança; review E2.166), instância que não fez a entrega. Delta lido: `forge-check parecer delta` deste parecer, intervalo `ee91a8f0..230dfb01` (o do brief, `79899789..230dfb01`, é o mesmo commit 230dfb01 de código), domínio: `changelog.d/v047-catraca-hook-por-script.md`, `docs/engineering/achados-recorrentes.md` (o AR-14 deste parecer), `tests/catraca.py`, `tests/fixtures/catraca-hooks/sondas.json`, `tests/mutantes/v047-catraca-hook-por-script-4.json` e `tests/test_catraca.py`. Código e teste contra a base cb45a962: 316 linhas (`tests/catraca.py` 145+13, `tests/test_catraca.py` 158+0), acima da orientação M14 de 150; um comportamento só (a catraca do hooks.json), o excesso são casos de teste das sondas: o corpo do PR precisa de `teto: excedido, 316 linhas, <motivo>`.
## Achados
- A1 (recomendado) tests/catraca.py:330 · Corrigido em 66a3a9a4: `hooks_contados` conta as chaves (Counter).
- A2 (recomendado) tests/catraca.py:272 · Corrigido em 66a3a9a4: `_sem_aspas` tira só o par de aspas iguais (CH-M14, CH-M15).
- A3 (recomendado) tests/mutantes/v047-catraca-hook-por-script-2.json:79 · Segue aberto: falta a isenta da apagada `ar or cm` (linha_base 277); o `motivo` da isenta existente cita `_opcao_inocua`, que não existe mais.
- A4 (recomendado) tests/catraca.py:258 · Corrigido em ee91a8f0: `b` saiu da lista inócua; `-b` e `-bb` acusam (CH-M22 morreu).
- A5 (recomendado) tests/catraca.py:263 · Segue aberto: `once` está na lista inócua, mas o esquema do Claude Code instalado diz "runs once and is removed after execution"; hoje só hook de skill o honra (sonda S2), sem gatilho no hooks.json do plugin. Tirar `once` da lista fecha a porta.
- A6 (bloqueante) tests/catraca.py:344 · `EVENTOS_DO_HOOK` traz `PreModelSwitch` e `PostModelSwitch`, que não existem no Claude Code 2.1.224 (lista `XU` do binário: 31 eventos). Hook novo nesses eventos passa calado e a carga descarta todos os hooks (S3). Use a lista do binário.
- A7 (recomendado) tests/mutantes/v047-catraca-hook-por-script-4.json:4 · 16 mutantes num arquivo; a prática pede abrir outra spec ao passar de 8 (`-5.json`). Todos aplicam e morrem.

## Sondas
- S1 · hooks.json real, hook conformidade do PreToolUse sem `args`, `"command": "python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0"` · espera: 1 removido · obtido: 1 removido no head ee91a8f0 (sonda `review-S1` do corpus; era 0 no head 66a3a9a4)
- S2 · hooks.json real, `"once": true` no hook conformidade do PreToolUse · espera: 0 removidos (inócuo no runtime atual) · obtido: 0 removidos; no binário do Claude Code instalado o único uso de `once` é o registro de hooks de skill ("Removing one-shot hook ... in skill"), por isso A5 é recomendado
- S3 · hooks.json real com evento novo `PreModelSwitch` (e `PostModelSwitch`), hook `{"type": "command", "command": "true"}` · espera: acusa (`claude plugin validate` 2.1.224: `hooks.PreModelSwitch: Invalid key in record`) · obtido: `erros_de_forma` vazio, 0 removidos

## Parecer
**Reprovado** pelo A6, fuga provada no hooks.json real (régua do dono desta volta). O resto da volta responde ao A10 da segurança como pedido: `erros_de_forma` e `erros_do_hook` seguem a lista (b) do parecer de segurança, falha fechada; NaN e Infinity recusados por `parse_constant`; `regra_hooks` confere a forma do head antes das chaves e a mensagem cita os cinco primeiros erros. S12 a S16 estão no corpus (36 sondas, mínimo 36, alvo único; o hooks.json real sem erro de forma, sonda `real`). O A12 da segurança (`timeout` 0, negativo ou infinito, S17) é dela e o cito sem refazer. A6 nasce da lista (b) do próprio parecer de segurança, que o autor copiou; a correção é a lista do binário, com S18 no corpus (`acrescenta` em `PreModelSwitch`, `fora_do_esquema: true`).

Leitura: funções pequenas, docstring com o porquê, constantes nomeadas; teste do ramo de falha por campo e por forma de arquivo (`test_cada_campo_fora_do_esquema_acusa`, `test_hooks_json_fora_do_esquema_barra`), com o legítimo e o hooks.json real sem erro (checklist 7 e 11).

Guardas: um mutante por linha de guarda mudada (CH-M23 a CH-M38, spec `-4`).

Verificadores citados (rodados aqui no head 230dfb01; a suíte inteira fica no CI do PR):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script-4.json`: CH-M23 a CH-M38 `morreu` (M23, M32 e M35 por erro do teste sob o mutante).
- `bin/forge-mutante --cobertura --base ee91a8f0`: linhas 355, 357, 359, 361, 363, 366, 378, 383, 385, 389, 392, 404 e 405 `coberta`, nenhuma descoberta.
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 14 tests ... OK`.

AR-14 sobe para 6 (A10 da segurança e A6 deste parecer). Commit 230dfb01 (fix), Conventional Commits em português com a etapa.
