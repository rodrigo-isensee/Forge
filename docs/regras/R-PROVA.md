---
id: R-PROVA
titulo: Afirmação com prova
verificada_por: conferente (modo entrega) e revisão (transcrições, ADR 0007); o hook `prova` (formato e lastro) ainda não existe
---
# R-PROVA: Afirmação com prova

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-14.

- Todo critério do "Pronto quando" de uma delegação tem um rótulo (`PQ-1`, `PQ-2`…) e o **tipo de prova** esperado: `sha`, `push`, `pr`, `run`, `cmd`, `arquivo` ou `merge`.
- O relatório traz, depois das linhas, o bloco `Provas:` com uma linha por `PQ-n`: a prova **copiada da saída de uma ferramenta** que o próprio agente rodou (hash do commit, linha do push, número do PR, id do run, comando e saída, caminho do arquivo), ou "não cumprido" com o motivo.
- Item sem prova conta como **não feito**. Resumo no lugar da cópia ("os testes passaram") não é prova.
- Entrega que termina em commit ou em ato no GitHub é conferida pelo `forge:conferente` no modo `entrega` antes do code review. Ele não recebe o relatório do autor: lê o estado real (git, GitHub, disco) e o compara com o brief, com o escopo e com a etapa do fluxo.
- Divergência entre o veredito do conferente e o bloco `Provas:` devolve a entrega ao autor, com a linha do conferente, e conta como retrabalho em `docs/kanban/entregas.md`.
