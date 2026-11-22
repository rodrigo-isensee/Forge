---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-prazo-unico-estavel
commit: 08e2525e442b1754e2df6e066afb1948d175f422
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: PrazoUnico determinístico (v0478 E124.3)

Só `tests/test_fechar_checks_do_head.py::PrazoUnico` mudou (diff contra a base 48d6f4b8).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Estável sob carga (E124.1) | `PrazoUnico.test_espera_do_passo_4_desconta_o_prazo_do_passo_6`, 10 rodadas seguidas, carga 8 a 16 | prazo esgotado no passo 4 | 10/10 passou (6,9 a 8,0 s cada) |
| Nada mais frouxo | leitura do diff: rc 1, merges vazio e 1 chamada de `gh api commits` mantidos; somados 1 leitura única de `gh pr checks`, a mensagem completa do passo 6 (sha, `lida: in_progress/-`, `após 3s`) e o `checks verdes` do passo 4 | prazo único | mais estrito que antes |
| Mutante VU4 (prazo recomeçado no passo 6) | `bin/forge-mutante --ids VU4 tests/mutantes/v0480-seg-quarentena-fechar.json` | prazo único | morreu |

## Cenários e resultado real
- Rodada: `python3 -I -m unittest discover -s tests -p test_fechar_checks_do_head.py -k PrazoUnico`, 10 vezes: `Ran 1 test ... OK` em todas; carga da máquina 16,5 no início.
- VU4: `VU4 · morreu · bin/forge-fechar:867`.
- Suíte inteira: no CI do PR (sem rodada local, conforme o brief).
