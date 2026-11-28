---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v0479-vermelho-evals
commit: 05ee66764cc0008dfd77dd7481e9bec525ae0a19
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 E13.40 (retomada do VERMELHO-TESTS-EVALS, E13.32)

Revalidação. Rodada anterior: aprovado em `8b5d4a5f` (v0478 E48.2, 20/11). Delta lido com `forge-check parecer delta docs/reviews/v0479-vermelho-evals.md`: intervalo `8b5d4a5f..05ee6676`, no domínio `bin/forge-testes` e `tests/test_testes_tocados.py`. Os commits são `bdc7eb53` (a asserção no lugar do `next()`/índice nos testes do vermelho, só teste) e o merge `05ee6676` da develop `9479650b`.

## Achados
- A1 (bloqueante) bin/forge-testes:1287 · o patch muda a linha `modulos_pedidos = [m.removeprefix("tests.") ...]`, que é o `de` de M1 e M2 em tests/mutantes/forge-testes-modulos-nome.json. Sem alinhar a spec, o CI do head falha: test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes.

## Sondas

## Parecer
Reprovado, só pelo A1: o CI do `Revisar-sha` está vermelho.

O merge não perdeu nada. O patch do item em `bin/forge-testes`, `tests/test_testes_tocados.py` e `tests/mutantes/` tem as mesmas linhas `+`/`-` antes do merge (`004ce869..f913faea`) e depois dele (`9479650b..05ee6676`), sem diferença no `diff`. Os ajudantes de que o patch depende (`arquivo_do_modulo` e `nome_do_modulo` na l. 468-479, `MODULO_DE_TESTE`) continuam na árvore mesclada. O #960 não toca `NOME_DE_MODULO`, `TESTE_DO_DIFF`, `testes_da_base`, `da_base` nem `vermelho()`.

O patch convive com o plano do #960. O `--vermelho` volta na l. 1315, antes de `custo_e_catraca` e do `LIMITE_LOCAL` (l. 1346-1353), que valem só para o plano dirigido e para o `--afetados`. A l. 1271 já recusa `--vermelho` junto de `--afetados`. A catraca e o teste de custo entram pelo `planejar` do modo normal, e o vermelho não passa por ali.

Ferramentas citadas, sem rodar a suíte de novo (`R-REVIEW`):
- os 5 testes do item, rodados na árvore mesclada com ambiente limpo e `python3 -I`: `Ran 5 tests ... OK`;
- `forge-mutante --processos 1 tests/mutantes/vermelho-tests-evals.json` no `05ee66764cc0`: M1 a M11 morreram;
- `forge-mutante --cobertura --base 9479650b`: toda condição mudada está coberta (M3, M8, M10, M11) ou isenta com motivo (as l. 898 e 940 da base).

CI (`gh pr checks 970`, run 46169579448 no `05ee66764cc0008dfd77dd7481e9bec525ae0a19`): `suíte (python 3.12, parte 4/5)` falhou, e `bateria` falhou por consequência (`partes: failure`). Os outros checks passaram. A causa é o A1: o teste `ConferirTodas` (de `tests/test_forge_mutante.py:1564`, que já existia na base `004ce869`) exige que o `de` de cada spec do Forge exista na fonte atual, e a l. 1287 já não tem `m.removeprefix("tests.") for m in`. O defeito é do patch, não do merge, e a rodada de 20/11 não o viu. Não se cura com cartão: sem CI verde, não há aprovação.

Correção do autor: no mesmo commit, alinhar o `de` de M1 e M2 em `tests/mutantes/forge-testes-modulos-nome.json` à l. 1287 nova, com o `para` equivalente, e rodar `bin/forge-mutante --processos 1 tests/mutantes/forge-testes-modulos-nome.json` para confirmar que os dois morrem.

O A1 recomendado da rodada anterior (o `rglob` em `nome_do_modulo` sem conferir `__init__.py`) segue como cartão depois do merge.
