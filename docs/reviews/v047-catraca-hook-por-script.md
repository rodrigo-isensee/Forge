---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: d896a0c2e5def6f47841e5cc1397b63bd6b92cff
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61; revalidações E2.82, E2.113, E2.146, E2.166, E2.173 e E2.250)

Revalidação por delta da volta 7 (E2.204, CH-M30 do QA; review E2.250) até o head b32853e6, código em d896a0c2. Delta lido: `forge-check parecer delta` deste parecer, intervalo `24256248..b32853e6`, domínio: `tests/catraca.py` e `tests/test_catraca.py`. O hunk de `tests/catraca.py` no delta (PROMOCOES, modo `degrau`) veio da develop pelo merge 3bf73172 (#567; `git diff 3bf73172 d896a0c2` não toca `tests/catraca.py`) e não é do item; do item só entram 6 linhas de teste. Código e teste contra a base 4138445e: 329 linhas (`tests/catraca.py` 148+13, `tests/test_catraca.py` 168+0), o PR segue precisando de `teto: excedido, 329 linhas, <motivo>`.

Revalidação anterior (E2.173): delta das voltas 5 e 6 (E2.171, A12 da segurança; E2.172, A6 deste parecer; review E2.173), instância que não fez a entrega. Delta lido: `forge-check parecer delta` deste parecer, intervalo `230dfb01..24256248`, domínio: `changelog.d/v047-catraca-hook-por-script.md`, `docs/engineering/achados-recorrentes.md`, `tests/catraca.py`, `tests/fixtures/catraca-hooks/sondas.json`, `tests/mutantes/v047-catraca-hook-por-script-5.json` e `tests/test_catraca.py`. Código e teste contra a base cb45a962: 323 linhas (`tests/catraca.py` 148+13, `tests/test_catraca.py` 162+0), acima da orientação M14 de 150; um comportamento só (a catraca do hooks.json), o excesso são casos de teste das sondas: o corpo do PR precisa de `teto: excedido, 323 linhas, <motivo>`.
## Achados
- A1 (recomendado) tests/catraca.py:330 · Corrigido em 66a3a9a4: `hooks_contados` conta as chaves (Counter).
- A2 (recomendado) tests/catraca.py:272 · Corrigido em 66a3a9a4: `_sem_aspas` tira só o par de aspas iguais (CH-M14, CH-M15).
- A3 (recomendado) tests/mutantes/v047-catraca-hook-por-script-2.json:79 · Segue aberto: falta a isenta da apagada `ar or cm` (linha_base 277); o `motivo` da isenta existente cita `_opcao_inocua`, que não existe mais.
- A4 (recomendado) tests/catraca.py:258 · Corrigido em ee91a8f0: `b` saiu da lista inócua; `-b` e `-bb` acusam (CH-M22 morreu).
- A5 (recomendado) tests/catraca.py:263 · Segue aberto: `once` na lista inócua; só hook de skill o honra no 2.1.224 (sonda S2), sem gatilho no hooks.json do plugin. Tirar `once` da lista fecha a porta.
- A6 (bloqueante) tests/catraca.py:345 · Corrigido em 24256248: `EVENTOS_DO_HOOK` é igual, como conjunto, à lista de 31 eventos do binário do Claude Code 2.1.224 (sonda S5); `PreModelSwitch` acusa fora do esquema (S18 no corpus, CH-M42 morreu).
- A7 (recomendado) tests/mutantes/v047-catraca-hook-por-script-4.json:4 · Corrigido em 3f92e62f/24256248: os mutantes novos foram para a spec `-5.json` (4 mutantes).
- A8 (recomendado) tests/test_catraca.py:1385 · A docstring de `CorpusDasSondasDeHook` diz "S1 a S17", mas o corpus já traz S18; troque para "S1 a S18".

## Sondas
- S1 · hooks.json real, hook conformidade do PreToolUse sem `args`, `"command": "python3 -s -E ${CLAUDE_PLUGIN_ROOT}/hooks/conformidade.py\nexit 0"` · espera: 1 removido · obtido: 1 removido no head ee91a8f0 (sonda `review-S1` do corpus)
- S2 · hooks.json real, `"once": true` no hook conformidade do PreToolUse · espera: 0 removidos (inócuo no runtime atual) · obtido: 0 removidos (A5 recomendado)
- S3 · hooks.json real com evento novo `PreModelSwitch`, hook `{"type": "command", "command": "true"}` · espera: acusa (`claude plugin validate` 2.1.224: `hooks.PreModelSwitch: Invalid key in record`) · obtido: acusa fora do esquema no head 24256248 (sonda S18; era vazio no 230dfb01)
- S4 · plugin mínimo com `timeout` 0 e -1 em `claude plugin validate . --strict` (2.1.224) · espera: `Too small: expected number to be >0` · obtido: essa mensagem; `erros_de_forma` acusa 0, 0.0, -1 e `1e400` e aceita 0.5, 600 e 1e308 (A12 da segurança confere com a carga)
- S5 · lista `["PreToolUse",...,"MessageDisplay"]` lida de `/usr/local/bin/claude` 2.1.224 contra `catraca.EVENTOS_DO_HOOK` · espera: mesmo conjunto · obtido: 31 eventos, diferença simétrica vazia

## Parecer
**Aprovado** no head b32853e6 (código em d896a0c2). Volta 7: o teste novo (tests/test_catraca.py:456) afirma, por igualdade, que `NaN`, `Infinity` e `-Infinity` em campo sem validação de tipo (chave solta na raiz e `foo` no hook) só acusam pela guarda da constante (tests/catraca.py:351); com o mutante CH-M30 (`return 0`) a lista vem vazia. Teste de comportamento do ramo de falha, não de texto da fonte (checklist 7). Nenhum achado novo; A3, A5 e A8 seguem recomendados.

Volta 7, rodado aqui: `python3 -m unittest tests.test_catraca.Hooks.test_cada_campo_fora_do_esquema_acusa` `Ran 1 test ... OK` no head; com CH-M30 aplicado (cópia em $TMPDIR) `FAILED`, `Lists differ: [] != ['JSON ilegível (NaN não é JSON)']`: CH-M30 morreu, o que confirma o parecer do QA E2.217 (b32853e6).

Anterior (E2.173), **aprovado** no head 24256248. A6 corrigido com a lista do binário (S5) e S18 no corpus; o A12 da segurança (`timeout` finito e maior que 0, S17) é dela e o cito sem refazer, com a leitura conferida contra a carga (S4). O `elif` só roda com número já validado (bool e texto saem no ramo anterior), então `math.isfinite` não recebe tipo errado. O corpus troca `Infinity` por `1e400` só no texto do `depois` e afirma que o hooks.json real não tem `Infinity` (checklist 11). Recomendados abertos (A3, A5, A8) não bloqueiam.

Leitura: guarda pequena e com o porquê no comentário; teste do ramo de falha por valor (`timeout zero`, `zero real`, `negativo`, `1e400`) e o legítimo sem erro (checklist 7).

Guardas: um mutante por linha de guarda mudada (CH-M39 a CH-M42, spec `-5`).

Verificadores (rodados aqui no head 24256248; a suíte inteira fica no CI do PR):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script-5.json`: CH-M39, CH-M40 e CH-M41 (tests/catraca.py:366) e CH-M42 (tests/catraca.py:345) `morreu`.
- `bin/forge-mutante --cobertura --base 230dfb01`: `coberta · tests/catraca.py:366` (CH-M39 a CH-M41), nenhuma descoberta.
- `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook`: `Ran 14 tests ... OK`.

AR-14 fica em 6: o A6 já estava contado; nenhuma classe nova repetida nesta volta. Commits 3f92e62f e 24256248 (fix), Conventional Commits em português com a etapa.
