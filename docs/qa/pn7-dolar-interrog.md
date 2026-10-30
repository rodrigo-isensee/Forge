---
tipo: qa
contrato: 1
pedido: pn7-dolar-interrog
branch: melhoria/pn7-dolar-interrog
commit: cec2b422dccee2c4c9009e5677aac209b351763a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: PN7-DOLAR-INTERROG, voltas 4 a 7 (H1-1 da P-N7, `R-QA`)

Código testado: `cec2b42` (worktree desanexada, base `31257c1`), delta `836ee2a..cec2b42` sobre o meu parecer anterior (`15150bc`). Sem `CA-n` de UX; as obrigações são o escopo do pedido e as decisões do dono de 2026-10-30 (05:14, 06:27 e 07:45): o `$?` vale só entre aspas duplas; fora de aspas volta ao comportamento da base (recusado com marcador crítico, lido como na base sem ele); saem `codigo_de_saida_vale`, `codigo_de_saida_solto` e `SUBSTITUICAO`.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `"$?"` passa; `$?` fora de aspas e todo outro `$` recusam, em todo lugar da propriedade | `CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs` (mínimo 5000) | posição, aspas, `IFS`, `@(x)`, `>&`, `2>&`, `<&`, `>\|`, `$(…)` | passou |
| Fora de aspas recusa também em `echo`; entre aspas duplas passa; K3 em `simples_da_gramatica` | `CodigoDeSaida.test_codigo_fora_de_aspas_recusa_em_todo_lugar` | `echo rc=$?`, `echo "$$?"`, extglob, `>&`, `>\|` | passou |
| Sondas novas (extglob, `>&`, `2>&`, `<&`, `>\|`) recusam com rc 2; as `-libera` seguem como na base | `Hooks.test_fixtures` | fixtures `-bloqueia` e `-libera` | passou |
| Corpus contra o bash (teto de 10 fora do corpus, as duas sondas de extglob) | `Hooks.test_t5_*` e `tests.test_hooks_volta_corpus` (16 testes) | `bash -n` sem o `shopt` da 1ª linha | passou |

## Execução (head `cec2b42`)
- `tests.test_hooks.CodigoDeSaida` e `Hooks.test_fixtures`: 4 testes, OK. `tests.test_hooks_volta_corpus`: 16 testes, OK.
- Mutantes: `bin/forge-mutante tests/mutantes/pn7-dolar-interrog.json` rc=0: D1, D2 (`_comum.py:1457`) e D3, D4 (`_comum.py:1574`) morreram.
- Conferência da lista contra o diff: a única condição Python mudada contra a base é `_comum.py:1457`; `forge-mutante --cobertura --base 31257c1` (sem a spec) lista `coberta · hooks/_comum.py:1457 · D1, D2 · declarado, não provado`, rc=0. Sem linha de guarda sem mutante. D3 e D4 cobrem o `replace("$?", "")` da gramática, que a base já tinha.
- Vermelho: `bin/forge-testes --vermelho 836ee2a4d1b6a2186af54b2e34ac83c5b7a6eca5 --modulos test_hooks`, rc=0, abre com `vermelho: base=836ee2a4d1b6 head=cec2b422dcce`; prova (asserção): `CodigoDeSaida.test_codigo_fora_de_aspas_recusa_em_todo_lugar`, `CodigoDeSaida.test_dolar_interrogacao_por_posicao_aspas_lugar_e_ifs`, `Hooks.test_fixtures` (H=ok, B=falha); nenhum cai no HEAD; 52 não provam (passam na base, esperado).
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 (lista de mutantes incompleta) conferido acima; AR-2 (ramo de falha sem teste): os ramos removidos saíram com os testes; sem recorrência.

## Veredito
Aprovado sobre `cec2b42`; sem achado, sem bug aberto. Risco residual: o `$?` fora de aspas só é recusado com marcador crítico (decisão do dono); sem ele o hook lê como na base.
