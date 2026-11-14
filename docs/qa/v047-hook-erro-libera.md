---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 804c96124a10056bd58c621c6e7e2aa5274a0cd5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047-hook-erro-libera

Pedido v047, etapa E3.46: QA por delta `9666b6bf..804c9612` (índice de fixtures e corpus mudaram depois do parecer E3.41). O código de produção do pedido não mudou; o delta é só de teste e índice. Review e segurança já revalidados.

## Achados
- A4 (recomendado) agents/tech-lead.md:21 · M14 segue acima da orientação (445 linhas contáveis contra 150); o corpo do PR precisa de `teto: excedido, <linhas>, <motivo>` (herdado da E3.37, não bloqueia).

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Driver do lote passa ao `executar` o mesmo marcador do `__main__` (`R-CONFORMIDADE`) | `CorpusDaVoltaUnica.test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` | marcador `MARCADOR` (conformidade) e `CriticoOuAlias` (parecer); não `None` | passou; `hooks/conformidade.py:2959` chama `executar(..., MARCADOR, ...)`, igual ao driver |
| Índice de fixtures bate com o corpus | `scripts/indice-fixtures.py` regerado | 2463 fixtures, `errointerno-*` = 31 (23 recusa, 8 libera) | regerar não muda `docs/hooks-fixtures.md`; contagem em disco 2463 |
| C1 a C8 do pedido | `tests.test_hook_erro_libera` | ver E3.37 | sem mudança no código; não rerrodado |

## Provas

**Delta** (`forge-check parecer delta`): rc 0; intervalo `9666b6bf..` ao head; no domínio só `docs/hooks-fixtures.md`, `tests/apoio_volta_unica.py` (`CRITICO` por `MARCADOR` no driver) e `tests/test_hooks_volta_corpus.py` (mesma troca e docstring).

**Testes afetados** (`python3 -m unittest tests.test_hooks_volta_corpus`): `Ran 16 tests in 403.372s`, `OK`.

**Vermelho e mutação:** o delta não toca produção; 40 de 40 mutantes mortos e vermelho rc 0 da E3.37 valem. Não rerrodado.

**CI do PR 550** (head `909417fd`, só pareceres além do `804c9612`): `bateria (pareceres/passos/verificações longas)`, `instalação`, `suíte 3.12 partes 2 e 3` e `3.14 parte 2` passam; suítes restantes `pending` na leitura. `catraca` falha por `R-CONFORMIDADE`: mudança em `hooks/conformidade.py`, `hooks/_comum.py`, `tests/catraca.py` exige o rótulo `afrouxa-regra` do dono depois do último push (ADR 0008); não é defeito de teste e vira decisão do dono (`R-DECISAO`). Acessibilidade e E2E: n/a.
