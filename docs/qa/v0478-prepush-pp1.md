---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-prepush-pp1
commit: 6c84adb4ea7cda8e9b95de6d2857201afedc2f7e
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (patch PP1 do envio local, E14.5)

Escopo: `docs/devops/pp1-pre-push.patch`, `docs/devops/pp1-aplicar.md`, `tests/test_pre_push_patch.py`, mapa de `bin/forge-testes`. Sem especificação de UX nem contrato de API (pedido de controle do envio); as obrigações são os quatro cartões do roteiro. Sem suíte local; a suíte inteira fica no CI do PR.

## Achados
- A1 (bloqueante) docs/devops/pp1-pre-push.patch:156 · FILA-INTERVALO-ZERO: o mutante que troca `$((10#$intervalo))` por `$((intervalo))` sobreviveu à classe IntervaloDaFila (R-QA). Com "08"/"09" o bash dá erro de base octal e recusa um valor válido. Falta teste com "08" e "09" passando.
- A2 (bloqueante) docs/devops/pp1-pre-push.patch:53 · PREPUSH-INDICE-E-PULOS: os mutantes M11 (soltar `a != "tests/catraca.py"`) e M12 (soltar `startswith("tests/")`) sobreviveram (R-QA). Nenhum teste põe skip na catraca nem mistura `x.py` com skip fora de tests/.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cartão TEXTO-TRAVA-FD | TextoDaTravaPorFd (3 testes) | fd ausente, link trocado, limite de 200 bytes | passou; vermelho provado; M1 morreu |
| Cartão FILA-INTERVALO-ZERO | IntervaloDaFila (2 testes) | "0", "00", "000", inválidos, valor bom | passou; M2 morreu; M3 sobreviveu (A1) |
| Cartão COBERTURA-CATRACA | CoberturaDaCatraca (7 testes) | teste excluído, só falta em teste, saída 2 vira aviso, fora do controle | passou; M4, M5, M6, M7 morreram |
| Cartão INDICE (parte 1 de E-PULOS) | IndiceEPulos: fixture nova com e sem índice, fora do corpus | corpus, regenerado, fora do corpus | passou; M8, M9 morreram |
| Cartão PULOS (parte 2 de E-PULOS) | IndiceEPulos: skip novo, 4 decoradores, já existente, citado, catraca | skip, skipIf, skipUnless, expectedFailure, skipTest | passou; M10, M13, M14 morreram; M11, M12 sobreviveram (A2) |
| Roteiro de aplicar | PatchAplica | só o pre-push, bash -n, modo executável | passou |

## Cenários e resultado real
Comando do roteiro, numa cópia temporária de `git archive 6c84adb4`, com `git apply --check`, `git apply` e `bash -n` sem erro, depois `python3 -m unittest tests.test_pre_push_patch tests.test_testes_tocados`:

```
Ran 180 tests in 203.492s
OK (skipped=1)
```
O pulo é do sandbox (`MedidaDaVagaPesada`: /proc de outro namespace de pid), fora do diff.

Vermelho antes do verde: numa cópia com o hook sem os consertos (o do base, mantendo só o marcador `PRE-PUSH-TEXTO-TRAVA-FD`), os testes dos quatro cartões caem: `Ran 18 tests ... FAILED (failures=15)` (TextoDaTravaPorFd 2, IntervaloDaFila 3 valores, CoberturaDaCatraca 4, IndiceEPulos 6: fixture sem índice, skip novo e os 4 decoradores). Cada teste de cartão também compara o hook original (deve falhar) com o remendado (deve passar). No clone, com o hook original, a classe passa.

Mutantes (lista minha, um por guarda nova, 14, aplicados ao hook remendado e rodando a classe do cartão; `forge-mutante` não serve aqui porque o hook ainda não está no repositório): 11 morreram, 3 sobreviveram (M3, M11, M12). M3 confirmado em bash: `i=08; $((i))` dá "value too great for base"; com `10#` passa.

CI: o check-run `bateria` do mesmo sha fica a cargo do PR; não consultei.
