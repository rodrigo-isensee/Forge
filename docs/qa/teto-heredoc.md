---
tipo: qa
contrato: 1
pedido: teto-heredoc
branch: melhoria/teto-heredoc
commit: c3192f2fff7438da32036402d88a8add0b5e3021
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-31
---
# QA: teto-heredoc

Etapa E1.4 (R-QA). Diff lido: `git diff ce57f2d c3192f2` (`tests/test_hooks.py` +23/-2 e `changelog.d/teto-heredoc.md`). Entrega o item E1 do pedido: o `test_muitos_heredocs_recusam_dentro_do_orcamento` mede a parede só da execução do hook (montagem do fixture fora da janela) abaixo de 5,0 s e a CPU dos filhos (`RUSAGE_CHILDREN`) abaixo de 5,0 s; o teto não subiu (`limite/2` do `hooks.json`) e nenhum arquivo de `hooks/` mudou. Cumpre a M14 (`agents/tech-lead.md:19`): 25 linhas de código e teste contra o teto de 150, um comportamento só. Não há linha de guarda de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` no diff, então a spec de `forge-mutante` não se aplica; os mutantes abaixo são do hook, à mão, restaurados com `git checkout -- hooks/_comum.py` (árvore limpa depois).

## Achados
- A1 (recomendado) tests/test_hooks.py:1819 · a parede de 5,0 s ainda oscila com a máquina saturada (24 laços de CPU em 16 núcleos, load ~25): 4 de 6 falharam com 5,03 a 5,39 s; com load 6 a 13, 12 de 12 passaram. Risco residual aceito pela decisão técnica de 18:21.
- A2 (recomendado) tests/test_hooks.py:1822 · o laço de CPU de um processo só reprova pela parede, que cai antes; só CPU espalhada em filhos paralelos isola a cobrança da CPU. Os dois sinais coincidem; sem achado de código.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1 do pedido: passa sob carga | teste alvo, 6 execuções sem mutante, load 5 a 13 | parede 5,0 s e CPU 5,0 s | passou (12 de 12 subtestes); sob saturação extrema, A1 |
| PQ-1: reprova com hook lento de verdade (CPU) | mutante m1b | CPU dos filhos acima de 5,0 s | reprovou (6,75 s e 6,09 s) |
| PQ-1: idem, laço serial | mutante m1a | parede acima de 5,0 s | reprovou (9,25 s e 8,93 s) |
| A2 do modelo de ameaças (espera ociosa) | mutante m2 `sleep(6)` | parede acima de 5,0 s sem CPU | reprovou (8,00 s e 8,21 s) |
| Teto não afrouxa | leitura do diff | `limite/2` do `hooks.json` | nenhum número subiu |

## Cenários e resultado real
Mutação aplicada no começo de `tirar_heredocs` (`hooks/_comum.py:793`), só com 1000 `<<` ou mais no comando; comando do teste: `python3 -m unittest tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`.

- Sem mutante (referência): `Ran 1 test in 4.594s` / `OK`.
- m1a, laço serial de 400 milhões de voltas (um laço de 60 e de 150 milhões, mais curtos, não passaram de 5,0 s e o teste seguiu verde: mutante fraco, não lacuna do teste):
  `AssertionError: 9.254710761990282 not less than 5.0 : a decisão sai bem antes do Claude Code matar o hook` (forma='um por linha'); `8.932691748006619 not less than 5.0` (forma='&&'); `FAILED (failures=2)`, rc=1.
- m1b, CPU em 6 filhos paralelos de 20 milhões de voltas (parede quase intacta, CPU alta):
  `AssertionError: 6.754643 not less than 5.0 : o custo de CPU do hook (filhos) fica no mesmo teto, sem depender da carga` (um por linha); `6.0874320000000015 not less than 5.0` (&&); `FAILED (failures=2)`, rc=1.
- m2, `time.sleep(6)`:
  `AssertionError: 7.996972535998793 not less than 5.0 : a decisão sai bem antes do Claude Code matar o hook` (um por linha); `8.210941098994226 not less than 5.0` (&&); `FAILED (failures=2)`, rc=1. A parede segura a espera ociosa, como a decisão técnica de 18:26 manda.
- Seis execuções sem mutante, load de 1 min 5,2 a 6,1: `OK` nas seis (4,4 s, 4,7 s, 18,3 s, 4,2 s, 4,4 s, 4,2 s).
- Seis execuções com 12 laços de CPU extras (load até 13): `OK` nas seis (6,2 a 6,8 s cada).
- Seis execuções com 24 laços de CPU extras (load ~20 a 25 em 16 núcleos): 2 `OK` e 4 `FAILED` só pela parede (5,317 s, 5,153 s, 5,027 s, 5,387 e 5,274 s); a CPU nunca falhou. Isso é saturação além do uso real, registrada em A1; o teste continua mais estável que o anterior (que contava a montagem na janela), sem subir o teto.
- Suíte completa e pre-push: rodam no envio; falha só em arquivo fora do diff é tratada à parte.
