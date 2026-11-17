---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-conformidade-cf1
commit: 7412a90f2e2389af96e3e8aa0ead8f22de90baee
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 conformidade CF1, delta das duas junções da develop (E1.31)

Revalidação por delta sobre o parecer anterior (`docs/qa/v047-conformidade-destino-opaco.md`, pedido já integrado, não editado). Intervalo lido por `forge-check parecer delta`: `6f8bd39e..7412a90f`, sem o que veio da base. Domínio: `bin/forge-testes` (mapa: `test_estado_ilegivel`), `docs/hooks*.md`, as specs `v046-conformidade-caminho-git` (G6) e `v047-destino-opaco-10` (O60) realinhadas ao código novo da develop, `tests/test_conformidade_verde.py`, `tests/test_testes_tocados.py` (contagem 90; ambiente sem `GIT_*` herdado; teste do patch do pre-push). Escopo do plano inalterado; sem tela, sem acessibilidade.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G6: variável até o `}` e `$@`/`$*` (SO_VARIAVEL) | spec G6 (`test_fixtures_gitcomum`) | `${d%/}`, `$@`, `$*` | morreu |
| O60 (U4): variável atribuída mais de uma vez ou como argumento | spec O60 (`test_fixtures_opaco_u4`) | duas atribuições; atribuição como argumento | morreu |
| Contagem de módulos do plano dirigido do `forge-testes` (90) | `test_testes_tocados` | mínimo de módulos (guarda de suíte vazia) | passou |
| CF1 (conformidade verde) | `test_conformidade_verde` (16) | n/a | passou |
| Oráculo A9, A10, D2b | `test_oraculo_v047` (3) | recusas e liberações | passou |

## Execução (local, `TMPDIR` do sandbox, em primeiro plano)
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git.json`: cabeçalho `forge-mutante: pedido=v046 rev=7412a90f2e23 spec=040e2c2d…`; G1 a G8 `morreu` (G6 `hooks/conformidade.py:327`), rc=0.
- `bin/forge-mutante tests/mutantes/v047-destino-opaco-10.json`: cabeçalho `pedido=v047 rev=7412a90f2e23 spec=bdea461c…`; 16 `morreu` (O60 `hooks/conformidade.py:730`), nenhum `sobreviveu` nem `sem veredito`, rc=0. As duas specs são de pedidos diferentes e o `forge-mutante` recusa juntá-las (uma chamada por pedido).
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas tests.test_testes_tocados`: `Ran 166 tests in 269.028s`, `OK (skipped=1)`. O skip é do sandbox (`/proc` de outro namespace de pid, `MedidaDaVagaPesada`), não meu.
- `python3 -m unittest tests.test_conformidade_verde tests.test_oraculo_v047`: `Ran 19 tests in 139.426s`, OK.
- Vermelho antes do verde: o delta não traz teste novo de regra (realinha specs e contagem 90 e o ambiente de `test_testes_tocados`); o único teste novo, o do patch do pre-push (E2.567), veio da develop. Sem `--vermelho` neste delta.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.

## Observação sobre o oráculo (não bloqueia)
`tests/test_oraculo_v047.py` não tem mais o blob gravado no parecer anterior (`535134e9…`); hoje é `a9eddad2…`, e o log `730843a9..HEAD` traz o `cf6ccb64` (PR #611, develop: `sem_manutencao` e `LEIAME.md`, ajustes de ambiente). `git diff origin/develop HEAD -- tests/test_oraculo_v047.py` vazio: esta branch não o tocou, veio pela junção da develop; os casos (A9, A10, D2b) seguem iguais. O oráculo é do pedido anterior, já integrado; não reabro.

Parecer aprovado: nenhum achado aberto, nenhum mutante sobrevivente, nenhum bug de produto.
