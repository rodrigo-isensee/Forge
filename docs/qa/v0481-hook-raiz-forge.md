---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: e4998443f6eea0ef08c43dbbb9b35627f13582b0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 hook-raiz-forge (E37.12, PR #930, volta 2)

Delta 10c1b834..e4998443. O A9 da segurança (destino por variável com resto na raiz do Forge vale pelo valor calculado; sem valor, só o texto preciso do valor conta) está coberto. Os pareceres anteriores (volta 0 e 1) seguem valendo para o resto.

## Critério → teste → resultado
Sem docs/ux nem contrato de API; critérios da etapa E37.1 e do A9.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 a CA-9 da volta 1 | fixtures `raiz-forge-*` (sem mudança no delta) | ver parecer da volta 1 | passou (CI do head) |
| CA-10 (A9) destino por variável ou substituição com resto (`D=.githooks; printf x > $D/pre-push`) recusa na raiz | raiz-forge-s7-variavel-com-resto-githooks-bloqueia, raiz-forge-s8-variavel-com-resto-manifesto-bloqueia, raiz-forge-substituicao-com-resto-githooks-bloqueia | resto depois da variável; manifesto `.claude-plugin/` | passou |
| CA-11 (A9) sem valor calculado e com resto, recusa só se o texto do valor cita a entrada | raiz-forge-variavel-sem-valor-com-resto-githooks-bloqueia; mutantes RD7 e RD8 | `$TMPDIR/y; cat .githooks/pre-push` fora do valor passa | passou |
| CA-12 (A9) na cópia de wt/ o destino com resto segue livre | raiz-forge-wt-s7-variavel-com-resto-da-copia-libera, raiz-forge-wt-s8-variavel-com-resto-da-copia-libera | cópia x raiz | passou |
| CA-13 docs/hooks.md e changelog descrevem o comportamento | leitura do diff | n/a | coerente com o código |

## Cenários e resultado real (volta 2)
- ci: e4998443f6eea0ef08c43dbbb9b35627f13582b0 verde
- Leitura do CI (`gh pr checks 930`, head e4998443 conferido por `gh pr view`): tudo pass fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo; suítes 3.12 e 3.14 (partes 1 a 5) passaram.
- Local sob o flock da trava A: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge tests.test_indice_fixtures` deu `Ran 11 tests ... OK`.
- Mutantes (`bin/forge-mutante` das specs -3 e -4, `--base 10c1b834`, `base=10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf`): RD1 a RD6, RX1, RX2, RD7, RD8 todos `morreu`, rc=0, sem sobrevivente nem equivalente. RD1 e RD2 realinhadas a `fim_do_opaco`; RD7 e RD8 novas cobrem a linha `textos = ...`.
- `--cobertura --base 10c1b834`: as condições mudadas (4349, 4354, 4355) têm mutante declarado, e a rodada acima as provou.
- Vermelho antes do verde: as 6 fixtures novas são provadas pelos mutantes RD1, RD2, RD7 e RD8 mortos por elas (sem a lógica nova a fixture falha). `forge-testes --vermelho` não rodado (estourou o prazo de 10 min na volta 1, sem veredito).
- Acessibilidade e E2E: n/a (hook sem interface).
