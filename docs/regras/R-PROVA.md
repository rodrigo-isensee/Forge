---
id: R-PROVA
titulo: Afirmação com prova
verificada_por: `forge-check entrega` (confere o estado real e grava a linha `entrega conferida`), `forge-check pr` e o CI (`scripts/reexecutar-provas.py`)
---
# R-PROVA: Afirmação com prova

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto.

Revisar em: 2027-01-07
Medida: 351 de 905 entregas (39%) "não cumpriu" no conferente, só 34 por implementação (estudo 0.43.1)

- Todo critério do "Pronto quando" tem um rótulo (`PQ-1`, `PQ-2`…) e o **tipo de prova**: `sha`, `push`, `pr`, `run`, `cmd`, `arquivo` ou `merge`.
- PQ `cmd` traz o esperado: `PQ-n (cmd): <comando> · espera: rc=0 | contém '<t>' | igual '<t>' | linhas=N | linhas>=N`; prefira `igual` ou `linhas=N`, e combine `rc=0 e <espera de saída>` quando o código de saída importa. PQ `cmd` fora da lista branca da ferramenta sai "do autor" (CI ou QA).
- O relatório traz o bloco `Provas:`, uma linha por `PQ-n`, com a prova **copiada da saída de uma ferramenta** que o agente rodou, ou "não cumprido" com o motivo. Item sem prova conta como **não feito**; resumo ("os testes passaram") não é prova.
- **Entrega conferida pela ferramenta:** `forge-check entrega --pedido <p> --branch <b> --etapa <etapa>` lê o estado real (git, GitHub, disco), roda os PQ que sabe conferir e, com tudo cumprido, grava no `## Histórico` a linha `entrega conferida <sha40>`. É o único escritor dessa linha; com `--sem-gravar`, só confere. A ferramenta não recebe o relatório do autor; divergência com o bloco `Provas:` volta ao autor como retrabalho. Sem ela no head, o `forge-check pr` barra o merge.
- No Forge, a branch pode trazer `docs/provas/<pedido>.md` com PQ `cmd` que o CI reexecuta (`scripts/reexecutar-provas.py`).
