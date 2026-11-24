---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 4182040651ad42a57cd8d047c4684946efbf659d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 G1.2, revalidação por delta no head 41820406

Delta: `bdd44bc0..41820406`, que é só o merge da develop (216413c9). `forge-check parecer delta` lista no domínio `bin/forge-check`, `bin/forge-testes` e `tests/pesos-d4.json`, todos vindos da base (`autorizacao gravar`, #810, e outros). Nenhuma linha de `fora_do_delta`, de `cmd_docs`/`cmd_pr` nem de `tests/test_parecer_fora_do_delta.py` mudou no intervalo: `git diff bdd44bc0 41820406` não cita `fora_do_delta` em `bin/forge-check` e deixa o teste intacto. A tabela critério → teste → resultado do parecer anterior (head bdd44bc0, mesma tabela de G1.2) segue valendo e foi reexecutada abaixo. Sem suíte local; a inteira é do CI do PR.

## Cenários e resultado real
- Da raiz, sem `-I`: `python3 -m unittest tests.test_testes_tocados tests.test_parecer_fora_do_delta` → `Ran 217 tests ... OK (skipped=1)` (o skip já existia).
- Vermelho antes do verde e mutantes: não rerrodados, pois o código sob teste não mudou no delta; valem as provas do parecer em bdd44bc0 (24 mutantes mortos, sem sobrevivente).

## Observações
Nada bloqueante. Sem bug registrado.
