---
tipo: qa
contrato: 1
pedido: release-0.47.3
branch: melhoria/v047-release-0473
commit: eb9b4295bd8cafbbd70977f9c9170275b7932982
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: release 0.47.3 sobre a develop (v047, E2.586)

Head `eb9b4295`, base `24133d46` (develop). O intervalo é um commit só: sobe `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` de 0.47.2 para 0.47.3, junta ao `CHANGELOG.md` os 2 fragmentos (praticas P5, #610; prova-tmpdir, #606) e os apaga. Nenhum código muda. Suíte inteira: CI do push na develop no `24133d46` (run 44000733871, success); a suíte local completa não foi rodada, por ordem do dono de 16/11.

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Develop verde no base | `gh run view 44000733871`: CI push, headSha `24133d46`, success | base vermelha | passou |
| Os 2 fragmentos apagados têm entrada no CHANGELOG | diff do commit: as duas entradas (`### Adicionado` e `### Corrigido`) em `## [0.47.3]` com o texto dos fragmentos | fragmento sem entrada | passou (2 de 2) |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main` (0.47.1 para 0.47.3); os dois `plugin.json` em 0.47.3 | versão igual à da main | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (104, OK) |
| Testes dos itens da leva | `python3 -m unittest tests.test_forge_run.TmpdirDaProva tests.test_modelos_projeto.PraticasDoForge` | TMPDIR fora do repo; regra "ferramenta" cita comando existente | passou (11, OK) |

## Itens da leva e QA
- #606 (prova-tmpdir): tem `docs/qa/v047-prova-tmpdir.md`, parecer aprovado (commit `3fc4724d`, outro head), mais mutantes em `tests/mutantes/v047-prova-tmpdir.json`.
- #610 (cobertura-p5p6): só documento (`praticas.md`) e o teste `PraticasDoForge` (3 testes, passam acima); tem `docs/reviews/v047-cobertura-p5p6.md`, sem `docs/qa/` próprio. O teste é de estrutura, sem regra de código de produção; os 3 testes rodados aqui cobrem o QA. Não bloqueia.

## Notas
- Os checks vermelhos no `24133d46` (CI e Catraca, runs 44000741606 e 44000741368) são do PR de promoção #613 (develop para homolog 0.47.2): a etapa "release exige versão nova e changelog fechado" e o rótulo de decisão do #606 na catraca. Não são o CI da develop.
- `tests.test_selo_e_entrega` estourou 120 s no sandbox (rede para github bloqueada); não é arquivo tocado pelo intervalo e ficou fora.
- Vermelho antes do verde e mutação: não se aplicam; o intervalo não traz teste novo nem regra de código.
- `forge-check parecer delta`: sem parecer anterior da 0.47.3, parecer completo.
- Sem bugs abertos.
