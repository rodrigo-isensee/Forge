---
tipo: qa
contrato: 1
pedido: FIX-SUITE-LOCAL
branch: melhoria/suite-local-verde
commit: 10ed112c9cdffdc554743cd3126b6c40488ef943
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: FIX-SUITE-LOCAL

Correção sem especificação de UX nova: o plano é curto e as obrigações vêm do critério de pronto do pedido (PQ-1: suíte completa verde e envio pelo pre-push) e de `R-VERIFY`. Ambiente: Linux/WSL2, Python 3.14.4, shellcheck 0.11.0, sem root.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1 suíte verde | `python3 -m unittest discover -s tests` | n/a | passou (1594 testes, 1 skip, rc=0) |
| shellcheck 0.11 no hook | `test_pre_push_shellcheck.test_shellcheck_no_hook` | SC2329 em `.githooks/pre-push` | passou |
| falha fechada com lista de permissão | `test_hooks.test_erro_interno_com_lista_de_permissao_falha_fechado` | PermissionError de `Path.exists` em Python 3.14 | passou |
| falha fechada pela raiz (cwd home) | fixture `conformidade/contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` | erro interno com push bloqueia (código 2) | passou |
| falha fechada pela raiz (cwd wt) | fixture `conformidade/contrib-falha-fechada-pela-raiz-cwd-wt-bloqueia` | idem | passou |
| R-VERIFY: envio pelo pre-push | `.githooks/pre-push` direto com a linha de push de teste | suíte inteira antes de enviar | rc=0 |

## Cenários e resultado real
- CT-01 suíte completa, `python3 -m unittest discover -s tests`: `Ran 1594 tests in 348.686s, OK (skipped=1)`, rc=0.
- CT-02 as 4 falhas antigas: os dois testes isolados e `tests.test_hooks` inteiro (43 testes, 90 s) verdes; `tests.test_pre_push_shellcheck` 3 testes OK.
- CT-03 vermelho antes do verde: cópia de `git archive HEAD` em `$TMPDIR/semsc` sem `tests/apoio_pathlib_312/sitecustomize.py`. `python3 -m unittest tests.test_hooks`: `FAILED (failures=3)`: `test_erro_interno_com_lista_de_permissao_falha_fechado [forge-dev:aq]` e as duas fixtures `contrib-falha-fechada-pela-raiz-cwd-home-bloqueia` e `-cwd-wt-bloqueia`. Com o `sitecustomize`, os três passam; ele prova a causa (Python 3.14 engole o `OSError` de `Path.exists`) e sustenta a correção. O shellcheck não depende dele (a correção é o `disable=SC2329` no hook).
- CT-04 pre-push de push de teste: `printf 'refs/heads/melhoria/suite-local-verde <HEAD> refs/heads/melhoria/suite-local-verde <remoto>' | .githooks/pre-push origin <url>`: rc=0; 4 processos (510, 215, 441, 428 testes), `Ran 1594 tests in 167.795s`, `OK (skipped=1)`. O hook não afrouxou: o diff dele é só o comentário de `disable`.
- CT-05 neutralidade da correção: o `sitecustomize` só entra no `PYTHONPATH` dos testes que o pedem (`pathlib_312` na fixture e no teste), nunca no hook de produção; as demais fixtures seguem sem ele.
- Observações: avisos `catraca: a API do GitHub não respondeu` na saída são esperados sem rede e não falham nada. 1 skip é o mesmo da base (teste condicionado a ambiente); não é skip novo desta mudança.

## Bugs abertos
Nenhum.
