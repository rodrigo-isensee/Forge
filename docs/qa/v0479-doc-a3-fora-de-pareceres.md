---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-doc-a3-fora-de-pareceres
commit: 0d656a84a470ccb3ea48dd0dd3aa854290fe1a2e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E55.5 (documento da A3 sai de docs/devops/ para docs/engineering/)

Diff contra a base 5ccac0bf: renomeia `docs/devops/v0479-sandbox-controle.{md,patch}` para `docs/engineering/`, ajusta as referências (`bin/forge-testes` MAPA, `tests/test_sandbox_controle.py`, `docs/hooks.md`, fragmentos do changelog). Nenhuma referência ao caminho antigo fora de pareceres.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Promoção volta a passar (pareceres de devops só em docs/devops) | `promover-homolog.py --conferir-ref 0d656a84…` | pasta de pareceres sem documento alheio | rc=0, "34 arquivo(s) da promoção, todos aprovados" |
| O patch movido segue aplicável e o teste o encontra | `test_sandbox_controle` (14 testes, 2 pulados: bubblewrap indisponível aqui, valem no `bateria` do CI) | caminho do PATCH | OK |
| O mapa do `forge-testes` aponta o teste para o novo caminho | `test_testes_tocados` (164 testes, 1 pulado) | regex do MAPA | OK |

## Provas
- `python3 scripts/promover-homolog.py --conferir-ref 0d656a84a470ccb3ea48dd0dd3aa854290fe1a2e`: `conferir-ref: 0d656a84a470ccb3ea48dd0dd3aa854290fe1a2e promovível para a homolog`, rc=0.
- `python3 -I -m unittest discover -s tests -p test_sandbox_controle.py`: Ran 14 tests, OK (skipped=2).
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py`: Ran 164 tests, OK (skipped=1).
- Sem suíte local; sem teste novo de regra, então sem vermelho/mutação (mudança de caminho e documentação).
