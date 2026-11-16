---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-reverte-576
commit: 988ca87aa95f0b9dea54bdb442f0ee5b5b7f0e0f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (revert do #576, E2.439)

Parecer completo (não havia parecer anterior nesta branch). Base `befbb464` (develop), head `988ca87a`, um commit só: `git revert` de `22f1eaa8` (#576, CI-RAPIDO).

## O que foi conferido
- **Revert puro do #576.** `diff <(git diff 22f1eaa8 22f1eaa8^) <(git diff 988ca87a^ 988ca87a)` difere só na linha `index` de `docs/engineering/achados-recorrentes.md` (o arquivo mudou depois em #586/#590, fora do trecho revertido); os hunks são idênticos. Nenhum arquivo fora dos 17 do #576 é tocado; o que entrou depois do #576 fica.
- **Catraca de workflows volta a passar.** `python3 -m unittest tests.test_catraca.Workflows`: na base `befbb464`, `FAILED (failures=2)` (`test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore`, `test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde`); no head `988ca87a`, `Ran 6 tests` e `OK`. O teste de controle não foi mudado (`R-CONFORMIDADE`).
- **Referências órfãs.** Nenhum teste, script, hook ou workflow do head cita `scripts/pesos-do-ci.py` nem `v047-ci-rapido` (grep em `tests/ bin/ scripts/ hooks/ .github/ .githooks/`). `tests.test_dependabot_modelo` (lê `skills/ci-cd/SKILL.md`): OK.
- **Regras.** `R-FLUXO` (revert só do item, por ordem do dono, E2.430), `R-VERIFY` (sem force), `R-MAIN` (não toca a main). Tamanho (M14): o revert passa de 150 linhas de código, mas é a volta exata a um estado já aprovado; o corpo do PR deve trazer `teto: excedido, <n> linhas, revert puro do #576`.
- **Guardas.** Revert não cria guarda nova; as guardas que somem são as do #576, com a spec `tests/mutantes/v047-ci-rapido-1.json` removida junto (sem spec órfã, AR-12).

## Falhas vistas fora do item (não vêm do revert)
- `tests.test_metricas_texto`: `agents/jarvis.md: caracteres = 7796 passa do teto 7795`; o revert não toca `agents/jarvis.md` (vem de outro item da develop, E2.417).
- `tests.test_testes_tocados.MapaCobreImportacaoEVarredura`: 527 falhas na base, 520 no head; o revert reduz, não causa (o mapa de `tests/mutantes/` para `test_forge_mutante` vem de outro item da develop).
- Essas quebras seguem para a junção develop-verde (E2.416/E2.417), conforme o histórico do pedido.

## Achados

## Sondas

## Parecer
Aprovado. O head `988ca87a` desfaz só o #576, sem tocar arquivo fora dele, e a catraca `tests.test_catraca.Workflows` volta ao verde sem mudar o teste de controle. Sem achados no diff. O CI do PR ainda não rodou neste head (sem PR, pelo brief); a develop só fica verde com os consertos dos outros itens juntados (falhas acima).
