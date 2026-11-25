---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-docs-ok
commit: 2259b235acc1128432428bfa3723bd48a1610c55
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-docs-ok (E14.49), delta 6d71827e..2259b235

Clone `/root/.forge-contrib/wt/v0481-docs-ok-qa`, levado ao head remoto `2259b235` (`git fetch` e `merge --ff-only`). O delta de código é só o teste `test_brief_de_parecer_sem_a_linha_com_caminho_fora_da_forma` em `tests/test_forge_copia.py` e o mutante M5 em `tests/mutantes/v0481-docs-ok.json`; o resto são pareceres. Fecha o A1 recomendado da segurança.

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| COPIA-REVISAO: o brief de parecer (review, seguranca, qa) recusa a cópia fora da forma de shell | `test_forge_copia.BriefSugereACopia.test_brief_de_parecer_sem_a_linha_com_caminho_fora_da_forma` (3 subtestes, caminho com espaço: sem `CLONE-NOME-UNICO`, sem `--revisao`) | caminho com espaço, as três etapas do ramo de revisão | passou (`discover -k test_brief_de_parecer`: 2 testes, OK) |
| O teste mata a guarda do ramo de revisão | `forge-mutante tests/mutantes/v0481-docs-ok.json`, M5 (tira `valor_de_shell_seguro` da linha 9731) | a guarda sozinha | `M5 · morreu · bin/forge-check:9731` |
| M1 a M4 seguem mortos | mesma rodada | n/a | M1, M2 `:11239`; M3 `:9731`; M4 `:9735`: morreram, rc 0 |

```
forge-mutante: pedido=v0481-docs-ok rev=2259b235acc1 spec=a587efab95b27a026b5c1f9a914f7bfbd927564eae87be93b5f2e97ae45c4530
M1 · morreu · bin/forge-check:11239
M2 · morreu · bin/forge-check:11239
M3 · morreu · bin/forge-check:9731
M4 · morreu · bin/forge-check:9735
M5 · morreu · bin/forge-check:9731
```

Vermelho antes do verde: o delta é só teste sobre código que já está na base (a guarda existe desde o `6d71827e`), então `forge-testes --vermelho 6d71827e` não tem mudança de produção a provar. A prova de falha do teste é o M5: sem a guarda, ele cai; com ela, passa.

## CI do head
`gh pr checks 892`, run 45598108933, sha `2259b235acc1128432428bfa3723bd48a1610c55` (igual ao head do remoto): todas as `suíte` (3.12 e 3.14, partes 1 a 5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada` verdes. Vermelhas só `bateria (pareceres)`, `bateria` e `catraca` (faltam os pareceres do head e o rótulo do dono, `R-CONFORMIDADE`), fora do que conta.
- ci: verde nas partes que contam (run 45598108933, sha 2259b235acc1128432428bfa3723bd48a1610c55)
