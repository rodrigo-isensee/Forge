---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: ee91a8f00ceb1a52bc4ab41bc50a96996cc918e3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61; revalidações E2.82, E2.113 e E2.146)

Revalidação por delta da volta 3 (E2.139), instância que não fez a entrega. Delta lido: `forge-check parecer delta` deste parecer, intervalo `66a3a9a4..ee91a8f0`, domínio: `changelog.d/v047-catraca-hook-por-script.md`, `tests/catraca.py`, `tests/fixtures/catraca-hooks/sondas.json`, `tests/mutantes/v047-catraca-hook-por-script-3.json` e `tests/test_catraca.py`. Código e teste contra a base cb45a962: 213 linhas (`tests/catraca.py` 80+13, `tests/test_catraca.py` 120+0), acima da orientação M14 de 150; um comportamento só (a chave do hook), e o excesso são casos de teste das sondas: o corpo do PR precisa de `teto: excedido, 213 linhas, <motivo>`.

## Achados
- A1 (recomendado) tests/catraca.py:330 · Corrigido em 66a3a9a4: `hooks_contados` conta as chaves (Counter).
- A2 (recomendado) tests/catraca.py:272 · Corrigido em 66a3a9a4: `_sem_aspas` tira só o par de aspas iguais (CH-M14, CH-M15).
- A3 (recomendado) tests/mutantes/v047-catraca-hook-por-script-2.json:79 · Segue aberto: falta a isenta da apagada `ar or cm` (linha_base 277); o `motivo` da isenta existente cita `_opcao_inocua`, que não existe mais.
- A4 (recomendado) tests/catraca.py:258 · Corrigido em ee91a8f0: `b` saiu da lista inócua; `-b` e `-bb` acusam (CH-M22 morreu).
- A5 (recomendado) tests/catraca.py:263 · `once` está na lista inócua, mas o esquema do Claude Code instalado diz "runs once and is removed after execution"; hoje só hook de skill o honra (sonda S2), sem gatilho no hooks.json do plugin. Tirar `once` da lista fecha a porta.

## Sondas
- S1 · hooks.json real, hook conformidade do PreToolUse sem `args`, `"command": "python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0"` · espera: 1 removido · obtido: 1 removido no head ee91a8f0 (sonda `review-S1` do corpus; era 0 no head 66a3a9a4)
- S2 · hooks.json real, `"once": true` no hook conformidade do PreToolUse · espera: 0 removidos (inócuo no runtime atual) · obtido: 0 removidos; no binário do Claude Code instalado o único uso de `once` é o registro de hooks de skill ("Removing one-shot hook ... in skill"), por isso A5 é recomendado

## Parecer
**Aprovado** no domínio do code review. A volta responde ao A8 e ao A9 da segurança, ao A1 do QA e ao A4 deste parecer. Conferido contra o esquema do hook no Claude Code instalado: com `args` o `command` é o executável, sem shell ("exec form"), e `termos_do_hook` o lê inteiro (`args: []` e `command` com espaço viram linha inteira); sem `args` vai ao shell, e só o ASCII imprimível é dividido (quebra de linha, `\r`, tab, U+00A0 e U+0085 acusam); `if`, `async`, `asyncRewake`, `onFailure`, `shell` e campo novo entram na chave em JSON canônico (lista positiva de inócuos, falha fechada). O hooks.json real (18 hooks, todos `python3` com `args`) não muda de leitura.

Leitura: `termos_do_hook` e `campos_extras_do_hook` pequenas, com docstring do motivo; constantes nomeadas com o porquê; a mensagem de `regra_hooks` mostra os campos extras. Testes: `test_command_lido_como_o_claude_code_o_roda` e `test_campo_fora_da_lista_inocua_entra_na_chave` cobrem o ramo de falha de cada guarda nova; o corpus passou a 28 sondas com mínimo de 27 e alvo único (checklist 11); o caso PR565 do corpus foi reescrito na forma exec válida.

Guardas: um mutante por linha mudada (CH-M16 a CH-M22, spec `-3`). AR-12 conferido: as specs `.json` e `-2.json` seguem casando com as linhas depois do commit (todas aplicadas e mortas).

Segurança fora do meu domínio, citada sem refazer: o parecer `docs/security/v047-catraca-hook-por-script.md` segue no head 66a3a9a4 (reprovado A8, A9) até a revalidação dela por delta; a classe fecha com os pareceres no head ee91a8f0. A classe "catraca lê o hook diferente do Claude Code" volta neste pedido (A2, A8, A9, A5): registrada como AR-14.

Verificadores citados (rodados aqui no head ee91a8f0; a suíte inteira fica no CI do PR):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script-3.json`: CH-M16 a CH-M22 `morreu` (CH-M19 por erro do teste sob o mutante).
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script.json tests/mutantes/v047-catraca-hook-por-script-2.json`: CH-M1 a CH-M15 `morreu`.
- `bin/forge-mutante --cobertura --base 66a3a9a4`: linhas 291, 292, 293, 298, 299 e 309 `coberta`, nenhuma descoberta.
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 12 tests ... OK`.

Commits: 802b16ee (fix) e ee91a8f0 (test), Conventional Commits em português com a etapa.
