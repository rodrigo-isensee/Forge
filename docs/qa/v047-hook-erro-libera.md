---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 9666b6bf53214ef46d9069cd1a38b5809b88c72a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047-hook-erro-libera

Pedido v047, etapa E3.41: QA por delta até `9666b6bf` (junção da `develop` em `4c350b2f`, conflito resolvido em `tests/test_hooks.py`). O parecer anterior (E3.37, `4c350b2f`, aprovado) vale para o código do pedido, que a junção não tocou (`hooks/conformidade.py` e os fixtures `errointerno-*` não entram no delta).

## Achados
- A4 (recomendado) agents/tech-lead.md:21 · M14 segue acima da orientação (445 linhas contáveis contra 150); o corpo do PR precisa de `teto: excedido, <linhas>, <motivo>` (herdado da E3.37, não bloqueia).

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Conflito: gh pendurado segue pegando o sleep | `Hooks.test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook` | teto `(limite-1)*fator`, com `limite=10` (hooks.json) e fator preso em 2: 18 s contra `sleep 30` | passou; aritmética conferida, a fronteira fica 12 s abaixo do sleep mesmo com carga alta |
| Ciclo de import `apoio_volta_unica` ↔ `test_hooks` | `import` isolado de cada módulo | ordem dos imports | os dois importam sem erro |
| `forge-testes` MAPA (`templates/projeto/.forge/config.json` → `test_ritmo`) | `tests.test_ritmo` | n/a | passou |
| C1 a C8 do pedido | `tests.test_hook_erro_libera` (11) | ver E3.37 | passou |

## Provas

**Delta** (`forge-check parecer delta`): intervalo `4c350b2f..9666b6bf`, sem o que veio da base; no domínio só `bin/forge-testes` (uma linha de MAPA), `tests/apoio_volta_unica.py` (`nucleos_do_processo`, `fator_de_carga`) e `tests/test_hooks.py` (resolução do conflito: `nucleos_do_processo` movida ao apoio, import de volta no fim do módulo, teto do teste do gh).

**Testes afetados** (`python3 -m unittest tests.test_hooks.Hooks.test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook tests.test_hook_erro_libera tests.test_ritmo`): `Ran 26 tests in 20.955s`, `OK`. Sonda: `fator_de_carga(100,12)=2.0`, teto 18.0 < 30.

**Vermelho e mutação:** sem mudança no código de produção do pedido desde a E3.37 (40 de 40 mutantes mortos, vermelho rc 0 no `4c350b2f`); a junção não reabre. Não rerrodado.

**Suíte e CI:** PR 550 aberto; checks do head `52cce202` ainda `pending` no momento (`bateria` sem resultado); a suíte inteira fica para o check-run `bateria` do CI. Carga ~14 em 12 núcleos. Acessibilidade e E2E: n/a.
