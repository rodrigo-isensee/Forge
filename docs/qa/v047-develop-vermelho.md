---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-develop-vermelho
commit: 0137e932d22d1ac2ab8e5d956479837fc4d41499
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-develop-vermelho

Pedido v047, etapa E1.210: intervalo `origin/develop (f4b0c2ae)..0137e932`. O diff é uma linha em `REAPROVEITAM_O_LOTE` de `bin/forge-testes` (`test_hook_erro_libera`) e o fragmento `changelog.d/v047-develop-vermelho.md`. Sem especificação de UX nem contrato de API; sem gatilho de segurança. Acessibilidade e E2E: n/a.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `tests/test_hooks.py` pedido pelo caminho roda todo módulo que reaproveita `Hooks.executar_em_lote` (E1.120) | `CaminhoFiltroEAviso.test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele` | o módulo `test_hook_erro_libera` (`tests/test_hook_erro_libera.py:34`) no conjunto; mínimo de 8 reaproveitadores | falha na base, passa no head |
| Mapa não regride nos demais casos do filtro | `CaminhoFiltroEAviso` (9 testes) | caminho inexistente, misto, aviso cedo | 9 OK no head |
| O módulo acrescentado continua verde | `tests.test_hook_erro_libera` | n/a | 11 testes OK |

## Provas

**Vermelho à mão** (o `forge-testes --vermelho` estourou o prazo, rc=124, sem veredito; não vale). Clone `wt/v047-develop-vermelho-qa210`, mesma classe, só o `bin/forge-testes` trocado (restaurado depois por `git checkout`):

base (`bin/forge-testes` de origin/develop f4b0c2ae):
```
.......F.
FAIL: test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele
AssertionError: {... 'test_hook_erro_libera' ...} not less than or equal to {... sem 'test_hook_erro_libera' ...}
Ran 9 tests in 13.586s
FAILED (failures=1)
```
head 0137e932:
```
.........
Ran 9 tests in 13.794s
OK
```
Só esse teste cai na base; nenhum cai no head.

**Mutação:** a mudança é uma linha de guarda (um item de tupla). O mutante é remover o item (a própria base): morto por esse teste, como acima. Sem outra condição mudada.

**Mapa:** `forge-testes --listar tests/test_hooks.py` lista `test_hook_erro_libera`.

**CI:** não consultei o check-run `bateria` do sha (sem `gh` utilizável aqui); a suíte inteira fica para o CI do PR, que o tech-lead confere antes do merge.
