---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 6d71827e0a25324caf731a6d17949b158ce7e348
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-docs-ok (E14.25), delta 9fa5f832..6d71827e

Clone `/root/.forge-contrib/wt/v0481-docs-ok-qa`, no head `6d71827e`. O parecer anterior (commit `9fa5f832`) reprovou por A1 e A2; o delta toca só `bin/forge-check` (1 linha) e `tests/mutantes/v0478-clone-nome-unico.json` (M6).

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: `gravar = not` com o espaço, M12 de `v046-pr-hook-prazo-2` confere com a fonte | `forge-mutante tests/mutantes/v046-pr-hook-prazo-2.json --ids M12` | trecho `de` com 1 ocorrência | `M12 · morreu · bin/forge-check:11241` |
| A2: M6 de `v0478-clone-nome-unico` no ramo `elif copia and ...` | `forge-mutante tests/mutantes/v0478-clone-nome-unico.json` | mesma guarda, ramo `elif` | M1 a M8 morreram, `M6 · morreu · bin/forge-check:9735`; rc 0 |
| Mutantes do pedido continuam mortos | `forge-mutante tests/mutantes/v0481-docs-ok.json` | n/a | M1 a M4 morreram (`:11239`, `:9731`, `:9735`) |
| `--todas` igual à base | `forge-mutante --conferir --todas` no head e na base `9fa5f832` (cópia por `git archive`) | n/a | a base lista 26 linhas, o head 24: somem só `v046-pr-hook-prazo-2 M12` e `v0478-clone-nome-unico M6`; as 24 restantes são idênticas (pendentes já conhecidas) |
| AR-12 | `test_forge_mutante.ConferirTodas` (4 testes) | n/a | OK |

Vermelho antes do verde: não há teste novo; o delta é correção de spec e de espaço, e a prova é o `--todas` da base acusando as duas linhas que o head não acusa.

## Pendente
Check-runs `suíte` do sha `6d71827e` ainda em andamento na hora deste parecer; a prova de suíte inteira é o check-run `bateria` do mesmo sha (`R-QA`), que não cito antes de concluir.
