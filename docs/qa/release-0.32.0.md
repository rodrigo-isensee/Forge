---
tipo: qa
contrato: 1
pedido: release-0.32.0
branch: melhoria/release-0.32.0
commit: cb9f7c1ee1a5ba99b8ddc80dae7c4c9535b20ff9
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: release-0.32.0

Leva `5b6d13a...cb9f7c1` contra a main 0.31.0: os PRs #427 a #430 (HEREDOC-COMENTARIO, HEREDOC-DONOS, CI-SUITE-NO-TETO, LOTE-UNICO-032), o commit de release 5e7f003 e a correção cb9f7c1 (`changelog.d/README.md`). Os commits depois de cb9f7c1 na branch são só pareceres (3 arquivos em docs/, 146 linhas); o código testado é o de cb9f7c1. Sem especificação de UX nem contrato de API; as obrigações são os escopos E1 a E3 do pedido e as regras com ID (R-QA, R-CUSTO, R-FLUXO).

## Achados
- A1 (recomendado) tests/mutantes/lote-unico-032-l49.json:1 · M10 desatualizado: o trecho `relogios := relogios_do_cartao(` não existe (o código usa `=`, bin/forge-check:2664); a spec sai rc 2 (inválido). Corrigido o trecho numa cópia, M10 morre. Nenhum sobrevivente.
- A2 (recomendado) bin/forge-check:695 · AR-1: `forge-mutante --cobertura --base 5b6d13a` lista 118 condições sem mutante (L03 a L18 e voltas, já aceitas como recomendado no QA do #430, A2 e A3); a release não soma código novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: a leva é os 4 PRs sobre a main | `git log 5b6d13a..cb9f7c1`: 6 commits (#427, #428, #429, #430, release, README) | n/a | passou |
| E2: versão 0.32.0 em plugin.json e no CHANGELOG | `scripts/conferir-release.py --base origin/main` | base 0.31.0 e release 0.32.0 batem; `changelog.d/` sem fragmento pendente | passou (rc 0) |
| E2: sem segredo nem caminho pessoal | `scripts/verificar-contribuicao.sh origin/main` | diff inteiro contra a main | passou (rc 0) |
| E2: plugin válido | `scripts/validar-plugin.sh` | manifesto e marketplace | passou (`Validation passed`) |
| R-QA: suíte inteira verde | `.githooks/pre-push --suite` sobre cb9f7c1 | 2489 testes em 88 módulos, 4 processos | passou (rc 0) |
| R-QA: controle com mutantes declarados | `forge-mutante` nas 11 specs da leva | um mutante por guarda declarada | passou (ver A1) |
| R-CUSTO: nada pago | diff: só ci.yml com `timeout-minutes` (20, 25, 25) e scripts locais | n/a | passou |
| E3: versão minor | leitura do CHANGELOG 0.32.0 e do diff | ver "Versão minor" | sem quebra |

## Cenários e resultado real
- Carga antes da suíte: load 1,45 e MemAvailable 6,5 GB (regra de máquina cumprida).
- Suíte: `Ran 2489 tests in 912.012s (4 processos)`, `OK (skipped=28)`, rc=0. Os 28 skips são marcações dos testes da própria suíte; não os investiguei um a um e este parecer não acrescentou nenhum.
- Mutantes (`bin/forge-mutante --processos 2`, uma rodada por pedido; specs de pedidos diferentes não se misturam, rc 2 na primeira tentativa em conjunto, sem execução):
  - heredoc-comentario (13): rc 0. heredoc-donos (16): rc 0.
  - lote-unico-032-l02, l31, l32 + l32-2, l33, l36, l37: rc 0 cada.
  - vel-p6-gate (9): rc 0.
  - lote-unico-032-l49: M1 a M4, M6 a M9, M11 e M12 morreram; M10 inválido por trecho desatualizado (A1); com o trecho `relogios = ` numa cópia, `M10 · morreu · bin/forge-check:2664`, rc 0. A spec não tem M5.
  - Total: nenhum sobrevivente; 1 inválido, que provei morto à mão.
- `forge-mutante --cobertura --base 5b6d13a`: rc 1, 118 `sem mutante` (A2), `não coberto`: .claude-plugin/plugin.json e .github/workflows/ci.yml. Com `--base c6244ac` (base do #430) a mesma contagem, 118: nada novo entrou depois do #430.
- Vermelho antes do verde: não repetido aqui; a release não adiciona teste novo de regra (os pareceres dos PRs trazem a saída do vermelho de cada um). Mutação no diff: coberta pelas rodadas acima.

## PA-7 (docs/engineering/achados-recorrentes.md)
- AR-1 (lista de mutantes incompleta) ocorre de novo (A1 e A2); a linha AR-1 não foi atualizada aqui porque o brief proíbe tocar outro arquivo além do parecer: fica para o tech-lead no PR.
- AR-2, AR-3, AR-5 a AR-8 e AR-10: nenhuma ocorrência nova vista no diff da release (só README em changelog.d e pareceres depois do #430).
- AR-4: nenhum teste novo na release. AR-9: sem limite antigo novo; os `timeout-minutes` do ci.yml (20, 25, 25) batem com o CHANGELOG.

## Versão minor (E3)
Nada na leva exige major: as mudanças são adições (`forge-check proximo`, `decisoes`, `--processos`, ADRs 0014 e 0015 como proposta) e correções. Dois pontos de atenção compatíveis, não quebras: `forge-check movimento` agora recusa coluna fora do KANBAN.md (rc 1, endurece entrada inválida, nenhum fluxo documentado a usava) e `templates/projeto/docs/pedidos/_modelo.md` ganha o formato de suposição (só aviso do `brief`, não recusa). Minor 0.32.0 é adequada.

## Bugs
Nenhum aberto (`docs/qa/bugs/` sem entrada nova).
