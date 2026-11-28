---
tipo: qa
contrato: 1
pedido: release-0.47.2
branch: melhoria/v047-release-0472
commit: b57bb55861115f7b9b5236d4349b4807fe842aa8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: release 0.47.2 sobre a develop (v047, E2.519)

Head `b57bb558`, base `86ac0fcb` (develop). O intervalo é um commit só: sobe `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` de 0.47.1 para 0.47.2, junta ao `CHANGELOG.md` os fragmentos pendentes e os apaga. Nenhum código muda. Suíte inteira: check-run do CI da develop no `86ac0fcb` (success); a suíte local completa não foi rodada, por ordem do dono de 16/11.

## Achados
- A1 (recomendado) docs/qa/release-0.47.2.md:1 · sem parecer de QA próprio os itens fixture-etapa (#570), mutantes-velhos (#578) e sessao-por-pedido (#589), que mudam teste ou spec; só as mudanças de documento (brief-vagas, brief-portoes, visao-de-foco) dispensam QA.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Develop verde no base | `gh run list --branch develop`: CI do `86ac0fcb` success | base vermelha | passou |
| Os 37 fragmentos apagados têm entrada no CHANGELOG | as 43 linhas `- ` dos fragmentos, lidas de `86ac0fcb`, procuradas uma a uma em `CHANGELOG.md` | fragmento sem entrada | passou (43 de 43, 0 faltando) |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Versão sobe contra a main | `scripts/conferir-release.py --base origin/main` (0.47.1 para 0.47.2); os dois `plugin.json` em 0.47.2 | versão acima da main | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (104, OK) |
| Testes dos itens da leva sem parecer | `python3 -m unittest tests.test_selo_e_entrega tests.test_sessao_por_pedido tests.test_testes_tocados` | contagem de módulos, vocabulário de etapa | passou (278, OK, skipped=1 herdado) |
| `forge-check docs` | rc | formato | passou (rc 0; aviso de versão do cache) |

## Itens da leva sem QA
Dos 37 fragmentos, 30 têm `docs/qa/<item>.md`. Sete não têm: brief-vagas, brief-portoes e visao-de-foco (só documento e review), develop-verde-2 (conserto de contagem em teste), fixture-etapa, mutantes-velhos e sessao-por-pedido (teste ou spec; testes rodados acima e a spec de mutantes velhos entra na cobertura de `v047-specs-conferidas`). Nenhum muda código de produção; por isso não bloqueia (A1, recomendado).

## Cenários e resultado real
- Remoto avançou para `a5a0b04d` (só `docs/devops/release-0.47.2.md`), trazido por merge antes do push.
- Vermelho antes do verde e mutação: não se aplicam; o intervalo não traz teste novo nem regra de código.
- Sem bugs abertos.
